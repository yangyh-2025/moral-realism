"""
互动规则实现 - 对应技术方案3.3.4节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from enum import Enum
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel
from datetime import datetime
import json


class InteractionType(Enum):
    """互动类型"""
    FORM_ALLIANCE = "form_alliance"
    SIGN_TREATY = "sign_treaty"
    PROVIDE_AID = "provide_aid"
    DIPLOMATIC_SUPPORT = "diplomatic_support"
    DECLARE_WAR = "declare_war"
    IMPOSE_SANCTIONS = "impose_sanctions"
    DIPLOMATIC_PROTEST = "diplomatic_protest"
    SEND_MESSAGE = "send_message"
    HOLD_SUMMIT = "hold_summit"
    PUBLIC_STATEMENT = "public_statement"
    ECONOMIC_PRESSURE = "economic_pressure"
    CULTURAL_INFLUENCE = "cultural_influence"
    MILITARY_POSTURE = "military_posture"

    def __str__(self) -> str:
        """字符串表示"""
        return self.value

    def get_description(self) -> str:
        """获取互动类型描述"""
        descriptions = {
            InteractionType.FORM_ALLIANCE: "建立军事或政治联盟",
            InteractionType.SIGN_TREATY: "签署国际条约或协定",
            InteractionType.PROVIDE_AID: "提供经济或技术援助",
            InteractionType.DIPLOMATIC_SUPPORT: "提供外交支持",
            InteractionType.DECLARE_WAR: "宣战或发动军事行动",
            InteractionType.IMPOSE_SANCTIONS: "实施经济制裁",
            InteractionType.DIPLOMATIC_PROTEST: "发表外交抗议声明",
            InteractionType.SEND_MESSAGE: "发送外交照会或信函",
            InteractionType.HOLD_SUMMIT: "举办或参与首脑会晤",
            InteractionType.PUBLIC_STATEMENT: "发表公开声明或演讲",
            InteractionType.ECONOMIC_PRESSURE: "施加经济压力",
            InteractionType.CULTURAL_INFLUENCE: "开展文化交流或影响活动",
            InteractionType.MILITARY_POSTURE: "军事部署或演习"
        }
        return descriptions.get(self, "")


class Interaction(BaseModel):
    """互动"""
    interaction_id: str
    interaction_type: InteractionType
    source_agent: str
    target_agent: Optional[str]
    parameters: Dict
    timestamp: str
    round: int

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "interaction_id": self.interaction_id,
            "interaction_type": self.interaction_type.value,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "round": self.round
        }


class ValidationResult(BaseModel):
    """验证结果"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

    def add_error(self, error: str) -> None:
        """添加错误"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings
        }


class Constraint(BaseModel):
    """约束"""
    constraint_type: str
    description: str
    severity: float  # 0-1

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "constraint_type": self.constraint_type,
            "description": self.description,
            "severity": self.severity
        }


class RelationChange(BaseModel):
    """关系变化"""
    agent_pair: Tuple[str, str]
    change_amount: float
    reason: str

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "agent_pair": self.agent_pair,
            "change_amount": self.change_amount,
            "reason": self.reason
        }


class PowerChange(BaseModel):
    """实力变化"""
    agent_id: str
    change_amount: float
    reason: str

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "change_amount": self.change_amount,
            "reason": self.reason
        }


class GlobalChange(BaseModel):
    """全局变化"""
    metric: str
    change_amount: float
    reason: str

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "metric": self.metric,
            "change_amount": self.change_amount,
            "reason": self.reason
        }


class ThirdPartyEffect(BaseModel):
    """第三方效应"""
    agent_id: str
    effect_type: str
    impact: float
    reason: str

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "effect_type": self.effect_type,
            "impact": self.impact,
            "reason": self.reason
        }


class InteractionPattern(BaseModel):
    """互动模式"""
    agent_id: str
    frequent_actions: List[InteractionType]
    preferred_partners: List[str]
    action_tendencies: Dict[InteractionType, float]

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "frequent_actions": [a.value for a in self.frequent_actions],
            "preferred_partners": self.preferred_partners,
            "action_tendencies": {k.value: v for k, v in self.action_tendencies.items()}
        }


class PredictedInteraction(BaseModel):
    """预测互动"""
    predicted_type: InteractionType
    source_agent: str
    target_agent: Optional[str]
    confidence: float
    reasoning: str

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "predicted_type": self.predicted_type.value,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


class InteractionRules:
    """
    互动规则

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, config: Dict):
        """
        初始化互动规则

        Args:
            config: 规则配置
        """
        self.config = config
        self._interaction_counter = 0

    def validate_interaction(self, interaction: Interaction, context: Dict) -> ValidationResult:
        """
        验证互动

        Args:
            interaction: 互动
            context: 上下文信息

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        # 1. 检查互动类型是否有效
        if not isinstance(interaction.interaction_type, InteractionType):
            result.add_error("无效的互动类型")

        # 2. 检查源智能体是否存在
        agents = context.get("agents", [])
        agent_ids = [a.get("agent_id") for a in agents]

        if interaction.source_agent not in agent_ids:
            result.add_error(f"源智能体 {interaction.source_agent} 不存在")

        # 3. 如果需要目标智能体，检查目标是否存在
        if interaction.target_agent:
            if interaction.target_agent not in agent_ids:
                result.add_error(f"目标智能体 {interaction.target_agent} 不存在")

            # 4. 检查源和目标是否相同
            if interaction.target_agent == interaction.source_agent:
                result.add_error("源智能体和目标智能体不能相同")

        # 5. 检查互动约束
        constraints = self.check_interaction_constraints(interaction, context)
        high_severity_constraints = [c for c in constraints if c.severity > 0.8]

        if high_severity_constraints:
            for constraint in high_severity_constraints:
                result.add_error(
                    f"违反约束: {constraint.description} "
                    f"(严重性: {constraint.severity:.2f})"
                )

        # 6. 检查是否在禁止的互动类型中
        forbidden_types = self._get_forbidden_types(interaction.source_agent, context)
        if interaction.interaction_type in forbidden_types:
            result.add_error(
                f"智能体 {interaction.source_agent} 禁止使用互动类型 "
                f"{interaction.interaction_type.value}"
            )

        return result

    def _get_forbidden_types(self, agent_id: str, context: Dict) -> List[InteractionType]:
        """
        获取禁止的互动类型

        Args:
            agent_id: 智能体ID
            context: 上下文

        Returns:
            禁止的互动类型列表
        """
        # 根据智能体的领导类型确定禁止的互动类型
        agents = context.get("agents", [])
        agent = next((a for a in agents if a.get("agent_id") == agent_id), None)

        if not agent:
            return []

        leader_type = agent.get("leader_type")

        if leader_type == "wangdao":
            # 王道型禁止使用武力等极端手段
            return [
                InteractionType.DECLARE_WAR,
            ]
        elif leader_type == "hunyong":
            # 昏庸型无特殊限制
            return []
        else:
            return []

    def get_allowed_interactions(self, agent: Dict, context: Dict) -> List[InteractionType]:
        """
        获取允许的互动

        Args:
            agent: 智能体
            context: 上下文

        Returns:
            允许的互动类型列表
        """
        forbidden_types = self._get_forbidden_types(agent.get("agent_id"), context)

        return [
            interaction_type
            for interaction_type in InteractionType
            if interaction_type not in forbidden_types
        ]

    def get_forbidden_interactions(self, agent: Dict, context: Dict) -> List[InteractionType]:
        """
        获取禁止的互动

        Args:
            agent: 智能体
            context: 上下文

        Returns:
            禁止的互动类型列表
        """
        return self._get_forbidden_types(agent.get("agent_id"), context)

    def check_interaction_constraints(self, interaction: Interaction, context: Dict) -> List[Constraint]:
        """
        检查互动约束

        Args:
            interaction: 互动
            context: 上下文

        Returns:
            约束列表
        """
        constraints = []

        # 检查关系约束
        relation_constraint = self._check_relation_constraint(interaction, context)
        if relation_constraint:
            constraints.append(relation_constraint)

        # 检查实力约束
        power_constraint = self._check_power_constraint(interaction, context)
        if power_constraint:
            constraints.append(power_constraint)

        # 检查频率约束
        frequency_constraint = self._check_frequency_constraint(interaction, context)
        if frequency_constraint:
            constraints.append(frequency_constraint)

        # 检查互斥约束
        mutual_exclusion_constraint = self._check_mutual_exclusion_constraint(interaction, context)
        if mutual_exclusion_constraint:
            constraints.append(mutual_exclusion_constraint)

        return constraints

    def _check_relation_constraint(self, interaction: Interaction, context: Dict) -> Optional[Constraint]:
        """检查关系约束"""
        # 某些互动需要特定的关系水平
        relations = context.get("relations", {})

        if interaction.target_agent:
            pair_key = f"{interaction.source_agent}_{interaction.target_agent}"
            if pair_key not in relations:
                pair_key = f"{interaction.target_agent}_{interaction.source_agent}"

            relation_level = relations.get(pair_key, 0)

            # 宣战需要敌对关系
            if interaction.interaction_type == InteractionType.DECLARE_WAR:
                if relation_level < -0.5:
                    pass  # 合理
                else:
                    return Constraint(
                        constraint_type="relation",
                        description=f"宣战需要敌对关系（当前: {relation_level:.2f}）",
                        severity=0.7
                    )

            # 联盟需要友好关系
            if interaction.interaction_type == InteractionType.FORM_ALLIANCE:
                if relation_level > 0.5:
                    pass  #合理
                else:
                    return Constraint(
                        constraint_type="relation",
                        description=f"建立联盟需要友好关系（当前: {relation_level:.2f}）",
                        severity=0.6
                    )

        return None

    def _check_power_constraint(self, interaction: Interaction, context: Dict) -> Optional[Constraint]:
        """检查实力约束"""
        # 某些互动需要足够的实力
        agents = context.get("agents", [])
        source_agent = next(
            (a for a in agents if a.get("agent_id") == interaction.source_agent),
            None
        )

        if not source_agent:
            return None

        source_power = source_agent.get("power", 0)

        # 宣战需要足够的实力
        if interaction.interaction_type == InteractionType.DECLARE_WAR:
            if source_power < 100:
                return Constraint(
                    constraint_type="power",
                    description="宣战需要足够的实力支持",
                    severity=0.8
                )

        # 提供援助需要一定的经济实力
        if interaction.interaction_type == InteractionType.PROVIDE_AID:
            if source_power < 50:
                return Constraint(
                    constraint_type="power",
                    description="提供援助需要一定的经济实力",
                    severity=0.5
                )

        return None

    def _check_frequency_constraint(self, interaction: Interaction, context: Dict) -> Optional[Constraint]:
        """检查频率约束"""
        # 检查同类型的互动是否过于频繁
        history = context.get("interaction_history", [])

        # 获取同一智能体的同类互动（最近10轮）
        recent_similar = [
            h for h in history
            if h.get("source_agent") == interaction.source_agent and
               h.get("interaction_type") == interaction.interaction_type.value and
               h.get("round", 0) >= interaction.round - 10
        ]

        if len(recent_similar) >= 5:
            return Constraint(
                constraint_type="frequency",
                description=f"该类型的互动过于频繁（最近10轮已{len(recent_similar)}次）",
                severity=0.6
            )

        return None

    def _check_mutual_exclusion_constraint(self, interaction: Interaction, context: Dict) -> Optional[Constraint]:
        """检查互斥约束"""
        # 某些互动类型是互斥的
        history = context.get("interaction_history", [])

        if not interaction.target_agent:
            return None

        # 检查最近是否执行了互斥的互动
        recent_interactions = [
            h for h in history
            if h.get("source_agent") == interaction.source_agent and
               h.get("target_agent") == interaction.target_agent and
               h.get("round", 0) >= interaction.round - 5
        ]

        mutual_exclusions = {
            InteractionType.FORM_ALLIANCE: [InteractionType.IMPOSE_SANCTIONS],
            InteractionType.PROVIDE_AID: [InteractionType.IMPOSE_SANCTIONS],
            InteractionType.SIGN_TREATY: [InteractionType.DECLARE_WAR],
        }

        for recent in recent_interactions:
            recent_type = InteractionType(recent.get("interaction_type"))
            if interaction.interaction_type in mutual_exclusions.get(recent_type, []):
                return Constraint(
                    constraint_type="mutual_exclusion",
                    description=f"与最近执行的互动 {recent_type.value} 互斥",
                    severity=0.9
                )

        return None

    def create_interaction(
        self,
        interaction_type: InteractionType,
        source_agent: str,
        target_agent: Optional[str],
        parameters: Dict,
        round: int
    ) -> Interaction:
        """
        创建互动

        Args:
            interaction_type: 互动类型
            source_agent: 源智能体
            target_agent: 目标智能体
            parameters: 参数
            round: 轮次

        Returns:
            互动
        """
        self._interaction_counter += 1
        interaction_id = f"interaction_{self._interaction_counter}"

        return Interaction(
            interaction_id=interaction_id,
            interaction_type=interaction_type,
            source_agent=source_agent,
            target_agent=target_agent,
            parameters=parameters,
            timestamp=datetime.now().isoformat(),
            round=round
        )


class InteractionImpactCalculator:
    """
    互动影响计算器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, rules: InteractionRules):
        """
        初始化影响计算器

        Args:
            rules: 互动规则
        """
        self.rules = rules

    def calculate_relation_impact(self, interaction: Interaction) -> RelationChange:
        """
        计算关系影响

        Args:
            interaction: 互动

        Returns:
            关系变化
        """
        if not interaction.target_agent:
            return RelationChange(
                agent_pair=(interaction.source_agent, ""),
                change_amount=0.0,
                reason="无目标智能体"
            )

        # 根据互动类型和参数计算关系影响
        change_amount = 0.0
        reason = ""

        interaction_type = interaction.interaction_type
        intensity = interaction.parameters.get("intensity", 1.0)

        if interaction_type == InteractionType.FORM_ALLIANCE:
            change_amount = 0.3 * intensity
            reason = "建立联盟，关系改善"

        elif interaction_type == InteractionType.SIGN_TREATY:
            change_amount = 0.2 * intensity
            reason = "签署条约，关系改善"

        elif interaction_type == InteractionType.PROVIDE_AID:
            change_amount = 0.25 * intensity
            reason = "提供援助，关系改善"

        elif interaction_type == InteractionType.DIPLOMATIC_SUPPORT:
            change_amount = 0.15 * intensity
            reason = "提供外交支持，关系改善"

        elif interaction_type == InteractionType.DECLARE_WAR:
            change_amount = -1.0
            reason = "宣战，关系恶化"

        elif interaction_type == InteractionType.IMPOSE_SANCTIONS:
            change_amount = -0.5 * intensity
            reason = "实施制裁，关系恶化"

        elif interaction_type == InteractionType.DIPLOMATIC_PROTEST:
            change_amount = -0.2 * intensity
            reason = "外交抗议，关系恶化"

        elif interaction_type == InteractionType.SEND_MESSAGE:
            message_type = interaction.parameters.get("message_type", "neutral")
            if message_type == "friendly":
                change_amount = 0.1
                reason = "发送友好信息"
            elif message_type == "hostile":
                change_amount = -0.1
                reason = "发送敌对信息"
            else:
                change_amount = 0.0
                reason = "发送中性信息"

        elif interaction_type == InteractionType.HOLD_SUMMIT:
            outcome = interaction.parameters.get("outcome", "neutral")
            if outcome == "successful":
                change_amount = 0.3
                reason = "首脑会晤成功"
            elif outcome == "failed":
                change_amount = -0.2
                reason = "首脑会晤失败"
            else:
                change_amount = 0.0
                reason = "首脑会晤无实质进展"

        elif interaction_type == InteractionType.PUBLIC_STATEMENT:
            statement_type = interaction.parameters.get("statement_type", "neutral")
            if statement_type == "praise":
                change_amount = 0.1
                reason = "公开赞扬"
            elif statement_type == "criticism":
                change_amount = -0.1
                reason = "公开批评"
            else:
                change_amount = 0.0
                reason = "中性公开声明"

        elif interaction_type == InteractionType.ECONOMIC_PRESSURE:
            change_amount = -0.3 * intensity
            reason = "经济施压，关系恶化"

        elif interaction_type == InteractionType.CULTURAL_INFLUENCE:
            change_amount = 0.1 * intensity
            reason = "文化影响，关系改善"

        elif interaction_type == InteractionType.MILITARY_POSTURE:
            posture_type = interaction.parameters.get("posture_type", "defensive")
            if posture_type == "defensive":
                change_amount = -0.1
                reason = "军事防御部署"
            elif posture_type == "offensive":
                change_amount = -0.3
                reason = "军事进攻部署"
            else:
                change_amount = 0.0
                reason = "常规军事部署"

        # 限制变化范围
        change_amount = max(-1.0, min(1.0, change_amount))

        return RelationChange(
            agent_pair=(interaction.source_agent, interaction.target_agent),
            change_amount=change_amount,
            reason=reason
        )

    def calculate_power_impact(self, interaction: Interaction) -> PowerChange:
        """
        计算实力影响

        Args:
            interaction: 互动

        Returns:
            实力变化
        """
        change_amount = 0.0
        reason = ""

        interaction_type = interaction.interaction_type
        intensity = interaction.parameters.get("intensity", 1.0)

        # 提供援助会消耗资源
        if interaction_type == InteractionType.PROVIDE_AID:
            aid_amount = interaction.parameters.get("amount", 10)
            change_amount = -aid_amount * 0.1 * intensity
            reason = "提供援助消耗资源"

        # 实施制裁也会消耗资源
        elif interaction_type == InteractionType.IMPOSE_SANCTIONS:
            change_amount = -5.0 * intensity
            reason = "实施制裁消耗资源"

        # 宣战会大量消耗资源
        elif interaction_type == InteractionType.DECLARE_WAR:
            change_amount = -20.0
            reason = "宣战消耗资源"

        # 首脑会晤会消耗少量资源
        elif interaction_type == InteractionType.HOLD_SUMMIT:
            change_amount = -1.0
            reason = "首脑会晤消耗资源"

        return PowerChange(
            agent_id=interaction.source_agent,
            change_amount=change_amount,
            reason=reason
        )

    def calculate_global_impact(self, interaction: Interaction) -> List[GlobalChange]:
        """
        计算全局影响

        Args:
            interaction: 互动

        Returns:
            全局变化列表
        """
        changes = []

        interaction_type = interaction.interaction_type

        # 宣战会影响全球稳定度
        if interaction_type == InteractionType.DECLARE_WAR:
            changes.append(GlobalChange(
                metric="global_stability",
                change_amount=-0.1,
                reason="宣战降低全球稳定度"
            ))

        # 建立联盟会影响全球平衡
        elif interaction_type == InteractionType.FORM_ALLIANCE:
            changes.append(GlobalChange(
                metric="alliance_count",
                change_amount=1.0,
                reason="新增联盟"
            ))

        # 签署条约会影响国际规范
        elif interaction_type == InteractionType.SIGN_TREATY:
            changes.append(GlobalChange(
                metric="treaty_count",
                change_amount=1.0,
                reason="新增条约"
            ))

        # 提供援助会影响全球发展水平
        elif interaction_type == InteractionType.PROVIDE_AID:
            changes.append(GlobalChange(
                metric="development_cooperation",
                change_amount=0.1,
                reason="发展合作增加"
            ))

        return changes

    def calculate_third_party_effects(self, interaction: Interaction, context: Dict) -> List[ThirdPartyEffect]:
        """
        计算第三方效应

        Args:
            interaction: 互动
            context: 上下文

        Returns:
            第三方效应列表
        """
        effects = []

        if not interaction.target_agent:
            return effects

        # 获取所有其他智能体
        agents = context.get("agents", [])
        third_parties = [
            a for a in agents
            if a.get("agent_id") != interaction.source_agent and
               a.get("agent_id") != interaction.target_agent
        ]

        interaction_type = interaction.interaction_type

        # 建立联盟会影响第三方的安全环境
        if interaction_type == InteractionType.FORM_ALLIANCE:
            for third_party in third_parties:
                # 检查第三方与源或目标的关系
                relations = context.get("relations", {})
                source_relation = relations.get(
                    f"{third_party['agent_id']}_{interaction.source_agent}",
                    relations.get(f"{interaction.source_agent}_{third_party['agent_id']}", 0)
                )
                target_relation = relations.get(
                    f"{third_party['agent_id']}_{interaction.target_agent}",
                    relations.get(f"{interaction.target_agent}_{third_party['agent_id']}", 0)
                )

                # 如果第三方与源或目标有友好关系，可能会感到安全威胁
                if source_relation > 0.5 or target_relation > 0.5:
                    effects.append(ThirdPartyEffect(
                        agent_id=third_party["agent_id"],
                        effect_type="security_concern",
                        impact=-0.1,
                        reason=f"对{interaction.source_agent}和{interaction.target_agent}建立联盟表示关注"
                    ))

        # 宣战会影响第三方的安全环境
        elif interaction_type == InteractionType.DECLARE_WAR:
            for third_party in third_parties:
                # 检查第三方与源或目标的关系
                relations = context.get("relations", {})
                source_relation = relations.get(
                    f"{third_party['agent_id']}_{interaction.source_agent}",
                    relations.get(f"{interaction.source_agent}_{third_party['agent_id']}", 0)
                )
                target_relation = relations.get(
                    f"{third_party['agent_id']}_{interaction.target_agent}",
                    relations.get(f"{interaction.target_agent}_{third_party['agent_id']}", 0)
                )

                # 如果第三方与目标有友好关系，可能会受到影响
                if target_relation > 0.5:
                    effects.append(ThirdPartyEffect(
                        agent_id=third_party["agent_id"],
                        effect_type="ally_under_attack",
                        impact=-0.2,
                        reason=f"盟友{interaction.target_agent}受到攻击"
                    ))

        return effects


class InteractionTracker:
    """
    互动追踪器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        self._history = []

    def record_interaction(self, interaction: Interaction, result: Dict) -> None:
        """
        记录互动

        Args:
            interaction: 互动
            result: 结果
        """
        record = {
            "interaction": interaction.to_dict(),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

        self._history.append(record)

    def get_interaction_history(self, agent_id: str) -> List[Dict]:
        """
        获取互动历史

        Args:
            agent_id: 智能体ID

        Returns:
            互动列表
        """
        history = []
        for record in self._history:
            interaction = record["interaction"]
            if (
                interaction.get("source_agent") == agent_id or
                interaction.get("target_agent") == agent_id
            ):
                history.append({
                    "interaction": interaction,
                    "result": record["result"]
                })

        return history

    def get_interaction_patterns(self, agent_id: str) -> InteractionPattern:
        """
        获取互动模式

        Args:
            agent_id: 智能体ID

        Returns:
            互动模式
        """
        # 获取该智能体的所有互动
        agent_history = self.get_interaction_history(agent_id)

        if not agent_history:
            return InteractionPattern(
                agent_id=agent_id,
                frequent_actions=[],
                preferred_partners=[],
                action_tendencies={}
            )

        # 统计频繁行动
        action_counts = {}
        partner_counts = {}
        total_interactions = len(agent_history)

        for record in agent_history:
            interaction = record["interaction"]
            interaction_type = InteractionType(interaction.get("interaction_type"))

            # 统计行动类型
            action_counts[interaction_type] = action_counts.get(interaction_type, 0) + 1

            # 统计合作伙伴
            target_agent = interaction.get("target_agent")
            if target_agent:
                partner_counts[target_agent] = partner_counts.get(target_agent, 0) + 1

        # 找出频繁行动（出现频率超过10%）
        frequent_actions = [
            action_type for action_type, count in action_counts.items()
            if count / total_interactions >= 0.1
        ]

        # 找出偏好的合作伙伴（出现频率超过20%）
        preferred_partners = [
            partner for partner, count in partner_counts.items()
            if count / total_interactions >= 0.2
        ]

        # 计算行动倾向
        action_tendencies = {
            action_type: count / total_interactions
            for action_type, count in action_counts.items()
        }

        return InteractionPattern(
            agent_id=agent_id,
            frequent_actions=frequent_actions,
            preferred_partners=preferred_partners,
            action_tendencies=action_tendencies
        )

    def predict_future_interactions(self, agent: Dict) -> List[PredictedInteraction]:
        """
        预测未来互动

        Args:
            agent: 智能体

        Returns:
            预测互动列表
        """
        predictions = []
        agent_id = agent.get("agent_id")

        if not agent_id:
            return predictions

        # 获取互动模式
        pattern = self.get_interaction_patterns(agent_id)

        # 根据互动模式预测
        for action_type, tendency in pattern.action_tendencies.items():
            # 如果倾向性超过30%，预测未来可能采取该行动
            if tendency >= 0.3:
                # 选择最偏好的合作伙伴作为预测目标
                target_agent = pattern.preferred_partners[0] if pattern.preferred_partners else None

                # 置信度基于倾向性
                confidence = min(1.0, tendency * 1.5)

                # 生成推理说明
                reasoning = f"基于历史互动模式，{agent_id}倾向于采取{action_type.value}行动"

                prediction = PredictedInteraction(
                    predicted_type=action_type,
                    source_agent=agent_id,
                    target_agent=target_agent,
                    confidence=confidence,
                    reasoning=reasoning
                )

                predictions.append(prediction)

        # 按置信度排序
        predictions.sort(key=lambda p: p.confidence, reverse=True)

        # 只返回置信度前5的预测
        return predictions[:5]

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        return {
            "total_interactions": len(self._history),
            "unique_agents": len(set(
                record["interaction"].get("source_agent")
                for record in self._history
            )),
            "interaction_types": self._get_interaction_type_counts()
        }

    def _get_interaction_type_counts(self) -> Dict[str, int]:
        """获取互动类型计数"""
        type_counts = {}
        for record in self._history:
            interaction_type = record["interaction"].get("interaction_type")
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1

        return type_counts

    def clear(self) -> None:
        """清空历史记录"""
        self._history.clear()
