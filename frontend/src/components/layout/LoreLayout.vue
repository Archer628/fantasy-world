<script setup>
/**
 * 前台布局 (LoreLayout)
 *
 * 前台页面的整体布局框架，包含：
 * - 顶部导航栏 (AppHeader)
 * - 侧边栏 (AppSidebar)
 * - 主内容区域 (router-view)
 * - 页脚 (AppFooter)
 *
 * 内容区域会根据侧边栏状态调整左边距
 */
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppFooter from './AppFooter.vue'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()
</script>

<template>
  <div class="lore-layout">
    <AppHeader />
    <AppSidebar />

    <main
      class="lore-layout__main"
      :class="{ 'lore-layout__main--expanded': !uiStore.sidebarExpanded }"
    >
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
.lore-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.lore-layout__main {
  flex: 1;
  margin-top: var(--header-height);
  margin-left: var(--sidebar-width);
  transition: margin-left var(--transition-normal);
  min-height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
}

.lore-layout__main--expanded {
  margin-left: var(--sidebar-collapsed-width);
}

@media (max-width: 768px) {
  .lore-layout__main,
  .lore-layout__main--expanded {
    margin-left: 0;
  }
}
</style>
