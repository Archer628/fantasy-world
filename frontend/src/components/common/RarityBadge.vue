<script setup>
/**
 * 稀有度徽章 (RarityBadge) - 原神风格增强版
 *
 * 根据稀有度等级显示对应颜色的徽章
 *
 * Props:
 *   - rarity: 稀有度等级
 *     支持: common / uncommon / rare / epic / legendary / mythic
 *           或对应的中文: 普通 / 优秀 / 稀有 / 史诗 / 传说 / 神话
 */
import { computed } from 'vue'

const props = defineProps({
  rarity: { type: String, default: '' },
})

/** 稀有度配置映射 - 带渐变背景 */
const rarityConfig = {
  common: { color: 'var(--rarity-common)', label: '普通', gradient: 'linear-gradient(135deg, #6B7B9A, #8B9DC3)', stars: 1 },
  uncommon: { color: 'var(--rarity-uncommon)', label: '优秀', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)', stars: 2 },
  rare: { color: 'var(--rarity-rare)', label: '稀有', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)', stars: 3 },
  epic: { color: 'var(--rarity-epic)', label: '史诗', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)', stars: 4 },
  legendary: { color: 'var(--rarity-legendary)', label: '传说', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)', stars: 5 },
  mythic: { color: 'var(--rarity-mythic)', label: '神话', gradient: 'linear-gradient(135deg, #CC2030, #FF4757)', stars: 6 },
  '普通': { color: 'var(--rarity-common)', label: '普通', gradient: 'linear-gradient(135deg, #6B7B9A, #8B9DC3)', stars: 1 },
  '优秀': { color: 'var(--rarity-uncommon)', label: '优秀', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)', stars: 2 },
  '稀有': { color: 'var(--rarity-rare)', label: '稀有', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)', stars: 3 },
  '史诗': { color: 'var(--rarity-epic)', label: '史诗', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)', stars: 4 },
  '传说': { color: 'var(--rarity-legendary)', label: '传说', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)', stars: 5 },
  '神话': { color: 'var(--rarity-mythic)', label: '神话', gradient: 'linear-gradient(135deg, #CC2030, #FF4757)', stars: 6 },
}

const config = computed(() => {
  return rarityConfig[props.rarity] || { color: 'var(--text-secondary)', label: props.rarity, gradient: 'linear-gradient(135deg, #4A5568, #718096)', stars: 0 }
})
</script>

<template>
  <span
    v-if="rarity"
    class="rarity-badge"
    :style="{ '--badge-color': config.color, '--badge-gradient': config.gradient }"
    :class="`rarity-badge--${rarity}`"
  >
    <span class="rarity-badge__dot"></span>
    <span class="rarity-badge__label">{{ config.label }}</span>
  </span>
</template>

<style scoped>
.rarity-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  background: var(--badge-gradient);
  color: #fff;
  border: 1px solid var(--badge-color);
  border-radius: var(--border-radius-sm);
  letter-spacing: 1px;
  box-shadow: 0 0 8px color-mix(in srgb, var(--badge-color) 40%, transparent);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.rarity-badge__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 0 6px #fff;
}

.rarity-badge__label {
  white-space: nowrap;
}

.rarity-badge--legendary,
.rarity-badge--mythic {
  animation: glowPulse 2s ease-in-out infinite;
}

.rarity-badge--legendary {
  box-shadow: 0 0 12px rgba(255, 140, 0, 0.6);
}

.rarity-badge--mythic {
  box-shadow: 0 0 12px rgba(255, 71, 87, 0.6);
}
</style>
