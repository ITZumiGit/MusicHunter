/**
 * Theme management composable
 */
import { ref, watch } from 'vue'

const STORAGE_KEY = 'mh-theme'

// Initialize from localStorage or default to dark
const theme = ref<'dark' | 'light'>(
  (localStorage.getItem(STORAGE_KEY) as 'dark' | 'light') || 'dark'
)

// Apply theme on initialization
if (typeof document !== 'undefined') {
  document.documentElement.setAttribute('data-theme', theme.value)
}

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  function setTheme(t: 'dark' | 'light') {
    theme.value = t
  }

  // Watch for changes and persist
  watch(theme, (t) => {
    if (typeof document !== 'undefined') {
      document.documentElement.setAttribute('data-theme', t)
      localStorage.setItem(STORAGE_KEY, t)
    }
  })

  return {
    theme,
    toggle,
    setTheme,
  }
}
