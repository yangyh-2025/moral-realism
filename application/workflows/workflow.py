"""
工作流编排 - 由智能体D实现

编排仿真工作流程，管理各阶段任务。

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from application.workflows.single_round import SingleRoundWorkflow


class SimulationWorkflow:
    """
    仿真工作流编排器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        environment: Any,  # EnvironmentEngine实例
        decision_engine: Any,  # DecisionEngine实例
        metrics_calculator: Any,  # MetricsCalculator实例
        storage: Any,  # StorageEngine实例
        logger: Any  # EnhancedLogger实例
    ):
        """
        初始化工作流编排器

        Args:
            environment: 环境引擎
            decision_engine: 决策引擎
            metrics_calculator: 指标计算器
            storage: 存储引擎
            logger: 日志记录器
        """
        self.environment = environment
        self.decision_engine = decision_engine
        self.metrics_calculator = metrics_calculator
        self.storage = storage
        self.logger = logger

        # 初始化单轮工作流
        self.single_round_workflow = SingleRoundWorkflow(
            environment=environment,
            decision_engine=decision_engine,
            metrics_calculator=metrics_calculator,
            storage=storage,
            logger=logger
        )

        self._simulation_state = {}
        self._is_paused = False
        self._is_cancelled = False

    async def run_multi_round_simulation(
        self,
        agents: List[Any],
        simulation_id: str,
        max_rounds: int = 100,
        stop_conditions: Optional[List[Dict]] = None
    ) -> Dict:
        """
        运行多轮仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            max_rounds: 最大轮次
            stop_conditions: 停止条件列表

        Returns:
            仿真结果
        """
        # 初始化仿真
        await self._initialize_simulation(
            agents=agents,
            simulation_id=simulation_id
        )

        results = {
            'simulation_id': simulation_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'total_rounds': 0,
            'rounds': [],
            'final_state': {},
            'stop_reason': None
        }

        # 运行轮次循环
        for round_num in range(1, max_rounds + 1):
            # 检查是否暂停或取消
            if self._is_paused:
                await self._wait_for_resume()

            if self._is_cancelled:
                results['stop_reason'] = 'cancelled'
                break

            # 执行单轮
            try:
                round_result = await self.single_round_workflow.execute(
                    agents=agents,
                    simulation_id=simulation_id,
                    round=round_num
                )

                results['rounds'].append(round_result)
                results['total_rounds'] = round_num

                # 检查停止条件
                if await self._check_stop_conditions(
                    agents=agents,
                    round_result=round_result,
                    conditions=stop_conditions
                ):
                    results['stop_reason'] = 'stop_condition_met'
                    break

                # 更新仿真状态
                self._update_simulation_state(round_result)

            except Exception as e:
                self.logger.log_error(
                    simulation_id=simulation_id,
                    error_type="round_execution_error",
                    error_message=str(e),
                    context={'round': round_num}
                )
                results['stop_reason'] = f'error_at_round_{round_num}'
                break

        # 仿真结束处理
        results['end_time'] = datetime.now().isoformat()
        results['final_state'] = self._get_final_state(agents)

        # 保存最终结果
        self.storage.save_simulation_result(simulation_id, results)

        return results

    async def run_single_round(
        self,
        agents: List[Any],
        simulation_id: str,
        round: int
    ) -> Dict:
        """
        运行单轮仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            round: 轮次

        Returns:
            轮次结果
        """
        return await self.single_round_workflow.execute(
            agents=agents,
            simulation_id=simulation_id,
            round=round
        )

    def pause(self) -> None:
        """暂停仿真"""
        self._is_paused = True
        self.logger.log_info(
            simulation_id=self._simulation_state.get('current_simulation_id', ''),
            message="Simulation paused"
        )

    def resume(self) -> None:
        """恢复仿真"""
        self._is_paused = False
        self.logger.log_info(
            simulation_id=self._simulation_state.get('current_simulation_id', ''),
            message="Simulation resumed"
        )

    def cancel(self) -> None:
        """取消仿真"""
        self._is_cancelled = True
        self.logger.log_info(
            simulation_id=self._simulation_state.get('current_simulation_id', ''),
            message="Simulation cancelled"
        )

    async def _initialize_simulation(
        self,
        agents: List[Any],
        simulation_id: str
    ) -> None:
        """
        初始化仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
        """
        self._simulation_state = {
            'current_simulation_id': simulation_id,
            'start_time': datetime.now(),
            'round_count': 0
        }

        # 初始化环境
        self.environment.initialize(agents)

        # 计算初始实力层级
        await self._calculate_power_tiers(agents)

        # 记录初始化日志
        self.logger.log_info(
            simulation_id=simulation_id,
            message=f"Simulation initialized with {len(agents)} agents"
        )

    async def _calculate_power_tiers(self, agents: List[Any]) -> None:
        """
        计算实力层级

        Args:
            agents: 智能体列表
        """
        # 获取所有智能体的综合国力
        powers = [
            agent.state.power_metrics.calculate_comprehensive_power()
            for agent in agents
            if agent.state.power_metrics
        ]

        if not powers:
            return

        # 计算均值和标准差
        import statistics
        mean_power = statistics.mean(powers)
        std_power = statistics.stdev(powers) if len(powers) > 1 else 0

        # 根据正态分布分配实力层级
        from domain.power.power_metrics import PowerTier
        for agent in agents:
            if not agent.state.power_metrics:
                continue

            power = agent.state.power_metrics.calculate_comprehensive_power()
            z_score = (power - mean_power) / std_power if std_power > 0 else 0

            if z_score > 2.0:
                agent.state.power_tier = PowerTier.SUPERPOWER
            elif z_score > 1.5:
                agent.state.power_tier = PowerTier.GREAT_POWER
            elif z_score > 0.5:
                agent.state.power_tier = PowerTier.MIDDLE_POWER
            else:
                agent.state.power_tier = PowerTier.SMALL_POWER

    async def _check_stop_conditions(
        self,
        agents: List[Any],
        round_result: Dict,
        conditions: Optional[List[Dict]]
    ) -> bool:
        """
        检查停止条件

        Args:
            agents: 智能体列表
            round_result: 轮次结果
            conditions: 停止条件列表

        Returns:
            是否满足停止条件
        """
        if not conditions:
            return False

        for condition in conditions:
            condition_type = condition.get('type')

            if condition_type == 'max_conflicts':
                # 检查冲突数量
                conflicts = round_result.get('interactions', [])
                conflict_count = len([
                    i for i in conflicts
                    if i.get('outcome', {}).get('success') == False
                ])
                if conflict_count >= condition.get('threshold', 10):
                    return True

            elif condition_type == 'power_concentration':
                # 检查权力集中度
                from statistics import mean
                powers = [
                    a.state.power_metrics.calculate_comprehensive_power()
                    for a in agents
                    if a.state.power_metrics
                ]
                if powers:
                    max_power = max(powers)
                    avg_power = mean(powers)
                    concentration = max_power / avg_power if avg_power > 0 else 0
                    if concentration >= condition.get('threshold', 3.0):
                        return True

            elif condition_type == 'stability':
                # 检查稳定性指标
                metrics = round_result.get('metrics', {})
                stability = metrics.get('system_stability', 1.0)
                if stability <= condition.get('threshold', 0.3):
                    return True

        return False

    def _update_simulation_state(self, round_result: Dict) -> None:
        """
        更新仿真状态

        Args:
            round_result: 轮次结果
        """
        self._simulation_state['round_count'] += 1
        self._simulation_state['last_round_time'] = datetime.now()

    def _get_final_state(self, agents: List[Any]) -> Dict:
        """
        获取最终状态

        Args:
            agents: 智能体列表

        Returns:
            最终状态
        """
        agent_states = []
        for agent in agents:
            agent_states.append({
                'agent_id': agent.state.agent_id,
                'name': agent.state.name,
                'power_tier': agent.state.power_tier.value if agent.state.power_tier else 'unknown',
                'power': agent.state.power_metrics.calculate_comprehensive_power() if agent.state.power_metrics else 0,
                'region': agent.state.region
            })

        return {
            'agents': agent_states,
            'total_rounds': self._simulation_state.get('round_count', 0)
        }

    async def _wait_for_resume(self) -> None:
        """等待恢复"""
        while self._is_paused:
            await asyncio.sleep(0.1)


class WorkflowManager:
    """
    工作流管理器 - 管理多个仿真工作流

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        self._active_workflows: Dict[str, SimulationWorkflow] = {}
        self._workflow_lock = asyncio.Lock()

    async def create_workflow(
        self,
        workflow_id: str,
        environment: Any,
        decision_engine: Any,
        metrics_calculator: Any,
        storage: Any,
        logger: Any
    ) -> SimulationWorkflow:
        """
        创建工作流

        Args:
            workflow_id: 工作流ID
            environment: 环境引擎
            decision_engine: 决策引擎
            metrics_calculator: 指标计算器
            storage: 存储引擎
            logger: 日志记录器

        Returns:
            工作流实例
        """
        async with self._workflow_lock:
            workflow = SimulationWorkflow(
                environment=environment,
                decision_engine=decision_engine,
                metrics_calculator=metrics_calculator,
                storage=storage,
                logger=logger
            )
            self._active_workflows[workflow_id] = workflow
            return workflow

    def get_workflow(self, workflow_id: str) -> Optional[SimulationWorkflow]:
        """
        获取工作流

        Args Args:
            workflow_id: 工作流ID

        Returns:
            工作流实例
        """
        return self._active_workflows.get(workflow_id)

    async def remove_workflow(self, workflow_id: str) -> None:
        """
        移除工作流

        Args:
            workflow_id: 工作流ID
        """
        async with self._workflow_lock:
            if workflow_id in self._active_workflows:
                workflow = self._active_workflows[workflow_id]
                workflow.cancel()
                del self._active_workflows[workflow_id]

    def list_active_workflows(self) -> List[str]:
        """
        列出活跃工作流

        Returns:
            工作流ID列表
        """
        return list(self._active_workflows.keys())
