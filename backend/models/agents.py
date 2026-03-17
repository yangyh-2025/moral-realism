"""
智能体相关数据模型

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class LeaderTypeEnum(str, Enum):
    """领导类型枚举"""
    WANGDAO = "wangdao"
    BAQUAN = "baquan"
    QIANGQUAN = "qiangquan"
    HUNYONG = "hunyong"
    NONE = "none"


class PowerTierEnum(str, Enum):
    """实力层级枚举"""
    SUPERPOWER = "superpower"
    GREAT_POWER = "great_power"
    MIDDLE_POWER = "middle_power"
    SMALL_POWER = "small_power"


class AgentTypeEnum(str, Enum):
    """智能体类型枚举"""
    STATE = "state"
    SMALL_STATE = "small_state"
    ORGANIZATION = "organization"


class Agent(BaseModel):
    """智能体"""
    id: str = Field(..., description="智能体ID")
    name: str = Field(..., description="智能体名称")
    region: str = Field(..., description="所属区域")
    agent_type: AgentTypeEnum = Field(..., description="智能体类型")
    power_tier: PowerTierEnum = Field(..., description="实力层级")
    leader_type: Optional[LeaderTypeEnum] = Field(None, description="领导类型")
    comprehensive_power: float = Field(0.0, ge=0, description="综合国力")
    strategic_reputation: float = Field(100.0, ge=0, le=100, description="战略声誉")
    decision_count: int = Field(0, ge=0, description="决策次数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class AgentConfig(BaseModel):
    """智能体配置"""
    id: str = Field(..., description="智能体ID")
    name: str = Field(..., description="智能体名称")
    region: str = Field(..., description="所属区域")
    agent_type: AgentTypeEnum = Field(default=AgentTypeEnum.STATE, description="智能体类型")
    critical_mass: float = Field(..., ge=0, le=100, description="临界质量")
    economic_capability: float = Field(..., ge=0, le=200, description="经济能力")
    military_capability: float = Field(..., ge=0, le=200, description="军事能力")
    strategic_purpose: float = Field(default=0.75, ge=0.5, le=1.0, description="战略目的")
    national_will: float = Field(default=0.8, ge=0.5, le=1.0, description="国家意志")
    leader_type: Optional[LeaderTypeEnum] = Field(None, description="领导类型")


class AgentCreateRequest(BaseModel):
    """创建智能体请求"""
    config: AgentConfig = Field(..., description="智能体配置")


class AgentUpdateRequest(BaseModel):
    """更新智能体请求"""
    agent_id: str = Field(..., description="智能体ID")
    updates: Dict[str, Any] = Field(..., description="更新字段")


class AgentDeleteRequest(BaseModel):
    """删除智能体请求"""
    agent_id: str = Field(..., description="智能体ID")


class AgentGetRequest(BaseModel):
    """获取获取智能体请求"""
    agent_id: str = Field(..., description="智能体ID")


class AgentListRequest(BaseModel):
    """获取智能体列表请求"""
    agent_type: Optional[AgentTypeEnum] = Field(None, description="筛选智能体类型")
    power_tier: Optional[PowerTierEnum] = Field(None, description="筛选实力层级")
    leader_type: Optional[LeaderTypeEnum] = Field(None, description="筛选领导类型")
    region: Optional[str] = Field(None, description="筛选区域")


class AgentResponse(BaseModel):
    """智能体响应"""
    success: bool = Field(True, description="是否成功")
    message: str = Field(..., description="响应消息")
    agent: Optional[Agent] = Field(None, description="智能体数据")


class AgentListResponse(BaseModel):
    """智能体列表响应"""
    success: bool = Field(True, description="是否成功")
    message: str = Field(..., description="响应消息")
    agents: List[Agent] = Field(default_factory=list, description="智能体列表")
    total: int = Field(0, description="总数")


class AgentState(BaseModel):
    """智能体状态"""
    agent_id: str = Field(..., description="智能体ID")
    name: str = Field(..., description="智能体名称")
    comprehensive_power: float = Field(..., description="综合国力")
    economic_capability: float = Field(..., description="经济能力")
    military_capability: float = Field(..., description="军事能力")
    strategic_reputation: float = Field(..., description="战略声誉")
    leader_type: Optional[LeaderTypeEnum] = Field(None, description="领导类型")
    power_tier: PowerTierEnum = Field(..., description="实力层级")
    memory_count: int = Field(..., description="记忆数量")
    decision_count: int = Field(..., description="决策次数")


class AgentDecision(BaseModel):
    """智能体决策"""
    agent_id: str = Field(..., description="智能体ID")
    agent_name: str = Field(..., description="智能体名称")
    round: int = Field(..., description="轮次")
    action: str = Field(..., description="行动类型")
    target: Optional[str] = Field(None, description="目标智能体ID")
    reason: str = Field(..., description="决策理由")
    confidence: float = Field(..., description="置信度")
    timestamp: str = Field(..., description="时间戳")
