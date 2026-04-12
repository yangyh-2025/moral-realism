import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const currentProject = ref(null)
  const systemConfig = ref({
    llmModelName: 'gpt-4',
    llmApiKey: '',
    llmApiBase: '',
    llmTimeout: 120,
    llmMaxRetries: 3,
    simulationConcurrency: 5,
    logLevel: 'INFO',
    defaultSceneId: 1
  })

  function setCurrentProject(project) {
    currentProject.value = project
  }

  function clearCurrentProject() {
    currentProject.value = null
  }

  function updateSystemConfig(config) {
    Object.assign(systemConfig.value, config)
  }

  return {
    currentProject,
    systemConfig,
    setCurrentProject,
    clearCurrentProject,
    updateSystemConfig
  }
})
