"""Claude's verification of Grok's G4 (sprite editing in the SWARM Forge)."""
from playwright.sync_api import sync_playwright


def ascii_(x):
    return str(x).encode("ascii", "replace").decode()


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    c = b.new_context(service_workers="block", viewport={"width": 1100, "height": 900})
    p = c.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.on("dialog", lambda d: d.accept())
    p.goto("http://127.0.0.1:8796/index.html", wait_until="load", timeout=20000)
    p.wait_for_timeout(1500)
    p.evaluate("document.querySelector('#forgeBtn').click()")
    p.wait_for_timeout(500)
    tabs = p.evaluate("Array.from(document.querySelectorAll('#forgeTabs button')).map(b=>b.textContent.trim())")
    p.evaluate("document.querySelectorAll('#forgeTabs button')[%d].click()" % tabs.index('SPRITES'))
    p.wait_for_timeout(600)
    p.evaluate("document.querySelectorAll('#forgeBody button')[0].click()")
    p.wait_for_timeout(900)
    print("after selecting the first enemy:")
    print("  canvases:", p.evaluate("document.querySelectorAll('#forgeBody canvas').length"))
    print("  file inputs:", p.evaluate("document.querySelectorAll('#forgeBody input[type=file]').length"))
    print("  color inputs:", p.evaluate("document.querySelectorAll('#forgeBody input[type=color]').length"))
    btns = p.evaluate("Array.from(document.querySelectorAll('#forgeBody button')).map(b=>b.textContent.trim()).slice(0,14)")
    print("  buttons:", ascii_(btns))
    txt = p.evaluate("(document.querySelector('#forgeBody')||{}).innerText||''")
    print("  text:", ascii_(txt[:300].replace("\n", " | ")))
    p.screenshot(path=r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_verify\sprites_editor.png", full_page=True)
    print("errors:", errs)
    b.close()
