<script setup>
/**
 * 角色详情 (CharacterDetail) - 原神风格
 *
 * 左侧：角色信息卡（名称、别名、6项基础资料、外貌描述）
 * 右侧：角色简介、性格特征、成长轨迹时间线、能力技能
 * 底部：持有宝物、关联种族、关联势力
 * 顶部有返回按钮
 */
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'
import RealmBadge from '@/components/common/RealmBadge.vue'
import RarityBadge from '@/components/common/RarityBadge.vue'

const route = useRoute()
const worldData = useWorldDataStore()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const character = ref(null)
const loading = ref(true)

/* ===================== 境界 tier 映射 ===================== */
const REALM_TIER_CN = {
  mortal: '凡境',
  spirit: '灵境',
  heaven: '天境',
  sage: '圣境'
}
const REALM_TIER_COLOR = {
  mortal: '#10B981', // 凡境 - 绿
  spirit: '#3B82F6', // 灵境 - 蓝
  heaven: '#A855F7', // 天境 - 紫
  sage: '#F59E0B'    // 圣境 - 金
}
const REALM_NAME_COLOR = {
  '凡境': '#10B981',
  '灵境': '#3B82F6',
  '天境': '#A855F7',
  '圣境': '#F59E0B'
}

/** 境界 tier 转中文 */
function tierToCN(tier) {
  if (!tier) return ''
  return REALM_TIER_CN[String(tier).toLowerCase()] || tier
}

/** 取境界颜色（支持 tier 或 中文名称） */
function getRealmColor(tierOrName) {
  if (!tierOrName) return REALM_TIER_COLOR.mortal
  const key = String(tierOrName).toLowerCase()
  if (REALM_TIER_COLOR[key]) return REALM_TIER_COLOR[key]
  if (REALM_NAME_COLOR[tierOrName]) return REALM_NAME_COLOR[tierOrName]
  return REALM_TIER_COLOR.mortal
}

/* ===================== 状态颜色 ===================== */
function statusColor(status) {
  if (!status) return 'var(--text-muted)'
  const s = String(status).toLowerCase()
  if (s.includes('活跃') || s.includes('alive') || s.includes('active')) return 'var(--color-success)'
  if (s.includes('死亡') || s.includes('dead') || s.includes('deceased')) return 'var(--color-danger)'
  if (s.includes('沉睡') || s.includes('sleep') || s.includes('unknown') || s.includes('封印')) return 'var(--text-muted)'
  if (s.includes('失踪') || s.includes('missing')) return 'var(--color-warning)'
  return 'var(--color-cyan-primary)'
}

/* ===================== 数据解析辅助 ===================== */

/**
 * 解析 race：优先对象 -> race_name -> 原字符串
 * 返回 { id?, name, type?, category?, grade? }
 */
const raceInfo = computed(() => {
  if (!character.value) return null
  const c = character.value
  // 情形 1：character.race 是对象 {id, name, type, ...}
  if (c.race && typeof c.race === 'object' && !Array.isArray(c.race)) {
    return {
      id: c.race.id,
      name: c.race.name || c.race_name || '未知',
      type: c.race.type,
      category: c.race.category,
      grade: c.race.grade
    }
  }
  // 情形 2：独立字段
  if (c.race_name || c.race) {
    return {
      name: c.race_name || (typeof c.race === 'string' ? c.race : '未知')
    }
  }
  return null
})

/**
 * 解析 faction：优先对象 -> faction_name -> 原字符串
 */
const factionInfo = computed(() => {
  if (!character.value) return null
  const c = character.value
  if (c.faction && typeof c.faction === 'object' && !Array.isArray(c.faction)) {
    return {
      id: c.faction.id,
      name: c.faction.name || c.faction_name || '无'
    }
  }
  if (c.faction_name || c.faction) {
    return {
      name: c.faction_name || (typeof c.faction === 'string' ? c.faction : '无')
    }
  }
  return null
})

/** faction_role 字段 */
const factionRole = computed(() => {
  if (!character.value) return ''
  return character.value.faction_role || ''
})

/** 境界 level（兼容 realm_level / realm_order） */
const realmLevel = computed(() => {
  if (!character.value) return null
  const c = character.value
  const lv = c.realm_level != null ? c.realm_level : c.realm_order
  return lv != null ? Number(lv) : null
})

/** 境界中文（realm 直接中文 或 realm_tier 映射） */
const realmCN = computed(() => {
  if (!character.value) return ''
  const c = character.value
  if (c.realm && REALM_NAME_COLOR[c.realm]) return c.realm
  if (c.realm) return c.realm
  return tierToCN(c.realm_tier)
})

/** 境界下方副标题（凡境 · 1阶） */
const realmSubtitle = computed(() => {
  const cn = realmCN.value || tierToCN(character.value?.realm_tier)
  const lv = realmLevel.value
  if (!cn && lv == null) return ''
  const parts = []
  if (cn) parts.push(cn)
  if (lv != null) parts.push(lv + '阶')
  return parts.join(' · ')
})

/** 将数组或逗号分隔字符串转成数组 */
function parseList(v) {
  if (v == null || v === '') return []
  if (Array.isArray(v)) return v.filter(x => x != null && x !== '')
  if (typeof v === 'string') {
    return v.split(/[,，、;；]/).map(s => s.trim()).filter(s => s.length)
  }
  return [String(v)]
}

/** 成长轨迹：非空数组 */
const powerProgression = computed(() => {
  if (!character.value) return []
  const arr = character.value.power_progression
  if (!Array.isArray(arr) || arr.length === 0) return []
  return arr
})

/* ===================== 加载 ===================== */
async function loadCharacter(id) {
  loading.value = true
  character.value = null
  try {
    const data = await worldData.loadCharacterDetail(id)
    character.value = data
  } catch (err) {
    console.error('加载角色详情失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

onMounted(() => {
  loadCharacter(route.params.id)
})

watch(() => route.params.id, (newId) => {
  if (newId) loadCharacter(newId)
})
</script>

<template>
  <div ref="pageRef" class="page-content char-detail">
    <!-- 返回按钮 -->
    <RouterLink to="/characters" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      返回角色列表
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在获取角色档案...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!character" class="empty-state">
      <div class="empty-state__icon">👤</div>
      <p class="empty-state__text">角色档案不存在</p>
      <RouterLink to="/characters" class="btn-genshin">返回列表</RouterLink>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <!-- 左右分栏布局 -->
      <div class="detail-body">
        <!-- ============ 左侧：角色信息卡 ============ -->
        <aside ref="leftRef" class="detail-left">
          <div class="card card-gold info-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <!-- 头像 -->
            <div class="info-card__avatar">
              <img v-if="character.image" :src="character.image" :alt="character.name" />
              <div v-else class="info-card__avatar-placeholder">
                {{ character.name ? character.name[0] : '?' }}
              </div>
            </div>

            <h1 class="info-card__name">{{ character.name }}</h1>
            <p v-if="character.aliases || character.alias" class="info-card__alias">
              「{{ character.aliases || character.alias }}」
            </p>

            <div class="ornate-divider">
              <span class="ornate-divider__diamond"></span>
            </div>

            <!-- info-list：6 项基础资料 -->
            <h4 class="info-list__section-title">基础资料</h4>
            <div class="info-list">
              <!-- A. 所属种族 🧬 -->
              <div v-if="raceInfo" class="info-item">
                <span class="info-item__label">🧬 所属种族</span>
                <span class="info-item__value-wrap">
                  <RouterLink
                    v-if="raceInfo.id"
                    :to="`/races/${raceInfo.id}`"
                    class="info-item__link"
                  >
                    {{ raceInfo.name }}
                  </RouterLink>
                  <span v-else class="info-item__value">{{ raceInfo.name }}</span>
                  <span v-if="raceInfo.type" class="info-item__sub">（{{ raceInfo.type }}血脉）</span>
                </span>
              </div>

              <!-- B. 所属势力 🏰 -->
              <div v-if="factionInfo" class="info-item">
                <span class="info-item__label">🏰 所属势力</span>
                <span class="info-item__value-wrap">
                  <RouterLink
                    v-if="factionInfo.id"
                    :to="`/forces/${factionInfo.id}`"
                    class="info-item__link"
                  >
                    {{ factionInfo.name }}
                  </RouterLink>
                  <span v-else class="info-item__value">{{ factionInfo.name }}</span>
                </span>
              </div>

              <!-- C. 势力身份 ⚔ -->
              <div class="info-item">
                <span class="info-item__label">⚔ 势力身份</span>
                <span v-if="factionRole" class="info-item__value">{{ factionRole }}</span>
                <span v-else class="info-item__value info-item__value--muted">未设定</span>
              </div>

              <!-- D. 当前境界 💎 -->
              <div v-if="realmCN || realmLevel != null" class="info-item info-item--realm">
                <span class="info-item__label">💎 当前境界</span>
                <span class="info-item__realm-wrap">
                  <RealmBadge :realm="realmCN || character.realm" :level="realmLevel" />
                  <span v-if="realmSubtitle" class="info-item__realm-sub">{{ realmSubtitle }}</span>
                </span>
              </div>

              <!-- E. 状态 🟢 -->
              <div v-if="character.status" class="info-item">
                <span class="info-item__label">🟢 状态</span>
                <span class="info-item__value" :style="{ color: statusColor(character.status) }">
                  {{ character.status }}
                </span>
              </div>

              <!-- F. 年龄 -->
              <div v-if="character.age" class="info-item">
                <span class="info-item__label">年龄</span>
                <span class="info-item__value">{{ character.age }}</span>
              </div>

              <!-- F. 性别 -->
              <div v-if="character.gender" class="info-item">
                <span class="info-item__label">性别</span>
                <span class="info-item__value">{{ character.gender }}</span>
              </div>
            </div>

            <!-- 外貌描述 -->
            <div v-if="character.appearance" class="info-card__appearance">
              <h4 class="info-card__sub-title">外貌特征</h4>
              <LoreLink :text="character.appearance" tag="p" />
            </div>
          </div>
        </aside>

        <!-- ============ 右侧：描述区域 ============ -->
        <main ref="rightRef" class="detail-right">
          <!-- 1) 角色简介 -->
          <div v-if="character.description || character.background" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              角色简介
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="character.description || character.background || '暂无描述'" tag="p" />
            </div>
          </div>

          <!-- 2) 性格特征 -->
          <div v-if="character.personality" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              性格特征
            </h2>
            <div class="desc-card__content">
              <LoreLink :text="character.personality" tag="p" />
            </div>
          </div>

          <!-- 3) 成长轨迹 / 实力时间线 -->
          <div class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">✨</span>
              成长轨迹
              <span class="desc-card__deco">✨</span>
            </h2>

            <!-- 空状态 -->
            <div v-if="!powerProgression.length" class="timeline__empty">
              <div class="timeline__empty-icon">📜</div>
              <p class="timeline__empty-text">暂无成长记录，等待故事展开…</p>
            </div>

            <!-- 时间线 -->
            <div v-else class="timeline">
              <div
                v-for="(node, idx) in powerProgression"
                :key="idx"
                class="timeline__item"
              >
                <!-- 左侧：圆形图标 + 竖线 -->
                <div class="timeline__rail">
                  <div
                    class="timeline__dot"
                    :style="{
                      backgroundColor: getRealmColor(node.realm_tier || node.realm_name),
                      boxShadow: '0 0 12px ' + getRealmColor(node.realm_tier || node.realm_name)
                    }"
                  ></div>
                  <div
                    v-if="idx < powerProgression.length - 1"
                    class="timeline__line"
                    :style="{
                      background: `linear-gradient(to bottom, ${getRealmColor(node.realm_tier || node.realm_name)} 0%, rgba(255,255,255,0.08) 100%)`
                    }"
                  ></div>
                </div>

                <!-- 右侧：节点内容 -->
                <div class="timeline__content">
                  <!-- 节点标题 -->
                  <h4 class="timeline__stage">
                    {{ node.stage || node.era || `第 ${idx + 1} 阶段` }}
                  </h4>
                  <!-- 副标题：纪元 · 年龄 -->
                  <p v-if="node.era || node.age" class="timeline__meta">
                    <template v-if="node.era">{{ node.era }}</template>
                    <template v-if="node.era && node.age"> · </template>
                    <template v-if="node.age">{{ node.age }} 岁</template>
                  </p>

                  <!-- 属性行：label:value -->
                  <div class="timeline__attrs">
                    <!-- 境界 -->
                    <div
                      v-if="node.realm_name || node.realm_tier || node.realm_order != null"
                      class="attr-row"
                    >
                      <span class="attr-row__label">境界</span>
                      <span
                        class="attr-row__value"
                        :style="{ color: getRealmColor(node.realm_tier || node.realm_name) }"
                      >
                        {{ node.realm_name || tierToCN(node.realm_tier) }}
                        <template v-if="node.realm_order != null">{{ node.realm_order }}阶</template>
                      </span>
                    </div>

                    <!-- 能力觉醒 -->
                    <div v-if="parseList(node.abilities).length" class="attr-row">
                      <span class="attr-row__label">能力觉醒</span>
                      <span class="attr-row__value">
                        {{ parseList(node.abilities).join('、') }}
                      </span>
                    </div>

                    <!-- 获得宝物 -->
                    <div v-if="parseList(node.artifacts).length" class="attr-row">
                      <span class="attr-row__label">获得宝物</span>
                      <span class="attr-row__value">
                        {{ parseList(node.artifacts).join('、') }}
                      </span>
                    </div>

                    <!-- 重要事件 -->
                    <div v-if="node.events || node.note" class="attr-row">
                      <span class="attr-row__label">重要事件</span>
                      <span class="attr-row__value">
                        {{ node.events || node.note }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 4) 能力技能 -->
          <div v-if="character.abilities && character.abilities.length" class="card card-gold desc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="desc-card__title">
              <span class="desc-card__deco">◆</span>
              能力技能
            </h2>
            <div class="abilities-list">
              <div v-for="ability in character.abilities" :key="ability.id" class="ability-item">
                <div class="ability-item__header">
                  <span class="ability-item__name">{{ ability.name }}</span>
                  <span v-if="ability.level" class="ability-item__level">{{ ability.level }}</span>
                </div>
                <p v-if="ability.description" class="ability-item__desc">
                  <LoreLink :text="ability.description" />
                </p>
              </div>
            </div>
          </div>
        </main>
      </div>

      <!-- ============ 底部：关联区 ============ -->

      <!-- 1) 持有宝物 -->
      <div v-if="character.artifacts && character.artifacts.length" class="detail-section">
        <h2 class="section-title">持有宝物</h2>
        <div class="grid-4">
          <RouterLink
            v-for="artifact in character.artifacts"
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
            <RarityBadge v-if="artifact.rarity" :rarity="artifact.rarity" />
          </RouterLink>
        </div>
      </div>

      <!-- 2) 关联种族（可选） -->
      <div v-if="raceInfo && raceInfo.id" class="detail-section">
        <h2 class="section-title">关联种族</h2>
        <div class="grid-4">
          <RouterLink
            :to="`/races/${raceInfo.id}`"
            class="related-card card related-card--race"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>
            <div class="related-card__icon">🧬</div>
            <h4 class="related-card__name">{{ raceInfo.name }}</h4>
            <span class="related-card__tag">种族档案</span>
          </RouterLink>
        </div>
      </div>

      <!-- 3) 关联势力（可选） -->
      <div v-if="factionInfo && factionInfo.id" class="detail-section">
        <h2 class="section-title">关联势力</h2>
        <div class="grid-4">
          <RouterLink
            :to="`/forces/${factionInfo.id}`"
            class="related-card card related-card--faction"
          >
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>
            <div class="related-card__icon">🏰</div>
            <h4 class="related-card__name">{{ factionInfo.name }}</h4>
            <span v-if="factionRole" class="related-card__role">{{ factionRole }}</span>
          </RouterLink>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.char-detail {
  padding-top: var(--spacing-lg);
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
}

.info-card__avatar {
  width: 120px;
  height: 120px;
  margin: 0 auto var(--spacing-md);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  border: 2px solid var(--color-gold-primary);
  box-shadow: 0 0 20px var(--color-gold-glow);
}

.info-card__avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-card__avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card-hover);
  font-family: var(--font-family-display);
  font-size: 48px;
  color: var(--text-gold);
}

.info-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-xs);
  letter-spacing: 2px;
}

.info-card__alias {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  font-style: italic;
  margin-bottom: var(--spacing-sm);
}

/* info-list 基础资料标题 */
.info-list__section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--color-gold-primary);
  text-align: left;
  letter-spacing: 2px;
  padding: var(--spacing-xs) var(--spacing-sm);
  margin: var(--spacing-xs) 0 var(--spacing-sm);
  border-left: 3px solid var(--color-gold-primary);
  background: linear-gradient(90deg, rgba(212, 168, 83, 0.08), transparent);
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
  align-items: flex-start;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-sm);
  border-left: 2px solid var(--color-gold-dark);
  gap: var(--spacing-xs);
}

.info-item__label {
  color: var(--text-muted);
  font-size: var(--font-size-sm);
  flex-shrink: 0;
  line-height: 1.6;
}

.info-item__value {
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  text-align: right;
  line-height: 1.6;
  word-break: break-all;
}

.info-item__value--muted {
  color: var(--text-muted);
  font-weight: 400;
  font-style: italic;
  opacity: 0.7;
}

.info-item__value-wrap {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-end;
  text-align: right;
  max-width: 60%;
}

.info-item__link {
  color: var(--color-cyan-primary);
  font-size: var(--font-size-sm);
  text-decoration: none;
  font-weight: 500;
}

.info-item__link:hover {
  color: var(--color-cyan-light);
  text-shadow: 0 0 8px var(--color-cyan-glow);
}

.info-item__sub {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin-top: 2px;
}

/* 境界行 */
.info-item--realm {
  align-items: center;
}

.info-item__realm-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.info-item__realm-sub {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
}

.info-card__appearance {
  text-align: left;
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.info-card__sub-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--color-gold-primary);
  margin-bottom: var(--spacing-xs);
  letter-spacing: 1px;
}

.info-card__appearance p {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.8;
}

/* 右侧描述 */
.detail-right {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.desc-card {
  padding: var(--spacing-xl);
  position: relative;
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
  font-size: 12px;
}

.desc-card__content {
  color: var(--text-primary);
  line-height: 2;
  font-size: var(--font-size-base);
}

/* ============ 时间线样式 ============ */
.timeline {
  display: flex;
  flex-direction: column;
  position: relative;
}

.timeline__item {
  display: flex;
  gap: var(--spacing-md);
  position: relative;
}

.timeline__rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 28px;
  flex-shrink: 0;
}

.timeline__dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.9);
  flex-shrink: 0;
  margin-top: 4px;
  position: relative;
  z-index: 2;
}

.timeline__line {
  width: 2px;
  flex: 1;
  min-height: 40px;
  margin-top: 4px;
  border-radius: 1px;
}

.timeline__content {
  flex: 1;
  padding: 0 0 var(--spacing-lg) 0;
  background: rgba(6, 11, 20, 0.3);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-left: 3px solid var(--color-gold-dark);
}

.timeline__stage {
  font-family: var(--font-family-display);
  font-size: var(--font-size-base);
  color: var(--text-gold);
  margin: 0 0 4px;
  letter-spacing: 0.5px;
}

.timeline__meta {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  margin: 0 0 var(--spacing-sm);
  font-style: italic;
}

.timeline__attrs {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.attr-row {
  display: flex;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  line-height: 1.7;
}

.attr-row__label {
  color: var(--text-muted);
  flex-shrink: 0;
  min-width: 64px;
}

.attr-row__value {
  color: var(--text-primary);
  flex: 1;
  word-break: break-word;
}

/* 时间线空状态 */
.timeline__empty {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-md);
  color: var(--text-muted);
}

.timeline__empty-icon {
  font-size: 40px;
  margin-bottom: var(--spacing-sm);
  filter: drop-shadow(0 0 8px var(--color-gold-glow));
  opacity: 0.7;
}

.timeline__empty-text {
  font-size: var(--font-size-sm);
  font-style: italic;
  opacity: 0.8;
}

/* 技能列表 */
.abilities-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.ability-item {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border-radius: var(--border-radius-md);
  border-left: 2px solid var(--color-cyan-dark);
}

.ability-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
}

.ability-item__name {
  color: var(--color-cyan-primary);
  font-weight: 600;
  font-size: var(--font-size-base);
}

.ability-item__level {
  font-size: var(--font-size-xs);
  color: var(--text-gold);
  padding: 2px 8px;
  background: rgba(212, 168, 83, 0.1);
  border-radius: var(--border-radius-sm);
}

.ability-item__desc {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  line-height: 1.6;
}

/* 底部关联区域 */
.detail-section {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
  padding-left: var(--spacing-sm);
  border-left: 4px solid var(--color-gold-primary);
  letter-spacing: 1px;
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
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(212, 168, 83, 0.15);
}

.related-card__icon {
  font-size: 32px;
  filter: drop-shadow(0 0 8px var(--color-gold-glow));
}

.related-card__name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-sm);
  color: var(--text-heading);
  margin: 0;
}

.related-card__tag {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: var(--border-radius-sm);
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.related-card__role {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  padding: 2px 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: var(--border-radius-sm);
  border: 1px solid rgba(59, 130, 246, 0.25);
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
