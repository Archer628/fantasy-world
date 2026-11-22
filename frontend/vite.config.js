import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

/**
 * Vite 构建配置
 * - Vue 3 单文件组件支持
 * - 路径别名 @ -> src/
 * - 开发服务器代理 API 请求到后端
 * - 设置 GITHUB_PAGES=1 时构建为 GitHub Pages 静态站点
 *   （base 变为 /fantasy-world/，并启用本地静态数据快照）
 */
const isGhPages = process.env.GITHUB_PAGES === '1'

export default defineConfig({
  base: isGhPages ? '/fantasy-world/' : '/',
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  define: {
    __USE_STATIC_DATA__: JSON.stringify(isGhPages),
  },
  server: {
    port: 7890,
    // 开发环境下将 /api 请求代理到后端服务
    proxy: {
      '/api': {
        target: 'http://localhost:9876',
        changeOrigin: true,
      },
    },
  },
})
