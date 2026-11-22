<script setup>
/**
 * 境界徽章 (RealmBadge) - 原神风格增强版
 *
 * 根据境界等级显示对应颜色的徽章
 * 支持三级九阶：凡境、灵境、神境
 *
 * Props:
 *   - realm: 境界名称或等级
 *     支持: 凡境 / 灵境 / 神境 / 混沌境
 *           或 mortal / spirit / divine / chaos
 *   - level: 具体阶数 (1-9)
 */
import { computed } from 'vue'

const props = defineProps({
  realm: { type: String, default: '' },
  level: { type: [Number, String], default: '' },
})

/** 境界配置映射 - 三级九阶 */
const realmConfig = {
  // 凡境 - 灰蓝色
  '凡境': { color: 'var(--realm-mortal)', label: '凡境', icon: '○', gradient: 'linear-gradient(135deg, #5A6B8C, #8B9DC3)' },
  mortal: { color: 'var(--realm-mortal)', label: '凡境', icon: '○', gradient: 'linear-gradient(135deg, #5A6B8C, #8B9DC3)' },
  // 灵境 - 绿色
  '灵境': { color: 'var(--realm-earth)', label: '灵境', icon: '◇', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
  spirit: { color: 'var(--realm-earth)', label: '灵境', icon: '◇', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
  // 神境 - 金色
  '神境': { color: 'var(--realm-divine)', label: '神境', icon: '✦', gradient: 'linear-gradient(135deg, #B8860B, #FFD700)' },
  divine: { color: 'var(--realm-divine)', label: '神境', icon: '✦', gradient: 'linear-gradient(135deg, #B8860B, #FFD700)' },
  // 混沌境 - 红色
  '混沌境': { color: 'var(--realm-chaos)', label: '混沌境', icon: '✧', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
  chaos: { color: 'var(--realm-chaos)', label: '混沌境', icon: '✧', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
}

const config = computed(() => {
  return realmConfig[props.realm] || { color: 'var(--text-secondary)', label: props.realm, icon: '•', gradient: 'linear-gradient(135deg, #4A5568, #718096)' }
})
</script>

<template>
  <span
    v-if="realm"
    class="realm-badge"
    :style="{ '--badge-color': config.color, '--badge-gradient': config.gradient }"
  >
    <span class="realm-badge__icon">{{ config.icon }}</span>
    <span class="realm-badge__label">{{ config.label }}</span>
    <span v-if="level" class="realm-badge__level">{{ level }}阶</span>
  </span>
</template>

<style scoped>
.realm-badge {
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

.realm-badge__icon {
  font-size: 10px;
  opacity: 0.9;
}

.realm-badge__label {
  white-space: nowrap;
}

.realm-badge__level {
  padding-left: 4px;
  border-left: 1px solid rgba(255, 255, 255, 0.4);
  font-size: 10px;
  opacity: 0.9;
}
</style>
