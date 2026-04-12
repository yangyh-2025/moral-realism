import request from './index'

/**
 * Get system config
 */
export function getSystemConfig() {
  return request({
    url: '/system/config',
    method: 'get'
  })
}

/**
 * Update system config
 */
export function updateSystemConfig(data) {
  return request({
    url: '/system/config',
    method: 'put',
    data
  })
}
