<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import SiteSidebar from './components/SiteSidebar.vue'
import TopBar from './components/TopBar.vue'
import SearchModal from './components/SearchModal.vue'
import { ui, closeAll } from './lib/ui'

const route = useRoute()

// 快捷键：Ctrl/Cmd+K 搜索，Esc 关闭所有浮层
function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    ui.searchOpen = true
  } else if (e.key === 'Escape') {
    closeAll()
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

// 路由切换后关闭移动端浮层
watch(() => route.fullPath, closeAll)

// 抽屉打开时锁定背景滚动
watch(
  () => ui.sidebarOpen || ui.tocOpen || ui.searchOpen,
  (locked) => {
    document.body.style.overflow = locked ? 'hidden' : ''
  },
)
</script>

<template>
  <div class="app" :data-route="route.name">
    <SiteSidebar />
    <div class="app-main">
      <TopBar :chapter-id="(route.params.id as string) || undefined" />
      <router-view />
    </div>
    <SearchModal v-if="ui.searchOpen" />
  </div>
</template>

<style scoped>
.app {
  min-height: 100dvh;
}
.app-main {
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}
@media (min-width: 1024px) {
  .app-main {
    margin-left: var(--sidebar-w);
  }
}
</style>
