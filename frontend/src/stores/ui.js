import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * UI 状态 Store
 *
 * 管理全局 UI 状态：
 * - 侧边栏展开/收起
 * - 搜索栏展开状态
 * - 当前主题（可扩展）
 * - 全局通知/Toast消息
 */
export const useUiStore = defineStore('ui', () => {
  // ==================== 侧边栏状态 ====================

  /** 侧边栏是否展开 */
  const sidebarExpanded = ref(true)

  /** 侧边栏展开/收起切换 */
  function toggleSidebar() {
    sidebarExpanded.value = !sidebarExpanded.value
  }

  /** 设置侧边栏状态 */
  function setSidebarExpanded(val) {
    sidebarExpanded.value = val
  }

  // ==================== 搜索状态 ====================

  /** 搜索栏是否展开 */
  const searchExpanded = ref(false)

  /** 切换搜索栏 */
  function toggleSearch() {
    searchExpanded.value = !searchExpanded.value
  }

  /** 关闭搜索栏 */
  function closeSearch() {
    searchExpanded.value = false
  }

  // ==================== 通知系统 ====================

  /** 通知消息列表 */
  const notifications = ref([])

  /** 添加通知 */
  function addNotification({ message, type = 'info', duration = 3000 }) {
    const id = Date.now()
    notifications.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
    return id
  }

  /** 移除通知 */
  function removeNotification(id) {
    const index = notifications.value.findIndex((n) => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  // ==================== 加载状态 ====================

  /** 全局加载状态 */
  const globalLoading = ref(false)

  /** 设置全局加载 */
  function setGlobalLoading(val) {
    globalLoading.value = val
  }

  // ==================== 当前激活的导航 ====================

  /** 当前激活的菜单项 */
  const activeMenuItem = ref('')

  /** 设置当前激活菜单 */
  function setActiveMenuItem(item) {
    activeMenuItem.value = item
  }

  // ==================== 移动端菜单 ====================

  /** 移动端菜单是否打开 */
  const mobileMenuOpen = ref(false)

  /** 切换移动端菜单 */
  function toggleMobileMenu() {
    mobileMenuOpen.value = !mobileMenuOpen.value
  }

  /** 关闭移动端菜单 */
  function closeMobileMenu() {
    mobileMenuOpen.value = false
  }

  // ==================== 计算属性 ====================

  /** 侧边栏宽度 */
  const sidebarWidth = computed(() =>
    sidebarExpanded.value
      ? 'var(--sidebar-width)'
      : 'var(--sidebar-collapsed-width)'
  )

  return {
    // 侧边栏
    sidebarExpanded,
    toggleSidebar,
    setSidebarExpanded,
    // 搜索
    searchExpanded,
    toggleSearch,
    closeSearch,
    // 通知
    notifications,
    addNotification,
    removeNotification,
    // 加载
    globalLoading,
    setGlobalLoading,
    // 导航
    activeMenuItem,
    setActiveMenuItem,
    // 移动端
    mobileMenuOpen,
    toggleMobileMenu,
    closeMobileMenu,
    // 计算属性
    sidebarWidth,
  }
})
