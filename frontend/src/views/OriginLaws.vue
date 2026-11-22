<script setup>
/**
 * 本源法则 (OriginLaws) - 原神风格
 *
 * 按层级分组展示本源法则，共四个层级：
 * - 根源二元层 (root)
 * - 时空框架层 (framework)
 * - 演化博弈层 (evolution)
 * - 具象叙事层 (narrative)
 *
 * 每张卡片展示：法则名称、层级徽章、核心定义、可用术式方向、过度亲和副作用
 * 支持按层级筛选
 */
import { ref, onMounted, computed, nextTick } from 'vue'
import { originLawApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import { RouterLink } from 'vue-router'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const laws = ref([])
const loading = ref(true)
const selectedTier = ref('')

/** 层级配置 */
const tierLabels = {
  'root': '根源二元层',
  'framework': '时空框架层',
  'evolution': '演化博弈层',
  'narrative': '具象叙事层',
}

/** 层级颜色配置 */
const tierColors = {
  'root': { color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
  'framework': { color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)' },
  'evolution': { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)' },
  'narrative': { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
}

/** 层级展示顺序 */
const tierOrder = ['root', 'framework', 'evolution', 'narrative']

function getTierColor(tier) {
  return tierColors[tier] || { color: 'var(--text-muted)', gradient: 'var(--bg-card-hover)' }
}

/** 按层级分组的法则（应用筛选） */
const groupedLaws = computed(() => {
  const groups = {}
  tierOrder.forEach((t) => { groups[t] = [] })
  laws.value.forEach((law) => {
    if (!selectedTier.value || law.tier === selectedTier.value) {
      if (groups[law.tier]) groups[law.tier].push(law)
    }
  })
  return groups
})

/** 当前展示的层级列表（筛选后非空的层级） */
const visibleTiers = computed(() => {
  return tierOrder.filter((t) => groupedLaws.value[t] && groupedLaws.value[t].length > 0)
})

/** 将可能为字符串/数组的术式方向格式化为数组展示 */
function formatDirections(val) {
  if (!val) return []
  if (Array.isArray(val)) return val
  return String(val).split(/[,，、;；\n]/).map((s) => s.trim()).filter(Boolean)
}

async function loadLaws() {
  loading.value = true
  try {
    // 确保当前世界 slug 已就绪，避免首次进入时为空
    const slug = await worldData.ensureCurrentWorld()
    const data = await originLawApi.list({ world: slug })
    laws.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    console.error('加载本源法则失败', e)
    laws.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadLaws()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  // 对每个层级的卡片执行错位入场动画
  document.querySelectorAll('.law-group__grid').forEach((grid) => {
    const cards = grid.querySelectorAll('.law-card')
    staggerList(cards, { stagger: 0.08 })
  })
})
</script>

<template>
  <div ref="pageRef" class="page-content origin-laws-page">
    <!-- 标题区域 -->
    <div class="laws-header">
      <div class="laws-header__deco">✦</div>
      <h1 class="laws-header__title gold-shimmer-text">本源法则</h1>
      <p class="laws-header__subtitle">万物运转之根，诸界秩序之源</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 层级筛选栏 -->
    <div class="filter-bar glass-panel">
      <button
        class="filter-btn"
        :class="{ 'filter-btn--active': !selectedTier }"
        @click="selectedTier = ''"
      >
        全部层级
      </button>
      <button
        v-for="t in tierOrder"
        :key="t"
        class="filter-btn"
        :class="{ 'filter-btn--active': selectedTier === t }"
        :style="selectedTier === t ? { borderColor: getTierColor(t).color, color: getTierColor(t).color } : {}"
        @click="selectedTier = t"
      >
        {{ tierLabels[t] }}
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在推演本源法则...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="laws.length === 0" class="empty-state">
      <div class="empty-state__icon">✦</div>
      <p class="empty-state__text">暂无法则数据</p>
    </div>

    <!-- 按层级分组展示 -->
    <template v-else>
      <section
        v-for="tier in visibleTiers"
        :key="tier"
        class="law-group"
      >
        <h2 class="law-group__title">
          <span
            class="law-group__badge"
            :style="{ background: getTierColor(tier).gradient, borderColor: getTierColor(tier).color }"
          >
            {{ tierLabels[tier] }}
          </span>
          <span class="law-group__count">{{ groupedLaws[tier].length }} 条法则</span>
        </h2>

        <div class="law-group__grid">
          <RouterLink
            v-for="law in groupedLaws[tier]"
            :key="law.id"
            :to="`/origin-laws/${law.id}`"
            class="law-card card card-gold"
          >
            <!-- 四角装饰 -->
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <!-- 层级徽章 -->
            <div
              class="law-card__tier"
              :style="{ '--tier-color': getTierColor(law.tier).color, '--tier-gradient': getTierColor(law.tier).gradient }"
            >
              {{ tierLabels[law.tier] || law.tier || '未知' }}
            </div>

            <!-- 卡片内容 -->
            <div class="law-card__body">
              <h3 class="law-card__name">{{ law.name }}</h3>

              <div v-if="law.core_definition" class="law-card__field">
                <span class="law-card__label">核心定义</span>
                <p class="law-card__text">{{ law.core_definition }}</p>
              </div>

              <div v-if="formatDirections(law.ability_directions).length" class="law-card__field">
                <span class="law-card__label">可用术式方向</span>
                <div class="law-card__tags">
                  <span
                    v-for="(dir, i) in formatDirections(law.ability_directions)"
                    :key="i"
                    class="law-card__tag"
                  >
                    {{ dir }}
                  </span>
                </div>
              </div>

              <div v-if="law.side_effect" class="law-card__field law-card__field--warn">
                <span class="law-card__label">过度亲和副作用</span>
                <p class="law-card__text law-card__text--warn">{{ law.side_effect }}</p>
              </div>
            </div>

            <!-- 底部装饰 -->
            <div class="law-card__footer">
              <span class="law-card__arrow">查看详情 ›</span>
            </div>
          </RouterLink>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.origin-laws-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.laws-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.laws-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.laws-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.laws-header__subtitle {
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
  margin-bottom: var(--spacing-xl);
  flex-wrap: wrap;
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

/* 层级分组 */
.law-group {
  margin-bottom: var(--spacing-2xl);
}

.law-group__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-heading);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
}

.law-group__badge {
  padding: 4px 14px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: #fff;
  border-radius: var(--border-radius-md);
  border: 1px solid;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  box-shadow: 0 0 10px color-mix(in srgb, currentColor 30%, transparent);
}

.law-group__count {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  font-family: var(--font-family);
  letter-spacing: 1px;
}

.law-group__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: var(--spacing-lg);
}

/* 法则卡片 */
.law-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  padding: 0;
  overflow: hidden;
  position: relative;
}

.law-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--border-color-active);
}

/* 层级徽章 */
.law-card__tier {
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--tier-gradient);
  color: #fff;
  font-size: var(--font-size-xs);
  font-weight: 600;
  letter-spacing: 1px;
  text-align: center;
  border-bottom: 2px solid var(--tier-color);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.law-card__body {
  padding: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.law-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  letter-spacing: 1px;
  transition: color var(--transition-fast);
}

.law-card:hover .law-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.law-card__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.law-card__label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.law-card__text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.law-card__field--warn {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(255, 71, 87, 0.08);
  border-left: 2px solid var(--color-danger);
  border-radius: var(--border-radius-sm);
}

.law-card__text--warn {
  color: #FFB3BA;
  -webkit-line-clamp: 2;
}

.law-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.law-card__tag {
  padding: 2px 10px;
  font-size: var(--font-size-xs);
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  border-radius: var(--border-radius-sm);
  color: var(--text-gold);
}

.law-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}

.law-card__arrow {
  font-size: var(--font-size-xs);
  color: var(--color-gold-dark);
  transition: color var(--transition-fast);
}

.law-card:hover .law-card__arrow {
  color: var(--color-gold-light);
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
  .laws-header__title {
    font-size: var(--font-size-3xl);
  }

  .law-group__grid {
    grid-template-columns: 1fr;
  }
}
</style>
