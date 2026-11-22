<script setup>
/**
 * 碎片世界详情 (FragmentWorldDetail) - 原神风格
 *
 * 左侧：碎片世界信息（编号、名称、面积、人口、主导法则、危险等级、最大势力、最强战力）
 * 右侧：详细描述和特征（使用 LoreLink）
 * 底部：该世界的异兽列表
 * 顶部有返回按钮
 */
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const route = useRoute()
const worldData = useWorldDataStore()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const world = ref(null)
const loading = ref(true)

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

/** 该世界的异兽列表 */
const worldCreatures = computed(() => {
  if (!world.value) return []
  const worldName = world.value.name
  return worldData.creatures.filter((c) => {
    const habitat = c.habitat || c.world || c.fragment_world || ''
    return habitat.includes(worldName) || (world.value.creatures && world.value.creatures.some((wc) => wc.id === c.id))
  })
})

/** 加载碎片世界详情 */
async function loadWorld(id) {
  loading.value = true
  world.value = null
  try {
    const data = await worldData.loadFragmentWorldDetail(id)
    world.value = data
  } catch (err) {
    console.error('加载碎片世界详情失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

onMounted(() => {
  loadWorld(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadWorld(newId)
})
</script>

<template>
  <div ref="pageRef" class="page-content fragment-world-detail">
    <!-- 返回按钮 -->
    <RouterLink to="/fragment-worlds" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      返回碎片世界
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在探索碎片世界...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!world" class="empty-state">
      <div class="empty-state__icon">🌌</div>
      <p class="empty-state__text">碎片世界不存在</p>
      <RouterLink to="/fragment-worlds" class="btn-genshin">返回列表</RouterLink>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <!-- 左右分栏布局 -->
      <div class="detail-body">
        <!-- 左侧：碎片世界信息 -->
        <aside ref="leftRef" class="detail-left">
          <div
            class="card card-gold info-card"
            :style="{ '--danger-color': getDangerConfig(world.danger_level).color, '--danger-gradient': getDangerConfig(world.danger_level).gradient }"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <!-- 编号 -->
            <div class="info-card__code">
              No.{{ String(world.code || world.number || world.id).padStart(2, '0') }}
            </div>

            <h1 class="info-card__name">{{ world.name }}</h1>

            <!-- 危险等级 -->
            <div class="info-card__danger">
              {{ getDangerConfig(world.danger_level).label }}
            </div>

            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>

            <div class="info-list">
              <div v-if="world.dominant_law || world.law" class="info-item">
                <span class="info-item__label">主导法则</span>
                <span class="info-item__value">{{ world.dominant_law || world.law }}</span>
              </div>
              <div v-if="world.area || world.size" class="info-item">
                <span class="info-item__label">面积</span>
                <span class="info-item__value">{{ world.area || world.size }}</span>
              </div>
              <div v-if="world.population" class="info-item">
                <span class="info-item__label">人口</span>
                <span class="info-item__value">{{ world.population }}</span>
              </div>
              <div v-if="world.danger_level" class="info-item">
                <span class="info-item__label">危险等级</span>
                <span class="info-item__value" :style="{ color: getDangerConfig(world.danger_level).color }">
                  {{ getDangerConfig(world.danger_level).label }}
                </span>
              </div>
              <div v-if="world.max_faction || world.major_faction || world.largest_faction" class="info-item">
                <span class="info-item__label">最大势力</span>
                <span class="info-item__value">{{ world.max_faction || world.major_faction || world.largest_faction }}</span>
              </div>
              <div v-if="world.faction_level" class="info-item">
                <span class="info-item__label">势力等级</span>
                <span class="info-item__value">{{ world.faction_level }}</span>
              </div>
              <div v-if="world.strongest_power || world.strongest_warrior" class="info-item">
                <span class="info-item__label">最强战力</span>
                <span class="info-item__value">{{ world.strongest_power || world.strongest_warrior }}</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- 右侧：详细描述和特征 -->
        <main ref="rightRef" class="detail-right">
          <!-- 世界简介 -->
          <div v-if="world.description" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              世界简介
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="world.description" tag="p" />
            </div>
          </div>

          <!-- 世界法则 -->
          <div v-if="world.laws || world.law_description" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              世界法则
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="world.laws || world.law_description" tag="p" />
            </div>
          </div>

          <!-- 世界特征 -->
          <div v-if="world.features || world.characteristics" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              世界特征
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="world.features || world.characteristics" tag="p" />
            </div>
          </div>

          <!-- 历史背景 -->
          <div v-if="world.history || world.background" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              历史背景
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="world.history || world.background" tag="p" />
            </div>
          </div>
        </main>
      </div>

      <!-- 底部：该世界的异兽列表 -->
      <div v-if="worldCreatures.length > 0" class="world-creatures">
        <h2 class="section-title">本世界异兽</h2>
        <div class="grid-3">
          <RouterLink
            v-for="creature in worldCreatures"
            :key="creature.id"
            :to="`/creatures/${creature.id}`"
            class="creature-mini card card-gold"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h4 class="creature-mini__name">{{ creature.name }}</h4>
            <p class="creature-mini__desc">{{ creature.species || creature.type || '未知物种' }}</p>
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.fragment-world-detail {
  padding-top: var(--spacing-xl);
}

/* 返回按钮 */
.back-btn {
  margin-bottom: var(--spacing-lg);
  align-self: flex-start;
}

.back-btn__arrow {
  font-size: var(--font-size-lg);
}

/* 左右分栏 */
.detail-body {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.detail-left {
  position: sticky;
  top: calc(var(--header-height) + var(--spacing-lg));
  align-self: start;
}

/* 信息卡 */
.info-card {
  padding: var(--spacing-xl);
  text-align: center;
  position: relative;
}

.info-card__code {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--color-gold-dark);
  letter-spacing: 2px;
  margin-bottom: var(--spacing-sm);
}

.info-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
  text-shadow: 0 0 12px var(--color-gold-glow);
}

.info-card__danger {
  display: inline-block;
  padding: 4px 16px;
  background: var(--danger-gradient);
  color: #fff;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  font-weight: 600;
  letter-spacing: 2px;
  margin-bottom: var(--spacing-md);
  box-shadow: 0 0 12px color-mix(in srgb, var(--danger-color) 50%, transparent);
}

.info-list {
  text-align: left;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--border-color-light);
}

.info-item:last-child {
  border-bottom: none;
}

.info-item__label {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  flex-shrink: 0;
}

.info-item__value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  text-align: right;
}

.info-item__link {
  color: var(--color-gold-primary);
  font-size: var(--font-size-sm);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.info-item__link:hover {
  color: var(--color-gold-light);
  text-shadow: 0 0 6px var(--color-gold-glow);
}

/* 右侧描述卡 */
.desc-card {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
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
  border-bottom: 1px solid var(--border-color-light);
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

/* 异兽列表 */
.world-creatures {
  margin-top: var(--spacing-xl);
}

.creature-mini {
  display: block;
  padding: var(--spacing-md);
  text-decoration: none;
  color: inherit;
  text-align: center;
  transition: all var(--transition-normal);
}

.creature-mini:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 20px rgba(212, 168, 83, 0.3);
}

.creature-mini__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  color: var(--text-gold);
  margin-bottom: var(--spacing-xs);
}

.creature-mini__desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

@media (max-width: 968px) {
  .detail-body {
    grid-template-columns: 1fr;
  }

  .detail-left {
    position: static;
  }
}
</style>
