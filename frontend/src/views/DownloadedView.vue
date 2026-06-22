<template>
  <div class="downloaded-view">
    <h1 class="page-title">Библиотека</h1>
    <p class="page-subtitle">Скачанные треки и музыка бота</p>

    <!-- Bot music section — featured card -->
    <div v-if="localTracks.length" class="bot-music-card" @click="scrollToBot">
      <div class="bot-card-bg"></div>
      <div class="bot-card-content">
        <div class="bot-card-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
            <line x1="12" y1="19" x2="12" y2="23"/>
            <line x1="8" y1="23" x2="16" y2="23"/>
          </svg>
        </div>
        <div class="bot-card-info">
          <div class="bot-card-title">Музыка бота</div>
          <div class="bot-card-desc">{{ localTracks.length }} треков • Всегда доступны</div>
        </div>
        <div class="bot-card-badge">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
      </div>
    </div>

    <!-- Bot music list -->
    <div v-if="localTracks.length" class="section" ref="botSection">
      <TrackList
        :tracks="localTracks"
        :current-track="player.currentTrack.value"
        :is-playing="player.isPlaying.value"
        :liked-ids="player.likedIds.value"
        @play="handlePlayLocal"
        @like="handleLike"
      />
    </div>

    <!-- Divider -->
    <div v-if="localTracks.length && downloads.count.value > 0" class="section-divider"></div>

    <!-- Downloaded section -->
    <div class="section">
      <div class="section-header" v-if="downloads.count.value > 0">
        <div class="section-title">
          <div class="section-icon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
          </div>
          Скачанные
        </div>
        <div class="section-meta">
          <span class="count-pill">{{ downloads.count.value }}</span>
          <button class="clear-btn" @click="handleClearAll">Очистить</button>
        </div>
      </div>

      <div v-if="downloads.count.value === 0 && !localTracks.length" class="empty-state">
        <div class="empty-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </div>
        <p class="empty-title">Пока пусто</p>
        <p class="empty-hint">Нажмите ⬇ в плеере, чтобы скачать</p>
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
const botSection = ref<HTMLElement | null>(null)

onMounted(async () => {
  try {
    const data = await getLocalTracks()
    localTracks.value = data.tracks
  } catch {
    localTracks.value = []
  }
})

function handlePlayLocal(track: Track, index: number) {
  player.setQueue(localTracks.value, index)
}

function handlePlayDownloaded(track: Track, index: number) {
  player.setQueue(downloads.downloadedTracks.value, index)
}

function handleLike(track: Track) {
  player.toggleTrackLike(track)
}

function scrollToBot() {
  botSection.value?.scrollIntoView({ behavior: 'smooth' })
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
  padding-bottom: var(--space-xl);
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--fg-primary);
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--fg-muted);
  margin-bottom: var(--space-xl);
}

/* ─── Bot Music Card ─── */
.bot-music-card {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: var(--space-lg);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.bot-card-bg {
  position: absolute;
  inset: 0;
  background: var(--accent-gradient);
  opacity: 0.15;
  transition: opacity 0.3s;
}

.bot-music-card:hover .bot-card-bg,
.bot-music-card:active .bot-card-bg {
  opacity: 0.25;
}

.bot-card-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-lg);
}

.bot-card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: var(--radius);
  background: var(--accent-gradient);
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3);
}

.bot-card-info {
  flex: 1;
  min-width: 0;
}

.bot-card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--fg-primary);
}

.bot-card-desc {
  font-size: 12px;
  color: var(--fg-secondary);
  margin-top: 2px;
}

.bot-card-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--bg-card);
  color: var(--fg-muted);
  border: 1px solid var(--border-light);
}

/* ─── Sections ─── */
.section {
  margin-bottom: var(--space-lg);
}

.section-divider {
  height: 1px;
  background: var(--border);
  margin: var(--space-xl) 0;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--fg-primary);
}

.section-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient-subtle);
  color: var(--accent);
}

.section-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.count-pill {
  font-size: 11px;
  font-weight: 700;
  color: var(--accent);
  background: var(--accent-glow);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

.clear-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--pink);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  transition: all var(--transition);
}

.clear-btn:hover {
  background: rgba(244, 114, 182, 0.1);
}

/* ─── Empty state ─── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 20px;
  text-align: center;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  border-radius: var(--radius-xl);
  background: var(--accent-gradient-subtle);
  color: var(--accent);
  margin-bottom: var(--space-lg);
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 13px;
  color: var(--fg-muted);
}
</style>
