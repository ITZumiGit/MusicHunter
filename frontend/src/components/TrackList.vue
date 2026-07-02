<template>
  <div class="track-list">
    <div
      v-for="(track, index) in tracks"
      :key="track.id"
      class="track-item"
      :class="{ active: player.currentTrack?.id === track.id }"
      @click="playTrack(track, index)"
      @touchstart.stop
      @touchend.stop
    >
      <div class="track-info">
        <img
          v-if="track.cover_url"
          :src="track.cover_url"
          class="track-cover"
          alt=""
          loading="lazy"
        />
        <div v-else class="track-cover-placeholder">&#9835;</div>
        <div class="track-text">
          <div class="track-title">{{ track.title }}</div>
          <div class="track-artist">{{ track.artist }}</div>
        </div>
      </div>
      <div class="track-actions">
        <button
          class="track-btn like-btn"
          :class="{ liked: player.isLiked(track.id) }"
          @click.stop="handleLike(track)"
          @touchstart.stop
        >
          {{ player.isLiked(track.id) ? '❤️' : '🤍' }}
        </button>
        <button
          class="track-btn playlist-btn"
          @click.stop="openPlaylistModal(track)"
          @touchstart.stop
          title="Добавить в плейлист"
        >
          📁
        </button>
        <button
          class="track-btn download-btn"
          :class="{ downloading: downloading, downloaded: downloads.isDownloaded(track.id) }"
          :disabled="downloading"
          @click.stop="handleDownload(track)"
          @touchstart.stop
        >
          <span v-if="downloads.isDownloaded(track.id)">&#10003;</span>
          <span v-else-if="downloading">&#9203;</span>
          <span v-else>&#11015;&#65039;</span>
        </button>
      </div>
    </div>
    <div v-if="tracks.length === 0" class="empty-state">
      <p>Ничего не найдено</p>
    </div>

    <!-- Playlist Modal -->
    <Teleport to="body">
      <div v-if="showPlaylistModal" class="playlist-modal-overlay" @click.self="showPlaylistModal = false">
        <div class="playlist-modal">
          <div class="modal-header">
            <h3>Добавить в плейлист</h3>
            <button class="modal-close" @click="showPlaylistModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <div v-if="playlistsLoading" class="modal-loading">Загрузка...</div>
            <template v-else>
              <div
                v-for="pl in playlists"
                :key="pl.id"
                class="playlist-item"
                @click="addToPlaylist(pl.id)"
              >
                <span class="playlist-icon">&#127925;</span>
                <div class="playlist-info">
                  <div class="playlist-name">{{ pl.name }}</div>
                  <div class="playlist-count">{{ pl.track_count }} треков</div>
                </div>
              </div>
              <div v-if="playlists.length === 0" class="no-playlists">Нет плейлистов, создайте новый</div>
              <div class="create-playlist">
                <input
                  v-model="newPlaylistName"
                  placeholder="Название нового плейлиста"
                  @keyup.enter="createAndAdd"
                  class="new-playlist-input"
                />
                <button
                  class="create-btn"
                  :disabled="!newPlaylistName.trim()"
                  @click="createAndAdd"
                >
                  Создать
                </button>
              </div>
            </template>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Track, Playlist } from '../services/api'
import { usePlayer } from '../composables/usePlayer'
import { useDownloads } from '../composables/useDownloads'
import { getPlaylists, addTrackToPlaylist, createPlaylist } from '../services/api'

const props = defineProps<{ tracks: Track[] }>()
const player = usePlayer()
const downloads = useDownloads()
const downloading = ref(false)

// Playlist modal state
const showPlaylistModal = ref(false)
const playlistsLoading = ref(false)
const playlists = ref<Playlist[]>([])
const newPlaylistName = ref('')
const selectedTrack = ref<Track | null>(null)

function playTrack(track: Track, index: number) {
  console.log('[TrackList] playTrack:', track.title)
  player.setQueue(props.tracks, index)
}

async function handleLike(track: Track) {
  console.log('[TrackList] handleLike:', track.title)
  try { await player.toggleTrackLike(track) } catch (e) { console.error(e) }
}

async function handleDownload(track: Track) {
  console.log('[TrackList] handleDownload:', track.title)
  if (downloading.value) return
  downloading.value = true
  try { await downloads.downloadTrack(track) } catch (e) { console.error(e) }
  finally { downloading.value = false }
}

async function openPlaylistModal(track: Track) {
  selectedTrack.value = track
  showPlaylistModal.value = true
  playlistsLoading.value = true
  try {
    const tgId = player.tgUserId.value || 12345
    const result = await getPlaylists(tgId)
    playlists.value = result.playlists || []
  } catch (e) {
    console.error('[TrackList] Failed to load playlists:', e)
    playlists.value = []
  } finally {
    playlistsLoading.value = false
  }
}

async function addToPlaylist(playlistId: number) {
  if (!selectedTrack.value) return
  try {
    const tgId = player.tgUserId.value || 12345
    await addTrackToPlaylist(tgId, playlistId, selectedTrack.value)
    console.log('[TrackList] Added to playlist:', playlistId)
    showPlaylistModal.value = false
  } catch (e) {
    console.error('[TrackList] Failed to add to playlist:', e)
    alert('Не удалось добавить, попробуйте снова')
  }
}

async function createAndAdd() {
  if (!selectedTrack.value || !newPlaylistName.value.trim()) return
  try {
    const tgId = player.tgUserId.value || 12345
    const newPl = await createPlaylist(tgId, newPlaylistName.value.trim(), '', false)
    if (newPl && newPl.id) {
      await addTrackToPlaylist(tgId, newPl.id, selectedTrack.value)
      console.log('[TrackList] Created playlist and added track:', newPl.id)
      showPlaylistModal.value = false
      newPlaylistName.value = ''
    }
  } catch (e) {
    console.error('[TrackList] Failed to create playlist:', e)
    alert('Не удалось создать плейлист')
  }
}
</script>

<style scoped>
.track-list { width: 100%; display: flex; flex-direction: column; gap: 4px; }
.track-item { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-radius: 10px; background: rgba(255,255,255,0.04); cursor: pointer; transition: background 0.15s; -webkit-tap-highlight-color: transparent; }
.track-item:active { background: rgba(255,255,255,0.08); }
.track-item.active { background: rgba(99,102,241,0.15); }
.track-info { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0; }
.track-cover { width: 44px; height: 44px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }
.track-cover-placeholder { width: 44px; height: 44px; border-radius: 8px; background: rgba(255,255,255,0.1); display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.track-text { min-width: 0; flex: 1; }
.track-title { font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track-artist { font-size: 12px; color: rgba(255,255,255,0.5); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track-actions { display: flex; gap: 4px; flex-shrink: 0; margin-left: 8px; }
.track-btn { width: 36px; height: 36px; border: none; background: none; font-size: 18px; cursor: pointer; border-radius: 8px; display: flex; align-items: center; justify-content: center; -webkit-tap-highlight-color: transparent; }
.track-btn:active { background: rgba(255,255,255,0.1); }
.like-btn.liked { animation: like-pop 0.3s ease; }
@keyframes like-pop { 0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }
.download-btn.downloading { opacity: 0.5; }
.download-btn.downloaded { color: #10b981; }
.playlist-btn { color: rgba(255,255,255,0.6); }
.playlist-btn:hover { color: #fff; }
.empty-state { text-align: center; padding: 40px 20px; color: rgba(255,255,255,0.4); }
</style>

<style>
/* Playlist Modal (unscoped for Teleport) */
.playlist-modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}
.playlist-modal {
  background: #1e1e2e; border-radius: 16px; width: 340px; max-height: 70vh;
  display: flex; flex-direction: column; overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.1);
}
.modal-header h3 { margin: 0; font-size: 16px; color: #fff; }
.modal-close {
  background: none; border: none; color: rgba(255,255,255,0.5);
  font-size: 24px; cursor: pointer; padding: 0; line-height: 1;
}
.modal-close:hover { color: #fff; }
.modal-body { padding: 12px 16px; overflow-y: auto; flex: 1; }
.modal-loading { text-align: center; padding: 20px; color: rgba(255,255,255,0.5); }
.playlist-item {
  display: flex; align-items: center; gap: 12px; padding: 12px;
  border-radius: 10px; cursor: pointer; transition: background 0.15s;
}
.playlist-item:hover { background: rgba(255,255,255,0.08); }
.playlist-item:active { background: rgba(255,255,255,0.12); }
.playlist-icon { font-size: 24px; }
.playlist-info { flex: 1; }
.playlist-name { font-size: 14px; color: #fff; font-weight: 500; }
.playlist-count { font-size: 12px; color: rgba(255,255,255,0.4); margin-top: 2px; }
.no-playlists { text-align: center; padding: 16px; color: rgba(255,255,255,0.4); font-size: 13px; }
.create-playlist { margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; gap: 8px; }
.new-playlist-input {
  flex: 1; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px; padding: 8px 12px; color: #fff; font-size: 13px; outline: none;
}
.new-playlist-input:focus { border-color: #6366f1; }
.new-playlist-input::placeholder { color: rgba(255,255,255,0.3); }
.create-btn {
  background: #6366f1; color: #fff; border: none; border-radius: 8px;
  padding: 8px 14px; font-size: 13px; cursor: pointer; white-space: nowrap;
}
.create-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.create-btn:hover:not(:disabled) { background: #5558e6; }
</style>
