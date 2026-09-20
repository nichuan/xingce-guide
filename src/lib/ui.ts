import { reactive } from 'vue'

/** 全局 UI 状态（移动端抽屉、搜索弹窗、目录面板） */
export const ui = reactive({
  sidebarOpen: false,
  searchOpen: false,
  tocOpen: false,
})

export function closeAll() {
  ui.sidebarOpen = false
  ui.searchOpen = false
  ui.tocOpen = false
}
