"""Tight-pack enemy sheets so the body fills the cell.

Root cause of "blank areas": 256px cells with a small opaque blob (and leftover
scrap at the bottom of some cyber_mutant frames). Draw uses the full cell, so
the character looks tiny with empty glass around it.

Per stem, take the largest connected opaque blob in every walk/idle/attack
frame, share one scale so facings stay consistent, scale to FILL of the cell,
and recenter.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

ART = Path(__file__).resolve().parents[1] / "art_src" / "topdown_v1"
CELL = 256
FILL = 0.90
STATES = ("walk", "idle", "attack")
DIRS = ("s", "se", "sw", "e", "w", "n", "ne", "nw")


def stems() -> list[str]:
    found = set()
    skip = {"player", "subterra_maw"}
    for p in ART.glob("*_walk_s.png"):
        stem = p.name[: -len("_walk_s.png")]
        if stem not in skip:
            found.add(stem)
    return sorted(found)


def largest_blob(cell: np.ndarray) -> tuple[int, int, int, int] | None:
    vis = cell[:, :, 3] > 12
    h, w = vis.shape
    seen = np.zeros_like(vis, dtype=np.uint8)
    best = None
    best_n = 0
    ys, xs = np.where(vis)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if seen[y, x]:
            continue
        stack = [(y, x)]
        seen[y, x] = 1
        pix = []
        while stack:
            cy, cx = stack.pop()
            pix.append((cy, cx))
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < h and 0 <= nx < w and vis[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = 1
                    stack.append((ny, nx))
        if len(pix) > best_n:
            best_n = len(pix)
            yy = [p[0] for p in pix]
            xx = [p[1] for p in pix]
            best = (min(xx), min(yy), max(xx) + 1, max(yy) + 1)
    if not best or best_n < 80:
        return None
    return best


def frames_of(path: Path) -> list[Image.Image]:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    cell = h
    n = max(1, w // cell)
    return [im.crop((i * cell, 0, (i + 1) * cell, cell)) for i in range(n)]


def process_stem(stem: str) -> int:
    files: list[Path] = []
    for state in STATES:
        for d in DIRS:
            p = ART / f"{stem}_{state}_{d}.png"
            if p.is_file():
                files.append(p)
    if not files:
        return 0
    maxd = 1
    crops: dict[Path, list[tuple[Image.Image, tuple[int, int, int, int]]]] = defaultdict(list)
    for path in files:
        for fr in frames_of(path):
            arr = np.array(fr)
            bb = largest_blob(arr)
            if not bb:
                crops[path].append((fr, (0, 0, fr.size[0], fr.size[1])))
                continue
            x0, y0, x1, y1 = bb
            pad = 4
            x0 = max(0, x0 - pad)
            y0 = max(0, y0 - pad)
            x1 = min(fr.size[0], x1 + pad)
            y1 = min(fr.size[1], y1 + pad)
            crops[path].append((fr, (x0, y0, x1, y1)))
            maxd = max(maxd, x1 - x0, y1 - y0)
    scale = (CELL * FILL) / maxd
    written = 0
    for path, items in crops.items():
        out = Image.new("RGBA", (CELL * len(items), CELL), (0, 0, 0, 0))
        for i, (fr, bb) in enumerate(items):
            blob = fr.crop(bb)
            nw = max(1, int(round(blob.size[0] * scale)))
            nh = max(1, int(round(blob.size[1] * scale)))
            blob = blob.resize((nw, nh), Image.Resampling.LANCZOS)
            cell = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
            cell.paste(blob, ((CELL - nw) // 2, (CELL - nh) // 2), blob)
            out.paste(cell, (i * CELL, 0))
        out.save(path)
        written += 1
    return written


def main() -> None:
    n = 0
    for stem in stems():
        w = process_stem(stem)
        print(f"{stem:20} packed {w} files")
        n += w
    print("total", n)


if __name__ == "__main__":
    main()
