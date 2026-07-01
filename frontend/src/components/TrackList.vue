<template>
  <div class="track-list">
    <div
      v-for="(track, index) in tracks"
      :key="track.id"
      class="track-item"
      :class="{ active: player.currentTrack?.id === track.id }"
      @click.stop="playTrack(track, index)"
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
        <div v-else class="track-cover-placeholder">♪</div>
        <div class="track-text">
          <div class="track-title">{{ track.title }}</div>
          <div class="track-artist">{{ track.artist }}</div>
        </div>
      </div>

      <div class="track-actions">
        <button
          class="track-btn like-btn"
          :class="{ liked: likedSet.has(track.id) }"
          @click.stop="handleLike(track)"
          @touchstart.stop
          @touchend.stop
        >
          {{ likedSet.has(track.id) ? '❤️' : '🤍' }}
        </button>

        <button
          class="track-btn download-btn"
          :class="{ downloading: downloading, downloaded: downloads.isDownloaded(track.id) }"
          :disabled="downloading"
          @click.stop="handleDownload(track)"
          @touchstart.stop
          @touchend.stop
        >
          <span v-if="downloads.isDownloaded(track.id)">✓</span>
          <span v-else-if="downloading">⏳</span>
          <span v-else>⬇️</span>
        </button>
      </div>
    </div>

    <div v-if="tracks.length === 0" class="empty-state">
      <p>Ничего не найдено</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { Track } from '../services/api'
import { usePlayer } from '../composables/usePlayer'
import { useDownloads } from '../composables/useDownloads'

const props = defineProps<{
  tracks: Track[]
}>()

const router = useRouter()
const player = usePlayer()
const downloads = useDownloads()
const downloading = ref(false)

// Safe computed - never crashes even if likedIds is undefined
const likedSet = computed<Set<string>>(() => {
  try {
    if (player.likedIds && player.likedIds.value instanceof Set) {
      return player.likedIds.value
    }
  } catch (e) {}
  return new Set<string>()
})

function playTrack(track: Track, index: number) {
  console.log('[TrackList] playTrack:', track.title)
  player.setQueue(props.tracks, index)
  router.push('/player')
}

async function handleLike(track: Track) {
  console.log('[TrackList] handleLike:', track.title, 'tgUserId:', player.tgUserId?.value)
  if (!player.toggleTrackLike) {
    console.error('[TrackList] toggleTrackLike not available!')
    return
  }
  try {
    await player.toggleTrackLike(track)
    console.log('[TrackList] handleLike done')
  } catch (e) {
    console.error('[TrackList] handleLike error:', e)
  }
}

async function handleDownload(track: Track) {
  console.log('[TrackList] handleDownload:', track.title)
  if (downloading.value) return
  downloading.value = true
  try {
    await downloads.downloadTrack(track)
    console.log('[TrackList] Download complete')
  } catch (e) {
    console.error('[TrackList] Download error:', e)
  } finally {
    downloading.value = false
  }
}
</script>

<style scoped>
.track-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.track-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: background 0.15s;
  -webkit-tap-highlight-color: transparent;
}

.track-item:active {
  background: rgba(255, 255, 255, 0.08);
}

.track-item.active {
  background: rgba(99, 102, 241, 0.15);
}

.track-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.track-cover {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.track-cover-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.track-text {
  min-width: 0;
  flex: 1;
}

.track-title {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  margin-left: 8px;
}

.track-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  font-size: 18px;
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-tap-highlight-color: transparent;
}

.track-btn:active {
  background: rgba(255, 255, 255, 0.1);
}

.like-btn.liked {
  animation: like-pop 0.3s ease;
}

@keyframes like-pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.download-btn.downloading {
  opacity: 0.5;
}

.download-btn.downloaded {
  color: #10b981;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
