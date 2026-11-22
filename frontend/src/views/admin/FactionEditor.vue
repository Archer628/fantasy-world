<script setup>
/**
 * 族群编辑 (FactionEditor)
 *
 * 后台族群管理页面，使用 CrudTable 组件。
 * 字段：name, description(富文本), level(S/E/A/B/C), type(光明/暗网),
 *      parent_faction(从已有族群选), territory, population, leader
 */
import { computed, onMounted } from 'vue'
import CrudTable from '@/components/admin/CrudTable.vue'
import { factionApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()

const extraParams = computed(() => ({ world: worldData.currentWorldSlug }))
const defaultValues = computed(() => ({ world: worldData.currentWorldSlug }))

/* ==================== 表格列配置 ==================== */
const columns = [
  { key: 'id', label: 'ID', width: '70px', sortable: true },
  { key: 'name', label: '族群名称', sortable: true },
  { key: 'level', label: '等级', width: '80px' },
  { key: 'type', label: '类型', width: '100px' },
  { key: 'leader', label: '领袖', width: '140px' },
  { key: 'population', label: '人口', width: '100px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

/* ==================== 等级/类型选项 ==================== */
const levelOptions = [
  { value: 'S', label: 'S 级' },
  { value: 'E', label: 'E 级' },
  { value: 'A', label: 'A 级' },
  { value: 'B', label: 'B 级' },
  { value: 'C', label: 'C 级' },
]

const typeOptions = [
  { value: '光明', label: '光明' },
  { value: '暗网', label: '暗网' },
]

/* ==================== 表单字段 ==================== */
const formFields = [
  {
    key: 'name',
    label: '族群名称',
    type: 'text',
    required: true,
    placeholder: '请输入族群名称',
  },
  {
    key: 'level',
    label: '族群等级',
    type: 'select',
    required: true,
    options: levelOptions,
    placeholder: '请选择族群等级',
  },
  {
    key: 'type',
    label: '族群类型',
    type: 'select',
    required: true,
    options: typeOptions,
    placeholder: '请选择族群类型',
  },
  {
    key: 'parent_faction',
    label: '父族群',
    type: 'select-remote',
    required: false,
    placeholder: '请选择父族群（可选）',
    fetchOptions: async () => {
      const res = await factionApi.list({ world: worldData.currentWorldSlug, page_size: 200 })
      let items = []
      if (Array.isArray(res)) items = res
      else if (res?.results) items = res.results
      else if (res?.data?.results) items = res.data.results
      else if (res?.data && Array.isArray(res.data)) items = res.data
      return items.map((f) => ({ value: f.id, label: f.name }))
    },
  },
  {
    key: 'leader',
    label: '领袖',
    type: 'text',
    required: false,
    placeholder: '请输入领袖名称',
  },
  {
    key: 'population',
    label: '人口数量',
    type: 'number',
    required: false,
    min: 0,
    placeholder: '请输入人口数量',
  },
  {
    key: 'territory',
    label: '领地',
    type: 'text',
    required: false,
    placeholder: '请输入领地范围',
    fullWidth: true,
  },
  {
    key: 'description',
    label: '族群描述',
    type: 'rich',
    required: false,
    placeholder: '请输入族群描述',
    fullWidth: true,
  },
]

/* ==================== CRUD 函数 ==================== */
const fetchFn = (params) => factionApi.list(params)
const createFn = (data) => factionApi.create(data)
const updateFn = (id, data) => factionApi.update(id, data)
const deleteFn = (id) => factionApi.delete(id)

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
      title="族群管理"
      search-placeholder="搜索族群名称..."
    >
      <!-- 等级列自定义渲染 -->
      <template #cell-level="{ value }">
        <span class="level-badge" :class="`level-${value}`">{{ value || '-' }}</span>
      </template>

      <!-- 类型列自定义渲染 -->
      <template #cell-type="{ value }">
        <span class="type-tag" :class="value === '光明' ? 'type-light' : 'type-dark'">
          {{ value || '-' }}
        </span>
      </template>
    </CrudTable>
  </div>
</template>

<style scoped>
.admin-page {
  animation: fadeIn 0.3s ease-out;
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

.level-S,
.level-SSS,
.level-SS {
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid var(--realm-divine);
  color: var(--realm-divine);
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

/* 类型标签 */
.type-tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: var(--font-size-xs);
}

.type-light {
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  color: #FFD700;
}

.type-dark {
  background: rgba(128, 0, 128, 0.1);
  border: 1px solid rgba(128, 0, 128, 0.3);
  color: #b06ab3;
}
</style>
