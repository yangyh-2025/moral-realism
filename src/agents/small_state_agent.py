"""
道义现实主义ABM系统的小国代理实现

本模块实现SmallStateAgent类，使用基于规则的
决策制定来评估大国并与最具吸引力的领导类型对齐，
验证"道义型领导吸引支持"的理论。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability


logger = logging.getLogger(__name__)


class SmallStateAction(Enum):
    """小国可用的行动类型"""

    ALIGN_FOLLOW = "align_follow"  # 结盟跟随
    NEUTRAL_OBSERVE = "neutral_observe"  # 中立观望
    SIDE_SELECTION = "side_selection"  # 选边站队
    DEFECT_SWITCH = "defect_switch"  # 倒戈转向
    NO_ALLIANCE_COALITION = "no_alliance_coalition"  # 不结盟联合
    MEDIATION = "mediation"  # 大国间调停
    COUNTER_RESPOND = "counter_respond"  # 反制/响应


class StrategicStance(Enum):
    """小国对大国的战略姿态"""

    ALIGNED = "aligned"  # 与特定大国结盟
    NEUTRAL = "neutral"  # 保持中立
    NON_ALIGNED = "non_aligned"  # 非结盟运动
    SWING = "swing"  # 摇摆国，会转变结盟


@dataclass
class SmallStateAgent(Agent):
    """
    小国代理类

    一个评估大国并跟随它们的小国代理。
    该代理使用基于规则的逻辑来评估大国的领导类型和行为，
    验证道义现实主义中的"道义型领导吸引支持"理论。

    关键原则：
    - 道义型领导提供最高吸引力（得分4）
    - 霸权型领导提供中高吸引力（得分3）
    - 强权型领导提供中等吸引力（得分2）
    - 昏庸型领导提供最低吸引力（得分1）
    """

    # 对大国的战略姿态
    strategic_stance: StrategicStance = StrategicStance.NEUTRAL

    # 当前结盟
    aligned_with: Optional[str] = None  # agent大国代理ID

    # 领导类型偏好（越高=越具吸引力）
    leadership_preferences: Dict[str, float] = field(
        default_factory=lambda: {
            "wangdao": 4.0,  # 对道义型领导的最高偏好
            "hegemon": 3.0,  # 对传统霸权的中高偏好
            "qiangquan": 2.0,  # 对强权型的中等偏好
            "hunyong": 1.0,  # 对绥庸型的最低偏好
        }
    )

    # 评估权重
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "leadership_type": 0.4,  # 领导类型的权重
            "behavior_score": 0.3,  # 最近行为的权重
            "capability": 0.2,  # 能力/权力的权重
            "relationship": 0.1,  # 现有关系的权重
        }
    )

    # 结盟的最低阈值
    alignment_threshold: float = 30.0  # 结盟的最低得分

    # 用于结盟比较的先前得分（用于检测背叛）
    previous_alignment_score: float = 0.0

    # 背叛的阈值（当得分下降这么多时）
    defection_threshold: float = 15.0

    def __post_init__(self) -> None:
        """数据类初始化后的处理"""
        # 设置代理类型
        self.agent_type = AgentType.SMALL_STATE

        # 初始化领导配置文件（如果未设置）
        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        # 初始化能力（如果未设置）
        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        # 初始化与自己的关系
        self.relations[self.agent_id] = 1.0

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        通过评估大国并选择结盟来做出决策

        实现7种行为类型：
        1. ALIGN_FOLLOW - 结盟并跟随一个大国
        2. NEUTRAL_OBSERVE - 保持中立并观察
        3. SIDE_SELECTION - 在冲突中选边站队
        4. DEFECT_SWITCH - 条件变化时转变结盟
        5. NO_ALLIANCE_COALITION - 结成非结盟联盟
        6. MEDIATION - 在大国间进行调停
        7. COUNTER_RESPOND - 反制/响应敌对行动

        Args:
            situation: 当前情况的描述
            available_actions: 代理可用的行动列表
            context: 决策制定的附加上下文，应包含'great_powers'

        Returns:
            包含决策和理由的字典
        """
        if context is None:
            context = {}

        great_powers = context.get("great_powers", [])
        events = situation.get("events", [])
        in_crisis = situation.get("in_crisis", False)

        # 评估所有大国
        assessments = self._assess_great_powers(great_powers, context)

        # 根据评估确定行动类型
        action_type, rationale = self._determine_action_type(
            assessments, great_powers, situation, context
        )

        # 根据行动更新姿态
        self._update_stance_from_action(action_type, assessments)

        decision = {
            "agent_id": self.agent_id,
            "action_type": action_type.value,
            "action": action_type.value,
            "target_agent_id": self.aligned_with,
            "rationale": rationale,
            "strategic_stance": self.strategic_stance.value,
            "assessments": assessments,
            "alignment_threshold": self.alignment_threshold,
            "in_crisis": in_crisis,
        }

        # 在历史中记录决策
        self.add_history(
            "decision",
            f"决定执行 {action_type.value}",
            metadata={
                "decision": decision,
                "situation": situation,
            },
        )

        logger.info(
            f"{self.name} 决定执行 {action_type.value}。"
            f"姿态: {self.strategic_stance.value}，"
            f"与 {self.aligned_with or '无大国'} 结盟"
        )

        return decision

    def _determine_action_type(
        self,
        assessments: List[Dict[str, Any]],
        great_powers: List[Dict[str, Any]],
        situation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> tuple[SmallStateAction, str]:
        """
        根据评估和情况确定行动类型

        实现7种行为类型的选择逻辑。

        Args:
            assessments: 大国评估列表
            great_powers: 大国列表
            situation: 当前情况
            context: 附加上下文

        Returns:
            (action_type, rationale) 元组
        """
        if not assessments:
            return SmallStateAction.NEUTRAL_OBSERVE, (
                "没有可用的大国进行评估。"
                "保持中立观察。"
            )

        in_crisis = situation.get("in_crisis", False)
        events = situation.get("events", [])

        # 找到最佳评估
        best = max(assessments, key=lambda x: x["score"])
        best_score = best["score"]

        # 检查是否触发背叛（得分显著下降）
        if self.aligned_with and self.previous_alignment_score > 0:
            if best_score < self.previous_alignment_score - self.defection_threshold:
                self.previous_alignment_score = best_score
                return SmallStateAction.DEFECT_SWITCH, (
                    f"当前结盟得分下降了"
                    f"{self.previous_alignment_score - best_score:.2f}，"
                    f"从先前的大国转向到"
                    f"{best.get('name', '新结盟')}。"
                    f"先前的政策不再符合我们的利益。"
                )

        self.previous_alignment_score = best_score

        # 行为1: ALIGN_FOLLOW - 当最佳满足阈值时
        if best_score >= self.alignment_threshold and not in_crisis:
            return SmallStateAction.ALIGN_FOLLOW, (
                f"与 {best['name']} 结盟，由于他们的"
                f"{best['leadership_type']} 领导型（得分：{best_score:.2f}）。"
                f"他们的道德行为和行为提供了有吸引力的益处。"
            )

        # 行为2: NEUTRAL_OBSERVE - 当没有大国满足阈值时
        if best_score < self.alignment_threshold and not in_crisis:
            return SmallStateAction.NEUTRAL_OBSERVE, (
                f"保持中立，因为没有大国满足"
                f"结盟阈值（阈值：{self.alignment_threshold}，"
                f"最佳得分：{best_score:.2f}）。"
                f"当前的大国缺乏足够的道义领导"
                f"或有吸引力的行为。"
            )

        # 行为：检查相似得分（联盟机会）
        if len(assessments) >= 2:
            scores = [a["score"] for a in assessments]
            score_variance = max(scores) - min(scores)
            if score_variance < 10 and len(assessments) > 2:
                return SmallStateAction.NO_ALLIANCE_COALITION, (
                    f"多个大国具有相似的得分"
                    f"（方差：{score_variance:.2f}）。"
                    f"结成非结盟联盟以平衡影响力。"
                )

        # 行为3: SIDE_SELECTION - 在危机中，选边站队
        if in_crisis:
            # 在危机中如果有可用的道义型领导则优先
            wangdao_assessment = next(
                (a for a in assessments if a["leadership_type"] == "wangdao"),
                None
            )
            if wangdao_assessment and wangdao_assessment["score"] >= 20:
                return SmallStateAction.SIDE_SELECTION, (
                    f"在危机中，选择与 {wangdao_assessment['name']} 的站队，"
                    f"由于他们的道德领导和提供安全的能力。"
                    f"在危机中与有原则的领导结盟。"
                )
            else:
                return SmallStateAction.SIDE_SELECTION, (
                    f"在危机中，选择与 {best['name']} 的站队"
                    f"（得分：{best_score:.2f}）以获得安全和支持。"
                )

        # 行为7: COUNTER_RESPOND - 响应敌对行动
        for event in events[-3:]:
            if self._is_hostile_action(event, great_powers):
                sender_id = event.get("sender_id", "")
                relationship = self.get_relationship(sender_id)
                if relationship < -0.3:
                    # 来自非结盟权力的敌对行动
                    sender = next(
                        (gp for gp in great_powers if gp.get("agent_id") == sender_id),
                        None
                    )
                    if sender:
                        return SmallStateAction.COUNTER_RESPOND, (
                            f"响应来自 {sender.get('name', '未知')} 的敌对行动。"
                            f"实施反制措施以保护国家利益。"
                        )

        # 默认：NEUTRAL_OBSERVE
        return SmallStateAction.NEUTRAL_OBSERVE, (
            f"保持中立观察姿态。"
            f"此时没有令人信服的结盟理由。"
        )

    def _is_hostile_action(
        self,
        event: Dict[str, Any],
        great_powers: List[Dict[str, Any]],
    ) -> bool:
        """
        检查事件是否代表敌对行动

        Args:
            event: 要检查的事件
            great_powers: 大国列表

        Returns:
            如果事件是敌对的则返回True
        """
        event_type = event.get("event_type", "").lower()
        hostile_actions = [
            "economic_sanction",
            "security_military",
            "military_escalation",
        ]

        return any(action in event_type for action in hostile_actions)

    def _update_stance_from_action(
        self,
        action_type: SmallStateAction,
        assessments: List[Dict[str, Any]],
    ) -> None:
        """
        根据选定的行动类型更新战略姿态

        Args:
            action_type: 选定的行动类型
            assessments: 大国评估
        """
        if action_type == SmallStateAction.ALIGN_FOLLOW:
            self.strategic_stance = StrategicStance.ALIGNED
            if assessments:
                best = max(assessments, key=lambda x: x["score"])
                self.aligned_with = best["agent_id"]
                self.set_relationship(best["agent_id"], 0.7)

        elif action_type == SmallStateAction.SIDE_SELECTION:
            self.strategic_stance = StrategicStance.ALIGNED
            if assessments:
                best = max(assessments, key=lambda x: x["score"])
                self.aligned_with = best["agent_id"]
                self.set_relationship(best["agent_id"], 0.6)

        elif action_type == SmallStateAction.DEFECT_SWITCH:
            self.strategic_stance = StrategicStance.SWING
            if assessments:
                best = max(assessments, key=lambda x: x["score"])
                self.aligned_with = best["agent_id"]
                # 减少与先前结盟的关系
                for agent_id in self.relations.keys():
                    if agent_id != self.agent_id and agent_id != best["agent_id"]:
                        current = self.get_relationship(agent_id)
                        self.set_relationship(agent_id, current - 0.2)

        elif action_type == SmallStateAction.NO_ALLIANCE_COALITION:
            self.strategic_stance = StrategicStance.NON_ALIGNED
            self.aligned_with = None

        elif action_type == SmallStateAction.MEDIATION:
            self.strategic_stance = StrategicStance.NEUTRAL
            self.aligned_with = None

        elif action_type == SmallStateAction.COUNTER_RESPOND:
            if self.aligned_with:
                self.strategic_stance = StrategicStance.ALIGNED
            else:
                self.strategic_stance = StrategicStance.NEUTRAL
        else:  # NEUTRAL_OBSERVE
            self.strategic_stance = StrategicStance.NEUTRAL
            # 保持现有结盟或设置为None
            pass

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        响应来自另一个代理的消息

        Args:
            sender_id: 发送消息的代理ID
            message: 消息内容和元数据
            context: 响应生成的附加上下文

        Returns:
            包含响应的字典
        """
        if context is None:
            context = {}

        # 根据结盟和关系确定响应
        relationship_score = self.get_relationship(sender_id)

        # 检查发送者是否为结盟大国
        is_aligned = self.aligned_with == sender_id

        message_type = message.get("type", "unknown")

        if is_aligned:
            # 对结盟大国的友好响应
            content = (
                f"我们感谢您发来的 {message_type}。"
                f"我们将支持您的倡议并相应合作。"
            )
            message_type_response = "support"
            relationship_adjustment = 0.05
        elif relationship_score > 0.3:
            # 友好但未结盟
            content = (
                f"我们以兴趣收到了您的 {message_type}。"
                f"我们将根据我们的国家利益来考虑它。"
            )
            message_type_response = "consider"
            relationship_adjustment = 0.02
        elif relationship_score < -0.3:
            # 敌对响应
            content = (
                f"我们收到了您的 {message_type}。"
                f"我们必须恭敬地拒绝，因为它与我们的利益冲突。"
            )
            message_type_response = "decline"
            relationship_adjustment = -0.05
        else:
            # 中立响应
            content = (
                f"我们收到了您的 {message_type}。"
                f"我们将评估它并适时做出回应。"
            )
            message_type_response = "acknowledge"
            relationship_adjustment = 0.0

        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": message_type_response,
            "aligned_with_sender": is_aligned,
            "relationship_score": relationship_score,
        }

        # 更新关系
        new = max(-1.0, min(1.0, relationship_score + relationship_adjustment))
        self.set_relationship(sender_id, new)

        # 在历史中记录响应
        self.add_history(
            "response",
            f"响应 {sender_id}",
            metadata={"response": response, "original_message": message},
        )

        return response

    def _assess_great_powers(
        self,
        great_powers: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        评估所有大国并计算吸引力得分

        Args:
            great_powers: 大国代理的字典列表
            context: 附加上下文

        Returns:
            包含得分的评估列表
        """
        assessments = []

        for gp in great_powers:
            gp_id = gp.get("agent_id")
            if gp_id == self.agent_id:
                continue  # 跳过自己

            leadership_type = gp.get("leadership_type", "unknown")
            name = gp.get("name", gp_id)

            # 来自领导类型偏好的基础得分
            leadership_score = self.leadership_preferences.get(leadership_type, 0) * 10

            # 来自最近行为的得分
            behavior_score = self._score_behavior(gp, leadership_type)

            # 来自能力的得分（小国偏好适度权力）
            capability_score = self._score_capability(gp)

            # 来自现有关系的得分
            relationship_score = self._score_relationship(gp_id)

            # 计算加权总分
            total_score = (
                leadership_score * self.weights["leadership_type"] +
                behavior_score * self.weights["behavior_score"] +
                capability_score * self.weights["capability"] +
                relationship_score * self.weights["relationship"]
            )

            assessments.append({
                "agent_id": gp_id,
                "name": name,
                "leadership_type": leadership_type,
                "leadership_score": leadership_score,
                "behavior_score": behavior_score,
                "capability_score": capability_score,
                "relationship_score": relationship_score,
                "score": total_score,
            })

        return assessments

    def _score_behavior(self, great_power: Dict[str, Any], leadership_type: str) -> float:
        """
        根据领导类型和最近行动对大国的行为进行评分

        Args:
            great_power: 大国代理字典
            leadership_type: 大国的领导类型

        Returns:
            行为得分（0-100）
        """
        # 来自领导类型道德特征的基础得分
        leadership_moral_scores = {
            "wangdao": 90,  # 最高道德行为
            "hegemon": 60,  # 中等道德行为
            "qiangquan": 30,  # 低道德行为
            "hunyong": 50,  # 混合道德行为
        }

        base_score = leadership_moral_scores.get(leadership_type, 50)

        # 如果可用则获取最近行为
        recent_behavior = great_power.get("recent_behavior", [])
        recent_actions = great_power.get("recent_actions", [])

        # 根据最近行动调整得分
        adjustment = 0

        for action in recent_actions[-5:]:  # 最近5个行动
            action_type = action.get("action_type", "").lower()

            # 正面行动
            if any(pos in action_type for pos in [
                "norm_proposal", "diplomatic_visit", "economic_aid"
            ]):
                adjustment += 5

            # 负面行动
            if any(neg in action_type for neg in [
                "economic_sanction", "military_aggression"
            ]):
                adjustment -= 10

        # 根据行为类型调整得分
        for behavior in recent_behavior[-3:]:  # 最近3个行为
            if behavior.get("moral", False):
                adjustment += 8
            elif behavior.get("coercive", False):
                adjustment -= 12
            elif behavior.get("cooperative", False):
                adjustment += 6

        return max(0, min(100, base_score + adjustment))

    def _score_capability(self, great_power: Dict[str, Any]]) -> float:
        """
        对大国的能力进行评分

        小国偏好足够强大提供安全但不过度主导的权力。

        Args:
            great_power: 大国代理字典

        Returns:
            能力得分（0-100）
        """
        capability_index = great_power.get("capability_index", 50)

        # 类似S形曲线：在中等权力水平时吸引力最高
        # 很高权力可能具有威胁性，很低则不足
        # 最佳范围：60-80
        if capability_index < 60:
            # 低于最优：线性增长
            return (capability_index / 60) * 80
        elif capability_index <= 80:
            # 最优范围：高得分
            return 100 - ((capability_index - 70) / 10) * 20
        else:
            # 高于最优：递减得分
            return max(50, 100 - (capability_index - 80) * 1.5)

    def _score_relationship(self, agent_id: str) -> float:
        """
        根据与代理的现有关系进行评分

        Args:
            agent_id: 代理ID

        Returns:
            关系得分（0-100）
        """
        # 关系是-1到1，转换为0-100
        current = self.get_relationship(agent_id)
        return (current + 1) * 50

    def _determine_best_alignment(
        self,
        assessments: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        确定最佳大国以结盟

        Args:
            assessments: 大国评估列表

        Returns:
            最佳评估（如果可用），否则返回None
        """
        if not assessments:
            return None

        # 找到得分最高的大国
        best = max(assessments, key=lambda x: x["score"])

        # 只有当它满足最低阈值时才返回
        if best["score"] >= self.alignment_threshold:
            return best

        return None

    def _calculate_risk_benefit_ratio(
        self,
        great_power_id: str,
        leadership_type: str,
        capability_index: float,
    ) -> float:
        """
        计算与大国结盟的风险-收益比

        Args:
            great_power_id: 大国ID
            leadership_type: 大国的领导类型
            capability_index: 大国的能力指数

        Returns:
            风险-收益比（越高=越有利）
        """
        # 获取预期收益和风险
        benefits = self.calculate_benefits(great_power_id, leadership_type)
        risks = self.calculate_risks(great_power_id, leadership_type)

        # 计算平均收益
        avg_benefit = sum(benefits.values()) / len(benefits) if benefits else 50

        # 计算平均风险
        avg_risk = sum(risks.values()) / len(risks) if risks else 50

        # 风险-收益比（收益由能力调整）
        ratio = (avg_benefit - avg_risk * 0.5) * (capability_index / 100)
        return max(0, min(100, ratio))

    def get_alignment_summary(self) -> Dict[str, Any]:
        """
        获取小国的结盟摘要

        Returns:
            包含结盟信息的字典
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "strategic_stance": self.strategic_stance.value,
            "aligned_with": self.aligned_with,
            "alignment_threshold": self.alignment_threshold,
            "previous_alignment_score": self.previous_alignment_score,
        }

    def update_alignment(
        self,
        great_power_id: Optional[str],
        new_stance: Optional[StrategicStance] = None,
    ) -> None:
        """
        更新与大国的结盟

        Args:
            great_power_id: 要结盟的大国ID（None表示中立）
            new_stance: 新战略姿态（如果未提供则从结盟推断）
        """
        self.aligned_with = great_power_id

        if great_power_id is None:
            self.strategic_stance = StrategicStance.NEUTRAL
        elif new_stance is not None:
            self.strategic_stance = new_stance
        else:
            self.strategic_stance = StrategicStance.ALIGNED

        # 记录变化
        self.add_history(
            "alignment_change",
            f"改变结盟为 {great_power_id or '中立'}",
            metadata={
                "previous_stance": self.strategic_stance.value,
                "new_stance": self.strategic_stance.value,
                "aligned_with": self.aligned_with,
            },
        )

    def calculate_benefits(
        self,
        great_power_id: str,
        leadership_type: str,
    ) -> Dict[str, float]:
        """
        计算与大国结盟的预期收益

        Args:
            great_power_id: 大国ID
            leadership_type: 大国的领导类型

        Returns:
            预期收益的字典
        """
        # 按领导类型的基础收益
        base_benefits = {
            "wangdao": {
                "security": 80,
                "economic": 75,
                "political_support": 85,
                "moral_legitimacy": 90,
            },
            "hegemon": {
                "security": 90,
                "economic": 70,
                "political_support": 65,
                "moral_legitimacy": 50,
            },
            "qiangquan": {
                "security": 60,
                "economic": 80,
                "political_support": 40,
                "moral_legitimacy": 20,
            },
            "hunyong": {
                "security": 50,
                "economic": 55,
                "political_support": 60,
                "moral_legitimacy": 65,
            },
        }

        return base_benefits.get(leadership_type, {})

    def calculate_risks(
        self,
        great_power_id: str,
        leadership_type: str,
    ) -> Dict[str, float]:
        """
        计算与大国结盟的预期风险

        Args:
            great_power_id: 大国ID
            leadership_type: 大国的领导类型

        Returns:
            预期风险的字典
        """
               # 按领导类型的基础风险
        base_risks = {
            "wangdao": {
                "entanglement": 20,
                "sovereignty_loss": 15,
                "moral_compromise": 10,
                "conflict_involvement": 25,
            },
            "hegemon": {
                "entanglement": 60,
                "sovereignty_loss": 50,
                "moral_compromise": 40,
                "conflict_involvement": 70,
            },
            "qiangquan": {
                "entanglement": 75,
                "sovereignty_loss": 80,
                "moral_compromise": 85,
                "conflict_involvement": 90,
            },
            "hunyong": {
                "entanglement": 25,
                "sovereignty_loss": 20,
                "moral_compromise": 15,
                "conflict_involvement": 30,
            },
        }

        return base_risks.get(leadership_type, {})
