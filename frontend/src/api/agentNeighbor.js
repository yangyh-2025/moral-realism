/**
 * 邻接关系 API 模块
 *
 * 邻接关系是 agent 之间的对子级地缘特征值（陆地或近海接壤），
 * 影响 prompt 中军事行为的成本估算与战略可达性判断。
 * 与战略关系不同，邻接关系是二元布尔值，且不受国力层级限制。
 */

import request from './index'

/**
 * 查询项目的邻接关系
 * @param {number} projectId - 项目ID
 * @param {number|null} agentId - 可选，若提供则返回该agent的邻接map，否则返回项目级双向矩阵
 * @returns {Promise} 返回邻接关系数据
 */
export function getAgentNeighbors(projectId, agentId = null) {
  return request({
    url: `/agent-neighbors/project/${projectId}`,
    method: 'get',
    params: agentId !== null && agentId !== undefined && agentId !== '' ? { agent_id: agentId } : {}
  })
}

/**
 * 设置两个智能体之间的邻接关系（单对，立即落库）
 * @param {number} projectId - 项目ID
 * @param {number} sourceId - 源智能体ID
 * @param {number} targetId - 目标智能体ID
 * @param {boolean} isNeighbor - 是否为邻国
 * @returns {Promise} 返回设置结果
 */
export function setAgentNeighbor(projectId, sourceId, targetId, isNeighbor) {
  return request({
    url: `/agent-neighbors/project/${projectId}`,
    method: 'post',
    data: {
      source_id: sourceId,
      target_id: targetId,
      is_neighbor: !!isNeighbor
    }
  })
}

/**
 * 用后端默认邻接矩阵初始化项目（场景1使用1913欧洲默认邻接）
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回初始化结果
 */
export function initializeAgentNeighbors(projectId) {
  return request({
    url: `/agent-neighbors/project/${projectId}/initialize`,
    method: 'post'
  })
}

/**
 * 批量保存邻接关系
 * @param {number} projectId - 项目ID
 * @param {Array<{source_id: number, target_id: number, is_neighbor: boolean}>} updates - 批量更新列表
 * @returns {Promise} 返回批量保存结果
 */
export function batchSetAgentNeighbors(projectId, updates) {
  return request({
    url: `/agent-neighbors/project/${projectId}/batch`,
    method: 'post',
    data: { updates }
  })
}
