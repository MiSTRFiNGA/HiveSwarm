"""Re-import Hive Slime from the owner sheet and punch lime splash + label text."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ART = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
SRC = Path(r"C:\Users\MiSTRFiNGA\Desktop\HiveSwarmGROK\Lovecraftian Slime.png")
CELL = 256
DIRS = ("e", "se", "s", "sw", "w", "nw", "n", "ne")
COLS, ROWS = 10, 2


def punch_lime_and_labels(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    lime = (g > 110) & (g > r + 18) & (g > b + 18)
    # Sheet titles are dark/mid green on the lime paper.
    label = (g > r + 12) & (g > b + 12) & (r < 90) & (b < 90) & (g < 200)
    # Thin washed halo that survives a hard lime key (high G, still greener than the body).
    halo = (g > 90) & (g > r + 12) & (g > b + 8) & (r < 160)
    mask = lime | label | halo
    arr[mask, 3] = 0
    if mask.any():
        dil = Image.fromarray((mask.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    return Image.fromarray(arr)


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


def drop_splash(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    vis = arr[:, :, 3] > 12
    if not vis.any():
        return Image.fromarray(arr)
    comps = islands(vis)
    thresh = max(90, int(vis.sum() * 0.04))
    keep = [c for c in comps if len(c) >= thresh]
    if not keep and comps:
        keep = [max(comps, key=len)]
    keep_set = {p for c in keep for p in c}
    h, w = vis.shape
    for y in range(h):
        for x in range(w):
            if (y, x) not in keep_set:
                arr[y, x, 3] = 0
    return Image.fromarray(arr)


def content_bbox(im: Image.Image):
    a = np.array(im.convert("RGBA"))
    ys, xs = np.where(a[:, :, 3] > 12)
    if len(xs) < 8:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def center_fill(im: Image.Image, fill: float = 0.88) -> Image.Image:
    box = content_bbox(im)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if not box:
        return canvas
    cut = im.convert("RGBA").crop(box)
    side = max(cut.size)
    t = int(CELL * fill)
    sc = t / max(1, side)
    nw, nh = max(1, int(round(cut.width * sc))), max(1, int(round(cut.height * sc)))
    cut = cut.resize((nw, nh), Image.Resampling.NEAREST)
    canvas.paste(cut, ((CELL - nw) // 2, (CELL - nh) // 2), cut)
    return canvas


def write_strip(path: Path, cells: list[Image.Image]) -> None:
    cells = [c.convert("RGBA") for c in cells]
    strip = Image.new("RGBA", (CELL * len(cells), CELL), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        strip.paste(c, (i * CELL, 0), c)
    path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(path)


def copy_all_dirs(cells: list[Image.Image], stem: str, kind: str) -> None:
    write_strip(ART / f"{stem}_{kind}.png", cells)
    for d in DIRS:
        write_strip(ART / f"{stem}_{kind}_{d}.png", cells)


def green_leak_frac(im: Image.Image) -> float:
    arr = np.array(im.convert("RGBA"))
    a = arr[:, :, 3] > 12
    if not a.any():
        return 0.0
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    leak = a & (g > r + 18) & (g > b + 18)
    return float(leak.sum() / a.sum())


def blob_boxes(im: Image.Image):
    arr = np.array(im.convert("RGBA"))
    comps = islands(arr[:, :, 3] > 12)
    h = arr.shape[0]
    items = []
    for c in comps:
        if len(c) < 200:
            continue
        ys = [p[0] for p in c]
        xs = [p[1] for p in c]
        x0, y0, x1, y1 = min(xs), min(ys), max(xs) + 1, max(ys) + 1
        cy = (y0 + y1) // 2
        items.append((x0, y0, x1, y1, cy, len(c)))
    items.sort(key=lambda t: (0 if t[4] < h / 2 else 1, t[0]))
    return items, h


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing source {SRC}")
    raw = Image.open(SRC)
    punched = punch_lime_and_labels(raw)
    boxes, h = blob_boxes(punched)
    # Bottom row of the owner sheet is clipped by the PNG edge — those halves are the
    # "splash" around the character. Keep only complete top-row bodies.
    top = [b for b in boxes if b[4] < h / 2 and b[3] < h - 2]
    if len(top) < 6:
        raise SystemExit(f"expected >=6 complete slime poses, got {len(top)}")

    def cell(box) -> Image.Image:
        pad = 2
        x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
        crop = punched.crop((max(0, x0), max(0, y0), x1, y1))
        return center_fill(drop_splash(crop))

    poses = [cell(b) for b in top]
    idle = poses[0:2]
    walk = poses[2:5] if len(poses) >= 5 else poses[0:2]
    atk = poses[5:] if len(poses) > 5 else poses[-2:]
    while len(idle) < 2:
        idle.append(idle[-1])
    while len(walk) < 3:
        walk.append(walk[-1])
    while len(atk) < 3:
        atk.append(atk[-1])

    copy_all_dirs(idle, "slime", "idle")
    copy_all_dirs(walk, "slime", "walk")
    copy_all_dirs(atk, "slime", "attack")
    write_strip(ART / "slime.png", [idle[0]])

    leaks = {
        "idle": green_leak_frac(Image.open(ART / "slime_idle.png")),
        "walk": green_leak_frac(Image.open(ART / "slime_walk.png")),
        "attack": green_leak_frac(Image.open(ART / "slime_attack.png")),
        "base": green_leak_frac(Image.open(ART / "slime.png")),
    }
    print("slime cleaned", {k: round(v, 4) for k, v in leaks.items()})
    if any(v > 0.01 for v in leaks.values()):
        raise SystemExit("slime still has green splash")


if __name__ == "__main__":
    main()
