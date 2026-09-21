import { ref } from 'vue'
import { safeGet, safeSet } from './storage'

const stored = safeGet('xc-theme')
const prefersDark =
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches
const isDark = ref(stored ? stored === 'dark' : prefersDark)

function applyTheme(dark: boolean) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('dark', dark)
  document
    .querySelector('meta[name="theme-color"]')
    ?.setAttribute('content', dark ? '#0b101e' : '#4f46e5')
}

export function useTheme() {
  const toggle = () => {
    isDark.value = !isDark.value
    safeSet('xc-theme', isDark.value ? 'dark' : 'light')
    applyTheme(isDark.value)
  }
  return { isDark, toggle }
}

applyTheme(isDark.value)
