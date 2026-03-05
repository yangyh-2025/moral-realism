"""
道义现实主义ABM系统的大国代理实现

本模块实现GreatPowerAgent类，使用基于LLM的
决策制定，由领导类型特征驱动。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability, get_strategic_interests
from src.core.llm_engine import LLMEngine, LLMConfig
from src.prompts.leadership_prompts import (
    GreatPowerPromptBuilder,
    ActionType,
)


logger = logging.getLogger(__name__)


@dataclass
class Commitment:
    """表示大国做出的承诺"""

    commitment_id: str  # 承诺ID
    description: str  # 承诺描述
    target_agent_id: Optional[str] = None  # 目标代理ID
    action_type: Optional[str] = None  # 行动类型
    start_round: int = 0  # 开始回合
    end_round: Optional[int] = None  # 结束回合（None表示无限期）
    is_active: bool = True  # 是否活跃
    fulfillment: float = 0.0  # 履行程度（0-1刻度）


@dataclass
class GreatPowerAgent(Agent):
    """
    大国代理类

    由LLM和领导类型驱动的大国代理。

    该代理使用LLM做出反映其领导类型
    （道义型、霸权型、强权型或昏庸型）的决策，
    并将其与能力水平作为常量自变量结合。
    """

    # 用于决策制定的LLM引擎
    llm_engine: Optional[LLMEngine] = None  # LLM引擎
    prompt_builder: GreatPowerPromptBuilder = field(default_factory=GreatPowerPromptBuilder)  # 提示词构建器

    # 承诺管理
    commitments: List[Commitment] = field(default_factory=list)  # 承诺列表
    current_round: int = 0  # 当前回合数

    def __post_init__(self) -> None:
        """数据类初始化后的处理"""
        # 设置代理类型
        self.agent_type = AgentType.GREAT_POWER

        # 如果未设置则初始化领导配置文件
        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        # 如果未设置则初始化能力
        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        # 使用默认配置初始化LLM引擎
        if self.llm_engine is None:
            try:
                self.llm_engine = LLMEngine()
            except ValueError as e:
                logger.warning(f"无法初始化LLM引擎: {e}")
                self.llm_engine = None

        # 初始化与自己的关系
        self.relations[self.agent_id] = 1.0

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        使用LLM驱动的决策制定做出决策

        Args:
            situation: 当前情况描述
            available_actions: 代理可用的行动列表
            context: 决策制定的附加上下文

        Returns:
            包含决策和理由的字典
        """
        if context is None:
            context = {}

        # 准备包含所需信息的上下文
        context["situation"] = situation
        context["available_actions"] = available_actions

        # 检查LLM是否可用
        if self.llm_engine is None:
            return self._fallback_decision(available_actions, context)

        try:
            # 构建系统提示词
            function_definitions = self.prompt_builder.get_function_definitions()
            system_prompt = self.prompt_builder.build_system_prompt(
                self, function_definitions
            )

            # �用户建提示词
            user_prompt = self.prompt_builder.build_user_prompt(self, context)

            # 调用LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            response = self.llm_engine.function_call(
                messages=messages,
                functions=function_definitions,
                temperature=0.7,  # 较低温度以获得更一致的决策
            )

            # 解析函数调用结果
            function_call = response.get("function_call")
            decision = self.prompt_builder.parse_function_call(function_call)

            # 验证决策
            decision = self._validate_decision(decision)

            # 添加元数据
            decision["agent_id"] = self.agent_id
            decision["leadership_type"] = self.leadership_type.value
            decision["round"] = self.current_round
            decision["llm_usage"] = {
                "model": response.get("model"),
                "finish_reason": response.get("finish_reason"),
                "usage": response.get("usage"),
            }

            # 根据决策更新承诺
            if decision["action_type"] != "no_action":
                self._update_commitments_from_decision(decision)

            # 在历史中记录决策
            self.add_history(
                "decision",
                f"决定采取行动: {decision['action_type']}",
                metadata={
                    "decision": decision,
                    "situation": situation,
                },
            )

            logger.info(
                f"{self.name} 决定采取行动: {decision['action_type']}，"
                f"理由: {decision['rationale'][:100]}..."
            )

            return decision
        except Exception as e:
            logger.error(f"{self.name} 的LLM决策制定出错: {e}")
            return self._fallback_decision(available_actions, context)

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        响应来自另一个代理的消息

        Args:
            sender_id: 发送代理的ID
            message: 消息内容和元数据
            context: 响应生成的附加上下文

        Returns:
            包含响应的字典
        """
        if context is None:
            context = {}

        # 如果可用则获取发送者信息
        sender = context.get("agents", {}).get(sender_id, {"name": sender_id})

        # 检查LLM是否可用
        if self.llm_engine is None:
            return self._fallback_response(sender_id, message, context)

        try:
            # 构建响应提示词
            prompt = self.prompt_builder.build_response_prompt(
                self, sender, message, context
            )

            # 获取系统提示词
            system_prompt = f"""你是 {self.name}（{self.name_zh}），一个{self.leadership_profile.name_zh}大国。

根据你的领导特征响应以下消息。
"""

            # 调用LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.llm_engine.chat_completion(
                messages=messages,
                temperature=0.8,  # 较高温度以获得更多样的响应
            )

            content = response.get("content", "")
            message_type = message.get("type", "unknown")

            response_data = {
                "sender_id": self.agent_id,
                "receiver_id": sender_id,
                "content": content,
                "message_type": message_type,
                "leadership_type": self.leadership_type.value,
                "round": self.current_round,
            }

            # 在历史中记录响应
            self.add_history(
                "response",
                f"响应 {sender_id}: {content[:100]}...",
                metadata={
                    "response": response_data,
                    "original_message": message,
                },
            )

            # 根据互动更新关系
            self._update_relationship_from_interaction(sender_id, message, response_data)

            return response_data
        except Exception as e:
            logger.error(f"{self.name} 的LLM响应生成出错: {e}")
            return self._fallback_response(sender_id, message, context)

    def _validate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证决策是否符合领导配置文件约束

        Args:
            decision: 要验证的决策

        Returns:
            验证后的决策（可能被修改）
        """
        action_type = decision.get("action_type", "no_action")

        # 检查行动是否被禁止
        if self.leadership_profile:
            prohibited = self.leadership_profile.prohibited_actions

            # 检查精确匹配和部分匹配
            is_prohibited = any(
                action_type in prohibited or
                prohibited_item in action_type
                for prohibited_item in prohibited
            )

            if is_prohibited:
                logger.warning(
                    f"{self.name} 尝试禁止行动: {action_type}。"
                    f"回退到不采取行动。"
                )
                decision["action_type"] = "no_action"
                decision["rationale"] = (
                    f"原始行动 '{action_type}' 被领导类型禁止。"
                    "改为不采取行动。"
                )

        # 确保优先级有效
        if "priority" not in decision or decision["priority"] not in ["high", "medium", "low"]:
            decision["priority"] = "medium"

        # 确保资源分配有效
        if "resource_allocation" not in decision:
            decision["resource_allocation"] = 50
        else:
            decision["resource_allocation"] = max(0, min(100, decision["resource_allocation"]))

        return decision

    def _fallback_decision(
        self,
        available_actions: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        当LLM不可用时生成回退决策

        Args:
            available_actions: 可用行动列表
            context: 上下文信息

        Returns:
            回退决策
        """
        # 默认使用优先行动（如果可用）
        prioritized = (
            self.leadership_profile.prioritized_actions
            if self.leadership_profile
            else []
        )

        # 根据领导类型选择行动
        if self.leadership_type == LeadershipType.WANGDAO:
            action_type = ActionType.DIPLOMATIC_VISIT.value
            rationale = "作为道义型领导，优先外交参与"
        elif self.leadership_type == LeadershipType.HEGEMON:
            action_type = ActionType.SECURITY_ALLIANCE.value
            rationale = "通过加强同盟来维持霸权地位"
        elif self.leadership_type == LeadershipType.QIANGQUAN:
            action_type = ActionType.ECONOMIC_TRADE.value
            rationale = "最大化经济利益和权力"
        else:  # HUNYONG
            action_type = ActionType.NO_ACTION.value
            rationale = "通过不行动避免对抗"

        return {
            "agent_id": self.agent_id,
            "action_type": action_type,
            "target_agent_id": None,
            "rationale": rationale + "（回退决策- LLM不可用）",
            "moral_consideration": "回退决策",
            "resource_allocation": 50,
            "priority": "medium",
            "leadership_type": self.leadership_type.value,
            "round": self.current_round,
            "fallback": True,
        }

    def _fallback_response(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        当LLM不可用时生成回退响应

        Args:
            sender_id: 发送者ID
            message: 消息
            context: 上下文信息

        Returns:
            回退响应
        """
        content = f"感谢您的消息。我们将考虑您的提议。"

        if self.leadership_type == LeadershipType.WANGDAO:
            content = (
                "我们感谢您的消息，并将以对所有相关方都"
                "考虑的方式处理此事。"
            )
        elif self.leadership_type == LeadershipType.HEGEMON:
            content = (
                "我们已收到您的消息。我们的回应将由"
                "我们的战略利益和同盟承诺指导。"
            )
        elif self.leadership_type == LeadershipType.QIANGQUAN:
            content = (
                "我们已注意到您的消息。我们将根据"
                "我们的国家利益做出回应。"
            )

        return {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": message.get("type", "unknown"),
            "leadership_type": self.leadership_type.value,
            "round": self.current_round,
            "fallback": True,
        }

    def _update_commitments_from_decision(self, decision: Dict[str, Any]) -> None:
        """
        根据新决策更新承诺

        Args:
            decision: 要处理的决策
        """
        action_type = decision.get("action_type")

        # 为重要行动创建承诺
        if action_type in [
            ActionType.DIPLOMATIC_ALLIANCE.value,
            ActionType.SECURITY_ALLIANCE.value,
            ActionType.NORM_PROPOSAL.value,
        ]:
            commitment = Commitment(
                commitment_id=f"{self.agent_id}_{self.current_round}_{action_type}",
                description=decision.get("rationale", "")[:200],
                target_agent_id=decision.get("target_agent_id"),
                action_type=action_type,
                start_round=self.current_round,
                is_active=True,
            )
            self.commitments.append(commitment)

    def _update_relationship_from_interaction(
        self,
        sender_id: str,
        message: Dict[str, Any],
        response: Dict[str, Any],
    ) -> None:
        """
        根据互动更新关系

        Args:
            sender_id: 发送者ID
            message: 传入消息
            response: 发送的响应
        """
        # 简单逻辑：正面互动增加关系
        message_type = message.get("type", "unknown")

        # 默认的小正面调整
        adjustment = 0.05

        # 根据消息类型调整
        if "threat" in message_type.lower() or "sanction" in message_type.lower():
            adjustment = -0.1
        elif "cooperation" in message_type.lower() or "alliance" in message_type.lower():
            adjustment = 0.15

        current_score = self.get_relationship(sender_id)
        new_score = max(-1.0, min(1.0, current_score + adjustment))
        self.set_relationship(sender_id, new_score)

    def get_active_commitments(self) -> List[Commitment]:
        """
        获取所有当前活跃的承诺

        Returns:
            活跃承诺列表
        """
        return [c for c in self.commitments if c.is_active]

    def get_objective_interests(self) -> List[str]:
        """
        根据能力层级获取客观战略利益

        Returns:
            战略利益列表
        """
        if self.capability is None:
            return []

        tier = self.capability.get_tier()
        return get_strategic_interests(tier)

    def advance_round(self) -> None:
        """推进到下一个模拟回合"""
        self.current_round += 1

        # 根据回合更新承诺状态
        for commitment in self.commitments:
            if commitment.end_round is not None and self.current_round > commitment.end_round:
                commitment.is_active = False

    def get_decision_summary(self) -> Dict[str, Any]:
        """
        获取最近决策的摘要

        Returns:
            包含决策统计的字典
        """
        decisions = self.get_history("decision")

        if not decisions:
            return {"total_decisions": 0}

        action_counts = {}
        for entry in decisions:
            action = entry.metadata.get("decision", {}).get("action_type", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_decisions": len(decisions),
            "action_distribution": action_counts,
            "recent_decision": decisions[-1].metadata.get("decision") if decisions else None,
        }
