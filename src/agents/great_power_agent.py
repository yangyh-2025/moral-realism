"""
Great power agent implementation for the moral realism ABM system.

This module implements the GreatPowerAgent class which uses LLM-based
decision making driven by leadership type characteristics.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability, get_strategic_interests
from src.core.llm_engine import LLMEngine, LLMConfig
from src.prompts.leadership_prompts import (
    GreatPowerPromptBuilder,
    ActionType,
)


logger = logging.getLogger(__name__)


@dataclass
class Commitment:
    """Represents a commitment made by a great power."""

    commitment_id: str
    description: str
    target_agent_id: Optional[str] = None
    action_type: Optional[str] = None
    start_round: int = 0
    end_round: Optional[int] = None  # None means indefinite
    is_active: bool = True
    fulfillment: float = 0.0  # 0-1 scale of how well it's being fulfilled


@dataclass
class GreatPowerAgent(Agent):
    """
    A great power agent driven by LLM and leadership type.

    This agent uses LLM to make decisions reflecting its leadership type
    (Wangdao, Hegemon, Qiangquan, or Hunyong) and combines it with
    its capability level as a constant independent variable.
    """

    # LLM engine for decision making
    llm_engine: Optional[LLMEngine] = None
    prompt_builder: GreatPowerPromptBuilder = field(default_factory=GreatPowerPromptBuilder)

    # Commitments management
    commitments: List[Commitment] = field(default_factory=list)
    current_round: int = 0

    def __post_init__(self) -> None:
        """Initialize the agent after dataclass initialization."""
        # Set agent type
        self.agent_type = AgentType.GREAT_POWER

        # Initialize leadership profile if not set
        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        # Initialize capability if not set
        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        # Initialize LLM engine with default config
        if self.llm_engine is None:
            try:
                self.llm_engine = LLMEngine()
            except ValueError as e:
                logger.warning(f"Could not initialize LLM engine: {e}")
                self.llm_engine = None

        # Initialize relations with self
        self.relations[self.agent_id] = 1.0

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a decision using LLM-driven decision making.

        Args:
            situation: Description of the current situation.
            available_actions: List of actions available to the agent.
            context: Additional context for decision-making.

        Returns:
            Dictionary containing the decision and rationale.
        """
        if context is None:
            context = {}

        # Prepare context with required information
        context["situation"] = situation
        context["available_actions"] = available_actions

        # Check if LLM is available
        if self.llm_engine is None:
            return self._fallback_decision(available_actions, context)

        try:
            # Build system prompt
            function_definitions = self.prompt_builder.get_function_definitions()
            system_prompt = self.prompt_builder.build_system_prompt(
                self, function_definitions
            )

            # Build user prompt
            user_prompt = self.prompt_builder.build_user_prompt(self, context)

            # Call LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            response = self.llm_engine.function_call(
                messages=messages,
                functions=function_definitions,
                temperature=0.7,  # Lower temperature for more consistent decisions
            )

            # Parse function call result
            function_call = response.get("function_call")
            decision = self.prompt_builder.parse_function_call(function_call)

            # Validate decision
            decision = self._validate_decision(decision)

            # Add metadata
            decision["agent_id"] = self.agent_id
            decision["leadership_type"] = self.leadership_type.value
            decision["round"] = self.current_round
            decision["llm_usage"] = {
                "model": response.get("model"),
                "finish_reason": response.get("finish_reason"),
                "usage": response.get("usage"),
            }

            # Update commitments based on decision
            if decision["action_type"] != "no_action":
                self._update_commitments_from_decision(decision)

            # Record decision in history
            self.add_history(
                "decision",
                f"Decided to take action: {decision['action_type']}",
                metadata={
                    "decision": decision,
                    "situation": situation,
                },
            )

            logger.info(
                f"{self.name} decided on action: {decision['action_type']} "
                f"with rationale: {decision['rationale'][:100]}..."
            )

            return decision

        except Exception as e:
            logger.error(f"Error in LLM decision making for {self.name}: {e}")
            return self._fallback_decision(available_actions, context)

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Respond to a message from another agent.

        Args:
            sender_id: ID of the sending agent.
            message: The message content and metadata.
            context: Additional context for response generation.

        Returns:
            Dictionary containing the response.
        """
        if context is None:
            context = {}

        # Get sender information if available in context
        sender = context.get("agents", {}).get(sender_id, {"name": sender_id})

        # Check if LLM is available
        if self.llm_engine is None:
            return self._fallback_response(sender_id, message, context)

        try:
            # Build response prompt
            prompt = self.prompt_builder.build_response_prompt(
                self, sender, message, context
            )

            # Get system prompt
            system_prompt = f"""You are {self.name} ({self.name_zh}), a {self.leadership_profile.name_zh} great power.

Respond to the following message based on your leadership characteristics.
"""

            # Call LLM
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            response = self.llm_engine.chat_completion(
                messages=messages,
                temperature=0.8,  # Higher temperature for more varied responses
            )

            content = response.get("content", "")
            message_type = message.get("type", "unknown")

            response_data = {
                "sender_id": self.agent_id,
                "receiver_id": sender_id,
                "content": content,
                "message_type": message_type,
                "leadership_type": self.leadership_type.value,
                "round": self.current_round,
            }

            # Record response in history
            self.add_history(
                "response",
                f"Responded to {sender_id}: {content[:100]}...",
                metadata={
                    "response": response_data,
                    "original_message": message,
                },
            )

            # Update relationship based on interaction
            self._update_relationship_from_interaction(sender_id, message, response_data)

            return response_data

        except Exception as e:
            logger.error(f"Error in LLM response generation for {self.name}: {e}")
            return self._fallback_response(sender_id, message, context)

    def _validate_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the decision against leadership profile constraints.

        Args:
            decision: The decision to validate.

        Returns:
            Validated decision (may be modified).
        """
        action_type = decision.get("action_type", "no_action")

        # Check if action is prohibited
        if self.leadership_profile:
            prohibited = self.leadership_profile.prohibited_actions

            # Check both exact match and partial match
            is_prohibited = any(
                action_type in prohibited or
                prohibited_item in action_type
                for prohibited_item in prohibited
            )

            if is_prohibited:
                logger.warning(
                    f"{self.name} attempted prohibited action: {action_type}. "
                    f"Falling back to no_action."
                )
                decision["action_type"] = "no_action"
                decision["rationale"] = (
                    f"Original action '{action_type}' is prohibited by leadership type. "
                    "Taking no action instead."
                )

        # Ensure priority is valid
        if "priority" not in decision or decision["priority"] not in ["high", "medium", "low"]:
            decision["priority"] = "medium"

        # Ensure resource allocation is valid
        if "resource_allocation" not in decision:
            decision["resource_allocation"] = 50
        else:
            decision["resource_allocation"] = max(0, min(100, decision["resource_allocation"]))

        return decision

    def _fallback_decision(
        self,
        available_actions: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a fallback decision when LLM is unavailable.

        Args:
            available_actions: List of available actions.
            context: Context information.

        Returns:
            Fallback decision.
        """
        # Default to prioritized actions if available
        prioritized = (
            self.leadership_profile.prioritized_actions
            if self.leadership_profile
            else []
        )

        # Select action based on leadership type
        if self.leadership_type == LeadershipType.WANGDAO:
            action_type = ActionType.DIPLOMATIC_VISIT.value
            rationale = "Prioritizing diplomatic engagement as Wangdao leader"
        elif self.leadership_type == LeadershipType.HEGEMON:
            action_type = ActionType.SECURITY_ALLIANCE.value
            rationale = "Strengthening alliances to maintain hegemonic position"
        elif self.leadership_type == LeadershipType.QIANGQUAN:
            action_type = ActionType.ECONOMIC_TRADE.value
            rationale = "Maximizing economic benefits and power"
        else:  # HUNYONG
            action_type = ActionType.NO_ACTION.value
            rationale = "Avoiding confrontation through inaction"

        return {
            "agent_id": self.agent_id,
            "action_type": action_type,
            "target_agent_id": None,
            "rationale": rationale + " (fallback decision - LLM unavailable)",
            "moral_consideration": "Fallback decision",
            "resource_allocation": 50,
            "priority": "medium",
            "leadership_type": self.leadership_type.value,
            "round": self.current_round,
            "fallback": True,
        }

    def _fallback_response(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate a fallback response when LLM is unavailable.

        Args:
            sender_id: ID of the sender.
            message: The message.
            context: Context information.

        Returns:
            Fallback response.
        """
        content = f"Thank you for your message. We will consider your proposal."

        if self.leadership_type == LeadershipType.WANGDAO:
            content = (
                "We appreciate your message and will approach this matter "
                "with consideration for all parties involved."
            )
        elif self.leadership_type == LeadershipType.HEGEMON:
            content = (
                "We have received your message. Our response will be guided "
                "by our strategic interests and alliance commitments."
            )
        elif self.leadership_type == LeadershipType.QIANGQUAN:
            content = (
                "We have noted your message. We will respond based on "
                "our national interests."
            )

        return {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": message.get("type", "unknown"),
            "leadership_type": self.leadership_type.value,
            "round": self.current_round,
            "fallback": True,
        }

    def _update_commitments_from_decision(self, decision: Dict[str, Any]) -> None:
        """
        Update commitments based on a new decision.

        Args:
            decision: The decision to process.
        """
        action_type = decision.get("action_type")

        # Create commitment for significant actions
        if action_type in [
            ActionType.DIPLOMATIC_ALLIANCE.value,
            ActionType.SECURITY_ALLIANCE.value,
            ActionType.NORM_PROPOSAL.value,
        ]:
            commitment = Commitment(
                commitment_id=f"{self.agent_id}_{self.current_round}_{action_type}",
                description=decision.get("rationale", "")[:200],
                target_agent_id=decision.get("target_agent_id"),
                action_type=action_type,
                start_round=self.current_round,
                is_active=True,
            )
            self.commitments.append(commitment)

    def _update_relationship_from_interaction(
        self,
        sender_id: str,
        message: Dict[str, Any],
        response: Dict[str, Any],
    ) -> None:
        """
        Update relationship based on interaction.

        Args:
            sender_id: ID of the sender.
            message: The incoming message.
            response: The response sent.
        """
        # Simple logic: positive interactions increase relationship
        message_type = message.get("type", "unknown")

        # Default small positive adjustment for engagement
        adjustment = 0.05

        # Adjust based on message type
        if "threat" in message_type.lower() or "sanction" in message_type.lower():
            adjustment = -0.1
        elif "cooperation" in message_type.lower() or "alliance" in message_type.lower():
            adjustment = 0.15

        current_score = self.get_relationship(sender_id)
        new_score = max(-1.0, min(1.0, current_score + adjustment))
        self.set_relationship(sender_id, new_score)

    def get_active_commitments(self) -> List[Commitment]:
        """
        Get all currently active commitments.

        Returns:
            List of active commitments.
        """
        return [c for c in self.commitments if c.is_active]

    def get_objective_interests(self) -> List[str]:
        """
        Get the objective strategic interests based on capability tier.

        Returns:
            List of strategic interests.
        """
        if self.capability is None:
            return []

        tier = self.capability.get_tier()
        return get_strategic_interests(tier)

    def advance_round(self) -> None:
        """Advance to the next simulation round."""
        self.current_round += 1

        # Update commitment status based on round
        for commitment in self.commitments:
            if commitment.end_round is not None and self.current_round > commitment.end_round:
                commitment.is_active = False

    def get_decision_summary(self) -> Dict[str, Any]:
        """
        Get a summary of recent decisions.

        Returns:
            Dictionary with decision statistics.
        """
        decisions = self.get_history("decision")

        if not decisions:
            return {"total_decisions": 0}

        action_counts = {}
        for entry in decisions:
            action = entry.metadata.get("decision", {}).get("action_type", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1

        return {
            "total_decisions": len(decisions),
            "action_distribution": action_counts,
            "recent_decision": decisions[-1].metadata.get("decision") if decisions else None,
        }
