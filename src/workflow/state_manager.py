"""
State manager for moral realism ABM system.

This module provides StateManager class which captures and restores
complete simulation states for checkpointing and recovery.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import logging
import copy

from src.models.agent import Agent, AgentType
from src.environment.dynamic_environment import Event
from src.environment.rule_environment import OrderType


logger = logging.getLogger(__name__)


@dataclass
class SimulationSnapshot:
    """
    Snapshot of complete simulation state at a point in time.

    Contains all necessary state information to restore a simulation
    to the exact same configuration.
    """

    snapshot_id: str
    timestamp: datetime
    round_number: int

    # Agent states
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Environment states
    environment_states: Dict[str, Any] = field(default_factory=dict)

    # Interaction history states
    interaction_states: Dict[str, Any] = field(default_factory=dict)

    # Event states
    event_states: List[Dict[str, Any]] = field(default_factory=list)
    pending_events: List[Dict[str, Any]] = field(default_factory=list)

    # Metrics states
    metrics_states: Dict[str, Any] = field(default_factory=dict)

    # Controller/Workflow states
    controller_states: Dict[str, Any] = field(default_factory=dict)
    workflow_states: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "round_number": self.round_number,
            "agent_states": self.agent_states,
            "environment_states": self.environment_states,
            "interaction_states": self.interaction_states,
            "event_states": self.event_states,
            "pending_events": self.pending_events,
            "metrics_states": self.metrics_states,
            "controller_states": self.controller_states,
            "workflow_states": self.workflow_states,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationSnapshot":
        """Create snapshot from dictionary."""
        return cls(
            snapshot_id=data["snapshot_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            round_number=data["round_number"],
            agent_states=data.get("agent_states", {}),
            environment_states=data.get("environment_states", {}),
            interaction_states=data.get("interaction_states", {}),
            event_states=data.get("event_states", []),
            pending_events=data.get("pending_events", []),
            metrics_states=data.get("metrics_states", {}),
            controller_states=data.get("controller_states", {}),
            workflow_states=data.get("workflow_states", {}),
        )


@dataclass
class StateDiff:
    """
    Difference between two simulation states.

    Used to track what changed between rounds or checkpoints.
    """

    from_round: int
    to_round: int
    timestamp: datetime

    # Changed components
    agents_changed: List[str] = field(default_factory=list)
    agents_added: List[str] = field(default_factory=list)
    agents_removed: List[str] = field(default_factory=list)

    events_added: int = 0
    interactions_count: int = 0

    # Metrics changes
    metrics_delta: Dict[str, Any] = field(default_factory=dict)

    # Order type changes
    order_type_changed: bool = False
    previous_order_type: Optional[str] = None
    new_order_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert diff to dictionary."""
        return {
            "from_round": self.from_round,
            "to_round": self.to_round,
            "timestamp": self.timestamp.isoformat(),
            "agents_changed": self.agents_changed,
            "agents_added": self.agents_added,
            "agents_removed": self.agents_removed,
            "events_added": self.events_added,
            "interactions_count": self.interactions_count,
            "metrics_delta": self.metrics_delta,
            "order_type_changed": self.order_type_changed,
            "previous_order_type": self.previous_order_type,
            "new_order_type": self.new_order_type,
        }


class StateManager:
    """
    Manages simulation state capture and restoration.

    Provides functionality to:
    - Capture complete simulation state for checkpointing
    - Restore simulation from saved state
    - Calculate differences between states
    - Validate state consistency
    """

    def __init__(self, enable_diff_tracking: bool = True) -> None:
        """
        Initialize state manager.

        Args:
            enable_diff_tracking: Whether to track state differences.
        """
        self._enable_diff_tracking = enable_diff_tracking
        self._snapshot_counter = 0
        self._previous_snapshot: Optional[SimulationSnapshot] = None

        # State components (will be populated during capture)
        self._agents: Dict[str, Agent] = {}
        self._environments: Dict[str, Any] = {}
        self._interaction_manager: Optional[Any] = None
        self._event_history: List[Event] = []
        self._pending_events: List[Event] = []

    def register_agents(self, agents: Dict[str, Agent]) -> None:
        """
        Register agents for state capture.

        Args:
            agents: Dictionary mapping agent IDs to Agent instances.
        """
        self._agents = agents

    def register_environments(self, environments: Dict[str, Any]) -> None:
        """
        Register environment components for state capture.

        Args:
            environments: Dictionary of environment components.
        """
        self._environments = environments

    def register_interaction_manager(self, interaction_manager: Any) -> None:
        """
        Register interaction manager for state capture.

        Args:
            interaction_manager: The interaction manager instance.
        """
        self._interaction_manager = interaction_manager

    def register_events(
        self,
        event_history: List[Event],
        pending_events: Optional[List[Event]] = None,
    ) -> None:
        """
        Register event lists for state capture.

        Args:
            event_history: List of historical events.
            pending_events: List of pending events (optional).
        """
        self._event_history = event_history
        if pending_events is not None:
            self._pending_events = pending_events

    def capture_state(
        self,
        round_number: int,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> SimulationSnapshot:
        """
        Capture complete simulation state.

        Args:
            round_number: Current simulation round.
            additional_context: Additional context to include.

        Returns:
            SimulationSnapshot containing all state information.
        """
        self._snapshot_counter += 1
        snapshot_id = f"snapshot_{self._snapshot_counter}"

        logger.info(f"Capturing state at round {round_number}: {snapshot_id}")

        # Capture agent states
        agent_states = self._capture_agent_states()

        # Capture environment states
        environment_states = self._capture_environment_states()

        # Capture interaction states
        interaction_states = self._capture_interaction_states()

        # Capture event states
        event_states = [e.to_dict() for e in self._event_history]
        pending_events = [e.to_dict() for e in self._pending_events]

        # Capture metrics states
        metrics_states = self._capture_metrics_states()

        # Create snapshot
        snapshot = SimulationSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            round_number=round_number,
            agent_states=agent_states,
            environment_states=environment_states,
            interaction_states=interaction_states,
            event_states=event_states,
            pending_events=pending_events,
            metrics_states=metrics_states,
            controller_states=additional_context.get("controller_states", {})
            if additional_context else {},
            workflow_states=additional_context.get("workflow_states", {})
            if additional_context else {},
        )

        # Update previous snapshot for diff tracking
        if self._enable_diff_tracking:
            self._previous_snapshot = snapshot

        return snapshot

    def restore_state(
        self,
        snapshot: SimulationSnapshot,
        agents_mutator: Optional[callable] = None,
    ) -> bool:
        """
        Restore simulation state from snapshot.

        Args:
            snapshot: The snapshot to restore.
            agents_mutator: Optional function to apply to restored agents.

        Returns:
            True if restoration successful, False otherwise.
        """
        logger.info(
            f"Restoring state from snapshot {snapshot.snapshot_id} "
            f"at round {snapshot.round_number}"
        )

        try:
            # Restore agent states
            self._restore_agent_states(snapshot.agent_states, agents_mutator)

            # Restore environment states
            self._restore_environment_states(snapshot.environment_states)

            # Restore interaction states
            self._restore_interaction_states(snapshot.interaction_states)

            # Restore event states
            self._restore_event_states(snapshot.event_states, snapshot.pending_events)

            # Restore metrics states
            self._restore_metrics_states(snapshot.metrics_states)

            # Restore controller/workflow states
            self._restore_controller_states(snapshot.controller_states)
            self._restore_workflow_states(snapshot.workflow_states)

            logger.info("State restoration completed successfully")
            return True

        except Exception as e:
            logger.error(f"State restoration failed: {e}")
            return False

    def get_state_diff(
        self,
        old_state: Optional[SimulationSnapshot] = None,
        new_state: Optional[SimulationSnapshot] = None,
    ) -> StateDiff:
        """
        Calculate difference between two states.

        If states not provided, uses stored previous snapshot.

        Args:
            old_state: Previous state (optional).
            new_state: Current state (optional).

        Returns:
            StateDiff describing what changed.
        """
        if old_state is None:
            old_state = self._previous_snapshot

        if new_state is None:
            new_state = self._capture_state_for_diff()

        if old_state is None:
            # First snapshot, no diff possible
            return StateDiff(
                from_round=0,
                to_round=new_state.round_number,
                timestamp=datetime.now(),
            )

        diff = StateDiff(
            from_round=old_state.round_number,
            to_round=new_state.round_number,
            timestamp=datetime.now(),
        )

        # Calculate agent changes
        self._calculate_agent_diff(old_state, new_state, diff)

        # Calculate event changes
        diff.events_added = len(new_state.event_states) - len(old_state.event_states)

        # Calculate interaction count
        if new_state.interaction_states:
            diff.interactions_count = new_state.interaction_states.get(
                "total_interactions", 0
            )

        # Calculate metrics delta
        self._calculate_metrics_diff(old_state, new_state, diff)

        # Check order type changes
        self._check_order_type_change(old_state, new_state, diff)

        return diff

    def validate_state(self, snapshot: SimulationSnapshot) -> Tuple[bool, List[str]]:
        """
        Validate a snapshot for consistency.

        Args:
            snapshot: The snapshot to validate.

        Returns:
            Tuple Tuple[is_valid, list of error messages].
        """
        errors = []

        # Check agent states
        for agent_id, agent_state in snapshot.agent_states.items():
            if not agent_state.get("agent_id"):
                errors.append(f"Agent{agent_id} missing agent_id")

            if not agent_state.get("name"):
                errors.append(f"Agent{agent_id} missing name")

            if "relations" not in agent_state:
                errors.append(f"Agent{agent_id} missing relations")

        # Check environment states
        for env_name, env_state in snapshot.environment_states.items():
            if not env_state:
                errors.append(f"Environment {env_name} has empty state")

        # Check round number consistency
        if snapshot.round_number < 0:
            errors.append(f"Invalid round number: {snapshot.round_number}")

        is_valid = len(errors) == 0

        if not is_valid:
            logger.warning(f"State validation failed: {errors}")

        return is_valid, errors

    # Private methods for state capture/restore

    def _capture_agent_states(self) -> Dict[str, Dict[str, Any]]:
        """Capture state of all registered agents."""
        agent_states = {}

        for agent_id, agent in self._agents.items():
            agent_states[agent_id] = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "name_zh": agent.name_zh,
                "agent_type": agent.agent_type.value,
                "leadership_type": agent.leadership_type.value,
                "is_active": agent.is_active,
                "is_alive": agent.is_alive,
                "relations": dict(agent.relations),
                "capability_tier": agent.get_capability_tier(),
                "capability_index": (
                    agent.capability.get_capability_index()
                    if agent.capability else None
                ),
                "history_length": len(agent.history),
            }

        return agent_states

    def _capture_environment_states(self) -> Dict[str, Any]:
        """Capture state of all registered environments."""
        environment_states = {}

        for env_name, env in self._environments.items():
            if hasattr(env, "get_environment_summary"):
                environment_states[env_name] = env.get_environment_summary()
            elif hasattr(env, "to_dict"):
                environment_states[env_name] = env.to_dict()
            else:
                environment_states[env_name] = str(type(env))

        return environment_states

    def _capture_interaction_states(self) -> Dict[str, Any]:
        """Capture state of interaction manager."""
        if self._interaction_manager is None:
            return {}

        if hasattr(self._interaction_manager, "get_interaction_summary"):
            return self._interaction_manager.get_interaction_summary()

        return {}

    def _capture_metrics_states(self) -> Dict[str, Any]:
        """Capture metrics states."""
        # Metrics will be captured from metrics calculator
        return {}

    def _capture_state_for_diff(self) -> SimulationSnapshot:
        """Capture minimal state for diff calculation."""
        return SimulationSnapshot(
            snapshot_id="temp_diff",
            timestamp=datetime.now(),
            round_number=0,
            agent_states=self._capture_agent_states(),
            environment_states=self._capture_environment_states(),
            interaction_states=self._capture_interaction_states(),
            event_states=[e.to_dict() for e in self._event_history],
            pending_events=[e.to_dict() for e in self._pending_events],
            metrics_states=self._capture_metrics_states(),
        )

    def _restore_agent_states(
        self,
        agent_states: Dict[str, Dict[str, Any]],
        agents_mutator: Optional[callable] = None,
    ) -> None:
        """Restore agent states."""
        for agent_id, state in agent_states.items():
            agent = self._agents.get(agent_id)
            if agent:
                agent.is_active = state.get("is_active", True)
                agent.is_alive = state.get("is_alive", True)
                agent.relations = state.get("relations", {})

                if agents_mutator:
                    agents_mutator(agent, state)

    def _restore_environment_states(
        self,
        environment_states: Dict[str, Any],
    ) -> None:
        """Restore environment states."""
        # Environment state restoration is environment-specific
        # This is a placeholder for actual restoration logic
        pass

    def _restore_interaction_states(self, interaction_states: Dict[str, Any]) -> None:
        """Restore interaction states."""
        # Interaction state restoration is manager-specific
        # This is a placeholder for actual restoration logic
        pass

    def _restore_event_states(
        self,
        event_states: List[Dict[str, Any]],
        pending_events: List[Dict[str, Any]],
    ) -> None:
        """Restore event states."""
        logger.info(f"Restoring {len(event_states)} historical events")
        logger.info(f"Restoring {len(pending_events)} pending events")
        # Actual event restoration would reconstruct Event objects
        # This is a placeholder

    def _restore_metrics_states(self, metrics_states: Dict[str, Any]) -> None:
        """Restore metrics states."""
        # Metrics state restoration is calculator-specific
        pass

    def _restore_controller_states(self, controller_states: Dict[str, Any]) -> None:
        """Restore controller states."""
        pass

    def _restore_workflow_states(self, workflow_states: Dict[str, Any]) -> None:
        """Restore workflow states."""
        pass

    def _calculate_agent_diff(
        self,
        old_state: SimulationSnapshot,
        new_state: SimulationSnapshot,
        diff: StateDiff,
    ) -> None:
        """Calculate agent differences between states."""
        old_agents = set(old_state.agent_states.keys())
        new_agents = set(new_state.agent_states.keys())

        diff.agents_added = list(new_agents - old_agents)
        diff.agents_removed = list(old_agents - new_agents)

        # Check for changes in existing agents
        for agent_id in old_agents & new_agents:
            old_agent = old_state.agent_states[agent_id]
            new_agent = new_state.agent_states[agent_id]

            if old_agent != new_agent:
                diff.agents_changed.append(agent_id)

    def _calculate_metrics_diff(
        self,
        old_state: SimulationSnapshot,
        new_state: SimulationSnapshot,
        diff: StateDiff,
    ) -> None:
        """Calculate metrics differences."""
        old_metrics = old_state.metrics_states
        new_metrics = new_state.metrics_states

        # Calculate deltas for common metrics
        for key in set(old_metrics.keys()) | set(new_metrics.keys()):
            old_value = old_metrics.get(key)
            new_value = new_metrics.get(key)

            if old_value != new_value:
                diff.metrics_delta[key] = {
                    "old": old_value,
                    "new": new_value,
                    "delta": None,
                }

                # Calculate numeric delta if possible
                try:
                    diff.metrics_delta[key]["delta"] = new_value - old_value
                except TypeError:
                    pass

    def _check_order_type_change(
        self,
        old_state: SimulationSnapshot,
        new_state: SimulationSnapshot,
        diff: StateDiff,
    ) -> None:
        """Check for order type changes."""
        old_order = None
        new_order = None

        # Extract order type from environment states or metrics
        if old_state.environment_states:
            for env_state in old_state.environment_states.values():
                if isinstance(env_state, dict) and "order_type" in env_state:
                    old_order = env_state["order_type"]
                    break

        if new_state.environment_states:
            for env_state in new_state.environment_states.values():
                if isinstance(env_state, dict) and "order_type" in env_state:
                    new_order = env_state["order_type"]
                    break

        diff.order_type_changed = old_order != new_order
        diff.previous_order_type = old_order
        diff.new_order_type = new_order
