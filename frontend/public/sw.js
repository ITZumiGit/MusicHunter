/**
 * MusicHunter Service Worker — Offline-first cache
 * Кеширует статические ресурсы (HTML, JS, CSS) для работы без интернета.
 * Аудио стримы не кешируются здесь — они кешируются через IndexedDB (useDownloads).
 */

const CACHE_NAME = 'musichunter-v2-20260628'
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
]

// Install — пре-кешируем критические ресурсы
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch(() => {
        // Если какие-то ресурсы не загрузились — не блокируем
        console.warn('[SW] Failed to cache some static assets')
      })
    })
  )
  self.skipWaiting()
})

// Activate — удаляем старые кеши
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    })
  )
  self.clients.claim()
})

// Fetch — network-first для HTML/API, cache-first для статики
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // API запросы — всегда network-first (нужны свежие данные)
  if (url.pathname.startsWith('/search') ||
      url.pathname.startsWith('/likes') ||
      url.pathname.startsWith('/playlists') ||
      url.pathname.startsWith('/history') ||
      url.pathname.startsWith('/stats') ||
      url.pathname.startsWith('/local')) {
    event.respondWith(
      fetch(request).catch(() => {
        // Если сеть недоступна и это навигация — вернуть кеш
        if (request.mode === 'navigate') {
          return caches.match('/index.html')
        }
        return new Response(JSON.stringify({ offline: true }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        })
      })
    )
    return
  }

  // Аудио стримы — network-first с fallback на IndexedDB (обрабатывается в приложении)
  if (url.pathname.startsWith('/stream/') || url.pathname.startsWith('/download/') || url.pathname.startsWith('/local/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(null, { status: 503, statusText: 'Offline' })
      })
    )
    return
  }

  // Статические ресурсы (JS, CSS, изображения) — network-first с кэшированием
  // Для Vite ассетов с хэш-именами это гарантирует актуальную версию
  event.respondWith(
    fetch(request).then((response) => {
      if (response.ok && request.method === 'GET') {
        const clone = response.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(request, clone))
      }
      return response
    }).catch(() => {
      return caches.match(request)
    })
  )
})
