<script setup>
/**
 * 页脚 (AppFooter) - 原神风格增强版
 *
 * 网站底部信息栏，包含：
 * - 带金色装饰的品牌标识
 * - 快速链接
 * - 装饰性分隔线
 * - 版权信息
 */
import { RouterLink } from 'vue-router'

const currentYear = new Date().getFullYear()

const footerLinks = [
  { name: '世界观总览', path: '/world-overview' },
  { name: '族群势力', path: '/factions' },
  { name: '英雄角色', path: '/characters' },
  { name: '神兵宝物', path: '/artifacts' },
  { name: '碎片世界', path: '/fragment-worlds' },
  { name: '后台管理', path: '/admin' },
]
</script>

<template>
  <footer class="app-footer">
    <!-- 顶部金色装饰线 -->
    <div class="app-footer__deco"></div>

    <div class="app-footer__inner">
      <!-- 品牌区 -->
      <div class="app-footer__brand">
        <div class="app-footer__brand-icon">✦</div>
        <span class="gold-shimmer-text app-footer__brand-name">残响界</span>
        <span class="app-footer__desc">世界观设定档案库 V3.0</span>
      </div>

      <!-- 装饰分隔线 -->
      <div class="ornate-divider app-footer__divider">
        <span class="ornate-divider__diamond"></span>
      </div>

      <!-- 链接区 -->
      <nav class="app-footer__links">
        <RouterLink
          v-for="link in footerLinks"
          :key="link.path"
          :to="link.path"
          class="footer-link"
        >
          {{ link.name }}
        </RouterLink>
      </nav>

      <!-- 版权 -->
      <div class="app-footer__copyright">
        <span class="copyright-deco">◆</span>
        © {{ currentYear }} 残响界 · 世界观设定档案库 · 仅供创作参考
        <span class="copyright-deco">◆</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.app-footer {
  background: linear-gradient(
    180deg,
    rgba(13, 21, 37, 0.9) 0%,
    rgba(6, 11, 20, 0.98) 100%
  );
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  margin-top: auto;
}

.app-footer__deco {
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--color-gold-dark) 20%,
    var(--color-gold-primary) 50%,
    var(--color-gold-dark) 80%,
    transparent 100%
  );
  box-shadow: 0 0 8px var(--color-gold-glow);
}

.app-footer__inner {
  max-width: var(--content-max-width);
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.app-footer__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.app-footer__brand-icon {
  color: var(--color-gold-primary);
  font-size: var(--font-size-2xl);
  text-shadow: 0 0 12px var(--color-gold-glow);
  animation: goldSparkle 3s ease-in-out infinite;
}

.app-footer__brand-name {
  font-family: var(--font-family-display);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  letter-spacing: 4px;
}

.app-footer__desc {
  font-size: var(--font-size-sm);
  color: var(--text-muted);
  letter-spacing: 2px;
}

.app-footer__divider {
  width: 60%;
  max-width: 400px;
}

.app-footer__links {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
  justify-content: center;
}

.footer-link {
  position: relative;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  text-decoration: none;
  transition: all var(--transition-fast);
  padding: 2px 4px;
}

.footer-link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  width: 0;
  height: 1px;
  background: var(--color-gold-primary);
  transform: translateX(-50%);
  transition: width var(--transition-fast);
}

.footer-link:hover {
  color: var(--text-gold);
  text-shadow: 0 0 6px var(--color-gold-glow);
}

.footer-link:hover::after {
  width: 100%;
}

.app-footer__copyright {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-xs);
  color: var(--text-muted);
  padding-top: var(--spacing-md);
  letter-spacing: 1px;
}

.copyright-deco {
  color: var(--color-gold-dark);
  font-size: 8px;
}

@media (max-width: 768px) {
  .app-footer__inner {
    padding: var(--spacing-lg) var(--spacing-md);
  }

  .app-footer__links {
    gap: var(--spacing-md);
  }

  .app-footer__divider {
    width: 80%;
  }
}
</style>
