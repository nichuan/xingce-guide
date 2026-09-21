<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Icon from './Icon.vue'
import { buildSearchIndex, type SearchSection } from '../lib/markdown'
import { loadAllContents } from '../content/load'
import { chapters } from '../content/chapters'
import { ui } from '../lib/ui'
import { searchSections } from '../lib/search'

const router = useRouter()
const query = ref('')
const inputEl = ref<HTMLInputElement>()
const panelEl = ref<HTMLElement>()
const activeIdx = ref(0)
const loading = ref(true)
const searchIndex = ref<SearchSection[]>([])
let previouslyFocused: HTMLElement | null = null

const hits = computed(() => searchSections(searchIndex.value, query.value))

watch(query, () => {
  activeIdx.value = 0
})
watch(hits, (items) => {
  activeIdx.value = items.length ? Math.min(activeIdx.value, items.length - 1) : 0
})

function go(hit: (typeof hits.value)[number]) {
  ui.searchOpen = false
  router.push(`/ch/${hit.chapterId}#${hit.anchor}`)
}

function onKey(e: KeyboardEvent) {
  if (!hits.value.length && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
    e.preventDefault()
    return
  }
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIdx.value = Math.min(activeIdx.value + 1, hits.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIdx.value = Math.max(activeIdx.value - 1, 0)
  } else if (e.key === 'Enter' && hits.value[activeIdx.value]) {
    go(hits.value[activeIdx.value])
  }
}

function trapFocus(e: KeyboardEvent) {
  if (e.key !== 'Tab' || !panelEl.value) return
  const focusable = Array.from(
    panelEl.value.querySelectorAll<HTMLElement>(
      'button:not([disabled]), input:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])',
    ),
  )
  if (!focusable.length) return
  const first = focusable[0]
  const last = focusable[focusable.length - 1]
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault()
    last.focus()
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault()
    first.focus()
  }
}

const chapterColor = (id: string) => chapters.find((c) => c.id === id)?.color ?? 'var(--c-primary)'

onMounted(async () => {
  previouslyFocused = document.activeElement as HTMLElement | null
  await nextTick()
  inputEl.value?.focus()
  try {
    const contents = await loadAllContents()
    searchIndex.value = chapters.flatMap((chapter) =>
      buildSearchIndex(chapter.id, chapter.short, contents[chapter.id] ?? ''),
    )
  } finally {
    loading.value = false
  }
})

onUnmounted(() => previouslyFocused?.focus())
</script>

<template>
  <Teleport to="body">
    <div class="search-mask" @click.self="ui.searchOpen = false">
      <div
        ref="panelEl"
        class="search-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-title"
        @keydown="trapFocus"
      >
        <h2 id="search-title" class="sr-only">站内搜索</h2>
        <div class="search-head">
          <Icon name="search" />
          <input
            ref="inputEl"
            v-model="query"
            aria-label="搜索考点、公式和技巧"
            role="combobox"
            aria-controls="search-results"
            aria-autocomplete="list"
            :aria-expanded="hits.length > 0"
            :aria-activedescendant="hits[activeIdx] ? `search-hit-${activeIdx}` : undefined"
            placeholder="搜索考点、公式、技巧……"
            @keydown="onKey"
          />
          <button class="close-btn" aria-label="关闭" @click="ui.searchOpen = false">
            <Icon name="x" />
          </button>
        </div>

        <div id="search-results" class="search-body" role="listbox" aria-label="搜索结果">
          <template v-if="loading">
            <div class="search-empty" role="status">正在加载搜索索引……</div>
          </template>
          <template v-else-if="!query.trim()">
            <div class="search-empty">
              <p>试试这些关键词：</p>
              <div class="hot-words">
                <button
                  v-for="w in ['基期量', '十字交叉', '翻译推理', '一笔画', '差分法', '成语']"
                  :key="w"
                  @click="query = w"
                >
                  {{ w }}
                </button>
              </div>
            </div>
          </template>
          <template v-else-if="hits.length === 0">
            <div class="search-empty">没有找到与「{{ query }}」相关的内容</div>
          </template>
          <template v-else>
            <button
              v-for="(hit, i) in hits"
              :id="`search-hit-${i}`"
              :key="hit.chapterId + hit.anchor"
              class="hit"
              role="option"
              :aria-selected="i === activeIdx"
              :class="{ active: i === activeIdx }"
              :data-active="i === activeIdx"
              @click="go(hit)"
              @mousemove="activeIdx = i"
            >
              <div class="hit-head">
                <span
                  class="hit-chip"
                  :style="{
                    color: chapterColor(hit.chapterId),
                    background: chapterColor(hit.chapterId) + '1a',
                  }"
                >
                  {{ hit.chapterTitle }}
                </span>
                <span class="hit-heading">{{ hit.heading }}</span>
              </div>
              <div class="hit-snippet" v-html="hit.snippet"></div>
            </button>
          </template>
        </div>

        <div class="search-foot">
          <span><kbd>↑</kbd><kbd>↓</kbd> 选择</span>
          <span><kbd>Enter</kbd> 跳转</span>
          <span><kbd>Esc</kbd> 关闭</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.search-mask {
  position: fixed;
  inset: 0;
  background: rgba(9, 12, 22, 0.55);
  backdrop-filter: blur(3px);
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 9vh 16px 16px;
}
.search-panel {
  width: min(620px, 100%);
  max-height: 72vh;
  display: flex;
  flex-direction: column;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  animation: pop 0.18s var(--ease);
}
@keyframes pop {
  from {
    transform: translateY(10px) scale(0.985);
    opacity: 0;
  }
}
.search-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px;
  border-bottom: 1px solid var(--c-border);
  color: var(--c-text-faint);
}
.search-head > svg {
  width: 17px;
  height: 17px;
  flex: none;
}
.search-head input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15.5px;
  color: var(--c-text-strong);
  padding: 11px 0;
  font-family: inherit;
}
.search-head input::placeholder {
  color: var(--c-text-faint);
}
.close-btn {
  border: none;
  background: transparent;
  color: var(--c-text-faint);
  cursor: pointer;
  display: grid;
  place-items: center;
  padding: 6px;
  border-radius: 8px;
}
.close-btn:hover {
  color: var(--c-text-strong);
  background: var(--c-bg);
}
.close-btn svg {
  width: 16px;
  height: 16px;
}

.search-body {
  flex: 1;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 8px;
}
.search-empty {
  padding: 34px 16px;
  text-align: center;
  color: var(--c-text-soft);
  font-size: 14px;
}
.hot-words {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}
.hot-words button {
  border: 1px solid var(--c-border);
  background: var(--c-bg);
  color: var(--c-text);
  border-radius: 999px;
  padding: 5px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.18s;
}
.hot-words button:hover {
  border-color: var(--c-primary);
  color: var(--c-primary);
  background: var(--c-primary-soft);
}

.hit {
  display: block;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
}
.hit.active {
  background: var(--c-primary-soft);
}
.hit-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 3px;
  min-width: 0;
}
.hit-chip {
  flex: none;
  font-size: 11px;
  font-weight: 600;
  border-radius: 999px;
  padding: 1px 9px;
}
.hit-heading {
  font-size: 14px;
  font-weight: 650;
  color: var(--c-text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.hit-snippet {
  font-size: 12.8px;
  color: var(--c-text-soft);
  line-height: 1.6;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.hit-snippet :deep(mark) {
  background: color-mix(in srgb, var(--c-warn) 30%, transparent);
  color: inherit;
  border-radius: 3px;
  padding: 0 1px;
}

.search-foot {
  display: flex;
  gap: 16px;
  padding: 9px 16px;
  border-top: 1px solid var(--c-border);
  color: var(--c-text-faint);
  font-size: 12px;
}
.search-foot span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.search-foot kbd {
  font-family: var(--font-sans);
  border: 1px solid var(--c-border);
  background: var(--c-bg);
  border-radius: 5px;
  padding: 0 5px;
  font-size: 11px;
}
@media (max-width: 640px) {
  .search-foot {
    display: none;
  }
  .search-mask {
    padding-top: 6vh;
  }
}
</style>
