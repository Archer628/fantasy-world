<script setup>
/**
 * 角色编辑 (CharacterEditor)
 *
 * 后台角色管理页面，使用 CrudTable 组件。
 * 字段：name, aliases(逗号分隔), faction(从族群选),
 *      realm_level(三级九阶), status(active/dead/missing/sealed),
 *      bio(富文本), personality(富文本), appearance_desc(富文本)
 */
import { computed, onMounted } from 'vue'
import CrudTable from '@/components/admin/CrudTable.vue'
import { characterApi, factionApi } from '@/api'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()

const extraParams = computed(() => ({ world: worldData.currentWorldSlug }))
const defaultValues = computed(() => ({ world: worldData.currentWorldSlug }))

/* ==================== 表格列配置 ==================== */
const columns = [
  { key: 'id', label: 'ID', width: '70px', sortable: true },
  { key: 'name', label: '角色名称', sortable: true },
  { key: 'faction_name', label: '所属族群', width: '140px' },
  { key: 'realm_level', label: '境界等级', width: '120px' },
  { key: 'status', label: '状态', width: '90px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

/* ==================== 境界等级选项（三级九阶） ==================== */
const realmLevelOptions = [
  { value: '凡境·初阶', label: '凡境·初阶' },
  { value: '凡境·中阶', label: '凡境·中阶' },
  { value: '凡境·高阶', label: '凡境·高阶' },
  { value: '灵境·初阶', label: '灵境·初阶' },
  { value: '灵境·中阶', label: '灵境·中阶' },
  { value: '灵境·高阶', label: '灵境·高阶' },
  { value: '圣境·初阶', label: '圣境·初阶' },
  { value: '圣境·中阶', label: '圣境·中阶' },
  { value: '圣境·高阶', label: '圣境·高阶' },
]

/* ==================== 状态选项 ==================== */
const statusOptions = [
  { value: 'active', label: '活跃' },
  { value: 'dead', label: '已故' },
  { value: 'missing', label: '失踪' },
  { value: 'sealed', label: '封印' },
]

/** 状态显示映射 */
const statusMap = {
  active: { label: '活跃', class: 'status-active' },
  dead: { label: '已故', class: 'status-dead' },
  missing: { label: '失踪', class: 'status-missing' },
  sealed: { label: '封印', class: 'status-sealed' },
}

/* ==================== 表单字段 ==================== */
const formFields = [
  {
    key: 'name',
    label: '角色名称',
    type: 'text',
    required: true,
    placeholder: '请输入角色名称',
  },
  {
    key: 'aliases',
    label: '别名/称号',
    type: 'text',
    required: false,
    placeholder: '多个别名用逗号分隔',
  },
  {
    key: 'faction',
    label: '所属族群',
    type: 'select-remote',
    required: false,
    placeholder: '请选择所属族群',
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
    key: 'realm_level',
    label: '境界等级',
    type: 'select',
    required: false,
    options: realmLevelOptions,
    placeholder: '请选择境界等级',
  },
  {
    key: 'status',
    label: '角色状态',
    type: 'select',
    required: true,
    options: statusOptions,
    placeholder: '请选择角色状态',
  },
  {
    key: 'bio',
    label: '角色背景',
    type: 'rich',
    required: false,
    placeholder: '请输入角色背景故事',
    fullWidth: true,
  },
  {
    key: 'personality',
    label: '性格特征',
    type: 'rich',
    required: false,
    placeholder: '请输入性格特征描述',
    fullWidth: true,
  },
  {
    key: 'appearance_desc',
    label: '外貌描述',
    type: 'rich',
    required: false,
    placeholder: '请输入外貌描述',
    fullWidth: true,
  },
]

/* ==================== CRUD 函数 ==================== */
const fetchFn = (params) => characterApi.list(params)
const createFn = (data) => characterApi.create(data)
const updateFn = (id, data) => characterApi.update(id, data)
const deleteFn = (id) => characterApi.delete(id)

/** 获取状态信息 */
function getStatusInfo(value) {
  return statusMap[value] || { label: value || '-', class: '' }
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
      title="角色管理"
      search-placeholder="搜索角色名称..."
    >
      <!-- 境界等级列自定义渲染 -->
      <template #cell-realm_level="{ value }">
        <span class="realm-badge">{{ value || '-' }}</span>
      </template>

      <!-- 状态列自定义渲染 -->
      <template #cell-status="{ value }">
        <span class="status-badge" :class="getStatusInfo(value).class">
          {{ getStatusInfo(value).label }}
        </span>
      </template>

      <!-- 族群名称列（兼容 faction_name 和 faction 对象） -->
      <template #cell-faction_name="{ row }">
        {{ row.faction_name || (row.faction && typeof row.faction === 'object' ? row.faction.name : row.faction) || '-' }}
      </template>
    </CrudTable>
  </div>
</template>

<style scoped>
.admin-page {
  animation: fadeIn 0.3s ease-out;
}

/* 境界徽章 */
.realm-badge {
  display: inline-block;
  padding: 2px 10px;
  background: rgba(74, 127, 187, 0.12);
  border: 1px solid rgba(74, 127, 187, 0.3);
  border-radius: 12px;
  font-size: var(--font-size-xs);
  color: var(--color-blue-accent);
  white-space: nowrap;
}

/* 状态徽章 */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.status-active {
  background: rgba(46, 213, 115, 0.12);
  border: 1px solid rgba(46, 213, 115, 0.3);
  color: var(--color-success);
}

.status-dead {
  background: rgba(255, 71, 87, 0.12);
  border: 1px solid rgba(255, 71, 87, 0.3);
  color: var(--color-danger);
}

.status-missing {
  background: rgba(255, 165, 2, 0.12);
  border: 1px solid rgba(255, 165, 2, 0.3);
  color: var(--color-warning);
}

.status-sealed {
  background: rgba(155, 89, 182, 0.12);
  border: 1px solid rgba(155, 89, 182, 0.3);
  color: var(--rarity-epic);
}
</style>
