# Action Config APIs
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel

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
    allowed_initiator_level: List[str]
    allowed_responder_level: List[str]
    forbidden_leader_type: List[str]


@router.get("/list", response_model=List[ActionConfigResponse])
async def get_action_configs():
    """
    获取20项标准互动行为集完整列表
    """
    # TODO: Implement actual logic to fetch all action configs from database
    # This is a placeholder returning the 20 standard actions
    return [
        ActionConfigResponse(
            action_id=1,
            action_name="发表公开声明",
            action_en_name="MAKE PUBLIC STATEMENT",
            action_category="外交手段",
            action_desc="发表公开声明，表达立场和观点",
            respect_sov=True,
            initiator_power_change=0,
            target_power_change=0,
           is_initiative=True,
            is_response=True,
            allowed_initiator_level=["超级大国", "大国", "中等强国", "小国"],
            allowed_responder_level=["超级大国", "大国", "中等强国", "小国"],
            forbidden_leader_type=[]
        )
    ]


@router.get("/{action_id}", response_model=ActionConfigResponse)
async def get_action_config(action_id: int):
    """
    获取单个行为详情
    """
    # TODO: Implement actual logic to fetch single action config
    if action_id == 1:
        return ActionConfigResponse(
            action_id=1,
            action_name="发表公开声明",
            action_en_name="MAKE PUBLIC STATEMENT",
            action_category="外交手段",
            action_desc="发表公开声明，表达立场和观点",
            respect_sov=True,
            initiator_power_change=0,
            target_power_change=0,
            is_initiative=True,
            is_response=True,
            allowed_initiator_level=["超级大国", "大国", "中等强国", "小国"],
            allowed_responder_level=["超级大国", "大国", "中等强国", "小国"],
            forbidden_leader_type=[]
        )
    raise HTTPException(status_code=404, detail="Action config not found")
