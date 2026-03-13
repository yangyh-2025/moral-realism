"""
仿真管理API路由

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

#数据模型
class SimulationConfig(BaseModel):
    total_rounds: int = 100
    round_duration_months: int = 6
    random_event_prob: float = 0.1

class SimulationState(BaseModel):
    current_round: int = 0
    active_events: int = 0
    power_pattern: str = "未判定"
    order_type: str = "未判定"
    is_running: bool = False
    is_paused: bool = False

# 内存存储（简化实现）
simulation_state = SimulationState()

@router.post("/start")
async def start_simulation(config: SimulationConfig):
    """启动仿真"""
    simulation_state.is_running = True
    simulation_state.is_paused = False
    return {"message": "仿真已启动", "state": simulation_state}

@router.post("/pause")
async def pause_simulation():
    """暂停仿真"""
    simulation_state.is_paused = True
    return {"message": "仿真已暂停", "state": simulation_state}

@router.post("/resume")
async def resume_simulation():
    """继续仿真"""
    simulation_state.is_paused = False
    return {"message": "仿真已继续", "state": simulation_state}

@router.post("/stop")
async def stop_simulation():
    """停止仿真"""
    simulation_state.is_running = False
    simulation_state.is_paused = False
    return {"message": "仿真已停止", "state": simulation_state}

@router.post("/reset")
async def reset_simulation():
    """重置仿真"""
    simulation_state.current_round = 0
    simulation_state.is_running = False
    simulation_state.is_paused = False
    return {"message": "仿真已重置", "state": simulation_state}

@router.get("/state", response_model=SimulationState)
async def get_simulation_state():
    """获取仿真状态"""
    return simulation_state
