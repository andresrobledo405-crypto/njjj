// Service worker mínimo: permite instalar la app. No guarda en caché datos de la API (información clínica).
const SHELL = "clinicapro-shell-v2";
self.addEventListener("install", e => e.waitUntil(caches.open(SHELL).then(c => c.addAll(["/static/icon.svg"]))));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== SHELL).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).pathname.startsWith("/api")) return;
});
