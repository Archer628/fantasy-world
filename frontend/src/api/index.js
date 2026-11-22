import axios from 'axios'

/**
 * Axios 实例配置
 * 基础URL指向后端API服务 http://localhost:8000/api/
 * 统一的请求/响应拦截器
 */

const api = axios.create({
  baseURL: '/api/',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ==================== 静态数据模式（GitHub Pages 等无后端环境） ====================
// 构建时通过 GITHUB_PAGES=1 打开，请求改为读取 public/static-api 下的 JSON 快照
const USE_STATIC_DATA = typeof __USE_STATIC_DATA__ !== 'undefined' && __USE_STATIC_DATA__
const STATIC_ROOT = `${import.meta.env.BASE_URL}static-api/`
const staticFileCache = new Map()

/** 加载并缓存单个快照文件 */
function loadStaticFile(rel) {
  if (!staticFileCache.has(rel)) {
    staticFileCache.set(
      rel,
      fetch(`${STATIC_ROOT}${rel}`)
        .then((r) => (r.ok ? r.json() : null))
        .catch(() => null)
    )
  }
  return staticFileCache.get(rel)
}

/** 解析请求地址中的路径段与查询参数（合并 config.params） */
function parseRequest(config) {
  const raw = String(config.url || '')
  const qIndex = raw.indexOf('?')
  const path = qIndex === -1 ? raw : raw.slice(0, qIndex)
  const queryString = qIndex === -1 ? '' : raw.slice(qIndex + 1)
  const segs = path.split('/').filter(Boolean)
  const params = {}
  new URLSearchParams(queryString).forEach((v, k) => {
    params[k] = v
  })
  Object.assign(params, config.params || {})
  return { segs, params }
}

/** 按请求查找对应的快照数据，找不到返回 null */
async function resolveStatic(config) {
  const { segs, params } = parseRequest(config)
  const endpoint = segs[0]
  const rest = segs.slice(1).join('/')
  if (!endpoint) return null

  // 搜索无静态数据，返回空结果
  if (endpoint === 'search') return { results: [] }

  // 统计接口
  if (endpoint === 'stats') {
    const all = await loadStaticFile('special/stats.json')
    return all ? all[params.world || ''] ?? null : null
  }

  // 关系图谱
  if (endpoint === 'relationships' && rest === 'graph') {
    const graph = await loadStaticFile('special/relation-graph.json')
    return graph || { nodes: [], edges: [] }
  }

  // 详情接口：/factions/37
  if (rest) {
    const all = await loadStaticFile(`detail/${endpoint}.json`)
    return all ? all[rest] ?? null : null
  }

  // 列表接口：/factions?world=xxx
  const all = await loadStaticFile(`list/${endpoint}.json`)
  if (!all) return null

  // 设定页面按 slug 查询
  if (params.slug) {
    const bySlug = await loadStaticFile('list/lore-pages-by-slug.json')
    const hit = bySlug ? bySlug[`slug=${params.slug}`] : null
    if (hit) return hit
  }

  return all[params.world || ''] ?? all[''] ?? null
}

/** 自定义 axios adapter：从静态快照返回数据 */
async function staticAdapter(config) {
  const data = await resolveStatic(config)
  if (data === null || data === undefined) {
    throw new Error(`静态数据缺失: ${config.url}`)
  }
  return {
    data,
    status: 200,
    statusText: 'OK',
    headers: {},
    config,
    request: {},
  }
}

if (USE_STATIC_DATA) {
  api.defaults.adapter = staticAdapter
}

/**
 * 请求拦截器
 * - 自动携带认证Token
 * - 显示加载状态（可扩展）
 */
api.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * - 统一错误处理
 * - 401 未授权跳转登录
 * - 数据解包
 */
api.interceptors.response.use(
  (response) => {
    // 如果后端返回的是包装格式 { data, code, message }，在此解包
    return response.data
  },
  (error) => {
    const { response } = error
    if (response) {
      switch (response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('auth_token')
          break
        case 403:
          console.error('没有权限访问该资源')
          break
        case 404:
          console.error('请求的资源不存在')
          break
        case 500:
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求错误: ${response.status}`)
      }
    } else {
      console.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

// ==================== API 模块导出 ====================

/** 族群相关 API */
export const factionApi = {
  list: (params) => api.get('/factions', { params }),
  detail: (id) => api.get(`/factions/${id}`),
  create: (data) => api.post('/factions', data),
  update: (id, data) => api.put(`/factions/${id}`, data),
  delete: (id) => api.delete(`/factions/${id}`),
}

/** 角色相关 API */
export const characterApi = {
  list: (params) => api.get('/characters', { params }),
  detail: (id) => api.get(`/characters/${id}`),
  create: (data) => api.post('/characters', data),
  update: (id, data) => api.put(`/characters/${id}`, data),
  delete: (id) => api.delete(`/characters/${id}`),
}

/** 宝物相关 API */
export const artifactApi = {
  list: (params) => api.get('/artifacts', { params }),
  detail: (id) => api.get(`/artifacts/${id}`),
  create: (data) => api.post('/artifacts', data),
  update: (id, data) => api.put(`/artifacts/${id}`, data),
  delete: (id) => api.delete(`/artifacts/${id}`),
}

/** 能力体系相关 API（别名，指向 ability-systems） */
export const abilityApi = {
  list: (params) => api.get('/ability-systems', { params }),
  detail: (id) => api.get(`/ability-systems/${id}`),
  create: (data) => api.post('/ability-systems', data),
  update: (id, data) => api.put(`/ability-systems/${id}`, data),
  delete: (id) => api.delete(`/ability-systems/${id}`),
}

/** 能力体系（体系分类）相关 API */
export const abilitySystemApi = {
  list: (params) => api.get('/ability-systems', { params }),
  detail: (id) => api.get(`/ability-systems/${id}`),
  create: (data) => api.post('/ability-systems', data),
  update: (id, data) => api.put(`/ability-systems/${id}`, data),
  delete: (id) => api.delete(`/ability-systems/${id}`),
}

/** 技能等级相关 API */
export const skillLevelApi = {
  list: (params) => api.get('/skill-levels', { params }),
  detail: (id) => api.get(`/skill-levels/${id}`),
  create: (data) => api.post('/skill-levels', data),
  update: (id, data) => api.put(`/skill-levels/${id}`, data),
  delete: (id) => api.delete(`/skill-levels/${id}`),
}

/** 技能相关 API */
export const skillApi = {
  list: (params) => api.get('/skills', { params }),
  detail: (id) => api.get(`/skills/${id}`),
  create: (data) => api.post('/skills', data),
  update: (id, data) => api.put(`/skills/${id}`, data),
  delete: (id) => api.delete(`/skills/${id}`),
}

/** 异兽相关 API */
export const creatureApi = {
  list: (params) => api.get('/creatures', { params }),
  detail: (id) => api.get(`/creatures/${id}`),
  create: (data) => api.post('/creatures', data),
  update: (id, data) => api.put(`/creatures/${id}`, data),
  delete: (id) => api.delete(`/creatures/${id}`),
}

/** 碎片世界相关 API */
export const fragmentWorldApi = {
  list: (params) => api.get('/fragment-worlds', { params }),
  detail: (id) => api.get(`/fragment-worlds/${id}`),
  create: (data) => api.post('/fragment-worlds', data),
  update: (id, data) => api.put(`/fragment-worlds/${id}`, data),
  delete: (id) => api.delete(`/fragment-worlds/${id}`),
}

/** 境界等级相关 API */
export const realmApi = {
  list: (params) => api.get('/realms', { params }),
  detail: (id) => api.get(`/realms/${id}`),
  create: (data) => api.post('/realms', data),
  update: (id, data) => api.put(`/realms/${id}`, data),
  delete: (id) => api.delete(`/realms/${id}`),
}

/** 历史事件相关 API */
export const historyApi = {
  list: (params) => api.get('/historical-events', { params }),
  detail: (id) => api.get(`/historical-events/${id}`),
}

/** 关系网络相关 API */
export const relationApi = {
  list: (params) => api.get('/relationships', { params }),
  graph: () => api.get('/relationships/graph'),
}

/** 搜索 API - 跨模块搜索（支持按大世界过滤） */
export const searchApi = {
  search: (query, worldSlug) => api.get('/search/', { params: { q: query, world: worldSlug } }),
}

/** 统计 API（支持按大世界过滤） */
export const worldApiStats = {
  stats: (worldSlug) => api.get('/stats/', { params: { world: worldSlug } }),
}

/** 大世界相关 API */
export const worldApi = {
  list: (params) => api.get('/worlds', { params }),
  detail: (slug) => api.get(`/worlds/${slug}`),
  create: (data) => api.post('/worlds', data),
  update: (slug, data) => api.put(`/worlds/${slug}`, data),
  delete: (slug) => api.delete(`/worlds/${slug}`),
}

/** 通用设定页面 API (通过 slug 获取) */
export const loreApi = {
  getBySlug: (slug) => api.get(`/lore-pages/`, { params: { slug } }),
  getAll: (params) => api.get('/lore-pages/', { params }),
}

/** 本源法则相关 API */
export const originLawApi = {
  list: (params) => api.get('/origin-laws', { params }),
  detail: (id) => api.get(`/origin-laws/${id}`),
  create: (data) => api.post('/origin-laws', data),
  update: (id, data) => api.put(`/origin-laws/${id}`, data),
  delete: (id) => api.delete(`/origin-laws/${id}`),
}

/** 异常物相关 API */
export const anomalyApi = {
  list: (params) => api.get('/anomalies', { params }),
  detail: (id) => api.get(`/anomalies/${id}`),
  create: (data) => api.post('/anomalies', data),
  update: (id, data) => api.put(`/anomalies/${id}`, data),
  delete: (id) => api.delete(`/anomalies/${id}`),
}

/** 宝物种类相关 API（通用基础设定） */
export const artifactCategoryApi = {
  list: (params) => api.get('/artifact-categories', { params }),
  detail: (id) => api.get(`/artifact-categories/${id}`),
  create: (data) => api.post('/artifact-categories', data),
  update: (id, data) => api.put(`/artifact-categories/${id}`, data),
  delete: (id) => api.delete(`/artifact-categories/${id}`),
}

export default api
