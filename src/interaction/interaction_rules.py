"""
Interaction rules for moral realism ABM system.

This module implements InteractionRules class which defines
constraints and rules for agent interactions, validates
interactions based on relationships and capabilities,
and calculates moral impact of interactions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType


logger = logging.getLogger(__name__)


class InteractionCategory(Enum):
    """Categories of interactions."""

    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    COERCIVE = "coercive"
    PERSUASIVE = "persuasive"
    NORMATIVE = "normative"
    INFORMATIONAL = "informational"


@dataclass
class MoralImpact:
    """Moral impact assessment of an interaction."""

    score: float
    dimensions: Dict[str, float]
    justification: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "score": self.score,
            "dimensions": self.dimensions,
            "justification": self.justification,
        }


@dataclass
class InteractionConstraint:
    """Constraint on agent interactions."""

    name: str
    description: str
    requires_positive_relation: bool = False
    requires_capability_above: float = 0.0
    requires_capability_below: float = 100.0
    allowed_agent_types: List[AgentType] = field(default_factory=list)
    prohibited_leadership_types: List[LeadershipType] = field(default_factory=list)

    def check(
        self,
        from_agent: Agent,
        to_agent: Optional[Agent] = None,
    ) -> Tuple[bool, str]:
        """Check if constraint is satisfied."""
        if self.requires_positive_relation and to_agent:
            relationship_score = from_agent.get_relationship(to_agent.agent_id)
            if relationship_score <= 0:
                return False, "Requires positive relationship"

        if from_agent.capability:
            capability = from_agent.capability.get_capability_index()
            if capability < self.requires_capability_above:
                return False, f"Capability below minimum {self.requires_capability_above}"
            if capability > self.requires_capability_below:
                return False, f"Capability above maximum {self.requires_capability_below}"

        if self.allowed_agent_types:
            if from_agent.agent_type not in self.allowed_agent_types:
                return False, "Agent type not allowed"

        if self.prohibited_leadership_types:
            if from_agent.leadership_type in self.prohibited_leadership_types:
                return False, "Leadership type prohibited"

        return True, "Constraint satisfied"


class InteractionRules:
    """
    Defines and validates interaction rules.

    Provides constraints based on agent types and relationships,
    calculates moral impact, and applies interaction effects.
    """

    _ACTION_CONSTRAINTS: Dict[str, List[InteractionConstraint]] = {
        "security_military": [
            InteractionConstraint(
                name="capability_requirement",
                description="Military action requires sufficient capability",
                requires_capability_above=50.0,
            ),
        ],
        "security_alliance": [
            InteractionConstraint(
                name="positive_relation_preference",
                description="Alliance prefers positive relationship",
                requires_positive_relation=False,
            ),
        ],
        "economic_sanction": [
            InteractionConstraint(
                name="capability_requirement",
                description="Sanctions require sufficient capability",
                requires_capability_above=40.0,
            ),
        ],
        "norm_proposal": [
            InteractionConstraint(
                name="moral_leadership_preference",
                description="Norm proposals benefit from moral leadership",
            ),
        ],
    }

    _ACTION_MORAL_IMPACTS: Dict[str, Dict[str, Any]] = {
        "security_military": {
            "base_impact": -30,
            "dimensions": {
                "respect_for_norms": -20,
                "peaceful_resolution": -40,
                "humanitarian_concern": -25,
            },
            "justification": "Military action generally violates norms of peaceful resolution",
        },
        "security_alliance": {
            "base_impact": 5,
            "dimensions": {
                "respect_for_norms": 10,
                "peaceful_resolution": 5,
                "international_cooperation": 10,
            },
            "justification": "Alliance building promotes cooperation",
        },
        "security_mediation": {
            "base_impact": 25,
            "dimensions": {
                "respect_for_norms": 20,
                "peaceful_resolution": 35,
                "justice_and_fairness": 20,
            },
            "justification": "Mediation promotes peaceful resolution",
        },
        "economic_trade": {
            "base_impact": 10,
            "dimensions": {
                "international_cooperation": 20,
                "respect_for_norms": 5,
            },
            "justification": "Trade promotes cooperation",
        },
        "economic_sanction": {
            "base_impact": -20,
            "dimensions": {
                "respect_for_norms": -15,
                "humanitarian_concern": -25,
            },
            "justification": "Sanctions can harm populations",
        },
        "economic_aid": {
            "base_impact": 30,
            "dimensions": {
                "humanitarian_concern": 40,
                "international_cooperation": 20,
            },
            "justification": "Aid demonstrates humanitarian concern",
        },
        "norm_proposal": {
            "base_impact": 20,
            "dimensions": {
                "respect_for_norms": 25,
                "international_cooperation": 15,
            },
            "justification": "Norm proposals strengthen international order",
        },
        "norm_reform": {
            "base_impact": 15,
            "dimensions": {
                "respect_for_norms": 20,
                "justice_and_fairness": 15,
            },
            "justification": "Norm reform promotes better governance",
        },
        "diplomatic_visit": {
            "base_impact": 10,
            "dimensions": {
                "peaceful_resolution": 10,
                "international_cooperation": 10,
            },
            "justification": "Diplomatic engagement promotes peaceful relations",
        },
        "diplomatic_alliance": {
            "base_impact": 15,
            "dimensions": {
                "international_cooperation": 20,
                "respect_for_norms": 10,
            },
            "justification": "Formal alliance strengthens cooperation",
        },
        "no_action": {
            "base_impact": 0,
            "dimensions": {},
            "justification": "No action has neutral moral impact",
        },
    }

    def __init__(
        self,
        custom_constraints: Optional[Dict[str, List[InteractionConstraint]]] = None,
        rule_environment: Optional[Any] = None,
    ) -> None:
        """Initialize interaction rules."""
        self._constraints = self._ACTION_CONSTRAINTS.copy()
        if custom_constraints:
            self._constraints.update(custom_constraints)

        self._rule_environment = rule_environment

    def validate_interaction(
        self,
        from_agent: Agent,
        to_agent: Optional[Agent],
        action: Dict[str, Any],
    ) -> Tuple[bool, str, List[str]]:
        """Validate an interaction between agents."""
        action_type = action.get("action_type", "no_action")

        violations = []
        reasons = []

        constraints = self._constraints.get(action_type, [])

        for constraint in constraints:
            is_satisfied, reason = constraint.check(from_agent, to_agent)
            if not is_satisfied:
                violations.append(constraint.name)
                reasons.append(reason)

        if to_agent and to_agent.agent_id == from_agent.agent_id:
            violations.append("self_interaction")
            reasons.append("Agent cannot interact with itself")

        if not from_agent.is_active:
            violations.append("source_inactive")
            reasons.append("Source agent is inactive")

        if to_agent and not to_agent.is_active:
            violations.append("target_inactive")
            reasons.append("Target agent is inactive")

        is_valid = len(violations) == 0

        if is_valid:
            reason = "Interaction is valid"
        else:
            reason = f"Interaction validation failed: {'; '.join(reasons)}"

        return is_valid, reason, violations

    def calculate_interaction_morality(
        self,
        action: Dict[str, Any],
        from_profile: Optional[Any] = None,
    ) -> MoralImpact:
        """Calculate moral impact of an interaction."""
        action_type = action.get("action_type", "no_action")

        base_impact = self._ACTION_MORAL_IMPACTS.get(action_type, {
            "base_impact": 0,
            "dimensions": {},
            "justification": "Unknown action type",
        })

        score = base_impact["base_impact"]
        dimensions = base_impact["dimensions"].copy()
        justification = base_impact["justification"]

        if from_profile:
            if score < 0 and from_profile.moral_standard > 0.7:
                score *= 0.7
                justification += " (mitigated by high moral standard)"
            elif score < 0 and from_profile.moral_standard < 0.3:
                score *= 1.3
                justification += " (amplified by low moral standard)"

            if score > 0 and from_profile.uses_moral_persuasion:
                score *= 1.2
                justification += " (enhanced by moral persuasion)"

        resource_allocation = action.get("resource_allocation", 50)
        if resource_allocation > 70:
            score *= 1.3
        elif resource_allocation < 30:
            score *= 0.7

        score = max(-100.0, min(100.0, score))

        return MoralImpact(
            score=score,
            dimensions=dimensions,
            justification=justification,
        )

    def get_allowed_interactions(
        self,
        agent_type: AgentType,
    ) -> List[str]:
        """Get allowed interaction types for an agent type."""
        all_actions = list(self._ACTION_MORAL_IMPACTS.keys())

        if agent_type == AgentType.SMALL_STATE:
            return [
                action for action in all_actions
                if action not in ["security_military"]
            ]
        elif agent_type == AgentType.ORGANIZATION:
            return [
                action for action in all_actions
                if action not in ["security_military", "security_alliance"]
            ]
        elif agent_type == AgentType.CONTROLLER:
            return ["no_action"]
        else:
            return all_actions

    def check_capability_constraints(
        self,
        from_agent: Agent,
        to_agent: Optional[Agent],
        action: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """Check if action is within capability constraints."""
        action_type = action.get("action_type", "no_action")

        if not from_agent.capability:
            return True, "No capability information available"

        from_capability = from_agent.capability.get_capability_index()

        requirements = {
            "security_military": {"min": 50, "description": "Military requires high capability"},
            "security_alliance": {"min": 30, "description": "Alliance requires moderate capability"},
            "economic_sanction": {"min": 40, "description": "Sanctions require moderate capability"},
            "norm_proposal": {"min": 60, "description": "Norm proposal requires high capability"},
            "diplomatic_alliance": {"min": 50, "description": "Formal alliance requires high capability"},
        }

        req = requirements.get(action_type)
        if req:
            if from_capability < req["min"]:
                return False, (
                    f"Capability ({from_capability:.1f}) below required "
                    f"minimum ({req['min']}) for {action_type}: {req['description']}"
                )

        if to_agent and to_agent.capability:
            to_capability = to_agent.capability.get_capability_index()

            if action_type == "security_alliance":
                capability_gap = abs(from_capability - to_capability)
                if capability_gap > 30:
                    return False, (
                        f"Capability gap ({capability_gap:.1f}) too large for alliance"
                    )

        return True, "Capability constraints satisfied"

    def apply_interaction_effects(
        self,
        from_agent: Agent,
        to_agent: Optional[Agent],
        action: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Apply effects of an interaction to agents."""
        effects = {}

        action_type = action.get("action_type", "no_action")

        moral_impact = self.calculate_interaction_morality(
            action, from_agent.leadership_profile
        )
        effects["moral_impact"] = moral_impact.to_dict()

        if to_agent:
            relationship_change = self._calculate_relationship_change(
                from_agent, to_agent, action, response
            )

            current = from_agent.get_relationship(to_agent.agent_id)
            new_from = max(-1.0, min(1.0, current + relationship_change))
            from_agent.set_relationship(to_agent.agent_id, new_from)

            current_to = to_agent.get_relationship(from_agent.agent_id)
            new_to = max(-1.0, min(1.0, current_to + relationship_change * 0.5))
            to_agent.set_relationship(from_agent.agent_id, new_to)

            effects["relationship_change"] = {
                "from_agent_new_score": new_from,
                "to_agent_new_score": new_to,
                "change_amount": relationship_change,
            }

        resource_allocation = action.get("resource_allocation", 0)
        if resource_allocation > 0 and from_agent.capability:
            effects["resource_effect"] = {
                "allocated": resource_allocation,
                "capability_impact": -resource_allocation * 0.01,
            }

        return effects

    def _calculate_relationship_change(
        self,
        from_agent: Agent,
        to_agent: Agent,
        action: Dict[str, Any],
        response: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate relationship change from an interaction."""
        action_type = action.get("action_type", "no_action")

        action_changes = {
            "security_military": -0.2,
            "security_alliance": 0.15,
            "security_mediation": 0.1,
            "economic_trade": 0.08,
            "economic_sanction": -0.25,
            "economic_aid": 0.2,
            "norm_proposal": 0.05,
            "norm_reform": 0.05,
            "diplomatic_visit": 0.1,
            "diplomatic_alliance": 0.15,
            "no_action": 0.0,
        }

        base_change = action_changes.get(action_type, 0.0)

        if response:
            response_type = response.get("response_type", "")

            if response_type in ["support", "accept"]:
                base_change += 0.1
            elif response_type in ["decline", "reject", "condemn"]:
                base_change -= 0.15
            elif response_type == "concern":
                base_change -= 0.05

        from_type = from_agent.leadership_type
        to_type = to_agent.leadership_type

        if from_type == to_type:
            base_change *= 1.1

        if {from_type, to_type} == {
            LeadershipType.WANGDAO, LeadershipType.HEGEMON
        } or {from_type, to_type} == {
            LeadershipType.HEGEMON, LeadershipType.WANGDAO
        }:
            base_change *= 1.05

        if {from_type, to_type} == {
            LeadershipType.QIANGQUAN, LeadershipType.WANGDAO
        } or {from_type, to_type} == {
            LeadershipType.WANGDAO, LeadershipType.QIANGQUAN
        }:
            base_change *= 0.9

        return max(-1.0, min(1.0, base_change))

    def get_interaction_category(
        self,
        action_type: str,
    ) -> InteractionCategory:
        """Get category of an interaction."""
        cooperative = [
            "economic_trade", "economic_aid", "security_alliance",
            "diplomatic_visit", "diplomatic_alliance", "norm_proposal",
        ]
        coercive = [
            "security_military", "economic_sanction",
        ]
        normative = [
            "norm_proposal", "norm_reform",
        ]
        informational = [
            "info_request", "info_sharing",
        ]

        if action_type in cooperative:
            return InteractionCategory.COOPERATIVE
        elif action_type in coercive:
            return InteractionCategory.COERCIVE
        elif action_type in normative:
            return InteractionCategory.NORMATIVE
        elif action_type in informational:
            return InteractionCategory.INFORMATIONAL
        else:
            return InteractionCategory.PERSUASIVE

    def get_rule_summary(self) -> Dict[str, Any]:
        """Get a summary of interaction rules."""
        return {
            "constraint_count": sum(len(constraints) for constraints in self._constraints.values()),
            "action_types": list(self._constraints.keys()),
            "has_rule_environment": self._rule_environment is not None,
        }

    def add_custom_constraint(
        self,
        action_type: str,
        constraint: InteractionConstraint,
    ) -> None:
        """Add a custom constraint for an action type."""
        if action_type not in self._constraints:
            self._constraints[action_type] = []

        self._constraints[action_type].append(constraint)
        logger.info(f"Added custom constraint for {action_type}")
