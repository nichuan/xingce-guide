import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import ChapterView from './views/ChapterView.vue'

/** 平滑滚动到锚点元素，返回是否找到 */
export function scrollToId(id: string, offset = 84): boolean {
  const el = document.getElementById(id)
  if (!el) return false
  const top = el.getBoundingClientRect().top + window.scrollY - offset
  window.scrollTo({ top, behavior: 'smooth' })
  return true
}

// 使用 hash 路由：GitHub Pages 无需 404 回退配置
export const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/ch/:id', name: 'chapter', component: ChapterView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(to, _from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) {
      // 中文锚点无法作为 CSS 选择器查询，且目标内容可能尚未渲染，轮询等待
      const id = decodeURIComponent(to.hash.slice(1))
      return new Promise((resolve) => {
        const start = performance.now()
        const tryScroll = () => {
          if (scrollToId(id)) {
            resolve(false)
          } else if (performance.now() - start > 1500) {
            resolve({ top: 0 })
          } else {
            setTimeout(tryScroll, 60)
          }
        }
        tryScroll()
      })
    }
    return { top: 0 }
  },
})
