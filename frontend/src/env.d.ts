/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// Telegram Web App SDK
interface Telegram {
  WebApp: {
    ready: () => void
    close: () => void
    expand: () => void
    MainButton: {
      text: string
      show: () => void
      hide: () => void
      onClick: (fn: () => void) => void
    }
    BackButton: {
      show: () => void
      hide: () => void
      onClick: (fn: () => void) => void
    }
    initDataUnsafe: {
      user?: {
        id: number
        first_name: string
        username?: string
      }
    }
    themeParams: {
      bg_color?: string
      text_color?: string
      hint_color?: string
      button_color?: string
      button_text_color?: string
    }
    colorScheme: 'light' | 'dark'
    openTelegramLink: (url: string) => void
  }
}

declare const Telegram: Telegram
