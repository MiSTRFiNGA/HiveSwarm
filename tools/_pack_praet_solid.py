"""Pack Praetorian diagonal frames. Keys only near-black BORDER, never dark armor."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
WORK = Path(r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_praet_se_2026_09_11")
ORANGE_OUT = Path(r"C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_praet_se_2026_09_11\contact")
CELL = 256
ORANGE = (255, 120, 0, 255)


def edge_key_true_black(arr: np.ndarray, max_ch: int = 10) -> np.ndarray:
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3]
    near = (rgb.max(axis=2) <= max_ch)
    seen = np.zeros((h, w), dtype=bool)
    stack = []
    for x in range(w):
        stack.append((0, x))
        stack.append((h - 1, x))
    for y in range(h):
        stack.append((y, 0))
        stack.append((y, w - 1))
    while stack:
        y, x = stack.pop()
        if y < 0 or x < 0 or y >= h or x >= w or seen[y, x]:
            continue
        if not near[y, x]:
            continue
        seen[y, x] = True
        arr[y, x, 3] = 0
        stack.extend(((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)))
    return arr


def fit_cell(im: Image.Image, ref_bbox) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    arr = edge_key_true_black(arr)
    a = arr[:, :, 3]
    ys, xs = np.where(a >= 32)
    if len(ys) == 0:
        return Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    crop = Image.fromarray(arr, "RGBA").crop((x0, y0, x1, y1))
    ref_h = max(1, ref_bbox[3] - ref_bbox[1])
    scale = ref_h / crop.size[1]
    nw = max(1, min(CELL - 8, int(round(crop.size[0] * scale))))
    nh = max(1, min(CELL - 8, int(round(crop.size[1] * scale))))
    crop = crop.resize((nw, nh), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))
    top = max(0, min(CELL - nh, ref_bbox[3] - nh))
    left = (CELL - nw) // 2
    out.paste(crop, (left, top), crop)
    return out


def ref_bbox(path: Path):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a >= 32)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def pack(frames, dest: Path) -> Image.Image:
    sheet = Image.new("RGBA", (CELL * 4, CELL), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * CELL, 0), fr)
    sheet.save(dest, "PNG")
    print("wrote", dest)
    return sheet


def orange_sheet(im: Image.Image, dest: Path) -> None:
    bg = Image.new("RGBA", im.size, ORANGE)
    bg.alpha_composite(im)
    dest.parent.mkdir(parents=True, exist_ok=True)
    bg.convert("RGB").save(dest)
    print("contact", dest)


def main():
    bbox = ref_bbox(ROOT / "praetorian_walk_s.png")
    bbox = (bbox[0] % CELL, bbox[1], bbox[2] % CELL if bbox[2] > CELL else bbox[2], bbox[3])
    # use first cell of walk_s
    s = Image.open(ROOT / "praetorian_walk_s.png").convert("RGBA").crop((0, 0, CELL, CELL))
    a = np.array(s)[:, :, 3]
    ys, xs = np.where(a >= 32)
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)

    walk = [fit_cell(Image.open(WORK / f"walk_se_f{i}.jpg"), bbox) for i in range(4)]
    atk_files = [WORK / f"atk_se_f{i}.jpg" for i in range(4)]
    if not atk_files[3].exists():
        atk_files[3] = atk_files[2]
    atk = [fit_cell(Image.open(p), bbox) for p in atk_files]
    idle = [walk[0]] * 4

    se_walk = pack(walk, ROOT / "praetorian_walk_se.png")
    se_idle = pack(idle, ROOT / "praetorian_idle_se.png")
    se_atk = pack(atk, ROOT / "praetorian_attack_se.png")
    walk[0].save(ROOT / "praetorian_se.png", "PNG")

    sw_walk = pack([fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for fr in walk], ROOT / "praetorian_walk_sw.png")
    pack([fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for fr in idle], ROOT / "praetorian_idle_sw.png")
    pack([fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for fr in atk], ROOT / "praetorian_attack_sw.png")
    walk[0].transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(ROOT / "praetorian_sw.png", "PNG")

    orange_sheet(se_walk, ORANGE_OUT / "orange_walk_se.png")
    orange_sheet(sw_walk, ORANGE_OUT / "orange_walk_sw.png")
    orange_sheet(se_idle, ORANGE_OUT / "orange_idle_se.png")
    orange_sheet(se_atk, ORANGE_OUT / "orange_attack_se.png")
    s_strip = Image.open(ROOT / "praetorian_walk_s.png").convert("RGBA")
    orange_sheet(s_strip, ORANGE_OUT / "orange_walk_s.png")


if __name__ == "__main__":
    main()
