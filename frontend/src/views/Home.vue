<script setup>
/**
 * 首页 (Home) - 原神风格登录页面式首页
 *
 * 全屏英雄区域：
 * - 深蓝星空背景 + 金色粒子
 * - 大标题"残响界"用金色衬线字体，带微光动画
 * - 副标题"世界观设定档案库 V3.0"
 * - 8个核心模块入口卡片，带装饰边框、交错入场动画
 * - 底部展示世界观简介，使用 LoreLink 组件
 */
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAnimations } from '@/composables/useAnimations'
import { useWorldDataStore } from '@/stores/worldData'
import LoreLink from '@/components/common/LoreLink.vue'

const { fadeInUp, staggerList, gsap } = useAnimations()
const worldData = useWorldDataStore()

/** Hero 区域文案：优先使用当前大世界的名称 / 副标题 / 描述 */
const heroTitle = computed(() => worldData.currentWorld?.name || '残响界')
const heroSubtitle = computed(
  () => worldData.currentWorld?.subtitle || '世界观设定档案库 V3.0'
)
const heroDescription = computed(() => worldData.currentWorld?.description || '')

/** 核心模块入口 */
const modules = [
  {
    title: '世界观总览',
    description: '探索这个异世界的整体设定、起源与法则',
    icon: '🌍',
    path: '/world-overview',
    color: 'var(--color-gold-primary)',
  },
  {
    title: '族群势力',
    description: '了解各大族群的势力分布与历史渊源',
    icon: '⚔',
    path: '/factions',
    color: 'var(--color-cyan-primary)',
  },
  {
    title: '英雄角色',
    description: '认识这个世界中那些传奇般的存在',
    icon: '👤',
    path: '/characters',
    color: 'var(--rarity-epic)',
  },
  {
    title: '神兵宝物',
    description: '探寻散落各处的神器与至宝',
    icon: '🗡',
    path: '/artifacts',
    color: 'var(--rarity-legendary)',
  },
  {
    title: '能力体系',
    description: '理解这个世界运转的力量法则',
    icon: '✨',
    path: '/abilities',
    color: 'var(--color-emerald)',
  },
  {
    title: '境界之路',
    description: '从凡人到神境的修炼阶梯',
    icon: '💎',
    path: '/realms',
    color: 'var(--realm-divine)',
  },
  {
    title: '异兽图鉴',
    description: '记录世间各种奇异生灵',
    icon: '🐉',
    path: '/creatures',
    color: 'var(--color-cyan-dark)',
  },
  {
    title: '碎片世界',
    description: '探索那些破碎分离的异世界领域',
    icon: '🌌',
    path: '/fragment-worlds',
    color: 'var(--rarity-rare)',
  },
]

/** 世界观简介文本：优先使用当前大世界的描述 */
const worldIntro = computed(() => worldData.currentWorld?.description || '远古时代，原初之神将混沌之力凝聚为无数碎片，每一枚碎片都演化出一个独立的世界。当碎片之力交汇，便诞生了这个充满奇迹与危险的异世界。诸神陨落，万族林立，在无尽的虚空之中，每一个碎片世界都藏着古老的秘密，每一位英雄都在书写属于自己的传说。')

const heroRef = ref(null)
const cardsRef = ref(null)
const introRef = ref(null)
const particlesRef = ref(null)

/** 生成金色粒子 */
const particles = ref([])
for (let i = 0; i < 20; i++) {
  particles.value.push({
    left: Math.random() * 100 + '%',
    duration: 8 + Math.random() * 12 + 's',
    delay: Math.random() * 8 + 's',
    size: 2 + Math.random() * 4 + 'px',
  })
}

onMounted(() => {
  // 预加载数据以初始化术语词典
  worldData.preloadAll()

  if (heroRef.value) {
    fadeInUp(heroRef.value, { duration: 0.8 })
  }
  if (cardsRef.value) {
    const cards = cardsRef.value.querySelectorAll('.module-card')
    staggerList(cards, { delay: 0.3, stagger: 0.1 })
  }
  if (introRef.value) {
    fadeInUp(introRef.value, { delay: 0.6, duration: 0.8 })
  }

  // 标题微光动画
  if (heroRef.value) {
    const title = heroRef.value.querySelector('.hero__title')
    if (title) {
      gsap.to(title, {
        textShadow: '0 0 30px rgba(212, 168, 83, 0.8), 0 0 60px rgba(212, 168, 83, 0.4)',
        duration: 2,
        repeat: -1,
        yoyo: true,
        ease: 'sine.inOut',
      })
    }
  }
})
</script>

<template>
  <div class="home">
    <!-- 英雄区域 -->
    <section ref="heroRef" class="hero starfield-bg">
      <!-- 金色粒子层 -->
      <div class="particles-container">
        <span
          v-for="(particle, index) in particles"
          :key="index"
          class="particle"
          :style="{
            left: particle.left,
            width: particle.size,
            height: particle.size,
            animationDuration: particle.duration,
            animationDelay: particle.delay,
          }"
        ></span>
      </div>

      <!-- 装饰光晕 -->
      <div class="hero__glow hero__glow--left"></div>
      <div class="hero__glow hero__glow--right"></div>

      <div class="hero__content">
        <!-- 顶部装饰 -->
        <div class="hero__deco-top">
          <span class="deco-line"></span>
          <span class="deco-diamond">◆</span>
          <span class="deco-line"></span>
        </div>

        <h1 class="hero__title gold-shimmer-text">{{ heroTitle }}</h1>
        <p class="hero__subtitle">{{ heroSubtitle }}</p>

        <div class="ornate-divider hero__divider">
          <span class="ornate-divider__diamond"></span>
        </div>

        <p v-if="heroDescription" class="hero__description" v-html="heroDescription"></p>
        <p v-else class="hero__description">
          这是一个由碎片构成的世界，诸神陨落，万族林立。<br />
          在无尽的虚空之中，每一个碎片世界都藏着古老的秘密，<br />
          每一位英雄都在书写属于自己的传说。
        </p>

        <div class="hero__actions">
          <RouterLink to="/world-overview" class="btn-genshin">
            开始探索
          </RouterLink>
          <RouterLink to="/characters" class="btn-genshin btn-genshin--secondary">
            查看角色
          </RouterLink>
        </div>

        <!-- 底部装饰 -->
        <div class="hero__deco-bottom">
          <span class="deco-line"></span>
          <span class="deco-diamond">◆</span>
          <span class="deco-line"></span>
        </div>
      </div>
    </section>

    <!-- 核心模块入口 -->
    <section class="page-content" ref="cardsRef">
      <h2 class="section-title">探索世界</h2>
      <div class="grid-4">
        <div
          v-for="module in modules"
          :key="module.path"
          class="module-card"
        >
          <RouterLink :to="module.path" class="module-link">
            <!-- 四角装饰 -->
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <div class="module-icon" :style="{ color: module.color }">
              {{ module.icon }}
            </div>
            <h3 class="module-title">{{ module.title }}</h3>
            <p class="module-desc">{{ module.description }}</p>
            <div class="module-arrow" :style="{ color: module.color }">›</div>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- 世界观简介 -->
    <section class="page-content" ref="introRef">
      <h2 class="section-title">世界简介</h2>
      <div class="card card-gold intro-card">
        <div class="intro-card__icon">✦</div>
        <LoreLink :text="worldIntro" tag="p" class="intro-card__text" />
        <div class="ornate-divider">
          <span class="ornate-divider__diamond"></span>
        </div>
        <RouterLink to="/world-overview" class="btn-genshin intro-card__btn">
          查看完整世界观
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  min-height: calc(100vh - var(--header-height));
}

/* ==================== 英雄区域 ==================== */
.hero {
  position: relative;
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  padding: var(--spacing-2xl) var(--spacing-xl);
}

.hero__glow {
  position: absolute;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
}

.hero__glow--left {
  top: 20%;
  left: 10%;
  background: radial-gradient(circle, rgba(212, 168, 83, 0.15) 0%, transparent 70%);
}

.hero__glow--right {
  bottom: 20%;
  right: 10%;
  background: radial-gradient(circle, rgba(0, 212, 170, 0.12) 0%, transparent 70%);
}

.hero__content {
  position: relative;
  text-align: center;
  z-index: 2;
  max-width: 700px;
}

/* 顶部底部装饰 */
.hero__deco-top,
.hero__deco-bottom {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  margin: var(--spacing-lg) 0;
}

.deco-line {
  display: block;
  width: 80px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-gold-primary), transparent);
}

.deco-diamond {
  color: var(--color-gold-primary);
  font-size: 10px;
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.hero__title {
  font-family: var(--font-family-display);
  font-size: 5.5rem;
  font-weight: 700;
  letter-spacing: 12px;
  margin-bottom: var(--spacing-sm);
  line-height: 1.2;
}

.hero__subtitle {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-secondary);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-md);
}

.hero__divider {
  max-width: 300px;
  margin: 0 auto var(--spacing-lg);
}

.hero__description {
  font-size: var(--font-size-lg);
  color: var(--text-secondary);
  line-height: 2;
  margin-bottom: var(--spacing-xl);
}

.hero__actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
}

/* ==================== 模块卡片 ==================== */
.module-card {
}

.module-link {
  position: relative;
  display: block;
  height: 100%;
  padding: var(--spacing-xl) var(--spacing-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-normal);
  text-align: center;
  overflow: hidden;
}

.module-link::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, rgba(212, 168, 83, 0.05) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.module-link:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-color-active);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.4);
  transform: translateY(-6px);
}

.module-link:hover::before {
  opacity: 1;
}

.module-icon {
  font-size: 52px;
  margin-bottom: var(--spacing-md);
  filter: drop-shadow(0 0 12px currentColor);
  transition: transform var(--transition-normal);
}

.module-link:hover .module-icon {
  transform: scale(1.15) translateY(-4px);
}

.module-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-heading);
  margin-bottom: var(--spacing-xs);
  transition: color var(--transition-fast);
}

.module-link:hover .module-title {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.module-desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
}

.module-arrow {
  margin-top: var(--spacing-md);
  font-size: var(--font-size-2xl);
  opacity: 0;
  transform: translateX(-10px);
  transition: all var(--transition-normal);
}

.module-link:hover .module-arrow {
  opacity: 1;
  transform: translateX(0);
}

/* ==================== 世界观简介 ==================== */
.intro-card {
  text-align: center;
  padding: var(--spacing-2xl);
}

.intro-card__icon {
  font-size: 48px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 20px var(--color-gold-glow);
  margin-bottom: var(--spacing-lg);
  animation: goldSparkle 3s ease-in-out infinite;
}

.intro-card__text {
  font-size: var(--font-size-lg);
  color: var(--text-primary);
  line-height: 2;
  margin-bottom: var(--spacing-lg);
  text-align: left;
}

.intro-card__btn {
  margin-top: var(--spacing-md);
}

@media (max-width: 768px) {
  .hero__title {
    font-size: 3.5rem;
    letter-spacing: 6px;
  }

  .hero__subtitle {
    font-size: var(--font-size-base);
    letter-spacing: 3px;
  }

  .hero__description {
    font-size: var(--font-size-base);
  }

  .hero__actions {
    flex-direction: column;
  }

  .deco-line {
    width: 40px;
  }
}

@media (max-width: 480px) {
  .hero__title {
    font-size: 2.5rem;
    letter-spacing: 4px;
  }
}
</style>
