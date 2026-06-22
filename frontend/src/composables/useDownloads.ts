/**
 * MusicHunter Downloads — локальный кэш музыки через IndexedDB
 * Скачанные треки хранятся локально и играют без интернета
 */
import { ref, computed } from 'vue'
import type { Track } from '../services/api'
import { getStreamUrl } from '../services/api'

const DB_NAME = 'MusicHunterDB'
const DB_VERSION = 1
const STORE_NAME = 'downloads'

// Глобальное реактивное состояние (singleton)
const downloadedIds = ref<Set<string>>(new Set())
const downloadedTracks = ref<Track[]>([])
const initialized = ref(false)

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const store = db.createObjectStore(STORE_NAME, { keyPath: 'id' })
        store.createIndex('downloadedAt', 'downloadedAt', { unique: false })
      }
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function getAllFromDB(): Promise<Array<Track & { blob: Blob; downloadedAt: number }>> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readonly')
    const store = tx.objectStore(STORE_NAME)
    const request = store.getAll()
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function putToDB(data: any): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    const request = store.put(data)
    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

async function deleteFromDB(id: string): Promise<void> {
  const db = await openDB()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, 'readwrite')
    const store = tx.objectStore(STORE_NAME)
    const request = store.delete(id)
    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

export function useDownloads() {
  // Инициализация — загружаем список скачанных из IndexedDB
  async function init() {
    if (initialized.value) return
    initialized.value = true
    try {
      const items = await getAllFromDB()
      const ids = new Set<string>()
      const tracks: Track[] = []
      for (const item of items) {
        ids.add(item.id)
        tracks.push({
          id: item.id,
          title: item.title,
          artist: item.artist,
          duration: item.duration,
          duration_str: item.duration_str,
          url: '',
          cover_url: item.cover_url,
        })
      }
      downloadedIds.value = ids
      downloadedTracks.value = tracks
    } catch (e) {
      console.error('Downloads init error:', e)
    }
  }

  // Скачивание трека — fetch аудио blob + сохранение в IndexedDB
  async function downloadTrack(track: Track): Promise<void> {
    if (downloadedIds.value.has(track.id)) return

    // 1. Получаем URL стрима
    let streamUrl = track.url
    if (!streamUrl) {
      try {
        streamUrl = await getStreamUrl(track.id)
      } catch {
        throw new Error('Не удалось получить ссылку на аудио')
      }
    }
    if (!streamUrl) throw new Error('Нет URL для скачивания')

    // 2. Скачиваем blob
    const response = await fetch(streamUrl)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const blob = await response.blob()

    // 3. Сохраняем в IndexedDB
    const record = {
      id: track.id,
      title: track.title,
      artist: track.artist,
      duration: track.duration,
      duration_str: track.duration_str || `${Math.floor(track.duration / 60)}:${(track.duration % 60).toString().padStart(2, '0')}`,
      cover_url: track.cover_url,
      blob,
      downloadedAt: Date.now(),
    }
    await putToDB(record)

    // 4. Обновляем реактивное состояние
    downloadedIds.value = new Set([...downloadedIds.value, track.id])
    downloadedTracks.value = [...downloadedTracks.value, {
      id: track.id,
      title: track.title,
      artist: track.artist,
      duration: track.duration,
      duration_str: record.duration_str,
      url: '',
      cover_url: track.cover_url,
    }]
  }

  // Получить локальный blob URL для воспроизведения оффлайн
  async function getLocalUrl(trackId: string): Promise<string | null> {
    if (!downloadedIds.value.has(trackId)) return null
    try {
      const db = await openDB()
      return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE_NAME, 'readonly')
        const store = tx.objectStore(STORE_NAME)
        const request = store.get(trackId)
        request.onsuccess = () => {
          const record = request.result
          if (record?.blob) {
            const url = URL.createObjectURL(record.blob)
            resolve(url)
          } else {
            resolve(null)
          }
        }
        request.onerror = () => reject(request.error)
      })
    } catch {
      return null
    }
  }

  // Удалить трек из кэша
  async function removeDownload(trackId: string): Promise<void> {
    await deleteFromDB(trackId)
    downloadedIds.value = new Set([...downloadedIds.value].filter(id => id !== trackId))
    downloadedTracks.value = downloadedTracks.value.filter(t => t.id !== trackId)
  }

  // Проверить, скачан ли трек
  function isDownloaded(trackId: string): boolean {
    return downloadedIds.value.has(trackId)
  }

  // Очистить все загрузки
  async function clearAll(): Promise<void> {
    const db = await openDB()
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite')
      const store = tx.objectStore(STORE_NAME)
      const request = store.clear()
      request.onsuccess = () => {
        downloadedIds.value = new Set()
        downloadedTracks.value = []
        resolve()
      }
      request.onerror = () => reject(request.error)
    })
  }

  const count = computed(() => downloadedTracks.value.length)

  // Инициализируем сразу
  init()

  return {
    downloadedIds,
    downloadedTracks,
    count,
    init,
    downloadTrack,
    getLocalUrl,
    removeDownload,
    isDownloaded,
    clearAll,
  }
}
