/**
 * MusicHunter Player v3 — full-featured audio player
 * Features: queue, shuffle, repeat, likes, history
 */
import { ref, computed, watch } from 'vue'
import type { Track } from '../services/api'
import { getStreamUrl, addToHistory, toggleLike, getLikes } from '../services/api'
import { useDownloads } from './useDownloads'

export type RepeatMode = 'off' | 'all' | 'one'

export function usePlayer() {
  // Playback state
  const currentTrack = ref<Track | null>(null)
  const isPlaying = ref(false)
  const currentTime = ref(0)
  const duration = ref(0)
  const volume = ref(0.8)
  
  // Queue
  const queue = ref<Track[]>([])
  const queueIndex = ref(-1)
  
  // Modes
  const shuffleMode = ref(false)
  const repeatMode = ref<RepeatMode>('off')
  
  // Likes & User
  const likedIds = ref<Set<string>>(new Set())
  const tgUserId = ref<number>(0)
  
  // Internal
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

  // Initialize audio element
  function initAudio() {
    if (audio) return
    
    audio = new Audio()
    audio.volume = volume.value
    audio.preload = 'metadata'

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
      // Try to resolve URL through API
      if (currentTrack.value && !currentTrack.value.url) {
        resolveAndPlay(currentTrack.value)
      }
    }
  }

  async function resolveAndPlay(track: Track) {
    if (!audio) initAudio()
    
    try {
      let url = track.url
      if (!url) {
        url = await getStreamUrl(track.id)
        track.url = url
      }
      
      if (url && audio) {
        audio.src = url
        await audio.play()
        isPlaying.value = true
      }
    } catch {
      // Silent fail
    }
  }

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
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      url = `${apiUrl}/local/${fileId}`
    }
    
    // 3. Если нет локально — получаем стрим URL
    if (!url) {
      url = track.url
      if (!url) {
        try {
          url = await getStreamUrl(track.id)
          track.url = url
        } catch {
          url = ''
        }
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

    // Add to history after 10 seconds
    scheduleHistory(track)
  }

  function scheduleHistory(track: Track) {
    if (historyTimer) clearTimeout(historyTimer)
    historyTimer = setTimeout(() => {
      if (tgUserId.value && currentTrack.value?.id === track.id) {
        addToHistory(tgUserId.value, track).catch(() => {})
      }
    }, 10000)
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
    if (!audio || !duration.value) return
    audio.currentTime = (percent / 100) * duration.value
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
      // Repeat current track
      if (audio) {
        audio.currentTime = 0
        audio.play().catch(() => {})
      }
      return
    }
    
    if (shuffleMode.value) {
      // Random track from queue
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
      // Loop to beginning
      queueIndex.value = 0
      play(queue.value[0])
    } else {
      isPlaying.value = false
    }
  }

  function prev() {
    // If more than 3 seconds played, restart current track
    if (audio && audio.currentTime > 3) {
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

  function handleTrackEnd() {
    next()
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
    if (!s || isNaN(s)) return '0:00'
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
  }
}
