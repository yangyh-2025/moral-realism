// API and data types for Moral Realism ABM System

export enum LeadershipType {
  WANGDAO = 'wangdao',
  HEGEMON = 'hegemon',
  QIANGQUAN = 'qiangquan',
  HUNYONG = 'hunyong',
}

export enum AgentType {
  GREAT_POWER = 'great_power',
  SMALL_STATE = 'small_state',
  ORGANIZATION = 'organization',
  CONTROLLER = 'controller',
}

export enum ControllerStatus {
  NOT_INITIALIZED = 'not_initialized',
  INITIALIZED = 'initialized',
  READY = 'ready',
  RUNNING = 'running',
  PAUSED = 'paused',
  STOPPED = 'stopped',
  COMPLETED = 'completed',
  ERROR = 'error',
}

export enum OrderType {
  MULTIPOLAR = 'multipolar',
  BIPOLAR = 'bipolar',
  UNIPOLAR_HEGEMONIC = 'unipolar_hegemonic',
  HIERARCHICAL = 'hierarchical',
}

export interface HardPowerConfig {
  military_capability: number;
  nuclear_capability: number;
  conventional_forces: number;
  force_projection: number;
  gdp_share: number;
  economic_growth: number;
  trade_volume: number;
  financial_influence: number;
  technology_level: number;
  military_technology: number;
  innovation_capacity: number;
  energy_access: number;
  strategic_materials: number;
}

export interface SoftPowerConfig {
  discourse_power: number;
  narrative_control: number;
  media_influence: number;
  allies_count: number;
  ally_strength: number;
  network_position: number;
  diplomatic_support: number;
  moral_legitimacy: number;
  cultural_influence: number;
  un_influence: number;
  institutional_leadership: number;
}

export interface CapabilityConfig {
  hard_power: HardPowerConfig;
  soft_power: SoftPowerConfig;
}

export interface CapabilityResponse {
  hard_power_index: number;
  soft_power_index: number;
  capability_index: number;
  tier: string;
  hard_power_details: HardPowerConfig;
  soft_power_details: SoftPowerConfig;
}

export interface Agent {
  agent_id: string;
  name: string;
  name_zh: string;
  agent_type: AgentType;
  leadership_type: LeadershipType;
  leadership_name: string | undefined;
  capability_tier: string | undefined;
  capability_index: number | undefined;
  is_active: boolean;
  is_alive: boolean;
  history_length: number;
  relations_count: number;
}

export interface AgentCreateRequest {
  agent_id: string;
  name: string;
  name_zh: string;
  agent_type: AgentType;
  leadership_type: LeadershipType;
  capability: CapabilityConfig | undefined;
  is_active: boolean | undefined;
}

export interface SimulationConfig {
  max_rounds: number;
  event_probability: number;
  checkpoint_interval: number;
  checkpoint_dir: string;
  log_level: string;
}

export interface ControllerState {
  current_round: number;
  is_running: boolean;
  is_paused: boolean;
  total_decisions: number;
  total_interactions: number;
  event_count: number;
}

export interface SimulationStatus {
  status: ControllerStatus;
  config: SimulationConfig;
  state: ControllerState;
  agent_count: number;
  remaining_rounds: number;
}

export interface SystemMetrics {
  pattern_type: string;
  power_concentration: number;
  order_stability: number;
  norm_consensus: number;
  public_goods_level: number;
  order_type: string;
}

export interface MetricsResponse {
  timestamp: string;
  round: number;
  agent_count: number;
  agent_metrics: Record<string, unknown>;
  system_metrics: SystemMetrics;
  pattern_type: string;
}

export interface Checkpoint {
  checkpoint_id: string;
  timestamp: string;
  round: number | undefined;
  agent_count: number | undefined;
}

export interface WSMessage {
  type: string;
  timestamp: string | undefined;
  [key: string]: unknown;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export interface ApiConfig {
  api_key: string;
  model: string;
  base_url: string;
  timeout: number;
}

export interface Norm {
  norm_id: string;
  name: string;
  name_zh: string;
  description: string;
  category: string;
  strength: number;
  origin_country: string;
  adoption_level: number;
}

export interface SystemicEvent {
  event_id: string;
  event_type: string;
  description: string;
  description_zh: string;
  participants: string[];
  impact_level: number;
  round: number;
  timestamp: string;
}

export interface SystemicInteractionEvent {
  event_type: string;
  data: {
    order_type?: string;
    norms?: Norm[];
    event?: SystemicEvent;
    round?: number;
    evolution?: {
      round: number;
      norms: Norm[];
    }[];
  };
  timestamp: string;
}
