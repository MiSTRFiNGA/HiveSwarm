# ⚒ THE FORGE STANDARD — how every empire game gets its editor

**Owner:** Eric (MiSTRFiNGA) · **Written:** 2026-08-01 · **Status:** canonical

Every game we build ships an internal editor called **`<Game> Forge`**. This document is the
contract, derived from the three that exist today — so the next one is right the first time.

| Game | Forge | Shape |
|---|---|---|
| HiVE WAR (`D:\Dev\HiveWar`) | HiVE FORGE | in-file IIFE, `⚒` button + F2 · units/weapons/bosses/world/sprites |
| Crypt Match (`D:\Dev\CryptMatch`) | CRYPT FORGE | in-file IIFE, `⚱` button + F2 · pieces/relics/levels/audio/data |
| Zelda (UE 5.8) | ZELDA FORGE (`D:\Dev\ZeldaForge`) | standalone Python app :8799 → UE Remote Control :30010 |

---

## 1. The two shapes

Pick by engine — do not invent a third.

**A. Single-file HTML5 game** → the Forge is an **IIFE inside `index.html`**, wrapped in
`try/catch` so a broken editor can never break the game. It shares the game's live arrays directly.

**B. Compiled/engine game (UE, etc.)** → the Forge is a **standalone app** that writes a data file
the game reads (`tunables.json`, `enemies.json`) plus a **live bridge** (UE Remote Control) for
things that only make sense against a running editor. The game must actually READ the file — a
Forge whose values the game ignores is a mock, not a tool.

---

## 2. Non-negotiables

### 2.1 Scope: data, art and audio — never behaviour
Names, numbers, colours, sprites, sounds, music, level targets, unlock gates: **editable**.
What a thing *does* (an ability's effect, an AI state machine) is **code**. Say so in the UI, in
one line, where the user would look for the knob. Do not fake a behaviour toggle that half-works.

### 2.2 Owner-only, never shipped to players
The opener is revealed only on the owner's own builds:

```js
const OWNER_BUILD = /^(localhost|127\.0\.0\.1|\[::1\]|)$/.test(location.hostname)
  || location.protocol === 'capacitor:' || location.search.includes('forge');
```

That covers local dev, `file://`, and the Android/Capacitor APK — and hides it on CrazyGames,
Poki and itch. The keyboard shortcut may stay live everywhere; a portal player will never press it.

### 2.3 Three ways in — always all three
1. **F2** (desktop),
2. a **visible button** in the game's own chrome (game-themed glyph, parked away from gameplay
   controls, `OWNER_BUILD` only),
3. a **press-and-hold gesture** (~700 ms) on an existing icon for phones/APK, where there is no F2.

A Forge with no button is a Forge that does not exist. (Learned the hard way on Crypt Match
2026-08-01 — it shipped F2-only and the owner could not find it.)

### 2.4 Live apply, no reload
Every edit lands on the running game immediately. If a roster can **shrink**, the apply step must
remap live state that points past the new end (Crypt Match remaps orphaned board tiles via
`t % TYPES`) — never leave a dangling index to crash a draw call.

### 2.5 Storage contract
- Keys: `<game>_forge_<domain>_v<N>` — separate keys for **values**, **art**, **audio**. One
  oversized sound must not be able to corrupt the values blob.
- Every write is `try/catch` with a **roll back on quota failure** and a plain-English alert
  ("Storage full — remove an imported sound first"), never a silent loss.
- Budget is ~5 MB of localStorage total. Downscale imported art to the size the game actually
  draws (128 px for a match-3 piece); warn above ~3 MB for audio.

### 2.6 BASE → EDIT → apply
```
CM_BASE  = deep copy of the shipped values, snapshotted BEFORE any override loads
CEDIT    = BASE + saved overrides (merge, don't replace — arrays that can grow must append)
cmApply() = writes CEDIT onto the live game arrays
```
RESET restores BASE. Without the pristine snapshot, "reset to defaults" resets to whatever was
edited last — the classic bug in this pattern.

### 2.7 DATA tab: export / import / reset
One JSON containing **values + art + audio**, so a backup is self-contained and moves machines.
Import merges through the same path as a saved blob. Reset asks once, then clears everything.

---

## 3. Standard tabs

Name them for the game's own vocabulary, but cover these roles:

| Role | Contents |
|---|---|
| **ROSTER** | The things the player sees most (pieces / units / enemies). Per row: **art thumbnail**, name, the 2–4 numbers that matter, colour, sound. Add/delete where the roster is dynamic. |
| **SPECIALS / WEAPONS** | The powers. Art, name, description text the game actually displays, sound, unlock gate. |
| **LEVELS** | Per-level targets, move/time budgets, spawn weights. Show the objective type as read-only context. |
| **AUDIO** | UI voices, an imported clip bank, and music (§5). |
| **WORLD** | Only where a game has environment art (HiVE WAR's per-level tiles). |
| **DATA** | Export / import / reset. |

Every tab opens with a `hint` line in plain English saying what the values do and what they do NOT
do. The Forge is the documentation.

---

## 4. Sprite editor (required wherever art exists)

**Clicking a thumbnail opens the editor** — never a blind file dialog. It must have:

- the art at **3×+ the in-game size**, on a **checkerboard** so transparency reads as transparency
  and not as black paint;
- **brush colour · brush size · erase · undo · clear**;
- **IMPORT PNG** (replaces wholesale, auto-downscaled to the cell size);
- **SAVE LIVE** — nothing touches the game until this is pressed;
- **REVERT TO SHIPPED** — drops the override, restores the repo asset;
- **DOWNLOAD PNG** — so a drawing can be baked into `assets/` and committed permanently.
- Animation strips (HiVE WAR) add frame thumbnails, ± frame, FPS. Single-image games skip these.

The download → drop into `assets/` → commit loop is what turns a local edit into a shipped one.
Say that in the UI.

---

## 5. Audio (required)

- **Imported clip bank** — the owner drops in mp3/ogg/wav, names it, and that name becomes valid
  in *every* sound field in the Forge. One bank, one namespace.
- **UI voices** — select / move / denied, blank = the shipped synth sound. Unknown names fall back
  to synth rather than silence.
- **Music** — plays during gameplay, stops on menus, with **its own mute button separate from the
  SFX mute** (`🔊` = effects, `🎵` = music, each remembering its own setting).
- The **default music is synthesised in-engine** (WebAudio drone + pattern), with editable
  tempo/key/volume. Costs the build nothing, works offline, and an imported track can replace it.
  Audio needs a user gesture before it can start — gate on the first pointer/key event.

---

## 6. QA (required)

A headless test file per game (`qa/test_forge.py`, Playwright) covering: opens clean with no page
errors, the button is visible on an owner build, each tab renders its controls, a roster add/delete
moves the live count, an edit reaches the live arrays, and the sprite editor saves and reverts.

This is not ceremony — it caught a load-order crash and a missing revert button on Crypt Match that
a syntax check could not see.

---

## 7. Build checklist

- [ ] Shape picked (§1) and the game genuinely reads the Forge's data
- [ ] BASE snapshot before overrides load; merge-not-replace; RESET verified
- [ ] Separate localStorage keys, quota rollback, art downscaled
- [ ] Three ways in; opener gated to owner builds
- [ ] Every tab has a plain-English hint, including what is NOT editable
- [ ] Sprite editor: 3× + checkerboard + paint/import/save/revert/download
- [ ] Audio: bank + UI voices + music with its own mute
- [ ] DATA export carries values + art + audio
- [ ] `qa/test_forge.py` green
- [ ] Live-apply verified on a running board, including a shrunk roster
