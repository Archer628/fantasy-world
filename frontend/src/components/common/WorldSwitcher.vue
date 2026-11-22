<script setup>
/**
 * 大世界切换器 (WorldSwitcher) - 原神风格
 *
 * 顶部导航栏中的下拉菜单，用于在多个大世界之间切换。
 * 使用 Teleport 将下拉菜单渲染到 body 层级，
 * 避免 header 的 backdrop-filter 创建层叠上下文导致下拉菜单被裁剪。
 */
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()
const isOpen = ref(false)
const switcherRef = ref(null)
const dropdownStyle = ref({})

/** 计算下拉菜单位置 */
function updateDropdownPosition() {
  if (!switcherRef.value) return
  const rect = switcherRef.value.getBoundingClientRect()
  dropdownStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 8}px`,
    right: `${window.innerWidth - rect.right}px`,
    minWidth: '280px',
  }
}

/** 切换下拉菜单开合状态 */
async function toggleDropdown() {
  if (!isOpen.value) {
    // 打开前先计算位置
    updateDropdownPosition()
  }
  isOpen.value = !isOpen.value
}

/** 选择世界并切换 */
function selectWorld(slug) {
  if (slug === worldData.currentWorldSlug) {
    isOpen.value = false
    return
  }
  worldData.switchWorld(slug)
  worldData.clearWorldCache(slug)
  isOpen.value = false
  window.location.reload()
}

/** 点击外部关闭下拉菜单 */
function handleDocumentClick(e) {
  if (!isOpen.value) return
  // 检查点击是否在切换器按钮内
  if (switcherRef.value && switcherRef.value.contains(e.target)) {
    return
  }
  // 检查点击是否在下拉菜单内（Teleport 后下拉菜单不在 switcherRef 内）
  const dropdown = document.querySelector('.world-switcher__dropdown')
  if (dropdown && dropdown.contains(e.target)) {
    return
  }
  isOpen.value = false
}

/** ESC 键关闭 */
function handleKeydown(e) {
  if (e.key === 'Escape' && isOpen.value) {
    isOpen.value = false
  }
}

/** 窗口大小变化时更新位置 */
function handleResize() {
  if (isOpen.value) {
    updateDropdownPosition()
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick, false)
  document.addEventListener('keydown', handleKeydown, false)
  window.addEventListener('resize', handleResize, false)
  if (worldData.worlds.length === 0) {
    worldData.loadWorlds()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleDocumentClick, false)
  document.removeEventListener('keydown', handleKeydown, false)
  window.removeEventListener('resize', handleResize, false)
})
</script>

<template>
  <div class="world-switcher" ref="switcherRef">
    <button
      class="world-switcher__trigger"
      @click.stop="toggleDropdown"
      :aria-expanded="isOpen"
      aria-haspopup="listbox"
    >
      <span class="world-switcher__icon">🌌</span>
      <span class="world-switcher__name">{{ worldData.currentWorld?.name || '选择世界' }}</span>
      <span class="world-switcher__arrow" :class="{ 'world-switcher__arrow--open': isOpen }">▼</span>
    </button>
  </div>

  <!-- 使用 Teleport 将下拉菜单渲染到 body，避免 header 层叠上下文裁剪 -->
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="world-switcher__dropdown"
      :style="dropdownStyle"
    >
      <div class="world-switcher__header">切换世界观</div>
      <div
        v-for="world in worldData.worlds"
        :key="world.slug"
        class="world-switcher__item"
        :class="{ 'world-switcher__item--active': world.slug === worldData.currentWorldSlug }"
        @click.stop="selectWorld(world.slug)"
      >
        <span class="world-switcher__item-icon">🌌</span>
        <div class="world-switcher__item-content">
          <span class="world-switcher__item-name">{{ world.name }}</span>
          <span class="world-switcher__item-subtitle">{{ world.subtitle }}</span>
        </div>
        <span v-if="world.slug === worldData.currentWorldSlug" class="world-switcher__check">✓</span>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.world-switcher {
  position: relative;
}

.world-switcher__trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-gold);
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.world-switcher__trigger:hover {
  border-color: var(--color-gold-primary);
  box-shadow: var(--shadow-gold);
  background: var(--bg-card-hover);
}

.world-switcher__icon {
  font-size: 16px;
}

.world-switcher__name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.world-switcher__arrow {
  font-size: 10px;
  transition: transform var(--transition-fast);
  opacity: 0.7;
}

.world-switcher__arrow--open {
  transform: rotate(180deg);
}
</style>

<!-- 非 scoped 样式：Teleport 到 body 的下拉菜单需要全局样式 -->
<style>
.world-switcher__dropdown {
  background: rgba(13, 21, 37, 0.98) !important;
  border: 1px solid rgba(212, 168, 83, 0.5) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  z-index: 99999 !important;
  overflow: hidden;
  opacity: 1 !important;
  visibility: visible !important;
  display: block !important;
}

.world-switcher__header {
  padding: 12px 16px;
  font-size: 0.75rem;
  color: #6B7280;
  text-transform: uppercase;
  letter-spacing: 2px;
  border-bottom: 1px solid rgba(212, 168, 83, 0.1);
}

.world-switcher__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.15s ease;
  border-bottom: 1px solid rgba(212, 168, 83, 0.1);
}

.world-switcher__item:last-child {
  border-bottom: none;
}

.world-switcher__item:hover {
  background: rgba(212, 168, 83, 0.1);
}

.world-switcher__item--active {
  background: rgba(212, 168, 83, 0.15);
}

.world-switcher__item-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.world-switcher__item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.world-switcher__item-name {
  color: #F5F3EF;
  font-size: 1rem;
  font-weight: 600;
}

.world-switcher__item-subtitle {
  color: #6B7280;
  font-size: 0.75rem;
}

.world-switcher__check {
  color: #D4A853;
  font-size: 16px;
}
</style>
