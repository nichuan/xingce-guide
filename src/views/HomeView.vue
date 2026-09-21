<script setup lang="ts">
import { computed } from 'vue'
import Icon from '../components/Icon.vue'
import { chapters, chapterGroups, getChapter } from '../content/chapters'
import { renderMarkdown } from '../lib/markdown'
import { completedCount, latestProgress } from '../lib/learning'

const continueChapter = computed(() =>
  latestProgress.value ? getChapter(latestProgress.value.chapterId) : undefined,
)
const continueTo = computed(() => {
  const item = latestProgress.value
  if (!item) return '/ch/intro'
  return `/ch/${item.chapterId}?resume=1`
})

const featureFormulas = [
  {
    title: '基期量',
    source: '$$\\text{基期量} = \\frac{\\text{现期量}}{1 + r}$$',
    link: '/ch/ziliao',
    note: '资料分析 · 最高频公式',
  },
  {
    title: '间隔增长率',
    source: '$$R = r_1 + r_2 + r_1 r_2$$',
    link: '/ch/ziliao',
    note: '两期增长率合并，小增长率可忽略乘积项',
  },
  {
    title: '十字交叉',
    source: '$$\\frac{A}{B} = \\frac{\\lvert r - b \\rvert}{\\lvert a - r \\rvert}$$',
    link: '/ch/shuliang',
    note: '平均数 / 浓度 / 增长率混合通解',
  },
].map((f, i) => ({ ...f, html: renderMarkdown(f.source, `home-f${i}`).html }))

const features = [
  {
    icon: 'layers',
    color: '#4f46e5',
    title: '方法体系化',
    desc: '每个考点都归结为"题型识别 → 核心方法 → 技巧清单"的三段式，先建框架，再练方法，最后练节奏。',
  },
  {
    icon: 'target',
    color: '#0ea5e9',
    title: '例题驱动',
    desc: '33 道精讲例题覆盖六大模块，每道都演示完整的思考路径——先判断考点归属，再套标准解法。',
  },
  {
    icon: 'zap',
    color: '#d97706',
    title: '速查即所得',
    desc: '速算对照表、核心公式速查、易错成语清单随手可查，配合 Ctrl + K 全站搜索，刷题复盘两不误。',
  },
]

const steps = [
  {
    stage: '第一阶段',
    name: '基础奠基',
    weeks: '约 4～6 周',
    desc: '过一遍六大模块考点清单，见到题知道考什么。不追求正确率，建立成语本、图形本、速算本。',
    to: '/ch/intro',
  },
  {
    stage: '第二阶段',
    name: '专项强化',
    weeks: '约 4～6 周',
    desc: '按模块集中刷真题，正确率拉到 70% 以上。重点突破资料分析与判断推理，每天复盘错因。',
    to: '/ch/beikao',
  },
  {
    stage: '第三阶段',
    name: '套题冲刺',
    weeks: '约 3～4 周',
    desc: '严格 120 分钟整卷训练，固定做题顺序，练出"战略性放弃"的肌肉记忆。',
    to: '/ch/beikao',
  },
]

const stats = [
  { value: '6', label: '大模块' },
  { value: '9', label: '章完整讲义' },
  { value: '33', label: '道精讲例题' },
  { value: '135', label: '题全卷结构' },
]
</script>

<template>
  <main class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-bg" aria-hidden="true"></div>
      <div class="hero-inner">
        <span class="hero-badge">公务员考试 · 行政职业能力测验</span>
        <h1 class="hero-title">
          行测，<br class="hero-br" />考的是<span class="hero-grad">方法</span>
        </h1>
        <p class="hero-sub">
          题量大、时间紧，是行测的本质。这里不堆知识点，只讲方法：
          六大模块的考点体系、解题技巧与精讲例题，帮你把 120 分钟用在刀刃上。
        </p>
        <div class="hero-cta">
          <RouterLink to="/ch/intro" class="btn btn-primary">
            开始学习
            <Icon name="arrow-right" />
          </RouterLink>
          <RouterLink to="/ch/fujian" class="btn btn-ghost">
            <Icon name="bookmark" />
            公式速查
          </RouterLink>
        </div>
        <div class="hero-stats">
          <div v-for="s in stats" :key="s.label" class="stat">
            <strong>{{ s.value }}</strong>
            <span>{{ s.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <section v-if="continueChapter && latestProgress" class="continue-card" aria-label="继续阅读">
      <div>
        <span>继续阅读 · 已完成 {{ completedCount }}/{{ chapters.length }} 章</span>
        <h2>{{ continueChapter.num }} · {{ continueChapter.title }}</h2>
        <div class="continue-progress" aria-hidden="true">
          <i :style="{ width: `${Math.round(latestProgress.ratio * 100)}%` }"></i>
        </div>
      </div>
      <RouterLink :to="continueTo" class="btn btn-primary">
        {{ latestProgress.completed ? '再次阅读' : '继续学习' }}
        <Icon name="arrow-right" />
      </RouterLink>
    </section>

    <!-- 公式一瞥 -->
    <section class="section">
      <div class="section-head">
        <h2>公式，就该这样好看</h2>
        <p>所有数学公式均以专业排版渲染，资料分析与数量关系的核心公式一眼看懂。</p>
      </div>
      <div class="formula-grid">
        <RouterLink v-for="f in featureFormulas" :key="f.title" :to="f.link" class="formula-card">
          <div class="formula-card-title">{{ f.title }}</div>
          <div class="formula-card-body" v-html="f.html"></div>
          <div class="formula-card-note">{{ f.note }}</div>
        </RouterLink>
      </div>
    </section>

    <!-- 章节导航 -->
    <section class="section">
      <div class="section-head">
        <h2>从全局到模块，逐步建立方法论</h2>
        <p>先读第一章建立试卷认知，再逐模块精读；判断推理、数量关系、资料分析是重点。</p>
      </div>

      <template v-for="group in chapterGroups" :key="group.key">
        <div class="ch-group-label">{{ group.label }}</div>
        <div class="chapter-grid" :class="{ wide: group.key === 'modules' }">
          <RouterLink
            v-for="ch in chapters.filter((c) => c.group === group.key)"
            :key="ch.id"
            :to="`/ch/${ch.id}`"
            class="chapter-card"
          >
            <div class="chapter-card-top">
              <span class="chapter-icon" :style="{ color: ch.color, background: ch.color + '1a' }">
                <Icon :name="ch.icon" />
              </span>
              <span class="chapter-num" :style="{ color: ch.color }">{{ ch.num }}</span>
            </div>
            <h3 class="chapter-title">{{ ch.title }}</h3>
            <p class="chapter-desc">{{ ch.desc }}</p>
            <div class="chapter-meta">
              <span v-if="ch.questions" class="meta-chip">{{ ch.questions }}</span>
              <span class="meta-chip">
                <Icon name="clock" />
                约 {{ ch.minutes }} 分钟
              </span>
              <Icon class="chapter-arrow" name="arrow-right" />
            </div>
          </RouterLink>
        </div>
      </template>
    </section>

    <!-- 特色 -->
    <section class="section">
      <div class="section-head">
        <h2>为什么这套方法有效</h2>
        <p>行测的规律性决定了它可以被方法化。本站的一切设计都围绕"方法可复制"展开。</p>
      </div>
      <div class="feature-grid">
        <div v-for="f in features" :key="f.title" class="feature-card">
          <span class="feature-icon" :style="{ color: f.color, background: f.color + '1a' }">
            <Icon :name="f.icon" />
          </span>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 备考路径 -->
    <section class="section">
      <div class="section-head">
        <h2>三阶段备考路线</h2>
        <p>先建框架，再练方法，最后练节奏——每一步都有明确的目标与验收标准。</p>
      </div>
      <div class="steps">
        <div v-for="(s, i) in steps" :key="s.name" class="step">
          <div class="step-rail" aria-hidden="true">
            <span class="step-dot" :class="{ done: i < steps.length - 1 }">{{ i + 1 }}</span>
            <span v-if="i < steps.length - 1" class="step-line"></span>
          </div>
          <RouterLink :to="s.to" class="step-card">
            <div class="step-head">
              <span class="step-stage">{{ s.stage }}</span>
              <span class="step-weeks">{{ s.weeks }}</span>
            </div>
            <h3>{{ s.name }}</h3>
            <p>{{ s.desc }}</p>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 结语 CTA -->
    <section class="section">
      <div class="final-cta">
        <h2>先懂全局，再学招式</h2>
        <p>用 8 分钟读完第一章，建立对整张试卷的结构性认知——这是后面所有技巧生效的前提。</p>
        <RouterLink to="/ch/intro" class="btn btn-primary">
          现在开始
          <Icon name="arrow-right" />
        </RouterLink>
      </div>
    </section>

    <footer class="home-footer">
      <p>行测指南 · 方法为先 —— 本站内容为原创整理的学习笔记，祝备考顺利。</p>
      <p class="scope-note">
        内容整理于
        2026-09，适用于国考与多数省考的通用框架；具体题量、政策与时政内容以最新招考公告和考试大纲为准。
      </p>
      <p>
        <a href="https://github.com/nichuan/xingce-guide" target="_blank" rel="noopener"
          >GitHub 仓库</a
        >
      </p>
    </footer>
  </main>
</template>

<style scoped>
.home {
  width: 100%;
  max-width: 1060px;
  margin: 0 auto;
  padding: 0 20px 40px;
}
.continue-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin: -20px auto 44px;
  max-width: 760px;
  padding: 18px 20px;
  border: 1px solid color-mix(in srgb, var(--c-primary) 25%, var(--c-border));
  border-radius: var(--radius);
  background: var(--c-surface);
  box-shadow: var(--shadow-sm);
}
.continue-card > div {
  min-width: 0;
  flex: 1;
}
.continue-card span {
  font-size: 12px;
  color: var(--c-text-soft);
}
.continue-card h2 {
  margin: 3px 0 9px;
  font-size: 16px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.continue-progress {
  height: 5px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--c-bg-soft);
}
.continue-progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--c-grad);
}
@media (max-width: 600px) {
  .continue-card {
    align-items: stretch;
    flex-direction: column;
  }
  .continue-card .btn {
    justify-content: center;
  }
}

/* ---------- Hero ---------- */
.hero {
  position: relative;
  padding: 72px 8px 56px;
  text-align: center;
  overflow: clip;
}
.hero-bg {
  position: absolute;
  inset: -40% -20% auto;
  height: 130%;
  background:
    radial-gradient(560px 320px at 24% 30%, rgba(99, 102, 241, 0.16), transparent 68%),
    radial-gradient(520px 300px at 78% 24%, rgba(14, 165, 233, 0.15), transparent 68%);
  pointer-events: none;
}
.hero-inner {
  position: relative;
  max-width: 680px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.hero-badge {
  display: inline-block;
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--c-primary-strong);
  background: var(--c-primary-soft);
  border: 1px solid color-mix(in srgb, var(--c-primary) 22%, transparent);
  border-radius: 999px;
  padding: 4px 15px;
  margin-bottom: 22px;
}
.hero-title {
  font-size: clamp(34px, 6.4vw, 52px);
  font-weight: 800;
  line-height: 1.22;
  letter-spacing: 0.01em;
  margin-bottom: 18px;
}
.hero-grad {
  background: var(--c-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero-br {
  display: none;
}
@media (max-width: 560px) {
  .hero-br {
    display: block;
  }
}
.hero-sub {
  font-size: 16px;
  color: var(--c-text-soft);
  line-height: 1.85;
  max-width: 560px;
  margin: 0 0 30px;
}
.hero-cta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 11px 22px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  transition:
    transform 0.18s var(--ease),
    box-shadow 0.18s,
    background 0.18s,
    border-color 0.18s;
}
.btn svg {
  width: 16px;
  height: 16px;
}
.btn-primary {
  background: var(--c-grad);
  color: #fff;
  box-shadow: 0 8px 20px -8px rgba(79, 70, 229, 0.55);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 26px -8px rgba(79, 70, 229, 0.6);
}
.btn-ghost {
  background: var(--c-surface);
  color: var(--c-text-strong);
  border: 1px solid var(--c-border);
}
.btn-ghost:hover {
  border-color: var(--c-primary);
  color: var(--c-primary);
  transform: translateY(-2px);
}
.hero-stats {
  display: flex;
  gap: clamp(20px, 5vw, 44px);
  margin-top: 42px;
}
.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat strong {
  font-size: clamp(24px, 4vw, 30px);
  font-weight: 800;
  background: var(--c-grad);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.stat span {
  font-size: 12.5px;
  color: var(--c-text-soft);
}

/* ---------- 通用 section ---------- */
.section {
  margin-top: 72px;
}
.section-head {
  max-width: 640px;
  margin: 0 auto 26px;
  text-align: center;
}
.section-head h2 {
  font-size: clamp(21px, 3.4vw, 26px);
  font-weight: 750;
  margin-bottom: 8px;
}
.section-head p {
  font-size: 14.5px;
  color: var(--c-text-soft);
  line-height: 1.8;
}

/* ---------- 公式卡 ---------- */
.formula-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
@media (max-width: 900px) {
  .formula-grid {
    grid-template-columns: 1fr;
  }
}
.formula-card {
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--c-primary-soft), transparent 60%), var(--c-surface);
  border: 1px solid color-mix(in srgb, var(--c-primary) 20%, var(--c-border));
  border-radius: var(--radius);
  padding: 18px 18px 14px;
  transition:
    transform 0.2s var(--ease),
    box-shadow 0.2s;
}
.formula-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}
.formula-card-title {
  font-weight: 700;
  color: var(--c-primary);
  font-size: 14.5px;
  margin-bottom: 6px;
}
.formula-card-body {
  flex: 1;
}
.formula-card-body :deep(.katex-display) {
  margin: 10px 0;
  padding: 8px 6px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
}
.formula-card-note {
  font-size: 12.5px;
  color: var(--c-text-soft);
}

/* ---------- 章节卡片 ---------- */
.ch-group {
  display: contents;
}
.ch-group-label {
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: var(--c-text-faint);
  margin: 26px 4px 12px;
}
.chapter-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.chapter-grid.wide {
  grid-template-columns: repeat(3, 1fr);
}
@media (max-width: 920px) {
  .chapter-grid,
  .chapter-grid.wide {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 600px) {
  .chapter-grid,
  .chapter-grid.wide {
    grid-template-columns: 1fr;
  }
}
.chapter-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: 18px;
  transition:
    transform 0.2s var(--ease),
    box-shadow 0.2s,
    border-color 0.2s;
}
.chapter-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: color-mix(in srgb, var(--c-primary) 30%, var(--c-border));
}
.chapter-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}
.chapter-icon {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  display: grid;
  place-items: center;
}
.chapter-icon svg {
  width: 20px;
  height: 20px;
}
.chapter-num {
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.06em;
  opacity: 0.85;
}
.chapter-title {
  font-size: 16.5px;
  font-weight: 700;
  color: var(--c-text-strong);
}
.chapter-desc {
  flex: 1;
  font-size: 13.2px;
  line-height: 1.75;
  color: var(--c-text-soft);
  margin: 0;
}
.chapter-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}
.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 11.5px;
  color: var(--c-text-soft);
  background: var(--c-bg);
  border: 1px solid var(--c-border);
  border-radius: 999px;
  padding: 2px 10px;
}
.meta-chip svg {
  width: 11px;
  height: 11px;
}
.chapter-arrow {
  margin-left: auto;
  width: 15px;
  height: 15px;
  color: var(--c-text-faint);
  transition:
    transform 0.2s,
    color 0.2s;
}
.chapter-card:hover .chapter-arrow {
  transform: translateX(3px);
  color: var(--c-primary);
}

/* ---------- 特色 ---------- */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
.feature-card {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: 22px;
}
.feature-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  margin-bottom: 14px;
}
.feature-icon svg {
  width: 21px;
  height: 21px;
}
.feature-card h3 {
  font-size: 16px;
  margin-bottom: 7px;
}
.feature-card p {
  font-size: 13.5px;
  color: var(--c-text-soft);
  line-height: 1.8;
  margin: 0;
}

/* ---------- 备考路径 ---------- */
.steps {
  max-width: 680px;
  margin: 0 auto;
}
.step {
  display: flex;
  gap: 18px;
}
.step-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: none;
}
.step-dot {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--c-primary-strong);
  background: var(--c-primary-soft);
  border: 1.5px solid color-mix(in srgb, var(--c-primary) 40%, transparent);
  flex: none;
}
.step-dot.done {
  background: var(--c-grad);
  color: #fff;
  border: none;
}
.step-line {
  width: 2px;
  flex: 1;
  background: linear-gradient(var(--c-border-strong), var(--c-border));
  margin: 6px 0;
  min-height: 26px;
}
.step-card {
  flex: 1;
  display: block;
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: 16px 20px;
  margin-bottom: 14px;
  transition:
    transform 0.2s var(--ease),
    box-shadow 0.2s,
    border-color 0.2s;
}
.step-card:hover {
  transform: translateX(3px);
  box-shadow: var(--shadow-md);
  border-color: color-mix(in srgb, var(--c-primary) 30%, var(--c-border));
}
.step-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}
.step-stage {
  font-size: 12px;
  font-weight: 700;
  color: var(--c-primary);
  letter-spacing: 0.08em;
}
.step-weeks {
  font-size: 12px;
  color: var(--c-text-faint);
}
.step-card h3 {
  font-size: 16px;
  margin-bottom: 5px;
}
.step-card p {
  font-size: 13.2px;
  color: var(--c-text-soft);
  line-height: 1.75;
  margin: 0;
}

/* ---------- 结语 CTA ---------- */
.final-cta {
  text-align: center;
  background:
    radial-gradient(480px 240px at 50% 0%, rgba(99, 102, 241, 0.14), transparent 70%),
    var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 20px;
  padding: 44px 24px 40px;
}
.final-cta h2 {
  font-size: clamp(20px, 3.4vw, 25px);
  margin-bottom: 10px;
}
.final-cta p {
  color: var(--c-text-soft);
  font-size: 14.5px;
  max-width: 460px;
  margin: 0 auto 22px;
  line-height: 1.8;
}

/* ---------- footer ---------- */
.home-footer {
  margin-top: 64px;
  padding: 22px 0 8px;
  border-top: 1px solid var(--c-border);
  text-align: center;
  font-size: 13px;
  color: var(--c-text-faint);
  line-height: 2;
}
.home-footer a {
  color: var(--c-text-soft);
}
.home-footer a:hover {
  color: var(--c-primary);
}
</style>
