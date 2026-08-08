/**
 * Build a collaborative sprite edit pack for HiVE SWARM.
 * - Copies every topdown_v1 PNG (plus pre-magenta backup mirror)
 * - Builds one atlas sheet per character: idle 8-dir + walk first-frame 8-dir
 * Output: D:\Dev\HiveSwarm\sprite_edit_pack\  and Desktop\HiveSwarm_sprite_edit_pack\
 */
const fs = require('fs');
const path = require('path');
const { createCanvas, loadImage } = (() => {
  try { return require('canvas'); } catch (_) { return { createCanvas: null, loadImage: null }; }
})();

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'art_src', 'topdown_v1');
const BAK = path.join(SRC, '_bak_pre_magenta_20260807');
const OUT = path.join(ROOT, 'sprite_edit_pack');
const DESK = path.join(process.env.USERPROFILE || process.env.HOME || '', 'Desktop', 'HiveSwarm_sprite_edit_pack');
const STEMS = ['player', 'shambler', 'runner', 'crawler', 'necro_node', 'brute', 'armored_dead', 'mutant_enforcer', 'zombie_colossus'];
const DIRS = ['e', 'se', 's', 'sw', 'w', 'nw', 'n', 'ne'];

function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
}
function copyFile(src, dest) {
  ensureDir(path.dirname(dest));
  fs.copyFileSync(src, dest);
}
function copyTree(from, to) {
  if (!fs.existsSync(from)) return 0;
  let n = 0;
  for (const ent of fs.readdirSync(from, { withFileTypes: true })) {
    if (ent.name.startsWith('_bak')) continue;
    const s = path.join(from, ent.name);
    const d = path.join(to, ent.name);
    if (ent.isDirectory()) n += copyTree(s, d);
    else if (/\.png$/i.test(ent.name)) {
      copyFile(s, d);
      n++;
    }
  }
  return n;
}

async function buildSheet(stem, outPng) {
  if (!createCanvas) {
    // Pure copy fallback — no node-canvas: write a manifest only
    return false;
  }
  const cell = 128;
  const cols = 8;
  const c = createCanvas(cell * cols, cell * 2 + 32);
  const g = c.getContext('2d');
  g.fillStyle = '#1a1018';
  g.fillRect(0, 0, c.width, c.height);
  g.fillStyle = '#6fffe2';
  g.font = '12px monospace';
  g.fillText(stem + '  top=idle 8-dir   bottom=walk first-frame 8-dir', 8, 18);

  async function drawCell(file, col, row) {
    const p = path.join(SRC, file);
    if (!fs.existsSync(p)) return;
    const im = await loadImage(p);
    const nf = im.width >= im.height * 1.6 ? Math.max(1, Math.round(im.width / im.height)) : 1;
    const fw = im.width / nf;
    g.fillStyle = '#2a2030';
    g.fillRect(col * cell, 28 + row * cell, cell, cell);
    g.drawImage(im, 0, 0, fw, im.height, col * cell, 28 + row * cell, cell, cell);
    g.fillStyle = '#8ab';
    g.font = '10px monospace';
    g.fillText(DIRS[col], col * cell + 4, 26 + row * cell);
  }

  for (let i = 0; i < DIRS.length; i++) {
    const d = DIRS[i];
    await drawCell(`${stem}_${d}.png`, i, 0);
    // fallback idle base
    if (!fs.existsSync(path.join(SRC, `${stem}_${d}.png`))) await drawCell(`${stem}.png`, i, 0);
    await drawCell(`${stem}_walk_${d}.png`, i, 1);
    if (!fs.existsSync(path.join(SRC, `${stem}_walk_${d}.png`))) await drawCell(`${stem}_walk.png`, i, 1);
  }
  ensureDir(path.dirname(outPng));
  fs.writeFileSync(outPng, c.toBuffer('image/png'));
  return true;
}

async function main() {
  ensureDir(OUT);
  ensureDir(path.join(OUT, 'raw_current'));
  ensureDir(path.join(OUT, 'raw_pre_magenta_backup'));
  ensureDir(path.join(OUT, 'character_sheets'));

  const n1 = copyTree(SRC, path.join(OUT, 'raw_current'));
  const n2 = fs.existsSync(BAK) ? copyTree(BAK, path.join(OUT, 'raw_pre_magenta_backup')) : 0;

  let sheets = 0;
  if (createCanvas) {
    for (const stem of STEMS) {
      const ok = await buildSheet(stem, path.join(OUT, 'character_sheets', `${stem}_sheet.png`));
      if (ok) sheets++;
    }
  } else {
    console.log('NOTE: node-canvas not installed — skipping PNG atlas build.');
    console.log('Install with: npm i canvas   (or use forge EXPORT ALL SHEETS in browser)');
  }

  const readme = `# HiVE SWARM sprite edit pack
Generated: ${new Date().toISOString()}

## Folders
- **raw_current/** — every current PNG under art_src/topdown_v1 (${n1} files)
- **raw_pre_magenta_backup/** — pre-magenta-key backup (${n2} files). Use if current files look worse.
- **character_sheets/** — one atlas per cast member: top row idle 8-dir, bottom walk first-frame 8-dir

## How we collaborate
1. Edit sheets or individual raw PNGs in Photoshop / Aseprite / etc.
2. Put fixed files back into art_src/topdown_v1/ with the same names, OR
3. Import into Forge (ENTITIES → click walk dir → IMPORT / SAVE).
4. Tell the agent which stem + direction you fixed.

## Naming
- idle: \`{stem}.png\`, \`{stem}_e.png\` … \`{stem}_ne.png\`
- walk: \`{stem}_walk_e.png\` … (optional multi-frame strips: wide horizontal)

## Stems
${STEMS.join(', ')}
`;
  fs.writeFileSync(path.join(OUT, 'README.md'), readme);

  // Mirror to Desktop
  try {
    ensureDir(DESK);
    // shallow copy via recursive
    function mirror(from, to) {
      ensureDir(to);
      for (const ent of fs.readdirSync(from, { withFileTypes: true })) {
        const s = path.join(from, ent.name);
        const d = path.join(to, ent.name);
        if (ent.isDirectory()) mirror(s, d);
        else copyFile(s, d);
      }
    }
    mirror(OUT, DESK);
    console.log('Desktop pack:', DESK);
  } catch (e) {
    console.warn('Desktop copy failed:', e.message);
  }

  console.log('Pack:', OUT);
  console.log('raw_current:', n1, 'backup:', n2, 'sheets:', sheets);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
