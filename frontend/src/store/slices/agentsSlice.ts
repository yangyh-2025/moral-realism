/**
 * 智能体状态管理
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';

export interface PowerMetrics {
  // 克莱因方程五要素
  // 物质要素
  C: number;  // 基本实体 (人口+领土) - 100分
  E: number;  // 经济实力 - 200分
  M: number;  // 军事实力 - 200分
  // 精神要素
  S: number;  // 战略目标 - 0.5-1分
  W: number;  // 国家意志 - 0.5-1分
  comprehensive_power: number;  // 综合国力 = (C+E+M) × (S+W)
}

export type PowerTier = 'superpower' | 'great_power' | 'middle_power' | 'small_power';

export type LeaderType = '王道型' | '霸权型' | '强权型' | '昏庸型';

export interface Agent {
  id: string;
  name: string;
  region: string;
  power_tier: PowerTier;
  leader_type?: LeaderType;
  power_metrics: PowerMetrics;
  strategic_interests: string[];
  current_support: number;
  alliances: string[];
}

export interface Relation {
  source_agent: string;
  target_agent: string;
  relation_type: 'alliance' | 'hostile' | 'neutral' | 'friendly';
  strength: number;  // 关系强度 -100 到 100
  duration: number;  // 关系持续轮次
}

interface AgentsState {
  agents: Agent[];
  selectedAgent: Agent | null;
  agentRelations: Record<string, Relation[]>;
  isLoading: boolean;
  error: string | null;
}

const initialState: AgentsState = {
  agents: [],
  selected: null,
  agentRelations: {},
  isLoading: false,
  error: null,
};

const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    setAgents: (state, action: PayloadAction<Agent[]>) => {
      state.agents = action.payload;
    },
    addAgent: (state, action: PayloadAction<Agent>) => {
      state.agents.push(action.payload);
    },
    updateAgent: (state, action: PayloadAction<Agent>) => {
      const index = state.agents.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.agents[index] = action.payload;
      }
    },
    deleteAgent: (state, action: PayloadAction<string>) => {
      state.agents = state.agents.filter(a => a.id !== action.payload);
      delete state.agentRelations[action.payload];
    },
    setSelectedAgent: (state, action: PayloadAction<Agent | null>) => {
      state.selectedAgent = action.payload;
    },
    updateAgentRelations: (state, action: PayloadAction<Record<string, Relation[]>>>) => {
      state.agentRelations = { ...state.agentRelations, ...action.payload };
    },
    updateAgentPower: (state, action: PayloadAction<{agentId: string; power: PowerMetrics}>) => {
      const { agentId, power } = action.payload;
      const agent = state.agents.find(a => a.id === agentId);
      if (agent) {
        agent.power_metrics = power;
      }
    },
    updateAgentSupport: (state, action: PayloadAction<{agentId: string; support: number}>) => {
      const { agentId, support } = action.payload;
      const agent = state.agents.find(a => a.id === agentId);
      if (agent) {
        agent.current_support = support;
      }
    },
  },
});

export const {
  setAgents,
  addAgent,
  updateAgent,
  deleteAgent,
  setSelectedAgent,
  updateAgentRelations,
  updateAgentPower,
  updateAgentSupport,
} = agentsSlice.actions;

export default agentsSlice.reducer;
