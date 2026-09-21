<script setup lang="ts">
import Icon from '../components/Icon.vue'
</script>

<template>
  <main class="not-found">
    <span>404</span>
    <h1>这一页不在题册里</h1>
    <p>链接可能已经调整，返回首页后可以通过章节导航或搜索继续学习。</p>
    <RouterLink to="/" class="back-home"><Icon name="home" />返回首页</RouterLink>
  </main>
</template>

<style scoped>
.not-found {
  min-height: calc(100dvh - var(--topbar-h));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 20px;
  text-align: center;
}
.not-found > span {
  font-size: clamp(70px, 18vw, 140px);
  font-weight: 900;
  line-height: 1;
  background: var(--c-grad);
  background-clip: text;
  color: transparent;
  opacity: 0.3;
}
.not-found h1 {
  margin-top: -8px;
  font-size: 26px;
}
.not-found p {
  max-width: 440px;
  color: var(--c-text-soft);
}
.back-home {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: 12px;
  padding: 9px 16px;
  border-radius: 10px;
  color: #fff;
  background: var(--c-grad);
}
.back-home svg {
  width: 16px;
}
</style>
