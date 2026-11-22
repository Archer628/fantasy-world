<script setup>
/**
 * 关系网络 (Relations) - 原神风格
 *
 * 展示角色关系
 * - 可以用简单的图谱或列表展示
 * - 每条关系显示：角色A → 关系类型 → 角色B
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import RelationGraph from '@/components/common/RelationGraph.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const listRef = ref(null)
const filterType = ref('')

/** 关系类型配置 */
const relationTypeConfig = {
  ally: { label: '盟友', color: 'var(--color-cyan-primary)', icon: '🤝', desc: '互相信任的合作者' },
  enemy: { label: '敌对', color: 'var(--color-danger)', icon: '⚔', desc: '互相敌视的对立者' },
  contract: { label: '契约', color: 'var(--color-gold-primary)', icon: '📜', desc: '受契约约束的关系' },
  family: { label: '亲缘', color: 'var(--color-emerald)', icon: '👪', desc: '有血缘或家族联系' },
  master: { label: '师徒', color: 'var(--rarity-epic)', icon: '🎓', desc: '传授与继承的关系' },
  subordinate: { label: '从属', color: 'var(--rarity-rare)', icon: '⛓', desc: '主从从属关系' },
}

function getRelationConfig(type) {
  return relationTypeConfig[type] || { label: type || '关联', color: 'var(--text-muted)', icon: '◆', desc: '' }
}

/** 节点数据（用于图谱） */
const graphNodes = computed(() => {
  const graph = worldData.relationGraph
  if (graph.nodes && graph.nodes.length > 0) return graph.nodes
  // 默认节点
  return [
    { id: 1, name: '旅者', type: 'character', x: 300, y: 200 },
    { id: 2, name: '剑圣', type: 'character', x: 150, y: 100 },
    { id: 3, name: '灵巫', type: 'character', x: 450, y: 100 },
    { id: 4, name: '暗影', type: 'character', x: 150, y: 300 },
    { id: 5, name: '圣女', type: 'character', x: 450, y: 300 },
  ]
})

/** 边数据（用于图谱） */
const graphEdges = computed(() => {
  const graph = worldData.relationGraph
  if (graph.edges && graph.edges.length > 0) return graph.edges
  // 默认关系
  return [
    { source: 1, target: 2, label: '盟友', type: 'ally' },
    { source: 1, target: 3, label: '契约', type: 'contract' },
    { source: 1, target: 4, label: '敌对', type: 'enemy' },
    { source: 1, target: 5, label: '盟友', type: 'ally' },
    { source: 2, target: 3, label: '师徒', type: 'master' },
    { source: 4, target: 5, label: '敌对', type: 'enemy' },
  ]
})

/** 关系列表（用于列表展示） */
const relationList = computed(() => {
  const nodes = graphNodes.value
  const edges = graphEdges.value
  return edges.map((edge) => {
    const sourceNode = nodes.find((n) => n.id === edge.source)
    const targetNode = nodes.find((n) => n.id === edge.target)
    return {
      ...edge,
      sourceName: sourceNode ? sourceNode.name : `#${edge.source}`,
      sourceType: sourceNode ? sourceNode.type : 'unknown',
      targetName: targetNode ? targetNode.name : `#${edge.target}`,
      targetType: targetNode ? targetNode.type : 'unknown',
    }
  })
})

/** 筛选后的关系列表 */
const filteredRelations = computed(() => {
  if (!filterType.value) return relationList.value
  return relationList.value.filter((r) => r.type === filterType.value)
})

onMounted(async () => {
  await worldData.loadRelations()
  await worldData.loadRelationGraph()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (listRef.value) {
    const items = listRef.value.querySelectorAll('.relation-item')
    staggerList(items, { stagger: 0.06 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content relations-page">
    <!-- 标题区域 -->
    <div class="relations-header">
      <div class="relations-header__deco">🔗</div>
      <h1 class="relations-header__title gold-shimmer-text">关系网络</h1>
      <p class="relations-header__subtitle">因果交织，命运相连</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 关系图谱 -->
    <h2 class="section-title">关系图谱</h2>
    <div class="card card-gold graph-card">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <RelationGraph
        :nodes="graphNodes"
        :edges="graphEdges"
        title="主要角色关系"
      />
    </div>

    <!-- 关系类型说明 -->
    <h2 class="section-title">关系类型</h2>
    <div class="card card-gold type-guide">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <div class="type-guide__list">
        <div
          v-for="(config, type) in relationTypeConfig"
          :key="type"
          class="type-guide__item"
          :style="{ '--type-color': config.color }"
          :class="{ 'type-guide__item--active': filterType === type }"
          @click="filterType = filterType === type ? '' : type"
        >
          <span class="type-guide__icon">{{ config.icon }}</span>
          <div class="type-guide__info">
            <span class="type-guide__label">{{ config.label }}</span>
            <span class="type-guide__desc">{{ config.desc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 关系列表 -->
    <div class="relations-list-header">
      <h2 class="section-title">关系列表</h2>
      <button
        v-if="filterType"
        class="btn-genshin btn-genshin--secondary filter-clear"
        @click="filterType = ''"
      >
        清除筛选
      </button>
    </div>

    <div v-if="worldData.relationsLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在梳理关系网络...</p>
    </div>

    <div v-else-if="filteredRelations.length === 0" class="empty-state">
      <div class="empty-state__icon">🔗</div>
      <p class="empty-state__text">暂无关系数据</p>
    </div>

    <div v-else ref="listRef" class="relations-list">
      <div
        v-for="(relation, index) in filteredRelations"
        :key="index"
        class="card card-gold relation-item"
        :style="{ '--rel-color': getRelationConfig(relation.type).color }"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <div class="relation-item__body">
          <!-- 角色A -->
          <div class="relation-node relation-node--source">
            <span class="relation-node__icon">{{ relation.sourceType === 'faction' ? '⚔' : '👤' }}</span>
            <span class="relation-node__name">{{ relation.sourceName }}</span>
          </div>

          <!-- 关系类型 -->
          <div class="relation-arrow">
            <span class="relation-arrow__icon">{{ getRelationConfig(relation.type).icon }}</span>
            <span class="relation-arrow__label" :style="{ color: getRelationConfig(relation.type).color }">
              {{ relation.label || getRelationConfig(relation.type).label }}
            </span>
            <span class="relation-arrow__line"></span>
          </div>

          <!-- 角色B -->
          <div class="relation-node relation-node--target">
            <span class="relation-node__icon">{{ relation.targetType === 'faction' ? '⚔' : '👤' }}</span>
            <span class="relation-node__name">{{ relation.targetName }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.relations-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.relations-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.relations-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.relations-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.relations-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
}

/* 图谱卡片 */
.graph-card {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

/* 关系类型说明 */
.type-guide {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.type-guide__list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.type-guide__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 3px solid var(--type-color);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.type-guide__item:hover {
  background: rgba(6, 11, 20, 0.6);
  transform: translateX(4px);
}

.type-guide__item--active {
  background: color-mix(in srgb, var(--type-color) 15%, rgba(6, 11, 20, 0.6));
  box-shadow: 0 0 12px color-mix(in srgb, var(--type-color) 30%, transparent);
}

.type-guide__icon {
  font-size: 24px;
}

.type-guide__info {
  display: flex;
  flex-direction: column;
}

.type-guide__label {
  font-family: var(--font-family-display);
  color: var(--type-color);
  font-size: var(--font-size-base);
  font-weight: 600;
}

.type-guide__desc {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* 关系列表 */
.relations-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.filter-clear {
  padding: 4px 12px;
  font-size: var(--font-size-xs);
}

.relations-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.relation-item {
  padding: var(--spacing-md) var(--spacing-lg);
  transition: all var(--transition-normal);
}

.relation-item:hover {
  border-color: var(--rel-color);
  box-shadow: 0 0 16px color-mix(in srgb, var(--rel-color) 30%, transparent);
}

.relation-item__body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
}

.relation-node {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
  min-width: 0;
}

.relation-node--source {
  justify-content: flex-start;
}

.relation-node--target {
  justify-content: flex-end;
  text-align: right;
}

.relation-node__icon {
  font-size: 20px;
  flex-shrink: 0;
}

.relation-node__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  color: var(--text-gold);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 关系箭头 */
.relation-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  position: relative;
  min-width: 120px;
}

.relation-arrow__icon {
  font-size: 20px;
}

.relation-arrow__label {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  font-weight: 600;
  letter-spacing: 1px;
}

.relation-arrow__line {
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--rel-color), transparent);
  z-index: -1;
  opacity: 0.4;
}

@media (max-width: 768px) {
  .relations-header__title {
    font-size: var(--font-size-3xl);
  }

  .type-guide__list {
    grid-template-columns: 1fr;
  }

  .relation-item__body {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .relation-node--source,
  .relation-node--target {
    justify-content: center;
    text-align: center;
  }

  .relation-arrow__line {
    display: none;
  }
}
</style>
