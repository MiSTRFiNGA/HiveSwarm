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
stick) and choose upgrades. Enemies spawn off-camera (~950 px out) and walk in.

| System | How it works |
|---|---|
| **Stages** | Each stage = 3 waves + a Guardian (stage boss). Clear the boss → debrief → reward → next stage. |
| **Waves** | Kill-based, not timed. A wave has a finite spawn quota and only ends when every enemy it spawned is dead. A stall watchdog drags blockers to the player so a wave can't soft-lock. |
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
| Pulse Carbine | `weapon.pulse` | bullet | — | — | — | Starter, always owned |
| Seeker | `weapon.seeker` | homing | — | — | — | Armory 4 |
| Flamethrower | `weapon.flame` | flame | 9 | .06 | 260 | Cone + burn DoT; ~59.8 sustained DPS |
| Toxin Injector | `weapon.poison` | poison | — | — | — | DoT + spread; targets *clean* enemies first |
| Breach Laser | `weapon.beam` | beam | 28 | — | 720 | Continuous ray, 84 DPS, single-target king |
| **Storm Arc** | `weapon.chain` | chain | 22 | .32 | 240 | 4 jumps, −12% damage per jump |
| Nova Shell | `weapon.nova` | nova | — | — | — | Kill explosions spit mini reactor-stars |

**Weapon kinds matter.** `beam`/`chain`/`flame` are continuous and never fire discrete projectiles,
so Scatter / Pierce / Ricochet do not apply to them (enforced via each mod's `appliesTo`).

### Upgrade mods (`MODS`, max 3 stacks each)

`rapid` · `knockback` · `ricochet` · `overcharge` · `novastar` (nova) · `arcjump` (Storm Arc) ·
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
