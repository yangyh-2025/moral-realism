/**
 * 行为配置API模块
 * 提供互动行为配置相关的API接口函数
 */

import request from './index'

/**
 * 获取所有行为配置列表
 * @returns {Promise} 返回包含所有行为配置的响应数据
 */
export function getActionConfigs() {
  return request({
    url: '/action-config/list',
    method: 'get'
  })
}

/**
 * 获取行为配置详细信息
 * @param {number} actionId - 行为配置ID
 * @returns {Promise} 返回行为配置详细信息的响应数据
 */
export function getActionConfig(actionId) {
  return request({
    url: `/action-config/${actionId}`,
    method: 'get'
  })
}
