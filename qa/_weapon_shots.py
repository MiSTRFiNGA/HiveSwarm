"""Capture one screenshot per weapon for G6 visual proof. Also checks pause button."""
from __future__ import annotations

import http.server
import threading
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)
WEAPONS = [
    'weapon.pulse',
    'weapon.seeker',
    'weapon.beam',
    'weapon.chain',
    'weapon.nova',
]


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, *_a):
        pass


def main() -> None:
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{srv.server_port}'
    print('serving', base)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 540, 'height': 960})
        page.goto(f'{base}/index.html', wait_until='domcontentloaded')
        page.wait_for_timeout(500)
        # pause button present on title
        assert page.locator('#pauseBtn').count() == 1
        page.keyboard.press('Enter')
        page.wait_for_timeout(400)
        # pause via button
        page.locator('#pauseBtn').click()
        page.wait_for_timeout(150)
        dbg = page.evaluate('() => window.__swarmDbg()')
        assert dbg.get('paused') is True, dbg
        page.screenshot(path=str(OUT / 'pause_button.png'))
        page.keyboard.press('p')
        page.wait_for_timeout(100)
        dbg = page.evaluate('() => window.__swarmDbg()')
        assert dbg.get('paused') is False, dbg

        for wid in WEAPONS:
            page.evaluate(
                """(id) => {
                  // equip only this weapon and force a short burst of fire
                  const T = window;
                  // reach via debug hooks + grant path
                  if (typeof window.__swarmDbg !== 'function') return false;
                  // force through evaluate by calling internal via a temp grant
                  // We re-deploy with start weapon owned
                  const m = JSON.parse(localStorage.getItem('hive_swarm_meta_v1_s1') || '{}');
                  m.ownedWeapons = m.ownedWeapons || {'weapon.pulse': true};
                  m.ownedWeapons[id] = true;
                  m.startWeapon = id;
                  localStorage.setItem('hive_swarm_meta_v1_s1', JSON.stringify(m));
                  localStorage.setItem('hive_swarm_slot', '1');
                  return true;
                }""",
                wid,
            )
            page.reload(wait_until='domcontentloaded')
            page.wait_for_timeout(400)
            page.keyboard.press('Enter')
            # run a few seconds so projectiles / beams are visible
            page.wait_for_timeout(2200)
            # also grant all held as that one for multi-fire types mid-run
            page.evaluate(
                """(id) => {
                  // inject by re-calling deploy path is hard; force fire by spawning enemies near player
                  // Use __swarmDbg only — weapon already startWeapon
                  return window.__swarmDbg();
                }""",
                wid,
            )
            page.screenshot(path=str(OUT / f'weapon_{wid.split(".")[-1]}.png'))
            print('shot', wid, page.evaluate('() => window.__swarmDbg().weapons'))

        print('SHOTS OK', list(OUT.glob('*.png')))
        browser.close()
    srv.shutdown()


if __name__ == '__main__':
    main()
