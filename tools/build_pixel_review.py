"""Build a local pixel-review pack for Eric.

Orange #FF7800 backdrop (green hid lime visors). Contact sheets + exploded
256px frames + an HTML pager. Does not modify art_src.

  python D:/Dev/HiveSwarm/tools/build_pixel_review.py
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r"D:\Dev\HiveSwarm\art_src\topdown_v1")
OUT = Path(r"C:\Users\MiSTRFiNGA\Desktop\HiveSwarm_pixel_review")
ORANGE = (255, 120, 0, 255)
GAP = 4
LABEL_H = 22
DIRS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]
STATES = ["idle", "walk", "attack"]
SKIP_PREFIX = ("subterra_maw", "obstacle", "drone", "node_spawn")
SKIP_DIRS = {"_bak_pre_magenta_20260807", "_bak_v030_framing", "_bak_art_0_6_23"}


def cell_size(w: int, h: int) -> int:
    if w >= h * 1.6:
        return h
    return min(w, h)


def stem_of(name: str) -> str:
    n = Path(name).stem
    for st in STATES:
        token = f"_{st}"
        if token in n:
            n = n.split(token)[0]
            break
    for d in DIRS:
        suf = f"_{d}"
        if n.endswith(suf):
            n = n[: -len(suf)]
            break
    return n


def resolve_strip(stem: str, state: str, d: str) -> Path | None:
    candidates = [
        ROOT / f"{stem}_{state}_{d}.png",
        ROOT / f"{stem}_{state}.png",
        ROOT / f"{stem}_{d}.png",
        ROOT / f"{stem}.png",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def split_cells(path: Path) -> list[Image.Image]:
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    cell = cell_size(w, h)
    cols = max(1, w // cell)
    return [im.crop((i * cell, 0, (i + 1) * cell, cell)) for i in range(cols)]


def on_orange(im: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", im.size, ORANGE)
    bg.alpha_composite(im)
    return bg.convert("RGB")


def font(size: int):
    for p in (
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def live_stems() -> list[str]:
    stems = set()
    for p in ROOT.glob("*.png"):
        if p.name.startswith(SKIP_PREFIX):
            continue
        stems.add(stem_of(p.name))
    # drop hull/turret split — player sheet is enough
    stems.discard("player_hull")
    stems.discard("player_turret")
    return sorted(stems)


def build_sheet(stem: str, fnt) -> dict:
    sheet_dir = OUT / "sheets"
    frame_dir = OUT / "frames" / stem
    sheet_dir.mkdir(parents=True, exist_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    blocks = []  # (state, dir, cells)
    max_frames = 1
    for state in STATES:
        for d in DIRS:
            src = resolve_strip(stem, state, d)
            if not src:
                continue
            cells = split_cells(src)
            max_frames = max(max_frames, len(cells))
            blocks.append((state, d, cells, src.name))
            for i, cell in enumerate(cells):
                on_orange(cell).save(frame_dir / f"{state}_{d}_f{i}.png", "PNG")

    if not blocks:
        return {"stem": stem, "frames": 0, "sheet": None}

    cell_w = blocks[0][2][0].size[0]
    cell_h = blocks[0][2][0].size[1]
    cols = 8
    rows = len(STATES) * max_frames
    W = GAP + cols * (cell_w + GAP)
    H = LABEL_H + GAP + rows * (cell_h + LABEL_H + GAP) + LABEL_H
    canvas = Image.new("RGB", (W, H), (20, 12, 8))
    dr = ImageDraw.Draw(canvas)
    dr.text((GAP, 4), f"{stem}  orange=#FF7800  idle/walk/attack x 8 dirs", fill=(255, 220, 180), font=fnt)

    # map (state, dir) -> cells
    lookup = {(st, d): cells for st, d, cells, _ in blocks}
    y = LABEL_H + GAP
    n_frames = 0
    for state in STATES:
        for fi in range(max_frames):
            dr.text((GAP, y), f"{state} f{fi}", fill=(200, 180, 140), font=fnt)
            y += LABEL_H
            x = GAP
            for di, d in enumerate(DIRS):
                cells = lookup.get((state, d))
                if cells and fi < len(cells):
                    canvas.paste(on_orange(cells[fi]), (x, y))
                    n_frames += 1
                else:
                    dr.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(80, 40, 20))
                dr.text((x + 2, y + 2), d, fill=(255, 255, 255), font=fnt)
                x += cell_w + GAP
            y += cell_h + GAP

    dest = sheet_dir / f"{stem}.png"
    canvas.save(dest, "PNG")
    return {
        "stem": stem,
        "frames": n_frames,
        "sheet": str(dest),
        "rel_sheet": f"sheets/{stem}.png",
        "rel_frames": f"frames/{stem}/",
    }


def write_html(rows: list[dict]) -> None:
    cards = []
    for r in rows:
        if not r.get("rel_sheet"):
            continue
        cards.append(
            f'<a class="card" href="{r["rel_sheet"]}" data-stem="{r["stem"]}">'
            f'<img src="{r["rel_sheet"]}" alt="{r["stem"]}">'
            f"<span>{r['stem']} · {r['frames']} frames</span></a>"
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HiVE SWARM pixel review</title>
<style>
  html,body {{ margin:0; background:#140c08; color:#f3e6d4; font:14px/1.4 Consolas, monospace; }}
  header {{ position:sticky; top:0; background:#1c100c; padding:12px 16px; border-bottom:1px solid #5a3020; z-index:2; }}
  h1 {{ margin:0 0 6px; font-size:16px; }}
  .hint {{ color:#c9a88a; max-width:70rem; }}
  kbd {{ background:#2a1810; padding:1px 5px; border:1px solid #6a4030; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:12px; padding:16px; }}
  .card {{ display:block; color:inherit; text-decoration:none; background:#1c100c; border:1px solid #5a3020; }}
  .card img {{ width:100%; height:160px; object-fit:cover; object-position:top; background:#ff7800; }}
  .card span {{ display:block; padding:6px 8px; }}
  .card:focus, .card:hover {{ outline:2px solid #ffcc88; }}
  #lightbox {{ display:none; position:fixed; inset:0; background:#000c; z-index:9; padding:12px; }}
  #lightbox.on {{ display:flex; flex-direction:column; }}
  #lightbox img {{ max-width:100%; max-height:calc(100vh - 48px); margin:auto; background:#ff7800; }}
  #bar {{ color:#ffcc88; padding:6px 0; }}
</style>
</head>
<body>
<header>
  <h1>HiVE SWARM pixel review</h1>
  <div class="hint">
    Orange backdrop is on purpose so holes and near-black blobs show. Click a card, then
    <kbd>←</kbd> <kbd>→</kbd> between characters. Exploded 256px frames are in
    <code>frames/&lt;name&gt;/</code> — open those in Paint.NET / Photoshop.
    These copies are for looking. Edit the real files in
    <code>D:\\Dev\\HiveSwarm\\art_src\\topdown_v1\\</code>.
  </div>
</header>
<div class="grid" id="grid">
{''.join(cards)}
</div>
<div id="lightbox"><div id="bar"></div><img id="full" alt=""></div>
<script>
const cards = [...document.querySelectorAll('.card')];
const box = document.getElementById('lightbox');
const full = document.getElementById('full');
const bar = document.getElementById('bar');
let i = 0;
function show(n) {{
  i = (n + cards.length) % cards.length;
  const a = cards[i];
  full.src = a.getAttribute('href');
  bar.textContent = (i+1) + '/' + cards.length + '  ' + a.dataset.stem + '   ← →  Esc';
  box.classList.add('on');
  cards[i].focus();
}}
cards.forEach((a, idx) => a.addEventListener('click', e => {{ e.preventDefault(); show(idx); }}));
document.addEventListener('keydown', e => {{
  if (!box.classList.contains('on') && (e.key === 'ArrowRight' || e.key === 'ArrowLeft')) {{
    show(0); return;
  }}
  if (!box.classList.contains('on')) return;
  if (e.key === 'Escape') box.classList.remove('on');
  if (e.key === 'ArrowRight') show(i+1);
  if (e.key === 'ArrowLeft') show(i-1);
}});
box.addEventListener('click', () => box.classList.remove('on'));
</script>
</body>
</html>
"""
    (OUT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    if OUT.exists():
        # rebuild clean
        for p in OUT.rglob("*"):
            if p.is_file():
                p.unlink()
    (OUT / "sheets").mkdir(parents=True, exist_ok=True)
    (OUT / "frames").mkdir(parents=True, exist_ok=True)
    fnt = font(14)
    stems = live_stems()
    rows = []
    for stem in stems:
        rows.append(build_sheet(stem, fnt))
        print("sheet", stem, rows[-1]["frames"])
    write_html(rows)
    manifest = {
        "out": str(OUT),
        "orange": "#FF7800",
        "stems": [r["stem"] for r in rows],
        "counts": rows,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    readme = """HiVE SWARM pixel review
=======================
Open index.html in a browser (double-click). Orange background on purpose.

sheets\\     one contact sheet per character (idle/walk/attack x 8 dirs x frames)
frames\\     individual 256px cells, same orange, for Paint.NET

Real art lives in D:\\Dev\\HiveSwarm\\art_src\\topdown_v1\\
Rebuild: python D:\\Dev\\HiveSwarm\\tools\\build_pixel_review.py
"""
    (OUT / "README.txt").write_text(readme, encoding="utf-8")
    print("OUT", OUT)
    print("characters", len(rows))


if __name__ == "__main__":
    main()
