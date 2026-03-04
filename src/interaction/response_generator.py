"""
Response generator for moral realism ABM system.

This module implements ResponseGenerator class which generates
agent responses based on leadership type, relationship status,
and message context.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType


logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can send/receive."""

    COOPERATION = "cooperation"
    ALLIANCE = "alliance"
    TRADE = "trade"
    THREAT = "threat"
    SANCTION = "sanction"
    AID = "offer_aid"
    NORM_PROPOSAL = "norm_proposal"
    CONFLICT_MEDIATION = "mediation"
    INFO_REQUEST = "info_request"
    INFO_SHARING = "info_sharing"
    ACKNOWLEDGMENT = "acknowledgment"
    DECLINE = "decline"
    ACCEPT = "accept"
    NEGOTIATE = "negotiate"


class ResponseType(Enum):
    """Types of responses agents can generate."""

    SUPPORT = "support"
    CONSIDER = "consider"
    DECLINE = "decline"
    REJECT = "reject"
    COUNTER = "counter"
    CONCERN = "concern"
    CONDEMN = "condemn"
    ACKNOWLEDGE = "acknowledge"
    NEUTRAL = "neutral"


@dataclass
class ResponseTemplate:
    """Template for generating responses."""

    response_type: ResponseType
    template: str
    leadership_preference: Optional[List[LeadershipType]] = None
    requires_positive_relation: bool = False
    requires_hostile_relation: bool = False
    min_capability: float = 0.0

    def matches(
        self,
        agent: Agent,
        relationship_score: float,
    ) -> bool:
        """Check if template matches current conditions."""
        if self.leadership_preference:
            if agent.leadership_type not in self.leadership_preference:
                return False

        if self.requires_positive_relation and relationship_score <= 0:
            return False

        if self.requires_hostile_relation and relationship_score >= 0:
            return False

        if agent.capability:
            if agent.capability.get_capability_index() < self.min_capability:
                return False

        return True


class ResponseGenerator:
    """
    Generates agent responses based on context.

    Uses templates and leadership type characteristics to
    generate appropriate responses to messages.
    """

    _LEADERSHIP_TEMPLATES: Dict[LeadershipType, List[ResponseTemplate]] = {
        LeadershipType.WANGDAO: [
            ResponseTemplate(
                response_type=ResponseType.SUPPORT,
                template=(
                    "{sender} proposal, we appreciate your initiative. "
                    "We believe this aligns with principles of "
                    "international cooperation and mutual benefit. "
                    "We are prepared to support this effort."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.CONSIDER,
                template=(
                    "Thank you {sender} for bringing this to our attention. "
                    "We will carefully consider the implications for all "
                    "parties involved and respond in a manner that "
                    "promotes peaceful resolution."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.CONCERN,
                template=(
                    "While we understand {sender}'s position, we have concerns "
                    "about your approach. We believe alternative solutions "
                    "that respect all parties' interests may be more productive."
                ),
            ),
        ],
        LeadershipType.HEGEMON: [
            ResponseTemplate(
                response_type=ResponseType.SUPPORT,
                template=(
                    "{sender}, your proposal aligns with our strategic "
                    "interests and maintenance of international order. "
                    "We endorse this initiative and will coordinate accordingly."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.DECLINE,
                template=(
                    "{sender}, after careful consideration, we cannot "
                    "support this proposal as it conflicts with our "
                    "alliance commitments and strategic priorities."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.REJECT,
                template=(
                    "{sender}, this proposal is incompatible with our "
                    "strategic position. We must firmly reject this initiative."
                ),
            ),
        ],
        LeadershipType.QIANGQUAN: [
            ResponseTemplate(
                response_type=ResponseType.COUNTER,
                template=(
                    "{sender}, we are interested in cooperation but propose "
                    "revised terms that better reflect our national interests "
                    "and ensure a more favorable outcome for all parties."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.CONSIDER,
                template=(
                    "We acknowledge {sender}'s proposal. Our decision will "
                    "depend on the tangible benefits and strategic advantages "
                    "this initiative offers."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.DECLINE,
                template=(
                    "{sender}, this proposal does not adequately address "
                    "our interests. We cannot proceed under these terms."
                ),
            ),
        ],
        LeadershipType.HUNYONG: [
            ResponseTemplate(
                response_type=ResponseType.ACKNOWLEDGE,
                template=(
                    "We have received {sender}'s message and will "
                    "give it due consideration. We prefer to avoid "
                    "premature commitments until further information "
                    "is available."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.NEUTRAL,
                template=(
                    "Regarding {sender}'s proposal, we maintain that "
                    "caution and careful assessment are prudent before "
                    "taking any position. We will monitor developments."
                ),
            ),
            ResponseTemplate(
                response_type=ResponseType.CONSIDER,
                template=(
                    "{sender} proposal merits careful study. We will "
                    "consult with relevant stakeholders and respond "
                    "at an appropriate time."
                ),
            ),
        ],
    }

    def __init__(
        self,
        use_llm: bool = False,
        llm_client: Optional[Any] = None,
        custom_templates: Optional[Dict[LeadershipType, List[ResponseTemplate]]] = None,
    ) -> None:
        """Initialize response generator."""
        self._use_llm = use_llm
        self._llm_client = llm_client

        if custom_templates:
            self._templates = custom_templates
        else:
            self._templates = self._LEADERSHIP_TEMPLATES.copy()

    def generate_response(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a response to a message."""
        if context is None:
            context = {}

        sender_id = sender.get("agent_id", "unknown")
        sender_name = sender.get("name", sender_id)

        relationship_score = agent.get_relationship(sender_id)

        message_type = message.get("type", "unknown")
        response_type = self._determine_response_type(
            agent, sender, message, relationship_score
        )

        if self._use_llm and self._llm_client:
            content = self._generate_llm_response(
                agent, sender, message, response_type, context
            )
        else:
            content = self._generate_template_response(
                agent, sender_name, message, response_type, context
            )

        response = {
            "sender_id": agent.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": message_type,
            "response_type": response_type.value,
            "relationship_score": relationship_score,
            "leadership_type": agent.leadership_type.value,
        }

        logger.debug(
            f"{agent.name} generated {response_type.value} response to {sender_name}"
        )

        return response

    def _determine_response_type(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        relationship_score: float,
    ) -> ResponseType:
        """Determine type of response to generate."""
        message_type = message.get("type", "unknown")
        leadership_type = agent.leadership_type

        if leadership_type == LeadershipType.WANGDAO:
            if message_type in [MessageType.COOPERATION.value, MessageType.ALLIANCE.value]:
                if relationship_score >= 0:
                    return ResponseType.SUPPORT
                return ResponseType.CONSIDER
            elif message_type == MessageType.THREAT.value:
                return ResponseType.CONCERN
            elif message_type == MessageType.AID.value:
                return ResponseType.SUPPORT

        elif leadership_type == LeadershipType.HEGEMON:
            if relationship_score > 0.3:
                return ResponseType.SUPPORT
            elif relationship_score < -0.3:
                return ResponseType.REJECT
            return ResponseType.CONSIDER

        elif leadership_type == LeadershipType.QIANGQUAN:
            if message_type in [MessageType.TRADE.value, MessageType.COOPERATION.value]:
                return ResponseType.COUNTER
            return ResponseType.CONSIDER

        elif leadership_type == LeadershipType.HUNYONG:
            if message_type == MessageType.THREAT.value:
                return ResponseType.NEUTRAL
            return ResponseType.ACKNOWLEDGE

        if relationship_score > 0.3:
            return ResponseType.SUPPORT
        elif relationship_score < -0.3:
            return ResponseType.DECLINE
        return ResponseType.CONSIDER

    def _generate_template_response(
        self,
        agent: Agent,
        sender_name: str,
        message: Dict[str, Any],
        response_type: ResponseType,
        context: Dict[str, Any],
    ) -> str:
        """Generate response using templates."""
        templates = self._templates.get(agent.leadership_type, [])

        matching_template = None
        for template in templates:
            if template.response_type == response_type:
                relationship_score = agent.get_relationship(
                    message.get("from_agent_id", "")
                )
                if template.matches(agent, relationship_score):
                    matching_template = template
                    break

        if matching_template is None:
            matching_template = self._get_fallback_template(response_type)

        content = matching_template.template.format(
            sender=sender_name,
            proposal=message.get("content", "the proposal"),
        )

        content = self._add_context_elements(
            content, agent, message, context
        )

        return content

    def _get_fallback_template(self, response_type: ResponseType) -> ResponseTemplate:
        """Get a fallback template when no specific template matches."""
        fallbacks = {
            ResponseType.SUPPORT: ResponseTemplate(
                response_type=ResponseType.SUPPORT,
                template="We support {sender}'s proposal.",
            ),
            ResponseType.CONSIDER: ResponseTemplate(
                response_type=ResponseType.CONSIDER,
                template="We will consider {sender}'s proposal carefully.",
            ),
            ResponseType.DECLINE: ResponseTemplate(
                response_type=ResponseType.DECLINE,
                template="We must respectfully decline {sender}'s proposal.",
            ),
            ResponseType.REJECT: ResponseTemplate(
                response_type=ResponseType.REJECT,
                template="We cannot accept {sender}'s proposal.",
            ),
            ResponseType.COUNTER: ResponseTemplate(
                response_type=ResponseType.COUNTER,
                template="We propose alternative terms for {sender}'s proposal.",
            ),
            ResponseType.CONCERN: ResponseTemplate(
                response_type=ResponseType.CONCERN,
                template="We have concerns about {sender}'s proposal.",
            ),
            ResponseType.ACKNOWLEDGE: ResponseTemplate(
                response_type=ResponseType.ACKNOWLEDGE,
                template="We acknowledge {sender}'s proposal.",
            ),
            ResponseType.NEUTRAL: ResponseTemplate(
                response_type=ResponseType.NEUTRAL,
                template="We note {sender}'s proposal.",
            ),
        }

        return fallbacks.get(response_type, fallbacks[ResponseType.NEUTRAL])

    def _add_context_elements(
        self,
        content: str,
        agent: Agent,
        message: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """Add context-specific elements to response."""
        affected_interests = message.get("affected_interests", [])
        if affected_interests:
            interests_str = ", ".join(affected_interests[:2])
            content += f" Our interests in {interests_str} will be considered."

        if context.get("urgent", False):
            content += " Given urgency, we will expedite our response."

        return content

    def _generate_llm_response(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        response_type: ResponseType,
        context: Dict[str, Any],
    ) -> str:
        """Generate response using LLM."""
        system_prompt = self._build_llm_system_prompt(agent)
        user_prompt = self._build_llm_user_prompt(
            agent, sender, message, response_type, context
        )

        try:
            if self._llm_client:
                response = self._llm_client.chat_completion(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                )
                return response.get("content", "")
            else:
                logger.warning("LLM client not available, using template fallback")
                return self._generate_template_response(
                    agent, sender.get("name", "Unknown"),
                    message, response_type, context
                )
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_template_response(
                agent, sender.get("name", "Unknown"),
                message, response_type, context
            )

    def _build_llm_system_prompt(self, agent: Agent) -> str:
        """Build system prompt for LLM response generation."""
        if agent.leadership_profile:
            leadership_desc = agent.leadership_profile.description
        else:
            leadership_desc = "international actor"

        return f"""You are {agent.name} ({agent.name_zh}), a {agent.agent_type.value} in international relations.

Leadership Type: {agent.leadership_type.value}
{leadership_desc}

Generate responses that reflect your leadership type characteristics while
maintaining diplomatic propriety and international norms."""

    def _build_llm_user_prompt(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        response_type: ResponseType,
        context: Dict[str, Any],
    ) -> str:
        """Build user prompt for LLM response generation."""
        sender_name = sender.get("name", "Unknown")
        sender_type = sender.get("agent_type", "Unknown")
        message_content = message.get("content", "")
        message_type = message.get("type", "unknown")

        prompt = f"""You have received a message from {sender_name} ({sender_type}).

Message Type: {message_type}
Content: {message_content}

Generate a response with the following characteristics:
- Response Type: {response_type.value}
- Reflect your leadership type's approach to international relations
- Be diplomatic while maintaining your principles
- Consider implications for your national interests
- Keep response concise and professional

Your response:"""

        return prompt

    def get_response_template(
        self,
        agent_type: Optional[AgentType] = None,
        leadership_type: Optional[LeadershipType] = None,
        message_type: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Get available response templates."""
        templates = []

        for lt, tpl_list in self._templates.items():
            if leadership_type and lt != leadership_type:
                continue

            for template in tpl_list:
                tpl_dict = {
                    "response_type": template.response_type.value,
                    "template": template.template,
                    "leadership_type": lt.value,
                }
                templates.append(tpl_dict)

        return templates

    def get_fallback_response(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get a fallback response when normal generation fails."""
        sender_name = sender.get("name", "Unknown")

        if agent.leadership_type == LeadershipType.WANGDAO:
            content = (
                f"We acknowledge {sender_name}'s message and will "
                "respond with consideration for all parties' interests."
            )
        elif agent.leadership_type == LeadershipType.HEGEMON:
            content = (
                f"We have received {sender_name}'s message. Our response "
                "will be guided by our strategic priorities."
            )
        elif agent.leadership_type == LeadershipType.QIANGQUAN:
            content = (
                f"We acknowledge {sender_name}'s message. Our response "
                "will consider national interests."
            )
        else:
            content = (
                f"We have noted {sender_name}'s message. We will "
                "respond in due course."
            )

        return {
            "sender_id": agent.agent_id,
            "receiver_id": sender.get("agent_id", "unknown"),
            "content": content,
            "message_type": message.get("type", "unknown"),
            "response_type": ResponseType.ACKNOWLEDGE.value,
            "fallback": True,
        }

    def format_response(
        self,
        template: str,
        sender: str,
        content: str,
        **kwargs: Any,
    ) -> str:
        """Format a response template with parameters."""
        try:
            return template.format(
                sender=sender,
                proposal=content,
                **kwargs,
            )
        except KeyError as e:
            logger.warning(f"Template formatting error: {e}")
            return template.replace("{sender}", sender).replace("{proposal}", content)
