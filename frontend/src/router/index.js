/**
 * 路由配置模块
 * 定义应用的所有路由规则和导航配置
 */

import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import SimulationConfig from '../views/SimulationConfig.vue'
import SimulationConsole from '../views/SimulationConsole.vue'
import BehaviorSet from '../views/BehaviorSet.vue'
import SystemConfig from '../views/SystemConfig.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '首页 · 预置场景' },
  },
  {
    path: '/history',
    name: 'SimulationHistory',
    component: () => import('../views/SimulationHistory.vue'),
    meta: { title: '历史任务' },
  },
  {
    path: '/config',
    name: 'SimulationConfig',
    component: SimulationConfig,
    meta: { title: '仿真配置' },
  },
  {
    path: '/console',
    name: 'SimulationConsole',
    component: SimulationConsole,
    meta: { title: '仿真控制台' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('../views/Analysis.vue'),
    meta: { title: '研究分析' },
  },
  // 兼容旧路径
  { path: '/results', redirect: '/analysis' },
  { path: '/statistics', redirect: '/analysis' },
  {
    path: '/behavior',
    name: 'BehaviorSet',
    component: BehaviorSet,
    meta: { title: '互动行为集' },
  },
  {
    path: '/system',
    name: 'SystemConfig',
    component: SystemConfig,
    meta: { title: '系统配置' },
  },
  {
    path: '/llm-calls',
    name: 'LLMCallLog',
    component: () => import('../views/LLMCallLog.vue'),
    meta: { title: 'LLM 调用记录' },
  },
  {
    path: '/dashboard',
    name: 'MultiSimDashboard',
    component: () => import('../views/MultiSimDashboard.vue'),
    meta: { title: '多项目监控面板' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
