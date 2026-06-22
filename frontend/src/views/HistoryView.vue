<template>
  <div class="history-view">
    <div class="header-row">
      <h1 class="page-title">История</h1>
      <button v-if="tracks.length" class="btn-clear" @click="clearHistory">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
        </svg>
        Очистить
      </button>
    </div>
    
    <!-- Loading -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Загрузка...</p>
    </div>
    
    <!-- Tracks -->
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
    
    <!-- Empty -->
    <div v-else class="state-container">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
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
  } catch {
    tracks.value = []
  } finally {
    loading.value = false
  }
}

async function clearHistory() {
  if (!confirm('Очистить всю историю?')) return
  
  try {
    await apiClearHistory(player.tgUserId.value)
    tracks.value = []
  } catch {
    // Error
  }
}

function onPlayTrack(track: Track, index: number) {
  player.setQueue(tracks.value, index)
}

onMounted(() => {
  loadHistory()
})
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
  font-size: 24px;
  font-weight: 700;
  color: var(--fg-primary);
}

.btn-clear {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: transparent;
  color: var(--fg-secondary);
  border-radius: var(--radius);
  font-size: 13px;
  transition: all var(--transition);
}

.btn-clear:hover {
  background: var(--bg-tertiary);
  color: var(--pink);
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-xl) * 2;
  text-align: center;
  color: var(--fg-secondary);
}

.state-container h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--fg-primary);
  margin-bottom: var(--space-sm);
}

.state-container p {
  font-size: 14px;
  color: var(--fg-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-lg);
}

.empty-icon {
  color: var(--fg-muted);
  opacity: 0.5;
  margin-bottom: var(--space-lg);
}

.tracks-container {
  margin-top: var(--space-md);
}

/* Mobile */
@media (max-width: 767px) {
  .history-view {
    padding: var(--space-lg);
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile) + var(--space-xl));
  }
}
</style>
