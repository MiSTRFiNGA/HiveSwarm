# Sprite Framing Fix Log

**Date:** 2026-08-08 18:18 UTC
**Sprite dir:** `D:\Dev\HiveSwarm\art_src\topdown_v1`
**Backup dir:** `D:\Dev\HiveSwarm\art_src\topdown_v1\_bak_v030_framing`
**Alpha threshold:** 12

## Method

For each problem file: load peer walk dirs, compute median content height (alpha>12 bbox) of *other* walk directions, compare framing.
If under-framed (content height < 85% of peer median): per-frame scale so each cell content height matches target, center on peer canvas, transparent bg, magenta→transparent.
Walk strips treated as N equal-width frames (N=4 for 1024×256).
Color-only / pose-hash / expected aspect outliers are **not** recolored or re-authored — skipped when framing already matches peers.

## Per-file actions

### `mutant_enforcer_walk_s.png`

- **Reported issue:** under-framed content height ~136 vs ~230 peers
- **Before:** canvas=(1024, 256) content=(870, 136) meanRGB=(55.7, 41.8, 42.0) opaque=25744
- **Peer dir:** `n` canvas=(1024, 256)
- **Median content height (other walk dirs):** 236 (heights=[230, 236, 236, 230, 236, 230, 236])
- **Height ratio (self/median):** 0.576
- **Decision:** `FIX_SCALE`
- **Backup:** `D:\Dev\HiveSwarm\art_src\topdown_v1\_bak_v030_framing\mutant_enforcer_walk_s.png`
- **After:** content=(945, 236) meanRGB=(57.2, 43.9, 43.8) opaque=83670
- **Target height:** 236
- **Frames:** 4
  - frame 0: (102, 136) → scale 1.7353 → (177, 236) paste@(39, 10)
  - frame 1: (102, 136) → scale 1.7353 → (177, 236) paste@(295, 10)
  - frame 2: (102, 136) → scale 1.7353 → (177, 236) paste@(551, 10)
  - frame 3: (102, 136) → scale 1.7353 → (177, 236) paste@(807, 10)

### `zombie_colossus_walk_e.png`

- **Reported issue:** much darker mean RGB than other walk dirs
- **Before:** canvas=(1024, 256) content=(953, 230) meanRGB=(57.2, 55.7, 56.4) opaque=72020
- **Peer dir:** `w` canvas=(1024, 256)
- **Median content height (other walk dirs):** 236 (heights=[236, 230, 236, 230, 236, 230, 236])
- **Height ratio (self/median):** 0.975
- **Decision:** `SKIP_COLOR_NOT_FRAMING`
- **Rationale:** Content height already matches peer median (~230). Darker mean RGB is inherent palette/lighting difference, not under-framing. No recolor performed (out of framing scope).

### `zombie_colossus_walk_w.png`

- **Reported issue:** much darker mean RGB than other walk dirs
- **Before:** canvas=(1024, 256) content=(953, 230) meanRGB=(57.2, 55.7, 56.4) opaque=72020
- **Peer dir:** `e` canvas=(1024, 256)
- **Median content height (other walk dirs):** 236 (heights=[230, 236, 230, 236, 236, 230, 236])
- **Height ratio (self/median):** 0.975
- **Decision:** `SKIP_COLOR_NOT_FRAMING`
- **Rationale:** Content height already matches peer median (~230). Darker mean RGB is inherent palette/lighting difference, not under-framing. No recolor performed (out of framing scope).

### `shambler_walk_e.png`

- **Reported issue:** high hash distance vs set
- **Before:** canvas=(1024, 256) content=(957, 230) meanRGB=(36.0, 69.0, 60.7) opaque=43840
- **Peer dir:** `w` canvas=(1024, 256)
- **Median content height (other walk dirs):** 236 (heights=[236, 228, 236, 230, 236, 229, 236])
- **Height ratio (self/median):** 0.975
- **Decision:** `SKIP_HASH_POSE_NOT_FRAMING`
- **Rationale:** Content height/canvas already consistent with walk set. High aHash distance is pose/silhouette (side-view strip vs front/back), not scale framing.

### `shambler_walk_w.png`

- **Reported issue:** high hash distance vs set
- **Before:** canvas=(1024, 256) content=(957, 230) meanRGB=(36.0, 69.0, 60.7) opaque=43840
- **Peer dir:** `e` canvas=(1024, 256)
- **Median content height (other walk dirs):** 236 (heights=[230, 236, 228, 236, 236, 229, 236])
- **Height ratio (self/median):** 0.975
- **Decision:** `SKIP_HASH_POSE_NOT_FRAMING`
- **Rationale:** Content height/canvas already consistent with walk set. High aHash distance is pose/silhouette (side-view strip vs front/back), not scale framing.

### `crawler_walk_n.png`

- **Reported issue:** aspect swing cardinals vs diagonals (may be OK)
- **Before:** canvas=(1024, 256) content=(864, 230) meanRGB=(69.6, 79.8, 53.5) opaque=21958
- **Peer dir:** `s` canvas=(1024, 256)
- **Median content height (other walk dirs):** 232 (heights=[230, 235, 230, 232, 230, 236, 236])
- **Height ratio (self/median):** 0.991
- **Decision:** `SKIP_EXPECTED_ASPECT`
- **Rationale:** Cardinal vs diagonal aspect swing expected for elongated crawler body. Heights already ~230. No change.

### `crawler_walk_s.png`

- **Reported issue:** aspect swing cardinals vs diagonals (may be OK)
- **Before:** canvas=(1024, 256) content=(870, 230) meanRGB=(66.5, 72.3, 51.4) opaque=18472
- **Peer dir:** `n` canvas=(1024, 256)
- **Median content height (other walk dirs):** 232 (heights=[230, 235, 232, 230, 236, 230, 236])
- **Height ratio (self/median):** 0.991
- **Decision:** `SKIP_EXPECTED_ASPECT`
- **Rationale:** Cardinal vs diagonal aspect swing expected for elongated crawler body. Heights already ~230. No change.

### `crawler_walk_e.png`

- **Reported issue:** aspect swing / elongated body (may be OK)
- **Before:** canvas=(1024, 256) content=(1024, 230) meanRGB=(98.3, 89.9, 87.5) opaque=95466
- **Peer dir:** `w` canvas=(1024, 256)
- **Median content height (other walk dirs):** 232 (heights=[235, 230, 232, 230, 236, 230, 236])
- **Height ratio (self/median):** 0.991
- **Decision:** `SKIP_EXPECTED_ASPECT`
- **Rationale:** Cardinal vs diagonal aspect swing expected for elongated crawler body. Heights already ~230. No change.

### `crawler_walk_w.png`

- **Reported issue:** aspect swing / elongated body (may be OK)
- **Before:** canvas=(1024, 256) content=(1024, 230) meanRGB=(98.3, 89.9, 87.5) opaque=95400
- **Peer dir:** `e` canvas=(1024, 256)
- **Median content height (other walk dirs):** 232 (heights=[230, 235, 230, 232, 236, 230, 236])
- **Height ratio (self/median):** 0.991
- **Decision:** `SKIP_EXPECTED_ASPECT`
- **Rationale:** Cardinal vs diagonal aspect swing expected for elongated crawler body. Heights already ~230. No change.

## Files changed

- `mutant_enforcer_walk_s.png`

## Post-fix analysis

Re-ran `tools/analyze_enemy_sprites.py` after the framing pass. Reports refreshed:
- `D:\Dev\HiveSwarm\tools\sprite_direction_report.json`
- `D:\Dev\HiveSwarm\tools\sprite_direction_report.md`

### Outlier count comparison

| Enemy | Pre-fix outliers | Post-fix outliers | Improved? |
|---|---:|---:|---|
| `mutant_enforcer` | 1 (`walk_s` aspect) | **0** | **Yes** — under-framing cleared |
| `zombie_colossus` | 2 (`walk_e`, `walk_w` color) | 2 (same color flags) | No change (framing already OK; color not in scope) |
| `shambler` | 2 (`walk_e`, `walk_w` hash) | 2 (same hash flags) | No change (pose/silhouette, not scale) |
| `crawler` | 6 (aspect/hash) | 6 (same) | No change (expected elongated body) |

### `mutant_enforcer_walk_s` detail

| Metric | Before | After |
|---|---|---|
| Content size | 870×136 | **945×236** |
| Aspect (w/h) | 6.397 | **4.004** |
| Mean RGB | (56, 42, 42) | (58, 44, 44) |
| Opaque pixels | ~25.7k | ~83.7k |
| Flagged outlier? | Yes (aspect vs median=2.264) | **No** |
| Per-frame content | 102×136 ×4 | **177×236 ×4** |

Walk pairwise aspect is now in family with peers (peer walk aspects ~4.0–4.2). Analyzer notes for mutant_enforcer walk: *"directions consistent with single subject identity"*.

### Unchanged problem files (inspection only)

- **zombie_colossus walk_e/w** — content height 230 vs peer median 236 (ratio 0.975). Mean RGB ~(58,56,57) vs peers ~92–109 remains a palette/lighting mismatch; would need recolor/re-render, not bbox rescale.
- **shambler walk_e/w** — content height 230, canvas 1024×256 aligned with set. Hash distance is side-view silhouette vs n/s, not framing.
- **crawler cardinals** — content heights already ~230; aspect swing is body shape under different facings.

### Files overwritten

- `mutant_enforcer_walk_s.png` only

### Backups

- `D:\Dev\HiveSwarm\art_src\topdown_v1\_bak_v030_framing\mutant_enforcer_walk_s.png`

