import { createHash } from 'node:crypto'
import { gzipSync } from 'node:zlib'
import { mkdir, readFile, readdir, stat, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { createServer } from 'vite'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const dist = path.join(root, 'dist')
const base = '/xingce-guide/'
const siteUrl = 'https://nichuan.github.io/xingce-guide/'

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')

function replaceMeta(html, { title, description, canonical, type = 'website' }) {
  return html
    .replace(/<title>.*?<\/title>/s, `<title>${escapeHtml(title)}</title>`)
    .replace(
      /<meta name="description" content=".*?"\s*\/?>/s,
      `<meta name="description" content="${escapeHtml(description)}" />`,
    )
    .replace(
      /<meta property="og:title" content=".*?"\s*\/?>/s,
      `<meta property="og:title" content="${escapeHtml(title)}" />`,
    )
    .replace(
      /<meta property="og:description" content=".*?"\s*\/?>/s,
      `<meta property="og:description" content="${escapeHtml(description)}" />`,
    )
    .replace(
      /<meta property="og:type" content=".*?"\s*\/?>/s,
      `<meta property="og:type" content="${type}" />`,
    )
    .replace(
      '</head>',
      `  <link rel="canonical" href="${canonical}" />\n    <meta property="og:url" content="${canonical}" />\n  </head>`,
    )
}

function withStaticBody(html, body) {
  return html.replace(
    '<div id="app"></div>',
    `<div id="app"><div class="static-shell">${body}</div></div>`,
  )
}

async function writeRoute(route, html) {
  const directory = path.join(dist, route)
  await mkdir(directory, { recursive: true })
  await writeFile(path.join(directory, 'index.html'), html)
}

async function walk(directory) {
  const out = []
  for (const entry of await readdir(directory)) {
    const absolute = path.join(directory, entry)
    const info = await stat(absolute)
    if (info.isDirectory()) out.push(...(await walk(absolute)))
    else out.push(absolute)
  }
  return out
}

const vite = await createServer({
  root,
  appType: 'custom',
  logLevel: 'error',
  server: { middlewareMode: true },
})

try {
  const { chapters } = await vite.ssrLoadModule('/src/content/chapters.ts')
  const { loadAllContents } = await vite.ssrLoadModule('/src/content/load.ts')
  const { renderMarkdown, extractContainers } = await vite.ssrLoadModule('/src/lib/markdown.ts')
  const contents = await loadAllContents()
  const template = await readFile(path.join(dist, 'index.html'), 'utf8')

  const shellStyle = `<style>
    .static-shell{max-width:820px;margin:0 auto;padding:56px 24px;color:#344054;font:16px/1.8 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
    .static-shell h1{font-size:36px}.static-shell h2{margin-top:36px}.static-shell a{color:#4f46e5}.static-shell nav{display:grid;gap:10px}.static-shell nav a{padding:10px 14px;border:1px solid #e4e8f1;border-radius:10px;text-decoration:none}.static-shell .static-note{color:#667085}.static-shell .prose table{width:100%}
  </style>`
  const injectStyle = (html) => html.replace('</head>', `${shellStyle}</head>`)

  const homeBody = `<main><p class="static-note">公务员考试 · 行政职业能力测验</p><h1>行测指南 · 方法为先</h1><p>六大模块的考点体系、解题技巧与精讲例题，帮助你把 120 分钟用在刀刃上。</p><h2>章节目录</h2><nav>${chapters
    .map(
      (chapter) =>
        `<a href="${base}ch/${chapter.id}/"><strong>${escapeHtml(chapter.num)} · ${escapeHtml(chapter.title)}</strong><br><span class="static-note">${escapeHtml(chapter.desc)}</span></a>`,
    )
    .join(
      '',
    )}<a href="${base}formulas/"><strong>全部公式</strong><br><span class="static-note">集中速查各章核心公式</span></a></nav></main>`
  const homeMeta = replaceMeta(template, {
    title: '行测指南 · 方法为先 | 公务员行测六大模块教学',
    description: '公务员考试行测六大模块学习指南：考点体系、解题方法、精讲例题与速算技巧。',
    canonical: siteUrl,
  })
  await writeFile(path.join(dist, 'index.html'), injectStyle(withStaticBody(homeMeta, homeBody)))

  for (const chapter of chapters) {
    const rendered = renderMarkdown(contents[chapter.id] ?? '', `static-${chapter.id}`)
    const body = `<main><p class="static-note">${escapeHtml(chapter.num)} · 更新于 ${escapeHtml(chapter.lastUpdated)}</p><h1>${escapeHtml(chapter.title)}</h1><p>${escapeHtml(chapter.desc)}</p><p class="static-note">${escapeHtml(chapter.applicableTo)} · 具体题量与政策以最新招考公告为准</p><article class="prose">${rendered.html}</article></main>`
    const html = replaceMeta(template, {
      title: `${chapter.title} | 行测指南 · 方法为先`,
      description: chapter.desc,
      canonical: `${siteUrl}ch/${chapter.id}/`,
      type: 'article',
    })
    await writeRoute(`ch/${chapter.id}`, injectStyle(withStaticBody(html, body)))
  }

  const formulaItems = chapters.flatMap((chapter) =>
    extractContainers(contents[chapter.id] ?? '', 'formula').map((formula) => ({
      chapter,
      ...formula,
    })),
  )
  const formulaBody = `<main><p class="static-note">速查工具</p><h1>全部公式</h1>${formulaItems
    .map(
      (item) =>
        `<section><h2>${escapeHtml(item.title)} · ${escapeHtml(item.chapter.short)}</h2><div class="prose">${item.html}</div></section>`,
    )
    .join('')}</main>`
  const formulaHtml = replaceMeta(template, {
    title: '公式速查 | 行测指南 · 方法为先',
    description: '集中速查数量关系与资料分析核心公式。',
    canonical: `${siteUrl}formulas/`,
  })
  await writeRoute('formulas', injectStyle(withStaticBody(formulaHtml, formulaBody)))

  const notFoundHtml = replaceMeta(template, {
    title: '页面未找到 | 行测指南 · 方法为先',
    description: '请求的页面不存在，请返回行测指南首页。',
    canonical: `${siteUrl}404/`,
  })
  const notFoundBody = `<main><p class="static-note">404</p><h1>这一页不在题册里</h1><p><a href="${base}">返回首页</a></p></main>`
  await writeRoute('404', injectStyle(withStaticBody(notFoundHtml, notFoundBody)))
  await writeFile(
    path.join(dist, '404.html'),
    injectStyle(withStaticBody(notFoundHtml, notFoundBody)),
  )

  const sitemapUrls = [
    siteUrl,
    `${siteUrl}formulas/`,
    ...chapters.map((chapter) => `${siteUrl}ch/${chapter.id}/`),
  ]
  await writeFile(
    path.join(dist, 'sitemap.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapUrls.map((url) => `  <url><loc>${url}</loc></url>`).join('\n')}\n</urlset>\n`,
  )
  await writeFile(
    path.join(dist, 'robots.txt'),
    `User-agent: *\nAllow: /\nSitemap: ${siteUrl}sitemap.xml\n`,
  )
} finally {
  await vite.close()
}

const files = (await walk(dist)).filter((file) => !file.endsWith('/sw.js'))
const relativeFiles = files
  .map((file) => path.relative(dist, file).split(path.sep).join('/'))
  .sort()
const fingerprints = await Promise.all(
  files.map(async (file) =>
    createHash('sha256')
      .update(await readFile(file))
      .digest('hex'),
  ),
)
const version = createHash('sha256').update(fingerprints.join('|')).digest('hex').slice(0, 12)

for (const file of files.filter((item) => item.endsWith('.js'))) {
  const gzipBytes = gzipSync(await readFile(file)).byteLength
  if (gzipBytes > 250 * 1024) {
    throw new Error(
      `JavaScript gzip budget exceeded: ${path.basename(file)} (${Math.ceil(gzipBytes / 1024)} KB)`,
    )
  }
}

const precache = relativeFiles.map((file) => {
  if (file === 'index.html') return base
  if (file.endsWith('/index.html')) return `${base}${file.slice(0, -'index.html'.length)}`
  return `${base}${file}`
})
const serviceWorker = `const CACHE = 'xingce-${version}'
const PRECACHE = ${JSON.stringify(precache, null, 2)}
self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting()))
})
self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith('xingce-') && key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim()))
})
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).then((response) => {
      const copy = response.clone()
      caches.open(CACHE).then((cache) => cache.put(event.request, copy))
      return response
    }).catch(async () => {
      const normalizedPath = url.pathname.endsWith('/') ? url.pathname : url.pathname + '/'
      return (await caches.match(event.request)) || (await caches.match(normalizedPath)) || (await caches.match('${base}404.html')) || caches.match('${base}')
    }))
    return
  }
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)))
})
`
await writeFile(path.join(dist, 'sw.js'), serviceWorker)

console.log(`Generated static routes, sitemap, robots.txt and offline cache ${version}.`)
