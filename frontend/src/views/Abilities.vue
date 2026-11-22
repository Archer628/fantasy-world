<script setup>
/**
 * 能力体系 (Abilities) - 原神风格
 *
 * 展示异能体系的总览
 * - 法则共鸣的说明
 * - 觉醒路径的展示
 */
import { ref, onMounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)

/** 能力体系分类 */
const abilityCategories = ref([
  {
    name: '元素之力',
    description: '掌控自然元素的力量体系，包括风、岩、雷、水、火、冰、草七种元素之力。修炼者通过感悟元素本源，将其化为己用，形成各具特色的战斗风格。',
    icon: '🔥',
    color: 'var(--color-danger)',
    abilities: ['风之切割', '岩之护盾', '雷之审判', '水之治愈', '火之爆裂', '冰之冻结', '草之生长'],
  },
  {
    name: '灵魂之力',
    description: '操控灵魂与精神的力量，修炼者可以感知、沟通甚至操控灵魂。高阶灵魂师能够进行灵魂出窍、精神攻击和灵魂共鸣等强大操作。',
    icon: '💭',
    color: 'var(--rarity-epic)',
    abilities: ['灵魂感知', '精神冲击', '灵魂出窍', '心灵感应', '灵魂共鸣'],
  },
  {
    name: '时空之力',
    description: '干涉时间与空间的能力，是最为罕见也最为强大的力量之一。修炼者可以短暂停滞时间、撕裂空间、甚至预见未来的片段。',
    icon: '⏳',
    color: 'var(--color-cyan-primary)',
    abilities: ['空间跳跃', '时间缓滞', '未来预知', '空间切割', '次元通道'],
  },
  {
    name: '生命之力',
    description: '掌控生死的治愈与毁灭之力。修炼者既可以治愈伤痛、恢复生命，也可以抽取生机、造成衰老。这是最受敬畏的力量之一。',
    icon: '🌿',
    color: 'var(--color-emerald)',
    abilities: ['生命恢复', '生机抽取', '衰老诅咒', '万物复苏', '生命链接'],
  },
])

/** 法则共鸣说明 */
const resonanceInfo = ref(
  '当修炼者的境界达到灵境以上后，可以与世界法则产生共鸣，从而借用天地之力。法则共鸣的强度取决于修炼者对碎片之力的感悟深度，共鸣越强，能调动的天地之力越庞大。共鸣分为初阶、中阶、高阶三个层次，高阶共鸣者甚至可以短暂改变局部法则。'
)

/** 觉醒路径 */
const awakeningPaths = ref([
  { stage: '感知期', description: '初步感知碎片之力的存在，体内灵力开始萌发', icon: '○' },
  { stage: '凝聚期', description: '将散乱的灵力凝聚为完整的灵力核心', icon: '◐' },
  { stage: '觉醒期', description: '灵力核心与碎片之力共鸣，正式觉醒异能', icon: '●' },
  { stage: '蜕变期', description: '异能与肉身融合，获得超越凡人的体质', icon: '◆' },
  { stage: '掌控期', description: '完全掌控自身异能，可自由施展', icon: '★' },
])

onMounted(async () => {
  await worldData.loadAbilities()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.ability-card')
    staggerList(cards, { stagger: 0.1 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content abilities-page">
    <!-- 标题区域 -->
    <div class="abilities-header">
      <div class="abilities-header__deco">✨</div>
      <h1 class="abilities-header__title gold-shimmer-text">能力体系</h1>
      <p class="abilities-header__subtitle">碎片之力，万象归一</p>
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
        力量之源
      </h2>
      <div class="intro-card__content">
        <LoreLink text="异世界的力量来源于碎片之力，不同的修炼方式衍生出各异的能力体系。从掌控元素的元素师，到操纵灵魂的通灵者，每种力量都有其独特的修行路径与代价。碎片之力是原初之神残留的意志和能量，修炼者通过感悟碎片之力来提升自身境界。" tag="p" />
      </div>
    </div>

    <!-- 能力分类卡片 -->
    <h2 class="section-title">能力分类</h2>
    <div ref="gridRef" class="grid-2">
      <div
        v-for="category in abilityCategories"
        :key="category.name"
        class="card card-gold ability-card"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <div class="ability-card__header">
          <div class="ability-card__icon" :style="{ color: category.color }">{{ category.icon }}</div>
          <h3 class="ability-card__name">{{ category.name }}</h3>
        </div>

        <div class="ability-card__content">
          <LoreLink :text="category.description" tag="p" />
        </div>

        <div class="ability-card__tags">
          <span
            v-for="ability in category.abilities"
            :key="ability"
            class="ability-tag"
            :style="{ borderColor: category.color, color: category.color }"
          >
            {{ ability }}
          </span>
        </div>
      </div>
    </div>

    <!-- 法则共鸣 -->
    <h2 class="section-title">法则共鸣</h2>
    <div class="card card-gold resonance-card">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <div class="resonance-card__visual">
        <div class="resonance-ring resonance-ring--1"></div>
        <div class="resonance-ring resonance-ring--2"></div>
        <div class="resonance-ring resonance-ring--3"></div>
        <div class="resonance-core">✦</div>
      </div>

      <div class="resonance-card__content">
        <LoreLink :text="resonanceInfo" tag="p" />
      </div>

      <div class="resonance-levels">
        <div class="resonance-level">
          <span class="resonance-level__name">初阶共鸣</span>
          <span class="resonance-level__desc">借用少量天地之力</span>
        </div>
        <div class="resonance-level">
          <span class="resonance-level__name">中阶共鸣</span>
          <span class="resonance-level__desc">调动区域法则之力</span>
        </div>
        <div class="resonance-level">
          <span class="resonance-level__name">高阶共鸣</span>
          <span class="resonance-level__desc">短暂改变局部法则</span>
        </div>
      </div>
    </div>

    <!-- 觉醒路径 -->
    <h2 class="section-title">觉醒路径</h2>
    <div class="awakening-path">
      <div
        v-for="(path, index) in awakeningPaths"
        :key="path.stage"
        class="path-step"
        :class="{ 'path-step--last': index === awakeningPaths.length - 1 }"
      >
        <div class="path-step__node">
          <span class="path-step__icon">{{ path.icon }}</span>
        </div>
        <div class="path-step__content card">
          <h4 class="path-step__name">{{ path.stage }}</h4>
          <p class="path-step__desc">{{ path.description }}</p>
        </div>
        <div v-if="index < awakeningPaths.length - 1" class="path-step__connector"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.abilities-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.abilities-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.abilities-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.abilities-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.abilities-header__subtitle {
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

/* 能力卡片 */
.ability-card {
  padding: var(--spacing-xl);
}

.ability-card__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.ability-card__icon {
  font-size: 40px;
  filter: drop-shadow(0 0 12px currentColor);
}

.ability-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
}

.ability-card__content {
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
}

.ability-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.ability-tag {
  padding: 2px 10px;
  font-size: var(--font-size-xs);
  border: 1px solid;
  border-radius: var(--border-radius-sm);
  background: rgba(13, 21, 37, 0.6);
}

/* 法则共鸣 */
.resonance-card {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
}

.resonance-card__visual {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto var(--spacing-lg);
}

.resonance-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid var(--color-gold-primary);
  opacity: 0.3;
}

.resonance-ring--1 {
  inset: 0;
  animation: elementRing 4s linear infinite;
}

.resonance-ring--2 {
  inset: 15px;
  border-color: var(--color-cyan-primary);
  opacity: 0.4;
  animation: elementRing 3s linear infinite reverse;
}

.resonance-ring--3 {
  inset: 30px;
  border-color: var(--rarity-epic);
  opacity: 0.5;
  animation: elementRing 2s linear infinite;
}

.resonance-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 24px;
  color: var(--color-gold-light);
  text-shadow: 0 0 16px var(--color-gold-glow);
  animation: goldSparkle 2s ease-in-out infinite;
}

.resonance-card__content {
  text-align: center;
  color: var(--text-primary);
  line-height: 2;
  margin-bottom: var(--spacing-lg);
}

.resonance-levels {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.resonance-level {
  text-align: center;
  padding: var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-top: 2px solid var(--color-gold-primary);
}

.resonance-level__name {
  display: block;
  font-family: var(--font-family-display);
  color: var(--text-gold);
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-xs);
}

.resonance-level__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 觉醒路径 */
.awakening-path {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.path-step {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding-left: 60px;
}

.path-step__node {
  position: absolute;
  left: 0;
  top: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 2px solid var(--color-gold-primary);
  border-radius: 50%;
  z-index: 1;
  box-shadow: 0 0 12px var(--color-gold-glow);
}

.path-step__icon {
  color: var(--text-gold);
  font-size: 18px;
}

.path-step__connector {
  position: absolute;
  left: 21px;
  top: 44px;
  bottom: -16px;
  width: 2px;
  background: linear-gradient(180deg, var(--color-gold-primary), transparent);
}

.path-step__content {
  flex: 1;
  padding: var(--spacing-md) var(--spacing-lg);
}

.path-step__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-gold);
  margin-bottom: var(--spacing-xs);
}

.path-step__desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.6;
}

@media (max-width: 768px) {
  .abilities-header__title {
    font-size: var(--font-size-3xl);
  }

  .resonance-levels {
    grid-template-columns: 1fr;
  }
}
</style>
