"""Punch leftover key-paper and maroon frames. Do not flood through character."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ART = Path(__file__).resolve().parents[1] / "art_src" / "topdown_v1"
CELL = 256
FILL = 0.90
STEMS = (
    "shambler", "runner", "crawler", "necro_node", "brute", "armored_dead",
    "mutant_enforcer", "zombie_colossus", "praetorian", "psychoid", "biomorph",
)


def paper_mask(arr: np.ndarray) -> np.ndarray:
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]
    vis = a > 8
    # Brute-style card frame + leftover wine blobs: near-zero green, wine/maroon.
    maroon = vis & (g < 22) & (r > 30) & (b > 20) & (r > g + 15)
    # Bright leftover paper (H3 crushed #FF00FF → rose / hot pink / checker).
    rose = vis & (r > 140) & (g < 80) & (b > 70) & (r > g + 45)
    hot = vis & (r > 170) & (b > 140) & (g < 95)
    return maroon | rose | hot


def punch_cell(cell: Image.Image) -> Image.Image:
    arr = np.array(cell.convert("RGBA"))
    mask = paper_mask(arr)
    if mask.any():
        dil = Image.fromarray((mask.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    alpha = arr[:, :, 3]
    vis = alpha > 12
    if vis.any():
        h, w = vis.shape
        seen = np.zeros_like(vis)
        comps = []
        for y, x in zip(*np.where(vis)):
            if seen[y, x]:
                continue
            stack = [(int(y), int(x))]
            pix = []
            seen[y, x] = True
            while stack:
                cy, cx = stack.pop()
                pix.append((cy, cx))
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and vis[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            comps.append(pix)
        thresh = max(80, int(vis.size * 0.008))
        keep = [c for c in comps if len(c) >= thresh]
        if not keep and comps:
            keep = [max(comps, key=len)]
        keep_set = {p for c in keep for p in c}
        for y in range(h):
            for x in range(w):
                if (y, x) not in keep_set:
                    arr[y, x, 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 12)
    if len(xs) < 30:
        return Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    pad = 6
    x0, y0 = max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad)
    x1, y1 = min(arr.shape[1], int(xs.max()) + 1 + pad), min(arr.shape[0], int(ys.max()) + 1 + pad)
    cut = Image.fromarray(arr).crop((x0, y0, x1, y1))
    side = max(cut.width, cut.height)
    target = max(8, int(CELL * FILL))
    scale = target / side
    nw, nh = max(1, int(round(cut.width * scale))), max(1, int(round(cut.height * scale)))
    cut = cut.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    canvas.paste(cut, ((CELL - nw) // 2, (CELL - nh) // 2), cut)
    return canvas


def process_strip(path: Path) -> None:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    if w < h * 1.5:
        cells = [im]
    else:
        nf = max(1, round(w / h))
        cw = w // nf
        cells = [im.crop((i * cw, 0, (i + 1) * cw, h)) for i in range(nf)]
    out = [punch_cell(c) for c in cells]
    strip = Image.new("RGBA", (CELL * len(out), CELL), (0, 0, 0, 0))
    for i, c in enumerate(out):
        strip.paste(c, (i * CELL, 0), c)
    strip.save(path)


def main() -> None:
    files = []
    for stem in STEMS:
        files.extend(sorted(ART.glob(f"{stem}_walk*.png")))
        files.extend(sorted(ART.glob(f"{stem}_idle*.png")))
        files.extend(sorted(ART.glob(f"{stem}_attack*.png")))
    print("processing", len(files))
    for p in files:
        process_strip(p)
        print("ok", p.name)


if __name__ == "__main__":
    main()
