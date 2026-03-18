"""
Unit tests for Interaction Rules module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from datetime import datetime
from typing import Dict, List

try:
    from domain.interactions.interaction_rules import (
        InteractionRules,
        InteractionImpactCalculator,
        InteractionTracker,
        Interaction,
        InteractionType,
        ValidationResult,
        Constraint,
        RelationChange,
        PowerChange,
        GlobalChange,
        ThirdPartyEffect,
        InteractionPattern,
        PredictedInteraction
    )
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not ENTITIES_AVAILABLE,
    reason="Entities module not available"
)


@pytest.mark.unit
class TestInteractionType:
    """Test InteractionType enum"""

    def test_interaction_types(self):
        """Test all interaction types have values"""
        interaction_types = [
            InteractionType.FORM_ALLIANCE,
            InteractionType.SIGN_TREATY,
            InteractionType.PROVIDE_AID,
            InteractionType.DIPLOMATIC_SUPPORT,
            InteractionType.DECLARE_WAR,
            InteractionType.IMPOSE_SANCTIONS,
            InteractionType.DIPLOMATIC_PROTEST,
            InteractionType.SEND_MESSAGE,
            InteractionType.HOLD_SUMMIT,
            InteractionType.PUBLIC_STATEMENT,
            InteractionType.ECONOMIC_PRESSURE,
            InteractionType.CULTURAL_INFLUENCE,
            InteractionType.MILITARY_POSTURE
        ]

        for interaction_type in interaction_types:
            assert isinstance(interaction_type.value, str)
            assert len(interaction_type.value) > 0

    def test_interaction_type_descriptions(self):
        """Test that interaction types have descriptions"""
        assert InteractionType.FORM_ALLIANCE.get_description()
        assert InteractionType.DECLARE_WAR.get_description()
        assert InteractionType.SEND_MESSAGE.get_description()


@pytest.mark.unit
class TestInteraction:
    """Test Interaction class"""

    @pytest.fixture
    def interaction(self):
        return Interaction(
            interaction_id="test_interaction",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={"message": "Hello"},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

    def test_interaction_creation(self, interaction):
        assert interaction.interaction_id == "test_interaction"
        assert interaction.interaction_type == InteractionType.SEND_MESSAGE
        assert interaction.source_agent == "agent_a"
        assert interaction.target_agent == "agent_b"

    def test_interaction_to_dict(self, interaction):
        result = interaction.to_dict()
        assert isinstance(result, dict)
        assert result["interaction_id"] == "test_interaction"
        assert result["interaction_type"] == "send_message"


@pytest.mark.unit
class TestInteractionRules:
    """Test InteractionRules class"""

    @pytest.fixture
    def rules(self):
        return InteractionRules(config={})

    @pytest.fixture
    def sample_context(self):
        return {
            "agents": [
                {"agent_id": "agent_a", "leader_type": "wangwangdao"},
                {"agent_id": "agent_b", "leader_type": "baquan"},
                {"agent_id": "agent_c", "leader_type": None}
            ],
            "relations": {
                "agent_a_agent_b": 0.5,
                "agent_a_agent_c": -0.3
            },
            "interaction_history": []
        }

    def test_rules_initialization(self, rules):
        assert rules.config == {}
        assert rules._interaction_counter == 0

    def test_validate_valid_interaction(self, rules, sample_context):
        interaction = Interaction(
            interaction_id="test",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

        result = rules.validate_interaction(interaction, sample_context)
        assert result.is_valid is True

    def test_validate_invalid_source_agent(self, rules, sample_context):
        interaction = Interaction(
            interaction_id="test",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="nonexistent",
            target_agent="agent_b",
            parameters={},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

        result = rules.validate_interaction(interaction, sample_context)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_same_source_and_target(self, rules, sample_context):
        interaction = Interaction(
            interaction_id="test",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_a",
            parameters={},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

        result = rules.validate_interaction(interaction, sample_context)
        assert result.is_valid is False

    def test_create_interaction(self, rules):
        interaction = rules.create_interaction(
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={},
            round=1
        )

        assert interaction.interaction_type == InteractionType.SEND_MESSAGE
        assert interaction.source_agent == "agent_a"
        assert interaction.target_agent == "agent_b"

    def test_get_allowed_interactions(self, rules, sample_context):
        agent = {"agent_id": "agent_a", "leader_type": "wangwangdao"}
        allowed = rules.get_allowed_interactions(agent, sample_context)
        assert isinstance(allowed, list)
        assert len(allowed) > 0

    def test_check_interaction_constraints(self, rules, sample_context):
        interaction = Interaction(
            interaction_id="test",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

        constraints = rules.check_interaction_constraints(interaction, sample_context)
        assert isinstance(constraints, list)


@pytest.mark.unit
class TestInteractionImpactCalculator:
    """Test InteractionImpactCalculator class"""

    @pytest.fixture
    def calculator(self):
        rules = InteractionRules(config={})
        return InteractionImpactCalculator(rules=rules)

    @pytest.fixture
    def sample_interaction(self):
        return Interaction(
            interaction_id="test",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={"message_type": "friendly"},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

    @pytest.fixture
    def sample_context(self):
        return {
            "agents": [
                {"agent_id": "agent_a", "power": 100},
                {"agent_id": "agent_b", "power": 90},
                {"agent_id": "agent_c", "power": 70}
            ],
            "relations": {}
        }

    def test_calculate_relation_impact(self, calculator, sample_interaction):
        result = calculator.calculate_relation_impact(sample_interaction)
        assert result.agent_pair == ("agent_a", "agent_b")
        assert isinstance(result.change_amount, float)

    def test_calculate_power_impact(self, calculator, sample_interaction):
        result = calculator.calculate_power_impact(sample_interaction)
        assert result.agent_id == "agent_a"
        assert isinstance(result.change_amount, float)

    def test_calculate_global_impact(self, calculator, sample_interaction):
        results = calculator.calculate_global_impact(sample_interaction)
        assert isinstance(results, list)

    def test_calculate_third_party_effects(self, calculator, sample_interaction, sample_context):
        effects = calculator.calculate_third_party_effects(sample_interaction, sample_context)
        assert isinstance(effects, list)

    def test_positive_relation_change(self, calculator):
        interaction = Interaction(
            interaction_id="test",
            interaction_type=InteractionType.FORM_ALLIANCE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={"intensity": 1.0},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

        result = calculator.calculate_relation_impact(interaction)
        assert result.change_amount > 0

    def test_negative_relation_change(self, calculator):
        interaction = Interaction(
            interaction_id="test",
            interaction_type=InteractionType.DECLARE_WAR,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

        result = calculator.calculate_relation_impact(interaction)
        assert result.change_amount < 0


@pytest.mark.unit
class TestInteractionTracker:
    """Test InteractionTracker class"""

    @pytest.fixture
    def tracker(self):
        return InteractionTracker()

    @pytest.fixture
    def sample_interaction(self):
        return Interaction(
            interaction_id="test",
            interaction_type=InteractionType.SEND_MESSAGE,
            source_agent="agent_a",
            target_agent="agent_b",
            parameters={},
            timestamp="2026-03-14T00:00:00Z",
            round=1
        )

    def test_tracker_initialization(self, tracker):
        assert isinstance(tracker._history, list)

    def test_record_interaction(self, tracker, sample_interaction):
        result = {"success": True}
        tracker.record_interaction(sample_interaction, result)
        assert len(tracker._history) == 1

    def test_get_interaction_history(self, tracker, sample_interaction):
        tracker.record_interaction(sample_interaction, {"success": True})

        history = tracker.get_interaction_history("agent_a")
        assert len(history) > 0

    def test_get_interaction_patterns(self, tracker, sample_interaction):
        # Record multiple interactions
        for i in range(10):
            tracker.record_interaction(sample_interaction, {"success": True})

        pattern = tracker.get_interaction_patterns("agent_a")
        assert pattern.agent_id == "agent_a"
        assert isinstance(pattern.action_tendencies, dict)

    def test_predict_future_interactions(self, tracker, sample_interaction):
        # Record interactions to build pattern
        for _ in range(10):
            tracker.record_interaction(sample_interaction, {"success": True})

        predictions = tracker.predict_future_interactions({"agent_id": "agent_a"})
        assert isinstance(predictions, list)

    def test_get_stats(self, tracker, sample_interaction):
        tracker.record_interaction(sample_interaction, {"success": True})

        stats = tracker.get_stats()
        assert stats["total_interactions"] == 1

    def test_clear(self, tracker, sample_interaction):
        tracker.record_interaction(sample_interaction, {"success": True})
        assert len(tracker._history) > 0

        tracker.clear()
        assert len(tracker._history) == 0


@pytest.mark.unit
class TestDataClasses:
    """Test dataclasses"""

    def test_validation_result(self):
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_validation_result_add_error(self):
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")
        assert result.is_valid is False
        assert len(result.errors) == 1

    def test_validation_result_to_dict(self):
        result = ValidationResult(
            is_valid=False,
            errors=["error1"],
            warnings=["warning1"]
        )

        data = result.to_dict()
        assert data["is_valid"] is False
        assert data["errors"] == ["error1"]
        assert data["warnings"] == ["warning1"]

    def test_constraint(self):
        constraint = Constraint(
            constraint_type="test_type",
            description="Test constraint",
            severity=0.8
        )

        assert constraint.constraint_type == "test_type"
        assert constraint.description == "Test constraint"
        assert constraint.severity == 0.8

    def test_relation_change(self):
        change = RelationChange(
            agent_pair=("agent_a", "agent_b"),
            change_amount=0.5,
            reason="Test reason"
        )

        assert change.agent_pair == ("agent_a", "agent_b")
        assert change.change_amount == 0.5

    def test_power_change(self):
        change = PowerChange(
            agent_id="agent_a",
            change_amount=10.0,
            reason="Test reason"
        )

        assert change.agent_id == "agent_a"
        assert change.change_amount == 10.0

    def test_global_change(self):
        change = GlobalChange(
            metric="global_stability",
            change_amount=-0.1,
            reason="Test reason"
        )

        assert change.metric == "global_stability"
        assert change.change_amount == -0.1

    def test_third_party_effect(self):
        effect = ThirdPartyEffect(
            agent_id="agent_c",
            effect_type="security_concern",
            impact=-0.1,
            reason="Test reason"
        )

        assert effect.agent_id == "agent_c"
        assert effect.effect_type == "security_concern"
