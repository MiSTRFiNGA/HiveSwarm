---
type: game-documentation
title: HiVE SWARM
description: Canonical source of truth for HiVE SWARM — status, play-feel, developer rules, AI rules, and roadmap.
status: playable-in-development
version: 0.6.22
updated: 2026-08-22
tags: [game, hivemind, webgame, documentation]
---

# 🐝 HiVE SWARM — source of truth

**This file is the only live document for HiVE SWARM.**  
Boards, GDD, README, empire memory, and `My Apps` copies are pointers or history. If they disagree with this file, this file wins. Update this file in place when the game, APK, Pages, or open work changes.

| | |
|---|---|
| **Version** | `0.6.22` · `sw.js` `CACHE_VERSION = v44` |
| **Master path** | `D:\Dev\HiveSwarm` — edit here only |
| **Game file** | `index.html` — one file: engine, FORGE, HUD, run loop |
| **Launcher** | `Launch HiVE Swarm.bat` → http://127.0.0.1:8795/index.html |
| **Desktop play link** | `Play HiVE Swarm.lnk` (Drive id `1mwDl1OW6xcSpdh9hjFhFsNdWhY_Wet6_`) always launches that bat — never the old `standalone\PLAY.bat`. |
| **GitHub** | https://github.com/MiSTRFiNGA/HiveSwarm (public, Pages on `master`) |
| **Pages** | https://mistrfinga.github.io/HiveSwarm/ |
| **APK (one only)** | `C:\Users\MiSTRFiNGA\Desktop\My Games\_APKs\HiveSwarm-0.6.22.apk`. Older Swarm APKs are in `_APKs\Archive`. |
| **Always-latest APK** | Not used for 0.6.16 — owner asked for numbered APKs only (`HiveSwarm-0.6.16.apk`). |
| **Genre** | 360° top-down survivors-like / bullet-heaven. Reference feel: `Zombie Waves.apk` (study only — never its art, audio, or code). |
| **Not** | HiVE WAR (`D:\Dev\HiveWar`) is a **lane / corridor shooter**. "Like HiVE WAR" means borrow a *behaviour*, not edit that repo. |

**Owner last human verdict (2026-08-05):** "getting fun." Everything since then is playtest feel, not "does the game exist."

**Do not** rebuild CrazyGames / Poki (`python build.py`) until the owner asks. Those zips are stale on purpose (`dist/*/index.html` still `0.1.1`).

---

## 1. How to run and verify

```bat
Launch HiVE Swarm.bat
```

Never open `file://`. That taints the canvas and FORGE save/undo fails silently.

```powershell
cd D:\Dev\HiveSwarm
python regen_extract.py          # MUST run after editing index.html
node _headless_harness.js        # crash detector, not a play bot
node _stage_verify.js            # stage/wave progression
python qa/_verify_2026_08_13_changes.py   # 0.6.0 range / movement / debrief
```

Debug hooks: `window.__swarmDbg()` and `window.__hiveSwarmDebug()`. Playwright `evaluate()` cannot see script-scoped `let`/`const`.

Screenshot the **canvas** with `canvas.toDataURL` for gameplay. HTML overlays (pause, cards, beastiary toast, `#pauseBtn`) will **not** appear in a canvas grab.

---

## 2. What the game is

You only steer. Weapons fire themselves at the nearest in-range threat. Stages are kill-quota waves, then a Guardian, then debrief → next stage.

| System | How it works |
|---|---|
| **Stages** | 5 shipped: Outskirts → Sewers → Downtown → Highway → HiVE Core (**Praetorian** guardian). Queen is not in this game. |
| **Waves** | Kill-based, not timed. Finite `waveQuota`. Ends when every spawned body is dead. |
| **XP / cards** | Orbs from kills. Level-up offers 3 cards. Multiple level-ups **queue**. First-three and every later hand force ≥1 equipped-weapon mod unless every applicable mod is 5/5. |
| **Meta** | 3 save slots. Biomatter buys permanent damage / HP / speed / venom and Armory unlocks. Cap +25% total meta power. |
| **Continues** | 1 per 3 stages reached. Hook for a future `PSDK.rewarded()` — **not wired**. |
| **FORGE** | `F2` or ⚒ only (no long-press). Key `hive_swarm_forge_values_v1`. Follow `FORGE_STANDARD.md`. |
| **Spawns (0.6.0)** | Off-camera by construction (outside the viewport rect). Exclusion wedge so a moving player is not fed a horde in the travel direction. |
| **Stall valve (0.6.0)** | Progress = damage, not kills. Only bodies that fail to cover ground (`e.stuckT`) relocate. |

### Weapons (shipped `0.6.0`)

| Weapon | id | Kind | Dmg | Rate | Range | Notes |
|---|---|---|---|---|---|---|
| Pulse Carbine | `weapon.pulse` | bullet | 18 | .16 | **100** | Starter, always owned |
| Heat Seeker | `weapon.seeker` | homing | 22 | .38 | **900 (exempt)** | Armory 4. Range never scales |
| Flamethrower | `weapon.flame` | flame | 9 | .06 | **100** | Cone + burn. `flameLength` tracks range |
| Toxin Injector | `weapon.poison` | poison | 6 | .5 | **100** | DoT + spread; prefers clean targets |
| Breach Laser | `weapon.beam` | beam | 28 | .08 | **200** | Continuous ray. 0.6.1 owner retune |
| Storm Arc | `weapon.chain` | chain | 22 | .32 | **200** | 4 jumps, −12% per jump. 0.6.1 owner retune |
| Nova Shell | `weapon.nova` | nova | 34 | .55 | **100** | Blast uses **weapon damage** (0.6.2). Falloff is distance-from-surface so Colossus/guardian bodies get hit. |

Range is authoritative for **every** kind. `wRange()` is the single source of truth. **Long Barrel** = +30% of that gun's own base per stack, max 5. Homing is excluded twice (`appliesTo` + `wRange()`).

`beam` / `chain` / `flame` are continuous. Scatter / Pierce / Ricochet do not apply (`appliesTo`). Giant Rounds is **removed** from the offer pool (`wSizeMul()` returns 1 so old saves cannot revive it).

### Mods / skills

Weapon mods (max 5 stacks): `rapid` · `knockback` · `ricochet` · `overcharge` · `longrange` · `novastar` · `arcjump` · flame length / spread / napalm · `scatter` · `pierce` · `venom`. Scatter shot curve: 2 / 3 / 4 / 5 / 7.

Run skills: Fleet Footed, Reinforced, Magnet, Shield Matrix, Vampiric, Drone Escort (+ drone rate/damage once a drone exists).

### Enemies

Roster in `EDIT.entities`, gated by `unlockWave` **and** the stage `enemyCap`. Behaviours: chasers, static nodes (`isStaticEnemy()` — knockback must not move them), stage Guardians (`isBoss`, own `EDIT.bosses` slot). Poison and burn use **separate** fields.

---

## 3. Play-feel — 2026-08-14 local `0.6.0`

Played on http://127.0.0.1:8795/index.html (never `file://`), Playwright Chromium, portrait 540×960, WASD kite ~40 s. Evidence: `C:\Users\MiSTRFiNGA\Desktop\Tests\hiveswarm_playfeel_2026_08_14\` (9 canvas frames + `playfeel.json`). Chrome DevTools MCP was unavailable (no `chrome.exe` on this box). Zero `pageerror`s.

### What the run actually did

| t | State | Notes |
|---|---|---|
| 0.0 | title | `v0.6.0` on the title. Cast lineup + cyan player orb. Slot 1, 0 biomatter. |
| 0.6 | play | Pulse Carbine rank 1, range 100. Beastiary toast: Pulse Carbine. |
| 3.5 | play | 4 hostiles, HP 100, player already off-origin. |
| 12 | play | Score 30. Beastiary toast: Biomatter Orb. Floating stick visible. |
| 29 | **levelup** | Wave 2/3, score 100, 13 live / 16 left. Cards: **Scatter 0→1/3**, Ricochet 0→1/3, Shield Matrix 0→1/3. Picked Scatter. |
| 40 | play | Level 2, XP 3/11, score 170, 9 hostiles, **HP still 100**. Pulse now `shots:3` via Scatter. `spawnOnCam: 0` / `spawnOffCam: 26`. `minEnemyDist` 289–300 px. |

### What feels good

- Title is a real product screen, not a greybox.
- Deploy is instant. Auto-fire contract holds: move only, Pulse tracks off-screen threats.
- **Off-camera spawn holds.** 26/26 recorded spawns were off-cam. Nothing popped in the lap. Closest live body stayed ~290 px.
- Opening wave is readable. Rubble obstacles make the arena a place, not a void.
- Off-screen threat ticks (green pips) work.
- Card guarantee worked on the first level-up: one of three cards was an equipped-weapon mod (Scatter). After the pick, Pulse visibly fans three cyan rounds.
- A moving player on Pulse 100 **does not die** in the first 40 s. That matches the 0.6.0 measurement that range 100 is not a difficulty cliff.

### What feels unfinished or wrong

1. **Player is still a cyan circle.** Enemies have 8-dir sheets. The title lineup even *shows* the player as that circle. The soldier sheet exists under `art_src/topdown_v1/player*.png` and is not winning the draw. This is the biggest "greybox leftover" on screen.
2. **HUD collision.** `Pulse Carbine` is drawn through `WAVE 1/3` at top-centre. Beastiary toasts cover the HP bar. Safe-area work happened; the weapon name and toast still fight the top band.
3. **Opening pressure is low if you kite.** 40 s, 26 spawns, 0 damage taken. Shamblers only (stage `enemyCap` 3). Fun starts when you stop or when later archetypes arrive — the first minute is a shooting gallery.
4. **On-screen population is thin.** HUD said 9–13 hostiles; canvas usually showed 1–3. Most of the wave lives off-screen. Off-cam spawn is correct; the *feel* of a swarm is not on the glass yet.
5. **Card and pause UI are HTML, not canvas.** A canvas screenshot during `state=levelup` / `KeyP` looks like live play. Do not use canvas grabs to prove overlays.
6. **Portal builds and published Pages can lie.** Local is 0.6.0. `dist/crazygames` and `dist/poki` are 0.1.1. Pages tracks `origin/master`. After this push they should match 0.6.0; verify the live URL before any phone report.

### Feel verdict

It is a real survivors-like loop: deploy → kite → auto-fire → orb → card → keep moving. Identity is clear. The remaining feel gap is **presence** (player sprite, on-screen swarm density, HUD that does not sit on itself), not missing systems.

---

## 4. Developer rules

- **One agent on `index.html` at a time.** Parallel edits on this file have stomped each other twice.
- Never `git checkout -- index.html`. It is the whole game.
- Bump `GAME_VERSION` **and** `sw.js CACHE_VERSION` together.
- `art_src/` is **runtime**. Do not strip it from the APK.
- Deleting a weapon/enemy from `FORGE_BASE` is not enough. Add the id to `RETIRED_FORGE_IDS` or `forgeMerge()` resurrects it from localStorage forever (rocket launcher bug, 2026-08-13).
- Range / stall / spawn changes need a **measured** before/after, not a feel retune. See §8.
- One versioned APK on the desktop shelf. Archive or delete the rest. Also overwrite `HiveSwarm-latest.apk` (shelf + `D:\Drive\APK`) so the desktop/Drive play link never points at an old numbered file.
- `Play HiVE Swarm.lnk` (including the Drive copy under `D:\Drive\PC\Desktop\My Games\HiVE Swarm\`) must target `D:\Dev\HiveSwarm\Launch HiVE Swarm.bat`. The Drive file id `1mwDl1OW6xcSpdh9hjFhFsNdWhY_Wet6_` is that shortcut.
- Serve on a fresh port and confirm *your* file (`GAME_VERSION` in the HTML). A wedged `http.server` has served the wrong tree.
- `_forge_stages_verify.js` currently fails `TABS[5] !== STAGES` (`STAGES` is index 4). Pre-existing since 0.5.2. Do not treat that red as a 0.6.0 regression.
- Regenerating `_game_extract.js` is required before claiming a harness result.

---

## 5. AI operating rules

| Agent | Lane |
|---|---|
| Whoever is assigned Swarm | `D:\Dev\HiveSwarm\**` only. Sequential edits. Write evidence back **into this file**. |
| Grok | Art / capture / APK / publish / this doc — not a second `index.html` editor while another agent is in it. |
| Codex | Do not open this repo unless assigned. Zelda stays in `D:\Dev\Zelda`. |
| Claude | Design review + verification. Does not invent a second board. |
| Eric | Play, store uploads, portal submit, Quest 3 go/no-go. Agents never submit to stores. |

**Read order for Swarm work:** this file → `index.html` → `FORGE_STANDARD.md`.  
Do **not** start from `design/GDD.md`, archived `BOARD_2026-08-02_HIVESWARM.md`, `BOARD_2026-08-03_LIVE.md`, `OVERLORD_HANDOFF_2026-08-09.md`, or `D:\Drive\AI\My Apps\HiveSwarm\`.

Report format: `✅ DONE — who — date — sha` + **VERIFIED:** command and real output. Visual claims need a whole-frame shot. `SIM ENDED clean` proves the sim ran, not that the game plays.

---

## 6. File map

| Path | Role |
|---|---|
| **`HiveSwarm.md`** | **This file — live source of truth** |
| `README.md` | GitHub stub. Points here. |
| `index.html` | The game |
| `sw.js` / `manifest.webmanifest` | PWA cache. Bump with version. |
| `Launch HiVE Swarm.bat` | Local serve `:8795` |
| `build.py` | Portal zips. **Do not run until asked.** |
| `regen_extract.py` + `_game_extract.js` | Headless extract |
| `_headless_harness.js` / `_stage_verify.js` | Crash / stage probes |
| `design/GDD.md` | Historical 2026-08-02 design |
| `design/ASSET_INVENTORY.md` | Historical media inventory |
| `design/SPRITE_CATALOG.md` | **Live** dir/frame/hole/angle audit + Praetorian import status |
| `docs/REF_ZombieWaves_store_and_meta.md` | Reference APK study |
| `FORGE_STANDARD.md` / `FORGE_TEMPLATE_V3.md` | Forge rules (shared) |
| `art_src/topdown_v1/` | Runtime 8-dir sheets |
| `media/title_art/` | Title options (unshipped into the title screen) |
| `forge_host_corridor_QUARANTINE.html` | Dead corridor host. Do not ship. |
| `dist/crazygames` · `dist/poki` | **Stale 0.1.1.** Leave until owner asks. |

Removed as stale on 2026-08-14: `design/HARVEST.md`, `design/DESIGN.md`, `docs/VERIFY_2026-08-06.md`.

Pointers updated to this file: `README.md`, `design/GDD.md`, `design/ASSET_INVENTORY.md`, `docs/REF_ZombieWaves_store_and_meta.md`, `D:\Drive\AI\START_HERE.md`, `D:\Drive\AI\HIVEMIND_ROADMAP.md`, `D:\Drive\AI\BOARD_2026-08-03_LIVE.md`, `D:\Drive\AI\AGENT_HANDOFF.md`, `C:\Users\MiSTRFiNGA\Desktop\OVERLORD_HANDOFF_2026-08-09.md`, `D:\Drive\AI\My Apps\HiveSwarm\{RESUME,DESIGN,HIVESWARM_STATUS_ROADMAP}.md`.

---

## 7. Roadmap (live)

Do these in order. Do not add weapons or stages in front of P0.

### P0 — publish / honesty (this session's leftover)

1. Push `master` so Pages = local `0.6.14`. Confirm https://mistrfinga.github.io/HiveSwarm/ shows `v0.6.14`.
2. Owner play on the **URL** or `HiveSwarm-latest.apk`. Do not play an old numbered APK.
3. Still **no** CrazyGames / Poki rebuild.

### P1 — feel (from 2026-08-14 play)

4. ✅ Player pawn is Twin Pod (0.6.5) — hull + independent turret. Cyan circle retired.
4b. Sprite rebuild per [`design/SPRITE_CATALOG.md`](design/SPRITE_CATALOG.md): Runner S title, Colossus angle split, Praetorian true diagonals + walk. Torso hole pass started in 0.6.4 (backup-only fill + FORGE ALPHA KEY).
5. ✅ HUD unstack (0.6.1) — STAGE left, WAVE right, weapon under HP, toast under the stack.
6. ✅ 0.6.22 — spawn in a thin off-camera band + higher wave quota. Off-cam invariant kept.
7. ✅ 0.6.22 — `_forge_stages_verify.js` uses `tabs.indexOf('STAGES')` (tab 4, not 5).

### P2 — systems already specified

8. ✅ 0.6.22 — jumps 2..N search at 1.35× first-acquire range.
9. ✅ 0.6.22 — guardian dash (speed burst + telegraph) besides chase.
10. ✅ 0.6.22 — 9% elites: shield / split / explode (ring).
11. ✅ 0.6.22 — Coolant Loop + Shockwave skills. **No Giant Rounds.**

### P3 — shipping (blocked on owner)

12. Wire `requestContinue()` to rewarded ads.
13. Title art from `media/title_art/` onto the title screen (files exist, unused).
14. Portal zips via `build.py` **only when asked**.
15. Store submission is Eric only.

### Explicitly not now

- Quest 3 is not a revenue lane (research 2026-08-09). Waiting on Eric.
- Skull Drift is frozen. Not this repo.
- Do not resurrect Giant Rounds or the rocket launcher.

---

## 8. Change record (keep — measured)

### 2026-08-22 — Grok · v0.6.22 · density, elites, guardian dash, extra skills

Closer off-cam spawn band + bigger wave quotas. Storm Arc later jumps 1.35× radius. Guardians dash. Elites shield/split/explode. Coolant Loop / Shockwave. Giant Rounds stays banned.

### 2026-08-22 — Grok · v0.6.21 · sprite crop + twin stick

Sheets had huge empty 256px padding (xenomorph / shambler / others) and scrap in some cells. Packed walk/idle/attack to the largest blob, and `drawSpriteAnim` now crops to the opaque union.

**Twin stick is not hard.** Title chrome now has **SINGLE STICK** (move + auto-aim, the old game) and **TWIN STICK** (left move, right aim; desktop WASD + mouse). Weapons still auto-fire. Stored per save slot as `META.twinStick`. Enter repeats last pick.

### 2026-08-19 — Grok · v0.6.20 · 0.6.19 blank launch

0.6.19 did not open on Android: the weapon-drop FORGE migrate closed `persistForge()` one brace too early (`Unexpected token '}'`). Script never parsed, WebView stayed black. Restored the function; `node --check` clean. APK `HiveSwarm-0.6.20.apk`.

### 2026-08-19 — Grok · v0.6.19 · Praetorian dirs, weapon drops, sprite punch

Praetorian walk/attack were the same front strip on every facing (and attack frames were sliced). New 8-dir walk (E/W stride, S cycle, N back, diagonals from stills) and attack (raise → slash). Weapon caches: shipped `weaponChance` was 0.05 but `applyForge` / `maybeDropWeapon` filled **0.04**, and old FORGE saves kept that — plus guns **replace** instead of stacking, so it felt like fewer drops. Defaults now **0.08 / 0.45 elite**; old 0.04/0.05 and 0.35/0.40 values migrate. Lime punch across 463 sprite files; node_spawn / cyber_mutant / psychoid cloned walks rebuilt from unique stills.

### 2026-08-19 — Grok · v0.6.18 · ground 256, biomorph stock fallback

Ground tiles draw at 256 world-px (was 1024) so slabs/grates match pawn size. Biomorph purple circle was the missing-sprite fallback: FORGE override objects and late/failed loads now retry and fall back to `biomorph.png`.

### 2026-08-19 — Grok · v0.6.17 · tiled grounds, rotter, colossus L/R, biomorph feet, slime west

Stage floors are now 1024² top-down tiles (`art_src/stages/*_tile.png`) drawn in world space. Isolated barrels/crates/pipes spawn on matching stages. Colossus east/west is the armored body again. The leftover rotting L/R is a new **Rotter** with N/S/NE/NW/SE/SW. Biomorph has feet. Slime west/SW/NW are mirrored left-facing.

### 2026-08-18 — Grok · v0.6.16 · slime punch, no necro boss, 3× boss, enemy SFX

Re-imported Hive Slime from the owner sheet by blob (not a 10-col grid), punched lime/label splash, dropped the clipped bottom row. Necro / speed-0 bodies can no longer roll as the guardian. Boss visual/hit scale floors at 3× the base entity. First pass of per-enemy attack/die samples in `assets/SFX/*_{attack,die}.mp3`. APK is numbered `HiveSwarm-0.6.16.apk` only.

### 2026-08-18 — Grok · v0.6.15 · flame Napalm, skeleton deaths, weapon SFX

Flame is constant (no Rapid). Wide Nozzle gone. Long Barrel is +70% flame reach per stack. Napalm stack 1 enables sticky burn + orange glow; extra stacks raise burn DPS/duration; 2+ adds a tertiary flare; death can splash fire. Kills show a same-size skeleton still then dust. New synthesized weapon SFX (pulse/seeker/flame loop/beam/chain/nova/poison).

### 2026-08-18 — Grok · v0.6.14 · owner edit list

HUD: stage 2× left, hostiles-left + score + wave centered (hostiles once), weapon under, FORGE no longer covers wave. Waves add one enemy type each until the roster is used. Boss HP floors at ~22s of current player DPS; boss sprite rolls from the stage types or Praetorian. Twin Pod FORGE cells no longer show the old pawn. Brute/Enforcer first frames copied from frame 2. Crawler N scaled + NE/NW angled; Necro idle is SE−90; new Node Spawn from Necro N+180. Imported slime, cyber mutant, owner praetorian + colossus L/R. Shambler/Psychoid/Runner FORGE paint is left in IndexedDB — do not reset FORGE.

### 2026-08-18 — Grok · v0.6.13 · paper punch v2, static hull, crawler scale

Restored H3 strips and re-punched: wine frames (brute N/S), dark runner wash, and mid-magenta smears on Praetorian / Biomorph / Colossus. Twin Pod hull is a still — glow no longer pulses, title lineup no longer bobs; hull only rotates with movement. Sheets share one scale per cast so crawler N/S compact poses do not inflate to E/W length.

### 2026-08-18 — Grok · v0.6.12 · paper boxes, static hull, crawler scale

First punch pass left wine scraps (g≈0, r≈20) on runner N and mid-magenta smears on xeno-like sheets. Superseded by 0.6.13.

### 2026-08-18 — Grok · v0.6.11 · blank APK screen

0.6.10 draw loop closed the enemy `for` one brace too early. `if(e.poisonT>0)` then threw `ReferenceError` every frame (strict mode). Canvas never finished a paint — only the HTML pause button showed. Brace restored so poison + HP bar stay inside the enemy loop.

### 2026-08-18 — Grok · v0.6.10 · walk / idle / attack sheets

Live cast now has keyed 4-frame **walk**, **idle**, and **attack** strips under `art_src/topdown_v1/` (`{stem}_{state}_{dir}.png`). Engine picks attack on contact (`atkT`), idle when still, walk when moving. Twin Pod uses `player_idle.png` for a hover cycle. Subterra Maw stays retired. Harvest was MiniMax H3 `:8191` I2V.

### 2026-08-16 — Grok · v0.6.9 · drone knobs, Psychoid frame 3

- Drone picker removed. Locked to **B**. FORGE PLAYER now has live **droneScale** and **droneGlow**. Tune those; tell me later and I’ll bake them as shipped defaults.
- Psychoid walk **frame 3** rotated 180° on every facing (`psychoid_walk*.png`).
- Enemy animation rebuild: online video harvest is blocked on this account (ZDR). Still-to-still edits drifted the Psychoid’s identity, so those tries are on the Desktop for review — **not** in the game yet. ComfyUI locally is the better next pipeline.

### 2026-08-16 — Grok · v0.6.8 · drone B live

Owner picked **B**. Disc + teal ring, cannon faces the target, shots leave the barrel tip. Teal glow under the disc. FORGE PLAYER still has the A–L dropdown if you want to compare.

### 2026-08-16 — Grok · v0.6.7 · per-frame rotate, 5/5, scatter curve, weaker KB

- FORGE ART ROTATE now hits **the selected frame only**. Tick **ALL FRAMES** for the old strip rotate. Switching thumbs resets the degree counter so you can flip one Psychoid cell 180° without spinning the rest.
- `MOD_MAX` 3 → **5**. Weapons, skills, drone mods all 5/5.
- Scatter shot counts: 1→**2**, 2→**3**, 3→**4**, 4→**5**, 5→**7** (was +2 per stack, so 1 stack used to be 3).
- Knockback: impulse 130→42, cap 420→140, extra stacks +45% not +100%. One stack is a nudge, not a keep-away.

### 2026-08-16 — Grok · v0.6.6 · FORGE hullSize + turretRatio

Owner: ratio **1.40** is the look. 2.0 turret too big, 0.52 too small. Wants live knobs, not another rebuild per tweak.

- Shipped `player.hullSize: 0.6` (pods vs the first Twin Pod ship) and `player.turretRatio: 1.40` (turret ÷ hull). Both on FORGE → PLAYER. Live.
- `scale` stays hit radius only. Muzzle still tracks the drawn barrel tip when you change the ratio.
- Proportion preview folder deleted after pick.

### 2026-08-16 — Grok · v0.6.5 · Twin Pod player pawn

Owner rejected the soldier sprites. Picked concept **L Twin Pod**.

- Live pawn is two layers: `player_hull.png` (faces `hullAngle` from the stick) + `player_turret.png` (faces `player.angle` from the primary gun). Movement no longer overwrites aim.
- Teal hover glow under each pod, pulses. Muzzle is the turret barrel tip so shots leave the gun, not the hull centre.
- Title lineup uses the same draw. Cyan sphere is fallback only if the PNGs fail to load.
- Art: `art_src/topdown_v1/player_hull.png`, `player_turret.png`, assembled `player.png`.

### 2026-08-16 — Grok · v0.6.4 · retire Maw + FORGE rotate/frames + hole pass

Owner: Subterra Maw is out. Rotate was missing from Swarm FORGE (it only lived in HiVE WAR). Wanted DUP FRAME + rearrange. Sprites still had magenta-key holes.

- **Maw retired.** `enemy.maw` removed from `FORGE_BASE` and added to `RETIRED_FORGE_IDS` (entities now prune the same way as weapons, so localStorage cannot resurrect it). Art files stay on disk unused. Poison still uses `subterrahit.mp3`.
- **FORGE rotate** ported from Hive WAR: ART ROTATE number, 15° LOCK, ↻ APPLY, ◀ 1° / 1° ▶. Incremental from the last apply. Rotates every frame of the current strip around the 128 cell centre. Hitboxes unchanged.
- **+ DUP FRAME** copies the selected cell and inserts it after. **◀ MOVE / MOVE ▶** and **drag the thumbs** reorder the walk cycle.
- **ALPHA KEY** (Hive WAR) punches leftover `#ff00ff` into transparent from FORGE. Shipped sheets: leftover exact magenta was already 0. Hole pass (`tools/fix_sprite_holes.py`) filled small interior islands from `_bak_pre_magenta_20260807/` only — no neighbour smear. Use ALPHA KEY / brush for anything still punched.

Rotate lives on **ENTITIES → pick a body → paint tools** (under FRAME). There was never a rotate button before 0.6.4.

**VERIFIED:** `python qa/_verify_0_6_4_forge.py` ALL CHECKS PASSED. `node _headless_harness.js` SIM ENDED clean (wave 3, score 460, minHp 58). APK extract: `GAME_VERSION='0.6.4'`, `ART ROTATE`, `spDupFrame`, `enemy.maw` in `RETIRED_FORGE_IDS` only.

### Fallback (do this if 0.6.4 goes wrong)

```
cd D:\Dev\HiveSwarm
git fetch origin
git checkout fallback-2026-08-16-pre-cast
# or keep the branch: git reset --hard fallback/v0.6.2-pre-cast
```

Tag + branch both point at `1548b45` (v0.6.2, pre-cast-import). Pushed to `origin`.

### 2026-08-16 — Grok · v0.6.3 · desktop Assets import

After the save point. Order as promised:

1. **Psychoid** — sliced from the 8-cell top-down sheet. 4-frame walk. Sewers+ (`unlockWave:5`).
2. **Praetorian dirs** — SE/SW from the field-guide + original; N/E/W from the earlier pass. Diagonals NE/NW still copy N.
3. **Biomorph** — 4-frame side walk + idle from the 16-cell sheet. Downtown+ (`unlockWave:7`). W dirs are flips.
4. **Subterra Maw** — **retired in 0.6.4** (owner: horrible). Was a scan-cycle node. Do not re-import unless asked.
5. **runner_s** — title card replaced with a front view. `runner_walk_s` / `_n` now use the SE run strip (the old S walk was "THE RUNNER" on every frame).

Slicer: `tools/slice_desktop_assets.py`. Sources stay on Desktop; we do not overwrite the save-point tree without the tag.

### 2026-08-16 — Grok · v0.6.2 · Nova vs heavies + Praetorian + sprite catalog

**Nova Shell "did not damage the 3 large enemies at the end of level 5; I set damage 22→30 in FORGE, no change."**

Two stacked causes, both real:

1. `explode()` used a **hardcoded 22** and never read the weapon. FORGE `damage` only lived on the held copy / `EDIT` — the blast ignored it. That is why 22→30 did nothing.
2. The blast tested **centre-to-centre** `d < blast` (78px). A HiVE Core guardian is `r ≈ 42 × 1.8 × 2 = 151`. The shell detonates on the *surface*, so `d ≈ 151 > 78` and the enemy that was just hit took **0**. Probe on 0.6.1: `bigDealt: 0`. After the fix: `bigDealt: 30` when `novaMeta.damage=30`.

Fix: falloff is distance-from-**surface**; damage is `novaMeta.damage`. Mid-run FORGE edits also sync into `heldWeapons` (rank reapplied). Probe `qa/_verify_nova_blast.py` — ALL CHECKS PASSED. Harness `SIM ENDED clean`.

**Praetorian** imported from HiVE WAR as the HiVE Core guardian. Queen stays out. 8-dir folder exists; only S/N/E/W are unique (SE/SW copy S, NE/NW copy N). Walk strip is the WAR idle on south-ish dirs.

**Sprite catalog:** [`design/SPRITE_CATALOG.md`](design/SPRITE_CATALOG.md). Worst live defects: `runner_s` has baked "THE RUNNER" text; Colossus side ≠ front body; player sheets exist but the pawn is still a cyan circle; magenta-key holes in several torsos.

### 2026-08-14 — Grok · v0.6.1 · HUD / debrief / range

Owner: fix HUD, punch up level-end text, Breach Laser + Storm Arc start at 200, new APK.

- HUD: STAGE/name left, WAVE right. Weapon name + orb bar sit under the HP/XP stack. Beastiary toast moved under that. Probe: `weaponY=150` vs `stageY=56`, toast `194` vs `hudBottom=128`.
- Debrief headline is now `OUTSKIRTS PURGED` (gold, glow) + `GUARDIAN DOWN · +250` + `TAP TO ADVANCE`. Not `STAGE N CLEAR`.
- Beam/chain shipped range 200. Migration walks known defaults (including 0.6.0's 100) up to 200; hand-tunes stay. Other guns remain 100, seeker 900.
- `qa/_verify_2026_08_14_hud_range.py` — ALL CHECKS PASSED. Harness `SIM ENDED clean`.
- APK: `HiveSwarm-0.6.1.apk`. Previous `0.6.0` moved to `_APKs\Archive`.

### 2026-08-14 — Grok · docs + shelf + play-feel

- This file is now the canonical Swarm document.
- Stale in-repo notes deleted (`HARVEST`, `DESIGN`, `VERIFY_2026-08-06`).
- All HiveSwarm APKs except `0.6.0` removed from Desktop `_APKs` and `D:\Dev\_mobile\dist`.
- Local play-feel recorded in §3. Title art PNGs committed.

### 2026-08-13 — Claude · v0.6.0 · `636e137`

Owner set: range 100 (seeker 900 exempt), modular Long Barrel, teleport fix, spawn-direction fix, FORGE movement knobs, smaller debrief.

- Teleports >300 px in a 40 s unkillable probe: **27 → 0**. Cause: stall valve on "no kill for 11 s" relocated the whole field.
- Spawns within 30° of travel: **57.4% → 0%**. Facing cone inverted to an exclusion.
- Range 100 mean survival 69.8 s vs old pulse 760 at 63.0 s (8-run headless). Not a nerf.
- Movement: `accel` / `brake` / `friction` on FORGE → PLAYER. Friction is coast-only.
- `qa/_verify_2026_08_13_changes.py` passed desktop + mobile.

### 2026-08-13 — Claude · v0.5.1 / 0.5.2

- Rocket launcher resurrected from localStorage via `forgeMerge()`. Fix: `RETIRED_FORGE_IDS`.
- Spawn-on-player: corner clamp ate distance (28.3% of cornered spawns <100 px). Now `placeAwayFromPlayer`.
- 0.5.2: spawn off-camera by construction, not distance-from-player.

### 2026-08-12 — Claude · muzzle / Storm Arc / cards

- Storm Arc "broken" was presentation (1.8 px bolt, 0.2 s, one concurrent), not range. Core/glow/lifetime fixed. Range left at the then-current value; later 0.6.0 set all non-seeker guns to 100.
- All weapons fire from `muzzle()`. Giant Rounds removed. `rollChoices()` guarantees an equipped-weapon card.
- First ~10 s of a stage nothing fires — enemies spawn ~950 px out. That is travel time, not a dead gun.

### 2026-08-09 — Claude · `521102c` · APK 0.4.1

- HiVE WAR-style flamethrower puffs. Per-weapon `fireClocks` (Storm Arc was inheriting the flamethrower's 0.06 s cadence).

### 2026-08-02–08 — Codex / Grok / Claude

Greybox 360° engine, Forge-first entities, stages, bosses, poison, 8-dir art, PWA, first APKs. Genre correction: this is **not** a HiVE WAR reskin. `D:\Dev\ZombieWaves` was the wrong-named scaffold; harvest only.

---

## 9. Dev traps (short)

- `?test=1` is a finite fixture. Never use it for art or "is it alive" claims. Use `?telemetry=1` or a normal load.
- `_headless_harness.js` dies around 20–90 s by design. Survival numbers come from `qa/telemetry.py` or a real play.
- Pause-to-screenshot dims / misses HTML UI. Shoot live.
- `D:\Drive\AI\My Apps\HiveSwarm` is a stale snapshot. Not the master.
