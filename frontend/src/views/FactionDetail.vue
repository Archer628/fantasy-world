<script setup>
/**
 * 族群详情 (FactionDetail) - 原神风格
 *
 * 支持两种视觉模式：
 *   - 种族详情 (race) ：绿色调左边框、血脉档案、种族渊源、血脉成员等
 *   - 势力详情 (force)：红色调左边框、组织档案、势力沿革、成员名录等
 *
 * 左侧：info-card（按模式显示差异化字段）
 * 右侧：desc-card（简介/历史/文化三张卡片，标题按模式切换）
 * 底部：关联成员列表、子势力/子种族、父势力/主族
 * 顶部有返回按钮（路由与文案按模式变化）
 */
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'
import RealmBadge from '@/components/common/RealmBadge.vue'

const route = useRoute()
const worldData = useWorldDataStore()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const faction = ref(null)
const loading = ref(true)

/** 等级配置 */
const gradeConfig = {
  S: { color: '#FF4757', gradient: 'linear-gradient(135deg, #8B0000, #FF4757)' },
  E: { color: '#FF8C00', gradient: 'linear-gradient(135deg, #CC7000, #FF8C00)' },
  A: { color: '#9B59B6', gradient: 'linear-gradient(135deg, #7B3B9E, #9B59B6)' },
  B: { color: '#4A7FBB', gradient: 'linear-gradient(135deg, #2A5B8A, #4A7FBB)' },
  C: { color: '#50C878', gradient: 'linear-gradient(135deg, #2E8B57, #50C878)' },
}

function getGradeConfig(grade) {
  const key = String(grade || '').toUpperCase()
  return gradeConfig[key] || { color: 'var(--text-muted)', gradient: 'var(--bg-card-hover)' }
}

/* =========================================================
 * 模式判断（race / force） + 兼容回退
 * ========================================================= */

/** 主模式：'race' | 'force'，优先 faction.category，否则根据名称/type 关键词猜测 */
const mode = computed(() => {
  const f = faction.value
  if (!f) return 'force'
  const cat = String(f.category || '').toLowerCase().trim()
  if (cat === 'race') return 'race'
  if (cat === 'force' || cat === 'organization' || cat === 'org') return 'force'
  // 猜测：带「族」字 → race，其余 → force
  const name = f.name || ''
  const type = f.type || ''
  if (name.includes('族') || type.includes('族') || type.includes('种族') || type.includes('血脉')) {
    return 'race'
  }
  return 'force'
})

const isRace = computed(() => mode.value === 'race')
const isForce = computed(() => mode.value === 'force')

/** 返回按钮配置 */
const backCfg = computed(() => {
  if (isRace.value) return { label: '← 返回种族百科', to: '/races' }
  if (isForce.value) return { label: '← 返回势力组织', to: '/forces' }
  return { label: '← 返回族群列表', to: '/factions' }
})

/** 标题前缀图标 */
const titleIcon = computed(() => (isRace.value ? '🧬' : '🏰'))

/** info-list 分割标题 */
const infoSectionTitle = computed(() => (isRace.value ? '血脉档案' : '组织档案'))

/** 左侧 info-card 左边框颜色变量值 */
const modeAccentColor = computed(() =>
  isRace.value ? 'var(--race-accent, #50C878)' : 'var(--force-accent, #FF4757)'
)

/* =========================================================
 * 字段兼容：从 description / ideology / traits 等中兜底提取
 * ========================================================= */

/** 从一段文本中粗略提取第一个句号/分号/换行之前的内容做短兜底 */
function shortExtract(...sources) {
  for (const s of sources) {
    if (typeof s === 'string' && s.trim()) {
      const txt = s.trim()
      const m = txt.split(/[。；;\n]/)[0]
      return (m || txt).slice(0, 60)
    }
  }
  return ''
}

/** 任意一个 truthy 就返回 */
function pickAny(...sources) {
  for (const s of sources) {
    if (s !== undefined && s !== null && s !== '') return s
  }
  return ''
}

/* ---------- 种族模式字段 ---------- */
const raceHabitat = computed(() =>
  pickAny(
    faction.value?.habitat,
    faction.value?.territory,
    faction.value?.habitat_region
  )
)
const racePopulation = computed(() =>
  pickAny(faction.value?.population, faction.value?.race_population, faction.value?.scale)
)
const racePatriarch = computed(() =>
  pickAny(
    faction.value?.patriarch,
    faction.value?.ancestor,
    faction.value?.族王,
    faction.value?.leader,
    faction.value?.始祖
  )
)
const raceTraits = computed(() =>
  pickAny(
    faction.value?.traits,
    faction.value?.bloodline_traits,
    faction.value?.血脉特征,
    shortExtract(faction.value?.description)
  )
)
const raceLifespan = computed(() =>
  pickAny(
    faction.value?.lifespan,
    faction.value?.average_lifespan,
    faction.value?.寿命,
    faction.value?.平均寿命
  )
)
const raceInnateAbilities = computed(() =>
  pickAny(
    faction.value?.innate_abilities,
    faction.value?.innate,
    faction.value?.种族天赋,
    faction.value?.talents
  )
)
const racePurity = computed(() =>
  pickAny(
    faction.value?.purity,
    faction.value?.blood_purity,
    faction.value?.血统纯度
  )
)

/* ---------- 势力模式字段 ---------- */
const forceTerritory = computed(() =>
  pickAny(faction.value?.territory, faction.value?.势力范围, faction.value?.region)
)
const forcePopulation = computed(() =>
  pickAny(faction.value?.population, faction.value?.member_count, faction.value?.成员规模)
)
const forceLeader = computed(() =>
  pickAny(
    faction.value?.leader,
    faction.value?.宗主,
    faction.value?.sect_master,
    faction.value?.首脑
  )
)
const forceIdeology = computed(() =>
  pickAny(
    faction.value?.ideology,
    faction.value?.核心理念,
    faction.value?.doctrine,
    shortExtract(faction.value?.description)
  )
)
const forceFounded = computed(() =>
  pickAny(
    faction.value?.founded,
    faction.value?.founded_year,
    faction.value?.创立年代,
    faction.value?.establish_year
  )
)
const forceAlignment = computed(() =>
  pickAny(
    faction.value?.alignment,
    faction.value?.阵营色彩,
    faction.value?.camp,
    faction.value?.阵营
  )
)
const forceRevenue = computed(() =>
  pickAny(
    faction.value?.revenue,
    faction.value?.主要收入,
    faction.value?.income_source,
    faction.value?.财源
  )
)

/* =========================================================
 * 成员列表：三字段 fallback
 * ========================================================= */
const memberList = computed(() => {
  const f = faction.value
  if (!f) return []
  if (isRace.value && Array.isArray(f.race_members) && f.race_members.length) return f.race_members
  if (isForce.value && Array.isArray(f.force_members) && f.force_members.length) return f.force_members
  if (Array.isArray(f.characters) && f.characters.length) return f.characters
  return []
})
const memberSectionTitle = computed(() =>
  isRace.value ? `血脉成员 · 共 ${memberList.value.length} 人` : `成员名录 · 共 ${memberList.value.length} 人`
)

/** 判断当前成员列表是否来自 force_members（用于显示 faction_role） */
const isForceMemberSource = computed(() => {
  const f = faction.value
  if (!f) return false
  return isForce.value && Array.isArray(f.force_members) && f.force_members.length
})

/* =========================================================
 * 子势力 / 子种族
 * ========================================================= */
const subFactions = computed(() => {
  const f = faction.value
  if (!f || !Array.isArray(f.sub_factions)) return []
  return f.sub_factions
})
const subSectionTitle = computed(() =>
  isRace.value ? `支族/亚种 · 共 ${subFactions.value.length} 支` : `分支机构 · 共 ${subFactions.value.length} 个`
)

/** 判断子条目的模式 */
function subCategory(sub) {
  const cat = String(sub?.category || '').toLowerCase().trim()
  if (cat === 'race') return 'race'
  if (cat === 'force' || cat === 'organization') return 'force'
  const name = sub?.name || ''
  if (name.includes('族')) return 'race'
  return isRace.value ? 'race' : 'force'
}
function subIcon(sub) {
  return subCategory(sub) === 'race' ? '🧬' : '🏰'
}
function subRoute(sub) {
  return subCategory(sub) === 'race' ? `/races/${sub.id}` : `/forces/${sub.id}`
}

/* =========================================================
 * 父势力 / 主族
 * ========================================================= */
const parentInfo = computed(() => {
  const f = faction.value
  if (!f) return null
  if (f.parent && typeof f.parent === 'object' && (f.parent.id || f.parent.name)) {
    const p = f.parent
    const cat = String(p.category || '').toLowerCase().trim()
    let resolved
    if (cat === 'race') resolved = 'race'
    else if (cat === 'force' || cat === 'organization') resolved = 'force'
    else resolved = isRace.value ? 'race' : 'force'
    return {
      id: p.id,
      name: p.name,
      category: resolved,
      grade: p.grade,
      type: p.type,
    }
  }
  const pid = f.parent_faction_id ?? f.parent_id ?? null
  if (pid != null) {
    // 只有 id 没有名字时，用一个兜底名
    return {
      id: pid,
      name: isRace.value ? '上位血脉' : '上级组织',
      category: isRace.value ? 'race' : 'force',
      grade: null,
    }
  }
  return null
})
const parentSectionTitle = computed(() =>
  isRace.value ? '主族/上位血脉' : '宗主势力/上级组织'
)
const parentSubLabel = computed(() => (isRace.value ? '上位血脉' : '上级组织'))
function parentRoute(p) {
  return p.category === 'race' ? `/races/${p.id}` : `/forces/${p.id}`
}

/* =========================================================
 * 角色成员卡片辅助
 * ========================================================= */
function memberRaceName(m) {
  if (!m) return '未分类'
  if (m.race_name) return m.race_name
  if (m.race && typeof m.race === 'object' && m.race.name) return m.race.name
  if (typeof m.race === 'string') return m.race
  return '未分类'
}
function memberAliases(m) {
  if (!m) return ''
  return m.aliases || m.alias || ''
}
function memberRealm(m) {
  if (!m) return ''
  return m.realm || m.realm_tier || m.get_realm_tier_display || ''
}
function memberRealmLevel(m) {
  if (!m) return ''
  return m.realm_order || m.level || m.order || ''
}
function memberInitial(m) {
  const n = m?.name || '?'
  return n.charAt(0)
}

/* =========================================================
 * 右侧 desc-card 标题按模式切换
 * ========================================================= */
const descTitleIntro = computed(() => (isRace.value ? '种族渊源' : '势力沿革'))
const descTitleHistory = computed(() => (isRace.value ? '血脉历史' : '历史背景'))
const descTitleCulture = computed(() => (isRace.value ? '文化与传统' : '组织架构'))

/** 加载族群详情 */
async function loadFaction(id) {
  loading.value = true
  faction.value = null
  try {
    const data = await worldData.loadFactionDetail(id)
    faction.value = data
  } catch (err) {
    console.error('加载族群详情失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

onMounted(() => {
  loadFaction(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadFaction(newId)
})
</script>

<template>
  <div ref="pageRef" class="page-content faction-detail">
    <!-- 返回按钮 -->
    <RouterLink :to="backCfg.to" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      {{ backCfg.label }}
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在获取族群档案...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!faction" class="empty-state">
      <div class="empty-state__icon">⚔</div>
      <p class="empty-state__text">族群档案不存在</p>
      <RouterLink :to="backCfg.to" class="btn-genshin">返回列表</RouterLink>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <!-- 左右分栏布局 -->
      <div class="detail-body">
        <!-- 左侧：信息卡 -->
        <aside ref="leftRef" class="detail-left">
          <div
            class="card card-gold info-card"
            :class="isRace ? 'info-card--race' : 'info-card--force'"
            :style="{ '--mode-accent': modeAccentColor }"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <!-- 等级徽章 -->
            <div
              class="info-card__grade"
              :style="{ '--grade-color': getGradeConfig(faction.grade).color, '--grade-gradient': getGradeConfig(faction.grade).gradient }"
            >
              {{ faction.grade || '?' }}
            </div>

            <h1 class="info-card__name">
              <span class="info-card__name-icon">{{ titleIcon }}</span>
              {{ faction.name }}
            </h1>

            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>

            <!-- 模式分割标题 -->
            <div class="info-list__section-title">{{ infoSectionTitle }}</div>

            <div class="info-list">
              <!-- grade / 类型 / 名称 之外的差异化字段 -->

              <!-- 通用：类型 -->
              <div v-if="faction.type" class="info-item">
                <span class="info-item__label">类型</span>
                <span class="info-item__value">{{ faction.type }}</span>
              </div>

              <!-- 通用：等级 -->
              <div v-if="faction.grade" class="info-item">
                <span class="info-item__label">等级</span>
                <span class="info-item__value">{{ faction.grade }}级</span>
              </div>

              <!-- ========= 种族模式专属字段 ========= -->
              <template v-if="isRace">
                <div v-if="raceHabitat" class="info-item">
                  <span class="info-item__label">栖息域</span>
                  <span class="info-item__value">{{ raceHabitat }}</span>
                </div>
                <div v-if="racePopulation" class="info-item">
                  <span class="info-item__label">种群规模</span>
                  <span class="info-item__value">{{ racePopulation }}</span>
                </div>
                <div v-if="racePatriarch" class="info-item">
                  <span class="info-item__label">族王/始祖</span>
                  <span class="info-item__value">{{ racePatriarch }}</span>
                </div>
                <div v-if="raceTraits" class="info-item info-item--multi">
                  <span class="info-item__label">血脉特征</span>
                  <span class="info-item__value">{{ raceTraits }}</span>
                </div>
                <div v-if="raceLifespan" class="info-item">
                  <span class="info-item__label">平均寿命</span>
                  <span class="info-item__value">{{ raceLifespan }}</span>
                </div>
                <div v-if="raceInnateAbilities" class="info-item info-item--multi">
                  <span class="info-item__label">种族天赋</span>
                  <span class="info-item__value">{{ raceInnateAbilities }}</span>
                </div>
                <div v-if="racePurity" class="info-item">
                  <span class="info-item__label">血统纯度</span>
                  <span class="info-item__value">{{ racePurity }}</span>
                </div>
              </template>

              <!-- ========= 势力模式专属字段 ========= -->
              <template v-else>
                <div v-if="forceTerritory" class="info-item">
                  <span class="info-item__label">势力范围</span>
                  <span class="info-item__value">{{ forceTerritory }}</span>
                </div>
                <div v-if="forcePopulation" class="info-item">
                  <span class="info-item__label">成员规模</span>
                  <span class="info-item__value">{{ forcePopulation }}</span>
                </div>
                <div v-if="forceLeader" class="info-item">
                  <span class="info-item__label">领袖/宗主</span>
                  <span class="info-item__value">{{ forceLeader }}</span>
                </div>
                <div v-if="forceIdeology" class="info-item info-item--multi">
                  <span class="info-item__label">核心理念</span>
                  <span class="info-item__value">{{ forceIdeology }}</span>
                </div>
                <div v-if="forceFounded" class="info-item">
                  <span class="info-item__label">创立年代</span>
                  <span class="info-item__value">{{ forceFounded }}</span>
                </div>
                <div v-if="forceAlignment" class="info-item">
                  <span class="info-item__label">阵营色彩</span>
                  <span class="info-item__value">{{ forceAlignment }}</span>
                </div>
                <div v-if="forceRevenue" class="info-item info-item--multi">
                  <span class="info-item__label">主要收入</span>
                  <span class="info-item__value">{{ forceRevenue }}</span>
                </div>
              </template>
            </div>
          </div>
        </aside>

        <!-- 右侧：详细描述 -->
        <main ref="rightRef" class="detail-right">
          <!-- 简介（渊源/沿革） -->
          <div class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              {{ descTitleIntro }}
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="faction.description || '暂无描述'" tag="p" />
            </div>
          </div>

          <!-- 历史（血脉历史/历史背景） -->
          <div v-if="faction.history" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              {{ descTitleHistory }}
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="faction.history" tag="p" />
            </div>
          </div>

          <!-- 文化/组织架构（文化与传统/组织架构） -->
          <div v-if="faction.culture" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              {{ descTitleCulture }}
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="faction.culture" tag="p" />
            </div>
          </div>
        </main>
      </div>

      <!-- ========== 底部 1：关联角色列表 ========== -->
      <div v-if="memberList.length" class="detail-section">
        <h2 class="section-title">{{ memberSectionTitle }}</h2>
        <div class="grid-4">
          <RouterLink
            v-for="m in memberList"
            :key="m.id"
            :to="`/characters/${m.id}`"
            class="related-card card related-card--member"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <!-- 头像或首字占位符 -->
            <div class="related-card__avatar">
              <span class="related-card__avatar-initials">{{ memberInitial(m) }}</span>
            </div>

            <h4 class="related-card__name">{{ m.name }}</h4>

            <!-- 别名小字 -->
            <p v-if="memberAliases(m)" class="related-card__alias">
              「{{ memberAliases(m) }}」
            </p>

            <!-- 标签行：种族 + 境界 -->
            <div class="related-card__tags">
              <span class="tag tag--race">
                <span class="tag__icon">🧬</span>
                <span class="tag__text">{{ memberRaceName(m) }}</span>
              </span>
              <RealmBadge
                v-if="memberRealm(m)"
                :realm="memberRealm(m)"
                :level="memberRealmLevel(m)"
              />
            </div>

            <!-- 势力身份（仅 force_members 源） -->
            <div v-if="isForceMemberSource && m.faction_role" class="related-card__role">
              {{ m.faction_role }}
            </div>
          </RouterLink>
        </div>
      </div>

      <!-- ========== 底部 2：子势力/子种族 ========== -->
      <div v-if="subFactions.length" class="detail-section">
        <h2 class="section-title">{{ subSectionTitle }}</h2>
        <div class="grid-4">
          <RouterLink
            v-for="sub in subFactions"
            :key="sub.id"
            :to="subRoute(sub)"
            class="related-card card related-card--sub"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <div class="related-card__icon related-card__icon--big">
              {{ subIcon(sub) }}
            </div>

            <h4 class="related-card__name">{{ sub.name }}</h4>

            <div v-if="sub.grade" class="related-card__grade-badge"
              :style="{
                '--grade-color': getGradeConfig(sub.grade).color,
                '--grade-gradient': getGradeConfig(sub.grade).gradient,
              }"
            >
              {{ sub.grade }}
            </div>

            <p v-if="sub.type" class="related-card__sub">{{ sub.type }}</p>
          </RouterLink>
        </div>
      </div>

      <!-- ========== 底部 3：父势力/主族 ========== -->
      <div v-if="parentInfo" class="detail-section">
        <h2 class="section-title">{{ parentSectionTitle }}</h2>
        <div class="parent-single">
          <RouterLink
            :to="parentRoute(parentInfo)"
            class="related-card card related-card--parent"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <div class="related-card__icon related-card__icon--big">
              {{ parentInfo.category === 'race' ? '🧬' : '🏰' }}
            </div>

            <h4 class="related-card__name">{{ parentInfo.name }}</h4>
            <p class="related-card__sub">{{ parentSubLabel }}</p>
          </RouterLink>
        </div>
      </div>

      <!-- 保留：关联宝物列表（旧字段兼容） -->
      <div v-if="faction.artifacts && faction.artifacts.length" class="detail-section">
        <h2 class="section-title">关联宝物</h2>
        <div class="grid-4">
          <RouterLink
            v-for="artifact in faction.artifacts"
            :key="artifact.id"
            :to="`/artifacts/${artifact.id}`"
            class="related-card card"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>
            <div class="related-card__icon">🗡</div>
            <h4 class="related-card__name">{{ artifact.name }}</h4>
            <p v-if="artifact.rarity" class="related-card__sub">{{ artifact.rarity }}</p>
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.faction-detail {
  padding-top: var(--spacing-lg);
  --race-accent: #50C878;
  --force-accent: #FF4757;
}

/* 返回按钮 */
.back-btn {
  margin-bottom: var(--spacing-lg);
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.back-btn__arrow {
  font-size: var(--font-size-lg);
}

/* 左右分栏 */
.detail-body {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

/* 左侧信息卡 */
.info-card {
  text-align: center;
  padding: var(--spacing-xl);
  position: relative;
  border-left: 4px solid var(--mode-accent, var(--color-gold-dark));
}

.info-card__grade {
  width: 60px;
  height: 60px;
  margin: 0 auto var(--spacing-md);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--grade-gradient);
  color: #fff;
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  border-radius: 50%;
  border: 3px solid var(--grade-color);
  box-shadow: 0 0 20px color-mix(in srgb, var(--grade-color) 50%, transparent);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.info-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-sm);
  letter-spacing: 2px;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.info-card__name-icon {
  font-size: var(--font-size-xl);
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.2));
}

.info-list__section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  color: var(--mode-accent, var(--color-gold-primary));
  text-align: left;
  padding: var(--spacing-xs) var(--spacing-sm);
  margin: var(--spacing-sm) 0 var(--spacing-md);
  border-bottom: 1px dashed var(--mode-accent, var(--border-color));
  letter-spacing: 2px;
}

.info-list {
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-sm);
  border-left: 2px solid var(--mode-accent, var(--color-gold-dark));
  gap: var(--spacing-sm);
}

.info-item--multi {
  align-items: flex-start;
  flex-direction: column;
  justify-content: flex-start;
}

.info-item__label {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  white-space: nowrap;
  flex-shrink: 0;
}

.info-item--multi .info-item__label {
  margin-bottom: 2px;
}

.info-item__value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  text-align: right;
  word-break: break-word;
  line-height: 1.6;
}

.info-item--multi .info-item__value {
  text-align: left;
}

/* 右侧描述 */
.detail-right {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.desc-card {
  padding: var(--spacing-xl);
}

.desc-card__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color);
}

.desc-card__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.desc-card__content {
  color: var(--text-primary);
  line-height: 2;
  font-size: var(--font-size-base);
}

/* 底部关联区域 */
.detail-section {
  margin-bottom: var(--spacing-xl);
}

.related-card {
  text-align: center;
  padding: var(--spacing-md);
  text-decoration: none;
  color: inherit;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.related-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px color-mix(in srgb, var(--color-gold-primary) 25%, transparent);
}

.related-card__icon {
  font-size: 32px;
  margin-bottom: var(--spacing-xs);
  filter: drop-shadow(0 0 8px var(--color-gold-glow));
}

.related-card__icon--big {
  font-size: 40px;
  margin: var(--spacing-xs) 0;
}

.related-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--text-heading);
  margin-bottom: 0;
}

.related-card__sub {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin: 0;
}

/* ========== 成员卡片新增样式 ========== */
.related-card--member {
  padding-bottom: var(--spacing-md);
}

.related-card__avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.25), rgba(212, 175, 55, 0.05));
  border: 2px solid var(--color-gold-dark);
  margin-bottom: var(--spacing-xs);
  box-shadow: 0 0 12px color-mix(in srgb, var(--color-gold-primary) 30%, transparent);
}

.related-card__avatar-initials {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  font-weight: 700;
}

.related-card__alias {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin: 0;
  font-style: italic;
  opacity: 0.85;
}

.related-card__tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: var(--spacing-xs);
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  line-height: 1.6;
}

.tag--race {
  background: rgba(80, 200, 120, 0.12);
  color: var(--race-accent, #50C878);
  border: 1px solid color-mix(in srgb, var(--race-accent, #50C878) 40%, transparent);
}

.tag__icon {
  font-size: 11px;
}

.tag__text {
  font-weight: 500;
}

.related-card__role {
  margin-top: auto;
  padding-top: 6px;
  border-top: 1px dashed var(--border-color);
  width: 100%;
  font-size: 11px;
  color: var(--color-gold-dark);
  font-weight: 500;
  letter-spacing: 1px;
}

/* ========== 子条目 grade 徽章 ========== */
.related-card__grade-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 22px;
  padding: 0 6px;
  font-size: 11px;
  font-weight: 700;
  color: #fff;
  background: var(--grade-gradient);
  border-radius: 4px;
  border: 1px solid var(--grade-color);
  font-family: var(--font-family-display);
  letter-spacing: 1px;
}

/* ========== 父势力单卡片 ========== */
.parent-single {
  display: flex;
  justify-content: center;
}

.parent-single .related-card {
  width: 280px;
  max-width: 100%;
}

.related-card--parent {
  background:
    linear-gradient(180deg, rgba(212, 175, 55, 0.05), transparent),
    var(--bg-card);
}

/* 加载/空状态 */
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.empty-state__icon {
  font-size: 56px;
  margin-bottom: var(--spacing-md);
  filter: drop-shadow(0 0 12px var(--color-gold-glow));
}

.empty-state__text {
  color: var(--text-muted);
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-md);
}

.genshin-loader {
  margin: 0 auto var(--spacing-md);
}

/* 响应式 */
@media (max-width: 1024px) {
  .detail-body {
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 768px) {
  .detail-body {
    grid-template-columns: 1fr;
  }
}
</style>
