import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('project', () => {
  const STORAGE_KEY = 'currentProjectId'
  const currentProjectId = ref(localStorage.getItem(STORAGE_KEY) || '')
  const projectList = ref([])
  const currentProjectMeta = ref(null)

  const currentProjectName = computed(() => {
    const p = projectList.value.find(
      x => x.id === currentProjectId.value || x.project_id === currentProjectId.value
    )
    return p ? (p.name || p.project_name || p.id) : ''
  })

  function setProjectId(id) {
    currentProjectId.value = id
    if (id) localStorage.setItem(STORAGE_KEY, id)
    else localStorage.removeItem(STORAGE_KEY)
  }

  async function fetchProjectList() {
    // TODO: 调用 presetScene 或 simulation API 拉取项目列表
    // 当前项目可能用 getSimulationHistory(),先留占位
    return projectList.value
  }

  function clearProject() {
    currentProjectId.value = ''
    localStorage.removeItem(STORAGE_KEY)
    currentProjectMeta.value = null
  }

  return {
    currentProjectId,
    projectList,
    currentProjectMeta,
    currentProjectName,
    setProjectId,
    fetchProjectList,
    clearProject,
  }
})
