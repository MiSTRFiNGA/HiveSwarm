"""Praetorian 8-dir walk/attack, lime punch, cloned-walk rebuild from unique stills."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ART = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
IMG = Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C%3A%5CWINDOWS%5Csystem32\01a017c0-ef3d-7b22-a247-43852703d5a3\images")
CELL = 256
DIRS = ("e", "se", "s", "sw", "w", "nw", "n", "ne")
STEMS = (
    "praetorian", "shambler", "slime", "runner", "node_spawn", "crawler", "necro_node",
    "brute", "cyber_mutant", "armored_dead", "mutant_enforcer", "zombie_colossus",
    "rotter", "psychoid", "biomorph",
)


def punch_lime(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    a = arr[:, :, 3]
    vis = a > 8
    lime = vis & (g > 145) & (g > r + 32) & (g > b + 32)
    arr[lime, 3] = 0
    if lime.any():
        dil = Image.fromarray((lime.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    # drop tiny leftover islands
    vis2 = arr[:, :, 3] > 12
    h, w = vis2.shape
    seen = np.zeros_like(vis2)
    ys, xs = np.where(vis2)
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
                if 0 <= ny < h and 0 <= nx < w and vis2[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        if len(pix) < 70:
            for py, px in pix:
                arr[py, px, 3] = 0
    return Image.fromarray(arr)


def punch_dark(im: Image.Image, t: int = 16) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    mask = (r < t) & (g < t) & (b < t)
    arr[mask, 3] = 0
    return Image.fromarray(arr)


def content_bbox(im: Image.Image):
    a = np.array(im.convert("RGBA"))
    ys, xs = np.where(a[:, :, 3] > 12)
    if len(xs) < 8:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def center_fill(im: Image.Image, fill: float = 0.90) -> Image.Image:
    im = punch_lime(punch_dark(im))
    box = content_bbox(im)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if not box:
        return canvas
    cut = im.crop(box)
    side = max(cut.size)
    t = int(CELL * fill)
    sc = t / max(1, side)
    nw, nh = max(1, int(round(cut.width * sc))), max(1, int(round(cut.height * sc)))
    cut = cut.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(cut, ((CELL - nw) // 2, (CELL - nh) // 2), cut)
    return canvas


def write_strip(path: Path, cells: list[Image.Image]) -> None:
    cells = [c if c.size == (CELL, CELL) else center_fill(c) for c in cells]
    strip = Image.new("RGBA", (CELL * len(cells), CELL), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        strip.paste(c, (i * CELL, 0), c)
    strip.save(path)


def flip_h(im: Image.Image) -> Image.Image:
    return im.convert("RGBA").transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def cell_from(name) -> Image.Image:
    if isinstance(name, Image.Image):
        return center_fill(name)
    p = IMG / name if str(name).endswith(".jpg") else ART / name
    return center_fill(Image.open(p))


def install_praetorian() -> None:
    s0 = cell_from("praetorian.png")
    s1 = cell_from("21.jpg")
    s2 = cell_from("19.jpg")
    s3 = cell_from("22.jpg")
    walk_s = [s0, s1, s2, s3]

    e0 = cell_from("praetorian_e.png")
    e1 = cell_from("20.jpg")
    e2 = cell_from("25.jpg")
    walk_e = [e0, e1, e2, e0]
    walk_w = [flip_h(c) for c in walk_e]

    n0 = cell_from("17.jpg")
    walk_n = [n0, n0, n0, n0]

    se = cell_from("praetorian_se.png")
    sw = cell_from("praetorian_sw.png")
    walk_se = [se, se, se, se]
    walk_sw = [sw, sw, sw, sw]
    walk_ne = [flip_h(sw)] * 4
    walk_nw = [flip_h(se)] * 4

    walks = {
        "s": walk_s, "e": walk_e, "w": walk_w, "n": walk_n,
        "se": walk_se, "sw": walk_sw, "ne": walk_ne, "nw": walk_nw,
    }
    for d, frames in walks.items():
        write_strip(ART / f"praetorian_walk_{d}.png", frames)
        write_strip(ART / f"praetorian_idle_{d}.png", [frames[0]] * 4)
        frames[0].save(ART / f"praetorian_{d}.png")
    write_strip(ART / "praetorian_walk.png", walk_s)
    write_strip(ART / "praetorian_idle.png", [s0] * 4)
    s0.save(ART / "praetorian.png")

    atk_s = [s0, cell_from("18.jpg"), cell_from("23.jpg"), s0]
    atk_e = [e0, cell_from("24.jpg"), cell_from("26.jpg"), e0]
    atk_w = [flip_h(c) for c in atk_e]
    atks = {
        "s": atk_s, "e": atk_e, "w": atk_w, "n": [n0, n0, n0, n0],
        "se": atk_e, "ne": atk_e, "sw": atk_w, "nw": atk_w,
    }
    for d, frames in atks.items():
        write_strip(ART / f"praetorian_attack_{d}.png", frames)
    write_strip(ART / "praetorian_attack.png", atk_s)
    print("praetorian walk/attack 8-dir written")


def punch_all() -> int:
    n = 0
    for stem in STEMS:
        for p in ART.glob(stem + "*.png"):
            if "skel" in p.name or "hero" in p.name:
                continue
            im = Image.open(p).convert("RGBA")
            out = punch_lime(im)
            if np.array(out)[..., 3].sum() != np.array(im)[..., 3].sum():
                out.save(p)
                n += 1
    print("punched", n, "files")
    return n


def rebuild_cloned_walks() -> None:
    """If all walk dirs are identical, stamp unique stills into walk/idle so facing at least changes."""
    import hashlib
    for stem in STEMS:
        if stem == "praetorian":
            continue
        walks = [ART / f"{stem}_walk_{d}.png" for d in DIRS]
        if not all(p.exists() for p in walks):
            continue
        hashes = {hashlib.md5(p.read_bytes()).hexdigest() for p in walks}
        if len(hashes) > 1:
            continue
        print("rebuild cloned walk", stem)
        for d in DIRS:
            still = ART / f"{stem}_{d}.png"
            if not still.exists():
                continue
            cell = center_fill(Image.open(still))
            write_strip(ART / f"{stem}_walk_{d}.png", [cell] * 4)
            write_strip(ART / f"{stem}_idle_{d}.png", [cell] * 4)


def main() -> None:
    install_praetorian()
    punch_all()
    rebuild_cloned_walks()
    print("0.6.19 art done")


if __name__ == "__main__":
    main()
