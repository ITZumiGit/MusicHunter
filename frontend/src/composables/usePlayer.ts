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
const currentTrack = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(0.8)
const queue = ref([])
const queueIndex = ref(-1)
const shuffleMode = ref(false)
const repeatMode = ref('off')
const likedIds = ref>(new Set())
const tgUserId = ref(0)

let audio: HTMLAudioElement | null = null
let historyTimer: ReturnType | null = null

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
  audio.crossOrigin = 'anonymous' // ВАЖНО: для CORS
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
  
  audio.onerror = (e) => {
    console.error('[Player] Audio error:', e, 'Error code:', audio?.error?.code, 'Message:', audio?.error?.message)
    isPlaying.value = false
  }
  
  audio.onstalled = () => {
    console.warn('[Player] Audio stalled')
  }
  
  audio.onwaiting = () => {
    console.warn('[Player] Audio waiting')
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
    console.log('[Player] play() called for:', track?.title)
    initAudio()
    currentTrack.value = track
    isPlaying.value = true

    let url: string | null = null
    if (downloads.isDownloaded(track.id)) {
        url = await downloads.getLocalUrl(track.id)
        console.log('[Player] Using cached:', url)
    }
    if (!url && track.id.startsWith('local_')) {
        const fileId = track.id.slice(6)
        url = API_URL + '/local/' + fileId
        console.log('[Player] Using local file:', url)
    }
    if (!url) {
        url = track.url
        if (!url) {
            url = API_URL + '/stream/' + encodeURIComponent(track.id)
            track.url = url
        }
        console.log('[Player] Using stream:', url)
    }

    if (url && audio) {
        audio.src = url
        console.log('[Player] Set audio.src:', url)
        try {
            await audio.play()
            console.log('[Player] Playing immediately!')
            isPlaying.value = true
        } catch (e: any) {
            console.warn('[Player] Immediate play failed, retrying on canplay:', e.message)
            const onReady = () => {
                audio!.play()
                    .then(() => { console.log('[Player] Playing after canplay'); isPlaying.value = true })
                    .catch(err => { console.error('[Player] play error:', err); isPlaying.value = false })
                audio!.removeEventListener('canplay', onReady)
            }
            audio!.addEventListener('canplay', onReady)
        }
    } else {
        console.error('[Player] No URL or audio element')
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
    }).catch((err) => {
      console.error('[Player] togglePlay failed:', err)
      isPlaying.value = false
    })
  }
}

function seek(percent: number) {
  if (!audio) return
  
  const dur = duration.value
  const isStream = !isFinite(dur) || dur === 0
  
  if (isStream) {
    // Для стримов — пробуем установить currentTime напрямую
    // Браузер использует Range requests для перехода к нужной позиции
    const estimatedDuration = 300 // fallback 5 минут
    const targetTime = (percent / 100) * estimatedDuration
    try {
      audio.currentTime = targetTime
      currentTime.value = targetTime
    } catch (e) {
      console.warn('[seek] Failed to set time for stream:', e)
    }
  } else {
    // Для обычных файлов с известной длительностью
    const time = (percent / 100) * dur
    if (isFinite(time) && time >= 0) {
      audio.currentTime = time
    }
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
  console.log('[Player] loadLikes called, tgId:', tgId)
  tgUserId.value = tgId
  console.log('[Player] tgUserId set to:', tgUserId.value)
  try {
    const data = await getLikes(tgId)
    likedIds.value = new Set(data.tracks.map((t: Track) => t.id))
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
    console.log('[Player] toggleTrackLike called for:', track.title, '| tgUserId:', tgUserId.value)
    if (!tgUserId.value) {
        console.warn('[Player] tgUserId not set, initializing with 12345...')
        await loadLikes(12345)
        if (!tgUserId.value) {
            console.error('[Player] Still no tgUserId!')
            return
        }
    }
    if (!likedIds.value) {
        console.warn('[Player] likedIds is falsy, reinitializing...')
        likedIds.value = new Set<string>()
    }
    try {
        console.log('[Player] Calling toggleLike API for:', track.id)
        const result = await toggleLike(tgUserId.value, track)
        console.log('[Player] toggleLike API result:', result)
        // Reassign entire Set for Vue reactivity
        const newSet = new Set(likedIds.value)
        if (result.action === 'liked') {
            newSet.add(track.id)
        } else {
            newSet.delete(track.id)
        }
        likedIds.value = newSet
        console.log('[Player] likedIds now has', likedIds.value.size, 'items')
    } catch (e) {
        console.error('[Player] toggleTrackLike error:', e)
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
