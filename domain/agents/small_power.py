"""
小国智能体

对应 PowerTier.SMALL_POWER (z ≤ 0.5, 约69.15%)
不需要配置 leader_type

特点：
- 生存安全与渐进发展
- 维护国家主权和安全
- 确保经济生存与发展
- 在大国间保持平衡
- 寻求盟友或保护伞

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import random

from domain.agents.base_agent import BaseAgent


class LeaderCandidate:
    """
    领导人候选

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        power_score: float,
        reliability_score: float,
        benefit_assessment: Dict
    ):
        self.agent_id = agent_id
        self.name = name
        self.power_score = power_score
        self.reliability_score = reliability_score
        self.benefit_assessment = benefit_assessment

    def total_score(self) -> float:
        """计算综合得分"""
        return (
            self.power_score * 0.4 +
            self.reliability_score * 0.4 +
            self.benefit_assessment.get("total_benefit", 0) * 0.2
        )

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "power_score": self.power_score,
            "reliability_score": self.reliability_score,
            "benefit_assessment": self.benefit_assessment,
            "total_score": self.total_score()
        }


class BenefitAssessment:
    """
    收益评估

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        security_benefit: float,
        economic_benefit: float,
        political_benefit: float,
        total_benefit: float,
        risks: List[str]
    ):
        self.security_benefit = security_benefit
        self.economic_benefit = economic_benefit
        self.political_benefit = political_benefit
        self.total_benefit = total_benefit
        self.risks = risks

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "security_benefit": self.security_benefit,
            "economic_benefit": self.economic_benefit,
            "political_benefit": self.political_benefit,
            "total_benefit": self.total_benefit,
            "risks": self.risks
        }


class SurvivalThreat:
    """
    生存威胁

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        threat_type: str,
        source: str,
        severity: float,
        urgency: float,
        description: str
    ):
        self.threat_type = threat_type  # military, economic, political, environmental
        self.source = source
        self.severity = severity  # 0-1
        self.urgency = urgency  # 0-1
        self.description = description

    def overall_threat_level(self) -> float:
        """计算总体威胁水平"""
        return (self.severity + self.urgency) / 2

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "threat_type": self.threat_type,
            "source": self.source,
            "severity": self.severity,
            "urgency": self.urgency,
            "overall_level": self.overall_threat_level(),
            "description": self.description
        }


class SurvivalAction:
    """
    生存行动

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        action_type: str,
        target: Optional[str],
        parameters: Dict,
        reasoning: str
    ):
        self.action_type = action_type
        self.target = target
        self.parameters = parameters
        self.reasoning = reasoning

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "action_type": self.action_type,
            "target": self.target,
            "parameters": self.parameters,
            "reasoning": self.reasoning
        }


class ProtectionRequest:
    """
    保护请求

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        target_protector: str,
        request_type: str,
        terms: Dict,
        reasoning: str
    ):
        self.target_protector = target_protector
        self.request_type = request_type
        self.terms = terms
        self.reasoning = reasoning

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "target_protector": self.target_protector,
            "request_type": self.request_type,
            "terms": self.terms,
            "reasoning": self.reasoning
        }


class RelationAdjustment:
    """
    关系调整

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        target_agent: str,
        adjustment_type: str,
        new_relation_level: float,
        reasoning: str
    ):
        self.target_agent = target_agent
        self.adjustment_type = adjustment_type  # improve, maintain, deteriorate
        self.new_relation_level = new_relation_level
        self.reasoning = reasoning

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "target_agent": self.target_agent,
            "adjustment_type": self.adjustment_type,
            "new_relation_level": self.new_relation_level,
            "reasoning": self.reasoning
        }


class FollowerStrategy:
    """
    追随选择策略

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化追随策略

        Args:
            agent: 小国智能体实例
        """
        self.agent = agent
        self._current_leader = None
        self._leader_history = []

    def identify_potential_leaders(self, global_data: Dict) -> List[LeaderCandidate]:
        """
        识别潜在领导者

        Args:
            global_data: 全球数据

        Returns:
            领导者候选列表
        """
        # 获取所有大国和超级大国
        all_agents = global_data.get("agents", [])
        potential_leaders = [
            a for a in all_agents
            if a.get("power_tier") in ["superpower", "great_power"]
        ]

        candidates = []
        for leader_info in potential_leaders:
            leader_id = leader_info["agent_id"]
            leader_name = leader_info["name"]

            # 计算实力得分（归一化）
            power_score = min(1.0, leader_info.get("power", 0) / 500.0)

            # 计算可靠性得分
            reliability_score = self._calculate_reliability_score(leader_info)

            # 评估收益
            benefit_assessment = self.evaluate_leader_benefits(leader_id, global_data)

            candidate = LeaderCandidate(
                agent_id=leader_id,
                name=leader_name,
                power_score=power_score,
                reliability_score=reliability_score,
                benefit_assessment=benefit_assessment.to_dict()
            )

            candidates.append(candidate)

        # 按综合得分排序
        candidates.sort(key=lambda c: c.total_score(), reverse=True)

        return candidates

    def _calculate_reliability_score(self, leader_info: Dict) -> float:
        """
        计算领导者可靠性得分

        Args:
            leader_info: 领导者信息

        Returns:
            可靠性得分 (0-1)
        """
        # 根据领导类型评估可靠性
        leader_type = leader_info.get("leader_type")

        # 王道型最可靠，霸权型次之，昏庸型最不可靠
        if leader_type == "wangdao":
            return 0.9
        elif leader_type == "baquan":
            return 0.7
        elif leader_type == "qiangquan":
            return 0.5
        elif leader_type == "hunyong":
            return 0.3
        else:
            return 0.6

    def evaluate_leader_benefits(self, leader_id: str, global_data: Dict) -> BenefitAssessment:
        """
        评估领导者收益

        Args:
            leader_id: 领导者ID
            global_data: 全球数据

        Returns:
            收益评估
        """
        # 获取当前关系
        relations = global_data.get("relations", {})
        current_relation = relations.get(
            f"{self.agent.state.agent_id}_{leader_id}",
            relations.get(f"{leader_id}_{self.agent.state.agent_id}", 0)
        )

        # 安全收益
        security_benefit = self._assess_security_benefit(leader_id, global_data)

        # 经济收益
        economic_benefit = self._assess_economic_benefit(leader_id, global_data)

        # 政治收益
        political_benefit = self._assess_political_benefit(leader_id, global_data, current_relation)

        # 识别风险
        risks = self._identify_risks(leader_id, global_data)

        # 计算总收益
        total_benefit = (
            security_benefit * 0.5 +
            economic_benefit * 0.3 +
            political_benefit * 0.2
        )

        return BenefitAssessment(
            security_benefit=security_benefit,
            economic_benefit=economic_benefit,
            political_benefit=political_benefit,
            total_benefit=total_benefit,
            risks=risks
        )

    def _assess_security_benefit(self, leader_id: str, global_data: Dict) -> float:
        """评估安全收益"""
        # 检查是否有安全保障
        security_guarantees = global_data.get("security_guarantees", [])
        my_guarantees = [
            sg for sg in security_guarantees
            if sg.get("protector") == leader_id and
               sg.get("protected") == self.agent.state.agent_id
        ]

        if my_guarantees:
            return 0.9

        # 检查是否在军事同盟中
        alliances = global_data.get("alliances", [])
        my_alliances = [
            a for a in alliances
            if self.agent.state.agent_id in [a.get("agent1"), a.get("agent2")] and
               leader_id in [a.get("agent1"), a.get("agent2")] and
               a.get("alliance_type") == "military"
        ]

        if my_alliances:
            return 0.8

        # 根据关系水平评估潜在安全收益
        relations = global_data.get("relations", {})
        current_relation = relations.get(
            f"{self.agent.state.agent_id}_{leader_id}",
            relations.get(f"{leader_id}_{self.agent.state.agent_id}", 0)
        )

        return max(0.0, current_relation)

    def _assess_economic_benefit(self, leader_id: str, global_data: Dict) -> float:
        """评估经济收益"""
        # 检查是否有自贸协定
        agreements = global_data.get("trade_agreements", [])
        my_agreements = [
            a for a in agreements
            if self.agent.state.agent_id in a.get("participants", []) and
               leader_id in a.get("participants", [])
        ]

        if my_agreements:
            return 0.8

        # 检查是否有经济援助
        aid_records = global_data.get("aid_records", [])
        recent_aid = [
            ar for ar in aid_records
            if ar.get("donor") == leader_id and
               ar.get("recipient") == self.agent.state.agent_id
        ]

        if recent_aid:
            return 0.7

        return 0.3

    def _assess_political_benefit(
        self,
        leader_id: str,
        global_data: Dict,
        current_relation: float
    ) -> float:
        """评估政治收益"""
        # 根据领导类型和关系水平评估
        leader_info = None
        for agent in global_data.get("agents", []):
            if agent.get("agent_id") == leader_id:
                leader_info = agent
                break

        if not leader_info:
            return 0.0

        leader_type = leader_info.get("leader_type")

        # 王道型提供更好的政治支持
        if leader_type == "wangdao" and current_relation > 0.5:
            return 0.9
        elif leader_type == "baquan" and current_relation > 0.5:
            return 0.7
        else:
            return max(0.0, current_relation)

    def _identify_risks(self, leader_id: str, global_data: Dict) -> List[str]:
        """识别风险"""
        risks = []

        # 检查是否有冲突关系
        conflicts = global_data.get("conflicts", [])
        leader_conflicts = [
            c for c in conflicts
            if leader_id in [c.get("agent1"), c.get("agent2")]
        ]

        if leader_conflicts:
            risks.append("领导者存在国际冲突，可能被卷入")

        # 检查领导者的敌人
        leader_enemies = global_data.get("hostile_relations", {}).get(leader_id, [])
        if leader_enemies:
            risks.append(f"领导者与{len(leader_enemies)}个国家存在敌对关系")

        # 检查领导者类型
        for agent in global_data.get("agents", []):
            if agent.get("agent_id") == leader_id:
                leader_type = agent.get("leader_type")
                if leader_type == "qiangquan":
                    risks.append("强权型领导者可能采取激进政策")
                elif leader_type == "hunyong":
                    risks.append("昏庸型领导者决策不可预测")
                break

        return risks

    def choose_leader(self, global_data: Dict) -> Optional[str]:
        """
        选择领导者

        Args:
            global_data: 全球数据

        Returns:
            选择的领导者ID，或者None
        """
        candidates = self.identify_potential_leaders(global_data)

        if not candidates:
            return None

        # 选择综合得分最高的候选人
        best_candidate = candidates[0]

        # 检查收益是否超过阈值
        if best_candidate.total_score() < 0.5:
            return None

        # 检查是否有严重风险
        if len(best_candidate.benefit_assessment.get("risks", [])) > 2:
            # 如果有严重风险，选择次优候选人
            if len(candidates) > 1:
                return candidates[1].agent_id
            return None

        return best_candidate.agent_id

    def adjust_follower_relationship(self, global_data: Dict) -> RelationAdjustment:
        """
        调整追随者关系

        Args:
            global_data: 全球数据

        Returns:
            关系调整
        """
        # 评估当前领导者的收益
        if not self._current_leader:
            return RelationAdjustment(
                target_agent="",
                adjustment_type="maintain",
                new_relation_level=0.0,
                reasoning="当前没有追随的领导者"
            )

        benefit_assessment = self.evaluate_leader_benefits(
            self._current_leader, global_data
        )

        # 如果收益不足，考虑更换领导者
        if benefit_assessment.total_benefit < 0.4:
            new_leader = self.choose_leader(global_data)
            if new_leader and new_leader != self._current_leader:
                # 记录历史
                self._leader_history.append({
                    "old_leader": self._current_leader,
                    "new_leader": new_leader,
                    "timestamp": datetime.now().isoformat(),
                    "reason": "收益不足，更换领导者"
                })

                self._current_leader = new_leader

                return RelationAdjustment(
                    target_agent=new_leader,
                    adjustment_type="improve",
                    new_relation_level=0.8,
                    reasoning=f"当前领导者收益不足，转向{new_leader}"
                )

        # 维持当前关系
        return RelationAdjustment(
            target_agent=self._current_leader,
            adjustment_type="maintain",
            new_relation_level=0.7,
            reasoning="当前领导者关系稳定，维持现状"
        )


class SurvivalStrategy:
    """
    生存策略

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent: Any):
        """
        初始化生存策略

        Args:
            agent: 小国智能体实例
        """
        self.agent = agent
        self._threat_history = []

    def assess_survival_threats(self, global_data: Dict) -> List[SurvivalThreat]:
        """
        评估生存威胁

        Args:
            global_data: 全球数据

        Returns:
            威胁列表
        """
        threats = []
        my_id = self.agent.state.agent_id

        # 评估军事威胁
        military_threats = self._assess_military_threats(my_id, global_data)
        threats.extend(military_threats)

        # 评估经济威胁
        economic_threats = self._assess_economic_threats(my_id, global_data)
        threats.extend(economic_threats)

        # 评估政治威胁
        political_threats = self._assess_political_threats(my_id, global_data)
        threats.extend(political_threats)

        # 按严重程度排序
        threats.sort(key=lambda t: t.overall_threat_level(), reverse=True)

        return threats

    def _assess_military_threats(self, my_id: str, global_data: Dict) -> List[SurvivalThreat]:
        """评估军事威胁"""
        threats = []

        # 检查是否有军事冲突
        conflicts = global_data.get("conflicts", [])
        my_conflicts = [
            c for c in conflicts
            if my_id in [c.get("agent1"), c.get("agent2")] and
               c.get("conflict_type") == "military"
        ]

        for conflict in my_conflicts:
            source = conflict.get("agent2") if conflict.get("agent1") == my_id else conflict.get("agent1")
            severity = conflict.get("intensity", 0.5)
            urgency = conflict.get("urgency", 0.5)

            threat = SurvivalThreat(
                threat_type="military",
                source=source,
                severity=severity,
                urgency=urgency,
                description=f"与{source}存在军事冲突，强度{severity:.2f}"
            )
            threats.append(threat)

        return threats

    def _assess_economic_threats(self, my_id: str, global_data: Dict) -> List[SurvivalThreat]:
        """评估经济威胁"""
        threats = []

        # 检查是否有经济制裁
        sanctions = global_data.get("sanctions", [])
        my_sanctions = [
            s for s in sanctions
            if s.get("target") == my_id
        ]

        for sanction in my_sanctions:
            source = sanction.get("imposer")
            severity = sanction.get("severity", 0.5)
            urgency = sanction.get("urgency", 0.3)

            threat = SurvivalThreat(
                threat_type="economic",
                source=source,
                severity=severity,
                urgency=urgency,
                description=f"受到{source}的经济制裁"
            )
            threats.append(threat)

        return threats

    def _assess_political_threats(self, my_id: str, global_data: Dict) -> List[SurvivalThreat]:
        """评估政治威胁"""
        threats = []

        # 检查敌对关系
        relations = global_data.get("relations", {})
        hostile_agents = []
        for key, value in relations.items():
            if my_id in key and value < -0.7:
                parts = key.split("_")
                source = parts[1] if parts[0] == my_id else parts[0]
                hostile_agents.append(source)

        for source in hostile_agents:
            threat = SurvivalThreat(
                threat_type="political",
                source=source,
                severity=0.6,
                urgency=0.4,
                description=f"与{source}存在敌对政治关系"
            )
            threats.append(threat)

        return threats

    def formulate_survival_response(self, threat: SurvivalThreat) -> SurvivalAction:
        """
        制定生存响应

        Args:
            threat: 威胁

        Returns:
            生存行动
        """
        # 根据威胁类型制定响应策略
        if threat.threat_type == "military":
            return self._formulate_military_response(threat)
        elif threat.threat_type == "economic":
            return self._formulate_economic_response(threat)
        elif threat.threat_type == "political":
            return self._formulate_political_response(threat)
        else:
            return SurvivalAction(
                action_type="observe",
                target=None,
                parameters={},
                reasoning="观察威胁发展"
            )

    def _formulate_military_response(self, threat: SurvivalThreat) -> SurvivalAction:
        """制定军事威胁响应"""
        if threat.urgency > 0.7:
            return SurvivalAction(
                action_type="seek_protection",
                target=threat.source,
                parameters={"urgency": "high"},
                reasoning=f"面临来自{threat.source}的紧迫军事威胁，寻求保护"
            )
        elif threat.urgency > 0.5:
            return SurvivalAction(
                action_type="diplomatic_appeal",
                target=threat.source,
                parameters={"message": "停止敌对行动"},
                reasoning=f"面临{threat.source}的军事威胁，通过外交途径解决"
            )
        else:
            return SurvivalAction(
                action_type="military_deterrence",
                target=None,
                parameters={"defensive_measures": True},
                reasoning="加强防御措施，威慑潜在军事威胁"
            )

    def _formulate_economic_response(self, threat: SurvivalThreat) -> SurvivalAction:
        """制定经济威胁响应"""
        if threat.urgency > 0.6:
            return SurvivalAction(
                action_type="seek_aid",
                target=threat.source,
                parameters={"alternative_partners": True},
                reasoning=f"寻求经济援助或寻找替代合作伙伴"
            )
        else:
            return SurvivalAction(
                action_type="economic_adjustment",
                target=None,
                parameters={"diversification": True},
                reasoning="调整经济结构，降低对单一来源的依赖"
            )

    def _formulate_political_response(self, threat: SurvivalThreat) -> SurvivalAction:
        """制定政治威胁响应"""
        if threat.urgency > 0.6:
            return SurvivalAction(
                action_type="seek_mediation",
                target=threat.source,
                parameters={"third_party": True},
                reasoning=f"寻求第三方调解与{threat.source}的政治冲突"
            )
        else:
            return SurvivalAction(
                action_type="public_appeal",
                target=None,
                parameters={"international_community": True},
                reasoning="向国际社区发出呼吁，寻求支持"
            )

    def seek_protection(self, global_data: Dict) -> ProtectionRequest:
        """
        寻求保护

        Args:
            global_data: 全球数据

        Returns:
            保护请求
        """
        # 评估威胁
        threats = self.assess_survival_threats(global_data)

        if not threats:
            return ProtectionRequest(
                target_protector="",
                request_type="none",
                terms={},
                reasoning="当前没有明显威胁，无需寻求保护"
            )

        # 选择最紧迫的威胁
        urgent_threat = max(threats, key=lambda t: t.urgency)

        # 选择合适的保护者（优先选择王道型大国）
        protector = self._select_protector(urgent_threat.source, global_data)

        if not protector:
            return ProtectionRequest(
                target_protector="",
                request_type="none",
                terms={},
                reasoning="没有找到合适的保护者"
            )

        # 制定保护请求条款
        terms = {
            "protection_type": "security_guarantee",
            "duration": "until_threat_resolved",
            "compensation": "political_support"
        }

        return ProtectionRequest(
            target_protector=protector,
            request_type="security_guarantee",
            terms=terms,
            reasoning=f"面临来自{urgent_threat.source}的{urgent_threat.threat_type}威胁，请求{protector}提供保护"
        )

    def _select_protector(self, threat_source: str, global_data: Dict) -> Optional[str]:
        """
        选择保护者

        Args:
            threat_source: 威胁来源
            global_data: 全球数据

        Returns:
            保护者ID
        """
        # 获取所有大国和超级大国
        all_agents = global_data.get("agents", [])
        potential_protectors = [
            a for a in all_agents
            if a.get("power_tier") in ["superpower", "great_power"]
        ]

        # 排除威胁来源
        potential_protectors = [
            p for p in potential_protectors
            if p.get("agent_id") != threat_source
        ]

        if not potential_protectors:
            return None

        # 优先选择王道型领导者
        for protector in potential_protectors:
            if protector.get("leader_type") == "wangdao":
                return protector["agent_id"]

        # 其次选择霸权型
        for protector in potential_protectors:
            if protector.get("leader_type") == "baquan":
                return protector["agent_id"]

        # 选择第一个可用的保护者
        return potential_protectors[0]["agent_id"]


class SmallPowerAgent(BaseAgent):
    """
    小国智能体

    适用范围：小国 (PowerTier.SMALL_POWER, z ≤ 0.5, 约69.15%)
    不需要配置 leader_type

    特点：
    - 生存安全与渐进发展
    - 维护国家主权和安全
    - 确保经济生存，渐进发展
    - 在大国间保持平衡
    - 寻求盟友或保护伞

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
        初始化小国智能体

        Args:
            agent_id: 智能体唯一ID
            name: 国家名称
            region: 国家所属区域
            power_metrics: 实力指标
        """
        super().__init__(agent_id, name, region, power_metrics)

        # 策略模块将在complete_initialization中初始化
        self.follower_strategy = None
        self.survival_strategy = None

    def complete_initialization(self) -> None:
        """完成最终初始化"""
        super().complete_initialization()

        # 初始化策略模块
        self.follower_strategy = FollowerStrategy(self)
        self.survival_strategy = SurvivalStrategy(self)

    def _get_core_preferences(self, leader_type=None) -> Dict[str, float]:
        """小国核心偏好"""
        return {
            "sovereignty_security": 1.0,
            "economic_development": 0.9,
            "avoid_conflict_spillover": 0.8,
            "favorable_external_environment": 0.7
        }

    def _get_behavior_boundaries(self, leader_type=None) -> List[str]:
        """小国行为边界"""
        return [
            "以大国行为带来的收益/风险为核心决策依据",
            "优先选择能保障自身核心利益的策略",
            "通过选边、结盟、投票影响大国软实力"
        ]
