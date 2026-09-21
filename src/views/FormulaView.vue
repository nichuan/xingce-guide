<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Icon from '../components/Icon.vue'
import { chapters } from '../content/chapters'
import { loadAllContents } from '../content/load'
import { extractContainers } from '../lib/markdown'

interface FormulaItem {
  chapterId: string
  chapterTitle: string
  color: string
  title: string
  html: string
}

const loading = ref(true)
const query = ref('')
const selected = ref('all')
const formulas = ref<FormulaItem[]>([])

const availableChapters = computed(() =>
  chapters.filter((chapter) => formulas.value.some((item) => item.chapterId === chapter.id)),
)

const filtered = computed(() => {
  const keyword = query.value.trim().toLowerCase()
  return formulas.value.filter((item) => {
    const inChapter = selected.value === 'all' || item.chapterId === selected.value
    const inQuery = !keyword || `${item.title} ${item.chapterTitle}`.toLowerCase().includes(keyword)
    return inChapter && inQuery
  })
})

onMounted(async () => {
  try {
    const contents = await loadAllContents()
    formulas.value = chapters.flatMap((chapter) =>
      extractContainers(contents[chapter.id] ?? '', 'formula').map((formula) => ({
        chapterId: chapter.id,
        chapterTitle: chapter.short,
        color: chapter.color,
        ...formula,
      })),
    )
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="formula-page">
    <header class="formula-hero">
      <span class="formula-icon"><Icon name="sigma" /></span>
      <div>
        <p>速查工具</p>
        <h1>全部公式</h1>
        <span>自动聚合各章公式卡，按模块筛选，复习时无需来回翻页。</span>
      </div>
    </header>

    <div class="formula-tools">
      <label>
        <span class="sr-only">搜索公式</span>
        <Icon name="search" />
        <input v-model="query" type="search" placeholder="搜索公式名称……" />
      </label>
      <div class="formula-filters" aria-label="按章节筛选">
        <button :class="{ active: selected === 'all' }" @click="selected = 'all'">全部</button>
        <button
          v-for="chapter in availableChapters"
          :key="chapter.id"
          :class="{ active: selected === chapter.id }"
          @click="selected = chapter.id"
        >
          {{ chapter.short }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="formula-state" role="status">正在整理公式……</div>
    <div v-else-if="!filtered.length" class="formula-state">没有匹配的公式</div>
    <section v-else class="formula-list" aria-live="polite">
      <article
        v-for="(item, index) in filtered"
        :key="`${item.chapterId}-${index}`"
        class="formula-item"
      >
        <div class="formula-item-head">
          <span :style="{ color: item.color, background: item.color + '1a' }">{{
            item.chapterTitle
          }}</span>
          <h2>{{ item.title }}</h2>
          <RouterLink :to="`/ch/${item.chapterId}`">查看原章</RouterLink>
        </div>
        <div class="prose formula-content" v-html="item.html"></div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.formula-page {
  width: min(900px, 100%);
  margin: 0 auto;
  padding: 42px 20px 72px;
}
.formula-hero {
  display: flex;
  gap: 18px;
  align-items: center;
  margin-bottom: 28px;
}
.formula-icon {
  width: 56px;
  height: 56px;
  display: grid;
  place-items: center;
  flex: none;
  border-radius: 16px;
  color: var(--c-primary);
  background: var(--c-primary-soft);
}
.formula-icon svg {
  width: 27px;
  height: 27px;
}
.formula-hero p,
.formula-hero h1 {
  margin: 0;
}
.formula-hero p {
  color: var(--c-primary);
  font-size: 12px;
  font-weight: 700;
}
.formula-hero h1 {
  font-size: clamp(26px, 5vw, 36px);
}
.formula-hero div > span {
  color: var(--c-text-soft);
  font-size: 14px;
}
.formula-tools {
  position: sticky;
  top: 12px;
  z-index: 5;
  padding: 12px;
  margin-bottom: 20px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  background: color-mix(in srgb, var(--c-surface) 92%, transparent);
  backdrop-filter: blur(10px);
}
.formula-tools label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 10px;
  border: 1px solid var(--c-border);
  border-radius: 9px;
  background: var(--c-bg);
}
.formula-tools label svg {
  width: 15px;
  color: var(--c-text-faint);
}
.formula-tools input {
  width: 100%;
  border: 0;
  outline: 0;
  padding: 9px 0;
  background: transparent;
  color: var(--c-text-strong);
}
.formula-filters {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding-top: 10px;
}
.formula-filters button {
  flex: none;
  border: 1px solid var(--c-border);
  border-radius: 999px;
  padding: 4px 11px;
  background: var(--c-surface);
  color: var(--c-text-soft);
  cursor: pointer;
}
.formula-filters button.active {
  border-color: var(--c-primary);
  background: var(--c-primary-soft);
  color: var(--c-primary);
}
.formula-list {
  display: grid;
  gap: 14px;
}
.formula-item {
  padding: 18px 20px;
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  background: var(--c-surface);
}
.formula-item-head {
  display: flex;
  align-items: center;
  gap: 9px;
}
.formula-item-head > span {
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}
.formula-item-head h2 {
  flex: 1;
  font-size: 16px;
}
.formula-item-head a {
  font-size: 12px;
}
.formula-content :deep(.katex-display) {
  margin-bottom: 0;
}
.formula-state {
  min-height: 40vh;
  display: grid;
  place-items: center;
  color: var(--c-text-soft);
}
@media (max-width: 600px) {
  .formula-page {
    padding-top: 28px;
  }
  .formula-item-head {
    flex-wrap: wrap;
  }
  .formula-item-head h2 {
    min-width: 50%;
  }
}
</style>
