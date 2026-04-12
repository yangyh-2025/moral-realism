import { storeToRefs } from 'pinia'
import { useProjectStore } from '@/store/project'

export function useProject() {
  const store = useProjectStore()
  const { currentProjectId, projectList, currentProjectName, currentProjectMeta } =
    storeToRefs(store)
  return {
    currentProjectId,
    projectList,
    currentProjectName,
    currentProjectMeta,
    setProjectId: store.setProjectId,
    fetchProjectList: store.fetchProjectList,
    clearProject: store.clearProject,
  }
}
