"""
事件影响范围传播模型 - 评估和传播事件影响

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import math
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

from domain.events.event_generator import EventType

logger = logging.getLogger(__name__)


class PropagationModel(Enum):
    """传播模型类型"""
    DISTANCE_BASED = "distance_based"  # 基于距离的传播
    RELATIONSHIP_BASED = "relationship_based"  # 基于关系的传播
    HYBRID = "hybrid"  # 混合模型


@dataclass
class AgentInfluence:
    """智能体影响数据"""
    agent_id: str
    power_change: float  # 实力变化（正为增益，负为损失）
    relationship_changes: Dict[str, float]  # {other_agent_id: relationship_delta}
    norm_impact: float  # 对规范的冲击


@dataclass
class ImpactMetrics:
    """全局影响指标"""
    norm_validity_change: float  # 规范有效性变化
    conflict_level_change: float  # 冲突水平变化
    overall_stability_change: float  # 整体稳定性变化


@dataclass
class ImpactReport:
    """事件影响报告"""
    event_id: str
    event_name: str
    directly_affected: List[str]  # 直接受影响的智能体
    influenced_agents: List[AgentInfluence]  # 受影响的智能体详情
    global_metrics: ImpactMetrics  # 全局指标变化
    propagation_paths: List[List[str]]  # 传播路径
    heat_map_data: Dict[str, float]  # 热力图数据 {agent_id: impact_level}


class EventImpactModel:
    """
    事件影响传播模型

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        # 影响衰减参数
        self._distance_decay_factor = 0.8  # 距离衰减因子
        self._relationship_decay_factor = 0.9  # 关系衰减因子
        self._max_propagation_depth = 3  # 最大传播深度

        # 事件类型影响配置
        self._event_impact_config = {
            "natural_disaster": {
                "power_impact_factor": 0.7,  # 实力影响因子
                "relationship_impact_factor": 0.3,  # 关系影响因子
                "norm_impact_factor": 0.2,  # 规范影响因子
                "conflict_factor": 0.4,  # 冲突因子
                "propagation_speed": 0.5  # 传播速度
            },
            "economic_crisis": {
                "power_impact_factor": 0.8,
                "relationship_impact_factor": 0.5,
                "norm_impact_factor": 0.3,
                "conflict_factor": 0.6,
                "propagation_speed": 0.7
            },
            "technical_breakthrough": {
                "power_impact_factor": 0.4,
                "relationship_impact_factor": 0.2,
                "norm_impact_factor": 0.1,
                "conflict_factor": 0.1,
                "propagation_speed": 0.3
            },
            "diplomatic_event": {
                "power_impact_factor": 0.2,
                "relationship_impact_factor": 0.9,
                "norm_impact_factor": 0.5,
                "conflict_factor": 0.3,
                "propagation_speed": 0.6
            },
            "regional_conflict": {
                "power_impact_factor": 0.6,
                "relationship_impact_factor": 0.8,
                "norm_impact_factor": 0.7,
                "conflict_factor": 0.9,
                "propagation_speed": 0.8
            },
            "territorial_dispute": {
                "power_impact_factor": 0.4,
                "relationship_impact_factor": 0.9,
                "norm_impact_factor": 0.6,
                "conflict_factor": 0.8,
        "propagation_speed": 0.7
            },
            "ally_betrayal": {
                "power_impact_factor": 0.3,
                "relationship_impact_factor": 1.0,
                "norm_impact_factor": 0.5,
                "conflict_factor": 0.7,
                "propagation_speed": 0.9
            },
            "public_health_crisis": {
                "power_impact_factor": 0.6,
                "relationship_impact_factor": 0.4,
                "norm_impact_factor": 0.3,
                "conflict_factor": 0.3,
                "propagation_speed": 0.6
            }
        }

        # 传播历史
        self._propagation_history: List[Dict] = []

    def _get_event_config(self, event_type: str) -> Dict[str, float]:
        """获取事件类型配置"""
        return self._event_impact_config.get(
            event_type,
            self._event_impact_config["diplomatic_event"]
        )

    def _calculate_distance(
        self,
        agent1_id: str,
        agent2_id: str,
        agent_positions: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> float:
        """
        计算两智能体间的距离

        Args:
            agent1_id: 智能体1 ID
            agent2_id: 智能体2 ID
            agent_positions: 智能体位置映射 {agent_id: (x, y)}

        Returns:
            距离值
        """
        if agent_positions is None:
            # 如果没有位置信息，使用哈希生成伪距离
            hash1 = hash(agent1_id)
            hash2 = hash(agent2_id)
            return abs(hash1 - hash2) % 100 / 10.0

        pos1 = agent_positions.get(agent1_id, (0, 0))
        pos2 = agent_positions.get(agent2_id, (0, 0))

        return math.sqrt(
            (pos1[0] - pos2[0]) ** 2 +
            (pos1[1] - pos2[1]) ** 2
        )

    def _get_relationship_strength(
        self,
        agent1_id: str,
        agent2_id: str,
        relationships: Optional[Dict[str, Dict[str, float]]] = None
    ) -> float:
        """
        获取两关系强度

        Args:
            agent1_id: 智能体1 ID
            agent2_id: 智能体2 ID
            relationships: 关系矩阵 {agent_id: {other_agent_id: strength}}

        Returns:
            关系强度 (-1到1)
        """
        if relationships is None:
            return 0.0

        if agent1_id in relationships and agent2_id in relationships[agent1_id]:
            return relationships[agent1_id][agent2_id]

        return 0.0

    def _identify_affected_agents(
        self,
        event,
        all_agent_ids: List[str],
        agent_power_levels: Optional[Dict[str, float]] = None
    ) -> List[str]:
        """
        识别受影响的智能体

        Args:
            event: 事件对象
            all_agent_ids: 所有智能体ID
            agent_power_levels: 智能体实力级别 {agent_id: power_level}

        Returns:
            受影响智能体ID列表
        """
        # 直接参与者
        directly_affected = event.participants if hasattr(event, 'participants') else []

        if not directly_affected:
            return []

        # 根据事件类型和影响级别扩展影响范围
        impact_level = event.impact_level if hasattr(event, 'impact_level') else 0.5
        event_type = event.event_type if hasattr(event, 'event_type') else "diplomatic_event"

        config = self._get_event_config(event_type)
        propagation_speed = config["propagation_speed"]

        # 确定传播深度
        propagation_depth = int(impact_level * propagation_speed * self._max_propagation_depth) + 1

        affected = set(directly_affected)

        # 简单扩展：选择实力相近的国家
        if agent_power_levels and propagation_depth > 1:
            for agent_id in directly_affected:
                power_level = agent_power_levels.get(agent_id, 50)
                for other_id in all_agent_ids:
                    if other_id not in affected:
                        other_power = agent_power_levels.get(other_id, 50)
                        if abs(power_level - other_power) < 30:  # 实力相近
                            affected.add(other_id)

        return list(affected)

    def _calculate_power_impact(
        self,
        agent_id: str,
        event,
        config: Dict[str, float],
        distance: float = 0.0,
        is_direct: bool = True
    ) -> float:
        """
        计算实力影响

        Args:
            agent_id: 智能体ID
            event: 事件对象
            config: 事件配置
            distance: 到事件中心的距离
            is_direct: 是否直接受影响

        Returns:
            实力变化值（负为损失）
        """
        impact_level = event.impact_level if hasattr(event, 'impact_level') else 0.5
        base_impact = config["power_impact_factor"] * impact_level

        # 距离衰减
        if not is_direct:
            distance_factor = self._distance_decay_factor ** distance
            base_impact *= distance_factor

        # 根据事件类型确定影响方向
        event_type = event.event_type if hasattr(event, 'event_type') else "diplomatic_event"

        # 技术突破是正向影响，其他通常是负向影响
        if event_type == "technical_breakthrough":
            return base_impact  # 正向影响

        return -base_impact  # 负向影响

    def _calculate_relationship_impact(
        self,
        agent_id: str,
        other_id: str,
        event,
        config: Dict[str, float],
        existing_relationship: float = 0.0
    ) -> float:
        """
        计算关系影响

        Args:
            agent_id: 智能体ID
            other_id: 其他智能体ID
            event: 事件对象
            config: 事件配置
            existing_relationship: 现有关系强度

        Returns:
            关系变化值
        """
        impact_level = event.impact_level if hasattr(event, 'impact_level') else 0.5
        base_impact = config["relationship_impact_factor"] * impact_level

        # 根据事件类型确定影响方向
        event_type = event.event_type if hasattr(event, 'event_type') else "diplomatic_event"

        # 冲突类事件降低关系
        if event_type in ["regional_conflict", "territorial_dispute", "ally_betrayal"]:
            return -base_impact

        # 技术突破可能改善关系
        if event_type == "technical_breakthrough":
            return base_impact * 0.5

        return 0.0

    def _calculate_global_metrics(
        self,
        event,
        influenced_agents: List[AgentInfluence],
        config: Dict[str, float]
    ) -> ImpactMetrics:
        """
        计算全局影响指标

        Args:
            event: 事件对象
            influenced_agents: 受影响智能体列表
            config: 事件配置

        Returns:
            全局影响指标
        """
        impact_level = event.impact_level if hasattr(event, 'impact_level') else 0.5

        # 规范有效性变化
        norm_impact = -config["norm_impact_factor"] * impact_level

        # 冲突水平变化
        conflict_impact = config["conflict_factor"] * impact_level

        # 整体稳定性变化（规范和冲突的综合）
        stability_impact = - (norm_impact * 0.5 + conflict_impact * 0.5)

        return ImpactMetrics(
            norm_validity_change=norm_impact,
            conflict_level_change=conflict_impact,
            overall_stability_change=stability_impact
        )

    def _propagate_influence(
        self,
        event,
        affected_agents: List[str],
        all_agent_ids: List[str],
        relationships: Optional[Dict[str, Dict[str, float]]] = None,
        model: PropagationModel = PropagationModel.HYBRID
    ) -> Tuple[List[List[str]], Dict[str, float]]:
        """
        传播影响

        Args:
            event: 事件对象
            affected_agents: 直接受影响的智能体
            all_agent_ids: 所有智能体ID
            relationships: 关系矩阵
            model: 传播模型

        Returns:
            (传播路径列表, 热力图数据)
        """
        propagation_paths = []
        heat_map_data = {agent_id: 0.0 for agent_id in all_agent_ids}

        # 初始化热力图：直接影响为1.0
        for agent_id in affected_agents:
            heat_map_data[agent_id] = 1.0

        # 传播路径
        for agent_id in affected_agents:
            propagation_paths.append([agent_id])

        # 基于关系的传播
        if model in [PropagationModel.RELATIONSHIP_BASED, PropagationModel.HYBRID]:
            for source_id in affected_agents:
                if relationships and source_id in relationships:
                    for target_id, strength in relationships[source_id].items():
                        if target_id in all_agent_ids and target_id not in affected_agents:
                            # 关系强度决定传播程度
                            if abs(strength) > 0.5:
                                heat_map_data[target_id] = max(
                                    heat_map_data[target_id],
                                    abs(strength) * self._relationship_decay_factor
                                )
                                propagation_paths.append([source_id, target_id])

        return propagation_paths, heat_map_data

    def calculate_impact(
        self,
        event,
        all_agent_ids: List[str],
        agent_positions: Optional[Dict[str, Tuple[float, float]]] = None,
        relationships: Optional[Dict[str, Dict[str, float]]] = None,
        agent_power_levels: Optional[Dict[str, float]] = None,
        propagation_model: PropagationModel = PropagationModel.HYBRID
    ) -> ImpactReport:
        """
        计算事件影响

        Args:
            event: 事件对象
            all_agent_ids: 所有智能体ID列表
            agent_positions: 智能体位置映射（可选）
            relationships: 关系矩阵（可选）
            agent_power_levels: 智能体实力级别（可选）
            propagation_model: 传播模型

        Returns:
            事件影响报告
        """
        # 获取事件配置
        event_type = event.event_type if hasattr(event, 'event_type') else "diplomatic_event"
        config = self._get_event_config(event_type)

        # 识别受影响智能体
        directly_affected = self._identify_affected_agents(
            event,
            all_agent_ids,
            agent_power_levels
        )

        if not directly_affected:
            return ImpactReport(
                event_id=event.event_id if hasattr(event, 'event_id') else "unknown",
                event_name=event.name if hasattr(event, 'name') else "Unknown Event",
                directly_affected=[],
                influenced_agents=[],
                global_metrics=ImpactMetrics(0, 0, 0),
                propagation_paths=[],
                heat_map_data={}
            )

        # 计算每个受影响智能体的具体影响
        influenced_agents = []

        for agent_id in directly_affected:
            # 计算到事件中心的距离
            distance = 0.0
            if agent_positions:
                center_agent = directly_affected[0] if directly_affected else agent_id
                distance = self._calculate_distance(agent_id, center_agent, agent_positions)

            # 计算实力影响
            power_change = self._calculate_power_impact(
                agent_id,
                event,
                config,
                distance,
                is_direct=(agent_id in directly_affected)
            )

            # 计算关系影响
            relationship_changes = {}
            for other_id in all_agent_ids:
                if other_id != agent_id:
                    existing_rel = self._get_relationship_strength(agent_id, other_id, relationships)
                    rel_change = self._calculate_relationship_impact(
                        agent_id,
                        other_id,
                        event,
                        config,
                        existing_rel
                    )
                    if abs(rel_change) > 0.01:
                        relationship_changes[other_id] = rel_change

            # 计算规范冲击
            norm_impact = -config["norm_impact_factor"] * abs(power_change)

            influenced_agents.append(AgentInfluence(
                agent_id=agent_id,
                power_change=power_change,
                relationship_changes=relationship_changes,
                norm_impact=norm_impact
            ))

        # 计算全局指标
        global_metrics = self._calculate_global_metrics(event, influenced_agents, config)

        # 传播影响
        propagation_paths, heat_map_data = self._propagate_influence(
            event,
            directly_affected,
            all_agent_ids,
            relationships,
            propagation_model
        )

        # 创建影响报告
        report = ImpactReport(
            event_id=event.event_id if hasattr(event, 'event_id') else "unknown",
            event_name=event.name if hasattr(event, 'name') else "Unknown Event",
            directly_affected=directly_affected,
            influenced_agents=influenced_agents,
            global_metrics=global_metrics,
            propagation_paths=propagation_paths,
            heat_map_data=heat_map_data
        )

        # 记录历史
        self._propagation_history.append({
            "round": getattr(event.metadata, 'round', 0) if hasattr(event, 'metadata') else 0,
            "event_id": report.event_id,
            "directly_affected": directly_affected,
            "impact_count": len(influenced_agents)
        })

        return report

    def generate_heatmap_data(
        self,
        report: ImpactReport
    ) -> Dict[str, Any]:
        """
        生成热力图数据（用于可视化）

        Args:
            report: 影响报告

        Returns:
            热力图数据字典
        """
        return {
            "event_id": report.event_id,
            "event_name": report.event_name,
            "heat_map": report.heat_map_data,
            "propagation_paths": report.propagation_paths,
            "global_impact": {
                "norm_validity_change": report.global_metrics.norm_validity_change,
                "conflict_level_change": report.global_metrics.conflict_level_change,
                "overall_stability_change": report.global_metrics.overall_stability_change
            }
        }

    def analyze_historical_impact(
        self,
        limit: int = 10
    ) -> List[Dict]:
        """
        分析历史影响数据

        Args:
            limit: 返回最近的记录数

        Returns:
            历史影响数据列表
        """
        return self._propagation_history[-limit:]

    def get_impact_summary(self, report: ImpactReport) -> str:
        """
        生成影响摘要

        Args:
            report: 影响报告

        Returns:
            影响摘要字符串
        """
        summary_lines = [
            f"事件: {report.event_name}",
            f"直接影响智能体: {len(report.directly_affected)}个",
            f"传播路径数: {len(report.propagation_paths)}条",
            f"规范有效性变化: {report.global_metrics.norm_validity_change:.2f}",
            f"冲突水平变化: {report.global_metrics.conflict_level_change:.2f}",
            f"整体稳定性变化: {report.global_metrics.overall_stability_change:.2f}",
            "",
            "详细影响:"
        ]

        for influence in report.influenced_agents:
            summary_lines.append(
                f"  - {influence.agent_id}: "
                f"实力{'+' if influence.power_change > 0 else ''}{influence.power_change:.2f}, "
                f"规范冲击{influence.norm_impact:.2f}"
            )

        return "\n".join(summary_lines)

    def clear_history(self):
        """清空传播历史"""
        self._propagation_history.clear()
