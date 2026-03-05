"""
道义现实主义ABM系统的回合执行器

本模块提供RoundExecutor类，用于执行单个模拟回合，
包含完整的流程：事件生成、分发、决策制定、互动执行、
规则应用和指标计算。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import logging

from src.models.agent import Agent
from src.environment.dynamic_environment import Event
from src.environment.rule_environment import MoralEvaluation


logger = logging.getLogger(__name__)


class RoundPhase(Enum):
    """回合执行的阶段"""

    PREPARATION = "preparation"  # 准备
    EVENT_GENERATION = "event_generation"  # 事件生成
    EVENT_DISTRIBUTION = "event_distribution"  # 事件分发
    AGENT_DECISION_MAKING = "agent_decision_making"  # 代理决策
    INTERACTION_EXECUTION = "interaction_execution"  # 互动执行
    RULE_APPLICATION = "rule_application"  # 规则应用
    METRICS_CALCULATION = "metrics_calculation"  # 指标计算
    SYSTEMIC_INTERACTION = "systemic_interaction"  # 体系互动
    CLEANUP = "cleanup"  # 清理


@dataclass
class RoundContext:
    """
    回合执行的上下文对象

    包含回合执行所需的所有引用和状态。
    """

    round_number: int  # 回合编号
    start_time: datetime  # 开始时间

    # 组件引用
    agents: Dict[str, Agent]  # 代理字典
    dynamic_environment: Any  # 动态环境
    rule_environment: Any  # 规则环境
    interaction_manager: Any  # 互动管理器
    behavior_selector: Any  # 行为选择器
    metrics_calculator: Any  # 指标计算器
    data_storage: Any  # 数据存储
    event_scheduler: Any  # 事件调度器

    # 回合特定状态
    events: List[Event] = field(default_factory=list)  # 事件列表
    agent_events: Dict[str, List[Event]] = field(default_factory=dict)  # 代理事件
    decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # 决策
    interactions: List[Any] = field(default_factory=list)  # 互动

    # 道德评估（来自规则环境）
    moral_evaluations: Dict[str, List[MoralEvaluation]] = field(default_factory=dict)  # 道德评估
    # 指标结果
    metrics: Dict[str, Any] = field(default_factory=dict)  # 指标

    # 体系互动结果
    systemic_results: Dict[str, Any] = field(default_factory=dict)  # 体系结果

    # 持久化设置
    persistence: bool = True  # 是否持久化
    decision_persistence: bool = True  # 决策持久化
    interaction_persistence: bool = True  # 互动持久化

    # 错误和警告
    errors: List[str] = field(default_factory=list)  # 错误列表
    warnings: List[str] = field(default_factory=list)  # 警告列表

    def add_error(self, message: str) -> None:
        """添加错误消息"""
        self.errors.append(message)
        logger.error(f"[回合 {self.round_number}] {message}")

    def add_warning(self, message: str) -> None:
        """添加警告消息"""
        self.warnings.append(message)
        logger.warning(f"[回合 {self.round_number}] {message}")


@dataclass
class RoundResult:
    """
    单次回合执行的结果

    包含回合执行的所有输出和指标。
    """

    round_number: int  # 回合编号
    start_time: datetime  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间
    duration_seconds: Optional[float] = None  # 持续时间（秒）

    # 阶段结果
    phases_completed: List[RoundPhase] = field(default_factory=list)  # 完成的阶段
    phases_failed: Dict[RoundPhase, str] = field(default_factory=dict)  # 失败的阶段

    # 事件结果
    events_generated: int = 0  # 生成的事件数
    events_processed: int = 0  # 处理的事件数

    # 决策结果
    decisions_count: int = 0  # 决策数量
    decisions_success_count: int = 0  # 成功的决策数

    # 互动结果
    interactions_executed: int = 0  # 执行的互动数
    interactions_success_count: int = 0  # 成功的互动数

    # 规则应用结果
    moral_evaluations: Dict[str, List[MoralEvaluation]] = field(default_factory=dict)  # 道德评估
    capability_changes_validated: int = 0  # 已验证的能力变化
    capability_changes_rejected: int = 0  # 已拒绝的能力变化

    # 指标结果
    metrics: Dict[str, Any] = field(default_factory=dict)  # 指标

    # 错误跟踪
    errors: List[str] = field(default_factory=list)  # 错误列表
    warnings: List[str] = field(default_factory=list)  # 警告列表

    # 状态标志
    is_complete: bool = False  # 是否完成
    is_successful: bool = False  # 是否成功

    def to_dict(self) -> Dict[str, Any]:
        """将结果转换为字典"""
        return {
            "round_number": self.round_number,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "phases_completed": [p.value for p in self.phases_completed],
            "phases_failed": {k.value: v for k, v in self.phases_failed.items()},
            "events_generated": self.events_generated,
            "events_processed": self.events_processed,
            "decisions_count": self.decisions_count,
            "decisions_success_count": self.decisions_success_count,
            "interactions_executed": self.interactions_executed,
            "interactions_success_count": self.interactions_success_count,
            "capability_changes_validated": self.capability_changes_validated,
            "capability_changes_rejected": self.capability_changes_rejected,
            "metrics_summary": self._get_metrics_summary(),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_complete": self.is_complete,
            "is_successful": self.is_successful,
        }

    def _get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        if not self.metrics:
            return {}
        return {
            "agent_count": self.metrics.get("agent_count", 0),
            "pattern_type": self.metrics.get("pattern_type", ""),
            "power_concentration": self.metrics.get("system_metrics", {}).get("power_concentration", 0),
            "order_stability": self.metrics.get("system_metrics", {}).get("order_stability", 0),
        }


class RoundExecutor:
    """
    回合执行器类

    执行单个模拟回合，实现完整的回合执行流程：
    1. 准备阶段 - 验证并创建上下文
    2. 事件生成 - 获取所有待处理事件
    3. 事件分发 - 将事件分发到受影响的代理
    4. 代理决策 - 收集所有代理的决策
    5. 互动执行 - 执行代理互动
    6. 规则应用 - 应用规则并验证变化
    7. 指标计算 - 计算并存储指标
    8. 清理 - 记录历史并更新统计
    """

    def __init__(
        self,
        enable_detailed_logging: bool = False,
    ) -> None:
        """
        初始化回合执行器

        Args:
            enable_detailed_logging: 启用详细日志
        """
        self._enable_detailed_logging = enable_detailed_logging
        self._phase_hooks: Dict[RoundPhase, List[callable]] = {}

    def execute_round(self, context: RoundContext) -> RoundResult:
        """
        执行完整的模拟回合

        Args:
            context: 包含所有组件引用的回合上下文

        Returns:
            带有执行结果的RoundResult
        """
        result = RoundResult(
            round_number=context.round_number,
            start_time=context.start_time,
        )

        logger.info(f"=== 开始第 {context.round_number} 回合 ===")

        # 执行各阶段
        try:
            self._phase_preparation(context, result)
            self._phase_event_generation(context, result)
            self._phase_event_distribution(context, result)
            self._phase_agent_decision_making(context, result)
            self._phase_interaction_execution(context, result)
            self._phase_systemic_interaction(context, result)
            self._phase_rule_application(context, result)
            self._phase_metrics_calculation(context, result)
            self._phase_cleanup(context, result)

            result.end_time = datetime.now()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.is_complete = True
            result.is_successful = len(result.errors) == 0

            logger.info(
                f"=== 第 {context.round_number} 回合已完成，"
                f"耗时 {result.duration_seconds:.3f}秒 ==="
            )

        except Exception as e:
            result.add_error(f"回合执行中发生致命错误: {e}")
            result.is_complete = False
            result.is_successful = False
            logger.error(f"第 {context.round_number} 回合失败: {e}", exc_info=True)

        return result

    def register_phase_hook(
        self,
        phase: RoundPhase,
        hook: callable,
    ) -> None:
        """
        注册阶段完成后调用的钩子

        Args:
            phase: 要挂钩的阶段
            hook: 阶段完成后调用的函数
        """
        if phase not in self._phase_hooks:
            self._phase_hooks[phase] = []
        self._phase_hooks[phase].append(hook)
        logger.debug(f"已为阶段 {phase.value} 注册钩子")

    # 阶段实现

    def _phase_preparation(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        准备阶段：验证上下文和状态

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.PREPARATION.value}")

        # 验证必要组件
        if not context.agents:
            result.add_error("没有为回合执行注册的代理")
            result.phases_failed[RoundPhase.PREPARATION] = "无代理"
            return

        if not context.dynamic_environment:
            result.add_error("未配置动态环境")
            result.phases_failed[RoundPhase.PREPARATION] = "无动态环境"
            return

        # 初始化代理事件映射
        agent_ids = list(context.agents.keys())
        for agent_id in agent_ids:
            context.agent_events[agent_id] = []

        if self._enable_detailed_logging:
            logger.debug(
                f"回合准备完成，包含 {len(agent_ids)} 个代理"
            )

        result.phases_completed.append(RoundPhase.PREPARATION)
        self._call_hooks(RoundPhase.PREPARATION, context, result)

    def _phase_event_generation(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        事件生成阶段：获取所有待处理事件

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.EVENT_GENERATION.value}")

        try:
            # 从动态环境获取事件
            agent_ids = list(context.agents.keys())
            context.events = context.dynamic_environment.get_all_pending_events(
                agent_ids
            )

            # 从调度器获取计划事件
            if context.event_scheduler:
                scheduled_events = context.event_scheduler.get_events_for_round(
                    context.round_number,
                    context={
                        "agents": context.agents,
                        "round": context.round_number,
                    },
                    execute_immediately=True,
                )
                context.events.extend(scheduled_events)

            result.events_generated = len(context.events)

            # 在动态环境中推进步数
            context.dynamic_environment.advance_step()

            if self._enable_detailed_logging:
                logger.debug(
                    f"为本回合生成了 {len(context.events)} 个事件"
                )

            result.phases_completed.append(RoundPhase.EVENT_GENERATION)
            self._call_hooks(RoundPhase.EVENT_GENERATION, context, result)
        except Exception as e:
            result.add_error(f"事件生成失败: {e}")
            result.phases_failed[RoundPhase.EVENT_GENERATION] = str(e)

    def _phase_event_distribution(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        事件分发阶段：将事件分发到受影响的代理

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.EVENT_DISTRIBUTION.value}")

        try:
            for event in context.events:
                # 记录事件
                context.dynamic_environment.record_event(event)

                # 分发到受影响的代理
                for agent_id in event.affected_agents:
                    if agent_id in context.agent_events:
                        context.agent_events[agent_id].append(event)
                    else:
                        context.add_warning(
                            f"事件 '{event.event_id}' 影响了未知代理 '{agent_id}'"
                        )

            result.events_processed = len(context.events)

            if self._enable_detailed_logging:
                for agent_id, events in context.agent_events.items():
                    logger.debug(
                        f"代理 {agent_id} 收到 {len(events)} 个事件"
                    )

            result.phases_completed.append(RoundPhase.EVENT_DISTRIBUTION)
            self._call_hooks(RoundPhase.EVENT_DISTRIBUTION, context, result)
        except Exception as e:
            result.add_error(f"事件分发失败: {e}")
            result.phases_failed[RoundPhase.EVENT_DISTRIBUTION] = str(e)

    def _phase_agent_decision_making(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        代理决策阶段：收集所有代理的决策

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.AGENT_DECISION_MAKING.value}")

        try:
            for agent_id, agent in context.agents.items():
                # 获取可用行为
                available_behaviors = []
                if context.behavior_selector:
                    available_behaviors = context.behavior_selector.get_available_behaviors(
                        agent,
                        situation={
                            "round": context.round_number,
                            "events": context.agent_events.get(agent_id, []),
                            "in_crisis": any(
                                e.event_type.value == "crisis"
                                for e in context.agent_events.get(agent_id, [])
                            ),
                        },
                    )

                # 构建情况上下文
                situation = {
                    "round": context.round_number,
                    "events": context.agent_events.get(agent_id, []),
                    "in_crisis": any(
                        e.event_type.value == "crisis"
                        for e in context.agent_events.get(agent_id, [])
                    ),
                }

                # 构建代理上下文
                agent_context = {
                    "agents": {
                        aid: a.get_summary()
                        for aid, a in context.agents.items()
                    },
                    "round": context.round_number,
                }

                # 获取决策
                try:
                    decision = agent.decide(situation, available_behaviors, agent_context)

                    # 添加回合信息到决策
                    decision["round"] = context.round_number
                    decision["agent_id"] = agent_id

                    context.decisions[agent_id] = decision
                    result.decisions_count += 1
                    result.decisions_success_count += 1

                except Exception as e:
                    result.add_error(
(
                        f"代理 {agent_id} 决策失败: {e}"
                    )
                    result.decisions_count += 1

            if self._enable_detailed_logging:
                logger.debug(f"收集了 {len(context.decisions)} 个决策")

            result.phases_completed.append(RoundPhase.AGENT_DECISION_MAKING)
            self._call_hooks(RoundPhase.AGENT_DECISION_MAKING, context, result)
        except Exception as e:
            result.add_error(f"代理决策阶段失败: {e}")
            result.phases_failed[RoundPhase.AGENT_DECISION_MAKING] = str(e)

    def _phase_interaction_execution(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        互动执行阶段：执行代理之间的互动

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.INTERACTION_EXECUTION.value}")

        try:
            # 将决策转换为互动格式
            decisions_list = list(context.decisions.values())

            # 执行互动
            if context.interaction_manager:
                context.interactions = context.interaction_manager.execute_interactions(
                    decisions_list,
                    context={
                        "round": context.round_number,
                        "agents": context.agents,
                    },
                )

                result.interactions_executed = len(context.interactions)
                result.interactions_success_count = sum(
                    1 for i in context.interactions
                    if getattr(i, "success", True)
                )

            if self._enable_detailed_logging:
                logger.debug(f"执行了 {len(context.interactions)} 次互动")

            result.phases_completed.append(RoundPhase.INTERACTION_EXECUTION)
            self._call_hooks(RoundPhase.INTERACTION_EXECUTION, context, result)
        except Exception as e:
            result.add_error(f"互动执行失败: {e}")
            result.phases_failed[RoundPhase.INTERACTION_EXECUTION] = str(e)

    def _phase_rule_application(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        规则应用阶段：应用规则并验证变化

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.RULE_APPLICATION.value}")

        try:
            if context.rule_environment:
                for agent_id, agent in context.agents.items():
                    # 获取代理行为用于道义评估
                    history = agent.get_history()
                    actions = []
                    for entry in history:
                        if entry.metadata:
                            actions.append({
                                "type": entry.event_type,
                                "content": entry.content,
                                **entry.metadata,
                            })

                    # 评估道德水平
                    interactions_for_agent = []
                    if context.interaction_manager:
                        interactions_for_agent = context.interaction_manager.get_interaction_history(
                            agent_id=agent_id,
                            limit=10,
                        )

                    moral_evals = context.rule_environment.evaluate_moral_level(
                        agent_id=agent_id,
                        actions=actions,
                        interactions=[
                            i.to_dict() if hasattr(i, "to_dict") else i
                            for i in interactions_for_agent
                        ],
 ],
                    )

                    context.moral_evaluations[agent_id] = moral_evals
                    result.moral_evaluations[agent_id] = moral_evals

                    # 验证能力变化（如果有）
                    if agent.capability:
                        old_capability = agent.capability.get_capability_index()
                        # 示例验证检查
                        is_valid, _ = context.rule_environment.validate_capability_change(
                            agent_id=agent_id,
                            old_capability=old_capability,
                            new_capability=old_capability + 5.0,  # 示例
                            context={"round": context.round_number},
                        )

                        if is_valid:
                            result.capability_changes_validated += 1
                        else:
                            result.capability_changes_rejected += 1

            if self._enable_detailed_logging:
                logger.debug(
                    f"对 {len(context.moral_evaluations)} 个代理应用了规则"
                )

            result.phases_completed.append(RoundPhase.RULE_APPLICATION)
            self._call_hooks(RoundPhase.RULE_APPLICATION, context, result)
        except Exception as e:
            result.add_error(f(f"规则应用失败: {e}")
            result.phases_failed[RoundPhase.RULE_APPLICATION] = str(e)

    def _phase_metrics_calculation(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        指标计算阶段：计算并存储指标

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.METRICS_CALCULATION.value}")

        try:
            if context.metrics_calculator:
                # 计算所有指标
                context.metrics = context.metrics_calculator.calculate_all_metrics(
                    agents=context.agents,
                    state={
                        "round": context.round_number,
                        "events": [e.to_dict() for e in context.events],
                    },
                    round_result={
                        "round": context.round_number,
                        "decisions": context.decisions,
                        "interactions": [
                            i.to_dict() if hasattr(i, "to_dict") else i
                            for i in context.interactions
                        ],
                    },
                )

                result.metrics = context.metrics.copy()

                # 如果配置了数据存储则保存指标
                if context.data_storage:
                    context.data_storage.save_metrics(
                        metrics_dict=context.metrics,
                        round_id=context.round_number,
                        metadata={
                            "round_result": result.to_dict(),
                        },
                    )

            if self._enable_detailed_logging:
                logger.debug("指标已计算并存储")

            result.phases_completed.append(RoundPhase.METRICS_CALCULATION)
            self._call_hooks(RoundPhase.METRICS_CALCULATION, context, result)
        except Exception as e:
            result.add_error(f"指标计算失败: {e}")
            result.phases_failed[RoundPhase.METRICS_CALCULATION] = str(e)

    def _phase_systemic_interaction(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        体系互动阶段：执行体系级互动

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.SYSTEMIC_INTERACTION.value}")

        try:
            if context.systemic_interaction:
                # 获取大国用于体系互动
                great_powers = [
                    agent_id for agent_id, agent in context.agents.items()
                    if hasattr(agent, 'agent_type') and agent.agent_type.value == "great_power"
                ]

                if great_powers:
                    # 塑造国际秩序
                    order_result = context.systemic_interaction.shape_international_order(
                        context.round_number
                    )

                    # 演化国际规范
                    norm_evolution = context.systemic_interaction.evolve_international_norms(
                        context.round_number
                    )

                    # 模拟价值观竞争
                    values_competition = context.systemic_interaction.simulate_values_competition(
                        context.round_number
                    )

                    # 在上下文中存储体系结果
                    context.systemic_results = {
                        "order_shape": order_result,
                        "norm_evolution": norm_evolution,
                        "values_competition": values_comatition,
                    }

                    # 如果启用了持久化则保存体系事件
                    if context.data_storage and context.persistence:
                        for event in context.systemic_interaction.get_systemic_events(limit=5):
                            context.data_storage.save_systemic_event(
                                event.to_dict() if hasattr(event, 'to_dict') else event,
                                context.round_number
                            )

            if self._enable_detailed_logging:
                logger.debug("体系互动阶段已完成")

            result.phases_completed.append(RoundPhase.SYSTEMIC_INTERACTION)
            self._call_hooks(RoundPhase.SYSTEMIC_INTERACTION, context, result)
        except Exception as e:
            result.add_error(f"体系互动失败: {e}")
            result.phases_failed[RoundPhase.SYSTEMIC_INTERACTION] = str(e)

    def _phase_cleanup(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        清理阶段：记录历史并更新统计

        Args:
            context: 回合上下文
            result: 要更新的回合结果
        """
        logger.debug(f"阶段: {RoundPhase.CLEANUP.value}")

        try:
            # 将上下文错误和警告复制到结果
            result.errors.extend(context.errors)
            result.warnings.extend(context.warnings)

            # 如果启用了持久化则保存决策历史
            if context.data_storage and context.persistence:
                for agent_id, decision in context.decisions.items():
                    context.data_storage.save_decision_history(
                        agent_id,
                        decision,
                        context.round_number
                    )

            # 如果启用了持久化则保存互动详情
            if context.data_storage and context.interaction_persistence:
                for interaction in context.interactions:
                    interaction_dict = interaction.to_dict() if hasattr(interaction, 'to_dict') else interaction
                    context.data_storage.save_interaction_details(
                        interaction_dict,
                        context.round_number
                    )

            if self._enable_detailed_logging:
                logger.debug(f"回合清理完成")

            result.phases_completed.append(RoundPhase.CLEANUP)
            self =_call_hooks(RoundPhase.CLEANUP, context, result)
        except Exception as e:
            result.add_error(f"清理失败: {e}")
            result.phases_failed[RoundPhase.CLEANUP] = str(e)

    def _call_hooks(
        self,
        phase: RoundPhase,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """调用阶段的所有注册钩子"""
        if phase in self._phase_hooks:
            for hook in self._phase_hooks[phase]:
                try:
                    hook(context, result)
                except Exception as e:
                    logger.error(f"阶段 {phase.value} 的钩子错误: {e}")
