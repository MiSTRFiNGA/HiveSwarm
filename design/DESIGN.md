# HiVE SWARM — design notes

## G7 — Weapon acquisition (2026-08-05)

### Problem
Wave progression only grants level-up cards. The only multi-weapon path is the **Scatter Shot** card, which stacks awkwardly. There is no field loot, no rank system, and no between-run weapon unlock beyond meta HP/DMG/SPD ranks.

### Goals
1. Feel like a survivors-like: find weapons *during* a run, not only at level-up.
2. Keep FORGE data-driven (new weapons stay in `EDIT.weapons`).
3. Stay small — no full inventory UI this pass.
4. Respect BEASTIARY: equipping or first-seeing a weapon already unlocks `weapon:<id>`.

### Proposal (chosen)

**Field weapon caches + rank stacking + title armory seed.**

| Path | When | What happens |
|---|---|---|
| **Weapon cache drop** | Elite kill (`dropXp >= 5`) or rare random on any kill (`EDIT.drops.weaponChance`) | Spawns a floating cache. Walking over it **adds that weapon** to `heldWeapons` (or ranks it up if already held). |
| **Rank-up** | Collect a cache of a weapon you already have | `damage ×1.18`, `rate ×0.94` (faster), `pierce +0` unless rank multiples of 3 then `pierce +1`. Max rank 5. |
| **Level-up cards** | Keep existing cards | Still the soft path for stats + one free weapon/stat pick. |
| **Title ARMORY (seed)** | Between runs, spend biomatter | Unlock a **starting sidearm** so run 2+ is not always pure Pulse. Stored in `META.ownedWeapons[]` + `META.startWeapon`. |

### Not in this pass
- Full fusion trees (A + B → C). Leave room: ranks 5 could later become “evolve” cards.
- Drag-drop inventory. Auto-hold up to 5 weapons (already the Scatter cap).

### Numbers (FORGE-tunable)
- `EDIT.drops.weaponChance` default `0.04` (4% on any kill; elites force a roll at 0.35).
- Starting catalog beyond Pulse: add **Needler** and **Arc Shotgun** as shipped `EDIT.weapons` rows so caches have variety without FORGE edits.
- Max held weapons: 5 (existing).

### Acceptance
- Headless harness still `SIM ENDED clean` after 90s with kite.
- A 90s run can pick up at least one non-Pulse weapon when forced (`weaponChance=1` smoke test).
- BEASTIARY unlocks `weapon:<id>` on first cache collect / equip.
- Version bump with `sw.js` cache.

### Implementation order
1. Ship 2 extra weapons in `FORGE_BASE.weapons`.
2. Drop + magnet + collect for `pickup.kind==='weapon'`.
3. Rank-up helper `upgradeWeapon(w)`.
4. Title ARMORY panel (M already opens meta — extend with start weapon buttons).
5. Evidence harness + commit.

## G8 — STAGE system (2026-08-06)

### Problem
HiVE SWARM had no stages — a run was one endless escalating wave timer (`wave = 1 + floor(elapsed / EDIT.waves.seconds)`), same backdrop and roster gate the whole run, no climax, no natural break to breathe or re-gear. Reference genre APK (Zombie Waves) uses discrete stages with their own look, enemy set, and a boss gate between them.

### Design
Discrete **stages** sit on top of the existing wave/spawn-budget math (unchanged — still drives per-enemy stat scaling and spawn density within a stage). A stage adds:
1. **Its own enemy set** — a roster cap (`enemyCap`) gates which `ENEMIES` entries can spawn this stage, layered on top of the existing `unlockWave` ramp.
2. **Its own backdrop** — a `bg: [top, bottom]` gradient tints the arena per stage (grid/geometry unchanged).
3. **A duration + climax** — after `seconds` of survival, a **guardian** (boss) spawns: one scaled-up copy of the strongest entity the stage's roster allows (`hp *= bossMul`, `dmg *= 1.4`, `r *= 1.6`). No new art required. Normal spawn-budget growth freezes while the guardian is up (existing mobs keep fighting) so the boss reads as a distinct fight, not more zerg.
4. **A between-stage break** — killing the guardian opens a reward-card overlay (same pool as the level-up cards: weapon mods + stat cards), heals the player 25%, wipes the field, and advances to the next stage on pick.
5. **Looping** — stages cycle (`stage % EDIT.stages.length`) once past the last defined stage; each lap multiplies `bossMul` by `1 + 0.4*cycle` so a repeat visit is tougher, keeping runs endless without repeating the exact same fight forever.

### Data (`FORGE_BASE.stages`, `index.html`)
```js
stages:[
  {id:'stage.outskirts',name:'Outskirts', seconds:60,  enemyCap:3,  bg:['#0a1622','#142434'], bossMul:6},
  {id:'stage.sewers',   name:'Sewers',    seconds:75,  enemyCap:6,  bg:['#0d1a12','#16301f'], bossMul:7},
  {id:'stage.downtown', name:'Downtown',  seconds:90,  enemyCap:9,  bg:['#160c1e','#2a1638'], bossMul:8},
  {id:'stage.highway',  name:'Highway',   seconds:105, enemyCap:13, bg:['#1c0a0a','#3a1414'], bossMul:9},
  {id:'stage.hivecore', name:'HiVE Core', seconds:120, enemyCap:99, bg:['#050b14','#111b2c'], bossMul:12}
]
```
Lives inside `FORGE_BASE` alongside `waves`/`weapons`/`entities`, so it round-trips through `forgeMerge()`/`localStorage`/the FORGE DATA-tab JSON export like every other tunable — a dedicated FORGE `STAGES` tab (table UI) is a natural follow-up but not required for the config to be editable today.

### Implementation
- State: `stage` (index), `stageT` (seconds into current stage, frozen while a guardian is alive or during the break), `stageBoss` (live ref, null when none up), `curStageCfg()` helper.
- `spawnEnemy()` roster filter gains a `stageCap = curStageCfg().enemyCap` clamp (falls back to the un-capped roster, then to all `ENEMIES`, so it can never produce an empty roster).
- `spawnBossEnemy()` builds the guardian from the strongest entity the current stage allows.
- `killEnemy()` special-cases `e.isBoss`: bonus score/shake/explosion, `state='stagebreak'`, calls `offerStageBreak()`.
- `offerStageBreak()` mirrors `offerCards()`'s DOM-overlay / headless-fallback split, but **schedules** the stage-advance via a `pendingStageAdvance` closure instead of mutating `enemies`/`bullets` synchronously — `killEnemy` runs the boss's death from inside the same-frame bullet/enemy iteration in `update()`, so wiping those arrays synchronously there corrupts the in-flight loop. `update(dt)` runs any pending advance as the very first thing each frame, before its own simulation loops touch those arrays.
- HUD: `STAGE n · name · WAVE n`, and a `NEXT GUARDIAN <n>s` / `GUARDIAN <hp>/<maxHp>` line replacing the old `SURVIVAL <time>` readout. Backdrop gradient drawn from `curStageCfg().bg`.
- Debug probes (`__swarmDbg`, `__hiveSwarmDebug`) expose `stage`, `stageT`, `stageBoss`, `stageName` for QA/harness use.

### Verification (2026-08-06)
`_stage_verify.js` (repo root, reuses the `_headless_harness.js` stub environment) drives a full run with real kiting input — no teleporting `elapsed` — and confirms:
- `stage 0 → 1` (Outskirts → Sewers) at ~61s, matching the 60s Outskirts budget.
- `stage 1 → 2` (Sewers → Downtown) at ~180s, matching 60 + 75s + a few seconds of guardian fight.
- Player survives both guardian fights and both reward picks (auto-applies the first stagebreak card, same convention `_headless_harness.js` uses for level-up cards).
- Existing `_headless_harness.js` 90s kite-survival gate still ends clean (`SIM ENDED clean`) with the new stage state present and not interfering.

### Not in this pass
- No dedicated FORGE `STAGES` table-editor tab (config is JSON-editable today via the existing DATA tab export/import).
- No unique boss sprite/attack pattern per guardian — it reuses the stage's strongest entity's sprite, scaled up.
- No stage-specific music/SFX swap.
