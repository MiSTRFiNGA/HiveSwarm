from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    c = b.new_context(service_workers="block", viewport={"width": 460, "height": 900})
    p = c.new_page(); errs=[]; p.on("pageerror", lambda e: errs.append(str(e))); p.on("dialog", lambda d: d.accept())
    p.goto("http://127.0.0.1:8796/index.html", wait_until="load", timeout=20000); p.wait_for_timeout(1500)
    print("pages:", p.evaluate("codexPages().map(x=>x.link+' | '+x.title)"))
    print("unlocked now:", p.evaluate("codexVisible().map(x=>x.title)"))
    print("seen map:", p.evaluate("JSON.stringify((typeof META!=='undefined'&&META.codexSeen)||null)"))
    # try unlocking a locked one
    locked = p.evaluate("(codexPages().find(x=>x.link&&!codexVisible().includes(x))||{}).link")
    print("try unlock link:", locked)
    p.evaluate(f"codexSee({locked!r},0)"); p.wait_for_timeout(300)
    print("after:", p.evaluate("codexVisible().length"), "of", p.evaluate("codexPages().length"))
    # G4 sprite editing present?
    print("G4 sprite fns:", p.evaluate("[typeof renderSprites,typeof savedSprites,typeof mediaPut].join(',')"))
    # slot independence
    p.evaluate("useSlot(2)"); p.wait_for_timeout(200)
    print("slot2 unlocked:", p.evaluate("codexVisible().length"), "slot:", p.evaluate("currentSlot()"))
    p.evaluate("useSlot(1)"); p.wait_for_timeout(200)
    print("slot1 back:", p.evaluate("codexVisible().length"))
    print("errors:", errs)
    b.close()
