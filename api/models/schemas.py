"""
Pydantic schemas for API request/response models.

This module defines all data models used by the API including
agent configurations, simulation parameters, metrics, and checkpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# ============================================================================
# Enums
# ============================================================================

class LeadershipType(str, Enum):
    """Leadership types for agents."""
    WANGDAO = "wangdao"
    HEGEMON = "hegemon"
    QIANGQUAN = "qiangquan"
    HUNYONG = "hunyong"


class AgentType(str, Enum):
    """Agent types in the simulation."""
    GREAT_POWER = "great_power"
    SMALL_STATE = "small_state"
    ORGANIZATION = "organization"
    CONTROLLER = "controller"


class ControllerStatus(str, Enum):
    """Status of simulation controller."""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class CapabilityTier(str, Enum):
    """Capability tiers."""
    T0_SUPERPOWER = "t0_superpower"
    T1_GREAT_POWER = "t1_great_power"
    T2_REGIONAL = "t2_regional"
    T3_MEDIUM = "t3_medium"
    T4_SMALL = "t4_small"


# ============================================================================
# Request Models
# ============================================================================

class HardPowerConfig(BaseModel):
    """Hard power configuration."""
    military_capability: float = Field(default=50.0, ge=0, le=100)
    nuclear_capability: float = Field(default=0.0, ge=0, le=100)
    conventional_forces: float = Field(default=50.0, ge=0, le=100)
    force_projection: float = Field(default=50.0, ge=0, le=100)
    gdp_share: float = Field(default=2.0, ge=0, le=100)
    economic_growth: float = Field(default=3.0, ge=-10, le=20)
    trade_volume: float = Field(default=50.0, ge=0, le=100)
    financial_influence: float = Field(default=50.0, ge=0, le=100)
    technology_level: float = Field(default=50.0, ge=0, le=100)
    military_technology: float = Field(default=50.0, ge=0, le=100)
    innovation_capacity: float = Field(default=50.0, ge=0, le=100)
    energy_access: float = Field(default=50.0, ge=0, le=100)
    strategic_materials: float = Field(default=50.0, ge=0, le=100)


class SoftPowerConfig(BaseModel):
    """Soft power configuration."""
    discourse_power: float = Field(default=50.0, ge=0, le=100)
    narrative_control: float = Field(default=50.0, ge=0, le=100)
    media_influence: float = Field(default=50.0, ge=0, le=100)
    allies_count: int = Field(default=0, ge=0, le=50)
    ally_strength: float = Field(default=50.0, ge=0, le=100)
    network_position: float = Field(default=50.0, ge=0, le=100)
    diplomatic_support: float = Field(default=50.0, ge=0, le=100)
    moral_legitimacy: float = Field(default=50.0, ge=0, le=100)
    cultural_influence: float = Field(default=50.0, ge=0, le=100)
    un_influence: float = Field(default=50.0, ge=0, le=100)
    institutional_leadership: float = Field(default=50.0, ge=0, le=100)


class CapabilityConfig(BaseModel):
    """Capability configuration."""
    hard_power: HardPowerConfig = Field(default_factory=HardPowerConfig)
    soft_power: SoftPowerConfig = Field(default_factory=SoftPowerConfig)


class AgentCreateRequest(BaseModel):
    """Request to create an agent."""
    agent_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    name_zh: str = Field(..., min_length=1, max_length=200)
    agent_type: AgentType
    leadership_type: LeadershipType
    capability: Optional[CapabilityConfig] = None
    is_active: bool = True


class AgentUpdateRequest(BaseModel):
    """Request to update an agent."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=200)
    leadership_type: Optional[LeadershipType] = None
    capability: Optional[CapabilityConfig] = None
    is_active: Optional[bool] = None


class SimulationConfigRequest(BaseModel):
    """Request to configure simulation."""
    max_rounds: int = Field(default=100, ge=1, le=10000)
    event_probability: float = Field(default=0.2, ge=0, le=1)
    checkpoint_interval: int = Field(default=10, ge=0, le=1000)
    checkpoint_dir: str = Field(default="./data/checkpoints")
    log_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")


class ApiConfigRequest(BaseModel):
    """Request to configure API settings."""
    api_key: str = Field(default="")
    model: str = Field(default="")
    base_url: str = Field(default="")
    timeout: int = Field(default=30, ge=1, le=300)


# ============================================================================
# Response Models
# ============================================================================

class HardPowerResponse(BaseModel):
    """Hard power response."""
    military_capability: float
    nuclear_capability: float
    conventional_forces: float
    force_projection: float
    gdp_share: float
    economic_growth: float
    trade_volume: float
    financial_influence: float
    technology_level: float
    military_technology: float
    innovation_capacity: float
    energy_access: float
    strategic_materials: float
    hard_power_index: float


class SoftPowerResponse(BaseModel):
    """Soft power response."""
    discourse_power: float
    narrative_control: float
    media_influence: float
    allies_count: int
    ally_strength: float
    network_position: float
    diplomatic_support: float
    moral_legitimacy: float
    cultural_influence: float
    un_influence: float
    institutional_leadership: float
    soft_power_index: float


class CapabilityResponse(BaseModel):
    """Capability response."""
    hard_power_index: float
    soft_power_index: float
    capability_index: float
    tier: str
    hard_power_details: HardPowerResponse
    soft_power_details: SoftPowerResponse


class MoralMetricsResponse(BaseModel):
    """Moral metrics response."""
    moral_index: float
    respect_for_norms: float
    humanitarian_concern: float
    peaceful_resolution: float
    international_cooperation: float
    justice_and_fairness: float


class SuccessMetricsResponse(BaseModel):
    """Success metrics response."""
    success_rate: float
    total_actions: int
    successful_actions: int
    avg_relationship: float
    friendly_relations: int
    hostile_relations: int
    neutral_relations: int


class AgentSummaryResponse(BaseModel):
    """Agent summary response."""
    agent_id: str
    name: str
    name_zh: str
    agent_type: str
    leadership_type: str
    leadership_name: Optional[str]
    capability_tier: str
    capability_index: Optional[float]
    is_active: bool
    is_alive: bool
    history_length: int
    relations_count: int


class AgentDetailResponse(BaseModel):
    """Agent detail response."""
    agent_id: str
    name: str
    name_zh: str
    agent_type: str
    leadership_type: str
    leadership_name: Optional[str]
    is_active: bool
    is_alive: bool
    capability_metrics: Optional[CapabilityResponse]
    moral_metrics: Optional[MoralMetricsResponse]
    success_metrics: Optional[SuccessMetricsResponse]
    relations: Dict[str, float]


class SystemMetricsResponse(BaseModel):
    """System-level metrics response."""
    pattern_type: str
    power_concentration: float
    order_stability: float
    norm_consensus: float
    public_goods_level: float
    order_type: str


class ControllerStateResponse(BaseModel):
    """Controller state response."""
    current_round: int
    is_running: bool
    is_paused: bool
    total_decisions: int
    total_interactions: int
    event_count: int


class ControllerStatsResponse(BaseModel):
    """Controller statistics response."""
    total_rounds_executed: int
    total_rounds_scheduled: int
    successful_rounds: int
    failed_rounds: int
    checkpoints_saved: int
    checkpoints_loaded: int
    start_time: Optional[str]
    end_time: Optional[str]
    total_execution_time: float


class SimulationStatusResponse(BaseModel):
    """Simulation status response."""
    status: str
    config: Dict[str, Any]
    state: ControllerStateResponse
    stats: ControllerStatsResponse
    agent_count: int
    remaining_rounds: int


class RoundResultResponse(BaseModel):
    """Round execution result response."""
    round: int
    is_successful: bool
    decisions_count: int
    interactions_executed: int
    events_generated: int
    execution_time: float
    timestamp: str


class MetricsResponse(BaseModel):
    """Comprehensive metrics response."""
    timestamp: str
    round: int
    agent_count: int
    agent_metrics: Dict[str, Dict[str, Any]]
    system_metrics: SystemMetricsResponse
    pattern_type: str


class CheckpointResponse(BaseModel):
    """Checkpoint response."""
    checkpoint_id: str
    timestamp: str
    round: Optional[int]
    agent_count: Optional[int]


class CheckpointListResponse(BaseModel):
    """List of checkpoints response."""
    checkpoints: List[CheckpointResponse]
    count: int


# ============================================================================
# WebSocket Message Models
# ============================================================================

class WSMessageType(str, Enum):
    """WebSocket message types."""
    CONNECTED = "connected"
    ROUND_START = "round_start"
    ROUND_COMPLETE = "round_complete"
    SIMULATION_COMPLETE = "simulation_complete"
    ERROR = "error"
    LOG = "log"
    CHECKPOINT_SAVED = "checkpoint_saved"
    METRICS_UPDATE = "metrics_update"
    STATUS_UPDATE = "status_update"


class WSConnected(BaseModel):
    """WebSocket connected message."""
    type: WSMessageType = WSMessageType.CONNECTED
    simulation_id: str
    timestamp: str


class WSLogMessage(BaseModel):
    """WebSocket log message."""
    type: WSMessageType = WSMessageType.LOG
    level: str
    message: str
    timestamp: str


class WSErrorMessage(BaseModel):
    """WebSocket error message."""
    type: WSMessageType = WSMessageType.ERROR
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


# ============================================================================
# Export Models
# ============================================================================

class ExportRequest(BaseModel):
    """Request to export data."""
    data_type: str = Field(..., regex="^(csv|json|report)$")
    start_round: int = Field(default=0, ge=0)
    end_round: Optional[int] = Field(None, ge=0)
    format: str = Field(default="json", regex="^(csv|json)$")


class ExportResponse(BaseModel):
    """Export response."""
    success: bool
    message: str
    filepath: Optional[str] = None
    download_url: Optional[str] = None
