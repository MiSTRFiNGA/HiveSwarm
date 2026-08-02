# HiVE SWARM

**Genre:** 360° run-and-gun survivors-like (open arena). **Not** a corridor / lane shooter.

Reference APK for *feel* only: `Zombie Waves.apk` (`D:\Dev\_ref\apks\`). Real War / Z Route inform **HiVE WAR**, not this title.

## This folder (post S.0 harvest)
- Forge v3 + entity table + WEAPONS + HiVE WAR media assets
- Temporary corridor host still in `index.html` for Forge QA — **quarantined**; replaced by Codex **S.3**
- See `design/HARVEST.md`

## Run Forge regressions
```powershell
cd D:\Dev\HiveSwarm
python -m unittest qa.test_forge_reference
```
Serve over HTTP (not `file://`). Default launch port will be set in S.5 (not 8791).
