/**
 * 路由配置模块
 * 定义应用的所有路由规则和导航配置
 */

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import SimulationConfig from '../views/SimulationConfig.vue'
import SimulationConsole from '../views/SimulationConsole.vue'
import SimulationResults from '../views/SimulationResults.vue'
import AcademicStatistics from '../views/AcademicStatistics.vue'
import BehaviorSet from '../views/BehaviorSet.vue'
import SystemConfig from '../views/SystemConfig.vue'

/**
 * 路由配置数组
 * 定义每个路径对应的组件和页面标题
 */
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 - 预置场景' }
  },
  {
    path: '/config',
    name: 'SimulationConfig',
    component: SimulationConfig,
    meta: { title: '仿真配置' }
  },
  {
    path: '/console',
    name: 'SimulationConsole',
    component: SimulationConsole,
    meta: { title: '仿真控制台' }
  },
  {
    path: '/results',
    name: 'SimulationResults',
    component: SimulationResults,
    meta: { title: '仿真结果' }
  },
  {
    path: '/statistics',
    name: 'AcademicStatistics',
    component: AcademicStatistics,
    meta: { title: '学术统计' }
  },
  {
    path: '/behavior',
    name: 'BehaviorSet',
    component: BehaviorSet,
    meta: { title: '互动行为集' }
  },
  {
    path: '/system',
    name: 'SystemConfig',
    component: SystemConfig,
    meta: { title: '系统配置' }
  }
]

/**
 * 创建路由实例
 * 使用HTML5 History模式，路由基于环境变量配置的基础URL
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
