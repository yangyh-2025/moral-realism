# Statistics APIs
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.statistics_service import statistics_service

router = APIRouter(prefix="/simulation", tags=["statistics"])

# Request/Response Models
class PowerHistoryResponse(BaseModel):
    history_id: int
    agent_id: int
    agent_name: str
    round_num: int
    round_start_power: float
    round_end_power: float
    round_change_value: float
    round_change_rate: float


class GrowthRateResponse(BaseModel):
    leader_type: str
    power_level: str
    avg_growth_rate: float
    sample_size: int


class ActionPreferenceResponse(BaseModel):
    action_id: int
    action_name: str
    action_category: str
    count: int
    percentage: float


class OrderEvolutionResponse(BaseModel):
    round_num: int
    order_type: str
    respect_sov_ratio: float
    has_leader: bool
    leader_follower_ratio: Optional[float]


class RoundDetailResponse(BaseModel):
    round_id: int
    round_num: int
    total_action_count: int
    respect_sov_action_count: int
    respect_sov_ratio: float
    has_leader: bool
    order_type: str
    actions: List[dict]
    follower_relations: List[dict]


class GoalEvaluationResponse(BaseModel):
    evaluation_id: int
    agent_id: int
    agent_name: str
    evaluation_round: int
    evaluation_round_start: int
    evaluation_round_end: int
    goal_achievement_score: float
    power_growth_contribution: Optional[float] = None
    action_effectiveness: Optional[float] = None
    leadership_alignment: Optional[float] = None
    overall_assessment: Optional[str] = None
    specific_achievements: Optional[str] = None
    challenges: Optional[str] = None


@router.get("/{project_id}/stats/power-history", response_model=List[PowerHistoryResponse])
async def get_power_history(project_id: int, agent_id: Optional[int] = None, start_round: Optional[int] = None, end_round: Optional[int] = None):
    """
    获取项目全量智能体国力历史数据
    """
    data = await statistics_service.get_power_history(
        project_id=project_id,
        agent_id=agent_id,
        start_round=start_round,
        end_round=end_round
    )
    return data


@router.get("/{project_id}/stats/power-growth-rate", response_model=List[GrowthRateResponse])
async def get_power_growth_rate(project_id: int, start_round: int = 1, end_round: Optional[int] = None):
    """
    计算自定义轮次区间的实力增长率
    """
    data = await statistics_service.calculate_power_growth_rate(
        project_id=project_id,
        start_round=start_round,
        end_round=end_round
    )
    return data


@router.get("/{project_id}/stats/action-preference", response_model=List[ActionPreferenceResponse])
async def get_action_preference(project_id: int, agent_id: Optional[int] = None, power_level: Optional[str] = None, leader_type: Optional[str] = None, start_round: Optional[int] = None, end_round: Optional[int] = None):
    """
    获取行为偏好统计数据
    """
    data = await statistics_service.get_action_preference(
        project_id=project_id,
        agent_id=agent_id,
        power_level=power_level,
        leader_type=leader_type,
        start_round=start_round,
        end_round=end_round
    )
    return data


@router.get("/{project_id}/stats/order-evolution", response_model=List[OrderEvolutionResponse])
async def get_order_evolution(project_id: int):
    """
    获取国际秩序演变时序数据
    """
    data = await statistics_service.get_order_evolution(project_id=project_id)
    return data


@router.get("/{project_id}/stats/round-detail", response_model=RoundDetailResponse)
async def get_round_detail(project_id: int, round_num: int):
    """
    获取单轮仿真完整详情
    """
    data = await statistics_service.get_round_detail(
        project_id=project_id,
        round_num=round_num
    )
    if data is None:
        raise HTTPException(status_code=404, detail="Round not found")
    return data


@router.get("/{project_id}/stats/goal-evaluations", response_model=List[GoalEvaluationResponse])
async def get_goal_evaluations(
    project_id: int,
    agent_id: Optional[int] = None,
    start_round: Optional[int] = None,
    end_round: Optional[int] = None
):
    """
    获取战略目标评估数据
    """
    data = await statistics_service.get_goal_evaluations(
        project_id=project_id,
        agent_id=agent_id,
        start_round=start_round,
        end_round=end_round
    )
    return data


@router.get("/{project_id}/stats/goal-evaluation-trend/{agent_id}", response_model=List[GoalEvaluationResponse])
async def get_goal_evaluation_trend(project_id: int, agent_id: int):
    """
    获取单个国家的目标达成度趋势
    """
    data = await statistics_service.get_goal_evaluation_trend(
        project_id=project_id,
        agent_id=agent_id
    )
    return data
