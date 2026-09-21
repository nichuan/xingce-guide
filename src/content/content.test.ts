import { describe, expect, it } from 'vitest'
import { chapters } from './chapters'
import { contentIds, loadAllContents } from './load'
import { renderMarkdown, slugify } from '../lib/markdown'

describe('content contracts', () => {
  it('has exactly one markdown source for every chapter', () => {
    expect([...contentIds].sort()).toEqual(chapters.map((chapter) => chapter.id).sort())
  })

  it('keeps headings, custom containers and internal links valid', async () => {
    const contents = await loadAllContents()
    const headings = new Map<string, Set<string>>()

    for (const chapter of chapters) {
      const source = contents[chapter.id]
      expect(source, `${chapter.id} 内容为空`).toBeTruthy()

      const slugs = [...source.matchAll(/^#{2,4}\s+(.+)$/gm)].map((match) => slugify(match[1]))
      expect(new Set(slugs).size, `${chapter.id} 存在重复标题 slug`).toBe(slugs.length)
      headings.set(chapter.id, new Set(slugs))

      const opens = source.match(/^:::\s*(tip|warn|note|formula|memo|example)(?:\s.*)?$/gm) ?? []
      const closes = source.match(/^:::\s*$/gm) ?? []
      expect(opens.length, `${chapter.id} 自定义容器未闭合`).toBe(closes.length)

      expect(() => renderMarkdown(source, `contract-${chapter.id}`)).not.toThrow()
    }

    for (const chapter of chapters) {
      const source = contents[chapter.id]
      for (const match of source.matchAll(/\]\(\/ch\/([^#)]+)(?:#([^)]+))?\)/g)) {
        const [, targetId, rawAnchor] = match
        expect(headings.has(targetId), `${chapter.id} 链接到无效章节 ${targetId}`).toBe(true)
        if (rawAnchor) {
          expect(
            headings.get(targetId)?.has(decodeURIComponent(rawAnchor)),
            `${chapter.id} 链接到无效锚点 ${targetId}#${rawAnchor}`,
          ).toBe(true)
        }
      }
    }
  })
})
