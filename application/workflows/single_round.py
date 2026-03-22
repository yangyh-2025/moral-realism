"""
单轮仿真工作流 - 对应技术方案7.1节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SingleRoundWorkflow:
    """
    单轮仿真工作流

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        environment,  # EnvironmentEngine实例
        decision_engine,  # DecisionEngine实例
        metrics_calculator,  # MetricsCalculator实例
        storage,  # StorageEngine实例
        logger  # EnhancedLogger实例
    ):
        self.environment = environment
        self.decision_engine = decision_engine
        self.metrics_calculator = metrics_calculator
        self.storage = storage
        self.logger = logger

    async def execute(
        self,
        agents: List,  # BaseAgent实例列表
        simulation_id: str,
        round: int
    ) -> Dict:
        """
        执行单轮仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            round: 当前轮次

        Returns:
            轮次结果
        """
        result = {
            'round': round,
            'decisions': [],
            'interactions': [],
            'metrics': {}
        }

        # 步骤1: 环境更新与事件触发
        self.environment.update_round()
        agent_ids = [agent.state.agent_id for agent in agents]
        periodic_events = self.environment.trigger_periodic_events(agent_ids)
        random_events = self.environment.trigger_random_events(agent_ids, probability=0.1)

        # 步骤2: 智能体决策生成（并行）
        environment_state = self.environment.get_full_state()
        decisions = await self.decision_engine.generate_decisions_for_all_agents(
            agents=agents,
            environment_state=environment_state,
            simulation_id=simulation_id,
            round=round
        )

        result['decisions'] = decisions

        # 步骤3: 决策冲突检测与解决
        conflicts = self.decision_engine.detect_conflicts(decisions)
        if conflicts:
            self.logger.log_event(
                simulation_id=simulation_id,
                round=round,
                event_type="decision_conflict_detected",
                description=f"检测到{len(conflicts)}个决策冲突",
                metadata={'conflicts': conflicts}
            )
            decisions = self.decision_engine.resolve_conflicts(decisions, conflicts, strategy='priority')

        # 步骤4: 决策执行与互动计算
        interactions = await self._execute_interactions(
            decisions=decisions,
            agents=agents,
            simulation_id=simulation_id,
            round=round
        )
        result['interactions'] = interactions

        # 步骤5: 影响更新
        await self._update_impact(
            interactions=interactions,
            agents=agents,
            simulation_id=simulation_id,
            round=round
        )

        # 步骤6: 指标计算
        metrics = await self.metrics_calculator.calculate_round_metrics(
            agents=agents,
            simulation_id=simulation_id,
            round=round
        )
        result['metrics'] = metrics

        # 步骤7: 秩序判定与推送
        order_result = await self._evaluate_and_push_order(
            agents=agents,
            interactions=interactions,
            metrics=metrics,
            simulation_id=simulation_id,
            round=round
        )
        result['order_type'] = order_result

        # 保存轮次结果
        self.storage.save_round_result(
            simulation_id=simulation_id,
            round=round,
            result=result
        )

        return result

    async def _execute_interactions(
        self,
        decisions: List[Dict],
        agents: List[Any],
        simulation_id: str,
        round: int
    ) -> List[Dict]:
        """
        执行决策并计算互动

        Args:
            decisions: 决策列表
            agents: 智能体列表
            simulation_id: 仿真ID
            round: 当前轮次

        Returns:
            互动列表
        """
        interactions = []
        agent_map = {agent.state.agent_id: agent for agent in agents}

        for decision in decisions:
            agent_id = decision.get('agent_id')
            function = decision.get('function')
            arguments = decision.get('arguments', {})

            if not function:
                continue

            agent = agent_map.get(agent_id)
            if not agent:
                continue

            try:
                # 执行决策
                outcome = await agent.execute_action(function, **arguments)

                # 记录互动
                interaction = {
                    'interaction_id': f"interaction_{agent_id}_{round}_{datetime.now().timestamp()}",
                    'round': round,
                    'initiator_id': agent_id,
                    'target_id': arguments.get('target'),
                    'interaction_type': function,
                    'interaction_data': arguments,
                    'outcome': outcome,
                    'timestamp': datetime.now().isoformat()
                }

                interactions.append(interaction)

                # 记录行动日志
                self.logger.log_action(
                    simulation_id=simulation_id,
                    round=round,
                    agent_id=agent_id,
                    action_type=function,
                    action_content=str(arguments),
                    outcome=str(outcome),
                    reasoning=decision.get('reasoning')
                )

            except Exception as e:
                self.logger.log_error(
                    simulation_id=simulation_id,
                    error_type="interaction_execution_error",
                    error_message=str(e),
                    context={'agent_id': agent_id, 'function': function}
                )

        return interactions

    async def _update_impact(
        self,
        interactions: List[Dict],
        agents: List[Any],
        simulation_id: str,
        round: int
    ) -> None:
        """
        更新互动影响

        Args:
            interactions: 互动列表
            agents: 智能体列表
            simulation_id: 仿真ID
            round: 当前轮次
        """
        agent_map = {agent.state.agent_id: agent for agent in agents}

        for interaction in interactions:
            initiator_id = interaction.get('initiator_id')
            target_id = interaction.get('target_id')
            outcome = interaction.get('outcome', {})

            # 更新发起者状态
            if initiator_id in agent_map:
                agent = agent_map[initiator_id]
                agent.update_after_interaction(
                    interaction_type=interaction.get('interaction_type'),
                    outcome=outcome
                )

            # 更新目标者状态
            if target_id and target_id in agent_map:
                agent = agent_map[target_id]
                agent.update_after_interaction(
                    interaction_type=interaction.get('interaction_type'),
                    outcome=outcome,
                    is_target=True
                )

    async def _evaluate_and_push_order(
        self,
        agents: List[Any],
        interactions: List[Dict],
        metrics: Dict,
        simulation_id: str,
        round: int
    ) -> Optional[Dict[str, Any]]:
        """
        评估秩序类型并推送

        Args:
            agents: 智能体列表
            interactions: 互动记录
            metrics: 指标数据
            simulation_id:: 仿真ID
            round: 当前轮次

        Returns:
            秩序评估结果，失败返回None
        """
        try:
            # 提取秩序判定所需指标
            indicators = self._extract_order_indicators(agents, interactions, metrics)

            # 评估秩序类型
            order_info = await self._evaluate_order_type(indicators)

            # 推送秩序更新
            await self._push_order_update(simulation_id, round, order_info)

            logger.debug(
                f"秩序类型评估完成: 仿真={simulation_id}, 轮次={round}, "
                f"类型={order_info.get('order_type', '未判定')}"
            )

            return order_info

        except Exception as e:
            logger.error(f"秩序评估与推送失败: {e}", exc_info=True)
            return {
                "order_type": "未判定",
                "confidence": 0.0,
                "error": str(e)
            }

    def _extract_order_indicators(
        self,
        agents: List[Any],
        interactions: List[Dict],
        metrics: Dict
    ) -> Dict[str, float]:
        """
        提取秩序判定所需指标

        Args:
            agents: 智能体列表
            interactions: 互动记录
            metrics: 指标数据

        Returns:
            指标字典
        """
        indicators = {}

        try:
            # 从指标数据中提取已计算的指标
            if isinstance(metrics, dict):
                # 实力集中度
                power_conc = self._find_metric_value(metrics, "power_concentration_index")
                indicators["power_concentration_index"] = power_conc if power_conc is not None else 0.0

                # 规范有效性
                norm_eff = self._find_metric_value(metrics, "international_norm_effectiveness")
                indicators["international_norm_effectiveness"] = norm_eff if norm_eff is not None else 0.0

                # 冲突水平
                conflict = self._find_metric_value(metrics, "conflict_level")
                indicators["conflict_level"] = conflict if conflict is not None else 0.0

                # 制度化程度
                inst = self._find_metric_value(metrics, "institutionalization_index")
                indicators["institutionalization_index"] = inst if inst is not None else 0.0

                # 联盟数量
                alliances = self._find_metric_value(metrics, "alliance_count")
                indicators["alliance_count"] = int(alliances) if alliances is not None else 0

            logger.debug(f"提取的秩序指标: {indicators}")

        except Exception as e:
            logger.warning(f"提取秩序指标失败: {e}")
            # 返回默认值
            indicators = {
                "power_concentration_index": 0.0,
                "international_norm_effectiveness": 0.0,
                "conflict_level": 0.0,
                "institutionalization_index": 0.0,
                "alliance_count": 0
            }

        return indicators

    def _find_metric_value(self, metrics: Dict, metric_name: str) -> Optional[float]:
        """
        在指标字典中查找指定指标的值

        Args:
            metrics: 指标字典
            metric_name: 指标名称

        Returns:
            指标值，如果未找到返回None
        """
        for category, metric_list in metrics.items():
            if isinstance(metric_list, list):
                for metric in metric_list:
                    if isinstance(metric, dict):
                        if metric.get("name") == metric_name:
                            return metric.get("value")
                    elif hasattr(metric, "name") and metric.name == metric_name:
                        return metric.value
        return None

    async def _evaluate_order_type(self, indicators: Dict[str, float]) -> Dict[str, Any]:
        """
        评估秩序类型

        Args:
            indicators: 指标字典

        Returns:
            秩序评估结果
        """
        try:
            # 导入OrderEvaluator
            from domain.analysis.order_evaluation import OrderEvaluator, OrderEvaluationContext

            # 构建评估上下文
            context = OrderEvaluationContext(
                power_concentration_index=indicators.get("power_concentration_index", 0.0),
                international_norm_effectiveness=indicators.get("international_norm_effectiveness", 0.0),
                conflict_level=indicators.get("conflict_level", 0.0),
                alliance_count=int(indicators.get("alliance_count", 0)),
                institutionalization_index=indicators.get("institutionalization_index", 0.0)
            )

            # 执行评估
            evaluator = OrderEvaluator()
            result = evaluator.evaluate(context)

            return {
                "order_type": result.order_type,
                "confidence": result.confidence,
                "indicators": indicators,
                "reasoning": result.reasoning,
                "timestamp": result.timestamp
            }

        except Exception as e:
            logger.error(f"秩序类型评估失败: {e}", exc_info=True)
            return {
                "order_type": "未判定",
                "confidence": 0.0,
                "indicators": indicators,
                "reasoning": f"评估失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def _push_order_update(
        self,
        simulation_id: str,
        round: int,
        order_info: Dict[str, Any]
    ) -> None:
        """
        推送秩序更新到前端

        Args:
            simulation_id: 仿真ID
            round: 当前轮次
            order_info: 秩序评估结果
        """
        try:
            # 导入WebSocket推送器
            from backend.api.ws import get_event_pusher

            event_pusher = get_event_pusher()

            # 构建消息
            message = {
                "type": "order_update",
                "simulation_id": simulation_id,
                "data": {
                    "round": round,
                    **order_info
                },
                "timestamp": datetime.now().isoformat()
            }

            # 推送消息
            await event_pusher.manager.broadcast_to_simulation(simulation_id, message)

            logger.debug(f"秩序更新已推送: 仿真={simulation_id}, 轮次={round}")

        except Exception as e:
            logger.error(f"秩序更新推送失败: {e}", exc_info=True)
            # 不抛出异常，不影响主流程
