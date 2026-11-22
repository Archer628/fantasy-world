<script setup>
/**
 * 碎片世界编辑 (FragmentWorldEditor)
 *
 * 后台碎片世界管理页面，使用 CrudTable 组件。
 * 字段：name, number_id(1-18), area, population, dominant_law,
 *      danger_level(1-5), max_faction, faction_level(S/E/A/B/C),
 *      strongest_power, description(富文本), features(富文本)
 */
import { computed, onMounted } from 'vue'
import CrudTable from '@/components/admin/CrudTable.vue'
import { fragmentWorldApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()

const extraParams = computed(() => ({ world: worldData.currentWorldSlug }))
const defaultValues = computed(() => ({ world: worldData.currentWorldSlug }))

/* ==================== 表格列配置 ==================== */
const columns = [
  { key: 'number_id', label: '编号', width: '70px', sortable: true },
  { key: 'name', label: '世界名称', sortable: true },
  { key: 'area', label: '区域', width: '120px' },
  { key: 'faction_level', label: '族群等级', width: '100px' },
  { key: 'danger_level', label: '危险度', width: '100px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

/* ==================== 族群等级选项 ==================== */
const factionLevelOptions = [
  { value: 'S', label: 'S 级 · 顶级' },
  { value: 'E', label: 'E 级 · 强力' },
  { value: 'A', label: 'A 级 · 中坚' },
  { value: 'B', label: 'B 级 · 普通' },
  { value: 'C', label: 'C 级 · 弱小' },
]

/* ==================== 危险度选项 ==================== */
const dangerOptions = [
  { value: 1, label: '1 级 · 安全' },
  { value: 2, label: '2 级 · 轻度' },
  { value: 3, label: '3 级 · 中度' },
  { value: 4, label: '4 级 · 高度' },
  { value: 5, label: '5 级 · 极度' },
]

/** 族群等级样式映射 */
const factionLevelClassMap = {
  S: 'level-S',
  E: 'level-E',
  A: 'level-A',
  B: 'level-B',
  C: 'level-C',
}

/** 危险度样式映射 */
const dangerClassMap = {
  1: 'danger-1',
  2: 'danger-2',
  3: 'danger-3',
  4: 'danger-4',
  5: 'danger-5',
}

/* ==================== 表单字段 ==================== */
const formFields = [
  {
    key: 'name',
    label: '世界名称',
    type: 'text',
    required: true,
    placeholder: '请输入碎片世界名称',
  },
  {
    key: 'number_id',
    label: '世界编号',
    type: 'number',
    required: true,
    min: 1,
    max: 18,
    placeholder: '请输入编号 (1-18)',
  },
  {
    key: 'area',
    label: '区域',
    type: 'text',
    required: false,
    placeholder: '请输入区域范围',
  },
  {
    key: 'population',
    label: '人口',
    type: 'text',
    required: false,
    placeholder: '请输入人口规模',
  },
  {
    key: 'faction_level',
    label: '族群等级',
    type: 'select',
    required: false,
    options: factionLevelOptions,
    placeholder: '请选择族群等级',
  },
  {
    key: 'danger_level',
    label: '危险等级',
    type: 'select',
    required: true,
    options: dangerOptions,
    placeholder: '请选择危险等级',
  },
  {
    key: 'dominant_law',
    label: '主导法则',
    type: 'text',
    required: false,
    placeholder: '请输入主导法则',
    fullWidth: true,
  },
  {
    key: 'max_faction',
    label: '最强族群',
    type: 'text',
    required: false,
    placeholder: '请输入最强族群名称',
    fullWidth: true,
  },
  {
    key: 'strongest_power',
    label: '最强力量',
    type: 'text',
    required: false,
    placeholder: '请输入最强力量描述',
    fullWidth: true,
  },
  {
    key: 'description',
    label: '世界描述',
    type: 'rich',
    required: false,
    placeholder: '请输入世界描述',
    fullWidth: true,
  },
  {
    key: 'features',
    label: '世界特征',
    type: 'rich',
    required: false,
    placeholder: '请输入世界特征',
    fullWidth: true,
  },
]

/* ==================== CRUD 函数 ==================== */
const fetchFn = (params) => fragmentWorldApi.list(params)
const createFn = (data) => fragmentWorldApi.create(data)
const updateFn = (id, data) => fragmentWorldApi.update(id, data)
const deleteFn = (id) => fragmentWorldApi.delete(id)

/** 获取族群等级样式 */
function getFactionLevelClass(value) {
  return factionLevelClassMap[value] || 'level-C'
}

/** 获取危险度样式 */
function getDangerClass(value) {
  return dangerClassMap[value] || 'danger-1'
}

/* ==================== 生命周期 ==================== */
onMounted(async () => {
  await worldData.ensureCurrentWorld()
})
</script>

<template>
  <div class="admin-page">
    <CrudTable
      :columns="columns"
      :fetch-fn="fetchFn"
      :create-fn="createFn"
      :update-fn="updateFn"
      :delete-fn="deleteFn"
      :form-fields="formFields"
      :extraParams="extraParams"
      :defaultValues="defaultValues"
      title="碎片世界管理"
      search-placeholder="搜索世界名称..."
      search-key="name"
    >
      <!-- 编号列自定义渲染 -->
      <template #cell-number_id="{ value }">
        <span class="world-number">No.{{ String(value).padStart(2, '0') }}</span>
      </template>

      <!-- 族群等级列自定义渲染 -->
      <template #cell-faction_level="{ value }">
        <span v-if="value" class="level-badge" :class="getFactionLevelClass(value)">{{ value }}</span>
        <span v-else>-</span>
      </template>

      <!-- 危险度列自定义渲染 -->
      <template #cell-danger_level="{ value }">
        <span class="danger-badge" :class="getDangerClass(value)">
          <span class="danger-dots">
            <span v-for="n in 5" :key="n" class="dot" :class="{ filled: n <= (value || 0) }"></span>
          </span>
        </span>
      </template>
    </CrudTable>
  </div>
</template>

<style scoped>
.admin-page {
  animation: fadeIn 0.3s ease-out;
}

/* 世界编号 */
.world-number {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--text-gold);
  font-weight: 600;
}

/* 等级徽章 */
.level-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 24px;
  padding: 0 8px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 700;
  font-family: var(--font-family-display);
}

.level-S {
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid var(--realm-divine);
  color: var(--realm-divine);
  text-shadow: 0 0 4px rgba(255, 215, 0, 0.4);
}

.level-E,
.level-A {
  background: rgba(212, 168, 83, 0.15);
  border: 1px solid var(--color-gold-primary);
  color: var(--color-gold-primary);
}

.level-B {
  background: rgba(74, 127, 187, 0.15);
  border: 1px solid var(--color-blue-accent);
  color: var(--color-blue-accent);
}

.level-C {
  background: rgba(139, 157, 195, 0.15);
  border: 1px solid var(--rarity-common);
  color: var(--rarity-common);
}

/* 危险度徽章 */
.danger-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 12px;
}

.danger-dots {
  display: inline-flex;
  gap: 3px;
}

.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  transition: all var(--transition-fast);
}

.danger-1 .dot.filled { background: var(--color-success); box-shadow: 0 0 4px rgba(46, 213, 115, 0.5); }
.danger-2 .dot.filled { background: var(--color-cyan-primary); box-shadow: 0 0 4px rgba(0, 212, 170, 0.5); }
.danger-3 .dot.filled { background: var(--color-warning); box-shadow: 0 0 4px rgba(255, 165, 2, 0.5); }
.danger-4 .dot.filled { background: var(--rarity-legendary); box-shadow: 0 0 4px rgba(255, 140, 0, 0.5); }
.danger-5 .dot.filled { background: var(--color-danger); box-shadow: 0 0 4px rgba(255, 71, 87, 0.6); }
</style>
