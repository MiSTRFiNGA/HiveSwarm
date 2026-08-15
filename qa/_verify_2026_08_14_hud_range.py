# 2026-08-14 owner set:
#   * HUD: weapon name must not sit on WAVE; beastiary toast must not cover HP
#   * Breach Laser + Storm Arc ship at range 200 (other guns stay 100, seeker 900)
#   * Stage-end debrief copy is a punchy clear banner, not "STAGE N CLEAR"
import base64, os, sys
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_2026_08_14_hud"
os.makedirs(OUT, exist_ok=True)
PORT = sys.argv[1] if len(sys.argv) > 1 else "8795"
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


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(service_workers="block", viewport={"width": 400, "height": 860})
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto(f"http://127.0.0.1:{PORT}/index.html?nocache=hud14", wait_until="load", timeout=20000)
    p.wait_for_timeout(500)
    p.keyboard.press("Enter")
    p.wait_for_timeout(800)

    ranges = p.evaluate("()=>{const o={};for(const w of EDIT.weapons)o[w.id]=w.range;return o}")
    print("  ranges:", ranges)
    check("pulse range 100", ranges.get("weapon.pulse") == 100, f"got {ranges.get('weapon.pulse')}")
    check("seeker range 900", ranges.get("weapon.seeker") == 900, f"got {ranges.get('weapon.seeker')}")
    check("flame range 100", ranges.get("weapon.flame") == 100, f"got {ranges.get('weapon.flame')}")
    check("beam range 200", ranges.get("weapon.beam") == 200, f"got {ranges.get('weapon.beam')}")
    check("chain range 200", ranges.get("weapon.chain") == 200, f"got {ranges.get('weapon.chain')}")
    check("nova range 100", ranges.get("weapon.nova") == 100, f"got {ranges.get('weapon.nova')}")
    check("poison range 100", ranges.get("weapon.poison") == 100, f"got {ranges.get('weapon.poison')}")

    hud = p.evaluate("()=>typeof __swarmHudLayout==='function'?__swarmHudLayout():null")
    print("  hud:", hud)
    check("__swarmHudLayout exists", isinstance(hud, dict))
    if isinstance(hud, dict):
        check("weapon name below stage line",
              hud["weaponY"] >= hud["stageY"] + 18,
              f"weaponY={hud.get('weaponY')} stageY={hud.get('stageY')}")
        check("weapon name below HP bar",
              hud["weaponY"] >= hud["hpBottom"] + 8,
              f"weaponY={hud.get('weaponY')} hpBottom={hud.get('hpBottom')}")
        check("toast below HUD stack",
              hud["toastY"] >= hud["hudBottom"] + 8,
              f"toastY={hud.get('toastY')} hudBottom={hud.get('hudBottom')}")

    p.evaluate("__swarmDebrief()")
    p.wait_for_timeout(500)
    copy = p.evaluate("()=>typeof __swarmDebriefCopy==='function'?__swarmDebriefCopy():null")
    print("  debrief copy:", copy)
    check("__swarmDebriefCopy exists", isinstance(copy, dict))
    if isinstance(copy, dict):
        head = (copy.get("headline") or "").upper()
        check("headline is not STAGE N CLEAR",
              "STAGE" not in head or "CLEAR" not in head,
              f"got {copy.get('headline')!r}")
        check("headline has a punch word",
              any(w in head for w in ("PURGED", "CLEARED", "BROKEN", "SECURED", "DOWN")),
              f"got {copy.get('headline')!r}")
        check("kicker names the stage",
              bool(copy.get("stageName")),
              f"got {copy.get('stageName')!r}")
    grab(p, "debrief_open")
    p.wait_for_timeout(5500)
    grab(p, "debrief_done")
    grab(p, "hud_play")
    check("no page errors", not errs, str(errs))
    b.close()

print()
if fails:
    print("FAILED:", "; ".join(fails))
    sys.exit(1)
print("ALL CHECKS PASSED")
