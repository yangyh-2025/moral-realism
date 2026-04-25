"""
战略关系API路由
提供战略关系查询和设置接口。
"""

from typing import Optional
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.database import db_config
from ..services.strategic_relationship_service import StrategicRelationshipService

router = APIRouter(prefix="/strategic-relationships", tags=["strategic-relationships"])


class SetRelationshipRequest(BaseModel):
    """设置战略关系请求"""
    source_id: int
    target_id: int
    relationship_type: str


class SetRelationshipResponse(BaseModel):
    """设置战略关系响应"""
    message: str


@router.get("/project/{project_id}")
async def get_strategic_relationships(
    project_id: int,
    agent_id: Optional[int] = None
):
    """
    获取项目的战略关系

    Args:
        project_id: 项目ID
        agent_id: 可选，特定智能体ID

    Returns:
        如果提供agent_id，返回该智能体的所有关系
        否则返回项目中所有智能体的关系映射
    """
    async for session in db_config.get_session():
        service = StrategicRelationshipService(session)

        if agent_id:
            relationships = await service.get_all_relationships(project_id, agent_id)
            return {"agent_id": agent_id, "relationships": relationships}
        else:
            all_relationships = await service.get_all_agents_relationships(project_id)
            return all_relationships


@router.post("/project/{project_id}", response_model=SetRelationshipResponse)
async def set_strategic_relationship(
    project_id: int,
    request: SetRelationshipRequest
):
    """
    设置两个智能体之间的战略关系

    允许的配对规则：
    - 起级大国 × 大国
    - 起级大国 × 中等强国
    - 起级大国 × 小国
    - 大国 × 中等强国
    - 大国 × 小国

    不允许的配对：
    - 中等强国 × 中等强国
    - 中等强国 × 小国
    - 小国 × 小国

    Args:
        project_id: 项目ID
        source_id: 源智能体ID
        target_id: 目标智能体ID
        relationship_type: 关系类型（战争关系/冲突关系/无外交关系/伙伴关系/盟友关系）

    Returns:
        操作结果
    """
    async for session in db_config.get_session():
        service = StrategicRelationshipService(session)
        await service.set_relationship(
            project_id,
            request.source_id,
            request.target_id,
            request.relationship_type
        )
        return SetRelationshipResponse(message="Relationship updated")


@router.post("/project/{project_id}/initialize", response_model=SetRelationshipResponse)
async def initialize_strategic_relationships(project_id: int):
    """
    初始化项目的战略关系

    系统将自动为以下配对建立战略关系（默认值为"无外交关系"）：
    - 起级大国 × 大国
    - 起级大国 × 中等强国
    - 起级大国x 小国
    - 大国 × 中等强国
    - 大国 × 小国

    Args:
        project_id: 项目ID

    Returns:
        操作结果
    """
    async for session in db_config.get_session():
        service = StrategicRelationshipService(session)
        await service.initialize_relationships(project_id)
        return SetRelationshipResponse(message="Relationships initialized")
