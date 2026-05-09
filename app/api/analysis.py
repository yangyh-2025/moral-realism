"""
仿真后验分析API模块

提供仿真结果的后验分析接口，包括行为模式、国力动态、秩序演变、领导类型分析等。
"""

from fastapi import APIRouter
from typing import Dict, Any

from app.services.analysis_service import get_analysis_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{project_id}/behavior")
async def analyze_behavior_patterns(project_id: int) -> Dict[str, Any]:
    """
    分析仿真中的行为模式

    识别稳定的合作/对抗关系对，统计互动频率和类型分布。
    """
    service = get_analysis_service()
    return await service.analyze_behavior_patterns(project_id)


@router.get("/{project_id}/power")
async def analyze_power_dynamics(project_id: int) -> Dict[str, Any]:
    """
    分析国力动态变化

    统计各国国力增长率、排名变化、层级跃迁等。
    """
    service = get_analysis_service()
    return await service.analyze_power_dynamics(project_id)


@router.get("/{project_id}/order")
async def analyze_order_evolution(project_id: int) -> Dict[str, Any]:
    """
    分析国际秩序演变

    统计秩序类型分布、持续时间、转换路径等。
    """
    service = get_analysis_service()
    return await service.analyze_order_evolution(project_id)


@router.get("/{project_id}/leader")
async def analyze_leader_behavior(project_id: int) -> Dict[str, Any]:
    """
    分析领导类型与行为关联

    统计不同领导类型的行为偏好、合作/对抗比例等。
    """
    service = get_analysis_service()
    return await service.analyze_leader_behavior(project_id)


@router.get("/{project_id}/report")
async def generate_full_report(project_id: int) -> Dict[str, Any]:
    """
    生成完整后验分析报告

    综合所有分析维度，生成完整的仿真后验分析报告。
    """
    service = get_analysis_service()
    return await service.generate_full_report(project_id)
