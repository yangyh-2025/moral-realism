"""
Dynamic environment module for the moral realism ABM system.

This module defines the dynamic event environment that generates and manages
regular events, crisis events, and user-defined custom events.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
import random
from datetime import datetime


class EventType(Enum):
    """General event type categories."""

    REGULAR = "regular"  # Periodic regular events
    CRISIS = "crisis"  # Random crisis events
    CUSTOM = "custom"  # User-defined custom events


class RegularEventType(Enum):
    """Types of regular periodic events."""

    LEADERSHIP_CHANGE = "leadership_change"  # 领导换届
    ECONOMIC_CYCLE = "economic_cycle"  # 经济周期
    DIPLOMATIC_SUMMIT = "diplomatic_summit"  # 外交峰会
    ELECTION = "election"  # 选举
    ALLIANCE_FORMATION = "alliance_formation"  # 同盟形成
    TREATY_RENEWAL = "treaty_renewal"  # 条约续签
    TRADE_AGREEMENT = "trade_agreement"  # 贸易协定


class CrisisEventType(Enum):
    """Types of crisis events."""

    MILITARY_CONFLICT = "military_conflict"  # 军事冲突
    ECONOMIC_CRISIS = "economic_crisis"  # 经济危机
    TERRITORIAL_DISPUTE = "territorial_dispute"  # 领土争端
    DIPLOMATIC_CRISES = "diplomatic_crises"  # 外交危机
    SANCTIONS_IMPOSED = "sanctions_imposed"  # 制裁实施
    HUMANITARIAN_DISASTER = "humanitarian_disaster"  # 人道主义灾难
    TERRORISM = "terrorism"  # 恐怖主义
    CYBER_ATTACK = "cyber_attack"  # 网络攻击


@dataclass
class Event:
    """Represents an event in the simulation."""

    event_id: str
    event_type: EventType
    sub_type: str  # Specific event type (e.g., "leadership_change", "military_conflict")
    description: str
    severity: float  # 0-100 scale
    affected_agents: List[str]
    context: Dict = field(default_factory=dict)
    timestamp: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate event data on creation."""
        if not 0 <= self.severity <= 100:
            raise ValueError(f"Event severity must be between 0 and 100, got {self.severity}")

    def validate(self) -> bool:
        """Validate event data."""
        return 0 <= self.severity <= 100

    def to_dict(self) -> Dict:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "sub_type": self.sub_type,
            "description": self.description,
            "severity": self.severity,
            "affected_agents": self.affected_agents,
            "context": self.context,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class DynamicEnvironment:
    """
    Dynamic event environment for the simulation.

    Generates and manages periodic regular events, random crisis events,
    and user-defined custom events.
    """

    def __init__(
        self,
        crisis_probability: float = 0.15,
        min_crisis_interval: int = 5,
    ) -> None:
        """
        Initialize the dynamic environment.

        Args:
            crisis_probability: Probability of a crisis event occurring (0-1).
            min_crisis_interval: Minimum steps between crisis events.
        """
        self.crisis_probability = max(0.0, min(1.0, crisis_probability))
        self.min_crisis_interval = max(1, min_crisis_interval)

        self.event_history: List[Event] = []
        self.event_queue: List[Event] = []
        self.custom_events: List[Event] = []

        self._last_crisis_step: int = -100
        self._event_counter: int = 0
        self._current_step: int = 0

        # Configuration for regular events
        self._regular_event_intervals: Dict[RegularEventType, int] = {
            RegularEventType.LEADERSHIP_CHANGE: 20,  # Every 20 steps
            RegularEventType.ECONOMIC_CYCLE: 10,  # Every 10 steps
            RegularEventType.DIPLOMATIC_SUMMIT: 15,  # Every 15 steps
            RegularEventType.ELECTION: 20,  # Every 20 steps
            RegularEventType.ALLIANCE_FORMATION: 25,  # Every 25 steps
            RegularEventType.TREATY_RENEWAL: 30,  # Every 30 steps
            RegularEventType.TRADE_AGREEMENT: 12,  # Every 12 steps
        }

    def _generate_event_id(self, event_type: EventType) -> str:
        """Generate a unique event ID."""
        self._event_counter += 1
        return f"{event_type.value}_{self._event_counter}"

    def _step_is_interval(self, interval: int) -> bool:
        """Check if current step is at the specified interval."""
        return interval > 0 and self._current_step > 0 and self._current_step % interval == 0

    def get_regular_events(self, agent_ids: Optional[List[str]] = None) -> List[Event]:
        """
        Get periodic regular events for the current step.

        Args:
            agent_ids: List of agent IDs to potentially affect.

        Returns:
            List of regular events for this step.
        """
        if agent_ids is None:
            agent_ids = []

        events = []

        # Leadership change events
        if self._step_is_interval(self._regular_event_intervals[RegularEventType.LEADERSHIP_CHANGE]):
            if agent_ids:
                affected = random.sample(agent_ids, min(2, len(agent_ids)))
                event = Event(
                    event_id=self._generate_event_id(EventType.REGULAR),
                    event_type=EventType.REGULAR,
                    sub_type=RegularEventType.LEADERSHIP_CHANGE.value,
                    description=f"Leadership change in {len(affected)} states",
                    severity=40.0,
                    affected_agents=affected,
                    context={"event": "leadership_transition"},
                )
                events.append(event)

        # Economic cycle events
        if self._step_is_interval(self._regular_event_intervals[RegularEventType.ECONOMIC_CYCLE]):
            event = Event(
                event_id=self._generate_event_id(EventType.REGULAR),
                event_type=EventType.REGULAR,
                sub_type=RegularEventType.ECONOMIC_CYCLE.value,
                description="Global economic cycle phase transition",
                severity=30.0,
                affected_agents=agent_ids.copy(),
                context={"phase": "contraction" if random.random() < 0.3 else "expansion"},
            )
            events.append(event)

        # Diplomatic summit events
        if self._step_is_interval(self._regular_event_intervals[RegularEventType.DIPLOMATIC_SUMMIT]):
            if agent_ids and len(agent_ids) >= 3:
                participants = random.sample(agent_ids, min(5, len(agent_ids)))
                event = Event(
                    event_id=self._generate_event_id(EventType.REGULAR),
                    event_type=EventType.REGULAR,
                    sub_type=RegularEventType.DIPLOMATIC_SUMMIT.value,
                    description=f"International summit with {len(participants)} participants",
                    severity=25.0,
                    affected_agents=participants,
                    context={"forum": "UN_General_Assembly" if random.random() < 0.5 else "regional_summit"},
                )
                events.append(event)

        # Election events
        if self._step_is_interval(self._regular_event_intervals[RegularEventType.ELECTION]):
            if agent_ids:
                affected = random.sample(agent_ids, min(3, len(agent_ids)))
                event = Event(
                    event_id=self._generate_event_id(EventType.REGULAR),
                    event_type=EventType.REGULAR,
                    sub_type=RegularEventType.ELECTION.value,
                    description=f"Elections in {len(affected)} states",
                    severity=35.0,
                    affected_agents=affected,
                    context={"type": "general_election"},
                )
                events.append(event)

        return events

    def get_random_events(self, agent_ids: Optional[List[str]] = None) -> List[Event]:
        """
        Get random crisis events for the current step.

        Args:
            agent_ids: List of agent IDs to potentially affect.

        Returns:
            List of crisis events for this step.
        """
        events = []

        # Check if crisis should occur
        steps_since_last_crisis = self._current_step - self._last_crisis_step

        if steps_since_last_crisis < self.min_crisis_interval:
            return events

        if random.random() > self.crisis_probability:
            return events

        if agent_ids is None or len(agent_ids) < 2:
            return events

        # Select crisis type
        crisis_types = list(CrisisEventType)
        crisis_type = random.choice(crisis_types)

        # Generate crisis event
        affected_count = random.randint(2, min(4, len(agent_ids)))
        affected = random.sample(agent_ids, affected_count)

        severity = random.uniform(50, 95)
        self._last_crisis_step = self._current_step

        if crisis_type == CrisisEventType.MILITARY_CONFLICT:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.MILITARY_CONFLICT.value,
                description=f"Armed conflict between {affected[0]} and {affected[1]}",
                severity=severity,
                affected_agents=affected[:2],
                context={"conflict_type": "conventional_warfare", "intensity": "high"},
            )
        elif crisis_type == CrisisEventType.ECONOMIC_CRISIS:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.ECONOMIC_CRISIS.value,
                description="Global economic crisis with financial market instability",
                severity=severity,
                affected_agents=agent_ids.copy(),
                context={
                    "type": "financial_crisis",
                    "trigger": "currency_devaluation" if random.random() < 0.5 else "credit_contraction",
                },
            )
        elif crisis_type == CrisisEventType.TERRITORIAL_DISPUTE:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.TERRITORIAL_DISPUTE.value,
                description=f"Territorial dispute between {affected[0]} and {affected[1]}",
                severity=severity,
                affected_agents=affected[:2],
                context={"region": f"region_{random.randint(1, 10)}", "disputed_area": "border_zone"},
            )
        elif crisis_type == CrisisEventType.DIPLOMATIC_CRISES:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.DIPLOMATIC_CRISES.value,
                description="Diplomatic standoff threatens to escalate",
                severity=severity,
                affected_agents=affected,
                context={"issue": "diplomatic_protocol_violation"},
            )
        elif crisis_type == CrisisEventType.SANCTIONS_IMPOSED:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.SANCTIONS_IMPOSED.value,
                description=f"Sanctions imposed on {affected[-1]}",
                severity=severity,
                affected_agents=affected,
                context={"sanction_type": "economic_sanctions", "duration": "indefinite"},
            )
        elif crisis_type == CrisisEventType.HUMANITARIAN_DISASTER:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.HUMANITARIAN_DISASTER.value,
                description="Humanitarian crisis requires international response",
                severity=severity,
                affected_agents=affected,
                context={"type": "natural_disaster" if random.random() < 0.5 else "famine"},
            )
        elif crisis_type == CrisisEventType.TERRORISM:
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.TERRORISM.value,
                description="Terrorist attack triggers security response",
                severity=severity,
                affected_agents=affected[:2],
                context={"target": "civilian_infrastructure"},
            )
        else:  # CYBER_ATTACK
            event = Event(
                event_id=self._generate_event_id(EventType.CRISIS),
                event_type=EventType.CRISIS,
                sub_type=CrisisEventType.CYBER_ATTACK.value,
                description="Cyber attack disrupts critical systems",
                severity=severity,
                affected_agents=affected[:2],
                context={"target": "government_networks" if random.random() < 0.5 else "financial_systems"},
            )

        events.append(event)
        return events

    def add_custom_event(
        self,
        event_type: str,
        description: str,
        severity: float,
        affected_agents: List[str],
        context: Optional[Dict] = None,
    ) -> str:
        """
        Add a user-defined custom event.

        Args:
            event_type: The type identifier for the custom event.
            description: Description of the event.
            severity: Event severity (0-100).
            affected_agents: List of affected agent IDs.
            context: Additional context information.

        Returns:
            The event ID of the created custom event.
        """
        event = Event(
            event_id=self._generate_event_id(EventType.CUSTOM),
            event_type=EventType.CUSTOM,
            sub_type=event_type,
            description=description,
            severity=severity,
            affected_agents=affected_agents.copy(),
            context=context or {},
        )
        self.custom_events.append(event)
        return event.event_id

    def get_custom_events(self) -> List[Event]:
        """
        Get and clear pending custom events.

        Returns:
            List of pending custom events (cleared after retrieval).
        """
        events = self.custom_events.copy()
        self.custom_events.clear()
        return events

    def get_all_pending_events(self, agent_ids: Optional[List[str]] = None) -> List[Event]:
        """
        Get all pending events for the current step.

        Args:
            agent_ids: List of agent IDs.

        Returns:
            List of all pending events (regular, crisis, and custom).
        """
        events = []
        events.extend(self.get_regular_events(agent_ids))
        events.extend(self.get_random_events(agent_ids))
        events.extend(self.get_custom_events())
        events.extend(self.event_queue)
        self.event_queue.clear()
        return events

    def record_event(self, event: Event) -> None:
        """
        Record a processed event to history.

        Args:
            event: The event to record.
        """
        event.validate()
        self.event_history.append(event)

    def get_event_summary(self, limit: int = 10) -> List[Dict]:
        """
        Get a summary of recent events.

        Args:
            limit: Maximum number of recent events to return.

        Returns:
            List of recent event summaries.
        """
        recent_events = self.event_history[-limit:]
        return [event.to_dict() for event in reversed(recent_events)]

    def set_regular_event_interval(self, event_type: RegularEventType, interval: int) -> None:
        """
        Set the interval for a regular event type.

        Args:
            event_type: The regular event type.
            interval: The interval in steps.
        """
        if interval < 1:
            raise ValueError(f"Interval must be at least 1, got {interval}")
        self._regular_event_intervals[event_type] = interval

    def advance_step(self) -> None:
        """Advance the simulation step counter."""
        self._current_step += 1

    def get_current_step(self) -> int:
        """Get the current simulation step."""
        return self._current_step

    def get_event_history(self) -> List[Event]:
        """Get the complete event history."""
        return self.event_history.copy()

    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """
        Get events from history by type.

        Args:
            event_type: The event type to filter by.

        Returns:
            List of events of the specified type.
        """
        return [event for event in self.event_history if event.event_type == event_type]

    def get_events_by_severity(self, min_severity: float = 0.0) -> List[Event]:
        """
        Get events from history with minimum severity.

        Args:
            min_severity: Minimum severity threshold.

        Returns:
            List of events meeting the severity threshold.
        """
        return [event for event in self.event_history if event.severity >= min_severity]

    def get_environment_summary(self) -> Dict:
        """
        Get a summary of the dynamic environment.

        Returns:
            Dictionary containing environment statistics.
        """
        event_counts = {
            EventType.REGULAR.value: 0,
            EventType.CRISIS.value: 0,
            EventType.CUSTOM.value: 0,
        }

        for event in self.event_history:
            event_counts[event.event_type.value] += 1

        avg_severity = 0.0
        if self.event_history:
            avg_severity = sum(event.severity for event in self.event_history) / len(self.event_history)

        return {
            "current_step": self._current_step,
            "total_events": len(self.event_history),
            "event_counts": event_counts,
            "pending_custom_events": len(self.custom_events),
            "pending_queued_events": len(self.event_queue),
            "average_severity": round(avg_severity, 2),
            "crisis_probability": self.crisis_probability,
            "min_crisis_interval": self.min_crisis_interval,
        }
