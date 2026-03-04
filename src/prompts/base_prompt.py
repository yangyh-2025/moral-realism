"""
Base prompt templates and utilities for the moral realism ABM system.

This module provides the BasePromptBuilder abstract class and common utilities
for constructing prompts across different agent types and scenarios.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.agent import Agent
from src.models.leadership_type import LeadershipType


class PromptSection(Enum):
    """Types of prompt sections for structured prompts."""

    # Core sections
    SYSTEM_INSTRUCTION = "system_instruction"
    AGENT_IDENTITY = "agent_identity"
    LEADERSHIP_PROFILE = "leadership_profile"
    CAPABILITIES = "capabilities"
    CONTEXT = "context"
    CONSTRAINTS = "constraints"
    TASK = "task"
    EXAMPLES = "examples"
    OUTPUT_FORMAT = "output_format"


@dataclass
class PromptContext:
    """
    Context information for prompt construction.

    This class provides a structured way to pass context information
    to prompt builders, ensuring consistent formatting across prompts.
    """

    # Situation description
    situation: str = ""
    situation_details: Dict[str, Any] = field(default_factory=dict)

    # Agent information
    agent_info: Dict[str, Any] = field(default_factory=dict)

    # Available actions
    available_actions: List[Dict[str, Any]] = field(default_factory=list)

    # Other agents in the system
    other_agents: List[Dict[str, Any]] = field(default_factory=list)

    # Recent events
    recent_events: List[Dict[str, Any]] = field(default_factory=list)

    # Relationships
    relationships: Dict[str, float] = field(default_factory=dict)

    # Custom context fields
    custom: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from context, checking all sections.

        Args:
            key: The key to look up.
            default: Default value if key not found.

        Returns:
            The value if found, otherwise default.
        """
        # Check main fields
        if hasattr(self, key):
            value = getattr(self, key)
            if value:
                return value

        # Check situation details
        if key in self.situation_details:
            return self.situation_details[key]

        # Check custom agent info
        if key in self.agent_info:
            return self.agent_info[key]

        # Check custom context
        if key in self.custom:
            return self.custom[key]

        return default

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary.

        Returns:
            Dictionary representation of context.
        """
        return {
            "situation": self.situation,
            "situation_details": self.situation_details,
            "agent_info": self.agent_info,
            "available_actions": self.available_actions,
            "other_agents": self.other_agents,
            "recent_events": self.recent_events,
            "relationships": self.relationships,
            "custom": self.custom,
        }


class BasePromptBuilder(ABC):
    """
    Abstract base class for all prompt builders.

    This class defines the interface that all prompt builders must implement,
    ensuring consistency across the system and providing common utilities.
    """

    def __init__(self) -> None:
        """Initialize the prompt builder."""
        self.templates: Dict[str, str] = self._load_default_templates()

    @abstractmethod
    def build_system_prompt(
        self,
        agent: Agent,
        **kwargs: Any,
    ) -> str:
        """
        Build the system prompt for an agent.

        Args:
            agent: The agent for which to build the prompt.
            **kwargs: Additional keyword arguments for prompt construction.

        Returns:
            The system prompt string.
        """
        pass

    @abstractmethod
    def build_user_prompt(
        self,
        agent: Agent,
        context: PromptContext,
        **kwargs: Any,
    ) -> str:
        """
        Build the user prompt for an agent.

        Args:
            agent: The agent for which to build the prompt.
            context: The prompt context information.
            **kwargs: Additional keyword arguments for prompt construction.

        Returns:
            The user prompt string.
        """
        pass

    def build_response_prompt(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        context: Optional[PromptContext] = None,
        **kwargs: Any,
    ) -> str:
        """
        Build a prompt for responding to another agent's message.

        Args:
            agent: The responding agent.
            sender: Dictionary with sender agent information.
            message: The message content.
            context: Additional prompt context.
            **kwargs: Additional keyword arguments for prompt construction.

        Returns:
            The response prompt string.
        """
        # Default implementation - override in subclasses
        return f"""Respond to the following message:

Sender: {sender.get('name', 'Unknown')}
Message: {message.get('content', '')}

Provide a response that reflects your leadership type and interests."""

    def _load_default_templates(self) -> Dict[str, str]:
        """
        Load default prompt templates.

        Returns:
            Dictionary of template names to template strings.
        """
        return {
            "identity": "You are {name} ({name_zh}), a {agent_type} in international relations.",
            "situation": "Current situation: {situation}",
            "task": "Your task is to: {task}",
        }

    def _format_agent_identity(self, agent: Agent) -> str:
        """
        Format agent identity information.

        Args:
            agent: The agent.

        Returns:
            Formatted identity string.
        """
        profile = agent.leadership_profile
        profile_name = profile.name_zh if profile else "Unknown"

        identity = f"""## Agent Identity

Name: {agent.name} ({agent.name_zh})
ID: {agent.agent_id}
Type: {agent.agent_type.value}
Leadership: {profile_name} ({agent.leadership_type.value})"""

        return identity

    def _format_leadership_profile(self, agent: Agent) -> str:
        """
        Format leadership profile information.

        Args:
            agent: The agent.

        Returns:
            Formatted leadership profile string.
        """
        profile = agent.leadership_profile
        if profile is None:
            return "No leadership profile available."

        sections = [
            "## Leadership Profile",
            "",
            f"**{profile.name} ({profile.name_zh})**",
            "",
            profile.description,
            "",
            "### Core Values",
            f"- Moral Standard: {profile.moral_standard:.2f} (0-1 scale)",
            f"- Core Interest Weight: {profile.core_interest_weight:.2f}",
            f"- Marginal Interest Weight: {profile.marginal_interest_weight:.2f}",
            f"- Moral Consideration Weight: {profile.moral_consideration_weight:.2f}",
            "",
            "### Behavioral Preferences",
            f"- Prefers Diplomatic Solutions: {profile.prefers_diplomatic_solution}",
            f"- Uses Moral Persuasion: {profile.uses_moral_persuasion}",
            f"- Accepts Moral Constraints: {profile.accepts_moral_constraints}",
            f"- Prioritizes Reputation: {profile.prioritizes_reputation}",
        ]

        if profile.prohibited_actions:
            sections.append("")
            sections.append("### Prohibited Actions")
            for action in profile.prohibited_actions:
                sections.append(f"- {action}")

        if profile.prioritized_actions:
            sections.append("")
            sections.append("### Prioritized Actions")
            for action in profile.prioritized_actions:
                sections.append(f"- {action}")

        return "\n".join(sections)

    def _format_capabilities(self, agent: Agent) -> str:
        """
        Format capability information.

        Args:
            agent: The agent.

        Returns:
            Formatted capabilities string.
        """
        if agent.capability is None:
            return "No capability information available."

        hard_power = agent.capability.hard_power.get_hard_power_index()
        soft_power = agent.capability.soft_power.get_soft_power_index()
        overall = agent.capability.get_capability_index()
        tier = agent.capability.get_tier().value

        sections = [
            "## Capabilities",
            "",
            f"- Hard Power Index: {hard_power:.2f}/100",
            f"- Soft Power Index: {soft_power:.2f}/100",
            f"- Overall Capability: {overall:.2f}/100",
            f"- Capability Tier: {tier}",
        ]

        # Add strategic interests if available
        from src.models.capability import get_strategic_interests
        interests = get_strategic_interests(agent.capability.get_tier())
        if interests:
            sections.append("")
            sections.append("### Strategic Interests")
            for interest in interests:
                sections.append(f"- {interest}")

        return "\n".join(sections)

    def _format_relationships(self, agent: Agent, context: PromptContext) -> str:
        """
        Format relationship information.

        Args:
            agent: The agent.
            context: The prompt context.

        Returns:
            Formatted relationships string.
        """
        sections = ["## Relationships", ""]

        # Get relationships from agent
        if len(agent.relations) <= 1:  # Only self
            sections.append("No established relationships yet.")
            return "\n".join(sections)

        # Format relationships
        for other_id, score in agent.relations.items():
            if other_id == agent.agent_id:
                continue

            rel_desc = self._describe_relationship(score)
            sections.append(f"- {other_id}: {rel_desc} ({score:.2f})")

        return "\n".join(sections)

    def _describe_relationship(self, score: float) -> str:
        """
        Describe a relationship score in words.

        Args:
            score: The relationship score (-1 to 1).

        Returns:
            Description of the relationship.
        """
        if score > 0.6:
            return "Very Friendly"
        elif score > 0.3:
            return "Friendly"
        elif score > -0.3:
            return "Neutral"
        elif score > -0.6:
            return "Hostile"
        else:
            return "Very Hostile"

    def _format_actions(self, actions: List[Dict[str, Any]]) -> str:
        """
        Format a list of available actions.

        Args:
            actions: List of action dictionaries.

        Returns:
            Formatted actions string.
        """
        if not actions:
            return "No actions available."

        sections = ["## Available Actions", ""]

        for action in actions:
            action_id = action.get("id", action.get("action_type", "unknown"))
            description = action.get("description", action.get("name", "No description"))
            sections.append(f"- **{action_id}**: {description}")

        return "\n".join(sections)

    def _format_events(self, events: List[Dict[str, Any]], max_count: int = 5) -> str:
        """
        Format recent events.

        Args:
            events: List of event dictionaries.
            max_count: Maximum number of events to format.

        Returns:
            Formatted events string.
        """
        if not events:
            return "No recent events."

        recent_events = events[-max_count:]

        sections = ["## Recent Events", ""]

        for i, event in enumerate(recent_events, 1):
            description = event.get("description", event.get("content", str(event)))
            timestamp = event.get("timestamp", "")
            sections.append(f"{i}. {description}")
            if timestamp:
                sections.append(f"   (Time: {timestamp})")

        return "\n".join(sections)

    def _format_other_agents(
        self,
        agents: List[Dict[str, Any]],
        include_relationships: bool = True,
    ) -> str:
        """
        Format information about other agents.

        Args:
            agents: List of agent dictionaries.
            include_relationships: Whether to include relationship scores.

        Returns:
            Formatted agents string.
        """
        if not agents:
            return "No other agents present."

        sections = ["## Other Agents", ""]

        for agent_info in agents:
            name = agent_info.get("name", agent_info.get("agent_id", "Unknown"))
            name_zh = agent_info.get("name_zh", "")
            agent_type = agent_info.get("agent_type", "unknown")
            leadership_type = agent_info.get("leadership_type", "unknown")

            sections.append(f"### {name}")
            if name_zh:
                sections.append(f"**{name_zh}**")
            sections.append(f"- Type: {agent_type}")
            sections.append(f"- Leadership: {leadership_type}")

            if include_relationships:
                relationship = agent_info.get("relationship_score")
                if relationship is not None:
                    rel_desc = self._describe_relationship(relationship)
                    sections.append(f"- Relationship: {rel_desc} ({relationship:.2f})")

            # Add capability if available
            capability_index = agent_info.get("capability_index")
            if capability_index is not None:
                sections.append(f"- Capability: {capability_index:.2f}/100")

            sections.append("")

        return "\n".join(sections)

    def _apply_template(
        self,
        template_name: str,
        **kwargs: Any,
    ) -> str:
        """
        Apply a template with the given variables.

        Args:
            template_name: Name of the template.
            **kwargs: Variables for the template.

        Returns:
            Formatted template string.
        """
        template = self.templates.get(template_name, "")

        try:
            return template.format(**kwargs)
        except KeyError as e:
            # Return template with missing keys highlighted
            return f"[Template Error: Missing key {e}] {template}"

    def validate_prompt(self, prompt: str) -> bool:
        """
        Validate that a prompt meets basic requirements.

        Args:
            prompt: The prompt to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not prompt or len(prompt.strip()) < 10:
            return False

        # Check for obvious placeholder issues
        if "{name}" in prompt or "{situation}" in prompt:
            # These are common placeholders that should be filled
            return False

        return True

    def get_prompt_length(self, prompt: str) -> int:
        """
        Get the length of a prompt in tokens (approximate).

        Args:
            prompt: The prompt string.

        Returns:
            Approximate token count (roughly 1/4 of character count).
        """
        # Rough approximation: ~4 characters per token for English text
        return len(prompt) // 4


class PromptBuilderRegistry:
    """
    Registry for prompt builders, enabling dynamic selection based on agent type.

    This registry allows the system to select the appropriate prompt builder
    for different agent types and scenarios.
    """

    _builders: Dict[str, BasePromptBuilder] = {}

    @classmethod
    def register(cls, name: str, builder: BasePromptBuilder) -> None:
        """
        Register a prompt builder.

        Args:
            name: Name to register the builder under.
            builder: The prompt builder instance.
        """
        cls._builders[name] = builder

    @classmethod
    def get(cls, name: str) -> Optional[BasePromptBuilder]:
        """
        Get a registered prompt builder.

        Args:
            name: Name of the builder to retrieve.

        Returns:
            The prompt builder if found, None otherwise.
        """
        return cls._builders.get(name)

    @classmethod
    def list_builders(cls) -> List[str]:
        """
        Get list of registered builder names.

        Returns:
            List of builder names.
        """
        return list(cls._builders.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered builders."""
        cls._builders.clear()


# Utility functions for prompt construction

def create_default_context(
    situation: str = "",
    available_actions: Optional[List[Dict[str, Any]]] = None,
) -> PromptContext:
    """
    Create a default prompt context.

    Args:
        situation: Situation description.
        available_actions: List of available actions.

    Returns:
        Default prompt context.
    """
    return PromptContext(
        situation=situation,
        available_actions=available_actions or [],
    )


def format_prompt_section(
    title: str,
    content: str,
    level: int = 2,
) -> str:
    """
    Format a prompt section with markdown heading.

    Args:
        title: Section title.
        content: Section content.
        level: Heading level (1-6).

    Returns:
        Formatted section string.
    """
    if not content:
        return ""

    heading = "#" * min(max(level, 1), 6)
    return f"{heading} {title}\n\n{content}\n"


def validate_template_variables(
    template: str,
    variables: Dict[str, Any],
) -> List[str]:
    """
    Validate that all variables in a template are provided.

    Args:
        template: The template string.
        variables: Dictionary of available variables.

    Returns:
        List of missing variable names.
    """
    import re

    # Find all {variable} patterns
    pattern = r'\{([^{}]+)\}'
    found = set(re.findall(pattern, template))

    # Find missing variables
    missing = [var for var in found if var not in variables]

    return missing
