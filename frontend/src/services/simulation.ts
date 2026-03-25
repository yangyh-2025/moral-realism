/**
 * 仿真管理API
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import api from './api';

export interface SimulationConfig {
  total_rounds: number;
  round_duration_months: number;
  random_event_prob: number;
}

export interface SimulationState {
  current_round: number;
  active_events: number;
  power_pattern: string;
  order_type: string;
  is_running: boolean;
  is_paused: boolean;
}

export const simulationAPI = {
  start: async (config: SimulationConfig) => {
    return await api.post('/simulation/start', config);
  },
  pause: async (simulationId: string) => {
    return await api.post(`/simulation/pause/${simulationId}`);
  },
  resume: async (simulationId: string) => {
    return await api.post(`/simulation/resume/${simulationId}`);
  },
  stop: async (simulationId: string) => {
    return await api.post(`/simulation/stop/${simulationId}`);
  },
  getState: async (simulationId: string) => {
    return await api.get(`/simulation/state/${simulationId}`);
  },
  // 使用 create 和 delete 替代 reset
  create: async (config: SimulationConfig) => {
    return await api.post('/simulation/create', config);
  },
  delete: async (simulationId: string) => {
    return await api.delete(`/simulation/${simulationId}`);
  },
};
