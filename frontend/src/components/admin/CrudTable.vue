<script setup>
/**
 * 通用CRUD表格 (CrudTable)
 *
 * 可复用的数据表格组件，集成完整的 CRUD 流程：
 * - 数据展示（表格 + 列配置 + 自定义渲染）
 * - 搜索过滤
 * - 分页
 * - 新增 / 编辑表单弹窗（基于 formFields 配置自动生成）
 * - 删除确认弹窗
 * - 加载状态 / 操作反馈通知
 * - 原神风格样式（深色背景 + 金色装饰）
 *
 * Props:
 *   - columns:      列定义 [{ key, label, width, sortable, render }]
 *   - fetchFn:      获取列表数据的函数 (params) => Promise<{results, count}>
 *   - createFn:     创建数据的函数 (data) => Promise
 *   - updateFn:     更新数据的函数 (id, data) => Promise
 *   - deleteFn:     删除数据的函数 (id) => Promise
 *   - formFields:   表单字段定义 [{ key, label, type, required, options, placeholder, rows }]
 *   - title:        表格标题
 *   - pageSize:     每页条数（默认 10）
 *   - searchKey:    搜索字段（默认 name）
 *   - searchPlaceholder
 *   - extraParams:  附加到 fetchFn 请求中的固定参数（例: { world: 'shenhai' }）
 *   - defaultValues: 新增表单的默认值，会覆盖 formFields 中的 default（例: { world: 'shenhai' }）
 *
 * 自定义渲染：通过具名插槽 cell-<key> 覆盖单元格内容
 */
import { ref, reactive, computed, onMounted, watch } from 'vue'
import RichEditor from './RichEditor.vue'

const props = defineProps({
  columns: { type: Array, default: () => [] },
  fetchFn: { type: Function, required: true },
  createFn: { type: Function, default: null },
  updateFn: { type: Function, default: null },
  deleteFn: { type: Function, default: null },
  formFields: { type: Array, default: () => [] },
  title: { type: String, default: '数据管理' },
  pageSize: { type: Number, default: 10 },
  searchKey: { type: String, default: 'name' },
  searchPlaceholder: { type: String, default: '搜索...' },
  extraParams: { type: Object, default: () => ({}) },
  defaultValues: { type: Object, default: () => ({}) },
})

/* ==================== 数据状态 ==================== */
const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const searchQuery = ref('')
const sortKey = ref('')
const sortOrder = ref('asc')

/* ==================== 弹窗状态 ==================== */
const modalVisible = ref(false)
const modalMode = ref('create') // 'create' | 'edit'
const formData = reactive({})
const formErrors = reactive({})
const saving = ref(false)
/** 当前正在编辑的原始行（用于以 slug 等非 id 字段为标识的资源） */
const editingRow = ref(null)

const confirmVisible = ref(false)
const deleteTarget = ref(null)
const deleting = ref(false)

/* ==================== Toast 通知 ==================== */
const toasts = ref([])
let toastId = 0

function showToast(type, message) {
  const id = ++toastId
  toasts.value.push({ id, type, message })
  setTimeout(() => {
    removeToast(id)
  }, 3000)
}

function removeToast(id) {
  const idx = toasts.value.findIndex((t) => t.id === id)
  if (idx > -1) toasts.value.splice(idx, 1)
}

/* ==================== 计算属性 ==================== */
const totalPages = computed(() => Math.ceil(total.value / props.pageSize) || 1)

const pageNumbers = computed(() => {
  const pages = []
  const max = totalPages.value
  const cur = currentPage.value
  if (max <= 7) {
    for (let i = 1; i <= max; i++) pages.push(i)
  } else {
    pages.push(1)
    if (cur > 3) pages.push('...')
    const start = Math.max(2, cur - 1)
    const end = Math.min(max - 1, cur + 1)
    for (let i = start; i <= end; i++) pages.push(i)
    if (cur < max - 2) pages.push('...')
    pages.push(max)
  }
  return pages
})

const canCreate = computed(() => !!props.createFn)
const canUpdate = computed(() => !!props.updateFn)
const canDelete = computed(() => !!props.deleteFn)
const showActions = computed(() => canUpdate.value || canDelete.value)

/* ==================== 数据加载 ==================== */
async function loadData() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: props.pageSize,
      // 附加固定参数（如 world 过滤）
      ...props.extraParams,
    }
    if (searchQuery.value.trim()) {
      params[props.searchKey] = searchQuery.value.trim()
    }
    if (sortKey.value) {
      params.ordering = sortOrder.value === 'desc' ? `-${sortKey.value}` : sortKey.value
    }
    const res = await props.fetchFn(params)
    // 兼容多种返回结构
    if (Array.isArray(res)) {
      tableData.value = res
      total.value = res.length
    } else if (res.results) {
      tableData.value = res.results
      total.value = res.count ?? res.results.length
    } else if (res.data) {
      if (Array.isArray(res.data)) {
        tableData.value = res.data
        total.value = res.data.length
      } else if (res.data.results) {
        tableData.value = res.data.results
        total.value = res.data.count ?? res.data.results.length
      } else {
        tableData.value = [res.data]
        total.value = 1
      }
    } else {
      tableData.value = []
      total.value = 0
    }
  } catch (err) {
    console.error('加载数据失败:', err)
    showToast('error', '加载数据失败，请稍后重试')
    tableData.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

/* ==================== 搜索 ==================== */
let searchTimer = null
function handleSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadData()
  }, 400)
}

function handleSearch() {
  currentPage.value = 1
  loadData()
}

/* ==================== 排序 ==================== */
function handleSort(column) {
  if (!column.sortable) return
  if (sortKey.value === column.key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = column.key
    sortOrder.value = 'asc'
  }
  loadData()
}

/* ==================== 分页 ==================== */
function handlePageChange(page) {
  if (page < 1 || page > totalPages.value || page === currentPage.value) return
  currentPage.value = page
  loadData()
}

/* ==================== 单元格渲染 ==================== */
function getCellValue(row, col) {
  if (col.render && typeof col.render === 'function') {
    return col.render(row)
  }
  const val = row[col.key]
  if (val === null || val === undefined || val === '') return '-'
  // 日期格式化
  if (col.key === 'updated_at' || col.key === 'created_at') {
    return formatDate(val)
  }
  return val
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const h = String(d.getHours()).padStart(2, '0')
    const min = String(d.getMinutes()).padStart(2, '0')
    return `${y}-${m}-${day} ${h}:${min}`
  } catch {
    return dateStr
  }
}

/* ==================== 表单操作 ==================== */
function resetForm() {
  Object.keys(formData).forEach((k) => delete formData[k])
  Object.keys(formErrors).forEach((k) => delete formErrors[k])
}

function openCreate() {
  resetForm()
  editingRow.value = null
  // 初始化默认值（defaultValues prop 优先级最高，其次 formFields.default）
  props.formFields.forEach((field) => {
    if (field.type === 'number') {
      formData[field.key] = props.defaultValues[field.key] ?? field.default ?? null
    } else if (field.type === 'switch') {
      formData[field.key] = props.defaultValues[field.key] ?? field.default ?? false
    } else if (field.type === 'select' || field.type === 'select-remote') {
      formData[field.key] = props.defaultValues[field.key] ?? field.default ?? ''
    } else if (field.type === 'rich') {
      formData[field.key] = props.defaultValues[field.key] ?? field.default ?? ''
    } else {
      formData[field.key] = props.defaultValues[field.key] ?? field.default ?? ''
    }
  })
  modalMode.value = 'create'
  modalVisible.value = true
}

function openEdit(row) {
  resetForm()
  editingRow.value = row
  props.formFields.forEach((field) => {
    if (field.type === 'switch') {
      formData[field.key] = row[field.key] !== undefined && row[field.key] !== null
        ? !!row[field.key]
        : (field.default ?? false)
    } else {
      formData[field.key] = row[field.key] !== undefined && row[field.key] !== null
        ? row[field.key]
        : (field.default ?? '')
    }
  })
  // 保存原始 id
  formData.id = row.id
  modalMode.value = 'edit'
  modalVisible.value = true
}

function closeModal() {
  if (saving.value) return
  modalVisible.value = false
  resetForm()
}

/* ==================== 表单校验 ==================== */
function validateForm() {
  Object.keys(formErrors).forEach((k) => delete formErrors[k])
  let valid = true
  props.formFields.forEach((field) => {
    if (field.required) {
      const val = formData[field.key]
      if (val === null || val === undefined || val === '' || (typeof val === 'string' && val.trim() === '')) {
        formErrors[field.key] = `${field.label}为必填项`
        valid = false
      }
    }
    // 数字范围校验
    if (field.type === 'number' && val !== null && val !== '' && val !== undefined) {
      const num = Number(val)
      if (isNaN(num)) {
        formErrors[field.key] = `${field.label}必须为数字`
        valid = false
      } else if (field.min !== undefined && num < field.min) {
        formErrors[field.key] = `${field.label}不能小于 ${field.min}`
        valid = false
      } else if (field.max !== undefined && num > field.max) {
        formErrors[field.key] = `${field.label}不能大于 ${field.max}`
        valid = false
      }
    }
  })
  return valid
}

/* ==================== 保存 ==================== */
async function handleSave() {
  if (!validateForm()) {
    showToast('warning', '请检查表单填写')
    return
  }
  saving.value = true
  try {
    // 构建提交数据（排除 id）
    const submitData = {}
    props.formFields.forEach((field) => {
      let val = formData[field.key]
      // 数字字段转换
      if (field.type === 'number' && val !== null && val !== '' && val !== undefined) {
        val = Number(val)
      }
      // 空字符串 -> null（可选字段）
      if (val === '' && !field.required) {
        val = null
      }
      submitData[field.key] = val
    })

    // 注入全局默认值（如 world），即使 formFields 中没有定义该字段
    Object.entries(props.defaultValues).forEach(([key, value]) => {
      if (submitData[key] === undefined && value !== undefined && value !== null && value !== '') {
        submitData[key] = value
      }
    })

    if (modalMode.value === 'create') {
      await props.createFn(submitData)
      showToast('success', '创建成功')
    } else {
      // 第三个参数传递原始行，便于以 slug 等非 id 字段寻址的资源更新
      await props.updateFn(formData.id, submitData, editingRow.value)
      showToast('success', '更新成功')
    }
    modalVisible.value = false
    resetForm()
    loadData()
  } catch (err) {
    console.error('保存失败:', err)
    const msg = err?.response?.data?.detail || err?.message || '操作失败'
    showToast('error', typeof msg === 'string' ? msg : '操作失败')
  } finally {
    saving.value = false
  }
}

/* ==================== 删除 ==================== */
function openDelete(row) {
  deleteTarget.value = row
  confirmVisible.value = true
}

function closeConfirm() {
  if (deleting.value) return
  confirmVisible.value = false
  deleteTarget.value = null
}

async function handleConfirmDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await props.deleteFn(deleteTarget.value.id, deleteTarget.value)
    showToast('success', '删除成功')
    confirmVisible.value = false
    deleteTarget.value = null
    // 如果删除后当前页空了，回退一页
    if (tableData.value.length === 1 && currentPage.value > 1) {
      currentPage.value -= 1
    }
    loadData()
  } catch (err) {
    console.error('删除失败:', err)
    const msg = err?.response?.data?.detail || err?.message || '删除失败'
    showToast('error', typeof msg === 'string' ? msg : '删除失败')
  } finally {
    deleting.value = false
  }
}

/* ==================== 远程选项加载 ==================== */
const remoteOptions = reactive({})

async function loadRemoteOptions() {
  for (const field of props.formFields) {
    if (field.type === 'select-remote' && field.fetchOptions && !remoteOptions[field.key]) {
      try {
        // 如果 fetchOptions 不依赖 world 则直接调用；否则父组件会把 world 注入到 fetchOptions 中
        const res = await field.fetchOptions()
        let opts = []
        if (Array.isArray(res)) opts = res
        else if (res?.results) opts = res.results
        else if (res?.data && Array.isArray(res.data)) opts = res.data
        else if (res?.data?.results) opts = res.data.results
        remoteOptions[field.key] = opts
      } catch (e) {
        console.error(`加载字段 ${field.key} 选项失败:`, e)
        remoteOptions[field.key] = []
      }
    }
  }
}

/** 重置远程选项缓存（当 world 变更时需要重新拉取当前 world 的关联数据） */
function resetRemoteOptions() {
  Object.keys(remoteOptions).forEach((k) => delete remoteOptions[k])
  loadRemoteOptions()
}

function getFieldOptions(field) {
  if (field.type === 'select') return field.options || []
  if (field.type === 'select-remote') return remoteOptions[field.key] || []
  return []
}

function getOptionLabel(field, value) {
  const opts = getFieldOptions(field)
  const opt = opts.find((o) => o.value === value)
  return opt ? opt.label : value
}

/* ==================== 初始化 ==================== */
onMounted(() => {
  loadData()
  loadRemoteOptions()
})

// 监听 extraParams 变化（world 变更时会触发）→ 重新加载数据
watch(
  () => props.extraParams,
  (newVal, oldVal) => {
    if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
      currentPage.value = 1
      searchQuery.value = ''
      sortKey.value = ''
      loadData()
      resetRemoteOptions()
    }
  },
  { deep: true }
)

// 监听 defaultValues 变化 → 重置远程选项
watch(
  () => props.defaultValues,
  (newVal, oldVal) => {
    if (JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
      resetRemoteOptions()
    }
  },
  { deep: true }
)

// 暴露刷新方法给父组件
defineExpose({
  refresh: loadData,
  openCreate,
})
</script>

<template>
  <div class="crud-table">
    <!-- ==================== 顶部标题栏 ==================== -->
    <div class="crud-table__header">
      <div class="crud-table__title-wrap">
        <h2 class="crud-table__title">
          <span class="title-deco">◆</span>
          {{ title }}
        </h2>
        <span class="crud-table__count" v-if="!loading">共 {{ total }} 条</span>
      </div>
      <div class="crud-table__actions">
        <button v-if="canCreate" class="btn-create" @click="openCreate">
          <span class="btn-icon">+</span>
          <span>新增</span>
        </button>
      </div>
    </div>

    <!-- ==================== 搜索栏 ==================== -->
    <div class="crud-table__searchbar">
      <div class="search-wrap">
        <span class="search-icon">⌕</span>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          :placeholder="searchPlaceholder"
          @input="handleSearchInput"
          @keyup.enter="handleSearch"
        />
        <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''; handleSearch()">×</button>
      </div>
    </div>

    <!-- ==================== 表格 ==================== -->
    <div class="crud-table__wrapper">
      <table class="crud-table__table">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :style="{ width: col.width }"
              :class="{ sortable: col.sortable, sorted: sortKey === col.key }"
              @click="handleSort(col)"
            >
              <span class="th-content">
                {{ col.label }}
                <span v-if="col.sortable" class="sort-arrow">
                  <template v-if="sortKey === col.key">{{ sortOrder === 'asc' ? '▲' : '▼' }}</template>
                  <template v-else>↕</template>
                </span>
              </span>
            </th>
            <th v-if="showActions" class="actions-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <!-- 加载中 -->
          <tr v-if="loading" class="state-row">
            <td :colspan="columns.length + (showActions ? 1 : 0)" class="loading-cell">
              <div class="loader-wrap">
                <div class="loader-diamond"></div>
                <span>加载中...</span>
              </div>
            </td>
          </tr>
          <!-- 空状态 -->
          <tr v-else-if="tableData.length === 0" class="state-row">
            <td :colspan="columns.length + (showActions ? 1 : 0)" class="empty-cell">
              <div class="empty-wrap">
                <div class="empty-icon">◇</div>
                <p>暂无数据</p>
              </div>
            </td>
          </tr>
          <!-- 数据行 -->
          <tr v-for="(row, index) in tableData" :key="row.id || index" class="data-row">
            <td v-for="col in columns" :key="col.key" :style="{ width: col.width }">
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]">
                <span v-if="col.html" v-html="getCellValue(row, col)"></span>
                <span v-else class="cell-text">{{ getCellValue(row, col) }}</span>
              </slot>
            </td>
            <td v-if="showActions" class="actions-cell">
              <button
                v-if="canUpdate"
                class="action-btn action-btn--edit"
                title="编辑"
                @click="openEdit(row)"
              >
                <span class="action-icon">✎</span>
                <span class="action-text">编辑</span>
              </button>
              <button
                v-if="canDelete"
                class="action-btn action-btn--delete"
                title="删除"
                @click="openDelete(row)"
              >
                <span class="action-icon">×</span>
                <span class="action-text">删除</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ==================== 分页 ==================== -->
    <div v-if="total > 0" class="crud-table__pagination">
      <div class="pagination-info">
        共 <span class="page-total">{{ total }}</span> 条 · 第
        <span class="page-current">{{ currentPage }}</span> /
        <span class="page-all">{{ totalPages }}</span> 页
      </div>
      <div class="pagination-btns">
        <button
          class="page-btn"
          :disabled="currentPage <= 1"
          @click="handlePageChange(1)"
          title="首页"
        >
          «
        </button>
        <button
          class="page-btn"
          :disabled="currentPage <= 1"
          @click="handlePageChange(currentPage - 1)"
          title="上一页"
        >
          ‹
        </button>
        <template v-for="(p, i) in pageNumbers" :key="i">
          <span v-if="p === '...'" class="page-ellipsis">…</span>
          <button
            v-else
            class="page-btn"
            :class="{ 'page-btn--active': p === currentPage }"
            @click="handlePageChange(p)"
          >
            {{ p }}
          </button>
        </template>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="handlePageChange(currentPage + 1)"
          title="下一页"
        >
          ›
        </button>
        <button
          class="page-btn"
          :disabled="currentPage >= totalPages"
          @click="handlePageChange(totalPages)"
          title="末页"
        >
          »
        </button>
      </div>
    </div>

    <!-- ==================== 表单弹窗 ==================== -->
    <transition name="modal">
      <div v-if="modalVisible" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <!-- 弹窗头部 -->
          <div class="modal__header">
            <h3 class="modal__title">
              <span class="modal__deco">◆</span>
              {{ modalMode === 'create' ? '新增' : '编辑' }}
            </h3>
            <button class="modal__close" @click="closeModal" :disabled="saving">×</button>
          </div>

          <!-- 弹窗内容 -->
          <div class="modal__body">
            <div
              v-for="field in formFields"
              :key="field.key"
              class="form-group"
              :class="{ 'form-group--full': field.type === 'rich' || field.fullWidth }"
            >
              <label class="form-label">
                {{ field.label }}
                <span v-if="field.required" class="required-mark">*</span>
              </label>

              <!-- 文本输入 -->
              <input
                v-if="field.type === 'text' || !field.type"
                v-model="formData[field.key]"
                type="text"
                class="form-input"
                :placeholder="field.placeholder || `请输入${field.label}`"
                :disabled="saving"
              />

              <!-- 数字输入 -->
              <input
                v-else-if="field.type === 'number'"
                v-model="formData[field.key]"
                type="number"
                class="form-input"
                :min="field.min"
                :max="field.max"
                :step="field.step || 1"
                :placeholder="field.placeholder || `请输入${field.label}`"
                :disabled="saving"
              />

              <!-- 文本域 -->
              <textarea
                v-else-if="field.type === 'textarea'"
                v-model="formData[field.key]"
                class="form-textarea"
                :rows="field.rows || 3"
                :placeholder="field.placeholder || `请输入${field.label}`"
                :disabled="saving"
              ></textarea>

              <!-- 下拉选择（静态选项） -->
              <select
                v-else-if="field.type === 'select'"
                v-model="formData[field.key]"
                class="form-select"
                :disabled="saving"
              >
                <option value="">{{ field.placeholder || `请选择${field.label}` }}</option>
                <option
                  v-for="opt in field.options"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>

              <!-- 下拉选择（远程选项） -->
              <select
                v-else-if="field.type === 'select-remote'"
                v-model="formData[field.key]"
                class="form-select"
                :disabled="saving"
              >
                <option value="">{{ field.placeholder || `请选择${field.label}` }}</option>
                <option
                  v-for="opt in getFieldOptions(field)"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>

              <!-- 富文本编辑器 -->
              <RichEditor
                v-else-if="field.type === 'rich'"
                v-model="formData[field.key]"
                :placeholder="field.placeholder || `请输入${field.label}`"
              />

              <!-- 开关 -->
              <label v-else-if="field.type === 'switch'" class="form-switch">
                <input
                  type="checkbox"
                  v-model="formData[field.key]"
                  :disabled="saving"
                />
                <span class="switch-slider"></span>
                <span class="switch-text">{{ formData[field.key] ? '启用' : '停用' }}</span>
              </label>

              <!-- 错误提示 -->
              <span v-if="formErrors[field.key]" class="form-error">
                {{ formErrors[field.key] }}
              </span>
            </div>
          </div>

          <!-- 弹窗底部 -->
          <div class="modal__footer">
            <button class="btn-cancel" @click="closeModal" :disabled="saving">
              取消
            </button>
            <button class="btn-save" @click="handleSave" :disabled="saving">
              <span v-if="saving" class="btn-loading"></span>
              {{ saving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ==================== 删除确认弹窗 ==================== -->
    <transition name="modal">
      <div v-if="confirmVisible" class="modal-overlay" @click.self="closeConfirm">
        <div class="confirm-modal">
          <div class="confirm-modal__icon">⚠</div>
          <h3 class="confirm-modal__title">确认删除</h3>
          <p class="confirm-modal__text">
            确定要删除「<span class="confirm-target">{{ deleteTarget?.name || deleteTarget?.id }}</span>」吗？
          </p>
          <p class="confirm-modal__hint">此操作不可恢复</p>
          <div class="confirm-modal__actions">
            <button class="btn-cancel" @click="closeConfirm" :disabled="deleting">
              取消
            </button>
            <button class="btn-danger" @click="handleConfirmDelete" :disabled="deleting">
              <span v-if="deleting" class="btn-loading"></span>
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- ==================== Toast 通知 ==================== -->
    <transition-group name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast"
        :class="`toast--${toast.type}`"
        @click="removeToast(toast.id)"
      >
        <span class="toast__icon">
          <template v-if="toast.type === 'success'">✓</template>
          <template v-else-if="toast.type === 'error'">✕</template>
          <template v-else-if="toast.type === 'warning'">⚠</template>
          <template v-else>ℹ</template>
        </span>
        <span class="toast__msg">{{ toast.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
/* ==================== 容器 ==================== */
.crud-table {
  width: 100%;
}

/* ==================== 顶部标题栏 ==================== */
.crud-table__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.crud-table__title-wrap {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.crud-table__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.title-deco {
  color: var(--color-gold-primary);
  font-size: var(--font-size-sm);
  filter: drop-shadow(0 0 4px var(--color-gold-glow));
}

.crud-table__count {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  padding: 2px 10px;
  border: 1px solid var(--border-color-light);
  border-radius: 12px;
}

.crud-table__actions {
  display: flex;
  gap: var(--spacing-sm);
}

/* 新增按钮 */
.btn-create {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: linear-gradient(135deg, var(--color-gold-dark), var(--color-gold-primary));
  border: 1px solid var(--color-gold-primary);
  border-radius: var(--border-radius-md);
  color: var(--color-blue-deep);
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-create:hover {
  background: linear-gradient(135deg, var(--color-gold-primary), var(--color-gold-light));
  box-shadow: var(--shadow-gold);
  transform: translateY(-1px);
}

.btn-icon {
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
}

/* ==================== 搜索栏 ==================== */
.crud-table__searchbar {
  margin-bottom: var(--spacing-md);
}

.search-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 100%;
  max-width: 360px;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  font-size: 18px;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 8px 32px 8px 38px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  outline: none;
  transition: all var(--transition-fast);
}

.search-input:focus {
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 0 2px rgba(212, 168, 83, 0.1);
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-clear {
  position: absolute;
  right: 8px;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: var(--bg-card-hover);
  color: var(--text-muted);
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
}

.search-clear:hover {
  color: var(--text-primary);
  background: var(--border-color);
}

/* ==================== 表格容器 ==================== */
.crud-table__wrapper {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  position: relative;
}

.crud-table__wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-gold-primary), transparent);
  opacity: 0.5;
}

.crud-table__table {
  width: 100%;
  border-collapse: collapse;
}

.crud-table__table th,
.crud-table__table td {
  padding: 10px var(--spacing-md);
  text-align: left;
  border-bottom: 1px solid var(--border-color-light);
}

.crud-table__table th {
  background: rgba(13, 21, 37, 0.6);
  color: var(--text-gold);
  font-size: var(--font-size-sm);
  font-weight: 600;
  white-space: nowrap;
  position: sticky;
  top: 0;
}

.th-content {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.sortable {
  cursor: pointer;
  user-select: none;
  transition: color var(--transition-fast);
}

.sortable:hover {
  color: var(--color-gold-light);
}

.sorted {
  color: var(--color-gold-light);
}

.sort-arrow {
  font-size: 10px;
  opacity: 0.7;
}

.crud-table__table td {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.cell-text {
  display: inline-block;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
}

.data-row {
  transition: background var(--transition-fast);
}

.data-row:hover {
  background: rgba(212, 168, 83, 0.05);
}

.data-row:last-child td {
  border-bottom: none;
}

/* 状态行 */
.state-row td {
  padding: var(--spacing-2xl);
}

.loading-cell,
.empty-cell {
  text-align: center;
}

.loader-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--text-muted);
}

.loader-diamond {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border-color);
  border-top-color: var(--color-gold-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.empty-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-sm);
  color: var(--text-muted);
}

.empty-icon {
  font-size: 40px;
  color: var(--color-gold-dark);
  opacity: 0.4;
}

/* 操作列 */
.actions-col,
.actions-cell {
  text-align: right;
  white-space: nowrap;
  width: 140px;
}

.actions-cell {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--font-size-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-icon {
  font-size: 12px;
}

.action-btn--edit:hover {
  border-color: var(--color-cyan-primary);
  color: var(--color-cyan-primary);
  background: rgba(0, 212, 170, 0.08);
}

.action-btn--delete:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
  background: rgba(255, 71, 87, 0.08);
}

/* ==================== 分页 ==================== */
.crud-table__pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.page-total,
.page-current {
  color: var(--text-gold);
  font-weight: 600;
}

.pagination-btns {
  display: flex;
  gap: 4px;
  align-items: center;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: var(--bg-card);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.08);
}

.page-btn--active {
  background: linear-gradient(135deg, var(--color-gold-dark), var(--color-gold-primary));
  border-color: var(--color-gold-primary);
  color: var(--color-blue-deep);
  font-weight: 600;
}

.page-btn--active:hover {
  color: var(--color-blue-deep);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-ellipsis {
  color: var(--text-muted);
  padding: 0 4px;
}

/* ==================== 弹窗 ==================== */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(6, 11, 20, 0.85);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  padding: var(--spacing-lg);
}

.modal {
  background: linear-gradient(180deg, rgba(26, 35, 64, 0.98) 0%, rgba(13, 21, 37, 0.99) 100%);
  border: 1px solid var(--border-color-active);
  border-radius: var(--border-radius-lg);
  width: 100%;
  max-width: 720px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg), 0 0 40px rgba(212, 168, 83, 0.1);
  overflow: hidden;
}

.modal::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-gold-primary), transparent);
}

.modal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.modal__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-gold);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.modal__deco {
  font-size: var(--font-size-sm);
  color: var(--color-gold-primary);
}

.modal__close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal__close:hover:not(:disabled) {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.modal__close:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal__body {
  padding: var(--spacing-lg) var(--spacing-xl);
  overflow-y: auto;
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

/* 表单组 */
.form-group {
  display: flex;
  flex-direction: column;
}

.form-group--full {
  grid-column: 1 / -1;
}

.form-label {
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.required-mark {
  color: var(--color-danger);
  margin-left: 2px;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 8px 12px;
  background: rgba(13, 21, 37, 0.6);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-family: inherit;
  outline: none;
  transition: all var(--transition-fast);
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 0 2px rgba(212, 168, 83, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: var(--text-muted);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23D4A853' stroke-width='2'%3e%3cpath d='M6 9l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  padding-right: 32px;
}

.form-select option {
  background: var(--color-blue-dark);
  color: var(--text-primary);
}

.form-error {
  margin-top: 4px;
  color: var(--color-danger);
  font-size: var(--font-size-xs);
}

/* 开关 */
.form-switch {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  padding: 6px 0;
}

.form-switch input[type='checkbox'] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: rgba(139, 157, 195, 0.25);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.switch-slider::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--text-muted);
  transform: translateY(-50%);
  transition: all var(--transition-fast);
}

.form-switch input:checked + .switch-slider {
  background: rgba(212, 168, 83, 0.3);
  border-color: var(--color-gold-primary);
}

.form-switch input:checked + .switch-slider::after {
  left: 23px;
  background: var(--color-gold-primary);
  box-shadow: 0 0 8px var(--color-gold-glow);
}

.switch-text {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 弹窗底部 */
.modal__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-xl);
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.btn-cancel,
.btn-save,
.btn-danger {
  padding: 8px 20px;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-cancel {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-cancel:hover:not(:disabled) {
  border-color: var(--text-secondary);
  color: var(--text-primary);
}

.btn-save {
  background: linear-gradient(135deg, var(--color-gold-dark), var(--color-gold-primary));
  border: 1px solid var(--color-gold-primary);
  color: var(--color-blue-deep);
  font-weight: 600;
}

.btn-save:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-gold-primary), var(--color-gold-light));
  box-shadow: var(--shadow-gold);
}

.btn-danger {
  background: linear-gradient(135deg, #c0392b, var(--color-danger));
  border: 1px solid var(--color-danger);
  color: #fff;
  font-weight: 600;
}

.btn-danger:hover:not(:disabled) {
  box-shadow: 0 0 16px rgba(255, 71, 87, 0.4);
}

.btn-cancel:disabled,
.btn-save:disabled,
.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-loading {
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

/* ==================== 确认弹窗 ==================== */
.confirm-modal {
  background: linear-gradient(180deg, rgba(26, 35, 64, 0.98) 0%, rgba(13, 21, 37, 0.99) 100%);
  border: 1px solid var(--color-danger);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  max-width: 420px;
  width: 100%;
  text-align: center;
  box-shadow: var(--shadow-lg), 0 0 40px rgba(255, 71, 87, 0.15);
}

.confirm-modal__icon {
  font-size: 48px;
  color: var(--color-danger);
  margin-bottom: var(--spacing-sm);
  filter: drop-shadow(0 0 12px rgba(255, 71, 87, 0.4));
}

.confirm-modal__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-heading);
  margin-bottom: var(--spacing-sm);
}

.confirm-modal__text {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xs);
}

.confirm-target {
  color: var(--text-gold);
  font-weight: 600;
}

.confirm-modal__hint {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  margin-bottom: var(--spacing-lg);
}

.confirm-modal__actions {
  display: flex;
  justify-content: center;
  gap: var(--spacing-sm);
}

/* ==================== Toast ==================== */
.toast-container {
  position: fixed;
  top: 72px;
  right: 24px;
  z-index: var(--z-toast);
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  cursor: pointer;
  pointer-events: auto;
  min-width: 240px;
  backdrop-filter: blur(8px);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
}

.toast--success {
  background: rgba(46, 213, 115, 0.15);
  border-color: var(--color-success);
  color: var(--color-success);
}

.toast--error {
  background: rgba(255, 71, 87, 0.15);
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.toast--warning {
  background: rgba(255, 165, 2, 0.15);
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.toast--info {
  background: rgba(30, 144, 255, 0.15);
  border-color: var(--color-info);
  color: var(--color-info);
}

.toast__icon {
  font-size: 16px;
  font-weight: 700;
}

.toast__msg {
  color: var(--text-primary);
  flex: 1;
}

/* ==================== 过渡动画 ==================== */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-normal);
}

.modal-enter-active .modal,
.modal-enter-active .confirm-modal,
.modal-leave-active .modal,
.modal-leave-active .confirm-modal {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal,
.modal-enter-from .confirm-modal {
  transform: scale(0.95) translateY(-10px);
}

.modal-leave-to .modal,
.modal-leave-to .confirm-modal {
  transform: scale(0.95) translateY(10px);
}

.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(40px);
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
  .modal__body {
    grid-template-columns: 1fr;
  }

  .actions-cell {
    flex-direction: column;
    gap: 4px;
  }

  .action-text {
    display: none;
  }

  .crud-table__pagination {
    flex-direction: column;
    align-items: stretch;
  }

  .pagination-btns {
    justify-content: center;
    flex-wrap: wrap;
  }

  .cell-text {
    max-width: 160px;
  }
}
</style>
