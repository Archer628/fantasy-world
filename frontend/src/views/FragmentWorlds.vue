<script setup>
/**
 * 碎片世界列表 (FragmentWorlds) - 原神风格
 *
 * 18个碎片世界的网格展示
 * - 每个碎片世界卡片包含：编号、名称、面积、人口、主导法则、危险等级
 * - 危险等级用颜色标识
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)
const searchKeyword = ref('')
const filterDanger = ref('')

/** 危险等级配置 */
const dangerConfig = {
  low: { label: '低危', color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
  medium: { label: '中危', color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)' },
  high: { label: '高危', color: '#FF8C00', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)' },
  extreme: { label: '极危', color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
}

/** 数字危险等级(1-5) → 文本键映射 */
const dangerLevelMap = {
  1: 'low', 2: 'low',
  3: 'medium',
  4: 'high',
  5: 'extreme',
}

function getDangerConfig(level) {
  const num = Number(level)
  const key = dangerLevelMap[num] || 'medium'
  return dangerConfig[key] || dangerConfig.medium
}

/** 筛选后的碎片世界列表 */
const filteredWorlds = computed(() => {
  let list = worldData.fragmentWorlds
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter((w) =>
      (w.name || '').toLowerCase().includes(kw) ||
      (w.code || w.number || '').toLowerCase().includes(kw) ||
      (w.dominant_law || w.law || '').toLowerCase().includes(kw)
    )
  }
  if (filterDanger.value) {
    list = list.filter((w) => {
      const num = Number(w.danger_level)
      const key = dangerLevelMap[num] || 'medium'
      return key === filterDanger.value
    })
  }
  return list
})

onMounted(async () => {
  await worldData.loadFragmentWorlds()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.world-card')
    staggerList(cards, { stagger: 0.08 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content fragment-worlds-page">
    <!-- 标题区域 -->
    <div class="worlds-header">
      <div class="worlds-header__deco">🌌</div>
      <h1 class="worlds-header__title gold-shimmer-text">碎片世界</h1>
      <p class="worlds-header__subtitle">十八世界，法则各异</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 总览介绍 -->
    <div class="card card-gold intro-card">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <h2 class="intro-card__title">
        <span class="intro-card__deco">◆</span>
        碎片之源
      </h2>
      <div class="intro-card__content">
        <LoreLink text="远古时代，原初之神将混沌之力凝聚为无数碎片。每一枚碎片都演化出一个独立的世界，拥有独特的法则与生态。其中最为稳定的十八枚碎片形成了如今的十八碎片世界。这些碎片世界既是机遇之地，也是危险之源。碎片世界之间通过虚空通道相连，但通道并不稳定，时有崩塌。" tag="p" />
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="card card-gold filter-bar">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <div class="filter-bar__search">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索世界名称或法则..."
          class="filter-bar__input"
        />
      </div>

      <select v-model="filterDanger" class="filter-bar__select">
        <option value="">全部危险等级</option>
        <option value="low">低危</option>
        <option value="medium">中危</option>
        <option value="high">高危</option>
        <option value="extreme">极危</option>
      </select>
    </div>

    <!-- 加载状态 -->
    <div v-if="worldData.fragmentWorldsLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在探索碎片世界...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredWorlds.length === 0" class="empty-state">
      <div class="empty-state__icon">🌌</div>
      <p class="empty-state__text">暂无符合条件的碎片世界</p>
    </div>

    <!-- 碎片世界卡片网格 -->
    <div v-else ref="gridRef" class="grid-3">
      <RouterLink
        v-for="world in filteredWorlds"
        :key="world.id"
        :to="`/fragment-worlds/${world.id}`"
        class="world-card card card-gold"
        :style="{ '--danger-color': getDangerConfig(world.danger_level).color, '--danger-gradient': getDangerConfig(world.danger_level).gradient }"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 编号 -->
        <div class="world-card__code">
          No.{{ String(world.code || world.number || world.id).padStart(2, '0') }}
        </div>

        <!-- 危险等级 -->
        <div class="world-card__danger">
          {{ getDangerConfig(world.danger_level).label }}
        </div>

        <!-- 卡片内容 -->
        <div class="world-card__body">
          <h3 class="world-card__name">{{ world.name }}</h3>

          <div class="world-card__info">
            <div v-if="world.dominant_law || world.law" class="info-row">
              <span class="info-label">主导法则</span>
              <span class="info-value">{{ world.dominant_law || world.law }}</span>
            </div>
            <div v-if="world.area || world.size" class="info-row">
              <span class="info-label">面积</span>
              <span class="info-value">{{ world.area || world.size }}</span>
            </div>
            <div v-if="world.population" class="info-row">
              <span class="info-label">人口</span>
              <span class="info-value">{{ world.population }}</span>
            </div>
          </div>

          <p v-if="world.description" class="world-card__desc">
            {{ world.description }}
          </p>
        </div>

        <!-- 底部装饰 -->
        <div class="world-card__footer">
          <span class="world-card__arrow">进入世界 ›</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.fragment-worlds-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.worlds-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.worlds-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.worlds-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.worlds-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
}

/* 总览介绍 */
.intro-card {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.intro-card__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
}

.intro-card__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.intro-card__content {
  color: var(--text-primary);
  line-height: 2;
  font-size: var(--font-size-base);
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
  flex-wrap: wrap;
}

.filter-bar__search {
  flex: 1;
  min-width: 200px;
}

.filter-bar__input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.filter-bar__input:focus {
  outline: none;
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 8px var(--color-gold-glow);
}

.filter-bar__select {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
}

.filter-bar__select:focus {
  outline: none;
  border-color: var(--color-gold-primary);
}

/* 碎片世界卡片 */
.world-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  position: relative;
}

.world-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 25px rgba(212, 168, 83, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.5);
}

.world-card__code {
  position: absolute;
  top: var(--spacing-sm);
  left: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xs);
  color: var(--color-gold-dark);
  letter-spacing: 1px;
  z-index: 2;
}

.world-card__danger {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  padding: 2px 8px;
  background: var(--danger-gradient);
  color: #fff;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 600;
  letter-spacing: 1px;
  z-index: 2;
  box-shadow: 0 0 8px color-mix(in srgb, var(--danger-color) 50%, transparent);
}

.world-card__body {
  padding: var(--spacing-lg);
  padding-top: var(--spacing-xl);
  flex: 1;
}

.world-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
}

.world-card__info {
  margin-bottom: var(--spacing-sm);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.info-label {
  color: var(--text-muted);
}

.info-value {
  color: var(--text-secondary);
}

.world-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.world-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}

.world-card__arrow {
  font-size: var(--font-size-xs);
  color: var(--color-gold-primary);
  letter-spacing: 1px;
}

@media (max-width: 768px) {
  .worlds-header__title {
    font-size: var(--font-size-3xl);
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-bar__select {
    width: 100%;
  }
}
</style>
