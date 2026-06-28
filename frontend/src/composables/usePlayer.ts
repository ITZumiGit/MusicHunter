/**
 * MusicHunter Player v4 — Singleton pattern
 * Все компоненты используют один и тот же экземпляр плеера
 */
import { ref, computed } from 'vue'
import type { Track } from '../services/api'
import { addToHistory, toggleLike, getLikes } from '../services/api'
import { useDownloads } from './useDownloads'

const API_URL = import.meta.env.VITE_API_URL || 'https://musichunter.ru'

export type RepeatMode = 'off' | 'all' | 'one'

// ─── Singleton state (module-level) ─────────
const currentTrack = ref<Track | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(0.8)

const queue = ref<Track[]>([])
const queueIndex = ref(-1)

const shuffleMode = ref(false)
const repeatMode = ref<RepeatMode>('off')

const likedIds = ref<Set<string>>(new Set())
const tgUserId = ref<number>(0)

let audio: HTMLAudioElement | null = null
let historyTimer: ReturnType<typeof setTimeout> | null = null
const downloads = useDownloads()

// Computed
const progress = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

const isCurrentLiked = computed(() => {
  return currentTrack.value ? likedIds.value.has(currentTrack.value.id) : false
})

// ─── Internal ───────────────────────────────
function initAudio() {
  if (audio) return

  audio = new Audio()
  audio.volume = volume.value
  audio.preload = 'auto'

  audio.ontimeupdate = () => {
    currentTime.value = audio?.currentTime ?? 0
  }

  audio.ondurationchange = () => {
    duration.value = audio?.duration ?? 0
  }

  audio.onended = () => {
    handleTrackEnd()
  }

  audio.onerror = () => {
    isPlaying.value = false
  }
}

function scheduleHistory(track: Track) {
  if (historyTimer) clearTimeout(historyTimer)
  historyTimer = setTimeout(() => {
    if (tgUserId.value && currentTrack.value?.id === track.id) {
      addToHistory(tgUserId.value, track).catch(() => {})
    }
  }, 10000)
}

function handleTrackEnd() {
  next()
}

// ─── Public API ─────────────────────────────
async function play(track: Track) {
  initAudio()

  currentTrack.value = track
  isPlaying.value = true

  // 1. Проверяем локальный кэш (IndexedDB) — оффлайн воспроизведение
  let url: string | null = null
  if (downloads.isDownloaded(track.id)) {
    url = await downloads.getLocalUrl(track.id)
  }

  // 2. Локальные файлы бота (local_*) — прямой URL
  if (!url && track.id.startsWith('local_')) {
    const fileId = track.id.slice(6)
    url = `${API_URL}/local/${fileId}`
  }

  // 3. Если нет локально — стрим через бэкенд (прокси)
  if (!url) {
    url = track.url
    if (!url) {
      url = `${API_URL}/stream/${encodeURIComponent(track.id)}`
      track.url = url
    }
  }

  if (url && audio) {
    audio.src = url
    try {
      await audio.play()
      isPlaying.value = true
    } catch {
      isPlaying.value = false
    }
  } else {
    isPlaying.value = false
  }

  scheduleHistory(track)
}

function togglePlay() {
  if (!audio || !currentTrack.value) return

  if (isPlaying.value) {
    audio.pause()
    isPlaying.value = false
  } else {
    audio.play().then(() => {
      isPlaying.value = true
    }).catch(() => {
      isPlaying.value = false
    })
  }
}

function seek(percent: number) {
  if (!audio) return
  // Если duration неизвестен (Infinity/NaN для стримов) — пробуем по проценту от 0
  const dur = (duration.value && isFinite(duration.value)) ? duration.value : 0
  if (dur === 0) {
    // Для стримов без известной длительности — пытаемся установить напрямую
    // Браузер сам обработает, если может
    const estimatedTime = (percent / 100) * 300 // предполагаем ~5мин
    if (audio.duration && isFinite(audio.duration)) {
      audio.currentTime = (percent / 100) * audio.duration
    } else {
      // Последний шанс — ставим напрямую и надеемся на Range support
      try { audio.currentTime = estimatedTime } catch { /* ignore */ }
    }
    return
  }
  const time = (percent / 100) * dur
  if (isFinite(time) && time >= 0) {
    audio.currentTime = time
  }
}

function setVolume(v: number) {
  volume.value = Math.max(0, Math.min(1, v))
  if (audio) audio.volume = volume.value
}

function setQueue(tracks: Track[], startIndex = 0) {
  queue.value = [...tracks]
  queueIndex.value = startIndex
  if (tracks[startIndex]) {
    play(tracks[startIndex])
  }
}

function next() {
  if (repeatMode.value === 'one') {
    if (audio) {
      audio.currentTime = 0
      audio.play().catch(() => {})
    }
    return
  }

  if (shuffleMode.value) {
    if (queue.value.length === 0) {
      isPlaying.value = false
      return
    }
    const idx = Math.floor(Math.random() * queue.value.length)
    queueIndex.value = idx
    play(queue.value[idx])
    return
  }

  if (queueIndex.value < queue.value.length - 1) {
    queueIndex.value++
    play(queue.value[queueIndex.value])
  } else if (repeatMode.value === 'all') {
    queueIndex.value = 0
    play(queue.value[0])
  } else {
    isPlaying.value = false
  }
}

function prev() {
  // Если прошло больше 3 секунд — перезапуск трека
  if (audio && currentTime.value > 3) {
    audio.currentTime = 0
    return
  }

  if (queueIndex.value > 0) {
    queueIndex.value--
    play(queue.value[queueIndex.value])
  }
}

function stop() {
  if (audio) {
    audio.pause()
    audio.src = ''
  }
  currentTrack.value = null
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
  if (historyTimer) {
    clearTimeout(historyTimer)
    historyTimer = null
  }
}

function toggleShuffle() {
  shuffleMode.value = !shuffleMode.value
}

function toggleRepeat() {
  const modes: RepeatMode[] = ['off', 'all', 'one']
  const currentIdx = modes.indexOf(repeatMode.value)
  repeatMode.value = modes[(currentIdx + 1) % modes.length]
}

function formatTime(s: number): string {
  if (!s || isNaN(s) || !isFinite(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

// Likes
async function loadLikes(tgId: number) {
  tgUserId.value = tgId
  try {
    const data = await getLikes(tgId)
    likedIds.value = new Set(data.tracks.map(t => t.id))
  } catch {
    // Silent fail
  }
}

async function likeCurrent() {
  if (!currentTrack.value || !tgUserId.value) return
  try {
    const result = await toggleLike(tgUserId.value, currentTrack.value)
    if (result.action === 'liked') {
      likedIds.value.add(currentTrack.value.id)
    } else {
      likedIds.value.delete(currentTrack.value.id)
    }
  } catch {
    // Silent fail
  }
}

function isLiked(trackId: string): boolean {
  return likedIds.value.has(trackId)
}

async function toggleTrackLike(track: Track) {
  if (!tgUserId.value) return
  try {
    const result = await toggleLike(tgUserId.value, track)
    if (result.action === 'liked') {
      likedIds.value.add(track.id)
    } else {
      likedIds.value.delete(track.id)
    }
  } catch {
    // Silent fail
  }
}

// Get audio element reference for visualizer
function getAudioElement(): HTMLAudioElement | null {
  return audio
}

// ─── Export singleton ───────────────────────
export function usePlayer() {
  return {
    // State
    currentTrack,
    isPlaying,
    currentTime,
    duration,
    volume,
    progress,
    queue,
    queueIndex,
    shuffleMode,
    repeatMode,
    likedIds,
    tgUserId,
    isCurrentLiked,

    // Actions
    play,
    stop,
    togglePlay,
    seek,
    setVolume,
    setQueue,
    next,
    prev,
    toggleShuffle,
    toggleRepeat,
    formatTime,

    // Likes
    loadLikes,
    likeCurrent,
    isLiked,
    toggleTrackLike,

    // Visualizer
    getAudioElement,
  }
}
