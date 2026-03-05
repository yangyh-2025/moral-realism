"""
道义现实主义ABM系统的模拟控制器

本模块提供SimulationController类，用于管理：
- 模拟生命周期（启动、暂停、恢复、停止）
- 回合执行（单回合、批处理、运行到完成）
- 检查点管理（保存、加载）
- 状态查询
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent
from src.agents.controller_agent import SimulationConfig, ControllerState


logger = logging.getLogger(__name__)


class ControllerStatus(Enum):
    """模拟控制器状态"""

    NOT_INITIALIZED = "not_initialized"  # 未初始化
    INITIALIZED = "initialized"  # 已初始化
    READY = "ready"  # 准备就绪
    RUNNING = "running"  # 正在运行
    PAUSED = "paused"  # 已暂停
    STOPPED = "stopped"  # 已停止
    COMPLETED = "completed"  # 已完成
    ERROR = "error"  # 发生错误


class ExecutionMode(Enum):
    """模拟执行模式"""

    STEP_BY_STEP = "step_by_step"  # 逐步执行
    BATCH = "batch"  # 批处理
    RUN_TO_COMPLETION = "run_to_completion"  # 运行到完成


@dataclass
class ControllerStats:
    """模拟控制器统计信息"""

    total_rounds_executed: int = 0  # 执行的总回合数
    total_rounds_scheduled: int = 0  # 调度的总回合数
    successful_rounds: int = 0  # 成功的回合数
    failed_rounds: int = 0  # 失败的回合数

    # 检查点统计
    checkpoints_saved: int = 0  # 保存的检查点数
    checkpoints_loaded: int = 0  # 加载的检查点数

    # 时间统计
    start_time: Optional[datetime] = None  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间
    total_execution_time: float = 0.0  # 总执行时间（秒）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "total_rounds_executed": self.total_rounds_executed,
            "total_rounds_scheduled": self.total_rounds_scheduled,
            "successful_rounds": self.successful_rounds,
            "failed_rounds": self.failed_rounds,
            "checkpoints_saved": self.checkpoints_saved,
            "checkpoints_loaded": self.checkpoints_loaded,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_execution_time": self.total_execution_time,
        }


class SimulationController:
    """
    模拟控制器类

    控制模拟生命周期和执行。

    提供的功能：
    - 模拟生命周期管理（启动、暂停、恢复、停止）
    - 回合执行（单回合、批处理、运行到完成）
    - 检查点管理（保存、加载）
    - 状态查询
    """

    def __init__(
        self,
        config: Optional[SimulationConfig] = None,
    ) -> None:
        """
        初始化模拟控制器

        Args:
            config: 模拟配置
        """
        self.config = config or SimulationConfig()

        # 状态跟踪
        self.status = ControllerStatus.INITIALIZED
        self.state = ControllerState()

        # 统计信息
        self.stats = ControllerStats()

        # 组件引用（待注入）
        self._agents: Dict[str, Agent] = {}
        self._round_executor: Optional[Any] = None
        self._data_storage: Optional[Any] = None
        self._state_manager: Optional[Any] = None
        self._performance_monitor: Optional[Any] = None

        # 执行模式
        self._execution_mode = ExecutionMode.STEP_BY_STEP

        logger.info(f"模拟控制器已初始化，配置: {self.config.max_rounds} 最大回合")

    def initialize(self) -> bool:
        """
        初始化控制器并准备执行

        Returns:
            初始化成功返回True
        """
        if self.status == ControllerStatus.RUNNING:
            logger.warning("控制器已在运行，无法初始化")
            return False

        # 验证必需组件
        if not self._agents:
            logger.warning("未注册代理，无法初始化")
            return False

        if self._round_executor is None:
            logger.warning("未配置回合执行器，无法初始化")
            return False

        # 将代理注册到互动管理器（如果可用）
        if hasattr(self._round_executor, "_interaction_manager"):
            interaction_mgr = self._round_executor._interaction_manager
            if interaction_mgr:
                for agent in self._agents.values():
                    interaction_mgr.register_agent(agent)

        self.status = ControllerStatus.READY
        logger.info("模拟控制器已初始化并就绪")
        return True

    def start(self) -> bool:
        """
        启动模拟执行

        Returns:
            启动成功返回True
        """
        if self.status != ControllerStatus.READY:
            logger.warning(f"无法从状态 {self.status.value} 启动")
            return False

        self.status = ControllerStatus.RUNNING
        self.state.is_running = True
        self.state.is_paused = False
        self.state.current_round = 0
        self.stats.start_time = datetime.now()

        logger.info("模拟已启动")
        return True

    def pause(self) -> bool:
        """
        暂停模拟执行

        Returns:
            暂停成功返回True
        """
        if self.status != ControllerStatus.RUNNING:
            logger.warning(f"无法从状态 {self.status.value} 暂停")
            return False

        self.status = ControllerStatus.PAUSED
        self.state.is_running = True
        self.state.is_paused = True

        logger.info("模拟已暂停")
        return True

    def resume(self) -> bool:
        """
        恢复模拟执行

        Returns:
            恢复成功返回True
        """
        if self.status != ControllerStatus.PAUSED:
            logger.warning(f"无法从状态 {self.status.value} 恢复")
            return False

        self.status = ControllerStatus.RUNNING
        self.state.is_running = True
        self.state.is_paused = False

        logger.info("模拟已恢复")
        return True

    def stop(self) -> bool:
        """
        停止模拟执行

        Returns:
            停止成功返回True
        """
        if self.status not in [
            ControllerStatus.RUNNING,
            ControllerStatus.PAUSED,
        ]:
            logger.warning(f"无法从状态 {self.status.value} 停止")
            return False

        self.status = ControllerStatus.STOPPED
        self.state.is_running = False
        self.state.is_paused = False
        self.stats.end_time = datetime.now()

        if self.stats.start_time:
            self.stats.total_execution_time = (
                self.stats.end_time - self.stats.start_time
            ).total_seconds()

        logger.info(f"模拟已停止，执行时间: {self.stats.total_execution_time:.2f}秒")
        return True

    def reset(self) -> None:
        """重置控制器状态以进行新的模拟"""
        self.status = ControllerStatus.INITIALIZED
        self.state = ControllerState()
        self.stats = ControllerStats()
        self.state.current_round = 0

        logger.info("控制器已重置")

    def execute_single_round(self) -> Optional[Dict[str, Any]]:
        """
        执行单个模拟回合

        Returns:
            回合结果字典，失败返回None
        """
        if self.status != ControllerStatus.RUNNING:
            logger.warning(f"无法从状态 {self.status.value} 执行回合")
            return None

        if self.state.current_round >= self.config.max_rounds:
            logger.info("达到最大回合数，模拟完成")
            self.status = ControllerStatus.COMPLETED
            self.stats.end_time = datetime.now()
            return None

        # 启动性能跟踪
        if self._performance_monitor:
            self._performance_monitor.start_round(self.state.current_round + 1)

        # 执行回合
        try:
            round_result = self._execute_round_internal()

            if round_result and round_result.get("is_successful", False):
                self.stats.successful_rounds += 1
            else:
                self.stats.failed_rounds += 1

            # 需要时保存检查点
            if self._should_checkpoint():
                self.save_checkpoint()

            self.stats.total_rounds_executed += 1

            return round_result
        except Exception as e:
            logger.error(f"回合执行失败: {e}", exc_info=True)
            self.stats.failed_rounds += 1
            self.status = ControllerStatus.ERROR
            return None
        finally:
            # 结束性能跟踪
            if self._performance_monitor:
                self._performance_monitor.end_round()

    def execute_rounds(self, n: int) -> List[Dict[str, Any]]:
        """
        执行n个模拟回合

        Args:
            n: 要执行的回合数

        Returns:
            回合结果列表
        """
        results = []

        for _ in range(n):
            if self.status != ControllerStatus.RUNNING:
                break

            result = self.execute_single_round()

            if result is None:
                break

            results.append(result)

        return results

    def run_to_completion(self) -> Dict[str, Any]:
        """
        运行模拟直到完成（最大回合数）

        Returns:
            执行结果摘要
        """
        self._execution_mode = ExecutionMode.RUN_TO_COMPLETION

        if not self.start():
            return {"status": "failed", "reason": "无法启动模拟"}

        results = []

        while self.status == ControllerStatus.RUNNING:
            result = self.execute_single_round()

            if result is None:
                break

            results.append(result)

        self.stop()

        return {
            "status": self.status.value,
            "total_rounds": len(results),
            "successful_rounds": self.stats.successful_rounds,
            "failed_rounds": self.stats.failed_rounds,
            "execution_time": self.stats.total_execution_time,
            "rounds": results,
        }

    def save_checkpoint(self, checkpoint_id: Optional[str] = None) -> Optional[str]:
        """
        将当前模拟状态保存为检查点

        Args:
            checkpoint_id: 可选的检查点ID

        Returns:
            保存的检查点路径，失败返回None
        """
        if self._state_manager is None or self._data_storage is None:
            logger.warning("无法保存检查点：state_manager或data_storage未配置")
            return None

        try:
            # 捕获状态
            snapshot = self._state_manager.capture_state(
                round_number=self.state.current_round,
                additional_context={
                    "controller_states": {
                        "current_round": self.state.current_round,
                        "is_running": self.state.is_running,
                        "is_paused": self.state.is_paused,
                        "total_decisions": self.state.total_decisions,
                        "total_interactions": self.state.total_interactions,
                        "event_count": self.state.event_count,
                    },
                    "workflow_states": {
                        "status": self.status.value,
                        "execution_mode": self._execution_mode.value,
                    },
                },
            )

            # 保存检查点
            state_dict = snapshot.to_dict()
            path = self._data_storage.save_checkpoint(
                simulation_state=state_dict,
                checkpoint_id=checkpoint_id,
            )

            if path:
                self.stats.checkpoints_saved += 1
                logger.info(f"检查点已保存到 {path}")

            return path
        except Exception as e:
            logger.error(f"检查点保存失败: {e}", exc_info=True)
            return None

    def load_checkpoint(self, checkpoint_id: str) -> bool:
        """
        从检查点加载模拟状态

        Args:
            checkpoint_id: 要加载的检查点ID

        Returns:
            加载成功返回True
        """
        if self._data_storage is None:
            logger.warning("无法加载检查点：data_storage未配置")
            return False

        try:
            # 加载检查点
            checkpoint = self._data_storage.load_checkpoint(checkpoint_id)
            if checkpoint is None:
                logger.error(f"未找到检查点: {checkpoint_id}")
                return False

            # 恢复状态
            if self._state_manager:
                from src.workflow.state_manager import SimulationSnapshot
                snapshot = SimulationSnapshot.from_dict(checkpoint.get("state", {}))

                if self._state_manager.restore_state(snapshot):
                    self.stats.checkpoints_loaded += 1

                    # 更新控制器状态
                    controller_states = checkpoint.get("state", {}).get(
                        "controller_states", {}
                    )

                    self.state.current_round = controller_states.get("current_round", 0)
                    self.state.is_running = controller_states.get("is_running", False)
                    self.state.is_paused = controller_states.get("is_paused", False)
                    self.state.total_decisions = controller_states.get(
                        "total_decisions", 0
                    )
                    self.state.total_interactions = controller_states.get(
                        "total_interactions", 0
                    )
                    self.state.event_count = controller_states.get("event_count", 0)

                    self.status = ControllerStatus.READY

                    logger.info(f"检查点已加载: {checkpoint_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"检查点加载失败: {e}", exc_info=True)
            return False

    def get_status(self) -> ControllerStatus:
        """
        获取当前控制器状态

        Returns:
            当前ControllerStatus
        """
        return self.status

    def get_performance_stats(self) -> Optional[Dict[str, Any]]:
        """
        获取性能统计信息

        Returns:
            性能统计字典，监控器未配置返回None
        """
        if self._performance_monitor is None:
            return None

        stats = self._performance_monitor.get_stats()
        return stats.to_dict()

    def get_controller_summary(self) -> Dict[str, Any]:
        """
        获取完整的控制器摘要

        Returns:
            包含控制器状态和统计信息的字典
        """
        return {
            "status": self.status.value,
            "config": {
                "max_rounds": self.config.max_rounds,
                "event_probability": self.config.event_probability,
                "checkpoint_interval": self.config.checkpoint_interval,
                "checkpoint_dir": self.config.checkpoint_dir,
                "log_level": self.config.log_level,
            },
            "state": {
                "current_round": self.state.current_round,
                "is_running": self.state.is_running,
                "is_paused": self.state.is_paused,
                "total_decisions": self.state.total_decisions,
                "total_interactions": self.state.total_interactions,
                "event_count": self.state.event_count,
            },
            "stats": self.stats.to_dict(),
            "performance": self.get_performance_stats(),
            "execution_mode": self._execution_mode.value,
        }

    # 组件注入方法

    def set_agents(self, agents: Dict[str, Agent]) -> None:
        """设置代理字典"""
        self._agents = agents
        logger.info(f"已注册 {len(agents)} 个代理")

    def set_round_executor(self, executor: Any) -> None:
        """设置回合执行器"""
        self._round_executor = executor
        logger.info("回合执行器已配置")

    def set_data_storage(self, storage: Any) -> None:
        """设置数据存储"""
        self._data_storage = storage
        logger.info("数据存储已配置")

    def set_state_manager(self, state_manager: Any) -> None:
        """设置状态管理器"""
        self._state_manager = state_manager
        logger.info("状态管理器已配置")

    def set_performance_monitor(self, monitor: Any) -> None:
        """设置性能监控器"""
        self._performance_monitor = monitor
        logger.info("性能监控器已配置")

    # 私有辅助方法

    def _should_checkpoint(self) -> bool:
        """检查是否应该保存检查点"""
        if self.config.checkpoint_interval <= 0:
            return False

        if self.state.current_round % self.config.checkpoint_interval == 0:
            return True

        return False

    def _execute_round_internal(self) -> Dict[str, Any]:
        """
        使用回合执行器内部执行回合

        Returns:
            回合结果字典
        """
        from src.workflow.round_executor import RoundContext
        from src.workflow.state_manager import SimulationSnapshot

        # 构建回合上下文
        context = RoundContext(
            round_number=self.state.current_round + 1,
            start_time=datetime.now(),
            agents=self._agents,
            dynamic_environment=getattr(
                self._round_executor, "_dynamic_env", None
            ),
            rule_environment=getattr(
                self._round_executor, "_rule_env", None
            ),
            interaction_manager=getattr(
                self._round_executor, "_interaction_manager", None
            ),
            behavior_selector=getattr(
                self._round_executor, "_behavior_selector", None
            ),
            metrics_calculator=getattr(
                self._round_executor, "_metrics_calculator", None
            ),
            data_storage=self._data_storage,
            event_scheduler=getattr(
                self._round_executor, "_event_scheduler", None
            ),
        )

        # 执行回合
        result = self._round_executor.execute_round(context)

        # 更新控制器状态
        self.state.current_round += 1
        self.state.total_decisions += result.decisions_count
        self.state.total_interactions += result.interactions_executed
        self.state.event_count += result.events_generated

        return result.to_dict()

    def is_running(self) -> bool:
        """检查模拟是否正在运行"""
        return self.status == ControllerStatus.RUNNING

    def is_paused(self) -> bool:
        """检查模拟是否已暂停"""
        return self.status == ControllerStatus.PAUSED

    def is_ready(self) -> bool:
        """检查模拟是否就绪"""
        return self.status == ControllerStatus.READY

    def get_remaining_rounds(self) -> int:
        """获取剩余回合数"""
        return max(0, self.config.max_rounds - self.state.current_round)
