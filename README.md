# HiVE SWARM — v1.2-alpha

**Genre:** 360° run-and-gun survivors-like (open arena). **Not** a corridor / lane shooter.

Reference APK for *feel* only: `Zombie Waves.apk` (`D:\Dev\_ref\apks\`). Real War / Z Route inform **HiVE WAR**, not this title.

## This folder (post S.0 harvest)
- Forge v3 + entity table + WEAPONS + HiVE WAR media assets
- Temporary corridor host still in `index.html` for Forge QA — **quarantined**; replaced by Codex **S.3**
- See `design/HARVEST.md`

## Version / builds
- Web + APK build string: **`v1.2-alpha`** (shown under the title on the start/death screen,
  `<title>` tag, and `sw.js` `CACHE_VERSION = 'v2'` — bump both together).
- Signed APK: `Desktop\My Games\_APKs\HiveSwarm-1.2-alpha.apk` (26.6 MB, built 2026-08-03).
- Rebuild: `powershell -File D:\Dev\_mobile/build_apk.ps1 -Game HiveSwarm -Version 1.2-alpha`

## Forge open gesture (2026-08-03 fix)
The Forge opens **only** via the ⚒ button or **F2**. The old 700 ms canvas long-press trigger was
removed — it fired during normal hold-to-move / hold-to-fire play and yanked the player into the
editor mid-run (reported by Eric 2026-08-03, both touch and mouse).

## Run Forge regressions
```powershell
cd D:\Dev\HiveSwarm
python -m unittest qa.test_forge_reference
```
Serve over HTTP (not `file://`). Default launch port will be set in S.5 (not 8791).
