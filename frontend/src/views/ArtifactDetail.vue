<script setup>
/**
 * 宝物详情 (ArtifactDetail) - 原神风格
 *
 * 左侧：宝物信息（名称、种类、稀有度、拥有者链接、来源）
 * 右侧：描述和效果（使用 LoreLink）
 */
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'
import RarityBadge from '@/components/common/RarityBadge.vue'

const route = useRoute()
const worldData = useWorldDataStore()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const artifact = ref(null)
const loading = ref(true)

/** 稀有度颜色 */
const rarityColors = {
  common: 'var(--rarity-common)',
  uncommon: 'var(--rarity-uncommon)',
  rare: 'var(--rarity-rare)',
  epic: 'var(--rarity-epic)',
  legendary: 'var(--rarity-legendary)',
  mythic: 'var(--rarity-mythic)',
}

function getRarityColor(rarity) {
  return rarityColors[rarity] || 'var(--color-gold-primary)'
}

/** 加载宝物详情 */
async function loadArtifact(id) {
  loading.value = true
  artifact.value = null
  try {
    const data = await worldData.loadArtifactDetail(id)
    artifact.value = data
  } catch (err) {
    console.error('加载宝物详情失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

onMounted(() => {
  loadArtifact(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadArtifact(newId)
})
</script>

<template>
  <div ref="pageRef" class="page-content artifact-detail">
    <!-- 返回按钮 -->
    <RouterLink to="/artifacts" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      返回宝物列表
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在鉴定宝物信息...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!artifact" class="empty-state">
      <div class="empty-state__icon">🗡</div>
      <p class="empty-state__text">宝物档案不存在</p>
      <RouterLink to="/artifacts" class="btn-genshin">返回列表</RouterLink>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <div class="detail-body">
        <!-- 左侧：宝物信息 -->
        <aside ref="leftRef" class="detail-left">
          <div
            class="card card-gold info-card"
            :style="{ '--rarity-color': getRarityColor(artifact.rarity) }"
          >
            <span class="ornate-corner ornate-corner--tl" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>
            <span class="ornate-corner ornate-corner--tr" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>
            <span class="ornate-corner ornate-corner--bl" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>
            <span class="ornate-corner ornate-corner--br" :style="{ borderColor: getRarityColor(artifact.rarity) }"></span>

            <!-- 图标 -->
            <div class="info-card__icon" :style="{ color: getRarityColor(artifact.rarity) }">🗡</div>

            <h1 class="info-card__name">{{ artifact.name }}</h1>

            <div class="info-card__rarity">
              <RarityBadge v-if="artifact.rarity" :rarity="artifact.rarity" />
            </div>

            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>

            <div class="info-list">
              <div v-if="artifact.type || artifact.category" class="info-item">
                <span class="info-item__label">种类</span>
                <span class="info-item__value">{{ artifact.type || artifact.category }}</span>
              </div>
              <div v-if="artifact.owner || artifact.owner_name" class="info-item">
                <span class="info-item__label">拥有者</span>
                <RouterLink
                  v-if="artifact.owner_id"
                  :to="`/characters/${artifact.owner_id}`"
                  class="info-item__link"
                >
                  {{ artifact.owner || artifact.owner_name }}
                </RouterLink>
                <span v-else class="info-item__value">{{ artifact.owner || artifact.owner_name }}</span>
              </div>
              <div v-if="artifact.origin || artifact.source" class="info-item">
                <span class="info-item__label">来源</span>
                <span class="info-item__value">{{ artifact.origin || artifact.source }}</span>
              </div>
              <div v-if="artifact.rarity" class="info-item">
                <span class="info-item__label">稀有度</span>
                <span class="info-item__value" :style="{ color: getRarityColor(artifact.rarity) }">
                  {{ artifact.rarity }}
                </span>
              </div>
            </div>
          </div>
        </aside>

        <!-- 右侧：描述和效果 -->
        <main ref="rightRef" class="detail-right">
          <div v-if="artifact.description" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              宝物简介
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="artifact.description" tag="p" />
            </div>
          </div>

          <div v-if="artifact.origin || artifact.background" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              宝物来历
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="artifact.origin || artifact.background" tag="p" />
            </div>
          </div>

          <div v-if="artifact.effects" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              能力效果
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="artifact.effects" tag="p" />
            </div>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped>
.artifact-detail {
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
}

/* 左侧信息卡 */
.info-card {
  text-align: center;
  padding: var(--spacing-xl);
  position: relative;
  border-color: var(--rarity-color, var(--border-color));
}

.info-card__icon {
  font-size: 56px;
  margin-bottom: var(--spacing-md);
  filter: drop-shadow(0 0 16px currentColor);
  animation: float 3s ease-in-out infinite;
}

.info-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
  letter-spacing: 2px;
}

.info-card__rarity {
  margin-bottom: var(--spacing-sm);
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
  border-left: 2px solid var(--rarity-color, var(--color-gold-dark));
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

.info-item__link {
  color: var(--color-cyan-primary);
  font-size: var(--font-size-sm);
  text-decoration: none;
}

.info-item__link:hover {
  color: var(--color-cyan-light);
  text-shadow: 0 0 8px var(--color-cyan-glow);
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
