/**
 * 仿真管理API模块
 * 提供项目管理、智能体管理和仿真控制相关的API接口函数
 */

import request from './index'

/**
 * 获取所有项目列表
 * @param {string} statusFilter - 状态筛选条件
 * @returns {Promise} 返回项目列表的响应数据
 */
export function getProjects(statusFilter) {
  return request({
    url: '/simulation/project/list',
    method: 'get',
    params: { status: statusFilter }
  })
}

/**
 * 创建新项目
 * @param {Object} data - 项目数据
 * @returns {Promise} 返回创建项目的响应数据
 */
export function createProject(data) {
  return request({
    url: '/simulation/project',
    method: 'post',
    data
  })
}

/**
 * 获取项目详细信息
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回项目详细信息的响应数据
 */
export function getProject(projectId) {
  return request({
    url: `/simulation/project/${projectId}`,
    method: 'get'
  })
}

/**
 * 更新项目信息
 * @param {number} projectId - 项目ID
 * @param {Object} data - 项目数据
 * @returns {Promise} 返回更新后的项目响应数据
 */
export function updateProject(projectId, data) {
  return request({
    url: `/simulation/project/${projectId}`,
    method: 'put',
    data
  })
}

/**
 * 删除项目
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回删除项目的响应数据
 */
export function deleteProject(projectId) {
  return request({
    url: `/simulation/project/${projectId}`,
    method: 'delete'
  })
}

/**
 * 向项目添加智能体
 * @param {number} projectId - 项目ID
 * @param {Object} data - 智能体数据
 * @returns {Promise} 返回添加智能体的响应数据
 */
export function addAgent(projectId, data) {
  return request({
    url: `/simulation/project/${projectId}/agent`,
    method: 'post',
    data
  })
}

/**
 * 获取项目中的智能体列表
 * @param {number} projectId - 项目ID
 * @param {Object} filters - 查询筛选条件
 * @returns {Promise} 返回智能体列表的响应数据
 */
export function getAgents(projectId, filters) {
  return request({
    url: `/simulation/project/${projectId}/agent/list`,
    method: 'get',
    params: filters
  })
}

/**
 * 获取智能体详细信息
 * @param {number} projectId - 项目ID
 * @param {number} agentId - 智能体ID
 * @returns {Promise} 返回智能体详细信息的响应数据
 */
export function getAgent(projectId, agentId) {
  return request({
    url: `/simulation/project/${projectId}/agent/${agentId}`,
    method: 'get'
  })
}

/**
 * 更新智能体信息
 * @param {number} projectId - 项目ID
 * @param {number} agentId - 智能体ID
 * @param {Object} data - 智能体数据
 * @returns {Promise} 返回更新后的智能体响应数据
 */
export function updateAgent(projectId, agentId, data) {
  return request({
    url: `/simulation/project/${projectId}/agent/${agentId}`,
    method: 'put',
    data
  })
}

/**
 * 删除智能体
 * @param {number} projectId - 项目ID
 * @param {number} agentId - 智能体ID
 * @returns {Promise} 返回删除智能体的响应数据
 */
export function deleteAgent(projectId, agentId) {
  return request({
    url: `/simulation/project/${projectId}/agent/${agentId}`,
    method: 'delete'
  })
}

/**
 * 启动仿真
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回启动仿真的响应数据
 */
export function startSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/start`,
    method: 'post'
  })
}

/**
 * 单步执行仿真
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回单步执行的响应数据
 */
export function stepSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/step`,
    method: 'post'
  })
}

/**
 * 暂停仿真
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回暂停仿真的响应数据
 */
export function pauseSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/pause`,
    method: 'post'
  })
}

/**
 * 恢复仿真
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回恢复仿真的响应数据
 */
export function resumeSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/resume`,
    method: 'post'
  })
}

/**
 * 停止仿真
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回停止仿真的响应数据
 */
export function stopSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/stop`,
    method: 'post'
  })
}

/**
 * 重置仿真
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回重置仿真的响应数据
 */
export function resetSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/reset`,
    method: 'post'
  })
}

/**
 * 获取轮次详细信息
 * @param {number} projectId - 项目ID
 * @param {number} roundNum - 轮次编号
 * @returns {Promise} 返回轮次详细信息的响应数据
 */
export function getRoundDetail(projectId, roundNum) {
  return request({
    url: `/simulation/${projectId}/round/${roundNum}`,
    method: 'get'
  })
}

/**
 * 获取指定轮次的LLM调用日志
 * @param {number} projectId - 项目ID
 * @param {number} roundNum - 轮次编号
 * @returns {Promise} 返回LLM调用日志的响应数据
 */
export function getLLMPrompts(projectId, roundNum) {
  return request({
    url: `/simulation/project/${projectId}/round/${roundNum}/llm-prompts`,
    method: 'get'
  })
}
