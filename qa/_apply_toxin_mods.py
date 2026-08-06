"""S.7 — toxin rework + per-weapon mods that survive a weapon swap + orb-fed weapon track.

Owner spec 2026-08-06:
  - Toxin gun "hits an enemy and continues to hit"; once an enemy is poisoned the gun should
    stop targeting it and move to a clean one.
  - Poisoned enemies should INFECT enemies they touch.
  - Poison damage belongs in FORGE, with a poison multiplier you can buy.
  - Every weapon should be upgradable, fed by orbs.
  - Perks apply to any weapon you own, stackable up to 3x on the same weapon, and you must NOT
    lose the perk you just earned when the weapon changes.

Kept as a file (not an inline heredoc) so the prose and quotes survive shell quoting.
"""
import io

p = 'index.html'
s = io.open(p, encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:80], s.count(a))
    s = s.replace(a, b)


# ---------------------------------------------------------------- A. FORGE poison values
rep(
  """  {id:'weapon.poison',name:'Toxin Injector',kind:'poison',damage:6,rate:.5,speed:600,shots:1,pierce:1,color:'#7cff4f',range:640,dot:8,dotTime:3}""",
  """  // S.7 poison fields, all FORGE-editable: dot = damage/sec while infected, dotTime = seconds
  // an infection lasts, spreadChance = per-second chance a carrier infects a clean neighbour,
  // spreadRadius = how close that neighbour must be, spreadFactor = potency the infection is
  // passed on at (0.7 = each generation is 30% weaker, so a plague fades instead of snowballing).
  {id:'weapon.poison',name:'Toxin Injector',kind:'poison',damage:6,rate:.5,speed:600,shots:1,pierce:1,color:'#7cff4f',range:640,dot:8,dotTime:3,spreadChance:.9,spreadRadius:52,spreadFactor:.7}""")


# ---------------------------------------------------------------- B. mods + weapon track state
rep(
  """let orbsCollected=0;""",
  """let orbsCollected=0;
// ---- S.7 WEAPON MODS + ORB TRACK ----------------------------------------------------------
// Both are keyed by WEAPON ID, never by the held weapon object. That is the whole point: picking
// up a new gun used to replace heldWeapons outright (see pickWeapon), which threw away every card
// the player had just earned. Mods and track progress live outside the object, so swapping to a
// gun you modded earlier restores its mods intact, and nothing is ever lost by switching.
const MOD_MAX=3;                       // owner spec: up to 3 stacks of the same mod on one weapon
const MODS=[
  {id:'scatter', name:'Scatter',  text:'+2 projectiles per shot'},
  {id:'venom',   name:'Venom',    text:'+60% poison damage and spread'},
  {id:'pierce',  name:'Piercing', text:'+1 pierce'},
  {id:'rapid',   name:'Rapid',    text:'-15% time between shots'},
];
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
function venomMul(w){return (1+.6*modStacks(w.id,'venom'))*(1+.25*(META.venom||0))}""")


# ---------------------------------------------------------------- C. targeting
rep(
  """function nearestEnemy(from,ignore){let target=null,best=Infinity;for(const e of enemies){if(ignore&&ignore.has(e))continue;let d=(from.x-e.x)**2+(from.y-e.y)**2;if(d<best){best=d;target=e}}return target}""",
  """function nearestEnemy(from,ignore,ok){let target=null,best=Infinity;for(const e of enemies){if(ignore&&ignore.has(e))continue;if(ok&&!ok(e))continue;let d=(from.x-e.x)**2+(from.y-e.y)**2;if(d<best){best=d;target=e}}return target}
// S.7 owner bug: "after an enemy is poisoned the weapon stops targeting them". The toxin gun kept
// dumping shots into a target that was already dying of the DoT. It now looks for the nearest
// CLEAN enemy first and only falls back to the plain nearest when the whole screen is infected.
function poisonTarget(){return nearestEnemy(player,null,e=>!(e.poisonT>0))||nearestEnemy(player)}""")

rep(
  """    const kind=w.kind||'bullet', dmg=w.damage*dmgMul;""",
  """    const kind=w.kind||'bullet', dmg=w.damage*dmgMul;
    // Each weapon aims for itself now - the toxin gun wants a clean target, everything else wants
    // the closest body.
    let wTarget=kind==='poison'?poisonTarget():target;
    if(!wTarget)continue;
    let wa=Math.atan2(wTarget.y-player.y,wTarget.x-player.x);
    if(w===heldWeapons[0])player.angle=wa;""")

rep("""      let cur=target, hit=new Set(), jumps=w.jumps||4, from={x:player.x,y:player.y};""",
    """      let cur=wTarget, hit=new Set(), jumps=w.jumps||4, from={x:player.x,y:player.y};""")

# beam + projectiles must use the per-weapon angle and the modded stats
rep("""      const len=w.range||720, x2=player.x+Math.cos(a)*len, y2=player.y+Math.sin(a)*len;""",
    """      const len=w.range||720, x2=player.x+Math.cos(wa)*len, y2=player.y+Math.sin(wa)*len;""")
rep("""    for(let i=0;i<w.shots;i++){
      let spread=(i-(w.shots-1)/2)*.1;
      const ang=a+spread;""",
    """    const shots=wShots(w);
    for(let i=0;i<shots;i++){
      let spread=(i-(shots-1)/2)*.1;
      const ang=wa+spread;""")
rep("""        damage:dmg,pierce:w.pierce??0,life:kind==='homing'?2.2:kind==='nova'?1.4:1.05,""",
    """        damage:dmg,pierce:wPierce(w),life:kind==='homing'?2.2:kind==='nova'?1.4:1.05,""")


# ---------------------------------------------------------------- D. poison bullet no longer wasted
rep(
  """    if(b.kind==='poison'){e.poisonDps=Math.max(e.poisonDps||0,b.dot||8);e.poisonT=Math.max(e.poisonT||0,b.dotTime||3);e.hit=.1;sfx('hit',.06);burst(b.x,b.y,b.color||'#7cff4f',3);b.pierce--;if(b.pierce<0)removed=true;continue}""",
  """    if(b.kind==='poison'){
      // Owner bug 2026-08-06: "it hits an enemy and continues to hit". A carrier no longer eats the
      // dart at all - the shot flies THROUGH anything already infected without spending pierce, so
      // it reaches a clean target instead of being wasted re-poisoning the same body.
      if(e.poisonT>0)continue;
      e.poisonDps=Math.max(e.poisonDps||0,b.dot||8);e.poisonT=Math.max(e.poisonT||0,b.dotTime||3);
      e.poisonSrc=b.spread||null;e.hit=.1;sfx('hit',.06);burst(b.x,b.y,b.color||'#7cff4f',3);
      b.pierce--;if(b.pierce<0)removed=true;continue}""")


# ---------------------------------------------------------------- E. contagion
rep(
  """      if(e.poisonT>0){e.hp-=e.poisonDps*dt;e.poisonT=Math.max(0,e.poisonT-dt);e.poisonTick=(e.poisonTick||0)+dt;if(e.poisonTick>.18){spawnDmgNum(e.x,e.y-e.r,e.poisonDps*.18);burst(e.x,e.y,'#7cff4f',1);e.poisonTick=0}}""",
  """      if(e.poisonT>0){e.hp-=e.poisonDps*dt;e.poisonT=Math.max(0,e.poisonT-dt);e.poisonTick=(e.poisonTick||0)+dt;if(e.poisonTick>.18){spawnDmgNum(e.x,e.y-e.r,e.poisonDps*.18);burst(e.x,e.y,'#7cff4f',1);e.poisonTick=0}
        // S.7 CONTAGION (owner spec): "if the infected hit another enemy, they get infected".
        // A carrier passes it to whatever it is touching, at spreadFactor potency so each
        // generation is weaker and a plague burns out instead of clearing the map for free.
        const sp=e.poisonSrc;
        if(sp&&e.poisonDps>.5){e.spreadCd=(e.spreadCd||0)-dt;
          if(e.spreadCd<=0){e.spreadCd=.25;
            if(Math.random()<(sp.chance??.9)*.25){
              const rad=sp.radius??52;
              for(const o of enemies){if(o===e||o.poisonT>0)continue;
                const dx=o.x-e.x,dy=o.y-e.y;if(dx*dx+dy*dy>(rad+o.r)*(rad+o.r))continue;
                o.poisonDps=e.poisonDps*(sp.factor??.7);o.poisonT=e.poisonT;o.poisonSrc=sp;
                burst(o.x,o.y,'#7cff4f',3);break}}}}}""")


# ---------------------------------------------------------------- F. carry spread data on the dart
rep(
  """        damage:dmg,pierce:wPierce(w),life:kind==='homing'?2.2:kind==='nova'?1.4:1.05,""",
  """        damage:dmg,pierce:wPierce(w),life:kind==='homing'?2.2:kind==='nova'?1.4:1.05,
        dot:(w.dot||0)*venomMul(w),dotTime:w.dotTime||0,
        spread:kind==='poison'?{chance:(w.spreadChance??.9)*venomMul(w),radius:w.spreadRadius??52,factor:w.spreadFactor??.7}:null,""")


# ---------------------------------------------------------------- G. orbs feed the weapon track
rep("""    else{xp+=p.value;orbsCollected++;burst(p.x,p.y,'#6fffe2',5);codexSee('item:xp',0)}""",
    """    else{xp+=p.value;orbsCollected++;bankOrb();burst(p.x,p.y,'#6fffe2',5);codexSee('item:xp',0)}""")


# ---------------------------------------------------------------- H. cards grant MODS, not mutations
rep(
  """function offerCards(){let weapons=[{name:'Pulse Overdrive',text:'+25% Pulse damage',apply:()=>WEAPON.damage=Math.round(WEAPON.damage*1.25)},{name:'Scatter Shot',text:'New spread weapon: +2 bolts',apply:()=>WEAPON.shots=Math.min(5,WEAPON.shots+2)},{name:'Piercing Rounds',text:'+1 projectile pierce',apply:()=>WEAPON.pierce++}]""",
  """function offerCards(){
  // S.7: weapon cards now grant a MOD attached to the held weapon's ID instead of mutating the
  // weapon object. Swapping guns no longer deletes what you just earned, and the same mod can be
  // stacked up to MOD_MAX times on one weapon (owner spec: "up to 3 times on the same weapon").
  const held=heldWeapons[0]||WEAPON;
  let weapons=MODS.filter(m=>modStacks(held.id,m.id)<MOD_MAX).map(m=>({
    name:m.name+' '+(modStacks(held.id,m.id)+1)+'/'+MOD_MAX,
    text:m.text+' — '+held.name,
    apply:()=>addMod(held.id,m.id)}))"""
)
rep("""let pool=[...weapons,...stats,...(wave>=10&&!evolved?[evo]:[])],first=cardPicks<3?weapons[Math.floor(Math.random()*weapons.length)]:null;""",
    """let pool=[...weapons,...stats,...(wave>=10&&!evolved?[evo]:[])],first=cardPicks<3&&weapons.length?weapons[Math.floor(Math.random()*weapons.length)]:null;""")


# ---------------------------------------------------------------- I. debug surface for the harness
rep("""  weapons:heldWeapons.map(w=>({id:w.id,name:w.name,kind:w.kind||'bullet',rank:w.rank||1,damage:w.damage})),""",
    """  weapons:heldWeapons.map(w=>({id:w.id,name:w.name,kind:w.kind||'bullet',rank:w.rank||1,damage:w.damage,
    shots:wShots(w),pierce:wPierce(w),mods:Object.assign({},weaponMods[w.id]||{}),orbs:weaponOrbs[w.id]||0,nextRankAt:orbsForRank(w.rank||1)})),
  weaponMods:Object.assign({},weaponMods),""")


# ---------------------------------------------------------------- J. reset per run
rep("""elapsed=score=wave=spawnBudget=fireClock=shake=xp=cardPicks=orbsCollected=0;""",
    """elapsed=score=wave=spawnBudget=fireClock=shake=xp=cardPicks=orbsCollected=0;weaponMods={};weaponOrbs={};""")

io.open(p, 'w', encoding='utf-8').write(s)
print('ok')
