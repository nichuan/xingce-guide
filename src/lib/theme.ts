import { ref } from 'vue'

const stored = localStorage.getItem('xc-theme')
const isDark = ref(stored ? stored === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches)

export function useTheme() {
  const toggle = () => {
    isDark.value = !isDark.value
    localStorage.setItem('xc-theme', isDark.value ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', isDark.value)
  }
  return { isDark, toggle }
}
