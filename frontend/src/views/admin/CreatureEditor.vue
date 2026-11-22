<script setup>
/**
 * 异兽编辑 (CreatureEditor)
 *
 * 后台异兽管理页面，使用 CrudTable 组件。
 * 字段：name, species, danger_level(1-5), habitat(从碎片世界选),
 *      abilities, description(富文本)
 */
import { computed, onMounted } from 'vue'
import CrudTable from '@/components/admin/CrudTable.vue'
import { creatureApi, fragmentWorldApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()

const extraParams = computed(() => ({ world: worldData.currentWorldSlug }))
const defaultValues = computed(() => ({ world: worldData.currentWorldSlug }))

/* ==================== 表格列配置 ==================== */
const columns = [
  { key: 'id', label: 'ID', width: '70px', sortable: true },
  { key: 'name', label: '异兽名称', sortable: true },
  { key: 'species', label: '物种', width: '140px' },
  { key: 'danger_level', label: '危险度', width: '100px' },
  { key: 'habitat_name', label: '栖息地', width: '160px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

/* ==================== 危险度选项 ==================== */
const dangerOptions = [
  { value: 1, label: '1 级 · 无害' },
  { value: 2, label: '2 级 · 低危' },
  { value: 3, label: '3 级 · 中危' },
  { value: 4, label: '4 级 · 高危' },
  { value: 5, label: '5 级 · 致命' },
]

/** 危险度样式映射 */
const dangerClassMap = {
  1: 'danger-1',
  2: 'danger-2',
  3: 'danger-3',
  4: 'danger-4',
  5: 'danger-5',
}

const dangerLabelMap = {
  1: '1',
  2: '2',
  3: '3',
  4: '4',
  5: '5',
}

/* ==================== 表单字段 ==================== */
const formFields = [
  {
    key: 'name',
    label: '异兽名称',
    type: 'text',
    required: true,
    placeholder: '请输入异兽名称',
  },
  {
    key: 'species',
    label: '物种',
    type: 'text',
    required: true,
    placeholder: '请输入物种分类',
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
    key: 'habitat',
    label: '栖息地',
    type: 'select-remote',
    required: false,
    placeholder: '请选择栖息地（碎片世界）',
    fetchOptions: async () => {
      const res = await fragmentWorldApi.list({ world: worldData.currentWorldSlug, page_size: 200 })
      let items = []
      if (Array.isArray(res)) items = res
      else if (res?.results) items = res.results
      else if (res?.data?.results) items = res.data.results
      else if (res?.data && Array.isArray(res.data)) items = res.data
      return items.map((w) => ({ value: w.id, label: w.name }))
    },
  },
  {
    key: 'abilities',
    label: '能力',
    type: 'text',
    required: false,
    placeholder: '请输入异兽能力（多个用逗号分隔）',
    fullWidth: true,
  },
  {
    key: 'description',
    label: '异兽描述',
    type: 'rich',
    required: false,
    placeholder: '请输入异兽描述',
    fullWidth: true,
  },
]

/* ==================== CRUD 函数 ==================== */
const fetchFn = (params) => creatureApi.list(params)
const createFn = (data) => creatureApi.create(data)
const updateFn = (id, data) => creatureApi.update(id, data)
const deleteFn = (id) => creatureApi.delete(id)

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
      title="异兽管理"
      search-placeholder="搜索异兽名称..."
    >
      <!-- 危险度列自定义渲染 -->
      <template #cell-danger_level="{ value }">
        <span class="danger-badge" :class="getDangerClass(value)">
          <span class="danger-dots">
            <span v-for="n in 5" :key="n" class="dot" :class="{ filled: n <= (value || 0) }"></span>
          </span>
        </span>
      </template>

      <!-- 栖息地列（兼容对象） -->
      <template #cell-habitat_name="{ row }">
        {{ row.habitat_name || (row.habitat && typeof row.habitat === 'object' ? row.habitat.name : row.habitat) || '-' }}
      </template>
    </CrudTable>
  </div>
</template>

<style scoped>
.admin-page {
  animation: fadeIn 0.3s ease-out;
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

.danger-1 .dot.filled { background: var(--color-success); }
.danger-2 .dot.filled { background: var(--color-cyan-primary); }
.danger-3 .dot.filled { background: var(--color-warning); }
.danger-4 .dot.filled { background: var(--rarity-legendary); }
.danger-5 .dot.filled { background: var(--color-danger); }

.danger-1 .dot.filled { box-shadow: 0 0 4px rgba(46, 213, 115, 0.5); }
.danger-2 .dot.filled { box-shadow: 0 0 4px rgba(0, 212, 170, 0.5); }
.danger-3 .dot.filled { box-shadow: 0 0 4px rgba(255, 165, 2, 0.5); }
.danger-4 .dot.filled { box-shadow: 0 0 4px rgba(255, 140, 0, 0.5); }
.danger-5 .dot.filled { box-shadow: 0 0 4px rgba(255, 71, 87, 0.6); }
</style>
