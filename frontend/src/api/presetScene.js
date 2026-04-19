/**
 * 预置场景API模块
 * 提供预置场景相关的API接口函数
 */

import request from './index'

/**
 * 获取所有预置场景列表
 * @returns {Promise} 返回包含所有预置场景的响应数据
 */
export function getPresetScenes() {
  return request({
    url: '/preset-scene/list',
    method: 'get'
  })
}

/**
 * 获取预置场景详细信息
 * @param {number} sceneId - 场景ID
 * @returns {Promise} 返回场景详细信息的响应数据
 */
export function getPresetScene(sceneId) {
  return request({
    url: `/preset-scene/${sceneId}`,
    method: 'get'
  })
}

/**
 * 从预置场景创建项目
 * @param {number} sceneId - 场景ID
 * @param {string} projectName - 项目名称
 * @param {string} projectDesc - 项目描述
 * @returns {Promise} 返回创建项目的响应数据
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
