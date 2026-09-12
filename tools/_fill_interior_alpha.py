"""Fill torso-scale interior alpha holes. Does not change outer silhouette.

Interior = transparent islands NOT connected to the cell edge (so leg-gaps
that open to the floor stay open). Size 2..400 px. Colour copied from the
nearest opaque pixel. Magenta leftovers are punched first.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
SKIP_DIRS = {"_bak_pre_magenta_20260807", "_bak_v030_framing", "_bak_art_0_6_23"}
SKIP_PREFIX = ("subterra_maw", "player", "drone", "obstacle")
KEY = np.array([255, 0, 255], dtype=np.int32)
TOL2 = 24 * 24
MIN_ISLAND = 2
MAX_ISLAND = 400
EDGE_A = 16
OPAQUE_A = 32


def cell_size(w: int, h: int) -> int:
    if w >= h * 1.6:
        return h
    return min(w, h)


def punch_magenta(arr: np.ndarray) -> int:
    # int32: (255-0)^2 overflows int16 and falsely keys half the sheet.
    rgb = arr[:, :, :3].astype(np.int32)
    d2 = np.sum((rgb - KEY) ** 2, axis=2)
    a = arr[:, :, 3]
    mask = (a >= 8) & (d2 <= TOL2)
    n = int(mask.sum())
    if n:
        arr[mask, 3] = 0
    return n


def nearest_opaque(arr: np.ndarray, ys: np.ndarray, xs: np.ndarray) -> None:
    h, w = arr.shape[:2]
    a = arr[:, :, 3]
    opaque = a >= OPAQUE_A
    if not opaque.any():
        return
    oy, ox = np.nonzero(opaque)
    # chunked brute-force nearest; cells are 256² so this is fine
    pts = np.stack([ys, xs], axis=1)
    src = np.stack([oy, ox], axis=1)
    # for each hole pixel, nearest opaque in L2
    # 400 holes * ~20k opaque is OK; if huge, subsample
    if len(oy) > 8000:
        step = max(1, len(oy) // 8000)
        src = src[::step]
        oy, ox = src[:, 0], src[:, 1]
    # broadcast in batches of 256 hole pixels
    for i in range(0, len(pts), 256):
        batch = pts[i : i + 256]
        d = (batch[:, None, 0] - oy[None, :]) ** 2 + (batch[:, None, 1] - ox[None, :]) ** 2
        j = d.argmin(axis=1)
        ty, tx = oy[j], ox[j]
        arr[batch[:, 0], batch[:, 1]] = arr[ty, tx]


def islands_in_cell(trans: np.ndarray) -> list[list[tuple[int, int]]]:
    ch, cw = trans.shape
    seen = np.zeros((ch, cw), dtype=np.uint8)
    q = deque()
    for x in range(cw):
        q.append((0, x))
        q.append((ch - 1, x))
    for y in range(ch):
        q.append((y, 0))
        q.append((y, cw - 1))
    while q:
        y, x = q.popleft()
        if y < 0 or x < 0 or y >= ch or x >= cw:
            continue
        if seen[y, x]:
            continue
        if not trans[y, x]:
            continue
        seen[y, x] = 1
        q.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    out = []
    for y in range(ch):
        for x in range(cw):
            if seen[y, x] or not trans[y, x]:
                continue
            blob = []
            q.append((y, x))
            seen[y, x] = 1
            while q:
                cy, cx = q.popleft()
                blob.append((cy, cx))
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                    if 0 <= ny < ch and 0 <= nx < cw and not seen[ny, nx] and trans[ny, nx]:
                        seen[ny, nx] = 1
                        q.append((ny, nx))
            if MIN_ISLAND <= len(blob) <= MAX_ISLAND:
                out.append(blob)
    return out


def process(path: Path) -> dict:
    im = Image.open(path).convert("RGBA")
    arr = np.array(im)
    h, w = arr.shape[:2]
    punched = punch_magenta(arr)
    cell = cell_size(w, h)
    cols = max(1, w // cell)
    rows = max(1, h // cell)
    filled = 0
    n_isl = 0
    for row in range(rows):
        for col in range(cols):
            y0, x0 = row * cell, col * cell
            sl = arr[y0 : y0 + cell, x0 : x0 + cell]
            trans = sl[:, :, 3] < EDGE_A
            blobs = islands_in_cell(trans)
            if not blobs:
                continue
            n_isl += len(blobs)
            ys, xs = [], []
            for blob in blobs:
                for ly, lx in blob:
                    ys.append(y0 + ly)
                    xs.append(x0 + lx)
            ys = np.array(ys, dtype=np.int32)
            xs = np.array(xs, dtype=np.int32)
            nearest_opaque(arr, ys, xs)
            filled += len(ys)
    changed = punched or filled
    if changed:
        Image.fromarray(arr, "RGBA").save(path, "PNG")
    return {
        "file": path.name,
        "punched": punched,
        "filled": filled,
        "islands": n_isl,
        "changed": bool(changed),
    }


def main() -> int:
    files = [
        p
        for p in ROOT.glob("*.png")
        if not any(part in SKIP_DIRS for part in p.parts)
        and not p.name.startswith(SKIP_PREFIX)
    ]
    files.sort()
    rows = [process(p) for p in files]
    changed = [r for r in rows if r["changed"]]
    filled_px = sum(r["filled"] for r in rows)
    print(f"scanned {len(files)} pngs, changed {len(changed)}, filled_px {filled_px}")
    print(f"{'file':<42} {'magenta':>8} {'filled':>8} {'islands':>8}")
    for r in sorted(changed, key=lambda x: -x["filled"])[:60]:
        print(f"{r['file']:<42} {r['punched']:8d} {r['filled']:8d} {r['islands']:8d}")
    if not changed:
        print("no interior holes in 2..400 px range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
