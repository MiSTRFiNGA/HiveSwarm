# 2026-08-18 owner set:
#   * HUD titles must not overlap (STAGE vs HOSTILES/SCORE/WAVE)
#   * Stage-end weapon line must wrap inside the debrief panel
import base64, os, sys
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_2026_08_18_hud"
os.makedirs(OUT, exist_ok=True)
PORT = sys.argv[1] if len(sys.argv) > 1 else "8797"
fails = []


def grab(page, name):
    data = page.evaluate("()=>document.querySelector('canvas').toDataURL('image/png')")
    path = os.path.join(OUT, name + ".png")
    open(path, "wb").write(base64.b64decode(data.split(",", 1)[1]))
    print("  wrote", name + ".png")


def check(label, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + label + ("  " + detail if detail else ""))
    if not cond:
        fails.append(label)


def run_at(pw, width, height, tag):
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(service_workers="block", viewport={"width": width, "height": height})
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(f"http://127.0.0.1:{PORT}/index.html?nocache=hud18", wait_until="load", timeout=20000)
    p.wait_for_timeout(400)
    p.keyboard.press("Enter")
    p.wait_for_timeout(700)

    hud = p.evaluate("""()=>{
      const h = __swarmHudLayout();
      const h2 = __swarmHudLayout({centerLines:2});
      return {h, h2, gapStageCenter: h.centerY - h.stageY, gapCenterWeapon: h.weaponY - h.centerY, gapWeaponHp: h.hpY - h.weaponBarY};
    }""")
    print("  hud", tag, hud)
    check(f"{tag} layout exists", isinstance(hud.get("h"), dict))
    h = hud.get("h") or {}
    check(f"{tag} stage above combat cluster",
          (h.get("centerY", 0) - h.get("stageY", 0)) >= 18,
          f"stageY={h.get('stageY')} centerY={h.get('centerY')}")
    check(f"{tag} weapon below combat cluster",
          (h.get("weaponY", 0) - h.get("centerY", 0)) >= 18,
          f"centerY={h.get('centerY')} weaponY={h.get('weaponY')}")
    check(f"{tag} HP below weapon bar",
          (h.get("hpY", 0) - h.get("weaponBarY", 0)) >= 8,
          f"weaponBarY={h.get('weaponBarY')} hpY={h.get('hpY')}")
    check(f"{tag} wrapped cluster pushes weapon down",
          hud["h2"]["weaponY"] > hud["h"]["weaponY"],
          f"1line={hud['h']['weaponY']} 2line={hud['h2']['weaponY']}")

    wrap = p.evaluate("""()=>{
      const c = document.createElement('canvas').getContext('2d');
      c.font = '700 14px system-ui';
      const long = 'Pulse Carbine  Rk.5 · scatter 3/5, ricochet 1/5, rapid 1/5, longreach 2/5';
      const lines = __swarmWrapText(c, long, 220);
      const widths = lines.map(ln => c.measureText(ln).width);
      return {lines, widths, max: Math.max(...widths), count: lines.length};
    }""")
    print("  wrap", tag, wrap)
    check(f"{tag} wrap produces multiple lines", wrap["count"] >= 2, f"got {wrap['lines']}")
    check(f"{tag} wrap stays inside 220px", wrap["max"] <= 220 + 1, f"max={wrap['max']}")

    grab(p, f"play_{tag}")

    p.evaluate("""()=>{
      const pulse = EDIT.weapons.find(w => w.id === 'weapon.pulse') || heldWeapons[0];
      if (pulse && !heldWeapons.some(h => h.id === pulse.id)) heldWeapons.push(pulse);
      weaponMods[pulse.id] = {scatter:3, ricochet:1, rapid:1, longreach:2};
      if (typeof runStats !== 'undefined') {
        runStats.killsBy = runStats.killsBy || {};
        runStats.weaponsSeen = runStats.weaponsSeen || {};
        runStats.weaponsSeen[pulse.id] = {id:pulse.id, name:pulse.name, rank:5};
        runStats.totalKills = 61; runStats.orbs = 65;
      }
      if (heldWeapons[0]) heldWeapons[0].rank = 5;
      __swarmDebrief();
    }""")
    p.wait_for_timeout(700)
    rows = p.evaluate("""()=>{
      const rows = debriefRows();
      const wep = rows.filter(r => r.weapon);
      return {count: rows.length, wep: wep.map(r => ({label:r.label, detail:r.detail, hasLongCombo: !!(r.label && r.detail)}))};
    }""")
    print("  debrief rows", tag, rows)
    check(f"{tag} weapon row splits name and mods",
          bool(rows["wep"]) and all(w.get("hasLongCombo") for w in rows["wep"]),
          f"got {rows['wep']}")
    grab(p, f"debrief_{tag}")
    p.wait_for_timeout(5200)
    grab(p, f"debrief_done_{tag}")
    check(f"{tag} no page errors", not errs, str(errs))
    b.close()


with sync_playwright() as pw:
    run_at(pw, 400, 860, "phone")
    run_at(pw, 800, 1280, "tablet")

if fails:
    print("FAILED:", fails)
    sys.exit(1)
print("ALL PASS")
