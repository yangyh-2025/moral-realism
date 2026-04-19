/**
 * 应用状态管理模块
 * 使用Pinia管理应用全局状态，包括当前项目、仿真配置、系统配置等
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 定义应用状态管理Store
 * @returns {Object} Store对象，包含状态和操作方法
 */
export const useAppStore = defineStore('app', () => {
  // 当前项目数据
  const currentProject = ref(null)

  // 当前项目ID
  const projectId = ref(null)

  // 仿真配置数据
  const simulationConfig = ref({
    projectName: '', // 项目名称
    projectDesc: '', // 项目描述
    totalRounds: 50, // 总轮次数
    agents: [] // 智能体列表
  })

  // 系统配置数据
  const systemConfig = ref({
    llmModelName: 'gpt-4', // LLM模型名称
    llmApiKey: '', // LLM API密钥
    llmApiBase: '', // LLM API基础地址
    llmTimeout: 120, // LLM超时时间（秒）
    llmMaxRetries: 3, // LLM最大重试次数
    simulationConcurrency: 5, // 仿真并发数
    logLevel: 'INFO', // 日志级别
    defaultSceneId: 1 // 默认场景ID
  })

  /**
   * 设置当前项目
   * @param {Object} project - 项目数据对象
   */
  function setCurrentProject(project) {
    currentProject.value = project
  }

  /**
   * 清除当前项目
   */
  function clearCurrentProject() {
    currentProject.value = null
  }

  /**
   * 更新系统配置
   * @param {Object} config - 系统配置数据
   */
  function updateSystemConfig(config) {
    Object.assign(systemConfig.value, config)
  }

  /**
   * 保存仿真配置到本地存储
   * @param {Object} config - 仿真配置数据
   */
  function saveSimulationConfig(config) {
    // 合并新旧配置
    simulationConfig.value = { ...simulationConfig.value, ...config }
    // 保存到localStorage
    localStorage.setItem('simulationConfig', JSON.stringify(simulationConfig.value))
  }

  /**
   * 从本地存储加载仿真配置
   * @returns {Object} 仿真配置对象
   */
  function loadSimulationConfig() {
    const saved = localStorage.getItem('simulationConfig')
    if (saved) {
      simulationConfig.value = JSON.parse(saved)
    }
    return simulationConfig.value
  }

  /**
   * 清除仿真配置和本地存储
   */
  function clearSimulationConfig() {
    // 重置为默认值
    simulationConfig.value = {
      projectName: '',
      projectDesc: '',
      totalRounds: 50,
      agents: []
    }
    // 从localStorage中移除
    localStorage.removeItem('simulationConfig')
  }

  /**
   * 设置项目ID并保存到本地存储
   * @param {number} id - 项目ID
   */
  function setProjectId(id) {
    projectId.value = id
    localStorage.setItem('currentProjectId', id)
  }

  /**
   * 从本地存储加载项目ID
   * @returns {number|null} 项目ID
   */
  function loadProjectId() {
    const saved = localStorage.getItem('currentProjectId')
    if (saved) {
      projectId.value = parseInt(saved)
    }
    return projectId.value
  }

  /**
   * 清除项目ID和本地存储
   */
  function clearProjectId() {
    projectId.value = null
    localStorage.removeItem('currentProjectId')
  }

  // 导出状态和方法供组件使用
  return {
    currentProject,
    projectId,
    simulationConfig,
    systemConfig,
    setCurrentProject,
    clearCurrentProject,
    updateSystemConfig,
    saveSimulationConfig,
    loadSimulationConfig,
    clearSimulationConfig,
    setProjectId,
    loadProjectId,
    clearProjectId
  }
})
