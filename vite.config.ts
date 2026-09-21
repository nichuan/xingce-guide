import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/xingce-guide/',
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/katex') || id.includes('node_modules/markdown-it')) {
            return 'markdown'
          }
          if (id.includes('node_modules/vue')) return 'vue'
        },
      },
    },
  },
})
