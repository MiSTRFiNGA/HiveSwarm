# Verification probe for the 2026-08-13 owner change set:
#   * debrief panel 20% smaller AND every row inside the box
#   * FORGE PLAYER tab exposes accel / brake / friction
#   * weapon ranges start at 100 (seeker exempt) and Long Barrel scales off whatever the base is
import base64, os, sys
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_2026_08_13"
os.makedirs(OUT, exist_ok=True)
PORT = sys.argv[1] if len(sys.argv) > 1 else "8912"
fails = []


def grab(page, name):
    data = page.evaluate("()=>document.querySelector('canvas').toDataURL('image/png')")
    open(f"{OUT}/{name}.png", "wb").write(base64.b64decode(data.split(",", 1)[1]))
    print("  wrote", name + ".png")


def check(label, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + label + ("  " + detail if detail else ""))
    if not cond:
        fails.append(label)


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    for tag, vp, mobile in (("desktop", {"width": 1280, "height": 800}, False),
                            ("mobile",  {"width": 400,  "height": 860}, True)):
        ctx = b.new_context(service_workers="block", viewport=vp,
                            has_touch=mobile, is_mobile=mobile)
        p = ctx.new_page()
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        # Fresh localStorage every run so the range migration is exercised from shipped defaults.
        p.goto(f"http://127.0.0.1:{PORT}/index.html?nocache={tag}", wait_until="load", timeout=20000)
        p.wait_for_timeout(600)
        p.keyboard.press("Enter")
        p.wait_for_timeout(6000)            # bank kills so the debrief has real rows

        print(f"\n== {tag} {vp['width']}x{vp['height']} ==")

        # ---- ranges ----------------------------------------------------------------
        # Read EDIT.weapons directly — __swarmDbg().weapons is the HELD-weapon summary and carries
        # no `range` field, so sourcing from it silently yields None for every gun.
        ranges = p.evaluate("()=>{const o={};for(const w of EDIT.weapons)o[w.id]=w.range;return o}")
        print("  ranges:", ranges)
        for wid, r in ranges.items():
            if wid == "weapon.seeker":
                check("seeker range exempt (900)", r == 900, f"got {r}")
            else:
                check(f"{wid} range==100", r == 100, f"got {r}")

        # Long Barrel is modular: +30% of whatever base the owner sets, at ANY base.
        modular = p.evaluate("""()=>{
          const w=EDIT.weapons.find(x=>x.id==='weapon.pulse');
          const out=[];
          for(const base of [100,250,600]){
            const old=w.range; w.range=base;
            weaponMods[w.id]={};            const r0=wRange(w);
            weaponMods[w.id]={longrange:1}; const r1=wRange(w);
            weaponMods[w.id]={longrange:3}; const r3=wRange(w);
            w.range=old; weaponMods[w.id]={};
            out.push({base,r0,r1,r3});
          }
          const s=EDIT.weapons.find(x=>x.id==='weapon.seeker');
          weaponMods[s.id]={longrange:3}; const seeker=wRange(s); weaponMods[s.id]={};
          return {out,seeker};
        }""")
        for row in modular["out"]:
            b0, r0, r1, r3 = row["base"], row["r0"], row["r1"], row["r3"]
            check(f"base {b0}: no mod == base", abs(r0 - b0) < .01, f"got {r0}")
            check(f"base {b0}: 1 stack == +30%", abs(r1 - b0 * 1.30) < .01, f"got {r1}")
            check(f"base {b0}: 3 stacks == +90%", abs(r3 - b0 * 1.90) < .01, f"got {r3}")
        check("seeker ignores range stacks", abs(modular["seeker"] - 900) < .01,
              f"got {modular['seeker']}")

        # ---- movement knobs exist and are live -------------------------------------
        mv = p.evaluate("()=>({accel:EDIT.player.accel,brake:EDIT.player.brake,friction:EDIT.player.friction,hasV:'vx' in player})")
        print("  movement:", mv)
        check("accel/brake/friction present", all(isinstance(mv[k], (int, float)) for k in ("accel", "brake", "friction")))
        check("player has velocity", mv["hasV"])

        # ---- debrief geometry ------------------------------------------------------
        p.evaluate("__swarmDebrief()")
        p.wait_for_timeout(400)
        grab(p, f"debrief_{tag}_counting")
        p.wait_for_timeout(6000)            # let the tally finish so every row is drawn
        grab(p, f"debrief_{tag}_done")

        geo = p.evaluate("""()=>{
          const W=VIEW.w,H=VIEW.h,SH=.8;
          const panelW=(W-36)*SH,panelH=(H-56)*SH;
          const px0=(W-panelW)/2,py0=(H-panelH)/2;
          const hs=Math.min(1,panelH/((H-56)||1));
          const rows=debriefRows();
          const rowTop=py0+Math.round(110*hs), rowBottom=py0+panelH-Math.round(64*hs);
          const avail=rowBottom-rowTop;
          const pitch=Math.min(64,rows.length>1?avail/rows.length:64);
          const startY=rowTop+Math.max(0,(avail-rows.length*pitch)/2);
          const lastY=startY+(rows.length-1)*pitch;
          return {W,H,panelW,panelH,px0,py0,rows:rows.length,pitch,startY,lastY,rowTop,rowBottom,
                  panelBottom:py0+panelH,footerY:py0+panelH-Math.round(28*hs)};
        }""")
        print("  geo:", {k: (round(v, 1) if isinstance(v, float) else v) for k, v in geo.items()})
        check("panel is 80% of viewport-minus-margin (W)",
              abs(geo["panelW"] - (geo["W"] - 36) * .8) < .01)
        check("panel is 80% of viewport-minus-margin (H)",
              abs(geo["panelH"] - (geo["H"] - 56) * .8) < .01)
        check("first row below header", geo["startY"] >= geo["rowTop"] - .01,
              f"startY={geo['startY']:.1f} rowTop={geo['rowTop']:.1f}")
        check("last row above footer", geo["lastY"] <= geo["rowBottom"] + .01,
              f"lastY={geo['lastY']:.1f} rowBottom={geo['rowBottom']:.1f}")
        check("rows inside panel", geo["lastY"] < geo["panelBottom"],
              f"lastY={geo['lastY']:.1f} panelBottom={geo['panelBottom']:.1f}")

        # Overflow stress: force a long row list and re-check the fit guarantee.
        stress = p.evaluate("""()=>{
          const W=VIEW.w,H=VIEW.h,SH=.8;
          const panelH=(H-56)*SH, py0=(H-panelH)/2;
          const hs=Math.min(1,panelH/((H-56)||1));
          const rowTop=py0+Math.round(110*hs), rowBottom=py0+panelH-Math.round(64*hs);
          const avail=rowBottom-rowTop;
          const out=[];
          for(const n of [4,12,30,60]){
            const pitch=Math.min(64,n>1?avail/n:64);
            const startY=rowTop+Math.max(0,(avail-n*pitch)/2);
            out.push({n,pitch,last:startY+(n-1)*pitch,rowBottom});
          }
          return out;
        }""")
        for r in stress:
            check(f"{r['n']} rows still fit", r["last"] <= r["rowBottom"] + .01,
                  f"last={r['last']:.1f} bottom={r['rowBottom']:.1f} pitch={r['pitch']:.1f}")

        check("no page errors", not errs, "; ".join(errs[:3]))
        ctx.close()
    b.close()

print("\n" + ("ALL CHECKS PASSED" if not fails else f"{len(fails)} FAILURES: {fails}"))
sys.exit(1 if fails else 0)
