<template>
  <!-- Desktop Player (always compact at bottom) -->
  <div v-if="currentTrack" class="desktop-player">
    <div class="progress-line" @click="handleSeek">
      <div class="progress-fill" :style="{ width: progress + '%' }"></div>
    </div>
    <div class="player-content">
      <!-- Left: Track info + visualizer -->
      <div class="player-left">
        <div class="player-cover" @click="toggleVisualizer">
          <img v-if="currentTrack.cover_url && !showVisualizer" :src="currentTrack.cover_url" :alt="currentTrack.title" />
          <canvas v-show="showVisualizer" ref="desktopVisualizerCanvas" class="visualizer-canvas-cover"></canvas>
          <div v-if="!currentTrack.cover_url && !showVisualizer" class="cover-placeholder">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          </div>
        </div>
        <div class="player-info">
          <div class="player-title">{{ currentTrack.title }}</div>
          <div class="player-artist">{{ currentTrack.artist }}</div>
        </div>
        <button class="ctrl-btn" :class="{ active: isCurrentLiked }" @click="likeCurrent">
          <svg width="18" height="18" viewBox="0 0 24 24" :fill="isCurrentLiked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        </button>
      </div>
      
      <!-- Center: Controls -->
      <div class="player-center">
        <button class="mode-btn" :class="{ active: shuffleMode }" @click="toggleShuffle" title="Перемешать">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
        </button>
        <button class="ctrl-btn" @click="prev">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
        </button>
        <button class="play-btn" @click="togglePlay">
          <svg v-if="!isPlaying" width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
          <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
        </button>
        <button class="ctrl-btn" @click="next">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
        </button>
        <button class="mode-btn" :class="{ active: repeatMode !== 'off' }" @click="toggleRepeat" title="Повтор">
          <svg v-if="repeatMode === 'one'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
          <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
          <span v-if="repeatMode === 'one'" class="repeat-one">1</span>
        </button>
      </div>
      
      <!-- Right: Progress, Volume, Download, Stop -->
      <div class="player-right">
        <span class="time">{{ formatTime(currentTime) }}</span>
        <div class="progress-track" @click="handleSeek">
          <div class="progress-fill-bar" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="time">{{ formatTime(duration) }}</span>
        <div class="volume-control">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11,5 6,9 2,9 2,15 6,15 11,19"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
          <input type="range" min="0" max="1" step="0.01" :value="volume" @input="setVolume(Number(($event.target as HTMLInputElement).value))" class="volume-slider" />
        </div>
        <!-- Download -->
        <button class="icon-btn" :class="{ active: isDownloaded }" @click="handleDownload" :title="downloading ? 'Загрузка...' : (isDownloaded ? 'Сохранено' : 'Скачать')" :disabled="downloading || isDownloaded">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        </button>
        <!-- Stop -->
        <button class="icon-btn stop-icon" @click="handleStop" title="Стоп">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
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
const downloading = ref(false)
const showVisualizer = ref(false)
const desktopVisualizerCanvas = ref<HTMLCanvasElement | null>(null)

const isDownloaded = computed(() => {
  return props.currentTrack ? downloads.isDownloaded(props.currentTrack.id) : false
})

function toggleVisualizer() {
  showVisualizer.value = !showVisualizer.value
  if (showVisualizer.value && props.isPlaying) {
    nextTick(() => {
      if (desktopVisualizerCanvas.value) {
        const audioEl = player.getAudioElement()
        if (audioEl) {
          desktopVisualizerCanvas.value.width = 48
          desktopVisualizerCanvas.value.height = 48
          visualizer.init(audioEl, desktopVisualizerCanvas.value)
        }
      }
    })
  } else {
    visualizer.stop()
  }
}

watch(() => props.isPlaying, (playing) => {
  if (showVisualizer.value && playing) {
    nextTick(() => {
      if (desktopVisualizerCanvas.value) {
        const audioEl = player.getAudioElement()
        if (audioEl) {
          desktopVisualizerCanvas.value.width = 48
          desktopVisualizerCanvas.value.height = 48
          visualizer.init(audioEl, desktopVisualizerCanvas.value)
        }
      }
    })
  } else if (!playing) {
    visualizer.stop()
  }
})

function handleSeek(e: MouseEvent) {
  const target = e.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const percent = ((e.clientX - rect.left) / rect.width) * 100
  props.seek(Math.max(0, Math.min(100, percent)))
}

function handleStop() {
  visualizer.stop()
  showVisualizer.value = false
  props.stop()
}

async function handleDownload() {
  if (!props.currentTrack || downloading.value || isDownloaded.value) return
  downloading.value = true
  try {
    await downloads.downloadTrack(props.currentTrack)
  } catch (e) {
    console.error('Download failed:', e)
  }
  downloading.value = false
}

onBeforeUnmount(() => {
  visualizer.cleanup()
})
</script>

<style scoped>
.desktop-player {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: var(--player-height); background: var(--bg-player);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border); z-index: 100;
}
.progress-line { height: 2px; background: var(--border); cursor: pointer; }
.progress-fill { height: 100%; background: var(--accent); transition: width 0.1s linear; }
.player-content {
  display: grid; grid-template-columns: 1fr auto 1fr;
  align-items: center; height: calc(var(--player-height) - 2px);
  padding: 0 var(--space-lg); gap: var(--space-lg);
}
.player-left { display: flex; align-items: center; gap: var(--space-md); min-width: 0; }
.player-cover {
  width: 48px; height: 48px; border-radius: var(--radius-sm);
  overflow: hidden; flex-shrink: 0; cursor: pointer;
  position: relative;
}
.player-cover:hover { opacity: 0.85; }
.player-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); color: var(--fg-muted); }
.visualizer-canvas-cover {
  width: 100%; height: 100%; display: block;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(244, 114, 182, 0.1));
}
.player-info { min-width: 0; }
.player-title { font-size: 14px; font-weight: 500; color: var(--fg-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.player-artist { font-size: 12px; color: var(--fg-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
.player-center { display: flex; align-items: center; gap: var(--space-sm); }
.mode-btn { position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: var(--radius-full); color: var(--fg-muted); transition: all var(--transition); }
.mode-btn:hover { color: var(--fg-primary); background: var(--bg-tertiary); }
.mode-btn.active { color: var(--accent); }
.repeat-one { position: absolute; bottom: 4px; right: 4px; font-size: 8px; font-weight: 700; }
.ctrl-btn { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: var(--radius-full); color: var(--fg-secondary); transition: all var(--transition); }
.ctrl-btn:hover { color: var(--fg-primary); background: var(--bg-tertiary); }
.ctrl-btn.active { color: var(--pink); }
.play-btn { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: var(--radius-full); background: var(--fg-primary); color: var(--bg-primary); transition: all var(--transition); }
.play-btn:hover { transform: scale(1.05); }
.player-right { display: flex; align-items: center; gap: var(--space-md); justify-content: flex-end; }
.time { font-size: 11px; color: var(--fg-muted); min-width: 40px; }
.time:last-of-type { text-align: right; }
.progress-track { width: 120px; height: 4px; background: var(--border); border-radius: 2px; cursor: pointer; }
.progress-fill-bar { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.1s linear; }
.volume-control { display: flex; align-items: center; gap: var(--space-sm); color: var(--fg-muted); }
.volume-slider { width: 80px; height: 4px; -webkit-appearance: none; appearance: none; background: var(--border); border-radius: 2px; outline: none; }
.volume-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; border-radius: 50%; background: var(--accent); cursor: pointer; }

.icon-btn {
  display: flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: var(--radius-full);
  color: var(--fg-muted); transition: all var(--transition);
}
.icon-btn:hover { color: var(--fg-primary); background: var(--bg-tertiary); }
.icon-btn.active { color: var(--teal); }
.icon-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.stop-icon:hover { color: var(--pink); }

@media (max-width: 767px) { .desktop-player { display: none; } }
</style>
