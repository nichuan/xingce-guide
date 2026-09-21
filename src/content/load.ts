const files = import.meta.glob('./*.md', {
  query: '?raw',
  import: 'default',
}) as Record<string, () => Promise<string>>

/** 章节 id → 懒加载器（01-intro.md → intro） */
const loaders: Record<string, () => Promise<string>> = {}
for (const [path, loader] of Object.entries(files)) {
  const name = path.split('/').pop()!.replace(/\.md$/, '')
  const id = name.replace(/^\d+-/, '')
  loaders[id] = loader
}

const cache = new Map<string, string>()

export const contentIds = Object.keys(loaders)

export async function loadContent(id: string): Promise<string> {
  const hit = cache.get(id)
  if (hit !== undefined) return hit
  const loader = loaders[id]
  if (!loader) return ''
  const raw = await loader()
  cache.set(id, raw)
  return raw
}

export async function loadAllContents(): Promise<Record<string, string>> {
  const entries = await Promise.all(
    contentIds.map(async (id) => [id, await loadContent(id)] as const),
  )
  return Object.fromEntries(entries)
}
