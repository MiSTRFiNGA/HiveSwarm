# 2026-08-18: slime splash gone, necro never a boss, boss scale >= 3, enemy SFX present
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(r"D:\Dev\HiveSwarm")
html = (ROOT / "index.html").read_text(encoding="utf-8")
fails = []


def ok(cond, label, detail=""):
    print(("PASS " if cond else "FAIL ") + label + (("  " + detail) if detail else ""))
    if not cond:
        fails.append(label)


ok("const GAME_VERSION='0.6.16'" in html, "GAME_VERSION 0.6.16")
ok("CACHE_VERSION = 'v38'" in (ROOT / "sw.js").read_text(encoding="utf-8"), "sw cache v38")
ok("function canBeBoss" in html, "canBeBoss helper")
ok("id==='enemy.necroNode'" in html, "necro explicitly banned from boss")
ok("Math.max(3," in html and "BOSS_FIGHT_SCALE" in html, "boss scale floors at 3x")
ok("waveRoster().filter(canBeBoss)" in html, "boss pool filters static/necro")

sfx_dir = ROOT / "assets" / "SFX"
needed = [
    "shambler_attack.mp3", "shambler_die.mp3", "slime_attack.mp3", "slime_die.mp3",
    "runner_attack.mp3", "runner_die.mp3", "node_attack.mp3", "node_die.mp3",
    "crawler_attack.mp3", "crawler_die.mp3", "psychoid_attack.mp3", "psychoid_die.mp3",
    "necro_attack.mp3", "necro_die.mp3", "biomorph_attack.mp3", "biomorph_die.mp3",
    "brute_attack.mp3", "brute_die.mp3", "cyber_attack.mp3", "cyber_die.mp3",
    "armored_attack.mp3", "armored_die.mp3", "mutant_attack.mp3", "mutant_die.mp3",
    "colossus_attack.mp3", "colossus_die.mp3", "praetorian_attack.mp3", "praetorian_die.mp3",
]
for name in needed:
    p = sfx_dir / name
    ok(p.is_file() and p.stat().st_size > 800, f"sfx {name}", f"bytes={p.stat().st_size if p.is_file() else 0}")
    ok(name in html, f"library lists {name}")

for stem, field in (
    ("enemy.shambler", "shambler_attack.mp3"),
    ("enemy.slime", "slime_attack.mp3"),
    ("enemy.necroNode", "necro_die.mp3"),
    ("enemy.praetorian", "praetorian_attack.mp3"),
):
    ok(stem in html and field in html, f"{stem} wired to {field}")


def green_leak(path: Path) -> float:
    arr = np.array(Image.open(path).convert("RGBA"))
    a = arr[:, :, 3] > 12
    if not a.any():
        return 1
    r, g, b = arr[:, :, 0].astype(np.int16), arr[:, :, 1].astype(np.int16), arr[:, :, 2].astype(np.int16)
    leak = a & (g > r + 18) & (g > b + 18)
    return float(leak.sum() / a.sum())


for name in ("slime.png", "slime_idle.png", "slime_walk.png", "slime_attack.png"):
    p = ROOT / "art_src" / "topdown_v1" / name
    leak = green_leak(p)
    ok(p.is_file() and leak < 0.01, f"slime {name} no green splash", f"leak={leak:.4f}")
    im = Image.open(p)
    ok(im.size[0] >= 256 and im.size[1] == 256, f"slime {name} cell height", f"{im.size}")

if fails:
    print("FAILED", fails)
    raise SystemExit(1)
print("ALL PASS")
