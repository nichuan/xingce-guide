<script setup lang="ts">
import type { TocItem } from '../lib/markdown'

defineProps<{
  toc: TocItem[]
  activeId: string
}>()

const emit = defineEmits<{ jump: [id: string] }>()
</script>

<template>
  <nav class="toc" aria-label="本页目录">
    <div class="toc-label">本页目录</div>
    <!-- hash 路由下普通锚点会破坏地址，改为受控滚动 -->
    <a
      v-for="item in toc"
      :key="item.id"
      :href="`#${item.id}`"
      class="toc-item"
      :class="[`lv${item.level}`, { active: item.id === activeId }]"
      @click.prevent="emit('jump', item.id)"
    >
      {{ item.text }}
    </a>
  </nav>
</template>

<style scoped>
.toc {
  display: flex;
  flex-direction: column;
  gap: 1px;
}
.toc-label {
  font-size: 11.5px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: var(--c-text-faint);
  margin-bottom: 8px;
  padding-left: 12px;
}
.toc-item {
  position: relative;
  padding: 5px 10px 5px 12px;
  font-size: 12.8px;
  line-height: 1.5;
  color: var(--c-text-soft);
  border-left: 2px solid var(--c-border);
  text-decoration: none;
  transition: color 0.18s, border-color 0.18s;
  max-height: 5.5em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.toc-item:hover {
  color: var(--c-text-strong);
}
.toc-item.active {
  color: var(--c-primary);
  border-left-color: var(--c-primary);
  font-weight: 600;
}
.toc-item.lv3 {
  padding-left: 24px;
}
.toc-item.lv4 {
  padding-left: 36px;
  font-size: 12.2px;
}
</style>
