<script setup>
/**
 * 后台仪表盘 (Dashboard)
 *
 * 残响界管理后台首页，展示：
 * - 4个核心统计卡片（角色总数、族群总数、宝物总数、碎片世界总数）
 * - 快捷操作入口
 * - 最近更新记录列表
 * - 原神风格装饰
 */
import { ref, reactive, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import {
  factionApi,
  characterApi,
  artifactApi,
  creatureApi,
  fragmentWorldApi,
  abilityApi,
} from '@/api'

const worldData = useWorldDataStore()

/** 当前大世界 slug（用于按世界过滤） */
function currentWorld() {
  return worldData.currentWorldSlug
}

/* ==================== 统计数据 ==================== */
const stats = reactive([
  {
    label: '角色总数',
    value: 0,
    icon: '◉',
    path: '/admin/characters',
    color: 'var(--color-cyan-primary)',
    glow: 'rgba(0, 212, 170, 0.3)',
    loading: true,
    fetchFn: () => characterApi.list({ page_size: 1, world: currentWorld() }),
  },
  {
    label: '族群总数',
    value: 0,
    icon: '◈',
    path: '/admin/factions',
    color: 'var(--color-gold-primary)',
    glow: 'rgba(212, 168, 83, 0.3)',
    loading: true,
    fetchFn: () => factionApi.list({ page_size: 1, world: currentWorld() }),
  },
  {
    label: '宝物总数',
    value: 0,
    icon: '◇',
    path: '/admin/artifacts',
    color: 'var(--rarity-legendary)',
    glow: 'rgba(255, 140, 0, 0.3)',
    loading: true,
    fetchFn: () => artifactApi.list({ page_size: 1, world: currentWorld() }),
  },
  {
    label: '碎片世界',
    value: 0,
    icon: '✧',
    path: '/admin/fragment-worlds',
    color: 'var(--rarity-epic)',
    glow: 'rgba(155, 89, 182, 0.3)',
    loading: true,
    fetchFn: () => fragmentWorldApi.list({ page_size: 1, world: currentWorld() }),
  },
])

/* ==================== 次级统计 ==================== */
const secondaryStats = reactive([
  {
    label: '异兽总数',
    value: 0,
    icon: '❖',
    path: '/admin/creatures',
    fetchFn: () => creatureApi.list({ page_size: 1, world: currentWorld() }),
  },
  {
    label: '能力体系',
    value: 0,
    icon: '✦',
    path: '/admin/abilities',
    fetchFn: () => abilityApi.list({ page_size: 1, world: currentWorld() }),
  },
])

/* ==================== 快捷操作 ==================== */
const quickActions = [
  { name: '新增族群', path: '/admin/factions', icon: '◈', desc: '创建新的势力阵营' },
  { name: '新增角色', path: '/admin/characters', icon: '◉', desc: '录入新角色信息' },
  { name: '新增宝物', path: '/admin/artifacts', icon: '◇', desc: '添加神器宝物' },
  { name: '新增异兽', path: '/admin/creatures', icon: '❖', desc: '记录异兽图鉴' },
  { name: '新增碎片世界', path: '/admin/fragment-worlds', icon: '✧', desc: '建立新世界设定' },
  { name: '能力体系', path: '/admin/abilities', icon: '✦', desc: '管理境界与技能' },
]

/* ==================== 最近更新 ==================== */
const recentUpdates = ref([])
const loadingRecent = ref(true)

/** 加载统计数据 */
async function loadStats() {
  // 主统计卡片
  const mainPromises = stats.map(async (stat) => {
    try {
      const res = await stat.fetchFn()
      let count = 0
      if (Array.isArray(res)) count = res.length
      else if (res?.count !== undefined) count = res.count
      else if (res?.results) count = res.count ?? res.results.length
      else if (res?.data?.count !== undefined) count = res.data.count
      else if (res?.data?.results) count = res.data.count ?? res.data.results.length
      else if (res?.data && Array.isArray(res.data)) count = res.data.length
      stat.value = count
    } catch (e) {
      console.error(`加载${stat.label}失败:`, e)
      stat.value = 0
    } finally {
      stat.loading = false
    }
  })

  // 次级统计
  const secPromises = secondaryStats.map(async (stat) => {
    try {
      const res = await stat.fetchFn()
      let count = 0
      if (Array.isArray(res)) count = res.length
      else if (res?.count !== undefined) count = res.count
      else if (res?.results) count = res.count ?? res.results.length
      else if (res?.data?.count !== undefined) count = res.data.count
      else if (res?.data?.results) count = res.data.count ?? res.data.results.length
      else if (res?.data && Array.isArray(res.data)) count = res.data.length
      stat.value = count
    } catch (e) {
      console.error(`加载${stat.label}失败:`, e)
    }
  })

  await Promise.allSettled([...mainPromises, ...secPromises])
}

/** 加载最近更新记录 */
async function loadRecentUpdates() {
  loadingRecent.value = true
  try {
    // 获取各模块最近更新的数据
    const modules = [
      { name: '角色', path: '/admin/characters', api: characterApi, icon: '◉' },
      { name: '族群', path: '/admin/factions', api: factionApi, icon: '◈' },
      { name: '宝物', path: '/admin/artifacts', api: artifactApi, icon: '◇' },
      { name: '碎片世界', path: '/admin/fragment-worlds', api: fragmentWorldApi, icon: '✧' },
    ]

    const results = await Promise.allSettled(
      modules.map(async (m) => {
        const res = await m.api.list({ page_size: 3, ordering: '-updated_at', world: currentWorld() })
        let items = []
        if (Array.isArray(res)) items = res
        else if (res?.results) items = res.results
        else if (res?.data?.results) items = res.data.results
        else if (res?.data && Array.isArray(res.data)) items = res.data
        return items.map((item) => ({
          ...item,
          moduleName: m.name,
          modulePath: m.path,
          moduleIcon: m.icon,
          title: item.name || item.title || `#${item.id}`,
        }))
      })
    )

    const allUpdates = []
    results.forEach((r) => {
      if (r.status === 'fulfilled' && Array.isArray(r.value)) {
        allUpdates.push(...r.value)
      }
    })

    // 按更新时间排序
    allUpdates.sort((a, b) => {
      const ta = new Date(a.updated_at || a.created_at || 0).getTime()
      const tb = new Date(b.updated_at || b.created_at || 0).getTime()
      return tb - ta
    })

    recentUpdates.value = allUpdates.slice(0, 8)
  } catch (e) {
    console.error('加载最近更新失败:', e)
    recentUpdates.value = []
  } finally {
    loadingRecent.value = false
  }
}

/** 格式化时间 */
function formatRelativeTime(dateStr) {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes} 分钟前`
  if (hours < 24) return `${hours} 小时前`
  if (days < 30) return `${days} 天前`
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${m}-${d}`
}

onMounted(async () => {
  // 确保当前大世界上下文已就绪
  await worldData.ensureCurrentWorld()
  loadStats()
  loadRecentUpdates()
})

// 大世界切换时重新加载统计数据
watch(
  () => worldData.currentWorldSlug,
  (newSlug, oldSlug) => {
    if (newSlug && newSlug !== oldSlug) {
      loadStats()
      loadRecentUpdates()
    }
  }
)
</script>

<template>
  <div class="dashboard">
    <!-- 欢迎标题 -->
    <div class="dashboard__welcome">
      <h1 class="dashboard__title">
        <span class="title-deco-left">◆</span>
        残响界 · 管理后台
        <span class="title-deco-right">◆</span>
      </h1>
      <p class="dashboard__subtitle">异世界世界观设定管理系统</p>
    </div>

    <!-- ==================== 统计卡片 ==================== -->
    <div class="stats-grid">
      <RouterLink
        v-for="stat in stats"
        :key="stat.label"
        :to="stat.path"
        class="stat-card"
        :style="{ '--card-color': stat.color, '--card-glow': stat.glow }"
      >
        <div class="stat-card__icon-wrap">
          <span class="stat-card__icon">{{ stat.icon }}</span>
        </div>
        <div class="stat-card__body">
          <div class="stat-card__value">
            <span v-if="stat.loading" class="stat-loader"></span>
            <span v-else>{{ stat.value }}</span>
          </div>
          <div class="stat-card__label">{{ stat.label }}</div>
        </div>
        <div class="stat-card__arrow">→</div>
      </RouterLink>
    </div>

    <!-- 次级统计 -->
    <div class="secondary-stats">
      <RouterLink
        v-for="stat in secondaryStats"
        :key="stat.label"
        :to="stat.path"
        class="secondary-stat"
      >
        <span class="secondary-stat__icon">{{ stat.icon }}</span>
        <span class="secondary-stat__value">{{ stat.value }}</span>
        <span class="secondary-stat__label">{{ stat.label }}</span>
      </RouterLink>
    </div>

    <!-- ==================== 快捷操作 ==================== -->
    <section class="dashboard-section">
      <h2 class="section-heading">
        <span class="heading-deco">◆</span>
        快捷操作
      </h2>
      <div class="quick-actions">
        <RouterLink
          v-for="action in quickActions"
          :key="action.name"
          :to="action.path"
          class="quick-action"
        >
          <div class="quick-action__icon">{{ action.icon }}</div>
          <div class="quick-action__info">
            <div class="quick-action__name">{{ action.name }}</div>
            <div class="quick-action__desc">{{ action.desc }}</div>
          </div>
          <div class="quick-action__arrow">›</div>
        </RouterLink>
      </div>
    </section>

    <!-- ==================== 最近更新 ==================== -->
    <section class="dashboard-section">
      <h2 class="section-heading">
        <span class="heading-deco">◆</span>
        最近更新
      </h2>
      <div class="recent-panel">
        <div v-if="loadingRecent" class="recent-loading">
          <div class="loader-diamond"></div>
          <span>加载中...</span>
        </div>
        <div v-else-if="recentUpdates.length === 0" class="recent-empty">
          <div class="empty-icon">◇</div>
          <p>暂无更新记录</p>
        </div>
        <ul v-else class="recent-list">
          <li
            v-for="(item, idx) in recentUpdates"
            :key="idx"
            class="recent-item"
          >
            <RouterLink :to="item.modulePath" class="recent-item__link">
              <span class="recent-item__icon">{{ item.moduleIcon }}</span>
              <div class="recent-item__content">
                <div class="recent-item__title">
                  <span class="recent-item__name">{{ item.title }}</span>
                  <span class="recent-item__module">{{ item.moduleName }}</span>
                </div>
                <div class="recent-item__time">{{ formatRelativeTime(item.updated_at) }}</div>
              </div>
            </RouterLink>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ==================== 欢迎区 ==================== */
.dashboard__welcome {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  padding: var(--spacing-xl) 0;
}

.dashboard__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-3xl);
  color: var(--text-gold);
  margin: 0 0 var(--spacing-sm);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-md);
}

.title-deco-left,
.title-deco-right {
  font-size: var(--font-size-sm);
  color: var(--color-gold-primary);
  filter: drop-shadow(0 0 6px var(--color-gold-glow));
}

.dashboard__subtitle {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  letter-spacing: 4px;
  margin: 0;
}

/* ==================== 统计卡片 ==================== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, rgba(26, 35, 64, 0.8) 0%, rgba(13, 21, 37, 0.9) 100%);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  text-decoration: none;
  color: inherit;
  transition: all var(--transition-normal);
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--card-color);
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.stat-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle at top right, var(--card-glow), transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-normal);
  pointer-events: none;
}

.stat-card:hover {
  border-color: var(--card-color);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3), 0 0 20px var(--card-glow);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card:hover::after {
  opacity: 1;
}

.stat-card__icon-wrap {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--card-color);
  border-radius: var(--border-radius-md);
  background: rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.stat-card__icon {
  font-size: 26px;
  color: var(--card-color);
  filter: drop-shadow(0 0 6px var(--card-glow));
}

.stat-card__body {
  flex: 1;
  min-width: 0;
}

.stat-card__value {
  font-family: var(--font-family-display);
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-heading);
  line-height: 1.1;
}

.stat-card__label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-top: 4px;
}

.stat-card__arrow {
  color: var(--card-color);
  font-size: var(--font-size-lg);
  opacity: 0;
  transform: translateX(-8px);
  transition: all var(--transition-fast);
}

.stat-card:hover .stat-card__arrow {
  opacity: 1;
  transform: translateX(0);
}

.stat-loader {
  display: inline-block;
  width: 24px;
  height: 24px;
  border: 2px solid var(--border-color);
  border-top-color: var(--color-gold-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* ==================== 次级统计 ==================== */
.secondary-stats {
  display: flex;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
  flex-wrap: wrap;
}

.secondary-stat {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: 8px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color-light);
  border-radius: 20px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.secondary-stat:hover {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.08);
}

.secondary-stat__icon {
  font-size: 16px;
}

.secondary-stat__value {
  font-weight: 600;
  color: var(--text-heading);
}

/* ==================== 区块标题 ==================== */
.dashboard-section {
  margin-bottom: var(--spacing-xl);
}

.section-heading {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin: 0 0 var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color-light);
}

.heading-deco {
  font-size: var(--font-size-sm);
  color: var(--color-gold-primary);
}

/* ==================== 快捷操作 ==================== */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-md);
}

.quick-action {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  text-decoration: none;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.quick-action:hover {
  border-color: var(--color-gold-primary);
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.06);
  transform: translateX(4px);
}

.quick-action__icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 20px;
  color: var(--color-gold-primary);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.quick-action:hover .quick-action__icon {
  border-color: var(--color-gold-primary);
  background: rgba(212, 168, 83, 0.1);
}

.quick-action__info {
  flex: 1;
  min-width: 0;
}

.quick-action__name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.quick-action__desc {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

.quick-action__arrow {
  color: var(--text-muted);
  font-size: var(--font-size-xl);
  transition: all var(--transition-fast);
}

.quick-action:hover .quick-action__arrow {
  color: var(--text-gold);
  transform: translateX(2px);
}

/* ==================== 最近更新 ==================== */
.recent-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.recent-loading,
.recent-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-2xl);
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

.empty-icon {
  font-size: 40px;
  color: var(--color-gold-dark);
  opacity: 0.4;
}

.recent-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.recent-item {
  border-bottom: 1px solid var(--border-color-light);
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-item__link {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: 12px var(--spacing-lg);
  text-decoration: none;
  color: inherit;
  transition: background var(--transition-fast);
}

.recent-item__link:hover {
  background: rgba(212, 168, 83, 0.05);
}

.recent-item__icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 18px;
  color: var(--color-gold-primary);
  flex-shrink: 0;
}

.recent-item__content {
  flex: 1;
  min-width: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
}

.recent-item__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-width: 0;
}

.recent-item__name {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-item__module {
  flex-shrink: 0;
  padding: 1px 8px;
  border: 1px solid var(--border-color-light);
  border-radius: 10px;
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.recent-item__time {
  color: var(--text-muted);
  font-size: var(--font-size-xs);
  white-space: nowrap;
  flex-shrink: 0;
}

/* ==================== 响应式 ==================== */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .dashboard__title {
    font-size: var(--font-size-2xl);
  }

  .recent-item__content {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
