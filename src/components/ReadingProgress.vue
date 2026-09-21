<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import Icon from './Icon.vue'

const progress = ref(0)
const showTop = ref(false)
let raf = 0

function onScroll() {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(() => {
    const doc = document.documentElement
    const total = doc.scrollHeight - doc.clientHeight
    progress.value = total > 0 ? Math.min(100, (doc.scrollTop / total) * 100) : 0
    showTop.value = doc.scrollTop > 640
  })
}

function toTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  cancelAnimationFrame(raf)
})
</script>

<template>
  <Teleport to="body">
    <div class="progress-track" aria-hidden="true">
      <div class="progress-bar" :style="{ width: progress + '%' }"></div>
    </div>
    <Transition name="pop">
      <button v-if="showTop" class="back-top" aria-label="回到顶部" @click="toTop">
        <Icon name="arrow-up" />
      </button>
    </Transition>
  </Teleport>
</template>

<style scoped>
.progress-track {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 80;
  pointer-events: none;
}
.progress-bar {
  height: 100%;
  background: var(--c-grad);
  border-radius: 0 3px 3px 0;
  transition: width 0.08s linear;
}
.back-top {
  position: fixed;
  right: 22px;
  bottom: 96px;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 1px solid var(--c-border);
  background: var(--c-surface);
  color: var(--c-text-soft);
  display: grid;
  place-items: center;
  cursor: pointer;
  box-shadow: var(--shadow-md);
  z-index: 60;
  transition:
    color 0.2s,
    border-color 0.2s,
    transform 0.2s;
}
.back-top:hover {
  color: var(--c-primary);
  border-color: var(--c-primary);
  transform: translateY(-2px);
}
.back-top svg {
  width: 18px;
  height: 18px;
}
.pop-enter-active,
.pop-leave-active {
  transition:
    opacity 0.2s,
    transform 0.2s;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
@media (min-width: 1024px) {
  .back-top {
    bottom: 34px;
  }
}
</style>
