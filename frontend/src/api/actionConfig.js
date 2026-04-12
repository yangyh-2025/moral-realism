import request from './index'

/**
 * Get all action configs
 */
export function getActionConfigs() {
  return request({
    url: '/action-config/list',
    method: 'get'
  })
}

/**
 * Get action config detail
 */
export function getActionConfig(actionId) {
  return request({
    url: `/action-config/${actionId}`,
    method: 'get'
  })
}
