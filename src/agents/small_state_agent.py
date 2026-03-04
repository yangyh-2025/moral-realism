"""
Small state agent implementation for moral realism ABM system.

This module implements SmallStateAgent class which uses rule-based
decision making to evaluate great powers and align with most
attractive leadership type, validating the "moral leadership attracts support"
theory.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability


logger = logging.getLogger(__name__)


class SmallStateAction(Enum):
    """Action types available to small states."""

    ALIGN_FOLLOW = "align_follow"  # 结盟跟随
    NEUTRAL_OBSERVE = "neutral_observe"  # 中立观望
    SIDE_SELECTION = "side_selection"  # 选边站队
    DEFECT_SWITCH = "defect_switch"  # 倒戈转向
    NO_ALLIANCE_COALITION = "no_alliance_coalition"  # 不结盟联合
    MEDIATION = "mediation" 间调停
    COUNTER_RESPOND = "counter_respond"  # 反制/响应


class StrategicStance(Enum):
    """Strategic stance of a small state toward great powers."""

    ALIGNED = "aligned"  # Aligned with a specific great power
    NEUTRAL = "neutral"  # Maintains neutrality
    NON_ALIGNED = "non_aligned"  # Non-aligned movement
    SWING = "swing"  # Swing state, shifts alignment


@dataclass
class SmallStateAgent(Agent):
    """
    A small state agent that evaluates and follows great powers.

    This agent uses rule-based logic to assess great powers based on
    their leadership types and behaviors, validating the "moral leadership
    attracts support" theory of moral realism.

    Key principles:
    - Wangdao (Moral) leadership provides highest attraction (score 4)
    - Hegemon leadership provides medium-high attraction (score 3)
    - Qiangquan (Power-seeking) provides medium attraction (score 2)
    - Hunyong (Appeasement) provides lowest attraction (score 1)
    """

    # Strategic stance toward great powers
    strategic_stance: StrategicStance = StrategicStance.NEUTRAL

    # Current alignment
    aligned_with: Optional[str] = None  # agent_id of aligned great power

    # Leadership type preferences (higher = more attractive)
    leadership_preferences: Dict[str, float] = field(
        default_factory=lambda: {
            "wangdao": 4.0,  # Highest preference for moral leadership
            "hegemon": 3.0,  # Medium-high for traditional hegemon
            "qiangquan": 2.0,  # Medium for power-seeking
            "hunyong": 1.0,  # Lowest for appeasement
        }
    )

    # Assessment weights
    weights: Dict[str, float] = field(
        default_factory=lambda: {
            "leadership_type": 0.4,  # Weight for leadership type
            "behavior_score": 0.3,  # Weight for recent behavior
            "capability": 0.2,  # Weight for capability/power
            "relationship": 0.1,  # Weight for existing relationship
        }
    )

    # Minimum threshold for alignment
    alignment_threshold: float = 30.0  # Minimum score to align

    # Previous score for alignment comparison (for defection detection)
    previous_alignment_score: float = 0.0

    # Threshold for defection (when score drops by this much)
    defection_threshold: float = 15.0

    def __post_init__(self) -> None:
        """Initialize agent after dataclass initialization."""
        # Set agent type
        self.agent_type = AgentType.SMALL_STATE

        # Initialize leadership profile if not set
        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        # Initialize capability if not set
        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        # Initialize relations with self
        self.relations[self.agent_id] = 1.0

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a decision by assessing great powers and choosing alignment.

        Implements 7 behavior types:
        1. ALIGN_FOLLOW - Align and follow a great power
        2. NEUTRAL_OBSERVE - Maintain neutrality and observe
        3. SIDE_SELECTION - Choose a side in conflict
        4. DEFECT_SWITCH - Switch allegiance when conditions change
        5. NO_ALLIANCE_COALITION - Form non-aligned coalition
        6. MEDIATION - Mediate between great powers
        7. COUNTER_RESPOND - Counter/Respond to hostile actions

        Args:
            situation: Description of current situation.
            available_actions: List of actions available to agent.
            context: Additional context for decision-making, should include 'great_powers'.

        Returns:
            Dictionary containing decision and rationale.
        """
        if context is None:
            context = {}

        great_powers = context.get("great_powers", [])
        events = situation.get("events", [])
        in_crisis = situation.get("in_crisis", False)

        # Assess all great powers
        assessments = self._assess_great_powers(great_powers, context)

        # Determine action based on 7 behavior types
        action_type, rationale = self._determine_action_type(
            assessments, great_powers, situation, context
        )

        # Update stance based on action
        self._update_stance_from_action(action_type, assessments)

        decision = {
            "agent_id": self.agent_id,
            "action_type": action_type.value,
            "action": action_type.value,
            "target_agent_id": self.aligned_with,
            "rationale": rationale,
            "strategic_stance": self.strategic_stance.value,
            "assessments": assessments,
            "alignment_threshold": self.alignment_threshold,
            "in_crisis": in_crisis,
        }

        # Record decision in history
        self.add_history(
            "decision",
            f"Decided to {action_type.value}",
            metadata={
                "decision": decision,
                "situation": situation,
            },
        )

        logger.info(
            f"{self.name} decided to {action_type.value}. "
            f"Stance: {self.strategic_stance.value}, "
            f"Aligned with: {self.aligned_with or 'None'}"
        )

        return decision

    def _determine_action_type(
        self,
        assessments: List[Dict[str, Any]],
        great_powers: List[Dict[str, Any]],
        situation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> tuple[SmallStateAction, str]:
        """
        Determine action type based on assessments and situation.

        Implements the 7 behavior types selection logic.

        Args:
            assessments: List of great power assessments.
            great_powers: List of great powers.
            situation: Current situation.
            context: Additional context.

        Returns:
            Tuple of (action_type, rationale).
        """
        if not assessments:
            return SmallStateAction.NEUTRAL_OBSERVE, (
                "No great powers available to assess. "
                "Maintaining neutral observation."
            )

        in_crisis = situation.get("in_crisis", False)
        events = situation.get("events", [])

        # Find best assessment
        best = max(assessments, key=lambda x: x["score"])
        best_score = best["score"]

        # Check for deflection trigger (score dropped significantly)
        if self.aligned_with and self.previous_alignment_score > 0:
            if best_score < self.previous_alignment_score - self.defection_threshold:
                self.previous_alignment_score = best_score
                return SmallStateAction.DEFECT_SWITCH, (
                    f"Current alignment score decreased by "
                    f"{self.previous_alignment_score - best_score:.2f}, "
                    f"switching allegiance from previous great power to "
                    f"{best.get('name', 'new alignment')}. "
                    f"Previous policy no longer serves our interests."
                )

        self.previous_alignment_score = best_score

        # Behavior 1: ALIGN_FOLLOW - When best meets threshold
        if best_score >= self.alignment_threshold and not in_crisis:
            return SmallStateAction.ALIGN_FOLLOW, (
                f"Aligning with {best['name']} due to their "
                f"{best['leadership_type']} leadership (score: {best_score:.2f}). "
                f"Their moral conduct and behavior provide attractive benefits."
            )

        # Behavior 2: NEUTRAL_OBSERVE - When no great power meets threshold
        if best_score < self.alignment_threshold and not in_crisis:
            return SmallStateAction.NEUTRAL_OBSERVE, (
                f"Maintaining neutrality as no great power meets "
                f"alignment threshold (threshold: {self.alignment_threshold}, "
                f"best score: {best_score:.2f}). "
                f"Current great powers lack sufficient moral leadership "
                f"or attractive behavior."
            )

        # Behavior: Check for similar scores (coalition opportunity)
        if len(assessments) >= 2:
            scores = [a["score"] for a in assessments]
            score_variance = max(scores) - min(scores)
            if score_variance < 10 and len(assessments) > 2:
                return SmallStateAction.NO_ALLIANCE_COALITION, (
                    f"Multiple great powers have similar scores "
                    f"(variance: {score_variance:.2f}). "
                    f"Forming non-aligned coalition to balance influence."
                )

        # Behavior 3: SIDE_SELECTION - In crisis, choose a side
        if in_crisis:
            # Prefer Wangdao leader in crisis if available
            wangdao_assessment = next(
                (a for a in assessments if a["leadership_type"] == "wangdao"),
                None
            )
            if wangdao_assessment and wangdao_assessment["score"] >= 20:
                return SmallStateAction.SIDE_SELECTION, (
                    f"In crisis, selecting side with {wangdao_assessment['name']} "
                    f"due to their moral leadership and ability to provide security. "
                    f"Aligning with principled leadership in crisis."
                )
            else:
                return SmallStateAction.SIDE_SELECTION, (
                    f"In crisis, selecting side with {best['name']} "
                    f"(score: {best_score:.2f}) for security and support."
                )

        # Behavior 7: COUNTER_RESPOND - Respond to hostile actions
        for event in events[-3:]:
            if self._is_hostile_action(event, great_powers):
                sender_id = event.get("sender_id", "")
                relationship = self.get_relationship(sender_id)
                if relationship < -0.3:
                    # Hostile action from non-aligned power
                    sender = next(
                        (gp for gp in great_powers if gp.get("agent_id") == sender_id),
                        None
                    )
                    if sender:
                        return SmallStateAction.COUNTER_RESPOND, (
                            f"Responding to hostile action from {sender.get('name', 'unknown')}. "
                            f"Implementing countermeasures to protect national interests."
                        )

        # Default: NEUTRAL_OBSERVE
        return SmallStateAction.NEUTRAL_OBSERVE, (
            f"Maintaining neutral observation posture. "
            f"No compelling reason to align at this time."
        )

    def _is_hostile_action(
        self,
        event: Dict[str, Any],
        great_powers: List[Dict[str, Any]],
    ) -> bool:
        """
        Check if an event represents a hostile action.

        Args:
            event: Event to check.
            great_powers: List of great powers.

        Returns:
            True if event is hostile.
        """
        event_type = event.get("event_type", "").lower()

        hostile_actions = [
            "economic_sanction",
            "security_military",
            "military_escalation",
        ]

        return any(action in event_type for action in hostile_actions)

    def _update_stance_from_action(
        self,
        action_type: SmallStateAction,
        assessments: List[Dict[str, Any]],
    ) -> None:
        """
        Update strategic stance based on selected action type.

        Args:
            action_type: The selected action type.
            assessments: Great power assessments.
        """
        if action_type == SmallStateAction.ALIGN_FOLLOW:
            self.strategic_stance = StrategicStance.ALIGNED
            if assessments:
                best = max(assessments, key=lambda x: x["score"])
                self.aligned_with = best["agent_id"]
                self.set_relationship(best["agent_id"], 0.7)

        elif action_type == SmallStateAction.SIDE_SELECTION:
            self.strategic_stance = StrategicStance.ALIGNED
            if assessments:
                best = max(assessments, key=lambda x: x["score"])
                self.aligned_with = best["agent_id"]
                self.set_relationship(best["agent_id"], 0.6)

        elif action_type == SmallStateAction.DEFECT_SWITCH:
            self.strategic_stance = StrategicStance.SWING
            if assessments:
                best = max(assessments, key=lambda x: x["score"])
                self.aligned_with = best["agent_id"]
                # Reduce relationship with previous alignment
                for agent_id in self.relations.keys():
                    if agent_id != self.agent_id and agent_id != best["agent_id"]:
                        current = self.get_relationship(agent_id)
                        self.set_relationship(agent_id, current - 0.2)

        elif action_type == SmallStateAction.NO_ALLIANCE_COALITION:
            self.strategic_stance = StrategicStance.NON_ALIGNED
            self.aligned_with = None

        elif action_type == SmallStateAction.MEDIATION:
            self.strategic_stance = StrategicStance.NEUTRAL
            self.aligned_with = None

        elif action_type == SmallStateAction.COUNTER_RESPOND:
            if self.aligned_with:
                self.strategic_stance = StrategicStance.ALIGNED
            else:
                self.strategic_stance = StrategicStance.NEUTRAL

        else:  # NEUTRAL_OBSERVE
            self.strategic_stance = StrategicStance.NEUTRAL
            # Keep existing alignment or set to None
            pass

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Respond to a message from another agent.

        Args:
            sender_id: ID of sending agent.
            message: The message content and metadata.
            context: Additional context for response generation.

        Returns:
            Dictionary containing response.
        """
        if context is None:
            context = {}

        # Determine response based on alignment and relationship
        relationship_score = self.get_relationship(sender_id)

        # Check if sender is aligned great power
        is_aligned = self.aligned_with == sender_id

        message_type = message.get("type", "unknown")

        if is_aligned:
            # Friendly response to aligned power
            content = (
                f"We appreciate {message_type} from our partner. "
                f"We support your initiative and will cooperate accordingly."
            )
            message_type_response = "support"
            relationship_adjustment = 0.05
        elif relationship_score > 0.3:
            # Friendly but not aligned
            content = (
                f"We have received your {message_type} with interest. "
                f"We will consider it based on our national interests."
            )
            message_type_response = "consider"
            relationship_adjustment = 0.02
        elif relationship_score < -0.3:
            # Hostile response
            content = (
                f"We have received your {message_type}. "
                f"We must respectfully decline as it conflicts with our interests."
            )
            message_type_response = "decline"
            relationship_adjustment = -0.05
        else:
            # Neutral response
            content = (
                f"We have received your {message_type}. "
                f"We will evaluate it and respond in due course."
            )
            message_type_response = "acknowledge"
            relationship_adjustment = 0.0

        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": message_type_response,
            "aligned_with_sender": is_aligned,
            "relationship_score": relationship_score,
        }

        # Update relationship
        new = max(-1.0, min(1.0, relationship_score + relationship_adjustment))
        self.set_relationship(sender_id, new)

        # Record response in history
        self.add_history(
            "response",
            f"Responded to {sender_id}",
            metadata={"response": response, "original_message": message},
        )

        return response

    def _assess_great_powers(
        self,
        great_powers: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Assess all great powers and calculate attraction scores.

        Args:
            great_powers: List of great power agent dictionaries.
            context: Additional context.

        Returns:
            List of assessments with scores.
        """
        assessments = []

        for gp in great_powers:
            gp_id = gp.get("agent_id")
            if gp_id == self.agent_id:
                continue  # Skip self

            leadership_type = gp.get("leadership_type", "unknown")
            name = gp.get("name", gp_id)

            # Base score from leadership type preference
            leadership_score = self.leadership_preferences.get(leadership_type, 0) * 10

            # Score from recent behavior
            behavior_score = self._score_behavior(gp, leadership_type)

            # Score from capability (smaller states prefer moderate power)
            capability_score = self._score_capability(gp)

            # Score from existing relationship
            relationship_score = self._score_relationship(gp_id)

            # Calculate weighted total
            total_score = (
                leadership_score * self.weights["leadership_type"] +
                behavior_score * self.weights["behavior_score"] +
                capability_score * self.weights["capability"] +
                relationship_score * self.weights["relationship"]
            )

            assessments.append({
                "agent_id": gp_id,
                "name": name,
                "leadership_type": leadership_type,
                "leadership_score": leadership_score,
                "behavior_score": behavior_score,
                "capability_score": capability_score,
                "relationship_score": relationship_score,
                "score": total_score,
            })

        return assessments

    def _score_behavior(self, great_power: Dict[str, Any], leadership_type: str) -> float:
        """
        Score a great power's behavior based on leadership type and recent actions.

        Args:
            great_power: Great power agent dictionary.
            leadership_type: The leadership type of great power.

        Returns:
            Behavior score (0-100).
        """
        # Base score from leadership type moral characteristics
        leadership_moral_scores = {
            "wangdao": 90,  # Highest moral behavior
            "hegemon": 60,  # Moderate moral behavior
            "qiangquan": 30,  # Low moral behavior
            "hunyong": 50,  # Mixed moral behavior
        }

        base_score = leadership_moral_scores.get(leadership_type, 50)

        # Get recent behavior if available
        recent_behavior = great_power.get("recent_behavior", [])
        recent_actions = great_power.get("recent_actions", [])

        # Adjust score based on recent actions
        adjustment = 0

        for action in recent_actions[-5:]:  # Last 5 actions
            action_type = action.get("action_type", "").lower()

            # Positive actions
            if any(pos in action_type for pos in [
                "norm_proposal", "diplomatic_visit", "economic_aid"
            ]):
                adjustment += 5

            # Negative actions
            if any(neg in action_type for neg in [
                "economic_sanction", "military aggression"
            ]):
                adjustment -= 10

        # Adjust score based on behavior types
        for behavior in recent_behavior[-3:]:  # Last 3 behaviors
            if behavior.get("moral", False):
                adjustment += 8
            elif behavior.get("coercive", False):
                adjustment -= 12
            elif behavior.get("cooperative", False):
                adjustment += 6

        return max(0, min(100, base_score + adjustment))

    def _score_capability(self, great_power: Dict[str, Any]) -> float:
        """
        Score a great power's capability.

        Small states prefer powers that are strong enough to provide security
        but not overwhelmingly dominant (moderate power is attractive).

        Args:
            great_power: Great power agent dictionary.

        Returns:
            Capability score (0-100).
        """
        capability_index = great_power.get("capability_index", 50)

        # Sigmoid-like curve: highest attraction at moderate power levels
        # Very high power can be threatening, very low is insufficient
        # Optimal range: 60-80

        if capability_index < 60:
            # Below optimal: linear increase
            return (capability_index / 60) * 80
        elif capability_index <= 80:
            # Optimal range: high score
            return 100 - ((capability_index - 70) / 10) * 20
        else:
            # Above optimal: decreasing score
            return max(50, 100 - (capability_index - 80) * 1.5)

    def _score_relationship(self, agent_id: str) -> float:
        """
        Score based on existing relationship with agent.

        Args:
            agent_id: ID of agent.

        Returns:
            Relationship score (0-100).
        """
        # Relationship is -1 to 1, convert to 0-100
        current = self.get_relationship(agent_id)
        return (current + 1) * 50

    def _determine_best_alignment(
        self,
        assessments: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Determine best great power to align with.

        Args:
            assessments: List of great power assessments.

        Returns:
            Best assessment if available, None otherwise.
        """
        if not assessments:
            return None

        # Find highest scoring great power
        best = max(assessments, key=lambda x: x["score"])

        # Only return if it meets a minimum threshold
        if best["score"] >= self.alignment_threshold:
            return best

        return None

    def _calculate_risk_benefit_ratio(
        self,
        great_power_id: str,
        leadership_type: str,
        capability_index: float,
    ) -> float:
        """
        Calculate risk-benefit ratio for aligning with a great power.

        Args:
            great_power_id: ID of great power.
            leadership_type: Leadership type of great power.
            capability_index: Capability index of great power.

        Returns:
            Risk-benefit ratio (higher = more favorable).
        """
        # Get expected benefits and risks
        benefits = self.calculate_benefits(great_power_id, leadership_type)
        risks = self.calculate_risks(great_power_id, leadership_type)

        # Calculate average benefit
        avg_benefit = sum(benefits.values()) / len(benefits) if benefits else 50

        # Calculate average risk
        avg_risk = sum(risks.values()) / len(risks) if risks else 50

        # Risk-benefit ratio (benefit adjusted by capability)
        ratio = (avg_benefit - avg_risk * 0.5) * (capability_index / 100)

        return max(0, min(100, ratio))

    def get_alignment_summary(self) -> Dict[str, Any]:
        """
        Get a summary of small state's alignment.

        Returns:
            Dictionary with alignment information.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "strategic_stance": self.strategic_stance.value,
            "aligned_with": self.aligned_with,
            "alignment_threshold": self.alignment_threshold,
            "previous_alignment_score": self.previous_alignment_score,
        }

    def update_alignment(
        self,
        great_power_id: Optional[str],
        new_stance: Optional[StrategicStance] = None,
    ) -> None:
        """
        Update alignment with a great power.

        Args:
            great_power_id: ID of great power to align with (None for neutral).
            new_stance: New strategic stance (inferred from alignment if not provided).
        """
        self.aligned_with = great_power_id

        if great_power_id is None:
            self.strategic_stance = StrategicStance.NEUTRAL
        elif new_stance is not None:
            self.strategic_stance = new_stance
        else:
            self.strategic_stance = StrategicStance.ALIGNED

        # Record change
        self.add_history(
            "alignment_change",
            f"Changed alignment to {great_power_id or 'neutral'}",
            metadata={
                "previous_stance": self.strategic_stance.value,
                "new_stance": self.strategic_stance.value,
                "aligned_with": self.aligned_with,
            },
        )

    def calculate_benefits(
        self,
        great_power_id: str,
        leadership_type: str,
    ) -> Dict[str, float]:
        """
        Calculate expected benefits from aligning with a great power.

        Args:
            great_power_id: ID of great power.
            leadership_type: Leadership type of great power.

        Returns:
            Dictionary of expected benefits.
        """
        # Base benefits by leadership type
        base_benefits = {
            "wangdao": {
                "security": 80,
                "economic": 75,
                "political_support": 85,
                "moral_legitimacy": 90,
            },
            "hegemon": {
                "security": 90,
                "economic": 70,
                "political_support": 65,
                "moral_legitimacy": 50,
            },
            "qiangquan": {
                "security": 60,
                "economic": 80,
                "political_support": 40,
                "moral_legitimacy": 20,
            },
            "hunyong": {
                "security": 50,
                "economic": 55,
                "political_support": 60,
                "moral_legitimacy": 65,
            },
        }

        return base_benefits.get(leadership_type, {})

    def calculate_risks(
        self,
        great_power_id: str,
        leadership_type: str,
    ) -> Dict[str, float]:
        """
        Calculate expected risks from aligning with a great power.

        Args:
            great_power_id: ID of great power.
            leadership_type: Leadership type of great power.

        Returns:
            Dictionary of expected risks.
        """
        # Base risks by leadership type
        base_risks = {
            "wangdao": {
                "entanglement": 20,
                "sovereignty_loss": 15,
                "moral_compromise": 10,
                "conflict_involvement": 25,
            },
            "hegemon": {
                "entanglement": 60,
                "sovereignty_loss": 50,
                "moral_compromise": 40,
                "conflict_involvement": 70,
            },
            "qiangquan": {
                "entanglement": 75,
                "sovereignty_loss": 80,
                "moral_compromise": 85,
                "conflict_involvement": 90,
            },
            "hunyong": {
                "entanglement": 25,
                "sovereignty_loss": 20,
                "moral_compromise": 15,
                "conflict_involvement": 30,
            },
        }

        return base_risks.get(leadership_type, {})
