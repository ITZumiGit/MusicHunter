<template>
  <div class="search-view">
    <!-- Search header -->
    <div class="search-header">
      <h1 class="page-title">Поиск</h1>
      <SearchBar @search="handleSearch" :loading="loading" />
    </div>
    
    <!-- Loading -->
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Ищем музыку...</p>
    </div>
    
    <!-- Error -->
    <div v-else-if="errorMsg" class="state-container error-state">
      <div class="error-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      </div>
      <h3>Ошибка загрузки</h3>
      <p class="error-text">{{ errorMsg }}</p>
      <button class="retry-btn" @click="retryLastSearch">Повторить</button>
    </div>
    
    <!-- Results -->
    <div v-else-if="results.length" class="results-container">
      <div class="results-header">
        <span class="results-count">Найдено: {{ results.length }}</span>
      </div>
      <TrackList
        :tracks="results"
        :current-track="player.currentTrack.value"
        :is-playing="player.isPlaying.value"
        :liked-ids="player.likedIds.value"
        @play="onPlayTrack"
        @like="player.toggleTrackLike"
      />
    </div>
    
    <!-- Empty state -->
    <div v-else-if="searched" class="state-container">
      <div class="empty-icon">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
      </div>
      <h3>Ничего не найдено</h3>
      <p>Попробуйте другой запрос</p>
    </div>
    
    <!-- Welcome state -->
    <div v-else class="welcome">
      <div class="welcome-visual">
        <div class="welcome-orb"></div>
        <svg class="welcome-note" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
        </svg>
      </div>
      <h2>MusicHunter</h2>
      <p>Найдите любой трек</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { inject } from 'vue'
import SearchBar from '../components/SearchBar.vue'
import TrackList from '../components/TrackList.vue'
import { searchTracks, type Track } from '../services/api'

const player = inject<any>('player')

const loading = ref(false)
const searched = ref(false)
const results = ref<Track[]>([])
const errorMsg = ref('')
const lastQuery = ref('')

async function handleSearch(query: string) {
  if (!query.trim()) return
  lastQuery.value = query
  loading.value = true
  searched.value = true
  errorMsg.value = ''
  try {
    const data = await searchTracks(query)
    results.value = data.tracks
  } catch (e: any) {
    errorMsg.value = e?.message || 'Не удалось выполнить поиск'
    results.value = []
  } finally {
    loading.value = false
  }
}

function retryLastSearch() {
  if (lastQuery.value) handleSearch(lastQuery.value)
}

function onPlayTrack(track: Track, index: number) {
  player.setQueue(results.value, index)
}
</script>

<style scoped>
.search-view {
  padding: var(--space-xl);
  min-height: 100%;
}

.search-header {
  margin-bottom: var(--space-xl);
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--fg-primary);
  margin-bottom: var(--space-lg);
}

/* ─── States ─── */
.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: calc(var(--space-xl) * 2);
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
  color: var(--fg-secondary);
}

.error-icon {
  color: var(--pink);
  margin-bottom: var(--space-lg);
}

.error-text {
  color: var(--fg-muted);
  font-size: 13px;
  max-width: 260px;
  word-break: break-word;
  margin-bottom: var(--space-md);
}

.retry-btn {
  padding: 10px 28px;
  border-radius: var(--radius-full);
  background: var(--accent-gradient);
  color: white;
  font-size: 14px;
  font-weight: 600;
  transition: all var(--transition);
  border: none;
  cursor: pointer;
}

.retry-btn:active { transform: scale(0.95); }

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-lg);
}

.empty-icon {
  color: var(--fg-muted);
  margin-bottom: var(--space-lg);
}

/* ─── Welcome ─── */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 18vh;
  text-align: center;
}

.welcome-visual {
  position: relative;
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-2xl);
}

.welcome-orb {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: var(--accent-gradient);
  opacity: 0.12;
  animation: orb-pulse 3s ease-in-out infinite;
}

.welcome-note {
  position: relative;
  z-index: 1;
  color: var(--accent);
}

.welcome h2 {
  font-size: 28px;
  font-weight: 800;
  color: var(--fg-primary);
  margin-bottom: var(--space-sm);
}

.welcome p {
  font-size: 15px;
  color: var(--fg-muted);
}

@keyframes orb-pulse {
  0%, 100% { transform: scale(1); opacity: 0.12; }
  50% { transform: scale(1.15); opacity: 0.2; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ─── Results ─── */
.results-container { margin-top: var(--space-md); }

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.results-count {
  font-size: 12px;
  color: var(--fg-muted);
  font-weight: 600;
}

/* Mobile */
@media (max-width: 767px) {
  .search-view {
    padding: var(--space-lg);
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile) + var(--space-xl));
  }
}
</style>
