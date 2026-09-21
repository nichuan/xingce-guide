import { computed, reactive, ref } from 'vue'
import { chapters } from '../content/chapters'
import { safeGet, safeSet } from './storage'

const STORAGE_KEY = 'xc-learning-v1'
const SELF_TEST_KEY = 'xc-self-test'

export interface ChapterProgress {
  chapterId: string
  anchor: string
  ratio: number
  completed: boolean
  updatedAt: number
}

export interface Bookmark {
  chapterId: string
  anchor: string
  heading: string
  createdAt: number
}

interface LearningData {
  version: 1
  progress: Record<string, ChapterProgress>
  bookmarks: Bookmark[]
}

function initialData(): LearningData {
  const saved = safeGet(STORAGE_KEY)
  if (saved) {
    try {
      const parsed = JSON.parse(saved) as Partial<LearningData>
      if (parsed.version === 1 && parsed.progress && Array.isArray(parsed.bookmarks)) {
        return parsed as LearningData
      }
    } catch {
      // 损坏或旧版本数据自动回退，不阻断应用启动。
    }
  }
  return { version: 1, progress: {}, bookmarks: [] }
}

export const learning = reactive<LearningData>(initialData())
export const selfTestMode = ref(safeGet(SELF_TEST_KEY) !== 'off')

function persist() {
  safeSet(STORAGE_KEY, JSON.stringify(learning))
}

export function recordProgress(chapterId: string, anchor: string, ratio: number) {
  const normalized = Math.max(0, Math.min(1, ratio))
  learning.progress[chapterId] = {
    chapterId,
    anchor,
    ratio: normalized,
    completed: normalized >= 0.9,
    updatedAt: Date.now(),
  }
  persist()
}

export function toggleSelfTest() {
  selfTestMode.value = !selfTestMode.value
  safeSet(SELF_TEST_KEY, selfTestMode.value ? 'on' : 'off')
}

export function isBookmarked(chapterId: string, anchor: string): boolean {
  return learning.bookmarks.some((item) => item.chapterId === chapterId && item.anchor === anchor)
}

export function toggleBookmark(chapterId: string, anchor: string, heading: string): boolean {
  const index = learning.bookmarks.findIndex(
    (item) => item.chapterId === chapterId && item.anchor === anchor,
  )
  if (index >= 0) {
    learning.bookmarks.splice(index, 1)
    persist()
    return false
  }
  learning.bookmarks.unshift({
    chapterId,
    anchor,
    heading,
    createdAt: Date.now(),
  })
  persist()
  return true
}

export function removeBookmark(chapterId: string, anchor: string) {
  const index = learning.bookmarks.findIndex(
    (item) => item.chapterId === chapterId && item.anchor === anchor,
  )
  if (index >= 0) {
    learning.bookmarks.splice(index, 1)
    persist()
  }
}

export const latestProgress = computed(() => {
  return Object.values(learning.progress)
    .filter((item) => chapters.some((chapter) => chapter.id === item.chapterId))
    .sort((a, b) => b.updatedAt - a.updatedAt)[0]
})

export const completedCount = computed(
  () => Object.values(learning.progress).filter((item) => item.completed).length,
)
