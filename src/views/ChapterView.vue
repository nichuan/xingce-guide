<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Icon from '../components/Icon.vue'
import TocPanel from '../components/TocPanel.vue'
import ReadingProgress from '../components/ReadingProgress.vue'
import { renderMarkdown, type TocItem } from '../lib/markdown'
import { rawContents } from '../content/load'
import { chapters, getChapter } from '../content/chapters'
import { ui } from '../lib/ui'
import { scrollToId } from '../router'

const route = useRoute()
const router = useRouter()

const chapter = computed(() => getChapter(route.params.id as string))
const content = computed(() => rawContents[chapter.value?.id ?? ''] ?? '')
const rendered = computed(() => renderMarkdown(content.value, chapter.value?.id ?? ''))

const toc = computed<TocItem[]>(() => rendered.value.toc)
const html = computed(() => rendered.value.html)

const idx = computed(() => chapters.findIndex((c) => c.id === chapter.value?.id))
const prev = computed(() => (idx.value > 0 ? chapters[idx.value - 1] : undefined))
const next = computed(() => (idx.value < chapters.length - 1 ? chapters[idx.value + 1] : undefined))

/* ---------- 滚动侦测（目录高亮 + 阅读进度） ---------- */
const articleEl = ref<HTMLElement>()
const activeId = ref('')

let headingEls: HTMLElement[] = []
let rafId = 0

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
  })
}

watch(html, async () => {
  if (!chapter.value) {
    router.replace('/')
    return
  }
  activeId.value = ''
  await nextTick()
  refreshHeadings()
  // 等字体/公式渲染完成后重算一次
  setTimeout(refreshHeadings, 350)
})

function onTocJump(id: string) {
  ui.tocOpen = false
  scrollToId(id)
  // 仅更新地址栏，便于分享锚点；不触发路由导航
  history.replaceState(history.state, '', `${location.pathname}#/ch/${chapter.value?.id ?? ''}#${id}`)
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
})
</script>

<template>
  <ReadingProgress />

  <div v-if="chapter" class="chapter-page">
    <div class="chapter-layout">
      <!-- 主栏 -->
      <article class="chapter-main">
        <header class="chapter-header">
          <span class="chapter-icon" :style="{ color: chapter.color, background: chapter.color + '1a' }">
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
          </div>
        </header>

        <!-- 移动端目录折叠条 -->
        <button class="toc-toggle" @click="ui.tocOpen = true">
          <Icon name="list" />
          <span>本页目录（{{ toc.length }} 节）</span>
          <Icon name="chevron-right" />
        </button>

        <div ref="articleEl" class="prose" v-html="html"></div>

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
      <div v-if="ui.tocOpen" class="toc-sheet">
        <div class="sheet-head">
          <strong>本页目录</strong>
          <button aria-label="关闭" @click="ui.tocOpen = false"><Icon name="x" /></button>
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
  transition: border-color 0.2s, transform 0.2s var(--ease), box-shadow 0.2s;
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
