# Storm Arc probe: drive the player into the swarm, then sample until a chain beam is live and
# screenshot it. Also records how often the arc actually fires (per-weapon fireClocks fix).
import os
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_flame_arc_debrief"
os.makedirs(OUT, exist_ok=True)

with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(service_workers="block", viewport={"width": 400, "height": 860},
                        has_touch=True, is_mobile=True)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("http://127.0.0.1:8795/index.html?nocache=905", wait_until="load", timeout=20000)
    p.evaluate("""()=>{
      const meta={credits:99,damage:0,hp:0,speed:0,venom:0,bestScore:0,codexSeen:{},
        ownedWeapons:{'weapon.pulse':true,'weapon.chain':true},startWeapon:'weapon.chain'};
      localStorage.setItem('hive_swarm_meta_v1_s1',JSON.stringify(meta));
      localStorage.setItem('hive_swarm_slot','1');
    }""")
    p.reload(wait_until="load")
    p.wait_for_timeout(700)
    p.keyboard.press("Enter")
    p.wait_for_timeout(3000)
    p.keyboard.down("w")                      # charge into the spawn side
    hits = shots = 0
    for i in range(120):
        # Grab the canvas bitmap IN THE SAME evaluate that sees the live beam — a Playwright
        # screenshot round-trip takes longer than the arc's 0.2s life, so it always misses.
        data = p.evaluate("""()=>{
          if(!__swarmDbg().beams)return null;
          return document.querySelector('canvas').toDataURL('image/png');
        }""")
        if data:
            hits += 1
            if hits == 1:
                import base64
                open(f"{OUT}/arc_firing.png", "wb").write(base64.b64decode(data.split(",", 1)[1]))
        p.wait_for_timeout(100)
    p.keyboard.up("w")
    print("frames with a live arc beam:", hits, "/120   score:", p.evaluate("__swarmDbg().score"))
    print("errors:", errs)
    b.close()
