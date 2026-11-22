<script setup>
/**
 * 种族列表 (Races) — 原神风格
 *
 * 只展示 Faction.category === 'race' 的条目（生灵的物种/血脉分类）
 * 按父-子结构分组（如：人族 → 中原人 / 北境蛮人 / 南岛土著）
 * 卡片显示：种族类型徽章、血脉特征、寿命、代表成员数量、主要栖息域
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import { RouterLink } from 'vue-router'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)
const filterType = ref('')   // 按 RACE_TYPE 大类筛选（人族/精灵族/兽人族…）
const filterGrade = ref('')  // 按等级筛选（S/E/A/B/C）

/** 等级配置 */
const gradeConfig = {
  S: { color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)', label: 'S' },
  E: { color: '#FF8C00', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)', label: 'E' },
  A: { color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)', label: 'A' },
  B: { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)', label: 'B' },
  C: { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)', label: 'C' },
}

function getGradeConfig(grade) {
  const key = String(grade || '').toUpperCase()
  return gradeConfig[key] || { color: 'var(--text-muted)', gradient: 'var(--bg-card-hover)', label: grade || '?' }
}

/** 种族类型色彩（按大类血脉区分） */
function raceTypeColor(type) {
  if (!type) return 'var(--text-muted)'
  const t = String(type)
  if (/人|human/i.test(t))    return '#F4C878'
  if (/精灵|elf/i.test(t))    return '#6EE7B7'
  if (/矮人|dwarf/i.test(t))  return '#D2915A'
  if (/兽人|orc/i.test(t))    return '#8FB56E'
  if (/牛头|半兽|beast/i.test(t)) return '#A78BFA'
  if (/龙|dragon/i.test(t))   return '#F87171'
  if (/海|鱼|人鱼|sea|fish/i.test(t)) return '#38BDF8'
  if (/魔|demon|devil/i.test(t)) return '#C084FC'
  if (/天使|angel/i.test(t))  return '#FCD34D'
  if (/亡灵|不死|undead/i.test(t)) return '#94A3B8'
  if (/妖精|fairy/i.test(t))  return '#F9A8D4'
  if (/巨人|giant/i.test(t))  return '#B45309'
  if (/侏儒|地精|gnome/i.test(t)) return '#84CC16'
  if (/虫|insect/i.test(t))   return '#65A30D'
  if (/德鲁|druid/i.test(t))  return '#10B981'
  return 'var(--color-cyan-primary)'
}

/** 所有种族（category=race） */
const allRaces = computed(() =>
  (worldData.factions || []).filter((f) => (f.category || f.type_category) === 'race' || /族$/.test(f.type || '') ? false : (f.category === 'race') || (f.category == null && /族$/.test(f.type || '')))
)
// 上面的计算写复杂了，简化：
const races = computed(() =>
  (worldData.factions || []).filter((f) => f.category === 'race')
)

/** 父种族（顶级）与子种族分组 */
const parentRaces = computed(() => races.value.filter((r) => !r.parent_faction && !r.parent_id))
const childrenByParent = computed(() => {
  const m = new Map()
  races.value.forEach((r) => {
    const pid = r.parent_faction || r.parent_id
    if (!pid) return
    if (!m.has(pid)) m.set(pid, [])
    m.get(pid).push(r)
  })
  return m
})

/** 种族大类选项（来自 RACE_TYPES） */
const raceTypeOptions = computed(() => {
  const s = new Set()
  races.value.forEach((r) => r.type && s.add(r.type))
  return Array.from(s).sort()
})

/** 等级选项 */
const gradeOptions = ['S', 'E', 'A', 'B', 'C']

/** 筛选后 */
const filteredRaces = computed(() => {
  return races.value.filter((r) => {
    if (filterType.value && r.type !== filterType.value) return false
    if (filterGrade.value && String(r.grade || '').toUpperCase() !== filterGrade.value) return false
    return true
  })
})

/** 显示列表：如果存在父-子层级，则按父→子的顺序平铺展示 */
const displayList = computed(() => {
  const list = []
  const roots = filteredRaces.value.filter((r) => !r.parent_faction && !r.parent_id)
  const rootsMap = new Set(roots.map((r) => r.id))
  // 先按 grade 排序顶级种族
  roots.sort((a, b) => {
    const order = { S: 0, E: 1, A: 2, B: 3, C: 4 }
    const ga = order[String(a.grade || '').toUpperCase()] ?? 9
    const gb = order[String(b.grade || '').toUpperCase()] ?? 9
    if (ga !== gb) return ga - gb
    return (a.name || '').localeCompare(b.name || '')
  })
  roots.forEach((r) => {
    list.push({ ...r, _level: 0, _isParent: true })
    const children = childrenByParent.value.get(r.id) || []
    children
      .sort((a, b) => (a.name || '').localeCompare(b.name || ''))
      .forEach((c) => list.push({ ...c, _level: 1, _parentName: r.name, _isParent: false }))
  })
  // 不属于任何顶级父类的种族追加到底部
  filteredRaces.value
    .filter((r) => !rootsMap.has(r.id) && !(r.parent_faction || r.parent_id))
    .forEach((r) => list.push({ ...r, _level: 0, _isParent: false }))
  filteredRaces.value
    .filter((r) => (r.parent_faction || r.parent_id) && !rootsMap.has(r.parent_faction || r.parent_id))
    .forEach((r) => list.push({ ...r, _level: 1, _isParent: false }))
  return list
})

onMounted(async () => {
  await worldData.loadFactions()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.race-card')
    staggerList(cards, { stagger: 0.06 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content races-page">
    <!-- 标题区 -->
    <div class="page-header">
      <div class="page-header__deco">🧬</div>
      <h1 class="page-header__title gold-shimmer-text">种族百科</h1>
      <p class="page-header__subtitle">万族林立，血脉各有传承</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
      <p class="page-header__tip">
        共 <span class="hl">{{ races.length }}</span> 个种族分支 ·
        顶级血脉 <span class="hl">{{ parentRaces.length }}</span> 支
      </p>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-groups glass-panel">
      <div class="filter-group">
        <span class="filter-group__label">血脉大类</span>
        <div class="filter-chips">
          <button
            class="chip" :class="{ 'chip--active': !filterType }"
            @click="filterType = ''"
          >全部</button>
          <button
            v-for="t in raceTypeOptions" :key="t"
            class="chip" :class="{ 'chip--active': filterType === t }"
            @click="filterType = t"
          >{{ t }}</button>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-group__label">等级</span>
        <div class="filter-chips">
          <button
            class="chip" :class="{ 'chip--active': !filterGrade }"
            @click="filterGrade = ''"
          >全部</button>
          <button
            v-for="g in gradeOptions" :key="g"
            class="chip chip--grade"
            :class="{ 'chip--active': filterGrade === g }"
            :style="{ '--chip-c': getGradeConfig(g).color }"
            @click="filterGrade = g"
          >{{ g }}</button>
        </div>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="worldData.factionsLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在探询万族血脉…</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="displayList.length === 0" class="empty-state">
      <div class="empty-state__icon">🧬</div>
      <p class="empty-state__text">暂无种族数据</p>
    </div>

    <!-- 卡片网格 -->
    <div v-else ref="gridRef" class="grid-3 grid-races">
      <RouterLink
        v-for="(r, idx) in displayList"
        :key="r.id + '-' + idx"
        :to="`/races/${r.id}`"
        class="race-card card card-gold"
        :class="{ 'race-card--child': r._level > 0, 'race-card--parent': r._isParent }"
        :style="{ '--race-color': raceTypeColor(r.type) }"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 等级徽章 -->
        <div
          class="race-card__grade"
          :style="{ '--grade-color': getGradeConfig(r.grade).color, '--grade-gradient': getGradeConfig(r.grade).gradient }"
        >{{ getGradeConfig(r.grade).label }}</div>

        <!-- 层级指示（子种族显示父族名） -->
        <div v-if="r._level > 0" class="race-card__sub">
          <span class="race-card__sub-arrow">↳</span>
          <span class="race-card__sub-parent">{{ r._parentName || '支族' }}</span>
        </div>

        <div class="race-card__body">
          <h3 class="race-card__name">{{ r.name }}</h3>

          <div class="race-card__badges">
            <span
              class="race-card__type"
              :style="{ color: raceTypeColor(r.type), borderColor: raceTypeColor(r.type) }"
            >{{ r.type || '未知血脉' }}</span>
            <span v-if="r._isParent" class="race-card__tag race-card__tag--parent">主族</span>
            <span v-else-if="r._level > 0" class="race-card__tag race-card__tag--branch">支族</span>
          </div>

          <div class="race-card__info">
            <div v-if="r.territory" class="info-row">
              <span class="info-label">栖息域</span>
              <span class="info-value">{{ r.territory }}</span>
            </div>
            <div v-if="r.population" class="info-row">
              <span class="info-label">种群规模</span>
              <span class="info-value">{{ r.population }}</span>
            </div>
            <div v-if="r.leader" class="info-row">
              <span class="info-label">{{ r._level > 0 ? '族长' : '族王/始祖' }}</span>
              <span class="info-value">{{ r.leader }}</span>
            </div>
            <div v-if="r.traits" class="info-row info-row--full">
              <span class="info-label">血脉特征</span>
              <span class="info-value">{{ r.traits }}</span>
            </div>
          </div>

          <p v-if="r.description" class="race-card__desc">
            {{ r.description }}
          </p>
        </div>

        <div class="race-card__footer">
          <span class="race-card__arrow">查看血脉传承 ›</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.races-page { padding-top: var(--spacing-xl); }

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}
.page-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}
.page-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}
.page-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
}
.page-header__tip {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-sm);
}
.page-header__tip .hl {
  color: var(--text-gold);
  font-weight: 600;
  font-family: var(--font-family-display);
}

/* 筛选组（双层：大类 + 等级） */
.filter-groups {
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.filter-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}
.filter-group__label {
  font-size: var(--font-size-xs);
  letter-spacing: 2px;
  color: var(--color-gold-primary);
  font-family: var(--font-family-display);
  padding: 2px 10px;
  border: 1px dashed var(--color-gold-dark);
  border-radius: var(--border-radius-sm);
  white-space: nowrap;
}
.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
}
.chip {
  padding: 4px 12px;
  font-size: var(--font-size-xs);
  border-radius: 999px;
  border: 1px solid transparent;
  background: rgba(13, 21, 37, 0.5);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}
.chip:hover {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.08);
}
.chip--active {
  background: rgba(212, 168, 83, 0.18);
  color: var(--text-gold);
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 10px var(--color-gold-glow);
}
.chip--grade.chip--active {
  background: color-mix(in srgb, var(--chip-c, var(--color-gold-primary)) 25%, transparent);
  border-color: var(--chip-c, var(--color-gold-primary));
  color: var(--chip-c, var(--text-gold));
  box-shadow: 0 0 10px color-mix(in srgb, var(--chip-c, var(--color-gold-primary)) 40%, transparent);
}

/* 种族卡片 */
.grid-races { align-items: stretch; }
.race-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  border-top: 2px solid transparent;
}
.race-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--border-color-active);
  border-top-color: var(--race-color, var(--color-gold-primary));
}
.race-card--child {
  border-left: 3px solid var(--race-color, var(--color-gold-primary));
}
.race-card__grade {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  width: 34px; height: 34px;
  display: flex; align-items: center; justify-content: center;
  background: var(--grade-gradient);
  color: #fff;
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  font-weight: 700;
  border-radius: 50%;
  border: 2px solid var(--grade-color);
  box-shadow: 0 0 12px color-mix(in srgb, var(--grade-color) 50%, transparent);
  z-index: 2;
}
.race-card__sub {
  position: absolute;
  top: var(--spacing-md);
  left: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  background: rgba(6, 11, 20, 0.7);
  border: 1px solid var(--race-color, var(--color-gold-dark));
  border-radius: var(--border-radius-sm);
  z-index: 2;
}
.race-card__sub-arrow { color: var(--text-muted); font-size: 12px; }
.race-card__sub-parent {
  font-size: var(--font-size-xs);
  color: var(--race-color, var(--color-gold-primary));
  font-weight: 500;
}
.race-card__body {
  padding: var(--spacing-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
}
.race-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-heading);
  margin-bottom: var(--spacing-sm);
  padding-right: 40px;
}
.race-card:hover .race-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}
.race-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  align-items: center;
}
.race-card__type {
  padding: 2px 10px;
  font-size: var(--font-size-xs);
  border: 1px solid;
  border-radius: var(--border-radius-sm);
  background: rgba(13, 21, 37, 0.6);
}
.race-card__tag {
  padding: 2px 8px;
  font-size: 10px;
  border-radius: 999px;
  letter-spacing: 1px;
}
.race-card__tag--parent {
  background: rgba(212, 168, 83, 0.15);
  color: var(--text-gold);
  border: 1px solid var(--color-gold-primary);
}
.race-card__tag--branch {
  background: rgba(56, 189, 248, 0.12);
  color: #7DD3FC;
  border: 1px solid #38BDF8;
}
.race-card__info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 2px solid var(--race-color, var(--color-gold-dark));
}
.info-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  gap: var(--spacing-xs);
}
.info-row--full { flex-direction: column; align-items: flex-start; }
.info-row--full .info-value { margin-top: 2px; line-height: 1.5; }
.info-label { color: var(--text-muted); flex-shrink: 0; }
.info-value { color: var(--text-primary); font-weight: 500; }
.race-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.race-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}
.race-card__arrow {
  font-size: var(--font-size-xs);
  color: var(--color-gold-dark);
}
.race-card:hover .race-card__arrow { color: var(--color-gold-light); }

/* 加载/空 */
.empty-state { text-align: center; padding: var(--spacing-2xl); }
.empty-state__icon { font-size: 56px; margin-bottom: var(--spacing-md); filter: drop-shadow(0 0 12px var(--color-gold-glow)); }
.empty-state__text { color: var(--text-muted); font-size: var(--font-size-lg); }
.genshin-loader { margin: 0 auto var(--spacing-md); }

@media (max-width: 768px) {
  .page-header__title { font-size: var(--font-size-3xl); }
  .filter-group { flex-direction: column; align-items: flex-start; }
}
</style>
