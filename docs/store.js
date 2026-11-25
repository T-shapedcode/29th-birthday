// Local-first storage for the Vision Book.
//
//  1. Your device (IndexedDB)  — always. Works offline. No server can wipe it.
//  2. A backup file             — optional, laptop (Chrome/Edge): auto-saves into a file
//                                 you choose, e.g. inside iCloud Drive / OneDrive / Google Drive.
//  3. Your private GitHub vault — optional: syncs phone <-> laptop, merged per field.
//
// The data format is identical to the earlier Streamlit version, so old backups
// and an existing vault file (vision_book.json) load straight in.

const DB_NAME = "visionbook";
let dbp = null;

function db() {
  if (!dbp) {
    dbp = new Promise((res, rej) => {
      const r = indexedDB.open(DB_NAME, 1);
      r.onupgradeneeded = () => {
        for (const s of ["kv", "images"]) if (!r.result.objectStoreNames.contains(s)) r.result.createObjectStore(s);
      };
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  }
  return dbp;
}

async function idb(store, mode, fn) {
  const d = await db();
  return new Promise((res, rej) => {
    const tx = d.transaction(store, mode);
    const req = fn(tx.objectStore(store));
    tx.oncomplete = () => res(req && req.result);
    tx.onerror = () => rej(tx.error);
  });
}
const kvGet = (k) => idb("kv", "readonly", (s) => s.get(k));
const kvSet = (k, v) => idb("kv", "readwrite", (s) => s.put(v, k));
export const imgGet = (k) => idb("images", "readonly", (s) => s.get(k));
const imgSet = (k, v) => idb("images", "readwrite", (s) => s.put(v, k));

const clone = (o) => JSON.parse(JSON.stringify(o ?? {}));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// ---------------------------------------------------------------------------
export const state = {
  book: {},          // all your writing
  meta: {},          // sync bookkeeping: base snapshot, sha, settings
  status: { cloud: "off", file: "off", lastError: "" },
  onRemoteChange: null,
  onStatus: null,
};

function emit() { state.onStatus && state.onStatus(state.status); }

export async function init() {
  try { if (navigator.storage && navigator.storage.persist) await navigator.storage.persist(); } catch (e) {}
  state.book = (await kvGet("book")) || {};
  state.meta = (await kvGet("meta")) || {};
  if (state.meta.vault?.token) state.status.cloud = navigator.onLine ? "syncing" : "offline";
  if (await kvGet("fileHandle")) state.status.file = "connected";
  emit();
  window.addEventListener("online", () => scheduleSync(0));
  document.addEventListener("visibilitychange", () => { if (!document.hidden) scheduleSync(0); });
  await checkFilePermission();
  scheduleSync(0);
}

let saveTimer = null;
export function save() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {
    await kvSet("book", state.book);
    state.meta.lastLocalSave = new Date().toISOString();
    await kvSet("meta", state.meta);
    scheduleFile();
    scheduleSync(1500);
  }, 250);
}
// make sure nothing is lost when the tab closes
window.addEventListener("pagehide", () => { kvSet("book", state.book); });

export async function replaceBook(data) {
  for (const k of Object.keys(state.book)) delete state.book[k];
  Object.assign(state.book, data || {});
  await kvSet("book", state.book);
  scheduleFile();
  scheduleSync(0);
}

// ---------------------------------------------------------------------------
// GitHub vault
// ---------------------------------------------------------------------------
const API = "https://api.github.com";

function b64encode(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
function b64decode(str) {
  const bin = atob(str.replace(/\n/g, ""));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function gh(path, opts = {}) {
  const v = state.meta.vault;
  return fetch(`${API}/repos/${v.repo}${path}`, {
    ...opts,
    cache: "no-store",
    headers: { Authorization: `Bearer ${v.token}`, Accept: "application/vnd.github+json", ...(opts.headers || {}) },
  });
}
const filePath = () => state.meta.vault.path || "vision_book.json";

export async function connectVault(token, repo) {
  repo = repo.trim().replace(/^https?:\/\/github\.com\//, "").replace(/\/$/, "");
  const prev = state.meta.vault;
  state.meta.vault = { token: token.trim(), repo, path: "vision_book.json" };
  const r = await gh("");
  let problem = "";
  if (r.status === 401 || r.status === 403) problem = "The key (token) isn't accepted. Check it was copied completely and hasn't expired.";
  else if (r.status === 404) problem = `I can't find "${repo}". Check the name, and that the key has access to this repository.`;
  else if (!r.ok) problem = `GitHub answered ${r.status}.`;
  else if (!(await r.json()).private) problem = `"${repo}" is PUBLIC. Your journal may only live in a private repository.`;
  if (problem) { state.meta.vault = prev; return problem; }
  state.meta.base = {}; state.meta.sha = null;   // first sync merges both sides, nothing is dropped
  await kvSet("meta", state.meta);
  await sync();
  return state.status.cloud === "synced" ? "" : state.status.lastError;
}

export async function disconnectVault() {
  delete state.meta.vault; state.meta.base = {}; state.meta.sha = null;
  state.status.cloud = "off"; await kvSet("meta", state.meta); emit();
}

async function pull() {
  const r = await gh(`/contents/${filePath()}`);
  if (r.status === 404) return { remote: {}, sha: null };
  if (!r.ok) throw new Error(`reading the vault failed (${r.status})`);
  const meta = await r.json();
  let bytes;
  if (meta.content) bytes = b64decode(meta.content);
  else {
    const rr = await gh(`/contents/${filePath()}`, { headers: { Accept: "application/vnd.github.raw" } });
    bytes = new Uint8Array(await rr.arrayBuffer());
  }
  return { remote: JSON.parse(new TextDecoder().decode(bytes) || "{}"), sha: meta.sha };
}

// 3-way merge per field: what changed on this device wins for that field,
// everything else comes from the vault (= the other device's changes).
function merge(base, local, remote) {
  const out = clone(remote);
  for (const k of new Set([...Object.keys(local), ...Object.keys(base)])) {
    const changedHere = !same(local[k], base[k]);
    if (!changedHere) continue;
    if (k in local) out[k] = clone(local[k]);
    else delete out[k];
  }
  return out;
}

let syncTimer = null, syncing = false, again = false;
export function scheduleSync(ms) {
  if (!state.meta.vault?.token) return;
  clearTimeout(syncTimer);
  syncTimer = setTimeout(sync, ms);
}

export async function sync() {
  if (!state.meta.vault?.token) return;
  if (!navigator.onLine) { state.status.cloud = "offline"; emit(); return; }
  if (syncing) { again = true; return; }
  syncing = true; state.status.cloud = "syncing"; emit();
  try {
    for (let attempt = 0; attempt < 4; attempt++) {
      const { remote, sha } = await pull();
      const base = state.meta.base || {};
      const snap = clone(state.book);              // what this device has right now
      const merged = merge(base, snap, remote);
      const remoteChangedUs = !same(merged, snap);
      if (same(merged, remote)) {       // nothing to upload
        state.meta.sha = sha; state.meta.base = clone(remote);
      } else {
        const body = {
          message: "journal update",
          content: b64encode(new TextEncoder().encode(JSON.stringify(merged, null, 1))),
          ...(sha ? { sha } : {}),
        };
        const r = await gh(`/contents/${filePath()}`, { method: "PUT", body: JSON.stringify(body) });
        if (r.status === 409 || r.status === 422) continue;   // the other device saved in between: merge again
        if (!r.ok) throw new Error(`saving to the vault failed (${r.status})`);
        state.meta.sha = (await r.json()).content.sha;
        state.meta.base = clone(merged);
      }
      // apply the merge to the live book, but never touch a field you edited while this sync ran
      for (const k of new Set([...Object.keys(state.book), ...Object.keys(merged)])) {
        if (!same(state.book[k], snap[k])) continue;
        if (k in merged) state.book[k] = clone(merged[k]); else delete state.book[k];
      }
      await kvSet("book", state.book);
      state.meta.lastCloudSync = new Date().toISOString();
      await kvSet("meta", state.meta);
      state.status.cloud = "synced"; state.status.lastError = "";
      if (remoteChangedUs && state.onRemoteChange) state.onRemoteChange();
      await uploadPendingImages();
      break;
    }
  } catch (e) {
    state.status.cloud = navigator.onLine ? "error" : "offline";
    state.status.lastError = String(e.message || e);
  } finally {
    syncing = false; emit();
    if (again) { again = false; scheduleSync(500); }
  }
}

// ---------------------------------------------------------------------------
// Images (mood board) — stored on the device, copied to the vault when connected
// ---------------------------------------------------------------------------
export async function addImage(file) {
  const blob = await shrink(file);
  const id = Date.now().toString(36) + Math.random().toString(36).slice(2, 6) + ".jpg";
  await imgSet(id, blob);
  state.meta.pendingImages = [...(state.meta.pendingImages || []), id];
  await kvSet("meta", state.meta);
  scheduleSync(500);
  return "img:" + id;
}

async function shrink(file, max = 1200) {
  try {
    const bmp = await createImageBitmap(file);
    const s = Math.min(1, max / Math.max(bmp.width, bmp.height));
    const c = document.createElement("canvas");
    c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
    c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
    return await new Promise((res) => c.toBlob(res, "image/jpeg", 0.85));
  } catch (e) { return file; }
}

async function uploadPendingImages() {
  const left = [];
  for (const id of state.meta.pendingImages || []) {
    const blob = await imgGet(id);
    if (!blob) continue;
    const r = await gh(`/contents/images/${id}`, {
      method: "PUT",
      body: JSON.stringify({ message: "mood board image", content: b64encode(new Uint8Array(await blob.arrayBuffer())) }),
    });
    if (!r.ok && r.status !== 422) left.push(id);
  }
  state.meta.pendingImages = left; await kvSet("meta", state.meta);
}

const urlCache = {};
export async function imageURL(src) {
  if (!src) return "";
  if (urlCache[src]) return urlCache[src];
  let path = null, id = null;
  if (src.startsWith("img:")) { id = src.slice(4); path = `images/${id}`; }
  else if (src.startsWith("gh:")) { path = src.slice(3); id = path.split("/").pop(); }
  else if (src.startsWith("file:")) return "";
  else return src;
  let blob = await imgGet(id);
  if (!blob && state.meta.vault?.token && navigator.onLine) {
    const r = await gh(`/contents/${path}`, { headers: { Accept: "application/vnd.github.raw" } });
    if (r.ok) { blob = await r.blob(); await imgSet(id, blob); }
  }
  return blob ? (urlCache[src] = URL.createObjectURL(blob)) : "";
}

// ---------------------------------------------------------------------------
// Backup file on the laptop (File System Access API — Chrome / Edge)
// ---------------------------------------------------------------------------
export const fileSupported = () => "showSaveFilePicker" in window;

export async function connectFile() {
  const handle = await window.showSaveFilePicker({
    suggestedName: "my-vision-book.json",
    types: [{ description: "Vision Book", accept: { "application/json": [".json"] } }],
  });
  await kvSet("fileHandle", handle);
  state.status.file = "connected"; emit();
  await writeFile();
}

export async function reconnectFile() {
  const h = await kvGet("fileHandle");
  if (h && (await h.requestPermission({ mode: "readwrite" })) === "granted") {
    state.status.file = "connected"; emit(); await writeFile();
  }
}

export async function disconnectFile() {
  await kvSet("fileHandle", null); state.status.file = "off"; emit();
}

async function checkFilePermission() {
  const h = await kvGet("fileHandle");
  if (!h) return;
  try {
    state.status.file = (await h.queryPermission({ mode: "readwrite" })) === "granted" ? "connected" : "needs-permission";
  } catch (e) { state.status.file = "needs-permission"; }
  emit();
}

let fileTimer = null;
function scheduleFile() { clearTimeout(fileTimer); fileTimer = setTimeout(writeFile, 1200); }

async function writeFile() {
  const h = await kvGet("fileHandle");
  if (!h || state.status.file !== "connected") return;
  try {
    const w = await h.createWritable();
    await w.write(JSON.stringify(state.book, null, 1));
    await w.close();
    state.meta.lastFileSave = new Date().toISOString();
    await kvSet("meta", state.meta);
  } catch (e) {
    state.status.file = "needs-permission"; emit();
  }
}

export async function markExported() {
  state.meta.lastExport = new Date().toISOString();
  await kvSet("meta", state.meta);
}
