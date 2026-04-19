/**
 * 应用入口文件
 * 初始化Vue应用实例，注册插件和路由，并挂载到DOM
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

console.log('Starting Vue application...')

// 创建Vue应用实例
const app = createApp(App)

// 创建Pinia状态管理实例
const pinia = createPinia()

// 注册插件：Pinia状态管理
app.use(pinia)

// 注册插件：Vue Router路由管理
app.use(router)

// 注册插件：Element Plus UI组件库
app.use(ElementPlus)

console.log('Plugins registered, mounting app...')

// 将应用挂载到DOM中的#app元素上
const mountResult = app.mount('#app')
console.log('App mounted successfully!', mountResult)
