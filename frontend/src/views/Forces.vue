<script setup>
/**
 * 势力/组织列表 (Forces) — 原神风格
 *
 * 只展示 Faction.category === 'force' 的条目（组织、宗门、王国、商会、公会、基地等）
 * 卡片显示：势力类型（宗门/皇朝/商会/公会/基地/骑士团…）、等级、领地/势力范围、领袖、
 *           成员规模、阵营（光明/中立/暗网）、意识形态、组织层级结构
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import { RouterLink } from 'vue-router'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)
const filterType = ref('')     // 势力类型：宗门/皇朝/商会…
const filterAlign = ref('')    // 阵营：light/neutral/dark
const filterGrade = ref('')    // 等级 S/E/A/B/C

/** 等级配置 */
const gradeConfig = {
  S: { color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)', label: 'S' },
  E: { color: '#FF8C00', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)', label: 'E' },
  A: { color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)', label: 'A' },
  B: { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)', label: 'B' },
  C: { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)', label: 'C' },
}
function getGradeConfig(grade) {
  const k = String(grade || '').toUpperCase()
  return gradeConfig[k] || { color: 'var(--text-muted)', gradient: 'var(--bg-card-hover)', label: grade || '?' }
}

/** 势力类型配色（按大类组织区分） */
function forceTypeColor(type) {
  if (!type) return 'var(--text-muted)'
  const t = String(type)
  if (/宗|门|派|教|sect|cult/i.test(t))    return '#FBBF24'   // 宗门/教派 — 金黄
  if (/皇朝|王国|帝国|国|kingdom|empire/i.test(t)) return '#EF4444' // 王国/皇朝 — 朱红
  if (/商|行|钱庄|商会|trade|merchant/i.test(t)) return '#10B981'   // 商会/财阀 — 翠绿
  if (/公|工会|协会|guild/i.test(t))        return '#3B82F6'        // 公会/协会 — 湛蓝
  if (/基地|组织|团|研究院|实验室|group/i.test(t)) return '#8B5CF6'   // 基地/组织 — 紫罗兰
  if (/骑士|军|军团|团|order|legion/i.test(t)) return '#DC2626'      // 骑士团/军团 — 赤红
  if (/家族|世家|clan|family/i.test(t))     return '#F59E0B'         // 家族/世家 — 橙金
  if (/联盟|议会|联盟|alliance|council/i.test(t)) return '#06B6D4'   // 联盟/议会 — 青碧
  if (/匪|盗|黑暗|暗|黑|shadow|dark/i.test(t)) return '#64748B'      // 暗势力 — 铁灰
  return 'var(--color-cyan-primary)'
}

/** 阵营判定（从 ideology/type/description 关键词推断） */
function alignOf(force) {
  const txt = `${force.ideology || ''} ${force.type || ''} ${force.description || ''} ${force.alignment || ''}`
  if (/光明|正义|善良|圣|光|守序|白|light|holy|just/i.test(txt)) return 'light'
  if (/暗|邪|魔|黑|恶|暗网|dark|evil|shadow/i.test(txt)) return 'dark'
  return 'neutral'
}
function alignLabel(a) { return { light: '🜲 守序·光明', neutral: '☯ 中立·平衡', dark: '☽ 混沌·暗网' }[a] || '☯ 中立' }
function alignColor(a) { return { light: '#FBBF24', neutral: '#60A5FA', dark: '#A78BFA' }[a] || '#60A5FA' }

/** 所有势力（category=force） */
const forces = computed(() => (worldData.factions || []).filter((f) => f.category === 'force'))

/** 势力类型选项 */
const forceTypeOptions = computed(() => {
  const s = new Set()
  forces.value.forEach((r) => r.type && s.add(r.type))
  return Array.from(s).sort()
})
const gradeOptions = ['S', 'E', 'A', 'B', 'C']
const alignOptions = [
  { key: 'light', label: '光明阵营' },
  { key: 'neutral', label: '中立阵营' },
  { key: 'dark', label: '暗网阵营' },
]

/** 父势力分组（多层级组织，例：天剑盟 → 天剑盟-外门 / 内门 / 执法堂） */
const parentForces = computed(() => forces.value.filter((f) => !f.parent_faction && !f.parent_id))
const childrenByParent = computed(() => {
  const m = new Map()
  forces.value.forEach((r) => {
    const pid = r.parent_faction || r.parent_id
    if (!pid) return
    if (!m.has(pid)) m.set(pid, [])
    m.get(pid).push(r)
  })
  return m
})

const filteredForces = computed(() => {
  return forces.value.filter((f) => {
    if (filterType.value && f.type !== filterType.value) return false
    if (filterGrade.value && String(f.grade || '').toUpperCase() !== filterGrade.value) return false
    if (filterAlign.value && alignOf(f) !== filterAlign.value) return false
    return true
  })
})

/** 平铺展示：父势力 → 分支势力（缩进/箭头指示从属） */
const displayList = computed(() => {
  const list = []
  const order = { S: 0, E: 1, A: 2, B: 3, C: 4 }
  const roots = filteredForces.value
    .filter((f) => !f.parent_faction && !f.parent_id)
    .sort((a, b) => {
      const ga = order[String(a.grade || '').toUpperCase()] ?? 9
      const gb = order[String(b.grade || '').toUpperCase()] ?? 9
      if (ga !== gb) return ga - gb
      return (a.name || '').localeCompare(b.name || '')
    })
  const rootIds = new Set(roots.map((r) => r.id))
  roots.forEach((f) => {
    list.push({ ...f, _level: 0, _isParent: true })
    const children = childrenByParent.value.get(f.id) || []
    children
      .sort((a, b) => (a.name || '').localeCompare(b.name || ''))
      .forEach((c) => list.push({ ...c, _level: 1, _parentName: f.name, _isParent: false }))
  })
  filteredForces.value
    .filter((f) => !rootIds.has(f.id) && !(f.parent_faction || f.parent_id))
    .forEach((f) => list.push({ ...f, _level: 0, _isParent: false }))
  filteredForces.value
    .filter((f) => (f.parent_faction || f.parent_id) && !rootIds.has(f.parent_faction || f.parent_id))
    .forEach((f) => list.push({ ...f, _level: 1, _isParent: false }))
  return list
})

onMounted(async () => {
  await worldData.loadFactions()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.force-card')
    staggerList(cards, { stagger: 0.06 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content forces-page">
    <div class="page-header">
      <div class="page-header__deco">🏰</div>
      <h1 class="page-header__title gold-shimmer-text">势力组织</h1>
      <p class="page-header__subtitle">宗门林立，列国纵横，群雄逐鹿</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
      <p class="page-header__tip">
        共 <span class="hl">{{ forces.length }}</span> 个势力组织 ·
        顶级势力 <span class="hl">{{ parentForces.length }}</span> 座
      </p>
    </div>

    <!-- 筛选组（3 维：类型 + 阵营 + 等级） -->
    <div class="filter-groups glass-panel">
      <div class="filter-group">
        <span class="filter-group__label">组织类型</span>
        <div class="filter-chips">
          <button class="chip" :class="{ 'chip--active': !filterType }" @click="filterType = ''">全部</button>
          <button
            v-for="t in forceTypeOptions" :key="t" class="chip"
            :class="{ 'chip--active': filterType === t }"
            :style="filterType === t ? { borderColor: forceTypeColor(t), color: forceTypeColor(t) } : {}"
            @click="filterType = t"
          >{{ t }}</button>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-group__label">阵营</span>
        <div class="filter-chips">
          <button class="chip" :class="{ 'chip--active': !filterAlign }" @click="filterAlign = ''">全部</button>
          <button
            v-for="a in alignOptions" :key="a.key" class="chip"
            :class="{ 'chip--active': filterAlign === a.key }"
            :style="filterAlign === a.key ? { borderColor: alignColor(a.key), color: alignColor(a.key) } : {}"
            @click="filterAlign = a.key"
          >{{ a.label }}</button>
        </div>
      </div>
      <div class="filter-group">
        <span class="filter-group__label">等级</span>
        <div class="filter-chips">
          <button class="chip" :class="{ 'chip--active': !filterGrade }" @click="filterGrade = ''">全部</button>
          <button
            v-for="g in gradeOptions" :key="g" class="chip chip--grade"
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
      <p class="empty-state__text">正在探查各方势力虚实…</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="displayList.length === 0" class="empty-state">
      <div class="empty-state__icon">🏰</div>
      <p class="empty-state__text">暂无势力数据</p>
    </div>

    <!-- 势力卡片网格 -->
    <div v-else ref="gridRef" class="grid-3 grid-forces">
      <RouterLink
        v-for="(f, idx) in displayList"
        :key="f.id + '-' + idx"
        :to="`/forces/${f.id}`"
        class="force-card card card-gold"
        :class="{ 'force-card--child': f._level > 0, 'force-card--parent': f._isParent }"
        :style="{ '--force-color': forceTypeColor(f.type), '--align-c': alignColor(alignOf(f)) }"
      >
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 阵营色条 -->
        <div class="force-card__align-bar"></div>

        <!-- 等级徽章 -->
        <div
          class="force-card__grade"
          :style="{ '--grade-color': getGradeConfig(f.grade).color, '--grade-gradient': getGradeConfig(f.grade).gradient }"
        >{{ getGradeConfig(f.grade).label }}</div>

        <!-- 分支从属指示 -->
        <div v-if="f._level > 0" class="force-card__sub">
          <span class="force-card__sub-arrow">↳</span>
          <span class="force-card__sub-parent">{{ f._parentName || '分支势力' }}</span>
        </div>

        <div class="force-card__body">
          <h3 class="force-card__name">{{ f.name }}</h3>

          <div class="force-card__badges">
            <span
              class="force-card__type"
              :style="{ color: forceTypeColor(f.type), borderColor: forceTypeColor(f.type) }"
            >{{ f.type || '未知组织' }}</span>
            <span
              class="force-card__align"
              :style="{ color: alignColor(alignOf(f)), borderColor: alignColor(alignOf(f)) }"
            >{{ alignLabel(alignOf(f)) }}</span>
            <span v-if="f._isParent" class="force-card__tag force-card__tag--parent">盟主/宗主国</span>
            <span v-else-if="f._level > 0" class="force-card__tag force-card__tag--branch">分部/分支</span>
          </div>

          <div class="force-card__info">
            <div v-if="f.territory" class="info-row">
              <span class="info-label">势力范围</span>
              <span class="info-value">{{ f.territory }}</span>
            </div>
            <div v-if="f.population" class="info-row">
              <span class="info-label">成员规模</span>
              <span class="info-value">{{ f.population }}</span>
            </div>
            <div v-if="f.leader" class="info-row">
              <span class="info-label">{{ f._level > 0 ? '主事' : '领袖/宗主' }}</span>
              <span class="info-value">{{ f.leader }}</span>
            </div>
            <div v-if="f.ideology" class="info-row info-row--full">
              <span class="info-label">核心理念</span>
              <span class="info-value">{{ f.ideology }}</span>
            </div>
          </div>

          <p v-if="f.description" class="force-card__desc">
            {{ f.description }}
          </p>
        </div>

        <div class="force-card__footer">
          <span class="force-card__arrow">进入势力档案 ›</span>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.forces-page { padding-top: var(--spacing-xl); }

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

/* 筛选 */
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
.filter-chips { display: flex; flex-wrap: wrap; gap: var(--spacing-xs); }
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
.chip:hover { color: var(--text-gold); background: rgba(212, 168, 83, 0.08); }
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

/* 势力卡片 */
.grid-forces { align-items: stretch; }
.force-card {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
}
.force-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--border-color-active);
}
.force-card--child {
  border-left: 3px solid var(--force-color, var(--color-gold-primary));
}
/* 阵营色条（卡片顶部） */
.force-card__align-bar {
  position: absolute;
  inset: 0 0 auto 0;
  height: 4px;
  background: linear-gradient(90deg, var(--align-c, #60A5FA), transparent 80%);
  z-index: 1;
}
.force-card__grade {
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
.force-card__sub {
  position: absolute;
  top: calc(var(--spacing-md) + 4px);
  left: var(--spacing-md);
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 10px;
  background: rgba(6, 11, 20, 0.7);
  border: 1px solid var(--force-color, var(--color-gold-dark));
  border-radius: var(--border-radius-sm);
  z-index: 2;
}
.force-card__sub-arrow { color: var(--text-muted); font-size: 12px; }
.force-card__sub-parent {
  font-size: var(--font-size-xs);
  color: var(--force-color, var(--color-gold-primary));
  font-weight: 500;
}
.force-card__body {
  padding: var(--spacing-lg);
  padding-top: calc(var(--spacing-lg) + 6px);
  flex: 1;
  display: flex;
  flex-direction: column;
}
.force-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-heading);
  margin-bottom: var(--spacing-sm);
  padding-right: 40px;
}
.force-card:hover .force-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}
.force-card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
  align-items: center;
}
.force-card__type, .force-card__align {
  padding: 2px 10px;
  font-size: var(--font-size-xs);
  border: 1px solid;
  border-radius: var(--border-radius-sm);
  background: rgba(13, 21, 37, 0.6);
}
.force-card__tag {
  padding: 2px 8px;
  font-size: 10px;
  border-radius: 999px;
  letter-spacing: 1px;
}
.force-card__tag--parent {
  background: rgba(239, 68, 68, 0.12);
  color: #FCA5A5;
  border: 1px solid #EF4444;
}
.force-card__tag--branch {
  background: rgba(59, 130, 246, 0.12);
  color: #93C5FD;
  border: 1px solid #3B82F6;
}
.force-card__info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 2px solid var(--force-color, var(--color-gold-dark));
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
.force-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.6;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.force-card__footer {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-top: 1px solid var(--border-color-light);
  text-align: right;
}
.force-card__arrow { font-size: var(--font-size-xs); color: var(--color-gold-dark); }
.force-card:hover .force-card__arrow { color: var(--color-gold-light); }

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
