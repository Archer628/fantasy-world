<script setup>
/**
 * 关系图谱 (RelationGraph) - 原神风格增强版
 *
 * 使用 SVG 绘制角色/族群之间的关系网络图
 * 节点代表实体，连线代表关系
 *
 * Props:
 *   - nodes: 节点数组 [{ id, name, type, x, y }]
 *   - edges: 关系连线数组 [{ source, target, label, type }]
 *   - title: 图谱标题
 */
import { ref, onMounted, watch, nextTick } from 'vue'
import { useAnimations } from '@/composables/useAnimations'

const props = defineProps({
  nodes: {
    type: Array,
    default: () => [],
  },
  edges: {
    type: Array,
    default: () => [],
  },
  title: { type: String, default: '关系网络' },
})

const { fadeIn, staggerList } = useAnimations()
const svgRef = ref(null)

/** 关系类型配置 - 颜色和标签 */
const edgeConfig = {
  ally: { color: '#00D4AA', label: '盟友' },
  enemy: { color: '#FF4757', label: '敌对' },
  contract: { color: '#D4A853', label: '契约' },
  family: { color: '#50C878', label: '亲属' },
  master: { color: '#9B59B6', label: '师徒' },
  subordinate: { color: '#4A7FBB', label: '从属' },
}

/** 节点类型颜色 */
const nodeColors = {
  character: '#00D4AA',
  faction: '#D4A853',
  artifact: '#FF8C00',
  creature: '#50C878',
  'fragment-world': '#9B59B6',
}

/** 根据 source/target id 查找节点 */
function getNodeById(id) {
  return props.nodes.find((n) => n.id === id)
}

/** 获取边配置 */
function getEdgeConfig(type) {
  return edgeConfig[type] || { color: '#9BA3B0', label: type || '关联' }
}

onMounted(() => {
  if (svgRef.value) {
    fadeIn(svgRef.value, { duration: 0.6 })
  }
})

watch(() => props.nodes, () => {
  nextTick(() => {
    if (svgRef.value) {
      const nodes = svgRef.value.querySelectorAll('.relation-graph__node')
      staggerList(nodes, { stagger: 0.1 })
    }
  })
})
</script>

<template>
  <div class="relation-graph">
    <h3 v-if="title" class="section-title">{{ title }}</h3>

    <div class="relation-graph__container glass-panel">
      <svg
        ref="svgRef"
        class="relation-graph__svg"
        viewBox="0 0 600 400"
        preserveAspectRatio="xMidYMid meet"
      >
        <!-- 定义箭头标记和滤镜 -->
        <defs>
          <marker
            v-for="(config, type) in edgeConfig"
            :key="type"
            :id="`arrowhead-${type}`"
            markerWidth="10"
            markerHeight="7"
            refX="10"
            refY="3.5"
            orient="auto"
          >
            <polygon points="0 0, 10 3.5, 0 7" :fill="config.color" />
          </marker>
          <filter id="node-glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        <!-- 绘制连线 -->
        <g class="relation-graph__edges">
          <g
            v-for="(edge, index) in edges"
            :key="`edge-${index}`"
            class="relation-graph__edge"
          >
            <line
              :x1="getNodeById(edge.source)?.x || 0"
              :y1="getNodeById(edge.source)?.y || 0"
              :x2="getNodeById(edge.target)?.x || 0"
              :y2="getNodeById(edge.target)?.y || 0"
              :stroke="getEdgeConfig(edge.type).color"
              stroke-width="2"
              stroke-dasharray="5,5"
              :marker-end="`url(#arrowhead-${edge.type})`"
              class="edge-line"
              opacity="0.7"
            />
            <!-- 关系标签背景 -->
            <rect
              :x="((getNodeById(edge.source)?.x || 0) + (getNodeById(edge.target)?.x || 0)) / 2 - 20"
              :y="((getNodeById(edge.source)?.y || 0) + (getNodeById(edge.target)?.y || 0)) / 2 - 14"
              width="40"
              height="16"
              rx="3"
              fill="rgba(13, 21, 37, 0.9)"
              :stroke="getEdgeConfig(edge.type).color"
              stroke-width="0.5"
              opacity="0.9"
            />
            <!-- 关系标签 -->
            <text
              :x="((getNodeById(edge.source)?.x || 0) + (getNodeById(edge.target)?.x || 0)) / 2"
              :y="((getNodeById(edge.source)?.y || 0) + (getNodeById(edge.target)?.y || 0)) / 2 - 2"
              text-anchor="middle"
              class="edge-label"
              :fill="getEdgeConfig(edge.type).color"
            >
              {{ edge.label || getEdgeConfig(edge.type).label }}
            </text>
          </g>
        </g>

        <!-- 绘制节点 -->
        <g class="relation-graph__nodes">
          <g
            v-for="node in nodes"
            :key="node.id"
            :transform="`translate(${node.x}, ${node.y})`"
            class="relation-graph__node"
          >
            <!-- 外层光环 -->
            <circle
              r="24"
              :fill="nodeColors[node.type] || '#9BA3B0'"
              fill-opacity="0.1"
              :stroke="nodeColors[node.type] || '#9BA3B0'"
              stroke-width="1"
              opacity="0.5"
              class="node-aura"
            />
            <!-- 主节点圆 -->
            <circle
              r="18"
              :fill="nodeColors[node.type] || '#9BA3B0'"
              fill-opacity="0.3"
              :stroke="nodeColors[node.type] || '#9BA3B0'"
              stroke-width="2"
              filter="url(#node-glow)"
              class="node-circle"
            />
            <!-- 节点名称背景 -->
            <rect
              :x="-30"
              y="24"
              width="60"
              height="18"
              rx="3"
              fill="rgba(13, 21, 37, 0.9)"
              :stroke="nodeColors[node.type] || '#9BA3B0'"
              stroke-width="0.5"
              opacity="0.9"
            />
            <!-- 节点名称 -->
            <text
              y="36"
              text-anchor="middle"
              class="node-label"
              fill="#E8E6E3"
            >
              {{ node.name }}
            </text>
          </g>
        </g>
      </svg>
    </div>

    <!-- 图例 -->
    <div class="relation-graph__legend">
      <div v-for="(config, type) in edgeConfig" :key="type" class="legend-item">
        <span class="legend-dot" :style="{ background: config.color, boxShadow: `0 0 6px ${config.color}` }"></span>
        <span class="legend-text">{{ config.label }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.relation-graph {
  width: 100%;
}

.relation-graph__container {
  padding: var(--spacing-md);
  overflow: hidden;
  position: relative;
}

.relation-graph__svg {
  width: 100%;
  height: 400px;
}

.edge-line {
  transition: all var(--transition-fast);
}

.relation-graph__edge:hover .edge-line {
  stroke-width: 3;
  opacity: 1;
}

.edge-label {
  font-size: 11px;
  font-family: var(--font-family);
  font-weight: 500;
}

.node-circle {
  transition: all var(--transition-fast);
  cursor: pointer;
}

.node-aura {
  transition: all var(--transition-fast);
  animation: elementRing 4s linear infinite;
  transform-origin: center;
}

.relation-graph__node:hover .node-circle {
  fill-opacity: 0.5;
  r: 22;
}

.relation-graph__node:hover .node-aura {
  opacity: 0.8;
  r: 28;
}

.node-label {
  font-size: 12px;
  font-family: var(--font-family);
  pointer-events: none;
  font-weight: 500;
}

.relation-graph__legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  margin-top: var(--spacing-sm);
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-text {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}
</style>
