# Debrief celebration probe: jump to the stage-clear screen via __swarmDebrief() and capture the
# opening fanfare burst and the sustained celebration once the tally finishes.
import base64
import os
from playwright.sync_api import sync_playwright

OUT = r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_flame_arc_debrief"
os.makedirs(OUT, exist_ok=True)


def grab(page, name):
    data = page.evaluate("()=>document.querySelector('canvas').toDataURL('image/png')")
    open(f"{OUT}/{name}.png", "wb").write(base64.b64decode(data.split(",", 1)[1]))


with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(service_workers="block", viewport={"width": 400, "height": 860},
                        has_touch=True, is_mobile=True)
    p = ctx.new_page()
    errs = []
    p.on("pageerror", lambda e: errs.append(str(e)))
    p.goto("http://127.0.0.1:8795/index.html?nocache=904", wait_until="load", timeout=20000)
    p.wait_for_timeout(600)
    p.keyboard.press("Enter")
    p.wait_for_timeout(6000)                 # bank a few kills so the tally has rows
    p.evaluate("__swarmDebrief()")
    p.wait_for_timeout(500)
    print("state:", p.evaluate("__swarmDbg().state"))
    grab(p, "debrief_fanfare")
    p.wait_for_timeout(4000)                 # tally finishes -> sustained celebration
    grab(p, "debrief_celebrating")
    print("errors:", errs)
    b.close()
