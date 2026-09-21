<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import TocPanel from '../components/TocPanel.vue'
import ReadingProgress from '../components/ReadingProgress.vue'
import { renderMarkdown, type TocItem } from '../lib/markdown'
import { loadContent } from '../content/load'
import { chapters, getChapter } from '../content/chapters'
import { ui } from '../lib/ui'
import { scrollToId } from '../router'
import {
  isBookmarked,
  learning,
  recordProgress,
  selfTestMode,
  toggleBookmark,
  toggleSelfTest,
} from '../lib/learning'

const route = useRoute()
const router = useRouter()

const chapter = computed(() => getChapter(route.params.id as string))
const content = ref('')
const loading = ref(true)
const loadError = ref(false)
const rendered = computed(() =>
  content.value
    ? renderMarkdown(content.value, chapter.value?.id ?? '')
    : { html: '', toc: [] as TocItem[] },
)

const toc = computed<TocItem[]>(() => rendered.value.toc)
const html = computed(() => rendered.value.html)

const idx = computed(() => chapters.findIndex((c) => c.id === chapter.value?.id))
const prev = computed(() => (idx.value > 0 ? chapters[idx.value - 1] : undefined))
const next = computed(() => (idx.value < chapters.length - 1 ? chapters[idx.value + 1] : undefined))

/* ---------- 滚动侦测（目录高亮 + 阅读进度） ---------- */
const articleEl = ref<HTMLElement>()
const tocSheetEl = ref<HTMLElement>()
const tocCloseEl = ref<HTMLButtonElement>()
const activeId = ref('')

let headingEls: HTMLElement[] = []
let rafId = 0
let refreshTimer = 0
let loadId = 0
let lastPersist = 0
let tocTrigger: HTMLElement | null = null
let readyForProgress = false

function refreshHeadings() {
  if (!articleEl.value) return
  headingEls = Array.from(articleEl.value.querySelectorAll('h2[id], h3[id], h4[id]'))
}

function onScroll() {
  cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    let current = ''
    for (const el of headingEls) {
      if (el.getBoundingClientRect().top <= 110) current = el.id
      else break
    }
    activeId.value = current
    const now = Date.now()
    if (readyForProgress && chapter.value && now - lastPersist > 600) {
      const doc = document.documentElement
      const total = doc.scrollHeight - doc.clientHeight
      recordProgress(chapter.value.id, current, total > 0 ? doc.scrollTop / total : 0)
      lastPersist = now
    }
  })
}

function applySolutionMode() {
  articleEl.value
    ?.querySelectorAll<HTMLDetailsElement>('details.example-solution')
    .forEach((item) => {
      item.open = !selfTestMode.value
    })
}

async function restoreProgress() {
  if (route.query.resume !== '1' || route.hash || !chapter.value) return
  const saved = learning.progress[chapter.value.id]
  if (saved?.anchor && scrollToId(saved.anchor)) return
  if (typeof saved?.ratio === 'number') {
    const doc = document.documentElement
    window.scrollTo({
      top: saved.ratio * (doc.scrollHeight - doc.clientHeight),
      behavior: 'smooth',
    })
  }
}

watch(
  () => chapter.value?.id,
  async (id) => {
    if (!id) return
    readyForProgress = false
    const currentLoad = ++loadId
    loading.value = true
    loadError.value = false
    try {
      const raw = await loadContent(id)
      if (currentLoad !== loadId) return
      content.value = raw
    } catch {
      if (currentLoad !== loadId) return
      content.value = ''
      loadError.value = true
    } finally {
      if (currentLoad === loadId) loading.value = false
    }
  },
  { immediate: true },
)

watch(html, async () => {
  activeId.value = ''
  await nextTick()
  refreshHeadings()
  applySolutionMode()
  await restoreProgress()
  readyForProgress = true
  // 等字体/公式渲染完成后重算一次
  window.clearTimeout(refreshTimer)
  refreshTimer = window.setTimeout(() => {
    refreshHeadings()
    onScroll()
  }, 350)
})

watch(selfTestMode, async () => {
  await nextTick()
  applySolutionMode()
})

watch(
  () => ui.tocOpen,
  async (open) => {
    if (open) {
      tocTrigger = document.activeElement as HTMLElement | null
      await nextTick()
      tocCloseEl.value?.focus()
    } else if (tocTrigger) {
      await nextTick()
      tocTrigger.focus()
      tocTrigger = null
    }
  },
)

function trapTocFocus(e: KeyboardEvent) {
  if (e.key !== 'Tab' || !tocSheetEl.value) return
  const focusable = Array.from(
    tocSheetEl.value.querySelectorAll<HTMLElement>('a[href], button:not([disabled])'),
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

function onTocJump(id: string) {
  ui.tocOpen = false
  scrollToId(id)
  void router.replace({
    name: 'chapter',
    params: { id: chapter.value?.id },
    hash: `#${id}`,
  })
}

const currentHeading = computed(
  () =>
    toc.value.find((item) => item.id === activeId.value)?.text ?? chapter.value?.short ?? '本章',
)
const bookmarked = computed(() =>
  chapter.value ? isBookmarked(chapter.value.id, activeId.value) : false,
)

function onBookmark() {
  if (!chapter.value) return
  toggleBookmark(chapter.value.id, activeId.value, currentHeading.value)
}

onMounted(async () => {
  await nextTick()
  refreshHeadings()
  window.addEventListener('scroll', onScroll, { passive: true })
  window.addEventListener('resize', onScroll, { passive: true })
  onScroll()
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  window.removeEventListener('resize', onScroll)
  cancelAnimationFrame(rafId)
  window.clearTimeout(refreshTimer)
  if (readyForProgress && chapter.value) {
    const doc = document.documentElement
    const total = doc.scrollHeight - doc.clientHeight
    recordProgress(chapter.value.id, activeId.value, total > 0 ? doc.scrollTop / total : 0)
  }
})
</script>

<template>
  <ReadingProgress />

  <div v-if="chapter" class="chapter-page">
    <div class="chapter-layout">
      <!-- 主栏 -->
      <article class="chapter-main">
        <header class="chapter-header">
          <span
            class="chapter-icon"
            :style="{ color: chapter.color, background: chapter.color + '1a' }"
          >
            <Icon :name="chapter.icon" />
          </span>
          <div class="chapter-heading">
            <span class="chapter-num" :style="{ color: chapter.color }">{{ chapter.num }}</span>
            <h1>{{ chapter.title }}</h1>
          </div>
          <p class="chapter-desc">{{ chapter.desc }}</p>
          <div class="chapter-meta">
            <span v-if="chapter.questions" class="meta-chip">{{ chapter.questions }}</span>
            <span class="meta-chip">
              <Icon name="clock" />
              阅读约 {{ chapter.minutes }} 分钟
            </span>
            <span class="meta-chip">更新于 {{ chapter.lastUpdated }}</span>
          </div>
          <p class="chapter-scope">{{ chapter.applicableTo }} · 具体题量与政策以最新招考公告为准</p>
          <div class="study-actions">
            <button type="button" :aria-pressed="selfTestMode" @click="toggleSelfTest">
              <Icon name="target" />
              自测模式：{{ selfTestMode ? '开' : '关' }}
            </button>
            <button type="button" :aria-pressed="bookmarked" @click="onBookmark">
              <Icon name="bookmark" />
              {{ bookmarked ? '已收藏本节' : '收藏本节' }}
            </button>
          </div>
        </header>

        <!-- 移动端目录折叠条 -->
        <button class="toc-toggle" @click="ui.tocOpen = true">
          <Icon name="list" />
          <span>本页目录（{{ toc.length }} 节）</span>
          <Icon name="chevron-right" />
        </button>

        <div v-if="loading" class="chapter-state" role="status">正在加载章节内容……</div>
        <div v-else-if="loadError" class="chapter-state error" role="alert">
          章节加载失败，请刷新页面后重试。
        </div>
        <div v-else ref="articleEl" class="prose" v-html="html"></div>

        <!-- 上一篇 / 下一篇 -->
        <nav class="pn-nav">
          <RouterLink v-if="prev" :to="`/ch/${prev.id}`" class="pn-card">
            <span class="pn-label"><Icon name="arrow-left" /> 上一篇</span>
            <span class="pn-title">{{ prev.num }} · {{ prev.short }}</span>
          </RouterLink>
          <span v-else class="pn-card placeholder"></span>
          <RouterLink v-if="next" :to="`/ch/${next.id}`" class="pn-card next">
            <span class="pn-label">下一篇 <Icon name="arrow-right" /></span>
            <span class="pn-title">{{ next.num }} · {{ next.short }}</span>
          </RouterLink>
          <span v-else class="pn-card placeholder"></span>
        </nav>
      </article>

      <!-- 桌面端目录 -->
      <aside class="chapter-toc">
        <TocPanel :toc="toc" :active-id="activeId" @jump="onTocJump" />
      </aside>
    </div>
  </div>

  <!-- 移动端目录抽屉 -->
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="ui.tocOpen" class="toc-mask" @click="ui.tocOpen = false"></div>
    </Transition>
    <Transition name="sheet">
      <div
        v-if="ui.tocOpen"
        ref="tocSheetEl"
        class="toc-sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby="toc-sheet-title"
        @keydown="trapTocFocus"
      >
        <div class="sheet-head">
          <strong id="toc-sheet-title">本页目录</strong>
          <button ref="tocCloseEl" aria-label="关闭" @click="ui.tocOpen = false">
            <Icon name="x" />
          </button>
        </div>
        <div class="sheet-body">
          <TocPanel :toc="toc" :active-id="activeId" @jump="onTocJump" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.chapter-page {
  flex: 1;
}
.chapter-layout {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  padding: 26px 20px 30px;
}
@media (min-width: 1280px) {
  .chapter-layout {
    max-width: calc(800px + var(--toc-w) + 48px);
    display: grid;
    grid-template-columns: minmax(0, 1fr) var(--toc-w);
    gap: 44px;
    align-items: start;
  }
}

/* ---------- 头部 ---------- */
.chapter-header {
  padding: 6px 4px 20px;
  border-bottom: 1px solid var(--c-border);
  margin-bottom: 24px;
}
.chapter-icon {
  width: 46px;
  height: 46px;
  border-radius: 13px;
  display: grid;
  place-items: center;
  margin-bottom: 14px;
}
.chapter-icon svg {
  width: 22px;
  height: 22px;
}
.chapter-num {
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
}
.chapter-heading h1 {
  font-size: clamp(24px, 5vw, 32px);
  font-weight: 800;
  margin-top: 4px;
  line-height: 1.3;
}
.chapter-desc {
  color: var(--c-text-soft);
  font-size: 14.5px;
  line-height: 1.8;
  margin: 12px 0 14px;
}
.chapter-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--c-text-soft);
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 999px;
  padding: 3px 12px;
}
.meta-chip svg {
  width: 12px;
  height: 12px;
}
.chapter-scope {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--c-text-faint);
}
.study-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}
.study-actions button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 1px solid var(--c-border);
  border-radius: 9px;
  background: var(--c-surface);
  color: var(--c-text-soft);
  padding: 6px 10px;
  cursor: pointer;
}
.study-actions button[aria-pressed='true'] {
  color: var(--c-primary);
  border-color: color-mix(in srgb, var(--c-primary) 40%, var(--c-border));
  background: var(--c-primary-soft);
}
.study-actions svg {
  width: 14px;
  height: 14px;
}
.chapter-state {
  min-height: 36vh;
  display: grid;
  place-items: center;
  color: var(--c-text-soft);
}
.chapter-state.error {
  color: var(--c-danger);
}

/* ---------- 移动端目录按钮 ---------- */
.toc-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  margin-bottom: 18px;
  padding: 10px 14px;
  border: 1px dashed var(--c-border-strong);
  border-radius: 11px;
  background: var(--c-surface-2);
  color: var(--c-text-soft);
  font-size: 13.5px;
  cursor: pointer;
}
.toc-toggle svg {
  width: 15px;
  height: 15px;
}
.toc-toggle span {
  flex: 1;
  text-align: left;
}
.toc-toggle:last-child {
  color: var(--c-text-faint);
}
@media (min-width: 1280px) {
  .toc-toggle {
    display: none;
  }
}

/* ---------- 目录侧栏 ---------- */
.chapter-toc {
  display: none;
}
@media (min-width: 1280px) {
  .chapter-toc {
    display: block;
    position: sticky;
    top: 30px;
    max-height: calc(100dvh - 60px);
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 6px 2px 20px;
  }
}

/* ---------- 上一篇/下一篇 ---------- */
.pn-nav {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 44px;
  padding-top: 22px;
  border-top: 1px solid var(--c-border);
}
.pn-card {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 14px 16px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  transition:
    border-color 0.2s,
    transform 0.2s var(--ease),
    box-shadow 0.2s;
}
.pn-card:not(.placeholder):hover {
  border-color: var(--c-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}
.pn-card.placeholder {
  visibility: hidden;
}
.pn-card.next {
  text-align: right;
}
.pn-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: var(--c-text-faint);
}
.pn-label svg {
  width: 13px;
  height: 13px;
}
.pn-title {
  font-size: 14px;
  font-weight: 650;
  color: var(--c-text-strong);
}
.next .pn-label {
  justify-content: flex-end;
}

/* ---------- 移动端目录抽屉 ---------- */
.toc-mask {
  position: fixed;
  inset: 0;
  background: rgba(9, 12, 22, 0.5);
  z-index: 94;
}
.toc-sheet {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  max-height: 72dvh;
  background: var(--c-surface);
  border-radius: 18px 18px 0 0;
  box-shadow: var(--shadow-lg);
  z-index: 96;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}
.sheet-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 20px 12px;
  border-bottom: 1px solid var(--c-border);
  color: var(--c-text-strong);
}
.sheet-head button {
  border: none;
  background: transparent;
  color: var(--c-text-faint);
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 4px;
}
.sheet-head button svg {
  width: 17px;
  height: 17px;
}
.sheet-body {
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 14px 20px 22px;
}
.sheet-body :deep(.toc-label) {
  display: none;
}
.overlay-enter-active,
.overlay-leave-active {
  transition: opacity 0.22s;
}
.overlay-enter-from,
.overlay-leave-to {
  opacity: 0;
}
.sheet-enter-active,
.sheet-leave-active {
  transition: transform 0.26s var(--ease);
}
.sheet-enter-from,
.sheet-leave-to {
  transform: translateY(100%);
}
</style>
