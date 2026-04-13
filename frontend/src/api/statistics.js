import request from './index'

/**
 * Get power history
 */
export function getPowerHistory(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/power-history`,
    method: 'get',
    params
  })
}

/**
 * Get power growth rate
 */
export function getPowerGrowthRate(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/power-growth-rate`,
    method: 'get',
    params
  })
}

/**
 * Get action preference
 */
export function getActionPreference(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/action-preference`,
    method: 'get',
    params
  })
}

/**
 * Get order evolution
 */
export function getOrderEvolution(projectId) {
  return request({
    url: `/simulation/${projectId}/stats/order-evolution`,
    method: 'get'
  })
}

/**
 * Get round detail
 */
export function getRoundDetail(projectId, roundNum) {
  return request({
    url: `/simulation/${projectId}/stats/round-detail`,
    method: 'get',
    params: { round_num: roundNum }
  })
}

/**
 * Get goal evaluations
 */
export function getGoalEvaluations(projectId, params) {
  return request({
    url: `/simulation/${projectId}/stats/goal-evaluations`,
    method: 'get',
    params
  })
}

/**
 * Get goal evaluation trend for specific agent
 */
export function getGoalEvaluationTrend(projectId, agentId) {
  return request({
    url: `/simulation/${projectId}/stats/goal-evaluation-trend/${agentId}`,
    method: 'get'
  })
}
