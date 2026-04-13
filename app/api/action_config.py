# Action Config APIs
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

from app.core.action_manager import get_all_actions, get_action_by_id, initialize_actions

router = APIRouter(prefix="/action-config", tags=["action_config"])

# Request/Response Models
class ActionConfigResponse(BaseModel):
    action_id: int
    action_name: str
    action_en_name: str
    action_category: str
    action_desc: str
    respect_sov: bool
    initiator_power_change: int
    target_power_change: int
    is_initiative: bool
    is_response: bool


def _convert_to_response(action) -> ActionConfigResponse:
    """将 ActionConfig 转换为 ActionConfigResponse"""
    return ActionConfigResponse(
        action_id=action.action_id,
        action_name=action.action_name,
        action_en_name=action.action_en_name,
        action_category=action.action_category,
        action_desc=action.action_desc,
        respect_sov=action.respect_sov,
        initiator_power_change=action.initiator_power_change,
        target_power_change=action.target_power_change,
        is_initiative=action.is_initiative,
        is_response=action.is_response
    )


@router.get("/list", response_model=List[ActionConfigResponse])
async def get_action_configs():
    """
    获取20项标准互动行为集完整列表
    """
    # 确保行为管理器已初始化
    initialize_actions()

    # 获取所有行为配置
    actions = get_all_actions()

    # 转换为响应模型
    return [_convert_to_response(action) for action in actions]


@router.get("/{action_id}", response_model=ActionConfigResponse)
async def get_action_config(action_id: int):
    """
    获取单个行为详情
    """
    # 确保行为管理器已初始化
    initialize_actions()

    # 获取指定行为
    action = get_action_by_id(action_id)

    if action is None:
        raise HTTPException(status_code=404, detail="Action config not found")

    return _convert_to_response(action)
