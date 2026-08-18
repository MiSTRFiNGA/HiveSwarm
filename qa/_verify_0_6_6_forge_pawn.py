"""Static checks for Hive Swarm 0.6.6 FORGE hullSize / turretRatio."""
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


print("== 0.6.6 forge pawn ==")
ok("const GAME_VERSION='0.6.6'" in html, "GAME_VERSION=0.6.6")
ok("CACHE_VERSION = 'v27'" in sw, "sw.js v27")
ok("hullSize:.6" in html and "turretRatio:1.4" in html, "shipped 0.6 / 1.40")
ok("function playerTurretRatio()" in html and "function playerHullDraw()" in html, "live size helpers")
ok("playerTurretDraw()*PLAYER_MUZZLE_FRAC" in html, "muzzle follows turret tip")
ok("PLAYER_TURRET_FRAC" not in html, "old fixed turret frac gone")
ok("hullSize:" in html and "turretRatio:" in html, "FORGE tooltips")

if fails:
    print("FAILED", len(fails))
    sys.exit(1)
print("ALL CHECKS PASSED")
