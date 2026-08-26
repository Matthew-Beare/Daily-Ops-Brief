"use strict";

const CACHE = "mirror-client-shell-v8";
const SHELL = [
  "./", "./index.html", "./app.js", "./client-hardening.js", "./platform-ui.js", "./product-v1.js",
  "./smart-capture.js", "./guided-migration.js", "./ble-proximity.js", "./receipt-v1.js", "./native-updater.js", "./integrations-v1.js", "./commercial.css",
  "./manifest.webmanifest", "./icon.svg", "./tutorial-google.svg", "./tutorial-github.svg", "./tutorial-conflict.svg", "./tutorial-hierarchy.svg"
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
