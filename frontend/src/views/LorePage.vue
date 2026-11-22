<script setup>
/**
 * 通用设定页面 (LorePage) - 原神风格
 *
 * 通过术语 slug 路由访问的通用设定页面
 * - 根据 slug 获取设定内容
 * - 左侧目录导航
 * - 右侧内容展示（使用 LoreLink）
 * - 底部相关术语链接
 *
 * 路由: /lore/:slug
 */
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useWorldDataStore } from '@/stores/worldData'
import { useAnimations } from '@/composables/useAnimations'
import LoreLink from '@/components/common/LoreLink.vue'

const route = useRoute()
const worldData = useWorldDataStore()
const { fadeInUp, slideInLeft } = useAnimations()

const pageRef = ref(null)
const leftRef = ref(null)
const rightRef = ref(null)
const lore = ref(null)
const loading = ref(true)
const activeSection = ref('')

/** 目录结构（从内容中提取或使用默认） */
const tableOfContents = computed(() => {
  if (!lore.value) return []
  // 如果后端提供了目录结构
  if (lore.value.sections && Array.isArray(lore.value.sections)) {
    return lore.value.sections
  }
  // 从内容中提取标题作为目录
  const content = lore.value.content || ''
  const headings = content.match(/^#{1,3}\s+.+$/gm) || []
  return headings.map((h, index) => {
    const level = h.match(/^#+/)[0].length
    const title = h.replace(/^#+\s+/, '')
    return { id: `section-${index}`, title, level }
  })
})

/** 根据 slug 加载设定内容 */
async function loadLore(slug) {
  loading.value = true
  lore.value = null
  try {
    const data = await worldData.loadLorePage(slug)
    lore.value = data
  } catch (err) {
    console.error('加载设定页面失败:', err)
  } finally {
    loading.value = false
    await nextTick()
    if (pageRef.value) fadeInUp(pageRef.value)
    if (leftRef.value) slideInLeft(leftRef.value, { delay: 0.1 })
    if (rightRef.value) fadeInUp(rightRef.value, { delay: 0.2 })
  }
}

/** 滚动到指定章节 */
function scrollToSection(sectionId) {
  activeSection.value = sectionId
  const el = document.getElementById(sectionId)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

onMounted(() => {
  loadLore(route.params.slug)
})

watch(() => route.params.slug, (newSlug) => {
  if (newSlug) loadLore(newSlug)
})
</script>

<template>
  <div ref="pageRef" class="page-content lore-page">
    <!-- 返回按钮 -->
    <RouterLink to="/" class="back-btn btn-genshin btn-genshin--secondary">
      <span class="back-btn__arrow">‹</span>
      返回首页
    </RouterLink>

    <!-- 加载状态 -->
    <div v-if="loading" class="empty-state">
      <div class="genshin-loader">
        <span class="genshin-loader__ring genshin-loader__ring--outer"></span>
        <span class="genshin-loader__ring genshin-loader__ring--inner"></span>
        <span class="genshin-loader__dot"></span>
      </div>
      <p class="empty-state__text">正在加载设定内容...</p>
    </div>

    <!-- 不存在 -->
    <div v-else-if="!lore" class="empty-state">
      <div class="empty-state__icon">📖</div>
      <p class="empty-state__text">该设定内容不存在</p>
      <RouterLink to="/" class="btn-genshin">返回首页</RouterLink>
    </div>

    <!-- 详情内容 -->
    <template v-else>
      <!-- 标题区域 -->
      <div class="lore-header">
        <div class="lore-header__deco">📖</div>
        <h1 class="lore-header__title gold-shimmer-text">{{ lore.title || lore.name || '设定详情' }}</h1>
        <div v-if="lore.category" class="lore-header__category">
          <span class="category-tag">{{ lore.category }}</span>
        </div>
        <div class="ornate-divider">
          <span class="ornate-divider__diamond"></span>
        </div>
      </div>

      <!-- 左右分栏布局 -->
      <div class="detail-body">
        <!-- 左侧：目录导航 -->
        <aside ref="leftRef" class="detail-left">
          <div v-if="tableOfContents.length > 0" class="card card-gold toc-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h3 class="toc-card__title">
              <span class="toc-card__deco">◆</span>
              目录导航
            </h3>

            <nav class="toc-nav">
              <a
                v-for="section in tableOfContents"
                :key="section.id"
                :href="`#${section.id}`"
                class="toc-nav__item"
                :class="{
                  'toc-nav__item--active': activeSection === section.id,
                  'toc-nav__item--level2': section.level === 2,
                  'toc-nav__item--level3': section.level >= 3,
                }"
                @click.prevent="scrollToSection(section.id)"
              >
                {{ section.title }}
              </a>
            </nav>
          </div>
        </aside>

        <!-- 右侧：内容展示 -->
        <main ref="rightRef" class="detail-right">
          <!-- 主要内容 -->
          <div v-if="lore.content || lore.description" class="card card-gold content-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="content-card__title">
              <span class="content-card__deco">◆</span>
              设定详情
            </h2>
            <div class="content-card__body">
              <LoreLink :text="lore.content || lore.description" tag="div" />
            </div>
          </div>

          <!-- 补充信息 -->
          <div v-if="lore.supplement || lore.extra" class="card card-gold content-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="content-card__title">
              <span class="content-card__deco">◆</span>
              补充信息
            </h2>
            <div class="content-card__body">
              <LoreLink :text="lore.supplement || lore.extra" tag="div" />
            </div>
          </div>

          <!-- 相关术语链接 -->
          <div v-if="lore.related && lore.related.length" class="card card-gold related-card">
            <span class="ornate-corner ornate-corner--tl"></span>
            <span class="ornate-corner ornate-corner--tr"></span>
            <span class="ornate-corner ornate-corner--bl"></span>
            <span class="ornate-corner ornate-corner--br"></span>

            <h2 class="related-card__title">
              <span class="related-card__deco">◆</span>
              相关设定
            </h2>
            <div class="related-list">
              <RouterLink
                v-for="item in lore.related"
                :key="item.slug || item.id"
                :to="`/lore/${item.slug || item.id}`"
                class="related-item"
              >
                <span class="related-item__icon">›</span>
                <span class="related-item__name">{{ item.title || item.name }}</span>
                <span v-if="item.category" class="related-item__category">{{ item.category }}</span>
              </RouterLink>
            </div>
          </div>
        </main>
      </div>
    </template>
  </div>
</template>

<style scoped>
.lore-page {
  padding-top: var(--spacing-xl);
}

/* 返回按钮 */
.back-btn {
  margin-bottom: var(--spacing-lg);
  align-self: flex-start;
}

.back-btn__arrow {
  font-size: var(--font-size-lg);
}

/* 标题区域 */
.lore-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.lore-header__deco {
  font-size: 40px;
  color: var(--color-gold-primary);
  text-shadow: 0 0 16px var(--color-gold-glow);
  margin-bottom: var(--spacing-sm);
}

.lore-header__title {
  font-family: var(--font-family-display);
  font-size: var(--font-size-4xl);
  letter-spacing: 4px;
  margin-bottom: var(--spacing-sm);
}

.lore-header__category {
  margin-bottom: var(--spacing-md);
}

.category-tag {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-lg);
  background: rgba(212, 168, 83, 0.1);
  border: 1px solid var(--color-gold-dark);
  color: var(--text-gold);
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-sm);
  letter-spacing: 2px;
}

/* 左右分栏 */
.detail-body {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: var(--spacing-xl);
}

.detail-left {
  position: sticky;
  top: calc(var(--header-height) + var(--spacing-lg));
  align-self: start;
}

/* 目录导航 */
.toc-card {
  padding: var(--spacing-lg);
}

.toc-card__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-lg);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color-light);
}

.toc-card__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.toc-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.toc-nav__item {
  display: block;
  padding: var(--spacing-xs) var(--spacing-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  border-radius: var(--border-radius-sm);
  border-left: 2px solid transparent;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.toc-nav__item:hover {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.08);
  border-left-color: var(--color-gold-dark);
  padding-left: calc(var(--spacing-sm) + 4px);
}

.toc-nav__item--active {
  color: var(--text-gold);
  background: rgba(212, 168, 83, 0.12);
  border-left-color: var(--color-gold-primary);
  text-shadow: 0 0 6px var(--color-gold-glow);
}

.toc-nav__item--level2 {
  padding-left: var(--spacing-md);
}

.toc-nav__item--level3 {
  padding-left: var(--spacing-lg);
  font-size: var(--font-size-xs);
}

/* 右侧内容 */
.content-card {
  padding: var(--spacing-xl);
  margin-bottom: var(--spacing-lg);
}

.content-card__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-sm);
  border-bottom: 1px solid var(--border-color-light);
}

.content-card__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.content-card__body {
  color: var(--text-primary);
  line-height: 2;
  font-size: var(--font-size-base);
}

/* 相关术语 */
.related-card {
  padding: var(--spacing-xl);
}

.related-card__title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-display);
  font-size: var(--font-size-xl);
  color: var(--text-gold);
  margin-bottom: var(--spacing-md);
}

.related-card__deco {
  color: var(--color-gold-primary);
  font-size: 10px;
}

.related-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.related-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(6, 11, 20, 0.4);
  border: 1px solid var(--border-color-light);
  border-radius: var(--border-radius-md);
  color: var(--text-link);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.related-item:hover {
  background: rgba(212, 168, 83, 0.1);
  border-color: var(--color-gold-dark);
  color: var(--color-gold-light);
  transform: translateX(4px);
  box-shadow: 0 0 12px rgba(212, 168, 83, 0.2);
}

.related-item__icon {
  color: var(--color-gold-primary);
  flex-shrink: 0;
}

.related-item__name {
  flex: 1;
}

.related-item__category {
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  padding: 2px 8px;
  background: rgba(13, 21, 37, 0.6);
  border-radius: var(--border-radius-sm);
}

@media (max-width: 968px) {
  .detail-body {
    grid-template-columns: 1fr;
  }

  .detail-left {
    position: static;
  }

  .lore-header__title {
    font-size: var(--font-size-3xl);
  }
}
</style>
