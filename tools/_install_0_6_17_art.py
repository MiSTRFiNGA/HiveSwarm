"""Install 0.6.17 grounds, props, rotter 8-dir, colossus L/R, biomorph feet, slime west."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ART = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
STAGES = Path(r"D:\Dev\HiveSwarm\art_src\stages")
OBS = Path(r"D:\Dev\HiveSwarm\art_src\obstacles")
IMG = Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C:\WINDOWS\system32\01a017c0-ef3d-7b22-a247-43852703d5a3\images".replace("C:\\WINDOWS", "C:\\WINDOWS"))
# session folder uses URL-encoded path
IMG = Path(r"C:\Users\MiSTRFiNGA\.grok\sessions\C%3A%5CWINDOWS%5Csystem32\01a017c0-ef3d-7b22-a247-43852703d5a3\images")
CELL = 256
DIRS = ("e", "se", "s", "sw", "w", "nw", "n", "ne")


def punch_dark(im: Image.Image, t: int = 22) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]
    mask = (r.astype(np.int16) < t) & (g.astype(np.int16) < t) & (b.astype(np.int16) < t)
    arr[mask, 3] = 0
    if mask.any():
        dil = Image.fromarray((mask.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    return Image.fromarray(arr)


def punch_lime(im: Image.Image) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)
    mask = (g > 110) & (g > r + 18) & (g > b + 18)
    arr[mask, 3] = 0
    if mask.any():
        dil = Image.fromarray((mask.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    return Image.fromarray(arr)


def content_bbox(im: Image.Image):
    a = np.array(im.convert("RGBA"))
    ys, xs = np.where(a[:, :, 3] > 12)
    if len(xs) < 8:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def center_fill(im: Image.Image, fill: float = 0.90) -> Image.Image:
    box = content_bbox(im)
    canvas = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    if not box:
        return canvas
    cut = im.convert("RGBA").crop(box)
    side = max(cut.size)
    t = int(CELL * fill)
    sc = t / max(1, side)
    nw, nh = max(1, int(round(cut.width * sc))), max(1, int(round(cut.height * sc)))
    cut = cut.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(cut, ((CELL - nw) // 2, (CELL - nh) // 2), cut)
    return canvas


def write_strip(path: Path, cells: list[Image.Image]) -> None:
    cells = [c.convert("RGBA") if c.size == (CELL, CELL) else center_fill(c) for c in cells]
    strip = Image.new("RGBA", (CELL * len(cells), CELL), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        strip.paste(c, (i * CELL, 0), c)
    path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(path)


def clone_dirs(cell: Image.Image, stem: str, extras: dict[str, Image.Image] | None = None) -> None:
    extras = extras or {}
    cell = center_fill(cell)
    cell.save(ART / f"{stem}.png")
    for d in DIRS:
        im = extras.get(d, cell)
        im = center_fill(im)
        im.save(ART / f"{stem}_{d}.png")
        write_strip(ART / f"{stem}_walk_{d}.png", [im] * 4)
        write_strip(ART / f"{stem}_idle_{d}.png", [im] * 4)
        write_strip(ART / f"{stem}_attack_{d}.png", [im] * 4)
    write_strip(ART / f"{stem}_walk.png", [extras.get("s", cell)] * 4)
    write_strip(ART / f"{stem}_idle.png", [extras.get("s", cell)] * 4)
    write_strip(ART / f"{stem}_attack.png", [extras.get("s", cell)] * 4)


def make_seamless(im: Image.Image, band: int = 40) -> Image.Image:
    arr = np.array(im.convert("RGB")).astype(np.float32)
    h, w, _ = arr.shape
    band = min(band, w // 4, h // 4)
    for i in range(band):
        t = i / band
        left = arr[:, i].copy()
        right = arr[:, w - band + i].copy()
        arr[:, i] = left * t + right * (1 - t)
        arr[:, w - band + i] = right * (1 - t) + left * t
        top = arr[i].copy()
        bot = arr[h - band + i].copy()
        arr[i] = top * t + bot * (1 - t)
        arr[h - band + i] = bot * (1 - t) + top * t
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def split_props(path: Path, names: list[str], dest_prefix: str) -> list[Path]:
    im = punch_lime(Image.open(path))
    arr = np.array(im)
    vis = arr[:, :, 3] > 12
    # vertical projection to find blobs
    cols = vis.any(axis=0)
    spans = []
    i = 0
    n = cols.size
    while i < n:
        if not cols[i]:
            i += 1
            continue
        j = i
        while j < n and cols[j]:
            j += 1
        if j - i > 20:
            spans.append((i, j))
        i = j
    out = []
    for k, name in enumerate(names):
        if k >= len(spans):
            break
        x0, x1 = spans[k]
        crop = punch_lime(im.crop((x0, 0, x1, im.height)))
        box = content_bbox(crop)
        if not box:
            continue
        cut = crop.crop(box)
        canvas = Image.new("RGBA", (384, 384), (0, 0, 0, 0))
        sc = min(340 / max(1, cut.width), 340 / max(1, cut.height))
        nw, nh = max(1, int(cut.width * sc)), max(1, int(cut.height * sc))
        cut = cut.resize((nw, nh), Image.Resampling.LANCZOS)
        canvas.paste(cut, ((384 - nw) // 2, (384 - nh) // 2), cut)
        dest = OBS / f"{dest_prefix}_{name}.png"
        canvas.save(dest)
        out.append(dest)
        print("prop", dest.name, canvas.size)
    return out


def punch_existing_obstacle(name: str) -> None:
    p = OBS / f"{name}.png"
    if not p.exists():
        return
    im = punch_lime(Image.open(p))
    im.save(p)
    print("punched", p.name)


def flip_h(im: Image.Image) -> Image.Image:
    return im.convert("RGBA").transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def install_grounds() -> None:
    mapping = {
        "outskirts": "3.jpg",
        "sewers": "4.jpg",
        "downtown": "2.jpg",
        "highway": "1.jpg",
        "hivecore": "5.jpg",
    }
    STAGES.mkdir(parents=True, exist_ok=True)
    for name, fn in mapping.items():
        src = IMG / fn
        im = Image.open(src).convert("RGB").resize((1024, 1024), Image.Resampling.LANCZOS)
        im = make_seamless(im, 48)
        dest = STAGES / f"{name}_tile.png"
        im.save(dest)
        print("ground", dest.name, im.size)


def install_props() -> None:
    OBS.mkdir(parents=True, exist_ok=True)
    split_props(IMG / "7.jpg", ["barrel", "crate", "pipe", "manhole"], "sewers")
    split_props(IMG / "9.jpg", ["barrel", "crate", "drum", "box"], "props")
    for name in ("outskirts", "sewers", "downtown", "highway", "hivecore"):
        punch_existing_obstacle(name)


def install_rotter_and_colossus() -> None:
    # Snapshot current colossus L/R (the leftover rotting zombie) into rotter.
    for kind in ("", "_walk", "_idle", "_attack"):
        for d in ("e", "w"):
            src = ART / f"zombie_colossus{kind}_{d}.png" if kind else ART / f"zombie_colossus_{d}.png"
            if not src.exists():
                src = ART / f"zombie_colossus{kind}_{d}.png"
            if src.exists():
                dest = ART / f"rotter{kind}_{d}.png" if kind else ART / f"rotter_{d}.png"
                shutil.copy2(src, dest)

    extras = {
        "e": punch_dark(Image.open(ART / "rotter_e.png")),
        "w": punch_dark(Image.open(ART / "rotter_w.png")),
        "s": punch_dark(Image.open(IMG / "6.jpg")),
        "n": punch_dark(Image.open(IMG / "8.jpg")),
        "se": punch_dark(Image.open(IMG / "15.jpg")),
        "sw": punch_dark(Image.open(IMG / "14.jpg")),
        "ne": punch_dark(Image.open(IMG / "16.jpg")),
        "nw": punch_dark(Image.open(IMG / "13.jpg")),
    }
    clone_dirs(extras["s"], "rotter", extras)

    colo_e = punch_dark(Image.open(IMG / "10.jpg"))
    colo_w = punch_dark(Image.open(IMG / "11.jpg"))
    colo_e = center_fill(colo_e)
    colo_w = center_fill(colo_w)
    colo_e.save(ART / "zombie_colossus_e.png")
    colo_w.save(ART / "zombie_colossus_w.png")
    write_strip(ART / "zombie_colossus_walk_e.png", [colo_e] * 4)
    write_strip(ART / "zombie_colossus_walk_w.png", [colo_w] * 4)
    write_strip(ART / "zombie_colossus_idle_e.png", [colo_e] * 4)
    write_strip(ART / "zombie_colossus_idle_w.png", [colo_w] * 4)
    write_strip(ART / "zombie_colossus_attack_e.png", [colo_e] * 4)
    write_strip(ART / "zombie_colossus_attack_w.png", [colo_w] * 4)
    print("rotter 8-dir + colossus E/W written")


def install_biomorph_feet() -> None:
    body = punch_dark(Image.open(IMG / "12.jpg"))
    extras = {d: body for d in DIRS}
    extras["w"] = flip_h(body)
    extras["sw"] = flip_h(body)
    extras["nw"] = flip_h(body)
    clone_dirs(body, "biomorph", extras)
    print("biomorph feet installed")


def install_slime_west() -> None:
    for kind in ("walk", "idle", "attack"):
        src = ART / f"slime_{kind}.png"
        if not src.exists():
            continue
        im = Image.open(src).convert("RGBA")
        flipped = flip_h(im)
        for d in ("w", "sw", "nw"):
            dest = ART / f"slime_{kind}_{d}.png"
            flipped.save(dest)
            print("slime", dest.name)
    # stills
    base = Image.open(ART / "slime.png").convert("RGBA")
    flip_h(base).save(ART / "slime_w.png")
    print("slime west stills written")


def main() -> None:
    if not IMG.exists():
        raise SystemExit(f"missing session images {IMG}")
    install_grounds()
    install_props()
    install_rotter_and_colossus()
    install_biomorph_feet()
    install_slime_west()
    print("ALL ART INSTALLED")


if __name__ == "__main__":
    main()
