# Build collaborative sprite pack (no node-canvas required)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$Root = 'D:\Dev\HiveSwarm'
$Src  = Join-Path $Root 'art_src\topdown_v1'
$Bak  = Join-Path $Src  '_bak_pre_magenta_20260807'
$Out  = Join-Path $Root 'sprite_edit_pack'
$Desk = Join-Path $env:USERPROFILE 'Desktop\HiveSwarm_sprite_edit_pack'
$Stems = @('player','shambler','runner','crawler','necro_node','brute','armored_dead','mutant_enforcer','zombie_colossus')
$Dirs  = @('e','se','s','sw','w','nw','n','ne')
$Cell = 128

function Ensure-Dir($p) { New-Item -ItemType Directory -Force -Path $p | Out-Null }
function Copy-Pngs($from, $to) {
  if (-not (Test-Path $from)) { return 0 }
  Ensure-Dir $to
  $n = 0
  Get-ChildItem $from -Filter *.png -File | ForEach-Object {
    Copy-Item $_.FullName (Join-Path $to $_.Name) -Force
    $n++
  }
  return $n
}

Ensure-Dir $Out
$rawCur = Join-Path $Out 'raw_current'
$rawBak = Join-Path $Out 'raw_pre_magenta_backup'
$sheets = Join-Path $Out 'character_sheets'
Ensure-Dir $rawCur; Ensure-Dir $rawBak; Ensure-Dir $sheets

# copy all current (including walk dirs) recursively without _bak folders
function Copy-TreePng($from, $to) {
  if (-not (Test-Path $from)) { return 0 }
  $n = 0
  Get-ChildItem $from -Recurse -Filter *.png -File | Where-Object {
    $_.FullName -notmatch '\\_bak'
  } | ForEach-Object {
    $rel = $_.FullName.Substring($from.Length).TrimStart('\')
    $dest = Join-Path $to $rel
    Ensure-Dir (Split-Path $dest)
    Copy-Item $_.FullName $dest -Force
    $n++
  }
  return $n
}

$n1 = Copy-TreePng $Src $rawCur
$n2 = if (Test-Path $Bak) { Copy-Pngs $Bak $rawBak } else { 0 }

function Load-Img($path) {
  if (-not (Test-Path $path)) { return $null }
  return [System.Drawing.Image]::FromFile($path)
}

function Draw-FirstFrame($g, $img, $dx, $dy, $cell) {
  if (-not $img) { return }
  $nf = 1
  if ($img.Width -ge $img.Height * 1.6) {
    $nf = [Math]::Max(1, [Math]::Round($img.Width / $img.Height))
  }
  $fw = [int]($img.Width / $nf)
  $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
  $g.DrawImage($img, (New-Object System.Drawing.Rectangle $dx,$dy,$cell,$cell),
    0, 0, $fw, $img.Height, [System.Drawing.GraphicsUnit]::Pixel)
}

$sheetCount = 0
foreach ($stem in $Stems) {
  $w = $Cell * 8
  $h = $Cell * 2 + 32
  $bmp = New-Object System.Drawing.Bitmap $w, $h
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.Clear([System.Drawing.Color]::FromArgb(255, 26, 16, 24))
  $font = New-Object System.Drawing.Font 'Consolas', 10
  $brush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 111, 255, 226))
  $g.DrawString("$stem  top=idle 8-dir  bottom=walk first-frame", $font, $brush, 6, 6)
  $labelBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 136, 170, 187))
  $boxBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(255, 42, 32, 48))

  for ($i = 0; $i -lt 8; $i++) {
    $d = $Dirs[$i]
    $g.FillRectangle($boxBrush, $i * $Cell, 28, $Cell, $Cell)
    $g.FillRectangle($boxBrush, $i * $Cell, 28 + $Cell, $Cell, $Cell)
    $g.DrawString($d, $font, $labelBrush, $i * $Cell + 4, 16)

    $idlePath = Join-Path $Src "${stem}_${d}.png"
    if (-not (Test-Path $idlePath)) { $idlePath = Join-Path $Src "$stem.png" }
    $walkPath = Join-Path $Src "${stem}_walk_${d}.png"
    if (-not (Test-Path $walkPath)) { $walkPath = Join-Path $Src "${stem}_walk.png" }

    $imI = Load-Img $idlePath
    $imW = Load-Img $walkPath
    try {
      Draw-FirstFrame $g $imI ($i * $Cell) 28 $Cell
      Draw-FirstFrame $g $imW ($i * $Cell) (28 + $Cell) $Cell
    } finally {
      if ($imI) { $imI.Dispose() }
      if ($imW) { $imW.Dispose() }
    }
  }

  $outPng = Join-Path $sheets "${stem}_sheet.png"
  $bmp.Save($outPng, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose()
  $font.Dispose(); $brush.Dispose(); $labelBrush.Dispose(); $boxBrush.Dispose()
  $sheetCount++
  Write-Host "sheet $stem"
}

$readme = @"
# HiVE SWARM sprite edit pack
Generated: $(Get-Date -Format o)

## Folders
- **raw_current/** — every current PNG under art_src/topdown_v1 ($n1 files)
- **raw_pre_magenta_backup/** — pre-magenta-key backup ($n2 files)
- **character_sheets/** — one atlas per cast: top idle 8-dir, bottom walk first-frame ($sheetCount sheets)

## How we collaborate
1. Edit sheets or individual raw PNGs in Photoshop / Aseprite / Photopea.
2. Drop fixed files back into ``art_src/topdown_v1/`` with the same names, OR
   import in Forge: ENTITIES → click walk still → IMPORT → SAVE.
3. Tell the agent which stem + direction you fixed (e.g. shambler walk_e).

## Naming
- idle: ``{stem}.png``, ``{stem}_e.png`` … ``{stem}_ne.png``
- walk: ``{stem}_walk_e.png`` … (wide horizontal strip = multi-frame)

## Stems
$($Stems -join ', ')
"@
Set-Content -Path (Join-Path $Out 'README.md') -Value $readme -Encoding UTF8

# Mirror to Desktop
if (Test-Path $Desk) { Remove-Item $Desk -Recurse -Force }
Copy-Item $Out $Desk -Recurse -Force

Write-Host "Pack: $Out"
Write-Host "Desktop: $Desk"
Write-Host "raw_current=$n1 backup=$n2 sheets=$sheetCount"
