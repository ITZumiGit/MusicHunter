<template>
  <div class="track-list">
    <div
      v-for="(track, index) in tracks"
      :key="track.id"
      class="track-item"
      :class="{ playing: currentTrack?.id === track.id && isPlaying }"
      @click="playTrack(track, index)"
    >
      <div class="track-index">{{ index + 1 }}</div>
      <div class="track-cover">
        <img v-if="track.cover_url" :src="track.cover_url" alt="" />
        <div v-else class="cover-placeholder">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
      </div>
      <div class="track-info">
        <div class="track-title">{{ track.title || 'Unknown' }}</div>
        <div class="track-artist">{{ track.artist || 'Unknown Artist' }}</div>
      </div>
      <div class="track-actions">
        <button
          class="like-btn"
          :class="{ liked: isLiked(track.id) }"
          @click.stop="toggleTrackLike(track)"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
        </button>
        <button class="download-btn" @click.stop="onDownload(track)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePlayer } from '../composables/usePlayer'
import { useDownloads } from '../composables/useDownloads'
import type { Track } from '../services/api'

const props = defineProps<{
  tracks: Track[]
}>()

const player = usePlayer()
const downloads = useDownloads()

const currentTrack = computed(() => player.currentTrack.value)
const isPlaying = computed(() => player.isPlaying.value)

const isLiked = player.isLiked
const toggleTrackLike = player.toggleTrackLike
const setQueue = player.setQueue

const isDownloaded = downloads.isDownloaded
const downloadTrackFn = downloads.downloadTrack

async function onDownload(track: Track) {
  try {
    await downloadTrackFn(track)
  } catch (e) {
    console.error('[TrackList] Download error:', e)
  }
}

function playTrack(track: Track, index: number) {
  console.log('[TrackList] playTrack:', track.title, 'index:', index, 'total:', props.tracks.length)
  setQueue(props.tracks, index)
}
</script>

<style scoped>
.track-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.track-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 12px;
}

.track-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.track-item.playing {
  background: rgba(255, 255, 255, 0.08);
}

.track-item.playing .track-title {
  color: #a78bfa;
}

.track-index {
  width: 24px;
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.track-cover {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.track-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  color: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.track-info {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.track-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.like-btn,
.download-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: none;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s ease;
  padding: 0;
}

.like-btn:hover,
.download-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
}

.like-btn.liked {
  color: #f472b6;
}

.like-btn.liked svg {
  fill: #f472b6;
  stroke: #f472b6;
}

@media (max-width: 767px) {
  .track-index {
    width: 20px;
    font-size: 12px;
  }
  .track-cover {
    width: 38px;
    height: 38px;
  }
  .like-btn,
  .download-btn {
    width: 30px;
    height: 30px;
  }
}
</style>
