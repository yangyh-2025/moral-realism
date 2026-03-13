/**
 * 仿真管理API
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import api from './api';

export interface SimulationConfig {
  total_rounds: number;
  round_duration: number;
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
  pause: async () => {
    return await api.post('/simulation/pause');
  },
  resume: async () => {
    return await api.post('/simulation/resume');
  },
  stop: async () => {
    return await api.post('/simulation/stop');
  },
  reset: async () => {
    return await api.post('/simulation/reset');
  },
  getState: async () => {
    const response = await api.get('/simulation/state/state');
    return response.data;
  },
};
