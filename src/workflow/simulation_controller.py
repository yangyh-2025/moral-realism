"""
Simulation controller for moral realism ABM system.

This module provides SimulationController class which manages
simulation lifecycle, round execution, and checkpoint management.
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
    """Status of simulation controller."""

    NOT_INITIALIZED = "not_initialized"
    INITIALIZED = "initialized"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    COMPLETED = "completed"
    ERROR = "error"


class ExecutionMode(Enum):
    """Modes of simulation execution."""

    STEP_BY_STEP = "step_by_step"
    BATCH = "batch"
    RUN_TO_COMPLETION = "run_to_completion"


@dataclass
class ControllerStats:
    """Statistics for simulation controller."""

    total_rounds_executed: int = 0
    total_rounds_scheduled: int = 0
    successful_rounds: int = 0
    failed_rounds: int = 0

    # Checkpoint statistics
    checkpoints_saved: int = 0
    checkpoints_loaded: int = 0

    # Time statistics
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
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
    Control simulation lifecycle and execution.

    Provides:
    - Simulation lifecycle management (start, pause, resume, stop)
    - Round execution (single, batch, run to completion)
    - Checkpoint management (save, load)
    - Status queries
    """

    def __init__(
        self,
        config: Optional[SimulationConfig] = None,
    ) -> None:
        """
        Initialize simulation controller.

        Args:
            config: Simulation configuration.
        """
        self.config = config or SimulationConfig()

        # State tracking
        self.status = ControllerStatus.INITIALIZED
        self.state = ControllerState()

        # Statistics
        self.stats = ControllerStats()

        # Component references (to be injected)
        self._agents: Dict[str, Agent] = {}
        self._round_executor: Optional[Any] = None
        self._data_storage: Optional[Any] = None
        self._state_manager: Optional[Any] = None
        self._performance_monitor: Optional[Any] = None

        # Execution mode
        self._execution_mode = ExecutionMode.STEP_BY_STEP

        logger.info(f"SimulationController initialized with config: {self.config.max_rounds} max rounds")

    def initialize(self) -> bool:
        """
        Initialize controller and prepare for execution.

        Returns:
            True if initialization successful.
        """
        if self.status == ControllerStatus.RUNNING:
            logger.warning("Controller already running, cannot initialize")
            return False

        # Validate required components
        if not self._agents:
            logger.warning("No agents registered, cannot initialize")
            return False

        if self._round_executor is None:
            logger.warning("No round executor configured, cannot initialize")
            return False

        # Register agents with interaction manager if available
        if hasattr(self._round_executor, "_interaction_manager"):
            interaction_mgr = self._round_executor._interaction_manager
            if interaction_mgr:
                for agent in self._agents.values():
                    interaction_mgr.register_agent(agent)

        self.status = ControllerStatus.READY
        logger.info("SimulationController initialized and ready")
        return True

    def start(self) -> bool:
        """
        Start simulation execution.

        Returns:
            True if start successful.
        """
        if self.status != ControllerStatus.READY:
            logger.warning(f"Cannot start from status {self.status.value}")
            return False

        self.status = ControllerStatus.RUNNING
        self.state.is_running = True
        self.state.is_paused = False
        self.state.current_round = 0
        self.stats.start_time = datetime.now()

        logger.info("Simulation started")
        return True

    def pause(self) -> bool:
        """
        Pause simulation execution.

        Returns:
            True if pause successful.
        """
        if self.status != ControllerStatus.RUNNING:
            logger.warning(f"Cannot pause from status {self.status.value}")
            return False

        self.status = ControllerStatus.PAUSED
        self.state.is_running = True
        self.state.is_paused = True

        logger.info("Simulation paused")
        return True

    def resume(self) -> bool:
        """
        Resume simulation execution.

        Returns:
            True if resume successful.
        """
        if self.status != ControllerStatus.PAUSED:
            logger.warning(f"Cannot resume from status {self.status.value}")
            return False

        self.status = ControllerStatus.RUNNING
        self.state.is_running = True
        self.state.is_paused = False

        logger.info("Simulation resumed")
        return True

    def stop(self) -> bool:
        """
        Stop simulation execution.

        Returns:
            True if stop successful.
        """
        if self.status not in [
            ControllerStatus.RUNNING,
            ControllerStatus.PAUSED,
        ]:
            logger.warning(f"Cannot stop from status {self.status.value}")
            return False

        self.status = ControllerStatus.STOPPED
        self.state.is_running = False
        self.state.is_paused = False
        self.stats.end_time = datetime.now()

        if self.stats.start_time:
            self.stats.total_execution_time = (
                self.stats.end_time - self.stats.start_time
            ).total_seconds()

        logger.info(f"Simulation stopped after {self.stats.total_execution_time:.2f}s")
        return True

    def reset(self) -> None:
        """Reset controller state for new simulation."""
        self.status = ControllerStatus.INITIALIZED
        self.state = ControllerState()
        self.stats = ControllerStats()
        self.state.current_round = 0

        logger.info("Controller reset")

    def execute_single_round(self) -> Optional[Dict[str, Any]]:
        """
        Execute a single simulation round.

        Returns:
            Round result dictionary, or None if execution failed.
        """
        if self.status != ControllerStatus.RUNNING:
            logger.warning(f"Cannot execute round from status {self.status.value}")
            return None

        if self.state.current_round >= self.config.max_rounds:
            logger.info("Max rounds reached, simulation complete")
            self.status = ControllerStatus.COMPLETED
            self.stats.end_time = datetime.now()
            return None

        # Start performance tracking
        if self._performance_monitor:
            self._performance_monitor.start_round(self.state.current_round + 1)

        # Execute round
        try:
            round_result = self._execute_round_internal()

            if round_result and round_result.get("is_successful", False):
                self.stats.successful_rounds += 1
            else:
                self.stats.failed_rounds += 1

            # Checkpoint if needed
            if self._should_checkpoint():
                self.save_checkpoint()

            self.stats.total_rounds_executed += 1

            return round_result

        except Exception as e:
            logger.error(f"Round execution failed: {e}", exc_info=True)
            self.stats.failed_rounds += 1
            self.status = ControllerStatus.ERROR
            return None

        finally:
            # End performance tracking
            if self._performance_monitor:
                self._performance_monitor.end_round()

    def execute_rounds(self, n: int) -> List[Dict[str, Any]]:
        """
        Execute n simulation rounds.

        Args:
            n: Number of rounds to execute.

        Returns:
            List of round results.
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
        Run simulation to completion (max rounds).

        Returns:
            Summary of execution results.
        """
        self._execution_mode = ExecutionMode.RUN_TO_COMPLETION

        if not self.start():
            return {"status": "failed", "reason": "Could not start simulation"}

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
        Save current simulation state as checkpoint.

        Args:
            checkpoint_id: Optional checkpoint ID.

        Returns:
            Path to saved checkpoint, or None if failed.
        """
        if self._state_manager is None or self._data_storage is None:
            logger.warning("Cannot save checkpoint: state_manager or data_storage not configured")
            return None

        try:
            # Capture state
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

            # Save checkpoint
            state_dict = snapshot.to_dict()
            path = self._data_storage.save_checkpoint(
                simulation_state=state_dict,
                checkpoint_id=checkpoint_id,
            )

            if path:
                self.stats.checkpoints_saved += 1
                logger.info(f"Checkpoint saved to {path}")

            return path

        except Exception as e:
            logger.error(f"Checkpoint save failed: {e}", exc_info=True)
            return None

    def load_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Load simulation state from checkpoint.

        Args:
            checkpoint_id: The checkpoint ID to load.

        Returns:
            True if load successful.
        """
        if self._data_storage is None:
            logger.warning("Cannot load checkpoint: data_storage not configured")
            return False

        try:
            # Load checkpoint
            checkpoint = self._data_storage.load_checkpoint(checkpoint_id)

            if checkpoint is None:
                logger.error(f"Checkpoint not found: {checkpoint_id}")
                return False

            # Restore state
            if self._state_manager:
                from src.workflow.state_manager import SimulationSnapshot
                snapshot = SimulationSnapshot.from_dict(checkpoint.get("state", {}))

                if self._state_manager.restore_state(snapshot):
                    self.stats.checkpoints_loaded += 1

                    # Update controller state
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

                    logger.info(f"Checkpoint loaded: {checkpoint_id}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Checkpoint load failed: {e}", exc_info=True)
            return False

    def get_status(self) -> ControllerStatus:
        """
        Get current controller status.

        Returns:
            Current ControllerStatus.
        """
        return self.status

    def get_performance_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get performance statistics.

        Returns:
            Performance statistics dictionary, or None if monitor not configured.
        """
        if self._performance_monitor is None:
            return None

        stats = self._performance_monitor.get_stats()
        return stats.to_dict()

    def get_controller_summary(self) -> Dict[str, Any]:
        """
        Get complete controller summary.

        Returns:
            Dictionary with controller state and statistics.
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

    # Component injection methods

    def set_agents(self, agents: Dict[str, Agent]) -> None:
        """Set agents dictionary."""
        self._agents = agents
        logger.info(f"Registered {len(agents)} agents")

    def set_round_executor(self, executor: Any) -> None:
        """Set round executor."""
        self._round_executor = executor
        logger.info("Round executor configured")

    def set_data_storage(self, storage: Any) -> None:
        """Set data storage."""
        self._data_storage = storage
        logger.info("Data storage configured")

    def set_state_manager(self, state_manager: Any) -> None:
        """Set state manager."""
        self._state_manager = state_manager
        logger.info("State manager configured")

    def set_performance_monitor(self, monitor: Any) -> None:
        """Set performance monitor."""
        self._performance_monitor = monitor
        logger.info("Performance monitor configured")

    # Private helper methods

    def _should_checkpoint(self) -> bool:
        """Check if checkpoint should be saved."""
        if self.config.checkpoint_interval <= 0:
            return False

        if self.state.current_round % self.config.checkpoint_interval == 0:
            return True

        return False

    def _execute_round_internal(self) -> Dict[str, Any]:
        """
        Internal round execution using round executor.

        Returns:
            Round result dictionary.
        """
        from src.workflow.round_executor import RoundContext
        from src.workflow.state_manager import SimulationSnapshot

        # Build round context
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

        # Execute round
        result = self._round_executor.execute_round(context)

        # Update controller state
        self.state.current_round += 1
        self.state.total_decisions += result.decisions_count
        self.state.total_interactions += result.interactions_executed
        self.state.event_count += result.events_generated

        return result.to_dict()

    def is_running(self) -> bool:
        """Check if simulation is running."""
        return self.status == ControllerStatus.RUNNING

    def is_paused(self) -> bool:
        """Check if simulation is paused."""
        return self.status == ControllerStatus.PAUSED

    def is_ready(self) -> bool:
        """Check if simulation is ready."""
        return self.status == ControllerStatus.READY

    def get_remaining_rounds(self) -> int:
        """Get number of remaining rounds."""
        return max(0, self.config.max_rounds - self.state.current_round)
