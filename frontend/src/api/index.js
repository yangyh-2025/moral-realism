/**
 * API请求配置模块
 * 统一管理所有API请求的基础配置和拦截器
 */

import axios from 'axios'

/**
 * 创建Axios实例
 * 配置基础URL、超时时间和默认请求头
 */
const request = axios.create({
  baseURL: '/api/v1', // API基础路径
  timeout: 30000, // 请求超时时间（30秒）
  headers: {
    'Content-Type': 'application/json' // 默认请求内容类型
  }
})

/**
 * 请求拦截器
 * 在请求发送前对请求配置进行处理
 */
request.interceptors.request.use(
  config => {
    // 可以在这里添加请求前的处理逻辑，如添加认证token
    return config
  },
  error => {
    // 请求错误处理
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 在接收到响应后对响应数据进行处理
 */
request.interceptors.response.use(
  response => {
    // 打印响应日志，便于调试
    console.log('API Response:', {
      url: response.config.url,
      method: response.config.method,
      status: response.status,
      data: response.data
    })
    return response
  },
  error => {
    // 打印错误日志，便于排查问题
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    })
    return Promise.reject(error)
  }
)

export default request
