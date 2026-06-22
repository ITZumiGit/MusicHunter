<template>
  <div class="track-card" :class="{ active: isActive }" @click="$emit('play', track)">
    <div class="cover">
      <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" loading="lazy" />
      <div v-else class="cover-placeholder">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
        </svg>
      </div>
      <div class="play-overlay">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5,3 19,12 5,21"/>
        </svg>
      </div>
    </div>
    <div class="info">
      <div class="title">{{ track.title }}</div>
      <div class="artist">{{ track.artist }}</div>
    </div>
    <div class="duration">{{ track.duration_str }}</div>
    <button class="like-btn" :class="{ liked: isLiked }" @click.stop="handleLike">
      <svg width="18" height="18" viewBox="0 0 24 24" :fill="isLiked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Track } from '../services/api'

const props = defineProps<{
  track: Track
  isActive?: boolean
  isLiked?: boolean
}>()

const emit = defineEmits<{
  play: [track: Track]
  like: [track: Track]
}>()

function handleLike() {
  emit('like', props.track)
}
</script>

<style scoped>
.track-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.track-card:hover {
  background: rgba(255, 255, 255, 0.06);
}

.track-card.active {
  background: rgba(137, 180, 250, 0.1);
}

.cover {
  position: relative;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.cover img {
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
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.3);
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
  opacity: 0;
  transition: opacity 0.15s;
}

.track-card:hover .play-overlay {
  opacity: 1;
}

.info {
  flex: 1;
  min-width: 0;
}

.title {
  font-size: 14px;
  font-weight: 500;
  color: #cdd6f4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.artist {
  font-size: 12px;
  color: #a6adc8;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.duration {
  font-size: 12px;
  color: #6c7086;
  flex-shrink: 0;
}

.like-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #6c7086;
  padding: 4px;
  transition: color 0.15s, transform 0.15s;
}

.like-btn:hover {
  color: #f38ba8;
  transform: scale(1.2);
}

.like-btn.liked {
  color: #f38ba8;
}
</style>
