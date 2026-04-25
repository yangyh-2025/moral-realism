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

    async def initialize_relationships(self, project_id: int, skip_existing: bool = False) -> None:
        """
        初始化项目中大国/超级大国与中小国家之间的战略关系

        配对规则（允许建立关系的组合）：
        - 超级大国 × 大国
        - 超级大国 × 中等强国
        - 超级大国 × 小国
        - 大国 × 中等强国
        - 大国 × 小国

        不建立关系的组合：
        - 中等强国 × 中等强国
        - 中等强国 × 小国
        - 小国 × 小国

        Args:
            project_id: 项目ID
            skip_existing: 如果为True，跳过已存在的关系而不覆盖
        """
        # 分别获取不同层级的智能体
        superpowers = await self._get_agents_by_power_level(project_id, PowerLevelEnum.SUPERPOWER)
        great_powers = await self._get_agents_by_power_level(project_id, PowerLevelEnum.GREAT_POWER)
        middle_powers = await self._get_agents_by_power_level(project_id, PowerLevelEnum.MIDDLE_POWER)
        small_states = await self._get_agents_by_power_level(project_id, PowerLevelEnum.SMALL_STATE)

        # 高层级智能体（超级大国 + 大国）
        high_level_agents = superpowers + great_powers
        # 低层级智能体（中等强国 + 小国）
        low_level_agents = middle_powers + small_states

        logger.info(
            f"Found {len(superpowers)} superpowers, {len(great_powers)} great powers, "
            f"{len(middle_powers)} middle powers, {len(small_states)} small states"
        )

        # 建立高层级 × 低层级的关系
        for high in high_level_agents:
            for low in low_level_agents:
                await self._ensure_relationship(
                    project_id,
                    high.agent_id,
                    low.agent_id,
                    StrategicRelationshipEnum.NO_DIPLOMACY,
                    skip_existing=skip_existing
                )

        # 建立高层级内部之间的关系
        for i, source in enumerate(high_level_agents):
            for target in high_level_agents[i+1:]:
                await self._ensure_relationship(
                    project_id,
                    source.agent_id,
                    target.agent_id,
                    StrategicRelationshipEnum.NO_DIPLOMACY,
                    skip_existing=skip_existing
                )

        await self.db.commit()
        logger.info(f"Strategic relationships initialized for project {project_id}")

    async def _ensure_relationship(
        self,
        project_id: int,
        agent_a: int,
        agent_b: int,
        relationship_type: str,
        skip_existing: bool = False
    ) -> StrategicRelationship:
        """
        确保存在两个智能体之间的关系，不存在则创建

        Args:
            project_id: 项目ID
            agent_a: 智能体A的ID
            agent_b: 智能体B的ID
            relationship_type: 关系类型
            skip_existing: 如果为True，跳过已存在的关系而不更新
        """
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
            if not skip_existing:
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
        """
        设置两个智能体之间的战略关系

        验证配对规则，只允许在符合规则的智能体之间建立关系。

        注意：此方法不会自动提交到数据库，调用方需要手动调用 await self.db.commit()
        或在数据库会话上下文管理器内调用，让上下文管理器自动提交。
        """
        # 获取两个智能体的国力等级
        source_agent = await self._get_agent_by_id(project_id, source_id)
        target_agent = await self._get_agent_by_id(project_id, target_id)

        if not source_agent or not target_agent:
            raise ValueError("智能体不存在")

        # 验证配对规则
        if not self._validate_relationship_pair(
            source_agent.power_level,
            target_agent.power_level
        ):
            raise ValueError(
                f"不允许在 {source_agent.power_level} 和 "
                f"{target_agent.power_level} 之间建立战略关系"
            )

        await self._ensure_relationship(project_id, source_id, target_id, relationship_type)

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

    async def _get_agent_by_id(
        self, project_id: int, agent_id: int
    ) -> Optional[AgentConfig]:
        """
        获取指定ID的智能体

        Args:
            project_id: 项目ID
            agent_id: 智能体ID

        Returns:
            智能体对象，不存在则返回None
        """
        stmt = select(AgentConfig).where(
            AgentConfig.project_id == project_id,
            AgentConfig.agent_id == agent_id
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_agents_by_power_level(
        self, project_id: int, power_level: PowerLevelEnum
    ) -> List[AgentConfig]:
        """
        获取指定国力等级的所有智能体

        Args:
            project_id: 项目ID
            power_level: 国力等级

        Returns:
            智能体列表
        """
        stmt = select(AgentConfig).where(
            AgentConfig.project_id == project_id,
            AgentConfig.power_level == power_level
        ).order_by(AgentConfig.agent_id)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    def _validate_relationship_pair(
        self, source_power, target_power
    ) -> bool:
        """
        验证两个层级的智能体是否允许建立战略关系

        允许的配对：
        - 超级大国 × 大国
        - 超级大国 × 中等强国
        - 超级大国 × 小国
        - 大国 × 中等强国
        - 大国 × 小国

        不允许的配对：
        - 中等强国 × 中等强国
        - 中等强国 × 小国
        - 小国 × 小国

        Args:
            source_power: 源智能体的国力等级（字符串或枚举）
            target_power: 目标智能体的国力等级（字符串或枚举）

        Returns:
            bool: 是否允许建立关系
        """
        # 如果是枚举对象，获取值
        if hasattr(source_power, 'value'):
            source_value = source_power.value
        else:
            source_value = source_power

        if hasattr(target_power, 'value'):
            target_value = target_power.value
        else:
            target_value = target_power

        # 定义各个层级的枚举值（使用前缀以避免中文截断问题）
        # 超级大国: '超级大国'
        # 大国: '大国'
        # 中等强国: '中等强国'
        # 小国: '小国'
        high_level_prefixes = ['超级', '大国']
        low_level_prefixes = ['中等', '小国']

        # 检查前缀匹配
        def is_high_level(level_str):
            return any(level_str.startswith(prefix) for prefix in high_level_prefixes)

        def is_low_level(level_str):
            return any(level_str.startswith(prefix) for prefix in low_level_prefixes)

        # 高层级 × 低层级：允许
        if (is_high_level(source_value) and is_low_level(target_value)) or \
           (is_high_level(target_value) and is_low_level(source_value)):
            return True

        # 高层级 × 高层级：允许
        if is_high_level(source_value) and is_high_level(target_value):
            return True

        return False

    def _normalize_pair(self, agent_a: int, agent_b: int) -> tuple:
        """确保 agent_a < agent_b，避免重复存储"""
        if agent_a < agent_b:
            return agent_a, agent_b
        else:
            return agent_b, agent_a
