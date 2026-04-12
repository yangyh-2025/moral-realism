# Simulation APIs
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/simulation", tags=["simulation"])

# Request/Response Models
class ProjectResponse(BaseModel):
    project_id: int
    project_name: str
    project_desc: Optional[str]
    scene_source: str
    total_rounds: int
    current_round: int
    status: str
    respect_sov_threshold: float
    leader_threshold: float
    created_at: datetime
    updated_at: datetime

class CreateProjectRequest(BaseModel):
    project_name: str
    project_desc: Optional[str] = None
    total_rounds: int = 50
    scene_source: str = "自定义"

class AgentConfigRequest(BaseModel):
    agent_name: str
    region: str
    c_score: float
    e_score: float
    m_score: float
    s_score: float = 0.5
    w_score: float = 0.5
    leader_type: Optional[str] = None

class AgentResponse(BaseModel):
    agent_id: int
    agent_name: str
    region: str
    c_score: float
    e_score: float
    m_score: float
    s_score: float
    w_score: float
    initial_total_power: float
    current_total_power: float
    power_level: str
    leader_type: Optional[str]


# Project Management APIs
@router.get("/project/list", response_model=List[ProjectResponse])
async def get_projects():
    """
    获取所有仿真项目列表
    """
    # TODO: Implement actual logic to fetch all projects
    return []


@router.post("/project", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """
    创建自定义仿真项目
    """
    # TODO: Implement actual logic to create project
    return ProjectResponse(
        project_id=1,
        project_name=request.project_name,
        project_desc=request.project_desc,
        scene_source=request.scene_source,
        total_rounds=request.total_rounds,
        current_round=0,
        status="未启动",
        respect_sov_threshold=0.6,
        leader_threshold=0.6,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """
    获取项目详情
    """
    # TODO: Implement actual logic to fetch project
    raise HTTPException(status_code=404, detail="Project not found")


@router.put("/project/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, request: CreateProjectRequest):
    """
    更新项目基础信息
    """
    # TODO: Implement actual logic to update project
    raise HTTPException(status_code=404, detail="Project not found")


@router.delete("/project/{project_id}")
async def delete_project(project_id: int):
    """
    删除仿真项目
    """
    # TODO: Implement actual logic to delete project
    return {"message": "Project deleted successfully"}


# Agent Configuration APIs
@router.post("/project/{project_id}/agent", response_model=AgentResponse)
async def add_agent(project_id: int, request: AgentConfigRequest):
    """
    为项目添加智能体
    """
    # TODO: Implement actual logic to add agent
    return AgentResponse(
        agent_id=1,
        agent_name=request.agent_name,
        region=request.region,
        c_score=request.c_score,
        e_score=request.e_score,
        m_score=request.m_score,
        s_score=request.s_score,
        w_score=request.w_score,
        initial_total_power=0.0,
        current_total_power=0.0,
        power_level="小国",
        leader_type=request.leader_type
    )


@router.get("/project/{project_id}/agent/list", response_model=List[AgentResponse])
async def get_agents(project_id: int):
    """
    获取项目智能体列表
    """
    # TODO: Implement actual logic to fetch agents
    return []


@router.get("/project/{project_id}/agent/{agent_id}", response_model=AgentResponse)
async def get_agent(project_id: int, agent_id: int):
    """
    获取智能体详情
    """
    # TODO: Implement actual logic to fetch agent
    raise HTTPException(status_code=404, detail="Agent not found")


@router.put("/project/{project_id}/agent/{agent_id}", response_model=AgentResponse)
async def update_agent(project_id: int, agent_id: int, request: AgentConfigRequest):
    """
    更新智能体初始配置
    """
    # TODO: Implement actual logic to update agent
    raise HTTPException(status_code=404, detail="Agent not found")


@router.delete("/project/{project_id}/agent/{agent_id}")
async def delete_agent(project_id: int, agent_id: int):
    """
    删除智能体
    """
    # TODO: Implement actual logic to delete agent
    return {"message": "Agent deleted successfully"}


# Simulation Control APIs
@router.post("/{project_id}/start")
async def start_simulation(project_id: int):
    """
    启动仿真项目
    """
    # TODO: Implement actual logic to start simulation
    return {"message": "Simulation started", "project_id": project_id}


@router.post("/{project_id}/step")
async def step_simulation(project_id: int):
    """
    单步执行一轮仿真
    """
    # TODO: Implement actual logic to execute single step
    return {"message": "Step executed", "project_id": project_id, "round": 1}


@router.post("/{project_id}/pause")
async def pause_simulation(project_id: int):
    """
    暂停仿真
    """
    # TODO: Implement actual logic to pause simulation
    return {"message": "Simulation paused", "project_id": project_id}


@router.post("/{project_id}/resume")
async def resume_simulation(project_id: int):
    """
    继续仿真
    """
    # TODO: Implement actual logic to resume simulation
    return {"message": "Simulation resumed", "project_id": project_id}


@router.post("/{project_id}/stop")
async def stop_simulation(project_id: int):
    """
    终止仿真
    """
    # TODO: Implement actual logic to stop simulation
    return {"message": "Simulation stopped", "project_id": project_id}


@router.post("/{project_id}/reset")
async def reset_simulation(project_id: int):
    """
    重置仿真
    """
    # TODO: Implement actual logic to reset simulation
    return {"message": "Simulation reset", "project_id": project_id}
