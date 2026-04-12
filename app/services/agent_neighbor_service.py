"""
邻接关系服务 - AgentNeighborService
提供智能体邻接关系(二元 is_neighbor)的初始化、查询和更新功能。

与 StrategicRelationshipService 的核心差异:
- 字段仅有 is_neighbor: bool, 无 enum
- 不需要 _validate_neighbor_pair 配对规则 — 所有对子均允许设置
- 与 strategic_relationship 一致, 用 _normalize_pair 保证 source<target
"""

from typing import Dict, List, Optional, Set, Tuple

from loguru import logger
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AgentNeighbor, AgentConfig


class AgentNeighborService:
    """邻接关系管理服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize_neighbors(
        self,
        project_id: int,
        default_pairs: Optional[Set[Tuple[int, int]]] = None
    ) -> None:
        """
        初始化项目中所有智能体之间的邻接关系

        为项目中所有 C(n, 2) 对子建立记录, 默认 is_neighbor=False;
        若某对子(以 normalized pair 形式)出现在 default_pairs 中, 则设为 True。

        Args:
            project_id: 项目ID
            default_pairs: 可选, 默认为邻接关系(True)的智能体对子集合。
                          集合元素为 (agent_a, agent_b) 元组, 内部会做 normalize。
        """
        # 获取项目中所有智能体
        all_agents = await self._get_all_agents(project_id)
        logger.info(f"Initializing neighbors for project {project_id}: {len(all_agents)} agents")

        # 规范化 default_pairs 为 normalized 形式以便比对
        normalized_defaults: Set[Tuple[int, int]] = set()
        if default_pairs:
            for a, b in default_pairs:
                normalized_defaults.add(self._normalize_pair(a, b))

        # 遍历所有无向对子 (i < j)
        pair_count = 0
        for i, source in enumerate(all_agents):
            for target in all_agents[i + 1:]:
                src_id, tgt_id = self._normalize_pair(source.agent_id, target.agent_id)
                is_neighbor = (src_id, tgt_id) in normalized_defaults
                await self._ensure_neighbor(project_id, src_id, tgt_id, is_neighbor)
                pair_count += 1

        await self.db.commit()
        logger.info(
            f"Agent neighbors initialized for project {project_id}: "
            f"{pair_count} pairs, {len(normalized_defaults)} defaulted to True"
        )

    async def _ensure_neighbor(
        self,
        project_id: int,
        agent_a: int,
        agent_b: int,
        is_neighbor: bool
    ) -> AgentNeighbor:
        """
        确保存在两个智能体之间的邻接记录, 不存在则创建

        采用"读时自愈": 即使表中存在重复(历史遗留), 仅取 relation_id 最大的一条,
        并删除其余冗余记录。

        Args:
            project_id: 项目ID
            agent_a: 智能体A的ID
            agent_b: 智能体B的ID
            is_neighbor: 是否为邻国
        """
        source_id, target_id = self._normalize_pair(agent_a, agent_b)

        stmt = select(AgentNeighbor).where(
            and_(
                AgentNeighbor.project_id == project_id,
                AgentNeighbor.source_agent_id == source_id,
                AgentNeighbor.target_agent_id == target_id
            )
        ).order_by(AgentNeighbor.relation_id.desc())

        result = await self.db.execute(stmt)
        all_existing = result.scalars().all()

        if all_existing:
            existing = all_existing[0]
            # 清理多余的重复记录(保留 relation_id 最大的一条)
            if len(all_existing) > 1:
                logger.warning(
                    f"agent_neighbor 表存在重复记录(project={project_id}, "
                    f"{source_id}<->{target_id}, 共{len(all_existing)}条), "
                    f"自动清理 {len(all_existing)-1} 条冗余"
                )
                for dup in all_existing[1:]:
                    await self.db.delete(dup)

            existing.is_neighbor = is_neighbor
            return existing
        else:
            new_relation = AgentNeighbor(
                project_id=project_id,
                source_agent_id=source_id,
                target_agent_id=target_id,
                is_neighbor=is_neighbor
            )
            self.db.add(new_relation)
            return new_relation

    async def set_neighbor(
        self,
        project_id: int,
        source_id: int,
        target_id: int,
        is_neighbor: bool
    ) -> None:
        """
        设置两个智能体之间的邻接关系

        不做配对规则校验 — 所有智能体对子均允许设置。

        注意: 此方法不会自动提交到数据库, 调用方需要手动调用 await self.db.commit()
        或在数据库会话上下文管理器内调用, 让上下文管理器自动提交。
        """
        await self._ensure_neighbor(project_id, source_id, target_id, is_neighbor)

    async def get_neighbor(
        self,
        project_id: int,
        source_id: int,
        target_id: int
    ) -> bool:
        """获取两个智能体之间的邻接关系, 不存在则返回 False"""
        a, b = self._normalize_pair(source_id, target_id)

        stmt = select(AgentNeighbor.is_neighbor).where(
            and_(
                AgentNeighbor.project_id == project_id,
                AgentNeighbor.source_agent_id == a,
                AgentNeighbor.target_agent_id == b
            )
        ).order_by(AgentNeighbor.relation_id.desc()).limit(1)

        result = await self.db.execute(stmt)
        value = result.scalars().first()
        return bool(value) if value is not None else False

    async def get_all_neighbors(self, project_id: int, agent_id: int) -> Dict[int, bool]:
        """
        获取一个智能体与所有其他智能体的邻接关系

        同时查 source 和 target 两端, 返回 {other_agent_id: is_neighbor} 字典。
        """
        stmt_source = select(AgentNeighbor).where(
            and_(
                AgentNeighbor.project_id == project_id,
                AgentNeighbor.source_agent_id == agent_id
            )
        )
        result_source = await self.db.execute(stmt_source)
        source_relations = result_source.scalars().all()

        stmt_target = select(AgentNeighbor).where(
            and_(
                AgentNeighbor.project_id == project_id,
                AgentNeighbor.target_agent_id == agent_id
            )
        )
        result_target = await self.db.execute(stmt_target)
        target_relations = result_target.scalars().all()

        neighbors: Dict[int, bool] = {}
        for rel in source_relations:
            neighbors[rel.target_agent_id] = bool(rel.is_neighbor)
        for rel in target_relations:
            neighbors[rel.source_agent_id] = bool(rel.is_neighbor)

        return neighbors

    async def get_all_neighbors_matrix(self, project_id: int) -> Dict[int, Dict[int, bool]]:
        """
        获取项目中所有智能体的邻接关系双向矩阵

        Returns:
            {agent_id: {other_agent_id: is_neighbor}} 形式的嵌套字典 (对称展开)
        """
        stmt = select(AgentNeighbor).where(
            AgentNeighbor.project_id == project_id
        )

        result = await self.db.execute(stmt)
        all_relations = result.scalars().all()

        matrix: Dict[int, Dict[int, bool]] = {}

        for rel in all_relations:
            is_n = bool(rel.is_neighbor)
            if rel.source_agent_id not in matrix:
                matrix[rel.source_agent_id] = {}
            matrix[rel.source_agent_id][rel.target_agent_id] = is_n

            if rel.target_agent_id not in matrix:
                matrix[rel.target_agent_id] = {}
            matrix[rel.target_agent_id][rel.source_agent_id] = is_n

        return matrix

    async def _get_all_agents(self, project_id: int) -> List[AgentConfig]:
        """获取项目中所有智能体, 按 agent_id 升序"""
        stmt = select(AgentConfig).where(
            AgentConfig.project_id == project_id
        ).order_by(AgentConfig.agent_id)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _normalize_pair(self, agent_a: int, agent_b: int) -> tuple:
        """确保 agent_a < agent_b, 避免重复存储"""
        if agent_a < agent_b:
            return agent_a, agent_b
        else:
            return agent_b, agent_a
