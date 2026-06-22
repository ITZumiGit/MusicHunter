<template>
  <div class="downloaded-view">
    <h1 class="page-title">Библиотека</h1>
    <p class="page-subtitle">Скачанные треки и музыка бота</p>

    <!-- Bot music section -->
    <div v-if="localTracks.length" class="section">
      <div class="section-header">
        <h2 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Музыка бота
        </h2>
        <span class="count-badge">{{ localTracks.length }}</span>
      </div>
      <p class="section-desc">Аудиофайлы с сервера — всегда доступны</p>
      <TrackList
        :tracks="localTracks"
        :current-track="player.currentTrack.value"
        :is-playing="player.isPlaying.value"
        :liked-ids="player.likedIds.value"
        @play="handlePlayLocal"
        @like="handleLike"
      />
    </div>

    <!-- Downloaded section -->
    <div class="section">
      <div class="section-header">
        <h2 class="section-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Скачанные
        </h2>
        <span class="count-badge">{{ downloads.count.value }}</span>
      </div>

      <div v-if="downloads.count.value === 0 && !localTracks.length" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <p>Нет скачанных треков</p>
        <p class="empty-hint">Нажмите ⬇ в плеере или в меню трека, чтобы скачать</p>
      </div>

      <div v-else-if="downloads.count.value > 0" class="downloaded-actions">
        <p class="section-desc">Доступны без интернета</p>
        <button class="clear-btn" @click="handleClearAll">Очистить</button>
      </div>

      <TrackList
        v-if="downloads.count.value > 0"
        :tracks="downloads.downloadedTracks.value"
        :current-track="player.currentTrack.value"
        :is-playing="player.isPlaying.value"
        :liked-ids="player.likedIds.value"
        @play="handlePlayDownloaded"
        @like="handleLike"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useDownloads } from '../composables/useDownloads'
import { usePlayer } from '../composables/usePlayer'
import { getLocalTracks } from '../services/api'
import TrackList from '../components/TrackList.vue'
import type { Track } from '../services/api'

const downloads = useDownloads()
const player = usePlayer()
const localTracks = ref<Track[]>([])

onMounted(async () => {
  try {
    const data = await getLocalTracks()
    localTracks.value = data.tracks
  } catch {
    localTracks.value = []
  }
})

function handlePlayLocal(track: Track, index: number) {
  // Для локальных треков URL строится на лету
  player.setQueue(localTracks.value, index)
}

function handlePlayDownloaded(track: Track, index: number) {
  player.setQueue(downloads.downloadedTracks.value, index)
}

function handleLike(track: Track) {
  player.toggleTrackLike(track)
}

async function handleClearAll() {
  if (confirm('Удалить все скачанные треки?')) {
    await downloads.clearAll()
  }
}
</script>

<style scoped>
.downloaded-view {
  padding: var(--space-lg);
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--fg-muted);
  margin-bottom: var(--space-xl);
}

.section {
  margin-bottom: var(--space-xl);
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: 4px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
  color: var(--fg-primary);
}

.count-badge {
  font-size: 11px;
  font-weight: 600;
  color: var(--accent);
  background: var(--accent-glow);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.section-desc {
  font-size: 12px;
  color: var(--fg-muted);
  margin-bottom: var(--space-md);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--fg-muted);
  text-align: center;
}

.empty-state p {
  font-size: 16px;
  margin-top: 16px;
}

.empty-hint {
  font-size: 13px !important;
  color: var(--fg-muted);
  margin-top: 8px;
}

.downloaded-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.clear-btn {
  font-size: 13px;
  color: var(--pink);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}

.clear-btn:hover {
  background: rgba(253, 121, 168, 0.1);
}
</style>
