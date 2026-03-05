"""
道义现实主义ABM系统的体系互动层模块

本模块实现SystemicInteractionManager类，用于处理：
- 国际秩序塑造
- 规范演化与扩散
- 价值观竞争
- 制度改革

核心概念：
- 系统级互动：涉及整个国际体系的互动
- 国际规范：体系中的行为准则和价值观
- 体系事件：影响整个体系的重要事件
- 秩序类型：多极、两极、单极霸权、等级秩序
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType


logger = logging.getLogger(__name__)


class OrderType(Enum):
    """国际秩序类型枚举"""

    MULTIPOLAR = "multipolar"  # 多极秩序
    BIPOLAR = "bipolar"  # 两极秩序
    UNIPOLAR_HEGEMONIC = = "unipolar_hegemonic"  # 单极霸权秩序
    HIERARCHICAL = "hierarchical"  # 等级秩序


@dataclass
class Norm:
    """表示国际规范"""

    norm_id: str  # 规范唯一标识符
    name: str  # 规范名称
    description: str  # 规范描述
    category: str  # 规范类别（安全、经济、人权等）
    strength: float  # 规范强度（0-1）
    originator: Optional[str] = None  # 发起该规范的大国代理ID
    adoption_level: float = 0.0  # 国际采纳程度（0-1）
    date_created: datetime = field(default_factory=datetime.now)  # 创建日期
    date_modified: Optional[datetime] = None  # 修改日期

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "norm_id": self.norm_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "strength": self.strength,
            "originator": self.originator,
            "adoption_level": self.adoption_level,
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat() if self.date_modified else None,
        }


@dataclass
class SystemicEvent:
    """表示体系级事件"""

    event_id: str  # 事件唯一标识符
    event_type: str  # 事件类型
    description: str  # 事件描述
    participants: List[str]  # 参与者列表
    impact_level: float  # 体系影响程度（0-1）
    timestamp: datetime = field(default_factory=datetime.now)  # 时间戳
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "description": self.description,
            "participants": self.participants,
            "impact_level": self.impact_level,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class SystemicInteractionManager:
    """
    体系互动管理器类

    管理ABM模拟中的体系级互动。

    主要功能：
    - 国际秩序塑造
    - 规范演化与扩散
    - 价值观竞争
    - 制度改革
    """

    def __init__(
        self,
        enable_logging: bool = True,
    ) -> None:
        """
        初始化体系互动管理器

        Args:
            enable_logging: 是否启用详细日志
        """
        self._agents: Dict[str, Agent] = {}  # 注册的代理字典
        self._norms: Dict[str, Norm] = {}  # 规范字典
        self._systemic_events: List[SystemicEvent] = []  # 体系事件列表
        self._order_history: List[Dict[str, Any]] = []  # 秩序历史记录

        self._enable_logging = enable_logging
        self._event_counter = 0  # 事件计数器

        # 初始化基础规范
        self._initialize_base_norms()

    def _initialize_base_norms(self) -> None:
        """初始化基础国际规范"""
        base_norms = [
            Norm(
                norm_id="norm_sovereignty",
                name="尊重主权",
                description="尊重国家主权和领土完整",
                category="security",
                strength=0.8,
                adoption_level=0.9,
            ),
            Norm(
                norm_id="norm_non_aggression",
                name="不侵略",
                description="除自卫外禁止使用武力",
                category="security",
                strength=0.85,
                adoption_level=0.85,
            ),
            Norm(
                norm_id="norm_self_determination",
                name="民族自决",
                description="民族自决权",
                category="human_rights",
                strength=0.75,
                adoption_level=0.8,
            ),
            Norm(
                norm_id="norm_free_trade",
                name="自由贸易",
                description="促进公平自由的贸易",
                category="economic",
                strength=0.7,
                adoption_level=0.75,
            ),
            Norm(
                norm_id="norm_human_rights",
                name="人权",
                description="普遍人权和基本自由",
                category="human_rights",
                strength=0.8,
                adoption_level=0.8,
            ),
        ]

        for norm in base_norms:
            self._norms[norm.norm_id] = norm

    def register_agent(self, agent: Agent) -> None:
        """
        向体系管理器注册代理

        Args:
            agent: 要注册的代理
        """
        self._agents[agent.agent_id] = agent
        logger.info(f"已注册代理用于体系互动: {agent.name}")

    def shape_international_order(
        self,
        round_id: int,
    ) -> Dict[str, Any]:
        """
        模拟大国对国际秩序的塑造

        领导类型影响秩序塑造：
        - 道义型(Wangdao): 推动多极、基于规则的秩序
        - 霸权型(Hegemon): 通过制度控制维持霸权秩序
        - 强权型(Qiangquan): 寻求权力集中和霸权秩序
        - 昏庸型(Hunyong): 倾向于支持现状

        Args:
            round_id: 当前模拟回合

        Returns:
            包含秩序分析和变化的字典
        """
        # 获取所有大国
        great_powers = [
            agent for agent in self._agents.values()
            if agent.agent_type == AgentType.GREAT_POWER
        ]

        if not great_powers:
            return {"order_type": "undefined", "power_distribution": {}}

        # 分析权力分布
        power_indices = {
            gp.agent_id: gp.capability.get_capability_index() if gp.capability else 50
            for gp in great_powers
        }

        # 确定秩序类型
        order_type = self._determine_order_type(great_powers, power_indices)

        # 分析秩序特征
        order_characteristics = self._analyze_order_characteristics(
            great_powers, order_type
        )

        # 记录秩序
        order_record = {
            "round": round_id,
            "order_type": order_type.value,
            "power_indices": power_indices,
            "characteristics": order_characteristics,
            "timestamp": datetime.now().isoformat(),
        }

        self._order_history.append(order_record)

        if self._enable_logging:
            logger.info(
                f"第 {round_id} 回合: 国际秩序类型 = {order_type.value}"
            )

        return order_record

    def _determine_order_type(
        self,
        great_powers: List[Agent],
        power_indices: Dict[str, float],
    ) -> OrderType:
        """
        确定当前国际秩序类型

        Args:
            great_powers: 大国代理列表
            power_indices: 权力能力指数

        Returns:
            秩序类型
        """
        if len(great_powers) < 2:
            return OrderType.UNIPOLAR_HEGEMONIC

        # 计算权力集中度
        total_power = sum(power_indices.values())
        max_power = max(power_indices.values())
        power_concentration = max_power / total_power

        # 分析领导类型
        leadership_types = [
            gp.leadership_type.value if gp.leadership_profile else "unknown"
            for gp in great_powers
        ]

        # 检查霸权
        if power_concentration > 0.5:
            return OrderType.UNIPOLAR_HEGEMONIC

        # 检查两极
        sorted_powers = sorted(power_indices.values(), reverse=True)
        if len(sorted_powers) >= 2 and sorted_powers[0] > sorted_powers[1] * 1.5:
            return OrderType.BIPOLAR

        # 检查多极（多个相对平衡的大国）
        if power_concentration < 0.4 and len(great_powers) >= 3:
            return OrderType.MULTIPOLAR

        # 默认：等级秩序
        return OrderType.HIERARCHICAL

    def _analyze_order_characteristics(
        self,
        great_powers: List[Agent],
        order_type: OrderType,
    ) -> Dict[str, Any]:
        """
        分析当前秩序的特征

        Args:
            great_powers: 大国代理列表
            order_type: 秩序类型

        Returns:
            包含秩序特征的字典
        """
        characteristics = {
            "order_type": order_type.value,
            "stability": 0.5,  # 稳定性（待计算）
            "norm_consensus": 0.5,  # 规范共识度（待计算）
            "conflict_level": 0.3,  # 冲突水平（待计算）
        }

        # 根据领导类型分布计算稳定性
        leadership_profiles = {}
        for gp in great_powers:
            if gp.leadership_profile:
                lt = gp.leadership_profile.leadership_type.value
                leadership_profiles[lt] = leadership_profiles.get(lt, 0) + 1

        total = sum(leadership_profiles.values())

        # 道义型领导增加稳定性
        wangdao_ratio = leadership_profiles.get("wangdao", 0) / total if total > 0 else 0
        hunyong_ratio = leadership_profiles.get("hunyong", 0) / total if total > 0 else 0

        characteristics["stability"] = 0.5 + wangdao_ratio * 0.3 + hunyong_ratio * 0.2

        # 计算规范共识度
        characteristics["norm_consensus"] = self._calculate_norm_consensus(leadership_profiles)

        # 计算冲突水平
        qiangquan_ratio = leadership_profiles.get("qiangquan", 0) / total if total > 0 else 0
        hegemon_ratio = leadership_profiles.get("hegemon", 0) / total if total > 0 else 0

        characteristics["conflict_level"] = qiangquan_ratio * 0.4 + hegemon_ratio * 0.2

        return characteristics

    def _calculate_norm_consensus(
        self,
        leadership_profiles: Dict[str, int],
    ) -> float:
        """
        计算规范共识水平

        Args:
            leadership_profiles: 各领导类型的数量

        Returns:
            共识水平（0-1）
        """
        total = sum(leadership_profiles.values())
        if total == 0:
            return 0.5

        # 道义型和昏庸型有助于规范共识
        wangdao = leadership_profiles.get("wangdao", 0)
        hunyong = leadership_profiles.get("hunyong", 0)

        return 0.5 + (wangdao + hunyong) / total * 0.3

    def evolve_international_norms(
        self,
        round_id: int,
    ) -> Dict[str, Any]:
        """
        模拟国际规范的演化

        处理过程：
        - 新规范提案
        - 规范强化/弱化
        - 旧规范过时
        - 规范在体系中的扩散

        Args:
            round_id: 当前模拟回合

        Returns:
            包含规范演化结果的字典
        """
        evolution_results = {
            "round": round_id,
            "new_norms": [],  # 新规范
            "strengthened_norms": [],  # 强化规范
            "weakened_norms": [],  # 弱化规范
            "obsolete_norms": [],  # 过时规范
        }

        # 从大国收集规范提案
        norm_proposals = self._collect_norm_proposals()

        # 处理每个提案
        for proposal in norm_proposals:
            result = self._process_norm_proposal(proposal, round_id)
            evolution_results["new_norms"].append(result)

        # 强化/弱化现有规范
        for norm_id, norm in list(self._norms.items()):
            change = self._evaluate_norm_change(norm, round_id)
            if change > 0:
                norm.strength = min(1.0, norm.strength + 0.05)
                evolution_results["strengthened_norms"].append(norm_id)
            elif change < 0:
                norm.strength = max(0.0, norm.strength - 0.05)
                evolution_results["weakened_norms"].append(norm_id)

        # 检查过时规范
        obsolete = self._identify_obsolete_norms()
        for norm_id in obsolete:
            norm = self._norms.pop(norm_id)
            evolution_results["obsolete_norms"].append(norm_id)

        if self._enable_logging:
            logger.info(
                f"第 {round_id} 回合: 规范演化 - "
                f"{len(evolution_results['new_norms'])} 个新规范, "
                f"{len(evolution_results['strengthened_norms'])} 个强化, "
                f"{len(evolution_results['obsolete_norms'])} 个过时"
            )

        return evolution_results

    def _collect_norm_proposals(self) -> List[Dict[str, Any]]:
        """
        从所有代理收集规范提案

        Returns:
            规范提案列表
        """
        proposals = []

        for agent in self._agents.values():
            if agent.agent_type != AgentType.GREAT_POWER:
                continue

            # 检查代理历史中的规范提案
            history = agent.get_history()
            for entry in history[-10:]:  # 最近10条记录
                if entry.event_type == "norm_proposal" or "norm" in str(entry.event_type).lower():
                    if entry.metadata:
                        proposals.append({
                            "agent_id": agent.agent_id,
                            "leadership_type": agent.leadership_type.value,
                            "proposal": entry.metadata,
                        })

        return proposals

    def _process_norm_proposal(
        self,
        proposal: Dict[str, Any],
        round_id: int,
    ) -> Dict[str, Any]:
        """
        处理规范提案

        Args:
            proposal: 规范提案
            round_id: 当前回合

        Returns:
            处理结果
        """
        agent_id = proposal.get("agent_id", "")
        leadership_type = proposal.get("leadership_type", "unknown")
        proposal_data = proposal.get("proposal", {})

        # 根据领导类型计算采纳度
        base_adoption = 0.3  # 基础采纳度

        if leadership_type == "wangdao":
            base_adoption += 0.4  # 道义型规范易于获得支持
        elif leadership_type == "hegemon":
            base_adoption += 0.3  # 霸权型规范也易于获得支持
        elif leadership_type == "hunyong":
            base_adoption += 0.1  # 昏庸型规范难以获得支持
        # 强权型规范没有额外加成

        # 创建新规范
        norm = Norm(
            norm_id=f"norm_{round_id}_{agent_id}_{len(self._norms)}",
            name=proposal_data.get("name", "未命名规范"),
            description=proposal_data.get("description", ""),
            category=proposal_data.get("category", "general"),
            strength=proposal_data.get("strength", 0.5),
            originator=agent_id,
            adoption_level=base_adoption,
        )

        self._norms[norm.norm_id] = norm

        return {
            "norm_id": norm.norm_id,
            "adoption_level": base_adoption,
            "originator": agent_id,
            "leadership_type": leadership_type,
        }

    def _evaluate_norm_change(self, norm: Norm, round_id: int) -> float:
        """
        评估规范应如何变化

        Args:
            norm: 要评估的规范
            round_id: 当前回合

        Returns:
            变化量（-1到1）
        """
        # 基础变化为零
        change = 0.0

        # 检查发起代理是否保持一致性
        if norm.originator:
            agent = self._agents.get(norm.originator)
            if agent and agent.leadership_profile:
                lt = agent.leadership_profile.leadership_type.value

                # 道义型规范随时间强化（如果维持）
                if lt == "wangdao":
                    change += 0.02
                # 霸权型规范可能强化
                elif lt == "hegemon":
                    change += 0.01
                # 其他规范可能弱化
                else:
                    change -= 0.01

        # 检查影响规范的最近事件
        recent_events = [
            e for e in self._systemic_events[-20:]
            if e.timestamp > (datetime.now().timestamp() - 86400)  # 最近一天
        ]

        norm_violations = sum(
            1 for e in recent_events
            if norm.norm_id in e.description or norm.category in e.event_type
        )

        if norm_violations > 0:
            change -= norm_violations * 0.05

        return change

    def _identify_obsolete_norms(self) -> List[str]:
        """
        识别已过时的规范

        Returns:
            过时规范ID列表
        """
        obsolete = []

        for norm_id, norm in self._norms.items():
            # 规范如果强度很低则过时
            if norm.strength < 0.2:
                obsolete.append(norm_id)
                continue

            # 检查年龄（超过50回合的规范可能过时）
            # 简化实现：主要使用强度作为主要指标

        return obsolete

    def simulate_values_competition(
        self,
        round_id: int,
    ) -> Dict[str, Any]:
        """
        模拟基于价值观的外交和竞争

        领导类型影响价值观竞争：
        - 道义型(Wangdao): 推广普世价值和人权
        - 霸权型(Hegemon): 推广自由民主价值观
        - 强权型(Qiangquan): 可能挑战普世价值
        - 昏庸型(Hunyong): 避免价值观对抗

        Args:
            round_id: 当前模拟回合

        Returns:
            包含价值观竞争结果的字典
        """
        # 获取大国
        great_powers = [
            agent for agent in self._agents.values()
            if agent.agent_type == AgentType.GREAT_POWER and agent.leadership_profile
        ]

        if not great_powers:
            return {"values_clusters": {}, "conflicts": []}

        # 识别价值观集群
        values_clusters = {
            "universal_humanist": [],  # 道义型对齐
            "liberal_democratic": [],  # 霸权型对齐
            "pragmatic_nationalist": [],  # 强权型/昏庸型对齐
        }

        for gp in great_powers:
            lt = gp.leadership_profile.leadership_type.value

            if lt == "wangdao":
                values_clusters["universal_humanist"].append(gp.agent_id)
            elif lt == "hegemon":
                values_clusters["liberal_democratic"].append(gp.agent_id)
            else:
                values_clusters["pragmatic_nationalist"].append(gp.agent_id)

        # 识别价值观冲突
        conflicts = self._identify_values_conflicts(great_powers)

        # 创建体系事件
        if conflicts:
            event = SystemicEvent(
                event_id=f"values_conflict_{round_id}",
                event_type="values_competition",
                description=f"价值观集群之间的竞争",
                participants=[gp.agent_id for gp in great_powers],
                impact_level=len(conflicts) / len(great_powers),
                metadata={
                    "conflicts": conflicts,
                    "clusters": values_clusters,
                },
            )

            self._systemic_events.append(event)

        if self._enable_logging:
            logger.info(
                f"第 {round_id} 回合: 价值观竞争 - "
                f"识别到 {len(conflicts)} 个冲突"
            )

        return {
            "round": round_id,
            "values_clusters": values_clusters,
            "conflicts": conflicts,
            "dominant_cluster": self._identify_dominant_cluster(values_clusters),
        }

    def _identify_values_conflicts(
        self,
        great_powers: List[Agent],
    ) -> List[Dict[str, Any]]:
        """
        识别大国之间的价值观冲突

        Args:
            great_powers: 大国代理列表

        Returns:
            冲突描述列表
        """
        conflicts = []

        for i, gp1 in enumerate(great_powers):
            for gp2 in great_powers[i + 1:]:
                if not gp1.leadership_profile or not gp2.leadership_profile:
                    continue

                lt1 = gp1.leadership_profile.leadership_type.value
                lt2 = gp2.leadership_profile.leadership_type.value

                # 检查不兼容的领导类型
                incompatible_pairs = [
                    ("wangdao", "qiangquan"),
                    ("qiangquan", "wangdao"),
                ]

                if (lt1, lt2) in incompatible_pairs:
                    conflicts.append({
                        "agent1": gp1.agent_id,
                        "agent2": gp2.agent_id,
                        "type": "values_incompatibility",
                        "description": f"{lt1} 与 {lt2} 价值观冲突",
                    })

        return conflicts

    def _identify_dominant_cluster(
        self,
        values_clusters: Dict[str, List[str]],
    ) -> Optional[str]:
        """
        识别主导价值观集群

        Args:
            values_clusters: 价值观集群成员资格

        Returns:
            主导集群名称或None
        """
        max_size = 0
        dominant = None

        for cluster_name, members in values_clusters.items():
            if len(members) > max_size:
                max_size = len(members)
                dominant = cluster_name

        return dominant

    def get_system_state(self) -> Dict[str, Any]:
        """
        获取当前体系状态摘要

        Returns:
            包含体系状态信息的字典
        """
        return {
            "norms": {k: v.to_dict() for k, v in self._norms.items()},
            "norm_count": len(self._norms),
            "events": [e.to_dict() for e in self._systemic_events[-10:]],
            "recent_events_count": len(self._systemic_events[-10:]),
            "order_history": self._order_history[-5:] if self._order_history else [],
        }

    def get_norm(self, norm_id: str) -> Optional[Norm]:
        """
        根据ID获取特定规范

        Args:
            norm_id: 规范ID

        Returns:
            规范对象（如果找到）
        """
        return self._norms.get(norm_id)

    def get_all_norms(self) -> List[Norm]:
        """
        获取所有当前规范

        Returns:
            所有规范列表
        """
        return list(self._norms.values())

    def get_norms_by_category(self, category: str) -> List[Norm]:
        """
        按类别获取规范

        Args:
            category: 要筛选的类别

        Returns:
            该类别中的规范列表
        """
        return [
            norm for norm in self._norms.values()
            if norm.category == category
        ]

    def get_systemic_events(
        self,
        limit: Optional[int] = None,
    ) -> List[SystemicEvent]:
        """
        获取体系事件

        Args:
            limit: 最多返回的事件数

        Returns:
            体系事件列表
        """
        if limit:
            return self._systemic_events[-limit:]
        return self._systemic_events.copy()
