<script setup>
/**
 * 后台布局 (AdminLayout)
 *
 * 残响界管理后台主布局，包含：
 * - 左侧固定侧边栏（240px）- 导航菜单
 * - 右侧主内容区域
 * - 顶部面包屑导航 + 大世界切换器
 * - 原神风格装饰（金色边框、深色背景、渐变效果）
 */
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'

const route = useRoute()
const router = useRouter()
const worldData = useWorldDataStore()

// 确保大世界列表已加载，以便后台标题显示当前世界名称
onMounted(async () => {
  if (worldData.worlds.length === 0) {
    await worldData.loadWorlds()
  }
})

/** 侧边栏折叠状态 */
const sidebarCollapsed = ref(false)

/** 后台导航菜单配置（不含基础设定：大世界管理等移到右上角齿轮） */
const adminNav = [
  { name: '仪表盘', path: '/admin', icon: '◆', exact: true },
  { name: '族群管理', path: '/admin/factions', icon: '◈' },
  { name: '角色管理', path: '/admin/characters', icon: '◉' },
  { name: '宝物管理', path: '/admin/artifacts', icon: '◇' },
  { name: '能力体系', path: '/admin/abilities', icon: '✦' },
  { name: '异兽管理', path: '/admin/creatures', icon: '❖' },
  { name: '碎片世界管理', path: '/admin/fragment-worlds', icon: '✧' },
]

/** 面包屑路径 */
const breadcrumbs = computed(() => {
  const matched = route.matched
  const crumbs = []
  crumbs.push({ name: '管理后台', path: '/admin' })
  if (route.path !== '/admin' && matched.length > 1) {
    const last = matched[matched.length - 1]
    crumbs.push({
      name: last.meta?.title || '未知页面',
      path: route.path,
    })
  }
  return crumbs
})

/* ==================== 大世界切换器 ==================== */
/** 切换器下拉是否展开 */
const worldDropdownOpen = ref(false)

/** 当前选中的大世界（从 store 获取） */
const currentWorld = computed(() => worldData.currentWorld)
const worlds = computed(() => worldData.worlds)

/** 切换大世界 */
function selectWorld(slug) {
  worldData.switchWorld(slug)
  worldDropdownOpen.value = false
}

/** 点击外部关闭下拉 */
const worldDropdownRef = ref(null)
function handleClickOutside(e) {
  if (worldDropdownRef.value && !worldDropdownRef.value.contains(e.target)) {
    worldDropdownOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', handleClickOutside))
// 当前大世界变更时，清空后台所有页面缓存（下一级子页面会自动通过 worldData 重新加载）
watch(
  () => worldData.currentWorldSlug,
  () => {
    // 刷新当前路由视图，触发子组件重新加载
    // 这里用刷新 key 的方式更轻量：在 RouterView 上绑定一个变更 key
    viewKey.value = Date.now()
  }
)
const viewKey = ref(0)
</script>

<template>
  <div class="admin-layout" :class="{ 'admin-layout--collapsed': sidebarCollapsed }">
    <!-- ==================== 左侧侧边栏 ==================== -->
    <aside class="admin-sidebar">
      <!-- Logo区域 -->
      <div class="admin-sidebar__header">
        <div class="admin-logo">
          <div class="admin-logo__icon">
            <span class="logo-diamond">◆</span>
          </div>
          <div class="admin-logo__text" v-show="!sidebarCollapsed">
            <span class="admin-logo__title gold-shimmer-text">{{ currentWorld?.name || '异世界' }}</span>
            <span class="admin-logo__subtitle">管理后台</span>
          </div>
        </div>
        <button
          class="admin-sidebar__toggle"
          @click="sidebarCollapsed = !sidebarCollapsed"
          :title="sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        >
          <span class="toggle-icon">{{ sidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
      </div>

      <!-- 装饰分隔线 -->
      <div class="admin-sidebar__divider">
        <div class="divider-line"></div>
        <div class="divider-diamond">◇</div>
        <div class="divider-line"></div>
      </div>

      <!-- 导航菜单 -->
      <nav class="admin-sidebar__nav">
        <RouterLink
          v-for="item in adminNav"
          :key="item.path"
          :to="item.path"
          class="admin-nav-item"
          :active-class="item.exact ? '' : 'admin-nav-item--active'"
          :exact-active-class="item.exact ? 'admin-nav-item--active' : ''"
          :title="item.name"
        >
          <span class="admin-nav-item__icon">{{ item.icon }}</span>
          <span class="admin-nav-item__name" v-show="!sidebarCollapsed">{{ item.name }}</span>
        </RouterLink>
      </nav>

      <!-- 底部返回前台 -->
      <div class="admin-sidebar__footer">
        <div class="admin-sidebar__divider">
          <div class="divider-line"></div>
          <div class="divider-diamond">◇</div>
          <div class="divider-line"></div>
        </div>
        <RouterLink to="/" class="admin-nav-item admin-nav-item--back" title="返回前台">
          <span class="admin-nav-item__icon">◀</span>
          <span class="admin-nav-item__name" v-show="!sidebarCollapsed">返回前台</span>
        </RouterLink>
      </div>
    </aside>

    <!-- ==================== 右侧主区域 ==================== -->
    <div class="admin-main">
      <!-- 顶部栏 -->
      <header class="admin-header">
        <!-- 面包屑导航 -->
        <nav class="admin-breadcrumb">
          <template v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
            <RouterLink
              v-if="index < breadcrumbs.length - 1"
              :to="crumb.path"
              class="breadcrumb-link"
            >
              {{ crumb.name }}
            </RouterLink>
            <span v-else class="breadcrumb-current">{{ crumb.name }}</span>
            <span v-if="index < breadcrumbs.length - 1" class="breadcrumb-sep">/</span>
          </template>
        </nav>

        <!-- 大世界切换器 -->
        <div
          ref="worldDropdownRef"
          class="world-switcher"
          :class="{ 'is-open': worldDropdownOpen }"
        >
          <button
            class="world-switcher__trigger"
            @click.stop="worldDropdownOpen = !worldDropdownOpen"
            type="button"
          >
            <span class="world-switcher__icon">🌌</span>
            <span class="world-switcher__name">{{ currentWorld?.name || '选择大世界' }}</span>
            <span class="world-switcher__arrow">{{ worldDropdownOpen ? '▲' : '▼' }}</span>
          </button>
          <div class="world-switcher__dropdown" v-show="worldDropdownOpen">
            <div class="world-switcher__list">
              <button
                v-for="w in worlds"
                :key="w.slug"
                type="button"
                class="world-switcher__item"
                :class="{ 'is-current': w.slug === currentWorld?.slug }"
                @click.stop="selectWorld(w.slug)"
              >
                <span class="ws-item__name">{{ w.name }}</span>
                <span v-if="w.subtitle" class="ws-item__subtitle">{{ w.subtitle }}</span>
                <span v-if="w.slug === currentWorld?.slug" class="ws-item__check">✓</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 齿轮：基础设定入口 -->
        <RouterLink
          to="/admin/settings"
          class="header-settings-btn"
          title="基础设定（管理大世界、族群等级、宝物种类等通用配置"
        >
          <span class="settings-icon">⚙</span>
        </RouterLink>

        <!-- 装饰 -->
        <div class="admin-header__deco">
          <span class="header-star">✦</span>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="admin-content">
        <router-view v-slot="{ Component }" :key="viewKey">
          <transition name="admin-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>

    <!-- ==================== 通知 Toast 容器 ==================== -->
    <div class="admin-toast-container" id="adminToastContainer"></div>
  </div>
</template>

<style scoped>
/* ==================== 布局基础 ==================== */
.admin-layout {
  display: flex;
  min-height: 100vh;
  background: var(--bg-admin);
  position: relative;
  overflow: hidden;
}

.admin-layout::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(212, 168, 83, 0.03) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(0, 212, 170, 0.02) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

/* ==================== 侧边栏 ==================== */
.admin-sidebar {
  width: var(--admin-sidebar-width);
  min-width: var(--admin-sidebar-width);
  background: linear-gradient(180deg, rgba(13, 21, 37, 0.98) 0%, rgba(10, 15, 28, 0.99) 100%);
  backdrop-filter: blur(12px);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: var(--z-sidebar);
  transition: width var(--transition-normal), min-width var(--transition-normal);
}

.admin-layout--collapsed .admin-sidebar {
  width: 64px;
  min-width: 64px;
}

/* 侧边栏头部 Logo */
.admin-sidebar__header {
  padding: var(--spacing-lg) var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color-light);
}

.admin-logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-decoration: none;
  cursor: pointer;
}

.admin-logo__icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-diamond {
  font-size: 24px;
  color: var(--color-gold-primary);
  filter: drop-shadow(0 0 8px var(--color-gold-glow));
  animation: glowPulse 3s ease-in-out infinite;
}

.admin-logo__text {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-logo__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.admin-logo__subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  letter-spacing: 2px;
  margin-top: 2px;
  white-space: nowrap;
}

/* 折叠按钮 */
.admin-sidebar__toggle {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.admin-sidebar__toggle:hover {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
}

.toggle-icon {
  font-size: 12px;
}

/* 装饰分隔线 */
.admin-sidebar__divider {
  display: flex;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-md);
  gap: var(--spacing-sm);
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border-color), transparent);
}

.divider-diamond {
  color: var(--color-gold-dark);
  font-size: 10px;
  flex-shrink: 0;
}

/* 导航菜单 */
.admin-sidebar__nav {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-sm);
  overflow-y: auto;
  overflow-x: hidden;
}

.admin-nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 10px var(--spacing-md);
  color: var(--text-secondary);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
  margin-bottom: 2px;
  font-size: var(--font-size-sm);
  border: 1px solid transparent;
  position: relative;
  white-space: nowrap;
  overflow: hidden;
}

.admin-nav-item:hover {
  background: rgba(212, 168, 83, 0.08);
  color: var(--text-gold);
  border-color: var(--border-color-light);
}

.admin-nav-item--active {
  background: linear-gradient(135deg, rgba(212, 168, 83, 0.15) 0%, rgba(212, 168, 83, 0.05) 100%);
  color: var(--text-gold);
  border-color: rgba(212, 168, 83, 0.3);
  border-left: 3px solid var(--color-gold-primary);
}

.admin-nav-item--active::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 60%;
  background: var(--color-gold-primary);
  border-radius: 0 2px 2px 0;
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.admin-nav-item--active:hover::after {
  opacity: 0.5;
}

.admin-nav-item__icon {
  font-size: 16px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
  transition: color var(--transition-fast), text-shadow var(--transition-fast);
}

.admin-nav-item--active .admin-nav-item__icon {
  color: var(--color-gold-primary);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

/* 返回前台按钮 */
.admin-nav-item--back {
  margin-top: var(--spacing-xs);
}

.admin-nav-item--back:hover {
  color: var(--color-cyan-primary);
}

.admin-nav-item--back .admin-nav-item__icon {
  color: var(--text-muted);
}

.admin-nav-item--back:hover .admin-nav-item__icon {
  color: var(--color-cyan-primary);
  text-shadow: 0 0 8px var(--color-cyan-glow);
}

/* 侧边栏底部 */
.admin-sidebar__footer {
  padding-bottom: var(--spacing-sm);
}

/* ==================== 主内容区 ==================== */
.admin-main {
  flex: 1;
  margin-left: var(--admin-sidebar-width);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
  z-index: 1;
  transition: margin-left var(--transition-normal);
}

.admin-layout--collapsed .admin-main {
  margin-left: 64px;
}

/* ==================== 顶部栏 ==================== */
.admin-header {
  height: 56px;
  min-height: 56px;
  background: rgba(13, 21, 37, 0.9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-xl);
  position: sticky;
  top: 0;
  z-index: var(--z-header);
}

/* 面包屑 */
.admin-breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.breadcrumb-link {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.breadcrumb-link:hover {
  color: var(--text-gold);
}

.breadcrumb-sep {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
}

.breadcrumb-current {
  color: var(--text-gold);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.admin-header__deco {
  display: flex;
  align-items: center;
}

.header-star {
  color: var(--color-gold-dark);
  font-size: 14px;
  opacity: 0.6;
  animation: twinkle 4s ease-in-out infinite;
}

/* ==================== 大世界切换器 ==================== */
.world-switcher {
  position: relative;
  margin-left: auto;
  margin-right: var(--spacing-md);
}

.world-switcher__trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: rgba(212, 168, 83, 0.05);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.world-switcher__trigger:hover {
  border-color: var(--color-gold-primary);
  background: rgba(212, 168, 83, 0.1);
  color: var(--text-gold);
}

.world-switcher.is-open .world-switcher__trigger {
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 0 1px rgba(212, 168, 83, 0.3), 0 0 16px rgba(212, 168, 83, 0.15);
}

.world-switcher__icon {
  font-size: 14px;
}

.world-switcher__name {
  font-weight: 600;
  color: var(--text-gold);
}

.world-switcher__arrow {
  font-size: 10px;
  color: var(--text-muted);
  transition: transform var(--transition-fast);
}

.world-switcher.is-open .world-switcher__arrow {
  transform: rotate(180deg);
  color: var(--color-gold-primary);
}

.world-switcher__dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 240px;
  background: linear-gradient(180deg, rgba(13, 21, 37, 0.98) 0%, rgba(10, 15, 28, 0.99) 100%);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(212, 168, 83, 0.1);
  z-index: var(--z-dropdown);
  overflow: hidden;
  animation: dropdownIn 0.18s ease-out;
}

@keyframes dropdownIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.world-switcher__list {
  padding: 4px;
  max-height: 360px;
  overflow-y: auto;
}

.world-switcher__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--border-radius-sm);
  color: var(--text-secondary);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
}

.world-switcher__item:last-child {
  margin-bottom: 0;
}

.world-switcher__item:hover {
  background: rgba(212, 168, 83, 0.08);
  color: var(--text-gold);
  border-color: rgba(212, 168, 83, 0.2);
}

.world-switcher__item.is-current {
  background: linear-gradient(135deg, rgba(212, 168, 83, 0.15) 0%, rgba(212, 168, 83, 0.05) 100%);
  color: var(--text-gold);
  border-color: rgba(212, 168, 83, 0.3);
}

.ws-item__name {
  flex: 1;
  font-weight: 500;
  font-size: var(--font-size-sm);
}

.ws-item__subtitle {
  font-size: 11px;
  color: var(--text-muted);
  margin-left: var(--spacing-xs);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.ws-item__check {
  color: var(--color-gold-primary);
  font-size: 12px;
  font-weight: 700;
}

/* ==================== 顶部齿轮（基础设定入口） ==================== */
.header-settings-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: rgba(212, 168, 83, 0.04);
  color: var(--text-secondary);
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-left: var(--spacing-xs);
}

.header-settings-btn:hover {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.1);
  box-shadow: 0 0 12px rgba(212, 168, 83, 0.2);
}

.settings-icon {
  font-size: 18px;
  line-height: 1;
  transition: transform 0.5s ease;
}

.header-settings-btn:hover .settings-icon {
  transform: rotate(90deg);
}

/* ==================== 内容区域 ==================== */
.admin-content {
  flex: 1;
  padding: var(--spacing-xl);
  animation: fadeIn 0.3s ease-out;
}

/* ==================== Toast 通知容器 ==================== */
.admin-toast-container {
  position: fixed;
  top: 72px;
  right: 24px;
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ==================== 过渡动画 ==================== */
.admin-fade-enter-active {
  transition: all 0.25s ease-out;
}

.admin-fade-leave-active {
  transition: all 0.2s ease-in;
}

.admin-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.admin-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .admin-sidebar {
    width: 64px;
    min-width: 64px;
  }

  .admin-sidebar__toggle {
    display: none;
  }

  .admin-nav-item__name,
  .admin-logo__text,
  .breadcrumb-sep,
  .breadcrumb-link:not(:first-child) {
    display: none;
  }

  .admin-main {
    margin-left: 64px;
  }

  .admin-content {
    padding: var(--spacing-md);
  }
}

@media (max-width: 768px) {
  .admin-sidebar {
    width: 0;
    min-width: 0;
    overflow: hidden;
    transform: translateX(-100%);
  }

  .admin-sidebar.mobile-open {
    width: var(--admin-sidebar-width);
    min-width: var(--admin-sidebar-width);
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
  }

  .admin-layout--collapsed .admin-sidebar {
    width: 0;
    min-width: 0;
  }

  .admin-main,
  .admin-layout--collapsed .admin-main {
    margin-left: 0;
  }

  .admin-content {
    padding: var(--spacing-sm);
  }

  .admin-header {
    padding: 0 var(--spacing-md);
  }
}
</style>
