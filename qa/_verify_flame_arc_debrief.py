# Visual verification for the 2026-08-09 owner asks:
#   1. Flamethrower must read like HiVE WAR's (soft additive puffs, not a gradient wedge)
#   2. Storm Arc must fire on its OWN rate (per-weapon fireClocks), not the primary's
#   3. Stage-clear debrief must have HiVE WAR's fireworks + fanfare
import os
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_flame_arc_debrief"
os.makedirs(OUT, exist_ok=True)
URL = "http://127.0.0.1:8795/index.html?nocache=902"

def seed(page, weapon):
    page.evaluate("""(w)=>{
      const meta={credits:99,damage:0,hp:0,speed:0,venom:0,bestScore:0,codexSeen:{},
        ownedWeapons:{'weapon.pulse':true,'weapon.flame':true,'weapon.chain':true},startWeapon:w};
      localStorage.setItem('hive_swarm_meta_v1_s1',JSON.stringify(meta));
      localStorage.setItem('hive_swarm_slot','1');
    }""", weapon)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    for weapon, tag in (("weapon.flame", "flame"), ("weapon.chain", "arc")):
        ctx = b.new_context(service_workers="block", viewport={"width": 400, "height": 860},
                            has_touch=True, is_mobile=True)
        p = ctx.new_page()
        errs = []
        p.on("pageerror", lambda e: errs.append(str(e)))
        p.goto(URL, wait_until="load", timeout=20000)
        seed(p, weapon)
        p.reload(wait_until="load")
        p.wait_for_timeout(800)
        p.keyboard.press("Enter")
        p.wait_for_timeout(14000)          # let enemies close in so the weapon is actually firing
        print(tag, "startWeapon:", p.evaluate("__swarmDbg().startWeapon"),
              "beams:", p.evaluate("__swarmDbg().beams"),
              "enemies:", p.evaluate("__swarmDbg().enemies"))
        for i in range(3):
            p.screenshot(path=f"{OUT}/{tag}_{i}.png")
            p.wait_for_timeout(300)
        print(tag, "errors:", errs)
        ctx.close()
    b.close()
