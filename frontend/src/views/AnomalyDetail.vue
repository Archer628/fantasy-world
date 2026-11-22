<script setup>
/**
 * 异常物详情 (AnomalyDetail) - 原神风格
 *
 * 左侧：异常物信息卡（名称、危险等级、法则属性、功能类型等关键字段）
 * 右侧：详细描述（外形、能力、副作用、补充说明，使用 LoreLink）
 * 顶部有返回按钮
 */
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { anomalyApi } from '@/api'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const route = useRoute()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const anomaly = ref(null)
const loading = ref(true)

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

function getDangerConfig(level) {
  const key = String(level || '').toUpperCase()
  return dangerConfig[key] || {
    label: level || '?',
    desc: '未知',
    color: 'var(--text-muted)',
    gradient: 'var(--bg-card-hover)',
  }
}

/** 加载异常物详情 */
async function loadAnomaly(id) {
  loading.value = true
  anomaly.value = null
  try {
    anomaly.value = await anomalyApi.detail(id)
  } catch (err) {
    console.error('加载异常物详情失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

onMounted(() => {
  loadAnomaly(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadAnomaly(newId)
})
</script>

<template>
  <div ref="pageRef" class="page-content anomaly-detail">
    <!-- 返回按钮 -->
    <RouterLink to="/anomalies" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      返回异常物图鉴
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在解析异常物档案...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!anomaly" class="empty-state">
      <div class="empty-state__icon">◈</div>
      <p class="empty-state__text">异常物档案不存在</p>
      <RouterLink to="/anomalies" class="btn-genshin">返回列表</RouterLink>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <!-- 左右分栏布局 -->
      <div class="detail-body">
        <!-- 左侧：信息卡 -->
        <aside ref="leftRef" class="detail-left">
          <div class="card card-gold info-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <!-- 危险等级徽章 -->
            <div
              class="info-card__danger"
              :style="{ '--danger-color': getDangerConfig(anomaly.danger_level).color, '--danger-gradient': getDangerConfig(anomaly.danger_level).gradient }"
            >
              <span class="info-card__danger-letter">{{ String(anomaly.danger_level || '?').toUpperCase() }}</span>
              <span class="info-card__danger-desc">{{ getDangerConfig(anomaly.danger_level).desc }}</span>
            </div>

            <h1 class="info-card__name">{{ anomaly.name }}</h1>

            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>

            <div class="info-list">
              <div v-if="anomaly.danger_level" class="info-item">
                <span class="info-item__label">危险等级</span>
                <span class="info-item__value">{{ getDangerConfig(anomaly.danger_level).label }}</span>
              </div>
              <div v-if="anomaly.law_attribute" class="info-item">
                <span class="info-item__label">法则属性</span>
                <span class="info-item__value">{{ anomaly.law_attribute }}</span>
              </div>
              <div v-if="anomaly.function_type" class="info-item">
                <span class="info-item__label">功能类型</span>
                <span class="info-item__value">{{ anomaly.function_type }}</span>
              </div>
              <div v-if="anomaly.item_code || anomaly.code" class="info-item">
                <span class="info-item__label">编号</span>
                <span class="info-item__value">{{ anomaly.item_code || anomaly.code }}</span>
              </div>
              <div v-if="anomaly.world_name || anomaly.world" class="info-item">
                <span class="info-item__label">所属世界</span>
                <span class="info-item__value">{{ anomaly.world_name || anomaly.world }}</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- 右侧：详细描述 -->
        <main ref="rightRef" class="detail-right">
          <!-- 外形 -->
          <div v-if="anomaly.appearance" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              外形特征
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="anomaly.appearance" tag="p" />
            </div>
          </div>

          <!-- 能力 -->
          <div v-if="anomaly.ability" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title desc-card__title--cyan">
              <span class="desc-card__deco">◆</span>
              异常能力
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="anomaly.ability" tag="p" />
            </div>
          </div>

          <!-- 副作用 -->
          <div v-if="anomaly.side_effect" class="card card-gold desc-card desc-card--warn">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title desc-card__title--warn">
              <span class="desc-card__deco">⚠</span>
              副作用
            </h2>
            <div class="desc-card__content desc-card__content--warn">
              <LoreLink :text="anomaly.side_effect" tag="p" />
            </div>
          </div>

          <!-- 补充说明 -->
          <div v-if="anomaly.description || anomaly.notes || anomaly.containment" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              补充说明
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="anomaly.description || anomaly.notes || anomaly.containment" tag="p" />
            </div>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped>
.anomaly-detail {
  padding-top: var(--spacing-lg);
}

/* 返回按钮 */
.back-btn {
  margin-bottom: var(--spacing-lg);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.back-btn__arrow {
  font-size: var(--font-size-lg);
}

/* 左右分栏 */
.detail-body {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

/* 左侧信息卡 */
.info-card {
  text-align: center;
  padding: var(--spacing-xl);
  position: relative;
}

.info-card__danger {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-lg);
  margin: 0 auto var(--spacing-md);
  background: var(--danger-gradient);
  color: #fff;
  border-radius: var(--border-radius-md);
  border: 2px solid var(--danger-color);
  box-shadow: 0 0 20px color-mix(in srgb, var(--danger-color) 50%, transparent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.info-card__danger-letter {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  line-height: 1;
}

.info-card__danger-desc {
  font-size: var(--font-size-sm);
  letter-spacing: 1px;
}

.info-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
  letter-spacing: 2px;
}

.info-list {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-sm);
  border-left: 2px solid var(--color-gold-dark);
}

.info-item__label {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

.info-item__value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

/* 右侧描述 */
.detail-right {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.desc-card {
  padding: var(--spacing-xl);
}

.desc-card__title {
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

.desc-card__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.desc-card__content {
  color: var(--text-primary);
  line-height: 2;
  font-size: var(--font-size-base);
}

/* 能力卡片 - 青色强调 */
.desc-card__title--cyan {
  color: var(--color-cyan-primary);
  border-bottom-color: var(--color-cyan-dark);
}

/* 警告卡片 */
.desc-card--warn {
  border-color: rgba(255, 71, 87, 0.3);
}

.desc-card__title--warn {
  color: var(--color-danger);
  border-bottom-color: rgba(255, 71, 87, 0.3);
}

.desc-card__content--warn {
  color: #FFB3BA;
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
  margin-bottom: var(--spacing-md);
}

.genshin-loader {
  margin: 0 auto var(--spacing-md);
}

/* 响应式 */
@media (max-width: 1024px) {
  .detail-body {
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 768px) {
  .detail-body {
    grid-template-columns: 1fr;
  }
}
</style>
