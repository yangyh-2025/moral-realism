"""
Behavior selection prompts for moral realism ABM system.

This module provides BehaviorPromptBuilder for generating prompts that
guide agents in selecting appropriate behaviors based on their
leadership type, capabilities, and current context.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from src.models.agent import Agent
from src.models.leadership_type import LeadershipType
from src.prompts.base_prompt import BasePromptBuilder, PromptContext
from src.prompts.leadership_prompts import ActionType, ACTION_DESCRIPTIONS


class BehaviorCategory(Enum):
    """Categories of behavior for agents."""

    # Cooperative behaviors
    DIPLOMATIC_ENGAGEMENT = "diplomatic_engagement"
    COOPERATIVE_ACTION = "cooperative_action"
    MUTUAL_BENEFIT = "mutual_benefit"

    # Coercive behaviors
    MILITARY_ACTION = "military_action"
    ECONOMIC_PRESSURE = "economic_pressure"
    SANCTION_APPLICATION = "sanction_application"

    # Normative behaviors
    NORM_PROPOSAL = "norm_proposal"
    NORM_ENFORCEMENT = "norm_enforcement"
    MORAL_PERSUASION = "moral_persuasion"

    # Passive behaviors
    OBSERVATION = "observation"
    DELAYED_RESPONSE = "delayed_response"
    INACTION = "inaction"


BEHAVIOR_DESCRIPTIONS: Dict[BehaviorCategory, str] = {
    BehaviorCategory.DIPLOMATIC_ENGAGEMENT: "Engage in diplomatic dialogue and negotiations",
    BehaviorCategory.COOPERATIVE_ACTION: "Take cooperative actions for mutual benefit",
    BehaviorCategory.MUTUAL_BENEFIT: "Seek solutions that benefit all parties",
    BehaviorCategory.MILITARY_ACTION: "Use military force or threat of force",
    BehaviorCategory.ECONOMIC_PRESSURE: "Apply economic leverage or pressure",
    BehaviorCategory.SANCTION_APPLICATION: "Impose or maintain economic sanctions",
    BehaviorCategory.NORM_PROPOSAL: "Propose new international norms or rules",
    BehaviorCategory.NORM_ENFORCEMENT: "Enforce existing international norms",
    BehaviorCategory.MORAL_PERSUASION: "Use moral arguments to persuade others",
    BehaviorCategory.OBSERVATION: "Observe and assess the situation without acting",
    BehaviorCategory.DELAYED_RESPONSE: "Delay action to gather more information",
    BehaviorCategory.INACTION: "Choose not to take action at this time",
}


class BehaviorPromptBuilder(BasePromptBuilder):
    """
    Builder for generating behavior selection prompts.

    This class constructs prompts that help agents select appropriate
    behaviors based on their leadership type, constraints, and context.
    """

    def __init__(self) -> None:
        """Initialize behavior prompt builder."""
        super().__init__()
        self._load_behavior_templates()

    def build_system_prompt(
        self,
        agent: Agent,
        function_definitions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Build system prompt for behavior selection.

        Args:
            agent: The agent for which to build the prompt.
            function_definitions: Optional function definitions for structured output.

        Returns:
            The system prompt string.
        """
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")

        sections = [
            self._format_agent_identity(agent),
            "",
            self._format_leadership_profile(agent),
            "",
            self._format_behavior_guidelines(agent),
        ]

        if function_definitions:
            sections.append("")
            sections.append("## Function Calling")
            sections.append("")
            sections.append("You must respond with a function call that selects an action from the available options.")
            sections.append("")
            sections.append("## Available Functions")
            sections.append("")
            for func_def in function_definitions:
                name = func_def.get("name", "unknown")
                description = func_def.get("description", "")
                sections.append(f"### {name}")
                sections.append(description)
                sections.append("")

        return "\n".join(sections)

    def build_user_prompt(
        self,
        agent: Agent,
        context: PromptContext,
        filtered_actions: Optional[List[Dict[str, Any]]] = None,
        constraints: Optional[List[str]] = None,
    ) -> str:
        """
        Build user prompt for behavior selection.

        Args:
            agent: The agent for which to build the prompt.
            context: The prompt context information.
            filtered_actions: Optional list of filtered actions (if action filtering is applied).
            constraints: Optional list of behavioral constraints.

        Returns:
            The user prompt string.
        """
        sections = []

        # Add situation description
        if context.situation:
            sections.append("## Current Situation")
            sections.append(context.situation)
            sections.append("")

        # Add situation details
        if context.situation_details:
            sections.append("## Situation Details")
            for key, value in context.situation_details.items():
                if isinstance(value, (dict, list)):
                    sections.append(f"\n**{key}**:")
                    sections.append(self._format_complex_value(value))
                else:
                    sections.append(f"- **{key}**: {value}")
            sections.append("")

        # Add capabilities
        if agent.capability:
            sections.append(self._format_capabilities(agent))
            sections.append("")

        # Add available actions or filtered actions
        if filtered_actions:
            sections.append("## Available Actions (Filtered by Constraints)")
            for action in filtered_actions:
                action_type = action.get("action_type", "unknown")
                description = action.get("description", "")
                sections.append(f"- {action_type}: {description}")
        elif context.available_actions:
            sections.append(self._format_actions(context.available_actions))
        else:
            # Use default action types
            sections.append("## Available Actions")
            for action_type, desc in ACTION_DESCRIPTIONS.items():
                sections.append(f"- {action_type.value}: {desc}")
        sections.append("")

        # Add constraints
        if constraints:
            sections.append("## Behavioral Constraints")
            for constraint in constraints:
                sections.append(f"- {constraint}")
            sections.append("")

        # Add other agents
        if context.other_agents:
            sections.append(self._format_other_agents(context.other_agents))
            sections.append("")

        # Add recent events
        if context.recent_events:
            sections.append(self._format_events(context.recent_events))
            sections.append("")

        # Add task
        sections.append("## Task")
        sections.append("")

        task = f"""Based on your leadership type ({agent.leadership_profile.name_zh}), capabilities, and the current situation, select the most appropriate action.

Consider:
1. Your moral standards and how they should guide this decision
2. Your strategic interests and what action best serves them
3. The impact on your international reputation
4. How your choice aligns with your prohibited/prioritized actions
5. The likely reactions of other great powers"""

        sections.append(task)

        return "\n".join(sections)

    def build_behavior_suggestion_prompt(
        self,
        agent: Agent,
        context: PromptContext,
        target_categories: Optional[List[BehaviorCategory]] = None,
    ) -> str:
        """
        Build prompt for suggesting behaviors from specific categories.

        Args:
            agent: The agent for which to build the prompt.
            context: The prompt context information.
            target_categories: Optional list of behavior categories to focus on.

        Returns:
            The behavior suggestion prompt string.
        """
        sections = [
            "You are a behavioral analyst suggesting appropriate actions for an agent.",
            "",
            self._format_agent_identity(agent),
            "",
            self._format_leadership_profile(agent),
            "",
        ]

        if target_categories:
            sections.append("## Target Behavior Categories")
            for category in target_categories:
                desc = BEHAVIOR_DESCRIPTIONS.get(category, "Unknown")
                sections.append(f"- {category.value}: {desc}")
            sections.append("")
        else:
            sections.append("## All Behavior Categories")
            for category, desc in BEHAVIOR_DESCRIPTIONS.items():
                sections.append(f"- {category.value}: {desc}")
            sections.append("")

        sections.append("## Current Situation")
        if context.situation:
            sections.append(context.situation)
        sections.append("")

        sections.append("## Task")
        sections.append("")

        if target_categories:
            categories_str = ", ".join([c.value for c in target_categories])
            task = f"""Suggest appropriate behaviors from these categories: {categories_str}

Based on the agent's leadership type and profile, provide:
1. Which specific actions align with the target categories
2. How these actions serve the agent's interests
3. Potential moral considerations
4. Expected impact on international relations"""
        else:
            task = """Suggest appropriate behaviors for this agent in the current situation.

Based on the agent's leadership type and profile, provide:
1. The most suitable behavior category
2. Specific actions within that category
3. How these actions serve the agent's interests
4. Potential moral considerations
5. Expected impact on international relations"""

        sections.append(task)

        return "\n".join(sections)

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get function definitions for behavior selection.

        Returns:
            List of function definitions for the LLM.
        """
        action_values = [action_type.value for action_type in ActionType]

        return [
            {
                "name": "select_behavior",
                "description": "Select a behavior/action based on the situation and leadership characteristics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "enum": action_values,
                            "description": "The type of action to take",
                        },
                        "behavior_category": {
                            "type": "string",
                            "enum": [cat.value for cat in BehaviorCategory],
                            "description": "The category of behavior this action represents",
                        },
                        "target_agent_id": {
                            "type": "string",
                            "description": "The ID of the target agent (if applicable)",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "The reasoning behind this behavior selection",
                        },
                        "moral_consideration": {
                            "type": "string",
                            "description": "How moral principles influenced this decision",
                        },
                        "expected_outcome": {
                            "type": "string",
                            "description": "Expected outcome of this behavior",
                        },
                    },
                    "required": ["action_type", "behavior_category", "rationale"],
                },
            }
        ]

    def filter_actions_by_constraints(
        self,
        actions: List[Dict[str, Any]],
        prohibited: List[str],
        prioritized: Optional[List[str]] = None,
    ) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Filter actions based on leadership constraints.

        Args:
            actions: List of available actions.
            prohibited: List of prohibited action types.
            prioritized: Optional list of prioritized actions (brought to front).

        Returns:
            Tuple of (filtered_actions, removed_action_descriptions).
        """
        filtered = []
        removed = []

        for action in actions:
            action_type = action.get("action_type", action.get("id", ""))
            description = action.get("description", "")

            # Check if action is prohibited
            is_prohibited = any(
                action_type == prohibited_item or
                prohibited_item.lower() in action_type.lower() or
                action_type.lower() in prohibited_item.lower()
                for prohibited_item in prohibited
            )

            if is_prohibited:
                removed.append(f"{action_type}: {description}")
            else:
                filtered.append(action)

        # If prioritized actions specified, reorder
        if prioritized:
            prioritized_items = []
            other_items = []

            for action in filtered:
                action_type = action.get("action_type", action.get("id", ""))
                if any(
                    action_type == p or p.lower() in action_type.lower()
                    for p in prioritized
                ):
                    prioritized_items.append(action)
                else:
                    other_items.append(action)

            filtered = prioritized_items + other_items

        return filtered, removed

    def validate_action_type(self, action_type: str) -> bool:
        """
        Validate that an action type is recognized.

        Args:
            action_type: The action type to validate.

        Returns:
            True if valid, False otherwise.
        """
        return action_type in [at.value for at in ActionType]

    def get_action_leadership_affinity(
        self,
        action_type: str,
        leadership_type: LeadershipType,
    ) -> float:
        """
        Get the affinity score between an action type and leadership type.

        This represents how well-suited an action is for a given
        leadership type (0-1 scale).

        Args:
            action_type: The action type.
            leadership_type: The leadership type.

        Returns:
            Affinity score (0-1).
        """
        # Define affinity scores for each leadership type
        # Higher score = more aligned with leadership type

        affinities = {
            LeadershipType.WANGDAO: {
                ActionType.SECURITY_MILITARY.value: 0.2,
                ActionType.SECURITY_ALLIANCE.value: 0.6,
                ActionType.SECURITY_MEDIATION.value: 0.9,
                ActionType.ECONOMIC_TRADE.value: 0.8,
                ActionType.ECONOMIC_SANCTION.value: 0.3,
                ActionType.ECONOMIC_AID.value: 0.9,
                ActionType.NORM_PROPOSAL.value: 0.95,
                ActionType.NORM_REFORM.value: 0.9,
                ActionType.DIPLOMATIC_VISIT.value: 0.9,
                ActionType.DIPLOMATIC_ALLIANCE.value: 0.7,
            },
            LeadershipType.HEGEMON: {
                ActionType.SECURITY_MILITARY.value: 0.7,
                ActionType.SECURITY_ALLIANCE.value: 0.95,
                ActionType.SECURITY_MEDIATION.value: 0.4,
                ActionType.ECONOMIC_TRADE.value: 0.6,
                ActionType.ECONOMIC_SANCTION.value: 0.7,
                ActionType.ECONOMIC_AID.value: 0.3,
                ActionType.NORM_PROPOSAL.value: 0.4,
                ActionType.NORM_REFORM.value: 0.5,
                ActionType.DIPLOMATIC_VISIT.value: 0.6,
                ActionType.DIPLOMATIC_ALLIANCE.value: 0.8,
            },
            LeadershipType.QIANGQUAN: {
                ActionType.SECURITY_MILITARY.value: 0.9,
                ActionType.SECURITY_ALLIANCE.value: 0.5,
                ActionType.SECURITY_MEDIATION.value: 0.2,
                ActionType.ECONOMIC_TRADE.value: 0.8,
                ActionType.ECONOMIC_SANCTION.value: 0.8,
                ActionType.ECONOMIC_AID.value: 0.1,
                ActionType.NORM_PROPOSAL.value: 0.2,
                ActionType.NORM_REFORM.value: 0.2,
                ActionType.DIPLOMATIC_VISIT.value: 0.4,
                ActionType.DIPLOMATIC_ALLIANCE.value: 0.5,
            },
            LeadershipType.HUNYONG: {
                ActionType.SECURITY_MILITARY.value: 0.1,
                ActionType.SECURITY_ALLIANCE.value: 0.5,
                ActionType.SECURITY_MEDIATION.value: 0.6,
                ActionType.ECONOMIC_TRADE.value: 0.7,
                ActionType.ECONOMIC_SANCTION.value: 0.2,
                ActionType.ECONOMIC_AID.value: 0.6,
                ActionType.NORM_PROPOSAL.value: 0.5,
                ActionType.NORM_REFORM.value: 0.5,
                ActionType.DIPLOMATIC_VISIT.value: 0.8,
                ActionType.DIPLOMATIC_ALLIANCE.value: 0.4,
            },
        }

        leadership_affinities = affinities.get(leadership_type, {})

        # Default to medium affinity if action not found
        return leadership_affinities.get(action_type, 0.5)

    def get_suggested_actions(
        self,
        leadership_type: LeadershipType,
        count: int = 3,
    ) -> List[str]:
        """
        Get suggested actions for a leadership type.

        Args:
            leadership_type: The leadership type.
            count: Number of suggestions to return.

        Returns:
            List of suggested action type values.
        """
        # Get all action types with their affinity scores
        action_affinities = [
            (action_type.value, self.get_action_leadership_affinity(action_type.value, leadership_type))
            for action_type in ActionType
        ]

        # Sort by affinity (descending) and return top N
        sorted_actions = sorted(action_affinities, key=lambda x: x[1], reverse=True)

        return [action[0] for action in sorted_actions[:count]]

    def _load_behavior_templates(self) -> None:
        """Load behavior-specific prompt templates."""
        self.templates.update({
            "behavior_guidelines_wangdao": """As a Wangdao (Moral) leader, your behavior is guided by moral principles:

### Decision-Making Principles
- Moral legitimacy is the primary consideration
- Diplomatic solutions are preferred over coercion
- International law and norms should be respected
- Actions should enhance your moral authority
- Consider the welfare and consent of affected parties

### Behavioral Preferences
- High preference for: mediation, norm proposal, diplomatic visits
- Moderate preference for: alliance building, economic cooperation
- Low preference for: military action, economic sanctions

### When Considering Force
- Only as a last resort
- Requires proper international authorization
- Must be necessary and proportional
- Consider humanitarian consequences
""",
            "behavior_guidelines_hegemon": """As a Traditional Hegemon, your behavior is guided by power projection:

### Decision-Making Principles
- Maintaining hegemonic position is the priority
- Power should be projected when core interests are at stake
- Alliance management is key to strategic positioning
- Balance power with selective concern for legitimacy

### Behavioral Preferences
- High preference for: alliance building, military action
- Moderate preference for: economic cooperation, sanctions
- Low preference for: mediation, unilateral norm proposals

### When Considering Cooperation
- Cooperate when it serves hegemonic interests
- Use alliance networks to achieve objectives
- Maintain sphere of influence
- Consider long-term strategic positioning
""",
            "behavior_guidelines_qiangquan": """As a Power-seeking (Qiangquan) leader, your behavior is guided by national interests:

### Decision-Making Principles
- Maximizing national power is the primary objective
- All means are justified for advancing interests
- Power is the ultimate arbiter of outcomes
- Moral considerations are secondary to results

### Behavioral Preferences
- High preference for: military action, economic pressure, sanctions
- Moderate preference for: economic cooperation, alliance building
- Low preference for: mediation, norm proposals, appeasement

### Decision Approach
- Act decisively when opportunities arise
- Exploit weaknesses in others
- Build deterrent capabilities
- Consider power calculus in all decisions
""",
            "behavior_guidelines_hunyong": """As a Hunyong (Appeasement/Cooperation) leader, your behavior is guided by conflict avoidance:

### Decision-Making Principles
- Avoiding confrontation is a primary objective
- Cooperation and accommodation are preferred
- Maintain positive relationships with others
- Be willing to make concessions

### Behavioral Preferences
- High preference for: diplomatic visits, mediation, cooperation
- Moderate preference for: norm proposals, economic aid
- Low preference for: military action, coercive measures

### Decision Approach
- Seek compromise and accommodation
- Use moral arguments to support cooperation
- Build confidence through transparency
- Prioritize relationship maintenance
""",
        })

    def _format_behavior_guidelines(self, agent: Agent) -> str:
        """
        Format behavior guidelines based on leadership type.

        Args:
            agent: The agent.

        Returns:
            Formatted behavior guidelines string.
        """
        leadership_type = agent.leadership_type
        template_key = f"behavior_guidelines_{leadership_type.value}"

        template = self.templates.get(template_key, "")

        if template:
            return f"## Behavior Guidelines\n\n{template}"
        else:
            return "## Behavior Guidelines\n\nStandard behavior guidelines apply."

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

    def parse_behavior_selection(self, function_call: Any) -> Dict[str, Any]:
        """
        Parse behavior selection result from LLM.

        Args:
            function_call: The function call object from LLM response.

        Returns:
            Parsed behavior selection as dictionary.
        """
        if function_call is None:
            return {
                "action_type": ActionType.NO_ACTION.value,
                "behavior_category": BehaviorCategory.INACTION.value,
                "rationale": "No behavior selected",
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
                "behavior_category": arguments.get(
                    "behavior_category",
                    BehaviorCategory.INACTION.value
                ),
                "target_agent_id": arguments.get("target_agent_id"),
                "rationale": arguments.get("rationale", ""),
                "moral_consideration": arguments.get("moral_consideration", ""),
                "expected_outcome": arguments.get("expected_outcome", ""),
            }
        elif isinstance(function_call, dict):
            return {
                "action_type": function_call.get("action_type", ActionType.NO_ACTION.value),
                "behavior_category": function_call.get(
                    "behavior_category",
                    BehaviorCategory.INACTION.value
                ),
                "target_agent_id": function_call.get("target_agent_id"),
                "rationale": function_call.get("rationale", ""),
                "moral_consideration": function_call.get("moral_consideration", ""),
                "expected_outcome": function_call.get("expected_outcome", ""),
            }
        else:
            return {
                "action_type": ActionType.NO_ACTION.value,
                "behavior_category": BehaviorCategory.INACTION.value,
                "rationale": "Unable to parse behavior selection",
            }


def get_behavior_category_for_action(action_type: str) -> Optional[BehaviorCategory]:
    """
    Get the behavior category for a given action type.

    Args:
        action_type: The action type value.

    Returns:
        The behavior category if mapped, None otherwise.
    """
    action_to_category = {
        ActionType.SECURITY_MILITARY.value: BehaviorCategory.MILITARY_ACTION,
        ActionType.SECURITY_ALLIANCE.value: BehaviorCategory.DIPLOMATIC_ENGAGEMENT,
        ActionType.SECURITY_MEDIATION.value: BehaviorCategory.DIPLOMATIC_ENGAGEMENT,
        ActionType.ECONOMIC_TRADE.value: BehaviorCategory.COOPERATIVE_ACTION,
        ActionType.ECONOMIC_SANCTION.value: BehaviorCategory.SANCTION_APPLICATION,
        ActionType.ECONOMIC_AID.value: BehaviorCategory.COOPERATIVE_ACTION,
        ActionType.NORM_PROPOSAL.value: BehaviorCategory.NORM_PROPOSAL,
        ActionType.NORM_REFORM.value: BehaviorCategory.NORM_ENFORCEMENT,
        ActionType.DIPLOMATIC_VISIT.value: BehaviorCategory.DIPLOMATIC_ENGAGEMENT,
        ActionType.DIPLOMATIC_ALLIANCE.value: BehaviorCategory.DIPLOMATIC_ENGAGEMENT,
        ActionType.NO_ACTION.value: BehaviorCategory.INACTION,
    }

    return action_to_category.get(action_type)
