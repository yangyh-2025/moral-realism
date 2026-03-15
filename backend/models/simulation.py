"""
仿真相关数据模型

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SimulationConfig(BaseModel):
    """仿真配置"""
    total_rounds: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="总轮数"
    )
    round_duration: int = Field(
        default=6,
        ge=1,
        le=12,
        description="每轮持续月数"
    )
    random_event_prob: float = Field(
        default=0.1,
        ge=0,
        le=1,
        description="随机事件概率"
    )
    checkpoint_interval: int = Field(
        default=10,
        ge=1,
        description="检查点保存间隔"
    )
    agent_configs: Optional[List[Dict]] = Field(
        default=None,
        description="智能体配置列表"
    )


class SimulationState(BaseModel):
    """仿真状态"""
    simulation_id: str = Field(..., description="仿真ID")
    current_round: int = Field(0, description="当前轮次")
    total_rounds: int = Field(100, description="总轮数")
    is_running: bool = Field(False, description="是否运行中")
    is_paused: bool = Field(False, description="是否暂停")
    power_pattern: str = Field("未判定", description="实力模式")
    order_type: str = Field("未判定", description="国际秩序类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    active_events: int = Field(0, description="活跃事件数")


class SimulationStartRequest(BaseModel):
    """启动仿真请求"""
    config: SimulationConfig = Field(..., description="仿真配置")
    simulation_id: Optional[str] = Field(None, description="仿真ID（可选）")
    name: Optional[str] = Field(None, description="仿真名称")
    description: Optional[str] = Field(None, description="仿真描述")


class SimulationStartResponse(BaseModel):
    """启动仿真响应"""
    simulation_id: str = Field(..., description="仿真ID")
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    state: SimulationState = Field(..., description="仿真状态")


class SimulationPauseRequest(BaseModel):
    """暂停仿真请求"""
    simulation_id: str = Field(..., description="仿真ID")


class SimulationResumeRequest(BaseModel):
    """继续仿真请求"""
    simulation_id: str = Field(..., description="仿真ID")


class SimulationStopRequest(BaseModel):
    """停止仿真请求"""
    simulation_id: str = Field(..., description="仿真ID")
    save_checkpoint: bool = Field(True, description="是否保存检查点")


class SimulationStateResponse(BaseModel):
    """获取仿真状态响应"""
    simulation_id: str = Field(..., description="仿真ID")
    state: SimulationState = Field(..., description="仿真状态")
    metrics: Optional[Dict[str, Any]] = Field(None, description="指标数据")
    agent_states: Optional[List[Dict]] = Field(None, description="智能体状态列表")


class SimulationListResponse(BaseModel):
    """仿真列表响应"""
    simulations: List[Dict] = Field(default_factory=list, description="仿真列表")
    total: int = Field(0, description="总数")


class ParallelSimulationConfig(BaseModel):
    """并行仿真配置"""
    name: str = Field(..., description="实验名称")
    description: Optional[str] = Field(None, description="实验描述")
    config_variants: List[Dict] = Field(..., description="配置变体列表")
    max_concurrent: int = Field(default=3, ge=1, description="最大并发数")
    timeout: int = Field(default=3600, ge=1, description="超时时间（秒）")


class ParallelSimulationStartResponse(BaseModel):
    """并行仿真启动响应"""
    batch_id: str = Field(..., description="批次ID")
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    total_tasks: int = Field(..., description="任务总数")


class ParallelSimulationProgressResponse(BaseModel):
    """并行仿真进度响应"""
    batch_id: str = Field(..., description="批次ID")
    total_tasks: int = Field(..., description="总任务数")
    completed_tasks: int = Field(..., description="已完成任务数")
    failed_tasks: int = Field(..., description="失败任务数")
    running_tasks: int = Field(..., description="运行中任务数")
    success_rate: float = Field(..., description="成功率")
    eta_seconds: Optional[float] = Field(None, description="预计剩余时间（秒）")
