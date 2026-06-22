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
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
          <line x1="8" y1="11" x2="14" y2="11"/>
        </svg>
      </div>
      <h3>Ничего не найдено</h3>
      <p>Попробуйте другой запрос</p>
    </div>
    
    <!-- Welcome state -->
    <div v-else class="state-container welcome">
      <div class="welcome-icon">
        <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M9 18V5l12-2v13"/>
          <circle cx="6" cy="18" r="3"/>
          <circle cx="18" cy="16" r="3"/>
        </svg>
      </div>
      <h2>MusicHunter</h2>
      <p>Найдите любой трек в поиске</p>
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

async function handleSearch(query: string) {
  if (!query.trim()) return
  
  loading.value = true
  searched.value = true
  
  try {
    const data = await searchTracks(query)
    console.log('[MusicHunter] Search results:', data.count)
    results.value = data.tracks
  } catch (e) {
    console.error('[MusicHunter] Search error:', e)
    results.value = []
  } finally {
    loading.value = false
  }
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
  font-size: 24px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: var(--space-lg);
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
  margin-bottom: var(--space-lg);
}

.welcome {
  padding-top: 15%;
}

.welcome-icon {
  color: var(--accent);
  opacity: 0.5;
  margin-bottom: var(--space-xl);
  animation: pulse 2s ease-in-out infinite;
}

.welcome h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: var(--space-sm);
}

.results-container {
  margin-top: var(--space-md);
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.results-count {
  font-size: 13px;
  color: var(--fg-muted);
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .search-view {
    padding: var(--space-lg);
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile) + var(--space-xl));
  }
}
</style>
