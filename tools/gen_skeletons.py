"""One bone-still per enemy stem: same silhouette, ivory ribs, no scene."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ART = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
STEMS = (
    "shambler", "slime", "runner", "node_spawn", "crawler", "psychoid",
    "necro_node", "biomorph", "brute", "cyber_mutant", "armored_dead",
    "mutant_enforcer", "zombie_colossus", "praetorian",
)


def first_cell(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    if w > h * 1.5:
        nf = max(1, round(w / h))
        im = im.crop((0, 0, w // nf, h))
    return im


def to_skel(im: Image.Image) -> Image.Image:
    arr = np.array(im)
    a = arr[:, :, 3]
    vis = a > 20
    # Bone fill
    out = np.zeros_like(arr)
    out[vis, 0] = 232
    out[vis, 1] = 220
    out[vis, 2] = 196
    out[vis, 3] = np.clip(a[vis].astype(np.int16) + 20, 0, 255).astype(np.uint8)
    # Darken interior with a blurred inverse so it reads as ribs, not a white blob
    mask = Image.fromarray((vis.astype(np.uint8) * 255))
    edge = ImageOps.invert(mask).filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    earr = np.array(edge)
    ribs = (earr > 40) & vis
    out[ribs, 0] = 90
    out[ribs, 1] = 78
    out[ribs, 2] = 62
    # Hollow some center pixels
    ys, xs = np.where(vis)
    if len(xs) > 40:
        cy, cx = int(ys.mean()), int(xs.mean())
        yy, xx = np.ogrid[: arr.shape[0], : arr.shape[1]]
        hole = ((yy - cy) ** 2 + (xx - cx) ** 2) < (min(arr.shape[:2]) * 0.08) ** 2
        out[hole & vis, 3] = (out[hole & vis, 3] * 0.35).astype(np.uint8)
    return Image.fromarray(out)


def main() -> None:
    for stem in STEMS:
        src = None
        for cand in (ART / f"{stem}_walk_s.png", ART / f"{stem}_s.png", ART / f"{stem}.png", ART / f"{stem}_walk_e.png"):
            src = first_cell(cand)
            if src:
                break
        if not src:
            print("skip", stem)
            continue
        sk = to_skel(src)
        dest = ART / f"{stem}_skel.png"
        sk.save(dest)
        print("skel", dest.name, sk.size)


if __name__ == "__main__":
    main()
