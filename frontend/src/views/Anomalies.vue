<script setup>
/**
 * 异常物图鉴 (Anomalies) - 原神风格
 *
 * 卡片网格布局，每张卡片展示一个异常物：
 * - 名称、危险等级徽章(C/B/A/S/X，带颜色编码)
 * - 法则属性、功能类型、外形、能力、副作用
 *
 * 支持按危险等级与关键字筛选
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { anomalyApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import { RouterLink } from 'vue-router'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)
const anomalies = ref([])
const loading = ref(true)
const searchKeyword = ref('')
const filterDanger = ref('')

/**
 * 危险等级配置
 * C: 灰蓝 - 低危
 * B: 绿色 - 中低危
 * A: 蓝色 - 中危
 * S: 紫色 - 高危
 * X: 红色 - 极危
 */
const dangerConfig = {
  C: { label: 'C 级', desc: '低危', color: '#8B9DC3', gradient: 'linear-gradient(135deg, #5A6B8A, #8B9DC3)' },
  B: { label: 'B 级', desc: '中低危', color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
  A: { label: 'A 级', desc: '中危', color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)' },
  S: { label: 'S 级', desc: '高危', color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)' },
  X: { label: 'X 级', desc: '极危', color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
}

const dangerOrder = ['C', 'B', 'A', 'S', 'X']

function getDangerConfig(level) {
  const key = String(level || '').toUpperCase()
  return dangerConfig[key] || {
    label: level || '?',
    desc: '未知',
    color: 'var(--text-muted)',
    gradient: 'var(--bg-card-hover)',
  }
}

/** 筛选后的异常物列表 */
const filteredAnomalies = computed(() => {
  let list = anomalies.value
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    list = list.filter((a) =>
      (a.name || '').toLowerCase().includes(kw) ||
      (a.ability || '').toLowerCase().includes(kw) ||
      (a.law_attribute || '').toLowerCase().includes(kw)
    )
  }
  if (filterDanger.value) {
    list = list.filter((a) => String(a.danger_level || '').toUpperCase() === filterDanger.value)
  }
  return list
})

async function loadAnomalies() {
  loading.value = true
  try {
    // 确保当前世界 slug 已就绪，避免首次进入时为空
    const slug = await worldData.ensureCurrentWorld()
    const data = await anomalyApi.list({ world: slug })
    anomalies.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    console.error('加载异常物失败', e)
    anomalies.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadAnomalies()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.anomaly-card')
    staggerList(cards, { stagger: 0.08 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content anomalies-page">
    <!-- 标题区域 -->
    <div class="anomalies-header">
      <div class="anomalies-header__deco">◈</div>
      <h1 class="anomalies-header__title gold-shimmer-text">异常物图鉴</h1>
      <p class="anomalies-header__subtitle">法则溢出之产物，秩序之外的异物</p>
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
          placeholder="搜索异常物名称、能力或法则属性..."
          class="filter-bar__input"
        />
      </div>

      <div class="filter-bar__selects">
        <select v-model="filterDanger" class="filter-bar__select">
          <option value="">全部危险等级</option>
          <option v-for="lv in dangerOrder" :key="lv" :value="lv">
            {{ getDangerConfig(lv).label }} - {{ getDangerConfig(lv).desc }}
          </option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在收录异常物...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredAnomalies.length === 0" class="empty-state">
      <div class="empty-state__icon">◈</div>
      <p class="empty-state__text">暂无符合条件的异常物数据</p>
    </div>

    <!-- 异常物卡片网格 -->
    <div v-else ref="gridRef" class="grid-3">
      <RouterLink
        v-for="anomaly in filteredAnomalies"
        :key="anomaly.id"
        :to="`/anomalies/${anomaly.id}`"
        class="anomaly-card card card-gold"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 危险等级徽章 -->
        <div
          class="anomaly-card__danger"
          :style="{ '--danger-color': getDangerConfig(anomaly.danger_level).color, '--danger-gradient': getDangerConfig(anomaly.danger_level).gradient }"
        >
          <span class="anomaly-card__danger-letter">{{ String(anomaly.danger_level || '?').toUpperCase() }}</span>
          <span class="anomaly-card__danger-desc">{{ getDangerConfig(anomaly.danger_level).desc }}</span>
        </div>

        <!-- 卡片内容 -->
        <div class="anomaly-card__body">
          <h3 class="anomaly-card__name">{{ anomaly.name }}</h3>

          <div class="anomaly-card__tags">
            <span v-if="anomaly.law_attribute" class="anomaly-card__tag">
              {{ anomaly.law_attribute }}
            </span>
            <span v-if="anomaly.function_type" class="anomaly-card__tag anomaly-card__tag--type">
              {{ anomaly.function_type }}
            </span>
          </div>

          <div class="anomaly-card__info">
            <div v-if="anomaly.appearance" class="info-row">
              <span class="info-label">外形</span>
              <span class="info-value">{{ anomaly.appearance }}</span>
            </div>
            <div v-if="anomaly.ability" class="info-row info-row--ability">
              <span class="info-label">能力</span>
              <span class="info-value info-value--clamp">{{ anomaly.ability }}</span>
            </div>
            <div v-if="anomaly.side_effect" class="info-row info-row--warn">
              <span class="info-label">副作用</span>
              <span class="info-value info-value--warn">{{ anomaly.side_effect }}</span>
            </div>
          </div>
        </div>

        <!-- 底部装饰 -->
        <div class="anomaly-card__footer">
          <span class="anomaly-card__arrow">查看详情 ›</span>
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
          v-for="lv in dangerOrder"
          :key="lv"
          class="danger-guide__item"
          :style="{ '--danger-color': getDangerConfig(lv).color, '--danger-gradient': getDangerConfig(lv).gradient }"
        >
          <div class="danger-guide__badge">{{ lv }}</div>
          <div class="danger-guide__info">
            <span class="danger-guide__label">{{ getDangerConfig(lv).label }} · {{ getDangerConfig(lv).desc }}</span>
            <span class="danger-guide__desc">需对应层级力量方可收容</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.anomalies-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.anomalies-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.anomalies-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.anomalies-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.anomalies-header__subtitle {
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

/* 异常物卡片 */
.anomaly-card {
  display: flex;
  flex-direction: column;
  padding: 0;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  position: relative;
}

.anomaly-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--border-color-active);
}

/* 危险等级徽章 */
.anomaly-card__danger {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--danger-gradient);
  border-bottom: 2px solid var(--danger-color);
  box-shadow: 0 0 12px color-mix(in srgb, var(--danger-color) 40%, transparent);
}

.anomaly-card__danger-letter {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
  line-height: 1;
}

.anomaly-card__danger-desc {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.9);
  letter-spacing: 1px;
}

.anomaly-card__body {
  padding: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.anomaly-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
  transition: color var(--transition-fast);
}

.anomaly-card:hover .anomaly-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.anomaly-card__tags {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
}

.anomaly-card__tag {
  padding: 2px 8px;
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  color: var(--text-gold);
}

.anomaly-card__tag--type {
  background: rgba(0, 212, 170, 0.08);
  border-color: var(--color-cyan-dark);
  color: var(--color-cyan-primary);
}

.anomaly-card__info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 2px solid var(--color-gold-dark);
}

.info-row {
  display: flex;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  align-items: flex-start;
}

.info-row--ability {
  border-left: 2px solid var(--color-cyan-dark);
  padding-left: var(--spacing-sm);
  margin-left: calc(var(--spacing-sm) * -1);
  border-radius: 0 var(--border-radius-sm) var(--border-radius-sm) 0;
  background: rgba(0, 212, 170, 0.04);
}

.info-row--warn {
  border-left: 2px solid var(--color-danger);
  padding-left: var(--spacing-sm);
  margin-left: calc(var(--spacing-sm) * -1);
  border-radius: 0 var(--border-radius-sm) var(--border-radius-sm) 0;
  background: rgba(255, 71, 87, 0.05);
}

.info-label {
  color: var(--text-muted);
  flex-shrink: 0;
  min-width: 42px;
}

.info-value {
  color: var(--text-secondary);
  flex: 1;
  word-break: break-word;
}

.info-value--clamp {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.info-value--warn {
  color: #FFB3BA;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.anomaly-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}

.anomaly-card__arrow {
  font-size: var(--font-size-xs);
  color: var(--color-gold-dark);
  transition: color var(--transition-fast);
}

.anomaly-card:hover .anomaly-card__arrow {
  color: var(--color-gold-light);
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

.danger-guide__badge {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--danger-gradient);
  color: #fff;
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  font-weight: 700;
  border-radius: 50%;
  border: 2px solid var(--danger-color);
  box-shadow: 0 0 12px color-mix(in srgb, var(--danger-color) 50%, transparent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  flex-shrink: 0;
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
  .anomalies-header__title {
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
