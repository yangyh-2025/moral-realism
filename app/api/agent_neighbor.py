"""
邻接关系API路由
提供智能体邻接关系(is_neighbor)查询和设置接口。
"""

from typing import Optional, List
from fastapi import APIRouter

from pydantic import BaseModel

from ..config.database import db_config
from ..services.agent_neighbor_service import AgentNeighborService

router = APIRouter(prefix="/agent-neighbors", tags=["agent-neighbors"])


class SetNeighborRequest(BaseModel):
    """设置单对邻接关系请求"""
    source_id: int
    target_id: int
    is_neighbor: bool


class BatchSetNeighborRequest(BaseModel):
    """批量设置邻接关系请求"""
    updates: List[SetNeighborRequest]


class NeighborResponse(BaseModel):
    """邻接关系操作响应"""
    message: str


@router.get("/project/{project_id}")
async def get_agent_neighbors(
    project_id: int,
    agent_id: Optional[int] = None
):
    """
    获取项目的邻接关系

    Args:
        project_id: 项目ID
        agent_id: 可选, 特定智能体ID

    Returns:
        如果提供agent_id, 返回该智能体与其他智能体的 {other_agent_id: bool} 映射
        否则返回项目所有智能体的 {source_agent_id: {target_agent_id: bool}} 双向矩阵
    """
    async for session in db_config.get_session():
        service = AgentNeighborService(session)

        if agent_id:
            neighbors = await service.get_all_neighbors(project_id, agent_id)
            return {"agent_id": agent_id, "neighbors": neighbors}
        else:
            matrix = await service.get_all_neighbors_matrix(project_id)
            return matrix


@router.post("/project/{project_id}", response_model=NeighborResponse)
async def set_agent_neighbor(
    project_id: int,
    request: SetNeighborRequest
):
    """
    设置两个智能体之间的邻接关系(单对)

    Args:
        project_id: 项目ID
        request: source_id / target_id / is_neighbor

    Returns:
        操作结果
    """
    async for session in db_config.get_session():
        service = AgentNeighborService(session)
        await service.set_neighbor(
            project_id,
            request.source_id,
            request.target_id,
            request.is_neighbor
        )
        await session.commit()
        return NeighborResponse(message="Neighbor updated")


@router.post("/project/{project_id}/initialize", response_model=NeighborResponse)
async def initialize_agent_neighbors(project_id: int):
    """
    初始化项目的邻接关系

    为项目中所有 C(n, 2) 对子建立 is_neighbor=False 的默认记录。
    若调用方需要带默认 True 对子, 请使用 scene 创建流程或 /batch 接口。

    Args:
        project_id: 项目ID

    Returns:
        操作结果
    """
    async for session in db_config.get_session():
        service = AgentNeighborService(session)
        await service.initialize_neighbors(project_id)
        return NeighborResponse(message="Neighbors initialized")


@router.post("/project/{project_id}/batch", response_model=NeighborResponse)
async def batch_set_agent_neighbors(
    project_id: int,
    request: BatchSetNeighborRequest
):
    """
    批量设置邻接关系

    Args:
        project_id: 项目ID
        request: updates 列表 [{source_id, target_id, is_neighbor}, ...]

    Returns:
        操作结果
    """
    async for session in db_config.get_session():
        service = AgentNeighborService(session)
        for upd in request.updates:
            await service.set_neighbor(
                project_id,
                upd.source_id,
                upd.target_id,
                upd.is_neighbor
            )
        await session.commit()
        return NeighborResponse(
            message=f"Batch update completed: {len(request.updates)} pairs"
        )
