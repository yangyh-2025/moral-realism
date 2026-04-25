"""
统计分析服务
负责仿真数据的统计计算和分析
"""

from typing import List, Optional
import numpy as np
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.config.database import db_config
from app.models import (
    AgentConfig,
    StrategicGoalEvaluation,
    AgentPowerHistory,
    ActionRecord,
    SimulationRound,
    FollowerRelation
)


class StatisticsService:
    """
    统计分析服务

    提供仿真数据的统计计算和分析功能，包括：
    - 国力历史数据查询
    - 实力增长率计算
    - 行为偏好统计
    - 国际秩序演变分析
    - 战略目标评估数据查询
    """

    async def get_power_history(self, project_id: int, agent_id: Optional[int] = None,
                               start_round: Optional[int] = None,
                               end_round: Optional[int] = None) -> List[dict]:
        """
        获取项目全量智能体国力历史数据

        支持按智能体、轮次范围筛选。

        Args:
            project_id: 项目ID
            agent_id: 可选，智能体ID
            start_round: 可选，起始轮次
            end_round: 可选，结束轮次

        Returns:
            国力历史数据列表
        """
        async for session in db_config.get_session():
            query = select(AgentPowerHistory, AgentConfig.agent_name).join(
                AgentConfig, AgentPowerHistory.agent_id == AgentConfig.agent_id
            ).where(AgentPowerHistory.project_id == project_id)

            if agent_id is not None:
                query = query.where(AgentPowerHistory.agent_id == agent_id)

            if start_round is not None:
                query = query.where(AgentPowerHistory.round_num >= start_round)

            if end_round is not None:
                query = query.where(AgentPowerHistory.round_num <= end_round)

            query = query.order_by(AgentPowerHistory.round_num, AgentPowerHistory.agent_id)

            result = await session.execute(query)
            rows = result.all()

            return [
                {
                    "history_id": history.history_id,
                    "agent_id": history.agent_id,
                    "agent_name": agent_name,
                    "round_num": history.round_num,
                    "round_start_power": history.round_start_power,
                    "round_end_power": history.round_end_power,
                    "round_change_value": history.round_change_value,
                    "round_change_rate": history.round_change_rate,
                }
                for history, agent_name in rows
            ]

    async def calculate_power_growth_rate(self, project_id: int, start_round: int = 1,
                                       end_round: Optional[int] = None) -> List[dict]:
        """
        计算自定义轮次区间的实力增长率

        按领导类型和实力层级分组计算平均增长率。

        Args:
            project_id: 项目ID
            start_round: 起始轮次（默认1）
            end_round: 结束轮次（默认最新轮次）

        Returns:
            - 相同领导类型+相同实力层级的平均增长率
            - 相同领导类型+不同实力层级的平均增长率
        """
        async for session in db_config.get_session():
            query = select(
                AgentPowerHistory,
                AgentConfig.agent_name,
                AgentConfig.leader_type,
                AgentConfig.power_level
            ).join(
                AgentConfig, AgentPowerHistory.agent_id == AgentConfig.agent_id
            ).where(
                AgentPowerHistory.project_id == project_id,
                AgentPowerHistory.round_num >= start_round
            )

            if end_round is not None:
                query = query.where(AgentPowerHistory.round_num <= end_round)

            result = await session.execute(query)
            rows = result.all()

            # 按领导类型和实力层级分组计算平均增长率
            groups = {}
            for history, agent_name, leader_type, power_level in rows:
                key = f"{leader_type or '无'}|{power_level}"
                if key not in groups:
                    groups[key] = {
                        "leader_type": leader_type or "无",
                        "power_level": power_level,
                        "total_growth_rate": 0.0,
                        "count": 0
                    }
                groups[key]["total_growth_rate"] += history.round_change_rate
                groups[key]["count"] += 1

            return [
                {
                    "leader_type": group["leader_type"],
                    "power_level": group["power_level"],
                    "avg_growth_rate": round(group["total_growth_rate"] / group["count"], 4),
                    "sample_size": group["count"]
                }
                for group in groups.values()
            ]

    async def get_action_preference(self, project_id: int, agent_id: Optional[int] = None,
                                  power_level: Optional[str] = None,
                                  leader_type: Optional[str] = None,
                                  start_round: Optional[int] = None,
                                  end_round: Optional[int] = None) -> List[dict]:
        """
        获取行为偏好统计数据

        统计行为频次、分类占比、主权尊重行为占比等。

        Args:
            project_id: 项目ID
            agent_id: 可选，智能体ID
            power_level: 可选，实力层级筛选
            leader_type: 可选，领导类型筛选
            start_round: 可选，起始轮次
            end_round: 可选，结束轮次

        Returns:
            - 20项互动行为的频次统计
            - 行为分类占比
            - 主权尊重行为占比
            - 高烈度/低烈度行为占比
        """
        async for session in db_config.get_session():
            query = select(
                ActionRecord,
                AgentConfig.power_level,
                AgentConfig.leader_type
            ).join(
                AgentConfig, ActionRecord.source_agent_id == AgentConfig.agent_id
            ).where(ActionRecord.project_id == project_id)

            if agent_id is not None:
                query = query.where(ActionRecord.source_agent_id == agent_id)

            if start_round is not None:
                query = query.where(ActionRecord.round_num >= start_round)

            if end_round is not None:
                query = query.where(ActionRecord.round_num <= end_round)

            result = await session.execute(query)
            rows = result.all()

            # 统计行为频次
            action_stats = {}
            total_count = 0

            for record, pl, lt in rows:
                if power_level and pl != power_level:
                    continue
                if leader_type and lt != leader_type:
                    continue

                total_count += 1
                key = record.action_name
                if key not in action_stats:
                    action_stats[key] = {
                        "action_id": record.action_id,
                        "action_name": record.action_name,
                        "action_category": record.action_category,
                        "count": 0
                    }
                action_stats[key]["count"] += 1

            return [
                {
                    "action_id": stats["action_id"],
                    "action_name": stats["action_name"],
                    "action_category": stats["action_category"],
                    "count": stats["count"],
                    "percentage": round(stats["count"] / total_count * 100, 2) if total_count > 0 else 0
                }
                for stats in action_stats.values()
            ]

    async def get_order_evolution(self, project_id: int) -> List[dict]:
        """
        获取国际秩序演变时序数据

        统计每轮的秩序类型、尊重主权率、领导国信息等。

        Returns:
            - 每轮的秩序类型
            - 尊重主权率趋势
            - 体系领导权更迭数据
            - 领导国追随率变化
        """
        async for session in db_config.get_session():
            query = select(SimulationRound).where(
                SimulationRound.project_id == project_id
            ).order_by(SimulationRound.round_num)

            result = await session.execute(query)
            rounds = result.scalars().all()

            return [
                {
                    "round_num": round_data.round_num,
                    "order_type": round_data.order_type,
                    "respect_sov_ratio": round_data.respect_sov_ratio,
                    "has_leader": round_data.has_leader,
                    "leader_follower_ratio": round_data.leader_follower_ratio
                }
                for round_data in rounds
                if round_data.order_type != "未判定"
            ]

    async def get_round_detail(self, project_id: int, round_num: int) -> Optional[dict]:
        """
        获取单轮仿真完整详情

        包含行为记录、国力变化、秩序判定、追随关系等信息。

        Args:
            project_id: 项目ID
            round_num: 轮次号

        Returns:
            - 本轮所有行为记录
            - 国力变化详情
            - 秩序判定结果
            - 追随关系数据
        """
        async for session in db_config.get_session():
            # 获取轮次数据
            round_result = await session.execute(
                select(SimulationRound).where(
                    SimulationRound.project_id == project_id,
                    SimulationRound.round_num == round_num
                )
            )
            round_data = round_result.scalar_one_or_none()

            if not round_data:
                return None

            # 获取行为记录
            actions_result = await session.execute(
                select(ActionRecord, AgentConfig.agent_name)
                .join(AgentConfig, ActionRecord.source_agent_id == AgentConfig.agent_id)
                .where(ActionRecord.round_id == round_data.round_id)
            )
            actions = actions_result.all()

            # 获取追随关系
            followers_result = await session.execute(
                select(FollowerRelation).where(
                    FollowerRelation.round_id == round_data.round_id
                )
            )
            follower_relations = followers_result.scalars().all()

            return {
                "round_id": round_data.round_id,
                "round_num": round_data.round_num,
                "total_action_count": round_data.total_action_count,
                "respect_sov_action_count": round_data.respect_sov_action_count,
                "respect_sov_ratio": round_data.respect_sov_ratio,
                "has_leader": round_data.has_leader,
                "order_type": round_data.order_type,
                "actions": [
                    {
                        "record_id": action.record_id,
                        "source_agent_id": action.source_agent_id,
                        "source_agent_name": agent_name,
                        "target_agent_id": action.target_agent_id,
                        "action_name": action.action_name,
                        "action_category": action.action_category,
                        "respect_sov": action.respect_sov
                    }
                    for action, agent_name in actions
                ],
                "follower_relations": [
                    {
                        "relation_id": rel.relation_id,
                        "follower_agent_id": rel.follower_agent_id,
                        "leader_agent_id": rel.leader_agent_id
                    }
                    for rel in follower_relations
                ]
            }

    async def get_goal_evaluations(
        self,
        project_id: int,
        agent_id: Optional[int] = None,
        start_round: Optional[int] = None,
        end_round: Optional[int] = None
    ) -> List[dict]:
        """
        获取战略目标评估数据

        支持按智能体、轮次范围筛选。

        Args:
            project_id: 项目ID
            agent_id: 可选，智能体ID
            start_round: 可选，起始轮次
            end_round: 可选，结束轮次

        Returns:
            - 指定轮次区间的评估记录
            - 可按智能体筛选
        """
        async for session in db_config.get_session():
            query = select(StrategicGoalEvaluation, AgentConfig.agent_name).join(
                AgentConfig, StrategicGoalEvaluation.agent_id == AgentConfig.agent_id
            ).where(StrategicGoalEvaluation.project_id == project_id)

            if agent_id is not None:
                query = query.where(StrategicGoalEvaluation.agent_id == agent_id)

            if start_round is not None:
                query = query.where(StrategicGoalEvaluation.evaluation_round >= start_round)

            if end_round is not None:
                query = query.where(StrategicGoalEvaluation.evaluation_round <= end_round)

            query = query.order_by(StrategicGoalEvaluation.evaluation_round, StrategicGoalEvaluation.agent_id)

            result = await session.execute(query)
            rows = result.all()

            return [
                {
                    "evaluation_id": eval.evaluation_id,
                    "agent_id": eval.agent_id,
                    "agent_name": agent_name,
                    "evaluation_round": eval.evaluation_round,
                    "evaluation_round_start": eval.evaluation_round_start,
                    "evaluation_round_end": eval.evaluation_round_end,
                    "goal_achievement_score": eval.goal_achievement_score,
                    "power_growth_contribution": eval.power_growth_contribution,
                    "action_effectiveness": eval.action_effectiveness,
                    "leadership_alignment": eval.leadership_alignment,
                    "overall_assessment": eval.overall_assessment,
                    "specific_achievements": eval.specific_achievements,
                    "challenges": eval.challenges,
                }
                for eval, agent_name in rows
            ]

    async def get_goal_evaluation_trend(
        self,
        project_id: int,
        agent_id: int
    ) -> List[dict]:
        """
        获取单个国家的目标达成度趋势

        统计指定国家在各个评估轮次的战略目标达成度数据。

        Args:
            project_id: 项目ID
            agent_id: 智能体ID

        Returns:
            - 该国所有评估轮次的达成度数据
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(StrategicGoalEvaluation, AgentConfig.agent_name).join(
                    AgentConfig, StrategicGoalEvaluation.agent_id == AgentConfig.agent_id
                ).where(
                    StrategicGoalEvaluation.project_id == project_id,
                    StrategicGoalEvaluation.agent_id == agent_id
                ).order_by(StrategicGoalEvaluation.evaluation_round)
            )
            rows = result.all()

            return [
                {
                    "evaluation_id": eval.evaluation_id,
                    "agent_id": eval.agent_id,
                    "agent_name": agent_name,
                    "evaluation_round": eval.evaluation_round,
                    "evaluation_round_start": eval.evaluation_round_start,
                    "evaluation_round_end": eval.evaluation_round_end,
                    "goal_achievement_score": eval.goal_achievement_score,
                    "power_growth_contribution": eval.power_growth_contribution,
                    "action_effectiveness": eval.action_effectiveness,
                    "leadership_alignment": eval.leadership_alignment,
                    "overall_assessment": eval.overall_assessment,
                    "specific_achievements": eval.specific_achievements,
                    "challenges": eval.challenges,
                }
                for eval, agent_name in rows
            ]

    async def get_agent_relations(
        self,
        project_id: int,
        round_num: Optional[int] = None
    ) -> dict:
        """
        获取智能体关系图谱数据

        获取指定项目（和轮次）的智能体追随关系数据，用于前端渲染关系图谱。

        Args:
            project_id: 项目ID
            round_num: 可选，指定轮次。如果为None，获取最新轮次的关系

        Returns:
            dict: 包含 nodes（节点）和 links（边）的数据
        """
        async for session in db_config.get_session():
            # 确定目标轮次
            target_round = round_num
            if target_round is None:
                # 获取最新轮次
                round_result = await session.execute(
                    select(SimulationRound).where(
                        SimulationRound.project_id == project_id
                    ).order_by(SimulationRound.round_num.desc()).limit(1)
                )
                latest_round = round_result.scalar_one_or_none()
                if not latest_round:
                    return {"nodes": [], "links": [], "round_num": 0}
                target_round = latest_round.round_num

            # 获取指定轮次的数据
            round_result = await session.execute(
                select(SimulationRound).where(
                    SimulationRound.project_id == project_id,
                    SimulationRound.round_num == target_round
                )
            )
            round_data = round_result.scalar_one_or_none()
            if not round_data:
                return {"nodes": [], "links": [], "round_num": target_round}

            # 获取该轮次的所有智能体（节点）
            agents_result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = agents_result.scalars().all()

            # 获取追随关系（边）
            relations_result = await session.execute(
                select(FollowerRelation).where(
                    FollowerRelation.round_id == round_data.round_id
                )
            )
            relations = relations_result.scalars().all()

            # 构建节点数据
            nodes = []
            for agent in agents:
                nodes.append({
                    "id": agent.agent_id,
                    "name": agent.agent_name,
                    "category": agent.leader_type or "无",
                    "symbolSize": 20,
                    "value": agent.initial_total_power
                })

            # 构建边数据（过滤掉 leader_agent_id 为 None 的关系）
            links = []
            for rel in relations:
                if rel.leader_agent_id is not None:
                    # 过滤掉自环（追随者就是自己），只保留真正的追随关系
                    if rel.follower_agent_id != rel.leader_agent_id:
                        links.append({
                            "source": rel.follower_agent_id,
                            "target": rel.leader_agent_id
                        })

            result = {
                "nodes": nodes,
                "links": links,
                "round_num": target_round
            }
            print(f"关系图谱数据 - 轮次 {target_round}: 节点数 {len(nodes)}, 连线数 {len(links)}")
            print(f"连线数据: {links}")
            return result


# 单例实例
statistics_service = StatisticsService()
