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
        self.environment.set_agents(agents)
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

        # 步骤6: 指标计算（传入logger用于JSON导出）
        # 从环境获取活跃事件和历史事件，并映射事件类型
        environment_events = []

        # 1. 添加环境默认国际规范作为norm类型事件
        if hasattr(self.environment.state, 'norms'):
            for norm in self.environment.state.norms:
                environment_events.append({
                    'event_id': f"norm_{norm.norm_id}",
                    'event_type': "norm",
                    'name': norm.name,
                    'description': norm.description,
                    'participants': [],
                    'impact_level': 0.8,  # 规范重要性高
                    'metadata': {},
                    'validity': norm.validity,
                    'adherence_rate': norm.adherence_rate
                })

        # 2. 添加其他环境事件
        for event in self.environment.state.active_events + self.environment.state.event_history:
            # 映射事件类型到秩序判定期望的类型
            mapped_event_type = self._map_event_type_for_order(event.event_type, event.metadata)

            # 构建事件数据，添加秩序指标计算所需的字段
            event_data = {
                'event_id': event.event_id,
                'event_type': mapped_event_type,
                'name': event.name,
                'description': event.description,
                'participants': event.participants,
                'impact_level': event.impact_level,
                'metadata': event.metadata
            }

            # 根据事件类型添加必要的计算字段
            if mapped_event_type == "conflict":
                # 冲突事件：添加严重程度（基于影响级别）
                event_data['severity'] = int(event.impact_level * 100)  # 0-100分
            elif mapped_event_type == "norm":
                # 规范事件：添加有效性和遵守率
                event_data['validity'] = 100.0
                event_data['adherence_rate'] = 1.0
            elif mapped_event_type == "institution":
                # 制度事件：添加有效性
                event_data['validity'] = event.impact_level * 100  # 0-100分

            environment_events.append(event_data)

        metrics = await self.metrics_calculator.calculate_round_metrics(
            agents=agents,
            simulation_id=simulation_id,
            round=round,
            events=environment_events,
            interactions=interactions,
            logger=self.logger
        )
        result['metrics'] = metrics

        # 推送指标更新到前端
        await self._push_metrics_update(
            simulation_id=simulation_id,
            round=round,
            metrics=metrics,
            agents=agents
        )

        # 步骤7: 秩序判定与推送
        order_result = await self._evaluate_and_push_order(
            agents=agents,
            interactions=interactions,
            metrics=metrics,
            simulation_id=simulation_id,
            round=round
        )
        result['order_result_dict'] = order_result  # 存储完整的订单结果

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
                    'action_content': decision.get('action_content', ''),
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

                # 为所有其他国家添加公开记忆
                initiator_name = agent.state.name
                target_id = arguments.get('target')
                target_name = agent_map[target_id].state.name if target_id and target_id in agent_map else '未知'

                # 创建结构化公开记忆内容
                public_memory = {
                    'initiator': initiator_name,
                    'initiator_id': agent_id,
                    'action_name': function,
                    'action_content': decision.get('action_content', ''),
                    'target': target_name,
                    'target_id': target_id,
                    'round': round,
                    'timestamp': datetime.now().isoformat()
                }

                # 为所有其他国家添加公开记忆
                for other_agent_id, other_agent in agent_map.items():
                    if other_agent_id != agent_id:  # 不记录自己的动作
                        other_agent.add_public_memory(public_memory)

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

            # 添加 agent_powers 到 order_info（用于前端计算实力分布）
            agent_powers = {}
            for agent in agents:
                if hasattr(agent, 'state') and hasattr(agent.state, 'power_metrics'):
                    agent_powers[agent.state.agent_id] = agent.state.power_metrics.calculate_comprehensive_power()
            order_info['agent_powers'] = agent_powers

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

            # 构建秩序数据
            order_data = {
                "round": round,
                **order_info
            }

            # 推送消息
            await event_pusher.push_order_update(simulation_id, order_data)

            logger.debug(f"秩序更新已推送: 仿真={simulation_id}, 轮次={round}")

        except Exception as e:
            logger.error(f"秩序更新推送失败: {e}", exc_info=True)
            # 不抛出异常，不影响主流程

    async def _push_metrics_update(
        self,
        simulation_id: str,
        round: int,
        metrics: Dict,
        agents: List[Any]
    ) -> None:
        """
        推送指标更新到前端

        Args:
            simulation_id: 仿真ID
            round: 当前轮次
            metrics: 指标数据
            agents: 智能体列表
        """
        try:
            # 提取关键指标
            order_metrics = self._extract_key_metrics(metrics)

            # 构建智能体实力数据
            agent_powers = {}
            for agent in agents:
                if hasattr(agent, 'state') and agent.state.power_metrics:
                    agent_powers[agent.state.agent_id] = agent.state.power_metrics.calculate_comprehensive_power()

            # 导入WebSocket推送器
            from backend.api.ws import get_event_pusher

            event_pusher = get_event_pusher()

            # 构建指标数据
            metric_data = {
                "round": round,
                "metrics": order_metrics,
                "agent_powers": agent_powers
            }

            # 推送消息
            await event_pusher.push_metric_update(simulation_id, metric_data)

            logger.debug(f"指标更新已推送: {simulation_id}, {round}")

        except Exception as e:
            logger.error(f"指标更新推送失败: {e}", exc_info=True)
            # 不抛出异常，不影响主流程

    def _extract_key_metrics(self, metrics: Dict) -> Dict[str, Any]:
        """
        提取前端需要的关键指标

        Args:
            metrics: 指标字典

        Returns:
            关键指标字典
        """
        key_metrics = {
            "order_type": "未判定",
            "power_pattern": "未判定",
            "power_concentration": 0.0,
            "power_concentration_index": 0.0,
            "international_norm_effectiveness": 0.0,  # 修复：使用正确的字段名
            "conflict_level": 0.0,
            "institutionalization_index": 0.0  # 修复：使用正确的字段名
        }

        if isinstance(metrics, dict):
            for category, metric_list in metrics.items():
                if isinstance(metric_list, list):
                    for metric in metric_list:
                        if isinstance(metric, dict):
                            name = metric.get("name")
                            value = metric.get("value", 0)

                            # 映射指标名称
                            if name == "international_order_type":
                                key_metrics["order_type"] = metric.get("metadata", {}).get("order_type", "未判定")
                                key_metrics["power_pattern"] = metric.get("metadata", {}).get("power_pattern", "未判定")
                            elif name == "power_concentration_index":
                                key_metrics["power_concentration"] = value
                                key_metrics["power_concentration_index"] = value
                            elif name == "international_norm_effectiveness":
                                key_metrics["norm_validity"] = value
                            elif name == "conflict_level":
                                key_metrics["conflict_level"] = value
                            elif name == "institutionalization_index":
                                key_metrics["institutionalization"] = value

        return key_metrics

    def _map_event_type_for_order(self, event_type: str, metadata: Dict) -> str:
        """
        将环境事件类型映射为秩序判定所需的类型

        Args:
            event_type: 原始事件类型
            metadata: 事件元数据

        Returns:
            映射后的事件类型
        """
        # 冲突类型事件
        conflict_types = ["regional_conflict", "territorial_dispute", "economic_crisis"]
        if event_type in conflict_types:
            return "conflict"

        # 制度化相关事件
        if event_type == "periodic":
            event_subtype = metadata.get("type", "")
            if event_subtype == "election":
                return "institution"  # 选举事件反映制度化程度
            elif event_subtype == "economic_cycle":
                return "institution"  # 经济周期反映制度化程度

        # 盟友事件
        if event_type == "ally_betrayal":
            return "norm"  # 违反盟约反映规范有效性降低

        # 默认返回原类型
        return event_type
