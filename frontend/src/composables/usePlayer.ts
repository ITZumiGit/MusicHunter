import { ref, computed } from 'vue'
import type { Track } from '../services/api'
import { toggleLike, getLikes } from '../services/api'
import { useDownloads } from './useDownloads'

const API_URL = import.meta.env.VITE_API_URL || 'https://musichunter.ru'
const downloads = useDownloads()

// ─── State ────────────────────────────────
const audio: { current: HTMLAudioElement | null } = { current: null }
const currentTrack = ref<Track | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const progress = computed(() => duration.value ? currentTime.value / duration.value : 0)
const queue = ref<Track[]>([])
const queueIndex = ref(0)
const shuffleMode = ref(false)
const repeatMode = ref<'off' | 'all' | 'one'>('off')

// CRITICAL: likedIds and tgUserId must ALWAYS be valid refs
const likedIds = ref<Set<string>>(new Set<string>())
const tgUserId = ref<number>(0)

const isCurrentLiked = computed(() => {
  if (!currentTrack.value) return false
  return likedIds.value instanceof Set && likedIds.value.has(currentTrack.value.id)
})

// ─── Audio init ───────────────────────────
function initAudio() {
  if (audio.current) return
  const a = new Audio()
  a.crossOrigin = 'anonymous'  // REQUIRED for Web Audio API (createMediaElementSource / visualizer)
  a.preload = 'auto'
  a.volume = volume.value
  
  a.addEventListener('timeupdate', () => { currentTime.value = a.currentTime })
  a.addEventListener('durationchange', () => { duration.value = a.duration })
  a.addEventListener('ended', () => {
    if (repeatMode.value === 'one') {
      a.currentTime = 0
      a.play().catch(() => {})
    } else {
      next()
    }
  })
  a.addEventListener('error', (e) => {
    console.error('[Player] Audio error:', a.error?.message || e)
    isPlaying.value = false
  })
  
  audio.current = a
}

function scheduleHistory(track: Track) {
  // Placeholder for history tracking
}

// ─── Playback ─────────────────────────────
async function play(track: Track) {
  console.log('[Player] play():', track?.title)
  initAudio()
  const a = audio.current!
  
  // Clean up previous state before starting new track
  a.pause()
  a.src = ''
  a.load() // Force reset of audio element
  
  currentTrack.value = track
  isPlaying.value = true

  let url: string | null = null

  if (downloads.isDownloaded(track.id)) {
    url = await downloads.getLocalUrl(track.id)
    console.log('[Player] Cached:', url)
  }
  if (!url && track.id.startsWith('local_')) {
    url = API_URL + '/local/' + track.id.slice(6)
  }
  if (!url) {
    url = track.url || (API_URL + '/stream/' + encodeURIComponent(track.id))
    track.url = url
    console.log('[Player] Stream:', url)
  }

  if (!url) {
    console.error('[Player] No URL!')
    isPlaying.value = false
    return
  }

  // Set new source
  a.src = url
  a.preload = 'auto'
  console.log('[Player] src =', url)

  // Remove any lingering error/canplay listeners
  const cleanupListeners = () => {
    a.removeEventListener('error', onError)
    a.removeEventListener('canplay', onCanPlay)
  }

  const onCanPlay = () => {
    cleanupListeners()
    a.play().then(() => {
      console.log('[Player] Playing after canplay')
      isPlaying.value = true
    }).catch(() => {
      // Retry once after short delay
      setTimeout(() => {
        a.play().then(() => {
          isPlaying.value = true
        }).catch(() => {
          console.error('[Player] Play failed after retry')
          isPlaying.value = false
        })
      }, 500)
    })
  }

  const onError = () => {
    cleanupListeners()
    console.warn('[Player] Load error, retrying once in 2s...')
    setTimeout(() => {
      a.src = url!
      a.play().then(() => {
        console.log('[Player] Retry succeeded')
        isPlaying.value = true
      }).catch((e) => {
        console.error('[Player] Retry failed:', e)
        isPlaying.value = false
      })
    }, 2000)
  }

  a.addEventListener('error', onError, { once: true })
  a.addEventListener('canplay', onCanPlay, { once: true })

  try {
    await a.play()
    console.log('[Player] Playing!')
    isPlaying.value = true
    cleanupListeners()
  } catch (e: any) {
    console.warn('[Player] Initial play() rejected, waiting for canplay:', e.message)
    // canplay listener will handle it
  }
  scheduleHistory(track)
}

function togglePlay() {
  if (!audio.current || !currentTrack.value) return
  if (isPlaying.value) {
    audio.current.pause()
    isPlaying.value = false
  } else {
    audio.current.play().then(() => { isPlaying.value = true }).catch(() => {})
  }
}

function seek(time: number) {
  if (audio.current && isFinite(time) && time >= 0) {
    audio.current.currentTime = time
  }
}

function setVolume(v: number) {
  volume.value = Math.max(0, Math.min(1, v))
  if (audio.current) audio.current.volume = volume.value
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
    if (audio.current) { audio.current.currentTime = 0; audio.current.play().catch(() => {}) }
    return
  }
  if (shuffleMode.value) {
    if (queue.value.length === 0) { isPlaying.value = false; return }
    const idx = Math.floor(Math.random() * queue.value.length)
    queueIndex.value = idx
    play(queue.value[idx])
    return
  }
  if (queueIndex.value < queue.value.length - 1) {
    queueIndex.value++
    play(queue.value[queueIndex.value])
  } else if (repeatMode.value === 'all' && queue.value.length > 0) {
    queueIndex.value = 0
    play(queue.value[0])
  } else {
    isPlaying.value = false
  }
}

function prev() {
  if (audio.current && audio.current.currentTime > 3) {
    audio.current.currentTime = 0
    return
  }
  if (queueIndex.value > 0) {
    queueIndex.value--
    play(queue.value[queueIndex.value])
  }
}

function stop() {
  if (audio.current) {
    audio.current.pause()
    audio.current.src = ''
  }
  currentTrack.value = null
  isPlaying.value = false
}

function toggleShuffle() { shuffleMode.value = !shuffleMode.value }
function toggleRepeat() {
  const modes: Array<'off' | 'all' | 'one'> = ['off', 'all', 'one']
  const idx = modes.indexOf(repeatMode.value)
  repeatMode.value = modes[(idx + 1) % modes.length]
}

function formatTime(seconds: number): string {
  if (!isFinite(seconds)) return '0:00'
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

// ─── Likes ────────────────────────────────
async function loadLikes(tgId: number) {
  console.log('[Player] loadLikes called, tgId:', tgId)
  // SAFETY: tgId must be a valid number
  if (typeof tgId !== 'number' || tgId <= 0) {
    console.error('[Player] loadLikes: invalid tgId:', tgId, typeof tgId)
    tgId = 12345
  }
  tgUserId.value = tgId
  
  // Ensure likedIds is always a valid Set before fetching
  if (!(likedIds.value instanceof Set)) {
    likedIds.value = new Set<string>()
  }
  
  try {
    const result = await getLikes(tgId)
    console.log('[Player] getLikes returned:', result.count, 'tracks')
    const ids = new Set<string>()
    if (result.tracks && Array.isArray(result.tracks)) {
      for (const t of result.tracks) {
        if (t.track_id) ids.add(t.track_id)
      }
    }
    likedIds.value = ids
    console.log('[Player] likedIds set to', likedIds.value.size, 'items')
  } catch (e) {
    console.error('[Player] loadLikes error:', e)
    // Keep existing Set, don't set to undefined
    if (!(likedIds.value instanceof Set)) {
      likedIds.value = new Set<string>()
    }
  }
}

function likeCurrent() {
  if (currentTrack.value) toggleTrackLike(currentTrack.value)
}

function isLiked(id: string): boolean {
  return likedIds.value instanceof Set && likedIds.value.has(id)
}

async function toggleTrackLike(track: Track) {
  console.log('[Player] toggleTrackLike:', track.title, '| tgUserId:', tgUserId.value)
  
  // Ensure tgUserId is valid
  if (!tgUserId.value || typeof tgUserId.value !== 'number' || tgUserId.value <= 0) {
    console.warn('[Player] Invalid tgUserId, initializing with 12345')
    await loadLikes(12345)
  }
  
  // Ensure likedIds is always a valid Set
  if (!(likedIds.value instanceof Set)) {
    likedIds.value = new Set<string>()
  }
  
  try {
    console.log('[Player] Calling toggleLike API...')
    const result = await toggleLike(tgUserId.value, track)
    console.log('[Player] API result:', result)
    
    // Reassign entire Set for Vue reactivity
    const newSet = new Set(likedIds.value)
    if (result.action === 'liked') {
      newSet.add(track.id)
    } else {
      newSet.delete(track.id)
    }
    likedIds.value = newSet
    console.log('[Player] likedIds now:', likedIds.value.size, 'items')
  } catch (e) {
    console.error('[Player] toggleTrackLike error:', e)
  }
}

// ─── Visualizer ───────────────────────────
function getAudioElement(): HTMLAudioElement | null {
  return audio.current
}

// ─── Export ───────────────────────────────
export function usePlayer() {
  return {
    currentTrack, isPlaying, currentTime, duration, volume, progress,
    queue, queueIndex, shuffleMode, repeatMode,
    likedIds, tgUserId, isCurrentLiked,
    play, stop, togglePlay, seek, setVolume, setQueue,
    next, prev, toggleShuffle, toggleRepeat, formatTime,
    loadLikes, likeCurrent, isLiked, toggleTrackLike,
    getAudioElement,
  }
}
