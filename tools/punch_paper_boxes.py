"""Punch leftover H3 key-paper (wine frames + dark-magenta scraps).

Restores relative scale: one scale per character stem so N/S compact poses
do not inflate to the same cell-fill as long E/W poses.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ART = Path(__file__).resolve().parents[1] / "art_src" / "topdown_v1"
CELL = 256
FILL = 0.90
STEMS = (
    "shambler",
    "runner",
    "crawler",
    "necro_node",
    "brute",
    "armored_dead",
    "mutant_enforcer",
    "zombie_colossus",
    "praetorian",
    "psychoid",
    "biomorph",
)


def paper_mask(arr: np.ndarray) -> np.ndarray:
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]
    vis = a > 8
    # Pre-punch brute frames: mean ~ (50, 0, 30). Runner wash: ~ (22, 0, 14).
    wine = vis & (g < 10) & (r > 8) & (r < 140) & (b > 2) & (b < 90) & (r > g + 8)
    rose = vis & (r > 140) & (g < 80) & (b > 70) & (r > g + 45)
    hot = vis & (r > 170) & (b > 140) & (g < 95)
    return wine | rose | hot


def smear_mask(arr: np.ndarray) -> np.ndarray:
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]
    vis = a > 8
    # Mid wine/magenta blobs that touch the silhouette. Do NOT use on brute
    # (skirt is this hue). Distinct from mutant red armor (low blue).
    return vis & (r > 70) & (g < 40) & (b > 40) & (r > g + 40) & (b > g + 15) & (b * 10 > r * 4)


def islands(mask: np.ndarray):
    h, w = mask.shape
    seen = np.zeros_like(mask)
    out = []
    ys, xs = np.where(mask)
    for y, x in zip(ys, xs):
        if seen[y, x]:
            continue
        stack = [(int(y), int(x))]
        pix = []
        seen[y, x] = True
        while stack:
            cy, cx = stack.pop()
            pix.append((cy, cx))
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        out.append(pix)
    return out


def punch_alpha(cell: Image.Image) -> Image.Image:
    arr = np.array(cell.convert("RGBA"))
    mask = paper_mask(arr)
    if mask.any():
        dil = Image.fromarray((mask.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    alpha = arr[:, :, 3]
    vis = alpha > 12
    if vis.any():
        comps = islands(vis)
        thresh = max(80, int(vis.size * 0.008))
        keep = [c for c in comps if len(c) >= thresh]
        if not keep and comps:
            keep = [max(comps, key=len)]
        keep_set = {p for c in keep for p in c}
        for y in range(arr.shape[0]):
            for x in range(arr.shape[1]):
                if (y, x) not in keep_set:
                    arr[y, x, 3] = 0
    return Image.fromarray(arr)


def content_side(im: Image.Image) -> int:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 12)
    if len(xs) < 30:
        return 0
    return max(int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1))


def place_scaled(im: Image.Image, scale: float) -> Image.Image:
    arr = np.array(im)
    ys, xs = np.where(arr[:, :, 3] > 12)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if len(xs) < 30:
        return canvas
    pad = 4
    x0, y0 = max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad)
    x1, y1 = min(arr.shape[1], int(xs.max()) + 1 + pad), min(arr.shape[0], int(ys.max()) + 1 + pad)
    cut = im.crop((x0, y0, x1, y1))
    nw = max(1, int(round(cut.width * scale)))
    nh = max(1, int(round(cut.height * scale)))
    if nw > CELL - 2 or nh > CELL - 2:
        fit = min((CELL - 2) / nw, (CELL - 2) / nh)
        nw, nh = max(1, int(round(nw * fit))), max(1, int(round(nh * fit)))
    cut = cut.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(cut, ((CELL - nw) // 2, (CELL - nh) // 2), cut)
    return canvas


def split_strip(path: Path) -> list[Image.Image]:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    if w < h * 1.5:
        return [im]
    nf = max(1, round(w / h))
    cw = w // nf
    return [im.crop((i * cw, 0, (i + 1) * cw, h)) for i in range(nf)]


def write_strip(path: Path, cells: list[Image.Image]) -> None:
    strip = Image.new("RGBA", (CELL * len(cells), CELL), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        strip.paste(c, (i * CELL, 0), c)
    strip.save(path)


def stem_files(stem: str) -> list[Path]:
    files = []
    for kind in ("walk", "idle", "attack"):
        files.extend(sorted(ART.glob(f"{stem}_{kind}*.png")))
    # unique
    seen = set()
    out = []
    for p in files:
        if p.name not in seen:
            seen.add(p.name)
            out.append(p)
    return out


def still_files(stem: str) -> list[Path]:
    names = [f"{stem}.png"] + [
        f"{stem}_{d}.png" for d in ("n", "s", "e", "w", "ne", "nw", "se", "sw")
    ]
    return [ART / n for n in names if (ART / n).exists()]


def main() -> None:
    for stem in STEMS:
        paths = stem_files(stem)
        punched: dict[Path, list[Image.Image]] = {}
        sides: dict[Path, list[int]] = {}
        for p in paths:
            cells = [punch_alpha(c) for c in split_strip(p)]
            punched[p] = cells
            sides[p] = [content_side(c) for c in cells]
        # Lift tiny glitch frames up to that strip's median (crawler N frame 0).
        for p, cells in punched.items():
            med = float(np.median([s for s in sides[p] if s > 0]) or 0)
            if med < 20:
                continue
            for i, (cell, side) in enumerate(zip(cells, sides[p])):
                if 0 < side < med * 0.70:
                    factor = med / side
                    w = max(1, int(round(cell.width * factor)))
                    h = max(1, int(round(cell.height * factor)))
                    cells[i] = cell.resize((w, h), Image.Resampling.LANCZOS)
                    sides[p][i] = content_side(cells[i])
        all_sides = [s for ss in sides.values() for s in ss if s > 0]
        stem_max = max(all_sides) if all_sides else CELL
        scale = (CELL * FILL) / max(1, stem_max)
        print(f"{stem}: files={len(paths)} stem_max={stem_max} scale={scale:.3f}")
        for p, cells in punched.items():
            write_strip(p, [place_scaled(c, scale) for c in cells])
            print("  ok", p.name)
        # Directional stills are fallbacks only — punch paper, keep stem scale.
        for p in still_files(stem):
            cells = [punch_alpha(c) for c in split_strip(p)]
            write_strip(p, [place_scaled(c, scale) for c in cells])
            print("  still", p.name)
    # Second pass: smear-only on xeno-like sheets. No island drop (brute-safe).
    for stem in ("praetorian", "biomorph", "zombie_colossus"):
        for p in stem_files(stem) + still_files(stem):
            cells = split_strip(p)
            out = []
            hit = 0
            for c in cells:
                arr = np.array(c.convert("RGBA"))
                m = smear_mask(arr)
                hit += int(m.sum())
                if m.any():
                    arr[m, 3] = 0
                out.append(Image.fromarray(arr))
            write_strip(p, out)
            print("  smear", p.name, hit)


if __name__ == "__main__":
    main()
