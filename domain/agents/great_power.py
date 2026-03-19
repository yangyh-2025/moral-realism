"""
大国智能体

对应 PowerTier.GREAT_POWER (1.5 < z ≤ 2.0, 约4.41%)
必须配置：leader_type（王道型/霸权型/强权型/昏庸型）

特点：
- 区域主导地位和全球影响力
- 维护区域主导地位
- 在全球事务中发声
- 防范区域挑战者
- 在超级大国间保持自主

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

from domain.agents.base_agent import BaseAgent
from config.leader_types import LeaderType


class RegionalGlobalAssessment:
    """
    区域与全球局势评估

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        regional_power_structure: Dict[str, float],
        regional_stability: float,
        global_opportunity_level: float,
        great_power_competition: float,
        recommended_strategy: str
    ):
        self.regional_power_structure = regional_power_structure
        self.regional_stability = regional_stability
        self.global_opportunity_level = global_opportunity_level
        self.great_power_competition = great_power_competition
        self.recommended_strategy = recommended_strategy

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "regional_power_structure": self.regional_power_structure,
            "regional_stability": self.regional_stability,
            "global_opportunity_level": self.global_opportunity_level,
            "great_power_competition": self.great_power_competition,
            "recommended_strategy": self.recommended_strategy
        }


class RegionalLeadershipDecision:
    """
    区域领导决策

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        action_type: str,
        priority: int,
        target_region: str,
        parameters: Dict,
        reasoning: str
    ):
        self.action_type = action_type
        self.priority = priority
        self.target_region = target_region
        self.parameters = parameters
        self.reasoning = reasoning

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "action_type": self.action_type,
            "priority": self.priority,
            "target_region": self.target_region,
            "parameters": self.parameters,
            "reasoning": self.reasoning
        }


class GlobalEngagementDecision:
    """
    全球参与决策

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        action_type: str,
        priority: int,
        target_organizations: List[str],
        parameters: Dict,
        reasoning: str
    ):
        self.action_type = action_type
        self.priority = priority
        self.target_organizations = target_organizations
        self.parameters = parameters
        self.reasoning = reasoning

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "action_type": self.action_type,
            "priority": self.priority,
            "target_organizations": self.target_organizations,
            "parameters": self.parameters,
            "reasoning": self.reasoning
        }


class RegionalLeadershipStrategy:
    """
    区域领导策略模块 - 大国专用

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化区域领导策略

        Args:
            agent: 大国智能体实例
        """
        self.agent = agent
        self._decisions = []

    def assess_regional_global_situation(self, global_data: Dict) -> RegionalGlobalAssessment:
        """
        评估区域与全球局势

        Args:
            global_data: 全球数据

        Returns:
            区域与全球局势评估
        """
        # 评估区域权力结构
        regional_power_structure = self._assess_regional_power_structure(global_data)

        # 评估区域稳定性
        regional_stability = self._assess_regional_stability(global_data)

        # 评估全球参与机会
        global_opportunity_level = self._assess_global_opportunities(global_data)

        # 评估与其他大国的竞争压力
        great_power_competition = self._assess_great_power_competition(global_data)

        # 推荐策略
        recommended_strategy = self._recommend_strategy(
            regional_stability,
            global_opportunity_level,
            great_power_competition
        )

        return RegionalGlobalAssessment(
            regional_power_structure=regional_power_structure,
            regional_stability=regional_stability,
            global_opportunity_level=global_opportunity_level,
            great_power_competition=great_power_competition,
            recommended_strategy=recommended_strategy
        )

    def _assess_regional_power_structure(self, global_data: Dict) -> Dict[str, float]:
        """评估区域权力结构"""
        agents = global_data.get("agents", [])
        region_agents = [
            a for a in agents
            if a.get("region") == self.agent.state.region
        ]

        if not region_agents:
            return {}

        total_power = sum(a.get("power", 0) for a in region_agents)
        if total_power == 0:
            return {}

        return {
            a["agent_id"]: a.get("power", 0) / total_power
            for a in region_agents
        }

    def _assess_regional_stability(self, global_data: Dict) -> float:
        """评估区域稳定性"""
        conflicts = global_data.get("conflicts", [])
        regional_conflicts = [
            c for c in conflicts
            if c.get("region") == self.agent.state.region
        ]

        conflict_severity = sum(c.get("severity", 0) for c in regional_conflicts)
        stability = max(0.0, 1.0 - conflict_severity / 5.0)

        return stability

    def _assess_global_opportunities(self, global_data: Dict) -> float:
        """评估全球参与机会"""
        opportunities = global_data.get("opportunities", [])
        my_opportunities = [
            o for o in opportunities
            if o.get("target") == self.agent.state.agent_id or
               o.get("type") == "global_cooperation"
        ]

        if not my_opportunities:
            return 0.3  # 基础参与机会

        return max(0.3, min(1.0, sum(o.get("benefit", 0) for o in my_opportunities) / len(my_opportunities)))

    def _assess_great_power_competition(self, global_data: Dict) -> float:
        """评估与其他大国的竞争压力"""
        agents = global_data.get("agents", [])
        other_great_powers = [
            a for a in agents
            if a.get("power_tier") in ["great_power", "superpower"] and
               a.get("agent_id") != self.agent.state.agent_id
        ]

        if not other_great_powers:
            return 0.0

        # 计算竞争压力
        my_power = self.agent.state.power_metrics.calculate_comprehensive_power()
        avg_competitor_power = sum(a.get("power", 0) for a in other_great_powers) / len(other_great_powers)

        competition = max(0.0, min(1.0, avg_competitor_power / (my_power + 0.01)))
        return competition

    def _recommend_strategy(
        self,
        regional_stability: float,
        global_opportunity_level: float,
        great_power_competition: float
    ) -> str:
        """推荐策略"""
        leader_type = self.agent.state.leader_type

        if leader_type == LeaderType.WANGDAO:
            if regional_stability < 0.5:
                return "regional_stabilization"
            elif global_opportunity_level > 0.7:
                return "global_cooperation"
            else:
                return "balanced_development"

        elif leader_type == LeaderType.BAQUAN:
            if great_power_competition > 0.6:
                return "regional_consolidation"
            elif global_opportunity_level > 0.6:
                return "global_influence_expansion"
            else:
                return "alliance_building"

        elif leader_type == LeaderType.QIANGQUAN:
            if regional_stability < 0.5:
                return "regional_dominance"
            elif great_power_competition > 0.5:
                return "power_assertion"
            else:
                return "selective_engagement"

        else:  # HUNYONG
            import random
            strategies = [
                "regional_stabilization",
                "global_cooperation",
                "regional_dominance",
                "random_action"
            ]
            return random.choice(strategies)

    def formulate_regional_leadership_strategy(
        self,
        assessment: RegionalGlobalAssessment
    ) -> RegionalLeadershipDecision:
        """
        制定区域领导策略

        Args:
            assessment: 局势评估

        Returns:
            区域领导决策
        """
        strategy = assessment.recommended_strategy

        if strategy == "regional_stabilization":
            return RegionalLeadershipDecision(
                action_type="mediate_regional_conflicts",
                priority=5,
                target_region=self.agent.state.region,
                parameters={
                    "method": "multilateral_dialogue",
                    "intensity": 0.7
                },
                reasoning=f"区域稳定性较低({assessment.regional_stability:.2f})，通过调解维护区域秩序"
            )

        elif strategy == "regional_consolidation":
            return RegionalLeadershipDecision(
                action_type="strengthen_regional_alliance",
                priority=5,
                target_region=self.agent.state.region,
                parameters={
                    "method": "economic_integration",
                    "security_cooperation": True
                },
                reasoning=f"面临大国竞争压力({assessment.great_power_competition:.2f})，巩固区域影响力"
            )

        elif strategy == "regional_dominance":
            return RegionalLeadershipDecision(
                action_type="assert_regional_leadership",
                priority=4,
                target_region=self.agent.state.region,
                parameters={
                    "method": "military_posture",
                    "economic_leverage": True
                },
                reasoning="展示区域领导地位，巩固区域影响力"
            )

        elif strategy == "global_cooperation":
            return RegionalLeadershipDecision(
                action_type="promote_multilateral_cooperation",
                priority=4,
                target_region=self.agent.state.region,
                parameters={
                    "focus": "economic_development",
                    "investment_level": 0.6
                },
                reasoning=f"全球合作机会良好({assessment.global_opportunity_level:.2f})，积极参与多边合作"
            )

        else:
            return RegionalLeadershipDecision(
                action_type="maintain_regional_balance",
                priority=3,
                target_region=self.agent.state.region,
                parameters={},
                reasoning="维持区域平衡，稳步发展"
            )


class GlobalEngagementStrategy:
    """
    全球参与策略模块 - 大国专用

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化全球参与策略

        Args:
            agent: 大国智能体实例
        """
        self.agent = agent

    def formulate_global_engagement(
        self,
        global_data: Dict,
        assessment: RegionalGlobalAssessment
    ) -> GlobalEngagementDecision:
        """
        制定全球参与策略

        Args:
            global_data: 全球数据
            assessment: 局势评估

        Returns:
            全球参与决策
        """
        leader_type = self.agent.state.leader_type

        if leader_type == LeaderType.WANGDAO:
            return GlobalEngagementDecision(
                action_type="constructive_global_participation",
                priority=4,
                target_organizations=["UN", "WTO"],
                parameters={
                    "focus": "global_governance",
                    "contribution_level": 0.7
                },
                reasoning="以建设性方式参与全球治理，提供公共产品"
            )

        elif leader_type == LeaderType.BAQUAN:
            return GlobalEngagementDecision(
                action_type="selective_global_leadership",
                priority=4,
                target_organizations=["key_alliances"],
                parameters={
                    "focus": "influence_expansion",
                    "resource_commitment": 0.6
                },
                reasoning="选择性参与全球事务，优先扩大自身影响力"
            )

        elif leader_type == LeaderType.QIANGQUAN:
            return GlobalEngagementDecision(
                action_type="assertive_global_position",
                priority=3,
                target_organizations=["strategic_forums"],
                parameters={
                    "focus": "power_display",
                    "confrontation_level": 0.5
                },
                reasoning="强硬表态，展示全球存在感"
            )

        else:  # HUNYONG
            import random
            actions = [
                "constructive_global_participation",
                "selective_global_leadership",
                "variable_engagement"
            ]
            return GlobalEngagementDecision(
                action_type=random.choice(actions),
                priority=2,
                target_organizations=[],
                parameters={},
                reasoning="根据具体情况调整全球参与"
            )


class RegionalAllianceManager:
    """
    区域联盟管理模块 - 大国专用

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, region: str, agent: Any):
        """
        初始化区域联盟管理

        Args:
            region: 区域名称
            agent: 大国智能体实例
        """
        self.region = region
        self.agent = agent

    def build_regional_alliance(self, target_id: str, alliance_type: str = "economic") -> Dict:
        """
        建立区域联盟

        Args:
            target_id: 目标国家ID
            alliance_type: 联盟类型

        Returns:
            联盟信息
        """
        leader_type = self.agent.state.leader_type

        if alliance_type == "economic":
            terms = {
                "type": "economic_integration",
                "trade_preferences": True,
                "investment_facilitation": True,
                "development_cooperation": True,
                "duration": "long_term"
            }
        elif alliance_type == "security":
            if leader_type == LeaderType.WANGDAO:
                terms = {
                    "type": "collective_security",
                    "mutual_defense": True,
                    "consultation_mechanism": True,
                    "crisis_response": "coordinated"
                }
            else:
                terms = {
                    "type": "led_security_cooperation",
                    "mutual_defense": True,
                    "leadership_role": self.agent.state.agent_id,
                    "obligation_level": "moderate"
                }
        else:
            terms = {}

        return {
            "alliance_id": f"{self.region}_{alliance_type}_{target_id}",
            "leader": self.agent.state.agent_id,
            "member": target_id,
            "type": alliance_type,
            "terms": terms,
            "status": "proposed"
        }


class GreatPowerAgent(BaseAgent):
    """
    大国智能体

    适用范围：大国 (PowerTier.GREAT_POWER, 1.5 < z ≤ 2.0, 约4.41%)
    必须配置：leader_type（王道型/霸权型/强权型/昏庸型）

    特点：
    - 区域主导地位和全球影响力
    - 维护区域主导地位，在全球事务中发声
    - 防范区域挑战者
    - 在超级大国间保持自主

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        region: str,
        power_metrics: Any
    ):
        """
        初始化大国智能体

        Args:
            agent_id: 智能体唯一ID
            name: 国家名称
            region: 国家所属区域
            power_metrics: 实力指标
        """
        super().__init__(agent_id, name, region, power_metrics)

        # 策略模块将在complete_initialization中初始化
        self.regional_leadership_strategy = None
        self.global_engagement_strategy = None
        self.regional_alliance_manager = None

    def complete_initialization(self) -> None:
        """完成最终初始化"""
        super().complete_initialization()

        # 初始化策略模块
        self.regional_leadership_strategy = RegionalLeadershipStrategy(self)
        self.global_engagement_strategy = GlobalEngagementStrategy(self)
        self.regional_alliance_manager = RegionalAllianceManager(
            region=self.state.region,
            agent=self
        )

    def _get_core_preferences(self, leader_type: Optional[LeaderType] = None) -> Dict[str, float]:
        """获取大国核心偏好"""
        preferences = {
            LeaderType.WANGDAO: {
                "regional_leadership": 1.0,
                "regional_stability": 0.9,
                "global_cooperation": 0.85,
                "national_long_term_interest": 0.8,
                "multilateral_engagement": 0.75,
                "national_short_term_interest": 0.6,
                "personal_interest": 0.1
            },
            LeaderType.BAQUAN: {
                "regional_leadership": 1.0,
                "global_influence": 0.9,
                "regional_dominance": 0.85,
                "alliance_system_interest": 0.8,
                "superpower_autonomy": 0.7,
                "regional_stability": 0.6,
                "personal_interest": 0.2
            },
            LeaderType.QIANGQUAN: {
                "regional_dominance": 1.0,
                "power_assertion":1.0,
                "regional_consolidation": 0.9,
                "national_core_interest": 0.85,
                "selective_global_engagement": 0.5,
                "others_interest": 0.1
            },
            LeaderType.HUNYONG: {
                "personal_interest": 1.0,
                "faction_interest": 0.9,
                "regional_opportunism": 0.8,
                "national_nominal_interest": 0.5
            }
        }
        return preferences.get(leader_type, {})

    def _get_behavior_boundaries(self, leader_type: Optional[LeaderType] = None) -> List[str]:
        """获取大国行为边界"""
        boundaries = {
            LeaderType.WANGDAO: [
                "维护区域稳定是首要任务",
                "在超级大国间保持相对自主",
                "通过多边协商解决问题",
                "促进区域合作与发展",
                "为中小国家提供发展支持"
            ],
            LeaderType.BAQUAN: [
                "维护区域主导地位是核心目标",
                "选择性使用武力/强制手段",
                "在超级大国间争取最大化自主",
                "主导区域组织和制度",
                "对区域挑战者采取制衡措施"
            ],
            LeaderType.QIANGQUAN: [
                "武力/强制手段优先",
                "强化区域主导地位",
                "对区域挑战者采取强硬立场",
                "在超级大国面前保持独立性",
                "拒绝多边协商，寻求单边优势"
            ],
            LeaderType.HUNYONG: [
                "区域政策高度个人化",
                "言行严重不一致",
                "频繁调整区域立场",
                "可能采取不利于区域稳定的行为",
                "政策缺乏连贯性和战略"
            ]
        }
        return boundaries.get(leader_type, [])
