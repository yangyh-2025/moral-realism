"""
战略关系服务 - StrategicRelationshipService
提供战略关系的初始化、查询和更新功能。
"""

from typing import Dict, List, Optional

from loguru import logger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import StrategicRelationship, AgentConfig
from ..models.agent_config import PowerLevelEnum
from ..models.strategic_relationship import StrategicRelationshipEnum


class StrategicRelationshipService:
    """战略关系管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize_relationships(self, project_id: int) -> None:
        """
        初始化项目中所有大国/超级大国之间的战略关系

        规则：
        1. 获取所有超级大国和大国
        2. 两两配对初始化关系
        3. 默认关系为"无外交关系"
        """
        stmt = select(AgentConfig).where(
            AgentConfig.project_id == project_id,
            AgentConfig.power_level.in_([PowerLevelEnum.SUPERPOWER, PowerLevelEnum.GREAT_POWER])
        ).order_by(AgentConfig.agent_id)

        result = await self.db.execute(stmt)
        major_powers = result.scalars().all()

        logger.info(f"Found {len(major_powers)} major powers for relationship initialization")

        for i, source in enumerate(major_powers):
            for target in major_powers[i+1:]:
                await self._ensure_relationship(
                    project_id,
                    source.agent_id,
                    target.agent_id,
                    StrategicRelationshipEnum.NO_DIPLOMACY
                )

        await self.db.commit()
        logger.info(f"Strategic relationships initialized for project {project_id}")

    async def _ensure_relationship(
        self,
        project_id: int,
        agent_a: int,
        agent_b: int,
        relationship_type: str
    ) -> StrategicRelationship:
        """确保存在两个智能体之间的关系，不存在则创建"""
        source_id, target_id = self._normalize_pair(agent_a, agent_b)

        stmt = select(StrategicRelationship).where(
            and_(
                StrategicRelationship.project_id == project_id,
                StrategicRelationship.source_agent_id == source_id,
                StrategicRelationship.target_agent_id == target_id
            )
        )

        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.relationship_type = relationship_type
            return existing
        else:
            new_relation = StrategicRelationship(
                project_id=project_id,
                source_agent_id=source_id,
                target_agent_id=target_id,
                relationship_type=relationship_type
            )
            self.db.add(new_relation)
            return new_relation

    async def set_relationship(
        self,
        project_id: int,
        source_id: int,
        target_id: int,
        relationship_type: str
    ) -> None:
        """设置两个智能体之间的战略关系"""
        await self._ensure_relationship(project_id, source_id, target_id, relationship_type)
        await self.db.commit()

    async def get_relationship(
        self,
        project_id: int,
        source_id: int,
        target_id: int
    ) -> Optional[str]:
        """获取两个智能体之间的战略关系"""
        a, b = self._normalize_pair(source_id, target_id)

        stmt = select(StrategicRelationship.relationship_type).where(
            and_(
                StrategicRelationship.project_id == project_id,
                StrategicRelationship.source_agent_id == a,
                StrategicRelationship.target_agent_id == b
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_relationships(self, project_id: int, agent_id: int) -> Dict[int, str]:
        """获取一个智能体与所有其他大国的战略关系"""
        stmt_source = select(StrategicRelationship).where(
            and_(
                StrategicRelationship.project_id == project_id,
                StrategicRelationship.source_agent_id == agent_id
            )
        )

        result_source = await self.db.execute(stmt_source)
        source_relations = result_source.scalars().all()

        stmt_target = select(StrategicRelationship).where(
            and_(
                StrategicRelationship.project_id == project_id,
                StrategicRelationship.target_agent_id == agent_id
            )
        )

        result_target = await self.db.execute(stmt_target)
        target_relations = result_target.scalars().all()

        relationships = {}
        for rel in source_relations:
            relationships[rel.target_agent_id] = rel.relationship_type
        for rel in target_relations:
            relationships[rel.source_agent_id] = rel.relationship_type

        return relationships

    async def get_all_agents_relationships(self, project_id: int) -> Dict[int, Dict[int, str]]:
        """获取项目中所有智能体的战略关系映射"""
        stmt = select(StrategicRelationship).where(
            StrategicRelationship.project_id == project_id
        )

        result = await self.db.execute(stmt)
        all_relations = result.scalars().all()

        relationships_map: Dict[int, Dict[int, str]] = {}

        for rel in all_relations:
            if rel.source_agent_id not in relationships_map:
                relationships_map[rel.source_agent_id] = {}
            relationships_map[rel.source_agent_id][rel.target_agent_id] = rel.relationship_type

            if rel.target_agent_id not in relationships_map:
                relationships_map[rel.target_agent_id] = {}
            relationships_map[rel.target_agent_id][rel.source_agent_id] = rel.relationship_type

        return relationships_map

    def _normalize_pair(self, agent_a: int, agent_b: int) -> tuple:
        """确保 agent_a < agent_b，避免重复存储"""
        if agent_a < agent_b:
            return agent_a, agent_b
        else:
            return agent_b, agent_a
