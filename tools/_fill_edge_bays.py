"""Fill almost-enclosed alpha bays without growing the outer silhouette.

A transparent pixel becomes opaque only if >= MIN_N of its 8-neighbors are
already opaque. Between-leg gaps stay open; pinholes and 1-px cracks close.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
MIN_N = 6
MAX_ITERS = 8


def fill_bays(arr: np.ndarray) -> int:
    rgb = arr[:, :, :3].copy()
    a = arr[:, :, 3].copy()
    filled = 0
    h, w = a.shape
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]], dtype=np.uint8)
    for _ in range(MAX_ITERS):
        opaque = (a >= 32).astype(np.uint8)
        # neighbor opaque count via shifts
        n = np.zeros((h, w), dtype=np.uint8)
        n[1:, :] += opaque[:-1, :]
        n[:-1, :] += opaque[1:, :]
        n[:, 1:] += opaque[:, :-1]
        n[:, :-1] += opaque[:, 1:]
        n[1:, 1:] += opaque[:-1, :-1]
        n[1:, :-1] += opaque[:-1, 1:]
        n[:-1, 1:] += opaque[1:, :-1]
        n[:-1, :-1] += opaque[1:, 1:]
        cand = (a < 32) & (n >= MIN_N)
        if not cand.any():
            break
        # color from mean of opaque 8-neighbors
        ys, xs = np.where(cand)
        for y, x in zip(ys, xs):
            y0, y1 = max(0, y - 1), min(h, y + 2)
            x0, x1 = max(0, x - 1), min(w, x + 2)
            patch = arr[y0:y1, x0:x1]
            m = patch[:, :, 3] >= 32
            if not m.any():
                continue
            rgb[y, x] = patch[:, :, :3][m].mean(axis=0).astype(np.uint8)
            a[y, x] = 255
            filled += 1
        arr[:, :, :3] = rgb
        arr[:, :, 3] = a
    return filled


def process(path: Path) -> dict:
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    n = fill_bays(arr)
    if n:
        Image.fromarray(arr, "RGBA").save(path, "PNG")
    return {"file": path.name, "filled": n}


def main():
    names = []
    for p in sorted(ROOT.glob("*.png")):
        n = p.name
        if n.startswith("mutant_enforcer") or n.startswith("zombie_colossus_idle") or (
            n.startswith("praetorian") and any(s in n for s in ("walk_s", "idle_s", "walk_se", "walk_sw", "idle_se", "idle_sw"))
        ):
            names.append(p)
    rows = [process(p) for p in names]
    print(f"processed {len(rows)}")
    for r in sorted(rows, key=lambda x: -x["filled"])[:40]:
        print(f"{r['file']:<42} {r['filled']:6d}")


if __name__ == "__main__":
    sys.exit(main())
