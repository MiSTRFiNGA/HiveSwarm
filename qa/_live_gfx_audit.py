"""Line up every Swarm enemy around the player and screenshot live art."""
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(r"D:\Dev\HiveSwarm\qa\evidence\live_gfx")
OUT.mkdir(parents=True, exist_ok=True)
BRAVE = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

PLACE = """() => {
  paused = true;
  enemies.length = 0;
  const roster = (ENEMIES || []).filter(e => e && e.id && e.id.indexOf('enemy.') === 0);
  const names = [];
  const n = roster.length;
  const R = 210;
  for (let i = 0; i < n; i++) {
    const type = roster[i];
    const a = -Math.PI/2 + (i / n) * Math.PI * 2;
    const er = (type.r || 16) * (type.scale || 1);
    enemies.push({
      x: player.x + Math.cos(a) * R,
      y: player.y + Math.sin(a) * R,
      r: er, hp: 9999, maxHp: 9999, speed: 0, damage: 0,
      type, color: type.color, hit: 0, elite: null, t: 0.4, angle: a + Math.PI
    });
    names.push(type.name);
  }
  WORLD.maxEnemies = enemies.length;
  return {n, names, version: GAME_VERSION, px: player.x, py: player.y};
}"""


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=BRAVE)
        page = browser.new_page(viewport={"width": 540, "height": 960})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto("http://127.0.0.1:8795/index.html", wait_until="load", timeout=30000)
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT / "00_title.png"))
        page.keyboard.press("Enter")
        page.wait_for_timeout(1200)
        info = page.evaluate(PLACE)
        print("placed", info)
        page.wait_for_timeout(200)
        page.screenshot(path=str(OUT / "01_all_kinds.png"))
        # runner + colossus close-ups, 3 facings
        page.evaluate(
            """() => {
              enemies.length = 0;
              const runner = ENEMIES.find(e => e.id === 'enemy.runner');
              const colo = ENEMIES.find(e => e.id === 'enemy.colossus');
              const specs = [
                {type: runner, x: player.x - 140, y: player.y - 40, angle: Math.PI/2},
                {type: runner, x: player.x, y: player.y - 40, angle: Math.PI*0.75},
                {type: runner, x: player.x + 140, y: player.y - 40, angle: Math.PI*0.25},
                {type: colo, x: player.x - 150, y: player.y + 160, angle: 0},
                {type: colo, x: player.x, y: player.y + 160, angle: Math.PI/2},
                {type: colo, x: player.x + 150, y: player.y + 160, angle: Math.PI},
              ];
              for (const s of specs) {
                enemies.push({
                  x:s.x,y:s.y,r:(s.type.r||16)*(s.type.scale||1),
                  hp:9999,maxHp:9999,speed:0,damage:0,type:s.type,color:s.type.color,
                  hit:0,elite:null,t:0.5,angle:s.angle,vx:Math.cos(s.angle)*40,vy:Math.sin(s.angle)*40
                });
              }
              WORLD.maxEnemies = enemies.length;
            }"""
        )
        page.wait_for_timeout(250)
        page.screenshot(path=str(OUT / "02_runner_colossus.png"))
        print("errors", errs)
        browser.close()


if __name__ == "__main__":
    main()
