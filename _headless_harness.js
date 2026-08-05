// Headless harness for HiVE SWARM S.3+ product (top-down greybox).
// G.5 — does NOT assume the quarantined corridor host's startRun / G / levelStart API.
// Uses: reset(), update(dt), draw(), window.__hiveSwarmDebug().
'use strict';
const fs = require('fs');

function makeCtx() {
  const grad = { addColorStop() {} };
  return new Proxy({
    canvas: { width: 540, height: 960 },
    createLinearGradient: (...a) => { if (a.some(v => !Number.isFinite(v))) throw new Error('createLinearGradient non-finite: ' + a); return grad; },
    createRadialGradient: (...a) => { if (a.some(v => !Number.isFinite(v))) throw new Error('createRadialGradient non-finite: ' + a); return grad; },
    createPattern: () => ({}),
    getImageData: () => ({ data: [] }),
    measureText: () => ({ width: 10 }),
    setLineDash() {}, save() {}, restore() {}, beginPath() {}, closePath() {},
    moveTo() {}, lineTo() {}, quadraticCurveTo() {}, bezierCurveTo() {}, arc() {},
    ellipse() {}, rect() {}, fill() {}, stroke() {}, clip() {}, fillRect() {},
    strokeRect() {}, clearRect() {}, fillText() {}, strokeText() {}, translate() {},
    scale() {}, rotate() {}, drawImage() {}, transform() {}, setTransform() {},
    resetTransform() {}, arcTo() {}, roundRect() {},
  }, { get(t, p) { return p in t ? t[p] : (typeof p === 'string' ? () => {} : undefined); },
       set(t, p, v) { t[p] = v; return true; } });
}
function makeCanvas() {
  return {
    width: 540, height: 960, style: {},
    getContext: () => makeCtx(),
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 540, height: 960 }),
    addEventListener() {}, setPointerCapture() {},
  };
}
const store = {};
global.localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = String(v); },
  removeItem: k => { delete store[k]; },
};
// IndexedDB stub — FORGE media path when present (ported from G.1 / HiVE WAR).
(function stubIndexedDB() {
  const dbs = new Map();
  function reqResult(value, err) {
    const r = { result: value, error: err || null, onsuccess: null, onerror: null, onupgradeneeded: null };
    queueMicrotask(() => {
      if (err) { if (r.onerror) r.onerror({ target: r }); }
      else if (r.onsuccess) r.onsuccess({ target: r });
    });
    return r;
  }
  function storeAPI(bucket) {
    return {
      put(val, key) { if (key !== undefined) bucket.set(key, val); else if (val && val.id != null) bucket.set(val.id, val); else bucket.set(String(bucket.size), val); return reqResult(key); },
      get(key) { return reqResult(bucket.has(key) ? bucket.get(key) : undefined); },
      delete(key) { bucket.delete(key); return reqResult(undefined); },
      clear() { bucket.clear(); return reqResult(undefined); },
      getAll() { return reqResult([...bucket.values()]); },
      openCursor() {
        const entries = [...bucket.entries()];
        let i = 0;
        const cursorReq = { result: null, onsuccess: null, onerror: null };
        const step = () => {
          if (i >= entries.length) { cursorReq.result = null; if (cursorReq.onsuccess) cursorReq.onsuccess({ target: cursorReq }); return; }
          const [k, v] = entries[i++];
          cursorReq.result = { key: k, value: v, continue: () => queueMicrotask(step) };
          if (cursorReq.onsuccess) cursorReq.onsuccess({ target: cursorReq });
        };
        queueMicrotask(step);
        return cursorReq;
      },
    };
  }
  global.indexedDB = {
    open(name) {
      if (!dbs.has(name)) dbs.set(name, new Map());
      const bucket = dbs.get(name);
      const r = { result: null, error: null, onsuccess: null, onerror: null, onupgradeneeded: null };
      queueMicrotask(() => {
        const db = {
          objectStoreNames: { contains: () => true },
          createObjectStore: () => storeAPI(bucket),
          transaction: () => ({ objectStore: () => storeAPI(bucket), oncomplete: null, onerror: null }),
          close() {},
        };
        r.result = db;
        if (r.onupgradeneeded) r.onupgradeneeded({ target: r });
        if (r.onsuccess) r.onsuccess({ target: r });
      });
      return r;
    },
    deleteDatabase(name) { dbs.delete(name); return reqResult(undefined); },
  };
  global.IDBKeyRange = { bound: () => ({}), only: () => ({}) };
})();
global.performance = { now: () => Date.now() };
global.requestAnimationFrame = () => 0;   // we drive the loop manually
global.cancelAnimationFrame = () => {};
class Img { constructor() { this.ok = false; setTimeout(() => { this.onload && this.onload(); }, 0); }
  set src(v) { this._src = v; } get src() { return this._src; } }
global.Image = Img;
global.AudioContext = function () {
  return {
    createGain: () => ({ connect() {}, gain: { value: 1, setValueAtTime() {} } }),
    createOscillator: () => ({ connect() {}, start() {}, stop() {}, frequency: { setValueAtTime() {}, value: 0 } }),
    createBuffer: () => ({ getChannelData: () => new Float32Array(1) }),
    createBufferSource: () => ({ connect() {}, start() {}, buffer: null }),
    destination: {}, currentTime: 0, sampleRate: 44100, resume() {}, state: 'running',
  };
};
global.webkitAudioContext = global.AudioContext;
const listeners = {};
function makeEl(tag) {
  if (tag === 'canvas') return makeCanvas();
  const kids = [];
  const byIdLocal = new Map();
  const el = {
    tagName: String(tag || 'div').toUpperCase(),
    style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false },
    children: kids, childNodes: kids,
    appendChild(c) { kids.push(c); if (c && c.id) byIdLocal.set(c.id, c); return c; },
    append(...nodes) { for (const c of nodes) el.appendChild(c); },
    removeChild(c) { const i = kids.indexOf(c); if (i >= 0) kids.splice(i, 1); return c; },
    insertBefore(c) { kids.push(c); return c; },
    setAttribute(k, v) { if (k === 'id') { el.id = v; byIdLocal.set(v, el); } },
    getAttribute: () => null, removeAttribute() {},
    addEventListener() {}, removeEventListener() {},
    querySelector(sel) {
      if (!sel) return null;
      if (sel.startsWith('#')) {
        const id = sel.slice(1);
        if (byIdLocal.has(id)) return byIdLocal.get(id);
        const child = makeEl('div'); child.id = id; byIdLocal.set(id, child); kids.push(child); return child;
      }
      if (sel.startsWith('.')) {
        const child = makeEl('div'); child.className = sel.slice(1); kids.push(child); return child;
      }
      return makeEl('div');
    },
    querySelectorAll: () => [],
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 100, height: 40 }),
    focus() {}, blur() {}, click() {},
    innerHTML: '', textContent: '', value: '', type: '', id: '', className: '',
    hidden: false,
  };
  return el;
}
const gameCanvas = makeCanvas();
gameCanvas.id = 'game';
const elCache = new Map([['game', gameCanvas], ['hint', makeEl('div')]]);
function byId(id) {
  if (!elCache.has(id)) elCache.set(id, makeEl('div'));
  return elCache.get(id);
}
const body = makeEl('body');
const doc = {
  getElementById: byId,
  createElement: tag => makeEl(tag),
  createTextNode: t => ({ textContent: t }),
  querySelector: sel => {
    if (!sel) return null;
    if (sel === '#game' || sel === 'canvas' || sel === 'canvas#game') return gameCanvas;
    if (sel.startsWith('#')) return byId(sel.slice(1));
    return makeEl('div');
  },
  querySelectorAll: () => [],
  addEventListener(t, f) { (listeners[t] = listeners[t] || []).push(f); },
  body,
  documentElement: { style: {} },
  head: makeEl('head'),
};
global.document = doc;
// Forge owner gate treats localhost as owner
global.location = {
  search: '',
  protocol: 'http:',
  hostname: 'localhost',
  href: 'http://localhost:8795/',
};
global.window = global;
global.addEventListener = (t, f) => doc.addEventListener(t, f);
global.PSDK = null;
global.devicePixelRatio = 1;
global.innerWidth = 540;
global.innerHeight = 960;
global.alert = () => {};
global.confirm = () => true;

// Load extracted product script (regen_extract.py → _game_extract.js from index.html)
let code = fs.readFileSync(__dirname + '/_game_extract.js', 'utf8');
// Expose S.3 product API only — never corridor startRun / G / levelStart
code += `
;globalThis.__H = {
  reset: typeof reset === 'function' ? reset : null,
  update: typeof update === 'function' ? update : null,
  draw: typeof draw === 'function' ? draw : null,
  debug: typeof globalThis.__hiveSwarmDebug === 'function' ? globalThis.__hiveSwarmDebug : null,
  forge: typeof globalThis.__hiveSwarmForge === 'function' ? globalThis.__hiveSwarmForge : null,
};
`;
try {
  (0, eval)(code);
} catch (e) {
  console.error('LOAD ERROR:', e && e.stack ? e.stack : e);
  process.exit(1);
}

const H = globalThis.__H;
if (!H.reset || !H.update || !H.draw) {
  console.error('API ERROR: product must export reset/update/draw (S.3 greybox). Got:', {
    reset: !!H.reset, update: !!H.update, draw: !!H.draw, debug: !!H.debug,
  });
  process.exit(1);
}
if (typeof H.reset !== 'function') {
  console.error('API ERROR: reset is not a function');
  process.exit(1);
}

// Title → play via the real deploy entry (Enter / reset), not corridor startRun
H.reset();
const d0 = H.debug ? H.debug() : null;
if (!d0 || d0.state !== 'play') {
  console.error('START ERROR: expected state=play after reset(), got', d0);
  process.exit(1);
}
console.log('started. state=', d0.state, 'wave=', d0.wave, 'enemies=', d0.enemies);

// G6: simulate a competent kite (circle-strafe), not a suicide walk into the facing cone.
// Press W always; alternate A/D every ~1.5s. Also dismiss level-up cards if the DOM offers them.
function fireKey(type, key) {
  const list = listeners[type] || [];
  for (const f of list) {
    try { f({ key, keyCode: 0, preventDefault() {} }); } catch (_) {}
  }
}
fireKey('keydown', 'w');
let strafe = 'd';
fireKey('keydown', strafe);

let step = 0;
let lastWave = d0.wave;
let maxEnemies = d0.enemies;
let minHp = 999;
try {
  // ~90 s of sim at 0.1s steps — balance gate: competent kite must still be alive at end
  for (step = 0; step < 900; step++) {
    if (step > 0 && step % 15 === 0) {
      fireKey('keyup', strafe);
      strafe = strafe === 'd' ? 'a' : 'd';
      fireKey('keydown', strafe);
    }
    // Auto-pick first level-up card if the product opened the chooser (DOM box #cards)
    try {
      const box = document.querySelector && document.querySelector('#cards');
      if (box && box.querySelector) {
        const btn = box.querySelector('[data-card]');
        if (btn && typeof btn.onclick === 'function') btn.onclick();
        else if (btn && btn.click) btn.click();
      }
    } catch (_) {}
    H.update(0.1);
    H.draw();
    const d = H.debug ? H.debug() : {};
    const hp = (d.player && d.player.hp != null) ? d.player.hp : (d.hp != null ? d.hp : null);
    if (hp != null && hp < minHp) minHp = hp;
    if (d.enemies > maxEnemies) maxEnemies = d.enemies;
    if (d.wave !== lastWave) {
      console.log(`--> wave ${d.wave} at step ${step} (t=${(step * 0.1).toFixed(0)}s) enemies=${d.enemies} hp=${hp}`);
      lastWave = d.wave;
    }
    if (d.state === 'dead') {
      console.log('reached dead at step', step, 'score', d.score, 'survived', d.elapsed, 'minHp', minHp);
      break;
    }
  }
  const fin = H.debug ? H.debug() : {};
  console.log(
    'SIM ENDED clean. state', fin.state,
    'wave', fin.wave,
    'enemies', fin.enemies,
    'maxEnemies', maxEnemies,
    'score', fin.score,
    'steps', step,
    'minHp', minHp,
    'survived', fin.elapsed != null ? fin.elapsed : (step * 0.1)
  );
  if (!H.debug) {
    console.error('WARN: __hiveSwarmDebug missing — coverage incomplete');
    process.exit(2);
  }
} catch (e) {
  const d = H.debug ? H.debug() : {};
  console.error(`\n*** THREW at step ${step} (t=${(step * 0.1).toFixed(1)}s) state=${d.state} wave=${d.wave} ***`);
  console.error(e && e.stack ? e.stack : e);
  process.exit(1);
}
