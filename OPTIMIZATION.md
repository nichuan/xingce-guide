# 行测指南 · 优化与功能规划清单

> 基于 2026-09 对 `3c1f61b`（Vue 3 + Vite 重构版）的代码审查与构建验证整理。
> 当前 `npm run check` 通过；主入口 JS 已降至约 20 KB（gzip 9 KB），Markdown / KaTeX 与各章内容均已分包，全站 Markdown 约 90 KB / 1791 行。
> 整体判断：完成度较高的内容型站点，内容与界面分离良好；下一阶段应先补正确性、可访问性与内容质量守护，再扩展学习功能。
> 以下按优先级分组，勾选框用于跟踪进度。

## 目录

- [P0 · 已知 Bug](#p0--已知-bug)
- [P1 · 低成本高收益优化](#p1--低成本高收益优化)
- [P2 · 新功能建议](#p2--新功能建议)
- [P3 · 工程健康](#p3--工程健康)
- [关键决策与实施顺序](#关键决策与实施顺序)

---

## P0 · 已知 Bug

- [x] **移动端顶栏章节标题不随路由更新**
  - 位置：`src/components/TopBar.vue:10`
  - 现象：`const chapter = props.chapterId ? getChapter(props.chapterId) : undefined` 是 setup 中一次性求值的普通变量，而 `TopBar` 只在 `App.vue` 挂载一次。从首页进入 `/ch/yanyu` 再切到 `/ch/panduan` 时，顶栏标题停留在首次渲染的值（首页进入则一直显示「行测指南」）。
  - 修复：改为 `computed(() => (props.chapterId ? getChapter(props.chapterId) : undefined))`。
  - 验收：移动端连续切换首页、两个有效章节和无效章节，标题均正确。

- [x] **直接访问不存在的章节会出现空白页**
  - 位置：`src/router.ts`、`src/views/ChapterView.vue:51-61`
  - 现象：`/ch/not-exist` 能匹配 `/ch/:id`，因此兜底路由不会生效；直接打开时 `watch(html, ...)` 又不会立即执行，页面只剩框架而不会跳回首页。
  - 修复：在路由守卫中用 `getChapter()` 校验 `id`，无效时跳转到显式 404 页或首页；不要把合法性校验只放在视图的非 immediate watch 中。
  - 验收：直接输入、站内跳转、浏览器前进后退三种方式访问无效章节都不会空白。

- [x] **搜索结果的键盘选中索引可能越界**
  - 位置：`src/components/SearchModal.vue:31-64`
  - 现象：无结果时按方向键可令 `activeIdx` 变为 `-1`；查询词改变后若结果数变少，旧索引也可能超出范围，导致没有高亮项且 Enter 无响应。
  - 修复：查询变化时将索引重置为 0，并在结果变化时 clamp 到合法范围；无结果时忽略方向键。

## P1 · 低成本高收益优化

- [x] **先明确 SEO / 分享所需的 URL 与渲染策略**
  - 已采用完整方案：迁移为 history 路由，并在构建后为首页、9 个章节、公式页与 404 生成真实 HTML 路径。
  - 每个可收录页面均有独立 title、description、canonical 与 Open Graph 元数据，同时生成 `robots.txt` 和 `sitemap.xml`。
  - GitHub Pages 的仓库 base path 已覆盖路由、章节内链、静态资源、离线缓存和分享地址。
  - 涉及：`index.html`、`src/router.ts`、`src/content/chapters.ts`、`vite.config.ts`

- [x] **阅读进度持久化 + 继续阅读**
  - `localStorage` 记录每章最后阅读锚点、滚动比例和完成状态；内容结构变化后优先按锚点恢复，比例只作为兜底。
  - 首页 Hero 下增加「继续阅读：第 N 章 · XXX」卡片；侧边栏已读章节打勾。
  - 节流写入并给存储结构加 `version`，避免每次滚动同步写存储及未来字段升级困难。
  - 涉及：`src/views/HomeView.vue`、`src/views/ChapterView.vue`、`src/components/SiteSidebar.vue`、新增 `src/lib/progress.ts`

- [x] **例题答案折叠（自测模式）**
  - 现状：33 道例题中并非每题都一定有 A-D 答案；现有正则只识别 `**答案 A**` 这类固定格式，不能安全地推断“解析从哪里开始、到哪里结束”。
  - 建议：不要继续依赖渲染后 HTML 正则切块；新增明确的 `::: answer` / `::: solution` 容器，或把 `example` 设计为题干与解析两个结构化区域。
  - 先支持单题展开/收起，再增加全局「自测模式」开关；偏好使用原生 `<details>`，并用 localStorage 记忆模式。
  - 这是教学站点的核心体验改进，建议先迁移 2～3 道不同题型验证结构，再批量改内容。

- [x] **可访问性与键盘操作补全**
  - 搜索弹窗补 `aria-modal="true"`、可感知的输入标签、焦点圈定（focus trap）和关闭后的焦点恢复；结果列表补合适的 listbox / option 或等价语义。
  - 移动端侧边栏、目录抽屉打开后应把背景设为 inert，关闭后恢复触发按钮焦点。
  - `SiteSidebar.vue` 的品牌入口目前是可点击 `div`，改为 `RouterLink` 或 `button`，确保键盘可达。
  - 增加 `prefers-reduced-motion` 降级，关闭平滑滚动和非必要动画。

- [x] **标题锚点 permalink 与路由状态统一**
  - 位置：`src/lib/markdown.ts:73`，当前 `permalink: false`。
  - 开启 hover / focus 显示 `#` 链接，方便复制某小节链接；触屏端需保留可发现的复制入口。
  - `ChapterView.vue` 当前用原生 `history.replaceState()` 更新地址，Vue Router 的 `currentRoute.hash` 不会同步；改用 `router.replace()` 或统一封装，避免地址栏与路由状态分离。
  - 对中文、重复标题、空 slug 和编码后的 URL 增加测试。

- [x] **完善打印样式（导出 PDF）**
  - 现状：`src/styles/layout.css` 已有基础 `@media print`，会隐藏侧边栏、目录和翻页导航，因此不是从零增加。
  - 补充：展开所有答案 / 折叠容器；避免标题、例题、表格、公式被跨页截断；移除滚动容器；设置打印色彩；必要时显示外链 URL。
  - 用至少一个表格密集章节和一个公式密集章节实际打印为 PDF 做视觉验收。

- [x] **内容适用范围、更新时间与来源说明**
  - 首页的「135 题」、题量、时间分配以及政治 / 时政内容可能随考试类型、地区和年份变化，应标明适用考试口径、资料更新时间和“以最新招考公告为准”。
  - 对易过期章节增加 `lastUpdated` / `applicableTo` 元数据，并在页面头部展示，避免高质量界面放大过时内容的可信度风险。

- [x] **本地存储与主题初始化容错**
  - `index.html` 对 localStorage 已有 try/catch，但 `src/lib/theme.ts` 模块顶层仍直接访问 `localStorage` / `matchMedia`；存储被禁用时可能阻断应用启动，也会妨碍后续 SSG。
  - 封装安全读写并区分浏览器环境；主题切换时同步更新 `meta[name="theme-color"]`。

## P2 · 新功能建议

- [x] **公式速查聚合页**
  - 构建期自动抽取各章 `::: formula` 容器，生成可按模块筛选的「全部公式」独立页面。
  - 内容已存在，只是重新组织；与搜索配合成为刷题速查工具。
  - 抽取逻辑应复用 Markdown token / AST，而不是新增一套正则解析规则。

- [x] **搜索增强**
  - 现状：单关键词、区分字符形式的子串匹配（`src/components/SearchModal.vue:31-49`）。
  - 先做低成本增强：多关键词 AND 匹配、空白归一化、命中词分别高亮、标题优先和无结果建议。
  - 数据量继续增长后再评估 MiniSearch / FlexSearch；拼音首字母匹配应以真实搜索需求为依据，避免先增加索引体积和依赖。

- [ ] **章节小测（quiz 容器）**
  - 新增 `::: quiz` 结构化语法：选项可点击、即时判分，成绩按章持久化。
  - 先在一章试点，再扩展错题重做、掌握度与复习队列；不要一开始就把题库、统计和账号系统一起引入。

- [x] **收藏夹**
  - 收藏某个小节锚点，侧边栏展示「我的收藏」列表；提供失效锚点清理与导出 / 导入，防止标题调整后产生死收藏。

- [x] **PWA 离线访问**
  - 备考人群适合移动与通勤场景，但建议在 URL / SSG 策略及内容分包确定后再做，避免缓存策略返工。
  - 明确更新提示、旧缓存淘汰、离线兜底页和 base path 验证；不要简单缓存全部请求后长期展示旧讲义。

## P3 · 工程健康

- [x] **接入 ESLint + Prettier**
  - `src/lib/markdown.ts` 中已有 `eslint-disable-next-line` 注释，但项目未安装 ESLint，注释目前无效。
  - 在 CI 中执行 lint / format check，避免只在本地编辑器生效。

- [x] **测试分三层，而不只测试纯函数**
  - 单元测试：`slugify`、`plainText`、搜索排序 / 高亮、进度存储迁移。
  - 内容契约测试：每个 `chapters.ts` id 都有 Markdown；标题 slug 唯一且与 markdown-it-anchor 一致；内部章节 / 锚点链接可解析；自定义容器成对闭合；例题结构和 KaTeX 可渲染。
  - 关键流程测试：顶栏随路由更新、无效章节不空白、搜索键盘边界、锚点跳转 / 后退、主题恢复。
  - 当前内容的容器数量与内部链接人工检查均正常，适合把这些规则固化为自动测试。

- [x] **主包拆分与性能预算**
  - 当前首页、章节视图、搜索弹窗和全部 Markdown 都是 eager / 静态导入，构建后主 JS 约 607 KB（gzip 221 KB）；`chunkSizeWarningLimit: 1200` 只是隐藏默认告警，不是优化。
  - 路由组件改为动态导入；章节正文按 id 加载；搜索索引及搜索弹窗在首次打开时加载；视情况将 KaTeX / Markdown 渲染器拆为独立 chunk。
  - 给 CI 增加 gzip 体积预算，并用 Lighthouse / Web Vitals 在 GitHub Pages 的真实 base path 下复测首屏、交互与布局偏移。

- [ ] **阅读时长自动计算**
  - `src/content/chapters.ts` 的 `minutes` 为手填，可从去除 Markdown 标记后的中文字符数、公式 / 表格 / 例题数量估算。
  - 如果保留人工值，至少用脚本检查内容大幅变化但阅读时长未更新的情况。

- [x] **依赖与部署维护**
  - 配置依赖更新机器人或定期升级节奏，并在升级后运行 build、内容契约测试和页面冒烟测试。
  - CI 除构建外增加类型检查、lint、test 和产物链接检查；GitHub Pages 发布后验证首页、章节直达、favicon 与静态资源均返回成功。

## 关键决策与实施顺序

已确定需要“每章可被搜索引擎独立收录并生成分享卡片”，因此本轮已完成真实路径、静态预渲染、canonical、Open Graph、sitemap 和 PWA，并在 GitHub Pages 的仓库 base path 下验证。

如果只先做三组工作：

1. **修复 3 个已知 Bug，并补对应回归测试** —— 先保证路由与搜索行为可靠；
2. **补内容契约测试 + 可访问性基础** —— 守住内容链接、键盘操作和后续批量改文档的安全线；
3. **结构化例题答案 + 阅读进度** —— 直接改善「学」与「练」的核心体验。

随后再依据 SEO 决策推进 SSG / 元数据与主包拆分。公式聚合、小测、收藏、PWA 属于第二阶段，避免同时扩张内容模型、路由和缓存三条主线。

## 已核实但不再单列为待办

- `dist/` 已被 `.gitignore` 忽略，Vite 构建时会自动清理旧产物；手动删除本地旧 `dist` 不属于产品优化项。
- favicon 与 JS / CSS 资源在生产构建中会自动带上 `/xingce-guide/` base path，当前构建产物路径正确。
- 当前 9 个 Markdown 文件未发现重复标题 slug、自定义容器不配对或失效的内部章节锚点；这些检查仍应进入自动化测试，防止后续回归。
