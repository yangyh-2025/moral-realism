# 全局配置类
"""
定义系统的全局配置，包括仿真配置、智能体配置和LLM配置。
使用Pydantic v2进行数据验证。
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any, Union
from pathlib import Path

from .leader_types import LeaderType
from .order_types import InternationalOrderType
from .event_config import EventConfig


class LLMConfig(BaseModel):
    """LLM配置类"""

    # LLM提供商
    provider: str = Field(default="siliconflow",
                           description="LLM服务提供商")

    # 模型名称
    model: str = Field(default="deepseek-v3-32b",
                        description="LLM模型名称")

    # API密钥列表（支持多密钥轮换）
    api_keys: List[str] = Field(default_factory=list,
                                 description="LLM API密钥列表，支持多密钥")

    # API基础URL
    base_url: Optional[str] = Field(
        default="https://api.siliconflow.cn/v1",
        description="LLM API基础URL"
    )

    # 温度参数
    temperature: float = Field(default=0.7, ge=0, le=2,
                               description="LLM生成的温度参数")

    # 最大token数
    max_tokens: int = Field(default=2048, gt=0,
                             description="LLM生成的最大token数")

    # 请求超时时间（秒）
    timeout: int = Field(default=30, gt=0,
                          description="API请求超时时间")

    # 重试次数
    max_retries: int = Field(default=3, ge=0,
                              description="API请求失败时的最大重试次数")

    @field_validator('api_keys')
    @classmethod
    def validate_api_keys(cls, v: List[str]) -> List[str]:
        """验证API密钥列表不为空（如果启用LLM）"""
        if not v:
            raise ValueError("至少需要提供一个LLM API密钥")
        return v


class AgentConfig(BaseModel):
    """智能体配置类"""

    # 基础信息
    agent_id: str = Field(..., description="智能体唯一标识符")
    name: str = Field(..., description="智能体名称，通常为国家名")
    region: str = Field(..., description="智能体所属地区")

    # 领导人类型
    leader_type: Optional[LeaderType] = Field(
        default=None,
        description="领导人类型，可选"
    )

    # 实力指标
    power_metrics: Dict[str, Union[int, float]] = Field(
        default_factory=lambda: {
            "economic_power": 50,
            "military_power": 50,
            "political_power": 50,
            "technological_power": 50,
            "cultural_power": 50
        },
        description="智能体的各项实力指标"
    )

    # 初始盟友列表
    initial_allies: List[str] = Field(default_factory=list,
                                        description="初始盟友ID列表")

    # 初始对手列表
    initial_rivals: List[str] = Field(default_factory=list,
                                       description="初始对手ID列表")

    # 策略偏好
    strategy_preferences: Dict[str, float] = Field(
        default_factory=lambda: {
            "cooperation": 0.5,
            "competition": 0.5,
            "security_focus": 0.5,
            "economic_focus": 0.5
        },
        description="智能体的策略偏好权重"
    )

    # 是否启用LLM决策
    use_llm: bool = Field(default=True, description="是否使用LLM进行决策")

    @field_validator('agent_id')
    @classmethod
    def validate_agent_id(cls, v: str) -> str:
        """验证agent_id格式"""
        if not v.strip():
            raise ValueError("agent_id不能为空")
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """验证name不为空"""
        if not v.strip():
            raise ValueError("name不能为空")
        return v


class SimulationConfig(BaseModel):
    """仿真配置类"""

    # 仿真基本信息
    simulation_id: Optional[str] = Field(default=None,
                                          description="仿真唯一标识符")
    name: str = Field(default="未命名仿真", description="仿真名称")
    description: Optional[str] = Field(default=None,
                                         description="仿真描述")

    # 仿真回合数
    total_rounds: int = Field(default=10, gt=0, le=1000,
                               description="仿真的总回合数")

    # 当前回合数
    current_round: int = Field(default=0, ge=0,
                                description="当前回合数")

    # 国际秩序类型
    order_type: InternationalOrderType = Field(
        default=InternationalOrderType.BALANCE_OF_POWER,
        description="国际秩序类型"
    )

    # 参与智能体列表
    agents: List[AgentConfig] = Field(default_factory=list,
                                       description="参与仿真的智能体配置列表")

    # LLM配置
    llm_config: LLMConfig = Field(default_factory=LLMConfig,
                                   description="LLM配置")

    # 事件配置
    event_config: EventConfig = Field(default_factory=EventConfig,
                                        description="事件系统配置")

    # 数据存储路径
    storage_path: Optional[Path] = Field(default=None,
                                          description="数据存储路径")

    # 日志级别
    log_level: str = Field(default="INFO",
                            description="日志级别：DEBUG, INFO, WARNING, ERROR")

    # 是否启用并行决策
    enable_parallel_decision: bool = Field(
        default=True,
        description="是否启用智能体并行决策"
    )

    # 最大并发决策数
    max_concurrent_decisions: int = Field(default=5, gt=0,
                                            description="最大并发决策数")

    # 是否启用保存中间状态
    save_intermediate_states: bool = Field(
        default=True,
        description="是否保存每一轮的中间状态"
    )

    # 随机种子（用于可复现的仿真）
    random_seed: Optional[int] = Field(default=None,
                                        description="随机种子，用于可复现的仿真")

    @field_validator('total_rounds')
    @classmethod
    def validate_total_rounds(cls, v: int) -> int:
        """验证总回合数"""
        if v <= 0:
            raise ValueError("total_rounds必须大于0")
        return v

    def is_complete(self) -> bool:
        """检查仿真是否完成"""
        return self.current_round >= self.total_rounds

    def advance_round(self) -> None:
        """推进到下一回合"""
        self.current_round += 1

    def get_remaining_rounds(self) -> int:
        """获取剩余回合数"""
        return max(0, self.total_rounds - self.current_round)


# 默认配置
DEFAULT_CONFIG = SimulationConfig(
    name="默认道义现实主义仿真",
    description="基于道义现实主义理论的国际关系仿真",
    total_rounds=50,
    order_type=InternationalOrderType.BALANCE_OF_POWER,
    log_level="INFO"
)
