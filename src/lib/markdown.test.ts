import { describe, expect, it } from 'vitest'
import { extractContainers, plainText, renderMarkdown, slugify } from './markdown'

describe('markdown helpers', () => {
  it('creates stable Chinese-friendly slugs', () => {
    expect(slugify(' 7.2.5 比重（重点） ')).toBe('7.2.5-比重重点')
  })

  it('removes markdown syntax for search text', () => {
    expect(plainText('## 标题\n**重点** $x + y$ | 内容 |')).toBe('标题 重点 内容')
  })

  it('uses structured tokens to hide example solutions', () => {
    const source = `::: example 例题\n> 题干\n\n**解析**：过程。**答案 A**。\n:::`
    const { html } = renderMarkdown(source, 'solution-test')
    expect(html).toContain('<details class="example-solution">')
    expect(html).toContain('查看解析与答案')
    expect(html).toContain('<span class="answer-badge">答案 A</span>')
  })

  it('extracts formula containers through markdown tokens', () => {
    const source = `::: formula 增长率\n$$r = a + b$$\n:::`
    const formulas = extractContainers(source, 'formula')
    expect(formulas).toHaveLength(1)
    expect(formulas[0].title).toBe('增长率')
    expect(formulas[0].html).toContain('katex')
  })
})
