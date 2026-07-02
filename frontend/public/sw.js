// MusicHunter Service Worker — minimal, network-only
// No caching to avoid stale JS/CSS and CORS issues with audio
const CACHE_NAME = 'musichunter-v4-20260702';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  // Network-first for everything — no caching to avoid stale assets
  event.respondWith(
    fetch(event.request).catch(() => {
      // Offline fallback only for navigation
      if (event.request.mode === 'navigate') {
        return caches.match('/index.html');
      }
      return new Response('Offline', { status: 503 });
    })
  );
});
