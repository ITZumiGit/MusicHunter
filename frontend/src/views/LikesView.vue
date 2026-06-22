<template>
  <div class="likes-view">
    <h1 class="page-title">Лайки</h1>
    
    <div v-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Загрузка...</p>
    </div>
    
    <div v-else-if="tracks.length" class="tracks-container">
      <div class="results-meta">
        <span class="count-pill">{{ tracks.length }} треков</span>
      </div>
      <TrackList
        :tracks="tracks"
        :current-track="player.currentTrack.value"
        :is-playing="player.isPlaying.value"
        :liked-ids="player.likedIds.value"
        @play="onPlayTrack"
        @like="player.toggleTrackLike"
      />
    </div>
    
    <div v-else class="state-container">
      <div class="empty-icon-wrap">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </div>
      <h3>Пока нет лайков</h3>
      <p>Нажмите ❤️ чтобы добавить трек</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { inject } from 'vue'
import TrackList from '../components/TrackList.vue'
import { getLikes, type Track } from '../services/api'

const player = inject<any>('player')
const loading = ref(true)
const tracks = ref<Track[]>([])

async function loadLikes() {
  loading.value = true
  try {
    const data = await getLikes(player.tgUserId.value)
    tracks.value = data.tracks
  } catch { tracks.value = [] }
  finally { loading.value = false }
}

function onPlayTrack(track: Track, index: number) {
  player.setQueue(tracks.value, index)
}

watch(() => player.likedIds.value.size, () => loadLikes())
onMounted(() => loadLikes())
</script>

<style scoped>
.likes-view {
  padding: var(--space-xl);
  min-height: 100%;
}

.page-title {
  font-size: 26px;
  font-weight: 800;
  color: var(--fg-primary);
  margin-bottom: var(--space-xl);
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 20vh;
  text-align: center;
  color: var(--fg-secondary);
}

.state-container h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--fg-primary);
  margin-bottom: var(--space-sm);
}

.state-container p {
  font-size: 14px;
  color: var(--fg-muted);
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: var(--space-lg);
}

.empty-icon-wrap {
  display: flex; align-items: center; justify-content: center;
  width: 80px; height: 80px; border-radius: var(--radius-xl);
  background: rgba(244, 114, 182, 0.1);
  color: var(--pink);
  margin-bottom: var(--space-lg);
}

.tracks-container { margin-top: var(--space-md); }

.results-meta { margin-bottom: var(--space-md); }

.count-pill {
  font-size: 11px; font-weight: 700; color: var(--accent);
  background: var(--accent-glow);
  padding: 2px 10px; border-radius: var(--radius-full);
}

@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 767px) {
  .likes-view {
    padding: var(--space-lg);
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile) + var(--space-xl));
  }
}
</style>
