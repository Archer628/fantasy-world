import { createRouter, createWebHistory } from 'vue-router'

/**
 * 路由配置
 *
 * 前台页面：使用 LoreLayout 布局
 * - /                     首页
 * - /world-overview       世界观总览
 * - /factions             族群列表
 * - /factions/:id         族群详情
 * - /characters           角色列表
 * - /characters/:id       角色详情
 * - /artifacts            宝物列表
 * - /artifacts/:id        宝物详情
 * - /abilities           能力体系
 * - /realms               境界等级
 * - /creatures            异兽图鉴
 * - /fragment-worlds      碎片世界列表
 * - /fragment-worlds/:id  碎片世界详情
 * - /history              历史事件
 * - /relations            关系网络
 * - /lore/:slug           通用设定页面（术语slug路由）
 *
 * 后台管理：使用 AdminLayout 布局
 * - /admin                后台首页
 * - /admin/worlds         大世界管理
 * - /admin/factions       族群管理
 * - /admin/characters     角色管理
 * - /admin/artifacts      宝物管理
 * - /admin/abilities      能力体系管理
 * - /admin/creatures      异兽管理
 * - /admin/fragment-worlds 碎片世界管理
 */

const routes = [
  // ==================== 前台路由 ====================
  {
    path: '/',
    component: () => import('@/components/layout/LoreLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'world-overview',
        name: 'WorldOverview',
        component: () => import('@/views/WorldOverview.vue'),
        meta: { title: '世界观总览' },
      },
      {
        path: 'factions',
        name: 'Factions',
        component: () => import('@/views/Factions.vue'),
        meta: { title: '族群列表' },
      },
      {
        path: 'races',
        name: 'Races',
        component: () => import('@/views/Races.vue'),
        meta: { title: '种族百科' },
      },
      {
        path: 'forces',
        name: 'Forces',
        component: () => import('@/views/Forces.vue'),
        meta: { title: '势力组织' },
      },
      {
        path: 'races/:id',
        name: 'RaceDetail',
        component: () => import('@/views/FactionDetail.vue'),
        meta: { title: '种族详情' },
      },
      {
        path: 'forces/:id',
        name: 'ForceDetail',
        component: () => import('@/views/FactionDetail.vue'),
        meta: { title: '势力详情' },
      },
      {
        path: 'factions/:id',
        name: 'FactionDetail',
        component: () => import('@/views/FactionDetail.vue'),
        meta: { title: '族群详情' },
      },
      {
        path: 'characters',
        name: 'Characters',
        component: () => import('@/views/Characters.vue'),
        meta: { title: '角色列表' },
      },
      {
        path: 'characters/:id',
        name: 'CharacterDetail',
        component: () => import('@/views/CharacterDetail.vue'),
        meta: { title: '角色详情' },
      },
      {
        path: 'artifacts',
        name: 'Artifacts',
        component: () => import('@/views/Artifacts.vue'),
        meta: { title: '宝物列表' },
      },
      {
        path: 'artifacts/:id',
        name: 'ArtifactDetail',
        component: () => import('@/views/ArtifactDetail.vue'),
        meta: { title: '宝物详情' },
      },
      {
        path: 'abilities',
        name: 'Abilities',
        component: () => import('@/views/Abilities.vue'),
        meta: { title: '能力体系' },
      },
      {
        path: 'realms',
        name: 'Realms',
        component: () => import('@/views/Realms.vue'),
        meta: { title: '境界等级' },
      },
      {
        path: 'creatures',
        name: 'Creatures',
        component: () => import('@/views/Creatures.vue'),
        meta: { title: '异兽图鉴' },
      },
      {
        path: 'fragment-worlds',
        name: 'FragmentWorlds',
        component: () => import('@/views/FragmentWorlds.vue'),
        meta: { title: '碎片世界' },
      },
      {
        path: 'fragment-worlds/:id',
        name: 'FragmentWorldDetail',
        component: () => import('@/views/FragmentWorldDetail.vue'),
        meta: { title: '碎片世界详情' },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('@/views/History.vue'),
        meta: { title: '历史事件' },
      },
      {
        path: 'relations',
        name: 'Relations',
        component: () => import('@/views/Relations.vue'),
        meta: { title: '关系网络' },
      },
      {
        path: 'lore/:slug',
        name: 'LorePage',
        component: () => import('@/views/LorePage.vue'),
        meta: { title: '设定详情' },
      },
      {
        path: 'origin-laws',
        name: 'OriginLaws',
        component: () => import('@/views/OriginLaws.vue'),
        meta: { title: '本源法则' },
      },
      {
        path: 'origin-laws/:id',
        name: 'OriginLawDetail',
        component: () => import('@/views/OriginLawDetail.vue'),
        meta: { title: '法则详情' },
      },
      {
        path: 'anomalies',
        name: 'Anomalies',
        component: () => import('@/views/Anomalies.vue'),
        meta: { title: '异常物' },
      },
      {
        path: 'anomalies/:id',
        name: 'AnomalyDetail',
        component: () => import('@/views/AnomalyDetail.vue'),
        meta: { title: '异常物详情' },
      },
    ],
  },

  // ==================== 后台管理路由 ====================
  {
    path: '/admin',
    component: () => import('@/components/admin/AdminLayout.vue'),
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '后台首页' },
      },
      {
        // 兼容旧链接：跳转到基础设定下的大世界管理
        path: 'worlds',
        redirect: '/admin/settings/worlds',
      },
      {
        path: 'factions',
        name: 'FactionEditor',
        component: () => import('@/views/admin/FactionEditor.vue'),
        meta: { title: '族群编辑' },
      },
      {
        path: 'characters',
        name: 'CharacterEditor',
        component: () => import('@/views/admin/CharacterEditor.vue'),
        meta: { title: '角色编辑' },
      },
      {
        path: 'artifacts',
        name: 'ArtifactEditor',
        component: () => import('@/views/admin/ArtifactEditor.vue'),
        meta: { title: '宝物编辑' },
      },
      {
        path: 'abilities',
        name: 'AbilityEditor',
        component: () => import('@/views/admin/AbilityEditor.vue'),
        meta: { title: '能力体系编辑' },
      },
      {
        path: 'creatures',
        name: 'CreatureEditor',
        component: () => import('@/views/admin/CreatureEditor.vue'),
        meta: { title: '异兽编辑' },
      },
      {
        path: 'fragment-worlds',
        name: 'FragmentWorldEditor',
        component: () => import('@/views/admin/FragmentWorldEditor.vue'),
        meta: { title: '碎片世界编辑' },
      },
    ],
  },

  // ==================== 基础设定路由（独立于后台数据编辑，通过右上角齿轮进入） ====================
  {
    path: '/admin/settings',
    component: () => import('@/components/admin/SettingsLayout.vue'),
    children: [
      {
        path: '',
        name: 'SettingsDashboard',
        component: () => import('@/views/admin/settings/SettingsDashboard.vue'),
        meta: { title: '基础设定' },
      },
      {
        path: 'worlds',
        name: 'SettingsWorldEditor',
        component: () => import('@/views/admin/WorldEditor.vue'),
        meta: { title: '大世界管理' },
      },
      {
        path: 'artifact-categories',
        name: 'ArtifactCategoryEditor',
        component: () => import('@/views/admin/settings/ArtifactCategoryEditor.vue'),
        meta: { title: '宝物种类' },
      },
      {
        path: 'faction-levels',
        name: 'FactionLevelEditor',
        component: () => import('@/views/admin/settings/FactionLevelEditor.vue'),
        meta: { title: '族群等级' },
      },
      {
        path: 'character-status',
        name: 'CharacterStatusEditor',
        component: () => import('@/views/admin/settings/CharacterStatusEditor.vue'),
        meta: { title: '角色状态' },
      },
      {
        path: 'realm-tiers',
        name: 'RealmTierEditor',
        component: () => import('@/views/admin/settings/RealmTierEditor.vue'),
        meta: { title: '境界等级' },
      },
    ],
  },

  // ==================== 404 页面 ====================
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' },
  },
]

const router = createRouter({
  // 使用构建 base 作为路由 base，以便在 GitHub Pages 子路径下正常工作
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 路由切换后滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

// 全局前置守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  const title = to.meta.title ? `${to.meta.title} - 异世界` : '异世界 - 世界观设定'
  document.title = title
  next()
})

export default router
