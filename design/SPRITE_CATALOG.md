# HiVE SWARM — sprite catalog

**This is the inventory.** Product rules stay in [`../HiveSwarm.md`](../HiveSwarm.md).
Audited 2026-08-16 from `art_src/topdown_v1/`.

Need per stem: **base + 8 idle dirs + 8 walk strips (2+ frames)**, same character at every angle,
no baked titles, no holes through the torso.

Facing map (engine `FACE_SFX8`): `e se s sw w nw n ne`. **s = facing camera (front).**

---

## Cast (playable now)

| Stem | Idle | Walk | Walk frames | Verdict | Notes |
|---|---:|---:|---|---|---|
| `player` | 8/8 | 8/8 | strip | **identity drift + unused in-game** | North is a clean back view. Default/`e` is 3/4 side. **Gameplay still draws a cyan circle** — sheets exist and are not winning `draw()`. |
| `shambler` | 8/8 | 8/8 | strip | **usable** | Same punk-zombie across N/E. Magenta leftover in some files (editor key). |
| `runner` | 8/8 | 8/8 | strip | **angle broken** | `runner_s.png` has **baked "THE RUNNER" title** over the sprite. That angle will never match the others. |
| `crawler` | 8/8 | 8/8 | 4 | **usable, different species look** | Walk `e` is a skeletal quadruped — fine if that *is* the crawler, but it does not read as the same mesh as the idle standing pose. |
| `necro_node` | 8/8 | 8/8 | strip | **usable** | Stationary; walk dirs are mostly unused. |
| `brute` | 8/8 | 8/8 | strip | **usable** | Most consistent silhouette. |
| `armored_dead` | 8/8 | 8/8 | strip | **usable** | |
| `mutant_enforcer` | 8/8 | 8/8 | strip | **usable** | W view is a squat red brute — reads as the same unit. |
| `zombie_colossus` | 8/8 | 8/8 | strip | **angle drift** | Side (`e`) is a bone-saw profile; front/back are a different mass. Same name, two bodies. |
| `praetorian` | 6 unique / 2 fallback | S walk = 4-frame idle; SE/SW new | **in** | SE/SW rebuilt 2026-08-16. NE/NW still copy N. Queen out. |
| `psychoid` **NEW** | 1 pose × 8 dirs | 4-frame top-down | **in** | Overhead already. Same sprite all dirs. |
| `biomorph` **NEW** | E-facing + W flip | 4-frame side walk | **in** | One facing, then flip. Unlock 7. |
| `subterra_maw` **NEW** | 1 pose × 8 dirs | 5-frame scan | **in** | Static node. Mini-map pip leftover on some frames. |

---

## Defects that match what you saw

1. **Transparent / punched torso** — several sheets were magenta-keyed. Magenta is the FORGE key color (`#ff00ff`). Aggressive keying eats body pixels that were close to pink/purple (shambler slime, runner jacket). Runtime draw uses PNG alpha, not a live chroma key, so holes are *in the file*.
2. **Different creature per angle** — Krea generated each dir as a new image, not a turnaround. Worst: Runner S (title card), Colossus E vs N, Crawler walk vs idle.
3. **Player never appears** — 8-dir sheets exist; the pawn is still the cyan circle. Separate draw bug, not missing files.

## Rebuild order (do not regenerate everything at once)

1. `runner_s` — remove the title; match `runner_e` identity.
2. `zombie_colossus` — edit-chain side views from the front body, do not invent a second giant.
3. `player` — wire the existing sheet into `draw()` so the circle dies.
4. `praetorian` — real SE/SW/NE/NW + walk strips (not stills).
5. Then hole-pass: fill torso holes from `_bak_pre_magenta_20260807/` where those files are cleaner.

Queen stays out.

---

## Hive WAR import

| Character | Status |
|---|---|
| **Praetorian** | In as HiVE Core guardian. SE/SW unique as of 0.6.3. |
| **Psychoid / Biomorph / Maw** | In as `enemy.psychoid`, `enemy.biomorph`, `enemy.maw`. |
| **Queen** | **Out.** Do not import. |
