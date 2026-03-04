"""
Tests for Phase 8: Prompt Engineering Implementation.

Tests for:
- BasePromptBuilder class and utilities
- BehaviorPromptBuilder class and functions
- ResponsePromptBuilder class and functions
- GreatPowerPromptBuilder additional coverage
- Prompt template validation
- Context integration
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType, get_leadership_profile
from src.models.capability import Capability
from src.prompts.base_prompt import (
    BasePromptBuilder,
    PromptContext,
    PromptSection,
    PromptBuilderRegistry,
    create_default_context,
    format_prompt_section,
    validate_template_variables,
)
from src.prompts.behavior_prompts import (
    BehaviorPromptBuilder,
    BehaviorCategory,
    BEHAVIOR_DESCRIPTIONS,
    get_behavior_category_for_action,
)
from src.prompts.response_prompts import (
    ResponsePromptBuilder,
    MessageType,
    ResponseTone,
    MESSAGE_DESCRIPTIONS,
    get_message_description,
    get_response_tone_description,
)
from src.prompts.leadership_prompts import (
    GreatPowerPromptBuilder,
    ActionType,
    ACTION_DESCRIPTIONS,
)


class TestPromptContext:
    """Tests for PromptContext dataclass."""

    def test_default_initialization(self) -> None:
        """Test default initialization of PromptContext."""
        context = PromptContext()

        assert context.s.situation == ""
        assert context.situation_details == {}
        assert context.agent_info == {}
        assert context.available_actions == []
        assert context.other_agents == []
        assert context.recent_events == []
        assert context.relationships == {}
        assert context.custom == {}

    def test_initialization_with_values(self) -> None:
        """Test initialization with values."""
        context = PromptContext(
            s="Test situation",
            agent_info={"name": "Test Agent"},
        )

        assert context.situation == "Test situation"
        assert context.agent_info == {"name": "Test Agent"}

    def test_get_method(self) -> None:
        """Test get method for context access."""
        context = PromptContext(
            s="Test situation",
            agent_info={"name": "Test Agent", "id": "test_agent"},
            custom={"extra": "value"},
        )

        # Test getting from different sources
        assert context.get("s") == "Test situation"
        assert context.get("name") == "Test Agent"
        assert context.get("id") == "test_agent"
        assert context.get("extra") == "value"
        assert context.get("nonexistent") is None

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        context = PromptContext(
            s="Test",
            agent_info={"key": "value"},
        )

        result_dict = context.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["s"] == "Test"
        assert result_dict["agent_info"] == {"key": "value"}


class TestPromptSection:
    """Tests for PromptSection enum."""

    def test_enum_values(self) -> None:
        """Test that enum values are defined."""
        assert PromptSection.SYSTEM_INSTRUCTION.value == "system_instruction"
        assert PromptSection.AGENT_IDENTITY.value == "agent_identity"
        assert PromptSection.LEADERSHIP_PROFILE.value == "leadership_profile"
        assert PromptSection.CAPABILITIES.value == "capabilities"
        assert PromptSection.CONTEXT.value == "context"
        assert PromptSection.CONSTRAINTS.value == "constraints"
        assert PromptSection.TASK.value == "task"
        assert PromptSection.EXAMPLES.value == "examples"
        assert PromptSection.OUTPUT_FORMAT.value == "output_format"


class TestBasePromptBuilderUtils:
    """Tests for BasePromptBuilder utility methods."""

    def test_format_agent_identity(self) -> None:
        """Test agent identity formatting."""
        # Create a mock agent
        agent = Mock(spec=Agent)
        agent.name = "Test State"
        agent.name_zh = "Test Country"
        agent.agent_id = "test_agent"
        agent.agent_type = AgentType.GREAT_POWER
        agent.leadership_type = LeadershipType.WANGDAO

        # Mock leadership profile
        profile = get_leadership_profile(LeadershipType.WANGDAO)
        agent.leadership_profile = profile

        builder = BasePromptBuilder()
        result = builder._format_agent_identity(agent)

        assert "Test State" in result
        assert "GREAT_POWER" in result
        assert "WANGDAO" in result

    def test_format_capabilities(self) -> None:
        """Test capability formatting."""
        agent = Mock(spec=Agent)
        agent.capability = Capability(agent_id="test_agent")

        builder = BasePromptBuilder()
        result = builder._format_capabilities(agent)

        assert "Hard Power Index" in result
        assert "Soft Power Index" in result
        assert "Overall Capability" in result

    def test_describe_relationship(self) -> None:
        """Test relationship description."""
        builder = BasePromptBuilder()

        assert builder._describe_relationship(0.8) == "Very Friendly"
        assert builder._describe_relationship(0.5) == "Friendly"
        assert builder._describe_relationship(0.1) == "Neutral"
        assert builder._describe_relationship(-0.5) == "Hostile"
        assert builder._describe_relationship(-0.8) == "Very Hostile"

    def test_validate_prompt(self) -> None:
        """Test prompt validation."""
        builder = BasePromptBuilder()

        # Valid prompt
        assert builder.validate_prompt("This is a valid prompt with sufficient content.")

        # Invalid prompts
        assert builder.validate_prompt("") is False
        assert builder.validate_prompt("   ") is False

    def test_get_prompt_length(self) -> None:
        """Test prompt length estimation."""
        builder = BasePromptBuilder()

        prompt = "This is a test prompt."
        length = builder.get_prompt_length(prompt)

        # Approximate: length should be around character count / 4
        assert length > 0
        assert length < len(prompt)


class TestPromptBuilderRegistry:
    """Tests for PromptBuilderRegistry."""

    def setup_method(self) -> None:
        """Set up test by clearing registry."""
        PromptBuilderRegistry.clear()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        PromptBuilderRegistry.clear()

    def test_register_and_get(self) -> None:
        """Test registering and retrieving builders."""
        mock_builder = Mock(spec=BasePromptBuilder)
        PromptBuilderRegistry.register("test_builder", mock_builder)

        retrieved = PromptBuilderRegistry.get("test_builder")

        assert retrieved is mock_builder

    def test_get_nonexistent(self) -> None:
        """Test getting non-existent builder."""
        result = PromptBuilderRegistry.get("nonexistent")

        assert result is None

    def test_list_builders(self) -> None:
        """TestList listing registered builders."""
        mock_builder1 = Mock(spec=BasePromptBuilder)
        mock_builder2 = Mock(spec=BasePromptBuilder)

        PromptBuilderRegistry.register("builder1", mock_builder1)
        PromptBuilderRegistry.register("builder2", mock_builder2)

        builder_list = PromptBuilderRegistry.list_builders()

        assert "builder1" in builder_list
        assert "builder2" in builder_list

    def test_clear(self) -> None:
        """Test clearing registry."""
        mock_builder = Mock(spec=BasePromptBuilder)
        PromptBuilderRegistry.register("test_builder", mock_builder)

        PromptBuilderRegistry.clear()

        assert PromptBuilderRegistry.get("test_builder") is None
        assert len(PromptBuilderRegistry.list_builders()) == 0


class TestUtilityFunctions:
    """Tests for prompt utility functions."""

    def test_create_default_context(self) -> None:
        """Test default context creation."""
        context = create_default_context("Test situation")

        assert context.s == "Test situation"
        assert isinstance(context.available_actions, list)

    def test_create_default_context_with_actions(self) -> None:
        """Test default context with actions."""
        actions = [{"id": "action1"}, {"id": "action2"}]
        context = create_default_context("Test", actions)

        assert context.available_actions == actions

    def test_format_prompt_section(self) -> None:
        """Test prompt section formatting."""
        result = format_prompt_section("Title", "Content", level=2)

        assert "## Title" in result
        assert "Content" in result

    def test_format_prompt_section_empty_content(self) -> None:
        """Test prompt section with empty content."""
        result = format_prompt_section("Title", "")

        assert result == ""

    def test_validate_template_variables(self) -> None:
        """Test template variable validation."""
        template = "Hello {name}, your situation is {situation}."

        variables = {
            "name": "Agent",
            "situation": "Good",
        }

        missing = validate_template_variables(template, variables)

        assert len(missing) == 0

    def test_validate_template_variables_missing(self) -> None:
        """Test template variable validation with missing variables."""
        template = "Hello {name}, your {role} is {status}."

        variables = {
            "name": "Agent",
        }

        missing = validate_template_variables(template, variables)

        assert "role" in missing
        assert "status" in missing


class TestBehaviorCategory:
    """Tests for BehaviorCategory enum."""

    def test_enum_values(self) -> None:
        """Test that behavior category enum values are defined."""
        assert BehaviorCategory.DIPLOMATIC_ENGAGEMENT.value == "diplomatic_engagement"
        assert BehaviorCategory.COOPERATIVE_ACTION.value == "cooperative_action"
        assert BehaviorCategory.MUTUAL_BENEFIT.value == "mutual_benefit"
        assert BehaviorCategory.MILITARY_ACTION.value == "military_action"
        assert BehaviorCategory.ECONOMIC_PRESSURE.value == "economic_pressure"
        assert BehaviorCategory.SANCTION_APPLICATION.value == "sanction_application"
        assert BehaviorCategory.NORM_PROPOSAL.value == "norm_proposal"
        assert BehaviorCategory.NORM_ENFORCEMENT.value == "norm_enforcement"
        assert BehaviorCategory.MORAL_PERSUASION.value == "moral_persuasion"
        assert BehaviorCategory.OBSERVATION.value == "observation"
        assert BehaviorCategory.DELAYED_RESPONSE.value == "delayed_response"
        assert BehaviorCategory.INACTION.value == "inaction"

    def test_descriptions(self) -> None:
        """Test that behavior category descriptions are defined."""
        assert len(BEHAVIOR_DESCRIPTIONS) > 0

        for category, description in BEHAVIOR_DESCRIPTIONS.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestBehaviorPromptBuilder:
    """Tests for BehaviorPromptBuilder class."""

    def setup_method(self) -> None:
        """Set up test with builder."""
        self.builder = BehaviorPromptBuilder()

    def test_initialization(self) -> None:
        """Test BehaviorPromptBuilder initialization."""
        builder = BehaviorPromptBuilder()

        assert isinstance(builder, BasePromptBuilder)

    def test_build_system_prompt(self) -> None:
        """Test building system prompt."""
        agent = Mock(spec=Agent)
        agent.name = "Test Agent"
        agent.name_zh = "Test Agent CN"
        agent.agent_type = AgentType.GREAT_POWER
        agent.leadership_type = LeadershipType.WANGDAO
        agent.leadership_profile = get_leadership_profile(LeadershipType.WANGDAO)

        builder = BehaviorPromptBuilder()
        system_prompt = builder.build_system_prompt(agent)

        assert "Test Agent" in system_prompt
        assert "Test Agent CN" in system_prompt
        assert "WANGDAO" in system_prompt or "Wangdao" in system_prompt

    def test_build_user_prompt(self) -> None:
        """Test building user prompt."""
        agent = Mock(spec=Agent)
        agent.name = "Test Agent"
        agent.leadership_type = LeadershipType.WANGDAO
        agent.leadership_profile = get_leadership_profile(LeadershipType.WANGDAO)

        context = PromptContext(
            s="Current international situation",
            available_actions=[
                {"action_type": "diplomatic_visit", "description": "Conduct diplomatic visit"},
            ],
        )

        builder = BehaviorPromptBuilder()
        user_prompt = builder.build_user_prompt(agent, context)

        assert "Current international situation" in user_prompt
        assert "Available Actions" in user_prompt or "Available Actions" in user_prompt

    def test_filter_actions_by_constraints(self) -> None:
        """Test action filtering by constraints."""
        actions = [
            {"action_type": "military_action", "description": "Use military force"},
            {"action_type": "diplomatic_visit", "description": "Diplomatic visit"},
            {"action_type": "norm_proposal", "description": "Propose norms"},
        ]

        prohibited = ["military", "aggression"]
        prioritized = ["diplomatic", "norm"]

        builder = BehaviorPromptBuilder()
        filtered, removed = builder.filter_actions_by_constraints(
            actions, prohibited, prioritized
        )

        # Check that military action was removed
        assert len(filtered) == 2
        assert len(removed) == 1

        # Check that prioritized actions are first
        filtered_types = [a["action_type"] for a in filtered]
        assert filtered_types[0] in ["diplomatic_visit", "norm_proposal"]

    def test_validate_action_type(self) -> None:
        """Test action type validation."""
        builder = BehaviorPromptBuilder()

        # Valid action types
        assert builder.validate_action_type("diplomatic_visit")
        assert builder.validate_action_type("security_military")
        assert builder.validate_action_type("economic_trade")

        # Invalid action type
        assert builder.validate_action_type("invalid_action") is False

    def test_get_action_leadership_affinity(self) -> None:
        """Test getting action-leadership affinity."""
        builder = BehaviorPromptBuilder()

        # Wangdao should have high affinity for normative actions
        wangdao_norm_affinity = builder.get_action_leadership_affinity(
            "norm_proposal", LeadershipType.WANGDAO
        )
        assert wangdao_norm_affinity > 0.8

        # Qiangquan should have high affinity for coercive actions
        qiangquan_military_affinity = builder.get_action_leadership_affinity(
            "security_military", LeadershipType.QIANGQUAN
        )
        assert qiangquan_military_affinity > 0.8

    def test_get_suggested_actions(self) -> None:
        """Test getting suggested actions for leadership type."""
        builder = BehaviorPromptBuilder()

        # Wangdao suggestions
        wangdao_actions = builder.get_suggested_actions(LeadershipType.WANGDAO, count=3)
        assert len(wangdao_actions) == 3
        assert "norm_proposal" in wangdao_actions

        # Qiangquan suggestions
        qiangquan_actions = builder.get_suggested_actions(LeadershipType.QIANGQUAN, count=3)
        assert len(qiangquan_actions) == 3
        assert "security_military" in qiangquan_actions


class TestMessageType:
    """Tests for MessageType enum."""

    def test_enum_values(self) -> None:
        """Test that message type enum values are defined."""
        assert MessageType.DIPLOMATIC_PROPOSAL.value == "diplomatic_proposal"
        assert MessageType.DIPLOMATIC_REQUEST.value == "diplomatic_request"
        assert MessageType.ALLIANCE_REQUEST.value == "alliance_request"
        assert MessageType.TRADE_PROPOSAL.value == "trade_proposal"
        assert MessageType.SECURITY_THREAT.value == "security_threat"
        assert MessageType.NORM_PROPOSAL.value == "norm_proposal"
        assert MessageType.MORAL_APPEAL.value == "moral_appeal"

    def test_descriptions(self) -> None:
        """Test that message type descriptions are defined."""
        assert len(MESSAGE_DESCRIPTIONS) > 0

        for msg_type, description in MESSAGE_DESCRIPTIONS.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestResponseTone:
    """Tests for ResponseTone enum."""

    def test_enum_values(self) -> None:
        """Test that response tone enum values are defined."""
        assert ResponseTone.COOPERATIVE.value == "cooperative"
        assert ResponseTone.ASSERTIVE.value == "assertive"
        assert ResponseTone.NEUTRAL.value == "neutral"
        assert ResponseTone.CONCILIATORY.value == "conciliatory"
        assert ResponseTone.FIRM.value == "firm"
        assert ResponseTone.HOSTILE.value == "hostile"


class TestResponsePromptBuilder:
    """Tests for ResponsePromptBuilder class."""

    def setup_method(self) -> None:
        """Set up test with builder."""
        self.builder = ResponsePromptBuilder()

    def test_initialization(self) -> None:
        """Test ResponsePromptBuilder initialization."""
        builder = ResponsePromptBuilder()

        assert isinstance(builder, BasePromptBuilder)

    def test_build_system_prompt(self) -> None:
        """Test building system prompt."""
        agent = Mock(spec=Agent)
        agent.name = "Test Agent"
        agent.name_zh = "Test Agent CN"
        agent.agent_type = AgentType.GREAT_POWER
        agent.leadership_type = LeadershipType.WANGDAO
        agent.leadership_profile = get_leadership_profile(LeadershipType.WANGDAO)

        builder = ResponsePromptBuilder()
        system_prompt = builder.build_system_prompt(agent)

        assert "Test Agent" in system_prompt
        assert "Test Agent CN" in system_prompt

    def test_build_response_prompt(self) -> None:
        """Test building response prompt."""
        agent = Mock(spec=Agent)
        agent.name = "Responder"
        agent.name_zh = "Responder CN"
        agent.leadership_type = LeadershipType.WANGDAO
        agent.leadership_profile = get_leadership_profile(LeadershipType.WANGDAO)

        sender = {
            "name": "Sender",
            "agent_id": "sender_001",
            "relationship_score": 0.7,
        }

        message = {
            "type": "diplomatic_proposal",
            "content": "Let us cooperate on this matter",
        }

        builder = ResponsePromptBuilder()
        response_prompt = builder.build_response_prompt(agent, sender, message)

        assert "Sender" in response_prompt
        assert "Incoming Message" in response_prompt
        assert "Let us cooperate on this matter" in response_prompt

    def test_get_recommended_tone(self) -> None:
        """Test getting recommended response tone."""
        builder = ResponsePromptBuilder()

        # Positive relationship
        tone_friendly = builder.get_recommended_tone(
            LeadershipType.WANGDAO, "diplomatic_proposal", 0.7
        )
        assert tone_friendly in [ResponseTone.COOPERATIVE, ResponseTone.CONCILIATORY]

        # Negative relationship
        tone_hostile = builder.get_recommended_tone(
            LeadershipType.QIANGQUAN, "security_threat", -0.6
        )
        assert tone_hostile in [ResponseTone.FIRM, ResponseTone.HOSTILE]

        # Neutral relationship
        tone_neutral = builder.get_recommended_tone(
            LeadershipType.HUNYONG, "trade_proposal", 0.1
        )
        assert tone_neutral == ResponseTone.NEUTRAL

    def test_format_response_metadata(self) -> None:
        """Test formatting response metadata."""
        agent = Mock(spec=Agent)
        agent.name = "Responder"
        agent.agent_id = "resp_001"
        agent.leadership_type = LeadershipType.WANGDAO

        builder = ResponsePromptBuilder()
        metadata = builder.format_response_metadata(
            agent, "sender_001", "diplomatic_proposal", ResponseTone.COOPERATIVE
        )

        assert metadata["sender_id"] == "resp_001"
        assert metadata["receiver_id"] == "sender_001"
        assert metadata["message_type"] == "diplomatic_proposal"
        assert metadata["response_tone"] == "cooperative"
        assert "leadership_type" in metadata
        assert "timestamp" in metadata


class TestUtilityFunctionsPrompts:
    """Tests for prompt-related utility functions."""

    def test_get_message_description(self) -> None:
        """Test getting message description."""
        desc = get_message_description("diplomatic_proposal")

        assert desc is not None
        assert isinstance(desc, str)

        # Unknown message type
        unknown_desc = get_message_description("unknown_type")
        assert unknown_desc == "Unknown message type"

    def test_get_response_tone_description(self) -> None:
        """Test getting response tone description."""
        desc = get_response_tone_description("cooperative")

        assert desc is not None
        assert isinstance(desc, str)

        # Unknown tone
        unknown_desc = get_response_tone_description("unknown")
        assert unknown_desc == "Unknown tone"

    def test_get_behavior_category_for_action(self) -> None:
        """Test getting behavior category for action."""
        category = get_behavior_category_for_action("norm_proposal")

        assert category == BehaviorCategory.NORM_PROPOSAL

        # Unknown action
        unknown_category = get_behavior_category_for_action("unknown_action")
        assert unknown_category is None


class TestGreatPowerPromptBuilderExtended:
    """Extended tests for GreatPowerPromptBuilder."""

    def setup_method(self) -> None:
        """Set up test with builder."""
        self.builder = GreatPowerPromptBuilder()

    def test_function_definitions_structure(self) -> None:
        """Test that function definitions have correct structure."""
        definitions = self.builder.get_function_definitions()

        assert isinstance(definitions, list)
        assert len(definitions) > 0

        # Check select_action function
        select_func = definitions[0]
        assert "name" in select_func
        assert "description" in select_func
        assert "parameters" in select_func
        assert select_func["name"] == "select_action"

    def test_parse_function_call_success(self) -> None:
        """Test parsing successful function call."""
        # Mock function call with arguments
        mock_call = Mock()
        mock_call.arguments = {
            "action_type": "diplomatic_visit",
            "target_agent_id": "target_001",
            "rationale": "Test rationale",
            "moral_consideration": "Considered moral aspects",
            "resource_allocation": 75,
            "priority": "high",
        }

        builder = GreatPowerPromptBuilder()
        result = builder.parse_function_call(mock_call)

        assert result["action_type"] == "diplomatic_visit"
        assert result["target_agent_id"] == "target_001"
        assert result["rationale"] == "Test rationale"
        assert result["moral_consideration"] == "Considered moral aspects"
        assert result["resource_allocation"] == 75
        assert result["priority"] == "high"

    def test_parse_function_call_none(self) -> None:
        """Test parsing None function call."""
        builder = GreatPowerPromptBuilder()
        result = builder.parse_function_call(None)

        assert result["action_type"] == "no_action"
        assert result["priority"] == "low"

    def test_parse_function_call_dict(self) -> None:
        """Test parsing function call from dict."""
        function_dict = {
            "action_type": "economic_trade",
            "rationale": "Economic cooperation",
            "priority": "medium",
        }

        builder = GreatPowerPromptBuilder()
        result = builder.parse_function_call(function_dict)

        assert result["action_type"] == "economic_trade"
        assert result["rationale"] == "Economic cooperation"

    def test_action_type_enum(self) -> None:
        """Test ActionType enum values."""
        # Security actions
        assert ActionType.SECURITY_MILITARY.value == "security_military"
        assert ActionType.SECURITY_ALLIANCE.value == "security_alliance"
        assert ActionType.SECURITY_MEDIATION.value == "security_mediation"

        # Economic actions
        assert ActionType.ECONOMIC_TRADE.value == "economic_trade"
        assert ActionType.ECONOMIC_SANCTION.value == "economic_sanction"
        assert ActionType.ECONOMIC_AID.value == "economic_aid"

        # Norm actions
        assert ActionType.NORM_PROPOSAL.value == "norm"
        assert ActionType.NORM_REFORM.value == "norm_reform"

        # Diplomatic actions
        assert ActionType.DIPLOMATIC_VISIT.value == "diplomatic_visit"
        assert ActionType.DIPLOMATIC_ALLIANCE.value == "diplomatic_alliance"

    def test_action_descriptions(self) -> None:
        """Test that action descriptions are defined."""
        assert len(ACTION_DESCRIPTIONS) > 0

        for action_type, description in ACTION_DESCRIPTIONS.items():
            assert isinstance(description, str)
            assert len(description) > 0
