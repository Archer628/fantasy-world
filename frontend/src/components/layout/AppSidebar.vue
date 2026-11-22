<script setup>
/**
 * 侧边栏 (AppSidebar) - 原神风格增强版
 *
 * 可折叠的侧边导航栏，带有金色装饰
 * - 分组导航（世界观、生灵、设定、世界）
 * - 激活项金色高亮 + 左侧装饰条
 * - 折叠模式仅显示图标
 */
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useUiStore } from '@/stores/ui'
import { useWorldDataStore } from '@/stores/worldData'

const uiStore = useUiStore()
const worldData = useWorldDataStore()

// 确保大世界列表已加载，以便侧边栏显示当前世界
onMounted(() => {
  if (worldData.worlds.length === 0) {
    worldData.loadWorlds()
  }
})

/** 侧边栏分组导航 */
const sidebarGroups = [
  {
    title: '世界观',
    items: [
      { name: '总览', path: '/world-overview', icon: '🌍' },
      { name: '历史事件', path: '/history', icon: '📜' },
      { name: '关系网络', path: '/relations', icon: '🔗' },
    ],
  },
  {
    title: '生灵',
    items: [
      { name: '种族', path: '/races', icon: '🧬' },
      { name: '势力', path: '/forces', icon: '🏰' },
      { name: '角色', path: '/characters', icon: '👤' },
      { name: '异兽图鉴', path: '/creatures', icon: '🐉' },
    ],
  },
  {
    title: '设定',
    items: [
      { name: '能力体系', path: '/abilities', icon: '✨' },
      { name: '境界等级', path: '/realms', icon: '💎' },
      { name: '宝物', path: '/artifacts', icon: '🗡' },
    ],
  },
  {
    title: '世界',
    items: [
      { name: '碎片世界', path: '/fragment-worlds', icon: '🌌' },
    ],
  },
]
</script>

<template>
  <aside
    class="app-sidebar"
    :class="{ 'app-sidebar--collapsed': !uiStore.sidebarExpanded }"
  >
    <!-- 顶部金色装饰 -->
    <div class="app-sidebar__deco-top"></div>

    <div class="app-sidebar__content">
      <!-- 当前大世界指示器 -->
      <div class="sidebar-world">
        <span class="sidebar-world__icon">🌌</span>
        <div v-if="uiStore.sidebarExpanded" class="sidebar-world__info">
          <span class="sidebar-world__label">当前世界</span>
          <span class="sidebar-world__name gold-shimmer-text">
            {{ worldData.currentWorld?.name || '未选择' }}
          </span>
          <span v-if="worldData.currentWorld?.subtitle" class="sidebar-world__subtitle">
            {{ worldData.currentWorld.subtitle }}
          </span>
        </div>
      </div>

      <div
        v-for="(group, index) in sidebarGroups"
        :key="index"
        class="sidebar-group"
      >
        <div v-if="uiStore.sidebarExpanded" class="sidebar-group__title">
          <span class="sidebar-group__title-deco">◆</span>
          {{ group.title }}
        </div>
        <div v-else class="sidebar-group__divider"></div>

        <RouterLink
          v-for="item in group.items"
          :key="item.path"
          :to="item.path"
          class="sidebar-item"
          active-class="sidebar-item--active"
          :title="item.name"
        >
          <span class="sidebar-item__icon">{{ item.icon }}</span>
          <span v-if="uiStore.sidebarExpanded" class="sidebar-item__name">
            {{ item.name }}
          </span>
          <span v-if="uiStore.sidebarExpanded" class="sidebar-item__arrow">›</span>
        </RouterLink>
      </div>
    </div>

    <!-- 底部装饰 -->
    <div v-if="uiStore.sidebarExpanded" class="app-sidebar__footer">
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
      <p class="app-sidebar__footer-text">{{ worldData.currentWorld?.name || '异世界' }} · 档案库</p>
    </div>
  </aside>
</template>

<style scoped>
.app-sidebar {
  position: fixed;
  top: var(--header-height);
  left: 0;
  bottom: 0;
  width: var(--sidebar-width);
  background: linear-gradient(
    180deg,
    rgba(13, 21, 37, 0.98) 0%,
    rgba(6, 11, 20, 0.95) 100%
  );
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  overflow-x: hidden;
  z-index: var(--z-sidebar);
  transition: width var(--transition-normal);
  display: flex;
  flex-direction: column;
}

.app-sidebar--collapsed {
  width: var(--sidebar-collapsed-width);
}

/* 顶部金色装饰 */
.app-sidebar__deco-top {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    var(--color-gold-primary) 50%,
    transparent
  );
  flex-shrink: 0;
}

.app-sidebar__content {
  padding: var(--spacing-md);
  flex: 1;
}

/* 当前大世界指示器 */
.sidebar-world {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  margin-bottom: var(--spacing-md);
  background: linear-gradient(135deg, rgba(212, 168, 83, 0.12) 0%, rgba(212, 168, 83, 0.04) 100%);
  border: 1px solid var(--border-color-light);
  border-radius: var(--border-radius-md);
}

.app-sidebar--collapsed .sidebar-world {
  justify-content: center;
  padding: var(--spacing-sm);
}

.sidebar-world__icon {
  font-size: 22px;
  flex-shrink: 0;
  filter: drop-shadow(0 0 6px var(--color-gold-glow));
}

.sidebar-world__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.sidebar-world__label {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.sidebar-world__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-world__subtitle {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sidebar-group {
  margin-bottom: var(--spacing-lg);
}

.sidebar-group__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--color-gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  padding: var(--spacing-xs) var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-family-display);
}

.sidebar-group__title-deco {
  font-size: 8px;
  opacity: 0.7;
}

.sidebar-group__divider {
  height: 1px;
  background: var(--border-color-light);
  margin: var(--spacing-sm) 0;
}

.sidebar-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--text-secondary);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
  text-decoration: none;
  margin-bottom: 2px;
  overflow: hidden;
}

.sidebar-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 3px;
  height: 0;
  background: var(--color-gold-primary);
  transform: translateY(-50%);
  transition: height var(--transition-normal);
  box-shadow: 0 0 6px var(--color-gold-glow);
  border-radius: 0 2px 2px 0;
}

.sidebar-item:hover {
  background: rgba(212, 168, 83, 0.08);
  color: var(--text-gold);
  padding-left: calc(var(--spacing-md) + 4px);
}

.sidebar-item--active {
  background: rgba(212, 168, 83, 0.12);
  color: var(--text-gold);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.sidebar-item--active::before {
  height: 60%;
}

.sidebar-item__icon {
  font-size: 18px;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
  filter: drop-shadow(0 0 2px rgba(212, 168, 83, 0.3));
}

.sidebar-item__name {
  font-size: var(--font-size-sm);
  white-space: nowrap;
  flex: 1;
}

.sidebar-item__arrow {
  color: var(--color-gold-dark);
  font-size: var(--font-size-lg);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.sidebar-item:hover .sidebar-item__arrow {
  opacity: 1;
}

.app-sidebar--collapsed .sidebar-item {
  justify-content: center;
  padding: var(--spacing-sm);
}

.app-sidebar--collapsed .sidebar-item:hover {
  padding-left: var(--spacing-sm);
}

/* 底部 */
.app-sidebar__footer {
  padding: var(--spacing-md);
  flex-shrink: 0;
}

.app-sidebar__footer-text {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  font-family: var(--font-family-display);
  letter-spacing: 1px;
}

@media (max-width: 768px) {
  .app-sidebar {
    transform: translateX(-100%);
  }

  .app-sidebar--mobile-open {
    transform: translateX(0);
  }
}
</style>
