"""
智能体管理API路由 - 智能体CRUD和批量操作

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter()


class AgentConfig(BaseModel):
    """智能体配置"""
    name: str = Field(..., description="智能体名称")
    region: str = Field(..., description="所属区域")
    leader_type: str = Field(..., description="领导类型")
    military: float = Field(default=0.0, ge=0.0, le=100.0, description="军事实力")
    economy: float = Field(default=0.0, ge=0.0, le=100.0, description="经济实力")
    technology: float = Field(default=0.0, ge=0.0, le=100.0, description="科技实力")
    influence: float = Field(default=0.0, ge=0.0, le=100.0, description="影响力")
    support: float = Field(default=0.0, ge=0.0, le=100.0, description="支持度")
    alliances: List[str] = Field(default_factory=list, description="盟友列表")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


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


@router.post("/agents", response_model=Agent)
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


@router.get("/agents", response_model=List[Agent])
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


@router.get("/agents/{agent_id}", response_model=Agent)
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


@router.put("/agents/{agent_id}", response_model=Agent)
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


@router.delete("/agents/{agent_id}")
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


@router.post("/agents/batch", response_model=BatchCreateResponse)
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


@router.get("/agents/simulation/{simulation_id}", response_model=List[Agent])
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


@router.post("/agents/{agent_id}/alliances/add")
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


@router.post("/agents/{agent_id}/alliances/remove")
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
