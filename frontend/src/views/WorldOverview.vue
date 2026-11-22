<script setup>
/**
 * 世界观总览 (WorldOverview) - 原神风格
 *
 * - 顶部大标题区域（动态显示当前大世界名称/副标题）
 * - 左侧导航树（根据当前世界的设定页面分类动态生成）
 * - 右侧内容区域，展示选中分类的设定内容
 * - 内容使用 LoreLink 组件渲染，自动识别术语
 * - 切换大世界后自动重新加载
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const worldData = useWorldDataStore()
const { fadeInUp } = useAnimations()

const pageRef = ref(null)
const contentRef = ref(null)
const activeCategory = ref('core')

/** 分类显示名映射 */
const categoryLabels = {
  core: '世界观核心',
  power: '力量体系',
  civilization: '文明体系',
  geography: '地理',
  history: '历史',
  creature: '异兽志',
  artifact: '宝物志',
  faction: '势力志',
  character: '人物志',
  other: '其他',
}

/** 分类图标映射 */
const categoryIcons = {
  core: '✦',
  power: '✨',
  civilization: '🏛',
  geography: '🗺',
  history: '📜',
  creature: '🐉',
  artifact: '🗡',
  faction: '⚔',
  character: '👤',
  other: '📋',
}

/** 根据当前世界的设定页面动态生成分类导航 */
const categories = computed(() => {
  const grouped = {}
  for (const page of worldData.lorePages) {
    const cat = page.category || 'other'
    if (!grouped[cat]) {
      grouped[cat] = {
        key: cat,
        name: categoryLabels[cat] || cat,
        icon: categoryIcons[cat] || '📋',
        sections: [],
      }
    }
    grouped[cat].sections.push({
      title: page.title,
      content: page.content || '',
      slug: page.slug,
    })
  }
  // 按 categoryLabels 的顺序排序
  const order = ['core', 'power', 'civilization', 'geography', 'history', 'creature', 'artifact', 'faction', 'character', 'other']
  return Object.values(grouped).sort((a, b) => order.indexOf(a.key) - order.indexOf(b.key))
})

/** 当前选中分类的内容 */
const currentCategory = computed(() => {
  return categories.value.find((c) => c.key === activeCategory.value) || categories.value[0] || null
})

/** 切换分类 */
function selectCategory(key) {
  activeCategory.value = key
  if (contentRef.value) {
    fadeInUp(contentRef.value, { duration: 0.4 })
  }
}

/** 加载当前世界的设定页面 */
async function loadWorldContent() {
  await worldData.loadLorePages()
  // 如果当前分类不存在，回退到第一个分类
  if (currentCategory.value) {
    activeCategory.value = currentCategory.value.key
  }
}

/** 监听世界切换，重新加载数据 */
watch(
  () => worldData.currentWorldSlug,
  () => {
    activeCategory.value = 'core'
    loadWorldContent()
  }
)

onMounted(async () => {
  // 预加载数据
  await worldData.preloadAll()
  await loadWorldContent()

  if (pageRef.value) {
    fadeInUp(pageRef.value)
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content world-overview">
    <!-- 顶部大标题区域 -->
    <div class="overview-header card card-gold">
      <div class="overview-header__deco">✦</div>
      <h1 class="overview-header__title gold-shimmer-text">
        {{ worldData.currentWorld?.name || '异世界' }}
      </h1>
      <p class="overview-header__subtitle">
        {{ worldData.currentWorld?.subtitle || '世界观设定档案库' }}
      </p>
      <div class="ornate-divider overview-header__divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 加载中状态 -->
    <div v-if="worldData.loreLoading" class="loading-state card">
      <div class="loading-spinner"></div>
      <p>正在加载世界观设定...</p>
    </div>

    <!-- 无数据状态 -->
    <div v-else-if="categories.length === 0" class="empty-state card">
      <div class="empty-state__icon">📜</div>
      <p>暂无世界观设定内容</p>
      <RouterLink to="/admin/worlds" class="btn-genshin">前往后台添加</RouterLink>
    </div>

    <!-- 左右分栏布局 -->
    <div v-else class="overview-body">
      <!-- 左侧导航树 -->
      <aside class="overview-nav glass-panel">
        <h3 class="overview-nav__title">分类导航</h3>
        <nav class="overview-nav__list">
          <button
            v-for="category in categories"
            :key="category.key"
            class="overview-nav__item"
            :class="{ 'overview-nav__item--active': activeCategory === category.key }"
            @click="selectCategory(category.key)"
          >
            <span class="overview-nav__icon">{{ category.icon }}</span>
            <span class="overview-nav__name">{{ category.name }}</span>
            <span class="overview-nav__count">{{ category.sections.length }}</span>
            <span class="overview-nav__arrow">›</span>
          </button>
        </nav>
      </aside>

      <!-- 右侧内容区域 -->
      <main ref="contentRef" class="overview-content">
        <div
          v-for="(section, index) in (currentCategory?.sections || [])"
          :key="index"
          class="card card-gold overview-section"
        >
          <!-- 四角装饰 -->
          <span class="ornate-corner ornate-corner--tl"></span>
          <span class="ornate-corner ornate-corner--tr"></span>
          <span class="ornate-corner ornate-corner--bl"></span>
          <span class="ornate-corner ornate-corner--br"></span>

          <h2 class="overview-section__title">
            <span class="overview-section__deco">◆</span>
            {{ section.title }}
          </h2>
          <div class="overview-section__content">
            <LoreLink :text="section.content" tag="p" />
          </div>
        </div>
      </main>
    </div>

    <!-- 统计数据 -->
    <div class="overview-stats">
      <h2 class="section-title">世界数据</h2>
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-card__icon">⚔</div>
          <div class="stat-card__value">{{ worldData.factions.length }}</div>
          <div class="stat-card__label">族群</div>
        </div>
        <div class="stat-card card">
          <div class="stat-card__icon">👤</div>
          <div class="stat-card__value">{{ worldData.characters.length }}</div>
          <div class="stat-card__label">角色</div>
        </div>
        <div class="stat-card card">
          <div class="stat-card__icon">🗡</div>
          <div class="stat-card__value">{{ worldData.artifacts.length }}</div>
          <div class="stat-card__label">宝物</div>
        </div>
        <div class="stat-card card">
          <div class="stat-card__icon">🐉</div>
          <div class="stat-card__value">{{ worldData.creatures.length }}</div>
          <div class="stat-card__label">异兽</div>
        </div>
        <div class="stat-card card">
          <div class="stat-card__icon">🌌</div>
          <div class="stat-card__value">{{ worldData.fragmentWorlds.length }}</div>
          <div class="stat-card__label">碎片世界</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.world-overview {
  padding-top: var(--spacing-xl);
}

/* 顶部标题 */
.overview-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-2xl);
  position: relative;
}

.overview-header__deco {
  font-size: 36px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-md);
  animation: goldSparkle 3s ease-in-out infinite;
}

.overview-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-sm);
  letter-spacing: 8px;
}

.overview-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 2px;
  margin-bottom: var(--spacing-md);
}

.overview-header__divider {
  max-width: 300px;
  margin: 0 auto;
}

/* 左右分栏 */
.overview-body {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

/* 左侧导航 */
.overview-nav {
  padding: var(--spacing-lg);
  height: fit-content;
  position: sticky;
  top: calc(var(--header-height) + var(--spacing-md));
}

.overview-nav__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--color-gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
}

.overview-nav__list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.overview-nav__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
  width: 100%;
  font-family: inherit;
}

.overview-nav__item:hover {
  background: rgba(212, 168, 83, 0.08);
  color: var(--text-gold);
  border-color: var(--border-color);
}

.overview-nav__item--active {
  background: rgba(212, 168, 83, 0.12);
  color: var(--text-gold);
  border-color: var(--border-color-active);
  box-shadow: inset 3px 0 0 var(--color-gold-primary);
}

.overview-nav__icon {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.overview-nav__name {
  flex: 1;
}

.overview-nav__count {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  background: rgba(212, 168, 83, 0.1);
  padding: 1px 6px;
  border-radius: var(--border-radius-sm);
}

.overview-nav__arrow {
  color: var(--color-gold-dark);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.overview-nav__item:hover .overview-nav__arrow,
.overview-nav__item--active .overview-nav__arrow {
  opacity: 1;
}

/* 右侧内容 */
.overview-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.overview-section {
  position: relative;
  padding: var(--spacing-xl);
}

.overview-section__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
}

.overview-section__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.overview-section__content {
  color: var(--text-primary);
  line-height: 2;
  font-size: var(--font-size-base);
}

/* 加载/空状态 */
.loading-state,
.empty-state {
  text-align: center;
  padding: var(--spacing-3xl);
  color: var(--text-secondary);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: var(--color-gold-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-md);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state__icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

/* 统计数据 */
.overview-stats {
  margin-top: var(--spacing-xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-md);
}

.stat-card {
  text-align: center;
  padding: var(--spacing-lg);
  position: relative;
}

.stat-card__icon {
  font-size: 32px;
  color: var(--color-gold-primary);
  margin-bottom: var(--spacing-sm);
  filter: drop-shadow(0 0 8px var(--color-gold-glow));
}

.stat-card__value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-gold);
  font-family: var(--font-family-display);
  margin-bottom: var(--spacing-xs);
}

.stat-card__label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

@media (max-width: 1024px) {
  .overview-body {
    grid-template-columns: 220px 1fr;
  }
}

@media (max-width: 768px) {
  .overview-body {
    grid-template-columns: 1fr;
  }

  .overview-nav {
    position: static;
  }

  .overview-nav__list {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .overview-nav__item {
    width: auto;
  }
}
</style>
