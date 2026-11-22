import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// 导入全局样式
import './styles/variables.css'
import './styles/global.css'
import './styles/animations.css'

/**
 * 应用入口
 * - 创建 Vue 实例
 * - 注册 Pinia 状态管理
 * - 注册 Vue Router
 * - 挂载到 #app
 */
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
