/**
 * 战略关系API模块
 * 提供战略关系查询和设置接口
 */

import request from './index'

/**
 * 关系类型枚举
 */
export const RELATIONSHIP_TYPES = [
  { label: '战争关系', value: '战争关系', type: 'danger' },
  { label: '冲突关系', value: '冲突关系', type: 'warning' },
  { label: '无外交关系', value: '无外交关系', type: 'info' },
  { label: '伙伴关系', value: '伙伴关系', type: 'primary' },
  { label: '盟友关系', value: '盟友关系', type: 'success' }
]

/**
 * 获取项目的战略关系
 * @param {number} projectId - 项目ID
 * @param {number} agentId - 可选，特定智能体ID
 * @returns {Promise} 返回战略关系的响应数据
 */
export function getStrategicRelationships(projectId, agentId) {
  return request({
    url: `/strategic-relationships/project/${projectId}`,
    method: 'get',
    params: agentId && agentId !== '' ? { agent_id: agentId } : {}
  })
}

/**
 * 设置两个智能体之间的战略关系
 * @param {number} projectId - 项目ID
 * @param {number} sourceId - 源智能体ID
 * @param {number} targetId - 目标智能体ID
 * @param {string} relationshipType - 关系类型
 * @returns {Promise} 返回设置关系的响应数据
 */
export function setStrategicRelationship(projectId, sourceId, targetId, relationshipType) {
  return request({
    url: `/strategic-relationships/project/${projectId}`,
    method: 'post',
    data: {
      source_id: sourceId,
      target_id: targetId,
      relationship_type: relationshipType
    }
    // 设置正确的内容类型，FastAPI会自动解析表单数据
  })
}

/**
 * 初始化项目的战略关系
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回初始化关系的响应数据
 */
export function initializeStrategicRelationships(projectId) {
  return request({
    url: `/strategic-relationships/project/${projectId}/initialize`,
    method: 'post'
  })
}

/**
 * 获取关系类型对应的标签类型
 * @param {string} relationshipType - 关系类型
 * @returns {string} Element Plus 标签类型
 */
export function getRelationTagType(relationshipType) {
  const relation = RELATIONSHIP_TYPES.find(r => r.value === relationshipType)
  return relation ? relation.type : 'info'
}
