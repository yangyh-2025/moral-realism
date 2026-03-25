/**
 * 仿真状态管理
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { simulationAPI } from '../../services/simulation';

export interface Simulation {
  id: string;
  name: string;
  total_rounds: number;
  current_round: number;
  status: 'idle' | 'running' | 'paused' | 'completed' | 'error';
  created_at: string;
  updated_at: string;
  description?: string;
}

export interface SimulationStatus {
  current_round: number;
  active_events: number;
  power_pattern: string;
  order_type: string;
  is_running: boolean;
  is_paused: boolean;
}

export interface ProgressInfo {
  current_round: number;
  total_rounds: number;
  percentage: number;
  estimated_time: number | null;
}

export interface SimulationConfig {
  total_rounds: number;
  round_duration_months: number;
  random_event_prob: number;
}

export interface LLMLogEntry {
  agent_id: string;
  agent_name: string;
  request_type: 'request' | 'response';
  content: string;
  round: number | null;
  timestamp: string;
}

export interface PowerDistribution {
  superpower: number;
  great_power: number;
  middle_power: number;
  small_power: number;
}

export interface RoundMetrics {
  round: number;
  power_concentration: number;
  power_concentration_index: number;
  international_norm_effectiveness: number;  // 后端返回的字段名
  conflict_level: number;
  institutionalization_index: number;  // 后端返回的字段名
  order_type: string;
  power_pattern: string;
  agent_powers: Record<string, number>;
  power_distribution: PowerDistribution;
}

export interface Interaction {
  round: number;
  initiator_id: string;
  target_id: string | null;
  interaction_type: string;
  action_content: string;  // 新增：行动的具体内容
  timestamp: string;
}

interface SimulationState {
  currentSimulationId: string | null;
  currentSimulation: Simulation | null;
  simulations: Simulation[];
  status: SimulationStatus;
  progress: ProgressInfo;
  llmLogs: LLMLogEntry[];
  // 仪表盘数据
  metricsHistory: RoundMetrics[];
  interactionsHistory: Interaction[];
  currentMetrics: RoundMetrics | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: SimulationState = {
  currentSimulationId: null,
  currentSimulation: null,
  simulations: [],
  status: {
    current_round: 0,
    active_events: 0,
    power_pattern: '未判定',
    order_type: '未判定',
    is_running: false,
    is_paused: false,
  },
  progress: {
    current_round: 0,
    total_rounds: 0,
    percentage: 0,
    estimated_time: null,
  },
  llmLogs: [],
  metricsHistory: [],
  interactionsHistory: [],
  currentMetrics: null,
  isLoading: false,
  error: null,
};

// 异步 Actions
export const startSimulation = createAsyncThunk(
  'simulation/start',
  async (config: SimulationConfig) => {
    const response = await simulationAPI.start(config);
    return response.data;
  }
);

export const pauseSimulation = createAsyncThunk(
  'simulation/pause',
  async (simulationId: string) => {
    const response = await simulationAPI.pause(simulationId);
    return response.data;
  }
);

export const resumeSimulation = createAsyncThunk(
  'simulation/resume',
  async (simulationId: string) => {
    const response = await simulationAPI.resume(simulationId);
    return response.data;
  }
);

export const stopSimulation = createAsyncThunk(
  'simulation/stop',
  async (simulationId: string) => {
    const response = await simulationAPI.stop(simulationId);
    return response.data;
  }
);

export const deleteSimulation = createAsyncThunk(
  'simulation/delete',
  async (simulationId: string) => {
    const response = await simulationAPI.delete(simulationId);
    return response.data;
  }
);

export const fetchSimulationState = createAsyncThunk(
  'simulation/fetchState',
  async (simulationId: string) => {
    const response = await simulationAPI.getState(simulationId);
    return response.data;
  }
);

const simulationSlice = createSlice({
  name: 'simulation',
  initialState,
  reducers: {
    setCurrentSimulation: (state, action: PayloadAction<Simulation | null>) => {
      state.currentSimulation = action.payload;
      state.currentSimulationId = action.payload?.id || null;
    },
    updateSimulation: (state, action: PayloadAction<Partial<Simulation>>) => {
      if (state.currentSimulation) {
        state.currentSimulation = { ...state.currentSimulation, ...action.payload };
      }
    },
    updateStatus: (state, action: PayloadAction<Partial<SimulationStatus>>) => {
      state.status = { ...state.status, ...action.payload };
    },
    updateProgress: (state, action: PayloadAction<Partial<ProgressInfo>>) => {
      state.progress = { ...state.progress, ...action.payload };
      state.progress.percentage = Math.round(
        (state.progress.current_round / state.progress.total_rounds) * 100
      );
    },
    clearError: (state) => {
      state.error = null;
    },
    addLLMLog: (state, action: PayloadAction<LLMLogEntry>) => {
      state.llmLogs.push(action.payload);
      // 限制日志数量为100条
      if (state.llmLogs.length > 100) {
        state.llmLogs = state.llmLogs.slice(-100);
      }
    },
    clearLLMLogs: (state) => {
      state.llmLogs = [];
    },
    // 更新当前轮次的指标
    updateMetrics: (state, action: PayloadAction<RoundMetrics>) => {
      state.currentMetrics = action.payload;
      // 添加到历史记录
      const existingIndex = state.metricsHistory.findIndex(m => m.round === action.payload.round);
      if (existingIndex >= 0) {
        state.metricsHistory[existingIndex] = action.payload;
      } else {
        state.metricsHistory.push(action.payload);
      }
      // 限制历史记录为100轮
      if (state.metricsHistory.length > 100) {
        state.metricsHistory = state.metricsHistory.slice(-100);
      }
    },
    // 添加互动记录
    addInteraction: (state, action: PayloadAction<Interaction>) => {
      state.interactionsHistory.push(action.payload);
      // 限制记录数量为200条
      if (state.interactionsHistory.length > 200) {
        state.interactionsHistory = state.interactionsHistory.slice(-200);
      }
    },
    // 清除仪表盘数据
    clearDashboardData: (state) => {
      state.metricsHistory = [];
      state.interactionsHistory = [];
      state.currentMetrics = null;
    },
  },
  extraReducers: (builder) => {
    // Start simulation
    builder
      .addCase(startSimulation.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(startSimulation.fulfilled, (state, action) => {
        state.isLoading = false;
        const data = action.payload;
        state.status.is_running = true;
        state.status.is_paused = false;

        // 清除旧的仪表盘数据
        state.metricsHistory = [];
        state.interactionsHistory = [];
        state.currentMetrics = null;

        // 设置当前仿真
        if (data.simulation_id) {
          state.currentSimulationId = data.simulation_id;
          state.currentSimulation = {
            id: data.simulation_id,
            name: '仿真',
            total_rounds: data.total_rounds || 100,
            current_round: data.completed_rounds || 0,
            status: data.status || 'running',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          // 更新进度
          state.progress.total_rounds = data.total_rounds || 100;
          state.progress.current_round = data.completed_rounds || 0;
          state.progress.percentage = Math.round(
            (state.progress.current_round / state.progress.total_rounds) * 100
          );
        }
      })
      .addCase(startSimulation.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || '启动仿真失败';
      });

    // Pause simulation
    builder
      .addCase(pauseSimulation.fulfilled, (state) => {
        state.status.is_paused = true;
      })
      .addCase(pauseSimulation.rejected, (state, action) => {
        state.error = action.error.message || '暂停仿真失败';
      });

    // Resume simulation
    builder
      .addCase(resumeSimulation.fulfilled, (state) => {
        state.status.is_paused = false;
      })
      .addCase(resumeSimulation.rejected, (state, action) => {
        state.error = action.error.message || '继续仿真失败';
      });

    // Stop simulation
    builder
      .addCase(stopSimulation.fulfilled, (state) => {
        state.status.is_running = false;
        state.status.is_paused = false;
      })
      .addCase(stopSimulation.rejected, (state, action) => {
        state.error = action.error.message || '停止仿真失败';
      });

    // Delete simulation
    builder
      .addCase(deleteSimulation.fulfilled, (state) => {
        state.currentSimulationId = null;
        state.currentSimulation = null;
        state.status.is_running = false;
        state.status.is_paused = false;
        state.status.current_round = 0;
      })
      .addCase(deleteSimulation.rejected, (state, action) => {
        state.error = action.error.message || '删除仿真失败';
      });

    // Fetch state
    builder
      .addCase(fetchSimulationState.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchSimulationState.fulfilled, (state, action) => {
        state.isLoading = false;
        // action.payload 是 axios 响应对象，需要访问 data 字段
        const data = action.payload?.data || action.payload;

        if (!data) {
          state.error = '获取仿真状态失败：响应数据为空';
          return;
        }

        // 保留 WebSocket 已更新的 order_type 和 power_pattern（如果后端返回未判定则不覆盖）
        const preserveOrderType = state.status.order_type && state.status.order_type !== '未判定';
        const preservePowerPattern = state.status.power_pattern && state.status.power_pattern !== '未判定';

        // 更新状态和进度
        state.status = {
          current_round: data.current_round || 0,
          active_events: data.active_events || 0,
          power_pattern: preservePowerPattern ? state.status.power_pattern : (data.power_pattern || '未判定'),
          order_type: preserveOrderType ? state.status.order_type : (data.order_type || '未判定'),
          is_running: data.is_running || false,
          is_paused: data.is_paused || false,
        };
        state.progress = {
          current_round: data.current_round || 0,
          total_rounds: data.total_rounds || 0,
          percentage: data.progress || 0,
          estimated_time: null,
        };
        // 同时更新当前仿真的进度
        if (state.currentSimulation) {
          state.currentSimulation.current_round = data.current_round || 0;
        }
      })
      .addCase(fetchSimulationState.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || '获取仿真状态失败';
      });
  },
});

export const {
  setCurrentSimulation,
  updateSimulation,
  updateStatus,
  updateProgress,
  clearError,
  addLLMLog,
  clearLLMLogs,
  updateMetrics,
  addInteraction,
  clearDashboardData,
} = simulationSlice.actions;

export default simulationSlice.reducer;
