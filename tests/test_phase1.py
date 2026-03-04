"""
Phase 1 tests for the moral realism ABM system.

This module contains basic tests to verify the core components
implemented in Phase 1 of the project.
"""

import pytest
from src.models.leadership_type import (
    LeadershipType,
    LeadershipProfile,
    LEADERSHIP_PROFILES,
    get_leadership_profile,
    get_all_leadership_types,
    compare_moral_standards,
)
from src.models.capability import (
    CapabilityTier,
    HardPower,
    SoftPower,
    Capability,
    get_strategic_interests,
    compare_capability,
    is_power_transition_possible,
)
from src.models.agent import (
    AgentType,
    InteractionType,
    HistoryEntry,
    Agent,
    GreatPower,
    SmallState,
)


class TestLeadershipType:
    """Tests for leadership type models."""

    def test_all_leadership_types_defined(self) -> None:
        """Test that all four leadership types are defined."""
        expected_types = [
            LeadershipType.WANGDAO,
            LeadershipType.HEGEMON,
            LeadershipType.QIANGQUAN,
            LeadershipType.HUNYONG,
        ]
        actual_types = get_all_leadership_types()
        assert set(actual_types) == set(expected_types)

    def test_leadership_profiles_exist(self) -> None:
        """Test that profiles exist for all leadership types."""
        for leadership_type in get_all_leadership_types():
            profile = get_leadership_profile(leadership_type)
            assert isinstance(profile, LeadershipProfile)
            assert profile.leadership_type == leadership_type
            assert profile.validate()

    def test_wangdao_profile(self) -> None:
        """Test Wangdao leadership profile characteristics."""
        profile = get_leadership_profile(LeadershipType.WANGDAO)
        assert profile.moral_standard > 0.8
        assert profile.prefers_diplomatic_solution is True
        assert profile.uses_moral_persuasion is True
        assert profile.accepts_moral_constraints is True
        assert "military aggression" in profile.prohibited_actions

    def test_qhegemon_profile(self) -> None:
        """Test Hegemon leadership profile characteristics."""
        profile = get_leadership_profile(LeadershipType.HEGEMON)
        assert 0.3 < profile.moral_standard < 0.7
        assert profile.prefers_diplomatic_solution is False
        assert profile.core_interest_weight > 0.8

    def test_qiangquan_profile(self) -> None:
        """Test Qiangquan leadership profile characteristics."""
        profile = get_leadership_profile(LeadershipType.QIANGQUAN)
        assert profile.moral_standard < 0.4
        assert profile.uses_moral_persuasion is False
        assert profile.accepts_moral_constraints is False
        assert profile.core_interest_weight > 0.9

    def test_moral_standard_comparison(self) -> None:
        """Test moral standard comparison."""
        diff = compare_moral_standards(LeadershipType.WANGDAO, LeadershipType.QIANGQUAN)
        assert diff > 0  # Wangdao has higher moral standard than Qiangquan


class TestCapability:
    """Tests for capability and power models."""

    def test_capability_tiers_defined(self) -> None:
        """Test that all capability tiers are defined."""
        expected_tiers = [
            CapabilityTier.T0_SUPERPOWER,
            CapabilityTier.T1_GREAT_POWER,
            CapabilityTier.T2_REGIONAL,
            CapabilityTier.T3_MEDIUM,
            CapabilityTier.T4_SMALL,
        ]
        assert all(tier in CapabilityTier for tier in expected_tiers)

    def test_hard_power_validation(self) -> None:
        """Test hard power validation."""
        hard_power = HardPower(military_capability=80.0, gdp_share=20.0)
        assert hard_power.validate() is True

    def test_hard_power_invalid(self) -> None:
        """Test hard power validation with invalid values."""
        with pytest.raises(ValueError):
            HardPower(military_capability=150.0)  # Must be <= 100

    def test_hard_power_index(self) -> None:
        """Test hard power index calculation."""
        hard_power = HardPower(
            military_capability=90.0,
            nuclear_capability=80.0,
            conventional_forces=85.0,
            force_projection=80.0,
            gdp_share=25.0,
            economic_growth=5.0,
            trade_volume=80.0,
            financial_influence=85.0,
            technology_level=85.0,
            military_technology=85.0,
            innovation_capacity=80.0,
            energy_access=85.0,
            strategic_materials=80.0,
        )
        index = hard_power.get_hard_power_index()
        assert 0 <= index <= 100
        assert index > 50  # Should be relatively high power

    def test_soft_power_validation(self) -> None:
        """Test soft power validation."""
        soft_power = SoftPower(discourse_power=70.0, allies_count=10)
        assert soft_power.validate() is True

    def test_soft_power_index(self) -> None:
        """Test soft power index calculation."""
        soft_power = SoftPower(
            discourse_power=80.0,
            allies_count=15,
            moral_legitimacy=75.0,
        )
        index = soft_power.get_soft_power_index()
        assert 0 <= index <= 100

    def test_capability_tier_determination(self) -> None:
        """Test capability tier determination."""
        # Superpower - use values that produce combined index >= 80
        superpower_hard = HardPower(
            military_capability=95.0,
            nuclear_capability=90.0,
            conventional_forces=90.0,
            force_projection=95.0,
            gdp_share=25.0,
            economic_growth=4.0,
            trade_volume=90.0,
            financial_influence=95.0,
            technology_level=95.0,
            military_technology=95.0,
            innovation_capacity=90.0,
            energy_access=95.0,
            strategic_materials=90.0,
        )
        superpower_soft = SoftPower(
            discourse_power=95.0,
            narrative_control=90.0,
            media_influence=90.0,
            allies_count=30,
            ally_strength=90.0,
            network_position=85.0,
            diplomatic_support=90.0,
            moral_legitimacy=90.0,
            cultural_influence=90.0,
            un_influence=90.0,
            institutional_leadership=90.0,
        )
        superpower = Capability(
            agent_id="sp1",
            hard_power=superpower_hard,
            soft_power=superpower_soft,
        )
        assert superpower.get_tier() == CapabilityTier.T0_SUPERPOWER

        # Small state - use values that produce combined index < 25
        small_hard = HardPower(
            military_capability=10.0,
            nuclear_capability=0.0,
            conventional_forces=10.0,
            force_projection=5.0,
            gdp_share=0.5,
            economic_growth=1.0,
            trade_volume=10.0,
            financial_influence=10.0,
            technology_level=15.0,
            military_technology=10.0,
            innovation_capacity=10.0,
            energy_access=15.0,
            strategic_materials=15.0,
        )
        small_soft = SoftPower(
            discourse_power=10.0,
            narrative_control=10.0,
            media_influence=10.0,
            allies_count=2,
            ally_strength=10.0,
            network_position=10.0,
            diplomatic_support=10.0,
            moral_legitimacy=10.0,
            cultural_influence=10.0,
            un_influence=10.0,
            institutional_leadership=10.0,
        )
        small = Capability(agent_id="ss1", hard_power=small_hard, soft_power=small_soft)
        assert small.get_tier() == CapabilityTier.T4_SMALL

    def test_capability_index(self) -> None:
        """Test combined capability index calculation."""
        capability = Capability(agent_id="agent1")
        index = capability.get_capability_index()
        assert 0 <= index <= 100

    def test_capability_history(self) -> None:
        """Test capability state history tracking."""
        capability = Capability(agent_id="agent1")
        capability.record_state(step=0, context={"event": "initial"})

        history = capability.get_history()
        assert len(history) == 1
        assert history[0]["step"] == 0

    def test_strategic_interests(self) -> None:
        """Test strategic interests by capability tier."""
        superpower_interests = get_strategic_interests(CapabilityTier.T0_SUPERPOWER)
        assert "global hegemony maintenance" in superpower_interests

        small_interests = get_strategic_interests(CapabilityTier.T4_SMALL)
        assert "survival" in small_interests

    def test_capability_comparison(self) -> None:
        """Test capability comparison."""
        cap1 = Capability(agent_id="agent1")
        cap1.hard_power.military_capability = 80.0

        cap2 = Capability(agent_id="agent2")
        cap2.hard_power.military_capability = 40.0

        diff = compare_capability(cap1, cap2)
        assert diff > 0

    def test_power_transition_feasibility(self) -> None:
        """Test power transition feasibility checks."""
        low_power = Capability(agent_id="low")
        low_power.hard_power.military_capability = 20.0

        # Transition to nearby tier should be possible
        assert is_power_transition_possible(low_power, CapabilityTier.T2_REGIONAL) is True

        # Transition from small to superpower directly should not be plausible
        assert is_power_transition_possible(low_power, CapabilityTier.T0_SUPERPOWER) is False


class TestAgentBase:
    """Tests for agent base classes."""

    def test_agent_type_enum(self) -> None:
        """Test agent type enum."""
        expected_types = [
            AgentType.GREAT_POWER,
            AgentType.SMALL_STATE,
            AgentType.ORGANIZATION,
            AgentType.CONTROLLER,
        ]
        for agent_type in expected_types:
            assert agent_type in AgentType

    def test_interaction_type_enum(self) -> None:
        """Test interaction type enum."""
        expected_types = [
            InteractionType.DIPLOMATIC,
            InteractionType.ECONOMIC,
            InteractionType.MILITARY,
            InteractionType.COERCIVE,
            InteractionType.COOPERATIVE,
        ]
        for interaction_type in expected_types:
            assert interaction_type in InteractionType

    def test_history_entry(self) -> None:
        """Test history entry creation and serialization."""
        entry = HistoryEntry(
            timestamp="2024-01-01",  # Will be converted to datetime
            event_type="decision",
            content="Agent decided to cooperate",
            metadata={"action": "cooperate"},
        )
        entry_dict = entry.to_dict()
        assert entry_dict["event_type"] == "decision"
        assert entry_dict["content"] == "Agent decided to cooperate"
        assert "timestamp" in entry_dict

    def test_great_power_creation(self) -> None:
        """Test great power agent creation."""
        agent = GreatPower(
            agent_id="gp1",
            name="GreatPower1",
            name_zh="大国1",
            leadership_type=LeadershipType.WANGDAO,
        )
        assert agent.agent_id == "gp1"
        assert agent.agent_type == AgentType.GREAT_POWER
        assert agent.leadership_type == LeadershipType.WANGDAO
        assert agent.is_active is True

    def test_great_power_decision(self) -> None:
        """Test great power decision making."""
        agent = GreatPower(
            agent_id="gp1",
            name="GreatPower1",
            name_zh="大国1",
            leadership_type=LeadershipType.WANGDAO,
        )
        situation = {"crisis": "economic"}
        available_actions = [{"id": "cooperate", "description": "Cooperate"}]

        decision = agent.decide(situation, available_actions)
        assert "action" in decision
        assert "rationale" in decision
        assert decision["leadership_influence"] == "wangdao"

    def test_great_power_response(self) -> None:
        """Test great power response generation."""
        agent = GreatPower(
            agent_id="gp1",
            name="GreatPower1",
            name_zh="大国1",
            leadership_type=LeadershipType.WANGDAO,
        )
        message = {"content": "Let's cooperate on this issue"}
        response = agent.respond(sender_id="other", message=message)
        assert response["sender_id"] == "gp1"
        assert response["receiver_id"] == "other"

    def test_small_state_creation(self) -> None:
        """Test small state agent creation."""
        agent = SmallState(
            agent_id="ss1",
            name="SmallState1",
            name_zh="小国1",
            leadership_type=LeadershipType.HUNYONG,
        )
        assert agent.agent_id == "ss1"
        assert agent.agent_type == AgentType.SMALL_STATE
        assert agent.leadership_type == LeadershipType.HUNYONG

    def test_agent_relationships(self) -> None:
        """Test agent relationship management."""
        agent = GreatPower( # Create a simple agent-like object
            agent_id="agent1",
            name="Agent1",
            name_zh="智能体1",
            leadership_type=LeadershipType.WANGDAO,
        )

        # Set relationships
        agent.set_relationship("agent2", 0.8)
        agent.set_relationship("agent3", -0.5)

        assert agent.get_relationship("agent2") == 0.8
        assert agent.get_relationship("agent3") == -0.5
        assert agent.is_friendly_with("agent2") is True
        assert agent.is_hostile_toward("agent3") is True
        assert agent.is_friendly_with("agent3") is False

    def test_agent_history_tracking(self) -> None:
        """Test agent history tracking."""
        agent = GreatPower(
            agent_id="agent1",
            name="Agent1",
            name_zh="智能体1",
            leadership_type=LeadershipType.WANGDAO,
        )

        agent.add_history("test_event", "Test message")
        assert len(agent.get_history()) == 1

        agent.add_history("test_event", "Another message")
        assert len(agent.get_history()) == 2

        # Filter by event type
        agent.add_history("other_event", "Other message")
        test_events = agent.get_history(event_type="test_event")
        assert len(test_events) == 2

    def test_agent_summary(self) -> None:
        """Test agent summary generation."""
        agent = GreatPower(
            agent_id="agent1",
            name="Agent1",
            name_zh="智能体1",
            leadership_type=LeadershipType.WANGDAO,
        )

        summary = agent.get_summary()
        assert summary["agent_id"] == "agent1"
        assert summary["name"] == "Agent1"
        assert summary["agent_type"] == "great_power"
        assert summary["leadership_type"] == "wangdao"


def test_module_imports():
    """Test that all core modules can be imported."""
    # Leadership type
    from src.models.leadership_type import LeadershipType, LEADERSHIP_PROFILES

    # Capability
    from src.models.capability import Capability

    # Agent
    from src.models.agent import GreatPower, SmallState

    # LLM Engine
    from src.core.llm_engine import LLMEngine, LLMConfig

    assert True  # All imports successful
