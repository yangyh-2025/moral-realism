"""
Response generation prompts for moral realism ABM system.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.prompts.base_prompt import BasePromptBuilder, PromptContext


class MessageType(Enum):
    """Types of messages that agents may send or receive."""

    DIPLOMATIC_PROPOSAL = "diplomatic_proposal"
    DIPLOMATIC_REQUEST = "diplomatic_request"
    ALLIANCE_REQUEST = "alliance_request"
    TRADE_PROPOSAL = "trade_proposal"
    SECURITY_THREAT = "security_threat"
    NORM_PROPOSAL = "norm_proposal"
    MORAL_APPEAL = "moral_appeal"
    INQUIRY = "inquiry"
    ACKNOWLEDGMENT = "acknowledgment"
    COMPLAINT = "complaint"


MESSAGE_DESCRIPTIONS: Dict[MessageType, str] = {
    MessageType.DIPLOMATIC_PROPOSAL: "A proposal for diplomatic engagement",
    MessageType.DIPLOMATIC_REQUEST: "A request for diplomatic action",
    MessageType.ALLIANCE_REQUEST: "A request to form an alliance",
    MessageType.TRADE_PROPOSAL: "A proposal for trade",
    MessageType.SECURITY_THREAT: "A security threat",
    MessageType.NORM_PROPOSAL: "A proposal for norms",
    MessageType.MORAL_APPEAL: "A moral appeal",
    MessageType.INQUIRY: "A request for information",
    MessageType.ACKNOWLEDGMENT: "An acknowledgment",
    MessageType.COMPLAINT: "A complaint",
}


class ResponseTone(Enum):
    """Tones that can be used in responses."""

    COOPERATIVE = "cooperative"
    ASSERTIVE = "assertive"
    NEUTRAL = "neutral"
    CONCILIATORY = "conciliatory"
    FIRM = "firm"
    HOSTILE = "hostile"


class ResponsePromptBuilder(BasePromptBuilder):
    """Builder for generating response prompts."""

    def build_system_prompt(self, agent: Agent, **kwargs: Any) -> str:
        """Build system prompt for response generation."""
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")

        sections = [
            f"You are {agent.name} ({agent.name_zh}), a {agent.agent_type.value}.",
            "",
            "Your response style should reflect your leadership type.",
            "",
            self._format_leadership_profile(agent),
        ]
        return "\n".join(sections)

    def build_user_prompt(self, agent: Agent, context: PromptContext, **kwargs: Any) -> str:
        """Build user prompt for response generation."""
        sender = kwargs.get("sender", context.agent_info.get("sender", {}))
        message = kwargs.get("message", context.situation_details.get("message", {}))
        return self.build_response_prompt(agent, sender, message, context, **kwargs)

    def build_response_prompt(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        context: Optional[PromptContext] = None,
        **kwargs: Any,
    ) -> str:
        """Build a prompt for responding to a message."""
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")
        if context is None:
            context = PromptContext()

        sections = ["## Incoming Message", ""]
        sender_name = sender.get("name", sender.get("agent_id", "Unknown"))
        message_type = message.get("type", "unknown")
        message_content = message.get("content", "No content")

        sections.append(f"**From**: {sender_name}")
        sections.append("")
        sections.append(f"**Type**: {message_type}")
        sections.append("")
        sections.append(f"**Content**:")
        sections.append(message_content)
        sections.append("")

        relationship_score = sender.get("relationship_score", context.relationships.get(sender.get("agent_id", ""), 0))
        if relationship_score is not None:
            rel_desc = self._describe_relationship(relationship_score)
            sections.append(f"**Relationship**: {rel_desc} ({relationship_score:.2f})")
            sections.append("")

        sections.append("Now provide your response.")

        return "\n".join(sections)

    def get_recommended_tone(
        self,
        leadership_type: LeadershipType,
        message_type: str,
        relationship_score: float,
    ) -> ResponseTone:
        """Get recommended response tone based on context."""
        if relationship_score > 0.5:
            base_tone = ResponseTone.COOPERATIVE
        elif relationship_score < -0.3:
            base_tone = ResponseTone.FIRM
        else:
            base_tone = ResponseTone.NEUTRAL

        if leadership_type == LeadershipType.WANGDAO and base_tone == ResponseTone.NEUTRAL:
            return ResponseTone.CONCILIATORY
        elif leadership_type == LeadershipType.QIANGQUAN and base_tone == ResponseTone.COOPERATIVE:
            return ResponseTone.ASSERTIVE

        return base_tone


def get_message_description(message_type: str) -> str:
    """Get description for a message type."""
    for msg_type, desc in MESSAGE_DESCRIPTIONS.items():
        if msg_type.value == message_type:
            return desc
    return "Unknown message type"


def get_response_tone_description(tone: str) -> str:
    """Get description for a response tone."""
    descriptions = {
        ResponseTone.COOPERATIVE.value: "Friendly, collaborative",
        ResponseTone.ASSERTIVE.value: "Confident, firm",
        ResponseTone.NEUTRAL.value: "Balanced, objective",
        ResponseTone.CONCILIATORY.value: "Accommodating, seeking compromise",
        ResponseTone.FIRM.value: "Strong, unyielding",
        ResponseTone.HOSTILE.value: "Adversarial, confrontational",
    }
    return descriptions.get(tone, "Unknown tone")
