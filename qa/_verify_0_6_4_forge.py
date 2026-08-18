"""Static checks for Hive Swarm 0.6.4: Maw gone, FORGE rotate/dup/reorder present."""
from pathlib import Path
import re
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


print("== 0.6.4 forge / maw / version ==")
ok("const GAME_VERSION='0.6.4'" in html, "GAME_VERSION=0.6.4")
ok("CACHE_VERSION = 'v25'" in sw, "sw.js CACHE_VERSION=v25")
ok("{id:'enemy.maw'" not in html.split("RETIRED_FORGE_IDS")[0], "enemy.maw not in FORGE_BASE")
ok("'enemy.maw'" in html and "RETIRED_FORGE_IDS=new Set(['weapon.rocket','enemy.maw'])" in html, "enemy.maw retired")
ok("edit.entities=edit.entities.filter(e=>!RETIRED_FORGE_IDS.has(e.id))" in html, "pruneRetired drops entities")
ok("'subterra_maw'" not in re.search(r"const PRELOAD_STEMS=\[([^\]]+)\]", html).group(1), "maw not in PRELOAD_STEMS")
ok("id=\"spRot\"" in html and "ART ROTATE" in html, "ART ROTATE control present")
ok("id=\"spRotLock\"" in html and "id=\"spRotGo\"" in html, "15 lock + APPLY present")
ok("function rotateSpriteArt(degrees)" in html, "rotateSpriteArt implemented")
ok("id=\"spDupFrame\"" in html and "function dupFrame()" in html, "DUP FRAME present")
ok("id=\"spMoveL\"" in html and "id=\"spMoveR\"" in html, "MOVE L/R present")
ok("function reorderFrames(from,to)" in html, "reorderFrames implemented")
ok("t.draggable=true" in html, "thumbs are draggable")
ok("function alphaKeySprite(hex,tolerance)" in html and "id=\"spKey\"" in html, "ALPHA KEY present")
ok("subterra_maw" not in re.search(r"const stems=\[([^\]]+)\];\s*expAll", html).group(1), "export-all drops maw")

if fails:
    print(f"FAILED {len(fails)}")
    sys.exit(1)
print("ALL CHECKS PASSED")
