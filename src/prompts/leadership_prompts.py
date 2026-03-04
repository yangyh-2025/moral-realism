"""
Prompt builders for leadership-driven agents in the moral realism ABM system.

This module provides the GreatPowerPromptBuilder for generating decision and
response prompts for great power agents with different leadership types.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.agent import Agent
from src.models.capability import get_strategic_interests
from src.models.leadership_type import LeadershipType


class ActionType(Enum):
    """Types of actions available to great power agents."""

    # Security actions
    SECURITY_MILITARY = "security_military"  # Military deployment/action
    SECURITY_ALLIANCE = "security_alliance"  # Form/maintain alliance
    SECURITY_MEDIATION = "security_mediation"  # Mediate conflict

    # Economic actions
    ECONOMIC_TRADE = "economic_trade"  # Trade agreement/cooperation
    ECONOMIC_SANCTION = "economic_sanction"  # Impose/lift sanctions
    ECONOMIC_AID = "economic_aid"  # Provide economic aid

    # Norm actions
    NORM_PROPOSAL = "norm_proposal"  # Propose new international norm
    NORM_REFORM = "norm_reform"  # Reform existing norm

    # Diplomatic actions
    DIPLOMATIC_VISIT = "diplomatic_visit"  # State visit/diplomacy
    DIPLOMATIC_ALLIANCE = "diplomatic_alliance"  # Formal alliance agreement

    # Special actions
    NO_ACTION = "no_action"  # Take no action


ACTION_DESCRIPTIONS: Dict[ActionType, str] = {
    ActionType.SECURITY_MILITARY: "Deploy or use military forces for security purposes",
    ActionType.SECURITY_ALLIANCE: "Form, strengthen, or maintain security alliances",
    ActionType.SECURITY_MEDIATION: "Mediate between conflicting parties",
    ActionType.ECONOMIC_TRADE: "Engage in trade agreements or economic cooperation",
    ActionType.ECONOMIC_SANCTION: "Impose, maintain, or lift economic sanctions",
    ActionType.ECONOMIC_AID: "Provide economic assistance or development aid",
    ActionType.NORM_PROPOSAL: "Propose new international norms or principles",
    ActionType.NORM_REFORM: "Propose reforms to existing international norms",
    ActionType.DIPLOMATIC_VISIT: "Conduct state visits or diplomatic outreach",
    ActionType.DIPLOMATIC_ALLIANCE: "Form formal diplomatic or strategic alliances",
    ActionType.NO_ACTION: "Take no action and observe developments",
}


class GreatPowerPromptBuilder:
    """
    Builder for generating prompts for great power agents.

    This class constructs system and user prompts that incorporate
    leadership type profiles, capability information, and context.
    """

    def build_system_prompt(
        self,
        agent: Agent,
        function_definitions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Build the system prompt for a great power agent.

        Args:
            agent: The great power agent.
            function_definitions: Optional function definitions for structured output.

        Returns:
            The system prompt string.
        """
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")

        profile = agent.leadership_profile

        system_prompt = f"""You are {agent.name} ({agent.name_zh}), a {profile.name_zh} great power in international relations.

## Leadership Type Characteristics

{profile.description}

### Core Values
- Moral Standard: {profile.moral_standard:.2f} (0-1 scale)
- Core Interest Weight: {profile.core_interest_weight:.2f}
- Moral Consideration Weight: {profile.moral_consideration_weight:.2f}
- Preference for Diplomatic Solutions: {profile.prefers_diplomatic_solution}
- Uses Moral Persuasion: {profile.uses_moral_persuasion}
- Accepts Moral Constraints: {profile.accepts_moral_constraints}
- Prioritizes Reputation: {profile.prioritizes_reputation}

### Prohibited Actions
{', '.join(profile.prohibited_actions) if profile.prohibited_actions else 'None'}

### Prioritized Actions
{', '.join(profile.prioritized_actions) if profile.prioritized_actions else 'None'}

## Decision-Making Guidelines

{profile.decision_prompt_template}

## Function Calling

You must respond with a function call that selects an action from the available options.
"""

        if function_definitions:
            system_prompt += "\n\n## Available Functions\n\n"
            for func_def in function_definitions:
                name = func_def.get("name", "unknown")
                description = func_def.get("description", "")
                system_prompt += f"### {name}\n{description}\n\n"

        return system_prompt

    def build_user_prompt(
        self,
        agent: Agent,
        context: Dict[str, Any],
    ) -> str:
        """
        Build the user prompt for a great power agent.

        Args:
            agent: The great power agent.
            context: Dictionary containing situation information, events, and other agents.

        Returns:
            The user prompt string.
        """
        # Extract context components
        situation = context.get("situation", {})
        events = context.get("events", [])
        other_agents = context.get("other_agents", [])
        available_actions = context.get("available_actions", [])

        # Build prompt
        prompt_parts = ["## Current Situation"]

        if situation:
            for key, value in situation.items():
                if isinstance(value, (dict, list)):
                    prompt_parts.append(f"\n**{key}**:\n{self._format_complex_value(value)}")
                else:
                    prompt_parts.append(f"\n**{key}**: {value}")

        # Add capability information
        if agent.capability:
            hard_power_index = agent.capability.hard_power.get_hard_power_index()
            soft = agent.capability.soft_power.get_soft_power_index()
            overall = agent.capability.get_capability_index()

            prompt_parts.append(f"""
## Your Capabilities
- Hard Power Index: {hard_power_index:.2f}/100
- Soft Power Index: {soft:.2f}/100
- Overall Capability: {overall:.2f}/100
- Capability Tier: {agent.capability.get_tier().value}
""")

        # Add strategic interests
        if agent.capability:
            tier = agent.capability.get_tier()
            interests = get_strategic_interests(tier)
            prompt_parts.append("## Your Strategic Interests\n")
            prompt_parts.extend(f"- {interest}" for interest in interests)

        # Add recent events
        if events:
            prompt_parts.append("\n## Recent Events")
            for i, event in enumerate(events[-5:], 1):  # Last 5 events
                prompt_parts.append(f"\n{i}. {event.get('description', str(event))}")

        # Add information about other agents
        if other_agents:
            prompt_parts.append("\n## Other Great Powers")
            for other in other_agents:
                prompt_parts.append(f"\n### {other['name']} ({other['name_zh']})")
                prompt_parts.append(f"- Leadership Type: {other['leadership_type']}")
                if 'capability_index' in other:
                    prompt_parts.append(f"- Capability Index: {other['capability_index']:.2f}")
                if 'relationship_score' in other:
                    score = other['relationship_score']
                    rel_desc = "friendly" if score > 0.3 else "hostile" if score < -0.3 else "neutral"
                    prompt_parts.append(f"- Relationship: {rel_desc} ({score:.2f})")

        # Add available actions
        if available_actions:
            prompt_parts.append("\n## Available Actions")
            for action in available_actions:
                action_type = action.get("action_type", "unknown")
                description = action.get("description", "")
                prompt_parts.append(f"\n- {action_type}: {description}")
        else:
            # Default actions
            prompt_parts.append("\n## Available Actions")
            for action_type, desc in ACTION_DESCRIPTIONS.items():
                prompt_parts.append(f"- {action_type.value}: {desc}")

        prompt_parts.append("\n\n## Task\n\nSelect the most appropriate action based on your leadership type, capabilities, and the current situation.")

        return "\n".join(prompt_parts)

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get function definitions for structured output.

        Returns:
            List of function definitions for the LLM.
        """
        action_values = [action_type.value for action_type in ActionType]

        return [
            {
                "name": "select_action",
                "description": "Select an action for the great power agent based on the current situation and leadership characteristics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "enum": action_values,
                            "description": "The type of action to take",
                        },
                        "target_agent_id": {
                            "type": "string",
                            "description": "The ID of the target agent (if applicable)",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "The reasoning behind this decision",
                        },
                        "moral_consideration": {
                            "type": "string",
                            "description": "How moral considerations influenced this decision",
                        },
                        "resource_allocation": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Level of resources to allocate to this action (0-100)",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Priority level of this action",
                        },
                    },
                    "required": ["action_type", "rationale", "priority"],
                },
            }
        ]

    def parse_function_call(self, function_call: Any) -> Dict[str, Any]:
        """
        Parse the function call result from the LLM.

        Args:
            function_call: The function call object from the LLM response.

        Returns:
            Parsed function call as dictionary.
        """
        if function_call is None:
            return {
                "action_type": ActionType.NO_ACTION.value,
                "rationale": "No action selected",
                "priority": "low",
            }

        if hasattr(function_call, "arguments"):
            # OpenAI function call object
            import json
            if isinstance(function_call.arguments, str):
                arguments = json.loads(function_call.arguments)
            else:
                arguments = function_call.arguments

            return {
                "action_type": arguments.get("action_type", ActionType.NO_ACTION.value),
                "target_agent_id": arguments.get("target_agent_id"),
                "rationale": arguments.get("rationale", ""),
                "moral_consideration": arguments.get("moral_consideration", "Not specified"),
                "resource_allocation": arguments.get("resource_allocation", 50),
                "priority": arguments.get("priority", "medium"),
            }
        elif isinstance(function_call, dict):
            return {
                "action_type": function_call.get("action_type", ActionType.NO_ACTION.value),
                "target_agent_id": function_call.get("target_agent_id"),
                "rationale": function_call.get("rationale", ""),
                "moral_consideration": function_call.get("moral_consideration", "Not specified"),
                "resource_allocation": function_call.get("resource_allocation", 50),
                "priority": function_call.get("priority", "medium"),
            }
        else:
            return {
                "action_type": ActionType.NO_ACTION.value,
                "rationale": "Unable to parse function call",
                "priority": "low",
            }

    def _format_complex_value(self, value: Any, indent: int = 0) -> str:
        """
        Format complex values for prompt display.

        Args:
            value: The value to format.
            indent: Indentation level.

        Returns:
            Formatted string.
        """
        prefix = "  " * indent

        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{prefix}{k}:")
                    lines.append(self._format_complex_value(v, indent + 1))
                else:
                    lines.append(f"{prefix}{k}: {v}")
            return "\n".join(lines)
        elif isinstance(value, list):
            lines = []
            for item in value:
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}-")
                    lines.append(self._format_complex_value(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {item}")
            return "\n".join(lines)
        else:
            return f"{prefix}{value}"

    def build_response_prompt(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build a prompt for responding to another agent's message.

        Args:
            agent: The responding agent.
            sender: Dictionary with sender agent information.
            message: The message content.
            context: Additional context.

        Returns:
            The response prompt string.
        """
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")

        profile = agent.leadership_profile

        # Get affected interests
        affected_interests = message.get("affected_interests", [])
        if agent.capability:
            tier = agent.capability.get_tier()
            all_interests = get_strategic_interests(tier)
            # Default to top 2 interests if not specified
            if not affected_interests:
                affected_interests = all_interests[:2]

        # Build prompt using the template
        prompt = profile.response_prompt_template.format(
            sender=sender.get("name", "Unknown"),
            proposal=message.get("content", "the proposal"),
            affected_interests=", ".join(affected_interests),
            situation=context.get("situation", "current situation") if context else "current situation",
        )

        return prompt
