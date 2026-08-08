# -*- coding: utf-8 -*-
"""Patch HiVE SWARM index.html for v0.3.0 combat/stage/debrief pass."""
from pathlib import Path

path = Path(r"D:\Dev\HiveSwarm\index.html")
t = path.read_text(encoding="utf-8")
orig_len = len(t)


def repl(old: str, new: str, label: str, count: int = 1) -> None:
    global t
    n = t.count(old)
    if n < count:
        raise SystemExit(f"FAIL {label}: found {n}, need >= {count}\n---OLD head---\n{old[:240]!r}")
    t = t.replace(old, new, count)
    print(f"OK {label} (x{count})")


# 1) Version
repl("const GAME_VERSION='0.2.4';", "const GAME_VERSION='0.3.0';", "version")

# 2) MODS + skills + helpers
old_mods = """const MODS=[
  {id:'scatter',   name:'Scatter',   text:'+2 projectiles per shot',              appliesTo:['bullet','homing','nova','poison']},
  {id:'venom',     name:'Venom',     text:'+60% poison damage and spread',        appliesTo:['poison']},
  {id:'pierce',    name:'Piercing',  text:'+1 pierce',                            appliesTo:['bullet','homing','nova','poison']},
  {id:'rapid',     name:'Rapid',     text:'-15% time between shots',              appliesTo:['bullet','homing','beam','chain','nova','poison']},
  {id:'knockback', name:'Knockback', text:'Pushes enemies back on hit',           appliesTo:['bullet','homing','beam','chain','nova','poison']},
  // Nova Shell unique: kill explosions spit mini reactor-stars. Base shards (3) + 2 per stack.
  {id:'novastar',  name:'Nova Star', text:'+2 mini nova stars on kill explosion', appliesTo:['nova']},
];
function modApplies(mod,w){return mod.appliesTo.includes(w.kind||'bullet')}
function wNovaShards(w){return Math.max(0,(w.shards??3)+2*modStacks(w.id,'novastar'))}
let weaponMods={};                     // { weaponId: { modId: stacks } }
let weaponOrbs={};                     // { weaponId: orbs banked toward the next rank }
function modsFor(id){return weaponMods[id]||(weaponMods[id]={})}
function modStacks(id,mod){return (weaponMods[id]||{})[mod]||0}
function addMod(id,mod){const m=modsFor(id);if((m[mod]||0)>=MOD_MAX)return false;m[mod]=(m[mod]||0)+1;return true}
// Orbs are the weapon's own progress bar. Only the gun you are actually holding banks them, so
// carrying a weapon IS the investment - which is the incentive the owner asked for.
function orbsForRank(rank){return Math.round(12*Math.pow(1.45,(rank||1)-1))}
function bankOrb(){for(const w of heldWeapons){const id=w.id;weaponOrbs[id]=(weaponOrbs[id]||0)+1;
  if(weaponOrbs[id]>=orbsForRank(w.rank||1)&&(w.rank||1)<5){weaponOrbs[id]=0;upgradeWeapon(w);burst(player.x,player.y,w.color||'#6fffe2',14);sfx('hit',.18)}}}
// Effective stats = base weapon + its mods. Nothing mutates the weapon object, so a mod can never
// be double-applied and removing one is just arithmetic.
function wShots(w){return Math.min(9,(w.shots||1)+2*modStacks(w.id,'scatter'))}
function wPierce(w){return (w.pierce??0)+modStacks(w.id,'pierce')}
function wRate(w){return Math.max(.05,(w.rate||.2)*Math.pow(.85,modStacks(w.id,'rapid')))}
function venomMul(w){return (1+.6*modStacks(w.id,'venom'))*(1+.25*(META.venom||0))}"""

new_mods = r"""const MODS=[
  // Scatter = multi-shot for discrete projectiles ONLY. Beam/chain never fire discrete shots —
  // offering Scatter for them is a dead card (owner 2026-08-08). rocket/nova/homing/poison/bullet all fire projectiles.
  {id:'scatter',   name:'Scatter',   text:'+2 projectiles per shot',              appliesTo:['bullet','homing','nova','poison','rocket']},
  {id:'venom',     name:'Venom',     text:'+60% poison damage and spread',        appliesTo:['poison']},
  {id:'pierce',    name:'Piercing',  text:'+1 pierce',                            appliesTo:['bullet','homing','nova','poison','rocket']},
  {id:'rapid',     name:'Rapid',     text:'-15% time between shots',              appliesTo:['bullet','homing','beam','chain','nova','poison','rocket']},
  {id:'knockback', name:'Knockback', text:'Pushes enemies back on hit',           appliesTo:['bullet','homing','beam','chain','nova','poison','rocket']},
  // Ricochet: bounce off enemies and arena walls (owner 2026-08-08).
  {id:'ricochet',  name:'Ricochet',  text:'Bullets bounce off enemies & walls',   appliesTo:['bullet','homing','poison','rocket']},
  // Damage amp — Zombie Waves Overclock cousin for raw DPS.
  {id:'overcharge',name:'Overcharge',text:'+22% weapon damage',                   appliesTo:['bullet','homing','beam','chain','nova','poison','rocket']},
  // Bigger projectiles / thicker beam.
  {id:'giant',     name:'Giant Rounds',text:'+35% projectile / beam size',        appliesTo:['bullet','homing','nova','poison','rocket','beam']},
  // Nova Shell unique: kill explosions spit mini reactor-stars. Base shards (3) + 2 per stack.
  {id:'novastar',  name:'Nova Star', text:'+2 mini nova stars on kill explosion', appliesTo:['nova']},
  // Storm Arc unique: adds jumps on top of the weapon's current jump count (owner 2026-08-08).
  {id:'arcjump',   name:'Forked Arc',text:'+2 Storm Arc jumps',                   appliesTo:['chain']},
];
// Passive skills (not weapon-bound). Cap at MOD_MAX stacks; never offer a 3/3 skill again.
const SKILLS=[
  {id:'fleet',  name:'Fleet Footed', text:'+12% movement speed'},
  {id:'bulk',   name:'Reinforced',   text:'+25 max HP and heal'},
  {id:'magnet', name:'Magnet',       text:'+45 pickup radius'},
  {id:'shield', name:'Shield Matrix',text:'Negate 1 hit every 12s (stacks = charges)'},
  {id:'vampiric',name:'Vampiric',    text:'Heal 2 HP per kill (stacks add +1)'},
  {id:'drone',  name:'Drone Escort', text:'Orbiting drones fire with you'},
];
function modApplies(mod,w){return mod.appliesTo.includes(w.kind||'bullet')}
function wNovaShards(w){return Math.max(0,(w.shards??3)+2*modStacks(w.id,'novastar'))}
function wJumps(w){return Math.max(1,(w.jumps||4)+2*modStacks(w.id,'arcjump'))}
function wDamage(w){return (w.damage||10)*(1+.22*modStacks(w.id,'overcharge'))}
function wSizeMul(w){return 1+.35*modStacks(w.id,'giant')}
function wBounces(w){return modStacks(w.id,'ricochet')}
let weaponMods={};                     // { weaponId: { modId: stacks } }
let weaponOrbs={};                     // { weaponId: orbs banked toward the next rank }
let skillStacks={};                    // { skillId: stacks } — run-scoped, max MOD_MAX
// Stage run stats for HiveWar-style debrief
let runStats={killsBy:{},totalKills:0,orbs:0,weaponsSeen:{},round:0};
function resetRunStats(){runStats={killsBy:{},totalKills:0,orbs:0,weaponsSeen:{},round:0}}
function noteKill(e){
  const id=(e&&e.type&&e.type.id)||'unknown', nm=(e&&e.type&&e.type.name)||id;
  if(!runStats.killsBy[id])runStats.killsBy[id]={name:nm,n:0,color:(e.type&&e.type.color)||'#8ab',sprite:(e.type&&e.type.sprite)||''};
  runStats.killsBy[id].n++;runStats.totalKills++;
  const vamp=skillStacks.vampiric||0;if(vamp)player.hp=Math.min(player.maxHp,player.hp+(1+vamp));
}
function noteWeapon(w){if(!w||!w.id)return;runStats.weaponsSeen[w.id]={id:w.id,name:w.name,rank:w.rank||1,color:w.color,icon:w.icon|0,kind:w.kind||'bullet'}}
function modsFor(id){return weaponMods[id]||(weaponMods[id]={})}
function modStacks(id,mod){return (weaponMods[id]||{})[mod]||0}
function addMod(id,mod){const m=modsFor(id);if((m[mod]||0)>=MOD_MAX)return false;m[mod]=(m[mod]||0)+1;return true}
function skillN(id){return skillStacks[id]||0}
function addSkill(id){if((skillStacks[id]||0)>=MOD_MAX)return false;skillStacks[id]=(skillStacks[id]||0)+1;return true}
// Orbs are the weapon's own progress bar. Only the gun you are actually holding banks them, so
// carrying a weapon IS the investment - which is the incentive the owner asked for.
function orbsForRank(rank){return Math.round(12*Math.pow(1.45,(rank||1)-1))}
function bankOrb(){for(const w of heldWeapons){const id=w.id;weaponOrbs[id]=(weaponOrbs[id]||0)+1;
  if(weaponOrbs[id]>=orbsForRank(w.rank||1)&&(w.rank||1)<5){weaponOrbs[id]=0;upgradeWeapon(w);burst(player.x,player.y,w.color||'#6fffe2',14);sfx('hit',.18)}}}
// Effective stats = base weapon + its mods. Nothing mutates the weapon object, so a mod can never
// be double-applied and removing one is just arithmetic.
// Scatter works for every projectile kind (including rocket/nova). Beam/chain excluded via appliesTo.
function wShots(w){const k=w.kind||'bullet';if(k==='beam'||k==='chain')return 1;return Math.min(9,(w.shots||1)+2*modStacks(w.id,'scatter'))}
function wPierce(w){return (w.pierce??0)+modStacks(w.id,'pierce')}
function wRate(w){return Math.max(.05,(w.rate||.2)*Math.pow(.85,modStacks(w.id,'rapid')))}
function venomMul(w){return (1+.6*modStacks(w.id,'venom'))*(1+.25*(META.venom||0))}"""

repl(old_mods, new_mods, "mods")

# 3) Knockback + clamp
old_kb = """function applyKnockback(e,dx,dy,stacks){
  if(!stacks)return;
  const d=Math.hypot(dx,dy)||1,resist=e.isBoss?KB_BOSS_RESIST:1,power=KB_IMPULSE*stacks*resist;
  let kx=(e.kx||0)+dx/d*power,ky=(e.ky||0)+dy/d*power,mag=Math.hypot(kx,ky);
  if(mag>KB_CAP){kx=kx/mag*KB_CAP;ky=ky/mag*KB_CAP}
  e.kx=kx;e.ky=ky;
}"""
new_kb = """function isStaticEnemy(e){return !!(e&&((e.speed||0)<=0.05||(e.type&&(e.type.speed||0)<=0)))}
function clampEnemy(e){
  if(!e)return;
  const r=e.r||12;
  e.x=Math.max(-WORLD.halfW+r,Math.min(WORLD.halfW-r,e.x));
  e.y=Math.max(-WORLD.halfH+r,Math.min(WORLD.halfH-r,e.y));
}
function applyKnockback(e,dx,dy,stacks){
  if(!stacks)return;
  // Static nodes (Necro Node etc.) MUST stay put — knockback used to shove them off-screen /
  // past the arena edge, soft-locking a stage (owner 2026-08-08).
  if(isStaticEnemy(e))return;
  const d=Math.hypot(dx,dy)||1,resist=e.isBoss?KB_BOSS_RESIST:1,power=KB_IMPULSE*stacks*resist;
  let kx=(e.kx||0)+dx/d*power,ky=(e.ky||0)+dy/d*power,mag=Math.hypot(kx,ky);
  if(mag>KB_CAP){kx=kx/mag*KB_CAP;ky=ky/mag*KB_CAP}
  e.kx=kx;e.ky=ky;
}"""
repl(old_kb, new_kb, "knockback")

# 4) Stage rounds state
old_stage = """let stage=0, stageT=0, stageBoss=null, pendingStageAdvance=null;
function curStageCfg(){const arr=EDIT.stages&&EDIT.stages.length?EDIT.stages:FORGE_BASE.stages;return arr[stage%arr.length]}"""
new_stage = """let stage=0, stageT=0, stageBoss=null, pendingStageAdvance=null;
// Owner 2026-08-08: each stage = 3 rounds of rising density, THEN the guardian, THEN debrief → next stage.
const ROUNDS_PER_STAGE=3;
let stageRound=0, roundT=0; // stageRound 0..2 during combat rounds; boss after last round
function curStageCfg(){const arr=EDIT.stages&&EDIT.stages.length?EDIT.stages:FORGE_BASE.stages;return arr[stage%arr.length]}
function roundDuration(){const s=curStageCfg().seconds||60;return Math.max(12,s/ROUNDS_PER_STAGE)}
function roundBudgetMul(){return 1+stageRound*0.55} // round 1 = 1x, round 2 ≈1.55x, round 3 ≈2.1x
let shieldCharges=0,shieldCd=0; // Shield Matrix runtime"""
repl(old_stage, new_stage, "stage rounds state")

# 5) reset
old_reset = """elapsed=score=wave=spawnBudget=fireClock=shake=xp=cardPicks=orbsCollected=0;weaponMods={};weaponOrbs={};evolved=false;level=1;nextXp=8;state='play';paused=false;setPaused(false);
  stage=0;stageT=0;stageBoss=null;
  genObstacles();for(const o of dmgNums)o.active=0;
  if(WEAPON&&WEAPON.id)codexSee('weapon:'+WEAPON.id,0)}"""
new_reset = """elapsed=score=wave=spawnBudget=fireClock=shake=xp=cardPicks=orbsCollected=0;weaponMods={};weaponOrbs={};skillStacks={};evolved=false;level=1;nextXp=8;state='play';paused=false;setPaused(false);
  stage=0;stageT=0;stageBoss=null;stageRound=0;roundT=0;shieldCharges=0;shieldCd=0;resetRunStats();
  genObstacles();for(const o of dmgNums)o.active=0;
  if(WEAPON&&WEAPON.id){codexSee('weapon:'+WEAPON.id,0);noteWeapon(WEAPON)}}"""
repl(old_reset, new_reset, "reset")

# 6) grantWeapon note
old_grant = """heldWeapons=[Object.assign(copy(base),{rank:1})];WEAPON=heldWeapons[0];return 'swap'}"""
new_grant = """heldWeapons=[Object.assign(copy(base),{rank:1})];WEAPON=heldWeapons[0];noteWeapon(WEAPON);return 'swap'}"""
repl(old_grant, new_grant, "grantWeapon note")

# 7) Heat Seeker also tagged as rocket-capable for scatter messaging — add rocket weapon entry after seeker?
# Rename seeker comment + add rocket weapon based on seeker
old_seeker = """  {id:'weapon.seeker',name:'Heat Seeker',kind:'homing',damage:22,rate:.38,speed:420,shots:1,pierce:0,color:'#ff6b3d',range:900,turn:7.5,dropWeight:1,sfx:'magic-spell.mp3',icon:1},"""
new_seeker = """  {id:'weapon.seeker',name:'Heat Seeker',kind:'homing',damage:22,rate:.38,speed:420,shots:1,pierce:0,color:'#ff6b3d',range:900,turn:7.5,dropWeight:1,sfx:'magic-spell.mp3',icon:1},
  // Rocket Launcher: unguided multi-shot friendly shell. Scatter/pierce/ricochet apply via kind 'rocket'.
  {id:'weapon.rocket',name:'Rocket Launcher',kind:'rocket',damage:40,rate:.62,speed:380,shots:1,pierce:0,color:'#ff9a3d',range:700,blast:56,dropWeight:1,sfx:'grenade.mp3',icon:5},"""
repl(old_seeker, new_seeker, "rocket weapon")

# 8) fire() damage + chain jumps + projectile size/bounces + rocket as projectile
old_fire_dmg = """  const dmgMul=1+Math.min(.25,META.damage*.05);
  for(const w of heldWeapons){
    const kind=w.kind||'bullet', dmg=w.damage*dmgMul;"""
new_fire_dmg = """  const dmgMul=1+Math.min(.25,META.damage*.05);
  for(const w of heldWeapons){
    const kind=w.kind||'bullet', dmg=wDamage(w)*dmgMul;"""
repl(old_fire_dmg, new_fire_dmg, "fire dmg")

old_chain = """    if(kind==='chain'){
      let cur=wTarget, hit=new Set(), jumps=w.jumps||4, from={x:player.x,y:player.y};"""
new_chain = """    if(kind==='chain'){
      let cur=wTarget, hit=new Set(), jumps=wJumps(w), from={x:player.x,y:player.y};"""
repl(old_chain, new_chain, "chain jumps")

old_beam_w = """      beams.push({x1:player.x,y1:player.y,x2,y2,color:w.color,core:w.coreColor,life:beamLife,lifeMax:beamLife,w:w.glowWidth||24,coreW:w.coreWidth||2.4,pulseRate:w.pulseRate||16});"""
new_beam_w = """      const sm=wSizeMul(w);
      beams.push({x1:player.x,y1:player.y,x2,y2,color:w.color,core:w.coreColor,life:beamLife,lifeMax:beamLife,w:(w.glowWidth||24)*sm,coreW:(w.coreWidth||2.4)*sm,pulseRate:w.pulseRate||16});"""
repl(old_beam_w, new_beam_w, "beam size")

old_proj = """    // projectile kinds: bullet / homing / nova / poison
    if(w.sfx)sfxFile(w.sfx,kind==='nova'?.14:.08);else sfx('fire',kind==='nova'?.12:.08);
    const shots=wShots(w);
    const shards=kind==='nova'?wNovaShards(w):0;
    for(let i=0;i<shots;i++){
      let spread=(i-(shots-1)/2)*.1;
      const ang=wa+spread;
      bullets.push({
        x:player.x+Math.cos(ang)*18,y:player.y+Math.sin(ang)*18,
        vx:Math.cos(ang)*(w.speed||700),vy:Math.sin(ang)*(w.speed||700),
        r:kind==='nova'?7:kind==='homing'?5:4,
        damage:dmg,pierce:wPierce(w),life:kind==='homing'?2.2:kind==='nova'?1.4:1.05,
        dot:(w.dot||0)*venomMul(w),dotTime:w.dotTime||0,slow:w.slowFactor??1,stackMax:w.poisonStackMax??1,
        spread:kind==='poison'?{chance:(w.spreadChance??.9)*venomMul(w),radius:w.spreadRadius??52,factor:w.spreadFactor??.7,slow:w.slowFactor??1}:null,
        // kb snapshotted at fire time (not looked up at hit time) — bullets never carry a weapon
        // reference, only kind, so modStacks(w.id,...) has to happen here while `w` is still in
        // scope. Same immutable-snapshot pattern as dot/spread above.
        kb:modStacks(w.id,'knockback'),
        shards, srcWep:w.id,
        color:w.color,kind,turn:w.turn||0,blast:w.blast||0,trail:[]
      })}}}"""
new_proj = """    // projectile kinds: bullet / homing / nova / poison / rocket
    if(w.sfx)sfxFile(w.sfx,(kind==='nova'||kind==='rocket')?.14:.08);else sfx('fire',(kind==='nova'||kind==='rocket')?.12:.08);
    const shots=wShots(w);
    const shards=kind==='nova'?wNovaShards(w):0;
    const sm=wSizeMul(w), bounces=wBounces(w);
    // Wider fan when Scatter stacks so multi-shot reads clearly (esp. rocket launcher).
    const fan=.12+.04*Math.max(0,shots-1);
    for(let i=0;i<shots;i++){
      let spread=(i-(shots-1)/2)*fan;
      const ang=wa+spread;
      const baseR=kind==='nova'?7:kind==='rocket'?6:kind==='homing'?5:4;
      bullets.push({
        x:player.x+Math.cos(ang)*18,y:player.y+Math.sin(ang)*18,
        vx:Math.cos(ang)*(w.speed||700),vy:Math.sin(ang)*(w.speed||700),
        r:baseR*sm,
        damage:dmg,pierce:wPierce(w),life:kind==='homing'?2.2:kind==='nova'?1.4:kind==='rocket'?1.5:1.05,
        dot:(w.dot||0)*venomMul(w),dotTime:w.dotTime||0,slow:w.slowFactor??1,stackMax:w.poisonStackMax??1,
        spread:kind==='poison'?{chance:(w.spreadChance??.9)*venomMul(w),radius:w.spreadRadius??52,factor:w.spreadFactor??.7,slow:w.slowFactor??1}:null,
        kb:modStacks(w.id,'knockback'),
        shards, srcWep:w.id, bounces, bounced:0,
        color:w.color,kind,turn:w.turn||0,blast:w.blast||0,trail:[],
        _hit:null
      })}}}"""
repl(old_proj, new_proj, "projectiles")

# 9) killEnemy noteKill + wasBoss debrief path (replace later with full debrief)
old_kill_score = """function killEnemy(e,gibs,killOpts){
  const idx=enemies.indexOf(e);if(idx<0)return;
  score+=10;"""
new_kill_score = """function killEnemy(e,gibs,killOpts){
  const idx=enemies.indexOf(e);if(idx<0)return;
  score+=10;noteKill(e);"""
repl(old_kill_score, new_kill_score, "noteKill")

old_boss_break = """  if(wasBoss){stageBoss=null;score+=250;shake=Math.min(10,shake+6);explode(ex,ey,'#ffe066',110,true);state='stagebreak';offerStageBreak()}}"""
new_boss_break = """  if(wasBoss){stageBoss=null;score+=250;shake=Math.min(10,shake+6);explode(ex,ey,'#ffe066',110,true);state='debrief';startDebrief()}}"""
repl(old_boss_break, new_boss_break, "boss->debrief")

# 10) explode: no push static
old_explode_hit = """  for(const e of enemies){const dx=e.x-x,dy=e.y-y,d=Math.hypot(dx,dy);if(d<r){const dmg=22*(1-d/r);e.hp-=dmg;e.hit=.15;spawnDmgNum(e.x,e.y-e.r,dmg);if(d>1){e.x+=dx/d*18;e.y+=dy/d*18}applyKnockback(e,dx,dy,kb);if(e.hp<=0)doomed.push(e)}}"""
new_explode_hit = """  for(const e of enemies){const dx=e.x-x,dy=e.y-y,d=Math.hypot(dx,dy);if(d<r){const dmg=22*(1-d/r);e.hp-=dmg;e.hit=.15;spawnDmgNum(e.x,e.y-e.r,dmg);if(d>1&&!isStaticEnemy(e)){e.x+=dx/d*18;e.y+=dy/d*18;clampEnemy(e)}applyKnockback(e,dx,dy,kb);if(e.hp<=0)doomed.push(e)}}"""
repl(old_explode_hit, new_explode_hit, "explode static")

# 11) Stage round loop in update
old_stage_loop = """if(!stageBoss){stageT+=dt;if(stageT>=curStageCfg().seconds)spawnBossEnemy()}
if(!stageBoss)spawnBudget+=dt*EDIT.waves.budgetBase*Math.pow(EDIT.waves.budgetExponent,wave);
while(spawnBudget>=1){spawnBudget-=1;spawnEnemy()}fireClock-=dt;if(fireClock<=0){fireClock+=wRate(WEAPON);fire()}"""
new_stage_loop = """// 3 rounds per stage then boss (owner 2026-08-08). stageT still tracks total stage time for HUD.
if(!stageBoss){
  stageT+=dt;roundT+=dt;
  const rd=roundDuration();
  if(roundT>=rd){
    if(stageRound<ROUNDS_PER_STAGE-1){
      stageRound++;roundT=0;wave=Math.max(wave,1+stageRound*2);
      // brief visual cue
      burst(player.x,player.y,'#6fffe2',18);sfx('kill',.12);
    }else if(!stageBoss){
      // final round expired → guardian
      spawnBossEnemy();
    }
  }
}
if(!stageBoss)spawnBudget+=dt*EDIT.waves.budgetBase*Math.pow(EDIT.waves.budgetExponent,wave)*roundBudgetMul();
while(spawnBudget>=1){spawnBudget-=1;spawnEnemy()}
// Shield Matrix recharge
if((skillStacks.shield||0)>0){shieldCd=Math.max(0,shieldCd-dt);if(shieldCd<=0&&shieldCharges<(skillStacks.shield||0)){shieldCharges=skillStacks.shield;shieldCd=12}}
fireClock-=dt;if(fireClock<=0){fireClock+=wRate(WEAPON);fire();fireDrones()}"""
repl(old_stage_loop, new_stage_loop, "stage round loop")

# 12) Always clamp enemies after movement; static stay put
old_enemy_move = """  e.x+=vx/d*moveSpeed*dt;e.y+=vy/d*moveSpeed*dt;e.vx=(e.x-(e._px||e.x));e.vy=(e.y-(e._py||e.y));e._px=e.x;e._py=e.y;"""
new_enemy_move = """  if(!isStaticEnemy(e)){e.x+=vx/d*moveSpeed*dt;e.y+=vy/d*moveSpeed*dt}
  e.vx=(e.x-(e._px||e.x));e.vy=(e.y-(e._py||e.y));e._px=e.x;e._py=e.y;"""
repl(old_enemy_move, new_enemy_move, "static no chase")

old_kb_apply = """  if(e.kx||e.ky){e.x+=e.kx*dt;e.y+=e.ky*dt;e.vx=(e.x-(e._px||e.x));e.vy=(e.y-(e._py||e.y));e._px=e.x;e._py=e.y;e.x=Math.max(-WORLD.halfW+e.r,Math.min(WORLD.halfW-e.r,e.x));e.y=Math.max(-WORLD.halfH+e.r,Math.min(WORLD.halfH-e.r,e.y));const kd=Math.pow(.5,dt/KB_HALFLIFE);e.kx*=kd;e.ky*=kd;if(Math.abs(e.kx)<1)e.kx=0;if(Math.abs(e.ky)<1)e.ky=0}
  for(let j=0;j<i;j++){let o=enemies[j],sx=e.x-o.x,sy=e.y-o.y,sd=Math.hypot(sx,sy)||.01,gap=(e.r+o.r)*.8;if(sd<gap){let push=(gap-sd)*.5;e.x+=sx/sd*push;e.y+=sy/sd*push;e.vx=(e.x-(e._px||e.x));e.vy=(e.y-(e._py||e.y));e._px=e.x;e._py=e.y;o.x-=sx/sd*push;o.y-=sy/sd*push}}pushOutOfObstacles(e);e.hit=Math.max(0,e.hit-dt);"""
new_kb_apply = """  if((e.kx||e.ky)&&!isStaticEnemy(e)){e.x+=e.kx*dt;e.y+=e.ky*dt;e.vx=(e.x-(e._px||e.x));e.vy=(e.y-(e._py||e.y));e._px=e.x;e._py=e.y;const kd=Math.pow(.5,dt/KB_HALFLIFE);e.kx*=kd;e.ky*=kd;if(Math.abs(e.kx)<1)e.kx=0;if(Math.abs(e.ky)<1)e.ky=0}
  else{e.kx=0;e.ky=0}
  for(let j=0;j<i;j++){let o=enemies[j],sx=e.x-o.x,sy=e.y-o.y,sd=Math.hypot(sx,sy)||.01,gap=(e.r+o.r)*.8;if(sd<gap){let push=(gap-sd)*.5;
    if(!isStaticEnemy(e)){e.x+=sx/sd*push;e.y+=sy/sd*push;e.vx=(e.x-(e._px||e.x));e.vy=(e.y-(e._py||e.y));e._px=e.x;e._py=e.y}
    if(!isStaticEnemy(o)){o.x-=sx/sd*push;o.y-=sy/sd*push;clampEnemy(o)}}}
  pushOutOfObstacles(e);clampEnemy(e);e.hit=Math.max(0,e.hit-dt);"""
repl(old_kb_apply, new_kb_apply, "clamp always")

# 13) Player hit shield + contact push clamp
old_player_hit = """      if(d<e.r+player.r){if(!player.inv){if(e.type&&e.type.sfxAttack)sfxFile(e.type.sfxAttack,.16);player.hp-=e.damage;player.inv=.7;shake=8;burst(player.x,player.y,'#ff718a',14);
        player.x-=vx/d*18;player.y-=vy/d*18;
        if(player.hp<=0){player.hp=0;if(score>(META.bestScore||0)){META.bestScore=score;saveMeta()}state='dead';setPaused(false)}}e.x-=vx/d*28;e.y-=vy/d*28}}"""
new_player_hit = """      if(d<e.r+player.r){if(!player.inv){
        if(shieldCharges>0){shieldCharges--;player.inv=.55;burst(player.x,player.y,'#6fffe2',12);sfx('hit',.1)}
        else{if(e.type&&e.type.sfxAttack)sfxFile(e.type.sfxAttack,.16);player.hp-=e.damage;player.inv=.7;shake=8;burst(player.x,player.y,'#ff718a',14);
        player.x-=vx/d*18;player.y-=vy/d*18;
        if(player.hp<=0){player.hp=0;if(score>(META.bestScore||0)){META.bestScore=score;saveMeta()}state='dead';setPaused(false)}}}
        if(!isStaticEnemy(e)){e.x-=vx/d*28;e.y-=vy/d*28;clampEnemy(e)}}}"""
repl(old_player_hit, new_player_hit, "shield + clamp contact")

# 14) Bullet ricochet + rocket explode + wall bounce
old_bullets = """for(let i=bullets.length-1;i>=0;i--){let b=bullets[i];
  if(b.kind==='homing'){const t=nearestEnemy(b);if(t){const desired=Math.atan2(t.y-b.y,t.x-b.x),cur=Math.atan2(b.vy,b.vx);let diff=((desired-cur+Math.PI*3)%(Math.PI*2))-Math.PI;const maxTurn=(b.turn||7)*dt;diff=Math.max(-maxTurn,Math.min(maxTurn,diff));const sp=Math.hypot(b.vx,b.vy)||400;const na=cur+diff;b.vx=Math.cos(na)*sp;b.vy=Math.sin(na)*sp}}
  b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt;
  if(b.trail){b.trail.push(b.x,b.y);if(b.trail.length>16)b.trail.splice(0,2)}
  let removed=b.life<=0;
  const novaMetaFor=()=>({shards:b.shards||0,damage:b.damage,color:b.color,blast:b.blast||70,kb:b.kb});
  if(removed&&(b.kind==='nova'||b.kind==='novashard'))explode(b.x,b.y,b.color||'#ffe066',b.blast||70,false,b.kb,b.kind==='nova'?novaMetaFor():null);
  for(let j=enemies.length-1;j>=0&&!removed;j--){let e=enemies[j],r=e.r+b.r;if((e.x-b.x)**2+(e.y-b.y)**2<r*r){
    if(b.kind==='nova'||b.kind==='novashard'){explode(b.x,b.y,b.color||'#ffe066',b.blast||70,false,b.kb,b.kind==='nova'?novaMetaFor():null);removed=true;break}
    if(b.kind==='poison'){"""
new_bullets = """for(let i=bullets.length-1;i>=0;i--){let b=bullets[i];
  if(b.kind==='homing'){const t=nearestEnemy(b);if(t){const desired=Math.atan2(t.y-b.y,t.x-b.x),cur=Math.atan2(b.vy,b.vx);let diff=((desired-cur+Math.PI*3)%(Math.PI*2))-Math.PI;const maxTurn=(b.turn||7)*dt;diff=Math.max(-maxTurn,Math.min(maxTurn,diff));const sp=Math.hypot(b.vx,b.vy)||400;const na=cur+diff;b.vx=Math.cos(na)*sp;b.vy=Math.sin(na)*sp}}
  b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt;
  // Ricochet off arena bounds
  if((b.bounces|0)>0){
    const margin=8;
    if(b.x<-WORLD.halfW+margin||b.x>WORLD.halfW-margin){b.vx*=-1;b.x=Math.max(-WORLD.halfW+margin,Math.min(WORLD.halfW-margin,b.x));b.bounces--;b.life=Math.max(b.life,.2);burst(b.x,b.y,b.color||'#fff',2)}
    if(b.y<-WORLD.halfH+margin||b.y>WORLD.halfH-margin){b.vy*=-1;b.y=Math.max(-WORLD.halfH+margin,Math.min(WORLD.halfH-margin,b.y));b.bounces--;b.life=Math.max(b.life,.2);burst(b.x,b.y,b.color||'#fff',2)}
  }
  if(b.trail){b.trail.push(b.x,b.y);if(b.trail.length>16)b.trail.splice(0,2)}
  let removed=b.life<=0;
  const novaMetaFor=()=>({shards:b.shards||0,damage:b.damage,color:b.color,blast:b.blast||70,kb:b.kb});
  if(removed&&(b.kind==='nova'||b.kind==='novashard'||b.kind==='rocket'))explode(b.x,b.y,b.color||'#ffe066',b.blast||(b.kind==='rocket'?56:70),false,b.kb,b.kind==='nova'?novaMetaFor():null);
  for(let j=enemies.length-1;j>=0&&!removed;j--){let e=enemies[j],r=e.r+b.r;if((e.x-b.x)**2+(e.y-b.y)**2<r*r){
    if(b.kind==='nova'||b.kind==='novashard'||b.kind==='rocket'){explode(b.x,b.y,b.color||'#ffe066',b.blast||(b.kind==='rocket'?56:70),false,b.kb,b.kind==='nova'?novaMetaFor():null);removed=true;break}
    if(b.kind==='poison'){"""
repl(old_bullets, new_bullets, "bullets ricochet walls")

# 15) Bullet hit ricochet off enemies (normal bullet path)
old_hit = """    e.hp-=b.damage;e.hit=.1;sfx('hit',.08);burst(b.x,b.y,b.color||WEAPON.color,4);spawnDmgNum(e.x,e.y-e.r,b.damage);applyKnockback(e,b.vx,b.vy,b.kb);b.pierce--;
    if(e.hp<=0)killEnemy(e,b.kind==='homing');if(b.pierce<0)removed=true}}
  if(removed)bullets.splice(i,1)}"""
new_hit = """    e.hp-=b.damage;e.hit=.1;sfx('hit',.08);burst(b.x,b.y,b.color||WEAPON.color,4);spawnDmgNum(e.x,e.y-e.r,b.damage);applyKnockback(e,b.vx,b.vy,b.kb);b.pierce--;
    if(e.hp<=0)killEnemy(e,b.kind==='homing');
    if(b.pierce<0){
      // Ricochet off the enemy surface instead of dying, while bounces remain.
      if((b.bounces|0)>0){
        const nx=b.x-e.x,ny=b.y-e.y,nd=Math.hypot(nx,ny)||1;
        // Reflect velocity about the contact normal
        const ux=nx/nd,uy=ny/nd,dot=b.vx*ux+b.vy*uy;
        b.vx=b.vx-2*dot*ux;b.vy=b.vy-2*dot*uy;
        b.x=e.x+ux*(e.r+b.r+2);b.y=e.y+uy*(e.r+b.r+2);
        b.bounces--;b.pierce=0;b.life=Math.max(b.life,.25);b.damage*=.92;
        burst(b.x,b.y,b.color||'#fff',3);
      }else removed=true;
    }}}
  if(removed)bullets.splice(i,1)}"""
repl(old_hit, new_hit, "enemy ricochet")

# 16) Orbs counted in runStats
old_orb = """else{xp+=p.value;orbsCollected++;bankOrb();burst(p.x,p.y,'#6fffe2',5);codexSee('item:xp',0)}"""
new_orb = """else{xp+=p.value;orbsCollected++;runStats.orbs++;bankOrb();burst(p.x,p.y,'#6fffe2',5);codexSee('item:xp',0)}"""
repl(old_orb, new_orb, "orb stats")

# 17) Toxin bubbles double
old_bub = """    const n=5+Math.min(4,stacks); // denser cloud at higher stacks"""
new_bub = """    const n=10+Math.min(8,stacks*2); // twice the bubbles (owner 2026-08-08)"""
repl(old_bub, new_bub, "double bubbles")

# 18) HUD round indicator in stage line
old_hud = """ctx.fillText('STAGE '+(stage+1)+' · '+curStageCfg().name+'  ·  WAVE '+wave,18,32+SAFE_TOP);ctx.font='14px system-ui';ctx.fillStyle='#a5c3be';
ctx.fillText((stageBoss?'GUARDIAN '+Math.max(0,Math.ceil(stageBoss.hp))+'/'+stageBoss.maxHp:'NEXT GUARDIAN '+Math.max(0,Math.ceil(curStageCfg().seconds-stageT))+'s')+'   SCORE '+score+'   HOSTILES '+enemies.length,18,55+SAFE_TOP);"""
new_hud = """ctx.fillText('STAGE '+(stage+1)+' · '+curStageCfg().name+'  ·  ROUND '+(stageBoss?'BOSS':(stageRound+1)+'/'+ROUNDS_PER_STAGE)+'  ·  WAVE '+wave,18,32+SAFE_TOP);ctx.font='14px system-ui';ctx.fillStyle='#a5c3be';
const roundLeft=stageBoss?0:Math.max(0,Math.ceil(roundDuration()-roundT));
ctx.fillText((stageBoss?'GUARDIAN '+Math.max(0,Math.ceil(stageBoss.hp))+'/'+stageBoss.maxHp:(stageRound>=ROUNDS_PER_STAGE-1?'GUARDIAN IN ':'ROUND END ')+roundLeft+'s')+'   SCORE '+score+'   HOSTILES '+enemies.length+(shieldCharges?'   🛡'+shieldCharges:''),18,55+SAFE_TOP);"""
repl(old_hud, new_hud, "hud rounds")

# 19) Replace offerCards + offerStageBreak with improved versions + debrief
old_offer = """function offerCards(){
  // S.7: weapon cards now grant a MOD attached to the held weapon's ID instead of mutating the
  // weapon object. Swapping guns no longer deletes what you just earned, and the same mod can be
  // stacked up to MOD_MAX times on one weapon (owner spec: "up to 3 times on the same weapon").
  const held=heldWeapons[0]||WEAPON;
  let weapons=MODS.filter(m=>modApplies(m,held)&&modStacks(held.id,m.id)<MOD_MAX).map(m=>({
    name:m.name+' '+(modStacks(held.id,m.id)+1)+'/'+MOD_MAX,
    text:m.text+' — '+held.name,
    apply:()=>addMod(held.id,m.id)})),stats=[{name:'Fleet Footed',text:'+12% movement speed',apply:()=>player.speed=Math.round(player.speed*1.12)},{name:'Reinforced',text:'+25 max HP and heal',apply:()=>{player.maxHp+=25;player.hp=Math.min(player.maxHp,player.hp+25)}},{name:'Magnet',text:'+45 pickup radius',apply:()=>player.pickupRadius+=45}],evo={name:'Plasma Evolution',text:'Wave 10 evolution: double pulse damage',apply:()=>{WEAPON.damage*=2;evolved=true}};let pool=[...weapons,...stats,...(wave>=10&&!evolved?[evo]:[])],first=cardPicks<3&&weapons.length?weapons[Math.floor(Math.random()*weapons.length)]:null;choices=[];if(first)choices.push(first);while(choices.length<3&&pool.length){let c=pool.splice(Math.floor(Math.random()*pool.length),1)[0];if(!choices.includes(c))choices.push(c)}
  // Headless harness has no real DOM — auto-pick so balance sims are not stuck on the chooser.
  if(typeof HTMLElement==='undefined'){if(choices[0])choices[0].apply();cardPicks++;state='play';return}
  let box=document.createElement('div');box.id='cards';box.className='overlay';box.innerHTML='<h2>LEVEL '+level+' — CHOOSE ONE</h2>'+choices.map((c,i)=>`<button data-card="${i}" style="width:260px;padding:18px;background:#16383a;color:#eafffa;border:1px solid #75f0db;border-radius:8px"><b>${c.name}</b><br>${c.text}</button>`).join('');document.body.append(box);box.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{choices[Number(b.dataset.card)].apply();cardPicks++;box.remove();state='play'})}
// STAGE break screen: boss is already dead (killEnemy set state='stagebreak' and cleared
// stageBoss before calling this). Reuses the same upgrade-card pool as offerCards() so a stage
// clear feels like a bigger level-up, then advances stage/stageT and wipes the field for a clean
// arrival into the next stage's backdrop + roster. Same headless-DOM fallback as offerCards() so
// the harness/verification scripts can drive straight through without a real browser.
function offerStageBreak(){
  const clearedCfg=curStageCfg();
  const held=heldWeapons[0]||WEAPON;
  let weapons=MODS.filter(m=>modApplies(m,held)&&modStacks(held.id,m.id)<MOD_MAX).map(m=>({
    name:m.name+' '+(modStacks(held.id,m.id)+1)+'/'+MOD_MAX,
    text:m.text+' — '+held.name,
    apply:()=>addMod(held.id,m.id)})),
    stats=[{name:'Fleet Footed',text:'+12% movement speed',apply:()=>player.speed=Math.round(player.speed*1.12)},
      {name:'Reinforced',text:'+40 max HP and full heal',apply:()=>{player.maxHp+=40;player.hp=player.maxHp}},
      {name:'Magnet',text:'+45 pickup radius',apply:()=>player.pickupRadius+=45}];
  let pool=[...weapons,...stats];choices=[];
  while(choices.length<3&&pool.length){let c=pool.splice(Math.floor(Math.random()*pool.length),1)[0];if(!choices.includes(c))choices.push(c)}
  if(!choices.length)choices.push({name:'Press On',text:'No upgrades available — deploy anyway',apply:()=>{}});
  // advance() mutates enemies/bullets — NEVER call it synchronously from inside killEnemy (it can
  // fire mid-iteration over the very bullets/enemies arrays update() is looping through, which
  // corrupts those loops). Both paths below only schedule it; update()'s top-of-frame check runs
  // it once the current frame's simulation loops have finished.
  const advance=()=>{stage++;genObstacles();stageT=0;stageBoss=null;enemies=[];bullets=[];beams=[];player.hp=Math.min(player.maxHp,player.hp+Math.round(player.maxHp*.25));state='play'};
  if(typeof HTMLElement==='undefined'){if(choices[0])choices[0].apply();pendingStageAdvance=advance;return}
  let box=document.createElement('div');box.id='stagebreak';box.className='overlay';
  box.innerHTML='<h2>STAGE '+(stage+1)+' CLEAR — '+clearedCfg.name+'</h2><div class="hint">Guardian down · score +250 · choose a reward, then deploy to Stage '+(stage+2)+'</div>'+
    choices.map((c,i)=>`<button data-card="${i}" style="width:260px;padding:18px;background:#16383a;color:#eafffa;border:1px solid #75f0db;border-radius:8px"><b>${c.name}</b><br>${c.text}</button>`).join('');
  document.body.append(box);
  box.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{choices[Number(b.dataset.card)].apply();box.remove();pendingStageAdvance=advance})}"""

new_offer = r"""function weaponIconHtml(w){
  // Tiny inline canvas-like chip: colored square + first letter, plus sheet icon if available.
  if(!w)return '';
  const col=w.color||'#6fffe2', nm=(w.name||'?')[0]||'?';
  return `<span style="display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:6px;background:${col}22;border:1px solid ${col};color:${col};font-weight:900;margin-right:8px;vertical-align:middle">${nm}</span>`;
}
function cardIconHtml(c){
  if(c.iconHtml)return c.iconHtml;
  if(c.wep)return weaponIconHtml(c.wep);
  return `<span style="display:inline-flex;width:28px;height:28px;border-radius:6px;background:#1a3034;border:1px solid #3a6a62;align-items:center;justify-content:center;margin-right:8px">✦</span>`;
}
function buildCardPool(opts){
  // Shared pool for level-up + stage break. Never offer a mod/skill already at MOD_MAX (3/3).
  opts=opts||{};
  const held=heldWeapons[0]||WEAPON;
  const weapons=MODS.filter(m=>held&&modApplies(m,held)&&modStacks(held.id,m.id)<MOD_MAX).map(m=>({
    name:m.name+' '+(modStacks(held.id,m.id)+1)+'/'+MOD_MAX,
    text:m.text+' — '+held.name,
    wep:held,
    apply:()=>addMod(held.id,m.id)}));
  const skillApply={
    fleet:()=>{addSkill('fleet');player.speed=Math.round(player.speed*1.12)},
    bulk:()=>{addSkill('bulk');const h=opts.bigHeal?40:25;player.maxHp+=h;player.hp=opts.bigHeal?player.maxHp:Math.min(player.maxHp,player.hp+h)},
    magnet:()=>{addSkill('magnet');player.pickupRadius+=45},
    shield:()=>{addSkill('shield');shieldCharges=skillN('shield');shieldCd=0},
    vampiric:()=>addSkill('vampiric'),
    drone:()=>addSkill('drone'),
  };
  const skills=SKILLS.filter(s=>skillN(s.id)<MOD_MAX).map(s=>({
    name:s.name+' '+(skillN(s.id)+1)+'/'+MOD_MAX,
    text:s.text,
    apply:()=>skillApply[s.id]&&skillApply[s.id]()}));
  const evo={name:'Plasma Evolution',text:'Wave 10 evolution: double pulse damage',apply:()=>{if(WEAPON)WEAPON.damage*=2;evolved=true}};
  let pool=[...weapons,...skills,...(opts.allowEvo&&wave>=10&&!evolved?[evo]:[])];
  return {held,weapons,skills,pool};
}
function offerCards(){
  // S.7: weapon cards grant a MOD attached to the held weapon's ID. Skills are run-scoped, max 3.
  const {weapons,pool}=buildCardPool({allowEvo:true,bigHeal:false});
  let first=cardPicks<3&&weapons.length?weapons[Math.floor(Math.random()*weapons.length)]:null;
  choices=[];if(first)choices.push(first);
  const bag=pool.slice();
  while(choices.length<3&&bag.length){let c=bag.splice(Math.floor(Math.random()*bag.length),1)[0];if(!choices.includes(c))choices.push(c)}
  if(!choices.length)choices.push({name:'Press On',text:'Everything is maxed — keep fighting',apply:()=>{}});
  if(typeof HTMLElement==='undefined'){if(choices[0])choices[0].apply();cardPicks++;state='play';return}
  let box=document.createElement('div');box.id='cards';box.className='overlay';
  box.innerHTML='<h2>LEVEL '+level+' — CHOOSE ONE</h2>'+choices.map((c,i)=>`<button data-card="${i}" style="width:280px;padding:16px;background:#16383a;color:#eafffa;border:1px solid #75f0db;border-radius:8px;text-align:left"><b style="display:flex;align-items:center">${cardIconHtml(c)}${c.name}</b><br><span style="opacity:.85">${c.text}</span></button>`).join('');
  document.body.append(box);
  box.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{choices[Number(b.dataset.card)].apply();cardPicks++;box.remove();state='play'});
}
// ---- HiveWar-style stage debrief (count-up stats) then upgrade pick ----
let debriefT=0, debriefDone=false, debriefRowsCache=null, debriefLastVal={};
function debriefRows(){
  if(debriefRowsCache)return debriefRowsCache;
  const rows=[];
  const kills=Object.values(runStats.killsBy||{}).sort((a,b)=>b.n-a.n);
  for(const k of kills)if(k.n>0)rows.push({label:k.name,value:k.n,col:k.color||'#9ef',kind:1});
  rows.push({label:'TOTAL KILLS',value:runStats.totalKills||0,big:true,col:'#4ff'});
  rows.push({label:'ORBS COLLECTED',value:runStats.orbs||0,col:'#6fffe2'});
  // Weapons seen this run with current rank + mod stacks
  const weps=Object.values(runStats.weaponsSeen||{});
  for(const w of weps){
    const live=(heldWeapons.find(h=>h.id===w.id))||weaponById(w.id)||w;
    const rank=live.rank||w.rank||1;
    const mods=weaponMods[w.id]||{};
    const modTxt=Object.keys(mods).filter(k=>mods[k]>0).map(k=>k+' '+mods[k]+'/'+MOD_MAX).join(', ');
    rows.push({label:(live.name||w.name)+'  Rk.'+rank+(modTxt?' · '+modTxt:''),value:rank,col:live.color||'#ffe08a',wep:live,weapon:1});
  }
  debriefRowsCache=rows;return rows;
}
function startDebrief(){
  debriefT=0;debriefDone=false;debriefRowsCache=null;debriefLastVal={};
  state='debrief';
  if(typeof HTMLElement==='undefined'){// harness: skip animation
    pendingStageAdvance=()=>offerStageBreak();return}
}
function updateDebrief(dt){
  if(state!=='debrief')return;
  debriefT+=dt;
  const rows=debriefRows();
  const full=rows.length*0.45+1.4;
  if(!debriefDone&&debriefT>full)debriefDone=true;
}
function drawDebrief(){
  if(state!=='debrief')return;
  const W=VIEW.w,H=VIEW.h;
  ctx.save();
  ctx.fillStyle='rgba(2,8,16,.86)';ctx.fillRect(0,0,W,H);
  const panelW=Math.min(W-36,520),panelH=Math.min(H-80,560);
  const px0=(W-panelW)/2,py0=(H-panelH)/2;
  ctx.fillStyle='rgba(12,28,32,.96)';ctx.strokeStyle='#6fffe2';ctx.lineWidth=2;
  ctx.shadowColor='#6fffe2';ctx.shadowBlur=22;
  if(ctx.roundRect){ctx.beginPath();ctx.roundRect(px0,py0,panelW,panelH,14);ctx.fill();ctx.stroke()}
  else{ctx.fillRect(px0,py0,panelW,panelH);ctx.strokeRect(px0,py0,panelW,panelH)}
  ctx.shadowBlur=0;ctx.textAlign='center';
  ctx.fillStyle='#6fffe2';ctx.font='900 32px system-ui';
  ctx.fillText('STAGE '+(stage+1)+' CLEAR',W/2,py0+48);
  ctx.fillStyle='#9ebbb6';ctx.font='14px system-ui';
  ctx.fillText(curStageCfg().name+' · Guardian down · +250 score',W/2,py0+74);
  const rows=debriefRows();
  rows.forEach((r,i)=>{
    const appear=i*0.45, shown=debriefT-appear;if(shown<=0)return;
    const k=Math.min(1,shown/0.4), val=Math.round((r.value||0)*k*k);
    const y=py0+110+i*36;
    if(r.big){
      ctx.fillStyle='#fff';ctx.font='900 28px system-ui';ctx.shadowColor='#4ff';ctx.shadowBlur=16;
      ctx.fillText(String(val),W/2,y);
      ctx.shadowBlur=0;ctx.fillStyle='#9ef';ctx.font='700 13px system-ui';
      ctx.fillText(r.label,W/2,y+18);
    }else{
      ctx.textAlign='left';ctx.fillStyle=r.col||'#dce9e7';ctx.font='700 15px system-ui';
      const labelX=px0+28;
      if(r.wep){/* weapon chip */
        ctx.fillStyle=(r.wep.color||'#6ff')+'33';ctx.fillRect(labelX,y-16,22,22);
        ctx.strokeStyle=r.wep.color||'#6ff';ctx.strokeRect(labelX,y-16,22,22);
        ctx.fillStyle=r.wep.color||'#6ff';ctx.font='900 12px system-ui';ctx.textAlign='center';
        ctx.fillText((r.wep.name||'?')[0],labelX+11,y+1);ctx.textAlign='left';
        ctx.fillStyle=r.col||'#dce9e7';ctx.font='700 14px system-ui';
        ctx.fillText(r.label,labelX+30,y);
      }else{
        ctx.fillText(r.label,labelX,y);
      }
      ctx.textAlign='right';ctx.fillStyle='#fff';ctx.font='900 18px system-ui';
      ctx.fillText(String(val),px0+panelW-28,y);
      ctx.textAlign='center';
    }
  });
  if(debriefDone){
    const pulse=.7+.3*Math.sin(debriefT*5);
    ctx.fillStyle=`rgba(111,255,226,${pulse})`;ctx.font='700 16px system-ui';
    ctx.fillText('TAP TO CONTINUE',W/2,py0+panelH-28);
  }
  ctx.restore();
}
function finishDebrief(){
  if(state!=='debrief'||!debriefDone)return;
  offerStageBreak();
}
function fireDrones(){
  // Drone Escort skill: small orbiting shots toward nearest enemy.
  const n=skillN('drone');if(!n)return;
  const t=nearestEnemy(player);if(!t)return;
  for(let i=0;i<n;i++){
    const ang=elapsed*2.2+i*(Math.PI*2/Math.max(1,n));
    const ox=player.x+Math.cos(ang)*36, oy=player.y+Math.sin(ang)*36;
    const a=Math.atan2(t.y-oy,t.x-ox), sp=520;
    bullets.push({x:ox,y:oy,vx:Math.cos(a)*sp,vy:Math.sin(a)*sp,r:3,damage:6+n*2,pierce:0,life:.7,color:'#9ef',kind:'bullet',kb:0,shards:0,trail:[],bounces:0});
  }
}
// STAGE break: after debrief, pick a reward then advance.
function offerStageBreak(){
  const clearedCfg=curStageCfg();
  const {pool}=buildCardPool({allowEvo:false,bigHeal:true});
  choices=[];const bag=pool.slice();
  while(choices.length<3&&bag.length){let c=bag.splice(Math.floor(Math.random()*bag.length),1)[0];if(!choices.includes(c))choices.push(c)}
  if(!choices.length)choices.push({name:'Press On',text:'No upgrades available — deploy anyway',apply:()=>{}});
  const advance=()=>{
    stage++;genObstacles();stageT=0;stageRound=0;roundT=0;stageBoss=null;
    enemies=[];bullets=[];beams=[];
    // Keep cumulative run stats; only clear per-stage kill ledger so next debrief is stage-local.
    runStats.killsBy={};runStats.totalKills=0;runStats.orbs=0;
    player.hp=Math.min(player.maxHp,player.hp+Math.round(player.maxHp*.25));
    state='play';
  };
  if(typeof HTMLElement==='undefined'){if(choices[0])choices[0].apply();pendingStageAdvance=advance;return}
  // remove any leftover debrief overlay
  const prev=document.getElementById('stagebreak');if(prev)prev.remove();
  let box=document.createElement('div');box.id='stagebreak';box.className='overlay';
  box.innerHTML='<h2>STAGE '+(stage+1)+' REWARD</h2><div class="hint">'+clearedCfg.name+' cleared · pick one, then deploy Stage '+(stage+2)+'</div>'+
    choices.map((c,i)=>`<button data-card="${i}" style="width:280px;padding:16px;background:#16383a;color:#eafffa;border:1px solid #75f0db;border-radius:8px;text-align:left"><b style="display:flex;align-items:center">${cardIconHtml(c)}${c.name}</b><br><span style="opacity:.85">${c.text}</span></button>`).join('');
  document.body.append(box);
  box.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{choices[Number(b.dataset.card)].apply();box.remove();pendingStageAdvance=advance});
  state='stagebreak';
}"""
repl(old_offer, new_offer, "cards+debrief")

# 20) Wire debrief into update/draw/input
# update() top — after pause check, handle debrief
old_update_head = """function update(dt){
  // Run any scheduled stage-advance BEFORE this frame's simulation loops touch enemies/bullets —
  // see the comment in offerStageBreak() for why this can't run synchronously from killEnemy.
  if(pendingStageAdvance){const fn=pendingStageAdvance;pendingStageAdvance=null;fn()}
  if(newCodexT>0)newCodexT=Math.max(0,newCodexT-dt);
  if(paused){// freeze sim: no spawnBudget/fireClock/enemy advance — resume is frame-clean
    for(let i=beams.length-1;i>=0;i--){beams[i].life-=dt;if(beams[i].life<=0)beams.splice(i,1)}
    return}
  if(state!=='play')return;elapsed+=dt;"""
new_update_head = """function update(dt){
  // Run any scheduled stage-advance BEFORE this frame's simulation loops touch enemies/bullets —
  // see the comment in offerStageBreak() for why this can't run synchronously from killEnemy.
  if(pendingStageAdvance){const fn=pendingStageAdvance;pendingStageAdvance=null;fn()}
  if(newCodexT>0)newCodexT=Math.max(0,newCodexT-dt);
  if(state==='debrief'){updateDebrief(dt);return}
  if(paused){// freeze sim: no spawnBudget/fireClock/enemy advance — resume is frame-clean
    for(let i=beams.length-1;i>=0;i--){beams[i].life-=dt;if(beams[i].life<=0)beams.splice(i,1)}
    return}
  if(state!=='play')return;elapsed+=dt;"""
repl(old_update_head, new_update_head, "update debrief")

# draw end: call drawDebrief
old_draw_end = """if(typeof ensureTitleChrome==='function')ensureTitleChrome();
}"""
new_draw_end = """if(state==='debrief')drawDebrief();
if(typeof ensureTitleChrome==='function')ensureTitleChrome();
}"""
repl(old_draw_end, new_draw_end, "draw debrief")

# click / pointer to finish debrief — find canvas click
old_click = """canvas.addEventListener('click',()=>{if(state==='title'||state==='dead')tryDeploy()});"""
new_click = """canvas.addEventListener('click',()=>{if(state==='title'||state==='dead')tryDeploy();else if(state==='debrief')finishDebrief()});
canvas.addEventListener('pointerdown',(e)=>{if(state==='debrief'){e.preventDefault();finishDebrief()}});"""
repl(old_click, new_click, "debrief click")

# 21) pause should allow debrief state
old_pause = """function setPaused(on){
  if(state!=='play'&&state!=='levelup'&&!(paused&&on===false)){if(state==='title'||state==='dead')return}"""
new_pause = """function setPaused(on){
  if(state==='debrief'||state==='stagebreak')return;
  if(state!=='play'&&state!=='levelup'&&!(paused&&on===false)){if(state==='title'||state==='dead')return}"""
repl(old_pause, new_pause, "pause skip debrief")

# 22) sw.js cache bump
sw = Path(r"D:\Dev\HiveSwarm\sw.js")
sw_t = sw.read_text(encoding="utf-8")
sw_t2 = sw_t.replace("const CACHE_VERSION = 'v16';", "const CACHE_VERSION = 'v17';  // v0.3.0 — rounds, debrief, ricochet, double toxin bubbles, rocket")
if sw_t2 == sw_t:
    # try looser
    import re
    sw_t2 = re.sub(r"const CACHE_VERSION = 'v\d+';[^\n]*", "const CACHE_VERSION = 'v17';  // v0.3.0 pass", sw_t, count=1)
sw.write_text(sw_t2, encoding="utf-8")
print("OK sw.js cache")

path.write_text(t, encoding="utf-8")
print(f"DONE: {orig_len} -> {len(t)} chars")
# sanity
for needle in ["GAME_VERSION='0.3.0'", "ROUNDS_PER_STAGE", "startDebrief", "wJumps", "ricochet", "weapon.rocket", "double the bubbles", "isStaticEnemy", "buildCardPool"]:
    print(("OK" if needle in t else "MISSING"), needle)
