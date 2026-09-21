import type { RouteLocationNormalizedLoaded } from 'vue-router'
import { getChapter } from '../content/chapters'

export const SITE_NAME = '行测指南 · 方法为先'
export const SITE_DESCRIPTION =
  '公务员考试行测六大模块学习指南：言语理解、政治理论、判断推理、常识判断、数量关系、资料分析的考点体系、解题方法与速算技巧。'
export const SITE_ORIGIN = 'https://nichuan.github.io'

function setMeta(selector: string, attr: 'name' | 'property', key: string, content: string) {
  let el = document.head.querySelector<HTMLMetaElement>(selector)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.append(el)
  }
  el.content = content
}

function setCanonical(url: string) {
  let el = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!el) {
    el = document.createElement('link')
    el.rel = 'canonical'
    document.head.append(el)
  }
  el.href = url
}

export function updateMetadata(route: RouteLocationNormalizedLoaded) {
  if (typeof document === 'undefined') return
  const chapter = route.name === 'chapter' ? getChapter(String(route.params.id)) : undefined
  const isFormula = route.name === 'formulas'
  const title = chapter
    ? `${chapter.title} | ${SITE_NAME}`
    : isFormula
      ? `公式速查 | ${SITE_NAME}`
      : route.name === 'not-found'
        ? `页面未找到 | ${SITE_NAME}`
        : `${SITE_NAME} | 公务员行测六大模块教学`
  const description =
    chapter?.desc ?? (isFormula ? '集中速查数量关系与资料分析核心公式。' : SITE_DESCRIPTION)
  const relativePath = route.path.replace(/^\//, '').replace(/\/$/, '')
  const canonical = new URL(
    relativePath ? `${relativePath}/` : '',
    `${SITE_ORIGIN}${import.meta.env.BASE_URL}`,
  ).href
  const image = new URL('og-image.jpg', `${SITE_ORIGIN}${import.meta.env.BASE_URL}`).href

  document.title = title
  setMeta('meta[name="description"]', 'name', 'description', description)
  setMeta('meta[property="og:title"]', 'property', 'og:title', title)
  setMeta('meta[property="og:description"]', 'property', 'og:description', description)
  setMeta('meta[property="og:type"]', 'property', 'og:type', chapter ? 'article' : 'website')
  setMeta('meta[property="og:url"]', 'property', 'og:url', canonical)
  setMeta('meta[property="og:image"]', 'property', 'og:image', image)
  setMeta('meta[name="twitter:card"]', 'name', 'twitter:card', 'summary_large_image')
  setCanonical(canonical)
}
