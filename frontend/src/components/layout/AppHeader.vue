<script setup>
/**
 * 主导航栏 (AppHeader) - 原神风格增强版
 *
 * 顶部固定导航栏，包含：
 * - 带金色装饰的 Logo / 网站标题
 * - 主导航菜单（带悬停发光）
 * - 搜索栏
 * - 侧边栏切换按钮
 * - 后台管理入口
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useWorldDataStore } from '@/stores/worldData'
import SearchBar from '@/components/common/SearchBar.vue'
import WorldSwitcher from '@/components/common/WorldSwitcher.vue'

const uiStore = useUiStore()
const worldData = useWorldDataStore()

// 确保大世界列表已加载，以便 Logo 显示当前世界名称
onMounted(() => {
  if (worldData.worlds.length === 0) {
    worldData.loadWorlds()
  }
})

/** 导航菜单项 */
const navItems = [
  { name: '首页', path: '/' },
  { name: '世界观', path: '/world-overview' },
  { name: '本源法则', path: '/origin-laws' },
  { name: '族群', path: '/factions' },
  { name: '角色', path: '/characters' },
  { name: '宝物', path: '/artifacts' },
  { name: '异常物', path: '/anomalies' },
  { name: '能力体系', path: '/abilities' },
  { name: '境界', path: '/realms' },
  { name: '异兽', path: '/creatures' },
  { name: '碎片世界', path: '/fragment-worlds' },
  { name: '历史', path: '/history' },
  { name: '关系网络', path: '/relations' },
]

const showMobileMenu = ref(false)

function toggleMobileMenu() {
  showMobileMenu.value = !showMobileMenu.value
}

function closeMobileMenu() {
  showMobileMenu.value = false
}
</script>

<template>
  <header class="app-header">
    <!-- 金色顶部装饰线 -->
    <div class="app-header__deco"></div>

    <div class="app-header__inner">
      <!-- Logo 区域 -->
      <div class="app-header__logo">
        <RouterLink to="/" class="logo-link">
          <span class="logo-icon">✦</span>
          <span class="logo-text gold-shimmer-text">{{ worldData.currentWorld?.name || '异世界' }}</span>
        </RouterLink>
      </div>

      <!-- 大世界切换器 -->
      <WorldSwitcher />

      <!-- 主导航 (桌面) -->
      <nav class="app-header__nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-item--active"
        >
          <span class="nav-item__text">{{ item.name }}</span>
        </RouterLink>
      </nav>

      <!-- 右侧操作区 -->
      <div class="app-header__actions">
        <SearchBar />

        <!-- 侧边栏切换按钮 -->
        <button class="icon-btn" @click="uiStore.toggleSidebar()" title="切换侧边栏">
          <span class="icon">☰</span>
        </button>

        <!-- 移动端菜单按钮 -->
        <button class="icon-btn icon-btn--mobile" @click="toggleMobileMenu" title="菜单">
          <span class="icon">{{ showMobileMenu ? '✕' : '☰' }}</span>
        </button>

        <!-- 后台管理入口 -->
        <RouterLink to="/admin" class="icon-btn admin-link" title="后台管理">
          <span class="icon">⚙</span>
        </RouterLink>
      </div>
    </div>

    <!-- 移动端菜单 -->
    <transition name="slide">
      <nav v-if="showMobileMenu" class="app-header__mobile-nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item"
          active-class="mobile-nav-item--active"
          @click="closeMobileMenu"
        >
          {{ item.name }}
        </RouterLink>
      </nav>
    </transition>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: linear-gradient(
    180deg,
    rgba(6, 11, 20, 0.95) 0%,
    rgba(13, 21, 37, 0.9) 100%
  );
  backdrop-filter: blur(16px) saturate(140%);
  -webkit-backdrop-filter: blur(16px) saturate(140%);
  border-bottom: 1px solid var(--border-color);
  z-index: var(--z-header);
}

/* 顶部金色装饰线 */
.app-header__deco {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--color-gold-dark) 20%,
    var(--color-gold-primary) 50%,
    var(--color-gold-light) 50%,
    var(--color-gold-dark) 80%,
    transparent 100%
  );
  box-shadow: 0 0 8px var(--color-gold-glow);
}

.app-header__inner {
  display: flex;
  align-items: center;
  height: 100%;
  padding: 0 var(--spacing-lg);
  gap: var(--spacing-lg);
}

.app-header__logo {
  flex-shrink: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  text-decoration: none;
}

.logo-icon {
  color: var(--color-gold-primary);
  font-size: var(--font-size-lg);
  text-shadow: 0 0 8px var(--color-gold-glow);
  animation: goldSparkle 3s ease-in-out infinite;
}

.logo-text {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  letter-spacing: 3px;
}

.app-header__nav {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 2px;
  overflow-x: auto;
  scrollbar-width: none;
}

.app-header__nav::-webkit-scrollbar {
  display: none;
}

.nav-item {
  position: relative;
  padding: var(--spacing-xs) var(--spacing-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  white-space: nowrap;
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
}

.nav-item::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  width: 0;
  height: 2px;
  background: var(--color-gold-primary);
  transition: all var(--transition-normal);
  transform: translateX(-50%);
  box-shadow: 0 0 6px var(--color-gold-glow);
}

.nav-item:hover {
  color: var(--text-gold);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.nav-item:hover::after {
  width: 70%;
}

.nav-item--active {
  color: var(--text-gold);
  font-weight: 600;
}

.nav-item--active::after {
  width: 70%;
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.icon-btn,
.admin-link {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
}

.icon-btn:hover,
.admin-link:hover {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
  box-shadow: 0 0 12px var(--color-gold-glow);
}

.icon {
  font-size: 18px;
}

.icon-btn--mobile {
  display: none;
}

/* 移动端导航 */
.app-header__mobile-nav {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(6, 11, 20, 0.98);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  padding: var(--spacing-md);
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-xs);
}

.mobile-nav-item {
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.mobile-nav-item:hover,
.mobile-nav-item--active {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.1);
}

@media (max-width: 1024px) {
  .app-header__nav {
    display: none;
  }

  .icon-btn--mobile {
    display: flex;
  }
}

@media (max-width: 768px) {
  .logo-text {
    font-size: var(--font-size-xl);
    letter-spacing: 2px;
  }

  .app-header__inner {
    padding: 0 var(--spacing-md);
    gap: var(--spacing-sm);
  }
}
</style>
