"""
统计数据API模块

该模块提供仿真项目的统计分析接口，包括国力历史、增长率、
行为偏好、秩序演变等多维度数据分析功能，帮助用户深入了解
仿真过程中的模式和趋势。
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.statistics_service import statistics_service

# 创建路由
router = APIRouter(prefix="/simulation", tags=["statistics"])

# 请求/响应模型
class PowerHistoryResponse(BaseModel):
    """国力历史响应模型"""
    history_id: int
    agent_id: int
    agent_name: str
    round_num: int
    round_start_power: float
    round_end_power: float
    round_change_value: float
    round_change_rate: float


class GrowthRateResponse(BaseModel):
    """增长率响应模型"""
    leader_type: str
    power_level: str
    avg_growth_rate: float
    sample_size: int


class ActionPreferenceResponse(BaseModel):
    """行为偏好响应模型"""
    action_id: int
    action_name: str
    action_category: str
    count: int
    percentage: float


class OrderEvolutionResponse(BaseModel):
    """秩序演变响应模型"""
    round_num: int
    order_type: str
    respect_sov_ratio: float
    has_leader: bool
    leader_follower_ratio: Optional[float]


class RoundDetailResponse(BaseModel):
    """单轮详情响应模型"""
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
    """目标评估响应模型"""
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

    获取仿真项目中所有智能体的国力变化历史记录，支持按智能体和轮次范围筛选。

    Args:
        project_id: 项目ID
        agent_id: 可选，智能体ID
        start_round: 可选，起始轮次
        end_round: 可选，结束轮次

    Returns:
        List[PowerHistoryResponse]: 国力历史数据列表
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

    计算智能体在指定轮次区间内的平均实力增长率，支持按领导类型和实力等级分组。

    Args:
        project_id: 项目ID
        start_round: 起始轮次
        end_round: 可选，结束轮次

    Returns:
        List[GrowthRateResponse]: 增长率数据列表
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

    统计智能体在仿真过程中对不同行为的偏好程度，支持按智能体、实力等级、
    领导类型和轮次范围筛选。

    Args:
        project_id: 项目ID
        agent_id: 可选，智能体ID
        power_level: 可选，实力等级
        leader_type: 可选，领导类型
        start_round: 可选，起始轮次
        end_round: 可选，结束轮次

    Returns:
        List[ActionPreferenceResponse]: 行为偏好统计数据
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

    获取仿真过程中国际秩序的演变趋势，包括主权尊重比例、领导关系等关键指标。

    Args:
        project_id: 项目ID

    Returns:
        List[OrderEvolutionResponse]: 秩序演变数据
    """
    data = await statistics_service.get_order_evolution(project_id=project_id)
    return data


@router.get("/{project_id}/stats/round-detail", response_model=RoundDetailResponse)
async def get_round_detail(project_id: int, round_num: int):
    """
    获取单轮仿真完整详情

    获取指定轮次的完整仿真数据，包括行为记录、智能体状态和秩序特征。

    Args:
        project_id: 项目ID
        round_num: 轮次号

    Returns:
        RoundDetailResponse: 单轮详情

    Raises:
        HTTPException: 轮次不存在时返回404错误
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

    获取智能体的战略目标达成度评估数据，包括综合评分、各维度贡献等信息。

    Args:
        project_id: 项目ID
        agent_id: 可选，智能体ID
        start_round: 可选，起始轮次
        end_round: 可选，结束轮次

    Returns:
        List[GoalEvaluationResponse]: 目标评估数据列表
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

    获取指定智能体在整个仿真过程中的目标达成度变化趋势。

    Args:
        project_id: 项目ID
        agent_id: 智能体ID

    Returns:
        List[GoalEvaluationResponse]: 目标达成度趋势数据
    """
    data = await statistics_service.get_goal_evaluation_trend(
        project_id=project_id,
        agent_id=agent_id
    )
    return data
