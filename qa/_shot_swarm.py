from playwright.sync_api import sync_playwright
OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_v12"
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(service_workers="block", viewport={"width":400,"height":860}, has_touch=True, is_mobile=True)
    p = ctx.new_page()
    errs = []; p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("http://127.0.0.1:8795/index.html?nocache=7", wait_until="load", timeout=20000)
    p.wait_for_timeout(800)
    p.screenshot(path=f"{OUT}/01_title.png")
    p.keyboard.press("Enter"); p.wait_for_timeout(2500)
    p.screenshot(path=f"{OUT}/02_play_idle_stick.png")
    # thumb down near bottom-left, drag: the stick should anchor there and the player should move
    p.mouse.move(120, 700); p.mouse.down(); p.mouse.move(170, 660, steps=5); p.wait_for_timeout(1400)
    print("stick:", p.evaluate("__swarmDbg().stick"))
    print("player moved:", p.evaluate("[__swarmDbg().px,__swarmDbg().py]"))
    p.screenshot(path=f"{OUT}/03_stick_engaged.png")
    p.mouse.up(); p.wait_for_timeout(2500)
    print("pickups on field:", p.evaluate("__swarmDbg().pickups"), "orbs collected:", p.evaluate("__swarmDbg().orbsCollected"), "xp:", p.evaluate("__swarmDbg().xp"))
    p.screenshot(path=f"{OUT}/04_orbs_hud.png")
    print("errors:", errs)
    b.close()
