"""
Interaction manager for moral realism ABM system.

This module implements InteractionManager class which coordinates
agent interactions, manages simulation flow, and maintains
interaction history.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType


logger = logging.getLogger(__name__)


@dataclass
class InteractionResult:
    """Result of a single interaction between agents."""

    interaction_id: str
    from_agent_id: str
    to_agent_id: str
    interaction_type: str
    action: Dict[str, Any]
    response: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "interaction_id": self.interaction_id,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "interaction_type": self.interaction_type,
            "action": self.action,
            "response": self.response,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


@dataclass
class InteractionStep:
    """Represents a single step in interaction cycle."""

    step_id: str
    round: int
    timestamp: datetime = field(default_factory=datetime.now)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    interactions: List[InteractionResult] = field(default_factory=list)
    step_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_id": self.step_id,
            "round": self.round,
            "timestamp": self.timestamp.isoformat(),
            "decisions": self.decisions,
            "interactions": [i.to_dict() for i in self.interactions],
            "step_metadata": self.step_metadata,
        }


class InteractionManager:
    """
    Manages interactions between agents in simulation.

    Coordinates agent decision-making, interaction execution,
    and response collection while maintaining history and statistics.
    """

    def __init__(
        self,
        max_history_length: int = 1000,
        enable_logging: bool = True,
    ) -> None:
        """
        Initialize interaction manager.

        Args:
            max_history_length: Maximum number of history entries to keep.
            enable_logging: Whether to enable detailed logging.
        """
        self._agents: Dict[str, Agent] = {}
        self._interaction_history: List[InteractionResult] = []
        self._step_history: List[InteractionStep] = []
        self._current_round: int = 0

        self._max_history_length = max_history_length
        self._enable_logging = enable_logging

        self._interaction_counter: int = 0

        # Statistics
        self._stats: Dict[str, Any] = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "interaction_counts_by_type": {},
            "interaction_counts_by_agent": {},
        }

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with interaction manager.

        Args:
            agent: The agent to register.
        """
        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")

    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from interaction manager.

        Args:
            agent_id: The ID of agent to unregister.

        Returns:
            True if agent was unregistered, False if not found.
        """
        if agent_id in self._agents:
            agent = self._agents.pop(agent_id)
            logger.info(f"Unregistered agent: {agent.name} ({agent_id})")
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get a registered agent by ID.

        Args:
            agent_id: The ID of agent.

        Returns:
            The agent if found, None otherwise.
        """
        return self._agents.get(agent_id)

    def get_all_agents(self) -> List[Agent]:
        """
        Get all registered agents.

        Returns:
            List of all registered agents.
        """
        return list(self._agents.values())

    def get_agents_by_type(self, agent_type: AgentType) -> List[Agent]:
        """
        Get all agents of a specific type.

        Args:
            agent_type: The type of agent to retrieve.

        Returns:
            List of agents of specified type.
        """
        return [
            agent for agent in self._agents.values()
            if agent.agent_type == agent_type
        ]

    def execute_interactions(
        self,
        decisions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[InteractionResult]:
        """
        Execute interactions based on agent decisions.

        Args:
            decisions: List of decisions made by agents.
            context: Additional context for interaction execution.

        Returns:
            List of interaction results.
        """
        if context is None:
            context = {}

        results = []
        step_id = f"step_{self._current_round}"

        # Create new step
        step = InteractionStep(
            step_id=step_id,
            round=self._current_round,
            decisions=decisions,
        )

        # Process each decision
        for decision in decisions:
            result = self._process_decision(decision, context)
            if result:
                results.append(result)
                step.interactions.append(result)

        # Update statistics
        self._update_statistics(results)

        # Store step
        self._step_history.append(step)

        # Advance round
        self._current_round += 1

        if self._enable_logging:
            logger.info(
                f"Executed {len(results)} interactions in round {self._current_round - 1}"
            )

        return results

    def _process_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[InteractionResult]:
        """
        Process a single agent decision into an interaction.

        Args:
            decision: The agent's decision.
            context: Additional context.

        Returns:
            Interaction result if applicable, None otherwise.
        """
        from_agent_id = decision.get("agent_id")
        action_type = decision.get("action_type", "no_action")
        target_agent_id = decision.get("target_agent_id")

        # Skip no_action decisions
        if action_type == "no_action":
            return None

        from_agent = self._agents.get(from_agent_id)
        if not from_agent:
            return InteractionResult(
                interaction_id=self._generate_interaction_id(),
                from_agent_id=from_agent_id,
                to_agent_id=target_agent_id or "unknown",
                interaction_type=action_type,
                action=decision,
                success=False,
                error_message=f"Source agent {from_agent_id} not found",
            )

        # Determine target agent
        if target_agent_id:
            to_agent = self._agents.get(target_agent_id)
            if not to_agent:
                return InteractionResult(
                    interaction_id=self._generate_interaction_id(),
                    from_agent_id=from_agent_id,
                    to_agent_id=target_agent_id,
                    interaction_type=action_type,
                    action=decision,
                    success=False,
                    error_message=f"Target agent {target_agent_id} not found",
                )
        else:
            # No specific target, broadcast to all other agents
            to_agent = None

        # Create interaction result
        result = InteractionResult(
            interaction_id=self._generate_interaction_id(),
            from_agent_id=from_agent_id,
            to_agent_id=target_agent_id or "broadcast",
            interaction_type=action_type,
            action=decision,
        )

        # Execute interaction
        try:
            if to_agent:
                # Direct interaction
                response = self._execute_direct_interaction(
                    from_agent, to_agent, decision, context
                )
            else:
                # Broadcast interaction
                response = self._execute_broadcast_interaction(
                    from_agent, decision, context
                )

            result.response = response
            result.success = True

            # Store in history
            self._add_to_history(result)

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(
                f"Error executing interaction from {from_agent_id}: {e}"
            )

        return result

    def _execute_direct_interaction(
        self,
        from_agent: Agent,
        to_agent: Agent,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a direct interaction between two agents.

        Args:
            from_agent: The initiating agent.
            to_agent: The target agent.
            decision: The action decision.
            context: Additional context.

        Returns:
            Response from target agent.
        """
        # Create message
        message = {
            "type": decision.get("action_type", "unknown"),
            "content": decision.get("rationale", ""),
            "from_agent_id": from_agent.agent_id,
            "from_agent_name": from_agent.name,
            "from_agent_type": from_agent.agent_type.value,
            "priority": decision.get("priority", "medium"),
            "resource_allocation": decision.get("resource_allocation", 50),
        }

        # Add context with agents information
        interaction_context = {
            **context,
            "agents": {
                agent.agent_id: {
                    "name": agent.name,
                    "agent_type": agent.agent_type.value,
                    "leadership_type": agent.leadership_type.value,
                }
                for agent in self._agents.values()
            },
        }

        # Get response
        response = to_agent.respond(
            from_agent.agent_id,
            message,
            interaction_context,
        )

        # Update relationships
        self._update_relationships(from_agent, to_agent, decision, response)

        return response

    def _execute_broadcast_interaction(
        self,
        from_agent: Agent,
        decision: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a broadcast interaction to all other agents.

        Args:
            from_agent: The initiating agent.
            decision: The action decision.
            context: Additional context.

        Returns:
            Aggregated responses from all targets.
        """
        responses = {}

        for target_agent in self._agents.values():
            if target_agent.agent_id == from_agent.agent_id:
                continue

            try:
                response = self._execute_direct_interaction(
                    from_agent, target_agent, decision, context
                )
                responses[target_agent.agent_id] = response
            except Exception as e:
                logger.error(
                    f"Error in broadcast to {target_agent.agent_id}: {e}"
                )
                responses[target_agent.agent_id] = {
                    "error": str(e),
                    "success": False,
                }

        return {
            "type": "broadcast_response",
            "responses": responses,
            "total_recipients": len(responses),
        }

    def _update_relationships(
        self,
        from_agent: Agent,
        to_agent: Agent,
        decision: Dict[str, Any],
        response: Dict[str, Any],
    ) -> None:
        """
        Update agent relationships based on interaction.

        Args:
            from_agent: The initiating agent.
            to_agent: The target agent.
            decision: The action decision.
            response: The response received.
        """
        action_type = decision.get("action_type", "")

        # Determine relationship adjustment
        adjustment = 0.0

        # Positive actions
        if any(pos in action_type for pos in [
            "diplomatic_visit", "diplomatic_alliance",
            "economic_aid", "norm_proposal", "norm_reform",
        ]):
            adjustment = 0.1

        # Negative actions
        elif any(neg in action_type for neg in [
            "economic_sanction", "military",
        ]):
            adjustment = -0.15

        # Adjust from response content
        if response.get("message_type") == "support":
            adjustment += 0.05
        elif response.get("message_type") == "decline":
            adjustment -= 0.1

        # Apply adjustment (clamped to -1 to 1)
        current = from_agent.get_relationship(to_agent.agent_id)
        new_score = max(-1.0, min(1.0, current + adjustment))
        from_agent.set_relationship(to_agent.agent_id, new_score)

        # Mirror relationship (simplified)
        target_current = to_agent.get_relationship(from_agent.agent_id)
        target_new = max(-1.0, min(1.0, target_current + adjustment * 0.5))
        to_agent.set_relationship(from_agent.agent_id, target_new)

    def _update_statistics(self, results: List[InteractionResult]) -> None:
        """
        Update interaction statistics.

        Args:
            results: List of interaction results.
        """
        self._stats["total_interactions"] += len(results)

        for result in results:
            if result.success:
                self._stats["successful_interactions"] += 1
            else:
                self._stats["failed_interactions"] += 1

            # Count by type
            interaction_type = result.interaction_type
            type_counts = self._stats["interaction_counts_by_type"]
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1

            # Count by agent
            agent_counts = self._stats["interaction_counts_by_agent"]
            agent_counts[result.from_agent_id] = (
                agent_counts.get(result.from_agent_id, 0) + 1
            )

    def _add_to_history(self, result: InteractionResult) -> None:
        """
        Add interaction result to history.

        Args:
            result: The interaction result to add.
        """
        self._interaction_history.append(result)

        # Maintain max history length
        if len(self._interaction_history) > self._max_history_length:
            self._interaction_history = self._interaction_history[
                -self._max_history_length:
            ]

    def _generate_interaction_id(self) -> str:
        """Generate a unique interaction ID."""
        self._interaction_counter += 1
        return f"interaction_{self._interaction_counter}_{self._current_round}"

    def get_interaction_history(
        self,
        limit: Optional[int] = None,
        agent_id: Optional[str] = None,
        interaction_type: Optional[str] = None,
    ) -> List[InteractionResult]:
        """
        Get interaction history with optional filters.

        Args:
            limit: Maximum number of results to return.
            agent_id: Filter by specific agent ID.
            interaction_type: Filter by interaction type.

        Returns:
            Filtered list of interaction results.
        """
        history = self._interaction_history

        # Filter by agent
        if agent_id:
            history = [
                r for r in history
                if r.from_agent_id == agent_id or r.to_agent_id == agent_id
            ]

        # Filter by type
        if interaction_type:
            history = [
                r for r in history
                if r.interaction_type == interaction_type
            ]

        # Apply limit
        if limit:
            history = history[-limit:]

        return history

    def get_step_history(
        self,
        limit: Optional[int] = None,
    ) -> List[InteractionStep]:
        """
        Get step history.

        Args:
            limit: Maximum number of steps to return.

        Returns:
            List of interaction steps.
        """
        if limit:
            return self._step_history[-limit:]
        return self._step_history.copy()

    def get_interaction_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about interactions.

        Returns:
            Dictionary with interaction statistics.
        """
        return {
            **self._stats,
            "current_round": self._current_round,
            "registered_agents": len(self._agents),
            "history_length": len(self._interaction_history),
            "success_rate": (
                self._stats["successful_interactions"] / self._stats["total_interactions"]
                if self._stats["total_interactions"] > 0
                else 0.0
            ),
        }

    def get_agent_interactions(
        self,
        agent_id: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get interactions involving a specific agent.

        Args:
            agent_id: The agent ID.
            limit: Maximum number of results.

        Returns:
            Dictionary with agent interaction statistics and history.
        """
        interactions = self.get_interaction_history(
            limit=limit,
            agent_id=agent_id,
        )

        # Calculate stats
        sent = [i for i in interactions if i.from_agent_id == agent_id]
        received = [i for i in interactions if i.to_agent_id == agent_id]

        return {
            "agent_id": agent_id,
            "total_interactions": len(interactions),
            "sent": len(sent),
            "received": len(received),
            "successful": sum(1 for i in interactions if i.success),
            "by_type": {
                i_type: sum(1 for i in interactions if i.interaction_type == i_type)
                for i_type in set(i.interaction_type for i in interactions)
            },
            "recent_interactions": [i.to_dict() for i in interactions[-5:]],
        }

    def reset_round(self) -> None:
        """Reset to current round counter to zero."""
        self._current_round = 0
        logger.info("Reset round counter to 0")

    def clear_history(self) -> None:
        """Clear all interaction history."""
        self._interaction_history.clear()
        self._step_history.clear()
        self._interaction_counter = 0
        logger.info("Cleared interaction history")

    def reset_statistics(self) -> None:
        """Reset interaction statistics."""
        self._stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "interaction_counts_by_type": {},
            "interaction_counts_by_agent": {},
        }
        logger.info("Reset interaction statistics")
