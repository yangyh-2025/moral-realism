/**
 * 系统配置API模块
 * 提供系统配置相关的API接口函数
 */

import request from './index'

/**
 * 获取系统配置
 * @returns {Promise} 返回系统配置的响应数据
 */
export function getSystemConfig() {
  return request({
    url: '/system/config',
    method: 'get'
  })
}

/**
 * 更新系统配置
 * @param {Object} data - 系统配置数据对象
 * @returns {Promise} 返回更新后的系统配置响应数据
 */
export function updateSystemConfig(data) {
  return request({
    url: '/system/config',
    method: 'put',
    data
  })
}
