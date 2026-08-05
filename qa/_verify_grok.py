"""Claude's verification of Grok's G1-G4 on HiVE SWARM."""
from playwright.sync_api import sync_playwright
URL = "http://127.0.0.1:8796/index.html"
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    c = b.new_context(service_workers="block", viewport={"width": 460, "height": 900})
    p = c.new_page()
    errs = []; p.on("pageerror", lambda e: errs.append(str(e))); p.on("dialog", lambda d: d.accept())
    p.goto(URL, wait_until="load", timeout=20000); p.wait_for_timeout(1800)
    dbg = p.evaluate("typeof window.__swarmDbg === 'function' ? __swarmDbg() : null")
    print("dbg keys:", sorted(dbg.keys()) if dbg else "NO PROBE")
    # G1: tabbed forge
    p.evaluate("document.querySelector('#forgeBtn')?.click()"); p.wait_for_timeout(700)
    tabs = p.evaluate("Array.from(document.querySelectorAll('#forgeTabs button')).map(b=>b.textContent.trim())")
    print("G1 forge tabs:", tabs)
    # G2: save slots
    print("G2 slot api:", p.evaluate("[typeof slotInfo,typeof useSlot,typeof eraseSlot,typeof currentSlot].join(',')"))
    print("G2 current slot:", p.evaluate("typeof currentSlot==='function'?currentSlot():'n/a'"))
    # G3: beastiary unlock
    print("G3 codex api:", p.evaluate("[typeof codexSee,typeof codexVisible,typeof codexPages].join(',')"))
    b4 = p.evaluate("typeof codexVisible==='function'?codexVisible().length:-1")
    p.evaluate("typeof codexSee==='function' && codexSee('enemy:0',0)"); p.wait_for_timeout(200)
    af = p.evaluate("typeof codexVisible==='function'?codexVisible().length:-1")
    print(f"G3 unlocked {b4} -> {af} of", p.evaluate("typeof codexPages==='function'?codexPages().length:-1"))
    p.screenshot(path=r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_verify\forge.png")
    print("errors:", errs)
    b.close()
