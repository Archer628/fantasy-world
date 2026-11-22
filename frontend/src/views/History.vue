<script setup>
/**
 * 历史事件 (History) - 原神风格
 *
 * 时间线布局（垂直时间线）
 * - 五大纪元用不同颜色标识
 * - 每个事件卡片展示：名称、时代、时间、描述（使用LoreLink）
 * - 关联势力和角色
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const timelineRef = ref(null)

/** 纪元配置 - 五大纪元用不同颜色 */
const eraConfig = {
  '混沌纪元': { color: '#9B59B6', gradient: 'linear-gradient(135deg, #6B2C91, #9B59B6)', icon: '🌑' },
  '远古纪元': { color: '#FF8C00', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)', icon: '🔥' },
  '上古纪元': { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)', icon: '⚔' },
  '中古纪元': { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)', icon: '📜' },
  '当代': { color: '#FFD700', gradient: 'linear-gradient(135deg, #B8860B, #FFD700)', icon: '✦' },
}

function getEraConfig(era) {
  return eraConfig[era] || { color: 'var(--color-gold-primary)', gradient: 'linear-gradient(135deg, var(--color-gold-dark), var(--color-gold-primary))', icon: '◆' }
}

/** 按纪元分组的事件 */
const groupedEvents = computed(() => {
  const groups = {}
  const events = worldData.historyEvents.length > 0 ? worldData.historyEvents : defaultEvents.value
  events.forEach((event) => {
    const era = event.era || event.epoch || '未知纪元'
    if (!groups[era]) groups[era] = []
    groups[era].push(event)
  })
  return Object.entries(groups).map(([era, events]) => ({
    era,
    config: getEraConfig(era),
    events,
  }))
})

/** 默认历史事件数据（API无数据时使用） */
const defaultEvents = ref([
  { id: 1, era: '混沌纪元', title: '原初之神创世', time: '混沌之初', description: '混沌之力被凝聚为无数碎片，世界由此诞生。原初之神以自身意志塑造天地法则，将混沌划分为有序的世界。', related_factions: [], related_characters: [] },
  { id: 2, era: '混沌纪元', title: '碎片分化', time: '创世之后', description: '原初之神的意志逐渐消散，碎片开始独立演化，各自形成独特的法则体系。十八枚最稳定的碎片成为了日后文明的基础。', related_factions: [], related_characters: [] },
  { id: 3, era: '远古纪元', title: '诸神之战', time: '远古初期', description: '众神为争夺碎片之力爆发战争，世界陷入动荡。神战持续千年，无数世界在战火中毁灭，也有新的世界在废墟中诞生。', related_factions: [], related_characters: [] },
  { id: 4, era: '远古纪元', title: '神之陨落', time: '远古末期', description: '诸神之战以众神陨落告终。陨落之神的神力散布于各碎片世界，成为后世修炼者感悟法则的基础。', related_factions: [], related_characters: [] },
  { id: 5, era: '上古纪元', title: '万族兴起', time: '上古初期', description: '诸神陨落后，各族在废墟上建立文明。人族、妖族、灵族等种族在碎片世界中繁衍生息，开始探索修炼之路。', related_factions: [], related_characters: [] },
  { id: 6, era: '上古纪元', title: '修炼体系建立', time: '上古中期', description: '各族先贤感悟碎片之力，逐步建立起完整的修炼体系。凡境、灵境、神境的划分在这一时期确立。', related_factions: [], related_characters: [] },
  { id: 7, era: '中古纪元', title: '碎片分裂', time: '中古初期', description: '一场未知的灾难导致世界再次碎裂，形成无数碎片世界。原有的文明秩序被打破，各族在新的碎片世界中重新建立势力。', related_factions: [], related_characters: [] },
  { id: 8, era: '中古纪元', title: '族群争霸', time: '中古中期', description: '碎片世界的分裂引发了各族群之间的领土争夺。光明势力与暗网势力在这一时期形成对立格局。', related_factions: [], related_characters: [] },
  { id: 9, era: '当代', title: '旅者降临', time: '当代', description: '来自异界的旅者踏入这片土地，新的故事开始。旅者的到来打破了各碎片世界之间的平衡，历史的齿轮再次转动。', related_factions: [], related_characters: [] },
])

onMounted(async () => {
  await worldData.loadHistory()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (timelineRef.value) {
    const cards = timelineRef.value.querySelectorAll('.history-event')
    staggerList(cards, { stagger: 0.1 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content history-page">
    <!-- 标题区域 -->
    <div class="history-header">
      <div class="history-header__deco">📜</div>
      <h1 class="history-header__title gold-shimmer-text">历史事件</h1>
      <p class="history-header__subtitle">五纪沧桑，万古兴亡</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
    </div>

    <!-- 纪元概览 -->
    <div class="card card-gold era-overview">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <h2 class="era-overview__title">
        <span class="era-overview__deco">◆</span>
        五大纪元
      </h2>
      <div class="era-overview__list">
        <div
          v-for="(group, index) in groupedEvents"
          :key="group.era"
          class="era-overview__item"
          :style="{ '--era-color': group.config.color, '--era-gradient': group.config.gradient }"
        >
          <div class="era-overview__icon">{{ group.config.icon }}</div>
          <div class="era-overview__info">
            <span class="era-overview__name">{{ group.era }}</span>
            <span class="era-overview__count">{{ group.events.length }}个事件</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="worldData.historyLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在翻阅历史典籍...</p>
    </div>

    <!-- 时间线 -->
    <div v-else ref="timelineRef" class="history-timeline">
      <template v-for="group in groupedEvents" :key="group.era">
        <!-- 纪元标题 -->
        <div class="era-header" :style="{ '--era-color': group.config.color, '--era-gradient': group.config.gradient }">
          <div class="era-header__icon">{{ group.config.icon }}</div>
          <h2 class="era-header__name">{{ group.era }}</h2>
          <div class="era-header__line"></div>
        </div>

        <!-- 该纪元的事件 -->
        <div
          v-for="event in group.events"
          :key="event.id"
          class="history-event card card-gold"
          :style="{ '--era-color': group.config.color }"
        >
          <span class="ornate-corner ornate-corner--tl"></span>
          <span class="ornate-corner ornate-corner--tr"></span>
          <span class="ornate-corner ornate-corner--bl"></span>
          <span class="ornate-corner ornate-corner--br"></span>

          <!-- 时间节点 -->
          <div class="history-event__node">
            <span class="history-event__node-dot"></span>
          </div>

          <!-- 事件内容 -->
          <div class="history-event__body">
            <div class="history-event__header">
              <h3 class="history-event__title">{{ event.title || event.name }}</h3>
              <span v-if="event.time || event.date" class="history-event__time">
                {{ event.time || event.date }}
              </span>
            </div>

            <div class="history-event__desc">
              <LoreLink :text="event.description || '暂无描述'" tag="p" />
            </div>

            <!-- 关联势力和角色 -->
            <div v-if="(event.related_factions && event.related_factions.length) || (event.related_characters && event.related_characters.length)" class="history-event__relations">
              <div v-if="event.related_factions && event.related_factions.length" class="relation-group">
                <span class="relation-group__label">关联势力：</span>
                <span
                  v-for="faction in event.related_factions"
                  :key="faction.id || faction"
                  class="relation-tag relation-tag--faction"
                >
                  {{ faction.name || faction }}
                </span>
              </div>
              <div v-if="event.related_characters && event.related_characters.length" class="relation-group">
                <span class="relation-group__label">关联角色：</span>
                <span
                  v-for="character in event.related_characters"
                  :key="character.id || character"
                  class="relation-tag relation-tag--character"
                >
                  {{ character.name || character }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.history-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.history-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.history-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.history-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.history-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
}

/* 纪元概览 */
.era-overview {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.era-overview__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-lg);
}

.era-overview__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.era-overview__list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-md);
}

.era-overview__item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 3px solid var(--era-color);
}

.era-overview__icon {
  font-size: 24px;
  filter: drop-shadow(0 0 8px var(--era-color));
}

.era-overview__info {
  display: flex;
  flex-direction: column;
}

.era-overview__name {
  font-family: var(--font-family-display);
  color: var(--era-color);
  font-size: var(--font-size-base);
  font-weight: 600;
}

.era-overview__count {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

/* 时间线 */
.history-timeline {
  position: relative;
  padding-left: 0;
}

/* 纪元标题 */
.era-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin: var(--spacing-xl) 0 var(--spacing-lg);
}

.era-header__icon {
  font-size: 32px;
  color: var(--era-color);
  filter: drop-shadow(0 0 12px var(--era-color));
}

.era-header__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--era-color);
  text-shadow: 0 0 12px color-mix(in srgb, var(--era-color) 40%, transparent);
  white-space: nowrap;
}

.era-header__line {
  flex: 1;
  height: 2px;
  background: linear-gradient(90deg, var(--era-color), transparent);
}

/* 事件卡片 */
.history-event {
  position: relative;
  margin-left: 32px;
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-lg);
}

/* 时间节点 */
.history-event__node {
  position: absolute;
  left: -32px;
  top: var(--spacing-lg);
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-event__node-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--era-color);
  box-shadow: 0 0 12px var(--era-color);
  position: relative;
  z-index: 2;
}

/* 时间线竖线 */
.history-event__node::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 24px;
  bottom: calc(-1 * var(--spacing-lg) - 2px);
  width: 2px;
  background: linear-gradient(180deg, var(--era-color), color-mix(in srgb, var(--era-color) 20%, transparent));
  transform: translateX(-50%);
}

.history-event:last-child .history-event__node::before {
  display: none;
}

.history-event__body {
  padding-left: var(--spacing-sm);
}

.history-event__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  flex-wrap: wrap;
}

.history-event__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
}

.history-event__time {
  padding: 2px 10px;
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  color: var(--text-gold);
  white-space: nowrap;
}

.history-event__desc {
  color: var(--text-primary);
  line-height: 1.8;
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-sm);
}

/* 关联信息 */
.history-event__relations {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-color-light);
}

.relation-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex-wrap: wrap;
}

.relation-group__label {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.relation-tag {
  padding: 2px 8px;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
}

.relation-tag--faction {
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  color: var(--text-gold);
}

.relation-tag--character {
  background: rgba(74, 127, 187, 0.1);
  border: 1px solid var(--color-cyan-dark);
  color: var(--color-cyan-primary);
}

@media (max-width: 768px) {
  .history-header__title {
    font-size: var(--font-size-3xl);
  }

  .era-overview__list {
    grid-template-columns: 1fr;
  }

  .era-header__name {
    font-size: var(--font-size-xl);
  }

  .history-event {
    margin-left: 24px;
  }

  .history-event__node {
    left: -24px;
  }
}
</style>
