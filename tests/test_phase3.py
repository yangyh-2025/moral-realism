"""
Phase 3 tests for the moral realism ABM system.

This module contains tests to verify the environment components
implemented in Phase 3 of the project.
"""

import pytest
from src.environment.static_environment import (
    SystemNature,
    SystemArchitecture,
    NormCategory,
    PatternType,
    InternationalNorm,
    PowerDistribution,
    StaticEnvironment,
)
from src.environment.dynamic_environment import (
    EventType,
    RegularEventType,
    CrisisEventType,
    Event,
    DynamicEnvironment,
)
from src.environment.rule_environment import (
    OrderType,
    MoralDimension,
    CapabilityChangeRule,
    MoralEvaluation,
    RuleEnvironment,
)


class TestStaticEnvironment:
    """Tests for static environment components."""

    def test_system_nature_enum(self) -> None:
        """Test system nature enum values."""
        expected = [SystemNature.ANARCHIC, SystemNature.HIERARCHICAL, SystemNature.MIXED]
        for nature in expected:
            assert nature in SystemNature

    def test_system_architecture_enum(self) -> None:
        """Test system architecture enum values."""
        expected = [
            SystemArchitecture.UNIPOLAR,
            SystemArchitecture.BIPOLAR,
            SystemArchitecture.MULTIPOLAR,
            SystemArchitecture.NONPOLAR,
        ]
        for arch in expected:
            assert arch in SystemArchitecture

    def test_norm_category_enum(self) -> None:
        """Test norm category enum values."""
        expected = [
            NormCategory.SOVEREIGNTY,
            NormCategory.FORCE,
            NormCategory.TREATY,
            NormCategory.INTERFERENCE,
        ]
        for category in expected:
            assert category in NormCategory

    def test_international_norm(self) -> None:
        """Test international norm creation and validation."""
        norm = InternationalNorm(
            name="test_norm",
            description="Test norm",
            category=NormCategory.SOVEREIGNTY,
            authority=75.0,
        )
        assert norm.validate() is True

    def test_international_norm_invalid(self) -> None:
        """Test international norm with invalid authority."""
        with pytest.raises(ValueError):
            InternationalNorm(
                name="test_norm",
                description="Test norm",
                category=NormCategory.SOVEREIGNTY,
                authority=150.0,  # Invalid: > 100
            )

    def test_power_distribution(self) -> None:
        """Test power distribution creation."""
        dist = PowerDistribution(
            agent_ids=["agent1", "agent2", "agent3"],
            power_shares=[0.5, 0.3, 0.2],
        )
        assert dist.get_agent_power_share("agent1") == 0.5
        assert dist.get_agent_power_share("agent2") == 0.3

    def test_power_distribution_invalid(self) -> None:
        """Test power distribution with invalid shares."""
        with pytest.raises(ValueError):
            PowerDistribution(
                agent_ids=["agent1", "agent2"],
                power_shares=[0.3, 0.3],  # Sum != 1.0
            )

    def test_power_distribution_hhi(self) -> None:
        """Test HHI calculation."""
        dist = PowerDistribution(
            agent_ids=["agent1", "agent2", "agent3"],
            power_shares=[0.5, 0.3, 0.2],
        )
        hhi = dist.calculate_hhi()
        assert 0 < hhi < 10000  # HHI range

    def test_static_environment_initialization(self) -> None:
        """Test static environment initialization."""
        env = StaticEnvironment(
            system_nature=SystemNature.ANARCHIC,
            system_architecture=SystemArchitecture.UNIPOLAR,
        )
        assert env.system_nature == SystemNature.ANARCHIC
        assert env.system_architecture == SystemArchitecture.UNIPOLAR
        assert len(env.norms) > 0  # Base norms should be initialized

    def test_static_environment_norms_by_category(self) -> None:
        """Test getting norms by category."""
        env = StaticEnvironment()
        sovereignty_norms = env.get_norms_by_category(NormCategory.SOVEREIGNTY)
        assert len(sovereignty_norms) > 0
        for norm in sovereignty_norms:
            assert norm.category == NormCategory.SOVEREIGNTY

    def test_static_environment_get_norm(self) -> None:
        """Test getting a specific norm."""
        env = StaticEnvironment()
        norm = env.get_norm("sovereign_equality")
        assert norm is not None
        assert norm.name == "sovereign_equality"

    def test_static_environment_add_remove_norm(self) -> None:
        """Test adding and removing norms."""
        env = StaticEnvironment()
        initial_count = len(env.norms)

        new_norm = InternationalNorm(
            name="custom_norm",
            description="Custom test norm",
            category=NormCategory.TREATY,
            authority=60.0,
        )
        env.add_norm(new_norm)
        assert len(env.norms) == initial_count + 1

        removed = env.remove_norm("custom_norm")
        assert removed is True
        assert len(env.norms) == initial_count

    def test_static_environment_update_norm_authority(self) -> None:
        """Test updating norm authority."""
        env = StaticEnvironment()
        updated = env.update_norm_authority("sovereign_equality", 95.0)
        assert updated is True

        norm = env.get_norm("sovereign_equality")
        assert norm.authority == 95.0

    def test_static_environment_power_distribution_initialization(self) -> None:
        """Test power distribution initialization."""
        env = StaticEnvironment()
        env.initialize_power_distribution(
            architecture=SystemArchitecture.UNIPOLAR,
            agent_ids=["agent1", "agent2", "agent3"],
        )
        assert env.power_distribution is not None
        assert env.system_architecture == SystemArchitecture.UNIPOLAR

    def test_static_environment_pattern_type_calculation(self) -> None:
        """Test pattern type calculation."""
        env = StaticEnvironment()
        env.initialize_power_distribution(architecture=SystemArchitecture.UNIPOLAR)
        pattern = env.calculate_pattern_type()
        assert pattern == PatternType.HEGEMONIC_STABILITY

    def test_static_environment_power_concentration(self) -> None:
        """Test power concentration calculation."""
        env = StaticEnvironment()
        env.initialize_power_distribution(architecture=SystemArchitecture.UNIPOLAR)

        concentration = env.calculate_power_concentration()
        assert "hhi" in concentration
        assert "top1_share" in concentration
        assert "top3_share" in concentration
        assert "gini" in concentration

    def test_static_environment_summary(self) -> None:
        """Test environment summary."""
        env = StaticEnvironment()
        env.initialize_power_distribution(architecture=SystemArchitecture.MULTIPOLAR)

        summary = env.get_system_summary()
        assert "system_nature" in summary
        assert "system_architecture" in summary
        assert "norm_count" in summary
        assert "pattern_type" in summary


class TestDynamicEnvironment:
    """Tests for dynamic environment components."""

    def test_event_type_enums(self) -> None:
        """Test event type enums."""
        assert EventType.REGULAR in EventType
        assert EventType.CRISIS in EventType
        assert EventType.CUSTOM in EventType

    def test_regular_event_type_enum(self) -> None:
        """Test regular event type enum."""
        assert RegularEventType.LEADERSHIP_CHANGE in RegularEventType
        assert RegularEventType.ECONOMIC_CYCLE in RegularEventType
        assert RegularEventType.DIPLOMATIC_SUMMIT in RegularEventType

    def test_crisis_event_type_enum(self) -> None:
        """Test crisis event type enum."""
        assert CrisisEventType.MILITARY_CONFLICT in CrisisEventType
        assert CrisisEventType.ECONOMIC_CRISIS in CrisisEventType
        assert CrisisEventType.TERRITORIAL_DISPUTE in CrisisEventType

    def test_event_creation(self) -> None:
        """Test event creation and validation."""
        event = Event(
            event_id="test_event_1",
            event_type=EventType.CRISIS,
            sub_type="military_conflict",
            description="Test conflict event",
            severity=75.0,
            affected_agents=["agent1", "agent2"],
            context={"type": "conventional"},
        )
        assert event.validate() is True

    def test_event_invalid_severity(self) -> None:
        """Test event with invalid severity."""
        with pytest.raises(ValueError):
            Event(
                event_id="test_event_1",
                event_type=EventType.CRISIS,
                sub_type="military_conflict",
                description="Test",
                severity=150.0,  # Invalid: > 100
                affected_agents=["agent1"],
            )

    def test_event_to_dict(self) -> None:
        """Test event serialization to dictionary."""
        event = Event(
            event_id="test_event_1",
            event_type=EventType.REGULAR,
            sub_type="economic_cycle",
            description="Test event",
            severity=50.0,
            affected_agents=["agent1"],
        )
        event_dict = event.to_dict()
        assert event_dict["event_id"] == "test_event_1"
        assert event_dict["event_type"] == "regular"
        assert "timestamp" in event_dict

    def test_dynamic_environment_initialization(self) -> None:
        """Test dynamic environment initialization."""
        env = DynamicEnvironment(crisis_probability=0.2, min_crisis_interval=5)
        assert env.crisis_probability == 0.2
        assert env.min_crisis_interval == 5
        assert len(env.event_history) == 0

    def test_dynamic_environment_regular_events(self) -> None:
        """Test regular event generation."""
        env = DynamicEnvironment()
        # Advance to step 10 (economic cycle occurs every 10 steps)
        for _ in range(10):
            env.advance_step()

        agent_ids = ["agent1", "agent2", "agent3", "agent4", "agent5"]
        events = env.get_regular_events(agent_ids)

        # At step 10, economic cycle event should occur
        assert len(events) > 0
        economic_events = [e for e in events if e.sub_type == "economic_cycle"]
        assert len(economic_events) > 0

    def test_dynamic_environment_regular_events_at_intervals(self) -> None:
        """Test regular events occur at correct intervals."""
        env = DynamicEnvironment()

        # Economic cycle occurs every 10 steps
        env.set_regular_event_interval(RegularEventType.ECONOMIC_CYCLE, 5)

        agent_ids = ["agent1", "agent2"]
        env._current_step = 5

        events = env.get_regular_events(agent_ids)
        economic_events = [e for e in events if e.sub_type == "economic_cycle"]
        assert len(economic_events) > 0

    def test_dynamic_environment_random_events(self) -> None:
        """Test random crisis event generation."""
        env = DynamicEnvironment(crisis_probability=1.0, min_crisis_interval=1)
        env.advance_step()

        agent_ids = ["agent1", "agent2", "agent3"]
        events = env.get_random_events(agent_ids)

        # With probability 1.0, should generate a crisis
        assert len(events) > 0
        assert events[0].event_type == EventType.CRISIS

    def test_dynamic_environment_custom_events(self) -> None:
        """Test custom event addition and retrieval."""
        env = DynamicEnvironment()

        event_id = env.add_custom_event(
            event_type="user_defined",
            description="Custom test event",
            severity=60.0,
            affected_agents=["agent1", "agent2"],
            context={"source": "user"},
        )

        assert event_id is not None

        custom_events = env.get_custom_events()
        assert len(custom_events) == 1
        assert custom_events[0].sub_type == "user_defined"

    def test_dynamic_environment_get_all_pending(self) -> None:
        """Test getting all pending events."""
        env = DynamicEnvironment()
        env.advance_step()

        # Add custom event
        env.add_custom_event(
            event_type="custom_test",
            description="Custom",
            severity=50.0,
            affected_agents=["agent1"],
        )

        agent_ids = ["agent1", "agent2", "agent3"]
        all_events = env.get_all_pending_events(agent_ids)

        # Should include regular events and custom events
        assert len(all_events) > 0

    def test_dynamic_environment_record_event(self) -> None:
        """Test event recording to history."""
        env = DynamicEnvironment()

        event = Event(
            event_id="test_1",
            event_type=EventType.REGULAR,
            sub_type="test",
            description="Test",
            severity=40.0,
            affected_agents=["agent1"],
        )

        env.record_event(event)
        assert len(env.event_history) == 1
        assert env.event_history[0].event_id == "test_1"

    def test_dynamic_environment_get_event_summary(self) -> None:
        """Test event summary retrieval."""
        env = DynamicEnvironment()

        # Record some events
        for i in range(5):
            event = Event(
                event_id=f"event_{i}",
                event_type=EventType.REGULAR,
                sub_type="test",
                description=f"Event {i}",
                severity=50.0,
                affected_agents=["agent1"],
            )
            env.record_event(event)

        summary = env.get_event_summary(limit=3)
        assert len(summary) == 3

    def test_dynamic_environment_get_events_by_type(self) -> None:
        """Test filtering events by type."""
        env = DynamicEnvironment()

        # Add different event types
        event1 = Event(
            event_id="reg_1",
            event_type=EventType.REGULAR,
            sub_type="test",
            description="Regular",
            severity=40.0,
            affected_agents=["agent1"],
        )
        event2 = Event(
            event_id="crisis_1",
            event_type=EventType.CRISIS,
            sub_type="test",
            description="Crisis",
            severity=70.0,
            affected_agents=["agent1"],
        )

        env.record_event(event1)
        env.record_event(event2)

        regular_events = env.get_events_by_type(EventType.REGULAR)
        assert len(regular_events) == 1

        crisis_events = env.get_events_by_type(EventType.CRISIS)
        assert len(crisis_events) == 1

    def test_dynamic_environment_get_events_by_severity(self) -> None:
        """Test filtering events by severity."""
        env = DynamicEnvironment()

        # Add events with different severities
        for severity in [30.0, 60.0, 90.0]:
            event = Event(
                event_id=f"event_{severity}",
                event_type=EventType.REGULAR,
                sub_type="test",
                description=f"Severity {severity}",
                severity=severity,
                affected_agents=["agent1"],
            )
            env.record_event(event)

        high_severity_events = env.get_events_by_severity(min_severity=60.0)
        assert len(high_severity_events) == 2

    def test_dynamic_environment_set_interval(self) -> None:
        """Test setting regular event interval."""
        env = DynamicEnvironment()
        env.set_regular_event_interval(RegularEventType.LEADERSHIP_CHANGE, 25)
        assert env._regular_event_intervals[RegularEventType.LEADERSHIP_CHANGE] == 25

    def test_dynamic_environment_advance_step(self) -> None:
        """Test step advancement."""
        env = DynamicEnvironment()
        assert env.get_current_step() == 0

        env.advance_step()
        assert env.get_current_step() == 1

        env.advance_step()
        assert env.get_current_step() == 2

    def test_dynamic_environment_summary(self) -> None:
        """Test environment summary."""
        env = DynamicEnvironment()

        # Record some events
        for i in range(3):
            event = Event(
                event_id=f"event_{i}",
                event_type=EventType.REGULAR,
                sub_type="test",
                description=f"Event {i}",
                severity=50.0,
                affected_agents=["agent1"],
            )
            env.record_event(event)

        summary = env.get_environment_summary()
        assert "current_step" in summary
        assert "total_events" in summary
        assert summary["total_events"] == 3


class TestRuleEnvironment:
    """Tests for rule environment components."""

    def test_order_type_enum(self) -> None:
        """Test order type enum."""
        expected = [
            OrderType.HEGEMONIC_ORDER,
            OrderType.BALANCE_OF_POWER,
            OrderType.CONCERT_OF_POWERS,
            OrderType.ANARCHIC_DISORDER,
            OrderType.MULTIPOLAR_BALANCE,
        ]
        for order_type in expected:
            assert order_type in OrderType

    def test_moral_dimension_enum(self) -> None:
        """Test moral dimension enum."""
        expected = [
            MoralDimension.RESPECT_FOR_NORMS,
            MoralDimension.HUMANITARIAN_CONCERN,
            MoralDimension.PEACEFUL_RESOLUTION,
            MoralDimension.INTERNATIONAL_COOPERATION,
            MoralDimension.JUSTICE_AND_FAIRNESS,
        ]
        for dimension in expected:
            assert dimension in MoralDimension

    def test_capability_change_rule(self) -> None:
        """Test capability change rule."""
        rule = CapabilityChangeRule(
            max_single_step_change=15.0,
            max_absolute_power_gain=25.0,
        )

        is_valid, reason = rule.validate_change(50.0, 60.0)
        assert is_valid is True

    def test_capability_change_rule_invalid(self) -> None:
        """Test capability change rule with invalid change."""
        rule = CapabilityChangeRule(
            max_single_step_change=10.0,
            max_absolute_power_gain=25.0,
        )

        is_valid, reason = rule.validate_change(50.0, 70.0)
        assert is_valid is False

    def test_rule_environment_initialization(self) -> None:
        """Test rule environment initialization."""
        env = RuleEnvironment()
        assert env.capability_change_rule is not None

    def test_rule_environment_custom_rule(self) -> None:
        """Test rule environment with custom rules."""
        custom_rule = CapabilityChangeRule(max_single_step_change=30.0)
        env = RuleEnvironment(capability_change_rule=custom_rule)

        assert env.capability_change_rule.max_single_step_change == 30.0

    def test_validate_capability_change_valid(self) -> None:
        """Test valid capability change."""
        env = RuleEnvironment()
        is_valid, reason = env.validate_capability_change(
            agent_id="agent1",
            old_capability=50.0,
            new_capability=55.0,
        )
        assert is_valid is True

    def test_validate_capability_change_invalid(self) -> None:
        """Test invalid capability change."""
        env = RuleEnvironment()
        is_valid, reason = env.validate_capability_change(
            agent_id="agent1",
            old_capability=50.0,
            new_capability=150.0,  # Too large
        )
        assert is_valid is False

    def test_validate_capability_change_in_crisis(self) -> None:
        """Test capability change during crisis."""
        env = RuleEnvironment()
        is_valid, reason = env.validate_capability_change(
            agent_id="agent1",
            old_capability=50.0,
            new_capability=70.0,  # Large gain
            context={"in_crisis": True},
        )
        # Large gains during crisis should be rejected
        assert is_valid is False

    def test_evaluate_moral_level(self) -> None:
        """Test moral level evaluation."""
        env = RuleEnvironment()

        actions = [
            {"type": "diplomatic_negotiation", "upholds_norm": True},
            {"type": "humanitarian_aid"},
        ]
        interactions = [
            {"type": "peaceful_resolution"},
            {"type": "alliance"},
        ]

        evaluations = env.evaluate_moral_level("agent1", actions, interactions)

        assert len(evaluations) == 5  # All 5 dimensions
        assert all(isinstance(ev, MoralEvaluation) for ev in evaluations)

        # Check all dimensions are present
        dimensions = [ev.dimension for ev in evaluations]
        assert MoralDimension.RESPECT_FOR_NORMS in dimensions
        assert MoralDimension.HUMANITARIAN_CONCERN in dimensions
        assert MoralDimension.PEACEFUL_RESOLUTION in dimensions
        assert MoralDimension.INTERNATIONAL_COOPERATION in dimensions
        assert MoralDimension.JUSTICE_AND_FAIRNESS in dimensions

    def test_evaluate_moral_level_with_violations(self) -> None:
        """Test moral evaluation with violations."""
        env = RuleEnvironment()

        actions = [
            {"type": "military_action", "violates_norm": True, "severity": 1.0},
            {"type": "disregard_humanitarian"},
        ]
        interactions = [
            {"type": "force_confrontation"},
        ]

        evaluations = env.evaluate_moral_level("agent1", actions, interactions)

        # Scores should be lower due to violations
        peaceful_ev = next(ev for ev in evaluations if ev.dimension == MoralDimension.PEACEFUL_RESOLUTION)
        assert peaceful_ev.score < 50  # Should be penalized

    def test_calculate_moral_level_index(self) -> None:
        """Test overall moral level index calculation."""
        env = RuleEnvironment()

        evaluations = [
            MoralEvaluation(
                dimension=MoralDimension.RESPECT_FOR_NORMS,
                score=80.0,
                justification="Test",
            ),
            MoralEvaluation(
                dimension=MoralDimension.HUMANITARIAN_CONCERN,
                score=70.0,
                justification="Test",
            ),
            MoralEvaluation(
                dimension=MoralDimension.PEACEFUL_RESOLUTION,
                score=90.0,
                justification="Test",
            ),
            MoralEvaluation(
                dimension=MoralDimension.INTERNATIONAL_COOPERATION,
                score=60.0,
                justification="Test",
            ),
            MoralEvaluation(
                dimension=MoralDimension.JUSTICE_AND_FAIRNESS,
                score=75.0,
                justification="Test",
            ),
        ]

        index = env.calculate_moral_level_index(evaluations)
        assert 0 <= index <= 100

    def test_check_order_evolution_hegemonic(self) -> None:
        """Test order evolution detection for hegemonic order."""
        env = RuleEnvironment()

        power_distribution = {
            "hegemon": 0.5,
            "state1": 0.2,
            "state2": 0.15,
            "state3": 0.15,
        }
        norm_authorities = {
            "sovereign_equality": 85.0,
            "prohibition_of_force": 75.0,
        }
        conflict_levels = {
            ("state1", "state2"): 20.0,
        }

        order_type, analysis = env.check_order_evolution(
            power_distribution, norm_authorities, conflict_levels
        )

        assert order_type == OrderType.HEGEMONIC_ORDER
        assert "power_concentration" in analysis
        assert "stability_score" in analysis

    def test_check_order_evolution_balance_of_power(self) -> None:
        """Test order evolution detection for balance of power."""
        env = RuleEnvironment()

        power_distribution = {
            "pole1": 0.35,
            "pole2": 0.35,
            "state1": 0.1,
            "state2": 0.1,
            "state3": 0.1,
        }
        norm_authorities = {"norm1": 60.0}
        conflict_levels = {("pole1", "pole2"): 30.0}

        order_type, analysis = env.check_order_evolution(
            power_distribution, norm_authorities, conflict_levels
        )

        assert order_type == OrderType.BALANCE_OF_POWER

    def test_determine_order_type_multipolar(self) -> None:
        """Test order type determination for multipolar."""
        env = RuleEnvironment()

        order_type = env.determine_order_type(
            top_share=0.25,  # Low concentration
            top3_share=0.65,  # High combined top 3
            norm_authority=50.0,
            conflict_level=50.0,
        )

        assert order_type == OrderType.MULTIPOLAR_BALANCE

    def test_determine_order_type_anarchic(self) -> None:
        """Test order type determination for anarchic."""
        env = RuleEnvironment()

        order_type = env.determine_order_type(
            top_share=0.20,
            top3_share=0.50,
            norm_authority=30.0,  # Low norm authority
            conflict_level=70.0,  # High conflict
        )

        assert order_type == OrderType.ANARCHIC_DISORDER

    def test_set_moral_weight(self) -> None:
        """Test setting moral dimension weight."""
        env = RuleEnvironment()
        env.set_moral_weight(MoralDimension.RESPECT_FOR_NORMS, 0.5)

        assert env._moral_weights[MoralDimension.RESPECT_FOR_NORMS] == 0.5

    def test_set_moral_weight_invalid(self) -> None:
        """Test setting invalid moral weight."""
        env = RuleEnvironment()

        with pytest.raises(ValueError):
            env.set_moral_weight(MoralDimension.RESPECT_FOR_NORMS, 1.5)

    def test_normalize_moral_weights(self) -> None:
        """Test normalizing moral weights."""
        env = RuleEnvironment()

        # Set weights that don't sum to 1
        env.set_moral_weight(MoralDimension.RESPECT_FOR_NORMS, 0.5)
        env.set_moral_weight(MoralDimension.HUMANITARIAN_CONCERN, 0.5)
        env.set_moral_weight(MoralDimension.PEACEFUL_RESOLUTION, 0.5)

        total = sum(env._moral_weights.values())
        assert total != 1.0

        env.normalize_moral_weights()

        total = sum(env._moral_weights.values())
        assert abs(total - 1.0) < 0.001  # Should sum to 1

    def test_rule_environment_summary(self) -> None:
        """Test rule environment summary."""
        env = RuleEnvironment()
        summary = env.get_environment_summary()

        assert "max_single_step_change" in summary
        assert "max_absolute_power_gain" in summary
        assert "power_decay_factor" in summary
        assert "moral_weights" in summary


def test_module_imports():
    """Test that all environment modules can be imported."""
    from src.environment import (
        StaticEnvironment,
        DynamicEnvironment,
        RuleEnvironment,
        Event,
        InternationalNorm,
        PowerDistribution,
        CapabilityChangeRule,
    )

    assert True  # All imports successful
