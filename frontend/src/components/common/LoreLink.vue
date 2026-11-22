<script setup>
/**
 * 可点击术语链接组件 (LoreLink) - 核心功能！
 *
 * 接收文本内容，自动将已知术语（角色名、族群名、宝物名等）
 * 转换为可点击链接，点击跳转到对应详情页。
 *
 * 使用 useLoreLinks composable 处理文本分割
 *
 * 使用方式：
 *   <LoreLink :text="character.description" />
 *   <LoreLink>旅者与雷电将军在稻妻相遇</LoreLink>
 *
 * Props:
 *   - text: String - 需要处理的文本内容
 *   - tag: String - 外层包裹标签 (默认 span)
 */
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useLoreLinks } from '@/composables/useLoreLinks'

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  tag: {
    type: String,
    default: 'span',
  },
})

const { processText } = useLoreLinks()

/** 处理后的文本段 */
const segments = computed(() => processText(props.text))
</script>

<template>
  <component :is="tag" class="lore-link-text">
    <template v-for="(segment, index) in segments" :key="index">
      <!-- 普通文本 -->
      <span v-if="segment.type === 'text'" class="lore-link__text">
        {{ segment.content }}
      </span>

      <!-- 术语链接 -->
      <RouterLink
        v-else-if="segment.type === 'link'"
        :to="segment.href"
        class="lore-link__anchor"
        :title="`查看${segment.linkType}: ${segment.content}`"
      >
        {{ segment.content }}
      </RouterLink>
    </template>
  </component>
</template>

<style scoped>
.lore-link-text {
  display: inline;
  line-height: inherit;
}

.lore-link__text {
  color: inherit;
}

.lore-link__anchor {
  color: var(--color-gold-primary);
  text-decoration: none;
  border-bottom: 1px dashed var(--color-gold-dark);
  transition: all var(--transition-fast);
  cursor: pointer;
  position: relative;
  padding: 0 2px;
}

.lore-link__anchor:hover {
  color: var(--color-gold-light);
  border-bottom-color: var(--color-gold-light);
  background: rgba(212, 168, 83, 0.1);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

/* 不同类型的术语链接使用不同的强调色 */
.lore-link__anchor[title*='character'] {
  color: var(--color-cyan-primary);
  border-bottom-color: var(--color-cyan-dark);
}

.lore-link__anchor[title*='character']:hover {
  color: var(--color-cyan-light);
  text-shadow: 0 0 8px var(--color-cyan-glow);
}

.lore-link__anchor[title*='faction'] {
  color: var(--color-gold-primary);
}

.lore-link__anchor[title*='artifact'] {
  color: var(--rarity-legendary);
  border-bottom-color: var(--rarity-legendary);
}

.lore-link__anchor[title*='creature'] {
  color: var(--color-emerald);
  border-bottom-color: var(--color-emerald);
}

.lore-link__anchor[title*='fragment-world'] {
  color: var(--rarity-epic);
  border-bottom-color: var(--rarity-epic);
}
</style>
