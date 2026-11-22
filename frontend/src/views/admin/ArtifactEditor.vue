<script setup>
/**
 * 宝物编辑 (ArtifactEditor)
 *
 * 后台宝物管理页面，使用 CrudTable 组件。
 * 字段：name, category(从宝物种类选), rarity_level(SSS/SS/S/A/B/C),
 *      owner(从角色选，可选), origin, description(富文本), effects
 */
import { computed, onMounted } from 'vue'
import CrudTable from '@/components/admin/CrudTable.vue'
import { artifactApi, characterApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()

const extraParams = computed(() => ({ world: worldData.currentWorldSlug }))
const defaultValues = computed(() => ({ world: worldData.currentWorldSlug }))

/* ==================== 表格列配置 ==================== */
const columns = [
  { key: 'id', label: 'ID', width: '70px', sortable: true },
  { key: 'name', label: '宝物名称', sortable: true },
  { key: 'category', label: '种类', width: '120px' },
  { key: 'rarity_level', label: '稀有度', width: '90px' },
  { key: 'owner_name', label: '持有者', width: '140px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

/* ==================== 稀有度选项 ==================== */
const rarityOptions = [
  { value: 'SSS', label: 'SSS · 神话' },
  { value: 'SS', label: 'SS · 传说' },
  { value: 'S', label: 'S · 史诗' },
  { value: 'A', label: 'A · 精良' },
  { value: 'B', label: 'B · 优秀' },
  { value: 'C', label: 'C · 普通' },
]

/* ==================== 宝物种类选项 ==================== */
const categoryOptions = [
  { value: '武器', label: '武器' },
  { value: '防具', label: '防具' },
  { value: '饰品', label: '饰品' },
  { value: '消耗品', label: '消耗品' },
  { value: '材料', label: '材料' },
  { value: '古籍', label: '古籍' },
  { value: '钥匙', label: '钥匙' },
  { value: '特殊', label: '特殊' },
]

/** 稀有度样式映射 */
const rarityStyleMap = {
  SSS: 'rarity-mythic',
  SS: 'rarity-legendary',
  S: 'rarity-epic',
  A: 'rarity-rare',
  B: 'rarity-uncommon',
  C: 'rarity-common',
}

/* ==================== 表单字段 ==================== */
const formFields = [
  {
    key: 'name',
    label: '宝物名称',
    type: 'text',
    required: true,
    placeholder: '请输入宝物名称',
  },
  {
    key: 'category',
    label: '宝物种类',
    type: 'select',
    required: true,
    options: categoryOptions,
    placeholder: '请选择宝物种类',
  },
  {
    key: 'rarity_level',
    label: '稀有度',
    type: 'select',
    required: true,
    options: rarityOptions,
    placeholder: '请选择稀有度等级',
  },
  {
    key: 'owner',
    label: '持有者',
    type: 'select-remote',
    required: false,
    placeholder: '请选择持有者（可选）',
    fetchOptions: async () => {
      const res = await characterApi.list({ world: worldData.currentWorldSlug, page_size: 200 })
      let items = []
      if (Array.isArray(res)) items = res
      else if (res?.results) items = res.results
      else if (res?.data?.results) items = res.data.results
      else if (res?.data && Array.isArray(res.data)) items = res.data
      return items.map((c) => ({ value: c.id, label: c.name }))
    },
  },
  {
    key: 'origin',
    label: '来历',
    type: 'text',
    required: false,
    placeholder: '请输入宝物来历',
    fullWidth: true,
  },
  {
    key: 'effects',
    label: '效果',
    type: 'text',
    required: false,
    placeholder: '请输入宝物效果（多个用逗号分隔）',
    fullWidth: true,
  },
  {
    key: 'description',
    label: '宝物描述',
    type: 'rich',
    required: false,
    placeholder: '请输入宝物描述',
    fullWidth: true,
  },
]

/* ==================== CRUD 函数 ==================== */
const fetchFn = (params) => artifactApi.list(params)
const createFn = (data) => artifactApi.create(data)
const updateFn = (id, data) => artifactApi.update(id, data)
const deleteFn = (id) => artifactApi.delete(id)

/** 获取稀有度样式 */
function getRarityClass(value) {
  return rarityStyleMap[value] || 'rarity-common'
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
      title="宝物管理"
      search-placeholder="搜索宝物名称..."
    >
      <!-- 稀有度列自定义渲染 -->
      <template #cell-rarity_level="{ value }">
        <span class="rarity-badge" :class="getRarityClass(value)">{{ value || '-' }}</span>
      </template>

      <!-- 持有者列（兼容对象） -->
      <template #cell-owner_name="{ row }">
        {{ row.owner_name || (row.owner && typeof row.owner === 'object' ? row.owner.name : row.owner) || '无主' }}
      </template>
    </CrudTable>
  </div>
</template>

<style scoped>
.admin-page {
  animation: fadeIn 0.3s ease-out;
}

/* 稀有度徽章 */
.rarity-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: 700;
  font-family: var(--font-family-display);
}

.rarity-mythic {
  background: rgba(255, 71, 87, 0.15);
  border: 1px solid var(--rarity-mythic);
  color: var(--rarity-mythic);
  text-shadow: 0 0 4px rgba(255, 71, 87, 0.4);
}

.rarity-legendary {
  background: rgba(255, 140, 0, 0.15);
  border: 1px solid var(--rarity-legendary);
  color: var(--rarity-legendary);
  text-shadow: 0 0 4px rgba(255, 140, 0, 0.4);
}

.rarity-epic {
  background: rgba(155, 89, 182, 0.15);
  border: 1px solid var(--rarity-epic);
  color: var(--rarity-epic);
}

.rarity-rare {
  background: rgba(74, 127, 187, 0.15);
  border: 1px solid var(--rarity-rare);
  color: var(--rarity-rare);
}

.rarity-uncommon {
  background: rgba(80, 200, 120, 0.15);
  border: 1px solid var(--rarity-uncommon);
  color: var(--rarity-uncommon);
}

.rarity-common {
  background: rgba(139, 157, 195, 0.15);
  border: 1px solid var(--rarity-common);
  color: var(--rarity-common);
}
</style>
