// S.7 checks — one per line of the owner's 2026-08-06 report.
// Reuses the headless harness stubs, then drives the real game functions directly.
'use strict';
const fs = require('fs');
const path = require('path');

const harness = fs.readFileSync(path.join(__dirname, '..', '_headless_harness.js'), 'utf8');
const prelude = harness.split('let code = fs.readFileSync')[0];
eval(prelude);

let code = fs.readFileSync(path.join(__dirname, '..', '_game_extract.js'), 'utf8');
code += `
;globalThis.__H = { get enemies(){return enemies}, get bullets(){return bullets}, get player(){return player},
  get heldWeapons(){return heldWeapons}, set heldWeapons(v){heldWeapons=v},
  get weaponMods(){return weaponMods}, get weaponOrbs(){return weaponOrbs},
  get state(){return state}, set state(v){state=v},
  EDIT, META, MODS, MOD_MAX, addMod, modStacks, wShots, wPierce, wRate, venomMul,
  orbsForRank, bankOrb, poisonTarget, nearestEnemy, fire, update, reset, offerCards,
  get cardPicks(){return cardPicks}, weaponById, copy };`;
(0, eval)(code);
const H = globalThis.__H;

let fails = 0;
const ok = (name, cond, extra) => {
  console.log((cond ? 'PASS  ' : 'FAIL  ') + name + (extra ? '   ' + extra : ''));
  if (!cond) fails++;
};
const mkEnemy = (x, y, over) => {
  const e = Object.assign({ x, y, r: 16, hp: 5000, maxHp: 5000, speed: 0, damage: 0,
    type: H.EDIT.entities[0], color: '#fff', hit: 0, poisonT: 0, poisonDps: 0 }, over || {});
  H.enemies.push(e); return e;
};
const poisonGun = H.copy(H.EDIT.weapons.find(w => w.id === 'weapon.poison'));

if (typeof H.reset === 'function') H.reset();

// ---------------------------------------------------------------- 1. targeting skips the infected
H.enemies.length = 0;
const sick = mkEnemy(60, 0, { poisonT: 3, poisonDps: 8 });   // closest, already infected
const clean = mkEnemy(140, 0);                                // further away, clean
const picked = H.poisonTarget();
ok('toxin gun retargets off an already-poisoned enemy',
   picked === clean, `nearest=${picked === sick ? 'the infected one (BUG)' : 'the clean one at 140px'}`);

H.enemies.length = 0;
const onlySick = mkEnemy(60, 0, { poisonT: 3, poisonDps: 8 });
ok('falls back to nearest when everything is infected', H.poisonTarget() === onlySick);

// ---------------------------------------------------------------- 2. darts are not wasted on carriers
H.enemies.length = 0; H.bullets.length = 0;
const carrier = mkEnemy(0, -40, { poisonT: 3, poisonDps: 8 });
const fresh = mkEnemy(0, -120);
H.bullets.push({ x: 0, y: 0, vx: 0, vy: -900, r: 4, damage: 6, pierce: 1, life: 2,
  kind: 'poison', color: '#7cff4f', dot: 8, dotTime: 3,
  spread: { chance: 0.9, radius: 52, factor: 0.7 } });
for (let i = 0; i < 12; i++) H.update(0.016);
ok('a poison dart passes THROUGH an infected body and reaches a clean one',
   fresh.poisonT > 0, `clean enemy poisonT=${fresh.poisonT.toFixed(2)} (dart was not consumed by the carrier)`);

// ---------------------------------------------------------------- 3. contagion
H.enemies.length = 0; H.bullets.length = 0;
const patientZero = mkEnemy(0, 0, { poisonT: 5, poisonDps: 10, poisonSrc: { chance: 1, radius: 60, factor: 0.7 } });
const neighbour = mkEnemy(30, 0);
const faraway = mkEnemy(900, 0);
for (let i = 0; i < 200 && !(neighbour.poisonT > 0); i++) H.update(0.016);
ok('infected enemies infect what they touch', neighbour.poisonT > 0,
   `neighbour dps=${(neighbour.poisonDps || 0).toFixed(1)} vs carrier 10 (weakened by spreadFactor)`);
ok('infection is weaker each generation, so a plague burns out',
   neighbour.poisonDps > 0 && neighbour.poisonDps < patientZero.poisonDps,
   `${patientZero.poisonDps} -> ${neighbour.poisonDps.toFixed(1)}`);
ok('contagion does not teleport across the map', !(faraway.poisonT > 0), 'enemy at 900px stayed clean');

// ---------------------------------------------------------------- 4. FORGE owns the poison numbers
const pg = H.EDIT.weapons.find(w => w.id === 'weapon.poison');
ok('poison damage + spread are FORGE fields',
   ['dot', 'dotTime', 'spreadChance', 'spreadRadius', 'spreadFactor'].every(k => Number.isFinite(pg[k])),
   `dot=${pg.dot} dotTime=${pg.dotTime}s chance=${pg.spreadChance} radius=${pg.spreadRadius} factor=${pg.spreadFactor}`);

// ---------------------------------------------------------------- 5. buyable poison multiplier
const before = H.venomMul(poisonGun);
H.META.venom = 4;
const after = H.venomMul(poisonGun);
H.META.venom = 0;
ok('VENOM is a purchasable poison multiplier', after > before, `x${before.toFixed(2)} -> x${after.toFixed(2)} at 4 ranks`);

// ---------------------------------------------------------------- 6. mods stack to 3, then stop
const id = 'weapon.pulse';
H.weaponMods[id] = {};
const results = [H.addMod(id, 'scatter'), H.addMod(id, 'scatter'), H.addMod(id, 'scatter'), H.addMod(id, 'scatter')];
ok('the same mod stacks exactly 3 times on one weapon',
   results.join(',') === 'true,true,true,false' && H.modStacks(id, 'scatter') === 3,
   `accepted ${results.filter(Boolean).length}/4 · stacks=${H.modStacks(id, 'scatter')} · cap=${H.MOD_MAX}`);

// ---------------------------------------------------------------- 7. Scatter actually adds bolts
const pulse = H.copy(H.EDIT.weapons[0]);
H.weaponMods[pulse.id] = {};
const baseShots = H.wShots(pulse);
H.addMod(pulse.id, 'scatter'); H.addMod(pulse.id, 'scatter');
ok('Scatter adds projectiles', H.wShots(pulse) === baseShots + 4, `${baseShots} -> ${H.wShots(pulse)} bolts at 2 stacks`);

// ---------------------------------------------------------------- 8. THE BIG ONE: swapping weapons keeps mods
H.weaponMods['weapon.pulse'] = {}; H.weaponMods['weapon.nova'] = {};
H.addMod('weapon.pulse', 'scatter'); H.addMod('weapon.pulse', 'pierce');
const pulseBefore = JSON.stringify(H.weaponMods['weapon.pulse']);
H.heldWeapons = [Object.assign(H.copy(H.weaponById('weapon.nova')), { rank: 1 })];   // pick up a new gun
H.addMod('weapon.nova', 'rapid');
H.heldWeapons = [Object.assign(H.copy(H.weaponById('weapon.pulse')), { rank: 1 })];  // swap back
ok('mods survive a weapon swap and come back with the gun',
   JSON.stringify(H.weaponMods['weapon.pulse']) === pulseBefore && H.modStacks('weapon.nova', 'rapid') === 1,
   `pulse=${pulseBefore} kept, nova kept its own rapid:1`);

// ---------------------------------------------------------------- 9. orbs feed the weapon's rank
H.heldWeapons = [Object.assign(H.copy(H.weaponById('weapon.pulse')), { rank: 1 })];
H.weaponOrbs['weapon.pulse'] = 0;
const rank0 = H.heldWeapons[0].rank, need = H.orbsForRank(rank0);
for (let i = 0; i < need; i++) H.bankOrb();
ok('gathering orbs ranks the held weapon up', H.heldWeapons[0].rank === rank0 + 1,
   `${need} orbs -> Rk.${H.heldWeapons[0].rank}; next rank needs ${H.orbsForRank(H.heldWeapons[0].rank)}`);

console.log(fails ? `\n${fails} CHECK(S) FAILED` : '\nALL CHECKS PASSED');
process.exit(fails ? 1 : 0);
