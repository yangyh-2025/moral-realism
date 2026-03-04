"""
Tests for enhanced action types and functionality.

This module tests:
- Extended ActionType enum (30+ actions)
- Complex leadership constraint validation
- Small state behavior options (7 types)
- Multilateral interactions
- Systemic interactions
- Decision history persistence
"""

import pytest
from datetime import datetime

from src.prompts.leadership_prompts import ActionType, ACTION_DESCRIPTIONS
from src.interaction.behavior_selector import BehaviorConstraint, BehaviorSelector
from src.models.leadership_type import LeadershipType, get_leadership_profile
from src.models.agent import Agent, AgentType
from src.models.capability import Capability


class TestExtendedActionTypes:
    """Tests for extended ActionType enum."""

    def test_action_type_count(self):
        """Verify we have 30+ action types."""
        action_types = list(ActionType)
        assert len(action_types) >= 30, f"Expected at least 30 action types, got {len(action_types)}"
        print(f"Action types count: {len(action_types)}")

    def test_security_actions_exist(self):
        """Verify all security action types exist."""
        security_actions = [
            ActionType.SECURITY_MILITARY,
            ActionType.SECURITY_ALLIANCE,
            ActionType.SECURITY_MEDIATION,
        ]
        for action in security_actions:
            assert action.value in ACTION_DESCRIPTIONS

    def test_economic_actions_exist(self):
        """Verify all economic action types exist."""
        assert ActionType.ECONOMIC_TRADE.value in ACTION_DESCRIPTIONS
        assert ActionType.ECONOMIC_SANCTION.value in ACTION_DESCRIPTIONS
        assert ActionType.ECONOMIC_AID.value in ACTION_DESCRIPTIONS

    def test_norm_actions_exist(self):
        """Verify all norm action types exist."""
        assert ActionType.NORM_PROPOSAL.value in ACTION_DESCRIPTIONS
        assert ActionType.NORM_REFORM.value in ACTION_DESCRIPTIONS

    def test_diplomatic_actions_exist(self):
        """Verify all diplomatic action types exist."""
        assert ActionType.DIPLOMATIC_VISIT.value in ACTION_DESCRIPTIONS
        assert ActionType.DIPLOMATIC_ALLIANCE.value in ACTION_DESCRIPTIONS


class TestComplexConstraints:
    """Tests for complex leadership constraint validation."""

    def test_prohibited_first_use_force_constraint(self):
        """Verify prohibited_first_use_force constraint exists."""
        assert BehaviorConstraint.PROHIBITED_FIRST_USE_FORCE
        assert BehaviorConstraint.PROHIBITED_FIRST_USE_FORCE.value == "prohibited_first_use_force"

    def test_prohibited_double_standard_constraint(self):
        """Verify prohibited_double_standard constraint exists."""
        assert BehaviorConstraint.PROHIBITED_DOUBLE_STANDARD
        assert BehaviorConstraint.PROHIBITED_DOUBLE_STANDARD.value == "prohibited_double_standard"

    def test_prohibited_treaty_violation_constraint(self):
        """Verify prohibited_treaty_violation constraint exists."""
        assert BehaviorConstraint.PROHIBITED_TREATY_VIOLATION
        assert BehaviorConstraint.PROHIBITED_TREATY_VIOLATION.value == "prohibited_treaty_violation"

    def test_requires_equal_consultation_constraint(self):
        """Verify requires_equal_consultation constraint exists."""
        assert BehaviorConstraint.REQUIRES_EQUAL_CONSULTATION
        assert BehaviorConstraint.REQUIRES_EQUAL_CONSULTATION.value == "requires_equal_consultation"

    def test_complex_constraint_validation(self):
        """Test complex constraint validation logic."""
        selector = BehaviorSelector(enable_moral=True)

        # Create test agents
        wangdao_agent = Agent(
            agent_id="gp1",
            name="Test Wangdao",
            name_zh="Test Wangdao",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.WANGDAO,
            capability=Capability(agent_id="gp1"),
        )

        hegemon_agent = Agent(
            agent_id="gp2",
            name="Test Hegemon",
            name_zh="Test Hegemon",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.HEGEMON,
            capability=Capability(agent_id="gp2"),
        )

        # Test Wangdao constraints
        result = selector.validate_behavior(
            wangdao_agent,
            "security_military",
            situation={"in_crisis": False},
            context={"action_history": []},
        )

        # Wangdao should be able to use peaceful alternatives
        assert "peaceful" in result.reason.lower() or result.is_valid

    def test_wangdao_forbids_first_use_force(self):
        """Test Wangdao leadership forbids first use of force."""
        selector = BehaviorSelector(enable_moral=True)

        agent = Agent(
            agent_id="gp1",
            name="Test Wangdao",
            name_zh="Test Wangdao",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.WANGDAO,
            capability=Capability(agent_id="gp1"),
        )

        # Context with previous military action
        context = {
            "action_history": [
                {"action_type": "security_military", "timestamp": "2024-01-01T00:00:00Z"}
            ]
        }

        result = selector.validate_behavior(
            agent,
            "security_military",
            situation={"in_crisis": True},
            context=context,
        )

        # Should be flagged or suggest alternatives
        assert not result.is_valid or "consider" in result.reason.lower()


class TestSmallStateBehaviors:
    """Tests for small state behavior options."""

    def test_small_state_action_enum(self):
        """Verify all 7 small state actions exist."""
        from src.agents.small_state_agent import SmallStateAction

        actions = list(SmallStateAction)
        assert len(actions) == 7

        # Verify each action type
        assert SmallStateAction.ALIGN_FOLLOW in actions
        assert SmallStateAction.NEUTRAL_OBSERVE in actions
        assert SmallStateAction.SIDE_SELECTION in actions
        assert SmallStateAction.DEFECT_SWITCH in actions
        assert SmallStateAction.NO_ALLIANCE_COALITION in actions
        assert SmallStateAction.MEDIATION in actions
        assert SmallStateAction.COUNTER_RESPOND in actions

    def test_small_state_initialization(self):
        """Test small state agent initialization."""
        from src.agents.small_state_agent import SmallStateAgent

        agent = SmallStateAgent(
            agent_id="ss1",
            name="Test Small State",
            name_zh="Test Small State",
            agent_type=AgentType.SMALL_STATE,
            leadership_type=LeadershipType.HUNYONG,
            capability=Capability(agent_id="ss1"),
        )

        assert agent.agent_type == AgentType.SMALL_STATE
        assert agent.strategic_stance.value == "neutral"
        assert agent.aligned_with is None


class TestMultilateralInteractions:
    """Tests for multilateral interactions."""

    def test_interaction_level_enum(self):
        """Verify interaction level enum exists."""
        from src.interaction.interaction_manager import InteractionLevel

        levels = list(InteractionLevel)
        assert len(levels) == 3

        assert InteractionLevel.BILATERAL in levels
        assert InteractionLevel.MULTILATERAL in levels
        assert InteractionLevel.SYSTEMIC in levels

    def test_multilateral_interaction_methods(self):
        """Test multilateral interaction methods exist."""
        from src.interaction.interaction_manager import InteractionManager

        manager = InteractionManager(enable_logging=False)

        # Verify methods exist
        assert hasattr(manager, 'execute_multilateral_interaction')
        assert hasattr(manager, '_execute_un_voting')
        assert hasattr(manager, '_execute_alliance_summit')
        assert hasattr(manager, '_execute_regional_negotiation')


class TestSystemicInteractions:
    """Tests for systemic interactions."""

    def test_systemic_interaction_manager(self):
        """Test systemic interaction manager can be imported."""
        from src.interaction.systemic_interaction import SystemicInteractionManager

        manager = SystemicInteractionManager(enable_logging=False)

        # Verify basic functionality
        assert hasattr(manager, 'register_agent')
        assert hasattr(manager, 'shape_international_order')
        assert hasattr(manager, 'evolve_international_norms')
        assert hasattr(manager, 'simulate_values_competition')

    def test_norm_creation(self):
        """Test norm creation."""
        from src.interaction.systemic_interaction import Norm, OrderType

        norm = Norm(
            norm_id="test_norm_1",
            name="Test Norm",
            description="A test norm for testing",
            category="test",
            strength=0.8,
            originator="test_gp",
            adoption_level=0.5,
        )

        assert norm.norm_id == "test_norm_1"
        assert norm.strength == 0.8
        assert norm.adoption_level == 0.5

    def test_order_type_enum(self):
        """Test order type enum exists."""
        from src.interaction.systemic_interaction import OrderType

        order_types = list(OrderType)
        assert len(order_types) == 4


class TestDecisionHistoryPersistence:
    """Tests for decision history persistence."""

    def test_decision_history_methods(self):
        """Test decision history methods exist."""
        from src.metrics.storage import DataStorage

        storage = DataStorage(base_dir="test_data", storage_format="csv")

        # Verify new methods exist
        assert hasattr(storage, 'save_decision_history')
        assert hasattr(storage, 'save_interaction_details')
        assert hasattr(storage, 'save_systemic_event')
        assert hasattr(storage, 'get_decision_history')
        assert hasattr(storage, 'get_interaction_history')
        assert hasattr(storage, 'get_systemic_events')

    def test_save_decision_history(self, tmp_path):
        """Test saving decision history."""
        from src.metrics.storage import DataStorage
        import os

        storage = DataStorage(base_dir=tmp_path, storage_format="csv")

        decision = {
            "agent_id": "test_agent",
            "action_type": "test_action",
            "rationale": "Test rationale",
            "strategic_stance": "aligned",
        }

        result = storage.save_decision_history(
            "test_agent",
            decision,
            round_id=1,
        )

        assert result is not None

        # Verify file was created
        csv_path = os.path.join(tmp_path, "exports", "decisions.csv")
        assert os.path.exists(csv_path)

    def test_save_systemic_event(self, tmp_path):
        """Test saving systemic events."""
        from src.metrics.storage import DataStorage
        import os

        storage = DataStorage(base_dir=tmp_path, storage_format="csv")

        event = {
            "event_id": "test_event_1",
            "event_type": "test_type",
            "description": "Test event",
            "participants": ["gp1", "gp2"],
            "impact_level": 0.7,
        }

        result = storage.save_systemic_event(event, round_id=1)

        assert result is not None

        # Verify file was created
        csv_path = os.path.join(tmp_path, "exports", "systemic_events.csv")
        assert os.path.exists(csv_path)

    def test_get_decision_history(self, tmp_path):
        """Test retrieving decision history."""
        from src.metrics.storage import DataStorage

        storage = DataStorage(base_dir=tmp_path, storage_format="csv")

        # First save some data
        decision = {
            "agent_id": "test_agent",
            "action_type": "test_action",
            "rationale": "Test rationale",
            "strategic_stance": "aligned",
        }
        storage.save_decision_history("test_agent", decision, round_id=1)

        # Now retrieve
        history = storage.get_decision_history()

        assert isinstance(history, list)
        assert len(history) >= 1

    def test_get_systemic_events(self, tmp_path):
        """Test retrieving systemic events."""
        from src.metrics.storage import DataStorage

        storage = DataStorage(base_dir=tmp_path, storage_format="csv")

        # First save some data
        event = {
            "event_id": "test_event_1",
            "event_type": "test_type",
            "description": "Test event",
            "participants": ["gp1", "gp2"],
            "impact_level": 0.7,
        }
        storage.save_systemic_event(event, round_id=1)

        # Now retrieve
        events = storage.get_systemic_events()

        assert isinstance(events, list)


def pytest_run_test(test_class, test_method):
    """Helper to run a pytest test."""
    import sys
    import pytest

    result = pytest.main([
        "-xvs",
        f"{test_class}::{test_method}",
        "-v",
    ])
    return result == 0


if __name__ == "__main__":
    print("Running enhanced functionality tests...")
    print("=" * 50)

    # Run all test classes
    test_classes = [
        ("TestExtendedActionTypes", "test_action_type_count"),
        ("TestExtendedActionTypes", "test_security_actions_exist"),
        ("TestComplexConstraints", "test_complex_constraint_validation"),
        ("TestComplexConstraints", "test_wangdao_forbids_first_use_force"),
        ("TestSmallStateBehaviors", "test_small_state_action_enum"),
        ("TestSmallStateBehaviors", "test_small_state_initialization"),
        ("TestMultilateralInteractions", "test_interaction_level_enum"),
        ("TestSystemicInteractions", "test_systemic_interaction_manager"),
        ("TestSystemicInteractions", "test_norm_creation"),
        ("TestSystemicInteractions", "test_order_type_enum"),
        ("TestDecisionHistoryPersistence", "test_decision_history_methods"),
    ]

    import tempfile
    tmp_path = tempfile.mkdtemp()

    # Run persistence tests with temp directory
    persistence_tests = [
        ("TestDecisionHistoryPersistence", "test_save_decision_history", tmp_path),
        ("TestDecisionHistoryPersistence", "test_save_systemic_event", tmp_path),
        ("TestDecisionHistoryPersistence", "test_get_decision_history", tmp_path),
        ("TestDecisionHistoryPersistence", "test_get_systemic_events", tmp_path),
    ]

    all_passed = True
    passed = 0
    failed = 0

    for test_class, test_method in test_classes:
        result = pytest_run_test(test_class, test_method)
        if result == 0:
            passed += 1
            print(f"PASS: {test_class}::{test_method}")
        else:
            failed += 1
            all_passed = False
            print(f"FAIL: {test_class}::{test_method}")

    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"All tests passed: {all_passed}")
