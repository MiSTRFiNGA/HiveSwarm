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
| `praetorian` | 8/8 | 8/8 | strip | **in** | SE/SW copy S; NE/NW copy N. Old SE/NE stills were shattered claws. E/W remain the scythe profile. Queen out. |
| `psychoid` **NEW** | 1 pose × 8 dirs | 4-frame top-down | **in** | Overhead already. Same sprite all dirs. |
| `biomorph` **NEW** | E-facing + W flip | 4-frame side walk | **in** | One facing, then flip. Unlock 7. |
| `subterra_maw` | 1 pose × 8 dirs | 5-frame scan | **retired 0.6.4** | Owner: horrible. Files remain on disk. Not in roster / preload. |

---

## Defects that match what you saw

1. **Transparent / punched torso** — several sheets were magenta-keyed. Magenta is the FORGE key color (`#ff00ff`). Aggressive keying eats body pixels that were close to pink/purple (shambler slime, runner jacket). Runtime draw uses PNG alpha, not a live chroma key, so holes are *in the file*. **0.6.4:** leftover exact `#ff00ff` is gone. Interior islands were filled from `_bak_pre_magenta_20260807/` where that file matches. FORGE now has ALPHA KEY + rotate/dup/reorder. Remaining holes: paint them in FORGE.
2. **Different creature per angle** — Krea generated each dir as a new image, not a turnaround. Worst: Runner S (title card), Colossus E vs N, Crawler walk vs idle.
3. **Player never appears** — 8-dir sheets exist; the pawn is still the cyan circle. Separate draw bug, not missing files.

## Rebuild order (do not regenerate everything at once)

1. `runner_s` / `runner_e` title cards — **done 2026-08-22**. S walk frame 0 no longer headless. E idle no longer says HIVE ZOM.
2. `zombie_colossus` E/W — **done 2026-08-22** from the front tank body. SE/SW walk is still the skull-and-saw giant.
3. `player` — wire the existing sheet into `draw()` so the circle dies.
4. `praetorian` — real SE/SW/NE/NW + walk strips (not stills).
5. Then hole-pass: fill torso holes from `_bak_pre_magenta_20260807/` where those files are cleaner.

Queen stays out.

---

## Hive WAR import

| Character | Status |
|---|---|
| **Praetorian** | In as HiVE Core guardian. SE/SW unique as of 0.6.3. |
| **Psychoid / Biomorph** | In as `enemy.psychoid`, `enemy.biomorph`. |
| **Subterra Maw** | **Retired 0.6.4.** Do not re-add unless asked. |
| **Queen** | **Out.** Do not import. |
