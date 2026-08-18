"""Conservative hole pass for shipped Swarm sprites.

Holes live IN the PNG (leftover FORGE #ff00ff keying / over-keyed torso).
This script:

  1. Punches remaining near-magenta pixels to transparent (tol 24).
  2. Splits wide strips into square cells.
  3. Floods each cell from its own edges (so walk-strip padding is background).
  4. Fills only SMALL interior islands (2..MAX_ISLAND px) from the pre-magenta
     backup when that pixel is opaque, else nearest opaque neighbour.

Large enclosed gaps (between legs, between frames) are left alone.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

from PIL import Image

ROOT = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
BAK = ROOT / "_bak_pre_magenta_20260807"
KEY = (255, 0, 255)
TOL2 = 24 * 24
MIN_ISLAND = 2
MAX_ISLAND = 400  # torso-scale. Never inpaint — backup pixels only.
SKIP_DIRS = {"_bak_pre_magenta_20260807", "_bak_v030_framing"}


def is_key(r: int, g: int, b: int, a: int) -> bool:
    if a < 8:
        return False
    return (r - KEY[0]) ** 2 + (g - KEY[1]) ** 2 + (b - KEY[2]) ** 2 <= TOL2


def cell_size(w: int, h: int) -> int:
    if w >= h * 1.6:
        return h
    return min(w, h)


def islands_in_cell(px, w: int, h: int, x0: int, y0: int, cw: int, ch: int):
    """Return list of interior transparent islands (index lists) inside one cell."""
    seen = bytearray(cw * ch)

    def at(lx, ly):
        return px[(y0 + ly) * w + (x0 + lx)][3] < 16

    q = deque()
    for x in range(cw):
        q.append((x, 0))
        q.append((x, ch - 1))
    for y in range(ch):
        q.append((0, y))
        q.append((cw - 1, y))
    while q:
        x, y = q.popleft()
        if x < 0 or y < 0 or x >= cw or y >= ch:
            continue
        i = y * cw + x
        if seen[i]:
            continue
        if not at(x, y):
            continue
        seen[i] = 1
        q.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))

    islands = []
    for ly in range(ch):
        for lx in range(cw):
            i = ly * cw + lx
            if seen[i] or not at(lx, ly):
                continue
            blob = []
            q.append((lx, ly))
            seen[i] = 1
            while q:
                x, y = q.popleft()
                blob.append((y0 + y) * w + (x0 + x))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < cw and 0 <= ny < ch:
                        j = ny * cw + nx
                        if not seen[j] and at(nx, ny):
                            seen[j] = 1
                            q.append((nx, ny))
            if MIN_ISLAND <= len(blob) <= MAX_ISLAND:
                islands.append(blob)
    return islands


def nearest_opaque(px, w: int, h: int, sx: int, sy: int, max_r: int = 6):
    for rad in range(1, max_r + 1):
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if abs(dx) != rad and abs(dy) != rad:
                    continue
                x, y = sx + dx, sy + dy
                if 0 <= x < w and 0 <= y < h:
                    r, g, b, a = px[y * w + x]
                    if a >= 32 and not is_key(r, g, b, a):
                        return (r, g, b, a)
    return None


def process(path: Path) -> dict:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = list(im.getdata())
    punched = 0
    out = []
    for r, g, b, a in px:
        if is_key(r, g, b, a):
            out.append((r, g, b, 0))
            punched += 1
        else:
            out.append((r, g, b, a))

    cell = cell_size(w, h)
    cols = max(1, w // cell)
    rows = max(1, h // cell)
    hole_px = 0
    filled_bak = 0
    filled_inpaint = 0

    bak = None
    bak_path = BAK / path.name
    if bak_path.is_file():
        bim = Image.open(bak_path).convert("RGBA")
        if bim.size == (w, h):
            bak = list(bim.getdata())

    for row in range(rows):
        for col in range(cols):
            x0, y0 = col * cell, row * cell
            for blob in islands_in_cell(out, w, h, x0, y0, cell, cell):
                hole_px += len(blob)
                if not bak:
                    continue
                for i in blob:
                    br, bgc, bb, ba = bak[i]
                    if ba >= 32 and not is_key(br, bgc, bb, ba):
                        out[i] = (br, bgc, bb, ba)
                        filled_bak += 1

    changed = punched or filled_bak or filled_inpaint
    if changed:
        im.putdata(out)
        im.save(path, "PNG")
    return {
        "file": path.name,
        "punched": punched,
        "holes": hole_px,
        "filled_bak": filled_bak,
        "filled_inpaint": filled_inpaint,
        "changed": bool(changed),
    }


def main() -> int:
    files = [
        p
        for p in ROOT.rglob("*.png")
        if not any(part in SKIP_DIRS for part in p.parts)
        and not p.name.startswith("subterra_maw")
    ]
    files.sort()
    rows = [process(p) for p in files]
    changed = [r for r in rows if r["changed"]]
    print(f"scanned {len(files)} pngs, changed {len(changed)}")
    print(f"{'file':<42} {'magenta':>8} {'holes':>7} {'bak':>6} {'inpaint':>7}")
    for r in sorted(changed, key=lambda x: -(x["punched"] + x["holes"]))[:50]:
        print(
            f"{r['file']:<42} {r['punched']:8d} {r['holes']:7d} "
            f"{r['filled_bak']:6d} {r['filled_inpaint']:7d}"
        )
    if not changed:
        print("no magenta leftovers or small interior holes found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
