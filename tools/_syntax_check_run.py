from pathlib import Path
import re, subprocess, sys

t = Path(r"D:\Dev\HiveSwarm\index.html").read_text(encoding="utf-8")
m = re.search(r"<script>\s*'use strict';(.*?)</script>", t, re.S)
print("script found", bool(m), "len", len(m.group(1)) if m else 0)
for s in [
    "twice the bubbles",
    "n=10+Math.min",
    "startDebrief",
    "fireDrones",
    "weapon.rocket",
    "wJumps",
    "isStaticEnemy",
    "buildCardPool",
    "GAME_VERSION='0.3.0'",
]:
    print(s, s in t)

if not m:
    sys.exit(2)
js = "'use strict';" + m.group(1)
p = Path(r"D:\Dev\HiveSwarm\tools\_syntax_check.js")
p.write_text(js, encoding="utf-8")
r = subprocess.run(["node", "--check", str(p)], capture_output=True, text=True)
print("node exit", r.returncode)
if r.stdout:
    print(r.stdout[:2000])
if r.stderr:
    print(r.stderr[:2000])
sys.exit(r.returncode)
