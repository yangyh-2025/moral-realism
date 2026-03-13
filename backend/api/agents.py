"""
智能体管理API路由

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Agent(BaseModel):
    id: str
    name: str
    region: str
    power_level: str
    leader_type: Optional[str] = None
    military: float = 0.0
    economy: float = 0.0
    technology: float = 0.0
    influence: float = 0.0
    alliances: List[str] = []
    support: float = 0.0

# 内存存储（简化实现）
agents_store: List[Agent] = []

@router.get("", response_model=List[Agent])
async def get_all_agents():
    """获取所有智能体"""
    return agents_store

@router.get("/{agent_id}", response_model=Agent)
async def get_agent_by_id(agent_id: str):
    """根据ID获取智能体"""
    for agent in agents_store:
        if agent.id == agent_id:
            return agent
    raise HTTPException(status_code=404, detail="智能体不存在")

@router.post("", response_model=Agent)
async def create_agent(agent: Agent):
    """创建智能体"""
    agents_store.append(agent)
    return agent

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent: Agent):
    """更新智能体"""
    for i, a in enumerate(agents_store):
        if a.id == agent_id:
            agents_store[i] = agent
            return agent
    raise HTTPException(status_code=404, detail="智能体不存在")

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    """删除智能体"""
    global agents_store
    agents_store = [a for a in agents_store if a.id != agent_id]
    return {"message": "智能体已删除"}

@router.post("/calculate-tiers")
async def calculate_power_tiers():
    """计算实力层级"""
    # 简化实现，返回示例结果
    return {
        "message": "实力层级计算完成",
        "results": []
    }
