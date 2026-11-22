<script setup>
/**
 * 法则详情 (OriginLawDetail) - 原神风格
 *
 * 左侧：法则信息卡（名称、层级、核心定义等关键字段）
 * 右侧：详细描述（可用术式方向、过度亲和副作用、补充说明，使用 LoreLink）
 * 顶部有返回按钮
 */
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { originLawApi } from '@/api'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const route = useRoute()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const law = ref(null)
const loading = ref(true)

/** 层级配置 */
const tierLabels = {
  'root': '根源二元层',
  'framework': '时空框架层',
  'evolution': '演化博弈层',
  'narrative': '具象叙事层',
}

const tierColors = {
  'root': { color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
  'framework': { color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)' },
  'evolution': { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)' },
  'narrative': { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
}

function getTierColor(tier) {
  return tierColors[tier] || { color: 'var(--text-muted)', gradient: 'var(--bg-card-hover)' }
}

function tierLabel(tier) {
  return tierLabels[tier] || tier || '未知'
}

/** 将可能为字符串/数组的术式方向格式化为数组展示 */
function formatDirections(val) {
  if (!val) return []
  if (Array.isArray(val)) return val
  return String(val).split(/[,，、;；\n]/).map((s) => s.trim()).filter(Boolean)
}

/** 加载法则详情 */
async function loadLaw(id) {
  loading.value = true
  law.value = null
  try {
    law.value = await originLawApi.detail(id)
  } catch (err) {
    console.error('加载法则详情失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

onMounted(() => {
  loadLaw(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadLaw(newId)
})
</script>

<template>
  <div ref="pageRef" class="page-content law-detail">
    <!-- 返回按钮 -->
    <RouterLink to="/origin-laws" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      返回本源法则
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在解析法则铭文...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!law" class="empty-state">
      <div class="empty-state__icon">✦</div>
      <p class="empty-state__text">法则档案不存在</p>
      <RouterLink to="/origin-laws" class="btn-genshin">返回列表</RouterLink>
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

            <!-- 层级徽章 -->
            <div
              class="info-card__tier"
              :style="{ '--tier-color': getTierColor(law.tier).color, '--tier-gradient': getTierColor(law.tier).gradient }"
            >
              {{ tierLabel(law.tier) }}
            </div>

            <h1 class="info-card__name">{{ law.name }}</h1>

            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>

            <div class="info-list">
              <div v-if="law.tier" class="info-item">
                <span class="info-item__label">所属层级</span>
                <span class="info-item__value">{{ tierLabel(law.tier) }}</span>
              </div>
              <div v-if="law.law_code || law.code" class="info-item">
                <span class="info-item__label">法则编号</span>
                <span class="info-item__value">{{ law.law_code || law.code }}</span>
              </div>
              <div v-if="law.rank || law.order" class="info-item">
                <span class="info-item__label">序号</span>
                <span class="info-item__value">{{ law.rank || law.order }}</span>
              </div>
              <div v-if="law.world_name || law.world" class="info-item">
                <span class="info-item__label">所属世界</span>
                <span class="info-item__value">{{ law.world_name || law.world }}</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- 右侧：详细描述 -->
        <main ref="rightRef" class="detail-right">
          <!-- 核心定义 -->
          <div v-if="law.core_definition" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              核心定义
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="law.core_definition" tag="p" />
            </div>
          </div>

          <!-- 可用术式方向 -->
          <div v-if="formatDirections(law.ability_directions).length" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              可用术式方向
            </h2>
            <div class="desc-card__content desc-card__tags">
              <span
                v-for="(dir, i) in formatDirections(law.ability_directions)"
                :key="i"
                class="desc-tag"
              >
                {{ dir }}
              </span>
            </div>
          </div>

          <!-- 过度亲和副作用 -->
          <div v-if="law.side_effect" class="card card-gold desc-card desc-card--warn">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title desc-card__title--warn">
              <span class="desc-card__deco">⚠</span>
              过度亲和副作用
            </h2>
            <div class="desc-card__content desc-card__content--warn">
              <LoreLink :text="law.side_effect" tag="p" />
            </div>
          </div>

          <!-- 补充说明 -->
          <div v-if="law.description || law.notes || law.manifestation" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              补充说明
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="law.description || law.notes || law.manifestation" tag="p" />
            </div>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped>
.law-detail {
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

.info-card__tier {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-lg);
  margin: 0 auto var(--spacing-md);
  background: var(--tier-gradient);
  color: #fff;
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  font-weight: 600;
  letter-spacing: 1px;
  border-radius: var(--border-radius-md);
  border: 2px solid var(--tier-color);
  box-shadow: 0 0 16px color-mix(in srgb, var(--tier-color) 50%, transparent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
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

/* 术式方向标签 */
.desc-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.desc-tag {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--font-size-sm);
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  border-radius: var(--border-radius-md);
  color: var(--text-gold);
  line-height: 1.6;
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
