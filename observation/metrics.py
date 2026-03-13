"""
指标测量模块 - 对应技术方案3.5节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class MetricType(str, Enum):
    """指标类型"""
    INDEPENDENT = "independent"      # 自变量
    INTERMEDIARY = "intermediary"    # 中介变量
    ENVIRONMENT = "environment"      # 体系环境指标
    DEPENDENT = "dependent"          # 因变量


@dataclass
class Metric:
    """指标数据类"""
    metric_type: MetricType
    name: str
    value: float
    unit: str = ""
    metadata: Optional[Dict] = None


class MetricsCalculator:
    """
    指标计算器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    @staticmethod
    def calculate_independent_metrics(
        agent_states: List[Dict]
    ) -> List[Metric]:
        """计算自变量指标"""
        metrics = []
        for agent in agent_states:
            agent_id = agent.get("agent_id", "")
            power_metrics = agent.get("power_metrics", {})

            # 综合实力指数
            metrics.append(Metric(
                metric_type=MetricType.INDEPENDENT,
                name=f"{agent_id}_comprehensive_power",
                value=agent.get("comprehensive_power", 0),
                unit="分"
            ))
        return metrics

    @staticmethod
    def calculate_intermediary_metrics(
        interactions: List[Dict]
    ) -> List[Metric]:
        """计算中介变量指标"""
        metrics = []
        if not interactions:
            return metrics

        # 战略行为特征指数
        total_interactions = len(interactions)
        multilateral_cooperations = sum(
            1 for i in interactions
            if "multilateral" in i.get("interaction_type", "").lower()
        )
        unilateral_actions = sum(
            1 for i in interactions
            if "unilateral" in i.get("interaction_type", "").lower()
        )

        if total_interactions > 0:
            multilateral_preference = (
                multilateral_cooperations / total_interactions * 100
            )
            unilateral_ratio = unilateral_actions / total_interactions * 100
        else:
            multilateral_preference = 0.0
            unilateral_ratio = 0.0

        metrics.append(Metric(
            metric_type=MetricType.INTERMEDIARY,
            name="multilateral_cooperation_preference",
            value=multilateral_preference,
            unit="%"
        ))

        return metrics

    @staticmethod
    def calculate_environment_metrics(
        norms: List[Dict],
        conflicts: List[Dict],
        agent_states: Optional[List[Dict]] = None
    ) -> List[Metric]:
        """计算体系环境指标"""
        metrics = []

        # 国际规范有效性指数
        if norms:
            avg_validity = sum(n.get("validity", 0) for n in norms) / len(norms)
            avg_adherence = sum(n.get("adherence_rate", 0) for n in norms) / len(norms)
            norm_effectiveness = (avg_validity * avg_adherence) / 100
        else:
            norm_effectiveness = 0.0

        metrics.append(Metric(
            metric_type=MetricType.ENVIRONMENT,
            name="international_norm_effectiveness",
            value=norm_effectiveness,
            unit="分"
        ))

        return metrics

    @staticmethod
    def calculate_dependent_metrics(
        agent_powers: List[float],
        power_distribution: Dict[str, float],
        norm_effectiveness: float,
        conflict_level: float,
        alliance_count: int,
        institutionalization: float
    ) -> List[Metric]:
        """计算因变量指标"""
        metrics = []

        if not agent_powers:
            return metrics

        # 实力集中度指数
        total_power = sum(agent_powers)
        if total_power > 0:
            top3_power = sum(sorted(agent_powers, reverse=True)[:3])
            power_concentration = (top3_power / total_power) * 100
        else:
            power_concentration = 0.0

        metrics.append(Metric(
            metric_type=MetricType.DEPENDENT,
            name="power_concentration_index",
            value=power_concentration,
            unit="%"
        ))

        return metrics

    @staticmethod
    def calculate_all_metrics(
        agent_states: List[Dict],
        interactions: List[Dict],
        norms: List[Dict],
        conflicts: List[Dict]
    ) -> Dict[str, List[Metric]]:
        """
        计算所有指标

        Args:
            agent_states: 智能体状态列表
            interactions: 互动记录列表
            norms: 国际规范列表
            conflicts: 冲突记录列表

        Returns:
            所有指标的字典
        """
        return {
            "independent": MetricsCalculator.calculate_independent_metrics(agent_states),
            "intermediary": MetricsCalculator.calculate_intermediary_metrics(interactions),
            "environment": MetricsCalculator.calculate_environment_metrics(norms, conflicts, agent_states),
            "dependent": []  # 暂时返回空列表，待完善
        }
