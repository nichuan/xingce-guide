const files = import.meta.glob('./*.md', {
  query: '?raw',
  import: 'default',
  eager: true,
}) as Record<string, string>

/** 文件名 → 章节 id（01-intro.md → intro） */
export const rawContents: Record<string, string> = {}
for (const [path, raw] of Object.entries(files)) {
  const name = path.split('/').pop()!.replace(/\.md$/, '')
  const id = name.replace(/^\d+-/, '')
  rawContents[id] = raw
}
