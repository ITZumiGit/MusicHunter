<template>
  <div class="track-list">
    <div
      v-for="(track, index) in tracks"
      :key="track.id"
      class="track-item"
      :class="{ active: isActive(track) }"
      @click="emit('play', track, index)"
      @contextmenu.prevent="openMenu(track, $event)"
    >
      <div class="track-index">
        <span v-if="isActive(track) && isPlaying" class="playing-bars">
          <span></span><span></span><span></span>
        </span>
        <span v-else class="index-num">{{ index + 1 }}</span>
      </div>

      <div class="track-cover">
        <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" loading="lazy" />
        <div v-else class="cover-placeholder">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M9 18V5l12-2v13" />
            <circle cx="6" cy="18" r="3" />
            <circle cx="18" cy="16" r="3" />
          </svg>
        </div>
      </div>

      <div class="track-info">
        <div class="track-title">{{ track.title }}</div>
        <div class="track-artist">{{ track.artist }}</div>
      </div>

      <div class="track-duration">{{ track.duration_str }}</div>

      <div class="track-actions">
        <button
          class="action-btn like-btn"
          :class="{ liked: isLiked(track.id) }"
          @click.stop="emit('like', track)"
          :title="isLiked(track.id) ? 'UnLike' : 'Like'"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" :fill="isLiked(track.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
        </button>
        <button class="action-btn more-btn" @click.stop="openMenu(track, $event)" title="More">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="1" />
            <circle cx="19" cy="12" r="1" />
            <circle cx="5" cy="12" r="1" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Context Menu Overlay -->
    <div v-if="menuTrack" class="menu-overlay" @click="closeMenu">
      <div class="context-menu" @click.stop>
        <button class="menu-item" @click="downloadFromMenu">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          {{ downloadingTrack ? 'Loading...' : (isPendingDownloaded ? 'Saved' : 'Download') }}
        </button>
        <button class="menu-item" @click="addToPlaylist" :disabled="!pendingTrack">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          To Playlist
        </button>
        <button class="menu-item" @click="likeFromMenu">
          <svg width="16" height="16" viewBox="0 0 24 24" :fill="isLiked(pendingTrack?.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
          </svg>
          {{ isLiked(pendingTrack?.id) ? 'UnLike' : 'Like' }}
        </button>
      </div>
    </div>

    <!-- Playlist Picker Modal -->
    <div v-if="showPlaylistPicker" class="menu-overlay" @click="closePlaylistPicker">
      <div class="playlist-picker" @click.stop>
        <div class="picker-header">
          <h3>To Playlist</h3>
          <button class="picker-close" @click="closePlaylistPicker">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div class="picker-create-form">
          <div class="create-row">
            <input v-model="newPlName" class="picker-input" placeholder="New playlist..." @keyup.enter="createAndAdd" />
            <button class="picker-create-btn" @click="createAndAdd" :disabled="!newPlName.trim()">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="playlistsLoading" class="picker-loading">Loading...</div>
        <div v-else-if="userPlaylists.length === 0" class="picker-empty">Create first playlist</div>
        <div v-else class="picker-list">
          <button v-for="pl in userPlaylists" :key="pl.id" class="picker-item" @click="addToExistingPlaylist(pl.id)">
            <div class="picker-pl-cover">
              <img v-if="pl.cover_url" :src="pl.cover_url" :alt="pl.name" />
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18V5l12-2v13" />
                <circle cx="6" cy="18" r="3" />
                <circle cx="18" cy="16" r="3" />
              </svg>
            </div>
            <div class="picker-pl-info">
              <div class="picker-pl-name">{{ pl.name }}</div>
              <div class="picker-pl-meta">{{ pl.track_count }} tracks</div>
            </div>
            <div class="picker-add-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </div>
          </button>
        </div>

        <div v-if="statusMsg" class="picker-status" :class="statusType">{{ statusMsg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { inject } from 'vue'
import type { Track, Playlist } from '../services/api'
import { getPlaylists, createPlaylist, addTrackToPlaylist } from '../services/api'
import { useDownloads } from '../composables/useDownloads'

const props = defineProps<{
  tracks: Track[]
  currentTrack: Track | null
  isPlaying: boolean
  likedIds?: Set<string>
}>()

const emit = defineEmits<{
  play: [track: Track, index: number]
  like: [track: Track]
}>()

const player = inject<any>('player')
const downloads = useDownloads()

function isActive(track: Track): boolean {
  return props.currentTrack?.id === track.id
}

function isLiked(trackId: string | undefined): boolean {
  if (!trackId) return false
  return props.likedIds?.has(trackId) ?? false
}

// -- Context menu --
const menuTrack = ref<Track | null>(null)
const menuPosition = ref<{ top: string; left: string }>({ top: '0px', left: '0px' })
const pendingTrack = ref<Track | null>(null)

function openMenu(track: Track, event: MouseEvent) {
  menuTrack.value = track
  pendingTrack.value = track
  const x = Math.min(event.clientX, window.innerWidth - 200)
  const y = Math.min(event.clientY - 10, window.innerHeight - 140)
  menuPosition.value = { top: y + 'px', left: x + 'px' }
}

function closeMenu() {
  menuTrack.value = null
}

function likeFromMenu() {
  if (pendingTrack.value) {
    emit('like', pendingTrack.value)
  }
  menuTrack.value = null
}

// -- Download --
const downloadingTrack = ref(false)
const isPendingDownloaded = computed(() => {
  return pendingTrack.value ? downloads.isDownloaded(pendingTrack.value.id) : false
})

const statusMsg = ref('')
const statusType = ref<'success' | 'error'>('success')

async function downloadFromMenu() {
  if (!pendingTrack.value || downloadingTrack.value || isPendingDownloaded.value) return

  downloadingTrack.value = true
  try {
    await downloads.downloadTrack(pendingTrack.value)
    statusType.value = 'success'
    statusMsg.value = 'Saved'
    setTimeout(() => { statusMsg.value = '' }, 1500)
  } catch {
    statusType.value = 'error'
    statusMsg.value = 'Download error'
  }
  downloadingTrack.value = false
  menuTrack.value = null
}

// -- Playlist picker --
const showPlaylistPicker = ref(false)
const userPlaylists = ref<Playlist[]>([])
const playlistsLoading = ref(false)
const newPlName = ref('')

async function addToPlaylist() {
  menuTrack.value = null
  if (!pendingTrack.value) return

  showPlaylistPicker.value = true
  newPlName.value = ''
  statusMsg.value = ''
  await loadPlaylists()
}

async function loadPlaylists() {
  if (!player?.tgUserId?.value) return
  playlistsLoading.value = true
  try {
    const data = await getPlaylists(player.tgUserId.value)
    userPlaylists.value = data.playlists
  } catch {
    userPlaylists.value = []
  }
  playlistsLoading.value = false
}

function closePlaylistPicker() {
  showPlaylistPicker.value = false
  pendingTrack.value = null
  newPlName.value = ''
  statusMsg.value = ''
}

async function addToExistingPlaylist(playlistId: number) {
  if (!pendingTrack.value) return
  try {
    await addTrackToPlaylist(player.tgUserId.value, playlistId, pendingTrack.value)
    statusType.value = 'success'
    statusMsg.value = 'Added!'
    setTimeout(() => {
      showPlaylistPicker.value = false
      pendingTrack.value = null
      statusMsg.value = ''
    }, 1000)
  } catch {
    statusType.value = 'error'
    statusMsg.value = 'Error'
  }
}

async function createAndAdd() {
  if (!newPlName.value.trim() || !pendingTrack.value) return
  try {
    const pl = await createPlaylist(player.tgUserId.value, newPlName.value, '')
    await addTrackToPlaylist(player.tgUserId.value, pl.id, pendingTrack.value)
    statusType.value = 'success'
    statusMsg.value = 'Created!'
    newPlName.value = ''
    await loadPlaylists()
    setTimeout(() => {
      showPlaylistPicker.value = false
      pendingTrack.value = null
      statusMsg.value = ''
    }, 1500)
  } catch {
    statusType.value = 'error'
    statusMsg.value = 'Create error'
  }
}
</script>

<style scoped>
.track-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.track-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px var(--space-md);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}

.track-item:hover {
  background: var(--bg-card);
}

.track-item.active {
  background: var(--accent-gradient-subtle);
}

.track-index {
  width: 22px;
  text-align: center;
  flex-shrink: 0;
}

.index-num {
  font-size: 12px;
  color: var(--fg-muted);
  font-variant-numeric: tabular-nums;
}

.playing-bars {
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 14px;
  justify-content: center;
}

.playing-bars span {
  width: 3px;
  background: var(--accent);
  border-radius: 2px;
  animation: bar-bounce 0.8s ease-in-out infinite;
}

.playing-bars span:nth-child(1) { height: 6px; animation-delay: 0s; }
.playing-bars span:nth-child(2) { height: 10px; animation-delay: 0.2s; }
.playing-bars span:nth-child(3) { height: 4px; animation-delay: 0.4s; }

.playing-bars span.paused {
  animation-play-state: paused;
}

@keyframes bar-bounce {
  0%, 100% { transform: scaleY(0.4); }
  50% { transform: scaleY(1.2); }
}

.track-cover {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
}

.track-cover img {
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

.track-info {
  flex: 1;
  min-width: 0;
}

.track-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--fg-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-item.active .track-title {
  color: var(--accent);
}

.track-artist {
  font-size: 12px;
  color: var(--fg-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.track-duration {
  font-size: 11px;
  color: var(--fg-muted);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

.track-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  color: var(--fg-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
  -webkit-tap-highlight-color: transparent;
}

.action-btn:active {
  transform: scale(0.85);
}

.action-btn:hover {
  color: var(--fg-primary);
  background: var(--bg-tertiary);
}

.like-btn.liked {
  color: var(--pink);
}

.more-btn {
  opacity: 0;
  transition: opacity 0.15s;
}

.track-item:hover .more-btn {
  opacity: 1;
}

@media (max-width: 767px) {
  .more-btn {
    opacity: 1;
  }
}

.menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.context-menu {
  position: fixed;
  background: var(--bg-secondary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-lg);
  padding: 6px;
  min-width: 180px;
  box-shadow: var(--shadow-lg);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  background: none;
  border: none;
  color: var(--fg-primary);
  font-size: 14px;
  cursor: pointer;
  border-radius: var(--radius);
  transition: background 0.15s;
}

.menu-item:hover {
  background: var(--bg-tertiary);
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.playlist-picker {
  background: var(--bg-secondary);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-xl);
  padding: 20px;
  width: 100%;
  max-width: 380px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.picker-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--fg-primary);
}

.picker-close {
  background: none;
  border: none;
  color: var(--fg-muted);
  cursor: pointer;
  padding: 4px;
}

.picker-create-form {
  margin-bottom: 16px;
}

.create-row {
  display: flex;
  gap: 8px;
}

.picker-input {
  flex: 1;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--fg-primary);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.picker-input:focus {
  border-color: var(--accent);
}

.picker-create-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  background: var(--accent-gradient);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: opacity 0.15s;
  flex-shrink: 0;
}

.picker-create-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.picker-loading,
.picker-empty {
  text-align: center;
  padding: 20px;
  color: var(--fg-muted);
  font-size: 14px;
}

.picker-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: none;
  border: none;
  color: var(--fg-primary);
  cursor: pointer;
  border-radius: var(--radius);
  transition: background 0.15s;
  width: 100%;
  text-align: left;
}

.picker-item:hover {
  background: var(--bg-tertiary);
}

.picker-pl-cover {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  color: var(--fg-muted);
}

.picker-pl-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.picker-pl-info {
  flex: 1;
  min-width: 0;
}

.picker-pl-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.picker-pl-meta {
  font-size: 12px;
  color: var(--fg-muted);
  margin-top: 2px;
}

.picker-add-icon {
  color: var(--accent);
  flex-shrink: 0;
}

.picker-status {
  text-align: center;
  padding: 10px;
  margin-top: 12px;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
}

.picker-status.success {
  background: rgba(45, 212, 191, 0.12);
  color: var(--teal);
}

.picker-status.error {
  background: rgba(244, 114, 182, 0.12);
  color: var(--pink);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>