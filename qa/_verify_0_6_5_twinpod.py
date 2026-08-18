"""Static checks for Hive Swarm 0.6.5 Twin Pod pawn."""
from pathlib import Path
import sys

ROOT = Path(r"D:\Dev\HiveSwarm")
html = (ROOT / "index.html").read_text(encoding="utf-8")
sw = (ROOT / "sw.js").read_text(encoding="utf-8")
fails = []


def ok(cond, msg):
    if cond:
        print("  PASS", msg)
    else:
        print("  FAIL", msg)
        fails.append(msg)


print("== 0.6.5 twin pod ==")
ok("const GAME_VERSION='0.6.5'" in html, "GAME_VERSION=0.6.5")
ok("CACHE_VERSION = 'v26'" in sw, "sw.js v26")
ok("function drawTwinPod(" in html, "drawTwinPod exists")
ok("player.hullAngle" in html and "player.angle=Math.atan2(dy,dx)" not in html, "move writes hullAngle not aim")
ok("PLAYER_HULL" in html and "PLAYER_TURRET" in html, "hull + turret paths")
ok((ROOT / "art_src/topdown_v1/player_hull.png").is_file(), "player_hull.png")
ok((ROOT / "art_src/topdown_v1/player_turret.png").is_file(), "player_turret.png")
ok("drawTwinPod(px,py" in html, "gameplay uses twin pod")
ok("playerDrawSize()*PLAYER_TURRET_FRAC*PLAYER_MUZZLE_FRAC" in html, "muzzle from turret tip")

if fails:
    print("FAILED", len(fails))
    sys.exit(1)
print("ALL CHECKS PASSED")
