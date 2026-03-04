"""
Workflow orchestration for moral realism ABM system.

This module provides Workflow class which coordinates
simulation execution, component initialization, and
finalization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import logging

from src.models.agent import Agent


logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Status of workflow execution."""

    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FINALIZING = "finalizing"
    FINALIZED = "finalized"
    ERROR = "error"


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""

    enable_checkpoints: bool = True
    enable_performance_monitoring: bool = True
    enable_interventions: bool = True

    # Completion conditions
    max_execution_time_seconds: Optional[int] = None
    completion_callback: Optional[Callable[[Dict[str, Any]], bool]] = None


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    status: WorkflowStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None

    # Execution summary
    total_rounds: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0

    # Intervention summary
    interventions_processed: int = 0

    # Checkpoint summary
    checkpoints_saved: int = 0
    checkpoints_loaded: int = 0

    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Final report
    final_report: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
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
    Orchestrate simulation workflow.

    Provides:
    - Component initialization and coordination
    - Main simulation loop
    - Intervention handling
    - Finalization and report generation
    """

    def __init__(
        self,
        config: Optional[WorkflowConfig] = None,
    ) -> None:
        """
        Initialize workflow.

        Args:
            config: Workflow configuration.
        """
        self.config = config or WorkflowConfig()

        # Status tracking
        self.status = WorkflowStatus.NOT_INITIALIZED

        # Component references
        self._simulation_controller: Optional[Any] = None
        self._intervention_manager: Optional[Any] = None
        self._performance_monitor: Optional[Any] = None
        self._state_manager: Optional[Any] = None
        self._data_storage: Optional[Any] = None

        # Results tracking
        self._result = WorkflowResult(status=self.status)

        # Completion hooks
        self._completion_hooks: List[Callable] = []
        self._round_hooks: List[Callable] = []

        logger.info("Workflow initialized")

    def initialize(self, components: Dict[str, Any]) -> bool:
        """
        Initialize workflow and all components.

        Args:
            components: Dictionary of simulation components.

        Returns:
            True if initialization successful.
        """
        self.status = WorkflowStatus.INITIALIZING
        logger.info("Initializing workflow...")

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
        Start workflow execution.

        Returns:
            True if start successful.
        """
        if self.status not in [
            WorkflowStatus.INITIALIZED,
            WorkflowStatus.READY,
            WorkflowStatus.PAUSED,
        ]:
            logger.warning(f"Cannot start from status {self.status.value}")
            return False

        # Start controller
        if self._simulation_controller and not self._simulation_controller.start():
            logger.warning("Controller start failed")
            return False

        self.status = WorkflowStatus.RUNNING
        self._result.status = self.status
        self._result.start_time = datetime.now()

        logger.info("Workflow started")
        return True

    def pause(self) -> bool:
        """
        Pause workflow execution.

        Returns:
            True if pause successful.
        """
        if self.status != WorkflowStatus.RUNNING:
            logger.warning(f"Cannot pause from status {self.status.value}")
            return False

        # Pause controller
        if self._simulation_controller and not self._simulation_controller.pause():
            logger.warning("Controller pause failed")
            return False

        self.status = WorkflowStatus.PAUSED
        logger.info("Workflow paused")
        return True

    def resume(self) -> bool:
        """
        Resume workflow execution.

        Returns:
            True if resume successful.
        """
        if self.status != WorkflowStatus.PAUSED:
            logger.warning(f"Cannot resume from status {self.status.value}")
            return False

        # Resume controller
        if self._simulation_controller and not self._simulation_controller.resume():
            logger.warning("Controller resume failed")
            return False

        self.status = WorkflowStatus.RUNNING
        logger.info("Workflow resumed")
        return True

    def stop(self) -> bool:
        """
        Stop workflow execution.

        Returns:
            True if stop successful.
        """
        if self.status not in [
            WorkflowStatus.RUNNING,
            WorkflowStatus.PAUSED,
        ]:
            logger.warning(f"Cannot stop from status {self.status.value}")
            return False

        # Stop controller
        if self._simulation_controller and not self._simulation_controller.stop():
            logger.warning("Controller stop failed")
            return False

        self.status = WorkflowStatus.STOPPED
        self._result.end_time = datetime.now()

        if self._result.start_time:
            self._result.total_duration_seconds = (
                self._result.end_time - self._result.start_time
            ).total_seconds()

        logger.info("Workflow stopped")
        return True

    def run(self, rounds: Optional[int] = None) -> Dict[str, Any]:
        """
        Run workflow for specified number of rounds.

        Args:
            rounds: Number of rounds to run (None for run to completion).

        Returns:
            Execution result summary.
        """
        if not self.start():
            return {"status": "failed", "reason": "Could not start workflow"}

        try:
            # Execute main loop
            if rounds is None:
                result = self._run_to_completion()
            else:
                result = self._run_rounds(rounds)

            # Finalize
            self.finalize()

            return result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            self.status = WorkflowStatus.ERROR
            self._result.errors.append(f"Execution failed: {e}")
            return {
                "status": "error",
                "reason": str(e),
                "result": self._result.to_dict(),
            }

    def finalize(self) -> bool:
        """
        Finalize workflow and generate final report.

        Returns:
            True if finalization successful.
        """
        self.status = WorkflowStatus.FINALIZING
        logger.info("Finalizing workflow...")

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
        Add a hook to be called on workflow completion.

        Args:
            hook: Function to call on completion.
        """
        self._completion_hooks.append(hook)
        logger.debug("Added completion hook")

    def add_round_hook(self, hook: Callable) -> None:
        """
        Add a hook to be called after each round.

        Args:
            hook: Function to call after round.
        """
        self._round_hooks.append(hook)
        logger.debug("Added round hook")

    def get_status(self) -> WorkflowStatus:
        """
        Get current workflow status.

        Returns:
            Current WorkflowStatus.
        """
        return self.status

    def get_result(self) -> WorkflowResult:
        """
        Get workflow result.

        Returns:
            Current WorkflowResult.
        """
        return self._result

    def get_summary(self) -> Dict[str, Any]:
        """
        Get workflow summary.

        Returns:
            Dictionary with current state information.
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
        logger.info("Running simulation to completion")

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
