<script setup>
/**
 * 设定卡片 (LoreCard) - 原神风格增强版
 *
 * 通用卡片组件，带四角金色花纹装饰
 * 支持图片、标题、描述、徽章等
 *
 * Props:
 *   - title: 卡片标题
 *   - description: 卡片描述
 *   - image: 卡片图片URL
 *   - to: 点击跳转路径
 *   - badges: 徽章数组 [{ text, type }]
 *   - rarity: 稀有度 (影响边框颜色)
 *   - realm: 境界
 *   - icon: 自定义图标（替代图片）
 */
import { RouterLink } from 'vue-router'
import RarityBadge from './RarityBadge.vue'
import RealmBadge from './RealmBadge.vue'

const props = defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  image: { type: String, default: '' },
  to: { type: [String, Object], default: null },
  badges: { type: Array, default: () => [] },
  rarity: { type: String, default: '' },
  realm: { type: String, default: '' },
  icon: { type: String, default: '' },
})
</script>

<template>
  <component
    :is="to ? RouterLink : 'div'"
    :to="to"
    class="lore-card card"
    :class="[rarity ? `lore-card--${rarity}` : '']"
  >
    <!-- 四角金色装饰 -->
    <span class="ornate-corner ornate-corner--tl"></span>
    <span class="ornate-corner ornate-corner--tr"></span>
    <span class="ornate-corner ornate-corner--bl"></span>
    <span class="ornate-corner ornate-corner--br"></span>

    <!-- 卡片图片 -->
    <div v-if="image" class="lore-card__image">
      <img :src="image" :alt="title" loading="lazy" />
      <div class="lore-card__image-overlay"></div>
    </div>

    <!-- 卡片图标 (无图片时) -->
    <div v-else-if="icon" class="lore-card__icon-wrap">
      <span class="lore-card__icon">{{ icon }}</span>
    </div>

    <!-- 卡片内容 -->
    <div class="lore-card__content">
      <div class="lore-card__header">
        <h3 class="lore-card__title">{{ title }}</h3>
        <div class="lore-card__badges">
          <RarityBadge v-if="rarity" :rarity="rarity" />
          <RealmBadge v-if="realm" :realm="realm" />
          <span
            v-for="(badge, index) in badges"
            :key="index"
            class="lore-card__badge"
            :class="`badge--${badge.type || 'default'}`"
          >
            {{ badge.text }}
          </span>
        </div>
      </div>

      <p v-if="description" class="lore-card__description">
        {{ description }}
      </p>

      <slot name="footer" />
    </div>
  </component>
</template>

<style scoped>
.lore-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  height: 100%;
  position: relative;
}

.lore-card__image {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
  background: var(--color-blue-dark);
}

.lore-card__image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.lore-card:hover .lore-card__image img {
  transform: scale(1.08);
}

.lore-card__image-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 50%,
    rgba(6, 11, 20, 0.8) 100%
  );
}

/* 图标样式 */
.lore-card__icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  background: linear-gradient(
    180deg,
    rgba(26, 35, 64, 0.6) 0%,
    rgba(13, 21, 37, 0.8) 100%
  );
}

.lore-card__icon {
  font-size: 56px;
  filter: drop-shadow(0 0 12px var(--color-gold-glow));
  transition: transform var(--transition-normal);
}

.lore-card:hover .lore-card__icon {
  transform: scale(1.15);
}

.lore-card__content {
  padding: var(--spacing-md);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.lore-card__header {
  margin-bottom: var(--spacing-sm);
}

.lore-card__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-heading);
  margin-bottom: var(--spacing-xs);
  transition: color var(--transition-fast);
}

.lore-card:hover .lore-card__title {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.lore-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}

.lore-card__description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 稀有度边框颜色 */
.lore-card--common { border-color: var(--rarity-common); }
.lore-card--uncommon { border-color: var(--rarity-uncommon); }
.lore-card--rare { border-color: var(--rarity-rare); }
.lore-card--epic { border-color: var(--rarity-epic); }
.lore-card--legendary { border-color: var(--rarity-legendary); }
.lore-card--mythic { border-color: var(--rarity-mythic); }

.lore-card--legendary .ornate-corner,
.lore-card--mythic .ornate-corner {
  border-color: var(--rarity-legendary);
  animation: goldSparkle 2s ease-in-out infinite;
}

.lore-card__badge {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
  border-radius: var(--border-radius-sm);
  background: var(--bg-card-hover);
  color: var(--text-secondary);
}

.badge--default { color: var(--text-secondary); }
.badge--gold { color: var(--text-gold); background: rgba(212, 168, 83, 0.1); }
.badge--cyan { color: var(--color-cyan-primary); background: rgba(0, 212, 170, 0.1); }
.badge--danger { color: var(--color-danger); background: rgba(255, 71, 87, 0.1); }
.badge--success { color: var(--color-success); background: rgba(46, 213, 115, 0.1); }
</style>
