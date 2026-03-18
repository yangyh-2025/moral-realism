"""
Unit tests for Environment module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from datetime import datetime
from typing import Dict, List

try:
    from domain.environment.environment_engine import (
        EnvironmentEngine,
        Event,
        EventPriority,
        EventScheduler,
        InternationalNorm,
        EnvironmentState
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not CORE_AVAILABLE,
    reason="Core module not available"
)


@pytest.mark.unit
class TestEventPriority:
    """Test EventPriority enum"""

    def test_priority_values(self):
        """Test priority values"""
        assert EventPriority.CRITICAL.value == 0
        assert EventPriority.HIGH.value == 1
        assert EventPriority.NORMAL.value == 2
        assert EventPriority.LOW.value == 3

    def test_priority_ordering(self):
        """Test priority ordering"""
        assert EventPriority.CRITICAL < EventPriority.HIGH
        assert EventPriority.HIGH < EventPriority.NORMAL
        assert EventPriority.NORMAL < EventPriority.LOW


@pytest.mark.unit
class TestEvent:
    """Test Event dataclass"""

    def test_event_creation(self):
        """Test creating event"""
        event = Event(
            _priority_index=EventPriority.NORMAL.value,
            event_id="test_event",
            event_type="user_defined",
            name="Test Event",
            description="A test event",
            participants=["agent1", "agent2"],
            impact_level=0.5,
            priority=EventPriority.NORMAL
        )

        assert event.event_id == "test_event"
        assert event.event_type == "user_defined"
        assert event.name == "Test Event"
        assert event.participants == ["agent1", "agent2"]
        assert event.impact_level == 0.5
        assert event.priority == EventPriority.NORMAL
        assert not event.cancelled

    def test_event_with_default_values(self):
        """Test creating event with defaults"""
        event = Event(
            _priority_index=2,
            event_id="test",
            event_type="periodic",
            name="Test",
            description="Test event"
        )

        assert event.participants == []
        assert event.impact_level == 0.5
        assert event.priority == EventPriority.NORMAL
        assert not event.cancelled
        assert event.callback is None

    def test_event_cancel(self):
        """Test cancelling event"""
        event = Event(
            _priority_index=2,
            event_id="test",
            event_type="periodic",
            name="Test",
            description="Test event"
        )

        event.cancelled = True
        assert event.cancelled


@pytest.mark.unit
class TestEventScheduler:
    """Test EventScheduler class"""

    @pytest.fixture
    def scheduler(self):
        """Create event scheduler"""
        return EventScheduler()

    def test_scheduler_initialization(self, scheduler):
        """Test scheduler initialization"""
        assert scheduler.get_pending_count() == 0
        stats = scheduler.get_stats()
        assert stats["total_scheduled"] == 0
        assert stats["total_executed"] == 0
        assert stats["total_cancelled"] == 0

    def test_schedule_event(self, scheduler):
        """Test scheduling event"""
        event = Event(
            _priority_index=EventPriority.NORMAL.value,
            event_id="test_event",
            event_type="user_defined",
            name="Test Event",
            description="Test description",
            priority=EventPriority.NORMAL
        )

        event_id = scheduler.schedule(event)

        assert event_id == "test_event"
        assert scheduler.get_pending_count() == 1
        stats = scheduler.get_stats()
        assert stats["total_scheduled"] == 1

    def test_schedule_multiple_events(self, scheduler):
        """Test scheduling multiple events"""
        for i in range(5):
            event = Event(
                _priority_index=EventPriority.NORMAL.value,
                event_id=f"event_{i}",
                event_type="periodic",
                name=f"Event {i}",
                description=f"Event {i}",
                priority=EventPriority.NORMAL
            )
            scheduler.schedule(event)

        assert scheduler.get_pending_count() == 5

    def test_schedule_with_priority_ordering(self, scheduler):
        """Test that events are scheduled by priority"""
        # Schedule events with different priorities
        normal = Event(
            _priority_index=EventPriority.NORMAL.value,
            event_id="normal",
            event_type="periodic",
            name="Normal",
            description="Normal",
            priority=EventPriority.NORMAL
        )

        high = Event(
            _priority_index=EventPriority.HIGH.value,
            event_id="high",
            event_type="periodic",
            name="High",
            description="High",
            priority=EventPriority.HIGH
        )

        scheduler.schedule(normal)
        scheduler.schedule(high)

        # High priority event should be executed first
        result = scheduler.execute_next(0)
        assert result is not None
        assert result.event_id == "high"

    def test_schedule_cancelled_event(self, scheduler):
        """Test scheduling already cancelled event"""
        event = Event(
            _priority_index=2,
            event_id="cancelled_event",
            event_type="periodic",
            name="Cancelled",
            description="Cancelled event",
            cancelled=True
        )

        event_id = scheduler.schedule(event)

        assert event_id == "cancelled_event"
        assert scheduler.get_pending_count() == 0  # Should not be added

    def test_cancel_event(self, scheduler):
        """Test cancelling scheduled event"""
        event = Event(
            _priority_index=2,
            event_id="test_event",
            event_type="periodic",
            name="Test",
            description="Test",
            priority=EventPriority.NORMAL
        )

        scheduler.schedule(event)
        assert scheduler.get_pending_count() == 1

        result = scheduler.cancel("test_event")
        assert result is True
        assert scheduler.get_pending_count() == 0

    def test_cancel_nonexistent_event(self, scheduler):
        """Test cancelling non-existent event"""
        result = scheduler.cancel("nonexistent")
        assert result is False

    def test_execute_next(self, scheduler):
        """Test executing next event"""
        event = Event(
            _priority_index=2,
            event_id="test_event",
            event_type="periodic",
            name="Test",
            description="Test",
            priority=EventPriority.NORMAL
        )

        scheduler.schedule(event)

        executed = scheduler.execute_next(0)

        assert executed is not None
        assert executed.event_id == "test_event"
        assert scheduler.get_pending_count() == 0

    def test_execute_next_with_callback(self, scheduler):
        """Test executing event with callback"""
        callback_called = []

        def test_callback(event, context):
            callback_called.append(event.event_id)

        event = Event(
            _priority_index=2,
            event_id="test_event",
            event_type="periodic",
            name="Test",
            description="Test",
            callback=test_callback,
            priority=EventPriority.NORMAL
        )

        scheduler.schedule(event)
        scheduler.execute_next(0)

        assert len(callback_called) == 1
        assert callback_called[0] == "test_event"

    def test_execute_next_empty_queue(self, scheduler):
        """Test executing from empty queue"""
        result = scheduler.execute_next(0)
        assert result is None

    def test_schedule_delayed_event(self, scheduler):
        """Test scheduling delayed event"""
        event = Event(
            _priority_index=2,
            event_id="delayed_event",
            event_type="periodic",
            name="Delayed",
            description="Delayed event",
            priority=EventPriority.NORMAL
        )

        event_id = scheduler.schedule_delayed(event, delay_rounds=5, current_round=0)

        assert event_id == "delayed_event"

        # Should not execute at round 0
        result = scheduler.execute_next(0)
        assert result is None

        # Should not execute at round 4
        for i in range(4):
            result = scheduler.execute_next(i)
            assert result is None

        # Should execute at round 5
        result = scheduler.execute_next(5)
        assert result is not None
        assert result.event_id == "delayed_event"

    def test_get_stats(self, scheduler):
        """Test getting scheduler stats"""
        # Schedule and execute some events
        for i in range(3):
            event = Event(
                _priority_index=2,
                event_id=f"event_{i}",
                event_type="periodic",
                name=f"Event {i}",
                description=f"Event {i}",
                priority=EventPriority.NORMAL
            )
            scheduler.schedule(event)
            scheduler.execute_next(0)

        stats = scheduler.get_stats()
        assert stats["total_scheduled"] == 3
        assert stats["total_executed"] == 3
        assert stats["total_cancelled"] == 0

    def test_clear(self, scheduler):
        """Test clearing scheduler"""
        for i in range(3):
            event = Event(
                _priority_index=2,
                event_id=f"event_{i}",
                event_type="periodic",
                name=f"Event {i}",
                description=f"Event {i}",
                priority=EventPriority.NORMAL
            )
            scheduler.schedule(event)

        assert scheduler.get_pending_count() == 3

        scheduler.clear()
        assert scheduler.get_pending_count() == 0


@pytest.mark.unit
class TestEnvironmentEngine:
    """Test EnvironmentEngine class"""

    @pytest.fixture
    def engine(self):
        """Create environment engine"""
        return EnvironmentEngine(initial_round=0, seed=42)

    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine.state.current_round == 0
        assert len(engine.state.norms) > 0
        assert engine.state.season == "spring"

    def test_default_norms_created(self, engine):
        """Test that default norms are created"""
        assert len(engine.state.norms) == 4

        norm_names = [norm.name for norm in engine.state.norms]
        assert "主权平等原则" in norm_names
        assert "不使用武力原则" in norm_names
        assert "条约必须信守原则" in norm_names
        assert "不干涉内政原则" in norm_names

    def test_update_round(self, engine):
        """Test updating round"""
        initial_round = engine.state.current_round
        new_round = engine.update_round()

        assert new_round == initial_round + 1
        assert engine.state.current_round == new_round

    def test_update_round_affects_season(self, engine):
        """Test that round update affects season"""
        seasons = []
        for i in range(12):
            seasons.append(engine.state.season)
            engine.update_round()

        assert len(set(seasons)) == 4  # Should see all 4 seasons
        assert all(s in ["spring", "summer", "fall", "winter"] for s in seasons)

    def test_trigger_periodic_events(self, engine):
        """Test triggering periodic events"""
        agent_ids = ["agent1", "agent2", "agent3"]

        events = engine.trigger_periodic_events(agent_ids)

        assert len(events) > 0

    def test_trigger_random_events(self, engine):
        """Test triggering random events"""
        agent_ids = ["agent1", "agent2", "agent3"]

        events = engine.trigger_random_events(
            agent_ids,
            probability=1.0  # High probability to trigger
        )

        # With probability=1.0, should always trigger
        assert len(events) > 0

    def test_trigger_random_events_with_low_probability(self, engine):
        """Test triggering random events with low probability"""
        agent_ids = ["agent1", "agent2", "agent3"]

        events = engine.trigger_random_events(
            agent_ids,
            probability=0.0  # Zero probability
        )

        # With probability=0.0, should not trigger
        assert len(events) == 0

    def test_add_user_event(self, engine):
        """Test adding user event"""
        event = Event(
            _priority_index=2,
            event_id="user_event",
            event_type="user_defined",
            name="User Event",
            description="User defined event",
            priority=EventPriority.HIGH
        )

        engine.add_user_event(event)

        assert len(engine.state.active_events) == 1
        assert engine.state.active_events[0].event_id == "user_event"

    def test_clear_active_events(self, engine):
        """Test clearing active events"""
        # Add some events
        for i in range(3):
            event = Event(
                _priority_index=2,
                event_id=f"event_{i}",
                event_type="user_defined",
                name=f"Event {i}",
                description=f"Event {i}",
                priority=EventPriority.NORMAL
            )
            engine.add_user_event(event)

        assert len(engine.state.active_events) == 3
        assert len(engine.state.event_history) == 0

        engine.clear_active_events()

        assert len(engine.state.active_events) == 0
        assert len(engine.state.event_history) == 3

    def test_schedule_event(self, engine):
        """Test scheduling event"""
        event = Event(
            _priority_index=2,
            event_id="test_event",
            event_type="user_defined",
            name="Test",
            description="Test",
            priority=EventPriority.NORMAL
        )

        event_id = engine.schedule_event(event)

        assert event_id == "test_event"
        stats = engine.get_scheduler_stats()
        assert stats["stats"]["total_scheduled"] == 1

    def test_cancel_event(self, engine):
        """Test cancelling event"""
        event = Event(
            _priority_index=2,
            event_id="test_event",
            event_type="user_defined",
            name="Test",
            description="Test",
            priority=EventPriority.NORMAL
        )

        engine.schedule_event(event)
        result = engine.cancel_event("test_event")

        assert result is True

    def test_execute_scheduled_events(self, engine):
        """Test executing scheduled events"""
        # Schedule some events
        for i in range(3):
            event = Event(
                _priority_index=2,
                event_id=f"event_{i}",
                event_type="periodic",
                name=f"Event {i}",
                description=f"Event {i}",
                priority=EventPriority.NORMAL
            )
            engine.schedule_event(event)

        executed = engine.execute_scheduled_events()

        assert len(executed) == 3

    def test_set_overlap_policy_valid(self, engine):
        """Test setting valid overlap policy"""
        valid_policies = ["merge", "replace", "queue", "ignore"]

        for policy in valid_policies:
            engine.set_overlap_policy(policy)
            assert engine._overlap_policy == policy

    def test_set_overlap_policy_invalid(self, engine):
        """Test setting invalid overlap policy"""
        with pytest.raises(ValueError):
            engine.set_overlap_policy("invalid_policy")

    def test_get_full_state(self, engine):
        """Test getting full environment state"""
        state = engine.get_full_state()

        assert "current_round" in state
        assert "current_date" in state
        assert "season" in state
        assert "norms" in state
        assert "active_events" in state
        assert "scheduler_stats" in state

        assert state["current_round"] == 0
        assert state["season"] == "spring"


@pytest.mark.unit
class TestInternationalNorm:
    """Test InternationalNorm dataclass"""

    def test_norm_creation(self):
        """Test creating international norm"""
        norm = InternationalNorm(
            norm_id="sovereign_equality",
            name="主权平等原则",
            description="所有国家主权平等",
            validity=100.0,
            adherence_rate=1.0
        )

        assert norm.norm_id == "sovereign_equality"
        assert norm.name == "主权平等原则"
        assert norm.validity == 100.0
        assert norm.adherence_rate == 1.0
