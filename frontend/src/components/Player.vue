<template>
  <!-- Mobile Player (expands from bottom) -->
  <div v-if="currentTrack" class="player-wrapper" :class="{ expanded }">
    <!-- Progress bar (top thin line) -->
    <div class="progress-line" @click="handleSeek">
      <div class="progress-fill" :style="{ width: progress + '%' }"></div>
    </div>
    
    <!-- Mini player (always visible) -->
    <div class="mini-player" @click="expanded = !expanded">
      <div class="mini-cover">
        <img v-if="currentTrack.cover_url" :src="currentTrack.cover_url" :alt="currentTrack.title" />
        <div v-else class="cover-placeholder">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
          </svg>
        </div>
      </div>
      <div class="mini-info">
        <div class="mini-title">{{ currentTrack.title }}</div>
        <div class="mini-artist">{{ currentTrack.artist }}</div>
      </div>
      <div class="mini-controls">
        <button class="ctrl-btn" :class="{ active: isCurrentLiked }" @click.stop="likeCurrent">
          <svg width="20" height="20" viewBox="0 0 24 24" :fill="isCurrentLiked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
        </button>
        <button class="ctrl-btn" @click.stop="prev">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
        </button>
        <button class="ctrl-btn play-btn" @click.stop="togglePlay">
          <svg v-if="!isPlaying" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
        </button>
        <button class="ctrl-btn" @click.stop="next">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
        </button>
        <button class="ctrl-btn close-btn" @click.stop="handleStop" title="Закрыть">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
    
    <!-- Full player (expanded) -->
    <Transition name="slide-up">
      <div v-if="expanded" class="full-player">
        <button class="close-btn-top" @click="expanded = false">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="full-cover">
          <img v-if="currentTrack.cover_url" :src="currentTrack.cover_url" :alt="currentTrack.title" />
          <div v-else class="cover-placeholder-lg">
            <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
          </div>
        </div>
        <div class="full-info">
          <div class="full-title">{{ currentTrack.title }}</div>
          <div class="full-artist">{{ currentTrack.artist }}</div>
        </div>
        <div class="full-progress">
          <span class="time">{{ formatTime(currentTime) }}</span>
          <div class="progress-track" @click="handleSeek">
            <div class="progress-thumb" :style="{ width: progress + '%' }"></div>
          </div>
          <span class="time">{{ formatTime(duration) }}</span>
        </div>
        <div class="full-controls">
          <button class="mode-btn" :class="{ active: shuffleMode }" @click="toggleShuffle">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 3 21 3 21 8"/><line x1="4" y1="20" x2="21" y2="3"/><polyline points="21 16 21 21 16 21"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="4" y1="4" x2="9" y2="9"/></svg>
          </button>
          <button class="ctrl-btn-lg" @click="prev">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/></svg>
          </button>
          <button class="play-btn-lg" @click="togglePlay">
            <svg v-if="!isPlaying" width="36" height="36" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg>
            <svg v-else width="36" height="36" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
          </button>
          <button class="ctrl-btn-lg" @click="next">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/></svg>
          </button>
          <button class="mode-btn" :class="{ active: repeatMode !== 'off' }" @click="toggleRepeat">
            <svg v-if="repeatMode === 'one'" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/><text x="12" y="14" font-size="8" fill="currentColor" text-anchor="middle">1</text></svg>
            <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
          </button>
        </div>
        <div class="full-bottom-actions">
          <button class="action-btn" @click="handleDownload" :class="{ loading: downloading }">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span>{{ downloading ? 'Загрузка...' : (isDownloaded ? 'Сохранено' : 'Скачать') }}</span>
          </button>
          <button class="action-btn stop-action" @click="handleStop">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="6" width="12" height="12" rx="1"/></svg>
            <span>Стоп</span>
          </button>
        </div>
        <div class="volume-row">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11,5 6,9 2,9 2,15 6,15 11,19"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
          <input type="range" min="0" max="1" step="0.01" :value="volume" @input="setVolume(Number(($event.target as HTMLInputElement).value))" class="volume-slider" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDownloads } from '../composables/useDownloads'

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
const expanded = ref(false)
const downloading = ref(false)

const isDownloaded = computed(() => {
  return props.currentTrack ? downloads.isDownloaded(props.currentTrack.id) : false
})

function handleSeek(e: MouseEvent) {
  const target = e.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  const percent = ((e.clientX - rect.left) / rect.width) * 100
  props.seek(Math.max(0, Math.min(100, percent)))
}

function handleStop() {
  expanded.value = false
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
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--bg-player);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border);
}
.progress-line { height: 2px; background: var(--border); cursor: pointer; }
.progress-fill { height: 100%; background: var(--accent); transition: width 0.1s linear; }
.mini-player {
  display: flex; align-items: center; gap: var(--space-md);
  padding: var(--space-sm) var(--space-md); height: var(--player-height-mobile); cursor: pointer;
}
.mini-cover { width: 44px; height: 44px; border-radius: var(--radius-sm); overflow: hidden; flex-shrink: 0; }
.mini-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); color: var(--fg-muted); }
.mini-info { flex: 1; min-width: 0; }
.mini-title { font-size: 14px; font-weight: 500; color: var(--fg-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mini-artist { font-size: 12px; color: var(--fg-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px; }
.mini-controls { display: flex; align-items: center; gap: 2px; }
.ctrl-btn {
  display: flex; align-items: center; justify-content: center;
  width: 40px; height: 40px; border-radius: var(--radius-full);
  color: var(--fg-secondary); transition: all var(--transition);
}
.ctrl-btn:hover { color: var(--fg-primary); background: var(--bg-tertiary); }
.ctrl-btn.active { color: var(--accent); }
.play-btn { color: var(--accent); }
.close-btn { color: var(--fg-muted); }
.close-btn:hover { color: var(--pink); background: rgba(253, 121, 168, 0.1); }

.full-player { padding: var(--space-xl); padding-bottom: calc(var(--nav-height) + var(--space-xl)); }
.close-btn-top {
  display: flex; align-items: center; justify-content: center;
  width: 44px; height: 44px; margin: 0 auto var(--space-lg);
  border-radius: var(--radius-full); color: var(--fg-secondary); transition: all var(--transition);
}
.close-btn-top:hover { background: var(--bg-tertiary); color: var(--fg-primary); }
.full-cover { width: 280px; height: 280px; margin: 0 auto var(--space-xl); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-lg); }
.full-cover img { width: 100%; height: 100%; object-fit: cover; }
.cover-placeholder-lg { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: var(--bg-tertiary); color: var(--fg-muted); }
.full-info { text-align: center; margin-bottom: var(--space-xl); }
.full-title { font-size: 18px; font-weight: 600; color: var(--fg-primary); margin-bottom: 4px; }
.full-artist { font-size: 14px; color: var(--fg-secondary); }
.full-progress { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-xl); }
.time { font-size: 12px; color: var(--fg-muted); min-width: 40px; }
.time:last-child { text-align: right; }
.progress-track { flex: 1; height: 4px; background: var(--border); border-radius: 2px; cursor: pointer; position: relative; }
.progress-thumb { height: 100%; background: var(--accent); border-radius: 2px; position: relative; }
.progress-thumb::after { content: ''; position: absolute; right: -6px; top: 50%; transform: translateY(-50%); width: 12px; height: 12px; background: var(--accent); border-radius: 50%; opacity: 0; transition: opacity var(--transition); }
.progress-track:hover .progress-thumb::after { opacity: 1; }
.full-controls { display: flex; align-items: center; justify-content: center; gap: var(--space-lg); margin-bottom: var(--space-lg); }
.mode-btn { display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: var(--radius-full); color: var(--fg-secondary); transition: all var(--transition); }
.mode-btn:hover { color: var(--fg-primary); background: var(--bg-tertiary); }
.mode-btn.active { color: var(--accent); }
.ctrl-btn-lg { display: flex; align-items: center; justify-content: center; width: 52px; height: 52px; border-radius: var(--radius-full); color: var(--fg-primary); transition: all var(--transition); }
.ctrl-btn-lg:hover { background: var(--bg-tertiary); }
.play-btn-lg { display: flex; align-items: center; justify-content: center; width: 64px; height: 64px; border-radius: var(--radius-full); background: var(--accent); color: white; transition: all var(--transition); }
.play-btn-lg:hover { background: var(--accent-hover); transform: scale(1.05); }

.full-bottom-actions { display: flex; justify-content: center; gap: var(--space-lg); margin-bottom: var(--space-lg); }
.action-btn {
  display: flex; align-items: center; gap: 6px; padding: 8px 16px;
  border-radius: var(--radius-full); color: var(--fg-secondary);
  background: var(--bg-tertiary); font-size: 13px; font-weight: 500;
  transition: all var(--transition);
}
.action-btn:hover { color: var(--fg-primary); background: var(--border-light); }
.action-btn.loading { opacity: 0.6; pointer-events: none; }
.stop-action:hover { color: var(--pink); }

.volume-row { display: flex; align-items: center; gap: var(--space-md); padding: 0 var(--space-xl); color: var(--fg-muted); }
.volume-slider { flex: 1; height: 4px; -webkit-appearance: none; appearance: none; background: var(--border); border-radius: 2px; outline: none; }
.volume-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 14px; height: 14px; border-radius: 50%; background: var(--accent); cursor: pointer; }

.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.3s ease, opacity 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); opacity: 0; }

@media (min-width: 768px) { .player-wrapper { display: none; } }
</style>
