/**
 * MusicHunter v3 — Entry Point
 */
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'

// Styles
import './styles/variables.css'
import './styles/base.css'

// Lazy-loaded views — загружаются только при переходе
const SearchView = () => import('./views/SearchView.vue')
const LikesView = () => import('./views/LikesView.vue')
const PlaylistsView = () => import('./views/PlaylistsView.vue')
const HistoryView = () => import('./views/HistoryView.vue')
const DownloadedView = () => import('./views/DownloadedView.vue')

// Router
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: SearchView },
    { path: '/likes', component: LikesView },
    { path: '/playlists', component: PlaylistsView },
    { path: '/downloaded', component: DownloadedView },
    { path: '/history', component: HistoryView },
  ],
})

// Create app
const app = createApp(App)
app.use(router)
app.mount('#app')

// Register Service Worker for offline support
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {})
  })
}
