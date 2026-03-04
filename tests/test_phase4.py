"""Phase 4 tests for moral realism ABM system.

This module contains tests to verify interaction components
implemented in Phase 4 of project.
"""

import pytest

from src.models.agent import AgentType
from src.models.leadership_type import LeadershipType
from src.agents.great_power_agent import GreatPowerAgent
from src.agents.small_state_agent import SmallStateAgent

from src.interaction import (
    InteractionManager,
    InteractionResult,
    InteractionStep,
    BehaviorSelector,
    Behavior,
    BehaviorConstraint,
    ValidationResult,
    ResponseGenerator,
    ResponseType,
    ResponseTemplate,
    MessageType,
    InteractionRules,
    InteractionConstraint,
    InteractionCategory,
    MoralImpact,
)


@pytest.fixture
def agents():
    """Create test agents for testing."""
    return [
        GreatPowerAgent(
            agent_id="gp1",
            name="Great Power 1",
            name_zh="大国1",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.WANGDAO,
        ),
        GreatPowerAgent(
            agent_id="gp2",
            name="Great Power 2",
            name_zh="大国2",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.HEGEMON,
        ),
        SmallStateAgent(
            agent_id="ss1",
            name="Small State 1",
            name_zh="小国1",
            agent_type=AgentType.SMALL_STATE,
            leadership_type=LeadershipType.HUNYONG,
        ),
    ]


class TestInteractionManager:
    """Tests for interaction manager functionality."""

    def test_initialization(self) -> None:
        """Test interaction manager initialization."""
        manager = InteractionManager(max_history_length=100)

        assert len(manager._agents) == 0
        assert len(manager._interaction_history) == 0
        assert manager._current_round == 0

    def test_register_agent(self, agents) -> None:
        """Test agent registration."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        assert len(manager._agents) == len(agents)

    def test_unregister_agent(self, agents) -> None:
        """Test agent unregistration."""
        manager = InteractionManager()

        agent = agents[0]
        manager.register_agent(agent)

        assert manager.get_agent(agent.agent_id) is not None
        assert len(manager._agents) == 1

        unregistered = manager.unregister_agent(agent.agent_id)
        assert unregistered is True
        assert manager.get_agent(agent.agent_id) is None
        assert len(manager._agents) == 0

    def test_get_agent_by_type(self, agents) -> None:
        """Test getting agents by type."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        great_powers = manager.get_agents_by_type(AgentType.GREAT_POWER)
        assert len(great_powers) == 2

        small_states = manager.get_agents_by_type(AgentType.SMALL_STATE)
        assert len(small_states) == 1

    def test_interaction_result_creation(self) -> None:
        """Test interaction result creation."""
        result = InteractionResult(
            interaction_id="test_1",
            from_agent_id="agent1",
            to_agent_id="agent2",
            interaction_type="test",
            action={"type": "test_action"},
        )

        assert result.interaction_id == "test_1"
        assert result.from_agent_id == "agent1"
        assert result.to_agent_id == "agent2"
        assert result.interaction_type == "test"
        assert result.success is True

        result_dict = result.to_dict()
        assert "interaction_id" in result_dict

    def test_interaction_step_creation(self) -> None:
        """Test interaction step creation."""
        step = InteractionStep(
            step_id="step_1",
            round=0,
            decisions=[{"type": "test"}],
        )

        assert step.step_id == "step_1"
        assert step.round == 0
        assert len(step.decisions) == 1

        step_dict = step.to_dict()
        assert "step_id" in step_dict

    def test_execute_interactions_no_action(self, agents) -> None:
        """Test executing interactions with no_action."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agent.agent_id,
                "action_type": "no_action",
            }
            for agent in agents
        ]

        results = manager.execute_interactions(decisions)

        # no_action should result in no interactions
        assert len(results) == 0

    def test_get_interaction_history(self, agents) -> None:
        """Test getting interaction history."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agents[0].agent_id,
                "action_type": "test",
                "target_agent_id": agents[1].agent_id,
            }
        ]

        manager.execute_interactions(decisions)

        history = manager.get_interaction_history()
        assert isinstance(history, list)
        assert len(history) > 0

        agent_history = manager.get_interaction_history(agent_id=agents[0].agent_id)
        assert len(agent_history) > 0

    def test_get_step_interaction_history(self, agents) -> None:
        """Test getting step interaction history."""
        from src.interaction.interaction_manager import InteractionStep

        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agent.agent_id,
                "action_type": "test",
                "target_agent_id": agents[1].agent_id,
            }
            for agent in agents
        ]

        step1 = InteractionStep(
            step_id="step1",
            round=0,
            decisions=decisions,
        )
        manager._step_history.append(step1)

        step2 = InteractionStep(
            step_id="step2",
            round=1,
            decisions=decisions,
        )
        manager._step_history.append(step2)

        history = manager.get_step_history()
        assert len(history) >= 2

        with_limit = manager.get_step_history(limit=1)
        assert len(with_limit) == 1

    def test_get_interaction_summary(self, agents) -> None:
        """Test getting interaction summary."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agent.agent_id,
                "action_type": "test",
            }
            for agent in agents
        ]

        manager.execute_interactions(decisions)

        summary = manager.get_interaction_summary()
        assert "total_interactions" in summary
        assert "current_round" in summary
        assert "registered_agents" in summary
        assert summary["registered_agents"] == len(agents)

    def test_get_agent_interactions(self, agents) -> None:
        """Test getting interactions for a specific agent."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agent.agent_id,
                "action_type": "test",
                "target_agent_id": agents[1].agent_id,
            }
            for agent in agents
        ]

        manager.execute_interactions(decisions)

        agent_stats = manager.get_agent_interactions(agents[0].agent_id)
        assert "agent_id" in agent_stats
        assert "total_interactions" in agent_stats

    def test_reset_round(self, agents) -> None:
        """Test resetting round counter."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agent.agent_id,
                "action_type": "test",
            }
            for agent in agents
        ]

        manager.execute_interactions(decisions)
        assert manager._current_round == 1

        manager.reset_round()
        assert manager._current_round == 0

    def test_clear_history(self, agents) -> None:
        """Test clearing history."""
        manager = InteractionManager()

        for agent in agents:
            manager.register_agent(agent)

        decisions = [
            {
                "agent_id": agent.agent_id,
                "action_type": "test",
            }
            for agent in agents
        ]

        manager.execute_interactions(decisions)
        assert len(manager._interaction_history) > 0

        manager.clear_history()
        assert len(manager._interaction_history) == 0
        assert len(manager._step_history) == 0


class TestBehaviorSelector:
    """Tests for behavior selector functionality."""

    def test_initialization(self) -> None:
        """Test behavior selector initialization."""
        selector = BehaviorSelector(enable_moral_validation=True)

        assert selector._enable_moral is True
        assert len(selector._base_behaviors) > 0

    def test_get_available_behaviors(self, agents) -> None:
        """Test getting available behaviors."""
        selector = BehaviorSelector()

        for agent in agents:
            behaviors = selector.get_available_behaviors(agent)

            assert isinstance(behaviors, list)
            assert len(behaviors) > 0

            for behavior in behaviors:
                assert "action_type" in behavior
                assert "description" in behavior
                assert "constraints" in behavior

    def test_validate_behavior(self, agents) -> None:
        """Test behavior validation."""
        selector = BehaviorSelector()

        # Test valid behavior
        for agent in agents:
            result = selector.validate_behavior(
                agent,
                "diplomatic_visit",
            )

            assert isinstance(result, ValidationResult)
            assert "is_valid" in result.to_dict()

    def test_validate_prohibited_behavior(self, agents) -> None:
        """Test validation of prohibited behaviors."""
        selector = BehaviorSelector()

        wangdao_agent = [
            agent for agent in agents
            if agent.leadership_type == LeadershipType.WANGDAO
        ][0]

        result = selector.validate_behavior(
            wangdao_agent,
            "security_military",
        )

        assert result.is_valid is False
        assert len(result.constraints_violated) > 0

    def test_get_prioritized_behaviors(self, agents) -> None:
        """Test getting prioritized behaviors."""
        selector = BehaviorSelector()

        for agent in agents:
            behaviors = selector.get_available_behaviors(agent)
            prioritized = selector.get_prioritized_behaviors(agent, behaviors)

            assert isinstance(prioritized, list)
            assert len(prioritized) == len(behaviors)

    def test_filter_by_constraints(self, agents) -> None:
        """Test filtering behaviors by constraints."""
        selector = BehaviorSelector()

        for agent in agents:
            behaviors = selector.get_available_behaviors(agent)

            filtered = selector.filter_by_constraints(
                agent,
                behaviors,
                {"max_resource_cost": 60},
            )

            assert isinstance(filtered, list)
            assert len(filtered) <= len(behaviors)

    def test_get_behavior_recommendations(self, agents) -> None:
        """Test getting behavior recommendations."""
        selector = BehaviorSelector()

        for agent in agents:
            recommendations = selector.get_behavior_recommendations(agent)

            assert "agent_id" in recommendations
            assert "recommendations" in recommendations
            assert "rationale" in recommendations
            assert "total_available" in recommendations


class TestResponseGenerator:
    """Tests for response generator functionality."""

    def test_initialization(self) -> None:
        """Test response generator initialization."""
        generator = ResponseGenerator(use_llm=False)

        assert generator._use_llm is False
        assert len(generator._templates) > 0

    def test_message_type_enum(self) -> None:
        """Test message type enum values."""
        message_types = [
            MessageType.COOPERATION,
            MessageType.ALLIANCE,
            MessageType.TRADE,
            MessageType.THREAT,
            MessageType.SANCTION,
            MessageType.AID,
            MessageType.NORM_PROPOSAL,
            MessageType.CONFLICT_MEDIATION,
            MessageType.INFO_REQUEST,
            MessageType.INFO_SHARING,
            MessageType.ACKNOWLEDGMENT,
            MessageType.DECLINE,
            MessageType.ACCEPT,
            MessageType.NEGOTIATE,
        ]

        for message_type in message_types:
            assert message_type in MessageType

    def test_response_type_enum(self) -> None:
        """Test response type enum values."""
        response_types = [
            ResponseType.SUPPORT,
            ResponseType.CONSIDER,
            ResponseType.DECLINE,
            ResponseType.REJECT,
            ResponseType.COUNTER,
            ResponseType.CONCERN,
            ResponseType.CONDEMN,
            ResponseType.ACKNOWLEDGE,
            ResponseType.NEUTRAL,
        ]

        for response_type in response_types:
            assert response_type in ResponseType

    def test_response_template_creation(self) -> None:
        """Test response template creation."""
        template = ResponseTemplate(
            response_type=ResponseType.SUPPORT,
            template="Test template from {sender}.",
        )

        assert template.response_type == ResponseType.SUPPORT
        assert template.template == "Test template from {sender}."

    def test_get_response_template(self, agents) -> None:
        """Test getting response templates."""
        generator = ResponseGenerator()

        templates = generator.get_response_template()

        assert isinstance(templates, list)
        assert len(templates) > 0

        for template in templates:
            assert "response_type" in template
            assert "template" in template
            assert "leadership_type" in template

    def test_get_fallback_response(self, agents) -> None:
        """Test getting fallback response."""
        generator = ResponseGenerator()

        for agent in agents:
            sender = {"agent_id": "test", "name": "Test Sender"}
            message = {"type": "unknown"}

            response = generator.get_fallback_response(agent, sender, message)

            assert "sender_id" in response
            assert "receiver_id" in response
            assert "content" in response
            assert "fallback" in response
            assert response["fallback"] is True


class TestInteractionRules:
    """Tests for interaction rules functionality."""

    def test_initialization(self) -> None:
        """Test interaction rules initialization."""
        rules = InteractionRules()

        assert len(rules._constraints) > 0
        assert "security_military" in rules._ACTION_MORAL_IMPACTS

    def test_validate_interaction(self, agents) -> None:
        """Test interaction validation."""
        rules = InteractionRules()

        from_agent = agents[0]
        to_agent = agents[1]
        action = {"action_type": "diplomatic_visit"}

        is_valid, reason, violations = rules.validate_interaction(
            from_agent, to_agent, action
        )

        assert isinstance(is_valid, bool)
        assert isinstance(reason, str)
        assert isinstance(violations, list)

    def test_validate_self_interaction(self, agents) -> None:
        """Test validation of self-interaction (should fail)."""
        rules = InteractionRules()

        agent = agents[0]
        action = {"action_type": "test"}

        is_valid, reason, violations = rules.validate_interaction(
            agent, agent, action
        )

        assert is_valid is False
        assert "self_interaction" in violations

    def test_calculate_interaction_morality(self, agents) -> None:
        """Test calculating interaction morality."""
        rules = InteractionRules()

        # Military action should have negative moral impact
        military_action = {"action_type": "security_military"}
        military_morality = rules.calculate_interaction_morality(
            military_action,
            agents[0].leadership_profile,
        )

        assert military_morality.score < 0
        assert "military" in military_morality.justification.lower()

        # Aid action should have positive moral impact
        aid_action = {"action_type": "economic_aid"}
        aid_morality = rules.calculate_interaction_morality(
            aid_action,
            agents[0].leadership_profile,
        )

        assert aid_morality.score > 0
        assert "aid" in aid_morality.justification.lower()

    def test_get_allowed_interactions(self, agents) -> None:
        """Test getting allowed interactions by agent type."""
        rules = InteractionRules()

        great_power_actions = rules.get_allowed_interactions(AgentType.GREAT_POWER)
        assert "security_military" in great_power_actions

        small_state_actions = rules.get_allowed_interactions(AgentType.SMALL_STATE)
        assert "security_military" not in small_state_actions

        org_actions = rules.get_allowed_interactions(AgentType.ORGANIZATION)
        assert "security_military" not in org_actions
        assert "security_alliance" not in org_actions

    def test_check_capability_constraints(self, agents) -> None:
        """Test checking capability constraints."""
        rules = InteractionRules()

        from_agent = agents[0]
        to_agent = agents[1]
        action = {"action_type": "diplomatic_visit"}

        is_allowed, reason = rules.check_capability_constraints(
            from_agent, to_agent, action
        )

        assert isinstance(is_allowed, bool)
        assert isinstance(reason, str)

    def test_get_interaction_category(self) -> None:
        """Test getting interaction category."""
        rules = InteractionRules()

        # Cooperative actions
        trade_category = rules.get_interaction_category("economic_trade")
        assert trade_category == InteractionCategory.COOPERATIVE

        aid_category = rules.get_interaction_category("economic_aid")
        assert aid_category == InteractionCategory.COOPERATIVE

        # Coercive actions
        military_category = rules.get_interaction_category("security_military")
        assert military_category == InteractionCategory.COERCIVE

        sanction_category = rules.get_interaction_category("economic_sanction")
        assert sanction_category == InteractionCategory.COERCIVE

    def test_moral_impact_creation(self) -> None:
        """Test moral impact creation."""
        impact = MoralImpact(
            score=50.0,
            dimensions={"test_dim": 10.0},
            justification="Test impact on test dimension",
        )

        assert impact.score == 50.0
        assert impact.dimensions["test_dim"] == 10.0
        assert impact.justification == "Test impact on test dimension"

        impact_dict = impact.to_dict()
        assert "score" in impact_dict
        assert "dimensions" in impact_dict
        assert "justification" in impact_dict

    def test_get_rule_summary(self) -> None:
        """Test getting rule summary."""
        rules = InteractionRules()

        summary = rules.get_rule_summary()
        assert "constraint_count" in summary
        assert "action_types" in summary

    def test_add_custom_constraint(self) -> None:
        """Test adding custom constraint."""
        rules = InteractionRules()

        initial_count = rules.get_rule_summary()["constraint_count"]

        custom_constraint = InteractionConstraint(
            name="test_custom",
            description="Test custom constraint",
            requires_capability_above=80.0,
        )

        rules.add_custom_constraint("test_action", custom_constraint)

        new_count = rules.get_rule_summary()["constraint_count"]
        assert new_count > initial_count


class TestIntegration:
    """Integration tests for complete interaction flow."""

    def test_full_setup_agents(self, agents) -> None:
        """Test full agent setup."""
        assert len(agents) == 3
        assert all(agent.capability for agent in agents)

    def test_interaction_flow(self, agents) -> None:
        """Test complete interaction flow."""
        manager = InteractionManager()
        selector = BehaviorSelector()
        rules = InteractionRules()
        generator = ResponseGenerator()

        # Register all agents
        for agent in agents:
            manager.register_agent(agent)

        # Get available behaviors for each agent
        for agent in agents:
            behaviors = selector.get_available_behaviors(agent)
            assert len(behaviors) > 0

            # Validate a behavior
            for agent in agents:
                if behaviors:
                    validation = selector.validate_behavior(
                        agent,
                        behaviors[0]["action_type"],
                    )
                    assert isinstance(validation, ValidationResult)

        # Test interaction validation
        from_agent = agents[0]
        to_agent = agents[1]
        action = {"action_type": "diplomatic_visit"}

        is_valid, reason, violations = rules.validate_interaction(
            from_agent,
            to_agent,
            action,
        )
        assert isinstance(is_valid, bool)

        # Test moral impact calculation
        moral_impact = rules.calculate_interaction_morality(
            action,
            from_agent.leadership_profile,
        )
        assert -100.0 <= moral_impact.score <= 100.0

        # Test response generation
        sender_info = {
            "agent_id": to_agent.agent_id,
            "name": to_agent.name,
            "agent_type": to_agent.agent_type.value,
            "leadership_type": to_agent.leadership_type.value,
        }
        message = {
            "type": "cooperation",
            "content": "Test message",
        }

        response = generator.generate_response(
            from_agent,
            sender_info,
            message,
        )

        assert "sender_id" in response
        assert "content" in response


def test_module_imports():
    """Test that all interaction modules can be imported."""
    from src.interaction import (
        InteractionManager,
        BehaviorSelector,
        ResponseGenerator,
        InteractionRules,
        InteractionResult,
        InteractionStep,
        Behavior,
        BehaviorConstraint,
        ValidationResult,
        ResponseType,
        ResponseTemplate,
        MessageType,
        InteractionConstraint,
        InteractionCategory,
        MoralImpact,
    )

    assert True  # All imports successful
