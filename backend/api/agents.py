"""
智能体管理API路由 - 智能体CRUD和批量操作

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from config.settings import Constants

router = APIRouter()


def calculate_comprehensiveFrom_dict(metrics_dict: dict) -> float:
    """从字典计算综合国力：综合国力 = (C+E+M) × (S+W)"""
    C = metrics_dict.get('C', 50.0)
    E = metrics_dict.get('E', 100.0)
    M = metrics_dict.get('M', 100.0)
    S = metrics_dict.get('S', 0.75)
    W = metrics_dict.get('W', 0.75)
    return (C + E + M) * (S + W)


def calculate_comprehensive_power(metrics: 'PowerMetrics') -> float:
    """计算综合国力：综合国力 = (C+E+M) × (S+W)"""
    return (metrics.C + metrics.E + metrics.M) * (metrics.S + metrics.W)


class PowerMetrics(BaseModel):
    """克莱因方程实力指标"""
    C: float = Field(default=50.0, ge=0.0, le=100.0, description="基本实体(临界质量)")
    E: float = Field(default=100.0, ge=0.0, le=200.0, description="经济实力")
    M: float = Field(default=100.0, ge=0.0, le=200.0, description="军事实力")
    S: float = Field(default=0.75, ge=0.5, le=1.0, description="战略目标")
    W: float = Field(default=0.75, ge=0.5, le=1.0, description="国家意志")
    comprehensive_power: float = Field(default=0.0, ge=0.0, description="综合国力")

    @validator('comprehensive_power', pre=True, always=True)
    def validate_comprehensive_power(cls, v, values):
        """确保综合国力被正确计算"""
        # 如果传入的值是0或None，重新计算
        if v is None or v == 0:
            return calculate_comprehensiveFrom_dict(values)
        return v


class AgentConfig(BaseModel):
    """智能体配置"""
    name: str = Field(..., description="智能体名称", min_length=1, max_length=Constants.MAX_AGENT_NAME_LENGTH)
    region: str = Field(..., description="所属区域", min_length=1, max_length=Constants.MAX_REGION_LENGTH)
    leader_type: str = Field(default="王道型", description="领导类型")
    power_metrics: PowerMetrics = Field(default_factory=PowerMetrics, description="实力指标")
    strategic_interests: List[str] = Field(default_factory=list, description="战略利益")
    alliances: List[str] = Field(default_factory=list, description="盟友列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    @validator('name')
    def validate_name(cls, v):
        """验证名称不为空且只包含有效字符"""
        if not v or v.strip() == '':
            raise ValueError('智能体名称不能为空')
        if len(v.strip()) == 0:
            raise ValueError('智能体名称不能只包含空格')
        return v.strip()

    @validator('alliances')
    def validate_alliances(cls, v):
        """验证盟友列表"""
        if v is None:
            return []
        # 去重并移除空字符串
        unique_alliances = list(set([a.strip() for a in v if a and a.strip()]))
        return unique_alliances


class Agent(BaseModel):
    """智能体"""
    id: str
    simulation_id: Optional[str] = None
    name: str
    region: str
    leader_type: Optional[str] = None
    power_tier: Optional[str] = None
    power_metrics: PowerMetrics
    strategic_interests: List[str]
    current_support: float = 0.0
    alliances: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class BatchCreateRequest(BaseModel):
    """批量创建请求"""
    agents: List[AgentConfig]
    simulation_id: Optional[str] = None


class BatchCreateResponse(BaseModel):
    """批量创建响应"""
    total: int
    successful: int
    failed: int
    agents: List[Agent]
    errors: List[Dict[str, str]]


def calculate_power_tier(power: float, all_powers: List[float]) -> str:
    """计算实力层级（基于正态分布 z-score）"""
    if len(all_powers) < 2:
        return "middle_power"

    import statistics
    mean = statistics.mean(all_powers)
    std_dev = statistics.stdev(all_powers)

    if std_dev == 0:
        return "middle_power"

    z_score = (power - mean) / std_dev

    if z_score > 2.0:
        return "superpower"
    elif z_score > 1.5:
        return "great_power"
    elif z_score > 0.5:
        return "middle_power"
    else:
        return "small_power"


def normalize_leader_type(power_tier: str, leader_type: Optional[str]) -> Optional[str]:
    """
    根据 power_tier 规范化 leader_type

    Args:
        power_tier: 实力层级
        leader_type: 领导类型

    Returns:
        规范化后的领导类型（超级大国/大国返回原值或默认，中等/小国返回 None）
    """
    from domain.power.power_metrics import PowerTier

    if power_tier in [PowerTier.SUPERPOWER.value, PowerTier.GREAT_POWER.value]:
        # 超级大国和大国必须有领导类型，没有则使用默认值
        return leader_type or "王道型"
    elif power_tier in [PowerTier.MIDDLE_POWER.value, PowerTier.SMALL_POWER.value]:
        # 中等强国和小国不应有领导类型，强制返回 None
        return None
    return leader_type


# 内存存储（简化实现）
_agents_store: Dict[str, Agent] = {}


@router.post("/", response_model=Agent)
async def create_agent(config: AgentConfig, simulation_id: Optional[str] = None):
    """
    创建智能体

    Args:
        config: 智能体配置
        simulation_id: 仿真ID（可选）

    Returns:
        Agent: 创建的智能体
    """
    agent_id = str(uuid.uuid4())
    now = datetime.now()

    # 确保综合国力被计算
    comprehensive_power = calculate_comprehensive_power(config.power_metrics)
    metrics_with_power = config.power_metrics.copy()
    metrics_with_power.comprehensive_power = comprehensive_power

    # 使用PowerTierClassifier计算实力层级
    # 需要包含当前智能体和所有现有智能体的综合国力
    from domain.power.power_metrics import PowerTierClassifier
    from domain.power.power_metrics import PowerMetrics as DomainPowerMetrics

    # 收集所有智能体的PowerMetrics（包括当前智能体）
    power_metrics_list = []

    # 添加当前智能体的PowerMetrics
    current_metrics = DomainPowerMetrics(
        critical_mass=metrics_with_power.C,
        economic_capability=metrics_with_power.E,
        military_capability=metrics_with_power.M,
        strategic_purpose=metrics_with_power.S,
        national_will=metrics_with_power.W
    )
    power_metrics_list.append(current_metrics)

    # 添加现有智能体的PowerMetrics
    for existing_agent in _agents_store.values():
        existing_metrics = DomainPowerMetrics(
            critical_mass=existing_agent.power_metrics.C,
            economic_capability=existing_agent.power_metrics.E,
            military_capability=existing_agent.power_metrics.M,
            strategic_purpose=existing_agent.power_metrics.S,
            national_will=existing_agent.power_metrics.W
        )
        power_metrics_list.append(existing_metrics)

    # 批量计算实力层级，取第一个（当前智能体）的层级
    tiers = PowerTierClassifier.classify_all(power_metrics_list)
    power_tier = tiers[0].value if tiers else "middle_power"

    # 根据 power_tier 规范化 leader_type
    normalized_leader_type = normalize_leader_type(power_tier, config.leader_type)

    agent = Agent(
        id=agent_id,
        simulation_id=simulation_id,
        name=config.name,
        region=config.region,
        leader_type=normalized_leader_type,
        power_tier=power_tier,
        power_metrics=metrics_with_power,
        strategic_interests=config.strategic_interests,
        alliances=config.alliances,
        metadata=config.metadata,
        created_at=now,
        updated_at=now
    )

    _agents_store[agent_id] = agent
    return agent


@router.get("/", response_model=List[Agent])
async def list_agents(
    simulation_id: Optional[str] = None,
    leader_type: Optional[str] = None,
    region: Optional[str] = None
):
    """
    列出智能体

    Args:
        simulation_id: 按仿真ID筛选
        leader_type: 按领导类型筛选
        region: 按区域筛选

    Returns:
        List[Agent]: 智能体列表
    """
    agents = list(_agents_store.values())

    # 重新计算所有智能体的实力层级（基于当前所有智能体的综合国力）
    if len(agents) > 0:
        from domain.power.power_metrics import PowerTierClassifier
        from domain.power.power_metrics import PowerMetrics as DomainPowerMetrics

        # 收集所有智能体的PowerMetrics
        power_metrics_list = []
        for agent in agents:
            metrics = DomainPowerMetrics(
                critical_mass=agent.power_metrics.C,
                economic_capability=agent.power_metrics.E,
                military_capability=agent.power_metrics.M,
                strategic_purpose=agent.power_metrics.S,
                national_will=agent.power_metrics.W
            )
            power_metrics_list.append(metrics)

        # 批量计算实力层级
        tiers = PowerTierClassifier.classify_all(power_metrics_list)

        # 更新所有智能体的实力层级
        for i, agent in enumerate(agents):
            if i < len(tiers):
                agent.power_tier = tiers[i].value
                # 同步更新到存储中
                _agents_store[agent.id].power_tier = tiers[i].value

    if simulation_id:
        agents = [a for a in agents if a.simulation_id == simulation_id]

    if leader_type:
        agents = [a for a in agents if a.leader_type == leader_type]

    if region:
        agents = [a for a in agents if a.region == region]

    return agents


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """
    获取智能体

    Args:
        agent_id: 智能体ID

    Returns:
        Agent: 智能体详情
    """
    if agent_id not in _agents_store:
        raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")

    return _agents_store[agent_id]


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, config: AgentConfig):
    """
    更新智能体

    Args:
        agent_id: 智能体ID
        config: 新的配置

    Returns:
        Agent: 更新后的智能体
    """
    if agent_id not in _agents_store:
        raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")

    existing = _agents_store[agent_id]

    # 确保综合国力被计算
    comprehensive_power = calculate_comprehensive_power(config.power_metrics)
    metrics_with_power = config.power_metrics.copy()
    metrics_with_power.comprehensive_power = comprehensive_power

    # 使用PowerTierClassifier计算实力层级
    # 需要包含所有智能体的综合国力（包括更新后的）
    from domain.power.power_metrics import PowerTierClassifier
    from domain.power.power_metrics import PowerMetrics as DomainPowerMetrics

    # 收集所有智能体的PowerMetrics
    power_metrics_list = []

    for existing_agent_id, existing_agent in _agents_store.items():
        if existing_agent_id == agent_id:
            # 使用更新后的指标
            agent_metrics = DomainPowerMetrics(
                critical_mass=metrics_with_power.C,
                economic_capability=metrics_with_power.E,
                military_capability=metrics_with_power.M,
                strategic_purpose=metrics_with_power.S,
                national_will=metrics_with_power.W
            )
        else:
            # 使用现有指标
            agent_metrics = DomainPowerMetrics(
                critical_mass=existing_agent.power_metrics.C,
                economic_capability=existing_agent.power_metrics.E,
                military_capability=existing_agent.power_metrics.M,
                strategic_purpose=existing_agent.power_metrics.S,
                national_will=existing_agent.power_metrics.W
            )
        power_metrics_list.append(agent_metrics)

    # 批量计算实力层级
    tiers = PowerTierClassifier.classify_all(power_metrics_list)

    # 更新所有智能体的实力层级到存储
    agent_ids = list(_agents_store.keys())
    for i, agent_id_key in enumerate(agent_ids):
        if i < len(tiers):
            _agents_store[agent_id_key].power_tier = tiers[i].value

    # 找到被更新智能体的索引和层级
    agent_idx = agent_ids.index(agent_id)
    power_tier = tiers[agent_idx].value if agent_idx < len(tiers) else "middle_power"

    # 根据 power_tier 规范化 leader_type
    normalized_leader_type = normalize_leader_type(power_tier, config.leader_type)

    updated = Agent(
        id=agent_id,
        simulation_id=existing.simulation_id,
        name=config.name,
        region=config.region,
        leader_type=normalized_leader_type,
        power_tier=power_tier,
        power_metrics=metrics_with_power,
        strategic_interests=config.strategic_interests,
        alliances=config.alliances,
        metadata=config.metadata,
        created_at=existing.created_at,
        updated_at=datetime.now()
    )

    _agents_store[agent_id] = updated
    return updated


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """
    删除智能体

    Args:
        agent_id: 智能体ID
    """
    if agent_id not in _agents_store:
        raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")

    del _agents_store[agent_id]
    return {"message": f"智能体 {agent_id} 已删除"}


@router.post("/batch", response_model=BatchCreateResponse)
async def create_agents_batch(request: BatchCreateRequest):
    """
    批量创建智能体

    Args:
        request: 批量创建请求

    Returns:
        BatchCreateResponse: 批量创建结果
    """
    successful_agents = []
    errors = []

    # 使用PowerTierClassifier批量计算实力层级
    # 需要包含新创建的智能体和现有智能体
    from domain.power.power_metrics import PowerTierClassifier
    from domain.power.power_metrics import PowerMetrics as DomainPowerMetrics

    # 收集所有智能体的PowerMetrics（包括新创建的和现有的）
    power_metrics_list = []

    # 添加现有智能体的PowerMetrics
    for existing_agent in _agents_store.values():
        existing_metrics = DomainPowerMetrics(
            critical_mass=existing_agent.power_metrics.C,
            economic_capability=existing_agent.power_metrics.E,
            military_capability=existing_agent.power_metrics.M,
            strategic_purpose=existing_agent.power_metrics.S,
            national_will=existing_agent.power_metrics.W
        )
        power_metrics_list.append(existing_metrics)

    # 添加新智能体的PowerMetrics
    for config in request.agents:
        new_metrics = DomainPowerMetrics(
            critical_mass=config.power_metrics.C,
            economic_capability=config.power_metrics.E,
            military_capability=config.power_metrics.M,
            strategic_purpose=config.power_metrics.S,
            national_will=config.power_metrics.W
        )
        power_metrics_list.append(new_metrics)

    # 批量计算实力层级
    tiers = PowerTierClassifier.classify_all(power_metrics_list)

    # 从现有智能体数量开始，取新智能体的层级
    existing_count = len(_agents_store)
    new_agent_tiers = tiers[existing_count:] if (len(tiers) > existing_count) else []

    for idx, config in enumerate(request.agents):
        try:
            agent_id = str(uuid.uuid4())
            now = datetime.now()

            # 获取预计算的实力层级
            power_tier = new_agent_tiers[idx].value if idx < len(new_agent_tiers) else "middle_power"

            # 根据 power_tier 规范化 leader_type
            normalized_leader_type = normalize_leader_type(power_tier, config.leader_type)

            agent = Agent(
                id=agent_id,
                simulation_id=request.simulation_id,
                name=config.name,
                region=config.region,
                leader_type=normalized_leader_type,
                power_tier=power_tier,
                power_metrics=config.power_metrics,
                strategic_interests=config.strategic_interests,
                alliances=config.alliances,
                metadata=config.metadata,
                created_at=now,
                updated_at=now
            )

            _agents_store[agent_id] = agent
            successful_agents.append(agent)

        except Exception as e:
            errors.append({
                "index": idx,
                "name": config.name,
                "error": str(e)
            })

    return BatchCreateResponse(
        total=len(request.agents),
        successful=len(successful_agents),
        failed=len(errors),
        agents=successful_agents,
        errors=errors
    )


@router.get("/simulation/{simulation_id}", response_model=List[Agent])
async def list_agents_by_simulation(simulation_id: str):
    """
    列出指定仿真的所有智能体

    Args:
        simulation_id: 仿真ID

    Returns:
        List[Agent]: 智能体列表
    """
    agents = [
        a for a in _agents_store.values()
        if a.simulation_id == simulation_id
    ]

    return agents


@router.post("/{agent_id}/alliances/add")
async def add_alliance(agent_id: str, alliance_id: str):
    """
    添加盟友

    Args:
        agent_id: 智能体ID
        alliance_id: 盟友ID
    """
    if agent_id not in _agents_store:
        raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")

    agent = _agents_store[agent_id]

    if alliance_id not in agent.alliances:
        agent.alliances.append(alliance_id)
        agent.updated_at = datetime.now()

    return {"message": "盟友已添加", "alliances": agent.alliances}


@router.post("/{agent_id}/alliances/remove")
async def remove_alliance(agent_id: str, alliance_id: str):
    """
    移除盟友

    Args:
        agent_id: 智能体ID
        alliance_id: 盟友ID
    """
    if agent_id not in _agents_store:
        raise HTTPException(status_code=404, detail=f"智能体 {agent_id} 不存在")

    agent = _agents_store[agent_id]

    if alliance_id in agent.alliances:
        agent.alliances.remove(alliance_id)
        agent.updated_at = datetime.now()

    return {"message": "盟友已移除", "alliances": agent.alliances}
