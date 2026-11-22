import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  worldApi,
  worldApiStats,
  factionApi,
  characterApi,
  artifactApi,
  abilitySystemApi,
  creatureApi,
  fragmentWorldApi,
  realmApi,
  historyApi,
  relationApi,
  searchApi,
  loreApi,
} from '@/api'

/**
 * 世界观数据 Store（大世界切换增强版）
 *
 * 核心能力：
 * - 管理多个大世界（worlds），支持切换当前世界
 * - 所有列表数据按 world slug 分组缓存（dataCache）
 * - 切换世界后所有计算属性自动指向新世界的数据
 * - 兼容旧版 API：保留详情缓存、加载状态、关系图谱、搜索结果等
 *
 * 同时维护术语词典，用于 LoreLink 组件的术语识别
 */
export const useWorldDataStore = defineStore('worldData', () => {
  // ==================== 大世界管理 ====================

  /** 所有大世界列表 */
  const worlds = ref([])
  /** 当前选中的大世界 slug（持久化到 localStorage） */
  const currentWorldSlug = ref(localStorage.getItem('currentWorldSlug') || '')
  /** 当前世界对象 */
  const currentWorld = computed(
    () => worlds.value.find((w) => w.slug === currentWorldSlug.value) || worlds.value[0] || null
  )

  /**
   * 数据缓存（按世界 slug 分组）
   * 结构：{ [worldSlug]: { factions: [], characters: [], ... } }
   */
  const dataCache = ref({})

  /** 当前世界的数据（计算属性） */
  const currentData = computed(() => dataCache.value[currentWorldSlug.value] || {})

  // 当前世界的各列表数据（计算属性，自动跟随 currentWorldSlug）
  const factions = computed(() => currentData.value.factions || [])
  const characters = computed(() => currentData.value.characters || [])
  const artifacts = computed(() => currentData.value.artifacts || [])
  const abilities = computed(() => currentData.value.abilities || [])
  const creatures = computed(() => currentData.value.creatures || [])
  const fragmentWorlds = computed(() => currentData.value.fragmentWorlds || [])
  const realms = computed(() => currentData.value.realms || [])
  const historyEvents = computed(() => currentData.value.historyEvents || [])
  const lorePages = computed(() => currentData.value.lorePages || [])
  const relationships = computed(() => currentData.value.relationships || [])

  // ==================== 加载状态 ====================

  /** 全局加载状态 */
  const loading = ref(false)

  // 兼容旧版的逐项加载状态
  const overviewLoading = ref(false)
  const factionsLoading = ref(false)
  const charactersLoading = ref(false)
  const artifactsLoading = ref(false)
  const abilitiesLoading = ref(false)
  const creaturesLoading = ref(false)
  const fragmentWorldsLoading = ref(false)
  const realmsLoading = ref(false)
  const historyLoading = ref(false)
  const relationsLoading = ref(false)
  const loreLoading = ref(false)
  const searchLoading = ref(false)

  /** 错误信息（兼容旧版） */
  const lastError = ref(null)

  // ==================== 详情缓存（兼容旧版） ====================

  const overview = ref(null)
  const factionMap = ref({})
  const characterMap = ref({})
  const artifactMap = ref({})
  const abilityMap = ref({})
  const creatureMap = ref({})
  const fragmentWorldMap = ref({})
  const lorePageMap = ref({}) // { [slug]: lorePageData }

  /** 关系网络（兼容旧版：relations 为列表，relationGraph 为图谱） */
  const relationGraph = ref({ nodes: [], edges: [] })
  const searchResults = ref([])

  // ==================== 辅助方法 ====================

  /** 从响应中提取结果数组，兼容多种后端返回格式 */
  function extractList(data) {
    if (Array.isArray(data)) return data
    if (data && Array.isArray(data.results)) return data.results
    if (data && Array.isArray(data.data)) return data.data
    if (data && Array.isArray(data.items)) return data.items
    return []
  }

  /** 确保某世界的缓存结构存在 */
  function ensureCache(slug) {
    if (!dataCache.value[slug]) {
      dataCache.value[slug] = {}
    }
    return dataCache.value[slug]
  }

  // ==================== 大世界 Actions ====================

  /** 进行中的世界列表请求（用于并发去重） */
  let worldsPromise = null

  /** 加载世界列表 */
  async function loadWorlds() {
    // 已加载则直接返回，避免重复请求
    if (worlds.value.length > 0) return worlds.value
    // 并发去重：多个调用复用同一个请求
    if (worldsPromise) return worldsPromise
    worldsPromise = (async () => {
      try {
        const data = await worldApi.list()
        const results = data.results || data
        worlds.value = results
        if (results.length > 0) {
          // 若当前 slug 为空或已失效，回退到第一个世界
          const exists = results.some((w) => w.slug === currentWorldSlug.value)
          if (!currentWorldSlug.value || !exists) {
            currentWorldSlug.value = results[0].slug
            localStorage.setItem('currentWorldSlug', currentWorldSlug.value)
          }
        }
        return results
      } catch (e) {
        console.error('加载世界列表失败:', e)
        return []
      } finally {
        worldsPromise = null
      }
    })()
    return worldsPromise
  }

  /**
   * 确保世界列表已加载且 currentWorldSlug 有效，返回当前 slug。
   * 解决首次直接进入列表页时 slug 为空导致无法加载数据的竞态问题。
   */
  async function ensureCurrentWorld() {
    if (worlds.value.length === 0) {
      await loadWorlds()
    }
    if (
      worlds.value.length > 0 &&
      !worlds.value.some((w) => w.slug === currentWorldSlug.value)
    ) {
      currentWorldSlug.value = worlds.value[0].slug
      localStorage.setItem('currentWorldSlug', currentWorldSlug.value)
    }
    return currentWorldSlug.value
  }

  /** 切换当前世界 */
  function switchWorld(slug) {
    currentWorldSlug.value = slug
    localStorage.setItem('currentWorldSlug', slug)
    // 确保新世界的缓存结构存在（保留已有缓存）
    if (!dataCache.value[slug]) {
      dataCache.value[slug] = {}
    }
  }

  /** 清除指定世界的缓存 */
  function clearWorldCache(slug) {
    if (dataCache.value[slug]) {
      delete dataCache.value[slug]
    }
  }

  /** 清除所有缓存 */
  function clearAllCache() {
    dataCache.value = {}
    // 同步清除详情缓存
    factionMap.value = {}
    characterMap.value = {}
    artifactMap.value = {}
    abilityMap.value = {}
    creatureMap.value = {}
    fragmentWorldMap.value = {}
    lorePageMap.value = {}
    overview.value = null
    relationGraph.value = { nodes: [], edges: [] }
    searchResults.value = []
  }

  /** 清除所有缓存（兼容旧版别名） */
  const clearCache = clearAllCache

  // ==================== 各列表加载（按当前世界过滤 + 缓存） ====================

  /** 加载族群列表 */
  async function loadFactions() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.factions) return cache.factions
    loading.value = true
    factionsLoading.value = true
    lastError.value = null
    try {
      const data = await factionApi.list({ world: slug })
      cache.factions = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载族群失败:', e)
      cache.factions = []
    } finally {
      loading.value = false
      factionsLoading.value = false
    }
    return cache.factions
  }

  /** 加载角色列表 */
  async function loadCharacters() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.characters) return cache.characters
    loading.value = true
    charactersLoading.value = true
    lastError.value = null
    try {
      const data = await characterApi.list({ world: slug })
      cache.characters = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载角色失败:', e)
      cache.characters = []
    } finally {
      loading.value = false
      charactersLoading.value = false
    }
    return cache.characters
  }

  /** 加载宝物列表 */
  async function loadArtifacts() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.artifacts) return cache.artifacts
    loading.value = true
    artifactsLoading.value = true
    lastError.value = null
    try {
      const data = await artifactApi.list({ world: slug })
      cache.artifacts = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载宝物失败:', e)
      cache.artifacts = []
    } finally {
      loading.value = false
      artifactsLoading.value = false
    }
    return cache.artifacts
  }

  /** 加载能力体系 */
  async function loadAbilities() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.abilities) return cache.abilities
    loading.value = true
    abilitiesLoading.value = true
    lastError.value = null
    try {
      const data = await abilitySystemApi.list({ world: slug })
      cache.abilities = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载能力体系失败:', e)
      cache.abilities = []
    } finally {
      loading.value = false
      abilitiesLoading.value = false
    }
    return cache.abilities
  }

  /** 加载异兽 */
  async function loadCreatures() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.creatures) return cache.creatures
    loading.value = true
    creaturesLoading.value = true
    lastError.value = null
    try {
      const data = await creatureApi.list({ world: slug })
      cache.creatures = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载异兽失败:', e)
      cache.creatures = []
    } finally {
      loading.value = false
      creaturesLoading.value = false
    }
    return cache.creatures
  }

  /** 加载碎片世界 */
  async function loadFragmentWorlds() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.fragmentWorlds) return cache.fragmentWorlds
    loading.value = true
    fragmentWorldsLoading.value = true
    lastError.value = null
    try {
      const data = await fragmentWorldApi.list({ world: slug })
      cache.fragmentWorlds = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载碎片世界失败:', e)
      cache.fragmentWorlds = []
    } finally {
      loading.value = false
      fragmentWorldsLoading.value = false
    }
    return cache.fragmentWorlds
  }

  /** 加载境界 */
  async function loadRealms() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.realms) return cache.realms
    loading.value = true
    realmsLoading.value = true
    lastError.value = null
    try {
      const data = await realmApi.list({ world: slug })
      cache.realms = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载境界失败:', e)
      cache.realms = []
    } finally {
      loading.value = false
      realmsLoading.value = false
    }
    return cache.realms
  }

  /** 加载历史事件 */
  async function loadHistory() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.historyEvents) return cache.historyEvents
    loading.value = true
    historyLoading.value = true
    lastError.value = null
    try {
      const data = await historyApi.list({ world: slug })
      cache.historyEvents = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载历史事件失败:', e)
      cache.historyEvents = []
    } finally {
      loading.value = false
      historyLoading.value = false
    }
    return cache.historyEvents
  }

  /** 加载设定页面（列表） */
  async function loadLorePages() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.lorePages) return cache.lorePages
    loading.value = true
    loreLoading.value = true
    lastError.value = null
    try {
      const data = await loreApi.getAll({ world: slug })
      cache.lorePages = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载设定页面失败:', e)
      cache.lorePages = []
    } finally {
      loading.value = false
      loreLoading.value = false
    }
    return cache.lorePages
  }

  /** 加载关系网络（列表） */
  async function loadRelations() {
    const slug = await ensureCurrentWorld()
    if (!slug) return []
    const cache = ensureCache(slug)
    if (cache.relationships) return cache.relationships
    loading.value = true
    relationsLoading.value = true
    lastError.value = null
    try {
      const data = await relationApi.list({ world: slug })
      cache.relationships = extractList(data)
    } catch (e) {
      lastError.value = e
      console.error('加载关系网络失败:', e)
      cache.relationships = []
    } finally {
      loading.value = false
      relationsLoading.value = false
    }
    return cache.relationships
  }

  /** 加载关系图谱 */
  async function loadRelationGraph() {
    try {
      const data = await relationApi.graph()
      relationGraph.value = data || { nodes: [], edges: [] }
      return relationGraph.value
    } catch (e) {
      console.error('加载关系图谱失败:', e)
      return { nodes: [], edges: [] }
    }
  }

  // ==================== 详情加载（兼容旧版） ====================

  /** 加载族群详情 */
  async function loadFactionDetail(id) {
    if (factionMap.value[id]) return factionMap.value[id]
    try {
      const data = await factionApi.detail(id)
      factionMap.value[id] = data
      return data
    } catch (e) {
      console.error('加载族群详情失败:', e)
      return null
    }
  }

  /** 加载角色详情 */
  async function loadCharacterDetail(id) {
    if (characterMap.value[id]) return characterMap.value[id]
    try {
      const data = await characterApi.detail(id)
      characterMap.value[id] = data
      return data
    } catch (e) {
      console.error('加载角色详情失败:', e)
      return null
    }
  }

  /** 加载宝物详情 */
  async function loadArtifactDetail(id) {
    if (artifactMap.value[id]) return artifactMap.value[id]
    try {
      const data = await artifactApi.detail(id)
      artifactMap.value[id] = data
      return data
    } catch (e) {
      console.error('加载宝物详情失败:', e)
      return null
    }
  }

  /** 加载异兽详情 */
  async function loadCreatureDetail(id) {
    if (creatureMap.value[id]) return creatureMap.value[id]
    try {
      const data = await creatureApi.detail(id)
      creatureMap.value[id] = data
      return data
    } catch (e) {
      console.error('加载异兽详情失败:', e)
      return null
    }
  }

  /** 加载碎片世界详情 */
  async function loadFragmentWorldDetail(id) {
    if (fragmentWorldMap.value[id]) return fragmentWorldMap.value[id]
    try {
      const data = await fragmentWorldApi.detail(id)
      fragmentWorldMap.value[id] = data
      return data
    } catch (e) {
      console.error('加载碎片世界详情失败:', e)
      return null
    }
  }

  /** 加载单个设定页面（通过 slug，兼容旧版） */
  async function loadLorePage(slug) {
    if (lorePageMap.value[slug]) return lorePageMap.value[slug]
    loreLoading.value = true
    lastError.value = null
    try {
      const data = await loreApi.getBySlug(slug)
      lorePageMap.value[slug] = data
      return data
    } catch (e) {
      lastError.value = e
      console.error('加载设定页面失败:', e)
      return null
    } finally {
      loreLoading.value = false
    }
  }

  /** 加载世界观总览（兼容旧版，按当前世界过滤） */
  async function loadOverview() {
    if (overview.value) return overview.value
    const slug = await ensureCurrentWorld()
    overviewLoading.value = true
    lastError.value = null
    try {
      const data = await loreApi.getAll({ category: '世界观核心', world: slug })
      overview.value = data
      return data
    } catch (e) {
      lastError.value = e
      console.error('加载世界观总览失败:', e)
      return null
    } finally {
      overviewLoading.value = false
    }
  }

  /** 获取当前世界统计（按世界过滤） */
  async function loadStats() {
    const slug = await ensureCurrentWorld()
    try {
      return await worldApiStats.stats(slug)
    } catch (e) {
      console.error('加载统计数据失败:', e)
      return null
    }
  }

  // ==================== 搜索 ====================

  /** 搜索（按当前世界过滤） */
  async function search(query) {
    if (!query) {
      searchResults.value = []
      return []
    }
    const slug = await ensureCurrentWorld()
    searchLoading.value = true
    lastError.value = null
    try {
      const data = await searchApi.search(query, slug)
      searchResults.value = extractList(data)
      return searchResults.value
    } catch (e) {
      lastError.value = e
      console.error('搜索失败:', e)
      searchResults.value = []
      return []
    } finally {
      searchLoading.value = false
    }
  }

  // ==================== 预加载 ====================

  /**
   * 预加载所有基础数据（用于初始化术语词典）
   * 静默失败，不阻塞页面渲染
   */
  async function preloadAll() {
    // 确保世界列表已加载，以便 currentWorldSlug 可用
    await loadWorlds()
    const tasks = [
      loadFactions(),
      loadCharacters(),
      loadArtifacts(),
      loadCreatures(),
      loadFragmentWorlds(),
    ]
    await Promise.allSettled(tasks)
  }

  // ==================== 术语词典（LoreLink 核心） ====================

  /**
   * 术语词典
   * 格式: { '术语名': { type, slug, id } }
   * 用于在文本中自动识别并替换为可点击链接
   */
  const loreDictionary = computed(() => {
    const dict = {}

    characters.value.forEach((c) => {
      if (c.name) dict[c.name] = { type: 'character', slug: c.slug, id: c.id }
      // 角色别名也加入词典
      if (c.aliases) {
        const aliases = Array.isArray(c.aliases)
          ? c.aliases
          : String(c.aliases).split(/[,，、]/)
        aliases.forEach((alias) => {
          const a = alias.trim()
          if (a) dict[a] = { type: 'character', slug: c.slug, id: c.id }
        })
      }
    })

    factions.value.forEach((f) => {
      if (f.name) dict[f.name] = { type: 'faction', slug: f.slug, id: f.id }
    })

    artifacts.value.forEach((a) => {
      if (a.name) dict[a.name] = { type: 'artifact', slug: a.slug, id: a.id }
    })

    creatures.value.forEach((c) => {
      if (c.name) dict[c.name] = { type: 'creature', slug: c.slug, id: c.id }
    })

    fragmentWorlds.value.forEach((w) => {
      if (w.name) dict[w.name] = { type: 'fragment-world', slug: w.slug, id: w.id }
    })

    return dict
  })

  return {
    // ===== 大世界 =====
    worlds,
    currentWorldSlug,
    currentWorld,
    dataCache,
    // ===== 当前世界列表数据 =====
    factions,
    characters,
    artifacts,
    abilities,
    creatures,
    fragmentWorlds,
    realms,
    historyEvents,
    lorePages,
    relationships,
    // ===== 兼容旧版：关系网络 =====
    relations: computed(() => relationships.value),
    relationGraph,
    searchResults,
    overview,
    // ===== 详情缓存 Map =====
    factionMap,
    characterMap,
    artifactMap,
    abilityMap,
    creatureMap,
    fragmentWorldMap,
    lorePageMap,
    // ===== 加载状态 =====
    loading,
    overviewLoading,
    factionsLoading,
    charactersLoading,
    artifactsLoading,
    abilitiesLoading,
    creaturesLoading,
    fragmentWorldsLoading,
    realmsLoading,
    historyLoading,
    relationsLoading,
    loreLoading,
    searchLoading,
    // ===== 错误 =====
    lastError,
    // ===== 计算属性 =====
    loreDictionary,
    // ===== 大世界方法 =====
    loadWorlds,
    ensureCurrentWorld,
    switchWorld,
    clearWorldCache,
    clearAllCache,
    clearCache,
    // ===== 列表加载方法 =====
    loadFactions,
    loadCharacters,
    loadArtifacts,
    loadAbilities,
    loadCreatures,
    loadFragmentWorlds,
    loadRealms,
    loadHistory,
    loadLorePages,
    loadRelations,
    loadRelationGraph,
    // ===== 详情加载方法 =====
    loadFactionDetail,
    loadCharacterDetail,
    loadArtifactDetail,
    loadCreatureDetail,
    loadFragmentWorldDetail,
    loadLorePage,
    // ===== 总览 / 统计 / 搜索 / 预加载 =====
    loadOverview,
    loadStats,
    search,
    preloadAll,
  }
})
