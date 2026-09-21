import type { SearchSection } from './markdown'

export interface SearchHit extends SearchSection {
  score: number
  snippet: string
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

export function normalizeQuery(query: string): string[] {
  return [...new Set(query.trim().toLowerCase().split(/\s+/).filter(Boolean))]
}

export function searchSections(index: SearchSection[], query: string, limit = 12): SearchHit[] {
  const words = normalizeQuery(query)
  if (!words.length) return []
  const out: SearchHit[] = []

  for (const section of index) {
    const heading = section.heading.toLowerCase()
    const text = section.text.toLowerCase()
    if (!words.every((word) => heading.includes(word) || text.includes(word))) continue

    let score = 0
    for (const word of words) {
      if (heading.includes(word)) score += 3
      score += Math.min(text.split(word).length - 1, 4)
    }

    const positions = words.map((word) => text.indexOf(word)).filter((pos) => pos >= 0)
    const pos = positions.length ? Math.min(...positions) : 0
    const start = Math.max(0, pos - 28)
    const end = Math.min(
      section.text.length,
      pos + Math.max(...words.map((word) => word.length)) + 64,
    )
    let snippet = escapeHtml(
      (start > 0 ? '…' : '') +
        section.text.slice(start, end) +
        (end < section.text.length ? '…' : ''),
    )
    for (const word of words.sort((a, b) => b.length - a.length)) {
      const escaped = escapeHtml(word).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      snippet = snippet.replace(new RegExp(escaped, 'gi'), (match) => `<mark>${match}</mark>`)
    }
    out.push({ ...section, score, snippet })
  }

  return out.sort((a, b) => b.score - a.score).slice(0, limit)
}
