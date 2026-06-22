<template>
  <div class="track-list">
    <div
      v-for="(track, index) in tracks"
      :key="track.id"
      class="track-item"
      :class="{ active: isActive(track) }"
      @click="$emit('play', track, index)"
    >
      <!-- Index / Play indicator -->
      <div class="track-index">
        <span v-if="!isActive(track)" class="index-num">{{ index + 1 }}</span>
        <svg v-else class="playing-icon" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <polygon v-if="!isPlaying" points="5,3 19,12 5,21"/>
          <g v-else>
            <rect x="6" y="4" width="4" height="16"/>
            <rect x="14" y="4" width="4" height="16"/>
          </g>
        </svg>
      </div>
      
      <!-- Cover -->
      <div class="track-cover">
        <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" loading="lazy" />
        <div v-else class="cover-placeholder">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18V5l12-2v13"/>
            <circle cx="6" cy="18" r="3"/>
            <circle cx="18" cy="16" r="3"/>
          </svg>
        </div>
      </div>
      
      <!-- Info -->
      <div class="track-info">
        <div class="track-title">{{ track.title }}</div>
        <div class="track-artist">{{ track.artist }}</div>
      </div>
      
      <!-- Duration -->
      <div class="track-duration">{{ track.duration_str }}</div>

      <!-- Like button -->
      <button class="track-action" :class="{ liked: isLiked(track.id) }" @click.stop="$emit('like', track)" title="Лайк">
        <svg width="18" height="18" viewBox="0 0 24 24" :fill="isLiked(track.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </button>

      <!-- More button (три точки) -->
      <button class="track-action more-btn" @click.stop="openMenu(track, $event)" title="Ещё">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="5" r="2"/>
          <circle cx="12" cy="12" r="2"/>
          <circle cx="12" cy="19" r="2"/>
        </svg>
      </button>
    </div>

    <!-- Context menu -->
    <Teleport to="body">
      <div v-if="menuTrack" class="menu-overlay" @click="closeMenu" @contextmenu.prevent="closeMenu">
        <div class="context-menu" :style="menuPosition">
          <button class="menu-item" @click="addToPlaylist">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="8" y1="6" x2="21" y2="6"/>
              <line x1="8" y1="12" x2="21" y2="12"/>
              <line x1="8" y1="18" x2="21" y2="18"/>
              <line x1="3" y1="6" x2="3.01" y2="6"/>
              <line x1="3" y1="12" x2="3.01" y2="12"/>
              <line x1="3" y1="18" x2="3.01" y2="18"/>
            </svg>
            Добавить в плейлист
          </button>
          <button class="menu-item" @click="likeFromMenu">
            <svg width="16" height="16" viewBox="0 0 24 24" :fill="isLiked(pendingTrack?.id) ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
            {{ isLiked(pendingTrack?.id) ? 'Убрать из лайков' : 'Лайк' }}
          </button>
          <button class="menu-item" @click="downloadFromMenu" :disabled="isPendingDownloaded || downloadingTrack">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            {{ downloadingTrack ? 'Загрузка...' : (isPendingDownloaded ? 'Сохранено' : 'Скачать') }}
          </button>
        </div>
      </div>

      <!-- Playlist picker modal -->
      <div v-if="showPlaylistPicker" class="menu-overlay" @click.self="closePlaylistPicker">
        <div class="playlist-picker">
          <div class="picker-header">
            <h3>Добавить в плейлист</h3>
            <button class="picker-close" @click="closePlaylistPicker">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Inline create form -->
          <div class="picker-create-form">
            <div class="create-row">
              <input
                v-model="newPlName"
                placeholder="Новый плейлист"
                class="picker-input"
                @keydown.enter="createAndAdd"
              />
              <button
                class="picker-create-btn"
                @click="createAndAdd"
                :disabled="!newPlName.trim()"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                Создать
              </button>
            </div>
          </div>

          <div v-if="playlistsLoading" class="picker-loading">Загрузка...</div>
          <div v-else-if="userPlaylists.length" class="picker-list">
            <button
              v-for="pl in userPlaylists"
              :key="pl.id"
              class="picker-item"
              @click="addToExistingPlaylist(pl.id)"
            >
              <div class="picker-pl-cover">
                <img v-if="pl.cover_url" :src="pl.cover_url" />
                <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/>
                  <line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/>
                </svg>
              </div>
              <div class="picker-pl-info">
                <div class="picker-pl-name">{{ pl.name }}</div>
                <div class="picker-pl-meta">{{ pl.track_count }} треков</div>
              </div>
              <svg class="picker-add-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
          </div>
          <div v-else class="picker-empty">Создайте первый плейлист выше ☝️</div>

          <!-- Status message -->
          <div v-if="statusMsg" class="picker-status" :class="statusType">{{ statusMsg }}</div>
        </div>
      </div>
    </Teleport>
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
  likedIds: Set<string>
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
  return props.likedIds.has(trackId)
}

// ── Context menu ──
const menuTrack = ref<Track | null>(null)
const menuPosition = ref<{ top: string; left: string }>({ top: '0px', left: '0px' })

// ⚠️ ВАЖНО: pendingTrack хранит трек отдельно от menuTrack,
// чтобы не потерять его при закрытии контекстного меню
const pendingTrack = ref<Track | null>(null)

function openMenu(track: Track, event: MouseEvent) {
  menuTrack.value = track
  pendingTrack.value = track  // Сохраняем в pendingTrack
  const x = Math.min(event.clientX, window.innerWidth - 220)
  const y = Math.min(event.clientY - 10, window.innerHeight - 120)
  menuPosition.value = { top: `${y}px`, left: `${x}px` }
}

function closeMenu() {
  menuTrack.value = null
  // НЕ обнуляем pendingTrack! Он нужен для плейлиста
}

function likeFromMenu() {
  if (pendingTrack.value) {
    emit('like', pendingTrack.value)
  }
  menuTrack.value = null
}

// ── Download from menu ──
const downloadingTrack = ref(false)
const isPendingDownloaded = computed(() => {
  return pendingTrack.value ? downloads.isDownloaded(pendingTrack.value.id) : false
})

async function downloadFromMenu() {
  if (!pendingTrack.value || downloadingTrack.value || isPendingDownloaded.value) return
  downloadingTrack.value = true
  try {
    await downloads.downloadTrack(pendingTrack.value)
    statusType.value = 'success'
    statusMsg.value = '✓ Сохранено в скачанные'
    setTimeout(() => { statusMsg.value = '' }, 1500)
  } catch (e: any) {
    statusType.value = 'error'
    statusMsg.value = 'Ошибка загрузки'
  }
  downloadingTrack.value = false
  menuTrack.value = null
}

// ── Playlist picker ──
const showPlaylistPicker = ref(false)
const userPlaylists = ref<Playlist[]>([])
const playlistsLoading = ref(false)
const newPlName = ref('')
const statusMsg = ref('')
const statusType = ref<'success' | 'error'>('success')

async function addToPlaylist() {
  menuTrack.value = null  // Закрываем контекстное меню
  // pendingTrack уже сохранён!
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
    statusMsg.value = '✓ Добавлено!'
    // Закрываем через секунду
    setTimeout(() => {
      showPlaylistPicker.value = false
      pendingTrack.value = null
      statusMsg.value = ''
    }, 1000)
  } catch (e: any) {
    statusType.value = 'error'
    statusMsg.value = e?.message || 'Ошибка добавления'
  }
}

async function createAndAdd() {
  if (!newPlName.value.trim() || !pendingTrack.value) return
  try {
    const pl = await createPlaylist(player.tgUserId.value, newPlName.value, '')
    await addTrackToPlaylist(player.tgUserId.value, pl.id, pendingTrack.value)
    statusType.value = 'success'
    statusMsg.value = `✓ Плейлист "${newPlName.value}" создан, трек добавлен!`
    newPlName.value = ''
    // Обновляем список плейлистов
    await loadPlaylists()
    // Закрываем через секунду
    setTimeout(() => {
      showPlaylistPicker.value = false
      pendingTrack.value = null
      statusMsg.value = ''
    }, 1500)
  } catch (e: any) {
    statusType.value = 'error'
    statusMsg.value = e?.message || 'Ошибка создания плейлиста'
  }
}
</script>

<style scoped>
.track-list {
  display: flex;
  flex-direction: column;
}

.track-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: background 0.15s;
}

.track-item:hover {
  background: var(--bg-tertiary);
}

.track-item.active {
  background: var(--accent-glow);
}

.track-index {
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.index-num {
  font-size: 13px;
  color: var(--fg-muted);
}

.playing-icon {
  color: var(--accent);
  animation: pulse 1s ease-in-out infinite;
}

.track-cover {
  width: 44px;
  height: 44px;
  border-radius: 8px;
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
  background: var(--bg-tertiary);
  color: var(--fg-muted);
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
  font-size: 12px;
  color: var(--fg-muted);
  flex-shrink: 0;
}

.track-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: var(--fg-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.track-action:hover {
  color: var(--fg-primary);
  background: var(--bg-tertiary);
}

.track-action.liked {
  color: var(--pink);
}

/* More button - hidden until hover on desktop */
.more-btn {
  opacity: 0;
  transition: opacity 0.15s, color 0.15s;
}

.track-item:hover .more-btn {
  opacity: 1;
}

/* Always show on mobile */
@media (max-width: 767px) {
  .more-btn {
    opacity: 1;
  }
}

/* Context menu overlay */
.menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.context-menu {
  position: fixed;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 6px;
  min-width: 200px;
  box-shadow: var(--shadow);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 12px;
  background: none;
  border: none;
  color: var(--fg-primary);
  font-size: 14px;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.15s;
}

.menu-item:hover {
  background: var(--bg-tertiary);
}

.menu-item:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Playlist picker */
.playlist-picker {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  padding: 20px;
  width: 100%;
  max-width: 400px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow);
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.picker-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--fg-primary);
}

.picker-close {
  background: none;
  border: none;
  color: var(--fg-muted);
  cursor: pointer;
  padding: 4px;
}

.picker-close:hover {
  color: var(--fg-primary);
}

/* Create form */
.picker-create-form {
  margin-bottom: 16px;
}

.create-row {
  display: flex;
  gap: 8px;
}

.picker-input {
  flex: 1;
  padding: 10px 12px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--fg-primary);
  font-size: 14px;
  outline: none;
}

.picker-input:focus {
  border-color: var(--accent);
}

.picker-create-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}

.picker-create-btn:disabled {
  opacity: 0.5;
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
  width: 40px;
  height: 40px;
  border-radius: 8px;
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

/* Status message */
.picker-status {
  text-align: center;
  padding: 10px;
  margin-top: 12px;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
}

.picker-status.success {
  background: rgba(0, 206, 201, 0.15);
  color: var(--teal);
}

.picker-status.error {
  background: rgba(253, 121, 168, 0.15);
  color: var(--pink);
}
</style>
