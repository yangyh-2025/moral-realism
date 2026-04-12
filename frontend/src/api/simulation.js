import request from './index'

/**
 * Get all projects
 */
export function getProjects(statusFilter) {
  return request({
    url: '/simulation/project/list',
    method: 'get',
    params: { status: statusFilter }
  })
}

/**
 * Create project
 */
export function createProject(data) {
  return request({
    url: '/simulation/project',
    method: 'post',
    data
  })
}

/**
 * Get project detail
 */
export function getProject(projectId) {
  return request({
    url: `/simulation/project/${projectId}`,
    method: 'get'
  })
}

/**
 * Update project
 */
export function updateProject(projectId, data) {
  return request({
    url: `/simulation/project/${projectId}`,
    method: 'put',
    data
  })
}

/**
 * Delete project
 */
export function deleteProject(projectId) {
  return request({
    url: `/simulation/project/${projectId}`,
    method: 'delete'
  })
}

/**
 * Add agent to project
 */
export function addAgent(projectId, data) {
  return request({
    url: `/simulation/project/${projectId}/agent`,
    method: 'post',
    data
  })
}

/**
 * Get project agents
 */
export function getAgents(projectId, filters) {
  return request({
    url: `/simulation/project/${projectId}/agent/list`,
    method: 'get',
    params: filters
  })
}

/**
 * Get agent detail
 */
export function getAgent(projectId, agentId) {
  return request({
    url: `/simulation/project/${projectId}/agent/${agentId}`,
    method: 'get'
  })
}

/**
 * Update agent
 */
export function updateAgent(projectId, agentId, data) {
  return request({
    url: `/simulation/project/${projectId}/agent/${agentId}`,
    method: 'put',
    data
  })
}

/**
 * Delete agent
 */
export function deleteAgent(projectId, agentId) {
  return request({
    url: `/simulation/project/${projectId}/agent/${agentId}`,
    method: 'delete'
  })
}

/**
 * Start simulation
 */
export function startSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/start`,
    method: 'post'
  })
}

/**
 * Step simulation
 */
export function stepSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/step`,
    method: 'post'
  })
}

/**
 * Pause simulation
 */
export function pauseSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/pause`,
    method: 'post'
  })
}

/**
 * Resume simulation
 */
export function resumeSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/resume`,
    method: 'post'
  })
}

/**
 * Stop simulation
 */
export function stopSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/stop`,
    method: 'post'
  })
}

/**
 * Reset simulation
 */
export function resetSimulation(projectId) {
  return request({
    url: `/simulation/${projectId}/reset`,
    method: 'post'
  })
}
