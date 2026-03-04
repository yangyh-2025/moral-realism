"""
Agent models for the moral realism ABM system.

This module defines the base agent class and agent types for the simulation.
Agents represent states or other actors in the international system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.capability import Capability
from src.models.leadership_type import LeadershipType, LeadershipProfile


class AgentType(Enum):
    """Types of agents in the simulation."""

    GREAT_POWER = "great_power"  # 大国
    SMALL_STATE = "small_state"  # 小国
    ORGANIZATION = "organization"  # 国际组织
    CONTROLLER = "controller"  # 控制者/实验者


class InteractionType(Enum):
    """Types of interactions between agents."""

    DIPLOMATIC = "diplomatic"  # 外交沟通
    ECONOMIC = "economic"  # 经济合作/制裁
    MILITARY = "military"  # 军事互动
    COERCIVE = "coercive"  # 强制措施
    COOPERATIVE = "cooperative"  # 合作项目


@dataclass
class HistoryEntry:
    """A single entry in an agent's history."""

    timestamp: datetime
    event_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        timestamp: datetime,
        event_type: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Initialize history entry with automatic timestamp conversion."""
        # Handle string timestamp conversion
        if isinstance(timestamp, str):
            from datetime import datetime as dt
            self.timestamp = dt.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp
        self.event_type = event_type
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "content": self.content,
            "metadata": self.metadata,
        }


@dataclass
class Agent(ABC):
    """
    Abstract base class for all agents in the simulation.

    This class defines the core structure and interface that all agents
    must implement. Specific agent types (Great Power, Small State, etc.)
    should inherit from this class.
    """

    # Basic identification
    agent_id: str
    name: str
    name_zh: str
    agent_type: AgentType

    # Leadership characteristics
    leadership_type: LeadershipType
    leadership_profile: Optional[LeadershipProfile] = None

    # Capability and power
    capability: Optional[Capability] = None

    # State and status
    is_active: bool = True
    is_alive: bool = True

    # Historical tracking
    history: List[HistoryEntry] = field(default_factory=list)
    max_history_length: int = 1000

    # Relations with other agents
    relations: Dict[str, float] = field(default_factory=dict)  # agent_id -> relationship_score (-1 to 1)

    # Custom attributes for specific agent types
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize the agent after dataclass initialization."""
        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        # Initialize relations with self
        self.relations[self.agent_id] = 1.0

    @abstractmethod
    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a decision based on the current situation.

        This is the core decision-making method that each agent must implement.
        The decision should reflect the agent's leadership type, interests,
        and capability level.

        Args:
            situation: Description of the current situation.
            available_actions: List of actions available to the agent.
            context: Additional context for decision-making.

        Returns:
            Dictionary containing the decision and rationale.
        """
        pass

    @abstractmethod
    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Respond to a message from another agent.

        Args:
            sender_id: ID of the sending agent.
            message: The message content and metadata.
            context: Additional context for response generation.

        Returns:
            Dictionary containing the response.
        """
        pass

    def add_history(
        self,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add an entry to the agent's history.

        Args:
            event_type: Type of event (e.g., "decision", "response", "interaction").
            content: Description of the event.
            metadata: Additional metadata about the event.
        """
        entry = HistoryEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            content=content,
            metadata=metadata or {},
        )
        self.history.append(entry)

        # Maintain max history length
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]

    def get_history(self, event_type: Optional[str] = None) -> List[HistoryEntry]:
        """
        Get the agent's history, optionally filtered by event type.

        Args:
            event_type: If specified, only return entries of this type.

        Returns:
            List of history entries.
        """
        if event_type is None:
            return self.history.copy()
        return [entry for entry in self.history if entry.event_type == event_type]

    def get_recent_history(self, n: int = 10) -> List[HistoryEntry]:
        """
        Get the most recent n history entries.

        Args:
            n: Number of recent entries to return.

        Returns:
            List of recent history entries.
        """
        return self.history[-n:] if len(self.history) >= n else self.history.copy()

    def set_relationship(self, target_id: str, score: float) -> None:
        """
        Set the relationship score with another agent.

        Args:
            target_id: ID of the target agent.
            score: Relationship score (-1 to 1, where -1 is hostile, 1 is friendly).
        """
        score = max(-1.0, min(1.0, score))
        self.relations[target_id] = score

    def get_relationship(self, target_id: str) -> float:
        """
        Get the relationship score with another agent.

        Args:
            target_id: ID of the target agent.

        Returns:
            Relationship score (-1 to 1).
        """
        return self.relations.get(target_id, 0.0)

    def is_friendly_with(self, target_id: str) -> bool:
        """
        Check if the agent has a friendly relationship with another agent.

        Args:
            target_id: ID of the target agent.

        Returns:
            True if relationship is friendly (score > 0.3).
        """
        return self.get_relationship(target_id) > 0.3

    def is_hostile_toward(self, target_id: str) -> bool:
        """
        Check if the agent has a hostile relationship with another agent.

        Args:
            target_id: ID of the target agent.

        Returns:
            True if relationship is hostile (score < -0.3).
        """
        return self.get_relationship(target_id) < -0.3

    def get_capability_tier(self) -> str:
        """
        Get the agent's capability tier as a string.

        Returns:
            Capability tier string.
        """
        if self.capability is None:
            return "unknown"
        return self.capability.get_tier().value

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the agent's current state.

        Returns:
            Dictionary containing agent summary information.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "name_zh": self.name_zh,
            "agent_type": self.agent_type.value,
            "leadership_type": self.leadership_type.value,
            "leadership_name": self.leadership_profile.name if self.leadership_profile else None,
            "capability_tier": self.get_capability_tier(),
            "capability_index": self.capability.get_capability_index() if self.capability else None,
            "is_active": self.is_active,
            "is_alive": self.is_alive,
            "history_length": len(self.history),
            "relations_count": len(self.relations),
        }


@dataclass
class GreatPower(Agent):
    """A great power agent with significant global influence."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_zh: str,
        leadership_type: LeadershipType,
        capability: Optional[Capability] = None,
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            name=name,
            name_zh=name_zh,
            agent_type=AgentType.GREAT_POWER,
            leadership_type=leadership_type,
            capability=capability,
        )

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a decision as a great power.

        Great powers consider global strategic implications and have
        broader range of actions available.
        """
        # This will be implemented with LLM integration in later phases
        decision = {
            "action": available_actions[0]["id"] if available_actions else "no_action",
            "rationale": "Decision made based on great power interests",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("decision", f"Decided to take action: {decision['action']}")
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Respond as a great power.

        Great powers respond from a position of strength and
        consider global implications of their responses.
        """
        # This will be implemented with LLM integration in later phases
        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": "Response from great power",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("response", f"Responded to {sender_id}")
        return response


@dataclass
class SmallState(Agent):
    """A small state agent with limited capabilities."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_zh: str,
        leadership_type: LeadershipType,
        capability: Optional[Capability] = None,
    ) -> None:
        super().__init__(
            agent_id=agent_id,
            name=name,
            name_zh=name_zh,
            agent_type=AgentType.SMALL_STATE,
            leadership_type=leadership_type,
            capability=capability,
        )

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a decision as a small state.

        Small states have limited options and must be strategic
        in their choices.
        """
        # This will be implemented with LLM integration in later phases
        decision = {
            "action": available_actions[0]["id"] if available_actions else "no_action",
            "rationale": "Decision made with limited options",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("decision", f"Decided to take action: {decision['action']}")
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Respond as a small state.

        Small states must be careful in their responses to avoid
        antagonizing more powerful states.
        """
        # This will be implemented with LLM integration in later phases
        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": "Response from small state",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("response", f"Responded to {sender_id}")
        return response
