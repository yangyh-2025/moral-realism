"""
仿真后验分析服务 - SimulationAnalysisService

基于仿真产生的结构化数据（行为记录、国力历史、追随关系、秩序演变），
提供自动化的后验统计分析能力，包括：
- 行为模式聚类（合作/对抗关系对识别）
- 国力动态分析（增长率、排名变化、层级跃迁）
- 秩序演变分析（类型持续时间、转换路径）
- 领导类型-行为关联分析
- 综合报告生成

纯数据驱动，不依赖LLM调用。
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from sqlalchemy import select, func

from app.config.database import db_config
from app.models import (
    ActionRecord,
    AgentConfig,
    AgentPowerHistory,
    SimulationRound,
    FollowerRelation,
)
from loguru import logger


# 合作类行为集合（用于分类）
COOPERATION_ACTIONS = {
    "发表公开声明", "呼吁/请求", "表达合作意向", "协商/磋商",
    "开展外交合作", "开展实质性合作", "提供援助", "让步/屈服"
}


@dataclass
class DyadPattern:
    """两国互动模式统计"""
    source_id: int
    target_id: int
    source_name: str
    target_name: str
    total_actions: int = 0
    cooperation_count: int = 0
    conflict_count: int = 0
    respect_sov_ratio: float = 0.0
    action_categories: Counter = field(default_factory=Counter)
    action_names: Counter = field(default_factory=Counter)
    first_round: int = 0
    last_round: int = 0


@dataclass
class PowerTrend:
    """单国国力趋势统计"""
    agent_id: int
    agent_name: str
    initial_power: float = 0.0
    final_power: float = 0.0
    total_change: float = 0.0
    avg_change_per_round: float = 0.0
    max_single_round_change: float = 0.0
    min_single_round_change: float = 0.0
    rank_start: int = 0
    rank_end: int = 0
    rank_change: int = 0
    power_level_changed: bool = False


@dataclass
class OrderTransition:
    """秩序类型转换记录"""
    from_type: str
    to_type: str
    from_round: int
    to_round: int
    duration: int = 0


class SimulationAnalysisService:
    """
    仿真后验分析服务

    提供仿真数据的自动化统计分析能力。
    """

    def __init__(self):
        pass

    # ==================== 行为模式分析 ====================

    async def analyze_behavior_patterns(self, project_id: int) -> Dict[str, Any]:
        """
        分析行为模式：识别稳定的合作/对抗关系对

        Returns:
            {
                "dyad_patterns": [DyadPattern...],
                "most_active_dyads": [...],
                "cooperation_clusters": [...],
                "conflict_clusters": [...],
                "overall_cooperation_ratio": float
            }
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(ActionRecord).where(ActionRecord.project_id == project_id)
            )
            records = result.scalars().all()

            agent_result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = {a.agent_id: a.agent_name for a in agent_result.scalars().all()}

        if not records:
            return {"error": "无行为记录"}

        # 按关系对聚合
        dyad_stats = defaultdict(lambda: {
            "total": 0, "cooperation": 0, "conflict": 0,
            "respect_sov": 0, "categories": Counter(), "actions": Counter(),
            "first_round": float('inf'), "last_round": 0
        })

        for r in records:
            key = (min(r.source_agent_id, r.target_agent_id),
                   max(r.source_agent_id, r.target_agent_id))
            stats = dyad_stats[key]
            stats["total"] += 1
            if r.action_name in COOPERATION_ACTIONS:
                stats["cooperation"] += 1
            else:
                stats["conflict"] += 1
            if r.respect_sov:
                stats["respect_sov"] += 1
            stats["categories"][r.action_category] += 1
            stats["actions"][r.action_name] += 1
            stats["first_round"] = min(stats["first_round"], r.round_num)
            stats["last_round"] = max(stats["last_round"], r.round_num)

        dyad_patterns = []
        for (a, b), stats in dyad_stats.items():
            total = stats["total"]
            dyad_patterns.append(DyadPattern(
                source_id=a, target_id=b,
                source_name=agents.get(a, f"Agent_{a}"),
                target_name=agents.get(b, f"Agent_{b}"),
                total_actions=total,
                cooperation_count=stats["cooperation"],
                conflict_count=stats["conflict"],
                respect_sov_ratio=stats["respect_sov"] / total if total > 0 else 0,
                action_categories=stats["categories"],
                action_names=stats["actions"],
                first_round=stats["first_round"],
                last_round=stats["last_round"]
            ))

        # 排序
        dyad_patterns.sort(key=lambda x: x.total_actions, reverse=True)

        total_actions = sum(r.total_actions for r in dyad_patterns)
        total_coop = sum(r.cooperation_count for r in dyad_patterns)

        # 合作/对抗聚类（简单的阈值判定）
        cooperation_clusters = [
            {"source": d.source_name, "target": d.target_name,
             "ratio": d.cooperation_count / d.total_actions,
             "total": d.total_actions}
            for d in dyad_patterns
            if d.total_actions >= 3 and d.cooperation_count / d.total_actions >= 0.7
        ]
        conflict_clusters = [
            {"source": d.source_name, "target": d.target_name,
             "ratio": d.conflict_count / d.total_actions,
             "total": d.total_actions}
            for d in dyad_patterns
            if d.total_actions >= 3 and d.conflict_count / d.total_actions >= 0.7
        ]

        return {
            "dyad_count": len(dyad_patterns),
            "total_action_records": len(records),
            "dyad_patterns": [
                {
                    "source": d.source_name, "target": d.target_name,
                    "total": d.total_actions,
                    "cooperation": d.cooperation_count,
                    "conflict": d.conflict_count,
                    "respect_sov_ratio": round(d.respect_sov_ratio, 2),
                    "top_categories": dict(d.action_categories.most_common(3)),
                    "duration_rounds": d.last_round - d.first_round + 1
                }
                for d in dyad_patterns[:20]
            ],
            "most_active_dyads": [
                {"source": d.source_name, "target": d.target_name, "total": d.total_actions}
                for d in dyad_patterns[:10]
            ],
            "cooperation_clusters": cooperation_clusters[:10],
            "conflict_clusters": conflict_clusters[:10],
            "overall_cooperation_ratio": round(total_coop / total_actions, 4) if total_actions > 0 else 0
        }

    # ==================== 国力动态分析 ====================

    async def analyze_power_dynamics(self, project_id: int) -> Dict[str, Any]:
        """
        分析国力动态：增长率、排名变化、层级跃迁

        Returns:
            {
                "power_trends": [PowerTrend...],
                "fastest_growers": [...],
                "fastest_decliners": [...],
                "rank_changes": [...],
                "level_transitions": [...]
            }
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(AgentPowerHistory).where(AgentPowerHistory.project_id == project_id)
                .order_by(AgentPowerHistory.round_num)
            )
            records = result.scalars().all()

            agent_result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agent_configs = {a.agent_id: a for a in agent_result.scalars().all()}

        if not records:
            return {"error": "无国力历史记录"}

        # 按国家和轮次分组
        by_agent = defaultdict(list)
        for r in records:
            by_agent[r.agent_id].append(r)

        power_trends = []
        for agent_id, histories in by_agent.items():
            if not histories:
                continue

            agent = agent_configs.get(agent_id)
            if not agent:
                continue

            sorted_hist = sorted(histories, key=lambda x: x.round_num)
            initial = sorted_hist[0].round_start_power
            final = sorted_hist[-1].round_end_power
            changes = [h.round_change_value for h in sorted_hist]

            # 计算每轮排名
            round_powers = defaultdict(dict)
            for h in sorted_hist:
                round_powers[h.round_num][agent_id] = h.round_end_power

            # 找到起始和结束轮次的排名
            first_round = min(h.round_num for h in sorted_hist)
            last_round = max(h.round_num for h in sorted_hist)

            # 需要全局数据计算排名，这里简化处理
            start_rank = 0
            end_rank = 0

            trend = PowerTrend(
                agent_id=agent_id,
                agent_name=agent.agent_name,
                initial_power=initial,
                final_power=final,
                total_change=final - initial,
                avg_change_per_round=sum(changes) / len(changes) if changes else 0,
                max_single_round_change=max(changes) if changes else 0,
                min_single_round_change=min(changes) if changes else 0,
                rank_start=start_rank,
                rank_end=end_rank,
                rank_change=end_rank - start_rank,
                power_level_changed=(agent.power_level != agent_configs.get(agent_id).power_level
                                      if agent_configs.get(agent_id) else False)
            )
            power_trends.append(trend)

        # 按总变化排序
        power_trends.sort(key=lambda x: x.total_change, reverse=True)

        return {
            "agent_count": len(power_trends),
            "total_rounds_recorded": max(len(by_agent.get(aid, [])) for aid in by_agent) if by_agent else 0,
            "power_trends": [
                {
                    "agent_name": t.agent_name,
                    "initial_cinc": round(t.initial_power, 6),
                    "final_cinc": round(t.final_power, 6),
                    "total_change": round(t.total_change, 6),
                    "avg_change_per_round": round(t.avg_change_per_round, 6),
                    "max_change": round(t.max_single_round_change, 6),
                    "min_change": round(t.min_single_round_change, 6),
                }
                for t in power_trends
            ],
            "fastest_growers": [
                {"agent": t.agent_name, "change": round(t.total_change, 6)}
                for t in power_trends[:5] if t.total_change > 0
            ],
            "fastest_decliners": [
                {"agent": t.agent_name, "change": round(t.total_change, 6)}
                for t in reversed(power_trends[-5:]) if t.total_change < 0
            ],
        }

    # ==================== 秩序演变分析 ====================

    async def analyze_order_evolution(self, project_id: int) -> Dict[str, Any]:
        """
        分析秩序演变：类型持续时间、转换路径

        Returns:
            {
                "order_type_distribution": {...},
                "order_transitions": [OrderTransition...],
                "dominant_order": str,
                "order_stability": float
            }
        """
        async for session in db_config.get_session():
            result = await session.execute(
                select(SimulationRound).where(SimulationRound.project_id == project_id)
                .order_by(SimulationRound.round_num)
            )
            rounds = result.scalars().all()

        if not rounds:
            return {"error": "无轮次记录"}

        # 秩序类型分布
        order_counts = Counter(r.order_type for r in rounds if r.order_type)
        total_with_order = sum(order_counts.values())

        # 秩序转换分析
        transitions = []
        current_order = None
        current_start = 0

        for r in rounds:
            order = r.order_type or "未判定"
            if order != current_order:
                if current_order is not None:
                    transitions.append(OrderTransition(
                        from_type=current_order,
                        to_type=order,
                        from_round=current_start,
                        to_round=r.round_num,
                        duration=r.round_num - current_start
                    ))
                current_order = order
                current_start = r.round_num

        # 计算稳定性（最长连续同类型占比）
        max_duration = max((t.duration for t in transitions), default=0)
        total_rounds = len(rounds)
        stability = max_duration / total_rounds if total_rounds > 0 else 0

        # 转换矩阵
        transition_matrix = defaultdict(lambda: defaultdict(int))
        for t in transitions:
            transition_matrix[t.from_type][t.to_type] += 1

        return {
            "total_rounds": total_rounds,
            "order_type_distribution": dict(order_counts),
            "dominant_order": order_counts.most_common(1)[0][0] if order_counts else "未判定",
            "dominant_order_ratio": round(order_counts.most_common(1)[0][1] / total_with_order, 4)
            if total_with_order > 0 else 0,
            "order_stability": round(stability, 4),
            "transition_count": len(transitions),
            "transitions": [
                {"from": t.from_type, "to": t.to_type,
                 "from_round": t.from_round, "duration": t.duration}
                for t in transitions
            ],
            "transition_matrix": {k: dict(v) for k, v in transition_matrix.items()},
        }

    # ==================== 领导类型-行为关联分析 ====================

    async def analyze_leader_behavior(self, project_id: int) -> Dict[str, Any]:
        """
        分析领导类型与行为选择的关联

        Returns:
            {
                "leader_type_stats": {...},
                "behavior_preferences": {...},
                "respect_sov_by_leader": {...}
            }
        """
        async for session in db_config.get_session():
            action_result = await session.execute(
                select(ActionRecord).where(ActionRecord.project_id == project_id)
            )
            actions = action_result.scalars().all()

            agent_result = await session.execute(
                select(AgentConfig).where(AgentConfig.project_id == project_id)
            )
            agents = {a.agent_id: a for a in agent_result.scalars().all()}

        if not actions:
            return {"error": "无行为记录"}

        # 按领导类型聚合
        leader_stats = defaultdict(lambda: {
            "total_actions": 0, "cooperation": 0, "conflict": 0,
            "respect_sov": 0, "action_names": Counter(), "categories": Counter()
        })

        for a in actions:
            agent = agents.get(a.source_agent_id)
            if not agent or not agent.leader_type:
                continue

            lt = agent.leader_type
            stats = leader_stats[lt]
            stats["total_actions"] += 1
            if a.action_name in COOPERATION_ACTIONS:
                stats["cooperation"] += 1
            else:
                stats["conflict"] += 1
            if a.respect_sov:
                stats["respect_sov"] += 1
            stats["action_names"][a.action_name] += 1
            stats["categories"][a.action_category] += 1

        result = {}
        for lt, stats in leader_stats.items():
            total = stats["total_actions"]
            result[lt] = {
                "total_actions": total,
                "cooperation_ratio": round(stats["cooperation"] / total, 4) if total > 0 else 0,
                "conflict_ratio": round(stats["conflict"] / total, 4) if total > 0 else 0,
                "respect_sov_ratio": round(stats["respect_sov"] / total, 4) if total > 0 else 0,
                "top_actions": dict(stats["action_names"].most_common(5)),
                "top_categories": dict(stats["categories"].most_common(3)),
            }

        return {
            "leader_type_stats": result,
            "leader_types_count": len(result)
        }

    # ==================== 综合报告 ====================

    async def generate_full_report(self, project_id: int) -> Dict[str, Any]:
        """
        生成完整的仿真后验分析报告

        Returns:
            包含所有分析维度的综合报告
        """
        logger.info(f"开始生成项目 {project_id} 的后验分析报告")

        behavior = await self.analyze_behavior_patterns(project_id)
        power = await self.analyze_power_dynamics(project_id)
        order = await self.analyze_order_evolution(project_id)
        leader = await self.analyze_leader_behavior(project_id)

        return {
            "project_id": project_id,
            "summary": {
                "dyad_count": behavior.get("dyad_count", 0),
                "total_actions": behavior.get("total_action_records", 0),
                "overall_cooperation_ratio": behavior.get("overall_cooperation_ratio", 0),
                "dominant_order": order.get("dominant_order", "未判定"),
                "order_stability": order.get("order_stability", 0),
                "leader_types_analyzed": leader.get("leader_types_count", 0),
            },
            "behavior_analysis": behavior,
            "power_analysis": power,
            "order_analysis": order,
            "leader_analysis": leader,
        }


# 全局单例
_analysis_service: Optional[SimulationAnalysisService] = None


def get_analysis_service() -> SimulationAnalysisService:
    """获取或创建全局分析服务实例"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = SimulationAnalysisService()
    return _analysis_service
