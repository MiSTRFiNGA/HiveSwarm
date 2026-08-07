// Verification for the new FORGE STAGES tab (2026-08-06).
// Two things to prove:
//  1. renderTab() with tab=STAGES produces real inputs bound to EDIT.stages (not the old
//     fields()-skips-arrays gap) — checked by string-inspecting the rendered body.innerHTML.
//  2. An edit persisted to localStorage under FORGE_KEY survives a reload — i.e. forgeMerge()
//     picks up a saved stages[] override on the next load, same path every other tab uses.
// Reuses the stub DOM/canvas/localStorage/indexedDB environment from _headless_harness.js.
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
    querySelectorAll: () => [],
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
global.location = { search: '?forge=1&ftab=5', protocol: 'http:', hostname: 'localhost', href: 'http://localhost:8795/?forge=1&ftab=5' };
global.window = global; global.addEventListener = (t, f) => doc.addEventListener(t, f);
global.PSDK = null; global.devicePixelRatio = 1; global.innerWidth = 540; global.innerHeight = 960;
global.alert = () => {}; global.confirm = () => true;
global.URL = { createObjectURL: () => 'blob:x' };
global.Blob = function (parts, opts) { this.parts = parts; this.type = opts && opts.type; };

// FORGE init is an async IIFE (media/IndexedDB loading) that assigns window.__forgeMediaReady
// to its own promise and sets the __hiveSwarm* hooks only once it resolves — must await it
// before touching forge()/ui(), or the hooks race the eval and read as undefined.
async function loadGame() {
  delete globalThis.__H; delete globalThis.__hiveSwarmForge; delete globalThis.__hiveSwarmForgeUI; delete globalThis.__forgeMediaReady;
  let code = fs.readFileSync(__dirname + '/_game_extract.js', 'utf8');
  code += `
;globalThis.__H = {
  reset: typeof reset === 'function' ? reset : null,
};
`;
  (0, eval)(code);
  if (globalThis.__forgeMediaReady) await globalThis.__forgeMediaReady;
  const H = globalThis.__H;
  H.forge = typeof globalThis.__hiveSwarmForge === 'function' ? globalThis.__hiveSwarmForge : null;
  H.ui = typeof globalThis.__hiveSwarmForgeUI !== 'undefined' ? globalThis.__hiveSwarmForgeUI : null;
  return H;
}

(async () => {
  // ---- Pass 1: fresh load, no saved overrides. Assert STAGES tab renders real stage data. ----
  let H = await loadGame();
  if (!H.forge || !H.ui) { console.error('API ERROR: forge hooks missing'); process.exit(1); }
  const tabs = H.ui.tabs();
  if (tabs[5] !== 'STAGES') { console.error('FAIL: TABS[5] !==STAGES, got', tabs); process.exit(1); }
  H.reset();
  H.ui.setTab(5);
  const html1 = H.ui.html();
  const expectStages = ['Outskirts', 'Sewers', 'Downtown', 'Highway', 'HiVE Core'];
  for (const name of expectStages) {
    if (!html1.includes(name)) { console.error('FAIL: STAGES tab missing', name, '\n', html1.slice(0, 400)); process.exit(1); }
  }
  if (!html1.includes('data-p="stages.0.seconds"') || !html1.includes('data-p="stages.0.enemyCap"') || !html1.includes('data-p="stages.0.bossMul"')) {
    console.error('FAIL: STAGES tab inputs not bound via fields()/data-p to stages.N.*\n', html1.slice(0, 800));
    process.exit(1);
  }
  if (!html1.includes('data-bg="0.0"') || !html1.includes('data-bg="0.1"')) {
    console.error('FAIL: STAGES tab missing bg colour inputs\n', html1.slice(0, 800));
    process.exit(1);
  }
  const before = H.forge();
  if (before.stages[0].seconds !== 60) { console.error('FAIL: unexpected baseline stage 0 seconds', before.stages[0].seconds); process.exit(1); }
  console.log('PASS 1: STAGES tab renders 5 stages with bound seconds/enemyCap/bossMul/bg inputs.');

  // ---- Pass 2: simulate what bindInputs()'s oninput handler does for a stages.N.field edit,
  // then persist via the SAME localStorage key + JSON shape every other tab uses, then reload
  // fresh (new eval) to prove forgeMerge() picks the override back up — i.e. survives reload. ----
  const FORGE_KEY = 'hive_swarm_forge_values_v1';
  const edited = JSON.parse(JSON.stringify(before));
  edited.stages[0].seconds = 999;
  edited.stages[0].name = 'Outskirts EDITED';
  edited.stages[0].bg = ['#111111', '#222222'];
  store[FORGE_KEY] = JSON.stringify(edited);

  H = await loadGame(); // fresh eval == reload; EDIT = forgeMerge(FORGE_BASE, localStorage[...]) runs at load time
  H.reset();
  const after = H.forge();
  if (after.stages[0].seconds !== 999) { console.error('FAIL: stage edit did not survive reload. got', after.stages[0].seconds); process.exit(1); }
  if (after.stages[0].name !== 'Outskirts EDITED') { console.error('FAIL: stage name edit did not survive reload. got', after.stages[0].name); process.exit(1); }
  if (!after.stages[0].bg || after.stages[0].bg[0] !== '#111111') { console.error('FAIL: stage bg edit did not survive reload. got', after.stages[0].bg); process.exit(1); }
  if (after.stages.length !== 5) { console.error('FAIL: stage count changed unexpectedly', after.stages.length); process.exit(1); }
  H.ui.setTab(5);
  const html2 = H.ui.html();
  if (!html2.includes('Outskirts EDITED') || !html2.includes('value="999"')) {
    console.error('FAIL: re-rendered STAGES tab does not reflect the persisted edit\n', html2.slice(0, 400));
    process.exit(1);
  }
  console.log('PASS 2: stage edit persisted to localStorage (' + FORGE_KEY + ') and survived a fresh reload via forgeMerge().');
  console.log('ALL PASS: FORGE STAGES tab verified.');
})().catch(e => { console.error('THREW', e); process.exit(1); });
