# 🧟 HiVE SWARM — Game Design Document

**Version:** 1.0 · **Author:** Claude (Opus 5) · **Date:** 2026-08-02
**Status:** ✅ Approved for build — this unblocks board row **S.3** (Codex)
**Board:** [`BOARD_2026-08-02_HIVESWARM.md`](file:///D:/Drive/AI/BOARD_2026-08-02_HIVESWARM.md) · **Protocol:** [`TEAM_PROTOCOL.md`](file:///D:/Drive/AI/Memory/TEAM_PROTOCOL.md)

---

## 1. 🎯 The one-sentence pitch

**You are one survivor in an open arena. You only steer — your guns fire themselves. The horde
closes from every direction, and every thirty seconds there is more of it than you can kill.**

**Genre:** survivors-like / bullet-heaven, roguelite run structure.
**Reference:** `Zombie Waves.apk` (study technique only — never its assets or code).
**Session length:** 8–12 minutes per run. **Platform:** mobile-first PWA + Android APK, portrait 540×960.

---

## 2. 🚫 What this game is NOT — the trap that already cost a scaffold

HiVE WAR is a **corridor lane shooter**. HiVE SWARM is **not**. None of this carries over:

| ❌ Do not port | Why it breaks the design |
|---|---|
| `e.lane`, `laneKeep`, `laneMargin` | There are no lanes. Enemies occupy continuous 2D space. |
| `HORIZON_Y`, `drawPerspectiveRoad`, `roadHalfWidthAtY` | There is no horizon and no road. The camera looks **straight down**. |
| Gate / barrier / weapon-pickup walls | Progression is level-up cards, not gates. |
| Forward auto-scroll | The player moves freely; the *world* does not move on rails. |

✅ **What does carry over:** art and audio, the `WEAPONS` definitions, the Forge v3 entity table,
the media/IndexedDB layer, `build.py`, the harness, and the PWA/APK toolchain.

---

## 3. 🎥 Camera & space

- **Top-down orthographic.** No perspective, no vanishing point. A sprite at the top of the screen
  is drawn at the same scale as one at the bottom.
- **Arena is larger than the viewport** — 3× viewport in each axis (≈1620×2880 world units).
  Bounded, not infinite: the player can be cornered, and cornering yourself is a real mistake.
- **Camera follows the player with a soft lag** — `cam += (target - cam) * 0.12` per frame — and
  **clamps to the arena edge** so the player walks toward the border rather than the world sliding.
- **A dead zone of ~15 % of the viewport** in the middle: small movements don't shove the camera.
- **Off-screen threat indicators.** Any elite or boss outside the viewport gets an arrow pinned to
  the screen edge. Without this, death from off-screen feels unfair — with it, it's a warning ignored.

---

## 4. 🕹 Control & the auto-fire contract

**The player has exactly one input: a direction.** Virtual thumbstick on mobile (floating origin
where the thumb lands), WASD/arrows on desktop. **No aim, no fire button, no dodge button.**

**Auto-fire rule:** each weapon independently fires on its own cooldown at the **nearest enemy in
range**, ties broken by lowest health. If nothing is in range, it does not fire (no wasted cooldown).

> ⚖️ **The design consequence — this is the whole game.** Because aim is automatic, **positioning is
> the only skill.** Every difficulty knob must therefore be a *spatial* one: where enemies come from,
> how fast they close, how much open floor is left. Never make the game harder by shrinking the
> auto-aim's accuracy — that punishes the player for something they don't control.

---

## 5. 🧟 The swarm — behaviour is the product

**Feel target:** *pressure, not puzzles.* The horde should feel like weather. The player is always
being pushed somewhere, and the fun is in choosing where.

### Enemy archetypes

Names come from the harvested entity table. Every value below is **Forge data, not code** (§9).

| Archetype | Behaviour | Speed | Role in the pressure curve |
|---|---|---|---|
| **Shambler** | Direct seek, no avoidance | 0.55× player | The mass. Trivially killable, lethal in volume. |
| **Runner** | Direct seek, accelerates in a straight line when >250 units away | 1.15× player | Punishes standing still. Forces the player to keep moving. |
| **Crawler** | Seeks, then **lunges** a fixed distance on a 3 s telegraph | 0.8× / 2.5× lunge | Punishes hugging the wall — the lunge closes the gap you thought was safe. |
| **Brute** | Slow, high HP, **body-blocks** projectiles | 0.4× | A moving wall. Reshapes the arena, doesn't threaten directly. |
| **Armored Dead** | Directional armor — takes 15 % from the front, 100 % from behind | 0.5× | Rewards circling; the first enemy that teaches orbiting. |
| **Necro Node** | **Stationary.** Spawns 1 Shambler every 4 s until killed | 0 | A priority target. Creates a reason to *leave* a safe pocket. |
| **Mutant Enforcer** | Elite. Ranged spit, leads the player's movement | 0.7× | The first enemy that punishes predictable pathing. |
| **Zombie Colossus** | Boss. Slow, huge HP, ground-slam AoE with a 1.5 s telegraph | 0.35× | Wave-10 gate. |

### Swarm rules

1. **Flocking separation, no formation.** Enemies push each other apart at close range
   (`separation radius ≈ 0.8 × sprite width`) so a mass reads as a *crowd*, not a stack of sprites
   at one pixel. This single rule does more for the swarm feel than any other.
2. **Spawn off-screen only**, on a ring 1.25× the viewport diagonal, **weighted toward the player's
   facing direction (60 %)** so running forward has a cost. Never spawn inside the viewport — an
   enemy popping into existence next to the player is the #1 unfairness complaint in this genre.
3. **Soft cap of 220 concurrent enemies** (mobile perf ceiling — see §11). When at cap, spawn budget
   converts into **upgrading pending spawns to stronger archetypes** rather than dropping them. The
   pressure curve continues; the entity count does not.
4. **Corpses persist ~4 s** as flat decals, then fade. Free visual proof of the player's damage output.

---

## 6. 📈 The wave curve — 12 minutes, one shape

Time-based, not kill-based. A wave is 30 seconds. **Run length target: 10 minutes (20 waves).**

| Phase | Waves | Time | What happens | Player feeling |
|---|---|---|---|---|
| **Breathe** | 1–3 | 0:00–1:30 | Shamblers only. Spawn rate low. First level-up at ~0:20. | "I'm strong." |
| **Learn** | 4–7 | 1:30–3:30 | Runners, then Crawlers. First Necro Node at wave 6. | "I have to keep moving." |
| **Squeeze** | 8–12 | 3:30–6:00 | Brutes + Armored Dead. Density doubles. **Colossus at wave 10.** | "I'm managing, barely." |
| **Break** | 13–17 | 6:00–8:30 | Mutant Enforcers. Multiple Nodes. Open floor genuinely shrinks. | "I need the right card." |
| **Overrun** | 18–20 | 8:30–10:00 | Everything at once, elites stacked. **Designed to be lost.** | "How far can I get?" |

**Spawn budget formula** (Forge-tunable): `budget(t) = 4.0 × 1.11^wave` enemy-points per second, where
each archetype costs points equal to its threat weight. **One curve, one exponent** — resist adding
per-archetype curves; they make the game impossible to reason about or retune.

**Difficulty band:** a competent human should reach **wave 14–17 (7–8.5 min)** on their third run.

> 🔴 **Calibrate to a HUMAN from day one.** HiVE WAR was tuned to a bot, and we still don't know
> whether the shipped build is the right difficulty. Do not repeat that. The telemetry bot is a
> **regression guard** — it proves the build didn't get *accidentally* harder or easier between
> commits. It is **not** the acceptance target. Acceptance is Eric playing 3 runs.

---

## 7. 🎴 Level-up cards — the run's identity

XP drops from every kill and auto-collects within a **pickup radius** (an upgradeable stat — its
first upgrade feels enormous, which makes it a great early card).

**On level-up: time freezes, 3 cards from a weighted pool, player picks 1.** Roughly 12–16 level-ups
per full run, so the player sees maybe a third of the pool — **that's the replay value.**

Card categories, and why each exists:

| Category | Examples | Design purpose |
|---|---|---|
| **New weapon** (max 5 held) | Shotgun cone, orbital drone, ground mines, chain lightning | Changes *where* you can safely stand |
| **Weapon rank** | +damage / −cooldown / +pierce on a held weapon | Depth over breadth; rewards commitment |
| **Survivor stat** | +move speed, +max HP, +pickup radius, +armor | Small, always-useful, never exciting — the filler that makes the good cards feel good |
| **Evolution** *(wave 10+)* | Two maxed weapons fuse into one signature weapon | The "build came together" moment. **One per run maximum.** |

**Three rules that keep the pool honest:**
1. **Never offer a strictly-worse duplicate.** If a weapon is maxed, its rank card leaves the pool.
2. **Guarantee at least one weapon card** in the first three level-ups, or a player can stat-drift
   into an unwinnable run through no fault of their own.
3. **No card may be a trap.** Every card must be defensible; a survivors-like dies when players learn
   that some picks are wrong.

**Between runs:** persistent meta-upgrades bought with a soft currency that drops from elites and
the Colossus. Meta should shorten the grind to a *strong start*, never exceed **+25 % total power** —
past that the game balances itself around the meta and new players get an unwinnable curve.

---

## 8. ☠️ Win / lose

- **Lose:** HP hits 0. Run ends, currency banks, score = time survived + kills. **No mid-run revive.**
- **Win:** there is no win. **Wave 20 is the intended wall**, and the run continues past it with the
  curve still climbing so leaderboard chasers have somewhere to go.
- **Death must be readable.** Show the killing enemy type and the last 3 seconds of incoming damage
  on the death card. A survivors-like player needs to know *what* they misplayed.

---

## 9. 🔨 Forge-first — the acceptance test for the whole programme

**Every value in this document is Forge data.** No exceptions, no "temporary" hardcoding.

The Forge entity table must own: enemy stats (hp / speed / damage / threat weight / behaviour enum),
the spawn budget curve and per-wave archetype unlocks, weapon definitions (damage / cooldown / range /
projectile count / spread / pierce), the card pool and its weights, meta-upgrade costs and caps, and
arena size + camera constants.

> ✅ **The acceptance test (board S.4):** *Eric must be able to add a new enemy type, give it art, put
> it in the wave curve, and play against it — using only the Forge, with no code change and no agent
> involved.* If standing up HiVE SWARM needs code from Claude rather than Forge edits, **the Forge
> template isn't finished** — and that's a finding to report, not a thing to work around.

---

## 10. 🎨 Art direction & the re-angle problem

Reskin of HiVE WAR's cyber-xeno palette into a **decayed-urban zombie** register: desaturated
concrete and rust, sodium-orange pooled lighting, blood and viscera as the only saturated color on
screen so damage reads instantly.

> ⚠️ **The known asset risk — flagged for board row S.2.** HiVE WAR's sprites are drawn for a
> corridor's **3/4 view**. Seen from **directly above**, most of them will read wrong: you'll see the
> front of a soldier's chest where you should see the top of their head. **Assume the character and
> enemy sprites need re-angling, and that only the effects, UI, icons, and audio port cleanly.**
> The inventory must state this per-asset rather than assuming reuse.

**Ports cleanly:** all SFX and music, weapon/perk icons, particle and muzzle effects, HUD, damage
numbers, the Forge UI. **Needs re-angle:** every character and enemy sprite, all environment tiles.

---

## 11. ⚙️ Performance budget — mobile is the constraint

Target **60 fps on a mid-range Android** at 540×960.

| Budget | Limit |
|---|---|
| Concurrent enemies | 220 soft cap (§5.3) |
| Concurrent projectiles | 400 |
| Particles | 300 |
| Frame time | 16.6 ms — **enemy update+draw ≤ 8 ms** |

**Required from the first commit, not retrofitted:**
- **Object pools** for enemies, projectiles, particles, damage numbers. Zero per-frame allocation in
  the hot loop — GC pauses are the #1 cause of stutter in a JS game at this entity count.
- **Spatial hash grid** (cell ≈ 64 units) for collision and nearest-target queries. At 220 enemies ×
  400 projectiles, naive O(n²) is 88,000 checks/frame and will not hold 60 fps.
- **Fixed timestep simulation at 1/60 s** with a decoupled render, so balance is reproducible across
  machines and the telemetry bot's numbers mean something.
- **Draw enemies in one batched pass** sorted by sprite, minimising canvas state changes.

---

## 12. 🚧 Build order for S.3 — ship it grey first

1. **Grey box:** arena, player circle, thumbstick, camera follow + clamp. *Verify: you can walk to
   all four corners and the camera clamps.*
2. **One enemy, one weapon:** Shamblers seek, auto-fire kills them, pools + spatial hash in from the
   start. *Verify: 200 spawned enemies hold 60 fps.*
3. **XP, level-up freeze, 3-card pick** with 5 placeholder cards.
4. **Wave curve + remaining archetypes**, all from Forge data.
5. **Colossus, death card, meta-upgrades.**
6. **Art pass** (needs S.2's inventory), then telemetry + APK.

**Do not add art before step 6.** Grey-box feel is the acceptance gate — if it isn't fun as circles,
art will not save it, and every art change after that point costs double to re-verify.

---

## 13. ❓ Open questions for Eric — not blockers, defaults are chosen

| # | Question | **Default if you don't answer** |
|---|---|---|
| Q1 | Arena — a single bounded rectangle, or destructible cover / obstacles in it? | **Bounded rectangle, no obstacles** for v1. Obstacles interact badly with auto-aim and body-blocking Brutes. |
| Q2 | Alien Queen (board E.4) — does she belong here as a late boss, or stay in HiVE WAR? | **Here, as the wave-20 boss.** Her eggs/hatchlings mechanic is a *swarm* mechanic and fits this game far better than a corridor. `Eggs Open.mp3` finally gets used. |
| Q3 | Multiple playable survivors with different starting weapons? | **One survivor for v1.** Ship, then add characters as the first content update. |
