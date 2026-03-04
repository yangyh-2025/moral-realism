"""
API请求/响应模型的Pydantic架构定义

本模块定义FastAPI使用的所有数据模型，包括：
- 代理配置模型（AgentCreateRequest, AgentUpdateRequest）
- 模拟参数配置（SimulationConfigRequest）
- 能力配置（HardPowerConfig, SoftPowerConfig, CapabilityConfig）
- 响应模型（各种响应类型）
- WebSocket消息模型
- 导出模型

所有模型使用Pydantic进行自动验证和序列化。
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# ============================================================================
# 枚举类型定义
# ============================================================================

class LeadershipType(str, Enum):
    """
    领导类型枚举

    基于道义现实主义理论的四种领导类型：
    - WANGDAO: 道义型领导
    - HEGEMON: 传统霸权
    - QIANGQUAN: 强权型领导
    - HUNYONG: 混合型/合作型领导
    """
    WANGDAO = "wangdao"
    HEGEMON = "hegemon"
    QIANGQUAN = "qiangquan"
    HUNYONG = "hunyong"


class AgentType(str, Enum):
    """
    代理类型枚举

    定义模拟中不同类型的代理：
    - GREAT_POWER: 大国
    - SMALL_STATE: 小国
    - ORGANIZATION: 国际组织
    - CONTROLLER: 控制者/实验者
    """
    GREAT_POWER = "great_power"
    SMALL_STATE = "small_state"
    ORGANIZATION = "organization"
    CONTROLLER = "controller"


class ControllerStatus(str, Enum):
    """
    模拟控制器状态枚举

    定义控制器的各种可能状态
    """
    NOT_INITIALIZED = "not_initialized"  # 未初始化
    INITIALIZED = "initialized"  # 已初始化
    READY = "ready"  # 准备就绪
    RUNNING = "running"  # 运行中
    PAUSED = "paused"  # 已暂停
    STOPPED = "stopped"  # 已停止
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 错误状态


class CapabilityTier(str, Enum):
    """
    能力层级枚举

    根据综合能力指数将国家划分为5个等级：
    - T0_SUPERPOWER: 超级大国
    - T1_GREAT_POWER: 大国
    - T2_REGIONAL: 区域性大国
    - T3_MEDIUM: 中等国家
    - T4_SMALL: 小国
    """
    T0_SUPERPOWER = "t0_superpower"
    T1_GREAT_POWER = "t1_great_power"
    T2_REGIONAL = "t2_regional"
    T3_MEDIUM = "t3_medium"
    T4_SMALL = "t4_small"


# ============================================================================
# 请求模型定义
# ============================================================================

class HardPowerConfig(BaseModel):
    """
    硬权力配置请求模型

    定义代理硬实力的各维度配置
    """
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
    """
    软权力配置请求模型

    定义代理软实力的各维度配置
    """
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
    """
    能力配置请求模型

    包含硬实力和软实力的完整配置
    """
    hard_power: HardPowerConfig = Field(default_factory=HardPowerConfig)
    soft_power: SoftPowerConfig = Field(default_factory=SoftPowerConfig)


class AgentCreateRequest(BaseModel):
    """
    代理创建请求模型

    用于创建新代理的API请求
    """
    agent_id: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    name_zh: str = Field(..., min_length=1, max_length=200)
    agent_type: AgentType
    leadership_type: LeadershipType
    capability: Optional[CapabilityConfig] = None
    is_active: bool = True


class AgentUpdateRequest(BaseModel):
    """
    代理更新请求模型

    用于更新现有代理的API请求
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    name_zh: Optional[str] = Field(None, min_length=1, max_length=200)
    leadership_type: Optional[LeadershipType] = None
    capability: Optional[CapabilityConfig] = None
    is_active: Optional[bool] = None


class SimulationConfigRequest(BaseModel):
    """
    模拟配置请求模型

    用于配置模拟运行参数的API请求
    """
    max_rounds: int = Field(default(default=100, ge=1, le=10000)
    event_probability: float = Field(default=0.2, ge=0, le=1)
    checkpoint_interval: int = Field(default=10, ge=0, le=1000)
    checkpoint_dir: str = Field(default="./data/checkpoints")
    log_level: str = Field(default="INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")


class ApiConfigRequest(BaseModel):
    """
    API配置请求模型

    用于配置API设置的请求
    """
    api_key: str = Field(default="")
    model: str = Field(default="")
    base_url: str = Field(default="")
    timeout: int = Field(default=30, ge=1, le=300)


# ============================================================================
# 响应模型定义
# ============================================================================

class HardPowerResponse(BaseModel):
    """
    硬权力响应模型

    返回代理的硬实力详细指标
    """
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
    """
    软权力响应模型

    返回代理的软实力详细指标
    """
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
    """
    能力响应模型

    返回代理的综合能力信息
    """
    hard_power_index: float
    soft_power_index: float
    capability_index: float
    tier: str
    hard_power_details: HardPowerResponse
    soft_power_details: SoftPowerResponse


class MoralMetricsResponse(BaseModel):
    """
    道德指标响应模型

    返回代理的道德相关指标
    """
    moral_index: float
    respect_for_norms: float
    humanitarian_concern: float
    peaceful_resolution: float
    international_cooperation: float
    justice_and_fairness: float


class SuccessMetricsResponse(BaseModel):
    """
    成功指标响应模型

    返回代理的行动成功率和关系指标
    """
    success_rate: float
    total_actions: int
    successful_actions: int
    avg_relationship: float
    friendly_relations: int
    hostile_relations: int
    neutral_relations: int


class AgentSummaryResponse(BaseModel):
    """
    代理摘要响应模型

    返回代理的基本信息摘要
    """
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
    """
    代理详细信息响应模型

    返回代理的完整详细信息
    """
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
    """
    系统级指标响应模型

    返回整个模拟系统的综合指标
    """
    pattern_type: str
    power_concentration: float
    order_stability: float
    norm_consensus: float
    public_goods_level: float
    order_type: str


class ControllerStateResponse(BaseModel):
    """
    控制器状态响应模型

    返回模拟控制器的当前状态
    """
    current_round: int
    is_running: bool
    is_paused: bool
    total_decisions: int
    total_interactions: int
    event_count: int


class ControllerStatsResponse(BaseModel):
    """
    控制器统计响应模型

    返回模拟控制器的执行统计信息
    """
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
    """
    模拟状态响应模型

    返回模拟的完整状态信息
    """
    status: str
    config: Dict[str, Any]
    state: ControllerStateResponse
    stats: ControllerStatsResponse
    agent_count: int
    remaining_rounds: int


class RoundResultResponse(BaseModel):
    """
    回合执行结果响应模型

    返回单次回合的执行结果
    """
    round: int
    is_successful: bool
    decisions_count: int
    interactions_executed: int
    events_generated: int
    execution_time: float
    timestamp: str


class MetricsResponse(BaseModel):
    """
    综合指标响应模型

    返回包含代理指标和系统指标的完整指标数据
    """
    timestamp: str
    round: int
    agent_count: int
    agent_metrics: Dict[str, Dict[str, Any]]
    system_metrics: SystemMetricsResponse
    pattern_type: str


class CheckpointResponse(BaseModel):
    """
    检查点响应模型

    返回检查点的基本信息
    """
    checkpoint_id: str
    timestamp: str
    round: Optional[int]
    agent_count: Optional[int]


class CheckpointListResponse(BaseModel):
    """
    检查点列表响应模型

    返回所有检查点的列表信息
    """
    checkpoints: List[CheckpointResponse]
    count: int


# ============================================================================
# WebSocket消息模型定义
# ============================================================================

class WSMessageType(str, Enum):
    """
    WebSocket消息类型枚举

    定义WebSocket通信中支持的消息类型
    """
    CONNECTED = "connected"  # 连接已建立
    ROUND_START = "round_start"  # 回合开始
    ROUND_COMPLETE = "round_complete"  # 回合完成
    SIMULATION_COMPLETE = "simulation_complete"  # 模拟完成
    ERROR = "error"  # 错误事件
    LOG = "log"  # 日志消息
    CHECKPOINT_SAVED = "checkpoint_saved"  # 检查点已保存
    METRICS_UPDATE = "metrics_update"  # 指标更新
    STATUS_UPDATE = "status_update"  # 状态更新


class WSConnected(BaseModel):
    """
    WebSocket连接已建立消息模型
    """
    type: WSMessageType = WSMessageType.CONNECTED
    simulation_id: str
    timestamp: str


class WSLogMessage(BaseModel):
    """
    WebSocket日志消息模型

    用于向客户端推送日志消息
    """
    type: WSMessageType = WSMessageType.LOG
    level: str
    message: str
    timestamp: str


class WSErrorMessage(BaseModel):
    """
    WebSocket错误消息模型

    用于向客户端推送错误信息
    """
    type: WSMessageType = WSMessageType.ERROR
    error: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str


# ============================================================================
# 导出模型定义
# ============================================================================

class ExportRequest(BaseModel):
    """
    数据导出请求模型

    用于请求导出模拟数据
    """
    data_type: str = Field(..., regex="^(csv|json|report)$")
    start_round: int = Field(default=0, ge=0)
    end_round: Optional[int] = Field(None, ge=0)
    format: str = Field(default="json", regex="^(csv|json)$")


class ExportResponse(BaseModel):
    """
    数据导出响应模型

    返回数据导出的结果信息
    """
    success: bool
    message: str
    filepath: Optional[str] = None
    download_url: Optional[str] = None
