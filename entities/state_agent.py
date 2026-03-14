"""
大国智能体 - 对应技术方案3.3.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from entities.base_agent import BaseAgent, DecisionPriority
from config.leader_types import LeaderType


class GlobalAssessment:
    """
    全球局势评估

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        power_balance: Dict[str, float],
        alliance_situation: Dict,
        threat_level: float,
        opportunity_level: float,
        recommended_strategy: str
    ):
        self.power_balance = power_balance
        self.alliance_situation = alliance_situation
        self.threat_level = threat_level
        self.opportunity_level = opportunity_level
        self.recommended_strategy = recommended_strategy

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "power_balance": self.power_balance,
            "alliance_situation": self.alliance_situation,
            "threat_level": self.threat_level,
            "opportunity_level": self.opportunity_level,
            "recommended_strategy": self.recommended_strategy
        }


class LeadershipDecision:
    """
    领导决策

    Git提交用户名: yangyh-2025
    Git Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        action_type: str,
        priority: int,
        target_agents: List[str],
        parameters: Dict,
        reasoning: str
    ):
        self.action_type = action_type
        self.priority = priority
        self.target_agents = target_agents
        self.parameters = parameters
        self.reasoning = reasoning

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "action_type": self.action_type,
            "priority": self.priority,
            "target_agents": self.target_agents,
            "parameters": self.parameters,
            "reasoning": self.reasoning
        }


class RegionalAssessment:
    """
    区域局势评估

    Git提交用户名: yangyhgh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        region: str,
        power_structure: Dict,
        stability_level: float,
        local_interests: List[str]
    ):
        self.region = region
        self.power_structure = power_structure
        self.stability_level = stability_level
        self.local_interests = local_interests

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "region": self.region,
            "power_structure": self.power_structure,
            "stability_level": self.stability_level,
            "local_interests": self.local_interests
        }


class RegionalPolicy:
    """
    区域政策

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        region: str,
        policy_type: str,
        actions: List[Dict],
        expected_outcome: str
    ):
        self.region = region
        self.policy_type = policy_type
        self.actions = actions
        self.expected_outcome = expected_outcome

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "region": self.region,
            "policy_type": self.policy_type,
            "actions": self.actions,
            "expected_outcome": self.expected_outcome
        }


class AllianceProposal:
    """
    联盟提议

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        proposal_id: str,
        proposer: str,
        target: str,
        alliance_type: str,
        terms: Dict,
        proposal_time: str
    ):
        self.proposal_id = proposal_id
        self.proposer = proposer
        self.target = target
        self.alliance_type = alliance_type
        self.terms = terms
        self.proposal_time = proposal_time

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "proposal_id": self.proposal_id,
            "proposer": self.proposer,
            "target": self.target,
            "alliance_type": self.alliance_type,
            "terms": self.terms,
            "proposal_time": self.proposal_time
        }


class AllianceResponse:
    """
    联盟响应

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        proposal_id: str,
        response_type: str,  # accept, reject, counter_proposal
        reasoning: str,
        counter_terms: Optional[Dict] = None
    ):
        self.proposal_id = proposal_id
        self.response_type = response_type
        self.reasoning = reasoning
        self.counter_terms = counter_terms

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "proposal_id": self.proposal_id,
            "response_type": self.response_type,
            "reasoning": self.reasoning,
            "counter_terms": self.counter_terms
        }


class GlobalLeadershipStrategy:
    """
    全球领导决策模块

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyariang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化全球领导策略

        Args:
            agent: 大国智能体实例
        """
        self.agent = agent
        self._decisions = []

    def assess_global_situation(self, global_data: Dict) -> GlobalAssessment:
        """
        评估全球局势

        Args:
            global_data: 全球数据，包含所有智能体的实力、关系等信息

        Returns:
            全球局势评估
        """
        # 计算权力平衡
        power_balance = self._calculate_power_balance(global_data)

        # 评估联盟局势
        alliance_situation = self._assess_alliance_situation(global_data)

        # 评估威胁水平
        threat_level = self._assess_threat_level(global_data, power_balance)

        # 评估机会水平
        opportunity_level = self._assess_opportunity_level(global_data, power_balance)

        # 根据领导类型推荐策略
        recommended_strategy = self._recommend_strategy(
            threat_level, opportunity_level
        )

        return GlobalAssessment(
            power_balance=power_balance,
            alliance_situation=alliance_situation,
            threat_level=threat_level,
            opportunity_level=opportunity_level,
            recommended_strategy=recommended_strategy
        )

    def _calculate_power_balance(self, global_data: Dict) -> Dict[str, float]:
        """
        计算权力平衡

        Args:
            global_data: 全球数据

        Returns:
            权力平衡字典 {agent_id: power_share}
        """
        agents = global_data.get("agents", [])
        total_power = sum(
            agent.get("power", 0) for agent in agents
        )

        if total_power == 0:
            return {}

        power_balance = {
            agent["agent_id"]: agent.get("power", 0) / total_power
            for agent in agents
        }

        return power_balance

    def _assess_alliance_situation(self, global_data: Dict) -> Dict:
        """
        评估联盟局势

        Args:
            global_data: 全球数据

        Returns:
            联盟局势评估
        """
        alliances = global_data.get("alliances", [])
        my_alliances = [
            a for a in alliances
            if self.agent.state.agent_id in [a["agent1"], a["agent2"]]
        ]

        return {
            "my_alliance_count": len(my_alliances),
            "total_alliance_count": len(alliances),
            "dominant_alliance": self._find_dominant_alliance(alliances),
            "my_position_in_alliances": self._assess_my_alliance_position(my_alliances)
        }

    def _find_dominant_alliance(self, alliances: List[Dict]) -> Optional[str]:
        """找出主导联盟"""
        if not alliances:
            return None

        from collections import Counter
        alliance_groups = {}
        for alliance in alliances:
            # 简化的联盟分组逻辑
            leader = alliance.get("leader")
            if leader:
                if leader not in alliance_groups:
                    alliance_groups[leader] = []
                alliance_groups[leader].append(alliance)

        if not alliance_groups:
            return None

        dominant = max(
            alliance_groups.keys(),
            key=lambda k: len(alliance_groups[k])
        )

        return dominant if len(alliance_groups[dominant]) > len(alliances) / 2 else None

    def _assess_my_alliance_position(self, my_alliances: List[Dict]) -> str:
        """评估我的联盟位置"""
        if not my_alliances:
            return "isolated"
        elif len(my_alliances) == 1:
            return "minor_player"
        else:
            # 检查是否是联盟领导者
            leader_count = sum(
                1 for a in my_alliances
                if a.get("leader") == self.agent.state.agent_id
            )
            if leader_count > 0:
                return "leader"
            else:
                return "member"

    def _assess_threat_level(self, global_data: Dict, power_balance: Dict) -> float:
        """
        评估威胁水平

        Args:
            global_data: 全球数据
            power_balance: 权力平衡

        Returns:
            威胁水平 (0-1)
        """
        threats = global_data.get("threats", [])
        my_threats = [
            t for t in threats
            if t.get("target") == self.agent.state.agent_id
        ]

        if not my_threats:
            return 0.0

        # 计算威胁严重程度
        max_severity = max(t.get("severity", 0) for t in my_threats)

        # 考虑敌对关系的智能体数量
        hostile_agents = [
            a for a in global_data.get("agents", [])
            if a.get("agent_id") != self.agent.state.agent_id and
               a.get("relation_level", 0) < -0.5
        ]

        hostile_power = sum(
            power_balance.get(a["agent_id"], 0) for a in hostile_agents
        )

        return max(0.0, min(1.0, max_severity * 0.7 + hostile_power * 0.3))

    def _assess_opportunity_level(self, global_data: Dict, power_balance: Dict) -> float:
        """
        评估机会水平

        Args:
            global_data: 全球数据
            power_balance: 权力平衡

        Returns:
            机会水平 (0-1)
        """
        opportunities = global_data.get("opportunities", [])
        my_opportunities = [
            o for o in opportunities
            if o.get("target") == self.agent.state.agent_id
        ]

        if not my_opportunities:
            return 0.0

        max_benefit = max(o.get("benefit", 0) for o in my_opportunities)

        return max(0.0, min(1.0, max_benefit))

    def _recommend_strategy(self, threat_level: float, opportunity_level: float) -> str:
        """
        推荐策略

        Args:
            threat_level: 威胁水平
            opportunity_level: 机会水平

        Returns:
            策略名称
        """
        leader_type = self.agent.state.leader_type

        if leader_type == LeaderType.WANGDAO:
            if threat_level > 0.7:
                return "defensive_stabilization"
            elif opportunity_level > 0.7:
                return "constructive_leadership"
            else:
                return "maintain_status_quo"

        elif leader_type == LeaderType.BAQUAN:
            if threat_level > 0.6:
                return "containment_strategy"
            elif opportunity_level > 0.6:
                return "expansionist_policy"
            else:
                return "alliance_management"

        elif leader_type == LeaderType.QIANGQUAN:
            if threat_level > 0.5:
                return "aggressive_response"
            elif opportunity_level > 0.5:
                return "power_projection"
            else:
                return "opportunistic_expansion"

        else:  # HUNYONG
            import random
            strategies = [
                "defensive_stabilization",
                "constructive_leadership",
                "containment_strategy",
                "expansionist_policy",
                "random_action"
            ]
            return random.choice(strategies)

    def formulate_leadership_strategy(self, global_assessment: GlobalAssessment) -> LeadershipDecision:
        """
        制定领导策略

        Args:
            global_assessment: 全球局势评估

        Returns:
            领导决策
        """
        strategy = global_assessment.recommended_strategy

        if strategy == "defensive_stabilization":
            return self._formulate_defensive_strategy(global_assessment)
        elif strategy == "constructive_leadership":
            return self._formulate_constructive_strategy(global_assessment)
        elif strategy == "containment_strategy":
            return self._formulate_containment_strategy(global_assessment)
        elif strategy == "expansionist_policy":
            return self._formulate_expansionist_strategy(global_assessment)
        else:
            return self._formulate_default_strategy(global_assessment)

    def _formulate_defensive_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """制定防御策略"""
        return LeadershipDecision(
            action_type="strengthen_alliances",
            priority=5,
            target_agents=[],
            parameters={
                "focus": "security",
                "investment": 0.3
            },
            reasoning=f"威胁水平较高({assessment.threat_level:.2f})，需要强化联盟和防御能力"
        )

    def _formulate_constructive_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """建设性领导策略"""
        return LeadershipDecision(
            action_type="provide_public_goods",
            priority=4,
            target_agents=[],
            parameters={
                "type": "economic_stability",
                "investment": 0.4
            },
            reasoning=f"机会水平较高({assessment.opportunity_level:.2f})，发挥建设性领导作用"
        )

    def _formulate_containment_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """遏制策略"""
        return LeadershipDecision(
            action_type="contain_rivals",
            priority=5,
            target_agents=[],
            parameters={
                "method": "alliance_encirclement",
                "intensity": 0.6
            },
            reasoning=f"威胁水平较高({assessment.threat_level:.2f})，采取遏制策略"
        )

    def _formulate_expansionist_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """扩张主义策略"""
        return LeadershipDecision(
            action_type="expand_influence",
            priority=4,
            target_agents=[],
            parameters={
                "method": "alliance_expansion",
                "intensity": 0.5
            },
            reasoning=f"机会水平较高({assessment.opportunity_level:.2f})，扩大影响力"
        )

    def _formulate_default_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """默认策略"""
        return LeadershipDecision(
            action_type="maintain_status_quo",
            priority=2,
            target_agents=[],
            parameters={},
            reasoning="维持现状，观察局势发展"
        )

    def evaluate_leadership_outcome(self, outcome: Dict) -> None:
        """
        评估领导结果

        Args:
            outcome: 执行结果
        """
        # 记录到学习机制
        if self.agent.state.learning:
            self.agent.state.learning.record_outcome(
                decision={"type": "leadership_action"},
                outcome=outcome
            )

        # 更新战略信誉度
        if outcome.get("success", False):
            self.agent.state.strategic_reputation = min(
                100.0,
                self.agent.state.strategic_reputation + 2.0
            )
        else:
            self.agent.state.strategic_reputation = max(
                0.0,
                self.agent.state.strategic_reputation - 5.0
            )


class RegionalManagementStrategy:
    """
    区域管理决策模块

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        self.agent = agent
        self._regional_policies = {}

    def assess_regional_situation(self, region: str, regional_data: Dict) -> RegionalAssessment:
        """
        评估区域局势

        Args:
            region: 区域名称
            regional_data: 区域数据

        Returns:
            区域局势评估
        """
        region_agents = [
            a for a in regional_data.get("agents", [])
            if a.get("region") == region
        ]

        # 计算区域权力结构
        power_structure = self._calculate_regional_power_structure(region_agents)

        # 评估区域稳定性
        stability_level = self._assess_regional_stability(region_agents, regional_data)

        # 识别区域利益
        local_interests = self._identify_regional_interests(region, regional_data)

        return RegionalAssessment(
            region=region,
            power_structure=power_structure,
            stability_level=stability_level,
            local_interests=local_interests
        )

    def _calculate_regional_power_structure(self, region_agents: List[Dict]) -> Dict:
        """计算区域权力结构"""
        if not region_agents:
            return {}

        total_power = sum(a.get("power", 0) for a in region_agents)
        if total_power == 0:
            return {}

        return {
            a["agent_id"]: a.get("power", 0) / total_power
            for a in region_agents
        }

    def _assess_regional_stability(self, region_agents: List[Dict], regional_data: Dict) -> float:
        """评估区域稳定性"""
        if not region_agents:
            return 1.0

        # 计算关系冲突程度
        conflicts = regional_data.get("conflicts", [])
        regional_conflicts = [
            c for c in conflicts
            if c.get("region") == self.agent.state.region
        ]

        conflict_severity = sum(c.get("severity", 0) for c in regional_conflicts)

        # 稳定性越高，冲突越低
        stability = max(0.0, 1.0 - conflict_severity / 10.0)

        return stability

    def _identify_regional_interests(self, region: str, regional_data: Dict) -> List[str]:
        """识别区域利益"""
        interests = regional_data.get("regional_interests", {})
        return interests.get(region, [])

    def formulate_regional_policy(self, region: str, assessment: RegionalAssessment) -> RegionalPolicy:
        """
        制定区域政策

        Args:
            region: 区域名称
            assessment: 区域局势评估

        Returns:
            区域政策
        """
        if assessment.stability_level < 0.5:
            policy_type = "stabilization"
            actions = [
                {"type": "mediate_conflict", "target": region},
                {"type": "promote_dialogue", "participants": list(assessment.power_structure.keys())}
            ]
            expected_outcome = "提高区域稳定性，减少冲突"
        elif assessment.stability_level < 0.8:
            policy_type = "development"
            actions = [
                {"type": "promote_cooperation", "area": "economic"},
                {"type": "regional_forums", "frequency": "regular"}
            ]
            expected_outcome = "促进区域合作与发展"
        else:
            policy_type = "maintain"
            actions = [
                {"type": "maintain_relations", "status": "stable"}
            ]
            expected_outcome = "维持区域稳定现状"

        return RegionalPolicy(
            region=region,
            policy_type=policy_type,
            actions=actions,
            expected_outcome=expected_outcome
        )

    def manage_regional_relations(self, region: str) -> List[Dict]:
        """
        管理区域关系

        Args:
            region: 区域名称

        Returns:
            关系行动列表
        """
        # 获取最近的区域政策
        policy = self._regional_policies.get(region)
        if not policy:
            return []

        return policy.actions


class AllianceManager:
    """
    联盟管理模块

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        self.agent = agent
        self._proposals = {}
        self._proposals_counter = 0

    def propose_alliance(self, target_id: str, alliance_type: str = "strategic") -> AllianceProposal:
        """
        提议建立联盟

        Args:
            target_id: 目标智能体ID
            alliance_type: 联盟类型 (strategic, economic, military, diplomatic)

        Returns:
            联盟提议
        """
        self._proposals_counter += 1
        proposal_id = f"alliance_{self.agent.state.agent_id}_{self._proposals_counter}"

        # 根据领导类型制定条款
        terms = self._formulate_alliance_terms(target_id, alliance_type)

        proposal = AllianceProposal(
            proposal_id=proposal_id,
            proposer=self.agent.state.agent_id,
            target=target_id,
            alliance_type=alliance_type,
            terms=terms,
            proposal_time=datetime.now().isoformat()
        )

        self._proposals[proposal_id] = proposal

    def _formulate_alliance_terms(self, target_id: str, alliance_type: str) -> Dict:
        """
        制定联盟条款

        Args:
            target_id: 目标智能体ID
            alliance_type: 联盟类型

        Returns:
            联盟条款
        """
        leader_type = self.agent.state.leader_type

        if alliance_type == "strategic":
            if leader_type == LeaderType.WANGDAO:
                return {
                    "mutual_defense": True,
                    "economic_cooperation": True,
                    "decision_making": "consultative",
                    "duration": "indefinite",
                    "terms": "平等互利，共同维护地区稳定"
                }
            elif leader_type == LeaderType.BAQUAN:
                return {
                    "mutual_defense": True,
                    "economic_cooperation": True,
                    "decision_making": "leader_led",  # 霸权主导
                    "duration": "indefinite",
                    "terms": "以我方为主导，共同对抗威胁"
                }
            elif leader_type == LeaderType.QIANGQUAN:
                return {
                    "mutual_defense": True,
                    "economic_cooperation": False,
                    "decision_making": "coercive",  # 强制执行
                    "duration": "contingent",
                    "terms": "服从我方领导，共同实现目标"
                }
            else:  # HUNYONG
                return {
                    "mutual_defense": True,
                    "economic_cooperation": True,
                    "decision_making": "variable",
                    "duration": "indefinite",
                    "terms": "灵活合作，具体事项协商"
                }

        elif alliance_type == "economic":
            return {
                "trade_preferences": True,
                "investment_protection": True,
                "dispute_resolution": "negotiation"
            }

        elif alliance_type == "military":
            return {
                "mutual_defense": True,
                "joint_exercises": True,
                "intelligence_sharing": True
            }

        elif alliance_type == "diplomatic":
            return {
                "coordinate_positions": True,
                "mutual_support": True,
                "joint_diplomacy": True
            }

        return {}

    def evaluate_alliance_request(self, proposal: AllianceProposal) -> AllianceResponse:
        """
        评估联盟请求

        Args:
            proposal: 联盟提议

        Returns:
            联盟响应
        """
        # 检查是否是对我的提议
        if proposal.target != self.agent.state.agent_id:
            return AllianceResponse(
                proposal_id=proposal.proposal_id,
                response_type="reject",
                reasoning="此提议不是针对我的"
            )

        # 评估联盟的收益
        benefit = self._evaluate_alliance_benefit(proposal)

        if benefit >= 0.7:
            return AllianceResponse(
                proposal_id=proposal.proposal_id,
                response_type="accept",
                reasoning=f"联盟收益({benefit:.2f})符合预期，接受提议"
            )
        elif benefit >= 0.4:
            # 可能提出反提案
            counter_terms = self._formulate_counter_terms(proposal)
            return AllianceResponse(
                proposal_id=proposal.proposal_id,
                response_type="counter_proposal",
                reasoning=f"联盟收益({benefit:.2f})需要调整条款",
                counter_terms=counter_terms
            )
        else:
            return AllianceResponse(
                proposal_id=proposal.proposal_id,
                response_type="reject",
                reasoning=f"联盟收益({benefit:.2f})低于预期"
            )

    def _evaluate_alliance_benefit(self, proposal: AllianceProposal) -> float:
        """
        评估联盟收益

        Args:
            proposal: 联盟提议

        Returns:
            收益评分 (0-1)
        """
        # 简化实现：根据条款评估收益
        terms = proposal.terms
        benefit = 0.0

        if terms.get("mutual_defense"):
            benefit += 0.3
        if terms.get("economic_cooperation"):
            benefit += 0.3
        if terms.get("trade_preferences"):
            benefit += 0.2
        if terms.get("decision_making") in ["consultative", "joint"]:
            benefit += 0.2

        return min(1.0, benefit)

    def _formulate_counter_terms(self, proposal: AllianceProposal) -> Dict:
        """
        制定反提案条款

        Args:
            proposal: 原始提议

        Returns:
            反提案条款
        """
        terms = proposal.terms.copy()

        # 尝试改善条款
        if terms.get("decision_making") == "leader_led":
            terms["decision_making"] = "consultative"
            terms["notes"] = "建议采用协商决策机制"

        return terms

    def maintain_alliance(self, alliance_id: str) -> Dict:
        """
        维护联盟

        Args:
            alliance_id: 联盟ID

        Returns:
            维护行动
        """
        # 根据领导类型决定维护方式
        leader_type = self.agent.state.leader_type

        if leader_type == LeaderType.WANGDAO:
            return {
                "action": "regular_consultation",
                "method": "multilateral_dialogue",
                "reasoning": "通过定期协商维护联盟关系"
            }
        elif leader_type == LeaderType.BAQUAN:
            return {
                "action": "reinforce_leadership",
                "method": "resource_allocation",
                "reasoning": "通过资源分配强化领导地位"
            }
        elif leader_type == LeaderType.QIANGQUAN:
            return {
                "action": "demand_compliance",
                "method": "pressure",
                "reasoning": "通过压力要求盟友服从"
            }
        else:  # HUNYONG
            return {
                "action": "variable_engagement",
                "method": "situational",
                "reasoning": "根据具体情况调整参与程度"
            }

    def dissolve_alliance(self, alliance_id: str, reason: str) -> Dict:
        """
        解散联盟

        Args:
            alliance_id: 联盟ID
            reason: 解散原因

        Returns:
            解散结果
        """
        return {
            "alliance_id": alliance_id,
            "action": "dissolve",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }


class StateAgent(BaseAgent):
    """
    大国智能体 - 对应技术方案3.3.2节

    适用范围：超级大国、大国
    必须配置：leader_type（王道型/霸权型/强权型/昏庸型）

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
        self.global_strategy = None
        self.regional_strategy = None
        self.alliance_manager = None

    def complete_initialization(self) -> None:
        """完成最终初始化"""
        super().complete_initialization()

        # 初始化策略模块
        self.global_strategy = GlobalLeadershipStrategy(self)
        self.regional_strategy = RegionalManagementStrategy(self)
        self.alliance_manager = AllianceManager(self)

    def _get_core_preferences(self, leader_type: Optional[LeaderType] = None) -> Dict[str, float]:
        """获取核心偏好 - 对应技术方案领导类型偏好表"""
        preferences = {
            LeaderType.WANGDAO: {
                "system_stability": 1.0,
                "national_long_term_interest": 0.9,
                "national_short_term_interest": 0.7,
                "personal_interest": 0.1
            },
            LeaderType.BAQUAN: {
                "national_core_interest": 1.0,
                "alliance_system_interest": 0.9,
                "system_stability": 0.7,
                "personal_interest": 0.2
            },
            LeaderType.QIANGQUAN: {
                "national_short_term_core_interest": 1.0,
                "national_long_term_interest": 0.6,
                "others_interest": 0.1
            },
            LeaderType.HUNYONG: {
                "personal_interest": 1.0,
                "faction_interest": 0.9,
                "national_nominal_interest": 0.5
            }
        }
        return preferences.get(leader_type, {})

    def _get_behavior_boundaries(self, leader_type: Optional[LeaderType] = None) -> List[str]:
        """获取行为边界"""
        boundaries = {
            LeaderType.WANGDAO: [
                "非暴力手段优先",
                "平等协商对话",
                "提供国际公共产品",
                "塑造公平国际规范"
            ],
            LeaderType.BAQUAN: [
                "选择性使用暴力/强制手段",
                "对盟友与对手执行双重标准",
                "主导国际制度",
                "有条件履行国际承诺"
            ],
            LeaderType.QIANGQUAN: [
                "暴力/强制手段优先",
                "无视国际承诺与规则",
                "通过实力压制实现目标",
                "拒绝多边协商与调停"
            ],
            LeaderType.HUNYONG: [
                "决策高度个人化",
                "言行严重不一致",
                "频繁毁约与外交转向",
                "可采取自我伤害行为"
            ]
        }
        return boundaries.get(leader_type, [])
