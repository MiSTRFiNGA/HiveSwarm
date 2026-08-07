// One-off verification for the STAGE system (2026-08-06). Not part of the shipped harness —
// reuses its stub environment inline, drives update() with large dt to fast-forward through
// Stage 1's 60s budget, auto-picks the stagebreak card via #stagebreak (mirrors how
// _headless_harness.js auto-picks #cards), and asserts stage advances 0 -> 1 -> 2.
'use strict';
const fs = require('fs');
function makeCtx() {
  const grad = { addColorStop() {} };
  return new Proxy({
    canvas: { width: 540, height: 960 },
    createLinearGradient: () => grad, createRadialGradient: () => grad, createPattern: () => ({}),
    getImageData: () => ({ data: [] }), measureText: () => ({ width: 10 }),
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
  return { width: 540, height: 960, style: {}, getContext: () => makeCtx(),
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 540, height: 960 }),
    addEventListener() {}, setPointerCapture() {} };
}
const store = {};
global.localStorage = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
(function stubIndexedDB() {
  const dbs = new Map();
  function reqResult(value, err) { const r = { result: value, error: err || null, onsuccess: null, onerror: null, onupgradeneeded: null }; queueMicrotask(() => { if (err) { if (r.onerror) r.onerror({ target: r }); } else if (r.onsuccess) r.onsuccess({ target: r }); }); return r; }
  function storeAPI(bucket) { return { put(val, key) { if (key !== undefined) bucket.set(key, val); else if (val && val.id != null) bucket.set(val.id, val); else bucket.set(String(bucket.size), val); return reqResult(key); }, get(key) { return reqResult(bucket.has(key) ? bucket.get(key) : undefined); }, delete(key) { bucket.delete(key); return reqResult(undefined); }, clear() { bucket.clear(); return reqResult(undefined); }, getAll() { return reqResult([...bucket.values()]); }, openCursor() { const entries = [...bucket.entries()]; let i = 0; const cursorReq = { result: null, onsuccess: null, onerror: null }; const step = () => { if (i >= entries.length) { cursorReq.result = null; if (cursorReq.onsuccess) cursorReq.onsuccess({ target: cursorReq }); return; } const [k, v] = entries[i++]; cursorReq.result = { key: k, value: v, continue: () => queueMicrotask(step) }; if (cursorReq.onsuccess) cursorReq.onsuccess({ target: cursorReq }); }; queueMicrotask(step); return cursorReq; } }; }
  global.indexedDB = { open(name) { if (!dbs.has(name)) dbs.set(name, new Map()); const bucket = dbs.get(name); const r = { result: null, error: null, onsuccess: null, onerror: null, onupgradeneeded: null }; queueMicrotask(() => { const db = { objectStoreNames: { contains: () => true }, createObjectStore: () => storeAPI(bucket), transaction: () => ({ objectStore: () => storeAPI(bucket), oncomplete: null, onerror: null }), close() {} }; r.result = db; if (r.onupgradeneeded) r.onupgradeneeded({ target: r }); if (r.onsuccess) r.onsuccess({ target: r }); }); return r; }, deleteDatabase(name) { dbs.delete(name); return reqResult(undefined); } };
  global.IDBKeyRange = { bound: () => ({}), only: () => ({}) };
})();
global.performance = { now: () => Date.now() };
global.requestAnimationFrame = () => 0; global.cancelAnimationFrame = () => {};
class Img { constructor() { this.ok = false; setTimeout(() => { this.onload && this.onload(); }, 0); } set src(v) { this._src = v; } get src() { return this._src; } }
global.Image = Img;
global.AudioContext = function () { return { createGain: () => ({ connect() {}, gain: { value: 1, setValueAtTime() {} } }), createOscillator: () => ({ connect() {}, start() {}, stop() {}, frequency: { setValueAtTime() {}, value: 0 } }), createBuffer: () => ({ getChannelData: () => new Float32Array(1) }), createBufferSource: () => ({ connect() {}, start() {}, buffer: null }), destination: {}, currentTime: 0, sampleRate: 44100, resume() {}, state: 'running' }; };
global.webkitAudioContext = global.AudioContext;
const listeners = {};
function makeEl(tag) {
  if (tag === 'canvas') return makeCanvas();
  const kids = []; const byIdLocal = new Map();
  const el = { tagName: String(tag || 'div').toUpperCase(), style: {}, dataset: {}, classList: { add() {}, remove() {}, toggle() {}, contains: () => false }, children: kids, childNodes: kids,
    appendChild(c) { kids.push(c); if (c && c.id) byIdLocal.set(c.id, c); return c; },
    append(...nodes) { for (const c of nodes) el.appendChild(c); },
    removeChild(c) { const i = kids.indexOf(c); if (i >= 0) kids.splice(i, 1); return c; },
    insertBefore(c) { kids.push(c); return c; },
    setAttribute(k, v) { if (k === 'id') { el.id = v; byIdLocal.set(v, el); } },
    getAttribute: () => null, removeAttribute() {}, addEventListener() {}, removeEventListener() {},
    querySelector(sel) { if (!sel) return null; if (sel.startsWith('#')) { const id = sel.slice(1); if (byIdLocal.has(id)) return byIdLocal.get(id); const child = makeEl('div'); child.id = id; byIdLocal.set(id, child); kids.push(child); return child; } if (sel.startsWith('.')) { const child = makeEl('div'); child.className = sel.slice(1); kids.push(child); return child; } return makeEl('div'); },
    querySelectorAll(sel) { if (sel === '[data-card]') return kids.filter(k => k.dataset && k.dataset.card !== undefined); return []; },
    getBoundingClientRect: () => ({ left: 0, top: 0, width: 100, height: 40 }), focus() {}, blur() {}, click() {},
    innerHTML: '', textContent: '', value: '', type: '', id: '', className: '', hidden: false };
  return el;
}
const gameCanvas = makeCanvas(); gameCanvas.id = 'game';
const elCache = new Map([['game', gameCanvas], ['hint', makeEl('div')]]);
function byId(id) { if (!elCache.has(id)) elCache.set(id, makeEl('div')); return elCache.get(id); }
const body = makeEl('body');
const doc = { getElementById: byId, createElement: tag => makeEl(tag), createTextNode: t => ({ textContent: t }),
  querySelector: sel => { if (!sel) return null; if (sel === '#game' || sel === 'canvas' || sel === 'canvas#game') return gameCanvas; if (sel.startsWith('#')) return byId(sel.slice(1)); return makeEl('div'); },
  querySelectorAll: () => [], addEventListener(t, f) { (listeners[t] = listeners[t] || []).push(f); }, body, documentElement: { style: {} }, head: makeEl('head') };
global.document = doc;
global.location = { search: '', protocol: 'http:', hostname: 'localhost', href: 'http://localhost:8795/' };
global.window = global; global.addEventListener = (t, f) => doc.addEventListener(t, f);
global.PSDK = null; global.devicePixelRatio = 1; global.innerWidth = 540; global.innerHeight = 960;
global.alert = () => {}; global.confirm = () => true;

let code = fs.readFileSync(__dirname + '/_game_extract.js', 'utf8');
code += `
;globalThis.__H = {
  reset: typeof reset === 'function' ? reset : null,
  update: typeof update === 'function' ? update : null,
  draw: typeof draw === 'function' ? draw : null,
  debug: typeof globalThis.__hiveSwarmDebug === 'function' ? globalThis.__hiveSwarmDebug : null,
};
`;
try { (0, eval)(code); } catch (e) { console.error('LOAD ERROR:', e && e.stack ? e.stack : e); process.exit(1); }
const H = globalThis.__H;
H.reset();
let d = H.debug();
if (d.state !== 'play' || d.stage !== 0) { console.error('START ERROR', d); process.exit(1); }
console.log('start ok. stage', d.stage, d.stageName, 'state', d.state);

// Drive time forward in 0.5s steps (real dt, not artificially teleporting elapsed) until we
// observe stage 0 -> 1 -> 2, auto-clicking the stagebreak card each time it appears (real
// player flow: kill the boss via the sim's own combat, then pick a reward to deploy).
function fireKey(type, key) { const list = listeners[type] || []; for (const f of list) { try { f({ key, keyCode: 0, preventDefault() {} }); } catch (_) {} } }
fireKey('keydown', 'w');
let strafe = 'd'; fireKey('keydown', strafe);

let seenStage1 = false, seenStage2 = false;
for (let step = 0; step < 20000; step++) {
  if (step > 0 && step % 15 === 0) { fireKey('keyup', strafe); strafe = strafe === 'd' ? 'a' : 'd'; fireKey('keydown', strafe); }
  try {
    const box = document.querySelector('#stagebreak');
    if (box && box.querySelectorAll) {
      const btn = box.querySelectorAll('[data-card]')[0];
      if (btn && typeof btn.onclick === 'function') btn.onclick();
    }
  } catch (_) {}
  H.update(0.1);
  d = H.debug();
  if (d.state === 'dead') { console.error('PLAYER DIED at step', step, d); process.exit(1); }
  if (d.stage === 1 && !seenStage1) { seenStage1 = true; console.log('--> reached stage 1 (', d.stageName, ') at t=', (step*0.1).toFixed(1), 's state=', d.state); }
  if (d.stage === 2 && !seenStage2) { seenStage2 = true; console.log('--> reached stage 2 (', d.stageName, ') at t=', (step*0.1).toFixed(1), 's state=', d.state); break; }
}
if (!seenStage1 || !seenStage2) { console.error('FAIL: did not reach stage 1 -> 2. final debug:', d); process.exit(1); }
console.log('PASS: stage system verified. final debug:', d);
