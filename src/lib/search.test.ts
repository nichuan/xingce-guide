import { describe, expect, it } from 'vitest'
import type { SearchSection } from './markdown'
import { normalizeQuery, searchSections } from './search'

const index: SearchSection[] = [
  {
    chapterId: 'ziliao',
    chapterTitle: '资料分析',
    anchor: '基期量',
    heading: '基期量与增长率',
    text: '已知现期量和增长率，可以快速计算基期量。',
  },
  {
    chapterId: 'shuliang',
    chapterTitle: '数量关系',
    anchor: '工程问题',
    heading: '工程问题',
    text: '先赋值工作总量，再计算效率。',
  },
]

describe('search', () => {
  it('normalizes and deduplicates query words', () => {
    expect(normalizeQuery('  基期量   增长率 基期量 ')).toEqual(['基期量', '增长率'])
  })

  it('matches all query words and highlights each hit', () => {
    const hits = searchSections(index, '基期量 增长率')
    expect(hits).toHaveLength(1)
    expect(hits[0].chapterId).toBe('ziliao')
    expect(hits[0].snippet).toContain('<mark>基期量</mark>')
    expect(hits[0].snippet).toContain('<mark>增长率</mark>')
  })

  it('returns no results for an empty query', () => {
    expect(searchSections(index, '   ')).toEqual([])
  })
})
