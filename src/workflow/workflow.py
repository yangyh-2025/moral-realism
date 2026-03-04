"""
工作流编排模块，用于道义现实主义ABM系统

本模块提供Workflow类，用于：
- 协调模拟执行
- 组件初始化
- 模拟终止和清理
- 生成最终报告

核心概念：
- WorkflowStatus: 工作流执行状态
- WorkflowConfig: 工作流配置
- WorkflowResult: 工作流执行结果
- Workflow: 主工作流编排器
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import logging

from src.models.agent import Agent


logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """
    工作流执行状态枚举

    定义工作流执行过程中的各种状态：
    - NOT_INITIALIZED: 未初始化
    - INITIALIZING: 正在初始化
    - INITIALIZED: 已初始化
    - READY: 准备就绪
    - RUNNING: 正在运行
    - PAUSED: 已暂停
    - STOPPED: 已停止
    - COMPLETED: 已完成
    - FINALIZING: 正在最终化
    - FINALIZED: 已最终化
    - ERROR: 发生错误
    """

    NOT_INITIALIZED = "not_initialized"  # 未初始化
    INITIALIZING = "initializing"  # 正在初始化
    INITIALIZED = "initialized"  # 已初始化
    READY = "ready"  # 准备就绪
    RUNNING = "running"  # 正在运行
    PAUSED = "paused"  # 已暂停
    STOPPED = "stopped"  # 已停止
    COMPLETED = "completed"  # 已完成
    FINALIZING = "finalizing"  # 正在最终化
    FINALIZED = "finalized"  # 已最终化
    ERROR = "error"  # 发生错误


@dataclass
class WorkflowConfig:
    """
    工作流执行配置类

    配置工作流执行的各项参数：
    - enable_checkpoints: 是否启用检查点功能
    - enable_performance_monitoring: 是否启用性能监控
    - enable_interventions: 是否启用干预功能
    - max_execution_time_seconds: 最大执行时间（秒）
    - completion_callback: 完成条件回调函数
    """

    enable_checkpoints: bool = True  # 是否启用检查点
    enable_performance_monitoring: bool = True  # 是否启用性能监控
    enable_interventions: bool = True  # 是否启用干预

    # Completion conditions
    max_execution_time_seconds: Optional[int] = None  # 最大执行时间
    completion_callback: Optional[Callable[[Dict[str, Any]], bool]] = None  # 完成回调


@dataclass
class WorkflowResult:
    """
    工作流执行结果类

    记录工作流执行的完整结果和统计信息。
    """

    status: WorkflowStatus  # 执行状态
    start_time: Optional[datetime] = None  # 开始时间
    end_time: Optional[datetime] = None  # 结束时间
    total_duration_seconds: Optional[float] = None  # 总持续时间（秒）

    # Execution summary
    total_rounds: int = 0  # 总回合数
    successful_rounds: int = 0  # 成功回合数
    failed_rounds: int = 0  # 失败回合数

    # Intervention summary
    interventions_processed: int = 0  # 处理的干预数量

    # Checkpoint summary
    checkpoints_saved: int = 0  # 保存的检查点数量
    checkpoints_loaded: int = 0  # 加载的检查点数量

    # Error tracking
    errors: List[str] = field(default_factory=list)  # 错误列表
    warnings: List[str] = field(default_factory=list)  # 警告列表

    # Final report
    final_report: Optional[Dict[str, Any]] = None  # 最终报告

    def to_dict(self) -> Dict[str, Any]:
        """将结果转换为字典格式"""
        return {
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": self.total_duration_seconds,
            "total_rounds": self.total_rounds,
            "successful_rounds": self.successful_rounds,
            "failed_rounds": self.failed_rounds,
            "interventions_processed": self.interventions_processed,
            "checkpoints_saved": self.checkpoints_saved,
            "checkpoints_loaded": self.checkpoints_loaded,
            "errors": self.errors,
            "warnings": self.warnings,
            "final_report": self.final_report,
        }


class Workflow:
    """
    工作流编排器类

    负责协调整个模拟组件的执行流程。

    主要功能：
    - 组件初始化和协调
    - 主模拟循环控制
    - 干预处理
    - 最终化和报告生成
    """

    def __init__(
        self,
        config: Optional[WorkflowConfig] = None,
    ) -> None:
        """
        初始化工作流

        Args:
            config: 工作流配置对象，如果为None则使用默认配置
        """
        self.config = config or WorkflowConfig()

        # Status tracking
        self.status = WorkflowStatus.NOT_INITIALIZED  # 当前状态

        # Component references
        self._simulation_controller: Optional[Any] = None  # 模拟控制器
        self._intervention_manager: Optional[Any] = None  # 干预管理器
        self._performance_monitor: Optional[Any] = None  # 性能监控器
        self._state_manager: Optional[Any] = None  # 状态管理器
        self._data_storage: Optional[Any] = None  # 数据存储

        # Results tracking
        self._result = WorkflowResult(status=self.status)  # 执行结果追踪

        # Completion hooks
        self._completion_hooks: List[Callable] = []  # 完成回调钩子
        self._round_hooks: List[Callable] = []  # 回合回调钩子

        logger.info("工作流已初始化")

    def initialize(self, components: Dict[str, Any]) -> bool:
        """
        初始化工作流和所有组件

        Args:
            components: 包含所有模拟组件的字典，包括：
                       - simulation_controller: 模拟控制器
                       - intervention_manager: 干预管理器
                       - performance_monitor: 性能监控器
                       - state_manager: 状态管理器
                       - data_storage: 数据存储
                       - agents: 代理字典
                       - round_executor: 回合执行器
                       - dynamic_environment: 动态环境
                       - rule_environment: 规则环境
                       - static_environment: 静态环境
                       - interaction_manager: 互动管理器

        Returns:
            bool: 初始化成功返回True，否则返回False

        Raises:
            RuntimeError: 当关键组件初始化失败时抛出异常
        """
        self.status = WorkflowStatus.INITIALIZING
        logger.info("正在初始化工作流...")

        try:
            # Extract components
            self._simulation_controller = components.get("simulation_controller")
            self._intervention_manager = components.get("intervention_manager")
            self._performance_monitor = components.get("performance_monitor")
            self._state_manager = components.get("state_manager")
            self._data_storage = components.get("data_storage")

            # Inject components into controller
            if self._simulation_controller:
                self._simulation_controller.set_agents(
                    components.get("agents", {})
                )
                self._simulation_controller.set_round_executor(
                    components.get("round_executor")
                )
                self._simulation_controller.set_data_storage(self._data_storage)
                self._simulation_controller.set_state_manager(self._state_manager)
                self._simulation_controller.set_performance_monitor(
                    self._performance_monitor
                )

                # Initialize controller
                if not self._simulation_controller.initialize():
                    raise RuntimeError("Controller initialization failed")

            # Register components with state manager
            if self._state_manager:
                self._state_manager.register_agents(
                    components.get("agents", {})
                )
                self._state_manager.register_environments({
                    "dynamic_environment": components.get("dynamic_environment"),
                    "rule_environment": components.get("rule_environment"),
                    "static_environment": components.get("static_environment"),
                })
                self._state_manager.register_interaction_manager(
                    components.get("interaction_manager")
                )

            # Register events with state manager
            if self._state_manager and components.get("dynamic_environment"):
                self._state_manager.register_events(
                    components.get("dynamic_environment").get_event_history(),
                    [],
                )

            self.status = WorkflowStatus.INITIALIZED
            logger.info("Workflow initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Workflow initialization failed: {e}", exc_info=True)
            self.status = WorkflowStatus.ERROR
            self._result.errors.append(f"Initialization failed: {e}")
            return False

    def start(self) -> bool:
        """
        启动工作流执行

        Returns:
            bool: 启动成功返回True，否则返回False
        """
        if self.status not in [
            WorkflowStatus.INITIALIZED,
            WorkflowStatus.READY,
            WorkflowStatus.PAUSED,
        ]:
            logger.warning(f"无法从状态 {self.status.value} 启动")
            return False

        # Start controller
        # 启动模拟控制器
        if self._simulation_controller and not self._simulation_controller.start():
            logger.warning("控制器启动失败")
            return False

        self.status = WorkflowStatus.RUNNING
        self._result.status = self.status
        self._result.start_time = datetime.now()

        logger.info("工作流已启动")
        return True

    def pause(self) -> bool:
        """
        暂停工作流执行

        Returns:
            bool: 暂停成功返回True，否则返回False
        """
        if self.status != WorkflowStatus.RUNNING:
            logger.warning(f"无法从状态 {self.status.value} 暂停")
            return False

        # Pause controller
        # 暂停模拟控制器
        if self._simulation_controller and not self._simulation_controller.pause():
            logger.warning("控制器暂停失败")
            return False

        self.status = WorkflowStatus.PAUSED
        logger.info("工作流已暂停")
        return True

    def resume(self) -> bool:
        """
        恢复工作流执行

        Returns:
            bool: 恢复成功返回True，否则返回False
        """
        if self.status != WorkflowStatus.PAUSED:
            logger.warning(f"无法从状态 {self.status.value} 恢复")
            return False

        # Resume controller
        # 恢复模拟控制器
        if self._simulation_controller and not self._simulation_controller.resume():
            logger.warning("控制器恢复失败")
            return False

        self.status = WorkflowStatus.RUNNING
        logger.info("工作流已恢复")
        return True

    def stop(self) -> bool:
        """
        停止工作流执行

        Returns:
            bool: 停止成功返回True，否则返回False
        """
        if self.status not in [
            WorkflowStatus.RUNNING,
            WorkflowStatus.PAUSED,
        ]:
            logger.warning(f"无法从状态 {self.status.value} 停止")
            return False

        # Stop controller
        # 停止模拟控制器
        if self._simulation_controller and not self._simulation_controller.stop():
            logger.warning("控制器停止失败")
            return False

        self.status = WorkflowStatus.STOPPED
        self._resultresult.end_time = datetime.now()

        if self._result.start_time:
            self._result.total_duration_seconds = (
                self._result.end_time - self._result.start_time
            ).total_seconds()

        logger.info("工作流已停止")
        return True

    def run(self, rounds: Optional[int] = None) -> Dict[str, Any]:
        """
        运行工作流

        Args:
            rounds: 要运行的回合数，None表示运行到完成条件满足

        Returns:
            Dict[str, Any]: 执行结果摘要
                - status: 执行状态
                - total_rounds: 总回合数
                - successful_rounds: 成功回合数
                - failed_rounds: 失败回合数
                - result: 完整结果字典
        """
        if not self.start():
            return {"status": "failed", "reason": "无法启动工作流"}

        try:
            # Execute main loop
            # 执行主循环
            if rounds is None:
                result = self._run_to_completion()
            else:
                result = self._run_rounds(rounds)

            # Finalize
            # 最终化
            self.finalize()

            return result

        except Exception as e:
            logger.error(f"工作流执行失败: {e}", exc_info=True)
            self.status = WorkflowStatus.ERROR
            self._result.errors.append(f"执行失败: {e}")
            return {
                "status": "error",
                "reason": str(e),
                "result": self._result.to_dict(),
            }

    def finalize(self) -> bool:
        """
        最终化工作流并生成最终报告

        Returns:
            bool: 最终化成功返回True，否则返回False
        """
        self.status = WorkflowStatus.FINALIZING
        logger.info("正在最终化工作流...")

        try:
            # Generate final report
            report = self._generate_final_report()
            self._result.final_report = report

            # Log performance summary
            if self._performance_monitor:
                self._performance_monitor.log_summary()

            # Stop controller if still running
            if self._simulation_controller and self._simulation_controller.is_running():
                self._simulation_controller.stop()

            # Execute completion hooks
            self._execute_completion_hooks()

            self.status = WorkflowStatus.FINALIZED
            self._result.status = self.status

            logger.info("Workflow finalized")
            return True

        except Exception as e:
            logger.error(f"Workflow finalization failed: {e}", exc_info=True)
            self.status = WorkflowStatus.ERROR
            self._result.errors.append(f"Finalization failed: {e}")
            return False

    def add_completion_hook(self, hook: Callable) -> None:
        """
        添加工作流完成时调用的钩子

        Args:
            hook: 完成时调用的函数
        """
        self._completion_hooks.append(hook)
        logger.debug("已添加完成钩子")

    def add_round_hook(self, hook: Callable) -> None:
        """
        添加每回合后调用的钩子

        Args:
            hook: 每回合后调用的函数
        """
        self._round_hooks.append(hook)
        logger.debug("已添加回合钩子")

    def get_status(self) -> WorkflowStatus:
        """
        获取当前工作流状态

        Returns:
            WorkflowStatus: 当前工作流状态
        """
        return self.status

    def get_result(self) -> WorkflowResult:
        """
        获取工作流执行结果

        Returns:
            WorkflowResult: 当前工作流结果对象
        """
        return self._result

    def get_summary(self) -> Dict[str, Any]:
        """
        获取工作流摘要信息

        Returns:
            Dict[str, Any]: 包含当前状态信息的字典
        """
        controller_summary = {}
        if self._simulation_controller:
            controller_summary = self._simulation_controller.get_controller_summary()

        intervention_stats = {}
        if self._intervention_manager:
            intervention_stats = self._intervention_manager.get_stats().to_dict()

        return {
            "status": self.status.value,
            "controller": controller_summary,
            "interventions": intervention_stats,
            "result": self._result.to_dict(),
        }

    # Private methods

    def _run_to_completion(self) -> Dict[str, Any]:
        """
        Run simulation to completion.

        Returns:
            Execution result summary.
        """
        logger.info("正在运行模拟直到完成条件满足")

        # Start time tracking
        start_time = datetime.now()

        if self.config.max_execution_time_seconds:
            timeout_time = start_time.timestamp() + (
                self.config.max_execution_time_seconds
            )
        else:
            timeout_time = None

        # Main loop
        while self.status == WorkflowStatus.RUNNING:
            # Check timeout
            if timeout_time and datetime.now().timestamp() > timeout_time:
                logger.warning("Execution timeout reached")
                self._result.warnings.append("Execution timeout reached")
                break

            # Check completion conditions
            if self.config.completion_callback:
                context = self._build_completion_context()
                if self.config.completion_callback(context):
                    logger.info("Completion condition met")
                    break

            # Handle interventions
            if self.config.enable_interventions:
                self._handle_interventions()

            # Execute single round
            round_result = self._simulation_controller.execute_single_round()

            if round_result is None:
                logger.info("Round execution returned None, stopping")
                break

            # Update result tracking
            self._result.total_rounds += 1
            if round_result.get("is_successful", False):
                self._result.successful_rounds += 1
            else:
                self._result.failed_rounds += 1

            # Execute round hooks
            for hook in self._round_hooks:
                try:
                    hook(round_result)
                except Exception as e:
                    logger.error(f"Round hook error: {e}")

            # Check if controller stopped
            if not self._simulation_controller.is_running():
                logger.info("Controller stopped, ending loop")
                break

        # Stop if not already stopped
        if self.status == WorkflowStatus.RUNNING:
            self.stop()

        return {
            "status": "completed",
            "total_rounds": self._result.total_rounds,
            "successful_rounds": self._result.successful_rounds,
            "failed_rounds": self._result.failed_rounds,
            "result": self._result.to_dict(),
        }

    def _run_rounds(self, n: int) -> Dict[str, Any]:
        """
        Run specified number of rounds.

        Args:
            n: Number of rounds to run.

        Returns:
            Execution result summary.
        """
        logger.info(f"Running {n} rounds")

        results = []

        for i in range(n):
            if self.status != WorkflowStatus.RUNNING:
                break

            # Handle interventions
            if self.config.enable_interventions:
                self._handle_interventions()

            # Execute round
            round_result = self._simulation_controller.execute_single_round()

            if round_result is None:
                break

            # Update tracking
            self._result.total_rounds += 1
            if round_result.get("is_successful", False):
                self._result.successful_rounds += 1
            else:
                self._result.failed_rounds += 1

            results.append(round_result)

            # Execute round hooks
            for hook in self._round_hooks:
                try:
                    hook(round_result)
                except Exception as e:
                    logger.error(f"Round hook error: {e}")

            # Check if controller stopped
            if not self._simulation_controller.is_running():
                break

        # Stop if not already stopped
        if self.status == WorkflowStatus.RUNNING:
            self.stop()

        return {
            "status": "completed",
            "total_rounds": len(results),
            "successful_rounds": self._result.successful_rounds,
            "failed_rounds": self._result.failed_rounds,
            "rounds": results,
            "result": self._result.to_dict(),
        }

    def _handle_interventions(self) -> None:
        """Handle pending interventions."""
        if self._intervention_manager is None:
            return

        # Check control interventions
        if self._intervention_manager.pause_requested():
            self.pause()
        elif self._intervention_manager.resume_requested():
            self.resume()
        elif self._intervention_manager.stop_requested():
            self.stop()

        # Execute pending interventions
        if self._intervention_manager.has_pending():
            context = self._build_intervention_context()
            executed = self._intervention_manager.execute_pending_interventions(context)
            self._result.interventions_processed += len(executed)

    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final execution report."""
        report = {
            "workflow_summary": {
                "status": self.status.value,
                "total_duration_seconds": self._result.total_duration_seconds,
                "total_rounds": self._result.total_rounds,
                "successful_rounds": self._result.successful_rounds,
                "failed_rounds": self._result.failed_rounds,
                "interventions_processed": self._result.interventions_processed,
            },
        }

        # Add controller summary
        if self._simulation_controller:
            report["controller_summary"] = (
                self._simulation_controller.get_controller_summary()
            )

        # Add performance summary
        if self._performance_monitor:
            report["performance_summary"] = (
                self._performance_monitor.get_stats().to_dict()
            )

        # Add intervention summary
        if self._intervention_manager:
            report["intervention_summary"] = (
                self._intervention_manager.get_stats().to_dict()
            )

        return report

    def _execute_completion_hooks(self) -> None:
        """Execute all completion hooks."""
        for hook in self._completion_hooks:
            try:
                hook(self._result)
            except Exception as e:
                logger.error(f"Completion hook error: {e}")

    def _build_completion_context(self) -> Dict[str, Any]:
        """Build context for completion callback."""
        return {
            "round_number": self._result.total_rounds,
            "successful_rounds": self._result.successful_rounds,
            "failed_rounds": self._result.failed_rounds,
            "controller_summary": (
                self._simulation_controller.get_controller_summary()
                if self._simulation_controller
                else {}
            ),
        }

    def _build_intervention_context(self) -> Dict[str, Any]:
        """Build context for intervention execution."""
        return {
            "agents": (
                self._simulation_controller.get_controller_summary()
                .get("agents", {})
                if self._simulation_controller
                else {}
            ),
            "current_round": (
                self._simulation_controller.get_controller_summary()
                .get("state", {})
                .get("current_round", 0)
                if self._simulation_controller
                else 0
            ),
            "data_storage": self._data_storage,
            "state_manager": self._state_manager,
        }
