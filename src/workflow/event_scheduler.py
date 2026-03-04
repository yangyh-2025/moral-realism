"""
Event scheduler for moral realism ABM system.

This module provides EventScheduler class which schedules
events to specific rounds, manages conditional events,
and provides event lookup functionality.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
import logging
import uuid

from src.environment.dynamic_environment import Event


logger = logging.getLogger(__name__)


@dataclass
class ScheduledEvent:
    """
    An event scheduled for a specific round or condition.

    Can be scheduled for a specific round number or
    triggered by a conditional function.
    """

    event_id: str
    event: Event
    target_round: Optional[int] = None
    conditional_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    is_executed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def should_execute(self, current_round: int, context: Dict[str, Any]) -> bool:
        """
        Check if event should execute in current round.

        Args:
            current_round: Current simulation round.
            context: Current simulation context.

        Returns:
            True if event should execute.
        """
        if self.is_executed:
            return False

        if self.target_round is not None:
            return current_round >= self.target_round

        if self.conditional_fn is not None:
            try:
                return self.conditional_fn(context)
            except Exception as e:
                logger.error(f"Error in conditional function: {e}")
                return False

        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event": self.event.to_dict(),
            "target_round": self.target_round,
            "is_executed": self.is_executed,
            "has_conditional_fn": self.conditional_fn is not None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ScheduleStats:
    """Statistics about scheduled events."""

    total_scheduled: int = 0
    total_executed: int = 0
    pending_count: int = 0
    by_round_count: int = 0
    by_condition_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_scheduled": self.total_scheduled,
            "total_executed": self.total_executed,
            "pending_count": self.pending_count,
            "by_round_count": self.by_round_count,
            "by_condition_count": self.by_condition_count,
        }


class EventScheduler:
    """
    Schedule and manage events for simulation rounds.

    Provides:
    - Schedule events for specific rounds
    - Schedule conditional events that trigger based on state
    - Retrieve events for current round
    - Track event execution status
    """

    def __init__(self) -> None:
        """Initialize event scheduler."""
        self._scheduled_events: List[ScheduledEvent] = []
        self._executed_events: List[ScheduledEvent] = []

        # Round-based index for faster lookup
        self._round_index: Dict[int, List[ScheduledEvent]] = {}

    def schedule_event(
        self,
        target_round: int,
        event: Event,
    ) -> str:
        """
        Schedule an event for a specific round.

        Args:
            target_round: The round number to execute event.
            event: The event to schedule.

        Returns:
            The scheduled event ID.
        """
        if target_round < 0:
            raise ValueError(f"Target round must be >= 0, got {target_round}")

        scheduled_id = f"scheduled_{uuid.uuid4().hex[:8]}"

        scheduled = ScheduledEvent(
            event_id=scheduled_id,
            event=event,
            target_round=target_round,
        )

        self._scheduled_events.append(scheduled)

        # Add to round index
        if target_round not in self._round_index:
            self._round_index[target_round] = []
        self._round_index[target_round].append(scheduled)

        logger.info(
            f"Scheduled event '{event.description}' for round {target_round} "
            f"(ID: {scheduled_id})"
        )

        return scheduled_id

    def schedule_conditional_event(
        self,
        conditional_fn: Callable[[Dict[str, Any]], bool],
        event: Event,
        description: Optional[str] = None,
    ) -> str:
        """
        Schedule an event that triggers on a condition.

        Args:
            conditional_fn: Function that takes context and returns True if event should trigger.
            event: The event to schedule.
            description: Optional description for logging.

        Returns:
            The scheduled event ID.
        """
        if not callable(conditional_fn):
            raise TypeError("conditional_fn must be callable")

        scheduled_id = f"scheduled_{uuid.uuid4().hex[:8]}"

        scheduled = ScheduledEvent(
            event_id=scheduled_id,
            event=event,
            conditional_fn=conditional_fn,
        )

        self._scheduled_events.append(scheduled)

        logger.info(
            f"Scheduled conditional event '{event.description}' "
            f"(ID: {scheduled_id}, description: {description})"
        )

        return scheduled_id

    def get_events_for_round(
        self,
        round_number: int,
        context: Optional[Dict[str, Any]] = None,
        execute_immediately: bool = False,
    ) -> List[Event]:
        """
        Get events scheduled for the current round.

        Args:
            round_number: Current simulation round.
            context: Current simulation context for conditional events.
            execute_immediately: If True, mark events as executed.

        Returns:
            List of events for this round.
        """
        if context is None:
            context = {}

        events = []

        # Get round-based events
        if round_number in self._round_index:
            for scheduled in self._round_index[round_number]:
                if not scheduled.is_executed:
                    events.append(scheduled.event)
                    if execute_immediately:
                        scheduled.is_executed = True
                        self._executed_events.append(scheduled)

        # Check conditional events
        for scheduled in self._scheduled_events:
            if (
                scheduled.target_round is None
                and not scheduled.is_executed
            ):
                if scheduled.should_execute(round_number, context):
                    events.append(scheduled.event)
                    if execute_immediately:
                        scheduled.is_executed = True
                        self._executed_events.append(scheduled)

        logger.debug(
            f"Retrieved {len(events)} events for round {round_number}"
        )

        return events

    def mark_executed(self, event_id: str) -> bool:
        """
        Manually mark a scheduled event as executed.

        Args:
            event_id: The scheduled event ID.

        Returns:
            True if found and marked, False otherwise.
        """
        for scheduled in self._scheduled_events:
            if scheduled.event_id == event_id and not scheduled.is_executed:
                scheduled.is_executed = True
                self._executed_events.append(scheduled)
                logger.info(f"Marked event {event_id} as executed")
                return True
        return False

    def cancel_event(self, event_id: str) -> bool:
        """
        Cancel a scheduled event.

        Args:
            event_id: The scheduled event ID.

        Returns:
            True if found and cancelled, False otherwise.
        """
        for i, scheduled in enumerate(self._scheduled_events):
            if scheduled.event_id == event_id and not scheduled.is_executed:
                # Remove from scheduled list
                self._scheduled_events.pop(i)

                # Remove from round index if applicable
                if scheduled.target_round in self._round_index:
                    round_events = self._round_index[scheduled.target_round]
                    if scheduled in round_events:
                        round_events.remove(scheduled)

                    if not round_events:
                        del self._round_index[scheduled.target_round]

                logger.info(f"Cancelled scheduled event {event_id}")
                return True
        return False

    def get_pending_events(self) -> List[ScheduledEvent]:
        """
        Get all pending (not yet executed) scheduled events.

        Returns:
            List of pending scheduled events.
        """
        return [
            s for s in self._scheduled_events
            if not s.is_executed
        ]

    def get_executed_events(self) -> List[ScheduledEvent]:
        """
        Get all executed scheduled events.

        Returns:
            List of executed scheduled events.
        """
        return self._executed_events.copy()

    def get_events_for_round_preview(
        self,
        round_number: int,
    ) -> List[Dict[str, Any]]:
        """
        Preview events scheduled for a specific round (without marking executed).

        Args:
            round_number: The round number.

        Returns:
            List of event dictionaries.
        """
        events = []

        if round_number in self._round_index:
            for scheduled in self._round_index[round_number]:
                if not scheduled.is_executed:
                    events.append({
                        "event_id": scheduled.event_id,
                        "event": scheduled.event.to_dict(),
                        "type": "round_scheduled",
                    })

        # Add conditional events (can't evaluate without context)
        for scheduled in self._scheduled_events:
            if (
                scheduled.target_round is None
                and not scheduled.is_executed
            ):
                events.append({
                    "event_id": scheduled.event_id,
                    "event": scheduled.event.to_dict(),
                    "type": "conditional",
                })

        return events

    def get_stats(self) -> ScheduleStats:
        """
        Get scheduling statistics.

        Returns:
            ScheduleStats with current counts.
        """
        by_round_count = sum(
            1 for s in self._scheduled_events
            if s.target_round is not None
        )
        by_condition_count = sum(
            1 for s in self._scheduled_events
            if s.target_round is None
        )

        return ScheduleStats(
            total_scheduled=len(self._scheduled_events),
            total_executed=len(self._executed_events),
            pending_count=len(self.get_pending_events()),
            by_round_count=by_round_count,
            by_condition_count=by_condition_count,
        )

    def clear_executed(self) -> None:
        """Clear executed events from history."""
        self._executed_events.clear()
        logger.info("Cleared executed events history")

    def clear_all(self) -> None:
        """Clear all scheduled and executed events."""
        self._scheduled_events.clear()
        self._executed_events.clear()
        self._round_index.clear()
        logger.info("Cleared all scheduled events")

    def get_schedule_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the event schedule.

        Returns:
            Dictionary with schedule information.
        """
        # Group pending events by round
        by_round: Dict[int, int] = {}
        for scheduled in self._pending_events():
            if scheduled.target_round is not None:
                by_round[scheduled.target_round] = (
                    by_round.get(scheduled.target_round, 0) + 1
                )

        return {
            "stats": self.get_stats().to_dict(),
            "pending_by_round": by_round,
            "upcoming_rounds": sorted(by_round.keys())[:5],
        }

    @property
    def _pending_events(self) -> List[ScheduledEvent]:
        """Property to get pending events."""
        return self.get_pending_events()

    def bulk_schedule(
        self,
        events: List[Tuple[int, Event]],
    ) -> List[str]:
        """
        Schedule multiple events at once.

        Args:
            events: List of (target_round, event) tuples.

        Returns:
            List of scheduled event IDs.
        """
        return [
            self.schedule_event(target_round, event)
            for target_round, event in events
        ]
