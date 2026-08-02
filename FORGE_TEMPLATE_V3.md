# ⚒ FORGE TEMPLATE v3 — the one base every game's editor is copied from

**Owner:** Eric (MiSTRFiNGA) · **Written:** 2026-08-01 · **Status:** SCOPE — awaiting Eric's approval
**Extends:** [FORGE_STANDARD.md](file:///D:/Drive/AI/Memory/FORGE_STANDARD.md) (still canonical for the *rules*)
**This doc adds:** the unified **data model** + **UI layout** + a **build order** so a new game's Forge is a copy-and-fill job, not a rewrite.

> **Decision (Eric, 2026-08-01):** **copy-per-game**, not a shared import. Each game will have unique
> features, so editing a base copy is fine. This file + the reference implementation *is* the base.
> **Reference implementation will be HiVE WAR's Forge** — it is the most advanced of the three.

---

## 0. Where we are today

| Game | Forge | Shape | Tabs today |
|---|---|---|---|
| **HiVE WAR** — [`D:\Dev\HiveWar\index.html`](file:///D:/Dev/HiveWar/index.html) | HiVE FORGE | in-file IIFE, `⚒` + F2 | `ENTITIES · PLAYER · WEAPONS · WAVES+BOSS · WORLD · SPRITES · DATA` |
| **Crypt Match** — [`D:\Dev\CryptMatch\index.html`](file:///D:/Dev/CryptMatch/index.html) | CRYPT FORGE | in-file IIFE, `⚱` + F2 | `PIECES · RELICS · LEVELS · AUDIO · DATA` |
| **Zelda** — [`D:\Dev\ZeldaForge\ui\forge.js`](file:///D:/Dev/ZeldaForge/ui/forge.js) | ZELDA FORGE | standalone Python :8799 → UE RC :30010 | `TRANSPORT · MAP · SCREENS · ENEMIES · ITEMS · SPRITES · CONSOLE` |

**What each one already does best — this is what gets merged:**

- **HiVE WAR** → sprite **frame/animation** editor, per-level **WORLD** env art w/ paint + **crop**,
  **MOD PACK** export (`PACK_FORMAT`), debug **transport** (⏸ ⏩ ⏭), playtest-from-level buttons,
  quota-guarded downscale on import, deep-link `?forge=1&ftab=N`.
- **Crypt Match** → **AUDIO** tab done properly (imported clip bank + UI voices + music w/ its own mute),
  roster shrink → live index remap.
- **Zelda** → **TRANSPORT** to a live engine, **MAP / SCREENS** spatial layout editing, **CONSOLE**
  with saved macros + a raw key/value table.

**What none of them do, that Eric wants:**
1. Per-**sprite** transform (HiVE WAR only has a per-**class** `EDIT.scale = {player,enemy,boss,…}`).
2. **Rotate** in the image editor (angle-snap + fine nudge).
3. **Tiling amount** for path / walls.
4. **Transparent PNG + animated GIF** worlds and walls.
5. **One grid where every entity is edited the same way** — blanks for params that don't apply.

---

## 1. The core idea — ONE entity table

The single biggest change. Today HiVE WAR has enemies in `UNITS`, the player in `PLAYER`, bosses in
`WAVES+BOSS`, rollers in `WORLD`, tanks half in `UNITS` and half in code — **five different shapes for
what is conceptually the same row.** That is why every tweak needs me.

**v3 rule: every drawable, tunable thing in the game is one row in one `ENTITIES` table, with one
identical column set. A column that doesn't apply to that row renders as a greyed blank — it does not
disappear, and it does not get its own bespoke panel.**

### 1.1 The universal entity row

```
id            "enemy.xenoid" | "player.soldier" | "boss.praetorian" | "hazard.roller"
              | "vehicle.tank" | "prop.barrier" | "pickup.credit" | "env.path" | "env.wallL"
class         enemy | player | boss | vehicle | hazard | prop | pickup | env | fx
label         display name

── ART ──────────────────────────────────────────────────────────────
sprite        slot key → SPRITES tab (strip / single / gif)
frames, fps   animation (blank for statics)
states        idle / walk / attack / die   (blank slots stay greyed, game ignores)

── TRANSFORM (per-sprite — THIS REPLACES THE GLOBAL SCALE) ───────────
scale         0.10 – 4.00, step 0.01     ← every row, including the player
rotate        −180 – 180°, snap 15/45/90 + fine ±1°
offsetX/Y     px nudge relative to the entity's anchor
flipX/flipY   bool
anchor        bottom-center | center | top-center
tileX/tileY   repeat count — MEANINGFUL ONLY for class `env` (path, walls, bg)
opacity       0 – 1

── STATS (blank = not applicable to this class) ──────────────────────
hpBase, hpPerLvl, dmg, speed, armor, credits
weight        spawn weight (enemies only — blank for player/env/props)
minLvl        unlock gate
cooldown, range, lifetime

── PRESENTATION ─────────────────────────────────────────────────────
color, glow, sfxSpawn, sfxHit, sfxDie
```

**Migration note for HiVE WAR:** `EDIT.scale = {player, enemy, boss, queen, roller, gate, tank}`
([index.html:255](file:///D:/Dev/HiveWar/index.html)) and the `SCL()` accessor
([index.html:262](file:///D:/Dev/HiveWar/index.html)) get **deleted**. Every `SCL().x` call site
becomes `ENT(id).scale`. On load, a one-time migration copies the old class scale down onto each
member row so existing mod packs keep looking identical.

### 1.2 Tab layout (v3 standard — name them in the game's vocabulary)

| # | Tab | Contents |
|---|---|---|
| 1 | **ENTITIES** | The universal table above. Filter chips by class. Click a row's thumbnail → SPRITES editor. **Everything lives here.** |
| 2 | **BALANCE** | Global curves that aren't per-entity: spawn rate per level, wave ramp, boss HP table, difficulty multipliers, economy/store prices, drop rates. |
| 3 | **WEAPONS** | Damage, RoF, projectile count, spread, tier multipliers, unlock gates, pickup art. |
| 4 | **LEVELS** | **Visual track editor** (Eric's choice): drag barriers / spawn groups / hazards / boss point along a side-on view of the level, drag the end marker to set length. Numeric fields alongside for precision. Plus per-level name, env art slots, tiling, music. Playtest ▶ / boss ☠ buttons. |
| 5 | **SPRITES** | Every art asset in the game, grouped by class, with the image editor (§2). Nothing is missing from here — if it draws, it's listed. |
| 6 | **AUDIO** | Imported clip bank + UI voices + music (own mute). Lifted from Crypt Match wholesale. |
| 7 | **DATA** | Export / import / reset. One pack = values + sprites + env + audio. |
| — | *header* | **TRANSPORT** ⏸ ⏩ ⏭ + resize/drag, always present, not a tab. |

Zelda's **MAP / SCREENS / CONSOLE** stay as extra game-specific tabs — that's exactly the
"unique feature" allowance.

---

## 2. Image editor v3 (the shared component)

Everything in [FORGE_STANDARD §4](file:///D:/Drive/AI/Memory/FORGE_STANDARD.md) **plus**:

- **ROTATE** — a slider −180…180 with **angle lock** buttons (15° / 45° / 90°) and **fine ±1°** nudge
  arrows. Rotation is applied to the *layer*, resampled bilinear, with an "apply / cancel" so it's
  undoable like crop already is.
- **TILING** — for `env` slots, live `tileX` × `tileY` spinners with a **preview showing the seam**,
  so path and wall art can be made to fit different assets without me. *(This is Eric's
  "add a Tiling amount for path and walls" — HiVE WAR's hardcoded `S=13` density knob in
  `drawPerspectiveRoad` becomes an exposed per-level value.)*
- **TRANSPARENCY** — checkerboard already exists; add an **alpha-threshold key** tool (pick a colour →
  make transparent) so sheets exported without alpha still work.
- **ANIMATED GIF import** — decode to frames on import and store as a normal strip. Same code path as
  a PNG strip afterwards, so the renderer needs no GIF support at runtime. Applies to backgrounds and
  walls too, which is what makes animated environments possible.
- Existing and kept: 3× checkerboard view, brush/size/erase/undo/clear, shift-line, import PNG,
  **SAVE LIVE**, **REVERT TO SHIPPED**, **DOWNLOAD PNG**, crop, frame ± / FPS.

⚠️ **Known trap:** running from `file://` taints the canvas and every save silently fails. Always
launch via [`Launch HiVE War.bat`](file:///D:/Dev/HiveWar/Launch%20HiVE%20War.bat). The v3 template
must keep the red taint warning banner that HiVE WAR already shows.

---

## 3. Phased build order

Each phase ends in a state that is shippable on its own. **Model column = who should do it**, to keep
my (expensive) tokens for design and review only.

| Phase | What | Model | Depends on |
|---|---|---|---|
| **F0** | **Spec freeze.** Eric approves this doc. Lock the entity schema + tab list. | Claude (done here) | — |
| **F1** | ✅ **DONE — Codex — 2026-08-01 — bbbc176** Entity model refactor (HiVE WAR). Per-entity registry now owns every runtime transform; `SCL()`/global `EDIT.scale` are removed. Legacy local saves, packs and DATA backups migrate scales safely; tank fire/draw share entity range; compatibility controls cover all rows until F2. **VERIFIED:** browser migration fixtures (legacy + explicit entities), Forge opens without page errors, `python regen_extract.py && node _headless_harness.js`, and final review pass. | Codex | F0 |
| **F1b** | ✅ **DONE — Codex — 2026-08-01 — 431ddc2** **Storage → IndexedDB.** Sprite/environment media now persists as binary Blobs; values/names remain in localStorage. Includes a first-draw hydration gate, per-record legacy migration, atomic pack replacement, and serialized media writes/resets. **VERIFIED:** browser legacy fixture confirms Blob records and legacy-key removal only after migration; clean Forge browser smoke; final persistence review approved. | Codex | F1 |
| **F2** | ✅ **DONE — Codex — 2026-08-01 — 9fedb75** **ENTITIES tab UI.** One semantic, live-apply table covers all 13 entity classes; filters, explicit N/A cells, per-field labels, enemy SFX/HP/share controls, and 44px thumbnail actions are included. Thumbnail edit/create opens the sprite editor and Back restores focus to the source row. **VERIFIED:** Playwright checks tab keyboard navigation, filters, SFX/previews, return focus, and both blank roller create flows with zero page errors; `python regen_extract.py && node _headless_harness.js` clean. | Codex | F1 |
| **F3** | ✅ **DONE — Codex — 2026-08-01 — 77beebe** **Image editor v3.** Art-only rotate with 15° lock and fine nudge, alpha-key, animated GIF import with no frame cap (large-frame warning only), and bounded tiling spinners with canvas seam preview. **VERIFIED:** live-browser controls smoke, regression review, and final reviewer approval. | Codex | F2, F1b |
| **F4** | ✅ **DONE — Codex — 2026-08-01 — 44ca34a** **Tabs fill-out.** Added BALANCE and AUDIO tabs, preserved all shifted tab routes, wired live start/reward/shop economy values, and made SFX/MUSIC settings persist. **VERIFIED:** all nine tabs deep-link in browser with zero page errors; focused final review approved. | Codex | F2 |
| **F4b** | ✅ **DONE — Codex — 2026-08-01** **VISUAL LEVEL EDITOR.** WORLD now includes a persisted side-on level timeline with draggable barriers, spawn groups, hazards, boss point and end marker; snap-to-grid, exact numeric fields, and a scrub-preview cursor/event readout. Authored marks drive the real gate, roller, spawn-burst and boss-timing paths; empty tracks retain legacy procedural cadence. **VERIFIED:** Chromium add/drag/persistence and scrub smoke, headless gameplay harness, syntax check, diff check, and focused code review. | Codex | F4 |
| **F5** | ✅ **DONE — Codex — 2026-08-01** **QA.** `qa/test_forge.py` covers all nine tabs, live balance application in a real run, pack export/import, sprite persistence/reload/revert through IndexedDB, rotate round-trip via saved-media signature, GIF frame import, tiling dimensions, and persisted visual-level marks with authored runtime boss/gate behavior. Per-entity scale is proved at the actual player `drawImage` destination-size calculation. **VERIFIED:** `python -m unittest qa.test_forge -v` (6/6), source syntax check, diff check, and final focused review with no high/critical findings. | Codex | F3, F4, F4b |
| **F6** | **Extract the template.** Strip HiVE WAR specifics → `D:\Dev\_shared\forge_template\` (a commented reference copy + this doc). Not imported — copied. | Claude (review) | F5 |
| **F7** | **Backport — IMAGE EDITOR ONLY** *(Eric's call: leave their tab layouts alone for now)*. Port the v3 image editor (rotate, alpha-key, GIF, tiling) into Crypt Match's and Zelda's existing Forges. **Do NOT convert their tabs to the v3 entity table.** | Grok | F6 |
| **F8** | **Zombie Waves.** New game scaffolds by copying the template, filling the entity table, and importing HiVE WAR's media + weapon definitions as the starting content set. | Codex | F6 |

**Critical-path note:** F1 is the risky one — it touches every draw call in a 220 KB single-file
game. It must land behind the headless harness (`node _headless_harness.js`) going green, and the
one-time scale migration must be verified against a saved mod pack before anything else starts.

---

## 4. Acceptance test — "can Eric do it without Claude?"

The template is done when Eric can, **with zero code from me**:

- [ ] Swap any sprite in the game, including the player, and set its own scale / rotation / offset / flip
- [ ] Import an animated GIF as a background or wall — **any size** — and see it animate
- [ ] Change how many times the path tile repeats until new art looks right
- [ ] Change any HP, damage, speed, spawn rate, spawn count, store price or drop rate
- [ ] **Drag** barriers, spawns and the boss point along a visual track, and set level length by dragging the end marker
- [ ] Swap music and any SFX, tune FX colour/intensity
- [ ] Export the whole thing as one pack file and load it on another machine
- [ ] Reset cleanly back to shipped defaults

If any box needs me, the template isn't finished.

---

## 5. ✅ Eric's decisions (2026-08-01) — all locked, no open questions

| # | Question | **Eric's answer** | Effect |
|---|---|---|---|
| 1 | Rotation & hitboxes | **ART ONLY** | Hitboxes stay axis-aligned boxes. Rotation never touches collision. Cheapest path — confirmed. |
| 2 | Levels tab | **VISUAL** — drag-on-a-track editor | F4 splits: the visual level editor becomes its own phase, **F4b**. |
| 3 | GIF storage | **Use IndexedDB** — no frame cap, size limited only by what runs smooth | Storage layer moves off localStorage → **new phase F1b**. |
| 4 | Crypt Match / Zelda backport | **IMAGE EDITOR UPGRADES ONLY, for now** | F7 shrinks massively — their tab layouts are left alone. |

**What #3 meant, in plain English:** localStorage caps at ~5 MB and stores text, so a GIF has to be
base64'd — a single animated background could eat the entire budget for the whole game. **IndexedDB**
is the browser's real database: it stores raw binary, has no practical size ceiling, and is
asynchronous so it doesn't stall the frame. Eric chose it, so **large animated backgrounds are on the
table** — the only remaining limit is decode/draw cost at runtime, which is a performance question,
not a storage one. F1b must include a frame-budget warning in the UI ("this GIF is 90 frames — expect
frame drops") rather than a hard block.

---

## 6. 📋 How to report progress in this doc

Everyone working from this file **edits it in place** when a phase completes:

- Change the phase's row to `✅ DONE — <who> — <date> — <commit sha>`
- Add a one-line **VERIFIED:** note saying *how* it was proven (harness output, screenshot path, test name)
- If something was **not** done, say so explicitly with `⚠️ PARTIAL:` and what's missing
- Never mark a visual item done without a screenshot in `C:\Users\MiSTRFiNGA\Desktop\Tests\`

Claude reads this file only when Eric says to.
