// Zustand store for Moral Realism ABM frontend
import { create } from 'zustand';
import type {
  Agent,
  SimulationConfig,
  SimulationStatus,
  MetricsResponse,
  Checkpoint,
  LogEntry,
  ApiConfig,
  ControllerStatus,
} from '../types';

interface AppState {
  // Simulation state
  simulationStatus: SimulationStatus | null;
  isConnected: boolean;

  // Agents
  agents: Agent[];
  selectedAgent: Agent | null;

  // Configuration
  simulationConfig: SimulationConfig;
  apiConfig: ApiConfig;

  // Metrics
  currentMetrics: MetricsResponse | null;
  metricsHistory: MetricsResponse[];

  // Checkpoints
  checkpoints: Checkpoint[];

  // Logs
  logs: LogEntry[];
  logFilter: string | null;

  // UI state
  currentView: 'dashboard' | 'configuration' | 'agents' | 'monitor';

  // Actions
  setSimulationStatus: (status: SimulationStatus | null) => void;
  setIsConnected: (connected: boolean) => void;
  setAgents: (agents: Agent[]) => void;
  addAgent: (agent: Agent) => void;
  updateAgent: (agentId: string, updates: Partial<Agent>) => void;
  removeAgent: (agentId: string) => void;
  setSelectedAgent: (agent: Agent | null) => void;
  setSimulationConfig: (config: Partial<SimulationConfig>) => void;
  setApiConfig: (config: Partial<ApiConfig>) => void;
  setCurrentMetrics: (metrics: MetricsResponse | null) => void;
  addMetricsHistory: (metrics: MetricsResponse) => void;
  setCheckpoints: (checkpoints: Checkpoint[]) => void;
  addLog: (log: LogEntry) => void;
  clearLogs: () => void;
  setLogFilter: (filter: string | null) => void;
  setCurrentView: (view: 'dashboard' | 'configuration' | 'agents' | 'monitor') => void;
  resetSimulation: () => void;
}

const defaultSimulationConfig: SimulationConfig = {
  max_rounds: 100,
  event_probability: 0.2,
  checkpoint_interval: 10,
  checkpoint_dir: './data/checkpoints',
  log_level: 'INFO',
};

const defaultApiConfig: ApiConfig = {
  api_key: '',
  model: '',
  base_url: '',
  timeout: 30,
};

function loadApiConfigFromStorage(): Partial<ApiConfig> {
  try {
    const stored = localStorage.getItem('apiConfig');
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.error('Failed to load API config:', error);
  }
  return {};
}

function saveApiConfigToStorage(config: ApiConfig): void {
  try {
    localStorage.setItem('apiConfig', JSON.stringify(config));
  } catch (error) {
    console.error('Failed to save API config:', error);
  }
}

export const useStore = create<AppState>((set) => ({
  // Initial state
  simulationStatus: null,
  isConnected: false,
  agents: [],
  selectedAgent: null,
  simulationConfig: defaultSimulationConfig,
  apiConfig: { ...defaultApiConfig, ...loadApiConfigFromStorage() },
  currentMetrics: null,
  metricsHistory: [],
  checkpoints: [],
  logs: [],
  logFilter: null,
  currentView: 'dashboard',

  // Actions
  setSimulationStatus: (status) => set({ simulationStatus: status }),
  setIsConnected: (connected) => set({ isConnected: connected }),
  setAgents: (agents) => set({ agents }),
  addAgent: (agent) => set((state) => ({ agents: [...state.agents, agent] })),
  updateAgent: (agentId, updates) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.agent_id === agentId ? { ...agent, ...updates } : agent
      ),
    })),
  removeAgent: (agentId) =>
    set((state) => ({
      agents: state.agents.filter((agent) => agent.agent_id !== agentId),
    })),
  setSelectedAgent: (agent) => set({ selectedAgent: agent }),
  setSimulationConfig: (config) =>
    set((state) => ({
      simulationConfig: { ...state.simulationConfig, ...config },
    })),
  setApiConfig: (config) => {
    const newConfig = { ...useStore.getState().apiConfig, ...config };
    set({ apiConfig: newConfig });
    saveApiConfigToStorage(newConfig);
  },
  setCurrentMetrics: (metrics) => set({ currentMetrics: metrics }),
  addMetricsHistory: (metrics) =>
    set((state) => ({
      metricsHistory: [...state.metricsHistory.slice(-100), metrics],
    })),
  setCheckpoints: (checkpoints) => set({ checkpoints }),
  addLog: (log) =>
    set((state) => ({
      logs: [...state.logs.slice(-500), log],
    })),
  clearLogs: () => set({ logs: [] }),
  setLogFilter: (filter) => set({ logFilter: filter }),
  setCurrentView: (view) => set({ currentView: view }),
  resetSimulation: () =>
    set({
      simulationStatus: null,
      currentMetrics: null,
      metricsHistory: [],
      logs: [],
    }),
}));
