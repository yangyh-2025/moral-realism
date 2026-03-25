"""
仿真管理服务 - 仿真生命周期管理和查询

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import uuid
import json
import logging
import os

from infrastructure.storage.storage_engine import StorageEngine
from domain.environment.environment_engine import EnvironmentEngine
from infrastructure.llm.llm_engine import LLMEngine, SiliconFlowProvider
from application.decision.decision_engine import DecisionEngine
from infrastructure.validation.validator import RuleValidator
from application.analysis.metrics import MetricsPipeline, CalculationContext
from application.workflows.single_round import SingleRoundWorkflow
from application.workflows.multi_round import MultiRoundWorkflow
from backend.api.ws import get_event_pusher

logger = logging.getLogger(__name__)


class SimulationStatus(Enum):
    """仿真状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class SimulationConfig:
    """仿真配置"""
    simulation_id: str
    total_rounds: int = 100
    round_duration_months: int = 6
    random_event_prob: float = 0.1
    agent_configs: List[Dict] = field(default_factory=list)
    event_config: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Simulation:
    """仿真实例"""
    simulation_id: str
    config: SimulationConfig
    status: SimulationStatus
    current_round: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class SimulationResult:
    """仿真结果"""
    simulation_id: str
    total_rounds: int
    completed_rounds: int
    status: SimulationStatus
    summary: Dict = field(default_factory=dict)
    final_state: Dict = field(default_factory=dict)


@dataclass
class ProgressInfo:
    """仿真进度信息"""
    simulation_id: str
    current_round: int
    total_rounds: int
    percentage: float
    estimated_remaining: Optional[float] = None
    current_phase: Optional[str] = None


@dataclass
class QueryFilters:
    """查询过滤器"""
    status: Optional[SimulationStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class SimulationLifecycle:
    """
    仿真生命周期管理

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, storage: StorageEngine):
        self.storage = storage
        self._active_simulations: Dict[str, Simulation] = {}
        self._simulation_tasks: Dict[str, asyncio.Task] = {}
        self._agents: Dict[str, List[Any]] = {}  # simulation_id -> agents list

    def _create_agents_from_api_data(self, agent_data_list: List[Dict]) -> List[Any]:
        """
        从 API 的 Agent 数据创建智能体对象

        Args:
            agent_data_list: API Agent 数据列表

        Returns:
            智能体对象列表
        """
        agents = []
        from domain.agents.base_agent import BaseAgent
        from domain.power.power_metrics import PowerMetrics, PowerTier
        from config.leader_types import LeaderType

        for agent_data in agent_data_list:
            # 轎取 power_metrics 字典
            pm_dict = agent_data.get('power_metrics', {})
            if isinstance(pm_dict, dict):
                # API 层使用 C,E,M,S,W，domain 层使用不同的字段名
                power_metrics = PowerMetrics(
                    critical_mass=pm_dict.get('C', pm_dict.get('critical_mass', 50.0)),
                    economic_capability=pm_dict.get('E', pm_dict.get('economic_capability', 100.0)),
                    military_capability=pm_dict.get('M', pm_dict.get('military_capability', 100.0)),
                    strategic_purpose=pm_dict.get('S', pm_dict.get('strategic_purpose', 0.75)),
                    national_will=pm_dict.get('W', pm_dict.get('national_will', 0.75))
                )
            else:
                power_metrics = PowerMetrics()

            # 创建智能体（根据 power_tier 选择类型）
            power_tier_str = agent_data.get('power_tier', 'middle_power')
            try:
                power_tier = PowerTier(power_tier_str)
            except ValueError:
                power_tier = PowerTier.MIDDLE_POWER

            # 获取 leader_type（支持中英文）
            from backend.helpers.leader_type_mapper import parse_leader_type
            leader_type_str = agent_data.get('leader_type')
            leader_type = parse_leader_type(leader_type_str)

            # 根据 power_tier 设置 leader_type
            if power_tier in [PowerTier.SUPERPOWER, PowerTier.GREAT_POWER]:
                # 超级大国和大国必须配置领导类型，未配置则使用默认值
                if leader_type is None:
                    leader_type = LeaderType.WANGDAO  # 默认使用王道型
            elif power_tier in [PowerTier.MIDDLE_POWER, PowerTier.SMALL_POWER]:
                # 中等强国和小国不应配置领导类型，强制设为 None
                leader_type = None

            # 使用工厂统一创建智能体，确保初始化流程正确
            from domain.agents.agent_factory import AgentFactory
            agent = AgentFactory.create_agent(
                agent_id=agent_data.get('id'),
                name=agent_data.get('name'),
                region=agent_data.get('region'),
                power_metrics=power_metrics,
                power_tier=power_tier,
                leader_type=leader_type
            )

            agents.append(agent)

        return agents

    def _get_agents_for_simulation(self, simulation_id: str) -> List[Any]:
        """
        获取仿真的智能体列表

        Args:
            simulation_id: 仿真ID

        Returns:
            智能体列表
        """
        if simulation_id in self._agents:
            return self._agents[simulation_id]

        # 从 API 的 agents_store 获取智能体数据
        import backend.api.agents as agents_module

        # 获取所有智能体（包括未关联到特定仿真的智能体）
        # 这样支持前端先创建智能体，再启动仿真的工作流程
        agent_data_list = [agent.model_dump() for agent in agents_module._agents_store.values()]

        if agent_data_list:
            logger.info(f"为仿真 {simulation_id} 获取到 {len(agent_data_list)} 个智能体")
            agents = self._create_agents_from_api_data(agent_data_list)
            self._agents[simulation_id] = agents
            return agents

        logger.warning(f"仿真 {simulation_id} 没有可用的智能体")
        return []

    async def create_simulation(self, config: SimulationConfig) -> Simulation:
        """
        创建仿真实例

        Args:
            config: 仿真配置

        Returns:
            Simulation: 创建的仿真实例
        """
        if config.simulation_id in self._active_simulations:
            raise ValueError(f"仿真 {config.simulation_id} 已存在")

        simulation = Simulation(
            simulation_id=config.simulation_id,
            config=config,
            status=SimulationStatus.PENDING,
            start_time=datetime.now()
        )

        self._active_simulations[simulation.simulation_id] = simulation

        # 保存仿真开始记录到存储
        self.storage.save_simulation_start(
            simulation_id=simulation.simulation_id,
            config=config.__dict__
        )

        return simulation

    async def start_simulation(self, simulation_id: str) -> SimulationResult:
        """
        启动仿真

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationResult: 仿真结果
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status == SimulationStatus.RUNNING:
            raise ValueError(f"仿真 {simulation_id} 正在运行中")

        simulation.status = SimulationStatus.RUNNING
        simulation.start_time = datetime.now() if not simulation.start_time else simulation.start_time

        # 启动仿真运行任务
        asyncio.create_task(self._run_simulation(simulation))

        return SimulationResult(
            simulation_id=simulation.simulation_id,
            total_rounds=simulation.config.total_rounds,
            completed_rounds=simulation.current_round,
            status=simulation.status,
            summary={"message": "仿真已启动"}
        )

    async def _run_simulation(self, simulation: Simulation) -> None:
        """
        运行仿真任务（后台任务）

        Args:
            simulation: 仿真实例
        """
        try:
            logger.info(f"开始仿真: {simulation.simulation_id}, 总轮次: {simulation.config.total_rounds}")

            # 获取或初始化智能体
            agents = self._get_agents_for_simulation(simulation.simulation_id)
            if not agents:
                logger.warning(f"仿真 {simulation.simulation_id} 没有智能体，直接完成")
                simulation.status = SimulationStatus.COMPLETED
                simulation.end_time = datetime.now()
                return

            # 导入配置中的 LLM API keys
            from config.settings import SimulationConfig as AppSettings
            import os

            # 初始化组件
            try:
                env_config = AppSettings()
            except:
                env_config = AppSettings()

            api_keys = env_config.llm_api_keys or [
                os.getenv("LLM_API_KEY", "")
            ]
            api_keys = [k for k in api_keys if k]  # 过滤空 key

            if not api_keys:
                logger.error("未配置 LLM API key，无法使用 LLM 决策")
                # 使用空 key 继续运行，但会报错
                api_keys = [""]

            # 获取事件推送器
            event_pusher = get_event_pusher()

            # 创建 LLM 引擎
            logger.info(f"LLM 配置加载: base_url={env_config.llm_base_url}, model={env_config.llm_model}, api_keys_count={len(api_keys)}")
            provider = SiliconFlowProvider(
                api_key=api_keys,
                base_url=env_config.llm_base_url,
                model=env_config.llm_model,
                event_pusher=event_pusher,
                simulation_id=simulation.simulation_id
            )
            logger.info(f"SiliconFlowProvider 初始化完成: base_url={provider.base_url}, model={provider.model}")

            # 创建 LLM 引擎
            from infrastructure.llm.llm_engine import LLMEngine
            llm_engine = LLMEngine(
                provider=provider,
                event_pusher=event_pusher,
                simulation_id=simulation.simulation_id
            )
            logger.info(f"LLMEngine 初始化完成")

            # 创建增强日志记录器（传入simulation_id）
            from infrastructure.logging.logger import EnhancedLogger
            enhanced_logger = EnhancedLogger(log_dir=f"logs/{simulation.simulation_id}", simulation_id=simulation.simulation_id)

            # 创建决策引擎
            validator = RuleValidator()
            decision_engine = DecisionEngine(
                llm_engine=llm_engine,
                validator=validator,
                storage=self.storage,
                logger=enhanced_logger
            )

            # 创建环境引擎
            environment = EnvironmentEngine()

            # 创建指标计算器
            metrics_pipeline = MetricsPipeline()

            # 创建单轮工作流
            single_round_workflow = SingleRoundWorkflow(
                environment=environment,
                decision_engine=decision_engine,
                metrics_calculator=metrics_pipeline,
                storage=self.storage,
                logger=enhanced_logger
            )

            # 创建多轮工作流
            multi_round_workflow = MultiRoundWorkflow()

            # 设置回调函数
            async def on_round_start(sim_id: str, rnd: int):
                logger.info(f"仿真 {sim_id}: 开始第 {rnd + 1} 轮")

            async def on_round_complete(sim_id: str, rnd: int, result: Dict):
                logger.info(f"仿真 {sim_id}: 完成第 {rnd + 1} 轮")
                # 更新进度
                simulation.current_round = rnd + 1
                simulation.progress = ((rnd + 1) / simulation.config.total_rounds) * 100.0

                # 推送轮次完成消息
                round_info = {
                    "round": rnd + 1,
                    "total_rounds": simulation.config.total_rounds,
                    "progress": simulation.progress,
                    "status": "completed"
                }
                await event_pusher.push_round_complete(sim_id, round_info)

                # 推送指标更新消息
                if "metrics" in result:
                    metrics_data = {
                        "round": rnd + 1,
                        "metrics": result["metrics"],
                        "agent_powers": {}
                    }
                    # 计算智能体实力数据
                    agent_powers = {}
                    for agent in agents:
                        if hasattr(agent, 'state') and hasattr(agent.state, 'power_metrics'):
                            agent_powers[agent.state.agent_id] = agent.state.power_metrics.calculate_comprehensive_power()
                    metrics_data["agent_powers"] = agent_powers
                    await event_pusher.push_metric_update(sim_id, metrics_data)

                # 推送秩序更新消息
                if "order_result_dict" in result:
                    order_info = {
                        "round": rnd + 1,
                        **result["order_result_dict"]
                    }
                    await event_pusher.push_order_update(sim_id, order_info)

                # 推送互动数据消息
                if "interactions" in result:
                    await event_pusher.push_interactions_update(sim_id, result["interactions"], rnd + 1)

            multi_round_workflow.callbacks.on_round_start(on_round_start)
            multi_round_workflow.callbacks.on_round_complete(on_round_complete)

            # 执行多轮仿真
            logger.info(f"开始执行多轮仿真: {simulation.simulation_id}, 智能体数: {len(agents)}")

            try:
                results = await multi_round_workflow.execute(
                    agents=agents,
                    simulation_id=simulation.simulation_id,
                    total_rounds=simulation.config.total_rounds,
                    round_func=lambda a, sid, rnd: single_round_workflow.execute(a, sid, rnd),
                    checkpoint_interval=10
                )

                logger.info(f"仿真完成: {simulation.simulation_id}, 完成 {len(results)} 轮")
                simulation.status = SimulationStatus.COMPLETED
                simulation.end_time = datetime.now()
                simulation.current_round = simulation.config.total_rounds
                simulation.progress = 100.0

                # 导出仿真数据到JSON
                try:
                    from infrastructure.storage.json_export import JSONExporter

                    exporter = JSONExporter(log_dir="logs")

                    # 导出智能体状态
                    exporter.export_agent_states(simulation.simulation_id, agents)
                    logger.info(f"仿真 {simulation.simulation_id} 数据已导出到 logs/{simulation.simulation_id}/")

                except Exception as export_error:
                    logger.error(f"导出仿真数据失败: {export_error}", exc_info=True)

            except Exception as e:
                logger.error(f"仿真执行失败: {e}", exc_info=True)
                simulation.status = SimulationStatus.ERROR
                simulation.error_message = str(e)
                simulation.end_time = datetime.now()

            # 保存仿真结束记录
            self.storage.save_simulation_end(
                simulation_id=simulation.simulation_id,
                total_rounds=simulation.current_round,
                status=simulation.status.value
            )

        except Exception as e:
            logger.error(f"仿真任务失败: {e}", exc_info=True)
            simulation.status = SimulationStatus.ERROR
            simulation.error_message = str(e)
            simulation.end_time = datetime.now()

    async def pause_simulation(self, simulation_id: str) -> None:
        """
        暂停仿真

        Args:
            simulation_id: 仿真ID
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status != SimulationStatus.RUNNING:
            raise ValueError(f"仿真 {simulation_id} 未在运行")

        simulation.status = SimulationStatus.PAUSED

        # 暂停仿真任务
        if simulation_id in self._simulation_tasks:
            self._simulation_tasks[simulation_id].cancel()
            del self._simulation_tasks[simulation_id]

    async def resume_simulation(self, simulation_id: str) -> SimulationResult:
        """
        继续仿真

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationResult: 仿真结果
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status != SimulationStatus.PAUSED:
            raise ValueError(f"仿真 {simulation_id} 未处于暂停状态")

        simulation.status = SimulationStatus.RUNNING

        # 在实际实现中，这里会继续仿真任务

        return SimulationResult(
            simulation_id=simulation.simulation_id,
            total_rounds=simulation.config.total_rounds,
            completed_rounds=simulation.current_round,
            status=simulation.status,
            summary={"message": "仿真已继续"}
        )

    async def stop_simulation(self, simulation_id: str) -> None:
        """
        停止仿真

        Args:
            simulation_id: 仿真ID
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        if simulation.status not in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]:
            raise ValueError(f"仿真 {simulation_id} 未在运行")

        simulation.status = SimulationStatus.STOPPED
        simulation.end_time = datetime.now()

        # 在实际实现中，这里会停止仿真任务
        # if simulation_id in self._simulation_tasks:
        #     self._simulation_tasks[simulation_id].cancel()

    async def delete_simulation(self, simulation_id: str) -> None:
        """
        删除仿真

        Args:
            simulation_id: 仿真ID
        """
        if simulation_id not in self._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self._active_simulations[simulation_id]

        # 只允许删除已完成的仿真
        if simulation.status not in [SimulationStatus.COMPLETED, SimulationStatus.STOPPED, SimulationStatus.ERROR]:
            raise ValueError(f"只能删除已完成或停止的仿真")

        del self._active_simulations[simulation_id]

        # 在实际实现中，这里会清理存储中的数据


class SimulationQuery:
    """
    仿真状态查询

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, lifecycle: SimulationLifecycle):
        self.lifecycle = lifecycle

    def get_simulation_status(self, simulation_id: str) -> SimulationStatus:
        """
        获取仿真状态

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationStatus: 仿真状态
        """
        if simulation_id not in self.lifecycle._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        return self.lifecycle._active_simulations[simulation_id].status

    def get_simulation_config(self, simulation_id: str) -> SimulationConfig:
        """
        获取仿真配置

        Args:
            simulation_id: 仿真ID

        Returns:
            SimulationConfig: 仿真配置
        """
        if simulation_id not in self.lifecycle._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        return self.lifecycle._active_simulations[simulation_id].config

    def get_simulation_progress(self, simulation_id: str) -> ProgressInfo:
        """
        获取仿真进度

        Args:
            simulation_id: 仿真ID

        Returns:
            ProgressInfo: 进度信息
        """
        if simulation_id not in self.lifecycle._active_simulations:
            raise ValueError(f"仿真 {simulation_id} 不存在")

        simulation = self.lifecycle._active_simulations[simulation_id]
        total_rounds = simulation.config.total_rounds
        current_round = simulation.current_round

        percentage = (current_round / total_rounds * 100) if total_rounds > 0 else 0.0

        # 简单估算剩余时间
        estimated_remaining = None
        if simulation.start_time and current_round > 0:
            elapsed = (datetime.now() - simulation.start_time).total_seconds()
            if elapsed > 0:
                time_per_round = elapsed / current_round
                estimated_remaining = time_per_round * (total_rounds - current_round)

        return ProgressInfo(
            simulation_id=simulation_id,
            current_round=current_round,
            total_rounds=total_rounds,
            percentage=percentage,
            estimated_remaining=estimated_remaining,
            current_phase=self._get_current_phase(simulation)
        )

    def list_simulations(self, filters: Optional[QueryFilters] = None) -> List[Simulation]:
        """
        列出仿真

        Args:
            filters: 查询过滤器

        Returns:
            List[Simulation]: 仿真列表
        """
        if filters is None:
            filters = QueryFilters()

        simulations = list(self.lifecycle._active_simulations.values())

        # 应用过滤器
        if filters.status is not None:
            simulations = [s for s in simulations if s.status == filters.status]

        if filters.start_date is not None:
            simulations = [
                s for s in simulations
                if s.start_time and s.start_time >= filters.start_date
            ]

        if filters.end_date is not None:
            simulations = [
                s for s in simulations
                if s.start_time and s.start_time <= filters.end_date
            ]

        # 应用分页
        simulations = simulations[filters.offset:filters.offset + filters.limit]

        return simulations

    def _get_current_phase(self, simulation: Simulation) -> Optional[str]:
        """获取当前仿真阶段"""
        total_rounds = simulation.config.total_rounds
        current_round = simulation.current_round

        if current_round == 0:
            return "初始化"
        elif current_round >= total_rounds:
            return "完成"
        else:
            percentage = current_round / total_rounds
            if percentage < 0.25:
                return "早期阶段"
            elif percentage < 0.5:
                return "中期阶段"
            elif percentage < 0.75:
                return "后期阶段"
            else:
                return "收尾阶段"
