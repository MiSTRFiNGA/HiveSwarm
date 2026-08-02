# S.0 Harvest note — ZombieWaves → HiveSwarm (2026-08-02)

## Taken (product value)
- `assets/` — 82 media files (HiVE WAR seed set)
- Forge v3 UI + entity registry + WEAPONS block
- `FORGE_STANDARD.md`, `FORGE_TEMPLATE_V3.md`
- `qa/test_forge_reference.py` (storage keys → `hive_swarm_*`)

## Explicitly NOT the product
Corridor systems remain in `index.html` **quarantined** as a temporary Forge host until Codex S.3:
- `drawPerspectiveRoad`, `HORIZON_Y`, `roadY`, `roadHalfWidth`, `roadHalfWidthAtY`
- `e.lane` / lane-relative enemy motion
- gate/barrier pair spawn

**Do not** build 360° survivors features on those APIs. S.3 ships a clean arena.

## Left in place
`D:\Dev\ZombieWaves` — deletion is Eric decision **E.1**.
