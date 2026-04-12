import request from './index'

/**
 * Get all preset scenes
 */
export function getPresetScenes() {
  return request({
    url: '/preset-scene/list',
    method: 'get'
  })
}

/**
 * Get preset scene detail
 */
export function getPresetScene(sceneId) {
  return request({
    url: `/preset-scene/${sceneId}`,
    method: 'get'
  })
}

/**
 * Create project from preset scene
 */
export function createProjectFromScene(sceneId, projectName, projectDesc) {
  return request({
    url: `/preset-scene/${sceneId}/create-project`,
    method: 'post',
    data: {
      scene_id: sceneId,
      project_name: projectName,
      project_desc: projectDesc
    }
  })
}
