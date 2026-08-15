# HiVE SWARM — Asset Inventory (S.2)

> **Historical inventory (2026-08-02).** Current product status, play-feel, AI rules, and roadmap:
> [`D:\Dev\HiveSwarm\HiveSwarm.md`](file:///D:/Dev/HiveSwarm/HiveSwarm.md).

**Date:** 2026-08-02 · **Author:** Grok · **Scope:** HiveWar + CryptMatch + HiveSwarm harvest

Camera target for HiVE SWARM: **top-down / high-angle 360 arena** (survivors-like).
HiVE WAR art is **corridor 3/4 / rear-view** — most character sprites will read wrong from above.

## Summary counts

| Source | Media files |
|---|---|
| HiVE WAR (assets+sounds) | 85 |
| Crypt Match (assets+sounds) | 49 |
| HiveSwarm harvest (assets) | 81 |

## Legend

| Tag | Meaning |
|---|---|
| CARRY_AS_IS | Usable in 360 without redraw |
| REANGLE | Needs top-down / new facing sheet |
| REANGLE_OR_REPLACE | Corridor env — scrap or re-author for arena |
| OPTIONAL_THEME | Not required for combat; cosmetics only |
| NEW | Must author for SWARM (none shipped yet beyond harvest) |

## HiVE WAR

| Path | Ext | Bytes | Verdict | Why |
|---|---|---:|---|---|
| biomorph_a.png | .png | 85537 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| biomorph_b.png | .png | 79225 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| burrower.png | .png | 90135 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| cyber_a.png | .png | 96494 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| cyber_b.png | .png | 97414 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| cyber_idle.png | .png | 56787 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| eldritch.png | .png | 151845 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| eldritch_ooze.png | .png | 66635 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| env\L10_bg.png | .png | 298297 | **REVIEW** | Classify manually |
| env\L10_path.png | .png | 114352 | **REVIEW** | Classify manually |
| env\L10_side.png | .png | 355034 | **REVIEW** | Classify manually |
| env\L1_bg.png | .png | 724953 | **REVIEW** | Classify manually |
| env\L1_path.png | .png | 197716 | **REVIEW** | Classify manually |
| env\L1_side.png | .png | 199749 | **REVIEW** | Classify manually |
| env\L2_bg.png | .png | 349934 | **REVIEW** | Classify manually |
| env\L2_path.png | .png | 120203 | **REVIEW** | Classify manually |
| env\L2_side.png | .png | 84743 | **REVIEW** | Classify manually |
| env\L3_bg.png | .png | 1086400 | **REVIEW** | Classify manually |
| env\L3_path.png | .png | 173551 | **REVIEW** | Classify manually |
| env\L3_side.png | .png | 278918 | **REVIEW** | Classify manually |
| env\L4_bg.png | .png | 1096443 | **REVIEW** | Classify manually |
| env\L4_path.png | .png | 214818 | **REVIEW** | Classify manually |
| env\L4_side.png | .png | 289259 | **REVIEW** | Classify manually |
| env\L5_bg.png | .png | 387657 | **REVIEW** | Classify manually |
| env\L5_path.png | .png | 326320 | **REVIEW** | Classify manually |
| env\L5_side.png | .png | 173733 | **REVIEW** | Classify manually |
| env\L6_bg.png | .png | 523422 | **REVIEW** | Classify manually |
| env\L6_path.png | .png | 126722 | **REVIEW** | Classify manually |
| env\L6_side.png | .png | 197045 | **REVIEW** | Classify manually |
| env\L7_bg.png | .png | 259132 | **REVIEW** | Classify manually |
| env\L7_path.png | .png | 171368 | **REVIEW** | Classify manually |
| env\L7_side.png | .png | 291437 | **REVIEW** | Classify manually |
| env\L8_bg.png | .png | 189804 | **REVIEW** | Classify manually |
| env\L8_path.png | .png | 120128 | **REVIEW** | Classify manually |
| env\L8_side.png | .png | 324388 | **REVIEW** | Classify manually |
| env\L9_bg.png | .png | 281915 | **REVIEW** | Classify manually |
| env\L9_path.png | .png | 146776 | **REVIEW** | Classify manually |
| env\L9_side.png | .png | 196803 | **REVIEW** | Classify manually |
| env\shared\Tile_cyber01.png | .png | 7066325 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| env\shared\Tile_Hive01.png | .png | 281632 | **REVIEW** | Classify manually |
| env\shared\Wall_City01.png | .png | 192686 | **REVIEW** | Classify manually |
| env\shared\Wall_Hive01.png | .png | 307725 | **REVIEW** | Classify manually |
| icons\apple-touch-icon.png | .png | 35779 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-192.png | .png | 37852 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-512-maskable.png | .png | 140728 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-512.png | .png | 178878 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| parallax_city.png | .png | 199062 | **REANGLE_OR_REPLACE** | Corridor path/wall/bg — wrong for top-down arena (use as texture source or scrap) |
| perk_icons.png | .png | 128343 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| praet_attack.png | .png | 224225 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praet_death.png | .png | 202636 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praet_idle.png | .png | 188727 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praetorian.png | .png | 172914 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praetorian_hero.png | .png | 49529 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| psychoid.png | .png | 20955 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| psychoid_swim.png | .png | 86013 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| queen_hero.png | .png | 61921 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| SFX\Eggs Open.mp3 | .mp3 | 162168 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\eldritch sponge attack.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\eldritch sponge death.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\electric-explosive.mp3 | .mp3 | 56468 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\grenade.mp3 | .mp3 | 49781 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\light-machine-gun.mp3 | .mp3 | 93600 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\lightning01.mp3 | .mp3 | 56468 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\lightning02.mp3 | .mp3 | 63991 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\m41a-pulse-rifle.mp3 | .mp3 | 309120 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\magic-spell.mp3 | .mp3 | 52288 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\money.mp3 | .mp3 | 8821 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\praetorian01.mp3 | .mp3 | 153600 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\praetorian02.mp3 | .mp3 | 170496 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\subterrahit.mp3 | .mp3 | 14254 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\xeno attack.mp3 | .mp3 | 95232 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\xenotera hit.mp3 | .mp3 | 14672 | **CARRY_AS_IS** | SFX/music is view-independent |
| soldier_fire.png | .png | 61515 | **REANGLE** | Drawn for rear/front corridor view — needs top-down (or billboard) for 360 |
| soldier_front.png | .png | 73025 | **REANGLE** | Drawn for rear/front corridor view — needs top-down (or billboard) for 360 |
| subterra_scan.png | .png | 101093 | **REVIEW** | Classify manually |
| tank_front.png | .png | 263231 | **REANGLE** | Drawn for rear/front corridor view — needs top-down (or billboard) for 360 |
| tile_highway.png | .png | 333177 | **REANGLE_OR_REPLACE** | Corridor path/wall/bg — wrong for top-down arena (use as texture source or scrap) |
| weapon_icons.png | .png | 54857 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| winged.png | .png | 104866 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| xeno_walk.png | .png | 65407 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| xenoptera_fly.png | .png | 33006 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| electric-explosive.mp3 | .mp3 | 56468 | **CARRY_AS_IS** | SFX/music is view-independent |
| explosion-05.mp3 | .mp3 | 49781 | **CARRY_AS_IS** | SFX/music is view-independent |
| explosion.mp3 | .mp3 | 31808 | **CARRY_AS_IS** | SFX/music is view-independent |
| hit-flesh-01.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |

## Crypt Match

| Path | Ext | Bytes | Verdict | Why |
|---|---|---:|---|---|
| blackcat.png | .png | 13223 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| book.png | .png | 20523 | **OPTIONAL_THEME** | Crypt Match asset — theme reuse only |
| cauldron.png | .png | 19692 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| coffin.png | .png | 15285 | **OPTIONAL_THEME** | Crypt Match asset — theme reuse only |
| coin.png | .png | 28947 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| cross.png | .png | 10547 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| crossbones.png | .png | 15528 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| eyeball.png | .png | 24070 | **OPTIONAL_THEME** | Crypt Match asset — theme reuse only |
| eyecoin.png | .png | 29258 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| femur.png | .png | 7783 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| femur_alt.png | .png | 5245 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| fingerjar.png | .png | 12939 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| gem.png | .png | 22835 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| hand.png | .png | 11986 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| heart.png | .png | 22218 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| icons\apple-touch-icon.png | .png | 34658 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-192.png | .png | 36380 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-512-maskable.png | .png | 124465 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-512.png | .png | 155328 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| key.png | .png | 11899 | **OPTIONAL_THEME** | Crypt Match asset — theme reuse only |
| knife.png | .png | 4847 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| moon.png | .png | 23878 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| potion.png | .png | 12565 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| ribcage.png | .png | 28949 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| ripple.png | .png | 23206 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| skull.png | .png | 24312 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| title_logo.jpg | .jpg | 102705 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| voodoo.png | .png | 14494 | **OPTIONAL_THEME** | Match-3 piece art — only if HiVE SWARM wants crypt cosmetics; not core combat |
| angelical-synth.mp3 | .mp3 | 42675 | **CARRY_AS_IS** | SFX/music is view-independent |
| bone-crack.mp3 | .mp3 | 14254 | **CARRY_AS_IS** | SFX/music is view-independent |
| bone-snap.mp3 | .mp3 | 14672 | **CARRY_AS_IS** | SFX/music is view-independent |
| bone_crack.mp3 | .mp3 | 11493 | **CARRY_AS_IS** | SFX/music is view-independent |
| bottle-shatter.mp3 | .mp3 | 32226 | **CARRY_AS_IS** | SFX/music is view-independent |
| cat-meowing.mp3 | .mp3 | 20524 | **CARRY_AS_IS** | SFX/music is view-independent |
| cauldron-bubbling.mp3 | .mp3 | 25121 | **CARRY_AS_IS** | SFX/music is view-independent |
| clinking-coins.mp3 | .mp3 | 8821 | **CARRY_AS_IS** | SFX/music is view-independent |
| electric-explosive.mp3 | .mp3 | 56468 | **CARRY_AS_IS** | SFX/music is view-independent |
| electric46.mp3 | .mp3 | 63991 | **CARRY_AS_IS** | SFX/music is view-independent |
| evil_laugh.mp3 | .mp3 | 67948 | **CARRY_AS_IS** | SFX/music is view-independent |
| evil_laugh_over.mp3 | .mp3 | 258772 | **CARRY_AS_IS** | SFX/music is view-independent |
| explosion-05.mp3 | .mp3 | 49781 | **CARRY_AS_IS** | SFX/music is view-independent |
| explosion.mp3 | .mp3 | 31808 | **CARRY_AS_IS** | SFX/music is view-independent |
| glass-breaking.mp3 | .mp3 | 28465 | **CARRY_AS_IS** | SFX/music is view-independent |
| hit-flesh-01.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |
| hit-flesh-02.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |
| knife-stab.mp3 | .mp3 | 33062 | **CARRY_AS_IS** | SFX/music is view-independent |
| magic-spell.mp3 | .mp3 | 52288 | **CARRY_AS_IS** | SFX/music is view-independent |
| wolf-howl.mp3 | .mp3 | 54796 | **CARRY_AS_IS** | SFX/music is view-independent |
| wooden-doll.mp3 | .mp3 | 44640 | **CARRY_AS_IS** | SFX/music is view-independent |

## HiveSwarm harvest (same media as WAR seed)

| Path | Ext | Bytes | Verdict | Why |
|---|---|---:|---|---|
| biomorph_a.png | .png | 85537 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| biomorph_b.png | .png | 79225 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| burrower.png | .png | 90135 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| cyber_a.png | .png | 96494 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| cyber_b.png | .png | 97414 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| cyber_idle.png | .png | 56787 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| eldritch.png | .png | 151845 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| eldritch_ooze.png | .png | 66635 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| env\L10_bg.png | .png | 298297 | **REVIEW** | Classify manually |
| env\L10_path.png | .png | 114352 | **REVIEW** | Classify manually |
| env\L10_side.png | .png | 355034 | **REVIEW** | Classify manually |
| env\L1_bg.png | .png | 724953 | **REVIEW** | Classify manually |
| env\L1_path.png | .png | 197716 | **REVIEW** | Classify manually |
| env\L1_side.png | .png | 199749 | **REVIEW** | Classify manually |
| env\L2_bg.png | .png | 349934 | **REVIEW** | Classify manually |
| env\L2_path.png | .png | 120203 | **REVIEW** | Classify manually |
| env\L2_side.png | .png | 84743 | **REVIEW** | Classify manually |
| env\L3_bg.png | .png | 1086400 | **REVIEW** | Classify manually |
| env\L3_path.png | .png | 173551 | **REVIEW** | Classify manually |
| env\L3_side.png | .png | 278918 | **REVIEW** | Classify manually |
| env\L4_bg.png | .png | 1096443 | **REVIEW** | Classify manually |
| env\L4_path.png | .png | 214818 | **REVIEW** | Classify manually |
| env\L4_side.png | .png | 289259 | **REVIEW** | Classify manually |
| env\L5_bg.png | .png | 387657 | **REVIEW** | Classify manually |
| env\L5_path.png | .png | 326320 | **REVIEW** | Classify manually |
| env\L5_side.png | .png | 173733 | **REVIEW** | Classify manually |
| env\L6_bg.png | .png | 523422 | **REVIEW** | Classify manually |
| env\L6_path.png | .png | 126722 | **REVIEW** | Classify manually |
| env\L6_side.png | .png | 197045 | **REVIEW** | Classify manually |
| env\L7_bg.png | .png | 259132 | **REVIEW** | Classify manually |
| env\L7_path.png | .png | 171368 | **REVIEW** | Classify manually |
| env\L7_side.png | .png | 291437 | **REVIEW** | Classify manually |
| env\L8_bg.png | .png | 189804 | **REVIEW** | Classify manually |
| env\L8_path.png | .png | 120128 | **REVIEW** | Classify manually |
| env\L8_side.png | .png | 324388 | **REVIEW** | Classify manually |
| env\L9_bg.png | .png | 281915 | **REVIEW** | Classify manually |
| env\L9_path.png | .png | 146776 | **REVIEW** | Classify manually |
| env\L9_side.png | .png | 196803 | **REVIEW** | Classify manually |
| env\shared\Tile_cyber01.png | .png | 7066325 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| env\shared\Tile_Hive01.png | .png | 281632 | **REVIEW** | Classify manually |
| env\shared\Wall_City01.png | .png | 192686 | **REVIEW** | Classify manually |
| env\shared\Wall_Hive01.png | .png | 307725 | **REVIEW** | Classify manually |
| icons\apple-touch-icon.png | .png | 35779 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-192.png | .png | 37852 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-512-maskable.png | .png | 140728 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| icons\icon-512.png | .png | 178878 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| parallax_city.png | .png | 199062 | **REANGLE_OR_REPLACE** | Corridor path/wall/bg — wrong for top-down arena (use as texture source or scrap) |
| perk_icons.png | .png | 128343 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| praet_attack.png | .png | 224225 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praet_death.png | .png | 202636 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praet_idle.png | .png | 188727 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praetorian.png | .png | 172914 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| praetorian_hero.png | .png | 49529 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| psychoid.png | .png | 20955 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| psychoid_swim.png | .png | 86013 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| queen_hero.png | .png | 61921 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| SFX\Eggs Open.mp3 | .mp3 | 162168 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\eldritch sponge attack.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\eldritch sponge death.mp3 | .mp3 | 10911 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\electric-explosive.mp3 | .mp3 | 56468 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\grenade.mp3 | .mp3 | 49781 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\light-machine-gun.mp3 | .mp3 | 93600 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\lightning01.mp3 | .mp3 | 56468 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\lightning02.mp3 | .mp3 | 63991 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\m41a-pulse-rifle.mp3 | .mp3 | 309120 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\magic-spell.mp3 | .mp3 | 52288 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\money.mp3 | .mp3 | 8821 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\praetorian01.mp3 | .mp3 | 153600 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\praetorian02.mp3 | .mp3 | 170496 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\subterrahit.mp3 | .mp3 | 14254 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\xeno attack.mp3 | .mp3 | 95232 | **CARRY_AS_IS** | SFX/music is view-independent |
| SFX\xenotera hit.mp3 | .mp3 | 14672 | **CARRY_AS_IS** | SFX/music is view-independent |
| soldier_fire.png | .png | 61515 | **REANGLE** | Drawn for rear/front corridor view — needs top-down (or billboard) for 360 |
| soldier_front.png | .png | 73025 | **REANGLE** | Drawn for rear/front corridor view — needs top-down (or billboard) for 360 |
| subterra_scan.png | .png | 101093 | **REVIEW** | Classify manually |
| tank_front.png | .png | 263231 | **REANGLE** | Drawn for rear/front corridor view — needs top-down (or billboard) for 360 |
| tile_highway.png | .png | 333177 | **REANGLE_OR_REPLACE** | Corridor path/wall/bg — wrong for top-down arena (use as texture source or scrap) |
| weapon_icons.png | .png | 54857 | **CARRY_AS_IS** | UI/icon sheet — works at any camera |
| winged.png | .png | 104866 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| xeno_walk.png | .png | 65407 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |
| xenoptera_fly.png | .png | 33006 | **REANGLE** | Enemy/boss art authored for corridor perspective — top-down silhouette pass needed |

## Rollup

- **CARRY_AS_IS**: 74
- **OPTIONAL_THEME**: 23
- **REANGLE**: 46
- **REANGLE_OR_REPLACE**: 4
- **REVIEW**: 68

## Genuinely new (not in existing packs)

Nothing authored specifically for top-down SWARM yet. Expected NEW set after S.3 greybox:

- Survivor top-down idle/walk 4- or 8-dir
- Zombie archetypes top-down (fodder / tank / runner / spitter) 4-dir min
- Arena ground tiles + props (not corridor path strips)
- XP gem / magnet / chest pickups (icon-scale OK to draft from Crypt Match gems)
- Level-up card frame UI

## Recommendation

1. **Ship greybox with geometric placeholders** (S.3) — do not block on re-angles.
2. **Carry all SFX + weapon/perk icon sheets** immediately.
3. **Queue top-down enemy/player sheet** as the first art sprint after greybox feels right.
4. Corridor env (ssets/env/L*_*.png) stays available as **texture scrap**, not playable BG.