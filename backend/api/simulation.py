"""
仿真管理API路由

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from infrastructure.storage.storage_engine import StorageEngine
from backend.services.simulation_manager import (
    SimulationLifecycle,
    SimulationConfig,
    Simulation,
    QueryFilters,
    SimulationStatus
)

router = APIRouter()

# 全局存储引擎实例（实际应用中应该从依赖注入获取）
_storage_engine = StorageEngine()
_simulation_lifecycle = SimulationLifecycle(_storage_engine)


# API数据模型
class SimulationConfigRequest(BaseModel):
    total_rounds: int = 100
    round_duration_months: int = 6
    random_event_prob: float = 0.1
    agent_configs: list = []
    event_config: dict = {}
    metadata: dict = {}


class SimulationStateResponse(BaseModel):
    simulation_id: str
    status: str
    current_round: int
    total_rounds: int
    progress: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None


class SimulationListResponse(BaseModel):
    simulations: list


@router.post("/start")
async def start_simulation(config: SimulationConfigRequest):
    """
    启动仿真

    Args:
        config: 仿真配置

    Returns:
        仿真状态
    """
    simulation_id = f"sim_{datetime.now().timestamp()}"

    # 创建仿真配置
    sim_config = SimulationConfig(
        simulation_id=simulation_id,
        total_rounds=config.total_rounds,
        round_duration_months=config.round_duration_months,
        random_event_prob=config.random_event_prob,
        agent_configs=config.agent_configs,
        event_config=config.event_config,
        metadata=config.metadata
    )

    # 创建并启动仿真
    simulation = await _simulation_lifecycle.create_simulation(sim_config)
    result = await _simulation_lifecycle.start_simulation(simulation_id)

    return {
        "message": "仿真已启动",
        "simulation_id": simulation_id,
        "status": result.status.value,
        "total_rounds": result.total_rounds,
        "completed_rounds": result.completed_rounds
    }


@router.post("/pause/{simulation_id}")
async def pause_simulation(simulation_id: str):
    """
    暂停仿真

    Args:
        simulation_id: 仿真ID

    Returns:
        操作结果
    """
    try:
        await _simulation_lifecycle.pause_simulation(simulation_id)
        return {"message": "仿真已暂停", "simulation_id": simulation_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/resume/{simulation_id}")
async def resume_simulation(simulation_id: str):
    """
    继续仿真

    Args:
        simulation_id: 仿真ID

    Returns:
        仿真结果
    """
    try:
        result = await _simulation_lifecycle.resume_simulation(simulation_id)
        return {
            "message": "仿真已继续",
            "simulation_id": simulation_id,
            "status": result.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stop/{simulation_id}")
async def stop_simulation(simulation_id: str):
    """
    停止仿真

    Args:
        simulation_id: 仿真ID

    Returns:
        操作结果
    """
    try:
        await _simulation_lifecycle.stop_simulation(simulation_id)
        return {"message": "仿真已停止", "simulation_id": simulation_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/create")
async def create_simulation(config: SimulationConfigRequest):
    """
    创建仿真

    Args:
        config: 仿真配置

    Returns:
        仿真信息
    """
    simulation_id = f"sim_{datetime.now().timestamp()}"

    sim_config = SimulationConfig(
        simulation_id=simulation_id,
        total_rounds=config.total_rounds,
        round_duration_months=config.round_duration_months,
        random_event_prob=config.random_event_prob,
        agent_configs=config.agent_configs,
        event_config=config.event_config,
        metadata=config.metadata
    )

    simulation = await _simulation_lifecycle.create_simulation(sim_config)

    return {
        "message": "仿真已创建",
        "simulation_id": simulation_id,
        "status": simulation.status.value,
        "config": {
            "total_rounds": simulation.config.total_rounds,
            "round_duration_months": simulation.config.round_duration_months
        }
    }


@router.get("/state/{simulation_id}", response_model=SimulationStateResponse)
async def get_simulation_state(simulation_id: str):
    """
    获取仿真状态

    Args:
        simulation_id: 仿真ID

    Returns:
        仿真状态
    """
    try:
        status = _simulation_lifecycle.get_simulation_status(simulation_id)
        config = _simulation_lifecycle.get_simulation_config(simulation_id)
        progress_info = _simulation_lifecycle.get_simulation_progress(simulation_id)

        return SimulationStateResponse(
            simulation_id=simulation_id,
            status=status.value,
            current_round=progress_info.current_round,
            total_rounds=progress_info.total_rounds,
            progress=progress_info.percentage,
            start_time=config.metadata.get("start_time"),
            end_time=None,
            error_message=None
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/list")
async def list_simulations(
    status: Optional[str] = None,
    limit: int = 100
):
    """
    获取可用仿真列表

    Args:
        status: 按状态筛选
        limit: 返回数量限制

    Returns:
        仿真列表
    """
    # 构建查询过滤器
    filters = QueryFilters(limit=limit)

    if status:
        try:
            status_enum = SimulationStatus(status)
            filters = QueryFilters(status=status_enum, limit=limit)
        except ValueError:
            # 无效的状态值
            pass

    simulations = _simulation_lifecycle.list_simulations(filters)

    # 转换为响应格式
    simulation_list = []
    for sim in simulations:
        simulation_list.append({
            "id": sim.simulation_id,
            "status": sim.status.value,
            "total_rounds": sim.config.total_rounds,
            "current_round": sim.current_round,
            "progress": sim.progress,
            "start_time": sim.start_time.isoformat() if sim.start_time else None,
            "end_time": sim.end_time.isoformat() if sim.end_time else None
        })

    return {"simulations": simulation_list}


@router.delete("/{simulation_id}")
async def delete_simulation(simulation_id: str):
    """
    删除仿真

    Args:
        simulation_id: 仿真ID

    Returns:
        操作结果
    """
    try:
        await _simulation_lifecycle.delete_simulation(simulation_id)
        return {"message": f"仿真 {simulation_id} 已删除"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{simulation_id}/progress")
async def get_simulation_progress(simulation_id: str):
    """
    获取仿真进度

    Args:
        simulation_id: 仿真ID

    Returns:
        进度信息
    """
    try:
        progress_info = _simulation_lifecycle.get_simulation_progress(simulation_id)

        return {
            "simulation_id": simulation_id,
            "current_round": progress_info.current_round,
            "total_rounds": progress_info.total_rounds,
            "percentage": progress_info.percentage,
            "estimated_remaining": progress_info.estimated_remaining,
            "current_phase": progress_info.current_phase
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
