"""
User intervention mechanism for moral realism ABM system.

This module provides Intervention dataclass and InterventionManager
for handling user interventions during simulation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging
import uuid
from queue import PriorityQueue


logger = logging.getLogger(__name__)


class InterventionType(Enum):
    """Types of user interventions."""

    # Control operations
    PAUSE = "pause"
    RESUME = "resume"
    STOP = "stop"

    # Parameter modifications
    MODIFY_AGENT_PARAMETER = "modify_agent_parameter"
    MODIFY_ENVIRONMENT = "modify_environment"
    MODIFY_SIMULATION_CONFIG = "modify_simulation_config"

    # Event injection
    INJECT_EVENT = "inject_event"
    INJECT_DECISION = "inject_decision"

    # Manual overrides
    OVERRIDE_DECISION = "override_decision"
    OVERRIDE_INTERACTION = "override_interaction"

    # Checkpoint operations
    SAVE_CHECKPOINT = "save_checkpoint"
    LOAD_CHECKPOINT = "load_checkpoint"

    # Info requests
    GET_STATUS = "get_status"
    GET_METRICS = "get_metrics"


class InterventionPriority(Enum):
    """Priority levels for interventions."""

    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class Intervention:
    """A user intervention in simulation."""

    intervention_id: str
    intervention_type: InterventionType
    priority: InterventionPriority
    timestamp: datetime
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    user_id: Optional[str] = None
    reason: Optional[str] = None
    queued_at: Optional[datetime] = None
    executed: bool = False
    execution_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        if self.queued_at is None:
            self.queued_at = datetime.now()

    def execute_success(self, result: Optional[Dict[str, Any]] = None) -> None:
        self.executed = True
        self.execution_time = datetime.now()
        self.result = result

    def execute_failed(self, error: str) -> None:
        self.executed = True
        self.execution_time = datetime.now()
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intervention_id": self.intervention_id,
            "intervention_type": self.intervention_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp.isoformat(),
            "target_type": self.target_type,
            "target_id": self.target_id,
            "parameters": self.parameters,
            "description": self.description,
            "user_id": self.user_id,
            "reason": self.reason,
            "queued_at": self.queued_at.isoformat() if self.queued_at else None,
            "executed": self.executed,
            "execution_time": self.execution_time.isoformat() if self.execution_time else None,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class InterventionStats:
    """Statistics about interventions."""

    total_queued: int = 0
    total_executed: int = 0
    total_failed: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_queued": self.total_queued,
            "total_executed": self.total_executed,
            "total_failed": self.total_failed,
            "by_type": self.by_type,
        }


class InterventionManager:
    """Manage user interventions during simulation."""

    def __init__(
        self,
        auto_execute: bool = False,
        max_queue_size: int = 1000,
    ) -> None:
        self._auto_execute = auto_execute
        self._max_queue_size = max_queue_size
        self._queue: PriorityQueue = PriorityQueue()
        self._interventions: Dict[str, Intervention] = {}
        self._executed_interventions: List[Intervention] = []
        self._stats = InterventionStats()
        self._pause_requested: bool = False
        self._resume_requested: bool = False
        self._stop_requested: bool = False

    def queue_intervention(self, intervention: Intervention) -> bool:
        if len(self._interventions) >= self._max_queue_size:
            logger.warning(f"Intervention queue full, cannot add {intervention.intervention_id}")
            return False

        self._interventions[intervention.intervention_id] = intervention
        self._queue.put((intervention.priority.value, intervention.timestamp.timestamp(), intervention))

        self._stats.total_queued += 1
        type_val = intervention.intervention_type.value
        self._stats.by_type[type_val] = self._stats.by_type.get(type_val, 0) + 1

        logger.info(f"Queued intervention {intervention.intervention_id}: {type_val}")

        if self._auto_execute:
            self._execute_single(intervention)

        if intervention.intervention_type == InterventionType.PAUSE:
            self._pause_requested = True
        elif intervention.intervention_type == InterventionType.RESUME:
            self._resume_requested = True
        elif intervention.intervention_type == InterventionType.STOP:
            self._stop_requested = True

        return True

    def execute_pending_interventions(
        self,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Intervention]:
        if context is None:
            context = {}

        executed = []

        while not self._queue.empty():
            _, _, intervention = self._queue.get()

            if intervention.executed:
                continue

            try:
                self._execute_single(intervention, context)
                executed.append(intervention)
            except Exception as e:
                intervention.execute_failed(str(e))
                self._stats.total_failed += 1
                logger.error(f"Intervention {intervention.intervention_id} failed: {e}")

        return executed

    def has_pending(self) -> bool:
        return not self._queue.empty()

    def get_pending_count(self) -> int:
        return self._queue.qsize()

    def pause_requested(self) -> bool:
        result = self._pause_requested
        self._pause_requested = False
        return result

    def resume_requested(self) -> bool:
        result = self._resume_requested
        self._resume_requested = False
        return result

    def stop_requested(self) -> bool:
        result = self._stop_requested
        self._stop_requested = False
        return result

    def get_intervention(self, intervention_id: str) -> Optional[Intervention]:
        return self._interventions.get(intervention_id)

    def get_history(
        self,
        intervention_type: Optional[InterventionType] = None,
        limit: Optional[int] = None,
    ) -> List[Intervention]:
        history = self._executed_interventions.copy()

        if intervention_type is not None:
            history = [i for i in history if i.intervention_type == intervention_type]

        if limit is not None:
            history = history[-limit:]

        return history

    def get_stats(self) -> InterventionStats:
        return self._stats

    def clear_queue(self) -> None:
        self._queue = PriorityQueue()
        logger.info("Cleared intervention queue")

    def clear_history(self) -> None:
        self._executed_interventions.clear()
        logger.info("Cleared intervention history")

    def reset(self) -> None:
        self._queue = PriorityQueue()
        self._interventions.clear()
        self._executed_interventions.clear()
        self._stats = InterventionStats()
        self._pause_requested = False
        self._resume_requested = False
        self._stop_requested = False
        logger.info("Intervention manager reset")

    @staticmethod
    def create_pause_intervention(
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Intervention:
        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=InterventionType.PAUSE,
            priority=InterventionPriority.CRITICAL,
            timestamp=datetime.now(),
            description=description or "Pause simulation",
            user_id=user_id,
        )

    @staticmethod
    def create_resume_intervention(
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Intervention:
        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=InterventionType.RESUME,
            priority=InterventionPriority.CRITICAL,
            timestamp=datetime.now(),
            description=description or "Resume simulation",
            user_id=user_id,
        )

    @staticmethod
    def create_stop_intervention(
        reason: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Intervention:
        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=InterventionType.STOP,
            priority=InterventionPriority.CRITICAL,
            timestamp=datetime.now(),
            description="Stop simulation",
            reason=reason,
            user_id=user_id,
        )

    @staticmethod
    def create_param_modification(
        target_type: str,
        target_id: str,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Intervention:
        if target_type == "environment":
            intervention_type = InterventionType.MODIFY_ENVIRONMENT
        elif target_type == "simulation":
            intervention_type = InterventionType.MODIFY_SIMULATION_CONFIG
        else:
            intervention_type = InterventionType.MODIFY_AGENT_PARAMETER

        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=intervention_type,
            priority=InterventionPriority.MEDIUM,
            timestamp=datetime.now(),
            target_type=target_type,
            target_id=target_id,
            parameters=parameters,
            description=f"Modify {target_type} {target_id}",
            user_id=user_id,
        )

    @staticmethod
    def create_event_injection(
        event: Any,
        description: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Intervention:
        event_dict = event.to_dict() if hasattr(event, "to_dict") else event

        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=InterventionType.INJECT_EVENT,
            priority=InterventionPriority.HIGH,
            timestamp=datetime.now(),
            parameters={"event": event_dict},
            description=description or "Inject event",
            user_id=user_id,
        )

    @staticmethod
    def create_checkpoint_save(
        checkpoint_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Intervention:
        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=InterventionType.SAVE_CHECKPOINT,
            priority=InterventionPriority.HIGH,
            timestamp=datetime.now(),
            parameters={"checkpoint_id": checkpoint_id},
            description="Save simulation checkpoint",
            user_id=user_id,
        )

    @staticmethod
    def create_checkpoint_load(
        checkpoint_id: str,
        user_id: Optional[str] = None,
    ) -> Intervention:
        return Intervention(
            intervention_id=f"int_{uuid.uuid4().hex[:8]}",
            intervention_type=InterventionType.LOAD_CHECKPOINT,
            priority=InterventionPriority.CRITICAL,
            timestamp=datetime.now(),
            parameters={"checkpoint_id": checkpoint_id},
            description=f"Load checkpoint {checkpoint_id}",
            user_id=user_id,
        )

    def _execute_single(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if intervention.executed:
            return

        logger.info(f"Executing intervention {intervention.intervention_id}: {intervention.intervention_type.value}")

        if intervention.intervention_type == InterventionType.PAUSE:
            self._execute_pause(intervention, context)
        elif intervention.intervention_type == InterventionType.RESUME:
            self._execute_resume(intervention, context)
        elif intervention.intervention_type == InterventionType.STOP:
            self._execute_stop(intervention, context)
        elif intervention.intervention_type == InterventionType.SAVE_CHECKPOINT:
            self._execute_save_checkpoint(intervention, context)
        elif intervention.intervention_type == InterventionType.LOAD_CHECKPOINT:
            self._execute_load_checkpoint(intervention, context)
        elif intervention.intervention_type == InterventionType.MODIFY_AGENT_PARAMETER:
            self._execute_modify_agent(intervention, context)
        elif intervention.intervention_type == InterventionType.INJECT_EVENT:
            self._execute_inject_event(intervention, context)
        else:
            intervention.execute_success({"message": "Executed"})

        if intervention.executed:
            self._executed_interventions.append(intervention)
            self._stats.total_executed += 1

    def _execute_pause(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._pause_requested = True
        intervention.execute_success({"status": "paused"})

    def _execute_resume(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._resume_requested = True
        intervention.execute_success({"status": "resumed"})

    def _execute_stop(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._stop_requested = True
        intervention.execute_success({"status": "stopped"})

    def _execute_save_checkpoint(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if context and "data_storage" in context:
            storage = context["data_storage"]
            if "state_manager" in context:
                state_manager = context["state_manager"]
                snapshot = state_manager.capture_state(
                    round_number=context.get("current_round", 0),
                )

                checkpoint_id = intervention.parameters.get("checkpoint_id")
                state_dict = snapshot.to_dict()

                path = storage.save_checkpoint(
                    state_dict,
                    checkpoint_id,
                )

                intervention.execute_success({"checkpoint_path": path})
            else:
                intervention.execute_failed("No state manager in context")
        else:
            intervention.execute_failed("No data storage or context provided")

    def _execute_load_checkpoint(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if context and "data_storage" in context:
            storage = context["data_storage"]
            checkpoint_id = intervention.parameters["checkpoint_id"]

            checkpoint = storage.load_checkpoint(checkpoint_id)

            if checkpoint:
                intervention.execute_success({"checkpoint": checkpoint})
            else:
                intervention.execute_failed(f"Checkpoint not found: {checkpoint_id}")
        else:
            intervention.execute_failed("No data storage in context")

    def _execute_modify_agent(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if context and "agents" in context:
            agents = context["agents"]
            target_id = intervention.target_id
            parameters = intervention.parameters

            if target_id in agents:
                agent = agents[target_id]

                for key, value in parameters.items():
                    if hasattr(agent, key) and not callable(getattr(agent, key)):
                        setattr(agent, key, value)

                intervention.execute_success({
                    "agent_id": target_id,
                    "modified": list(parameters.keys()),
                })
            else:
                intervention.execute_failed(f"Agent not found: {target_id}")
        else:
            intervention.execute_failed("No agents in context")

    def _execute_inject_event(
        self,
        intervention: Intervention,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if context and "dynamic_environment" in context:
            env = context["dynamic_environment"]
            event_dict = intervention.parameters.get("event", {})

            event_id = env.add_custom_event(
                event_type=event_dict.get("sub_type", "custom"),
                description=event_dict.get("description", "Injected event"),
                severity=event_dict.get("severity", 50.0),
                affected_agents=event_dict.get("affected_agents", []),
                context=event_dict.get("context", {}),
            )

            intervention.execute_success({
                "event_id": event_id,
                "injected_event": event_dict,
            })
        else:
            intervention.execute_failed("No dynamic environment in context")
