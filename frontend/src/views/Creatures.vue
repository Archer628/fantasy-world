<script setup>
/**
 * 异兽图鉴 (Creatures) - 原神风格
 *
 * 卡片网格布局
 * - 卡片包含：异兽名、物种、危险等级(1-5星)、栖息地
 * - 危险等级用骷髅图标显示
 * - 支持按危险等级和物种筛选
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
const filterSpecies = ref('')

/** 危险等级配置 */
const dangerConfig = {
  1: { label: '低危', color: '#50C878', skulls: 1, desc: '对凡人无威胁' },
  2: { label: '中危', color: '#4A7FBB', skulls: 2, desc: '需凡境修炼者应对' },
  3: { label: '高危', color: '#FF8C00', skulls: 3, desc: '需灵境修炼者应对' },
  4: { label: '极危', color: '#FF4757', skulls: 4, desc: '需灵境后期修炼者应对' },
  5: { label: '灾厄', color: '#9B59B6', skulls: 5, desc: '需神境修炼者方能抗衡' },
}

function getDangerConfig(level) {
  return dangerConfig[level] || dangerConfig[1]
}

/** 所有物种列表 */
const allSpecies = computed(() => {
  const species = new Set()
  worldData.creatures.forEach((c) => {
    if (c.species || c.type) species.add(c.species || c.type)
  })
  return Array.from(species).sort()
})

/** 筛选后的异兽列表 */
const filteredCreatures = computed(() => {
  let list = worldData.creatures
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter((c) =>
      (c.name || '').toLowerCase().includes(kw) ||
      (c.description || '').toLowerCase().includes(kw)
    )
  }
  if (filterDanger.value) {
    list = list.filter((c) => Number(c.danger_level) === Number(filterDanger.value))
  }
  if (filterSpecies.value) {
    list = list.filter((c) => (c.species || c.type) === filterSpecies.value)
  }
  return list
})

onMounted(async () => {
  await worldData.loadCreatures()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.creature-card')
    staggerList(cards, { stagger: 0.08 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content creatures-page">
    <!-- 标题区域 -->
    <div class="creatures-header">
      <div class="creatures-header__deco">🐉</div>
      <h1 class="creatures-header__title gold-shimmer-text">异兽图鉴</h1>
      <p class="creatures-header__subtitle">万界生灵，危险与机遇并存</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
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
          placeholder="搜索异兽名称..."
          class="filter-bar__input"
        />
      </div>

      <div class="filter-bar__selects">
        <select v-model="filterSpecies" class="filter-bar__select">
          <option value="">全部物种</option>
          <option v-for="sp in allSpecies" :key="sp" :value="sp">{{ sp }}</option>
        </select>

        <select v-model="filterDanger" class="filter-bar__select">
          <option value="">全部危险等级</option>
          <option v-for="n in 5" :key="n" :value="n">{{ getDangerConfig(n).label }} ({{ n }}星)</option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="worldData.creaturesLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在加载异兽图鉴...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredCreatures.length === 0" class="empty-state">
      <div class="empty-state__icon">🐉</div>
      <p class="empty-state__text">暂无符合条件的异兽数据</p>
    </div>

    <!-- 异兽卡片网格 -->
    <div v-else ref="gridRef" class="grid-3">
      <RouterLink
        v-for="creature in filteredCreatures"
        :key="creature.id"
        :to="`/creatures/${creature.id}`"
        class="creature-card card card-gold"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 危险等级标识 -->
        <div
          class="creature-card__danger"
          :style="{ '--danger-color': getDangerConfig(creature.danger_level).color }"
        >
          <span
            v-for="n in getDangerConfig(creature.danger_level).skulls"
            :key="n"
            class="creature-card__skull"
          >☠</span>
        </div>

        <!-- 卡片内容 -->
        <div class="creature-card__body">
          <h3 class="creature-card__name">{{ creature.name }}</h3>

          <div class="creature-card__tags">
            <span v-if="creature.species || creature.type" class="creature-card__species">
              {{ creature.species || creature.type }}
            </span>
            <span
              class="creature-card__danger-label"
              :style="{ color: getDangerConfig(creature.danger_level).color }"
            >
              {{ getDangerConfig(creature.danger_level).label }}
            </span>
          </div>

          <div class="creature-card__info">
            <div v-if="creature.habitat" class="info-row">
              <span class="info-label">栖息地</span>
              <span class="info-value">{{ creature.habitat }}</span>
            </div>
          </div>

          <p v-if="creature.description" class="creature-card__desc">
            {{ creature.description }}
          </p>
        </div>

        <!-- 底部装饰 -->
        <div class="creature-card__footer">
          <span class="creature-card__arrow">查看详情 ›</span>
        </div>
      </RouterLink>
    </div>

    <!-- 危险等级说明 -->
    <h2 class="section-title">危险等级说明</h2>
    <div class="card card-gold danger-guide">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <div class="danger-guide__list">
        <div
          v-for="n in 5"
          :key="n"
          class="danger-guide__item"
          :style="{ '--danger-color': getDangerConfig(n).color }"
        >
          <div class="danger-guide__skulls">
            <span v-for="s in n" :key="s">☠</span>
          </div>
          <div class="danger-guide__info">
            <span class="danger-guide__label">{{ getDangerConfig(n).label }}</span>
            <span class="danger-guide__desc">{{ getDangerConfig(n).desc }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.creatures-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.creatures-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.creatures-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.creatures-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.creatures-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
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

.filter-bar__selects {
  display: flex;
  gap: var(--spacing-sm);
}

.filter-bar__select {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-bar__select:focus {
  outline: none;
  border-color: var(--color-gold-primary);
}

/* 异兽卡片 */
.creature-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  position: relative;
}

.creature-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 25px rgba(212, 168, 83, 0.3),
    0 8px 32px rgba(0, 0, 0, 0.5);
}

.creature-card__danger {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  display: flex;
  gap: 2px;
  z-index: 2;
}

.creature-card__skull {
  font-size: 14px;
  color: var(--danger-color);
  text-shadow: 0 0 6px currentColor;
}

.creature-card__body {
  padding: var(--spacing-lg);
  flex: 1;
}

.creature-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
}

.creature-card__tags {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap;
}

.creature-card__species {
  padding: 2px 8px;
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  color: var(--text-gold);
}

.creature-card__danger-label {
  padding: 2px 8px;
  border: 1px solid currentColor;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.creature-card__info {
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

.creature-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.creature-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}

.creature-card__arrow {
  font-size: var(--font-size-xs);
  color: var(--color-gold-primary);
  letter-spacing: 1px;
}

/* 危险等级说明 */
.danger-guide {
  padding: var(--spacing-xl);
}

.danger-guide__list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--spacing-md);
}

.danger-guide__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 3px solid var(--danger-color);
}

.danger-guide__skulls {
  font-size: 18px;
  color: var(--danger-color);
  text-shadow: 0 0 8px currentColor;
  display: flex;
  gap: 2px;
}

.danger-guide__info {
  display: flex;
  flex-direction: column;
}

.danger-guide__label {
  font-family: var(--font-family-display);
  color: var(--danger-color);
  font-size: var(--font-size-base);
  font-weight: 600;
}

.danger-guide__desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .creatures-header__title {
    font-size: var(--font-size-3xl);
  }

  .filter-bar {
    flex-direction: column;
  }

  .filter-bar__selects {
    width: 100%;
  }

  .filter-bar__select {
    flex: 1;
  }

  .danger-guide__list {
    grid-template-columns: 1fr;
  }
}
</style>
