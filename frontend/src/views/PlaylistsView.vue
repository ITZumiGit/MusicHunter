<template>
  <div class="playlists-view">
    <div class="header-row">
      <h1 class="page-title">Плейлисты</h1>
      <button class="btn-create" @click="showCreateModal = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        Создать
      </button>
    </div>
    
    <!-- Create modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
          <div class="modal">
            <h3>Новый плейлист</h3>
            <input v-model="newPlaylistName" type="text" placeholder="Название" class="input" @keydown.enter="createPlaylist" />
            <textarea v-model="newPlaylistDesc" placeholder="Описание (необязательно)" class="input textarea"></textarea>
            <div class="modal-actions">
              <button class="btn-secondary" @click="showCreateModal = false">Отмена</button>
              <button class="btn-primary" @click="createPlaylist" :disabled="!newPlaylistName.trim()">Создать</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
    
    <!-- Playlist detail -->
    <div v-if="activePlaylist" class="playlist-detail">
      <button class="btn-back" @click="activePlaylist = null">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"/></svg>
        Назад
      </button>
      <h2 class="playlist-title">{{ activePlaylist.name }}</h2>
      <p v-if="activePlaylist.description" class="playlist-desc">{{ activePlaylist.description }}</p>
      
      <div v-if="activePlaylist.tracks.length" class="tracks-container">
        <TrackList
          :tracks="activePlaylist.tracks"
          :current-track="player.currentTrack.value"
          :is-playing="player.isPlaying.value"
          :liked-ids="player.likedIds.value"
          @play="onPlayTrack"
          @like="player.toggleTrackLike"
        />
      </div>
      <div v-else class="empty-playlist">Пока нет треков</div>
    </div>
    
    <!-- Playlists list -->
    <template v-else>
      <div v-if="loading" class="state-container">
        <div class="spinner"></div>
        <p>Загрузка...</p>
      </div>
      
      <div v-else-if="playlists.length" class="playlists-grid">
        <div v-for="pl in playlists" :key="pl.id" class="playlist-card" @click="openPlaylist(pl.id)">
          <div class="playlist-cover">
            <img v-if="pl.cover_url" :src="pl.cover_url" :alt="pl.name" />
            <div v-else class="cover-placeholder">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
              </svg>
            </div>
          </div>
          <div class="playlist-info">
            <div class="playlist-name">{{ pl.name }}</div>
            <div class="playlist-meta">{{ pl.track_count }} треков</div>
          </div>
        </div>
      </div>
      
      <div v-else class="state-container">
        <div class="empty-icon-wrap">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
          </svg>
        </div>
        <h3>Нет плейлистов</h3>
        <p>Создайте свой первый</p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { inject } from 'vue'
import TrackList from '../components/TrackList.vue'
import { getPlaylists, getPlaylist, createPlaylist as apiCreate, type Playlist, type PlaylistDetail, type Track } from '../services/api'

const player = inject<any>('player')
const loading = ref(true)
const playlists = ref<Playlist[]>([])
const activePlaylist = ref<PlaylistDetail | null>(null)
const showCreateModal = ref(false)
const newPlaylistName = ref('')
const newPlaylistDesc = ref('')

async function loadPlaylists() {
  loading.value = true
  try {
    const data = await getPlaylists(player.tgUserId.value)
    playlists.value = data.playlists
  } catch { playlists.value = [] }
  finally { loading.value = false }
}

async function openPlaylist(id: number) {
  try { activePlaylist.value = await getPlaylist(player.tgUserId.value, id) }
  catch { activePlaylist.value = null }
}

async function createPlaylist() {
  if (!newPlaylistName.value.trim()) return
  try {
    await apiCreate(player.tgUserId.value, newPlaylistName.value, newPlaylistDesc.value)
    newPlaylistName.value = ''
    newPlaylistDesc.value = ''
    showCreateModal.value = false
    await loadPlaylists()
  } catch { /* error */ }
}

function onPlayTrack(track: Track, index: number) {
  if (activePlaylist.value) player.setQueue(activePlaylist.value.tracks, index)
}

onMounted(() => loadPlaylists())
</script>

<style scoped>
.playlists-view {
  padding: var(--space-xl);
  min-height: 100%;
}

.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--fg-primary);
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: var(--accent-gradient);
  color: white;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: 700;
  transition: all var(--transition);
  box-shadow: 0 2px 12px rgba(139, 92, 246, 0.3);
}

.btn-create:active { transform: scale(0.95); }

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20vh;
  text-align: center;
}

.state-container h3 { font-size: 18px; font-weight: 700; color: var(--fg-primary); margin-bottom: var(--space-sm); }
.state-container p { font-size: 14px; color: var(--fg-muted); }

.spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-lg);
}

.empty-icon-wrap {
  display: flex; align-items: center; justify-content: center;
  width: 80px; height: 80px; border-radius: var(--radius-xl);
  background: var(--accent-gradient-subtle);
  color: var(--accent);
  margin-bottom: var(--space-lg);
}

/* Grid */
.playlists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-md);
}

.playlist-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: all var(--transition-slow);
  backdrop-filter: blur(8px);
}

.playlist-card:hover {
  border-color: var(--border-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.playlist-card:active { transform: scale(0.97); }

.playlist-cover {
  aspect-ratio: 1;
  background: var(--bg-tertiary);
}

.playlist-cover img { width: 100%; height: 100%; object-fit: cover; }

.cover-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  background: var(--accent-gradient-subtle);
  color: var(--accent);
}

.playlist-info { padding: var(--space-md); }

.playlist-name {
  font-size: 13px; font-weight: 600; color: var(--fg-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.playlist-meta { font-size: 11px; color: var(--fg-muted); margin-top: 3px; }

/* Detail */
.playlist-detail { margin-top: var(--space-md); }

.btn-back {
  display: flex; align-items: center; gap: 6px;
  padding: var(--space-sm) 0; color: var(--accent);
  font-size: 14px; font-weight: 600; margin-bottom: var(--space-lg);
}

.playlist-title { font-size: 22px; font-weight: 800; color: var(--fg-primary); margin-bottom: var(--space-sm); }
.playlist-desc { font-size: 14px; color: var(--fg-secondary); margin-bottom: var(--space-xl); }
.tracks-container { margin-top: var(--space-md); }
.empty-playlist { text-align: center; padding: var(--space-xl); color: var(--fg-muted); font-size: 14px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: var(--space-lg);
}

.modal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  width: 100%; max-width: 380px;
  box-shadow: var(--shadow-lg);
}

.modal h3 { font-size: 18px; font-weight: 700; color: var(--fg-primary); margin-bottom: var(--space-lg); }

.input {
  width: 100%; padding: 12px 14px;
  background: var(--bg-tertiary); border: 1px solid var(--border);
  border-radius: var(--radius); font-size: 14px; color: var(--fg-primary);
  margin-bottom: var(--space-md); outline: none; transition: border-color 0.2s;
}

.input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.input::placeholder { color: var(--fg-muted); }
.textarea { min-height: 80px; resize: vertical; }

.modal-actions { display: flex; justify-content: flex-end; gap: var(--space-md); margin-top: var(--space-lg); }

.btn-secondary {
  padding: 8px 18px; background: var(--bg-tertiary); color: var(--fg-primary);
  border-radius: var(--radius); font-size: 14px; font-weight: 500; transition: all var(--transition);
}

.btn-primary {
  padding: 8px 18px; background: var(--accent-gradient); color: white;
  border-radius: var(--radius); font-size: 14px; font-weight: 600; transition: all var(--transition);
}

.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

@keyframes spin { to { transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 767px) {
  .playlists-view {
    padding: var(--space-lg);
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile) + var(--space-xl));
  }
  .playlists-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
