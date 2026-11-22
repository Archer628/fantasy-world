<script setup>
/**
 * 404 页面 (NotFound) - 原神风格
 *
 * "迷失在虚空之中"主题
 * - 深蓝星空背景 + 漂浮的金色粒子
 * - 大号404数字带金色微光
 * - 返回主页按钮
 */
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAnimations } from '@/composables/useAnimations'

const { fadeInUp, gsap } = useAnimations()

const pageRef = ref(null)
const codeRef = ref(null)

/** 生成随机粒子位置 */
const particles = ref([])
for (let i = 0; i < 20; i++) {
  particles.value.push({
    left: Math.random() * 100,
    delay: Math.random() * 5,
    duration: 5 + Math.random() * 10,
    size: 2 + Math.random() * 4,
  })
}

onMounted(() => {
  if (pageRef.value) fadeInUp(pageRef.value, { duration: 0.8 })
  if (codeRef.value) {
    gsap.to(codeRef.value, {
      textShadow: '0 0 40px var(--color-gold-glow), 0 0 80px var(--color-gold-glow)',
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: 'sine.inOut',
    })
  }
})
</script>

<template>
  <div ref="pageRef" class="not-found starfield-bg">
    <!-- 漂浮的金色粒子 -->
    <div class="particles-container">
      <span
        v-for="(p, i) in particles"
        :key="i"
        class="particle"
        :style="{
          left: p.left + '%',
          animationDelay: p.delay + 's',
          animationDuration: p.duration + 's',
          width: p.size + 'px',
          height: p.size + 'px',
        }"
      ></span>
    </div>

    <!-- 装饰性光环 -->
    <div class="void-ring void-ring--1"></div>
    <div class="void-ring void-ring--2"></div>
    <div class="void-ring void-ring--3"></div>

    <!-- 内容 -->
    <div class="not-found__content">
      <!-- 装饰图标 -->
      <div class="not-found__deco">🌌</div>

      <!-- 404 数字 -->
      <h1 ref="codeRef" class="not-found__code gold-shimmer-text">404</h1>

      <!-- 装饰分隔线 -->
      <div class="ornate-divider not-found__divider">
        <span class="ornate-divider__diamond"></span>
      </div>

      <!-- 主标题 -->
      <h2 class="not-found__title glow-text">迷失在虚空之中</h2>

      <!-- 描述文字 -->
      <p class="not-found__message">
        这片区域不在已知的十八碎片世界之中...
      </p>
      <p class="not-found__hint">
        或许它还未被发现，又或许它已消散在虚空之中。<br />
        虚空的潮汐将你带往未知的角落，但归途依然存在。
      </p>

      <!-- 按钮组 -->
      <div class="not-found__actions">
        <RouterLink to="/" class="btn-genshin not-found__btn">
          <span class="not-found__btn-icon">⌂</span>
          返回主页
        </RouterLink>
        <RouterLink to="/fragment-worlds" class="btn-genshin btn-genshin--secondary not-found__btn">
          <span class="not-found__btn-icon">🌌</span>
          探索碎片世界
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  position: relative;
  overflow: hidden;
}

/* 粒子 */
.particles-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 1;
}

.particle {
  position: absolute;
  bottom: -10px;
  background: var(--color-gold-light);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--color-gold-glow);
  animation: particleFloat linear infinite;
  opacity: 0;
}

/* 虚空光环 */
.void-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid var(--color-gold-primary);
  opacity: 0.15;
  pointer-events: none;
  z-index: 0;
}

.void-ring--1 {
  width: 400px;
  height: 400px;
  animation: elementRing 8s linear infinite;
}

.void-ring--2 {
  width: 600px;
  height: 600px;
  border-color: var(--color-cyan-primary);
  opacity: 0.1;
  animation: elementRing 12s linear infinite reverse;
}

.void-ring--3 {
  width: 800px;
  height: 800px;
  border-color: var(--rarity-epic);
  opacity: 0.08;
  animation: elementRing 16s linear infinite;
}

/* 内容 */
.not-found__content {
  text-align: center;
  position: relative;
  z-index: 2;
  max-width: 600px;
}

.not-found__deco {
  font-size: 60px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 24px var(--color-gold-glow);
  margin-bottom: var(--spacing-md);
  animation: float 3s ease-in-out infinite;
}

.not-found__code {
  font-family: var(--font-family-display);
  font-size: 10rem;
  font-weight: 700;
  margin-bottom: var(--spacing-sm);
  line-height: 1;
  text-shadow: 0 0 40px var(--color-gold-glow);
}

.not-found__divider {
  margin: var(--spacing-md) auto;
  max-width: 300px;
}

.not-found__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-3xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-lg);
  letter-spacing: 4px;
}

.not-found__message {
  font-size: var(--font-size-xl);
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: 1.6;
}

.not-found__hint {
  color: var(--text-muted);
  margin-bottom: var(--spacing-2xl);
  line-height: 1.8;
  font-size: var(--font-size-sm);
}

/* 按钮组 */
.not-found__actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

.not-found__btn {
  padding: var(--spacing-sm) var(--spacing-xl);
}

.not-found__btn-icon {
  font-size: var(--font-size-lg);
}

@media (max-width: 768px) {
  .not-found__code {
    font-size: 6rem;
  }

  .not-found__title {
    font-size: var(--font-size-2xl);
  }

  .not-found__message {
    font-size: var(--font-size-lg);
  }

  .not-found__actions {
    flex-direction: column;
    align-items: center;
  }

  .void-ring--1 {
    width: 250px;
    height: 250px;
  }

  .void-ring--2 {
    width: 400px;
    height: 400px;
  }

  .void-ring--3 {
    width: 550px;
    height: 550px;
  }
}
</style>
