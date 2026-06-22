<template>
  <aside class="sidebar">
    <!-- Logo -->
    <div class="logo">
      <div class="logo-icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="10" stroke="var(--accent)" stroke-width="2"/>
          <circle cx="12" cy="12" r="4" fill="var(--accent)"/>
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4" stroke="var(--accent)" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </div>
      <span class="logo-text">MusicHunter</span>
    </div>
    
    <!-- Navigation -->
    <nav class="nav">
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
    
    <!-- Spacer -->
    <div class="spacer"></div>
    
    <!-- Theme toggle -->
    <div class="sidebar-footer">
      <ThemeToggle />
    </div>
  </aside>
</template>

<script setup lang="ts">
import { h } from 'vue'
import { useRoute } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'

const $route = useRoute()

// SVG icon components
const SearchIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('circle', { cx: 11, cy: 11, r: 8 }),
  h('path', { d: 'M21 21l-4.35-4.35' })
])

const HeartIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z' })
])

const PlaylistIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('line', { x1: 8, y1: 6, x2: 21, y2: 6 }),
  h('line', { x1: 8, y1: 12, x2: 21, y2: 12 }),
  h('line', { x1: 8, y1: 18, x2: 21, y2: 18 }),
  h('line', { x1: 3, y1: 6, x2: 3.01, y2: 6 }),
  h('line', { x1: 3, y1: 12, x2: 3.01, y2: 12 }),
  h('line', { x1: 3, y1: 18, x2: 3.01, y2: 18 })
])

const HistoryIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('circle', { cx: 12, cy: 12, r: 10 }),
  h('polyline', { points: '12 6 12 12 16 14' })
])

const DownloadIcon = () => h('svg', { width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2 }, [
  h('path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }),
  h('polyline', { points: '7 10 12 15 17 10' }),
  h('line', { x1: 12, y1: 15, x2: 12, y2: 3 })
])

const navItems = [
  { path: '/', label: 'Поиск', icon: SearchIcon },
  { path: '/likes', label: 'Лайки', icon: HeartIcon },
  { path: '/playlists', label: 'Плейлисты', icon: PlaylistIcon },
  { path: '/downloaded', label: 'Библиотека', icon: DownloadIcon },
  { path: '/history', label: 'История', icon: HistoryIcon },
]
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: var(--sidebar-width);
  height: 100vh;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  padding: var(--space-lg);
  position: sticky;
  top: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm) 0;
  margin-bottom: var(--space-xl);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-tertiary);
  border-radius: var(--radius);
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--fg-primary);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-md);
  border-radius: var(--radius);
  color: var(--fg-secondary);
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition);
}

.nav-item:hover {
  background: var(--bg-tertiary);
  color: var(--fg-primary);
}

.nav-item.active {
  background: var(--accent-glow);
  color: var(--accent);
}

.nav-item svg {
  flex-shrink: 0;
}

.spacer {
  flex: 1;
}

.sidebar-footer {
  padding-top: var(--space-lg);
  border-top: 1px solid var(--border);
}
</style>
