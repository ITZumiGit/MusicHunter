<template>
  <div class="app" :class="{ 'has-player': hasPlayer }">
    <!-- Desktop: Sidebar -->
    <Sidebar class="app-sidebar" />
    
    <!-- Main content -->
    <main class="app-content">
      <router-view />
    </main>
    
    <!-- Mobile: Bottom navigation -->
    <MobileNav class="app-mobile-nav" />
    
    <!-- Mobile: Player (sits above nav) -->
    <Player
      v-if="hasPlayer"
      :current-track="player.currentTrack.value"
      :is-playing="player.isPlaying.value"
      :current-time="player.currentTime.value"
      :duration="player.duration.value"
      :volume="player.volume.value"
      :progress="player.progress.value"
      :shuffle-mode="player.shuffleMode.value"
      :repeat-mode="player.repeatMode.value"
      :is-current-liked="player.isCurrentLiked.value"
      :toggle-play="player.togglePlay"
      :next="player.next"
      :prev="player.prev"
      :seek="player.seek"
      :set-volume="player.setVolume"
      :like-current="player.likeCurrent"
      :toggle-shuffle="player.toggleShuffle"
      :toggle-repeat="player.toggleRepeat"
      :format-time="player.formatTime"
      :stop="player.stop"
    />
    
    <!-- Desktop: Player (fixed bottom bar) -->
    <DesktopPlayer
      v-if="hasPlayer"
      :current-track="player.currentTrack.value"
      :is-playing="player.isPlaying.value"
      :current-time="player.currentTime.value"
      :duration="player.duration.value"
      :volume="player.volume.value"
      :progress="player.progress.value"
      :shuffle-mode="player.shuffleMode.value"
      :repeat-mode="player.repeatMode.value"
      :is-current-liked="player.isCurrentLiked.value"
      :toggle-play="player.togglePlay"
      :next="player.next"
      :prev="player.prev"
      :seek="player.seek"
      :set-volume="player.setVolume"
      :like-current="player.likeCurrent"
      :toggle-shuffle="player.toggleShuffle"
      :toggle-repeat="player.toggleRepeat"
      :format-time="player.formatTime"
      :stop="player.stop"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, provide, watch } from 'vue'
import Sidebar from './components/Sidebar.vue'
import MobileNav from './components/MobileNav.vue'
import Player from './components/Player.vue'
import DesktopPlayer from './components/DesktopPlayer.vue'
import { usePlayer } from './composables/usePlayer'
import { useTelegram } from './composables/useTelegram'

const player = usePlayer()
const tg = useTelegram()

provide('player', player)

const hasPlayer = computed(() => !!player.currentTrack.value)

// Загружаем лайки когда Telegram user становится доступен
const loadLikesForUser = async () => {
  const tgUser = tg.user.value
  if (tgUser?.id) {
    player.tgUserId.value = tgUser.id
    await player.loadLikes(tgUser.id)
  }
}

onMounted(async () => {
  // Попробуем сразу
  await loadLikesForUser()
})

// Если tg user загрузился позже — перезагрузим лайки с правильным ID
watch(() => tg.user.value, async (newUser) => {
  if (newUser?.id && newUser.id !== player.tgUserId.value) {
    console.log('[App] Telegram user changed, reloading likes for:', newUser.id)
    await loadLikesForUser()
  }
})
</script>

<style>
/* Global resets */
* { box-sizing: border-box; }
body { margin: 0; overflow: hidden; }

/* App layout */
.app {
  display: flex;
  min-height: 100vh;
  height: 100vh;
  background: var(--bg-primary);
  overflow: hidden;
}

/* ─── Desktop layout ─── */
@media (min-width: 768px) {
  .app {
    display: grid;
    grid-template-columns: var(--sidebar-width) 1fr;
    grid-template-rows: 1fr;
  }
  
  .app-sidebar {
    display: flex !important;
    grid-column: 1;
    grid-row: 1;
  }
  
  .app-content {
    grid-column: 2;
    grid-row: 1;
    overflow-y: auto;
    min-height: 100vh;
  }
  
  .app-mobile-nav { display: none !important; }
  
  .app.has-player .app-content {
    padding-bottom: var(--player-height);
  }
}

/* ─── Mobile layout ─── */
@media (max-width: 767px) {
  .app {
    flex-direction: column;
  }
  
  .app-sidebar { display: none !important; }
  
  .app-content {
    flex: 1;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    /* Base padding for nav */
    padding-bottom: var(--nav-height);
  }
  
  /* When player is visible, add extra padding for mini player above nav */
  .app.has-player .app-content {
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile));
  }
  
  .app-mobile-nav { display: flex !important; }
}
</style>
