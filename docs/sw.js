// Offline support: the app itself is cached on your device. Your writing is never
// sent here — it lives in IndexedDB (and your own backup/vault).
const VERSION = "vb-1";
const SHELL = ["./", "index.html", "app.js", "store.js", "content.js", "style.css", "manifest.webmanifest", "icon.svg", "icon-180.png", "icon-192.png", "icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION && k !== "fonts").map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.hostname === "api.github.com") return; // vault traffic always goes live
  if (url.hostname.includes("fonts.g")) {           // fonts: cache once, then offline
    e.respondWith(caches.open("fonts").then(async (c) => (await c.match(e.request)) || fetch(e.request).then((r) => { c.put(e.request, r.clone()); return r; })));
    return;
  }
  if (url.origin !== location.origin) return;
  // app files: use the network when online (so updates arrive), fall back to the cache offline
  e.respondWith(
    fetch(e.request).then((r) => { const copy = r.clone(); caches.open(VERSION).then((c) => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request, { ignoreSearch: true }).then((r) => r || caches.match("index.html")))
  );
});
