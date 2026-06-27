"""
仿真项目管理服务
负责项目的创建、查询、更新和删除
"""

import io
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func, select
from app.config.database import db_config
from app.models import SimulationProject
from app.models.agent_config import AgentConfig
from app.models.agent_power_history import AgentPowerHistory
from app.models.follower_relation import FollowerRelation
from app.models.simulation_round import SimulationRound
from app.models.action_record import ActionRecord
from app.models.strategic_goal_evaluation import StrategicGoalEvaluation
from app.models.strategic_relationship import StrategicRelationship


class ProjectService:
    """
    仿真项目管理服务

    提供仿真项目的完整生命周期管理：
    - 项目创建
    - 项目查询（支持分页、筛选、排序）
    - 项目更新
    - 项目删除（含 logs 清理）
    - 项目导出（ZIP 打包）
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

            return self._project_to_dict(project)

    async def get_projects(
        self,
        status_filter: Optional[str] = None,
        scene_source: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        size: int = 20,
        sort: str = "updated_at_desc",
    ) -> Dict[str, Any]:
        """
        获取仿真项目列表（支持分页、筛选、排序）

        Args:
            status_filter: 状态筛选条件（可选）
            scene_source: 场景来源筛选（可选）
            keyword: 关键词搜索（匹配项目名或描述）（可选）
            page: 页码（从1开始）
            size: 每页条数
            sort: 排序字段,格式为 "field_desc" 或 "field_asc"

        Returns:
            {"total": int, "items": List[dict]}
        """
        async for session in db_config.get_session():
            # 计数查询
            count_query = select(func.count()).select_from(SimulationProject)
            query = select(SimulationProject)

            # 筛选
            if status_filter:
                count_query = count_query.where(SimulationProject.status == status_filter)
                query = query.where(SimulationProject.status == status_filter)
            if scene_source:
                count_query = count_query.where(SimulationProject.scene_source == scene_source)
                query = query.where(SimulationProject.scene_source == scene_source)
            if keyword:
                like_pattern = f"%{keyword}%"
                count_query = count_query.where(
                    SimulationProject.project_name.ilike(like_pattern) |
                    SimulationProject.project_desc.ilike(like_pattern)
                )
                query = query.where(
                    SimulationProject.project_name.ilike(like_pattern) |
                    SimulationProject.project_desc.ilike(like_pattern)
                )

            # 排序
            sort_field, sort_dir = sort.rsplit("_", 1) if "_" in sort else ("updated_at", "desc")
            sort_col = getattr(SimulationProject, sort_field, SimulationProject.updated_at)
            if sort_dir == "asc":
                query = query.order_by(sort_col.asc())
            else:
                query = query.order_by(desc(sort_col))

            # 总数
            count_result = await session.execute(count_query)
            total = count_result.scalar() or 0

            # 分页
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)

            result = await session.execute(query)
            projects = result.scalars().all()

            # 获取每个项目的 agent 数量
            project_ids = [p.project_id for p in projects]
            agent_counts = {}
            if project_ids:
                agent_query = (
                    select(AgentConfig.project_id, func.count().label("count"))
                    .where(AgentConfig.project_id.in_(project_ids))
                    .group_by(AgentConfig.project_id)
                )
                agent_result = await session.execute(agent_query)
                for row in agent_result.mappings().all():
                    agent_counts[row["project_id"]] = row["count"]

            items = []
            for p in projects:
                d = self._project_to_dict(p)
                d["agent_count"] = agent_counts.get(p.project_id, 0)
                items.append(d)

            return {"total": total, "items": items}

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

            return self._project_to_dict(project)

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

            return self._project_to_dict(project)

    async def delete_project(self, project_id: int) -> bool:
        """
        删除仿真项目（含级联清理 logs 目录）

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

        # 清理 logs 目录（级联删除数据库已通过 SQLAlchemy cascade 处理）
        log_dir = Path("logs") / str(project_id)
        if log_dir.exists():
            shutil.rmtree(log_dir, ignore_errors=True)

        return True

    async def export_project(self, project_id: int) -> Optional[bytes]:
        """
        导出项目全部数据为 ZIP 压缩包

        Args:
            project_id: 项目ID

        Returns:
            ZIP 字节流，或 None（项目不存在）
        """
        async for session in db_config.get_session():
            project = await session.get(SimulationProject, project_id)
            if not project:
                return None

            # 收集所有关联数据
            result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = [self._orm_to_dict(a) for a in result.scalars().all()]

            result = await session.execute(
                select(SimulationRound).where(SimulationRound.project_id == project_id)
            )
            rounds = [self._orm_to_dict(r) for r in result.scalars().all()]

            result = await session.execute(
                select(ActionRecord).where(ActionRecord.project_id == project_id)
            )
            actions = [self._orm_to_dict(a) for a in result.scalars().all()]

            result = await session.execute(
                select(FollowerRelation).where(FollowerRelation.project_id == project_id)
            )
            follower_relations = [self._orm_to_dict(f) for f in result.scalars().all()]

            result = await session.execute(
                select(AgentPowerHistory).where(AgentPowerHistory.project_id == project_id)
            )
            power_histories = [self._orm_to_dict(h) for h in result.scalars().all()]

            result = await session.execute(
                select(StrategicRelationship).where(StrategicRelationship.project_id == project_id)
            )
            relationships = [self._orm_to_dict(r) for r in result.scalars().all()]

            result = await session.execute(
                select(StrategicGoalEvaluation).where(StrategicGoalEvaluation.project_id == project_id)
            )
            goal_evaluations = [self._orm_to_dict(g) for g in result.scalars().all()]

        # 打包为 ZIP
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("project.json", json.dumps(self._project_to_dict(project), ensure_ascii=False, default=str, indent=2))
            zf.writestr("agents.json", json.dumps(agents, ensure_ascii=False, default=str, indent=2))
            zf.writestr("rounds.json", json.dumps(rounds, ensure_ascii=False, default=str, indent=2))
            zf.writestr("actions.json", json.dumps(actions, ensure_ascii=False, default=str, indent=2))
            zf.writestr("follower_relations.json", json.dumps(follower_relations, ensure_ascii=False, default=str, indent=2))
            zf.writestr("power_histories.json", json.dumps(power_histories, ensure_ascii=False, default=str, indent=2))
            zf.writestr("strategic_relationships.json", json.dumps(relationships, ensure_ascii=False, default=str, indent=2))
            zf.writestr("goal_evaluations.json", json.dumps(goal_evaluations, ensure_ascii=False, default=str, indent=2))

            # 添加 logs 目录下的所有文件
            log_dir = Path("logs") / str(project_id)
            if log_dir.exists():
                for log_file in log_dir.rglob("*"):
                    if log_file.is_file():
                        arcname = f"logs/{log_file.relative_to(log_dir)}"
                        zf.write(log_file, arcname)

        buf.seek(0)
        return buf.read()

    @staticmethod
    def _ensure_utc(dt):
        """Attach UTC timezone to a naive datetime (SQLite returns naive datetimes)."""
        if dt is not None and dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _project_to_dict(project: SimulationProject) -> dict:
        """将 SimulationProject ORM 对象转为字典"""
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
            "started_at": ProjectService._ensure_utc(project.started_at),
            "completed_at": ProjectService._ensure_utc(project.completed_at),
            "duration_seconds": project.duration_seconds,
            "created_at": ProjectService._ensure_utc(project.created_at),
            "updated_at": ProjectService._ensure_utc(project.updated_at),
        }

    @staticmethod
    def _orm_to_dict(obj: Any) -> dict:
        """通用 ORM 对象转字典"""
        d = {}
        for col in obj.__table__.columns:
            val = getattr(obj, col.name)
            d[col.name] = val
        return d


# 单例实例
project_service = ProjectService()
