# Reference Teardown: Zombie Waves — Store, Meta, and Stage Structure

**APK analyzed:** `D:\Dev\_ref\apks\Zombie Waves.apk` (package `com.ddup.zombiewaves.zw`, billing client v8.3.0, ~25 MB on disk)
**Method:** Unzipped as a plain zip archive (`D:\Dev\_ref\apks\zombie_waves_extract\`); inspected `AndroidManifest.xml`, `res/`, `assets/`, `billing.properties`, and mediation metadata. No DEX decompilation performed, per instructions.

## Important caveat — what the APK actually contains

This APK is a **Unity** build (`assets/bin/Data/Managed/` present), but the folder is otherwise empty except a `.keep_folder` placeholder — there is no `data.unity3d` / asset-bundle payload, and there is **no `lib/` folder at all** (no `libil2cpp.so`, no `libunity.so`). This is the **base split** of the app; the real game code, art, and UI (where the shop/meta/stage screens actually live) ship in separate asset packs / config splits that aren't in this file. `res/drawable` (270 files) is 100% generic third-party SDK chrome — AppLovin MAX, AdMob, AIHelp in-app support chat — not game art.

**What we could reliably extract locally:**

| Signal | Finding |
|---|---|
| Monetization SDKs | AppLovin MAX (with mediation adapters for AdMob, Meta/Facebook, ironSource, Mintegral, InMobi, Bigo, Chartboost, Fyber, BidMachine, Amazon, adjoe) |
| IAP | Google Play Billing Library **8.3.0** wired in (`billing.properties`) |
| Analytics/Ops | Firebase (Analytics, Installations, Cloud Messaging), Google Play Services (Auth, Location, Tasks) |
| Support | AIHelp in-app help/ticket chat widget (`aihelp_*` resources) — in-app CS, not just FAQ |
| Game content | **None recoverable** — no shop item names, prices, or screen art present in this split |

Because static extraction hit a wall, the tables below are reconstructed from public player guides and the Play Store listing (research, not decompilation) so the report still delivers usable design intel.

## 1. In-game store / shop

Zombie Waves runs a **three-tier core currency** system layered under a much larger set of stage/event-specific soft currencies (players report seeing on the order of 15-20 named currencies across different game modes — temporal fragments, core crystals, cooperation coins, energy, alloy, steel, trade coins, unity coins, etc.).

| Currency | Role | Acquired via |
|---|---|---|
| **Gold** | Main soft currency — weapon/equipment upgrades | Stage clear rewards, first-clear bonuses, missions |
| **Diamonds** | Premium currency | IAP purchase, some free drops; spent on chests, converting to gold, skipping timers |
| **Intel** | Secondary progression currency | Ranking up weapon/equipment rarity tier |
| Mode-specific tokens (energy, alloy, steel, cooperation coins, etc.) | Gate specific mini-games/events | Grinding repetitive "press start and wait" side activities |

**Shop structure (from player reports):**
- Weapons/gear have a rarity ladder (normal → legendary); higher rarity = harder cap, better stats, gated behind Intel + Gold.
- Diamonds buy: chest openings, gold conversion, and (implied) time-skips — i.e. premium currency is the universal "solve it with money" lever, not a separate item catalog.
- Player sentiment is notably negative on the currency sprawl — a recurring complaint is that the shop/currency web is intentionally complex ("temple of temptation") to push players toward IAP by making free-to-play routes feel roadblocked.

## 2. Between-run / meta screens

- **Run structure:** each stage/run has a fixed **~10-minute survival timer** in normal mode (not an infinite endless mode by default).
- **Post-run loop:** stage-clear rewards (gold + possible intel/diamonds), plus **first-time-clear bonuses** that are richer than repeat-clear rewards — incentivizes chasing new stages over farming old ones.
- **Level-up:** skill/weapon upgrade choices are tied directly to in-run level-ups (roguelike pick-a-perk pattern), separate from the persistent meta-progression currencies.
- **Chests:** diamonds unlock chests as a gacha-style layer sitting on top of the stage-clear loop.
- **Social/guild layer:** joining an active guild is called out by guides as a meaningful resource multiplier — extra resources/items flow through guild participation, not just solo play.
- **Survival attribute system:** persistent passive stats (e.g., Freezing + Ice Jacket combo for damage immunity on contact, Regeneration for HP-over-time) that carry meta-progression weight between runs — a build-crafting layer independent of the shop.
- **Repetitive collector mini-games:** roughly a dozen small "start and wait for the timer" side activities exist purely to farm the various mode-specific currencies — flagged by players as filler rather than engaging gameplay.

## 3. Stage / level structure

- Presented as **stage-based, roguelike survival shooter** — not endless/hypercasual. Progression is chapter → stage, each stage a discrete ~10-minute clear.
- Each stage clear is a checkpoint: rewards, unlocks, and (on first clear) a bonus reward tier.
- In-run leveling grants roguelike perk/skill choices layered on top of the persistent equipment/currency meta-game.

## RECOMMENDED FOR HIVE SWARM

Ranked by expected value vs. implementation cost for a 360° run-and-gun survivors-like:

1. **First-clear bonus vs. repeat-clear reward split** — cheap to implement, strong retention lever; reward the *first* clear of a wave-tier meaningfully more than farming it again, to pull players toward pushing further instead of grinding a comfortable wave.
2. **Two-currency cap, not twenty** — this is the single loudest complaint about Zombie Waves. Steal the *intent* (soft currency for gear, premium currency as universal unlock) but explicitly avoid currency sprawl. Two currencies max for HiVE SWARM's launch scope.
3. **In-run perk/level-up picks separate from persistent meta-upgrades** — the roguelike "choose a perk on level-up mid-run" pattern is proven and cheap; keep it decoupled from the between-run shop so each run still feels fresh.
4. **Persistent passive "build" stats between runs** (their Freezing/Regeneration attributes) — gives players a build-crafting meta layer without needing a full talent tree UI; good v1 scope for a small team.
5. **Fixed run timer (~8-10 min) as the default mode** — gives runs a predictable shape for balancing and for ad/session pacing, with room for a separate "endless" mode later.
6. **Chest-as-gacha funded by premium currency only** — keep gacha mechanics opt-in and premium-currency-gated rather than a second currency sink, to avoid the "temple of temptation" complaint.
7. **Skip the mode-specific side-currencies/mini-games entirely** — players explicitly call these out as filler; not worth the dev time or the player goodwill cost.
8. **Guild/social resource multiplier — defer to post-launch.** Real retention value but heavy infra (guild backend, chat, moderation) for a small team; not v1.
9. **In-app support widget (AIHelp-style)** — worth a cheap third-party integration once HiVE SWARM has real spend; low priority pre-launch.
10. **Ad mediation stack (AppLovin MAX + waterfall)** — validates that a rewarded-ads-plus-IAP hybrid economy is standard for this genre; confirms HiVE SWARM's existing ad/IAP direction rather than suggesting a change.

## Sources

- [Zombie Waves - Apps on Google Play](https://play.google.com/store/apps/details?id=com.ddup.zombiewaves.zw&hl=en_US)
- [Zombie Waves - Ultimate Game Guide, Tips & Codes - Talk Android](https://www.talkandroid.com/24092-zombie-waves-ultimate-game-guide-tips-codes/)
- [Zombie Waves - Complete Guide | Heroes, Weapons, Tips & Codes](https://www.tipszombiewaves.com/)
