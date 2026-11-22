<script setup>
/**
 * 宝物列表 (Artifacts) - 原神风格
 *
 * 卡片网格布局
 * - 卡片包含：宝物名、种类、稀有度（用RarityBadge）、拥有者
 * - 稀有度用原神风格彩色边框
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import RarityBadge from '@/components/common/RarityBadge.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)
const selectedRarity = ref('')

/** 稀有度筛选选项 */
const rarities = [
  { value: 'common', label: '普通' },
  { value: 'uncommon', label: '优秀' },
  { value: 'rare', label: '稀有' },
  { value: 'epic', label: '史诗' },
  { value: 'legendary', label: '传说' },
  { value: 'mythic', label: '神话' },
]

/** 稀有度边框颜色映射 */
const rarityBorderColors = {
  common: 'var(--rarity-common)',
  uncommon: 'var(--rarity-uncommon)',
  rare: 'var(--rarity-rare)',
  epic: 'var(--rarity-epic)',
  legendary: 'var(--rarity-legendary)',
  mythic: 'var(--rarity-mythic)',
  '普通': 'var(--rarity-common)',
  '优秀': 'var(--rarity-uncommon)',
  '稀有': 'var(--rarity-rare)',
  '史诗': 'var(--rarity-epic)',
  '传说': 'var(--rarity-legendary)',
  '神话': 'var(--rarity-mythic)',
}

function getRarityColor(rarity) {
  return rarityBorderColors[rarity] || 'var(--border-color)'
}

/** 筛选后的宝物列表 */
const filteredArtifacts = computed(() => {
  if (!selectedRarity.value) return worldData.artifacts
  return worldData.artifacts.filter((a) => a.rarity === selectedRarity.value)
})

onMounted(async () => {
  await worldData.loadArtifacts()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.artifact-card')
    staggerList(cards, { stagger: 0.08 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content artifacts-page">
    <!-- 标题区域 -->
    <div class="artifacts-header">
      <div class="artifacts-header__deco">🗡</div>
      <h1 class="artifacts-header__title gold-shimmer-text">神兵宝物</h1>
      <p class="artifacts-header__subtitle">神器遗珍，蕴藏远古之力</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 稀有度筛选 -->
    <div class="filter-bar glass-panel">
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': !selectedRarity }"
        @click="selectedRarity = ''"
      >
        全部
      </button>
      <button
        v-for="rarity in rarities"
        :key="rarity.value"
        class="filter-btn"
        :class="{ 'filter-btn--active': selectedRarity === rarity.value }"
        :style="selectedRarity === rarity.value ? { color: getRarityColor(rarity.value), borderColor: getRarityColor(rarity.value) } : {}"
        @click="selectedRarity = rarity.value"
      >
        {{ rarity.label }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="worldData.artifactsLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在搜寻神兵宝物...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredArtifacts.length === 0" class="empty-state">
      <div class="empty-state__icon">🗡</div>
      <p class="empty-state__text">暂无宝物数据</p>
    </div>

    <!-- 宝物卡片网格 -->
    <div v-else ref="gridRef" class="grid-3">
      <RouterLink
        v-for="artifact in filteredArtifacts"
        :key="artifact.id"
        :to="`/artifacts/${artifact.id}`"
        class="artifact-card card"
        :style="{ '--rarity-color': getRarityColor(artifact.rarity) }"
      >
        <!-- 四角装饰 -->
        <span class="ornate-corner ornate-corner--tl" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>
        <span class="ornate-corner ornate-corner--tr" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>
        <span class="ornate-corner ornate-corner--bl" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>
        <span class="ornate-corner ornate-corner--br" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>

        <!-- 稀有度光晕 -->
        <div class="artifact-card__glow" :style="{ background: getRarityColor(artifact.rarity) }"></div>

        <!-- 卡片内容 -->
        <div class="artifact-card__body">
          <div class="artifact-card__header">
            <div class="artifact-card__icon">🗡</div>
            <RarityBadge v-if="artifact.rarity" :rarity="artifact.rarity" />
          </div>

          <h3 class="artifact-card__name">{{ artifact.name }}</h3>

          <div class="artifact-card__info">
            <div v-if="artifact.type || artifact.category" class="info-row">
              <span class="info-label">种类</span>
              <span class="info-value">{{ artifact.type || artifact.category }}</span>
            </div>
            <div v-if="artifact.owner || artifact.owner_name" class="info-row">
              <span class="info-label">拥有者</span>
              <span class="info-value">{{ artifact.owner || artifact.owner_name }}</span>
            </div>
          </div>

          <p v-if="artifact.description" class="artifact-card__desc">
            {{ artifact.description }}
          </p>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.artifacts-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.artifacts-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.artifacts-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.artifacts-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.artifacts-header__subtitle {
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
  flex-wrap: wrap;
}

.filter-btn {
  padding: var(--spacing-xs) var(--spacing-md);
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

/* 宝物卡片 */
.artifact-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  padding: 0;
  overflow: hidden;
  position: relative;
  border-color: var(--rarity-color, var(--border-color));
}

.artifact-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px color-mix(in srgb, var(--rarity-color, var(--color-gold-primary)) 40%, transparent), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--rarity-color, var(--border-color-active));
}

/* 稀有度光晕 */
.artifact-card__glow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  opacity: 0.6;
  filter: blur(8px);
}

/* 卡片内容 */
.artifact-card__body {
  padding: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.artifact-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.artifact-card__icon {
  font-size: 36px;
  filter: drop-shadow(0 0 10px var(--rarity-color, var(--color-gold-glow)));
  transition: transform var(--transition-normal);
}

.artifact-card:hover .artifact-card__icon {
  transform: scale(1.15) rotate(-10deg);
}

.artifact-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-heading);
  margin-bottom: var(--spacing-sm);
  transition: color var(--transition-fast);
}

.artifact-card:hover .artifact-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.artifact-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 2px solid var(--rarity-color, var(--color-gold-dark));
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

.artifact-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 加载/空状态 */
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
  .artifacts-header__title {
    font-size: var(--font-size-3xl);
  }
}
</style>
