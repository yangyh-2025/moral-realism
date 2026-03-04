"""
互动管理器模块

本模块实现InteractionManager类，用于：
- 协调代理之间的互动
- 管理模拟流程
- 维护互动历史记录
- 跟踪互动统计

核心功能：
- 注册/注销代理
- 执行基于决策的互动
- 管理直接和广播互动
- 更新代理关系
- 提供互动历史查询
- 支持联合国投票、同盟峰会、区域谈判等多边互动

核心类：
- InteractionManager: 互动管理器
- InteractionResult: 单次互动结果
- InteractionStep: 互动循环中的单个步骤
- InteractionLevel: 互动级别（双边、多边、体系）
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType


logger = logging.getLogger(__name__)


class InteractionLevel(Enum):
    """
    互动级别枚举

    定义模拟中不同层级的互动：
    1. BILATERAL (双边互动): 两个代理之间的直接互动
    2. MULTILATERAL (多边互动): 多个代理参与的互动（如投票）
    3. SYSTEMIC (体系互动): 涉及整个体系的互动
    """

    BILATERAL = "bilateral"  # 双边互动
    MULTILATERAL = "multilateral"  # 多边互动
    SYSTEMIC = "systemic"  # 体系互动


@dataclass
class InteractionResult:
    """
    单次互动结果类

    记录代理之间单次结果。

    属性说明：
    - interaction_id: 互动唯一标识符
    - from_agent_id: 发起互动的代理ID
    - to_agent_id: 接收互动的代理ID
    - interaction_type: 互动类型
    - action: 采取的行动内容
    - response: 接收方的响应（可选）
    - timestamp: 互动时间戳
    - success: 互动是否成功
    - error_message: 错误信息（如果有）
    - metadata: 附加元数据
    """

    interaction_id: str
    from_agent_id: str
    to_agent_id: str
    interaction_type: str
    action: Dict[str, Any]
    response: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        将互动结果转换为字典格式

        Returns:
            Dict[str, Any]: 包含互动结果的字典
        """
        return {
            "interaction_id": self.interaction_id,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "interaction_type": self.interaction_type,
            "action": self.action,
            "response": self.response,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class InteractionStep:
    """
    互动循环步骤类

    表示互动循环中的单个步骤。

    属性说明：
    - step_id: 步骤唯一标识符
    - round: 所在的回合数
    - timestamp: 步骤时间戳
    - decisions: 该步骤中的所有决策
    - interactions: 该步骤中的所有互动结果
    - step_metadata: 步骤附加元数据
    """

    step_id: str
    round: int
    timestamp: datetime = field(default_factory=datetime.now)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    interactions: List[InteractionResult] = field(default_factory=list)
    step_metadata: Dict[str] = Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        将互动步骤转换为字典格式

        Returns:
            Dict[str, Any]: 包含步骤信息的字典
        """
        return {
            "step_id": self.step_id,
            "round": self.round,
            "timestamp": self.timestamp.isoformat(),
            "decisions": self.decisions,
            "interactions": [i.to_dict() for i in self.interactions],
            "step_metadata": self.step_metadata,
        }


class InteractionManager:
    """
    互动管理器类

    管理模拟过程中代理之间的互动。
    协调代理决策、互动执行和响应收集，同时维护历史记录和统计信息。

    核心功能：
    - 代理注册/注销管理
    - 双边互动执行
    - 广播互动（向所有其他代理）
    - 多边互动支持（联合国投票、同盟峰会、区域谈判）
    - 关系动态更新
    - 统计信息跟踪
    """

    def __init__(
        self,
        max_history_length: int = 1000,
        enable_logging: bool = True,
    ) -> None:
        """
        初始化互动管理器

        Args:
            max_history_length: 保留的最大历史记录数
            enable_logging: 是否启用详细日志记录
        """
        self._agents: Dict[str, Agent] = {}  # 注册的代理字典
        self._interaction_history: List[InteractionResult] = []  # 互动历史记录
        self._step_history: List[InteractionStep] = []  # 步骤历史记录
        self._current_round: int = 0  # 当前回合计数

        self._max_history_length = max_history_length
        self._enable_logging = enable_logging

        self._interaction_counter: int = 0  # 互动ID计数器

        # 统计信息
        self._stats: Dict[str, Any] = {
            "total_interactions": 0,  # 总互动次数
            "successful_interactions": 0,  # 成功互动次数
            "failed_interactions": 0,  # 失败互动次数
            "interaction_counts_by_type": {},  # 按类型统计
            "interaction_counts_by_agent": {},  # 按代理统计
        }

    def register_agent(self, agent: Agent) -> None:
        """
        注册代理到互动管理器

        Args:
            agent: 要注册的代理对象
        """
        self._agents[agent.agent_id] = agent
        logger.info(f"注册代理: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str) -> bool:
        """
        从互动管理器中注销代理

        Args:
            agent_id: 要注销的代理ID

        Returns:
            如果代理被注销返回True，如果未找到返回False
        """
        if agent_id in self._agents:
            agent = self._agents.pop(agent_id)
            logger.info(f"注销代理: {agent.name} ({agent_id})")
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        根据ID获取注册的代理

        Args:
            agent_id: 代理ID

        Returns:
            如果找到返回代理，否则返回None
        """
        return self._agents.get(agent_id)

    def get_all_agents(self) -> List[Agent]:
        """
        获取所有注册的代理

        Returns:
            所有注册代理的列表
        """
        return list(self._agents.values())

    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """
        获取指定类型的所有代理

        Args:
            agent_type: 要检索的代理类型

        Returns:
            指定类型的代理列表
        """
        return [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type
        ]

    def execute_interactions(
        self,
        decisions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[InteractionResult]:
        """
        基于代理决策执行互动

        Args:
            decisions: 代理做出的决策列表
            context: 互动执行的附加上下文

        Returns:
            互动结果列表
        """
        if context is None:
            context = {}

        results = []
        step_id = f"step_{self._current_round}"

        # 创建新步骤
        step = InteractionStep(
            step_id=step_id,
            round=self._current_round,
            decisions=decisions,
        )

        # 处理每个决策
        for decision in decisions:
            result = self._process_decision(decision, context)
            if result:
                results.append(result)
                step.interactions.append(result)

        # 更新统计
        self._update_statistics(results)

        # 存储步骤
        self._step_history.append(step)

        # 推进回合
        self._current_round += 1

        if self._enable_logging:
            logger.info(
                f"在回合 {self._current_round - 1} 中执行了 {len(results)} 次互动"
            )

        return results

    def _process_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[InteractionResult]:
        """
        将单个代理决策处理为互动

        Args:
            decision: 代理的决策
            context: 附加上下文

        Returns:
            如果适用返回互动结果，否则返回None
        """
        from_agent_id = decision.get("agent_id")
        action_type = decision.get("action_type", "no_action")
        target_agent_id = decision.get("target_agent_id")

        # 跳过无行动决策
        if action_type == "no_action":
            return None

        from_agent = self._agents.get(from_agent_id)
        if not from_agent:
            return InteractionResult(
                interaction_id=self._generate_interaction_id(),
                from_agent_id=from_agent_id,
                to_agent_id=target_agent_id or "unknown",
                interaction_type=action_type,
                action=decision,
                success=False,
                error_message=f"源代理 {from_agent_id} 未找到",
            )

        # 确定目标代理
        if target_agent_id:
            to_agent = self._agents.get(target_agent_id)
            if not to_agent:
                return InteractionResult(
                    interaction_id=self._generate_interaction_id(),
                    from_agent_id=from_agent_id,
                    to_agent_id=target_agent_id,
                    interaction_type=action_type,
                    action=decision,
                    success=False,
                    error_message=f"目标代理 {target_agent_id} 未找到",
                )
        else:
            # 无特定目标，向所有其他代理广播
            to_agent = None

        # 创建互动结果
        result = InteractionResult(
            interaction_id=self._generate_interaction_id(),
            from_agent_id=from_agent_id,
            to_agent_id=target_agent_id or "broadcast",
            interaction_type=action_type,
            action=decision,
        )

        # 执行互动
        try:
            if to_agent:
                # 直接互动
                response = self._execute_direct_interaction(
                    from_agent, to_agent, decision, context
                )
            else:
                # 广播互动
                response = self._execute_broadcast_interaction(
                    from_agent, decision, context
                )

            result.response = response
            result.success = True

            # 存储到历史
            self._add_to_history(result)

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(
                f"执行来自 {from_agent_id} 的互动时出错: {e}"
            )

        return result

    def _execute_direct_interaction(
        self,
        from_agent: Agent,
        to_agent: Agent,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行两个代理之间的直接互动

        Args:
            from_agent: 发起代理
            to_agent: 目标代理
            decision: 行动决策
            context: 附加上下文

        Returns:
            来自目标代理的响应
        """
        # 创建消息
        message = {
            "type": decision.get("action_type", "unknown"),
            "content": decision.get("rationale", ""),
            "from_agent_id": from_agent.agent_id,
            "from_agent_name": from_agent.name,
            "from_agent_type": from_agent.agent_type.value,
            "priority": decision.get("priority", "medium"),
            "resource_allocation": decision.get("resource_allocation", 50),
        }

        # 添加代理信息到上下文
        interaction_context = {
            **context,
            "agents": {
                agent.agent_id: {
                    "name": agent.name,
                    "agent_type": agent.agent_type.value,
                    "leadership_type": agent.leadership_type.value,
                }
                for agent in self._agents.values()
            },
        }

        # 获取响应
        response = to_agent.respond(
            from_agent.agent_id,
            message,
            interaction_context,
        )

        # 更新关系
        self._update_relationships(from_agent, to_agent, decision, response)

        return response

    def _execute_broadcast_interaction(
        self,
        from_agent: Agent,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        执行向所有其他代理的广播互动

        Args:
            from_agent: 发起代理
            decision: 行动决策
            context: 附加上下文

        Returns:
            来自所有目标代理的聚合响应
        """
        responses = {}

        for target_agent in self._agents.values():
            if target_agent.agent_id == from_agent.agent_id:
                continue

            try:
                response = self._execute_direct_interaction(
                    from_agent, target_agent, decision, context
                )
                responses[target_agent.agent_id] = response
            except Exception as e:
                logger.error(
                    f"向 {target_agent.agent_id} 广播时出错: {e}"
                )
                responses[target_agent.agent_id] = {
                    "error": str(e),
                    "success": False,
                }

        return {
            "type": "broadcast_response",
            "responses": responses,
            "total_recipients": len(responses),
        }

    def _update_relationships(
        self,
        from_agent: Agent,
        to_agent: Agent,
        decision: Dict[str, Any],
        response: Dict[str, Any],
    ) -> None:
        """
        基于互动更新代理关系

        Args:
            from_agent: 发起代理
            to_agent: 目标代理
            decision: 行动决策
            response: 接收到的响应
        """
        action_type = decision.get("action_type", "")

        # 确定关系调整
        adjustment = 0.0

        # 正面行动
        if any(pos in action_type for pos in [
            "diplomatic_visit", "diplomatic_alliance",
            "economic_aid", "norm_proposal", "norm_reform",
        ]):
            adjustment = 0.1

        # 负面行动
        elif any(neg in action_type for neg in [
            "economic_sanction", "military",
        ]):
            adjustment = from_agent.leadership_type.value == -0.15

        # 根据响应内容调整
        if response.get("message_type") == "support":
            adjustment += 0.05
        elif response.get("message_type") == "decline":
            adjustment -= 0.1

        # 应用调整（限制在-1到1之间）
        current = from_agent.get_relationship(to_agent.agent_id)
        new_score = max(-1.0, min(1.0, current + adjustment))
        from_agent.set_relationship(to_agent.agent_id, new_score)

        # 镜像关系（简化版）
        target_current = to_agent.get_relationship(from_agent.agent_id)
        target_new = max(-1.0, min(1.0, target_current + adjustment * 0.5))
        to_agent.set_relationship(from_agent.agent_id, target_new)

    def _update_statistics(self, results: List[InteractionResult]) -> None:
        """
        更新互动统计

        Args:
            results: 互动结果列表
        """
        self._stats["total_interactions"] += len(results)

        for result in results:
            if result.success:
                self._stats["successful_interactions"] += 1
            else:
                self._stats["failed_interactions"] += 1

            # 按类型统计
            interaction_type = result.interaction_type
            type_counts = self._stats["interaction_counts_by_type"]
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1

            # 按代理统计
            agent_counts = self._stats["interaction_counts_by_agent"]
            agent_counts[result.from_agent_id] = (
                agent_counts.get(result.from_agent_id, 0) + 1
            )

    def _add_to_history(self, result: InteractionResult) -> None:
        """
        将互动结果添加到历史

        Args:
            result: 要添加的互动结果
        """
        self._interaction_history.append(result)

        # 维护最大历史长度
        if len(self._interaction_history) > self._max_history_length:
            self._interaction_history = self._interaction_history[
                -self._max_history_length:
            ]

    def _generate_interaction_id(self) -> str:
        """生成唯一的互动ID"""
        self._interaction_counter += 1
        return f"interaction_{self._interaction_counter}_{self._current_round}"

    def get_interaction_history(
        self,
        limit: Optional[int] = None,
        agent_id: Optional[str] = None,
        interaction_type: Optional[str] = None,
    ) -> List[InteractionResult]:
        """
        获取互动历史，支持可选过滤

        Args:
            limit: 返回的最大结果数
            agent_id: 按特定代理ID过滤
            interaction_type: 按互动类型过滤

        Returns:
            过滤后的互动结果列表
        """
        history = self._interaction_history

        # 按代理过滤
        if agent_id:
            history = [
                r for r in history
                if r.from_agent_id == agent_id or r.to_agent_id == agent_id
            ]

        # 按类型过滤
        if interaction_type:
            history = [
                r for r in history
                if r.interaction_type == interaction_type
            ]

        # 应用限制
        if limit:
            history = history[-limit:]

        return history

    def get_step_history(
        self,
        limit: Optional[int] = None,
    ) -> List[InteractionStep]:
        """
        获取步骤历史

        Args:
            limit: 返回的最大步骤数

        Returns:
            互动步骤列表
        """
        if limit:
            return self._step_history[-limit:]
        return self._step_history.copy()

    def get_interaction_summary(self) -> Dict[str, Any]:
        """
        获取关于互动的摘要统计

        Returns:
            包含互动统计的字典
        """
        return {
            **self._stats,
            "current_round": self._current_round,
            "registered_agents": len(self._agents),
            "history_length": len(self._interaction_history),
            "success_rate": (
                self._stats["successful_interactions"] / self._stats["total_interactions"]
                if self._stats["total_interactions"] > 0
                else 0.0
            ),
        }

    def get_agent_interactions(
        self,
        agent_id: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        获取涉及特定代理的互动

        Args:
            agent_id: 代理ID
            limit: 最大结果数

        Returns:
            包含代理互动统计和历史的字典
        """
        interactions = self.get_interaction_history(
            limit=limit,
            agent_id=agent_id,
        )

        # 计算统计
        sent = [i for i in interactions if i.from_agent_id == agent_id]
        received = [i for i in interactions if i.to_agent_id == agent_id]

        return {
            "agent_id": agent_id,
            "total_interactions": len(interactions),
            "sent": len(sent),
            "received": len(received),
            "successful": sum(1 for i in interactions if i.success),
            "by_type": {
                i_type: sum(1 for i in interactions if i.interaction_type == i_type)
                for i_type in set(i.interaction_type for i in interactions)
            },
            "recent_interactions": [i.to_dict() for i in interactions[-5:]],
        }

    def reset_round(self) -> None:
        """将当前回合计数器重置为零"""
        self._current_round = 0
        logger.info("将回合计数器重置为 0")

    def clear_history(self) -> None:
        """清除所有互动历史"""
        self._interaction_history.clear()
        self._step_history.clear()
        self._interaction_counter = 0
        logger.info("清除互动历史")

    def reset_statistics(self) -> None:
        """重置互动统计"""
        self._stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "interaction_counts_by_type": {},
            "interaction_counts_by_agent": {},
        }
        logger.info("重置互动统计")

    # 多边和体系互动方法

    def execute_multilateral_interaction(
        self,
        interaction_type: str,
        participants: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[InteractionResult]:
        """
        执行多个代理之间的多边互动

        支持联合国投票、同盟峰会和区域组织谈判。

        Args:
            interaction_type: 多边互动类型
            participants: 参与的代理ID列表
            context: 互动的附加上下文

        Returns:
            来自所有参与者的互动结果列表
        """
        if context is None:
            context = {}

        results = []
        step_id = f"multilateral_step_{self._current_round}"

        # 处理不同类型的多边互动
        if interaction_type == "un_voting":
            return self._execute_un_voting(participants, context)
        elif interaction_type == "alliance_summit":
            return self._execute_alliance_summit(participants, context)
        elif interaction_type == "regional_negotiation":
            return self._execute_regional_negotiation(participants, context)
        else:
            # 通用多边互动
            return self._execute_generic_multilateral(
                interaction_type, participants, context
            )

    def _execute_un_voting(
        self,
        participants: List[str],
        context: Dict[str, Any],
    ) -> List[InteractionResult]:
        """
        模拟联合国投票

        领导类型影响投票行为：
        - 道义型(Wangdao): 支持人道主义决议
        - 霸权型(Hegemon): 可能使用否决权
        - 强权型(Qiangquan): 基于国家利益投票
        - 混合型(Hunyong): 倾向于弃权或支持共识

        Args:
            participants: 参与者代理ID列表
            context: 投票上下文，包括决议类型

        Returns:
            投票互动结果列表
        """
        results = []
        resolution_type = context.get("resolution_type", "general")
        resolution_text = context.get("resolution_text", "")
        is_security_council = context.get("is_security_council", False)

        votes = {"support": [], "oppose": [], "abstain": [], "veto": []}

        for agent_id in participants:
            agent = self._agents.get(agent_id)
            if not agent or agent.agent_type != AgentType.GREAT_POWER:
                continue

            # 根据领 导类型确定投票
            vote = self._determine_un_vote(agent, resolution_type, context)
            votes[vote].append(agent_id)

            # 创建互动结果
            result = InteractionResult(
                interaction_id=self._generate_interaction_id(),
                from_agent_id=agent_id,
                "to_agent_id": "un_assembly",
                interaction_type="un_voting",
                action={
                    "vote": vote,
                    "resolution_type": resolution_type,
                    "resolution_text": resolution_text,
                    "leadership_type": agent.leadership_type.value,
                },
                response={
                    "vote_accepted": vote in ["support", "abstain"],
                    "resolution": resolution_type,
                },
                metadata={
                    "is_security_council": is_security_council,
                    "leadership_type": agent.leadership_type.value,
                },
            )

            results.append(result)
            self._add_to_history(result)

        # 检查决议是否通过
        total_votes = len(votes["support"]) + len(votes["oppose"]) + len(votes["abstain"])
        support_ratio = len(votes["support"]) / total_votes if total_votes > 0 else 0
        passed = support_ratio >= 0.67 or (is_security_council and not votes["veto"])

        if self._enable_logging:
            logger.info(
                f"联合国投票: {len(votes['support'])} 票成, "
                f"{len(votes['oppose'])} 反对, "
                f"{len(votes['abstain'])} 弃权, "
                f"{len(votes['veto'])} 否决. "
                f"决议 {'通过' if passed else '未通过'}."
            )

        return results

    def _determine_un_vote(
        self,
        agent: Agent,
        resolution_type: str,
        context: Dict[str, Any],
    ) -> str:
        """
        确定代理如何在联合国投票

        Args:
            agent: 投票代理
            resolution_type: 决议类型
            context: 附加上下文

        Returns:
            投票类型: "support", "opose", "abstain", 或 "veto"
        """
        if not agent.leadership_profile:
            return "abstain"

        leadership_type = agent.leadership_profile.leadership_type.value
        moral_standard = agent.leadership_profile.moral_standard

        # 道义型: 支持人道主义，反对侵略
        if leadership_type == "wangdao":
            if any(type_ in resolution_type for type_ in ["humanitarian", "peace", "development"]):
                return "support"
            elif any(type_ in resolution_type for type_ in ["sanctions", "use_force"]):
                return "oppose"
            else:
                return "support" if moral_standard > 0.7 else "abstain"

        # 霸权型: 可能否决，支持自身利益
        elif leadership_type == "hegemon":
            is_security_council = context.get("is_security_council", False)
            affects_interests = context.get("affects_hegemon_interests", False)

            if is_security_council and affects_interests:
                return "veto"
            elif affects_interests:
                return "oppose"
            else:
                return "support"

        # 强权型: 纯利益导向
        elif leadership_type == "qiangquan":
            affects_interests = context.get("affects_agent_interests", {}).get(agent.agent_id, False)
            return "oppose" if affects_interests else "abstain"

        # 混合型: 倾向于跟随共识
        elif leadership_type == "hunyong":
            if moral_standard > 0.5:
                return "support"
            else:
                return "abstain"

        return "abstain"

    def _execute_alliance_summit(
        self,
        participants: List[str],
        context: Dict[str, Any],
    ) -> List[InteractionResult]:
        """
        模拟同盟峰会协调

        Args:
            participants: 参与者代理ID列表
            context: 峰会上下文，包括议程

        Returns:
            互动结果列表
        """
        results = []
        agenda = context.get("agenda", "general coordination")

        # 识别同盟结构
        alliances = self._identify_alliance_groups(participants)

        for alliance_name, alliance_members in alliances.items():
            # 创建联合声明结果
            for agent_id in alliance_members:
                agent = self._agents.get(agent_id)
                if not agent:
                    continue

                result = InteractionResult(
                    interaction_id=self._generate_interaction_id(),
                    from_agent_id=agent_id,
                    to_agent_id=f"alliance_{alliance_name}",
                    interaction_type="alliance_summit",
                    action={
                        "agenda_item": agenda,
                        "action": "participate",
                        "leadership_type": agent.leadership_type.value,
                    },
                    response={
                        "summit_outcome": "joint_declaration",
                        "consensus": self._check_summit_consensus(alliance_members, context),
                    },
                    metadata={
                        "alliance": alliance_name,
                        "members": alliance_members,
                    },
                )

                results.append(result)
                self._add_to_history(result)

        if self._enable_logging:
            logger.info(f"同盟峰会完成，有 {len(results)} 个参与者")

        return results

    def _execute_regional_negotiation(
        self,
        participants: List[str],
        context: Dict[str, Any],
    ) -> List[InteractionResult]:
        """
        模拟区域组织谈判

        Args:
            participants: 参与者代理ID列表
            context: 谈判上下文

        Returns:
            互动结果列表
        """
        results = []
        issue = context.get("issue", "trade")

        for agent_id in participants:
            agent = self._agents.get(agent_id)
            if not agent:
                continue

            # 确定谈判立场
            position = self._determine_negotiation_position(agent, issue, context)

            result = InteractionResult(
                interaction_id=self._generate_interaction_id(),
                from_agent_id=agent_id,
                to_agent_id="regional_organization",
                interaction_type="regional_negotiation",
                action={
                    "position": position,
                    "issue": issue,
                    "leadership_type": agent.leadership_type.value,
                },
                response={
                    "negotiation_progress": "ongoing",
                    "issue": issue,
                },
                metadata={
                    "participants": participants,
                },
            )

            results.append(result)
            self._add_to_history(result)

        return results

    def _execute_generic_multilateral(
        self,
        interaction_type: str,
        participants: List[str],
        context: Dict[str, Any],
    ) -> List[InteractionResult]:
        """
        执行通用多边互动

        Args:
            interaction_type: 互动类型
            participants: 参与者代理ID列表
            context: 附加上下文

        Returns:
            互动结果列表
        """
        results = []

        for agent_id in participants:
            agent = self._agents.get(agent_id)
            if not agent:
                continue

            result = InteractionResult(
                interaction_id=self._generate_interaction_id(),
                from_agent_id=agent_id,
                to_agent_id="multilateral_group",
                interaction_type=interaction_type,
                action={
                    "interaction_type": interaction_type,
                    "participating": True,
                },
                response={
                    "acknowledged": True,
                },
                metadata={
                    "participants": participants,
                },
            )

            results.append(result)
            self._add_to_history(result)

        return results

    def _identify_alliance_groups(
        self,
        participants: List[str],
    ) -> Dict[str, List[str]]:
        """
        根据关系识别参与者中的同盟组

        Args:
            participants: 代理ID列表

        Returns:
            将同盟名称映射到成员列表的字典
        """
        alliances = {"alliance_1": [], "alliance_2": []}

        # 基于第一个代理的关系进行简单分组
        if participants:
            first_agent = self._agents.get(participants[0])
            if first_agent:
                # 按关系强度对代理进行分组
                for agent_id in participants:
                    rel_score = first_agent.get_relationship(agent_id)
                    if rel_score > 0.3:
                        alliances["alliance_1"].append(agent_id)
                    elif rel_score < -0.3:
                        alliances["alliance_2"].append(agent_id)
                    else:
                        # 默认加入alliance_1
                        if not alliances["alliance_2"]:
                            alliances["alliance_1"] = participants.copy()

        return alliances

    def _check_summit_consensus(
        self,
        members: List[str],
        context: Dict[str, Any],
    ) -> bool:
        """
        检查峰会是否在成员间达成共识

        Args:
            members: 同盟成员列表
            context: 峰会上下文

        Returns:
            如果达成共识返回True
        """
        if len(members) < 2:
            return True

        # 检查领 导类型兼容性
        leadership_types = []
        for agent_id in members:
            agent = self._agents.get(agent_id)
            if agent and agent.leadership_profile:
                leadership_types.append(agent.leadership_profile.leadership_type.value)

        # 如果领 导类型相似则高度共识
        unique_types = set(leadership_types)
        return len(unique_types) <= 2

    def _determine_negotiation_position(
        self,
        agent: Agent,
        issue: str,
        context: Dict[str, Any],
    ) -> str:
        """
        根据领 导类型确定谈判立场

        Args:
            agent: 谈判代理
            issue: 正在谈判的议题
            context: 附加上下文

        Returns:
            立场: "supportive", "moderate", "resistant", 或 "opposed"
        """
        if not agent.leadership_profile:
            return "moderate"

        leadership_type = agent.leadership_profile.leadership_type.value

        # 道义型: 支持合作解决方案
        if leadership_type == "wangdao":
            return "supportive"

        # 霸权型: 中等到抵制
        elif leadership_type == "hegemon":
            return "resistant"

        # 强权型: 对约束持反对态度
        elif leadership_type == "qiangquan":
            return "opposed"

        # 混合型: 中立
        elif leadership_type == "hunyong":
            return "moderate"

        return "moderate"
