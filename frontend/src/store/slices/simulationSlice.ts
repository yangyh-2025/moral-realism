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
  round_duration: number;
  random_event_prob: number;
}

interface SimulationState {
  currentSimulation: Simulation | null;
  simulations: Simulation[];
  status: SimulationStatus;
  progress: ProgressInfo;
  isLoading: boolean;
  error: string | null;
}

const initialState: SimulationState = {
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
  async () => {
    const response = await simulationAPI.pause();
    return response.data;
  }
);

export const resumeSimulation = createAsyncThunk(
  'simulation/resume',
  async () => {
    const response = await simulationAPI.resume();
    return response.data;
  }
);

export const stopSimulation = createAsyncThunk(
  'simulation/stop',
  async () => {
    const response = await simulationAPI.stop();
    return response.data;
  }
);

export const resetSimulation = createAsyncThunk(
  'simulation/reset',
  async () => {
    const response = await simulationAPI.reset();
    return response.data;
  }
);

export const fetchSimulationState = createAsyncThunk(
  'simulation/fetchState',
  async () => {
    const response = await simulationAPI.getState();
    return response.data;
  }
);

const simulationSlice = createSlice({
  name: 'simulation',
  initialState,
  reducers: {
    setCurrentSimulation: (state, action: PayloadAction<Simulation | null>) => {
      state.currentSimulation = action.payload;
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
        state.status.is_running = true;
        state.status.is_paused = false;
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

    // Reset simulation
    builder
      .addCaseCase(resetSimulation.fulfilled, (state) => {
        state.status.current_round = 0;
        state.status.is_running = false;
        state.status.is_paused = false;
      })
      .addCase(resetSimulation.rejected, (state, action) => {
        state.error = action.error.message || '重置仿真失败';
      });

    // Fetch state
    builder
      .addCase(fetchSimulationState.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchState.fulfilled, (state, action) => {
        state.isLoading = false;
        state.status = action.payload;
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
} = simulationSlice.actions;

export default simulationSlice.reducer;
