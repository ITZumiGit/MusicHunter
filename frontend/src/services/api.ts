/**
 * MusicHunter API v2 — полная музыкальная платформа
 * Поиск, лайки, плейлисты, история
 */

const API_URL = import.meta.env.VITE_API_URL || 'https://musichunter.ru'
console.log('[MusicHunter] API_URL:', API_URL)

export interface Track {
  id: string
  title: string
  artist: string
  duration: number
  duration_str: string
  url: string
  cover_url: string
}

export interface SearchResult {
  query: string
  count: number
  tracks: Track[]
}

export interface Playlist {
  id: number
  name: string
  description: string
  cover_url: string
  is_public: boolean
  track_count: number
  created_at: string
}

export interface PlaylistDetail extends Playlist {
  tracks: Track[]
}

export interface Stats {
  likes: number
  playlists: number
  listened: number
  top_artists: { name: string; count: number }[]
}

// ─── Search ──────────────────────────────────
export async function searchTracks(query: string, limit = 50): Promise<SearchResult> {
  const url = `${API_URL}/search?q=${encodeURIComponent(query)}&limit=${limit}`
  console.log('[MusicHunter] Fetching:', url)
  try {
    const res = await fetch(url)
    console.log('[MusicHunter] Response status:', res.status, res.ok)
    if (!res.ok) throw new Error(`Сервер вернул ${res.status}`)
    const data = await res.json()
    console.log('[MusicHunter] Got', data.count, 'tracks')
    return data
  } catch (e: any) {
    console.error('[MusicHunter] Fetch failed:', e?.message || e)
    throw e
  }
}

// ─── Stream ──────────────────────────────────
export async function getStreamUrl(trackId: string): Promise<string> {
  // Локальные файлы бота — прямой URL
  if (trackId.startsWith('local_')) {
    const fileId = trackId.slice(6)
    return `${API_URL}/local/${fileId}`
  }
  const res = await fetch(`${API_URL}/stream/${encodeURIComponent(trackId)}`)
  if (!res.ok) throw new Error('Не удалось получить ссылку на стрим')
  const data = await res.json()
  return data.url
}

export function getAudioUrl(track: Track): string {
  if (track.url && track.url.startsWith('/local/')) {
    return `${API_URL}${track.url}`
  }
  if (track.url) return track.url
  return `${API_URL}/stream/${encodeURIComponent(track.id)}`
}

// ─── Likes ───────────────────────────────────
export async function toggleLike(tgId: number, track: Track): Promise<{ action: string; track_id: string }> {
  const res = await fetch(`${API_URL}/likes/${tgId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      track_id: track.id,
      title: track.title,
      artist: track.artist,
      duration: track.duration,
      url: track.url,
      cover_url: track.cover_url,
    }),
  })
  if (!res.ok) throw new Error('Ошибка лайка')
  return res.json()
}

export async function getLikes(tgId: number): Promise<{ count: number; tracks: Track[] }> {
  const res = await fetch(`${API_URL}/likes/${tgId}`)
  if (!res.ok) throw new Error('Ошибка загрузки лайков')
  return res.json()
}

export async function removeLike(tgId: number, trackId: string): Promise<void> {
  await fetch(`${API_URL}/likes/${tgId}/${encodeURIComponent(trackId)}`, { method: 'DELETE' })
}

// ─── Playlists ───────────────────────────────
export async function createPlaylist(
  tgId: number,
  name: string,
  description = '',
  isPublic = true,
): Promise<Playlist> {
  const res = await fetch(`${API_URL}/playlists/${tgId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, description, is_public: isPublic }),
  })
  if (!res.ok) throw new Error('Ошибка создания плейлиста')
  return res.json()
}

export async function getPlaylists(tgId: number): Promise<{ count: number; playlists: Playlist[] }> {
  const res = await fetch(`${API_URL}/playlists/${tgId}`)
  if (!res.ok) throw new Error('Ошибка загрузки плейлистов')
  return res.json()
}

export async function getPlaylist(tgId: number, playlistId: number): Promise<PlaylistDetail> {
  const res = await fetch(`${API_URL}/playlists/${tgId}/${playlistId}`)
  if (!res.ok) throw new Error('Ошибка загрузки плейлиста')
  return res.json()
}

export async function updatePlaylist(
  tgId: number,
  playlistId: number,
  data: { name?: string; description?: string; cover_url?: string; is_public?: boolean },
): Promise<void> {
  await fetch(`${API_URL}/playlists/${tgId}/${playlistId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export async function deletePlaylist(tgId: number, playlistId: number): Promise<void> {
  await fetch(`${API_URL}/playlists/${tgId}/${playlistId}`, { method: 'DELETE' })
}

export async function addTrackToPlaylist(
  tgId: number,
  playlistId: number,
  track: Track,
): Promise<void> {
  const res = await fetch(`${API_URL}/playlists/${tgId}/${playlistId}/tracks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      track_id: track.id,
      title: track.title,
      artist: track.artist,
      duration: track.duration,
      url: track.url,
      cover_url: track.cover_url,
    }),
  })
  if (!res.ok) throw new Error('Ошибка добавления трека')
}

export async function removeTrackFromPlaylist(
  tgId: number,
  playlistId: number,
  trackId: string,
): Promise<void> {
  await fetch(
    `${API_URL}/playlists/${tgId}/${playlistId}/tracks/${encodeURIComponent(trackId)}`,
    { method: 'DELETE' },
  )
}

// ─── History ─────────────────────────────────
export async function addToHistory(tgId: number, track: Track): Promise<void> {
  await fetch(`${API_URL}/history/${tgId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      track_id: track.id,
      title: track.title,
      artist: track.artist,
      duration: track.duration,
      url: track.url,
      cover_url: track.cover_url,
    }),
  })
}

export async function getHistory(
  tgId: number,
  limit = 50,
): Promise<{ count: number; tracks: Track[] }> {
  const res = await fetch(`${API_URL}/history/${tgId}?limit=${limit}`)
  if (!res.ok) throw new Error('Ошибка загрузки истории')
  return res.json()
}

export async function clearHistory(tgId: number): Promise<void> {
  await fetch(`${API_URL}/history/${tgId}`, { method: 'DELETE' })
}

// ─── Stats ───────────────────────────────────
export async function getStats(tgId: number): Promise<Stats> {
  const res = await fetch(`${API_URL}/stats/${tgId}`)
  if (!res.ok) throw new Error('Ошибка загрузки статистики')
  return res.json()
}

// ─── Download (save to IndexedDB) ───────────
export async function downloadTrackAudio(trackId: string): Promise<Blob> {
  const url = await getStreamUrl(trackId)
  const res = await fetch(url)
  if (!res.ok) throw new Error('Ошибка скачивания')
  return res.blob()
}

// ─── Local Music (bot files) ─────────────────
export async function getLocalTracks(): Promise<{ count: number; tracks: Track[] }> {
  const res = await fetch(`${API_URL}/local`)
  if (!res.ok) throw new Error('Ошибка загрузки локальной музыки')
  return res.json()
}
