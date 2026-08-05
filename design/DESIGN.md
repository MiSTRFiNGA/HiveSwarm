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
