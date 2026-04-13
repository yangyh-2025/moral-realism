# Simulation APIs
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.services.project_service import project_service
from app.services.agent_service import agent_service, AgentConfig
from app.services.simulation_service import simulation_service

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
    projects = await project_service.get_projects()
    return [ProjectResponse(**p) for p in projects]


@router.post("/project", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """
    创建自定义仿真项目
    """
    project = await project_service.create_project(
        project_name=request.project_name,
        project_desc=request.project_desc,
        total_rounds=request.total_rounds,
        scene_source=request.scene_source
    )
    return ProjectResponse(**project)


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """
    获取项目详情
    """
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project)


@router.put("/project/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, request: CreateProjectRequest):
    """
    更新项目基础信息
    """
    project = await project_service.update_project(
        project_id,
        project_name=request.project_name,
        project_desc=request.project_desc,
        total_rounds=request.total_rounds,
        scene_source=request.scene_source
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project)


@router.delete("/project/{project_id}")
async def delete_project(project_id: int):
    """
    删除仿真项目
    """
    success = await project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


# Agent Configuration APIs
@router.post("/project/{project_id}/agent", response_model=AgentResponse)
async def add_agent(project_id: int, request: AgentConfigRequest):
    """
    为项目添加智能体
    """
    try:
        config = AgentConfig(
            agent_name=request.agent_name,
            region=request.region,
            c_score=request.c_score,
            e_score=request.e_score,
            m_score=request.m_score,
            s_score=request.s_score,
            w_score=request.w_score,
            leader_type=request.leader_type
        )
        agent = await agent_service.add_agent(project_id, config)
        return AgentResponse(**agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/project/{project_id}/agent/list", response_model=List[AgentResponse])
async def get_agents(project_id: int):
    """
    获取项目智能体列表
    """
    agents = await agent_service.get_agents(project_id)
    return [AgentResponse(**a) for a in agents]


@router.get("/project/{project_id}/agent/{agent_id}", response_model=AgentResponse)
async def get_agent(project_id: int, agent_id: int):
    """
    获取智能体详情
    """
    agent = await agent_service.get_agent(project_id, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**agent)


@router.put("/project/{project_id}/agent/{agent_id}", response_model=AgentResponse)
async def update_agent(project_id: int, agent_id: int, request: AgentConfigRequest):
    """
    更新智能体初始配置
    """
    try:
        config = AgentConfig(
            agent_name=request.agent_name,
            region=request.region,
            c_score=request.c_score,
            e_score=request.e_score,
            m_score=request.m_score,
            s_score=request.s_score,
            w_score=request.w_score,
            leader_type=request.leader_type
        )
        agent = await agent_service.update_agent(project_id, agent_id, config)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentResponse(**agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/project/{project_id}/agent/{agent_id}")
async def delete_agent(project_id: int, agent_id: int):
    """
    删除智能体
    """
    success = await agent_service.delete_agent(project_id, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}


# Simulation Control APIs
@router.post("/{project_id}/start")
async def start_simulation(project_id: int):
    """
    启动仿真项目
    """
    result = await simulation_service.start_simulation(project_id)
    return result


@router.post("/{project_id}/step")
async def step_simulation(project_id: int):
    """
    单步执行一轮仿真
    """
    result = await simulation_service.step_simulation(project_id)
    return result


@router.post("/{project_id}/pause")
async def pause_simulation(project_id: int):
    """
    暂停仿真
    """
    result = await simulation_service.pause_simulation(project_id)
    return result


@router.post("/{project_id}/resume")
async def resume_simulation(project_id: int):
    """
    继续仿真
    """
    result = await simulation_service.resume_simulation(project_id)
    return result


@router.post("/{project_id}/stop")
async def stop_simulation(project_id: int):
    """
    终止仿真
    """
    result = await simulation_service.stop_simulation(project_id)
    return result


@router.post("/{project_id}/reset")
async def reset_simulation(project_id: int):
    """
    重置仿真
    """
    result = await simulation_service.reset_simulation(project_id)
    return result
