import MarkdownIt from 'markdown-it'
import type Token from 'markdown-it/lib/token.mjs'
import anchor from 'markdown-it-anchor'
import container from 'markdown-it-container'
import katexPlugin from '@vscode/markdown-it-katex'
import 'katex/dist/katex.min.css'

export interface TocItem {
  level: number
  text: string
  id: string
}

export interface RenderResult {
  html: string
  toc: TocItem[]
}

/** 生成中文友好的锚点：去空白、去常见括号引号 */
export function slugify(s: string): string {
  return s
    .trim()
    .toLowerCase()
    .replace(/[（）()""''【】《》：:，,。；;、！？!?·]/g, '')
    .replace(/\s+/g, '-')
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/** 容器标题前的小图标（stroke 风格，随文字颜色） */
const CONTAINER_ICONS: Record<string, string> = {
  tip: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.4 1 2.3h6c0-.9.4-1.8 1-2.3A7 7 0 0 0 12 2z"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/></svg>',
  note: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>',
  formula:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16M7 5v6.5a9 2.5 0 0 0 10 0V5M12 11.5V19M8 19h8"/></svg>',
  memo: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v1M5.6 5.6l.7.7M3 12h1M5.6 18.4l.7-.7M19 12h1M17.7 6.3l.7-.7M9 21h6M10 17c0-1.5-2-2-2-4.5a5 5 0 0 1 10 0c0 2.5-2 3-2 4.5z"/><path d="M10 17h4"/></svg>',
  example:
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M9 13h6M9 17h6"/></svg>',
}

const DEFAULT_TITLES: Record<string, string> = {
  tip: '提示',
  warn: '注意',
  note: '说明',
  formula: '核心公式',
  memo: '记忆卡',
  example: '例题',
}

function useContainer(md: MarkdownIt, name: string) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  md.use(container as any, name, {
    render(tokens: Token[], idx: number) {
      const token = tokens[idx]
      if (token.nesting === 1) {
        // info 形如 "example 例 14 · 代入排除法"
        const raw = token.info.trim().slice(name.length).trim()
        const title = raw || DEFAULT_TITLES[name] || name
        return `<div class="ctn ctn-${name}"><div class="ctn-title">${CONTAINER_ICONS[name] ?? ''}<span>${escapeHtml(title)}</span></div>\n`
      }
      const closeSolution = name === 'example' && Boolean(token.meta?.closeSolution)
      return `${closeSolution ? '</div></details>\n' : ''}</div>\n`
    },
  })
}

const md = new MarkdownIt({ html: false, linkify: false, breaks: false })
const resolvedKatexPlugin =
  typeof katexPlugin === 'function'
    ? katexPlugin
    : (katexPlugin as unknown as { default: typeof katexPlugin }).default

// eslint-disable-next-line @typescript-eslint/no-explicit-any
md.use(anchor as any, {
  slugify,
  level: [2, 3, 4],
  permalink: anchor.permalink.linkAfterHeader({
    style: 'aria-label',
    assistiveText: (title: string) => `复制“${title}”的小节链接`,
    symbol: '#',
  }),
})
// eslint-disable-next-line @typescript-eslint/no-explicit-any
md.use(resolvedKatexPlugin as any, { throwOnError: false })
for (const name of ['tip', 'warn', 'note', 'formula', 'memo', 'example']) {
  useContainer(md, name)
}

/** 用 token 结构识别例题中的“解析”起点，避免对渲染后的 HTML 做脆弱切割。 */
md.core.ruler.after('inline', 'example-solution', (state) => {
  let exampleDepth = 0
  let solutionOpen = false
  for (let i = 0; i < state.tokens.length; i++) {
    const token = state.tokens[i]
    if (token.type === 'container_example_open') {
      exampleDepth++
      solutionOpen = false
      continue
    }
    if (token.type === 'container_example_close') {
      if (solutionOpen) token.meta = { ...token.meta, closeSolution: true }
      exampleDepth = Math.max(0, exampleDepth - 1)
      solutionOpen = false
      continue
    }
    if (!exampleDepth || solutionOpen || token.type !== 'paragraph_open') continue
    const inline = state.tokens[i + 1]
    const children = (inline?.children ?? []).filter(
      (child) => child.type !== 'text' || child.content.trim(),
    )
    const startsWithSolution =
      children[0]?.type === 'strong_open' &&
      children[1]?.type === 'text' &&
      /^(解析|答案)/.test(children[1].content.trim())
    if (startsWithSolution) {
      token.meta = { ...token.meta, solutionStart: true }
      solutionOpen = true
    }
  }
})

const defaultParagraphOpen = md.renderer.rules.paragraph_open
md.renderer.rules.paragraph_open = (tokens, idx, options, env, self) => {
  const opening = defaultParagraphOpen
    ? defaultParagraphOpen(tokens, idx, options, env, self)
    : self.renderToken(tokens, idx, options)
  if (!tokens[idx].meta?.solutionStart) return opening
  return `<details class="example-solution"><summary>查看解析与答案</summary><div class="example-solution-content">${opening}`
}

/** 渲染后处理：答案徽章 + 内链补齐部署 base 路径 */
function decorate(html: string): string {
  const base = import.meta.env.BASE_URL
  return html
    .replace(
      /<strong>答案\s*([A-D])\s*<\/strong>/g,
      (_m, letter) => `<span class="answer-badge">答案 ${letter}</span>`,
    )
    .replace(/href="\/ch\//g, `href="${base}ch/`)
}

function extractToc(tokens: Token[]): TocItem[] {
  const toc: TocItem[] = []
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i]
    if (t.type === 'heading_open' && ['h2', 'h3', 'h4'].includes(t.tag)) {
      const inline = tokens[i + 1]
      toc.push({
        level: Number(t.tag.slice(1)),
        text: inline?.content?.trim() ?? '',
        id: t.attrGet('id') ?? '',
      })
    }
  }
  return toc
}

const cache = new Map<string, RenderResult>()

export function renderMarkdown(source: string, key: string): RenderResult {
  const hit = cache.get(key)
  if (hit) return hit
  const tokens = md.parse(source, {})
  const toc = extractToc(tokens)
  const html = decorate(md.renderer.render(tokens, md.options, {}))
  const result = { html, toc }
  cache.set(key, result)
  return result
}

export interface ExtractedContainer {
  title: string
  html: string
}

/** 从 Markdown token 中抽取指定容器，供公式聚合等二次编排使用。 */
export function extractContainers(source: string, name: string): ExtractedContainer[] {
  const tokens = md.parse(source, {})
  const results: ExtractedContainer[] = []
  const openType = `container_${name}_open`
  const closeType = `container_${name}_close`
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].type !== openType) continue
    let depth = 1
    let end = i + 1
    while (end < tokens.length && depth > 0) {
      if (tokens[end].type === openType) depth++
      if (tokens[end].type === closeType) depth--
      end++
    }
    const rawTitle = tokens[i].info.trim().slice(name.length).trim()
    const inner = tokens.slice(i + 1, end - 1)
    results.push({
      title: rawTitle || DEFAULT_TITLES[name] || name,
      html: decorate(md.renderer.render(inner, md.options, {})),
    })
    i = end - 1
  }
  return results
}

/** 生成供搜索用的纯文本 */
export function plainText(source: string): string {
  return source
    .replace(/^:::.*$/gm, '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/\$\$[\s\S]*?\$\$/g, ' ')
    .replace(/\$[^$\n]*\$/g, ' ')
    .replace(/^\s*\|?[-\s:|]+\|?\s*$/gm, ' ')
    .replace(/\|/g, ' ')
    .replace(/[#>*`~_[\]]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

export interface SearchSection {
  chapterId: string
  chapterTitle: string
  anchor: string
  heading: string
  text: string
}

/** 按 h2 小节构建搜索索引 */
export function buildSearchIndex(
  chapterId: string,
  chapterTitle: string,
  source: string,
): SearchSection[] {
  const lines = source.split('\n')
  const sections: SearchSection[] = []
  let heading = '概述'
  let anchorId = ''
  let buf: string[] = []

  const flush = () => {
    const text = plainText(buf.join('\n'))
    if (text) {
      sections.push({
        chapterId,
        chapterTitle,
        anchor: anchorId,
        heading,
        text,
      })
    }
    buf = []
  }

  for (const line of lines) {
    const m = line.match(/^(#{2,3})\s+(.*)$/)
    if (m) {
      flush()
      heading = m[2].trim()
      anchorId = slugify(m[2])
    } else {
      buf.push(line)
    }
  }
  flush()
  return sections
}
