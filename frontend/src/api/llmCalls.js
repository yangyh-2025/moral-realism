import request from './index'

export function getLLMCalls(projectId, params = {}) {
  return request({
    url: `/llm-calls/project/${projectId}`,
    method: 'get',
    params
  })
}

export function getLLMCallDetail(callId) {
  return request({
    url: `/llm-calls/${callId}`,
    method: 'get'
  })
}
