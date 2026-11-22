<script setup>
/**
 * 族群列表 (Factions) - 原神风格
 *
 * 卡片网格布局，每张卡片展示一个族群
 * - 族群名、等级徽章(S/E/A/B/C)、类型(光明/暗网)
 * - 领地、人口、领袖
 * - 等级用不同颜色的原神风格徽章
 * - 悬停时卡片发光上浮
 * - 交错入场动画
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import { RouterLink } from 'vue-router'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)
const filterType = ref('') // 光明/暗网筛选

/** 等级配置 */
const gradeConfig = {
  S: { color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)', label: 'S' },
  E: { color: '#FF8C00', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)', label: 'E' },
  A: { color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)', label: 'A' },
  B: { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)', label: 'B' },
  C: { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)', label: 'C' },
}

function getGradeConfig(grade) {
  const key = String(grade || '').toUpperCase()
  return gradeConfig[key] || { color: 'var(--text-muted)', gradient: 'var(--bg-card-hover)', label: grade || '?' }
}

/** 类型颜色 */
function typeColor(type) {
  if (!type) return 'var(--text-muted)'
  if (type.includes('光明') || type.includes('light')) return 'var(--color-gold-primary)'
  if (type.includes('暗') || type.includes('dark')) return 'var(--rarity-epic)'
  return 'var(--color-cyan-primary)'
}

/** 筛选后的族群列表 */
const filteredFactions = computed(() => {
  if (!filterType.value) return worldData.factions
  return worldData.factions.filter((f) => {
    const t = f.type || ''
    if (filterType.value === 'light') return t.includes('光明') || t.includes('light')
    if (filterType.value === 'dark') return t.includes('暗') || t.includes('dark')
    return true
  })
})

onMounted(async () => {
  await worldData.loadFactions()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.faction-card')
    staggerList(cards, { stagger: 0.08 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content factions-page">
    <!-- 标题区域 -->
    <div class="factions-header">
      <div class="factions-header__deco">⚔</div>
      <h1 class="factions-header__title gold-shimmer-text">族群势力</h1>
      <p class="factions-header__subtitle">万族林立，各有传承</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar glass-panel">
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': !filterType }"
        @click="filterType = ''"
      >
        全部
      </button>
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': filterType === 'light' }"
        @click="filterType = 'light'"
      >
        光明阵营
      </button>
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': filterType === 'dark' }"
        @click="filterType = 'dark'"
      >
        暗网阵营
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="worldData.factionsLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在探查各族势力...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredFactions.length === 0" class="empty-state">
      <div class="empty-state__icon">⚔</div>
      <p class="empty-state__text">暂无族群数据</p>
    </div>

    <!-- 族群卡片网格 -->
    <div v-else ref="gridRef" class="grid-3">
      <RouterLink
        v-for="faction in filteredFactions"
        :key="faction.id"
        :to="`/factions/${faction.id}`"
        class="faction-card card card-gold"
      >
        <!-- 四角装饰 -->
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 等级徽章 -->
        <div
          class="faction-card__grade"
          :style="{ '--grade-color': getGradeConfig(faction.grade).color, '--grade-gradient': getGradeConfig(faction.grade).gradient }"
        >
          {{ getGradeConfig(faction.grade).label }}
        </div>

        <!-- 卡片内容 -->
        <div class="faction-card__body">
          <h3 class="faction-card__name">{{ faction.name }}</h3>

          <div class="faction-card__badges">
            <span
              class="faction-card__type"
              :style="{ color: typeColor(faction.type), borderColor: typeColor(faction.type) }"
            >
              {{ faction.type || '未知' }}
            </span>
          </div>

          <div class="faction-card__info">
            <div v-if="faction.territory" class="info-row">
              <span class="info-label">领地</span>
              <span class="info-value">{{ faction.territory }}</span>
            </div>
            <div v-if="faction.population" class="info-row">
              <span class="info-label">人口</span>
              <span class="info-value">{{ faction.population }}</span>
            </div>
            <div v-if="faction.leader" class="info-row">
              <span class="info-label">领袖</span>
              <span class="info-value">{{ faction.leader }}</span>
            </div>
          </div>

          <p v-if="faction.description" class="faction-card__desc">
            {{ faction.description }}
          </p>
        </div>

        <!-- 底部装饰 -->
        <div class="faction-card__footer">
          <span class="faction-card__arrow">查看详情 ›</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.factions-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.factions-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.factions-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.factions-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.factions-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.filter-btn {
  padding: var(--spacing-xs) var(--spacing-lg);
  border: 1px solid transparent;
  border-radius: var(--border-radius-md);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}

.filter-btn:hover {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.08);
}

.filter-btn--active {
  background: rgba(212, 168, 83, 0.15);
  color: var(--text-gold);
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 10px var(--color-gold-glow);
}

/* 族群卡片 */
.faction-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  padding: 0;
  overflow: hidden;
  position: relative;
}

.faction-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--border-color-active);
}

/* 等级徽章 */
.faction-card__grade {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--grade-gradient);
  color: #fff;
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 700;
  border-radius: 50%;
  border: 2px solid var(--grade-color);
  box-shadow: 0 0 12px color-mix(in srgb, var(--grade-color) 50%, transparent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  z-index: 2;
}

.faction-card__body {
  padding: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.faction-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-heading);
  margin-bottom: var(--spacing-sm);
  padding-right: 44px;
  transition: color var(--transition-fast);
}

.faction-card:hover .faction-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.faction-card__badges {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.faction-card__type {
  padding: 2px 10px;
  font-size: var(--font-size-xs);
  border: 1px solid;
  border-radius: var(--border-radius-sm);
  background: rgba(13, 21, 37, 0.6);
}

.faction-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 2px solid var(--color-gold-dark);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
}

.info-label {
  color: var(--text-muted);
}

.info-value {
  color: var(--text-primary);
  font-weight: 500;
}

.faction-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.faction-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}

.faction-card__arrow {
  font-size: var(--font-size-xs);
  color: var(--color-gold-dark);
  transition: color var(--transition-fast);
}

.faction-card:hover .faction-card__arrow {
  color: var(--color-gold-light);
}

/* 加载状态 */
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.empty-state__icon {
  font-size: 56px;
  margin-bottom: var(--spacing-md);
  filter: drop-shadow(0 0 12px var(--color-gold-glow));
}

.empty-state__text {
  color: var(--text-muted);
  font-size: var(--font-size-lg);
}

.genshin-loader {
  margin: 0 auto var(--spacing-md);
}

@media (max-width: 768px) {
  .factions-header__title {
    font-size: var(--font-size-3xl);
  }
}
</style>
