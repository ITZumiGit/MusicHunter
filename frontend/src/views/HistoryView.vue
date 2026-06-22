<template>
  <div class="history-view">
    <div class="header-row">
      <h1 class="page-title">История</h1>
      <button v-if="tracks.length" class="btn-clear" @click="clearHistory">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
        Очистить
      </button>
    </div>
    
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Загрузка...</p>
    </div>
    
    <div v-else-if="tracks.length" class="tracks-container">
      <TrackList
        :tracks="tracks"
        :current-track="player.currentTrack.value"
        :is-playing="player.isPlaying.value"
        :liked-ids="player.likedIds.value"
        @play="onPlayTrack"
        @like="player.toggleTrackLike"
      />
    </div>
    
    <div v-else class="state-container">
      <div class="empty-icon-wrap">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
      </div>
      <h3>История пуста</h3>
      <p>Включите музыку, чтобы начать</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { inject } from 'vue'
import TrackList from '../components/TrackList.vue'
import { getHistory, clearHistory as apiClearHistory, type Track } from '../services/api'

const player = inject<any>('player')
const loading = ref(true)
const tracks = ref<Track[]>([])

async function loadHistory() {
  loading.value = true
  try {
    const data = await getHistory(player.tgUserId.value)
    tracks.value = data.tracks
  } catch { tracks.value = [] }
  finally { loading.value = false }
}

async function clearHistory() {
  if (!confirm('Очистить всю историю?')) return
  try {
    await apiClearHistory(player.tgUserId.value)
    tracks.value = []
  } catch { /* error */ }
}

function onPlayTrack(track: Track, index: number) {
  player.setQueue(tracks.value, index)
}

onMounted(() => loadHistory())
</script>

<style scoped>
.history-view {
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

.btn-clear {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--bg-card);
  color: var(--fg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  transition: all var(--transition);
  cursor: pointer;
}

.btn-clear:hover {
  background: rgba(244, 114, 182, 0.1);
  color: var(--pink);
  border-color: rgba(244, 114, 182, 0.2);
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20vh;
  text-align: center;
  color: var(--fg-secondary);
}

.state-container h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: var(--space-sm);
}

.state-container p {
  font-size: 14px;
  color: var(--fg-muted);
}

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

.tracks-container { margin-top: var(--space-md); }

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 767px) {
  .history-view {
    padding: var(--space-lg);
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile) + var(--space-xl));
  }
}
</style>
