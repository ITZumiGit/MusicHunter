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
    
    <!-- Mobile: Player (expands from bottom) -->
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
import { computed, onMounted, provide } from 'vue'
import Sidebar from './components/Sidebar.vue'
import MobileNav from './components/MobileNav.vue'
import Player from './components/Player.vue'
import DesktopPlayer from './components/DesktopPlayer.vue'
import { usePlayer } from './composables/usePlayer'
import { useTelegram } from './composables/useTelegram'

const player = usePlayer()
const tg = useTelegram()

// Provide player globally
provide('player', player)

const hasPlayer = computed(() => !!player.currentTrack.value)

// Initialize
onMounted(async () => {
  // Get user ID from Telegram or use test ID
  const tgUser = tg.user.value
  if (tgUser?.id) {
    player.tgUserId.value = tgUser.id
    await player.loadLikes(tgUser.id)
  } else {
    // Dev mode
    player.tgUserId.value = 12345
    await player.loadLikes(12345)
  }
})
</script>

<style>
/* App layout */
.app {
  display: flex;
  min-height: 100vh;
  background: var(--bg-primary);
}

/* ─── Desktop layout ─── */
@media (min-width: 768px) {
  .app {
    display: grid;
    grid-template-columns: var(--sidebar-width) 1fr;
    grid-template-rows: 1fr;
  }
  
  .app-sidebar {
    display: flex !important; /* Force show on desktop */
    grid-column: 1;
    grid-row: 1;
  }
  
  .app-content {
    grid-column: 2;
    grid-row: 1;
    overflow-y: auto;
    min-height: 100vh;
  }
  
  .app-mobile-nav {
    display: none !important; /* Force hide on desktop */
  }
  
  .app.has-player .app-content {
    padding-bottom: var(--player-height);
  }
}

/* ─── Mobile layout ─── */
@media (max-width: 767px) {
  .app {
    flex-direction: column;
  }
  
  .app-sidebar {
    display: none !important; /* Force hide on mobile */
  }
  
  .app-content {
    flex: 1;
    overflow-y: auto;
    padding-bottom: calc(var(--nav-height) + var(--player-height-mobile, 64px));
  }
  
  .app-mobile-nav {
    display: flex !important; /* Force show on mobile */
  }
}
</style>
