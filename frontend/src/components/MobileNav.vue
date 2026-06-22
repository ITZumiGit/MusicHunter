<template>
  <nav class="mobile-nav" ref="navRef">
    <router-link
      v-for="item in navItems"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :class="{ active: $route.path === item.path }"
    >
      <component :is="item.icon" />
      <span>{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup lang="ts">
import { h, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const $route = useRoute()
const $router = useRouter()
const navRef = ref<HTMLElement | null>(null)

// SVG icon components
const SearchIcon = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('circle', { cx: 11, cy: 11, r: 8 }),
  h('path', { d: 'M21 21l-4.35-4.35' })
])

const HeartIcon = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z' })
])

const PlaylistIcon = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('line', { x1: 8, y1: 6, x2: 21, y2: 6 }),
  h('line', { x1: 8, y1: 12, x2: 21, y2: 12 }),
  h('line', { x1: 8, y1: 18, x2: 21, y2: 18 }),
  h('line', { x1: 3, y1: 6, x2: 3.01, y2: 6 }),
  h('line', { x1: 3, y1: 12, x2: 3.01, y2: 12 }),
  h('line', { x1: 3, y1: 18, x2: 3.01, y2: 18 })
])

const DownloadIcon = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }),
  h('polyline', { points: '7 10 12 15 17 10' }),
  h('line', { x1: 12, y1: 15, x2: 12, y2: 3 })
])

const HistoryIcon = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('circle', { cx: 12, cy: 12, r: 10 }),
  h('polyline', { points: '12 6 12 12 16 14' })
])

const navItems = [
  { path: '/', label: 'Поиск', icon: SearchIcon },
  { path: '/likes', label: 'Лайки', icon: HeartIcon },
  { path: '/playlists', label: 'Плейлисты', icon: PlaylistIcon },
  { path: '/downloaded', label: 'Библиотека', icon: DownloadIcon },
  { path: '/history', label: 'История', icon: HistoryIcon },
]

// ── Swipe navigation ──
let touchStartX = 0
let touchStartY = 0

function onTouchStart(e: TouchEvent) {
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
}

function onTouchEnd(e: TouchEvent) {
  const dx = e.changedTouches[0].clientX - touchStartX
  const dy = e.changedTouches[0].clientY - touchStartY
  
  // Only horizontal swipes (dx > 2*dy), minimum 60px
  if (Math.abs(dx) < 60 || Math.abs(dy) > Math.abs(dx) * 0.5) return

  const currentIndex = navItems.findIndex(item => item.path === $route.path)
  if (currentIndex === -1) return

  if (dx > 0 && currentIndex > 0) {
    // Swipe right → previous tab
    $router.push(navItems[currentIndex - 1].path)
  } else if (dx < 0 && currentIndex < navItems.length - 1) {
    // Swipe left → next tab
    $router.push(navItems[currentIndex + 1].path)
  }
}

onMounted(() => {
  // Swipe на всём экране, не только на навбаре
  document.addEventListener('touchstart', onTouchStart, { passive: true })
  document.addEventListener('touchend', onTouchEnd, { passive: true })
})

onUnmounted(() => {
  document.removeEventListener('touchstart', onTouchStart)
  document.removeEventListener('touchend', onTouchEnd)
})
</script>

<style scoped>
.mobile-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: var(--nav-height);
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 90;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-xs) var(--space-sm);
  color: var(--fg-muted);
  font-size: 10px;
  font-weight: 500;
  transition: all var(--transition);
  min-width: 0;
  flex: 1;
}

.nav-item:hover,
.nav-item.active {
  color: var(--accent);
}

.nav-item.active svg {
  transform: scale(1.1);
}
</style>
