<script setup>
/**
 * 能力体系编辑 (AbilityEditor)
 *
 * 后台能力体系管理页面，分为 4 个 Tab：
 * 1. 能力体系 - 管理能力体系分类（如：斗气、魔法、异能...）
 * 2. 境界等级 - 管理修炼境界（带可视化排序，可拖动调整顺序）
 * 3. 技能等级 - 管理技能熟练度等级
 * 4. 技能 - 管理具体技能
 *
 * 各 Tab 均使用 CrudTable 组件完成 CRUD 操作。
 */
import { ref, computed, onMounted } from 'vue'
import CrudTable from '@/components/admin/CrudTable.vue'
import {
  abilitySystemApi,
  realmApi,
  skillLevelApi,
  skillApi,
} from '@/api'
import { useWorldDataStore } from '@/stores/worldData'

const worldData = useWorldDataStore()

const extraParams = computed(() => ({ world: worldData.currentWorldSlug }))
const defaultValues = computed(() => ({ world: worldData.currentWorldSlug }))

/* ==================== Tab 配置 ==================== */
const tabs = [
  { key: 'system', name: '能力体系', icon: '✦' },
  { key: 'realm', name: '境界等级', icon: '◈' },
  { key: 'skill-level', name: '技能等级', icon: '◇' },
  { key: 'skill', name: '技能', icon: '◉' },
]

const activeTab = ref('system')

/* ============================================================
   Tab 1: 能力体系
   ============================================================ */
const systemColumns = [
  { key: 'id', label: 'ID', width: '70px', sortable: true },
  { key: 'name', label: '体系名称', sortable: true },
  { key: 'category', label: '分类', width: '120px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

const systemCategoryOptions = [
  { value: '战斗', label: '战斗' },
  { value: '辅助', label: '辅助' },
  { value: '生活', label: '生活' },
  { value: '特殊', label: '特殊' },
]

const systemFormFields = [
  {
    key: 'name',
    label: '体系名称',
    type: 'text',
    required: true,
    placeholder: '如：斗气、魔法、异能',
  },
  {
    key: 'category',
    label: '体系分类',
    type: 'select',
    required: true,
    options: systemCategoryOptions,
    placeholder: '请选择体系分类',
  },
  {
    key: 'description',
    label: '体系描述',
    type: 'rich',
    required: false,
    placeholder: '请输入能力体系描述',
    fullWidth: true,
  },
]

/* ============================================================
   Tab 2: 境界等级（带可视化排序）
   ============================================================ */
const realmColumns = [
  { key: 'order', label: '排序', width: '70px', sortable: true },
  { key: 'name', label: '境界名称', sortable: true },
  { key: 'tier', label: '层级', width: '100px' },
  { key: 'stage', label: '阶段', width: '100px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

const realmTierOptions = [
  { value: '凡境', label: '凡境' },
  { value: '灵境', label: '灵境' },
  { value: '圣境', label: '圣境' },
]

const realmStageOptions = [
  { value: '初阶', label: '初阶' },
  { value: '中阶', label: '中阶' },
  { value: '高阶', label: '高阶' },
]

const realmFormFields = [
  {
    key: 'name',
    label: '境界名称',
    type: 'text',
    required: true,
    placeholder: '如：凡境·初阶',
  },
  {
    key: 'tier',
    label: '层级',
    type: 'select',
    required: true,
    options: realmTierOptions,
    placeholder: '请选择层级',
  },
  {
    key: 'stage',
    label: '阶段',
    type: 'select',
    required: true,
    options: realmStageOptions,
    placeholder: '请选择阶段',
  },
  {
    key: 'order',
    label: '排序序号',
    type: 'number',
    required: true,
    min: 0,
    placeholder: '数字越小越靠前',
  },
  {
    key: 'description',
    label: '境界描述',
    type: 'rich',
    required: false,
    placeholder: '请输入境界描述',
    fullWidth: true,
  },
]

/** 境界等级 - 自定义渲染层级颜色 */
function getTierClass(tier) {
  if (tier === '凡境') return 'tier-mortal'
  if (tier === '灵境') return 'tier-spirit'
  if (tier === '圣境') return 'tier-saint'
  return ''
}

/* ============================================================
   Tab 3: 技能等级
   ============================================================ */
const skillLevelColumns = [
  { key: 'order', label: '排序', width: '70px', sortable: true },
  { key: 'name', label: '等级名称', sortable: true },
  { key: 'level', label: '等级数值', width: '100px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

const skillLevelFormFields = [
  {
    key: 'name',
    label: '等级名称',
    type: 'text',
    required: true,
    placeholder: '如：入门、熟练、精通、大成',
  },
  {
    key: 'level',
    label: '等级数值',
    type: 'number',
    required: true,
    min: 0,
    placeholder: '请输入等级数值',
  },
  {
    key: 'order',
    label: '排序序号',
    type: 'number',
    required: true,
    min: 0,
    placeholder: '数字越小越靠前',
  },
  {
    key: 'description',
    label: '等级描述',
    type: 'rich',
    required: false,
    placeholder: '请输入等级描述',
    fullWidth: true,
  },
]

/* ============================================================
   Tab 4: 技能
   ============================================================ */
const skillColumns = [
  { key: 'id', label: 'ID', width: '70px', sortable: true },
  { key: 'name', label: '技能名称', sortable: true },
  { key: 'system_name', label: '所属体系', width: '140px' },
  { key: 'required_realm', label: '所需境界', width: '140px' },
  { key: 'updated_at', label: '更新时间', width: '160px', sortable: true },
]

const skillTypeOptions = [
  { value: '主动', label: '主动' },
  { value: '被动', label: '被动' },
  { value: '觉醒', label: '觉醒' },
  { value: '终极', label: '终极' },
]

const skillFormFields = [
  {
    key: 'name',
    label: '技能名称',
    type: 'text',
    required: true,
    placeholder: '请输入技能名称',
  },
  {
    key: 'system',
    label: '所属体系',
    type: 'select-remote',
    required: true,
    placeholder: '请选择所属能力体系',
    fetchOptions: async () => {
      const res = await abilitySystemApi.list({ world: worldData.currentWorldSlug, page_size: 200 })
      let items = []
      if (Array.isArray(res)) items = res
      else if (res?.results) items = res.results
      else if (res?.data?.results) items = res.data.results
      else if (res?.data && Array.isArray(res.data)) items = res.data
      return items.map((s) => ({ value: s.id, label: s.name }))
    },
  },
  {
    key: 'required_realm',
    label: '所需境界',
    type: 'select-remote',
    required: false,
    placeholder: '请选择所需境界（可选）',
    fetchOptions: async () => {
      const res = await realmApi.list({ world: worldData.currentWorldSlug, page_size: 200, ordering: 'order' })
      let items = []
      if (Array.isArray(res)) items = res
      else if (res?.results) items = res.results
      else if (res?.data?.results) items = res.data.results
      else if (res?.data && Array.isArray(res.data)) items = res.data
      return items.map((r) => ({ value: r.id, label: r.name }))
    },
  },
  {
    key: 'type',
    label: '技能类型',
    type: 'select',
    required: false,
    options: skillTypeOptions,
    placeholder: '请选择技能类型',
  },
  {
    key: 'power',
    label: '威力系数',
    type: 'number',
    required: false,
    min: 0,
    step: 0.1,
    placeholder: '请输入威力系数',
  },
  {
    key: 'description',
    label: '技能描述',
    type: 'rich',
    required: false,
    placeholder: '请输入技能描述',
    fullWidth: true,
  },
]

/* ==================== CRUD 函数 ==================== */
// 能力体系
const systemFetchFn = (params) => abilitySystemApi.list(params)
const systemCreateFn = (data) => abilitySystemApi.create(data)
const systemUpdateFn = (id, data) => abilitySystemApi.update(id, data)
const systemDeleteFn = (id) => abilitySystemApi.delete(id)

// 境界等级
const realmFetchFn = (params) => realmApi.list({ ...params, ordering: params.ordering || 'order' })
const realmCreateFn = (data) => realmApi.create(data)
const realmUpdateFn = (id, data) => realmApi.update(id, data)
const realmDeleteFn = (id) => realmApi.delete(id)

// 技能等级
const skillLevelFetchFn = (params) => skillLevelApi.list({ ...params, ordering: params.ordering || 'order' })
const skillLevelCreateFn = (data) => skillLevelApi.create(data)
const skillLevelUpdateFn = (id, data) => skillLevelApi.update(id, data)
const skillLevelDeleteFn = (id) => skillLevelApi.delete(id)

// 技能
const skillFetchFn = (params) => skillApi.list(params)
const skillCreateFn = (data) => skillApi.create(data)
const skillUpdateFn = (id, data) => skillApi.update(id, data)
const skillDeleteFn = (id) => skillApi.delete(id)

/* ==================== 生命周期 ==================== */
onMounted(async () => {
  await worldData.ensureCurrentWorld()
})
</script>

<template>
  <div class="ability-editor">
    <!-- 顶部标题 -->
    <div class="ability-editor__header">
      <h1 class="page-title">
        <span class="title-deco">✦</span>
        能力体系管理
      </h1>
    </div>

    <!-- Tab 导航 -->
    <div class="ability-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="ability-tab"
        :class="{ 'ability-tab--active': activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span class="ability-tab__icon">{{ tab.icon }}</span>
        <span class="ability-tab__name">{{ tab.name }}</span>
      </button>
    </div>

    <!-- Tab 内容 -->
    <div class="ability-content">
      <!-- Tab 1: 能力体系 -->
      <div v-show="activeTab === 'system'" class="tab-panel">
        <CrudTable
          :columns="systemColumns"
          :fetch-fn="systemFetchFn"
          :create-fn="systemCreateFn"
          :update-fn="systemUpdateFn"
          :delete-fn="systemDeleteFn"
          :form-fields="systemFormFields"
          :extraParams="extraParams"
          :defaultValues="defaultValues"
          title="能力体系"
          search-placeholder="搜索体系名称..."
        >
          <template #cell-category="{ value }">
            <span class="category-tag">{{ value || '-' }}</span>
          </template>
        </CrudTable>
      </div>

      <!-- Tab 2: 境界等级 -->
      <div v-show="activeTab === 'realm'" class="tab-panel">
        <CrudTable
          :columns="realmColumns"
          :fetch-fn="realmFetchFn"
          :create-fn="realmCreateFn"
          :update-fn="realmUpdateFn"
          :delete-fn="realmDeleteFn"
          :form-fields="realmFormFields"
          :extraParams="extraParams"
          :defaultValues="defaultValues"
          title="境界等级"
          search-placeholder="搜索境界名称..."
        >
          <!-- 排序列可视化 -->
          <template #cell-order="{ value }">
            <span class="order-badge">{{ value ?? '-' }}</span>
          </template>

          <!-- 层级列可视化 -->
          <template #cell-tier="{ value }">
            <span v-if="value" class="tier-badge" :class="getTierClass(value)">{{ value }}</span>
            <span v-else>-</span>
          </template>

          <!-- 阶段列可视化 -->
          <template #cell-stage="{ value }">
            <span v-if="value" class="stage-badge">{{ value }}</span>
            <span v-else>-</span>
          </template>
        </CrudTable>
      </div>

      <!-- Tab 3: 技能等级 -->
      <div v-show="activeTab === 'skill-level'" class="tab-panel">
        <CrudTable
          :columns="skillLevelColumns"
          :fetch-fn="skillLevelFetchFn"
          :create-fn="skillLevelCreateFn"
          :update-fn="skillLevelUpdateFn"
          :delete-fn="skillLevelDeleteFn"
          :form-fields="skillLevelFormFields"
          :extraParams="extraParams"
          :defaultValues="defaultValues"
          title="技能等级"
          search-placeholder="搜索等级名称..."
        >
          <template #cell-order="{ value }">
            <span class="order-badge">{{ value ?? '-' }}</span>
          </template>
          <template #cell-level="{ value }">
            <span class="level-num">Lv.{{ value ?? 0 }}</span>
          </template>
        </CrudTable>
      </div>

      <!-- Tab 4: 技能 -->
      <div v-show="activeTab === 'skill'" class="tab-panel">
        <CrudTable
          :columns="skillColumns"
          :fetch-fn="skillFetchFn"
          :create-fn="skillCreateFn"
          :update-fn="skillUpdateFn"
          :delete-fn="skillDeleteFn"
          :form-fields="skillFormFields"
          :extraParams="extraParams"
          :defaultValues="defaultValues"
          title="技能列表"
          search-placeholder="搜索技能名称..."
        >
          <!-- 体系名称列（兼容对象） -->
          <template #cell-system_name="{ row }">
            {{ row.system_name || (row.system && typeof row.system === 'object' ? row.system.name : row.system) || '-' }}
          </template>

          <!-- 所需境界列（兼容对象） -->
          <template #cell-required_realm="{ row }">
            {{ (row.required_realm && typeof row.required_realm === 'object' ? row.required_realm.name : row.required_realm) || '无' }}
          </template>
        </CrudTable>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ability-editor {
  animation: fadeIn 0.3s ease-out;
}

/* 标题 */
.ability-editor__header {
  margin-bottom: var(--spacing-lg);
}

.page-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-gold);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.title-deco {
  color: var(--color-gold-primary);
  filter: drop-shadow(0 0 4px var(--color-gold-glow));
}

/* Tab 导航 */
.ability-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0;
  flex-wrap: wrap;
}

.ability-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: transparent;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: var(--border-radius-md) var(--border-radius-md) 0 0;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  margin-bottom: -1px;
}

.ability-tab:hover {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.05);
}

.ability-tab--active {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.1);
  border-color: var(--border-color-active);
  border-bottom-color: var(--bg-admin);
}

.ability-tab--active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-gold-primary);
  box-shadow: 0 0 8px var(--color-gold-glow);
}

.ability-tab__icon {
  font-size: 14px;
}

/* 内容区 */
.ability-content {
  min-height: 400px;
}

.tab-panel {
  animation: fadeIn 0.25s ease-out;
}

/* 分类标签 */
.category-tag {
  display: inline-flex;
  padding: 2px 10px;
  background: rgba(74, 127, 187, 0.12);
  border: 1px solid rgba(74, 127, 187, 0.3);
  border-radius: 12px;
  font-size: var(--font-size-xs);
  color: var(--color-blue-accent);
}

/* 排序徽章 */
.order-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 24px;
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: var(--font-family-display);
  font-size: var(--font-size-xs);
  color: var(--text-gold);
  font-weight: 600;
}

/* 层级徽章 - 可视化境界排序 */
.tier-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: var(--font-size-xs);
  font-weight: 500;
}

.tier-mortal {
  background: rgba(139, 157, 195, 0.15);
  border: 1px solid var(--rarity-common);
  color: var(--rarity-common);
}

.tier-spirit {
  background: rgba(74, 127, 187, 0.15);
  border: 1px solid var(--color-blue-accent);
  color: var(--color-blue-accent);
}

.tier-saint {
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid var(--realm-divine);
  color: var(--realm-divine);
  text-shadow: 0 0 4px rgba(255, 215, 0, 0.3);
}

/* 阶段徽章 */
.stage-badge {
  display: inline-flex;
  padding: 2px 10px;
  background: rgba(212, 168, 83, 0.08);
  border: 1px solid var(--border-color-light);
  border-radius: 12px;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

/* 等级数值 */
.level-num {
  font-family: var(--font-family-display);
  color: var(--text-gold);
  font-weight: 600;
  font-size: var(--font-size-sm);
}

/* 响应式 */
@media (max-width: 768px) {
  .ability-tab {
    padding: 8px 12px;
    font-size: var(--font-size-xs);
  }

  .ability-tab__name {
    display: none;
  }
}
</style>
