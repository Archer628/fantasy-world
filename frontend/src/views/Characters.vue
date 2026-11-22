<script setup>
/**
 * 角色列表 (Characters) - 原神风格
 *
 * 卡片网格布局，每张卡片展示一个角色
 * - 角色名、别名、种族+势力双标签（带图标/配色/跳转）、境界（RealmBadge）、状态
 * - 境界用原神风格的彩色徽章
 * - 悬停时卡片发光上浮
 * - 支持 种族 / 势力 / 境界 / 状态 四维 AND 筛选
 */
import { ref, computed, onMounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import RealmBadge from '@/components/common/RealmBadge.vue'

const worldData = useWorldDataStore()
const { fadeInUp, staggerList } = useAnimations()

const pageRef = ref(null)
const gridRef = ref(null)

/* -------------------- 四维筛选 ref -------------------- */
const filterRace = ref('')
const filterFaction = ref('')
const filterRealm = ref('')
const filterStatus = ref('')

/* -------------------- 重置筛选 -------------------- */
function resetFilters() {
  filterRace.value = ''
  filterFaction.value = ''
  filterRealm.value = ''
  filterStatus.value = ''
}

/* -------------------- 字段兼容辅助 -------------------- */
function getRaceName(c) {
  if (!c) return ''
  if (c.race && typeof c.race === 'object' && c.race.name) return c.race.name
  if (c.race_name) return c.race_name
  if (typeof c.race === 'string') return c.race
  return ''
}

function getRaceId(c) {
  return c?.race && typeof c.race === 'object' ? c.race.id : null
}

function getFactionName(c) {
  if (!c) return ''
  if (c.faction && typeof c.faction === 'object' && c.faction.name) return c.faction.name
  if (c.faction_name) return c.faction_name
  if (typeof c.faction === 'string') return c.faction
  return ''
}

function getFactionId(c) {
  return c?.faction && typeof c.faction === 'object' ? c.faction.id : null
}

function getRealmDisplay(c) {
  if (!c) return ''
  return c.realm || c.get_realm_tier_display || ''
}

/* -------------------- 状态颜色 -------------------- */
function statusColor(status) {
  if (!status) return 'var(--text-muted)'
  const s = String(status).toLowerCase()
  if (s.includes('活跃') || s.includes('alive') || s.includes('active')) return 'var(--color-success)'
  if (s.includes('死亡') || s.includes('dead') || s.includes('deceased')) return 'var(--color-danger)'
  if (s.includes('沉睡') || s.includes('sleep') || s.includes('封印') || s.includes('seal')) return 'var(--text-muted)'
  if (s.includes('失踪') || s.includes('missing') || s.includes('unknown')) return 'var(--color-warning)'
  return 'var(--color-cyan-primary)'
}

/* -------------------- 种族标签颜色（按关键词匹配） -------------------- */
function raceColor(name) {
  if (!name) return { bg: 'rgba(150,150,150,0.1)', border: 'rgba(150,150,150,0.3)', text: 'var(--text-muted)' }
  const n = String(name)
  // 人类
  if (/人|human|人族/i.test(n)) return { bg: 'rgba(212,168,83,0.12)', border: 'rgba(212,168,83,0.4)', text: 'var(--color-gold-light)' }
  // 精灵
  if (/精灵|elf|艾尔/i.test(n)) return { bg: 'rgba(82,196,26,0.12)', border: 'rgba(82,196,26,0.4)', text: '#7ed957' }
  // 矮人
  if (/矮人|dwarf/i.test(n)) return { bg: 'rgba(190,120,60,0.12)', border: 'rgba(190,120,60,0.4)', text: '#d4965a' }
  // 龙族
  if (/龙|dragon|draco/i.test(n)) return { bg: 'rgba(163,113,247,0.12)', border: 'rgba(163,113,247,0.4)', text: '#c39bff' }
  // 妖族
  if (/妖|demon|monster/i.test(n)) return { bg: 'rgba(255,105,180,0.12)', border: 'rgba(255,105,180,0.4)', text: '#ff8bc4' }
  // 魔族 / 恶魔
  if (/魔|dark|evil|mage/i.test(n)) return { bg: 'rgba(220,70,70,0.12)', border: 'rgba(220,70,70,0.4)', text: '#ff7878' }
  // 神族
  if (/神|god|deity|divine/i.test(n)) return { bg: 'rgba(0,212,170,0.12)', border: 'rgba(0,212,170,0.4)', text: 'var(--color-cyan-primary)' }
  // 兽族
  if (/兽|beast|兽人/i.test(n)) return { bg: 'rgba(255,150,50,0.12)', border: 'rgba(255,150,50,0.4)', text: '#ffb066' }
  // 鬼族
  if (/鬼|ghost|undead|skeleton/i.test(n)) return { bg: 'rgba(120,80,180,0.12)', border: 'rgba(120,80,180,0.4)', text: '#b088e0' }
  // 仙
  if (/仙|immortal|celestial/i.test(n)) return { bg: 'rgba(0,180,180,0.12)', border: 'rgba(0,180,180,0.4)', text: '#5fd0d0' }
  // 默认
  return { bg: 'rgba(150,170,200,0.1)', border: 'rgba(150,170,200,0.3)', text: '#aab8d0' }
}

/* -------------------- 势力标签颜色（按组织类型匹配） -------------------- */
function factionColor(c) {
  const name = getFactionName(c)
  const type = (c?.faction && typeof c.faction === 'object') ? (c.faction.type || c.faction.category || '') : ''
  const mix = (name + ' ' + type).toLowerCase()

  if (!name) return { bg: 'rgba(150,150,150,0.1)', border: 'rgba(150,150,150,0.3)', text: 'var(--text-muted)' }
  // 宗门 / 门派 / 学院
  if (/宗门|门派|学院|派|阁|谷|宗|school|sect|academy/.test(mix))
    return { bg: 'rgba(163,113,247,0.12)', border: 'rgba(163,113,247,0.4)', text: '#c39bff' }
  // 帝国 / 王朝 / 王国
  if (/帝国|王朝|王国|皇|朝|empire|kingdom|dynasty|royal/.test(mix))
    return { bg: 'rgba(212,168,83,0.12)', border: 'rgba(212,168,83,0.4)', text: 'var(--color-gold-light)' }
  // 商会 / 商行
  if (/商会|商行|商|trade|merchant|guild|commerce/.test(mix))
    return { bg: 'rgba(230,170,80,0.12)', border: 'rgba(230,170,80,0.4)', text: '#f0c070' }
  // 教会 / 教廷
  if (/教会|教廷|教|圣殿|church|temple|holy|faith/.test(mix))
    return { bg: 'rgba(230,230,250,0.12)', border: 'rgba(200,200,230,0.4)', text: '#e0e0f5' }
  // 家族
  if (/家族|家|族|family|clan|house/.test(mix))
    return { bg: 'rgba(190,90,80,0.12)', border: 'rgba(190,90,80,0.4)', text: '#e08878' }
  // 佣兵团 / 军团 / 军队
  if (/佣兵团|军团|军队|军|兵团|army|legion|mercenary|military|order/.test(mix))
    return { bg: 'rgba(220,60,60,0.12)', border: 'rgba(220,60,60,0.4)', text: '#ff7070' }
  // 组织 / 协会
  if (/组织|协会|联盟|同盟|association|union|league|alliance|org/.test(mix))
    return { bg: 'rgba(0,212,170,0.12)', border: 'rgba(0,212,170,0.4)', text: 'var(--color-cyan-primary)' }
  // 默认
  return { bg: 'rgba(80,150,230,0.12)', border: 'rgba(80,150,230,0.4)', text: '#7ab0f0' }
}

/* -------------------- 统计 -------------------- */
const stats = computed(() => {
  const list = worldData.characters || []
  const raceSet = new Set()
  const factionSet = new Set()
  list.forEach((c) => {
    const r = getRaceName(c)
    const f = getFactionName(c)
    if (r) raceSet.add(r)
    if (f) factionSet.add(f)
  })
  return {
    total: list.length,
    races: raceSet.size,
    factions: factionSet.size,
  }
})

/* -------------------- 筛选选项（去重） -------------------- */
const raceOptions = computed(() => {
  const set = new Set()
  worldData.characters.forEach((c) => {
    const r = getRaceName(c)
    if (r) set.add(r)
  })
  return Array.from(set).sort()
})

const factionOptions = computed(() => {
  const set = new Set()
  worldData.characters.forEach((c) => {
    const f = getFactionName(c)
    if (f) set.add(f)
  })
  return Array.from(set).sort()
})

const realmOptions = computed(() => {
  // 优先按用户指定的顺序展示，再追加数据里实际出现过的其他值
  const preferred = ['凡境', '灵境', '天境', '圣境']
  const set = new Set()
  worldData.characters.forEach((c) => {
    const r = getRealmDisplay(c)
    if (r) set.add(r)
  })
  const ordered = preferred.filter((p) => set.has(p))
  const extras = Array.from(set).filter((v) => !preferred.includes(v))
  return [...ordered, ...extras]
})

const statusOptions = computed(() => {
  const set = new Set()
  worldData.characters.forEach((c) => {
    if (c.status) set.add(c.status)
  })
  return Array.from(set).sort()
})

/* -------------------- 四维 AND 筛选 -------------------- */
const filteredCharacters = computed(() => {
  return worldData.characters.filter((c) => {
    if (filterRace.value && getRaceName(c) !== filterRace.value) return false
    if (filterFaction.value && getFactionName(c) !== filterFaction.value) return false
    if (filterRealm.value && getRealmDisplay(c) !== filterRealm.value) return false
    if (filterStatus.value && c.status !== filterStatus.value) return false
    return true
  })
})

/* -------------------- 是否有任一筛选激活（用于重置按钮高亮） -------------------- */
const hasActiveFilter = computed(() => {
  return filterRace.value || filterFaction.value || filterRealm.value || filterStatus.value
})

onMounted(async () => {
  await worldData.loadCharacters()
  if (pageRef.value) fadeInUp(pageRef.value)
  await nextTick()
  if (gridRef.value) {
    const cards = gridRef.value.querySelectorAll('.char-card')
    staggerList(cards, { stagger: 0.08 })
  }
})
</script>

<template>
  <div ref="pageRef" class="page-content characters-page">
    <!-- 标题区域 -->
    <div class="chars-header">
      <div class="chars-header__deco">👤</div>
      <h1 class="chars-header__title gold-shimmer-text">群英谱 / 英雄角色</h1>
      <p class="chars-header__subtitle">生而不同，各有所长</p>
      <div class="ornate-divider">
        <span class="ornate-divider__diamond"></span>
      </div>
      <!-- 统计信息 -->
      <div class="chars-header__stats">
        <span class="stats-item">
          <span class="stats-num gold-shimmer-text">{{ stats.total }}</span>
          <span class="stats-label">总角色</span>
        </span>
        <span class="stats-sep">·</span>
        <span class="stats-item">
          <span class="stats-num" style="color:#7ed957">{{ stats.races }}</span>
          <span class="stats-label">个种族</span>
        </span>
        <span class="stats-sep">·</span>
        <span class="stats-item">
          <span class="stats-num" style="color:#c39bff">{{ stats.factions }}</span>
          <span class="stats-label">个势力</span>
        </span>
      </div>
    </div>

    <!-- 四维筛选栏 -->
    <div
      v-if="raceOptions.length + factionOptions.length + realmOptions.length + statusOptions.length > 0"
      class="filter-panel glass-panel"
    >
      <!-- 重置筛选按钮 -->
      <div class="filter-panel__header">
        <span class="filter-panel__title">筛选条件</span>
        <button
          class="filter-reset"
          :class="{ 'filter-reset--active': hasActiveFilter }"
          @click="resetFilters"
        >
          <span class="filter-reset__icon">↺</span>
          重置筛选
        </button>
      </div>

      <!-- A. 种族 -->
      <div class="filter-group">
        <div class="filter-group__label">🧬 种族</div>
        <div class="filter-group__chips">
          <button
            class="chip"
            :class="{ 'chip--active': !filterRace }"
            @click="filterRace = ''"
          >
            全部
          </button>
          <button
            v-for="opt in raceOptions"
            :key="'r-'+opt"
            class="chip"
            :class="{ 'chip--active': filterRace === opt }"
            @click="filterRace = filterRace === opt ? '' : opt"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- B. 势力 -->
      <div class="filter-group">
        <div class="filter-group__label">🏰 势力</div>
        <div class="filter-group__chips">
          <button
            class="chip"
            :class="{ 'chip--active': !filterFaction }"
            @click="filterFaction = ''"
          >
            全部
          </button>
          <button
            v-for="opt in factionOptions"
            :key="'f-'+opt"
            class="chip"
            :class="{ 'chip--active': filterFaction === opt }"
            @click="filterFaction = filterFaction === opt ? '' : opt"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- C. 境界 -->
      <div class="filter-group">
        <div class="filter-group__label">✨ 境界</div>
        <div class="filter-group__chips">
          <button
            class="chip"
            :class="{ 'chip--active': !filterRealm }"
            @click="filterRealm = ''"
          >
            全部
          </button>
          <button
            v-for="opt in realmOptions"
            :key="'rl-'+opt"
            class="chip"
            :class="{ 'chip--active': filterRealm === opt }"
            @click="filterRealm = filterRealm === opt ? '' : opt"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- D. 状态 -->
      <div class="filter-group">
        <div class="filter-group__label">💠 状态</div>
        <div class="filter-group__chips">
          <button
            class="chip"
            :class="{ 'chip--active': !filterStatus }"
            @click="filterStatus = ''"
          >
            全部
          </button>
          <button
            v-for="opt in statusOptions"
            :key="'s-'+opt"
            class="chip"
            :class="{ 'chip--active': filterStatus === opt }"
            @click="filterStatus = filterStatus === opt ? '' : opt"
          >
            {{ opt }}
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="worldData.charactersLoading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在搜集英雄信息...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="filteredCharacters.length === 0" class="empty-state">
      <div class="empty-state__icon">👤</div>
      <p class="empty-state__text">暂无符合条件的角色</p>
    </div>

    <!-- 角色卡片网格 -->
    <div v-else ref="gridRef" class="grid-3">
      <RouterLink
        v-for="character in filteredCharacters"
        :key="character.id"
        :to="`/characters/${character.id}`"
        class="char-card card card-gold"
      >
        <!-- 四角装饰 -->
        <span class="ornate-corner ornate-corner--tl"></span>
        <span class="ornate-corner ornate-corner--tr"></span>
        <span class="ornate-corner ornate-corner--bl"></span>
        <span class="ornate-corner ornate-corner--br"></span>

        <!-- 头像区 -->
        <div class="char-card__avatar">
          <img v-if="character.image" :src="character.image" :alt="character.name" loading="lazy" />
          <div v-else class="char-card__avatar-placeholder">
            {{ character.name ? character.name[0] : '?' }}
          </div>
          <div class="char-card__avatar-overlay"></div>
        </div>

        <!-- 卡片内容 -->
        <div class="char-card__body">
          <div class="char-card__header">
            <h3 class="char-card__name">{{ character.name }}</h3>
            <span
              v-if="character.status"
              class="char-card__status"
              :style="{ color: statusColor(character.status), borderColor: statusColor(character.status) }"
            >
              {{ character.status }}
            </span>
          </div>

          <p v-if="character.aliases || character.alias" class="char-card__alias">
            「{{ character.aliases || character.alias }}」
          </p>

          <!-- 双标签：种族 + 势力 -->
          <div class="char-card__tags">
            <!-- 种族标签（🧬） -->
            <RouterLink
              v-if="getRaceId(character)"
              :to="`/races/${getRaceId(character)}`"
              class="tag-chip tag-chip--race"
              :style="{
                background: raceColor(getRaceName(character)).bg,
                borderColor: raceColor(getRaceName(character)).border,
                color: raceColor(getRaceName(character)).text,
              }"
              @click.stop
            >
              <span class="tag-chip__icon">🧬</span>
              {{ getRaceName(character) }}
            </RouterLink>
            <span
              v-else-if="getRaceName(character)"
              class="tag-chip tag-chip--race"
              :style="{
                background: raceColor(getRaceName(character)).bg,
                borderColor: raceColor(getRaceName(character)).border,
                color: raceColor(getRaceName(character)).text,
              }"
            >
              <span class="tag-chip__icon">🧬</span>
              {{ getRaceName(character) }}
            </span>

            <!-- 势力标签（🏰） -->
            <RouterLink
              v-if="getFactionId(character)"
              :to="`/forces/${getFactionId(character)}`"
              class="tag-chip tag-chip--faction"
              :style="{
                background: factionColor(character).bg,
                borderColor: factionColor(character).border,
                color: factionColor(character).text,
              }"
              @click.stop
            >
              <span class="tag-chip__icon">🏰</span>
              {{ getFactionName(character) }}
            </RouterLink>
            <span
              v-else-if="getFactionName(character)"
              class="tag-chip tag-chip--faction"
              :style="{
                background: factionColor(character).bg,
                borderColor: factionColor(character).border,
                color: factionColor(character).text,
              }"
            >
              <span class="tag-chip__icon">🏰</span>
              {{ getFactionName(character) }}
            </span>
          </div>

          <!-- 境界徽章 -->
          <div class="char-card__realm-row">
            <RealmBadge
              v-if="getRealmDisplay(character)"
              :realm="character.realm || getRealmDisplay(character)"
              :level="character.realm_level"
            />
          </div>

          <p v-if="character.description" class="char-card__desc">
            {{ character.description }}
          </p>

          <!-- 势力身份（卡片底部） -->
          <div v-if="character.faction_role" class="char-card__role">
            <span class="char-card__role-label">势力身份：</span>
            <span class="char-card__role-value">{{ character.faction_role }}</span>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.characters-page {
  padding-top: var(--spacing-xl);
}

/* ========== 标题 ========== */
.chars-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.chars-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.chars-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 6px;
  margin-bottom: var(--spacing-xs);
}

.chars-header__subtitle {
  color: var(--text-secondary);
  font-size: var(--font-size-lg);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-md);
}

/* 统计 */
.chars-header__stats {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-lg);
  margin-top: var(--spacing-sm);
  background: rgba(13, 21, 37, 0.5);
  border: 1px solid rgba(212, 168, 83, 0.2);
  border-radius: var(--border-radius-md);
  backdrop-filter: blur(6px);
}

.stats-item {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
}

.stats-num {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  font-weight: 700;
}

.stats-label {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  letter-spacing: 1px;
}

.stats-sep {
  color: var(--text-muted);
  opacity: 0.5;
}

/* ========== 筛选面板 ========== */
.filter-panel {
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.filter-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: var(--spacing-xs);
  border-bottom: 1px solid rgba(212, 168, 83, 0.15);
  margin-bottom: var(--spacing-xs);
}

.filter-panel__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  color: var(--text-gold);
  letter-spacing: 2px;
}

.filter-reset {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(150, 150, 150, 0.2);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}

.filter-reset:hover {
  color: var(--color-danger);
  border-color: var(--color-danger);
  background: rgba(220, 70, 70, 0.08);
}

.filter-reset--active {
  color: var(--text-gold);
  border-color: var(--color-gold-primary);
  background: rgba(212, 168, 83, 0.1);
}

.filter-reset__icon {
  font-size: 14px;
}

/* 筛选组（垂直堆叠） */
.filter-group {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: 4px 0;
}

.filter-group__label {
  flex-shrink: 0;
  width: 80px;
  padding-top: 4px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  letter-spacing: 1px;
}

.filter-group__chips {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 4px 12px;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(150, 160, 180, 0.2);
  border-radius: 999px;
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
  white-space: nowrap;
}

.chip:hover {
  color: var(--text-gold);
  border-color: rgba(212, 168, 83, 0.4);
  background: rgba(212, 168, 83, 0.06);
}

.chip--active {
  background: rgba(212, 168, 83, 0.16);
  color: var(--text-gold);
  border-color: var(--color-gold-primary);
  box-shadow: 0 0 10px var(--color-gold-glow);
}

/* ========== 角色卡片 ========== */
.char-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  padding: 0;
  overflow: hidden;
  position: relative;
}

.char-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 0 30px var(--color-gold-glow), 0 8px 32px rgba(0, 0, 0, 0.5);
  border-color: var(--border-color-active);
}

/* 头像 */
.char-card__avatar {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(26, 35, 64, 0.6), rgba(13, 21, 37, 0.8));
}

.char-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.char-card:hover .char-card__avatar img {
  transform: scale(1.08);
}

.char-card__avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-family-display);
  font-size: 64px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 20px var(--color-gold-glow);
}

.char-card__avatar-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(6, 11, 20, 0.8) 100%);
  pointer-events: none;
}

/* 卡片内容 */
.char-card__body {
  padding: var(--spacing-md);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.char-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-xs);
}

.char-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-heading);
  transition: color var(--transition-fast);
}

.char-card:hover .char-card__name {
  color: var(--color-gold-light);
  text-shadow: 0 0 8px var(--color-gold-glow);
}

.char-card__status {
  padding: 2px 8px;
  font-size: var(--font-size-xs);
  border: 1px solid;
  border-radius: var(--border-radius-sm);
  background: rgba(13, 21, 37, 0.6);
  white-space: nowrap;
  flex-shrink: 0;
}

.char-card__alias {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  font-style: italic;
  margin-bottom: var(--spacing-sm);
}

/* 双标签 */
.char-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  font-size: var(--font-size-xs);
  border: 1px solid;
  border-radius: var(--border-radius-sm);
  text-decoration: none;
  transition: all var(--transition-fast);
  line-height: 1.4;
}

.tag-chip:hover {
  filter: brightness(1.2);
  transform: translateY(-1px);
}

.tag-chip__icon {
  font-size: 12px;
  line-height: 1;
}

/* 境界徽章行 */
.char-card__realm-row {
  margin-bottom: var(--spacing-sm);
}

.char-card__desc {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 势力身份（底部） */
.char-card__role {
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px dashed rgba(212, 168, 83, 0.2);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.char-card__role-label {
  color: var(--text-muted);
}

.char-card__role-value {
  color: var(--color-cyan-primary);
  font-weight: 500;
}

/* ========== 加载/空状态 ========== */
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
}

.genshin-loader {
  margin: 0 auto var(--spacing-md);
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .chars-header__title {
    font-size: var(--font-size-3xl);
    letter-spacing: 3px;
  }

  .filter-group {
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .filter-group__label {
    width: auto;
    padding-top: 0;
  }

  .chars-header__stats {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
