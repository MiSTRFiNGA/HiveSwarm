"""Browser evidence for G1-G4. Serves ROOT, asserts tabs/slots/beastiary/sprites."""
from __future__ import annotations

import http.server
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TABS = ['ENTITIES', 'PLAYER', 'WEAPONS', 'WAVES', 'WORLD', 'SPRITES', 'AUDIO', 'DATA', 'BEASTIARY']


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *_args):
        pass


def main() -> None:
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    print('serving', base, 'from', ROOT)
    errors: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            page.on('pageerror', lambda e: errors.append(str(e)))

            # --- FORGE tabs (owner build on localhost) ---
            page.goto(f'{base}/index.html?forge=1', wait_until='domcontentloaded')
            page.wait_for_timeout(700)
            if not page.locator('#forge.open').count():
                page.locator('#forgeBtn').click()
                page.wait_for_timeout(200)
            tabs = page.locator('#forgeTabs button').all_text_contents()
            print('TABS', tabs)
            assert tabs == TABS, tabs
            for i, name in enumerate(TABS):
                page.locator(f'#forgeTab{i}').click()
                page.wait_for_timeout(80)
                n = page.locator(
                    '#forgeBody input, #forgeBody button, #forgeBody select, '
                    '#forgeBody textarea, #forgeBody canvas'
                ).count()
                print(f'  tab {i} {name}: controls={n}')
                assert n > 0, name

            # SPRITES paint surface
            page.locator('#forgeTab5').click()
            page.wait_for_timeout(80)
            page.locator('[data-sp]').first.click()
            page.wait_for_timeout(120)
            assert page.locator('#forgePaint').count() == 1
            assert page.locator('#spSave').count() == 1
            page.locator('#spSave').click()
            page.wait_for_timeout(200)
            page.locator('#forge .x').click()
            page.wait_for_timeout(100)

            # --- Title chrome: slots + beastiary (no ?forge=1) ---
            page.goto(f'{base}/index.html', wait_until='domcontentloaded')
            page.wait_for_timeout(600)
            assert page.locator('#btnSlots').count() == 1, 'SAVE SLOTS missing'
            assert page.locator('#btnCodex').count() == 1, 'BEASTIARY missing'
            page.locator('#btnSlots').click()
            page.wait_for_timeout(120)
            assert page.locator('#slots').count() == 1
            assert page.locator('[data-slot]').count() == 3
            assert page.locator('[data-erase]').count() == 3
            page.locator('#slotsClose').click()
            page.locator('#btnCodex').click()
            page.wait_for_timeout(120)
            assert page.locator('#codex').count() == 1
            page.locator('#codexClose').click()

            # Deploy + first-sighting unlocks
            page.keyboard.press('Enter')
            page.wait_for_timeout(1800)
            dbg = page.evaluate('() => window.__swarmDbg()')
            print('DBG', dbg)
            assert dbg['state'] in ('play', 'dead', 'levelup'), dbg
            assert dbg.get('codexTotal', 0) >= 10, dbg
            assert dbg.get('slot', 0) >= 1

            # Slot isolation via evaluate (localStorage)
            iso = page.evaluate(
                """() => {
                  const k = n => 'hive_swarm_meta_v1_s' + n;
                  localStorage.setItem(k(2), JSON.stringify({credits:9,codexSeen:{'enemy:enemy.shambler':0},damage:0,hp:0,speed:0,bestScore:0}));
                  localStorage.setItem('hive_swarm_slot','3');
                  return {
                    s2: localStorage.getItem(k(2)) !== null,
                    s3: localStorage.getItem(k(3)),
                    pick: localStorage.getItem('hive_swarm_slot'),
                  };
                }"""
            )
            print('SLOT LS', iso)
            assert iso['s2'] is True
            assert iso['pick'] == '3'

            print('BROWSER CHECKS PASS')
            if errors:
                print('PAGE ERRORS', errors)
                raise SystemExit(2)
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
