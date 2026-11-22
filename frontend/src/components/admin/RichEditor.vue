<script setup>
/**
 * 富文本编辑器 (RichEditor)
 *
 * 基于 contenteditable 的简易富文本编辑器，原神风格深色主题。
 * 支持格式：粗体、斜体、下划线、删除线、标题(H2/H3)、段落、
 * 有序/无序列表、引用、链接、清除格式、撤销/重做。
 *
 * Props:
 *   - modelValue:   v-model 绑定值 (HTML 字符串)
 *   - placeholder:  占位文本
 *   - minHeight:    最小高度
 */
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '请输入内容...' },
  minHeight: { type: String, default: '200px' },
})

const emit = defineEmits(['update:modelValue'])

const editorRef = ref(null)
const activeFormats = ref({})
let isInternalChange = false

/** 工具栏按钮分组配置 */
const toolbarGroups = [
  {
    name: 'history',
    buttons: [
      { command: 'undo', icon: '↶', title: '撤销' },
      { command: 'redo', icon: '↷', title: '重做' },
    ],
  },
  {
    name: 'basic',
    buttons: [
      { command: 'bold', icon: 'B', title: '粗体', style: 'font-weight:700' },
      { command: 'italic', icon: 'I', title: '斜体', style: 'font-style:italic' },
      { command: 'underline', icon: 'U', title: '下划线', style: 'text-decoration:underline' },
      { command: 'strikeThrough', icon: 'S', title: '删除线', style: 'text-decoration:line-through' },
    ],
  },
  {
    name: 'block',
    buttons: [
      { command: 'formatBlock', value: 'h2', icon: 'H2', title: '标题2' },
      { command: 'formatBlock', value: 'h3', icon: 'H3', title: '标题3' },
      { command: 'formatBlock', value: 'p', icon: '¶', title: '段落' },
      { command: 'formatBlock', value: 'blockquote', icon: '❝', title: '引用' },
    ],
  },
  {
    name: 'list',
    buttons: [
      { command: 'insertUnorderedList', icon: '•', title: '无序列表' },
      { command: 'insertOrderedList', icon: '1.', title: '有序列表' },
    ],
  },
  {
    name: 'extra',
    buttons: [
      { command: 'link', icon: '🔗', title: '插入链接', custom: true },
      { command: 'removeFormat', icon: '⌫', title: '清除格式' },
    ],
  },
]

/** 执行格式命令 */
function execCommand(command, value = null) {
  editorRef.value?.focus()
  document.execCommand(command, false, value)
  handleInput()
  updateActiveFormats()
}

/** 插入链接 */
function insertLink() {
  const selection = window.getSelection()
  const selectedText = selection ? selection.toString() : ''
  const url = window.prompt('请输入链接URL:', 'https://')
  if (url) {
    editorRef.value?.focus()
    if (selectedText) {
      document.execCommand('createLink', false, url)
    } else {
      const text = window.prompt('链接显示文字:', url) || url
      const linkHtml = `<a href="${url}" target="_blank">${text}</a>`
      document.execCommand('insertHTML', false, linkHtml)
    }
    handleInput()
  }
}

/** 处理工具栏按钮点击 */
function handleToolbarClick(btn) {
  if (btn.custom && btn.command === 'link') {
    insertLink()
  } else {
    execCommand(btn.command, btn.value)
  }
}

/** 输入处理 */
function handleInput() {
  if (editorRef.value) {
    isInternalChange = true
    emit('update:modelValue', editorRef.value.innerHTML)
    nextTick(() => {
      isInternalChange = false
    })
  }
  updateActiveFormats()
}

/** 更新当前激活的格式状态 */
function updateActiveFormats() {
  if (!editorRef.value) return
  try {
    activeFormats.value = {
      bold: document.queryCommandState('bold'),
      italic: document.queryCommandState('italic'),
      underline: document.queryCommandState('underline'),
      strikeThrough: document.queryCommandState('strikeThrough'),
      insertUnorderedList: document.queryCommandState('insertUnorderedList'),
      insertOrderedList: document.queryCommandState('insertOrderedList'),
    }
  } catch (e) {
    // 忽略
  }
}

/** 判断按钮是否激活 */
function isButtonActive(btn) {
  if (btn.command === 'formatBlock') {
    try {
      const block = document.queryCommandValue('formatBlock')
      return block === btn.value
    } catch {
      return false
    }
  }
  return !!activeFormats.value[btn.command]
}

/** 处理粘贴 - 清除样式仅保留文本结构 */
function handlePaste(e) {
  e.preventDefault()
  const text = (e.clipboardData || window.clipboardData).getData('text/plain')
  document.execCommand('insertText', false, text)
}

/** 处理按键 - Tab 缩进 */
function handleKeydown(e) {
  if (e.key === 'Tab') {
    e.preventDefault()
    document.execCommand('insertHTML', false, '&nbsp;&nbsp;&nbsp;&nbsp;')
  }
}

/** 初始化编辑器内容 */
onMounted(() => {
  if (editorRef.value && props.modelValue) {
    editorRef.value.innerHTML = props.modelValue
  }
})

/** 监听外部值变化 */
watch(
  () => props.modelValue,
  (newVal) => {
    if (editorRef.value && !isInternalChange) {
      const current = editorRef.value.innerHTML
      if (current !== newVal) {
        editorRef.value.innerHTML = newVal || ''
      }
    }
  }
)
</script>

<template>
  <div class="rich-editor">
    <!-- 工具栏 -->
    <div class="rich-editor__toolbar">
      <template v-for="(group, gIdx) in toolbarGroups" :key="group.name">
        <div class="toolbar-group">
          <button
            v-for="btn in group.buttons"
            :key="btn.command + (btn.value || '')"
            class="toolbar-btn"
            :class="{ 'toolbar-btn--active': isButtonActive(btn) }"
            :title="btn.title"
            :style="btn.style"
            @click="handleToolbarClick(btn)"
            @mousedown.prevent
          >
            {{ btn.icon }}
          </button>
        </div>
        <div v-if="gIdx < toolbarGroups.length - 1" class="toolbar-divider"></div>
      </template>
    </div>

    <!-- 编辑区域 -->
    <div
      ref="editorRef"
      class="rich-editor__content"
      contenteditable="true"
      :data-placeholder="placeholder"
      :style="{ minHeight: minHeight }"
      @input="handleInput"
      @paste="handlePaste"
      @keydown="handleKeydown"
      @mouseup="updateActiveFormats"
      @keyup="updateActiveFormats"
    ></div>
  </div>
</template>

<style scoped>
.rich-editor {
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  overflow: hidden;
  background: rgba(13, 21, 37, 0.6);
  transition: border-color var(--transition-fast);
}

.rich-editor:focus-within {
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 0 2px rgba(212, 168, 83, 0.1);
}

/* 工具栏 */
.rich-editor__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 2px;
  padding: 6px 8px;
  background: rgba(13, 21, 37, 0.8);
  border-bottom: 1px solid var(--border-color);
}

.toolbar-group {
  display: flex;
  gap: 2px;
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: var(--border-color);
  margin: 0 4px;
}

.toolbar-btn {
  min-width: 30px;
  height: 30px;
  padding: 0 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  border-radius: var(--border-radius-sm);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 600;
  transition: all var(--transition-fast);
  user-select: none;
}

.toolbar-btn:hover {
  background: rgba(212, 168, 83, 0.1);
  border-color: var(--border-color);
  color: var(--text-gold);
}

.toolbar-btn--active {
  background: rgba(212, 168, 83, 0.2);
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
}

/* 编辑区域 */
.rich-editor__content {
  max-height: 500px;
  overflow-y: auto;
  padding: 12px 16px;
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  line-height: 1.7;
  outline: none;
}

.rich-editor__content:empty::before {
  content: attr(data-placeholder);
  color: var(--text-muted);
  pointer-events: none;
}

/* 富文本内容样式 */
.rich-editor__content :deep(h2) {
  font-family: var(--font-family-display);
  color: var(--text-gold);
  font-size: var(--font-size-lg);
  margin: 14px 0 8px;
  padding-bottom: 4px;
  border-bottom: 1px solid var(--border-color-light);
}

.rich-editor__content :deep(h3) {
  color: var(--text-heading);
  font-size: var(--font-size-base);
  margin: 10px 0 6px;
}

.rich-editor__content :deep(p) {
  margin: 6px 0;
}

.rich-editor__content :deep(a) {
  color: var(--color-cyan-primary);
  text-decoration: underline;
  cursor: pointer;
}

.rich-editor__content :deep(a:hover) {
  color: var(--color-cyan-light);
}

.rich-editor__content :deep(ul),
.rich-editor__content :deep(ol) {
  padding-left: 24px;
  margin: 6px 0;
}

.rich-editor__content :deep(li) {
  margin: 2px 0;
}

.rich-editor__content :deep(blockquote) {
  margin: 10px 0;
  padding: 8px 16px;
  border-left: 3px solid var(--color-gold-primary);
  background: rgba(212, 168, 83, 0.05);
  color: var(--text-secondary);
  font-style: italic;
}

.rich-editor__content :deep(strong),
.rich-editor__content :deep(b) {
  color: var(--text-heading);
  font-weight: 700;
}

.rich-editor__content :deep(em),
.rich-editor__content :deep(i) {
  color: var(--color-cyan-light);
}
</style>
