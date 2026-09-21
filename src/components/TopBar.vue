<script setup lang="ts">
import { computed } from 'vue'
import Icon from './Icon.vue'
import { ui } from '../lib/ui'
import { useTheme } from '../lib/theme'
import { getChapter } from '../content/chapters'

const { isDark, toggle } = useTheme()

const props = defineProps<{ chapterId?: string }>()
const chapter = computed(() => (props.chapterId ? getChapter(props.chapterId) : undefined))
</script>

<template>
  <header class="topbar">
    <button
      class="icon-btn"
      aria-label="打开导航"
      aria-controls="site-sidebar"
      :aria-expanded="ui.sidebarOpen"
      @click="ui.sidebarOpen = true"
    >
      <Icon name="menu" />
    </button>
    <div class="topbar-title">
      <template v-if="chapter">
        <span class="crumb-num" :style="{ color: chapter.color }">{{ chapter.num }}</span>
        {{ chapter.short }}
      </template>
      <template v-else>行测指南</template>
    </div>
    <div class="topbar-actions">
      <button class="icon-btn" aria-label="搜索" @click="ui.searchOpen = true">
        <Icon name="search" />
      </button>
      <button class="icon-btn" aria-label="切换主题" @click="toggle">
        <Icon :name="isDark ? 'sun' : 'moon'" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  position: sticky;
  top: 0;
  height: var(--topbar-h);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  background: color-mix(in srgb, var(--c-bg) 82%, transparent);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--c-border);
  z-index: 40;
}
.topbar-title {
  flex: 1;
  min-width: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--c-text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.crumb-num {
  font-weight: 700;
  margin-right: 2px;
}
.topbar-actions {
  display: flex;
  gap: 4px;
}
.icon-btn {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: var(--c-text-soft);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition:
    background 0.18s,
    color 0.18s;
}
.icon-btn:hover {
  background: var(--c-primary-soft);
  color: var(--c-primary);
}
.icon-btn svg {
  width: 19px;
  height: 19px;
}

/* 桌面端隐藏顶栏（侧边栏已含全部导航） */
@media (min-width: 1024px) {
  .topbar {
    display: none;
  }
}
</style>
