/**
 * Composable для работы с Telegram Web App SDK
 */
import { ref, onMounted } from 'vue'

export function useTelegram() {
  const user = ref<{ id: number; first_name: string; username?: string } | null>(null)
  const isDark = ref(true)
  const isReady = ref(false)

  onMounted(() => {
    try {
      const tg = (window as any).Telegram?.WebApp
      if (tg) {
        tg.ready()
        tg.expand()
        isDark.value = tg.colorScheme === 'dark'
        user.value = tg.initDataUnsafe?.user ?? null
        isReady.value = true
      } else {
        // Not in Telegram — regular browser
        isReady.value = true
      }
    } catch {
      isReady.value = true
    }
  })

  function close() {
    try {
      (window as any).Telegram?.WebApp?.close()
    } catch {
      window.close()
    }
  }

  function openLink(url: string) {
    try {
      (window as any).Telegram?.WebApp?.openTelegramLink(url)
    } catch {
      window.open(url, '_blank')
    }
  }

  return { user, isDark, isReady, close, openLink }
}
