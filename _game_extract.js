
'use strict';
// S.3 greybox core: world-space simulation. Deliberately contains no lanes, horizon, road, or gates.
const GAME_VERSION='0.0.9';
// S1 (Eric, playtest): HUD sat under the phone's status-bar icons (clock/battery). Read the
// safe-area inset via a probe element (env() only resolves against a real CSS property, not a
// custom property read-back) with a sensible fallback for devices/browsers without the env().
function safeAreaTop(){
  try{
    const probe=document.createElement('div');
    probe.style.cssText='position:fixed;top:0;left:0;height:0;visibility:hidden;padding-top:env(safe-area-inset-top,24px)';
    document.body.appendChild(probe);
    const v=parseFloat(getComputedStyle(probe).paddingTop)||24;
    probe.remove();
    return v;
  }catch(_){return 24}
}
const SAFE_TOP=(typeof document!=='undefined'&&document.body)?safeAreaTop():24;
const canvas=document.querySelector('#game'), ctx=canvas.getContext('2d');
const VIEW={w:540,h:960}, WORLD={halfW:810,halfH:1440,maxEnemies:220}, CAMERA={deadZone:.15}; let dpr=1;
function resize(){dpr=Math.min(devicePixelRatio||1,2);canvas.width=innerWidth*dpr;canvas.height=innerHeight*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);VIEW.w=innerWidth;VIEW.h=innerHeight} addEventListener('resize',resize);resize();
const keys=new Set(), pointer={active:false,x:0,y:0};
// Virtual thumbstick (owner request 2026-08-03): anchors where the thumb lands; idle rest bottom-centre.
const STICK={home:{x:0,y:0},base:{x:0,y:0},knob:{x:0,y:0},radius:78,dead:0.16,active:false,dx:0,dy:0};
function stickHome(){STICK.home.x=VIEW.w/2;STICK.home.y=VIEW.h-Math.min(150,VIEW.h*0.22);}
function stickSet(x,y){let dx=x-STICK.base.x,dy=y-STICK.base.y,d=Math.hypot(dx,dy);
  if(d>STICK.radius){dx*=STICK.radius/d;dy*=STICK.radius/d;d=STICK.radius}
  STICK.knob.x=STICK.base.x+dx;STICK.knob.y=STICK.base.y+dy;
  let n=d/STICK.radius;if(n<STICK.dead){STICK.dx=STICK.dy=0;return}
  STICK.dx=dx/(d||1);STICK.dy=dy/(d||1);}
function stickRelease(){STICK.active=false;STICK.dx=STICK.dy=0;stickHome();STICK.base.x=STICK.home.x;STICK.base.y=STICK.home.y;STICK.knob.x=STICK.base.x;STICK.knob.y=STICK.base.y;}
stickRelease();addEventListener('resize',stickRelease);

addEventListener('keydown',e=>{keys.add(e.key.toLowerCase());if(['arrowup','arrowdown','arrowleft','arrowright',' '].includes(e.key))e.preventDefault()});addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));
canvas.addEventListener('pointerdown',e=>{if(state!=='play')return;pointer.active=true;pointer.x=e.clientX;pointer.y=e.clientY;canvas.setPointerCapture(e.pointerId);STICK.active=true;STICK.base.x=e.clientX;STICK.base.y=e.clientY;stickSet(e.clientX,e.clientY)});canvas.addEventListener('pointermove',e=>{if(pointer.active){pointer.x=e.clientX;pointer.y=e.clientY;if(STICK.active)stickSet(e.clientX,e.clientY)}});canvas.addEventListener('pointerup',()=>{pointer.active=false;stickRelease()});canvas.addEventListener('pointercancel',()=>{pointer.active=false;stickRelease()});

// ---- FORGE values ----
const FORGE_KEY='hive_swarm_forge_values_v1', copy=o=>JSON.parse(JSON.stringify(o));
// G6 root cause (2026-08-05): budgetBase:4 spawned ~4.4 hostiles/sec on wave 1. A standing
// player was buried by ~60 bodies before the first pack even finished arriving (~15s travel),
// then contact-DPS (~8 dmg / 0.45s iframe ≈ 18 HP/s) finished them by ~12–21s. Survivors-likes
// open near 1 spawn/sec and ramp; HP was never the lever.
const FORGE_BASE={player:{speed:245,maxHp:100,pickupRadius:90},world:{halfW:810,halfH:1440,maxEnemies:220,deadZone:.15},waves:{seconds:30,baseInterval:.68,intervalPerWave:.034,budgetBase:1.15,budgetExponent:1.065},drops:{xp:1,metaChance:.08,healChance:.07,heal:12,weaponChance:.05,eliteWeaponChance:.4},weapons:[
  {id:'weapon.pulse',name:'Pulse Carbine',kind:'bullet',damage:18,rate:.16,speed:820,shots:1,pierce:2,color:'#5dfff0',range:760},
  {id:'weapon.seeker',name:'Heat Seeker',kind:'homing',damage:22,rate:.38,speed:420,shots:1,pierce:0,color:'#ff6b3d',range:900,turn:7.5},
  {id:'weapon.beam',name:'Breach Laser',kind:'beam',damage:28,rate:.08,speed:0,shots:1,pierce:99,color:'#6ea8ff',range:720,width:6},
  {id:'weapon.chain',name:'Storm Arc',kind:'chain',damage:16,rate:.32,speed:0,shots:1,pierce:4,color:'#d7a6ff',range:280,jumps:4},
  {id:'weapon.nova',name:'Nova Shell',kind:'nova',damage:34,rate:.55,speed:340,shots:1,pierce:0,color:'#ffe066',range:520,blast:78},
  {id:'weapon.poison',name:'Toxin Injector',kind:'poison',damage:6,rate:.5,speed:600,shots:1,pierce:1,color:'#7cff4f',range:640,dot:8,dotTime:3}
],entities:[{id:'enemy.shambler',name:'Shambler',r:16,hp:26,speed:68,damage:6,color:'#9ab0b4',weight:7,dropXp:1,unlockWave:1,sprite:'art_src/topdown_v1/shambler.png'},{id:'enemy.runner',name:'Runner',r:14,hp:17,speed:128,damage:6,color:'#e97088',weight:4,dropXp:1,unlockWave:4,sprite:'art_src/topdown_v1/runner.png'},{id:'enemy.crawler',name:'Crawler',r:15,hp:38,speed:96,damage:10,color:'#b5bd76',weight:3,dropXp:2,unlockWave:5,sprite:'art_src/topdown_v1/crawler.png'},{id:'enemy.necroNode',name:'Necro Node',r:23,hp:140,speed:0,damage:8,color:'#a46fca',weight:1,dropXp:5,unlockWave:6,sprite:'art_src/topdown_v1/necro_node.png'},{id:'enemy.brute',name:'Brute',r:24,hp:95,speed:42,damage:16,color:'#e5a66e',weight:2,dropXp:3,unlockWave:8,sprite:'art_src/topdown_v1/brute.png'},{id:'enemy.armored',name:'Armored Dead',r:20,hp:120,speed:54,damage:14,color:'#71889b',weight:2,dropXp:4,unlockWave:9,sprite:'art_src/topdown_v1/armored_dead.png'},{id:'enemy.mutant',name:'Mutant Enforcer',r:21,hp:175,speed:68,damage:20,color:'#d86c67',weight:1,dropXp:7,unlockWave:13,sprite:'art_src/topdown_v1/mutant_enforcer.png'},{id:'enemy.colossus',name:'Zombie Colossus',r:42,hp:1200,speed:32,damage:35,color:'#8b765f',weight:1,dropXp:20,unlockWave:10,sprite:'art_src/topdown_v1/zombie_colossus.png'}],codexPages:null};
function forgeMerge(base,saved){let next=copy(base);if(!saved||typeof saved!=='object')return next;for(const key of Object.keys(base)){if(key==='codexPages'){if(Array.isArray(saved.codexPages))next.codexPages=saved.codexPages;continue}if(Array.isArray(base[key])&&Array.isArray(saved[key])){let shipped=new Map(base[key].map(row=>[row.id,row]));next[key]=saved[key].map(row=>Object.assign({},shipped.get(row.id)||{},row));for(const row of base[key])if(!saved[key].some(x=>x.id===row.id))next[key].push(copy(row))}else if(saved[key]&&typeof saved[key]==='object'&&!Array.isArray(base[key]))Object.assign(next[key],saved[key])}return next}
let EDIT=forgeMerge(FORGE_BASE,(()=>{try{return JSON.parse(localStorage.getItem(FORGE_KEY)||'null')}catch(_){return null}})());
Object.assign(EDIT.waves,{budgetBase:EDIT.waves.budgetBase??1.15,budgetExponent:EDIT.waves.budgetExponent??1.065});
// Migrate the deadly pre-G6 default so old localStorage cannot keep the softlock.
if(EDIT.waves.budgetBase>=3.5){EDIT.waves.budgetBase=1.15;EDIT.waves.budgetExponent=1.065}
function persistForge(){try{localStorage.setItem(FORGE_KEY,JSON.stringify(EDIT))}catch(_){alert('Storage full — Forge values were not saved.')}}
if(EDIT.waves.budgetBase===1.15&&EDIT.waves.budgetExponent===1.065){try{const raw=localStorage.getItem(FORGE_KEY);if(raw&&/"budgetBase"\s*:\s*[3-9]/.test(raw))persistForge()}catch(_){}}

// ---- SAVE SLOTS (mirror HiVE WAR: 3 slots + erase; legacy single key migrates into slot 1) ----
const SAVE_SLOTS=3, LEGACY_KEY='hive_swarm_meta_v1', SLOT_PICK_KEY='hive_swarm_slot';
function metaDefaults(){return {credits:0,damage:0,hp:0,speed:0,bestScore:0,codexSeen:{},ownedWeapons:{'weapon.pulse':true},startWeapon:'weapon.pulse'}}
function slotKey(n){return LEGACY_KEY+'_s'+n}
function currentSlot(){const n=Number(localStorage.getItem(SLOT_PICK_KEY));return Number.isFinite(n)&&n>=1&&n<=SAVE_SLOTS?n:1}
function migrateLegacySave(){try{const legacy=localStorage.getItem(LEGACY_KEY);if(legacy&&localStorage.getItem(slotKey(1))===null)localStorage.setItem(slotKey(1),legacy)}catch(_){}}
function slotInfo(n){let raw=null;try{raw=localStorage.getItem(slotKey(n))}catch(_){}if(!raw)return null;try{const m=JSON.parse(raw);return{credits:m.credits||0,best:m.bestScore||0,codex:m.codexSeen?Object.keys(m.codexSeen).length:0,damage:m.damage||0,hp:m.hp||0,speed:m.speed||0}}catch(_){return null}}
function eraseSlot(n){try{localStorage.removeItem(slotKey(n))}catch(_){}if(n===currentSlot()){META=metaDefaults();saveMeta()}}
function useSlot(n){try{localStorage.setItem(SLOT_PICK_KEY,String(n))}catch(_){}META=loadMeta()}
function loadMeta(){migrateLegacySave();try{return Object.assign({},metaDefaults(),JSON.parse(localStorage.getItem(slotKey(currentSlot()))||'{}'))}catch(_){return metaDefaults()}}
function saveMeta(){try{localStorage.setItem(slotKey(currentSlot()),JSON.stringify(META))}catch(_){}}
let META=loadMeta();

// ---- BEASTIARY / CODEX (unlock on first sighting; progress is per-slot via META.codexSeen) ----
const CODEX_CATS=['enemy','boss','weapon','item','player','lore'];
const CODEX_ICON={enemy:'👾',boss:'💀',weapon:'🔫',item:'📦',player:'🎖',lore:'📖'};
const CODEX_IMG={}; // pageId -> dataURL (hydrated from IndexedDB under codex:)
let newCodexTitle='', newCodexT=0;
function codexDefaults(){
  const pages=[]; let n=0;
  const mk=(cat,title,subtitle,body,link)=>pages.push({id:'cx'+(++n),cat,title,subtitle,body:body||'',link:link||''});
  (EDIT.entities||[]).forEach(e=>mk('enemy',e.name||e.id,'Hostile',`Wave ${e.unlockWave||1}+ · HP ${e.hp} · DMG ${e.damage}`,'enemy:'+e.id));
  (EDIT.weapons||[]).forEach(w=>mk('weapon',w.name||w.id,'Weapon',`Damage ${w.damage} · rate ${w.rate}`,'weapon:'+w.id));
  // Field items — unlock the first time the player actually collects one (not on kill alone).
  mk('item','Biomatter Orb','XP Drop','Glowing scrap that feeds your mid-run level bar. Magnet range pulls it in.','item:xp');
  mk('item','Stim Pack','Health Drop','Red cross vials. Rarer than XP; only worth the detour when you are hurt.','item:heal');
  mk('player','Swarm Operative','Player','Your avatar in the open arena. Survive waves, collect biomatter, evolve loadouts.','');
  mk('lore','The Greybox','Field note','S.3 open-arena survival. No lanes, no horizon — only the swarm.','');
  return pages;
}
function codexPages(){if(!Array.isArray(EDIT.codexPages)||!EDIT.codexPages.length)EDIT.codexPages=codexDefaults();return EDIT.codexPages}
function codexNewId(){let i=1;const used=new Set(codexPages().map(p=>p.id));while(used.has('cx'+i))i++;return 'cx'+i}
function codexUnlocked(page){return !page.link||(META.codexSeen&&META.codexSeen[page.link]!==undefined)}
function codexVisible(){return codexPages().filter(codexUnlocked)}
function codexSee(link,count){
  if(!link)return;
  if(!META.codexSeen)META.codexSeen={};
  const seen=META.codexSeen, had=seen[link]!==undefined;
  seen[link]=(seen[link]||0)+(count===undefined?1:count);
  if(!had){const page=codexPages().find(p=>p.link===link);if(page){newCodexTitle=page.title;newCodexT=3}saveMeta()}
}

// ---- sprites / media (FORGE paint + IndexedDB; game prefers override dataURL) ----
const SPRITES={}; const SPRITE_OVR={}; // key -> dataURL
function spriteFor(src){
  if(!src)return null;
  // FORGE override wins when the entity id (or path) was painted/saved
  const ovr=SPRITE_OVR[src]||SPRITE_OVR['path:'+src];
  if(ovr){if(!SPRITES[ovr]){const image=new Image();image.src=ovr;SPRITES[ovr]=image}return SPRITES[ovr]}
  if(!SPRITES[src]){const image=new Image();image.src=src;SPRITES[src]=image}return SPRITES[src]
}
function entitySpriteKey(e){return e&&e.id?e.id:('path:'+(e&&e.sprite||''))}
function spriteSrcForEntity(e){const k=entitySpriteKey(e);return SPRITE_OVR[k]||(e&&e.sprite)||''}

const SFX={fire:'assets/SFX/m41a-pulse-rifle.mp3',hit:'assets/SFX/xeno attack.mp3',kill:'assets/SFX/xenotera hit.mp3'};let audioOn=true;
function sfx(name,vol=.25){if(!audioOn||!SFX[name]||typeof Audio==='undefined')return;let a=new Audio(SFX[name]);a.volume=vol;a.play().catch(()=>{})}

let player={x:0,y:0,r:16,hp:100,maxHp:100,speed:245,pickupRadius:90,inv:0,angle:0};
let orbsCollected=0;
let cam={x:0,y:0}, enemies=[], bullets=[], particles=[], pickups=[], beams=[], obstacles=[], elapsed=0, score=0, wave=1,spawnBudget=0, fireClock=0, shake=0, state='title',xp=0,level=1,nextXp=8,choices=[],cardPicks=0,excessThreat=0,evolved=false,heldWeapons=[];
let WEAPON,ENEMIES,paused=false,pauseAccum=0;
const MAX_PARTICLES=220;
// S5 — pooled floating damage numbers. Fixed-size pool, no per-hit allocation at survivors-like fire rates.
const MAX_DMGNUM=60;
const dmgNums=(()=>{const a=[];for(let i=0;i<MAX_DMGNUM;i++)a.push({active:0,x:0,y:0,vy:0,life:0,text:''});return a})();
function spawnDmgNum(x,y,amount){if(!amount)return;const o=dmgNums.find(o=>!o.active);if(!o)return;o.active=1;o.x=x+rand(-6,6);o.y=y-10;o.vy=-46;o.life=.6;o.text=Math.round(amount)+''}
// S6 — static circular obstacles. Simplest version that reads as "a map": push-out collision
// against player + enemies (no pathfinding/avoidance, no bullet blocking — see report).
function genObstacles(){
  obstacles=[];const n=14;let tries=0;
  while(obstacles.length<n&&tries<n*8){
    tries++;
    const x=rand(-WORLD.halfW+140,WORLD.halfW-140),y=rand(-WORLD.halfH+140,WORLD.halfH-140);
    if(Math.hypot(x,y)<240)continue; // keep the deploy point clear
    obstacles.push({x,y,r:rand(30,58),seed:Math.random()*999});
  }
}
function pushOutOfObstacles(body){for(const o of obstacles){let dx=body.x-o.x,dy=body.y-o.y,d=Math.hypot(dx,dy),gap=o.r+body.r;if(d<1e-4){dx=1;dy=0;d=1}if(d<gap){body.x=o.x+dx/d*gap;body.y=o.y+dy/d*gap}}}
function applyForge(){Object.assign(WORLD,EDIT.world);CAMERA.deadZone=EDIT.world.deadZone;Object.assign(player,{speed:EDIT.player.speed,maxHp:EDIT.player.maxHp,pickupRadius:EDIT.player.pickupRadius});WEAPON=EDIT.weapons[0];ENEMIES=EDIT.entities;if(EDIT.drops.weaponChance==null)EDIT.drops.weaponChance=.04;if(EDIT.drops.eliteWeaponChance==null)EDIT.drops.eliteWeaponChance=.35}applyForge();
// G7 — weapon caches, ranks, armory seed
function weaponById(id){return (EDIT.weapons||[]).find(w=>w.id===id)||EDIT.weapons[0]}
function upgradeWeapon(w){w.rank=Math.min(5,(w.rank||1)+1);w.damage=Math.round(w.damage*1.18);w.rate=Math.max(.06,+(w.rate*0.94).toFixed(3));if(w.rank%3===0)w.pierce=(w.pierce||1)+1;if(w.kind==='poison')w.dot=+((w.dot||8)*1.18).toFixed(2);return w}
function grantWeapon(id){
  const base=weaponById(id);if(!base)return;
  codexSee('weapon:'+base.id,0);
  if(!META.ownedWeapons)META.ownedWeapons={'weapon.pulse':true};
  if(!META.ownedWeapons[base.id]){META.ownedWeapons[base.id]=true;saveMeta()}
  const have=heldWeapons.find(w=>w.id===base.id);
  if(have){upgradeWeapon(have);return 'rank'}
  /* 2026-08-05: picking a weapon now REPLACES the current one (Eric, playtest). It used to hold up
     to 5 and fire ALL of them at once, so the starting pulse gun kept firing underneath every new
     weapon — you could never actually see or feel what you just picked up. Same id still ranks up. */
  heldWeapons=[Object.assign(copy(base),{rank:1})];WEAPON=heldWeapons[0];return 'swap'}
function maybeDropWeapon(x,y,elite){
  const p=elite?(EDIT.drops.eliteWeaponChance??.35):(EDIT.drops.weaponChance??.04);
  if(rand(0,1)>=p)return;
  const pool=(EDIT.weapons||[]).filter(w=>w&&w.id);if(!pool.length)return;
  const w=pool[Math.floor(Math.random()*pool.length)];
  pickups.push({x,y,weapon:1,weaponId:w.id,color:w.color||'#ffe08a'})}
function reset(){applyForge();
  if(!META.ownedWeapons)META.ownedWeapons={'weapon.pulse':true};
  const startId=(META.startWeapon&&META.ownedWeapons[META.startWeapon])?META.startWeapon:'weapon.pulse';
  const start=weaponById(startId);
  heldWeapons=[Object.assign(copy(start),{rank:1})];WEAPON=heldWeapons[0];
  player.speed=Math.round(player.speed*(1+Math.min(.25,META.speed*.05)));player.maxHp=Math.round(player.maxHp*(1+Math.min(.25,META.hp*.05)));Object.assign(player,{x:0,y:0,hp:player.maxHp,inv:0,angle:0});cam={x:0,y:0};enemies=[];bullets=[];particles=[];pickups=[];beams=[];elapsed=score=wave=spawnBudget=fireClock=shake=xp=cardPicks=orbsCollected=0;evolved=false;level=1;nextXp=8;state='play';paused=false;setPaused(false);
  genObstacles();for(const o of dmgNums)o.active=0;
  if(WEAPON&&WEAPON.id)codexSee('weapon:'+WEAPON.id,0)}
function rand(a,b){return a+Math.random()*(b-a)} function dist2(a,b){let x=a.x-b.x,y=a.y-b.y;return x*x+y*y}
function spawnEnemy(){if(enemies.length>=WORLD.maxEnemies){excessThreat++;return}
  // G6: early waves spawn from full ring (not the facing cone). The cone made "walk forward"
  // walk into every spawn and soft-locked wave 1 even at sane spawn rates.
  let a=elapsed<45||Math.random()<.35?Math.random()*Math.PI*2:player.angle+rand(-Math.PI/3,Math.PI/3);
  let distance=Math.hypot(VIEW.w,VIEW.h)*.72+rand(60,180),level=1+Math.floor(elapsed/EDIT.waves.seconds),roster=ENEMIES.filter(e=>(e.unlockWave||1)<=level),total=roster.reduce((n,e)=>n+Math.max(0,e.weight||0),0),roll=Math.random()*total,type=roster[0],boost=1+Math.min(.8,excessThreat*.04);for(const e of roster){roll-=Math.max(0,e.weight||0);if(roll<=0){type=e;break}}excessThreat=Math.max(0,excessThreat-1);let x=Math.max(-WORLD.halfW+type.r,Math.min(WORLD.halfW-type.r,player.x+Math.cos(a)*distance)),y=Math.max(-WORLD.halfH+type.r,Math.min(WORLD.halfH-type.r,player.y+Math.sin(a)*distance));
  // BEASTIARY unlocks on first SIGHTING (spawn), not kill — mirror HiVE WAR codexSee
  codexSee('enemy:'+type.id,0);
  enemies.push({x,y,r:type.r,hp:type.hp*(1+level*.13)*boost,maxHp:type.hp*(1+level*.13)*boost,speed:type.speed*(1+level*.025),damage:type.damage*boost,type,color:type.color,hit:0});}
function nearestEnemy(from,ignore){let target=null,best=Infinity;for(const e of enemies){if(ignore&&ignore.has(e))continue;let d=(from.x-e.x)**2+(from.y-e.y)**2;if(d<best){best=d;target=e}}return target}
function fire(){
  let target=nearestEnemy(player);if(!target)return;
  let a=Math.atan2(target.y-player.y,target.x-player.x);player.angle=a;
  const dmgMul=1+Math.min(.25,META.damage*.05);
  for(const w of heldWeapons){
    const kind=w.kind||'bullet', dmg=w.damage*dmgMul;
    if(kind==='beam'){
      // continuous ray — damage everything on the segment this tick
      const len=w.range||720, x2=player.x+Math.cos(a)*len, y2=player.y+Math.sin(a)*len;
      beams.push({x1:player.x,y1:player.y,x2,y2,color:w.color,life:.06,w:w.width||6});
      const hitList=[];
      for(const e of enemies){
        const px=e.x-player.x,py=e.y-player.y,segx=x2-player.x,segy=y2-player.y,t=Math.max(0,Math.min(1,(px*segx+py*segy)/(segx*segx+segy*segy||1)));
        const dx=player.x+segx*t-e.x,dy=player.y+segy*t-e.y;if(dx*dx+dy*dy<(e.r+(w.width||6))**2){const tick=dmg*w.rate*3;e.hp-=tick;e.hit=.08;spawnDmgNum(e.x,e.y-e.r,tick);if(e.hp<=0)hitList.push(e)}}
      for(const e of hitList)killEnemy(e);
      sfx('fire',.04);continue}
    if(kind==='chain'){
      let cur=target, hit=new Set(), jumps=w.jumps||4, from={x:player.x,y:player.y};
      for(let j=0;j<jumps&&cur;j++){
        beams.push({x1:from.x,y1:from.y,x2:cur.x,y2:cur.y,color:w.color,life:.12,w:3,chain:1});
        const jd=dmg*(1-j*0.12);cur.hp-=jd;cur.hit=.12;spawnDmgNum(cur.x,cur.y-cur.r,jd);hit.add(cur);if(cur.hp<=0)killEnemy(cur);
        from={x:cur.x,y:cur.y};cur=nearestEnemy(from,hit);
        if(cur&&(cur.x-from.x)**2+(cur.y-from.y)**2>(w.range||280)**2)cur=null}
      sfx('hit',.1);continue}
    // projectile kinds: bullet / homing / nova
    sfx('fire',kind==='nova'?.12:.08);
    for(let i=0;i<w.shots;i++){
      let spread=(i-(w.shots-1)/2)*.1;
      const ang=a+spread;
      bullets.push({
        x:player.x+Math.cos(ang)*18,y:player.y+Math.sin(ang)*18,
        vx:Math.cos(ang)*(w.speed||700),vy:Math.sin(ang)*(w.speed||700),
        r:kind==='nova'?7:kind==='homing'?5:4,
        damage:dmg,pierce:w.pierce??0,life:kind==='homing'?2.2:kind==='nova'?1.4:1.05,
        color:w.color,kind,turn:w.turn||0,blast:w.blast||0,trail:[]
      })}}}
function killEnemy(e,gibs){
  const idx=enemies.indexOf(e);if(idx<0)return;
  score+=10;sfx('kill',.18);codexSee('enemy:'+e.type.id);
  const elite=(e.type.dropXp||0)>=5;if(elite){META.credits++;saveMeta()}
  pickups.push({x:e.x,y:e.y,value:(e.type.dropXp||1)*EDIT.drops.xp});
  if(rand(0,1)<(EDIT.drops.healChance!==undefined?EDIT.drops.healChance:.07))
    pickups.push({x:e.x+rand(-14,14),y:e.y+rand(-14,14),heal:1,value:EDIT.drops.heal||12});
  maybeDropWeapon(e.x+rand(-10,10),e.y+rand(-10,10),elite);
  explode(e.x,e.y,e.color||'#ff8',42,gibs);enemies.splice(idx,1)}
function burst(x,y,color,n=8){n=Math.min(n,MAX_PARTICLES-particles.length);for(let i=0;i<n;i++){let a=Math.random()*6.283,s=rand(25,160);particles.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:rand(.25,.6),color,r:rand(1.5,3.5)})}}
// S3 — Heat Seeker kills gib enemies into rotating debris chunks, on top of the existing puff.
// Same particle pool/budget as burst(); a dedicated draw-time shape (rotated rect) makes them
// read as "bits" instead of more circular spark.
function spawnGibs(x,y,color){const n=Math.min(6,MAX_PARTICLES-particles.length);for(let i=0;i<n;i++){let a=Math.random()*6.283,s=rand(60,220);particles.push({x,y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,life:rand(.35,.7),color,r:rand(2,4),gib:1,rot:Math.random()*6.283,rvel:rand(-8,8)})}}
function explode(x,y,color,r=60,gibs){// shockwave + debris + shake — budgeted particle count
  /* 2026-08-05: this ran on EVERY enemy death and re-armed shake to a full 10 each time. Decay is
     only ~25/s, so at survivors-like kill rates the screen never stopped shaking and the game was
     hard to play (Eric, playtest). Now a kill adds a small amount against a low cap; only genuinely
     big events (player hit, nova blast) are allowed to jolt harder, via their own shake= lines. */
  shake=Math.min(4.5,shake+1.6);burst(x,y,color,14);burst(x,y,'#fff6c8',8);
  if(gibs)spawnGibs(x,y,color);
  particles.push({x,y,vx:0,vy:0,life:.28,color,shock:r});
  for(const e of enemies){const d=Math.hypot(e.x-x,e.y-y);if(d<r){e.hp-=22*(1-d/r);e.hit=.15;if(d>1){e.x+=(e.x-x)/d*18;e.y+=(e.y-y)/d*18}}}}
function setPaused(on){
  if(state!=='play'&&state!=='levelup'&&!(paused&&on===false)){if(state==='title'||state==='dead')return}
  if(on===paused)return;
  paused=!!on;pauseAccum=0;
  const btn=document.getElementById('pauseBtn'), ov=document.getElementById('pauseOverlay');
  if(btn){btn.textContent=paused?'▶':'⏸';btn.title=paused?'Resume (P / Esc)':'Pause (P / Esc)';btn.setAttribute('aria-label',paused?'Resume':'Pause')}
  if(ov)ov.classList.toggle('on',paused);
  // Do NOT drain spawnBudget/fireClock while paused — they simply stop advancing.
}
function togglePause(){if(state==='play'||paused)setPaused(!paused)}
function followCamera(){let dx=player.x-cam.x,dy=player.y-cam.y,deadX=VIEW.w*CAMERA.deadZone,deadY=VIEW.h*CAMERA.deadZone;if(Math.abs(dx)>deadX)cam.x+=dx-Math.sign(dx)*deadX;if(Math.abs(dy)>deadY)cam.y+=dy-Math.sign(dy)*deadY;cam.x=Math.max(-WORLD.halfW+VIEW.w/2,Math.min(WORLD.halfW-VIEW.w/2,cam.x));cam.y=Math.max(-WORLD.halfH+VIEW.h/2,Math.min(WORLD.halfH-VIEW.h/2,cam.y));}
function update(dt){if(newCodexT>0)newCodexT=Math.max(0,newCodexT-dt);
  if(paused){// freeze sim: no spawnBudget/fireClock/enemy advance — resume is frame-clean
    for(let i=beams.length-1;i>=0;i--){beams[i].life-=dt;if(beams[i].life<=0)beams.splice(i,1)}
    return}
  if(state!=='play')return;elapsed+=dt;wave=1+Math.floor(elapsed/EDIT.waves.seconds);player.inv=Math.max(0,player.inv-dt);let dx=(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0),dy=(keys.has('s')||keys.has('arrowdown')?1:0)-(keys.has('w')||keys.has('arrowup')?1:0);if(STICK.active&&(STICK.dx||STICK.dy)){dx=STICK.dx;dy=STICK.dy}let mag=Math.hypot(dx,dy);if(mag){player.x+=dx/mag*player.speed*dt;player.y+=dy/mag*player.speed*dt;player.angle=Math.atan2(dy,dx)}player.x=Math.max(-WORLD.halfW+player.r,Math.min(WORLD.halfW-player.r,player.x));player.y=Math.max(-WORLD.halfH+player.r,Math.min(WORLD.halfH-player.r,player.y));pushOutOfObstacles(player);followCamera();
spawnBudget+=dt*EDIT.waves.budgetBase*Math.pow(EDIT.waves.budgetExponent,wave);while(spawnBudget>=1){spawnBudget-=1;spawnEnemy()}fireClock-=dt;if(fireClock<=0){fireClock+=Math.max(.05,WEAPON.rate||.16);fire()}
for(let i=enemies.length-1;i>=0;i--){let e=enemies[i],vx=player.x-e.x,vy=player.y-e.y,d=Math.hypot(vx,vy)||1;e.x+=vx/d*e.speed*dt;e.y+=vy/d*e.speed*dt;for(let j=0;j<i;j++){let o=enemies[j],sx=e.x-o.x,sy=e.y-o.y,sd=Math.hypot(sx,sy)||.01,gap=(e.r+o.r)*.8;if(sd<gap){let push=(gap-sd)*.5;e.x+=sx/sd*push;e.y+=sy/sd*push;o.x-=sx/sd*push;o.y-=sy/sd*push}}pushOutOfObstacles(e);e.hit=Math.max(0,e.hit-dt);
      // S4 — poison DoT tick: keeps draining after the hit lands, independent of contact/bullet damage.
      if(e.poisonT>0){e.hp-=e.poisonDps*dt;e.poisonT=Math.max(0,e.poisonT-dt);e.poisonTick=(e.poisonTick||0)+dt;if(e.poisonTick>.18){spawnDmgNum(e.x,e.y-e.r,e.poisonDps*.18);burst(e.x,e.y,'#7cff4f',1);e.poisonTick=0}}
      if(d<e.r+player.r){if(!player.inv){player.hp-=e.damage;player.inv=.7;shake=8;burst(player.x,player.y,'#ff718a',14);
        player.x-=vx/d*18;player.y-=vy/d*18;
        if(player.hp<=0){player.hp=0;if(score>(META.bestScore||0)){META.bestScore=score;saveMeta()}state='dead';setPaused(false)}}e.x-=vx/d*28;e.y-=vy/d*28}}
for(let i=bullets.length-1;i>=0;i--){let b=bullets[i];
  if(b.kind==='homing'){const t=nearestEnemy(b);if(t){const desired=Math.atan2(t.y-b.y,t.x-b.x),cur=Math.atan2(b.vy,b.vx);let diff=((desired-cur+Math.PI*3)%(Math.PI*2))-Math.PI;const maxTurn=(b.turn||7)*dt;diff=Math.max(-maxTurn,Math.min(maxTurn,diff));const sp=Math.hypot(b.vx,b.vy)||400;const na=cur+diff;b.vx=Math.cos(na)*sp;b.vy=Math.sin(na)*sp}}
  b.x+=b.vx*dt;b.y+=b.vy*dt;b.life-=dt;
  if(b.trail){b.trail.push(b.x,b.y);if(b.trail.length>16)b.trail.splice(0,2)}
  let removed=b.life<=0;
  if(removed&&b.kind==='nova')explode(b.x,b.y,b.color||'#ffe066',b.blast||70);
  for(let j=enemies.length-1;j>=0&&!removed;j--){let e=enemies[j],r=e.r+b.r;if((e.x-b.x)**2+(e.y-b.y)**2<r*r){
    if(b.kind==='nova'){explode(b.x,b.y,b.color||'#ffe066',b.blast||70);removed=true;break}
    if(b.kind==='poison'){e.poisonDps=Math.max(e.poisonDps||0,b.dot||8);e.poisonT=Math.max(e.poisonT||0,b.dotTime||3);e.hit=.1;sfx('hit',.06);burst(b.x,b.y,b.color||'#7cff4f',3);b.pierce--;if(b.pierce<0)removed=true;continue}
    e.hp-=b.damage;e.hit=.1;sfx('hit',.08);burst(b.x,b.y,b.color||WEAPON.color,4);spawnDmgNum(e.x,e.y-e.r,b.damage);b.pierce--;
    if(e.hp<=0)killEnemy(e,b.kind==='homing');if(b.pierce<0)removed=true}}
  if(removed)bullets.splice(i,1)}
for(let i=beams.length-1;i>=0;i--){beams[i].life-=dt;if(beams[i].life<=0)beams.splice(i,1)}
// clean dead marked by beam damage mid-loop
for(let i=enemies.length-1;i>=0;i--)if(enemies[i].hp<=0)killEnemy(enemies[i]);
// XP orbs — pickupRadius is magnet reach; bank only on touch.
for(let i=pickups.length-1;i>=0;i--){let p=pickups[i],dx=player.x-p.x,dy=player.y-p.y,d=Math.hypot(dx,dy)||1;
  p.t=(p.t||0)+dt;p.vx=p.vx||0;p.vy=p.vy||0;
  if(d<player.pickupRadius){
    let ux=dx/d,uy=dy/d,pull=520*(1-d/player.pickupRadius)+180;
    p.vx+=ux*pull*dt;p.vy+=uy*pull*dt;
    let tang=-p.vx*uy+p.vy*ux, damp=Math.min(1,6*dt);
    p.vx+=uy*tang*damp;p.vy-=ux*tang*damp;
    if(d<player.r+42){let sp=Math.max(340,Math.hypot(p.vx,p.vy));p.vx=ux*sp;p.vy=uy*sp}
    p.pulled=1;p.trail=p.trail||[];p.trail.push(p.x,p.y);if(p.trail.length>10)p.trail.splice(0,2);
  }
  else{p.vx*=Math.pow(.02,dt);p.vy*=Math.pow(.02,dt);p.pulled=0;if(p.trail)p.trail.length=0}
  p.x+=p.vx*dt;p.y+=p.vy*dt;
  if(d<player.r+10){
    if(p.weapon){grantWeapon(p.weaponId);burst(p.x,p.y,p.color||'#ffe08a',10);sfx('kill',.12)}
    else if(p.heal){player.hp=Math.min(player.maxHp,player.hp+p.value);burst(p.x,p.y,'#ff5f7a',7);codexSee('item:heal',0)}
    else{xp+=p.value;orbsCollected++;burst(p.x,p.y,'#6fffe2',5);codexSee('item:xp',0)}
    sfx('hit',.05);pickups.splice(i,1);
    if(!p.heal&&!p.weapon&&xp>=nextXp){xp-=nextXp;level++;nextXp=Math.ceil(nextXp*1.35);state='levelup';offerCards()}}}
for(let i=particles.length-1;i>=0;i--){let p=particles[i];p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt;if(p.gib)p.rot=(p.rot||0)+(p.rvel||0)*dt;if(p.life<=0)particles.splice(i,1)}
// S5 — advance pooled damage numbers (float up, gravity, fade); no allocation here.
for(let i=0;i<dmgNums.length;i++){const o=dmgNums[i];if(!o.active)continue;o.y+=o.vy*dt;o.vy+=40*dt;o.life-=dt;if(o.life<=0)o.active=0}
shake=Math.max(0,shake-dt*25)}
function sx(x){return x-cam.x+VIEW.w/2}function sy(y){return y-cam.y+VIEW.h/2}
// QA probe — Playwright cannot see script-scoped let; publish on window.
window.__swarmDbg=()=>({state,wave,elapsed,score,level,xp,nextXp,orbsCollected,
  pickups:pickups.length,enemies:enemies.length,hp:player.hp,px:Math.round(player.x),py:Math.round(player.y),
  slot:currentSlot(),codexUnlocked:codexVisible().length,codexTotal:codexPages().length,
  credits:META.credits||0,bestScore:META.bestScore||0,paused,version:GAME_VERSION,
  weapons:heldWeapons.map(w=>({id:w.id,name:w.name,kind:w.kind||'bullet',rank:w.rank||1,damage:w.damage})),
  startWeapon:META.startWeapon||'weapon.pulse',bullets:bullets.length,beams:beams.length,particles:particles.length,
  obstacles:obstacles.length,poisoned:enemies.filter(e=>e.poisonT>0).length,dmgNumsActive:dmgNums.filter(o=>o.active).length,
  stick:{active:STICK.active,dx:Math.round(STICK.dx*100)/100,dy:Math.round(STICK.dy*100)/100,
         baseX:Math.round(STICK.base.x),baseY:Math.round(STICK.base.y),homeX:Math.round(STICK.home.x),homeY:Math.round(STICK.home.y)}});
window.__swarmPause=setPaused;window.__swarmTogglePause=togglePause;
function draw(){ctx.fillStyle='#050b14';ctx.fillRect(0,0,VIEW.w,VIEW.h);let ox=rand(-shake,shake),oy=rand(-shake,shake);ctx.save();ctx.translate(ox,oy);ctx.strokeStyle='#0f2a38';ctx.lineWidth=1;let grid=80,startX=(-cam.x%grid+grid)%grid,startY=(-cam.y%grid+grid)%grid;for(let x=startX;x<VIEW.w;x+=grid){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,VIEW.h);ctx.stroke()}for(let y=startY;y<VIEW.h;y+=grid){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(VIEW.w,y);ctx.stroke()}
// S6 — static obstacles (procedural rock-cluster shapes, deterministic per-seed so they don't
// flicker frame to frame). Push-out collision handled in update(); drawn under everything else.
for(const o of obstacles){const ox2=sx(o.x),oy2=sy(o.y);if(ox2<-80||ox2>VIEW.w+80||oy2<-80||oy2>VIEW.h+80)continue;
  ctx.save();ctx.translate(ox2,oy2);ctx.fillStyle='#2a3d3a';ctx.strokeStyle='#5a7d76';ctx.lineWidth=2;ctx.shadowColor='#000';ctx.shadowBlur=14;
  ctx.beginPath();const spikes=7;
  for(let i=0;i<=spikes;i++){const ang=i/spikes*6.283,rr=o.r*(0.75+((Math.sin((o.seed+i)*12.9898)*43758.5453)%1+1)%1*0.45),px=Math.cos(ang)*rr,py=Math.sin(ang)*rr;if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py)}
  ctx.closePath();ctx.fill();ctx.stroke();ctx.shadowBlur=0;
  ctx.fillStyle='rgba(120,239,219,.12)';ctx.beginPath();ctx.arc(-o.r*.25,-o.r*.25,o.r*.35,0,7);ctx.fill();
  ctx.restore()}
// beams (laser + chain) under projectiles
for(const b of beams){ctx.save();ctx.globalAlpha=Math.min(1,b.life*10);ctx.strokeStyle=b.color||'#6ea8ff';ctx.shadowColor=b.color||'#6ea8ff';ctx.shadowBlur=b.chain?18:28;ctx.lineWidth=b.w||4;ctx.lineCap='round';
  ctx.beginPath();ctx.moveTo(sx(b.x1),sy(b.y1));if(b.chain){const mx=(b.x1+b.x2)/2+rand(-8,8),my=(b.y1+b.y2)/2+rand(-8,8);ctx.lineTo(sx(mx),sy(my))}ctx.lineTo(sx(b.x2),sy(b.y2));ctx.stroke();ctx.restore()}
for(const p of particles){ctx.globalAlpha=Math.min(1,p.life*3);ctx.fillStyle=p.color;
  if(p.shock){ctx.strokeStyle=p.color;ctx.lineWidth=3;ctx.shadowColor=p.color;ctx.shadowBlur=20;ctx.beginPath();ctx.arc(sx(p.x),sy(p.y),p.shock*(1-p.life/.28),0,7);ctx.stroke();ctx.shadowBlur=0}
  else if(p.gib){const rr=p.r||2;ctx.save();ctx.translate(sx(p.x),sy(p.y));ctx.rotate(p.rot||0);ctx.shadowColor=p.color;ctx.shadowBlur=6;ctx.fillRect(-rr,-rr*.6,rr*2,rr*1.2);ctx.restore();ctx.shadowBlur=0}
  else{const rr=p.r||2;ctx.shadowColor=p.color;ctx.shadowBlur=10;ctx.beginPath();ctx.arc(sx(p.x),sy(p.y),rr,0,7);ctx.fill();ctx.shadowBlur=0}}ctx.globalAlpha=1;
// S5 — pooled floating damage numbers, drawn in world space (camera + shake applied).
ctx.textAlign='center';ctx.font='700 13px system-ui';
for(const o of dmgNums){if(!o.active)continue;ctx.globalAlpha=Math.max(0,Math.min(1,o.life/.6));ctx.fillStyle='#fff';ctx.fillText(o.text,sx(o.x),sy(o.y))}
ctx.globalAlpha=1;ctx.textAlign='left';
for(const b of bullets){const col=b.color||WEAPON.color;
  if(b.trail&&b.trail.length>3){ctx.strokeStyle=col;ctx.lineWidth=b.kind==='homing'?3:2;ctx.lineCap='round';ctx.shadowColor=col;ctx.shadowBlur=12;
    for(let k=0;k<b.trail.length-2;k+=2){ctx.globalAlpha=.08+.45*(k/b.trail.length);ctx.beginPath();ctx.moveTo(sx(b.trail[k]),sy(b.trail[k+1]));ctx.lineTo(sx(b.trail[k+2]),sy(b.trail[k+3]));ctx.stroke()}ctx.globalAlpha=1;ctx.shadowBlur=0}
  ctx.fillStyle=col;ctx.shadowColor=col;ctx.shadowBlur=b.kind==='nova'?22:16;
  if(b.kind==='nova'){ctx.beginPath();ctx.arc(sx(b.x),sy(b.y),b.r,0,7);ctx.fill();ctx.fillStyle='#fff8c8';ctx.beginPath();ctx.arc(sx(b.x),sy(b.y),b.r*.45,0,7);ctx.fill()}
  else if(b.kind==='homing'){const ang=Math.atan2(b.vy,b.vx);ctx.save();ctx.translate(sx(b.x),sy(b.y));ctx.rotate(ang);ctx.fillRect(-8,-3,14,6);ctx.fillStyle='#fff';ctx.fillRect(4,-2,6,4);ctx.restore()}
  else{ctx.beginPath();ctx.arc(sx(b.x),sy(b.y),b.r,0,7);ctx.fill()}ctx.shadowBlur=0}
for(const p of pickups){let x=sx(p.x),y=sy(p.y),bob=Math.sin((p.t||0)*6)*1.6,
    r=p.weapon?8:p.heal?6:4+Math.min(3,(p.value||1)*.5),
    col=p.weapon?(p.color||'#ffe08a'):p.heal?'#ff5f7a':'#8ffff0',glow=p.weapon?'#ffd76a':p.heal?'#ff2d55':'#6fffe2';
  ctx.save();
  if(p.pulled&&p.trail&&p.trail.length>3){ctx.strokeStyle=glow;ctx.lineWidth=r*.9;ctx.lineCap='round';
    for(let k=0;k<p.trail.length-2;k+=2){ctx.globalAlpha=.06+.5*(k/p.trail.length);
      ctx.beginPath();ctx.moveTo(sx(p.trail[k]),sy(p.trail[k+1]));ctx.lineTo(sx(p.trail[k+2]),sy(p.trail[k+3]));ctx.stroke()}
    ctx.globalAlpha=1}
  ctx.shadowColor=glow;ctx.shadowBlur=p.pulled?18:10;ctx.fillStyle=col;
  if(p.weapon){ctx.fillRect(x-r,y+bob-r*.6,r*2,r*1.2);ctx.fillStyle='#111';ctx.fillRect(x-r*.3,y+bob-r*1.1,r*.6,r*.5)}
  else{ctx.beginPath();ctx.arc(x,y+bob,r,0,7);ctx.fill()}
  if(p.heal){ctx.fillStyle='#fff';ctx.fillRect(x-1.4,y+bob-4,2.8,8);ctx.fillRect(x-4,y+bob-1.4,8,2.8)}
  ctx.globalAlpha=.35;ctx.strokeStyle=glow;ctx.lineWidth=1;ctx.beginPath();ctx.arc(x,y+bob,r+3,0,7);ctx.stroke();ctx.restore()}
/* 2026-08-05 enemy-art fix: this passed the entity KEY ('enemy.shambler') to spriteFor(), which
   treats its argument as an image SOURCE. With no FORGE override present it did
   new Image().src='enemy.shambler' -> a bogus URL -> a truthy Image, so the `||` fallback to the
   real path never ran, naturalWidth stayed 0, and every enemy drew as the plain circle.
   spriteSrcForEntity() resolves override-or-path correctly, which is what spriteFor() wants. */
for(const e of enemies){let x=sx(e.x),y=sy(e.y),img=spriteFor(spriteSrcForEntity(e.type));if(img&&img.complete&&img.naturalWidth){let s=e.r*2.7;ctx.globalAlpha=e.hit?.72:1;ctx.drawImage(img,x-s/2,y-s/2,s,s);ctx.globalAlpha=1}else{ctx.fillStyle=e.hit?'#fff':e.color;ctx.beginPath();ctx.arc(x,y,e.r,0,7);ctx.fill()}
  // S4 — visually distinct poison tell: pulsing green ring while a DoT stack is active.
  if(e.poisonT>0){ctx.globalAlpha=.35;ctx.fillStyle='#7cff4f';ctx.beginPath();ctx.arc(x,y,e.r*1.15,0,7);ctx.fill();ctx.globalAlpha=1}
  ctx.fillStyle='#152025';ctx.fillRect(x-e.r,y-e.r-8,e.r*2,3);ctx.fillStyle='#8aff9b';ctx.fillRect(x-e.r,y-e.r-8,e.r*2*(e.hp/e.maxHp),3)}
let px=sx(player.x),py=sy(player.y);ctx.save();ctx.translate(px,py);ctx.rotate(player.angle);ctx.fillStyle=player.inv?'#ffffff':'#6fffe2';ctx.beginPath();ctx.arc(0,0,player.r,0,7);ctx.fill();ctx.fillStyle='#dff';ctx.fillRect(8,-4,22,8);ctx.restore();ctx.restore();
/* S1 (Eric, playtest): the whole HUD sat under the phone's status-bar icons (clock/battery).
   Every HUD y-coordinate below is shifted down by SAFE_TOP (safe-area-inset-top + fallback,
   computed once at load — see SAFE_TOP above) instead of a hardcoded magic number. */
ctx.fillStyle='#dce9e7';ctx.font='700 16px system-ui';ctx.fillText('HiVE SWARM  ·  WAVE '+wave,18,32+SAFE_TOP);ctx.font='14px system-ui';ctx.fillStyle='#a5c3be';ctx.fillText('SURVIVAL '+formatTime(elapsed)+'   SCORE '+score+'   HOSTILES '+enemies.length,18,55+SAFE_TOP);ctx.fillStyle='#26383a';ctx.fillRect(18,70+SAFE_TOP,180,10);ctx.fillStyle=player.hp>30?'#64e7b5':'#ff718a';ctx.fillRect(18,70+SAFE_TOP,180*player.hp/player.maxHp,10);ctx.fillStyle='#dce9e7';ctx.fillText('HP '+Math.ceil(player.hp)+' / '+player.maxHp,205,80+SAFE_TOP);
ctx.fillStyle='#1b2f33';ctx.fillRect(18,88+SAFE_TOP,180,8);ctx.fillStyle='#6fffe2';ctx.fillRect(18,88+SAFE_TOP,180*Math.max(0,Math.min(1,xp/nextXp)),8);
ctx.fillStyle='#9fded2';ctx.font='13px system-ui';ctx.fillText('LVL '+level+'   XP '+Math.floor(xp)+' / '+nextXp+'   ◆ '+orbsCollected+'   🔫 '+heldWeapons.length,205,96+SAFE_TOP);
// S2 — current weapon name, top-centre, just below the phone icons. Updates whenever grantWeapon
// replaces heldWeapons[0] (or upgradeWeapon renames rank-ups — name itself doesn't change on rank).
if((state==='play'||state==='levelup')&&heldWeapons[0]){ctx.save();ctx.textAlign='center';ctx.fillStyle='#ffe066';ctx.font='700 14px system-ui';ctx.shadowColor='#000';ctx.shadowBlur=4;
  ctx.fillText((heldWeapons[0].name||'')+(heldWeapons[0].rank>1?'  Rk.'+heldWeapons[0].rank:''),VIEW.w/2,20+SAFE_TOP);ctx.restore()}
if(state==='play'){let bx=STICK.active?STICK.base.x:STICK.home.x,by=STICK.active?STICK.base.y:STICK.home.y,
  kx=STICK.active?STICK.knob.x:bx,ky=STICK.active?STICK.knob.y:by;
  ctx.save();ctx.globalAlpha=STICK.active?.34:.16;ctx.strokeStyle='#6fffe2';ctx.lineWidth=2;
  ctx.beginPath();ctx.arc(bx,by,STICK.radius,0,7);ctx.stroke();
  ctx.globalAlpha=STICK.active?.5:.22;ctx.fillStyle='#6fffe2';ctx.beginPath();ctx.arc(kx,ky,26,0,7);ctx.fill();ctx.restore()}
if(state==='title'||state==='dead'){ctx.fillStyle='rgba(3,8,10,.72)';ctx.fillRect(0,0,VIEW.w,VIEW.h);ctx.textAlign='center';ctx.fillStyle='#e4fff8';ctx.font='700 34px system-ui';ctx.fillText(state==='dead'?'RUN ENDED':'HiVE SWARM',VIEW.w/2,VIEW.h/2-80);ctx.save();ctx.font='12px system-ui';ctx.fillStyle='rgba(150,200,190,.55)';ctx.fillText('v'+GAME_VERSION,VIEW.w/2,VIEW.h/2-58);ctx.restore();ctx.font='16px system-ui';ctx.fillStyle='#b3cbc7';ctx.fillText(state==='dead'?'Score '+score+' · survived '+formatTime(elapsed):'Open arena survival greybox',VIEW.w/2,VIEW.h/2-30);ctx.fillStyle='#8ab';ctx.font='14px system-ui';ctx.fillText('SLOT '+currentSlot()+'  ·  '+ (META.credits||0)+' biomatter  ·  best '+(META.bestScore||0),VIEW.w/2,VIEW.h/2-6);ctx.fillStyle='#6fffe2';ctx.font='16px system-ui';ctx.fillText('Click or press Enter to deploy',VIEW.w/2,VIEW.h/2+28);ctx.textAlign='left'}
// First-sighting toast
if(newCodexT>0&&newCodexTitle){const a=Math.min(1,newCodexT/.5);ctx.save();ctx.globalAlpha=a;ctx.textAlign='center';
  ctx.fillStyle='rgba(60,20,90,.82)';ctx.fillRect(VIEW.w/2-170,96,340,52);ctx.strokeStyle='#c6f';ctx.strokeRect(VIEW.w/2-170,96,340,52);
  ctx.fillStyle='#e8d8ff';ctx.font='bold 13px system-ui';ctx.fillText('NEW BEASTIARY ENTRY',VIEW.w/2,118);
  ctx.fillStyle='#fff';ctx.font='bold 18px system-ui';ctx.fillText(newCodexTitle,VIEW.w/2,140);ctx.restore()}
if(typeof ensureTitleChrome==='function')ensureTitleChrome();
}
function formatTime(t){return Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0')}
function tryDeploy(){if(state==='title'||state==='dead'){setPaused(false);reset()}}
addEventListener('keydown',e=>{
  if(e.key==='Enter')tryDeploy();
  if(e.key==='Escape'||e.key==='p'||e.key==='P'){e.preventDefault();togglePause()}
});
canvas.addEventListener('click',()=>{if(state==='title'||state==='dead')tryDeploy()});
(function wirePauseBtn(){
  const btn=document.getElementById('pauseBtn');if(!btn)return;
  btn.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();togglePause()});
})();
let last=performance.now(),accumulator=0;function frame(now){accumulator+=Math.min(.05,(now-last)/1000);last=now;while(accumulator>=1/60){update(1/60);accumulator-=1/60}draw();requestAnimationFrame(frame)}requestAnimationFrame(frame);
window.__hiveSwarmDebug=()=>({state,elapsed,score,wave,enemies:enemies.length,heldWeapons:heldWeapons.length,player:{x:player.x,y:player.y,hp:player.hp},camera:cam,slot:currentSlot(),codex:codexVisible().length});
function offerCards(){let weapons=[{name:'Pulse Overdrive',text:'+25% Pulse damage',apply:()=>WEAPON.damage=Math.round(WEAPON.damage*1.25)},{name:'Scatter Shot',text:'New spread weapon: +2 bolts',apply:()=>WEAPON.shots=Math.min(5,WEAPON.shots+2)},{name:'Piercing Rounds',text:'+1 projectile pierce',apply:()=>WEAPON.pierce++}],stats=[{name:'Fleet Footed',text:'+12% movement speed',apply:()=>player.speed=Math.round(player.speed*1.12)},{name:'Reinforced',text:'+25 max HP and heal',apply:()=>{player.maxHp+=25;player.hp=Math.min(player.maxHp,player.hp+25)}},{name:'Magnet',text:'+45 pickup radius',apply:()=>player.pickupRadius+=45}],evo={name:'Plasma Evolution',text:'Wave 10 evolution: double pulse damage',apply:()=>{WEAPON.damage*=2;evolved=true}};let pool=[...weapons,...stats,...(wave>=10&&!evolved?[evo]:[])],first=cardPicks<3?weapons[Math.floor(Math.random()*weapons.length)]:null;choices=[];if(first)choices.push(first);while(choices.length<3&&pool.length){let c=pool.splice(Math.floor(Math.random()*pool.length),1)[0];if(!choices.includes(c))choices.push(c)}
  // Headless harness has no real DOM — auto-pick so balance sims are not stuck on the chooser.
  if(typeof HTMLElement==='undefined'){if(choices[0])choices[0].apply();cardPicks++;state='play';return}
  let box=document.createElement('div');box.id='cards';box.className='overlay';box.innerHTML='<h2>LEVEL '+level+' — CHOOSE ONE</h2>'+choices.map((c,i)=>`<button data-card="${i}" style="width:260px;padding:18px;background:#16383a;color:#eafffa;border:1px solid #75f0db;border-radius:8px"><b>${c.name}</b><br>${c.text}</button>`).join('');document.body.append(box);box.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{choices[Number(b.dataset.card)].apply();cardPicks++;box.remove();state='play'})}
function openMeta(){if(document.querySelector('#meta'))return;let box=document.createElement('div');box.id='meta';box.className='overlay';
  if(!META.ownedWeapons)META.ownedWeapons={'weapon.pulse':true};
  let render=()=>{const owned=Object.keys(META.ownedWeapons||{}).filter(id=>META.ownedWeapons[id]);
    const armory=(EDIT.weapons||[]).map(w=>{const have=!!META.ownedWeapons[w.id];const start=META.startWeapon===w.id;
      const cost=have?0:(w.id==='weapon.seeker'?4:w.id==='weapon.beam'?5:w.id==='weapon.chain'?5:w.id==='weapon.nova'?6:3);
      return `<button data-arm="${w.id}" ${have&&start?'style="outline:2px solid #6fffe2"':''}>${start?'▶ ':''}${w.name}${have?' · OWNED · set start':' · BUY '+cost}</button>`}).join('');
    box.innerHTML=`<h2>META + ARMORY</h2><p>SLOT ${currentSlot()} · ${META.credits} biomatter · ranks 5% each (cap 25%)</p>
      ${['damage','hp','speed'].map(k=>`<button data-meta="${k}">${k.toUpperCase()} ${META[k]}/5 · cost ${META[k]+1}</button>`).join('')}
      <h3 style="margin:12px 0 6px;color:#ffe08a">STARTING WEAPON</h3><p style="color:#9ebbb6;max-width:420px;margin:0 auto 8px">Buy with biomatter (from elite kills). Owned guns can be set as your deploy loadout. Field caches still drop mid-run.</p>
      ${armory}<br><button id="metaClose">Close</button>`;
    box.querySelectorAll('[data-meta]').forEach(b=>b.onclick=()=>{let k=b.dataset.meta,cost=META[k]+1;if(META[k]<5&&META.credits>=cost){META.credits-=cost;META[k]++;saveMeta();render()}});
    box.querySelectorAll('[data-arm]').forEach(b=>b.onclick=()=>{const id=b.dataset.arm;const w=weaponById(id);if(!w)return;
      if(META.ownedWeapons[id]){META.startWeapon=id;saveMeta();render();return}
      const cost=id==='weapon.seeker'?4:id==='weapon.beam'?5:id==='weapon.chain'?5:id==='weapon.nova'?6:3;
      if(META.credits>=cost){META.credits-=cost;META.ownedWeapons[id]=true;META.startWeapon=id;saveMeta();codexSee('weapon:'+id,0);render()}});
    box.querySelector('#metaClose').onclick=()=>box.remove()};render();document.body.append(box)}
function openSlots(){if(document.querySelector('#slots'))return;const box=document.createElement('div');box.id='slots';box.className='overlay';
  const render=()=>{box.innerHTML=`<h2>💾 SAVE SLOTS</h2><p>tap a slot to play it · ERASE wipes that save (campaign, credits, beastiary)</p>`+
    [1,2,3].map(i=>{const info=slotInfo(i),on=i===currentSlot();return `<div class="slot${on?' on':''}" data-slot="${i}"><button type="button" data-erase="${i}" ${info?'':'disabled'}>ERASE</button><b>SLOT ${i}${on?' · ACTIVE':''}</b><br>${info?`${info.credits} biomatter · beastiary ${info.codex} · best ${info.best}`:'empty — tap to start fresh'}</div>`}).join('')+
    `<button id="slotsClose">Close</button>`;
    box.querySelectorAll('[data-slot]').forEach(el=>el.onclick=e=>{if(e.target.dataset.erase)return;useSlot(Number(el.dataset.slot));render()});
    box.querySelectorAll('[data-erase]').forEach(b=>b.onclick=e=>{e.stopPropagation();const i=Number(b.dataset.erase);if(confirm('Erase SLOT '+i+'? Its campaign, credits and beastiary are deleted.')){eraseSlot(i);render()}});
    box.querySelector('#slotsClose').onclick=()=>box.remove()};
  render();document.body.append(box)}
function openCodex(){if(document.querySelector('#codex'))return;const box=document.createElement('div');box.id='codex';box.className='overlay';let page=0;
  const render=()=>{const pages=codexVisible(),total=codexPages().length;
    if(!pages.length){box.innerHTML=`<h2>📖 BEASTIARY</h2><p>Nothing catalogued yet.</p><p>Pages unlock the first time you meet each beast or weapon.</p><button id="codexClose">Close</button>`;box.querySelector('#codexClose').onclick=()=>box.remove();return}
    page=Math.min(Math.max(0,page),pages.length-1);const c=pages[page];const img=CODEX_IMG[c.id];const seen=(META.codexSeen&&c.link&&META.codexSeen[c.link])||0;
    box.innerHTML=`<h2>📖 BEASTIARY  ${page+1}/${pages.length}  (catalogued ${pages.length} of ${total})</h2>
      ${img?`<img src="${img}" alt="" style="max-width:220px;max-height:180px;border:1px solid #5a4a7a;background:#021">`:`<div style="font-size:48px">${CODEX_ICON[c.cat]||'•'}</div>`}
      <h3 style="margin:6px 0;color:#eaddff">${c.title||''}</h3>
      <p style="color:#a89ad0;font-style:italic;margin:0">${c.subtitle||''}${c.link&&c.link.indexOf('enemy:')===0?' · '+seen+' terminated':''}</p>
      <p style="max-width:420px;margin:10px auto;color:#d8e8ff">${c.body||''}</p>
      <div style="display:flex;gap:10px;justify-content:center"><button id="cxPrev">◄</button><button id="codexClose">Close</button><button id="cxNext">►</button></div>`;
    box.querySelector('#codexClose').onclick=()=>box.remove();
    box.querySelector('#cxPrev').onclick=()=>{page=(page+pages.length-1)%pages.length;render()};
    box.querySelector('#cxNext').onclick=()=>{page=(page+1)%pages.length;render()}};
  render();document.body.append(box)}
// Title-screen DOM chrome (slots + beastiary + meta) — mirrors HiveWar buttons without canvas hit-tests.
function ensureTitleChrome(){
  // Headless harness stubs DOM — only mount chrome in a real browser.
  if(typeof HTMLElement==='undefined')return;
  let bar=document.getElementById&&document.getElementById('titleChrome');
  // Hide while FORGE is open (z-index sits under the panel and steals/blocks clicks).
  const forgeOpen=!!(document.getElementById('forge')&&document.getElementById('forge').classList.contains('open'));
  if((state!=='title'&&state!=='dead')||forgeOpen){
    if(bar){if(typeof bar.remove==='function')bar.remove();else if(bar.parentNode)bar.parentNode.removeChild(bar)}
    return}
  if(!bar){bar=document.createElement('div');if(!bar||typeof bar!=='object')return;bar.id='titleChrome';bar.style.cssText='position:fixed;left:50%;bottom:88px;transform:translateX(-50%);z-index:4;display:flex;gap:8px;flex-wrap:wrap;justify-content:center';
    bar.innerHTML=`<button id="btnSlots" style="padding:10px 14px;background:#16383a;color:#dff;border:1px solid #5cf;border-radius:8px;cursor:pointer;font-weight:700">💾 SAVE SLOTS</button>
      <button id="btnCodex" style="padding:10px 14px;background:#261638;color:#e8d8ff;border:1px solid #c6f;border-radius:8px;cursor:pointer;font-weight:700">📖 BEASTIARY</button>
      <button id="btnMeta" style="padding:10px 14px;background:#16383a;color:#dff;border:1px solid #6fffe2;border-radius:8px;cursor:pointer;font-weight:700">META (M)</button>`;
    try{document.body.append(bar)}catch(_){return}
    const qs=sel=>bar.querySelector?bar.querySelector(sel):null;
    const b1=qs('#btnSlots'),b2=qs('#btnCodex'),b3=qs('#btnMeta');
    if(b1)b1.onclick=e=>{e.stopPropagation();openSlots()};
    if(b2)b2.onclick=e=>{e.stopPropagation();openCodex()};
    if(b3)b3.onclick=e=>{e.stopPropagation();openMeta()}}
  try{const n=codexVisible().length,t=codexPages().length;const bc=bar.querySelector&&bar.querySelector('#btnCodex');if(bc)bc.textContent='📖 BEASTIARY  '+n+' / '+t}catch(_){}}
// Title chrome is refreshed from draw() — no setInterval (keeps Node harness alive forever).
addEventListener('keydown',e=>{if(e.key.toLowerCase()==='m'&&(state==='title'||state==='dead'))openMeta()});
/* 2026-08-05 removed: this was a SECOND handler for the Scatter Shot card. The card already applies
   itself at offerCards() (`WEAPON.shots = min(5, shots+2)`), so this fired on the same click and
   pushed an extra permanent weapon that then fired alongside the real one — part of the
   "weapons are stacking, I still see my 1st gun" report. The card upgrades the current weapon. */

// ============================================================
// ⬡ HiVE SWARM FORGE — tabbed editor (mirror HiVE WAR patterns)
// ============================================================
window.__forgeMediaReady=(async function FORGE(){
try{
const owner=/^(localhost|127\.0\.0\.1|\[::1\]|)$/.test(location.hostname)||location.protocol==='file:'||location.protocol==='capacitor:'||location.search.includes('forge');
if(!owner||typeof document==='undefined'||!document.body)return;
const MEDIA_DB='hive_swarm_forge_media_v1', MEDIA_STORE='media';
let mediaQueue=Promise.resolve();
function queueMedia(task){const next=mediaQueue.then(task,task);mediaQueue=next.catch(()=>{});return next}
function mediaDB(){return new Promise((resolve,reject)=>{const q=indexedDB.open(MEDIA_DB,1);q.onupgradeneeded=()=>q.result.createObjectStore(MEDIA_STORE,{keyPath:'id'});q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)})}
async function mediaAll(){const db=await mediaDB();return new Promise((resolve,reject)=>{const q=db.transaction(MEDIA_STORE).objectStore(MEDIA_STORE).getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)})}
async function mediaPut(record){const db=await mediaDB();return new Promise((resolve,reject)=>{const q=db.transaction(MEDIA_STORE,'readwrite').objectStore(MEDIA_STORE).put(record);q.onsuccess=()=>resolve();q.onerror=()=>reject(q.error)})}
async function mediaDel(id){const db=await mediaDB();return new Promise((resolve,reject)=>{const q=db.transaction(MEDIA_STORE,'readwrite').objectStore(MEDIA_STORE).delete(id);q.onsuccess=()=>resolve();q.onerror=()=>reject(q.error)})}
async function dataBlob(data){return (await fetch(data)).blob()}
async function blobData(blob){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.readAsDataURL(blob)})}
async function hydrateMedia(){
  try{const rows=await mediaAll();
    for(const row of rows){const data=await blobData(row.blob);
      if(row.id.startsWith('sprite:'))SPRITE_OVR[row.key]=data;
      else if(row.id.startsWith('codex:'))CODEX_IMG[row.key]=data}}
  catch(_){}}
await hydrateMedia();
function saveSpriteMedia(key){const data=SPRITE_OVR[key];return queueMedia(async()=>data?mediaPut({id:'sprite:'+key,key,blob:await dataBlob(data),frames:1,fps:8}):mediaDel('sprite:'+key))}
function saveCodexMedia(id){const data=CODEX_IMG[id];return queueMedia(async()=>data?mediaPut({id:'codex:'+id,key:id,blob:await dataBlob(data)}):mediaDel('codex:'+id))}

const btn=document.createElement('button');btn.id='forgeBtn';btn.textContent='⚒';btn.title='HiVE SWARM Forge (F2)';document.body.appendChild(btn);
const win=document.createElement('section');win.id='forge';
win.innerHTML=`<div id="forgeHead"><b>⬡ HiVE SWARM FORGE</b><small>MiSTRFiNGA INTERNAL // v${GAME_VERSION}</small><span class="x">✕</span></div><div id="forgeTabs"></div><div id="forgeBody"></div>`;
document.body.appendChild(win);
const body=win.querySelector('#forgeBody'), tabsEl=win.querySelector('#forgeTabs');
function openForge(){win.classList.add('open');renderTab()}
function closeForge(){win.classList.remove('open')}
function toggleForge(){win.classList.contains('open')?closeForge():openForge()}
win.querySelector('.x').onclick=closeForge;btn.onclick=toggleForge;
addEventListener('keydown',e=>{if(e.key==='F2'){e.preventDefault();toggleForge()}});
if(/[?&]forge=1/.test(location.search))setTimeout(()=>{const m=location.search.match(/[?&]ftab=(\d+)/);if(m)tab=Math.min(TABS.length-1,+m[1]);openForge()},300);
// drag by header
(function(){const head=win.querySelector('#forgeHead');let sx,sy,ox,oy,drag=false;
  head.addEventListener('pointerdown',e=>{if(e.target.classList.contains('x'))return;drag=true;sx=e.clientX;sy=e.clientY;const r=win.getBoundingClientRect();ox=r.left;oy=r.top;head.setPointerCapture(e.pointerId)});
  head.addEventListener('pointermove',e=>{if(!drag)return;win.style.left=Math.max(0,ox+e.clientX-sx)+'px';win.style.top=Math.max(0,oy+e.clientY-sy)+'px';win.style.right='auto'});
  head.addEventListener('pointerup',()=>drag=false)})();

const TABS=['ENTITIES','PLAYER','WEAPONS','WAVES','WORLD','SPRITES','AUDIO','DATA','BEASTIARY'];
let tab=0, spriteSel=-1, work=null, brush={col:'#ff00ff',size:4,erase:false}, codexSel=0;
TABS.forEach((t,i)=>{const d=document.createElement('button');d.type='button';d.textContent=t;d.id='forgeTab'+i;d.onclick=()=>{tab=i;spriteSel=-1;renderTab()};tabsEl.appendChild(d)});
function getP(p){return p.split('.').reduce((o,k)=>o[k],EDIT)}
function setP(p,v){const ks=p.split('.'),last=ks.pop();ks.reduce((o,k)=>o[k],EDIT)[last]=v}
function fields(obj,path){return Object.entries(obj).filter(([,v])=>typeof v==='number'||typeof v==='string').map(([k,v])=>`<label>${k}<input data-p="${path}.${k}" value="${v}" ${typeof v==='number'?'type="number" step="any"':''}></label>`).join('')}
function bindInputs(){body.querySelectorAll('input[data-p]').forEach(input=>{input.oninput=()=>{const p=input.dataset.p;const old=getP(p);let value=typeof old==='number'?Number(input.value):input.value;if(typeof old==='number'&&!Number.isFinite(value))return;setP(p,value);applyForge();persistForge()}})}
function esc(v){return String(v==null?'':v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;')}

function renderTab(){
  tabsEl.querySelectorAll('button').forEach((d,i)=>d.classList.toggle('on',i===tab));
  if(tab===0){// ENTITIES
    body.innerHTML=`<div class="hint">Enemy roster. Numbers, names, colours and sprite paths apply live. Behaviours stay in code.</div>
      <table><tr><th></th><th>ID</th><th>NAME</th><th>HP</th><th>SPD</th><th>DMG</th><th>W</th><th>WAVE</th><th></th></tr>
      ${EDIT.entities.map((e,i)=>`<tr>
        <td><img class="kthumb" src="${esc(spriteSrcForEntity(e)||e.sprite||'')}" onerror="this.style.opacity=.2"></td>
        <td><input data-p="entities.${i}.id" value="${esc(e.id)}" style="width:110px"></td>
        <td><input data-p="entities.${i}.name" value="${esc(e.name)}" style="width:100px"></td>
        <td><input type="number" data-p="entities.${i}.hp" value="${e.hp}" style="width:56px"></td>
        <td><input type="number" data-p="entities.${i}.speed" value="${e.speed}" style="width:56px"></td>
        <td><input type="number" data-p="entities.${i}.damage" value="${e.damage}" style="width:56px"></td>
        <td><input type="number" data-p="entities.${i}.weight" value="${e.weight}" style="width:48px"></td>
        <td><input type="number" data-p="entities.${i}.unlockWave" value="${e.unlockWave||1}" style="width:48px"></td>
        <td><button data-del="${i}" class="warn">✕</button></td></tr>`).join('')}</table>
      <div class="row"><button id="addEnemy">+ ADD ENEMY</button></div>`;
    bindInputs();
    body.querySelectorAll('[data-del]').forEach(b=>b.onclick=()=>{if(EDIT.entities.length>1){EDIT.entities.splice(+b.dataset.del,1);applyForge();persistForge();renderTab()}});
    body.querySelector('#addEnemy').onclick=()=>{const n=EDIT.entities.length+1;EDIT.entities.push({id:'enemy.custom'+n,name:'Custom '+n,r:12,hp:30,speed:70,damage:8,color:'#c7d4d3',weight:1,dropXp:1,unlockWave:1,sprite:''});applyForge();persistForge();renderTab()};
  }
  else if(tab===1){// PLAYER
    body.innerHTML=`<div class="hint">Player combat knobs. Apply to the next deploy (or immediately if mid-run via applyForge).</div>
      <div class="row">${fields(EDIT.player,'player')}</div>
      <div class="row">${fields(EDIT.drops,'drops')}</div>`;
    bindInputs();
  }
  else if(tab===2){// WEAPONS
    body.innerHTML=`<div class="hint">Per-weapon tuning. Weapons fire automatically at the nearest hostile.</div>
      ${EDIT.weapons.map((w,i)=>`<article style="background:#13262a;padding:10px;border-radius:7px;margin:8px 0"><h3 style="margin:0 0 6px;color:#78efdb">${esc(w.name||w.id)}</h3>${fields(w,'weapons.'+i)}</article>`).join('')}
      <div class="row"><button id="addWep">+ ADD WEAPON</button></div>`;
    bindInputs();
    body.querySelector('#addWep').onclick=()=>{EDIT.weapons.push({id:'weapon.custom'+(EDIT.weapons.length+1),name:'Custom',damage:12,rate:.2,speed:700,shots:1,pierce:1,color:'#b7fff5',range:700});persistForge();renderTab()};
  }
  else if(tab===3){// WAVES
    body.innerHTML=`<div class="hint">Wave budget drives spawn density. seconds = wave length for the WAVE counter.</div>
      <div class="row">${fields(EDIT.waves,'waves')}</div>`;
    bindInputs();
  }
  else if(tab===4){// WORLD
    body.innerHTML=`<div class="hint">Arena bounds and camera dead-zone. halfW/halfH are world half-extents in px.</div>
      <div class="row">${fields(EDIT.world,'world')}</div>`;
    bindInputs();
  }
  else if(tab===5){// SPRITES
    renderSprites();
  }
  else if(tab===6){// AUDIO
    body.innerHTML=`<div class="hint">Global SFX toggle. Per-entity samples stay code-side in this greybox.</div>
      <div class="row"><button id="audSfx">${audioOn?'SFX ON':'SFX OFF'}</button>
      <span class="hint">Samples: ${Object.keys(SFX).join(', ')}</span></div>`;
    body.querySelector('#audSfx').onclick=()=>{audioOn=!audioOn;renderTab()};
  }
  else if(tab===7){// DATA
    body.innerHTML=`<div class="hint">Export / import a self-contained pack (values + optional media keys). Reset restores shipped numbers.</div>
      <div class="row"><button id="pkSave">⬇ EXPORT JSON</button>
        <label style="display:inline;grid-template-columns:none">⬆ IMPORT <input type="file" id="pkLoad" accept="application/json,.json" style="width:auto"></label>
        <button id="forgeReset" class="warn">RESET SHIPPED VALUES</button></div>`;
    body.querySelector('#pkSave').onclick=()=>{const pack={version:GAME_VERSION,values:EDIT,sprites:SPRITE_OVR,codexImages:CODEX_IMG};
      const blob=new Blob([JSON.stringify(pack,null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='hiveswarm-forge-pack.json';a.click()};
    body.querySelector('#pkLoad').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{const pack=JSON.parse(await f.text());
      if(pack.values){EDIT=forgeMerge(FORGE_BASE,pack.values);if(Array.isArray(pack.values.codexPages))EDIT.codexPages=pack.values.codexPages;persistForge();applyForge()}
      if(pack.sprites){Object.assign(SPRITE_OVR,pack.sprites);for(const [k,d] of Object.entries(pack.sprites))await saveSpriteMedia(k)}
      if(pack.codexImages){Object.assign(CODEX_IMG,pack.codexImages);for(const [k,d] of Object.entries(pack.codexImages))await saveCodexMedia(k)}
      renderTab()}catch(err){alert('Bad pack: '+err.message)}};
    body.querySelector('#forgeReset').onclick=()=>{if(confirm('Restore shipped Forge values?')){EDIT=copy(FORGE_BASE);EDIT.codexPages=codexDefaults();applyForge();persistForge();renderTab()}};
  }
  else{// BEASTIARY tab
    renderCodex();
  }
}

function renderCodex(){
  const pages=codexPages();
  if(codexSel>=pages.length)codexSel=Math.max(0,pages.length-1);
  const pg=pages[codexSel];
  const list=pages.map((p,i)=>`<button type="button" data-pick="${i}" class="${i===codexSel?'on':''}" style="display:block;width:100%;text-align:left;margin:2px 0">${CODEX_ICON[p.cat]||'•'} ${esc(p.title)||'(untitled)'}</button>`).join('');
  const img=pg?CODEX_IMG[pg.id]:null;
  body.innerHTML=`<div class="hint">Field guide. Pages unlock in-game on first sighting (spawn). Progress is per save slot. Word is <b>BEASTIARY</b>.</div>
    <div style="display:flex;gap:12px;align-items:flex-start">
      <div style="flex:0 0 200px;max-height:60vh;overflow:auto">${list||'<div class="hint">No pages.</div>'}
        <button id="cxAdd" style="width:100%;margin-top:8px">+ ADD PAGE</button>
        <button id="cxReset" class="warn" style="width:100%;margin-top:4px">RESET DEFAULT PAGES</button>
        <button id="cxRelock" class="warn" style="width:100%;margin-top:4px">RE-LOCK ALL (this slot)</button></div>
      <div style="flex:1">${pg?`
        <div class="row">CATEGORY <select id="cxCat">${CODEX_CATS.map(c=>`<option value="${c}" ${c===pg.cat?'selected':''}>${c}</option>`).join('')}</select></div>
        <div class="row">TITLE <input type="text" id="cxTitle" value="${esc(pg.title)}" style="width:220px"></div>
        <div class="row">SUBTITLE <input type="text" id="cxSub" value="${esc(pg.subtitle)}" style="width:220px"></div>
        <div class="row">UNLOCK KEY <input type="text" id="cxLink" value="${esc(pg.link)}" placeholder="enemy:enemy.shambler" style="width:200px">
          <span class="hint">${pg.link?(META.codexSeen&&META.codexSeen[pg.link]!==undefined?'<b style="color:#6f6">UNLOCKED</b>':'<b style="color:#f84">LOCKED</b>')+' slot '+currentSlot():'<b style="color:#6f6">ALWAYS VISIBLE</b>'}</span></div>
        <div class="row">BODY <textarea id="cxBody">${esc(pg.body)}</textarea></div>
        <div class="row"><button id="cxPick">🖼 UPLOAD IMAGE</button>
          <button id="cxClr" class="warn" ${img?'':'disabled'}>REMOVE IMAGE</button>
          <input type="file" id="cxFile" accept="image/*" style="display:none"></div>
        <div class="row">${img?`<img src="${img}" alt="" style="max-width:220px;max-height:160px;border:1px solid #245">`:'<span class="hint">No image yet.</span>'}</div>
        <div class="row"><button id="cxDel" class="warn">DELETE PAGE</button></div>`:'<div class="hint">Add a page.</div>'}</div></div>`;
  body.querySelectorAll('[data-pick]').forEach(b=>b.onclick=()=>{codexSel=+b.dataset.pick;renderCodex()});
  body.querySelector('#cxAdd').onclick=()=>{codexPages().push({id:codexNewId(),cat:'enemy',title:'New Entry',subtitle:'',body:'',link:''});codexSel=codexPages().length-1;persistForge();renderCodex()};
  body.querySelector('#cxRelock').onclick=()=>{if(!confirm('Re-lock every beastiary page in save slot '+currentSlot()+'?'))return;META.codexSeen={};saveMeta();renderCodex()};
  body.querySelector('#cxReset').onclick=()=>{if(!confirm('Replace ALL beastiary pages with shipped defaults?'))return;EDIT.codexPages=codexDefaults();codexSel=0;persistForge();renderCodex()};
  if(!pg)return;
  const bind=(sel,key)=>{const el=body.querySelector(sel);if(!el)return;el.oninput=()=>{pg[key]=el.value;persistForge()}};
  bind('#cxTitle','title');bind('#cxSub','subtitle');bind('#cxBody','body');bind('#cxLink','link');
  body.querySelector('#cxCat').onchange=e=>{pg.cat=e.target.value;persistForge();renderCodex()};
  body.querySelector('#cxPick').onclick=()=>body.querySelector('#cxFile').click();
  body.querySelector('#cxFile').onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();rd.onload=()=>{CODEX_IMG[pg.id]=rd.result;saveCodexMedia(pg.id).then(()=>renderCodex()).catch(()=>alert('Could not store image in IndexedDB.'))};rd.readAsDataURL(f)};
  body.querySelector('#cxClr').onclick=()=>{delete CODEX_IMG[pg.id];saveCodexMedia(pg.id).then(()=>renderCodex())};
  body.querySelector('#cxDel').onclick=()=>{if(!confirm('Delete "'+(pg.title||'untitled')+'"?'))return;delete CODEX_IMG[pg.id];saveCodexMedia(pg.id).catch(()=>{});codexPages().splice(codexSel,1);codexSel=Math.max(0,codexSel-1);persistForge();renderCodex()};
}

function renderSprites(){
  const list=EDIT.entities.map((e,i)=>({key:entitySpriteKey(e),name:e.name||e.id,path:e.sprite||'',idx:i}));
  if(spriteSel<0){
    body.innerHTML=`<div class="hint">Paint or import a PNG per enemy. Overrides live in IndexedDB (<code>sprite:</code> prefix) and apply immediately in-game.</div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px">
      ${list.map((r,i)=>`<button data-sp="${i}" style="padding:8px;background:#13262a;border:1px solid #426862;border-radius:6px;cursor:pointer;color:#dff">
        <img class="kthumb" src="${esc(SPRITE_OVR[r.key]||r.path)}" onerror="this.style.opacity=.25" style="display:block;margin:0 auto 6px"><b>${esc(r.name)}</b></button>`).join('')}
      </div>`;
    body.querySelectorAll('[data-sp]').forEach(b=>b.onclick=()=>{spriteSel=+b.dataset.sp;renderSprites()});
    return;
  }
  const r=list[spriteSel]; if(!r){spriteSel=-1;renderSprites();return}
  const src=SPRITE_OVR[r.key]||r.path||'';
  body.innerHTML=`<div class="row"><button id="spBack">← BACK</button><b style="color:#6fffe2">${esc(r.name)}</b><span class="hint">${esc(r.key)}</span></div>
    <div class="row"><canvas id="forgePaint" width="128" height="128"></canvas>
      <div><div class="row">COLOR <input type="color" id="spCol" value="${brush.col}"> SIZE <input type="number" id="spSize" value="${brush.size}" min="1" max="32" style="width:48px">
        <button id="spErase">${brush.erase?'ERASE ON':'ERASE'}</button></div>
        <div class="row"><button id="spSave">💾 SAVE</button><button id="spImp">⇧ IMPORT PNG</button>
          <button id="spRev" class="warn">REVERT</button><input type="file" id="spFile" accept="image/*" style="display:none"></div>
        <div class="hint">Paint then SAVE. REVERT clears the IndexedDB override and restores the shipped path.</div></div></div>`;
  const cv=body.querySelector('#forgePaint'), cx=cv.getContext('2d');
  work=document.createElement('canvas');work.width=128;work.height=128;const wg=work.getContext('2d');
  function loadInto(){wg.clearRect(0,0,128,128);if(!src){drawPaint();return}const im=new Image();im.crossOrigin='anonymous';im.onload=()=>{wg.drawImage(im,0,0,128,128);drawPaint()};im.onerror=()=>drawPaint();im.src=src}
  function drawPaint(){cx.clearRect(0,0,128,128);cx.drawImage(work,0,0)}
  loadInto();
  let painting=false;
  function paintAt(ev){const rect=cv.getBoundingClientRect(),x=Math.floor((ev.clientX-rect.left)/rect.width*128),y=Math.floor((ev.clientY-rect.top)/rect.height*128);
    wg.fillStyle=brush.erase?'rgba(0,0,0,0)':brush.col;if(brush.erase){wg.clearRect(x-brush.size/2,y-brush.size/2,brush.size,brush.size)}
    else{wg.fillRect(x-brush.size/2,y-brush.size/2,brush.size,brush.size)}drawPaint()}
  cv.onpointerdown=e=>{painting=true;cv.setPointerCapture(e.pointerId);paintAt(e)};
  cv.onpointermove=e=>{if(painting)paintAt(e)};
  cv.onpointerup=()=>{painting=false};
  body.querySelector('#spCol').oninput=e=>{brush.col=e.target.value;brush.erase=false};
  body.querySelector('#spSize').oninput=e=>{brush.size=Math.max(1,Math.min(32,+e.target.value||4))};
  body.querySelector('#spErase').onclick=()=>{brush.erase=!brush.erase;renderSprites()};
  body.querySelector('#spBack').onclick=()=>{spriteSel=-1;renderSprites()};
  body.querySelector('#spSave').onclick=()=>{const data=work.toDataURL('image/png');SPRITE_OVR[r.key]=data;delete SPRITES[data];
    // also map path for quick lookups
    if(r.path)SPRITE_OVR['path:'+r.path]=data;
    saveSpriteMedia(r.key).then(()=>{if(r.path)return saveSpriteMedia('path:'+r.path)}).then(()=>alert('Sprite saved.')).catch(()=>alert('IndexedDB save failed.'))};
  body.querySelector('#spRev').onclick=()=>{delete SPRITE_OVR[r.key];if(r.path)delete SPRITE_OVR['path:'+r.path];
    saveSpriteMedia(r.key).then(()=>r.path?saveSpriteMedia('path:'+r.path):null).then(()=>{spriteSel=-1;renderSprites()})};
  body.querySelector('#spImp').onclick=()=>body.querySelector('#spFile').click();
  body.querySelector('#spFile').onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();rd.onload=()=>{const im=new Image();im.onload=()=>{wg.clearRect(0,0,128,128);wg.drawImage(im,0,0,128,128);drawPaint()};im.src=rd.result};rd.readAsDataURL(f)};
}

window.__hiveSwarmForge=()=>copy(EDIT);
}catch(err){console.error('FORGE init failed',err)}
})();
