import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/xingce-guide/',
  build: {
    chunkSizeWarningLimit: 1200,
  },
})
