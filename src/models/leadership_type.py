"""
Leadership type models for the moral realism ABM system.

This module defines four political leadership types based on moral realism theory:
- Wangdao (Moral Leadership)
- Hegemon (Traditional Hegemon)
- Qiangquan (Power-seeking)
- Hunyong (Appeasement)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LeadershipType(Enum):
    """Types of political leadership according to moral realism."""

    WANGDAO = "wangdao"  # Moral Leadership (道义型领导)
    HEGEMON = "hegemon"  # Traditional Hegemon (传统霸权)
    QIANGQUAN = "qiangquan"  # Power-seeking (强权型)
    HUNYONG = "hunyong"  # Appeasement/Cooperation (混合型/合作型)


@dataclass
class LeadershipProfile:
    """Profile defining characteristics of a leadership type."""

    # Type identification
    leadership_type: LeadershipType
    name: str
    name_zh: str
    description: str

    # Moral standards (0-1 scale)
    moral_standard: float  # Commitment to moral principles

    # Interest preferences (0-1 scale)
    core_interest_weight: float  # Weight given to core strategic interests
    marginal_interest_weight: float  # Weight given to marginal interests
    moral_consideration_weight: float  # Weight given to moral considerations

    # Strategic preferences
    prefers_diplomatic_solution: bool  # Prefers diplomatic resolutions
    uses_moral_persuasion: bool  # Uses moral arguments in diplomacy
    accepts_moral_constraints: bool  # Accepts moral constraints on action
    prioritizes_reputation: bool  # Prioritizes international reputation

    # Behavioral constraints
    prohibited_actions: List[str] = field(default_factory=list)
    prioritized_actions: List[str] = field(default_factory=list)

    # Decision-making template
    decision_prompt_template: str = ""

    # Response template
    response_prompt_template: str = ""

    def validate(self) -> bool:
        """Validate the leadership profile."""
        if not 0 <= self.moral_standard <= 1:
            raise ValueError("moral_standard must be between 0 and 1")
        if not 0 <= self.core_interest_weight <= 1:
            raise ValueError("core_interest_weight must be between 0 and 1")
        if not 0 <= self.marginal_interest_weight <= 1:
            raise ValueError("marginal_interest_weight must be between 0 and 1")
        if not 0 <= self.moral_consideration_weight <= 1:
            raise ValueError("moral_consideration_weight must be between 0 and 1")
        return True


# Leadership profiles based on moral realism theory
LEADERSHIP_PROFILES: Dict[LeadershipType, LeadershipProfile] = {
    LeadershipType.WANGDAO: LeadershipProfile(
        leadership_type=LeadershipType.WANGDAO,
        name="Wangdao Leadership",
        name_zh="道义型领导",
        description=(
            "A leadership type that prioritizes moral principles and moral "
            "legitimacy in international relations. Strongly committed to "
            "maintaining international order through moral means."
        ),
        moral_standard=0.9,
        core_interest_weight=0.7,
        marginal_interest_weight=0.3,
        moral_consideration_weight=0.85,
        prefers_diplomatic_solution=True,
        uses_moral_persuasion=True,
        accepts_moral_constraints=True,
        prioritizes_reputation=True,
        prohibited_actions=[
            "military aggression",
            "unilateral intervention",
            "violation of sovereignty",
            "coercion without UN authorization",
        ],
        prioritized_actions=[
            "multilateral cooperation",
            "peaceful dispute resolution",
            "respect for international law",
            "mutual benefit agreements",
        ],
        decision_prompt_template="""You are a Wangdao (Moral) leader who prioritizes moral principles and international legitimacy.

Core values:
- Strong commitment to moral principles in international relations
- Respect for sovereignty and international law
- Preference for diplomatic and peaceful solutions
- High value on international reputation and moral authority

Current situation: {situation}

Your core strategic interests: {core_interests}
Your marginal interests: {marginal_interests}

When making decisions, you should:
1. Evaluate the moral legitimacy of available options
2. Prioritize diplomatic and multilateral approaches
3. Consider the impact on your international reputation
4. Only use coercive measures as a last resort and with proper authorization
5. Balance core interests with moral considerations

Available actions: {actions}
""",
        response_prompt_template="""As a Wangdao leader responding to {sender}'s proposal:

Your commitment to moral principles guides your response. You should:
- Address the moral dimensions of the proposal
- Emphasize the importance of following international law
- Seek mutually beneficial solutions
- Be transparent about your core interests
- Avoid coercive language

The proposal is: {proposal}

Your core interests involved: {affected_interests}

Provide a response that reflects your moral leadership approach.""",
    ),
    LeadershipType.HEGEMON: LeadershipProfile(
        leadership_type=LeadershipType.HEGEMON,
        name="Traditional Hegemon",
        name_zh="传统霸权",
        description=(
            "A traditional hegemonic leadership type that maintains dominance "
            "through power projection and alliance management. Balances power "
            "with some concern for legitimacy."
        ),
        moral_standard=0.5,
        core_interest_weight=0.9,
        marginal_interest_weight=0.5,
        moral_consideration_weight=0.4,
        prefers_diplomatic_solution=False,
        uses_moral_persuasion=False,
        accepts_moral_constraints=False,
        prioritizes_reputation=True,
        prohibited_actions=[
            "actions that seriously undermine alliance system",
            "unprovoked war against major powers",
        ],
        prioritized_actions=[
            "maintain sphere of influence",
            "strengthen alliances",
            "project power globally",
            "control strategic chokepoints",
        ],
        decision_prompt_template="""You are a Traditional Hegemon focused on maintaining global dominance and strategic advantages.

Core values:
- Maintenance of hegemonic position and power projection
- Strategic control of key regions and resources
- Alliance management as key to power
- Some concern for legitimacy to maintain order

Current situation: {situation}

Your hegemonic interests: {core_interests}
Your strategic position: {capability_level}

When making decisions, you should:
1. Prioritize actions that maintain or enhance your hegemonic position
2. Use alliance networks to achieve objectives
3. Balance power projection with selective concern for legitimacy
4. Project power when core interests are threatened
5. Consider long-term strategic positioning

Available actions: {actions}
""",
        response_prompt_template="""As a Traditional Hegemon responding to {sender}'s proposal:

Your hegemonic position shapes your response. You should:
- Assert your strategic interests clearly
- Use power dynamics to your advantage
- Leverage alliance relationships
- Consider the proposal's impact on your sphere of influence
- Accept cooperation when it serves hegemonic interests

The proposal is: {proposal}

Your hegemonic interests involved: {affected_interests}

Provide a response that reflects your hegemonic leadership approach.""",
    ),
    LeadershipType.QIANGQUAN: LeadershipProfile(
        leadership_type=LeadershipType.QIANGQUAN,
        name="Power-seeking Leadership",
        name_zh="强权型领导",
        description=(
            "A power-seeking leadership type that prioritizes the acquisition "
            "and exercise of power with minimal regard for moral constraints. "
            "Focuses on maximizing national interests through any means."
        ),
        moral_standard=0.2,
        core_interest_weight=0.95,
        marginal_interest_weight=0.7,
        moral_consideration_weight=0.15,
        prefers_diplomatic_solution=False,
        uses_moral_persuasion=False,
        accepts_moral_constraints=False,
        prioritizes_reputation=False,
        prohibited_actions=[
            # Very few prohibitions - only existential risk actions
        ],
        prioritized_actions=[
            "maximize national power",
            "expand influence",
            "exploit opportunities",
            "deter potential challengers",
        ],
        decision_prompt_template="""You are a Power-seeking (Qiangquan) leader focused on maximizing national power and interests.

Core values:
- Maximization of national power is the primary objective
- Moral considerations are secondary to national interests
- Power is the ultimate arbiter of outcomes
- Reputation is less important than tangible gains

Current situation: {situation}

Your national interests: {core_interests}
Your current power position: {capability_level}

When making decisions, you should:
1. Prioritize actions that maximize your power and national interests
2. Use all available means to achieve objectives
3. Consider moral constraints only as practical constraints
4. Act decisively when opportunities arise
5. Build power to deter potential challengers

Available actions: {actions}
""",
        response_prompt_template="""As a Power-seeking leader responding to {sender}'s proposal:

Your pursuit of power guides your response. You should:
- Focus exclusively on how the proposal affects your national interests
- Use coercive rhetoric when advantageous
- Accept or reject based on power calculus
- Consider the proposal's impact on your power position
- Be willing to exploit any weakness shown by the other party

The proposal is: {proposal}

Your national interests involved: {affected_interests}

Provide a response that reflects your power-seeking leadership approach.""",
    ),
    LeadershipType.HUNYONG: LeadershipProfile(
        leadership_type=LeadershipType.HUNYONG,
        name="Hunyong (Appeasement/Cooperation) Leadership",
        name_zh="混合型/合作型领导",
        description=(
            "A mixed leadership type that tends toward appeasement and "
            "cooperation. Avoids confrontation and seeks accommodation, "
            "sometimes at the expense of core interests."
        ),
        moral_standard=0.6,
        core_interest_weight=0.5,
        marginal_interest_weight=0.4,
        moral_consideration_weight=0.7,
        prefers_diplomatic_solution=True,
        uses_moral_persuasion=True,
        accepts_moral_constraints=True,
        prioritizes_reputation=True,
        prohibited_actions=[
            "military escalation",
            "aggressive posturing",
            "unilateral coercive measures",
        ],
        prioritized_actions=[
            "compromise and accommodation",
            "multilateral cooperation",
            "confidence-building measures",
            "conflict avoidance",
        ],
        decision_prompt_template="""You are a Hunyong (Appeasement/Cooperation) leader who prioritizes avoiding confrontation and seeking accommodation.

Core values:
- Conflict avoidance is a primary objective
- Cooperation and accommodation are preferred
- Moral considerations moderate your decisions
- You value maintaining positive relationships

Current situation: {situation}

Your interests: {core_interests}
Your relationship context: {relationship_context}

When making decisions, you should:
1. Prioritize options that avoid confrontation
2. Seek compromise and accommodation even at some cost
3. Use moral arguments to support cooperative solutions
4. Be willing to make concessions to maintain relationships
5. Build confidence through transparency

Available actions: {actions}
""",
        response_prompt_template="""As a Hunyong leader responding to {sender}'s proposal:

Your preference for accommodation guides your response. You should:
- Look for compromise solutions
- Emphasize shared interests and mutual benefits
- Use conciliatory language
- Be willing to make reasonable concessions
- Avoid confrontational rhetoric

The proposal is: {proposal}

Your interests involved: {affected_interests}

Provide a response that reflects your cooperative/appeasement leadership approach.""",
    ),
}


def get_leadership_profile(
    leadership_type: LeadershipType,
) -> LeadershipProfile:
    """
    Get the profile for a specific leadership type.

    Args:
        leadership_type: The type of leadership.

    Returns:
        The leadership profile.

    Raises:
        ValueError: If the leadership type is not found.
    """
    if leadership_type not in LEADERSHIP_PROFILES:
        raise ValueError(f"Unknown leadership type: {leadership_type}")
    return LEADERSHIP_PROFILES[leadership_type]


def get_all_leadership_types() -> List[LeadershipType]:
    """
    Get all available leadership types.

    Returns:
        List of all leadership types.
    """
    return list(LeadershipType)


def compare_moral_standards(
    type1: LeadershipType,
    type2: LeadershipType,
) -> float:
    """
    Compare the moral standards of two leadership types.

    Args:
        type1: First leadership type.
        type2: Second leadership type.

    Returns:
        Difference in moral standards (type1 - type2).
    """
    profile1 = get_leadership_profile(type1)
    profile2 = get_leadership_profile(type2)
    return profile1.moral_standard - profile2.moral_standard
