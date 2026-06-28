<template>
  <!-- Mobile Player -->
  <div v-if="currentTrack" class="player-wrapper" :class="{ expanded }">
    <!-- Mini player — sits above the nav bar -->
    <div class="mini-player" @click="expanded = !expanded">
      <!-- Gradient progress line -->
      <div class="progress-line" @click.stop="handleSeek">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      
      <div class="mini-body">
        <div class="mini-cover">
          <img v-if="currentTrack.cover_url" :src="currentTrack.cover_url" :alt="currentTrack.title" />
          <div v-else class="cover-placeholder">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
            </svg>
          </div>
          <!-- Playing animation -->
          <div v-if="isPlaying" class="playing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
        <div class="mini-info">
          <div class="mini-title">{{ currentTrack.title }}</div>
          <div class="mini-artist">{{ currentTrack.artist }}</div>
        </div>
        <div class="mini-controls">
          <button class="ctrl-btn" @click.stop="togglePlay">
            <svg v-if="!isPlaying" width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
            <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>
          </button>
          <button class="ctrl-btn next-btn" @click.stop="next">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Full player (expanded overlay) -->
    <Transition name="expand">
      <div v-if="expanded" class="full-player">
        <!-- BG gradient from cover -->
        <div class="full-bg-gradient"></div>
        
        <div class="full-content">
          <!-- Header -->
          <div class="full-header">
            <button class="chevron-btn" @click="expanded = false">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <div class="full-header-label">Сейчас играет</div>
            <button class="close-btn" @click="handleStop">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
          
          <!-- Visualizer OR Cover art -->
          <div class="full-cover-wrap">
            <!-- Visualizer canvas (shown when playing) -->
            <div v-if="isPlaying" class="visualizer-container">
              <canvas ref="visualizerCanvas" class="visualizer-canvas"></canvas>
            </div>
            <!-- Cover art (shown when paused) -->
            <div v-else class="full-cover">
              <img v-if="currentTrack.cover_url" :src="currentTrack.cover_url" :alt="currentTrack.title" />
              <div v-else class="cover-placeholder-lg">
                <svg width="72" height="72" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
              </div>
            </div>
          </div>
          
          <!-- Track info -->
          <div class="full-info">
            <div class="full-title">{{ currentTrack.title }}</div>
            <div class="full-artist">{{ currentTrack.artist }}</div>
          </div>
          
          <!-- Progress -->
          <div class="full-progress">
            <div class="progress-bar-wrap" @click="handleSeek">
              <div class="progress-bar-bg">
                <div class="progress-bar-fill" :style="{ width: progress + '%' }"></div>
              </div>
            </div>
            <div class="progress-times">
              <span>{{ formatTime(currentTime) }}</span>
              <span>{{ formatTime(duration) }}</span>
            </div>
          </div>
          
          <!-- Main controls -->
          <div class="full-controls">
            <button class="mode-btn" :class="{ active: shuffleMode }" @click="toggleShuffle">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
            </button>
            <button class="ctrl-btn-lg" @click="prev">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
            </button>
            <button class="play-btn-lg" @click="togglePlay">
              <svg v-if="!isPlaying" width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
              <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>
            </button>
            <button class="ctrl-btn-lg" @click="next">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
            </button>
            <button class="mode-btn" :class="{ active: repeatMode !== 'off' }" @click="toggleRepeat">
              <svg v-if="repeatMode === 'one'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/><text x="12" y="14" font-size="8" fill="currentColor" text-anchor="middle">1</text></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
            </button>
          </div>
          
          <!-- Bottom actions -->
          <div class="full-bottom">
            <button class="action-chip" :class="{ liked: isCurrentLiked }" @click="likeCurrent">
              <svg width="18" height="18" viewBox="0 0 24 24" :fill="isCurrentLiked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
              <span>{{ isCurrentLiked ? 'В лайках' : 'Лайк' }}</span>
            </button>
            <button class="action-chip" @click="handleDownload" :class="{ loading: downloading, saved: isDownloaded }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              <span>{{ downloading ? 'Загрузка...' : (isDownloaded ? 'Сохранено' : 'Скачать') }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import { useDownloads } from '../composables/useDownloads'
import { useVisualizer } from '../composables/useVisualizer'
import { usePlayer } from '../composables/usePlayer'

const props = defineProps<{
  currentTrack: any
  isPlaying: boolean
  currentTime: number
  duration: number
  volume: number
  progress: number
  shuffleMode: boolean
  repeatMode: 'off' | 'all' | 'one'
  isCurrentLiked: boolean
  togglePlay: () => void
  next: () => void
  prev: () => void
  seek: (percent: number) => void
  setVolume: (v: number) => void
  likeCurrent: () => void
  toggleShuffle: () => void
  toggleRepeat: () => void
  formatTime: (s: number) => string
  stop: () => void
}>()

const downloads = useDownloads()
const player = usePlayer()
const visualizer = useVisualizer()
const expanded = ref(false)
const downloading = ref(false)
const visualizerCanvas = ref<HTMLCanvasElement | null>(null)

const isDownloaded = computed(() => {
  return props.currentTrack ? downloads.isDownloaded(props.currentTrack.id) : false
})

// Initialize visualizer when expanded and playing
watch([expanded, () => props.isPlaying], async ([isExpanded, isPlayingNow]) => {
  if (isExpanded && isPlayingNow) {
    await nextTick()
    if (visualizerCanvas.value) {
      const audioEl = player.getAudioElement()
      if (audioEl) {
        // Set canvas size
        const container = visualizerCanvas.value.parentElement
        if (container) {
          visualizerCanvas.value.width = container.clientWidth
          visualizerCanvas.value.height = container.clientHeight
        }
        visualizer.init(audioEl, visualizerCanvas.value)
      }
    }
  } else if (!isPlayingNow) {
    visualizer.stop()
  }
}, { immediate: true })

// Resize canvas on expand
watch(expanded, async (val) => {
  if (val) {
    await nextTick()
    if (visualizerCanvas.value) {
      const container = visualizerCanvas.value.parentElement
      if (container) {
        visualizerCanvas.value.width = container.clientWidth
        visualizerCanvas.value.height = container.clientHeight
      }
    }
  }
})

onBeforeUnmount(() => {
  visualizer.cleanup()
})

function handleSeek(e: MouseEvent) {
  const target = e.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const percent = ((e.clientX - rect.left) / rect.width) * 100
  props.seek(Math.max(0, Math.min(100, percent)))
}

function handleStop() {
  expanded.value = false
  visualizer.stop()
  props.stop()
}

async function handleDownload() {
  if (!props.currentTrack || downloading.value) return
  if (isDownloaded.value) return
  downloading.value = true
  try {
    await downloads.downloadTrack(props.currentTrack)
  } catch (e) {
    console.error('Download failed:', e)
  }
  downloading.value = false
}
</script>

<style scoped>
.player-wrapper {
  position: fixed;
  bottom: var(--nav-height);
  left: 0;
  right: 0;
  z-index: 95;
}

/* ─── Mini Player ─── */
.mini-player {
  background: var(--bg-glass);
  backdrop-filter: blur(24px) saturate(1.8);
  -webkit-backdrop-filter: blur(24px) saturate(1.8);
  border-top: 1px solid var(--border-glass);
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}

.progress-line {
  height: 2px;
  background: var(--bg-tertiary);
  cursor: pointer;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  transition: width 0.15s linear;
  position: relative;
}

.mini-body {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  height: var(--player-height-mobile);
}

.mini-cover {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.mini-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient-subtle);
  color: var(--accent);
}

/* Playing bars animation */
.playing-indicator {
  position: absolute;
  bottom: 3px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 12px;
}

.playing-indicator span {
  width: 3px;
  background: var(--accent);
  border-radius: 2px;
  animation: bars 0.8s ease-in-out infinite;
}

.playing-indicator span:nth-child(1) { height: 6px; animation-delay: 0s; }
.playing-indicator span:nth-child(2) { height: 10px; animation-delay: 0.2s; }
.playing-indicator span:nth-child(3) { height: 4px; animation-delay: 0.4s; }

@keyframes bars {
  0%, 100% { transform: scaleY(0.5); }
  50% { transform: scaleY(1.2); }
}

.mini-info {
  flex: 1;
  min-width: 0;
}

.mini-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--fg-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mini-artist {
  font-size: 12px;
  color: var(--fg-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.mini-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.ctrl-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  color: var(--fg-primary);
  transition: all var(--transition);
  -webkit-tap-highlight-color: transparent;
}

.ctrl-btn:active {
  transform: scale(0.9);
}

.next-btn {
  color: var(--fg-secondary);
}

/* ─── Full Player ─── */
.full-player {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: var(--bg-primary);
  overflow: hidden;
}

.full-bg-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 0%, var(--accent-glow) 0%, transparent 70%);
  opacity: 0.6;
  pointer-events: none;
}

.full-content {
  position: relative;
  z-index: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--space-lg) var(--space-xl);
  padding-bottom: calc(var(--nav-height) + var(--space-xl) + env(safe-area-inset-bottom, 0));
}

/* Header */
.full-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.chevron-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  color: var(--fg-secondary);
  transition: all var(--transition);
}

.chevron-btn:active { transform: scale(0.9); }

.full-header-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  color: var(--fg-muted);
  transition: all var(--transition);
}

.close-btn:active { transform: scale(0.9); }
.close-btn:hover { color: var(--pink); }

/* Visualizer / Cover */
.full-cover-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: var(--space-lg);
  flex: 1;
  min-height: 0;
}

.visualizer-container {
  width: min(280px, 70vw);
  height: min(280px, 70vw);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 80px var(--accent-glow);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(244, 114, 182, 0.05));
}

.visualizer-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.full-cover {
  width: min(280px, 70vw);
  height: min(280px, 70vw);
  border-radius: var(--radius-xl);
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 80px var(--accent-glow);
}

.full-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-lg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient-subtle);
  color: var(--fg-muted);
}

/* Info */
.full-info {
  text-align: center;
  margin-bottom: var(--space-lg);
}

.full-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.full-artist {
  font-size: 15px;
  color: var(--fg-secondary);
}

/* Progress */
.full-progress {
  margin-bottom: var(--space-lg);
}

.progress-bar-wrap {
  cursor: pointer;
  padding: 8px 0;
}

.progress-bar-bg {
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--accent-gradient);
  border-radius: 4px;
  transition: width 0.15s linear;
}

.progress-bar-wrap:hover .progress-bar-bg {
  height: 6px;
}

.progress-times {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--fg-muted);
  margin-top: 6px;
  font-variant-numeric: tabular-nums;
}

/* Controls */
.full-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  margin-bottom: var(--space-xl);
}

.mode-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  color: var(--fg-muted);
  transition: all var(--transition);
}

.mode-btn.active { color: var(--accent); }
.mode-btn:active { transform: scale(0.9); }

.ctrl-btn-lg {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: var(--radius-full);
  color: var(--fg-primary);
  transition: all var(--transition);
}

.ctrl-btn-lg:active { transform: scale(0.9); }

.play-btn-lg {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 68px;
  height: 68px;
  border-radius: var(--radius-full);
  background: var(--accent-gradient);
  color: white;
  box-shadow: 0 4px 24px rgba(139, 92, 246, 0.4);
  transition: all var(--transition);
}

.play-btn-lg:active {
  transform: scale(0.92);
}

.play-btn-lg:hover {
  box-shadow: 0 6px 32px rgba(139, 92, 246, 0.5);
}

/* Bottom actions */
.full-bottom {
  display: flex;
  justify-content: center;
  gap: var(--space-md);
}

.action-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: var(--radius-full);
  color: var(--fg-secondary);
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  font-size: 13px;
  font-weight: 600;
  transition: all var(--transition);
  backdrop-filter: blur(12px);
  -webkit-tap-highlight-color: transparent;
}

.action-chip:active {
  transform: scale(0.95);
}

.action-chip.liked {
  color: var(--pink);
  border-color: rgba(244, 114, 182, 0.2);
  background: rgba(244, 114, 182, 0.1);
}

.action-chip.saved {
  color: var(--teal);
  border-color: rgba(45, 212, 191, 0.2);
  background: rgba(45, 212, 191, 0.1);
}

.action-chip.loading {
  opacity: 0.5;
  pointer-events: none;
}

/* ─── Transitions ─── */
.expand-enter-active, .expand-leave-active {
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.25s ease;
}

.expand-enter-from, .expand-leave-to {
  transform: translateY(100%);
  opacity: 0;
}

@media (min-width: 768px) {
  .player-wrapper { display: none; }
}
</style>
