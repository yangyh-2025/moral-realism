"""
单轮仿真工作流 - 对应技术方案7.1节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Any
import asyncio
from datetime import datetime


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
