/**
 * 统计数据API模块
 * 提供仿真结果统计相关的API接口函数
 */

import request from './index'

/**
 * 获取权力历史数据
 * @param {number} projectId - 项目ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回权力历史数据的响应
 */
export function getPowerHistory(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/power-history`,
    method: 'get',
    params
  })
}

/**
 * 获取权力增长率数据
 * @param {number} projectId - 项目ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回权力增长率数据的响应
 */
export function getPowerGrowthRate(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/power-growth-rate`,
    method: 'get',
    params
  })
}

/**
 * 获取行为偏好数据
 * @param {number} projectId - 项目ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回行为偏好数据的响应
 */
export function getActionPreference(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/action-preference`,
    method: 'get',
    params
  })
}

/**
 * 获取秩序演化数据
 * @param {number} projectId - 项目ID
 * @returns {Promise} 返回秩序演化数据的响应
 */
export function getOrderEvolution(projectId) {
  return request({
    url: `/simulation/${projectId}/stats/order-evolution`,
    method: 'get'
  })
}

/**
 * 获取轮次详细数据
 * @param {number} projectId - 项目ID
 * @param {number} roundNum - 轮次编号
 * @returns {Promise} 返回轮次详细数据的响应
 */
export function getRoundDetail(projectId, roundNum) {
  return request({
    url: `/simulation/${projectId}/stats/round-detail`,
    method: 'get',
    params: { round_num: roundNum }
  })
}

/**
 * 获取目标评估数据
 * @param {number} projectId - 项目ID
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回目标评估数据的响应
 */
export function getGoalEvaluations(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/goal-evaluations`,
    method: 'get',
    params
  })
}

/**
 * 获取特定智能体的目标评估趋势
 * @param {number} projectId - 项目ID
 * @param {number} agentId - 智能体ID
 * @returns {Promise} 返回目标评估趋势数据的响应
 */
export function getGoalEvaluationTrend(projectId, agentId) {
  return request({
    url: `/simulation/${projectId}/stats/goal-evaluation-trend/${agentId}`,
    method: 'get'
  })
}

/**
 * 获取智能体关系图谱数据
 * @param {number} projectId - 项目ID
 * @param {number} roundNum - 可选，指定轮次
 * @returns {Promise} 返回关系图谱数据的响应
 */
export function getAgentRelations(projectId, roundNum) {
  console.log('请求关系数据 - projectId:', projectId, 'roundNum:', roundNum)
  return request({
    url: `/simulation/${projectId}/stats/agent-relations`,
    method: 'get',
    params: { round_num: roundNum }
  }).then(res => {
    console.log('关系数据响应:', res)
    return res
  })
}
