/**
 * MusicHunter v3 — Entry Point
 */
import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'

// Styles
import './styles/variables.css'
import './styles/base.css'

// Views
import SearchView from './views/SearchView.vue'
import LikesView from './views/LikesView.vue'
import PlaylistsView from './views/PlaylistsView.vue'
import HistoryView from './views/HistoryView.vue'
import DownloadedView from './views/DownloadedView.vue'

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
