"use strict";

const CACHE = "mirror-client-shell-v16";
const SHELL = [
  "./", "./index.html", "./app.js", "./provider-connect-v3.js", "./google-authority-v1.js", "./cloud-authority-compat.js", "./client-hardening.js", "./platform-ui.js", "./product-v1.js",
  "./smart-capture.js", "./guided-migration.js", "./ble-proximity.js", "./receipt-v1.js", "./native-updater.js", "./integrations-v1.js", "./dashboard-v2.js", "./onboarding-polish.js", "./interaction-audit.js", "./experience-v3.js", "./native-kiosk-bridge.js", "./brand-final.js",
  "./commercial.css", "./sleek-v2.css", "./experience-v3.css", "./android-fixes.css", "./brand-final.css",
  "./manifest.webmanifest", "./mira-logo.png", "./tutorial-google.svg", "./tutorial-github.svg", "./tutorial-conflict.svg", "./tutorial-hierarchy.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/v1/")) return;
  event.respondWith(fetch(event.request).then((response) => { const copy = response.clone(); caches.open(CACHE).then((cache) => cache.put(event.request, copy)); return response; }).catch(() => caches.match(event.request).then((cached) => cached || caches.match("./index.html"))));
});

self.addEventListener("push", (event) => {
  let payload = {};
  try { payload = event.data ? event.data.json() : {}; } catch (_) { payload = { body: event.data?.text?.() || "" }; }
  const title = String(payload.title || "MIRA");
  const options = {
    body: String(payload.body || "You have an update."),
    icon: "./mira-logo.png",
    badge: "./mira-logo.png",
    tag: String(payload.tag || "mira-update"),
    data: { url: String(payload.url || "./") },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const target = event.notification.data?.url || "./";
  event.waitUntil(clients.matchAll({ type: "window", includeUncontrolled: true }).then((windows) => {
    const existing = windows.find((client) => "focus" in client);
    if (existing) { existing.navigate(target).catch(() => {}); return existing.focus(); }
    return clients.openWindow(target);
  }));
});
