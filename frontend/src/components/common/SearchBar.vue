<script setup>
/**
 * 搜索栏 (SearchBar) - 原神风格增强版
 *
 * 跨模块搜索功能，点击展开搜索输入框
 * 支持搜索角色、族群、宝物、技能、异兽、碎片世界
 */
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'

const router = useRouter()
const worldData = useWorldDataStore()

const searchQuery = ref('')
const searchExpanded = ref(false)
const showResults = ref(false)

/** 类型标签映射 */
const typeLabels = {
  character: '角色',
  faction: '族群',
  artifact: '宝物',
  ability: '能力',
  creature: '异兽',
  'fragment-world': '世界',
  realm: '境界',
}

/** 搜索防抖 */
let debounceTimer = null
watch(searchQuery, (newVal) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!newVal.trim()) {
    showResults.value = false
    return
  }
  debounceTimer = setTimeout(() => {
    worldData.search(newVal)
    showResults.value = true
  }, 300)
})

/** 展开搜索框 */
function expandSearch() {
  searchExpanded.value = true
}

/** 收起搜索框 */
function collapseSearch() {
  setTimeout(() => {
    searchExpanded.value = false
    showResults.value = false
  }, 200)
}

/** 跳转到搜索结果 */
function goToResult(result) {
  showResults.value = false
  searchQuery.value = ''
  searchExpanded.value = false
  const routeMap = {
    character: `/characters/${result.id}`,
    faction: `/factions/${result.id}`,
    artifact: `/artifacts/${result.id}`,
    creature: `/creatures/${result.id}`,
    'fragment-world': `/fragment-worlds/${result.id}`,
  }
  const path = routeMap[result.type] || `/lore/${result.slug}`
  router.push(path)
}
</script>

<template>
  <div class="search-bar" :class="{ 'search-bar--expanded': searchExpanded }">
    <button class="search-bar__trigger" @click="expandSearch" title="搜索">
      <span class="search-icon">🔍</span>
    </button>

    <div v-if="searchExpanded" class="search-bar__input-wrapper">
      <input
        v-model="searchQuery"
        type="text"
        class="search-bar__input"
        placeholder="搜索角色、族群、宝物..."
        @blur="collapseSearch"
        @focus="expandSearch"
        autofocus
      />

      <!-- 搜索结果下拉 -->
      <div v-if="showResults" class="search-bar__results">
        <div v-if="worldData.searchResults.length === 0" class="search-bar__empty">
          <span v-if="worldData.searchLoading" class="search-loading">
            <span class="genshin-loader" style="width: 30px; height: 30px;">
              <span class="genshin-loader__ring genshin-loader__ring--outer" style="border-width: 1.5px;"></span>
              <span class="genshin-loader__ring genshin-loader__ring--inner" style="border-width: 1.5px;"></span>
            </span>
            搜索中...
          </span>
          <span v-else>未找到相关结果</span>
        </div>

        <div
          v-for="(result, index) in worldData.searchResults"
          :key="index"
          class="search-bar__result-item"
          @mousedown="goToResult(result)"
        >
          <span class="result-type">{{ typeLabels[result.type] || result.type }}</span>
          <span class="result-name">{{ result.name }}</span>
          <span v-if="result.description" class="result-desc">
            {{ result.description }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-bar {
  position: relative;
  display: flex;
  align-items: center;
}

.search-bar__trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: var(--bg-card);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.search-bar__trigger:hover {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
  box-shadow: 0 0 10px var(--color-gold-glow);
}

.search-icon {
  font-size: 16px;
}

.search-bar__input-wrapper {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: var(--spacing-xs);
  width: 320px;
}

.search-bar__input {
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(13, 21, 37, 0.95);
  border: 1px solid var(--border-color-active);
  border-radius: var(--border-radius-md);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  outline: none;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: all var(--transition-fast);
}

.search-bar__input:focus {
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 16px var(--color-gold-glow);
}

.search-bar__input::placeholder {
  color: var(--text-muted);
}

.search-bar__results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: var(--spacing-xs);
  background: rgba(13, 21, 37, 0.98);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  max-height: 400px;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.search-bar__empty {
  padding: var(--spacing-lg);
  text-align: center;
  color: var(--text-muted);
  font-size: var(--font-size-sm);
}

.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.search-bar__result-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-bottom: 1px solid var(--border-color-light);
}

.search-bar__result-item:last-child {
  border-bottom: none;
}

.search-bar__result-item:hover {
  background: rgba(212, 168, 83, 0.08);
  padding-left: calc(var(--spacing-md) + 4px);
}

.result-type {
  font-size: var(--font-size-xs);
  color: var(--text-gold);
  padding: 2px 6px;
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  flex-shrink: 0;
}

.result-name {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
}

.result-desc {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  margin-left: auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 150px;
}

@media (max-width: 768px) {
  .search-bar__input-wrapper {
    width: 260px;
  }
}
</style>
