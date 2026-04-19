"""
仿真项目管理服务
负责项目的创建、查询、更新和删除
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from sqlalchemy import select
from app.config.database import db_config
from app.models import SimulationProject


class ProjectService:
    """
    仿真项目管理服务

    提供仿真项目的完整生命周期管理：
    - 项目创建
    - 项目查询
    - 项目更新
    - 项目删除
    """

    async def create_project(self, project_name: str, project_desc: Optional[str] = None,
                          total_rounds: int = 50, scene_source: str = "自定义") -> dict:
        """
        创建仿真项目

        Args:
            project_name: 项目名称
            project_desc: 项目描述（可选）
            total_rounds: 总轮数（默认50）
            scene_source: 场景来源（默认"自定义"）

        Returns:
            创建的项目信息字典
        """
        async for session in db_config.get_session():
            project = SimulationProject(
                project_name=project_name,
                project_desc=project_desc,
                scene_source=scene_source,
                total_rounds=total_rounds,
                current_round=0,
                status="未启动",
                respect_sov_threshold=0.6,
                leader_threshold=0.6
            )
            session.add(project)
            await session.commit()
            await session.refresh(project)

            return {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "project_desc": project.project_desc,
                "scene_source": project.scene_source,
                "total_rounds": project.total_rounds,
                "current_round": project.current_round,
                "status": project.status,
                "respect_sov_threshold": project.respect_sov_threshold,
                "leader_threshold": project.leader_threshold,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }

    async def get_projects(self, status_filter: Optional[str] = None) -> List[dict]:
        """
        获取所有仿真项目列表

        支持按状态筛选。

        Args:
            status_filter: 状态筛选条件（可选）

        Returns:
            项目列表
        """
        async for session in db_config.get_session():
            query = select(SimulationProject)
            if status_filter:
                query = query.where(SimulationProject.status == status_filter)
            result = await session.execute(query)
            projects = result.scalars().all()

            return [
                {
                    "project_id": p.project_id,
                    "project_name": p.project_name,
                    "project_desc": p.project_desc,
                    "scene_source": p.scene_source,
                    "total_rounds": p.total_rounds,
                    "current_round": p.current_round,
                    "status": p.status,
                    "respect_sov_threshold": p.respect_sov_threshold,
                    "leader_threshold": p.leader_threshold,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at
                }
                for p in projects
            ]

    async def get_project(self, project_id: int) -> Optional[dict]:
        """
        获取项目详情

        Args:
            project_id: 项目ID

        Returns:
            项目详情字典，或None（如果不存在）
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationProject).where(SimulationProject.project_id == project_id)
            )
            project = result.scalar_one_or_none()

            if not project:
                return None

            return {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "project_desc": project.project_desc,
                "scene_source": project.scene_source,
                "total_rounds": project.total_rounds,
                "current_round": project.current_round,
                "status": project.status,
                "respect_sov_threshold": project.respect_sov_threshold,
                "leader_threshold": project.leader_threshold,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }

    async def update_project(self, project_id: int, **kwargs) -> Optional[dict]:
        """
        更新项目基础信息

        Args:
            project_id: 项目ID
            **kwargs: 需要更新的字段和值

        Returns:
            更新后的项目信息字典，或None（如果不存在）
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationProject).where(SimulationProject.project_id == project_id)
            )
            project = result.scalar_one_or_none()

            if not project:
                return None

            for key, value in kwargs.items():
                if hasattr(project, key):
                    setattr(project, key, value)

            await session.commit()
            await session.refresh(project)

            return {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "project_desc": project.project_desc,
                "scene_source": project.scene_source,
                "total_rounds": project.total_rounds,
                "current_round": project.current_round,
                "status": project.status,
                "respect_sov_threshold": project.respect_sov_threshold,
                "leader_threshold": project.leader_threshold,
                "created_at": project.created_at,
                "updated_at": project.updated_at
            }

    async def delete_project(self, project_id: int) -> bool:
        """
        删除仿真项目

        Args:
            project_id: 项目ID

        Returns:
            删除是否成功
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationProject).where(SimulationProject.project_id == project_id)
            )
            project = result.scalar_one_or_none()

            if not project:
                return False

            await session.delete(project)
            await session.commit()
            return True


# 单例实例
project_service = ProjectService()
