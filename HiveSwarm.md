---
type: game-documentation
title: HiVE SWARM
description: 360° top-down survivors-like — gameplay, enemies, weapons, change record and upgrade roadmap.
status: playable-in-development
tags: [game, hivemind, websgame, documentation]
---

# 🐝 HiVE SWARM

- **Master path:** `D:\Dev\HiveSwarm` — **edit here only**
- **Game file:** `index.html` — ONE ~210 KB single-file build (engine, art refs, FORGE, all of it)
- **Launcher:** `Launch HiVE Swarm.bat`
- **Genre:** 360° run-and-gun survivors-like. Reference APK: **Zombie Waves**.
- **⚠️ Not the same game as HiVE WAR** (`D:\Dev\HiveWar`), which is a LANE shooter. Eric saying
  "like hive war" means *borrow that behaviour*, not *edit that repo*.

---

## 🎮 Gameplay

Top-down arena survival. **Weapons fire automatically** — you only move (WASD / arrows / on-screen
stick) and choose upgrades. Enemies spawn **off-camera by construction** (outside the viewport
rect, not a fixed distance from the player) and walk in — and never in the direction you are
travelling (v0.6.0).

| System | How it works |
|---|---|
| **Stages** | Each stage = 3 waves + a Guardian (stage boss). Clear the boss → debrief → reward → next stage. |
| **Waves** | Kill-based, not timed. A wave has a finite spawn quota and only ends when every enemy it spawned is dead. A stall watchdog relocates **genuinely wedged** bodies (see v0.6.0) so a wave can't soft-lock. |
| **XP / levels** | Orbs drop from kills. Each level-up offers 3 cards. Multiple level-ups in one frame **queue** rather than stack overlays. |
| **Meta progression** | 3 save slots. Credits buy permanent damage/hp/speed/venom and unlock weapons in the Armory. |
| **Continues** | Limited per run; currently granted free — this is the single wiring point for a future rewarded-ad SDK (`PSDK.rewarded()`), deliberately not wired yet. |
| **FORGE** | Built-in editor (`hive_swarm_forge_values_v1` in localStorage) for tuning weapons, enemies, bosses, waves. Follows `FORGE_STANDARD.md`. |

## 👾 Enemies

Roster lives in the `ENEMIES` table in `index.html`, gated by `unlockWave`. Behaviours in play:

- **Chasers** (Shambler and family) — walk straight at the player; the bulk of every wave.
- **Static / node enemies** — don't chase; flagged by `isStaticEnemy()` and given an off-screen
  marker so a stage can never soft-lock on an unreachable target.
- **Stage Guardians (bosses)** — one per stage, `isBoss:true`. HP = base × `bossMul` × cycle scaling,
  85% knockback resistance, own FORGE slot in `EDIT.bosses` keyed by the stage's `bossId`.
  They spawn adds during the fight on their own budget, with a stall watchdog.
- **Status effects** — poison (`e.poisonT/poisonDps/poisonStacks`, incremental multiplicative
  stacking) and burn (`e.burnDps/e.burnT`, take-the-max). ⚠️ These deliberately use **separate
  fields**; they shared fields once and silently ate each other's damage.

## 🔫 Weapons

| Weapon | id | Kind | Damage | Rate | Range | Notes |
|---|---|---|---|---|---|---|
| Pulse Carbine | `weapon.pulse` | bullet | 18 | .16 | **100** | Starter, always owned |
| Seeker | `weapon.seeker` | homing | 22 | .38 | **900 (exempt)** | Armory 4. **The one weapon whose range never scales** |
| Flamethrower | `weapon.flame` | flame | 9 | .06 | **100** | Cone + burn DoT; `flameLength` tracks `range` |
| Toxin Injector | `weapon.poison` | poison | 6 | .5 | **100** | DoT + spread; targets *clean* enemies first |
| Breach Laser | `weapon.beam` | beam | 28 | .08 | **100** | Continuous ray, single-target king |
| **Storm Arc** | `weapon.chain` | chain | 22 | .32 | **100** | 4 jumps, −12% damage per jump |
| Nova Shell | `weapon.nova` | nova | 34 | .55 | **100** | Kill explosions spit mini reactor-stars |

> **Range is now authoritative for every kind** (v0.6.0). Before this, `range` only fed beam and
> chain — projectile weapons ignored it entirely and their reach was an accident of `speed × life`,
> so the FORGE `range` field was a lie for five of the seven guns. Bullets now retire once they have
> travelled `range` px.

**Weapon kinds matter.** `beam`/`chain`/`flame` are continuous and never fire discrete projectiles,
so Scatter / Pierce / Ricochet do not apply to them (enforced via each mod's `appliesTo`).

### Upgrade mods (`MODS`, max 3 stacks each)

`rapid` · `knockback` · `ricochet` · `overcharge` · **`longrange`** · `novastar` (nova) · `arcjump` (Storm Arc) ·
flame length/spread/napalm · plus run-scoped **skills** (fleet, bulk, magnet, shield, vampiric,
drone) and drone mods.

---

## 📝 Change record — 2026-08-12 (Claude)

Everything below is **done and verified**, with evidence in
[`C:\Users\MiSTRFiNGA\Desktop\Tests\HiveSwarm_0812\`](file:///C:/Users/MiSTRFiNGA/Desktop/Tests/HiveSwarm_0812/).

| # | Owner request | Status | What changed |
|---|---|---|---|
| 1 | Storm arc broken / invisible | ✅ **DONE** | Presentation fix — see the measurement below |
| 2 | Flame should start at top of the firing rectangle | ✅ **DONE** | Cone origin + damage cone moved to the barrel tip |
| 3 | All weapons shoot from the cannon tip | ✅ **DONE** | New `muzzle()` helper; bullets, beam, chain, flame all use it |
| 4 | Remove large/giant bullet upgrade | ✅ **DONE** | `Giant Rounds` removed from the pool; `wSizeMul()` returns 1 |
| 5 | Every upgrade turn needs ≥1 equipped-weapon option | ✅ **DONE** | New `rollChoices()`, used by level-up **and** stage reward |
| 6 | Stop showing all weapons at level end | ✅ **DONE** | Debrief lists only weapons you're actually holding |
| 7 | Stats fill the window at end of level | ✅ **DONE** | Panel fills the viewport; rows scale and centre |
| 8 | Boss 2× scale, boss fight only | ✅ **DONE** | `BOSS_FIGHT_SCALE=2` inside `spawnBossEnemy()` only |
| 9 | Poison bubbles ×2 and easier to see | ✅ **DONE** | Count doubled, ~70% bigger, alpha floor raised, dark rim added |
| 10 | This document | ✅ **DONE** | You're reading it |

### 🔍 The Storm Arc finding — read this before touching that weapon again

**Two previous passes retuned range and damage on feel alone** (280 → 150 → 240, damage 16 → 22).
This pass instrumented the game instead. Findings:

1. **Nothing fires for the first ~10 s of a stage.** Enemies spawn ~950 px out and walk in. That is
   not a Storm Arc bug — every short-range weapon is idle until they arrive.
2. **Range is almost irrelevant to that wait.** A/B on time-to-first-bolt:
   `range 241 → 11.0 s`, `range 340 → 10.4 s`. **A 41% range increase bought 0.6 seconds** because
   travel time dominates. The range was therefore left at **240** — a balance change that buys
   nothing is just drift.
3. **The real defect:** once engaged, bolts were on screen ~50% of samples with a **maximum of one
   concurrent bolt**, drawn with a 1.8 px core for 0.2 s. One thin bolt, half the time, in a busy
   fight is invisible — you only ever noticed the weapon when several bolts stacked, i.e. "when it
   chains 6 enemies", exactly as reported.

**Fix was presentational, not a buff.** `coreWidth` 1.8 → 3.4, `glowWidth` 12 → 15,
`glowIntensity` 1 → 1.15, bolt lifetime raised to the full fire interval (0.2 s → ~0.3 s), and an
impact spark added per link. **Damage, rate, range and jumps are untouched.**

⚠️ **Duty-cycle is a confounded metric here** — a longer range kills the pack sooner, which *lowers*
the fraction of frames with a live target. Use **time-to-first-bolt** if you measure this again.

### Verification performed

- Syntax: `node --check` on the extracted script — clean.
- Served over `http://127.0.0.1:8823` (never `file://` — that taints the canvas and silently breaks
  all FORGE save/undo).
- Playwright, real Chromium, **zero page errors** across every probe.
- Screenshots: Storm Arc chaining from the barrel tip, flame cone from the barrel, laser from the
  barrel, boss on screen at 2× next to normal enemies, poison cloud, debrief filling the window.
- Upgrade offers captured live — slot 1 was a Storm Arc mod on every offer (`Overcharge … — Storm Arc`).

### NOT done / not attempted

- ❌ No mobile/touch pass on the resized debrief panel — it was verified at 900×1000 desktop only.
- ❌ No APK rebuild. ⚠️ `art_src` **is runtime for HiveSwarm** (unlike HiveWar) — don't strip it.
- ❌ `_game_extract.js` was **not** regenerated; the headless harness evaluates that stale copy, so
  harness results will not reflect these changes until it's regenerated.
- ❌ Balance not re-tuned after the Giant Rounds removal — the offer pool is one card smaller.

---

## 📝 Change record — 2026-08-13 (Claude) · v0.6.0

| Owner request | Status | What changed |
|---|---|---|
| All weapons start at range 100; upgrades extend it; **homing exempt** | ✅ DONE | 6 of 7 guns ship `range:100`; `weapon.seeker` keeps 900 and ignores range upgrades |
| Upgrades must be **modular** — work at any base range I set | ✅ DONE | New **Long Barrel** mod is **multiplicative** (`+30% of the weapon's own base`, 3 stacks) |
| Enemies disappear and reappear elsewhere, especially large ones | ✅ DONE | The wave stall valve was relocating **the entire field every 11s**. Root-caused and fixed |
| A horde appears where I'm moving to instead of walking into frame | ✅ DONE | 57% of spawns landed within 30° of the travel direction. Now 0% within 60° |
| Movement feel knobs (drag / resistance) in FORGE | ✅ DONE | `accel` / `brake` / `friction` on the **FORGE → PLAYER** tab, live + persisted |
| Level-clear stats box 20% smaller, everything fits | ✅ DONE | `PANEL_SHRINK=.8`; removed the pitch/font floors that made overflow inevitable |

### 🎯 Range is multiplicative on purpose

The owner's requirement was *"make upgrades modular so no matter what number I set the range to for
the weapon, the upgrades work."* An **additive** `+150px` card silently fails that: at the shipped
100 baseline it is a +150% buff, but retune a gun to 600 in FORGE and the same card is a +25% nudge.
`RANGE_PER_STACK = .30` is a fraction of whatever `range` currently is, so a card is worth the same
**proportion** at any baseline. `wRange()` is the single source of truth — every reach in the game
(bullet travel, beam ray length, Storm Arc jump radius, flame cone) reads it.

The homing exemption is enforced **twice**: `appliesTo` keeps the card from being *offered* to the
seeker, and `wRange()` returns the flat base for `kind==='homing'` so a stack that reaches it some
other way (old save, FORGE preset) still has **no effect**.

**Old saves are migrated.** `forgeMerge()` keeps the saved row wholesale, so editing the shipped
table alone does nothing for an existing player — the same trap that resurrected the rocket
launcher. A migration walks each gun's range to 100 **only** when the saved value is still one of
that gun's known shipped defaults, so a hand-tuned FORGE number is never overwritten.

### 🐛 The stall valve was the "enemies disappear" bug — measured

`WAVE_STALL_T` fires when there has been **no KILL for 11s**, which is *not* the same as "the wave is
stuck". Two completely normal situations trip it:

* **Grinding a tanky body.** A Zombie Colossus is 1200 HP; a Guardian more. Chewing one at early-run
  DPS routinely exceeds 11s with zero kills — hence *"especially the larger enemies."*
* **Kiting.** Running while shooting means low DPS and few kills.

Once tripped, `stallCap` becomes `Infinity` as soon as the spawn quota drains, so it relocated
**every body on the field at once**. The earlier 2026-08-13 pass made this worse, not better: moving
stragglers **off-camera** (instead of the old 240–420px) is exactly what turned "they jump a bit"
into "they vanish and come back somewhere else".

**Reproduced and fixed** (40s probe, unkillable enemies, identical scenario both builds):

| Build | Teleports >300px | Pattern |
|---|---|---|
| v0.5.2 (before) | **27** | All 9 enemies relocated at once at t=10.2s, 21.2s, 32.2s — i.e. every `WAVE_STALL_T` |
| v0.6.0 (after) | **0** | — |

Two narrowing fixes, neither of which weakens the genuine soft-lock guard:

1. **Progress is measured as damage, not kills.** `waveStallHp` is a low-water mark of total live
   enemy HP; any dip resets the timer. Same technique the boss guard already used (`bossStallHp`).
2. **Only genuinely wedged bodies move.** `e.stuckT` counts seconds an enemy fails to *cover ground*
   relative to its own `speed`. This is deliberately **not** a distance-to-player test — a kiting
   player outruns the swarm, so "isn't getting closer" would flag every healthy chaser and blank the
   field for exactly the playstyle that reported the bug.

### 🐛 Spawns were steered into your path — measured

`spawnEnemy()`'s facing cone was only disabled for the first 45 seconds. After that, **65% of spawns
landed in a ±60° wedge centred on `player.angle`** — which is written from the movement input every
frame, so "facing" is literally "the direction you are running."

| Build | Spawns within 30° of travel | Within 60° |
|---|---|---|
| v0.5.2 (before) | **57.4%** | 61.7% |
| v0.6.0 (after) | **0%** | **0%** |

The wedge is now an **exclusion**: spawns are drawn from the full ring, and one landing dead ahead of
a *moving* player is pushed to the nearer edge. A stationary player has no travel direction, so the
ring stays uniform.

### ⚖️ Range 100 is NOT a difficulty regression — measured

8 headless runs per baseline (`_headless_harness.js`, 90s cap). Run-to-run variance is large, so
single runs are meaningless here — these are means:

| Starting range | Mean survival | Deaths |
|---|---|---|
| **100 (shipped)** | 69.8s | 5/8 |
| 200 | 86.4s | 2/8 |
| 300 | 87.6s | 1/8 |
| 500 | 88.7s | 2/8 |
| 760 (old pulse) | 63.0s | 5/8 |

Range 100 (69.8s) is **not worse** than the old shipped reach (63.0s). If you want it easier, the
measured sweet spot is **200–300** — one number per gun in FORGE → ENTITIES, and Long Barrel scales
off whatever you pick.

### 🕹️ Movement feel — FORGE → PLAYER

Movement used to write straight to position (`player.x += dir * speed * dt`): infinite acceleration,
instant dead stop, **no velocity to tune**, which is why there was nothing to expose. The pawn now
carries a velocity.

| Field | Default | Meaning |
|---|---|---|
| `accel` | 2600 | px/s² while a direction is held. High = arcade; low = heavy ramp-up |
| `brake` | 3400 | px/s² when **no** direction is held. High = stops dead; low = long coast |
| `friction` | 4 | Extra drag/sec **while coasting only**. 0 = pure linear brake |

Defaults are deliberately close to the old instant response (~0.09s to top speed) so this lands as a
tuning knob, not a stealth nerf. Measured: `accel 4000 / brake 6000 / friction 8` → full 245 px/s in
0.25s and a 2.5px coast; `accel 300 / brake 200 / friction 0` → 75 px/s and a 13.4px slide.

**`friction` is coast-only by design.** Applying drag every frame would fight `accel` and silently
cap top speed *below* `EDIT.player.speed`, so raising friction would quietly nerf the speed stat and
every Fleet Footed stack with it.

### 📐 Debrief panel

`PANEL_SHRINK = .8` on both axes, still centred; header/footer metrics scale with the panel via
`hs`. The real fit bug was the **floors**: pitch had a hard 22px floor and the font scale a hard 1.0
floor, so past ~14 rows the list drew straight off the bottom of the panel. Both removed — pitch is
now exactly `avail / rows`, which fits **by construction** at any panel size or row count. Verified
at 4 / 12 / 30 / 60 rows on desktop (1280×800) and mobile (400×860).

### 🧪 Verification

`qa/_verify_2026_08_13_changes.py` — Playwright probe, run against a local static server. Covers
shipped ranges, `wRange()` modularity at bases 100/250/600, the homing exemption, the FORGE movement
fields, debrief geometry, and the row-fit guarantee under stress. **ALL CHECKS PASSED** on desktop
and mobile. Screenshots in `Desktop\Tests\hiveswarm_2026_08_13\`.

> ⚠️ `_forge_stages_verify.js` fails with `TABS[5] !== STAGES`. **Pre-existing** — `STAGES` is at
> index 4 and the assertion was never updated. Confirmed failing on v0.5.2 too; not caused by this
> change set.

---

## 📝 Change record — 2026-08-13 (Claude) · v0.5.1

| Owner request | Status | What changed |
|---|---|---|
| Storm Arc at 200 length | ✅ DONE | Shipped `range` 240 → 200, with a migration step so old saves land on it |
| Remove rocket launcher | ✅ DONE | It was already deleted from source on 2026-08-08 — see the resurrection bug below |
| Enemies appear/reappear on top of the player | ✅ DONE | Two separate causes, both fixed |
| Larger stats on level clear | ✅ DONE | Debrief type scales with row pitch (~2× on a roomy screen) |

### 🐛 Retired content resurrects from localStorage — READ BEFORE DELETING ANY WEAPON/ENEMY

`weapon.rocket` was removed from the shipped table on 2026-08-08 (commit `1dde751`) and **was still
appearing in game five days later.** `forgeMerge()` is why:

```js
next[key] = saved[key].map(row => Object.assign({}, shipped.get(row.id)||{}, row))
```

It iterates the **saved** array. A row whose id no longer exists in `FORGE_BASE` falls back to `{}`
and the saved copy is kept wholesale — so **anything deleted from the shipped tables comes back from
localStorage on every load, forever, for anyone who played the old build.**

**Deleting content from source is not enough.** Add its id to `RETIRED_FORGE_IDS`; `pruneRetired()`
strips it from `EDIT` and re-persists, and `reset()` scrubs it from the save's `ownedWeapons` /
`startWeapon`. Verified with a poisoned save (rocket in FORGE + owned + set as start weapon): after
one load the FORGE list is clean, `ownedWeapons` is `['weapon.pulse']`, and `startWeapon` is reset.

### 🐛 Spawning on top of the player — quantified

1. `spawnEnemy()` computed `player + dir*distance` then **clamped to world bounds**. Near an edge the
   clamp eats the whole distance. Simulated at the cornered position a Playwright run actually
   reached (794, 1424): **minimum spawn distance 0px, and 28.3% of spawns within 100px of the
   player.** That is the bug, not bad luck.
2. The wave-stall watchdog **teleported stragglers to `rand(60,140)` of the player** with no
   telegraph — enemies materialising in your lap.

Both now go through `placeAwayFromPlayer(r, minD, maxD)`, which retries angles until the *clamped*
result still clears `minD` (half the screen diagonal for spawns, 240px for the stall valve) and
falls back to the farthest legal point when genuinely cornered. The stall valve also flashes a
`burst()` where each straggler lands. Verified in-game while cornered: worst observed spawn distance
**703px** vs a 673px off-camera threshold. `__swarmDbg().minEnemyDist` was added so this stays
regression-testable.

---

## 🗺️ Upgrade roadmap (future builds)

**P1 — correctness / polish**
1. Regenerate `_game_extract.js` so the headless harness tests the current build.
2. Re-check the debrief panel at phone aspect ratios (320/375 wide).
3. Storm Arc still peaks at **1 concurrent bolt** in open fights — the jump requires the next enemy
   within `range` of the *previous link*. Consider measuring jump-chain length and, if it's usually
   1, letting jumps 2..N use a slightly larger search radius than the first acquisition.

**P2 — content**
4. More Guardians with distinct attack patterns (they currently just chase with more HP).
5. Elite//modifier enemies (shielded, splitter, exploder).
6. A second upgrade axis so late-run picks aren't just "+22% again".

**P3 — shipping**
7. Wire the rewarded-ad SDK at the single `requestContinue()` hook.
8. Store art + APK build (`D:\Dev\_mobile\build_apk.ps1`), then portal submission.

---

## 🚧 Dev traps (learned the hard way)

- **Single file = NO parallel agents.** Fan-out on one 210 KB `index.html` stomps itself. Batch
  sequentially, verify with a separate adversarial pass.
- **Never open it as `file://`** — canvas taint makes all FORGE save/undo fail silently.
- **Never `git checkout --` `index.html`** — it's the whole game.
- **Serve on a fresh port and confirm you're getting YOUR file** (`curl | grep` a token you just
  added). A stale `http.server` squatting a port has served the wrong game before.
- **`window.__swarmDbg()` / `window.__hiveSwarmDebug()`** are the probe hooks; Playwright's
  `evaluate()` cannot see game-internal variables without them.
- Pausing to screenshot dims the whole screen — useless as visual proof. Screenshot live instead.
