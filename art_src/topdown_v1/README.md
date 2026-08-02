# Top-down sprite set v1 — generated 2026-08-02

**8 GDD archetypes**, generated locally with **Krea 2 Turbo (NVFP4)** in ComfyUI at 512x512,
8 steps, ~12 s each — **96 s for the whole set, zero cloud cost.**

These are **source art, not shipping assets.** Still to do (M.2):
- alpha-key the near-black background and crop to content
- normalise scale per archetype against the GDD's threat weights
- pack into a sprite sheet the Forge entity table can reference

Prompt recipe is in `D:\Drive\AI\Memory\LOCAL_MODELS_TOC.md` under Krea 2. Regenerate with a new
seed rather than editing these by hand — it costs 12 s.

| File | GDD role |
|---|---|
| `shambler.png` | the mass — trivially killable, lethal in volume |
| `runner.png` | punishes standing still |
| `crawler.png` | punishes hugging the wall (lunge) |
| `brute.png` | moving wall, body-blocks projectiles |
| `armored_dead.png` | directional armour — rewards circling |
| `necro_node.png` | stationary spawner, priority target |
| `mutant_enforcer.png` | elite, leads the player's movement |
| `zombie_colossus.png` | wave-10 boss |
