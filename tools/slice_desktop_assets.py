"""Slice Desktop HiveSwarm_sprite_edit_pack Assets into engine-ready PNGs."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

DESK = Path(r"C:\Users\MiSTRFiNGA\Desktop\HiveSwarm_sprite_edit_pack\Assets")
DST = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
DBG = Path(r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_cast_import")
DBG.mkdir(parents=True, exist_ok=True)
DIRS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]


def is_paper(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn < 22 and mn > 70) or (r < 24 and g < 24 and b < 24)


def key_bg(im: Image.Image, mode="checker") -> Image.Image:
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    if mode == "green":
        for y in range(h):
            for x in range(w):
                r, g, b, a = pix[x, y]
                if g > 140 and g > r + 40 and g > b + 40:
                    pix[x, y] = (0, 0, 0, 0)
        return im
    if mode == "black":
        for y in range(h):
            for x in range(w):
                r, g, b, a = pix[x, y]
                if r < 28 and g < 28 and b < 28:
                    pix[x, y] = (0, 0, 0, 0)
                # grey panel / HUD chrome around the maw
                elif mx := max(r, g, b):
                    if mx - min(r, g, b) < 16 and 40 < mx < 160:
                        pix[x, y] = (0, 0, 0, 0)
        return im
    # checker: flood from the edges so grid paper dies, creature greys stay
    seen = [[False] * w for _ in range(h)]
    stack = []
    for x in range(w):
        stack.append((x, 0))
        stack.append((x, h - 1))
    for y in range(h):
        stack.append((0, y))
        stack.append((w - 1, y))
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y][x]:
            continue
        seen[y][x] = True
        r, g, b, a = pix[x, y]
        if not is_paper(r, g, b):
            continue
        pix[x, y] = (0, 0, 0, 0)
        stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    return im


def crop_content(im: Image.Image, pad=6) -> Image.Image:
    bb = im.getchannel("A").point(lambda p: 255 if p >= 16 else 0).getbbox()
    if not bb:
        return im
    x0, y0, x1, y1 = bb
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def fit_square(im: Image.Image, size=256) -> Image.Image:
    im = crop_content(im)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    scale = min((size - 12) / im.width, (size - 12) / im.height)
    nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(im, ((size - nw) // 2, (size - nh) // 2), im)
    return canvas


def hstrip(frames, size=256) -> Image.Image:
    out = Image.new("RGBA", (size * len(frames), size), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(fit_square(f, size), (i * size, 0), fit_square(f, size))
    return out


def grid_cells(im: Image.Image, cols, rows, title_h, caption_h, pad=10):
    w, h = im.size
    body_h = h - title_h
    cw, ch = w / cols, body_h / rows
    cells = []
    for r in range(rows):
        for c in range(cols):
            x0 = int(c * cw) + pad
            y0 = int(title_h + r * ch + caption_h) + pad
            x1 = int((c + 1) * cw) - pad
            y1 = int(title_h + (r + 1) * ch) - pad
            cells.append(im.crop((x0, y0, x1, y1)))
    return cells


def write_stem(stem: str, idle: Image.Image, walk: Image.Image, flip_w=False):
    DST.mkdir(parents=True, exist_ok=True)
    idle.save(DST / f"{stem}.png")
    walk.save(DST / f"{stem}_walk.png")
    e = idle
    wimg = idle.transpose(Image.FLIP_LEFT_RIGHT) if flip_w else idle
    mapping = {
        "e": e, "se": e, "ne": e,
        "s": idle, "n": idle,
        "w": wimg, "sw": wimg, "nw": wimg,
    }
    walk_e = walk
    walk_w = walk.transpose(Image.FLIP_LEFT_RIGHT) if flip_w else walk
    walk_map = {
        "e": walk_e, "se": walk_e, "ne": walk_e,
        "s": walk, "n": walk,
        "w": walk_w, "sw": walk_w, "nw": walk_w,
    }
    for d in DIRS:
        mapping[d].save(DST / f"{stem}_{d}.png")
        walk_map[d].save(DST / f"{stem}_walk_{d}.png")
    print("wrote", stem)


def cells_from_boxes(im, col_ys, n_cols, inset=8):
    """col_ys = list of (y0,y1) art rows. Split each row into n_cols."""
    w = im.width
    cw = w / n_cols
    out = []
    for y0, y1 in col_ys:
        for c in range(n_cols):
            box = (int(c * cw) + inset, y0 + 2, int((c + 1) * cw) - inset, y1 - 2)
            out.append(im.crop(box))
    return out


# ---- 1. Psychoid: 2x4 top-down (art rows measured from brightness) ----
psy = Image.open(DESK / "Beastiary" / "Gemini_Generated_Image_.png")
psy_cells = [key_bg(c, "checker") for c in cells_from_boxes(psy, [(120, 425), (555, 825)], 4, 14)]
for i, c in enumerate(psy_cells, 1):
    crop_content(c).save(DBG / f"psychoid_cell_{i:02d}.png")
psy_idle = fit_square(psy_cells[0])
psy_walk = hstrip([psy_cells[0], psy_cells[1], psy_cells[2], psy_cells[6]])
write_stem("psychoid", psy_idle, psy_walk, flip_w=False)

# ---- 3. Biomorph: 4x4 side-view, walk 1-4, idle 5 ----
bio = Image.open(DESK / "Beastiary" / "Gemini_Generated_Image_ (1).png")
bio_cells = [key_bg(c, "checker") for c in cells_from_boxes(
    bio, [(100, 265), (305, 455), (505, 655), (690, 855)], 4, 12)]
for i, c in enumerate(bio_cells, 1):
    crop_content(c).save(DBG / f"biomorph_cell_{i:02d}.png")
bio_idle = fit_square(bio_cells[4])
bio_walk = hstrip(bio_cells[0:4])
write_stem("biomorph", bio_idle, bio_walk, flip_w=True)

# ---- 4. Subterra-Maw: scan row (skip captions by taking the upper 72% of each cell) ----
maw = Image.open(DESK / "Beastiary" / "Gemini_Generated_Image_ (5).png")
maw_rows = [(155, 305), (400, 545), (620, 755)]  # emerge / scan / strike, caption sits below
maw_frames = []
for y0, y1 in maw_rows:
    row = maw.crop((8, y0, maw.width - 8, y1))
    cw = row.width / 5
    for i in range(5):
        cell = row.crop((int(i * cw) + 6, 2, int((i + 1) * cw) - 6, row.height - 2))
        cell = cell.crop((int(cell.width * 0.18), 0, cell.width, cell.height))
        cell = key_bg(cell, "black")
        maw_frames.append(cell)
        crop_content(cell).save(DBG / f"maw_{len(maw_frames):02d}.png")
maw_idle = fit_square(maw_frames[5])
maw_walk = hstrip(maw_frames[5:10])
write_stem("subterra_maw", maw_idle, maw_walk, flip_w=False)

print("sliced psychoid, biomorph, subterra_maw ->", DST)
