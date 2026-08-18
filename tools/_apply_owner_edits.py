"""Apply owner 0.6.14 sprite notes. Does not overwrite shambler/psychoid/runner user FORGE paint."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ART = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
SRC = Path(r"C:\Users\MiSTRFiNGA\Desktop\HiveSwarmGROK")
CELL = 256
DIRS = ("e", "se", "s", "sw", "w", "nw", "n", "ne")


def split_strip(im: Image.Image) -> list[Image.Image]:
    im = im.convert("RGBA")
    w, h = im.size
    if w < h * 1.5:
        return [im]
    nf = max(1, round(w / h))
    cw = w // nf
    return [im.crop((i * cw, 0, (i + 1) * cw, h)) for i in range(nf)]


def write_strip(path: Path, cells: list[Image.Image]) -> None:
    cells = [c.convert("RGBA").resize((CELL, CELL), Image.Resampling.LANCZOS) if c.size != (CELL, CELL) else c.convert("RGBA") for c in cells]
    strip = Image.new("RGBA", (CELL * len(cells), CELL), (0, 0, 0, 0))
    for i, c in enumerate(cells):
        strip.paste(c, (i * CELL, 0), c)
    path.parent.mkdir(parents=True, exist_ok=True)
    strip.save(path)


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


def rotate_cell(im: Image.Image, deg: float) -> Image.Image:
    r = im.convert("RGBA").rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True)
    return center_fill(r)


def punch_chroma(im: Image.Image, mode: str) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    r, g, b, a = arr[:, :, 0].astype(np.int16), arr[:, :, 1].astype(np.int16), arr[:, :, 2].astype(np.int16), arr[:, :, 3]
    if mode == "lime":
        mask = (g > 140) & (g > r + 30) & (g > b + 30)
    elif mode == "white":
        mask = (r > 230) & (g > 230) & (b > 230)
    elif mode == "black":
        mask = (r < 18) & (g < 18) & (b < 18) & (a > 8)
    else:
        mask = np.zeros(a.shape, bool)
    arr[mask, 3] = 0
    if mask.any():
        dil = Image.fromarray((mask.astype(np.uint8) * 255)).filter(ImageFilter.MaxFilter(3))
        arr[np.array(dil) > 0, 3] = 0
    return Image.fromarray(arr)


def replace_frame0(path: Path) -> None:
    if not path.exists():
        return
    cells = split_strip(Image.open(path))
    if len(cells) < 2:
        return
    cells[0] = cells[1].copy()
    write_strip(path, [center_fill(c) for c in cells])
    print("frame0", path.name)


def copy_all_dirs(src_cells: list[Image.Image], stem: str, kind: str) -> None:
    for d in DIRS:
        write_strip(ART / f"{stem}_{kind}_{d}.png", src_cells)
    write_strip(ART / f"{stem}_{kind}.png", src_cells)


def fix_first_frames() -> None:
    for stem in ("brute", "mutant_enforcer"):
        for kind in ("walk", "idle", "attack"):
            for p in ART.glob(f"{stem}_{kind}*.png"):
                replace_frame0(p)


def fix_crawler() -> None:
    n = ART / "crawler_walk_n.png"
    e = ART / "crawler_walk_e.png"
    if n.exists() and e.exists():
        ncells = [center_fill(c, 0.90) for c in split_strip(Image.open(n))]
        write_strip(n, ncells)
        write_strip(ART / "crawler_walk_ne.png", [rotate_cell(c, 45) for c in ncells])
        write_strip(ART / "crawler_walk_nw.png", [rotate_cell(c, -45) for c in ncells])
        print("crawler N scaled + NE/NW angled")
    s = ART / "crawler_walk_s.png"
    if s.exists():
        cells = split_strip(Image.open(s))
        if len(cells) >= 4:
            # 0 compact, 1 lunge — reuse 1 mirrored as 2, 0 as 3 for a step
            cells[2] = cells[1].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            cells[3] = cells[0].transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            write_strip(s, [center_fill(c) for c in cells])
            print("crawler S walk reordered")


def fix_colossus() -> None:
    se, sw = ART / "zombie_colossus_walk_se.png", ART / "zombie_colossus_walk_sw.png"
    if se.exists() and sw.exists():
        a, b = split_strip(Image.open(se)), split_strip(Image.open(sw))
        if a and b:
            a[0], b[0] = b[0], a[0]
            write_strip(se, [center_fill(punch_chroma(c, "black")) for c in a])
            write_strip(sw, [center_fill(punch_chroma(c, "black")) for c in b])
            print("colossus SE/SW frame0 swapped")
    for p in ART.glob("zombie_colossus_*.png"):
        cells = [center_fill(punch_chroma(c, "black")) for c in split_strip(Image.open(p))]
        write_strip(p, cells)
    n = ART / "zombie_colossus_walk_n.png"
    if n.exists():
        ncells = [center_fill(c, 0.90) for c in split_strip(Image.open(n))]
        write_strip(n, ncells)
        write_strip(ART / "zombie_colossus_walk_ne.png", [rotate_cell(c, 40) for c in ncells])
        write_strip(ART / "zombie_colossus_walk_nw.png", [rotate_cell(c, -40) for c in ncells])
        print("colossus N scale + NE/NW")
    sheet = SRC / "zombie_colossus.png"
    if sheet.exists():
        im = punch_chroma(Image.open(sheet).convert("RGBA"), "black")
        w, h = im.size
        left, right = center_fill(im.crop((0, 0, w // 2, h))), center_fill(im.crop((w // 2, 0, w, h)))
        write_strip(ART / "zombie_colossus_e.png", [right])
        write_strip(ART / "zombie_colossus_w.png", [left])
        write_strip(ART / "zombie_colossus_walk_e.png", [right] * 4)
        write_strip(ART / "zombie_colossus_walk_w.png", [left] * 4)
        print("colossus L/R from owner sheet")


def necro_and_spawn() -> None:
    se = ART / "necro_node_walk_se.png"
    n = ART / "necro_node_walk_n.png"
    if se.exists():
        idle = [rotate_cell(c, -90) for c in split_strip(Image.open(se))]
        copy_all_dirs(idle, "necro_node", "idle")
        print("necro idle from SE -90")
    if n.exists():
        walk = [rotate_cell(c, 180) for c in split_strip(Image.open(n))]
        copy_all_dirs(walk, "node_spawn", "walk")
        copy_all_dirs(walk, "node_spawn", "idle")
        copy_all_dirs([walk[0]], "node_spawn", "attack")
        write_strip(ART / "node_spawn.png", [walk[0]])
        print("node_spawn from necro N +180")


def import_slime() -> None:
    p = SRC / "Lovecraftian Slime.png"
    if not p.exists():
        return
    im = punch_chroma(Image.open(p), "lime")
    w, h = im.size
    # 2 rows x 10 cells roughly
    cols, rows = 10, 2
    cw, ch = w // cols, h // rows
    idle, walk, atk = [], [], []
    for i in range(cols):
        top = center_fill(im.crop((i * cw, 0, (i + 1) * cw, ch)))
        bot = center_fill(im.crop((i * cw, ch, (i + 1) * cw, h)))
        if i < 2:
            idle.append(top)
        elif i < 5:
            walk.append(top)
        elif i < 8:
            atk.append(top)
        if i < 4:
            walk.append(bot)
    idle = (idle or walk)[:4] or [center_fill(im)]
    walk = (walk or idle)[:4]
    atk = (atk or walk)[:4]
    while len(idle) < 4:
        idle.append(idle[-1])
    while len(walk) < 4:
        walk.append(walk[-1])
    while len(atk) < 4:
        atk.append(atk[-1])
    copy_all_dirs(idle, "slime", "idle")
    copy_all_dirs(walk, "slime", "walk")
    copy_all_dirs(atk, "slime", "attack")
    write_strip(ART / "slime.png", [idle[0]])
    print("slime imported")


def import_cyber() -> None:
    p = SRC / "Cyber Mutant.png"
    if not p.exists():
        return
    im = punch_chroma(Image.open(p), "white")
    w, h = im.size
    # middle grid ~ 5x2 walk
    cells = []
    # sample a 5-wide band from the middle third
    y0, y1 = int(h * 0.28), int(h * 0.72)
    band = im.crop((int(w * 0.04), y0, int(w * 0.96), y1))
    bw, bh = band.size
    cols = 5
    cw = bw // cols
    ch = bh // 2
    for row in range(2):
        for col in range(cols):
            cells.append(center_fill(band.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))))
    walk = cells[:4] if len(cells) >= 4 else cells * 4
    idle = cells[4:8] if len(cells) >= 8 else walk
    atk = cells[-4:] if len(cells) >= 4 else walk
    copy_all_dirs(idle[:4], "cyber_mutant", "idle")
    copy_all_dirs(walk[:4], "cyber_mutant", "walk")
    copy_all_dirs(atk[:4], "cyber_mutant", "attack")
    write_strip(ART / "cyber_mutant.png", [walk[0]])
    print("cyber mutant imported")


def import_praet() -> None:
    p = SRC / "praetorian.png"
    if not p.exists():
        return
    im = punch_chroma(Image.open(p), "lime")
    w, h = im.size
    # 5 cols x 5 rows
    cols, rows = 5, 5
    cw, ch = w // cols, h // rows
    grid = []
    for row in range(rows):
        for col in range(cols):
            grid.append(center_fill(im.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))))
    idle = grid[0:4]
    walk = grid[0:4]
    atk = grid[5:9]
    copy_all_dirs(idle, "praetorian", "idle")
    copy_all_dirs(walk, "praetorian", "walk")
    copy_all_dirs(atk, "praetorian", "attack")
    write_strip(ART / "praetorian.png", [idle[0]])
    print("praetorian imported from owner sheet")


def main() -> None:
    fix_first_frames()
    fix_crawler()
    fix_colossus()
    necro_and_spawn()
    import_slime()
    import_cyber()
    import_praet()
    print("done")


if __name__ == "__main__":
    main()
