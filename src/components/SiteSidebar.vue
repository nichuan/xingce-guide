<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import Icon from './Icon.vue'
import { chapters, chapterGroups, getChapter } from '../content/chapters'
import { ui } from '../lib/ui'
import { useTheme } from '../lib/theme'
import { learning, removeBookmark } from '../lib/learning'

const { isDark, toggle } = useTheme()
const sidebarEl = ref<HTMLElement>()
let sidebarTrigger: HTMLElement | null = null

function goSearch() {
  ui.searchOpen = true
}

function trapSidebarFocus(e: KeyboardEvent) {
  if (!ui.sidebarOpen || e.key !== 'Tab' || !sidebarEl.value) return
  const focusable = Array.from(
    sidebarEl.value.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'),
  )
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (!first || !last) return
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
}

watch(
  () => ui.sidebarOpen,
  async (open) => {
    if (open) {
      sidebarTrigger = document.activeElement as HTMLElement | null
      await nextTick()
      sidebarEl.value?.querySelector<HTMLElement>('a[href], button')?.focus()
    } else if (sidebarTrigger) {
      await nextTick()
      sidebarTrigger.focus()
      sidebarTrigger = null
    }
  },
)
</script>

<template>
  <Transition name="overlay">
    <div v-if="ui.sidebarOpen" class="sidebar-overlay" @click="ui.sidebarOpen = false"></div>
  </Transition>

  <aside
    id="site-sidebar"
    ref="sidebarEl"
    class="sidebar"
    :class="{ open: ui.sidebarOpen }"
    :role="ui.sidebarOpen ? 'dialog' : undefined"
    :aria-modal="ui.sidebarOpen ? 'true' : undefined"
    aria-label="主导航"
    @keydown="trapSidebarFocus"
  >
    <RouterLink class="brand" to="/" aria-label="返回行测指南首页">
      <svg class="brand-logo" viewBox="0 0 64 64" aria-hidden="true">
        <defs>
          <linearGradient id="brand-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stop-color="#6366f1" />
            <stop offset="1" stop-color="#0ea5e9" />
          </linearGradient>
        </defs>
        <rect width="64" height="64" rx="14" fill="url(#brand-g)" />
        <path
          d="M18 22h28M32 22v24M22 46h20"
          stroke="#fff"
          stroke-width="5"
          stroke-linecap="round"
          fill="none"
        />
        <circle cx="44" cy="18" r="5" fill="#fbbf24" />
      </svg>
      <div class="brand-text">
        <strong>行测指南</strong>
        <span>方法为先 · 轻松掌握</span>
      </div>
    </RouterLink>

    <button class="search-trigger" @click="goSearch">
      <Icon name="search" />
      <span>搜索考点、公式、技巧</span>
      <kbd>Ctrl K</kbd>
    </button>

    <nav class="nav">
      <div v-for="group in chapterGroups" :key="group.key" class="nav-group">
        <div class="nav-group-label">{{ group.label }}</div>
        <RouterLink
          v-for="ch in chapters.filter((c) => c.group === group.key)"
          :key="ch.id"
          :to="`/ch/${ch.id}`"
          class="nav-item"
          active-class="active"
        >
          <span class="nav-icon" :style="{ color: ch.color, background: ch.color + '1a' }">
            <Icon :name="ch.icon" />
          </span>
          <span class="nav-text">
            <span class="nav-title">{{ ch.short }}</span>
            <Icon v-if="learning.progress[ch.id]?.completed" class="nav-done" name="check" />
            <span v-if="ch.questions" class="nav-badge">{{ ch.questions }}</span>
          </span>
        </RouterLink>
      </div>

      <div class="nav-group">
        <div class="nav-group-label">速查</div>
        <RouterLink to="/formulas" class="nav-item" active-class="active">
          <span class="nav-icon formula-icon"><Icon name="sigma" /></span>
          <span class="nav-text"><span class="nav-title">全部公式</span></span>
        </RouterLink>
      </div>

      <div v-if="learning.bookmarks.length" class="nav-group bookmarks">
        <div class="nav-group-label">我的收藏</div>
        <div
          v-for="item in learning.bookmarks.slice(0, 8)"
          :key="item.chapterId + item.anchor"
          class="bookmark-row"
        >
          <RouterLink
            :to="`/ch/${item.chapterId}${item.anchor ? `#${item.anchor}` : ''}`"
            class="bookmark-link"
          >
            <span>{{ getChapter(item.chapterId)?.short }}</span>
            <strong>{{ item.heading }}</strong>
          </RouterLink>
          <button aria-label="移除收藏" @click="removeBookmark(item.chapterId, item.anchor)">
            <Icon name="x" />
          </button>
        </div>
      </div>
    </nav>

    <div class="sidebar-foot">
      <button class="foot-btn" @click="toggle">
        <Icon :name="isDark ? 'sun' : 'moon'" />
        <span>{{ isDark ? '浅色模式' : '深色模式' }}</span>
      </button>
      <a
        class="foot-btn"
        href="https://github.com/nichuan/xingce-guide"
        target="_blank"
        rel="noopener"
      >
        <Icon name="github" />
        <span>GitHub</span>
      </a>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-w);
  background: var(--c-surface);
  border-right: 1px solid var(--c-border);
  display: flex;
  flex-direction: column;
  padding: 18px 14px;
  gap: 14px;
  z-index: 95;
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(9, 12, 22, 0.5);
  backdrop-filter: blur(2px);
  z-index: 90;
}

/* 品牌 */
.brand {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 4px 6px;
  cursor: pointer;
  user-select: none;
}
.brand-logo {
  width: 38px;
  height: 38px;
  flex: none;
}
.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}
.brand-text strong {
  font-size: 17px;
  color: var(--c-text-strong);
  letter-spacing: 0.02em;
}
.brand-text span {
  font-size: 11.5px;
  color: var(--c-text-soft);
}

/* 搜索按钮 */
.search-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 9px 12px;
  border: 1px solid var(--c-border);
  border-radius: 10px;
  background: var(--c-bg);
  color: var(--c-text-faint);
  font-size: 13px;
  cursor: pointer;
  transition:
    border-color 0.2s,
    color 0.2s;
}
.search-trigger:hover {
  border-color: var(--c-primary);
  color: var(--c-text-soft);
}
.search-trigger svg {
  width: 15px;
  height: 15px;
  flex: none;
}
.search-trigger span {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
}
.search-trigger kbd {
  font-family: var(--font-sans);
  font-size: 10.5px;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  border-radius: 5px;
  padding: 1px 6px;
  color: var(--c-text-faint);
}

/* 导航 */
.nav {
  flex: 1;
  overflow-y: auto;
  overscroll-behavior: contain;
  margin: 0 -6px;
  padding: 0 6px;
}
.nav-group {
  margin-bottom: 14px;
}
.nav-group-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.14em;
  color: var(--c-text-faint);
  padding: 0 10px 7px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7.5px 10px;
  border-radius: 10px;
  color: var(--c-text);
  font-size: 14px;
  margin-bottom: 2px;
  transition:
    background 0.18s var(--ease),
    color 0.18s var(--ease);
}
.nav-item:hover {
  background: var(--c-bg);
  color: var(--c-text-strong);
}
.nav-item.active {
  background: var(--c-primary-soft);
  color: var(--c-primary-strong);
  font-weight: 600;
}
.nav-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  flex: none;
}
.nav-icon svg {
  width: 15.5px;
  height: 15.5px;
}
.nav-text {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}
.nav-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nav-badge {
  flex: none;
  font-size: 10.5px;
  font-weight: 600;
  color: var(--c-text-soft);
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 999px;
  padding: 0 7px;
  line-height: 1.7;
}
.nav-done {
  width: 14px;
  height: 14px;
  color: var(--c-ok);
  flex: none;
}
.formula-icon {
  color: var(--c-primary);
  background: var(--c-primary-soft);
}
.bookmarks {
  border-top: 1px solid var(--c-border);
  padding-top: 12px;
}
.bookmark-row {
  display: flex;
  align-items: center;
  gap: 4px;
  border-radius: 9px;
}
.bookmark-row:hover {
  background: var(--c-bg);
}
.bookmark-link {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 6px 8px;
  color: var(--c-text-soft);
  line-height: 1.35;
}
.bookmark-link span {
  font-size: 10.5px;
  color: var(--c-text-faint);
}
.bookmark-link strong {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-text);
}
.bookmark-row button {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 0;
  background: transparent;
  color: var(--c-text-faint);
  cursor: pointer;
}
.bookmark-row button:hover {
  color: var(--c-danger);
}
.bookmark-row button svg {
  width: 13px;
  height: 13px;
}
.nav-item.active .nav-badge {
  color: var(--c-primary-strong);
  background: var(--c-surface);
  border-color: color-mix(in srgb, var(--c-primary) 30%, transparent);
}

/* 底部 */
.sidebar-foot {
  display: flex;
  gap: 8px;
  border-top: 1px solid var(--c-border);
  padding-top: 12px;
}
.foot-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 8px;
  border: 1px solid var(--c-border);
  border-radius: 10px;
  background: var(--c-surface);
  color: var(--c-text-soft);
  font-size: 12.5px;
  cursor: pointer;
  transition:
    color 0.2s,
    border-color 0.2s;
}
.foot-btn:hover {
  color: var(--c-primary);
  border-color: var(--c-primary);
}
.foot-btn svg {
  width: 15px;
  height: 15px;
}

/* 移动端抽屉 */
.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.25s;
}
.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}
@media (max-width: 1023.98px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.28s var(--ease);
    box-shadow: none;
    width: min(84vw, 320px);
  }
  .sidebar.open {
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
  }
  .search-trigger kbd {
    display: none;
  }
}
@media (min-width: 1024px) {
  .sidebar-overlay {
    display: none;
  }
}
</style>
