"""
Round executor for moral realism ABM system.

This module provides RoundExecutor class which executes
a single simulation round with the complete flow:
event generation, distribution, decision-making, interactions,
rule application, and metrics calculation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import logging

from src.models.agent import Agent
from src.environment.dynamic_environment import Event
from src.environment.rule_environment import MoralEvaluation


logger = logging.getLogger(__name__)


class RoundPhase(Enum):
    """Phases of round execution."""

    PREPARATION = "preparation"
    EVENT_GENERATION = "event_generation"
    EVENT_DISTRIBUTION = "event_distribution"
    AGENT_DECISION_MAKING = "agent_decision_making"
    INTERACTION_EXECUTION = "interaction_execution"
    RULE_APPLICATION = "rule_application"
    METRICS_CALCULATION = "metrics_calculation"
    SYSTEMIC_INTERACTION = "systemic_interaction"
    CLEANUP = "cleanup"


@dataclass
class RoundContext:
    """
    Context object passed through round execution.

    Contains all necessary references and state for round phases.
    """

    round_number: int
    start_time: datetime

    # Component references
    agents: Dict[str, Agent]
    dynamic_environment: Any
    rule_environment: Any
    interaction_manager: Any
    behavior_selector: Any
    metrics_calculator: Any
    data_storage: Any
    event_scheduler: Any

    # Round-specific state
    events: List[Event] = field(default_factory=list)
    agent_events: Dict[str, List[Event]] = field(default_factory=dict)
    decisions: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interactions: List[Any] = field(default_factory=list)

    # Moral evaluations (from rule environment)
    moral_evaluations: Dict[str, List[MoralEvaluation]] = field(default_factory=dict)

    # Metrics results
    metrics: Dict[str, Any] = field(default_factory=dict)

    # Systemic interaction results
    systemic_results: Dict[str, Any] = field(default_factory=dict)

    # Persistence settings
    persistence: bool = True
    decision_persistence: bool = True
    interaction_persistence: bool = True

    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        logger.error(f"[Round {self.round_number}] {message}")

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)
        logger.warning(f"[Round {self.round_number}] {message}")


@dataclass
class RoundResult:
    """
    Result of a single round execution.

    Contains all outputs and metrics from round execution.
    """

    round_number: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None

    # Phase results
    phases_completed: List[RoundPhase] = field(default_factory=list)
    phases_failed: Dict[RoundPhase, str] = field(default_factory=dict)

    # Event results
    events_generated: int = 0
    events_processed: int = 0

    # Decision results
    decisions_count: int = 0
    decisions_success_count: int = 0

    # Interaction results
    interactions_executed: int = 0
    interactions_success_count: int = 0

    # Rule application results
    moral_evaluations: Dict[str, List[MoralEvaluation]] = field(default_factory=dict)
    capability_changes_validated: int = 0
    capability_changes_rejected: int = 0

    # Metrics results
    metrics: Dict[str, Any] = field(default_factory=dict)

    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Status flags
    is_complete: bool = False
    is_successful: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "round_number": self.round_number,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "phases_completed": [p.value for p in self.phases_completed],
            "phases_failed": {k.value: v for k, v in self.phases_failed.items()},
            "events_generated": self.events_generated,
            "events_processed": self.events_processed,
            "decisions_count": self.decisions_count,
            "decisions_success_count": self.decisions_success_count,
            "interactions_executed": self.interactions_executed,
            "interactions_success_count": self.interactions_success_count,
            "capability_changes_validated": self.capability_changes_validated,
            "capability_changes_rejected": self.capability_changes_rejected,
            "metrics_summary": self._get_metrics_summary(),
            "errors": self.errors,
            "warnings": self.warnings,
            "is_complete": self.is_complete,
            "is_successful": self.is_successful,
        }

    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of metrics."""
        if not self.metrics:
            return {}

        return {
            "agent_count": self.metrics.get("agent_count", 0),
            "pattern_type": self.metrics.get("pattern_type", ""),
            "power_concentration": self.metrics.get("system_metrics", {}).get("power_concentration", 0),
            "order_stability": self.metrics.get("system_metrics", {}).get("order_stability", 0),
        }


class RoundExecutor:
    """
    Execute single simulation rounds.

    Implements the complete round execution flow:
    1. PREPARATION - Validate and create context
    2. EVENT_GENERATION - Get all pending events
    3. EVENT_DISTRIBUTION - Distribute events to affected agents
    4. AGENT_DECISION_MAKING - Collect all agent decisions
    5. INTERACTION_EXECUTION - Execute agent interactions
    6. RULE_APPLICATION - Apply rules and validate changes
    7. METRICS_CALCULATION - Calculate and store metrics
    8. CLEANUP - Record history and update statistics
    """

    def __init__(
        self,
        enable_detailed_logging: bool = False,
    ) -> None:
        """
        Initialize round executor.

        Args:
            enable_detailed_logging: Enable verbose logging.
        """
        self._enable_detailed_logging = enable_detailed_logging
        self._phase_hooks: Dict[RoundPhase, List[callable]] = {}

    def execute_round(self, context: RoundContext) -> RoundResult:
        """
        Execute a complete simulation round.

        Args:
            context: The round context with all component references.

        Returns:
            RoundResult with execution outcomes.
        """
        result = RoundResult(
            round_number=context.round_number,
            start_time=context.start_time,
        )

        logger.info(f"=== Starting Round {context.round_number} ===")

        # Execute phases
        try:
            self._phase_preparation(context, result)
            self._phase_event_generation(context, result)
            self._phase_event_distribution(context, result)
            self._phase_agent_decision_making(context, result)
            self._phase_interaction_execution(context, result)
            self._phase_systemic_interaction(context, result)
            self._phase_rule_application(context, result)
            self._phase_metrics_calculation(context, result)
            self._phase_cleanup(context, result)

            result.end_time = datetime.now()
            result.duration_seconds = (
                result.end_time - result.start_time
            ).total_seconds()
            result.is_complete = True
            result.is_successful = len(result.errors) == 0

            logger.info(
                f"=== Round {context.round_number} completed in "
                f"{result.duration_seconds:.3f}s ==="
            )

        except Exception as e:
            result.add_error(f"Fatal error in round execution: {e}")
            result.is_complete = False
            result.is_successful = False
            logger.error(f"Round {context.round_number} failed: {e}", exc_info=True)

        return result

    def register_phase_hook(
        self,
        phase: RoundPhase,
        hook: callable,
    ) -> None:
        """
        Register a hook to be called after a phase completes.

        Args:
            phase: The phase to hook into.
            hook: Function to call after phase.
        """
        if phase not in self._phase_hooks:
            self._phase_hooks[phase] = []
        self._phase_hooks[phase].append(hook)
        logger.debug(f"Registered hook for phase {phase.value}")

    # Phase implementations

    def _phase_preparation(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Preparation phase: Validate context and state.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.PREPARATION.value}")

        # Validate essential components
        if not context.agents:
            result.add_error("No agents registered for round execution")
            result.phases_failed[RoundPhase.PREPARATION] = "No agents"
            return

        if not context.dynamic_environment:
            result.add_error("Dynamic environment not configured")
            result.phases_failed[RoundPhase.PREPARATION] = "No dynamic environment"
            return

        # Initialize agent event mapping
        agent_ids = list(context.agents.keys())
        for agent_id in agent_ids:
            context.agent_events[agent_id] = []

        if self._enable_detailed_logging:
            logger.debug(
                f"Round prepared with {len(agent_ids)} agents"
            )

        result.phases_completed.append(RoundPhase.PREPARATION)
        self._call_hooks(RoundPhase.PREPARATION, context, result)

    def _phase_event_generation(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Event generation phase: Get all pending events.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.EVENT_GENERATION.value}")

        try:
            # Get events from dynamic environment
            agent_ids = list(context.agents.keys())
            context.events = context.dynamic_environment.get_all_pending_events(
                agent_ids
            )

            # Get scheduled events from scheduler
            if context.event_scheduler:
                scheduled_events = context.event_scheduler.get_events_for_round(
                    context.round_number,
                    context={
                        "agents": context.agents,
                        "round": context.round_number,
                    },
                    execute_immediately=True,
                )
                context.events.extend(scheduled_events)

            result.events_generated = len(context.events)

            # Advance step in dynamic environment
            context.dynamic_environment.advance_step()

            if self._enable_detailed_logging:
                logger.debug(
                    f"Generated {len(context.events)} events for round"
                )

            result.phases_completed.append(RoundPhase.EVENT_GENERATION)
            self._call_hooks(RoundPhase.EVENT_GENERATION, context, result)

        except Exception as e:
            result.add_error(f"Event generation failed: {e}")
            result.phases_failed[RoundPhase.EVENT_GENERATION] = str(e)

    def _phase_event_distribution(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Event distribution phase: Distribute events to affected agents.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.EVENT_DISTRIBUTION.value}")

        try:
            for event in context.events:
                # Record event
                context.dynamic_environment.record_event(event)

                # Distribute to affected agents
                for agent_id in event.affected_agents:
                    if agent_id in context.agent_events:
                        context.agent_events[agent_id].append(event)
                    else:
                        context.add_warning(
                            f"Event '{event.event_id}' affected "
                            f"unknown agent '{agent_id}'"
                        )

            result.events_processed = len(context.events)

            if self._enable_detailed_logging:
                for agent_id, events in context.agent_events.items():
                    logger.debug(
                        f"Agent {agent_id} received {len(events)} events"
                    )

            result.phases_completed.append(RoundPhase.EVENT_DISTRIBUTION)
            self._call_hooks(RoundPhase.EVENT_DISTRIBUTION, context, result)

        except Exception as e:
            result.add_error(f"Event distribution failed: {e}")
            result.phases_failed[RoundPhase.EVENT_DISTRIBUTION] = str(e)

    def _phase_agent_decision_making(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Agent decision-making phase: Collect decisions from all agents.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.AGENT_DECISION_MAKING.value}")

        try:
            for agent_id, agent in context.agents.items():
                # Get available behaviors
                available_behaviors = []
                if context.behavior_selector:
                    available_behaviors = context.behavior_selector.get_available_behaviors(
                        agent,
                        situation={
                            "round": context.round_number,
                            "events": context.agent_events.get(agent_id, []),
                            "in_crisis": any(
                                e.event_type.value == "crisis"
                                for e in context.agent_events.get(agent_id, [])
                            ),
                        },
                    )

                # Build situation context
                situation = {
                    "round": context.round_number,
                    "events": context.agent_events.get(agent_id, []),
                    "in_crisis": any(
                        e.event_type.value == "crisis"
                        for e in context.agent_events.get(agent_id, [])
                    ),
                }

                # Build agent context
                agent_context = {
                    "agents": {
                        aid: a.get_summary()
                        for aid, a in context.agents.items()
                    },
                    "round": context.round_number,
                }

                # Get decision
                try:
                    decision = agent.decide(situation, available_behaviors, agent_context)

                    # Add round info to decision
                    decision["round"] = context.round_number
                    decision["agent_id"] = agent_id

                    context.decisions[agent_id] = decision
                    result.decisions_count += 1
                    result.decisions_success_count += 1

                except Exception as e:
                    result.add_error(
                        f"Decision failed for agent {agent_id}: {e}"
                    )
                    result.decisions_count += 1

            if self._enable_detailed_logging:
                logger.debug(f"Collected {len(context.decisions)} decisions")

            result.phases_completed.append(RoundPhase.AGENT_DECISION_MAKING)
            self._call_hooks(RoundPhase.AGENT_DECISION_MAKING, context, result)

        except Exception as e:
            result.add_error(f"Agent decision-making failed: {e}")
            result.phases_failed[RoundPhase.AGENT_DECISION_MAKING] = str(e)

    def _phase_interaction_execution(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Interaction execution phase: Execute interactions between agents.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.INTERACTION_EXECUTION.value}")

        try:
            # Convert decisions to interaction format
            decisions_list = list(context.decisions.values())

            # Execute interactions
            if context.interaction_manager:
                context.interactions = context.interaction_manager.execute_interactions(
                    decisions_list,
                    context={
                        "round": context.round_number,
                        "agents": context.agents,
                    },
                )

                result.interactions_executed = len(context.interactions)
                result.interactions_success_count = sum(
                    1 for i in context.interactions
                    if getattr(i, "success", True)
                )

            if self._enable_detailed_logging:
                logger.debug(f"Executed {len(context.interactions)} interactions")

            result.phases_completed.append(RoundPhase.INTERACTION_EXECUTION)
            self._call_hooks(RoundPhase.INTERACTION_EXECUTION, context, result)

        except Exception as e:
            result.add_error(f"Interaction execution failed: {e}")
            result.phases_failed[RoundPhase.INTERACTION_EXECUTION] = str(e)

    def _phase_rule_application(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Rule application phase: Apply rules and validate changes.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.RULE_APPLICATION.value}")

        try:
            if context.rule_environment:
                for agent_id, agent in context.agents.items():
                    # Get agent actions for moral evaluation
                    history = agent.get_history()
                    actions = []
                    for entry in history:
                        if entry.metadata:
                            actions.append({
                                "type": entry.event_type,
                                "content": entry.content,
                                **entry.metadata,
                            })

                    # Evaluate moral level
                    interactions_for_agent = []
                    if context.interaction_manager:
                        interactions_for_agent = context.interaction_manager.get_interaction_history(
                            agent_id=agent_id,
                            limit=10,
                        )

                    moral_evals = context.rule_environment.evaluate_moral_level(
                        agent_id=agent_id,
                        actions=actions,
                        interactions=[
                            i.to_dict() if hasattr(i, "to_dict") else i
                            for i in interactions_for_agent
                        ],
                    )

                    context.moral_evaluations[agent_id] = moral_evals
                    result.moral_evaluations[agent_id] = moral_evals

                    # Validate capability changes (if any)
                    if agent.capability:
                        old_capability = agent.capability.get_capability_index()
                        # Example validation check
                        is_valid, _ = context.rule_environment.validate_capability_change(
                            agent_id=agent_id,
                            old_capability=old_capability,
                            new_capability=old_capability + 5.0,  # Example
                            context={"round": context.round_number},
                        )

                        if is_valid:
                            result.capability_changes_validated += 1
                        else:
                            result.capability_changes_rejected += 1

            if self._enable_detailed_logging:
                logger.debug(
                    f"Applied rules to {len(context.moral_evaluations)} agents"
                )

            result.phases_completed.append(RoundPhase.RULE_APPLICATION)
            self._call_hooks(RoundPhase.RULE_APPLICATION, context, result)

        except Exception as e:
            result.add_error(f"Rule application failed: {e}")
            result.phases_failed[RoundPhase.RULE_APPLICATION] = str(e)

    def _phase_metrics_calculation(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Metrics calculation phase: Calculate and store metrics.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.METRICS_CALCULATION.value}")

        try:
            if context.metrics_calculator:
                # Calculate all metrics
                context.metrics = context.metrics_calculator.calculate_all_metrics(
                    agents=context.agents,
                    state={
                        "round": context.round_number,
                        "events": [e.to_dict() for e in context.events],
                    },
                    round_result={
                        "round": context.round_number,
                        "decisions": context.decisions,
                        "interactions": [
                            i.to_dict() if hasattr(i, "to_dict") else i
                            for i in context.interactions
                        ],
                    },
                )

                result.metrics = context.metrics.copy()

                # Save metrics if data storage configured
                if context.data_storage:
                    context.data_storage.save_metrics(
                        metrics_dict=context.metrics,
                        round_id=context.round_number,
                        metadata={
                            "round_result": result.to_dict(),
                        },
                    )

            if self._enable_detailed_logging:
                logger.debug("Metrics calculated and stored")

            result.phases_completed.append(RoundPhase.METRICS_CALCULATION)
            self._call_hooks(RoundPhase.METRICS_CALCULATION, context, result)

        except Exception as e:
            result.add_error(f"Metrics calculation failed: {e}")
            result.phases_failed[RoundPhase.METRICS_CALCULATION] = str(e)

    def _phase_systemic_interaction(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Systemic interaction phase: Execute system-level interactions.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.SYSTEMIC_INTERACTION.value}")

        try:
            if context.systemic_interaction:
                # Get great powers for systemic interactions
                great_powers = [
                    agent_id for agent_id, agent in context.agents.items()
                    if hasattr(agent, 'agent_type') and agent.agent_type.value == "great_power"
                ]

                if great_powers:
                    # Shape international order
                    order_result = context.systemic_interaction.shape_international_order(
                        context.round_number
                    )

                    # Evolve international norms
                    norm_evolution = context.systemic_interaction.evolve_international_norms(
                        context.round_number
                    )

                    # Simulate values competition
                    values_competition = context.systemic_interaction.simulate_values_competition(
                        context.round_number
                    )

                    # Store systemic results in context
                    context.systemic_results = {
                        "order_shape": order_result,
                        "norm_evolution": norm_evolution,
                        "values_competition": values_competition,
                    }

                    # Save systemic events if persistence enabled
                    if context.data_storage and context.persistence:
                        for event in context.systemic_interaction.get_systemic_events(limit=5):
                            context.data_storage.save_systemic_event(
                                event.to_dict() if hasattr(event, 'to_dict') else event,
                                context.round_number
                            )

            if self._enable_detailed_logging:
                logger.debug("Systemic interaction phase completed")

            result.phases_completed.append(RoundPhase.SYSTEMIC_INTERACTION)
            self._call_hooks(RoundPhase.SYSTEMIC_INTERACTION, context, result)

        except Exception as e:
            result.add_error(f"Systemic interaction failed: {e}")
            result.phases_failed[RoundPhase.SYSTEMIC_INTERACTION] = str(e)

    def _phase_cleanup(
        self,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """
        Cleanup phase: Record history and update statistics.

        Args:
            context: Round context.
            result: Round result to update.
        """
        logger.debug(f"Phase {RoundPhase.CLEANUP.value}")

        try:
            # Copy context errors and warnings to result
            result.errors.extend(context.errors)
            result.warnings.extend(context.warnings)

            # Save decision history if persistence enabled
            if context.data_storage and context.persistence:
                for agent_id, decision in context.decisions.items():
                    context.data_storage.save_decision_history(
                        agent_id,
                        decision,
                        context.round_number
                    )

            # Save interaction details if persistence enabled
            if context.data_storage and context.ion_persistence:
                for interaction in context.interactions:
                    interaction_dict = interaction.to_dict() if hasattr(interaction, 'to_dict') else interaction
                    context.data_storage.save_interaction_details(
                        interaction_dict,
                        context.round_number
                    )

            if self._enable_detailed_logging:
                logger.debug(f"Round cleanup completed")

            result.phases_completed.append(RoundPhase.CLEANUP)
            self._call_hooks(RoundPhase.CLEANUP, context, result)

        except Exception as e:
            result.add_error(f"Cleanup failed: {e}")
            result.phases_failed[RoundPhase.CLEANUP] = str(e)

    def _call_hooks(
        self,
        phase: RoundPhase,
        context: RoundContext,
        result: RoundResult,
    ) -> None:
        """Call all registered hooks for a phase."""
        if phase in self._phase_hooks:
            for hook in self._phase_hooks[phase]:
                try:
                    hook(context, result)
                except Exception as e:
                    logger.error(f"Hook error for phase {phase.value}: {e}")
