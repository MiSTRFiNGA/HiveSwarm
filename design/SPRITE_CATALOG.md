# HiVE SWARM — sprite catalog

**This is the inventory.** Product rules stay in [`../HiveSwarm.md`](../HiveSwarm.md).
Audited 2026-08-16 from `art_src/topdown_v1/`.

Need per stem: **base + 8 idle dirs + 8 walk strips + 8 attack strips (2+ frames)**, same character at every angle,
no baked titles, no holes through the torso.

**0.6.10:** H3 I2V harvest landed `{stem}_{walk|idle|attack}_{dir}.png` for the live roster. Engine uses idle when still, walk when moving, attack on contact. Twin Pod uses `player_idle.png`. Maw still retired.

Facing map (engine `FACE_SFX8`): `e se s sw w nw n ne`. **s = facing camera (front).**

---

## Cast (playable now)

| Stem | Idle | Walk | Walk frames | Verdict | Notes |
|---|---:|---:|---|---|---|
| `player` | Twin Pod hull + turret | rotate in draw | n/a | **in (0.6.5)** | Soldier 8-dir retired as the pawn. Live art is `player_hull.png` + `player_turret.png`. |
| `shambler` | 8/8 | 8/8 | strip | **usable** | Same punk-zombie across N/E. Magenta leftover in some files (editor key). |
| `runner` | 8/8 | 8/8 | strip | **usable** | S walk frame 0 was a headless torso — replaced 2026-08-22. E idle no longer has baked "HIVE ZOM" title. |
| `crawler` | 8/8 | 8/8 | 4 | **usable** | Unified 2026-08-22 to the skull-hopper. E/W are a two-leg hopper profile, not the old skeleton dog. |
| `necro_node` | 8/8 | 8/8 | strip | **usable** | Stationary; walk dirs are mostly unused. |
| `brute` | 8/8 | 8/8 | strip | **usable** | Most consistent silhouette. |
| `armored_dead` | 8/8 | 8/8 | strip | **usable** | |
| `mutant_enforcer` | 8/8 | 8/8 | strip | **usable** | W view is a squat red brute — reads as the same unit. |
| `zombie_colossus` | 8/8 | 8/8 | strip | **tank** | E/W tank profile. SE/SW copy the front tank walk (2026-08-22 live play). |
| `praetorian` | 8/8 | 8/8 | strip | **in** | **NE/NW true** 3/4 back walks (2026-09-11). **SE/SW still copies of S** (generated SE/SW shattered; reverted). E/W remain the scythe profile. Attack diagonals still copy S/N. Queen out. |
| `psychoid` **NEW** | 1 pose × 8 dirs | 4-frame top-down | **in** | Overhead already. Same sprite all dirs. |
| `biomorph` **NEW** | E-facing + W flip | 4-frame side walk | **in** | One facing, then flip. Unlock 7. |
| `subterra_maw` | 1 pose × 8 dirs | 5-frame scan | **retired 0.6.4** | Owner: horrible. Files remain on disk. Not in roster / preload. |

---

## Defects that match what you saw

1. **Transparent / punched torso** — several sheets were magenta-keyed. Magenta is the FORGE key color (`#ff00ff`). Aggressive keying eats body pixels that were close to pink/purple (shambler slime, runner jacket). Runtime draw uses PNG alpha, not a live chroma key, so holes are *in the file*. **0.6.4:** leftover exact `#ff00ff` is gone. **2026-09-11:** interior islands 2–400 px filled on 517 enemy sheets (nearest opaque). Remaining holes are **edge-connected** punch-throughs — paint in FORGE.
2. **Different creature per angle** — Krea generated each dir as a new image, not a turnaround. Worst remaining: Praetorian E/W scythe xeno vs S/N knight. Runner S title and crawler identity were fixed 2026-08-22.
3. **Player pawn** — Twin Pod hull + turret since 0.6.5. Soldier 8-dir sheets exist unused.

## Rebuild order (do not regenerate everything at once)

1. `runner_s` / `runner_e` title cards — **done 2026-08-22**. S walk frame 0 no longer headless. E idle no longer says HIVE ZOM.
2. `zombie_colossus` E/W — **done 2026-08-22** from the front tank body. SE/SW copy the front tank (0.6.24).
3. `player` — **done 0.6.5** Twin Pod. Cyan circle is fallback only.
4. `praetorian` NE/NW walks — **done 2026-09-11**. SE/SW still copies of S (shattered gens reverted). Attack diagonals still copy S/N. E/W still the scythe profile.
5. Hole-pass interior islands — **done 2026-09-11**. Edge-connected punch-throughs: FORGE paint.

Queen stays out.

---

## Hive WAR import

| Character | Status |
|---|---|
| **Praetorian** | In as HiVE Core guardian. SE/SW unique as of 0.6.3. |
| **Psychoid / Biomorph** | In as `enemy.psychoid`, `enemy.biomorph`. |
| **Subterra Maw** | **Retired 0.6.4.** Do not re-add unless asked. |
| **Queen** | **Out.** Do not import. |
