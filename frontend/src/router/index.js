import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import SimulationConfig from '../views/SimulationConfig.vue'
import SimulationConsole from '../views/SimulationConsole.vue'
import SimulationResults from '../views/SimulationResults.vue'
import AcademicStatistics from '../views/AcademicStatistics.vue'
import BehaviorSet from '../views/BehaviorSet.vue'
import SystemConfig from '../views/SystemConfig.vue'

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

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
