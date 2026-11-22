<script setup>
/**
 * 境界等级 (Realms) - 原神风格
 *
 * 三级九阶的可视化展示：
 * - 凡境(9阶) → 灵境(9阶) → 神境(3阶) 的进阶路线图
 * - 每个境界用不同颜色的原神风格卡片
 * - 悬停显示详细描述
 */
import { ref, onMounted, nextTick, computed } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import RealmBadge from '@/components/common/RealmBadge.vue'
import LoreLink from '@/components/common/LoreLink.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList, gsap } = useAnimations()

const pageRef = ref(null)
const tiersRef = ref(null)
const expandedRealm = ref(null)

/**
 * 三级九阶境界体系配置
 * 凡境9阶 → 灵境9阶 → 神境3阶，共21阶
 */
const realmTiers = ref([
  {
    name: '凡境',
    type: 'mortal',
    icon: '○',
    color: 'var(--realm-mortal)',
    gradient: 'linear-gradient(135deg, #5A6B8C, #8B9DC3)',
    description: '凡人之躯，尚未踏入修炼之门。通过锤炼体魄、感悟灵气，逐步突破肉体极限，为踏入灵境打下根基。',
    levels: [
      { level: 1, name: '凡人', desc: '未修炼的普通凡人，体能与常人无异' },
      { level: 2, name: '锻体', desc: '初步锤炼体魄，力量与速度略胜常人' },
      { level: 3, name: '通脉', desc: '打通经脉，灵气开始在体内流转' },
      { level: 4, name: '聚气', desc: '凝聚散乱灵气，形成初步灵力' },
      { level: 5, name: '凝元', desc: '灵力凝聚为元力，可短暂外放' },
      { level: 6, name: '化神', desc: '元力转化为神识，可感知周遭' },
      { level: 7, name: '通玄', desc: '触碰玄妙之境，初窥天地法则' },
      { level: 8, name: '破凡', desc: '打破凡躯桎梏，准备踏入灵境' },
      { level: 9, name: '渡凡', desc: '凡境巅峰，渡过凡劫方可入灵' },
    ],
  },
  {
    name: '灵境',
    type: 'spirit',
    icon: '◇',
    color: 'var(--realm-earth)',
    gradient: 'linear-gradient(135deg, #2E8B57, #50C878)',
    description: '脱离凡躯，灵力与肉身融合。修炼者可操控元素之力，飞行于天际，寿命大幅延长。灵境是大多数修炼者终其一生追求的境界。',
    levels: [
      { level: 1, name: '入灵', desc: '正式踏入灵境，灵力充盈全身' },
      { level: 2, name: '灵涌', desc: '灵力如潮涌动，可操控单一元素' },
      { level: 3, name: '灵凝', desc: '灵力凝实，元素操控更加精准' },
      { level: 4, name: '灵变', desc: '灵力千变万化，可操控多种元素' },
      { level: 5, name: '灵翔', desc: '灵力托身，可自由飞行' },
      { level: 6, name: '灵通', desc: '灵觉通明，可感知千里之外' },
      { level: 7, name: '灵域', desc: '形成灵力领域，领域内无敌手' },
      { level: 8, name: '灵极', desc: '灵力达到极致，触及法则之门' },
      { level: 9, name: '渡灵', desc: '灵境巅峰，渡过灵劫方可入神' },
    ],
  },
  {
    name: '神境',
    type: 'divine',
    icon: '✦',
    color: 'var(--realm-divine)',
    gradient: 'linear-gradient(135deg, #B8860B, #FFD700)',
    description: '触摸神之领域，近乎不朽。神境修炼者可操控天地法则，拥有移山填海、改天换地之力。达到神境者已是世间巅峰，万中无一。',
    levels: [
      { level: 1, name: '入神', desc: '正式踏入神境，掌控法则之力' },
      { level: 2, name: '神威', desc: '神威临世，可改天换地' },
      { level: 3, name: '神极', desc: '神境巅峰，近乎不朽不灭' },
    ],
  },
])

/** 总阶数 */
const totalLevels = computed(() => {
  return realmTiers.value.reduce((sum, tier) => sum + tier.levels.length, 0)
})

/** 切换展开的境界 */
function toggleRealm(tierName) {
  expandedRealm.value = expandedRealm.value === tierName ? null : tierName
}

onMounted(async () => {
  await worldData.loadRealms()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (tiersRef.value) {
    const cards = tiersRef.value.querySelectorAll('.realm-tier')
    staggerList(cards, { stagger: 0.15 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content realms-page">
    <!-- 标题区域 -->
    <div class="realms-header">
      <div class="realms-header__deco">💎</div>
      <h1 class="realms-header__title gold-shimmer-text">境界等级</h1>
      <p class="realms-header__subtitle">三级九阶，登天之梯</p>
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
        修炼之路
      </h2>
      <div class="intro-card__content">
        <LoreLink text="残响界的修炼体系分为三级九阶：凡境九阶、灵境九阶、神境三阶，共计二十一个小境界。每突破一个大境界都需要渡过天劫，失败则修为尽毁。修炼之路漫漫，唯有心志坚定者方能登顶。凡境锤炼根基，灵境驾驭灵力，神境掌控法则，层层递进，不可躐等。" tag="p" />
      </div>

      <div class="intro-card__stats">
        <div class="stat-item">
          <span class="stat-item__value">{{ totalLevels }}</span>
          <span class="stat-item__label">总阶数</span>
        </div>
        <div class="stat-item">
          <span class="stat-item__value">3</span>
          <span class="stat-item__label">大境界</span>
        </div>
        <div class="stat-item">
          <span class="stat-item__value">3</span>
          <span class="stat-item__label">天劫数</span>
        </div>
      </div>
    </div>

    <!-- 进阶路线图 -->
    <h2 class="section-title">进阶路线</h2>
    <div class="progression-path">
      <div
        v-for="(tier, index) in realmTiers"
        :key="tier.name"
        class="path-tier"
        :style="{ '--tier-color': tier.color, '--tier-gradient': tier.gradient }"
      >
        <div class="path-tier__icon">{{ tier.icon }}</div>
        <div class="path-tier__name">{{ tier.name }}</div>
        <div class="path-tier__levels">{{ tier.levels.length }}阶</div>
        <div v-if="index < realmTiers.length - 1" class="path-tier__arrow">→</div>
      </div>
    </div>

    <!-- 各境界详情 -->
    <h2 class="section-title">境界详情</h2>
    <div ref="tiersRef" class="realm-tiers">
      <div
        v-for="tier in realmTiers"
        :key="tier.name"
        class="card card-gold realm-tier"
        :style="{ '--tier-color': tier.color, '--tier-gradient': tier.gradient }"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 境界头部 -->
        <div class="realm-tier__header" @click="toggleRealm(tier.name)">
          <div class="realm-tier__icon">{{ tier.icon }}</div>
          <div class="realm-tier__info">
            <h3 class="realm-tier__name">{{ tier.name }}</h3>
            <span class="realm-tier__badge">
              <RealmBadge :realm="tier.type" />
            </span>
          </div>
          <div class="realm-tier__levels-tag">{{ tier.levels.length }}阶</div>
          <span class="realm-tier__expand" :class="{ 'realm-tier__expand--open': expandedRealm === tier.name }">›</span>
        </div>

        <!-- 境界描述 -->
        <div class="realm-tier__desc">
          <LoreLink :text="tier.description" tag="p" />
        </div>

        <!-- 各阶详情（展开时显示） -->
        <transition name="slide">
          <div v-if="expandedRealm === tier.name" class="realm-tier__levels">
            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>
            <div
              v-for="lvl in tier.levels"
              :key="lvl.level"
              class="level-item"
            >
              <div class="level-item__node" :style="{ background: tier.gradient }">
                {{ lvl.level }}
              </div>
              <div class="level-item__content">
                <div class="level-item__header">
                  <span class="level-item__name">{{ lvl.name }}</span>
                  <span class="level-item__stage">{{ tier.name }} · {{ lvl.level }}阶</span>
                </div>
                <p class="level-item__desc">{{ lvl.desc }}</p>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- 天劫说明 -->
    <h2 class="section-title">天劫试炼</h2>
    <div class="card card-gold tribulation-card">
      <span class="ornate-corner ornate-corner--tl"></span>
      <span class="ornate-corner ornate-corner--tr"></span>
      <span class="ornate-corner ornate-corner--bl"></span>
      <span class="ornate-corner ornate-corner--br"></span>

      <div class="tribulation-list">
        <div class="tribulation-item">
          <div class="tribulation-item__icon" style="color: var(--realm-mortal)">⚡</div>
          <div class="tribulation-item__content">
            <h4 class="tribulation-item__name">凡劫</h4>
            <p class="tribulation-item__desc">凡境突破灵境时降临的天劫，以雷劫为主，考验修炼者的根基是否扎实。</p>
          </div>
        </div>
        <div class="tribulation-item">
          <div class="tribulation-item__icon" style="color: var(--realm-earth)">🌩</div>
          <div class="tribulation-item__content">
            <h4 class="tribulation-item__name">灵劫</h4>
            <p class="tribulation-item__desc">灵境突破神境时降临的天劫，包含雷劫、火劫、心劫三重考验，九死一生。</p>
          </div>
        </div>
        <div class="tribulation-item">
          <div class="tribulation-item__icon" style="color: var(--realm-divine)">🌌</div>
          <div class="tribulation-item__content">
            <h4 class="tribulation-item__name">神劫</h4>
            <p class="tribulation-item__desc">神境巅峰试图突破混沌境时的天劫，传说中无人渡过，渡过者将超脱一切。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.realms-page {
  padding-top: var(--spacing-xl);
}

/* 标题 */
.realms-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.realms-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.realms-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.realms-header__subtitle {
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
  margin-bottom: var(--spacing-lg);
}

.intro-card__stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
}

.stat-item {
  text-align: center;
  padding: var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-top: 2px solid var(--color-gold-primary);
}

.stat-item__value {
  display: block;
  font-family: var(--font-family-display);
  font-size: var(--font-size-3xl);
  color: var(--text-gold);
  font-weight: 700;
}

.stat-item__label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 进阶路线图 */
.progression-path {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xl);
  flex-wrap: wrap;
}

.path-tier {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  background: rgba(6, 11, 20, 0.5);
  border: 1px solid var(--tier-color);
  border-radius: var(--border-radius-md);
  min-width: 140px;
  box-shadow: 0 0 12px color-mix(in srgb, var(--tier-color) 30%, transparent);
}

.path-tier__icon {
  font-size: 32px;
  color: var(--tier-color);
  text-shadow: 0 0 12px currentColor;
  margin-bottom: var(--spacing-xs);
}

.path-tier__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-heading);
  margin-bottom: var(--spacing-xs);
}

.path-tier__levels {
  font-size: var(--font-size-sm);
  color: var(--tier-color);
  font-weight: 600;
}

.path-tier__arrow {
  font-size: 28px;
  color: var(--color-gold-primary);
  align-self: center;
  margin: 0 var(--spacing-xs);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

/* 境界详情卡片 */
.realm-tiers {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.realm-tier {
  padding: var(--spacing-xl);
  overflow: hidden;
}

.realm-tier__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  cursor: pointer;
  user-select: none;
}

.realm-tier__icon {
  font-size: 36px;
  color: var(--tier-color);
  text-shadow: 0 0 16px currentColor;
  filter: drop-shadow(0 0 8px var(--tier-color));
}

.realm-tier__info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.realm-tier__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-heading);
}

.realm-tier__levels-tag {
  padding: 2px 12px;
  background: var(--tier-gradient);
  color: #fff;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-xs);
  font-weight: 600;
  letter-spacing: 1px;
}

.realm-tier__expand {
  font-size: 24px;
  color: var(--color-gold-primary);
  transition: transform var(--transition-normal);
}

.realm-tier__expand--open {
  transform: rotate(90deg);
}

.realm-tier__desc {
  margin-top: var(--spacing-md);
  padding-left: 52px;
  color: var(--text-secondary);
  line-height: 1.8;
  font-size: var(--font-size-sm);
}

/* 各阶详情 */
.realm-tier__levels {
  margin-top: var(--spacing-md);
  padding-left: 52px;
}

.level-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--border-color-light);
}

.level-item:last-child {
  border-bottom: none;
}

.level-item__node {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #fff;
  font-family: var(--font-family-display);
  font-weight: 700;
  font-size: var(--font-size-sm);
  box-shadow: 0 0 8px color-mix(in srgb, var(--tier-color) 40%, transparent);
}

.level-item__content {
  flex: 1;
}

.level-item__header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 4px;
}

.level-item__name {
  font-family: var(--font-family-display);
  color: var(--text-gold);
  font-size: var(--font-size-base);
}

.level-item__stage {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.level-item__desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.6;
}

/* 天劫说明 */
.tribulation-card {
  padding: var(--spacing-xl);
}

.tribulation-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.tribulation-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 3px solid var(--color-gold-primary);
}

.tribulation-item__icon {
  font-size: 28px;
  flex-shrink: 0;
}

.tribulation-item__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-gold);
  margin-bottom: var(--spacing-xs);
}

.tribulation-item__desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.6;
}

/* 展开过渡 */
.slide-enter-active,
.slide-leave-active {
  transition: all var(--transition-normal);
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  max-height: 0;
}

.slide-enter-to,
.slide-leave-from {
  opacity: 1;
  max-height: 1000px;
}

@media (max-width: 768px) {
  .realms-header__title {
    font-size: var(--font-size-3xl);
  }

  .intro-card__stats {
    grid-template-columns: 1fr;
  }

  .progression-path {
    flex-direction: column;
  }

  .path-tier__arrow {
    transform: rotate(90deg);
  }

  .realm-tier__desc,
  .realm-tier__levels {
    padding-left: 0;
  }
}
</style>
