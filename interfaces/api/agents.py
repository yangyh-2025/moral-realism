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


class AgentConfig(BaseModel):
    """智能体配置"""
    name: str = Field(..., description="智能体名称", min_length=1, max_length=Constants.MAX_AGENT_NAME_LENGTH)
    region: str = Field(..., description="所属区域", min_length=1, max_length=Constants.MAX_REGION_LENGTH)
    leader_type: str = Field(..., description="领导类型", min_length=1, max_length=Constants.MAX_LEADER_TYPE_LENGTH)
    military: float = Field(default=0.0, ge=0.0, le=100.0, description="军事实力")
    economy: float = Field(default=0.0, ge=0.0, le=100.0, description="经济实力")
    technology: float = Field(default=0.0, ge=0.0, le=100.0, description="科技实力")
    influence: float = Field(default=0.0, ge=0.0, le=100.0, description="影响力")
    support: float = Field(default=0.0, ge=0.0, le=100.0, description="支持度")
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
    leader_type: str
    military: float
    economy: float
    technology: float
    influence: float
    support: float
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
        Agent: 创建的智能
    """
    agent_id = str(uuid.uuid4())
    now = datetime.now()

    agent = Agent(
        id=agent_id,
        simulation_id=simulation_id,
        name=config.name,
        region=config.region,
        leader_type=config.leader_type,
        military=config.military,
        economy=config.economy,
        technology=config.technology,
        influence=config.influence,
        support=config.support,
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

    updated = Agent(
        id=agent_id,
        simulation_id=existing.simulation_id,
        name=config.name,
        region=config.region,
        leader_type=config.leader_type,
        military=config.military,
        economy=config.economy,
        technology=config.technology,
        influence=config.influence,
        support=config.support,
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

    for idx, config in enumerate(request.agents):
        try:
            agent_id = str(uuid.uuid4())
            now = datetime.now()

            agent = Agent(
                id=agent_id,
                simulation_id=request.simulation_id,
                name=config.name,
                region=config.region,
                leader_type=config.leader_type,
                military=config.military,
                economy=config.economy,
                technology=config.technology,
                influence=config.influence,
                support=config.support,
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
