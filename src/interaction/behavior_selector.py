"""
Behavior selector for moral realism ABM system.

This module implements BehaviorSelector class which provides
available behaviors based on leadership type constraints,
validates behaviors against leadership rules, and prioritizes
behaviors.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.prompts.leadership_prompts import ActionType, ACTION_DESCRIPTIONS


logger = logging.getLogger(__name__)


class BehaviorConstraint(Enum):
    """Types of behavior constraints."""

    PROHIBITED = "prohibited"
    PRIORITY_HIGH = "priority_high"
    PRIORITY_MEDIUM = "priority_medium"
    PRIORITY_LOW = "priority_low"
    REQUIRES_MORAL_VALIDATION = "requires_moral_validation"
    REQUIRES_RESOURCE_CHECK = "requires_resource_check"


@dataclass
class Behavior:
    """Represents an available behavior for an agent."""

    action_type: ActionType
    description: str
    constraints: Set[BehaviorConstraint] = None
    resource_cost: float = 50.0
    moral_impact: float = 0.0

    def __post_init__(self) -> None:
        if self.constraints is None:
            self.constraints = set()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_type": self.action_type.value,
            "description": self.description,
            "constraints": [c.value for c in self.constraints],
            "resource_cost": self.resource_cost,
            "moral_impact": self.moral_impact,
        }


@dataclass
class ValidationResult:
    """Result of behavior validation."""

    is_valid: bool
    reason: str
    constraints_violated: List[str]
    suggestions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "reason": self.reason,
            "constraints_violated": self.constraints_violated,
            "suggestions": self.suggestions,
        }


class BehaviorSelector:
    """
    Selects and validates behaviors for agents.

    Provides available behaviors based on leadership type,
    validates behaviors against leadership constraints,
    and prioritizes behaviors based on agent characteristics.
    """

    _LEADERSHIP_BEHAVIORS: Dict[LeadershipType, Dict[str, Any]] = {
        LeadershipType.WANGDAO: {
            "prohibited": [
                "security_military",
                "economic_sanction",
            ],
            "prioritized": [
                "security_mediation",
                "diplomatic_visit",
                "norm_proposal",
                "economic_aid",
            ],
        },
        LeadershipType.HEGEMON: {
            "prohibited": [],
            "prioritized": [
                "security_alliance",
                "diplomatic_alliance",
                "norm_proposal",
            ],
        },
        LeadershipType.QIANGQUAN: {
            "prohibited": [],
            "prioritized": [
                "economic_trade",
                "economic_sanction",
                "security_military",
            ],
        },
        LeadershipType.HUNYONG: {
            "prohibited": [
                "security_military",
            ],
            "prioritized": [
                "economic_trade",
                "diplomatic_visit",
            ],
        },
    }

    _AGENT_TYPE_RESTRICTIONS: Dict[AgentType, List[str]] = {
        AgentType.SMALL_STATE: [
            "security_military",
        ],
        AgentType.ORGANIZATION: [
            "security_military",
        ],
        AgentType.CONTROLLER: [
            "security_military",
            "security_alliance",
        ],
    }

    def __init__(
        self,
        enable_moral_validation: bool = True,
        custom_behaviors: Optional[Dict[ActionType, Behavior]] = None,
    ) -> None:
        """
        Initialize behavior selector.

        Args:
            enable_moral: Whether to perform moral validation.
            custom_behaviors: Custom behavior definitions.
        """
        self._enable_moral = enable_moral_validation
        self._custom_behaviors = custom_behaviors or {}

        self._base_behaviors = {
            action_type: Behavior(
                action_type=action_type,
                description=ACTION_DESCRIPTIONS[action_type],
            )
            for action_type in ActionType
        }

        self._base_behaviors.update(self._custom_behaviors)

    def get_available_behaviors(
        self,
        agent: Agent,
        situation: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get available behaviors for an agent.

        Args:
            agent: The agent to get behaviors for.
            situation: Current situation context.

        Returns:
            List of available behaviors as dictionaries.
        """
        if situation is None:
            situation = {}

        behaviors = self._base_behaviors.copy()

        behaviors = self._filter_by_agent_type(agent, behaviors)
        behaviors = self._filter_by_leadership_type(agent, behaviors)
        behaviors = self._filter_by_capability(agent, behaviors)
        behaviors = self._filter_by_situation(agent, behaviors, situation)
        behaviors = self._apply_behavior_constraints(agent, behaviors)

        return [b.to_dict() for b in behaviors.values()]

    def _filter_by_agent_type(
        self,
        agent: Agent,
        behaviors: Dict[ActionType, Behavior],
    ) -> Dict[ActionType, Behavior]:
        """Filter behaviors by agent type restrictions."""
        restrictions = self._AGENT_TYPE_RESTRICTIONS.get(
            agent.agent_type, []
        )

        return {
            action_type: behavior
            for action_type, behavior in behaviors.items()
            if action_type.value not in restrictions
        }

    def _filter_by_leadership_type(
        self,
        agent: Agent,
        behaviors: Dict[ActionType, Behavior],
    ) -> Dict[ActionType, Behavior]:
        """Filter behaviors by leadership type constraints."""
        leadership_config = self._LEADERSHIP_BEHAVIORS.get(
            agent.leadership_type, {}
        )

        prohibited = leadership_config.get("prohibited", [])

        return {
            action_type: behavior
            for action_type, behavior in behaviors.items()
            if action_type.value not in prohibited
        }

    def _filter_by_capability(
        self,
        agent: Agent,
        behaviors: Dict[ActionType, Behavior],
    ) -> Dict[ActionType, Behavior]:
        """Filter behaviors by agent capability."""
        if agent.capability is None:
            return behaviors

        capability_index = agent.capability.get_capability_index()

        filtered = {}

        for action_type, behavior in behaviors.items():
            requires_high_capability = action_type in [
                ActionType.SECURITY_MILITARY,
                ActionType.ECONOMIC_SANCTION,
            ]

            if requires_high_capability and capability_index < 40:
                continue

            filtered[action_type] = behavior

        return filtered

    def _filter_by_situation(
        self,
        agent: Agent,
        behaviors: Dict[ActionType, Behavior],
        situation: Dict[str, Any],
    ) -> Dict[ActionType, Behavior]:
        """Filter behaviors based on current situation."""
        in_crisis = situation.get("in_crisis", False)

        if in_crisis:
            behaviors = {
                action_type: behavior
                for action_type, behavior in behaviors.items()
                if action_type != ActionType.DIPLOMATIC_VISIT
            }

        return behaviors

    def _apply_behavior_constraints(
        self,
        agent: Agent,
        behaviors: Dict[ActionType, Behavior],
    ) -> Dict[ActionType, Behavior]:
        """Apply leadership-specific constraints and priorities."""
        leadership_config = self._LEADERSHIP_BEHAVIORS.get(
            agent.leadership_type, {}
        )

        prioritized = leadership_config.get("prioritized", [])

        for action_type, behavior in behaviors.items():
            if action_type.value in prioritized:
                behavior.constraints.add(BehaviorConstraint.PRIORITY_HIGH)
            else:
                behavior.constraints.add(BehaviorConstraint.PRIORITY_MEDIUM)

            if action_type in [
                ActionType.ECONOMIC_SANCTION,
                ActionType.SECURITY_MILITARY,
            ]:
                behavior.constraints.add(
                    BehaviorConstraint.REQUIRES_MORAL_VALIDATION
                )

        return behaviors

    def validate_behavior(
        self,
        agent: Agent,
        action_type: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate a specific behavior for an agent.

        Args:
            agent: The agent.
            action_type: The action type to validate.
            context: Additional context.

        Returns:
            Validation result.
        """
        if context is None:
            context = {}

        violated = []
        suggestions = []

        agent_restrictions = self._AGENT_TYPE_RESTRICTIONS.get(
            agent.agent_type, []
        )
        if action_type in agent_restrictions:
            violated.append(
                f"Action '{action_type}' is restricted for "
                f"{agent.agent_type.value} agents"
            )

        leadership_config = self._LEADERSHIP_BEHAVIORS.get(
            agent.leadership_type, {}
        )
        prohibited = leadership_config.get("prohibited", [])
        if action_type in prohibited:
            violated.append(
                f"Action '{action_type}' is prohibited by "
                f"{agent.leadership_type.value} leadership type"
            )
            prioritized = leadership_config.get("prioritized", [])
            if prioritized:
                suggestions.append(
                    f"Consider prioritized actions: {', '.join(prioritized[:2])}"
                )

        if agent.capability:
            capability_index = agent.capability.get_capability_index()

            if action_type in ["security_military", "economic_sanction"]:
                if capability_index < 40:
                    violated.append(
                        f"Insufficient capability ({capability_index:.1f}) "
                        f"for action '{action_type}'"
                    )
                    suggestions.append(
                        "Build up capability before taking this action"
                    )

        if self._enable_moral:
            moral_check = self._validate_moral_constraints(
                agent, action_type, context
            )
            if not moral_check["valid"]:
                violated.extend(moral_check["reasons"])

        is_valid = len(violated) == 0

        reason = (
            "Behavior is valid for this agent"
            if is_valid
            else f"Behavior validation failed: {'; '.join(violated)}"
        )

        return ValidationResult(
            is_valid=is_valid,
            reason=reason,
            constraints_violated=violated,
            suggestions=suggestions,
        )

    def _validate_moral_constraints(
        self,
        agent: Agent,
        action_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Validate moral constraints for an action."""
        reasons = []

        if agent.leadership_profile:
            if not agent.leadership_profile.accepts_moral_constraints:
                return {"valid": True, "reasons": []}

            if action_type in ["security_military", "economic_sanction"]:
                moral_standard = agent.leadership_profile.moral_standard

                if moral_standard > 0.8 and context.get("has_peaceful_alternative", True):
                    reasons.append(
                        f"High moral standard ({moral_standard:.2f}) "
                        "requires considering peaceful alternatives"
                    )

        return {"valid": len(reasons) == 0, "reasons": reasons}

    def get_prioritized_behaviors(
        self,
        agent: Agent,
        behaviors: Optional[List[Dict[str, Any]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get behaviors prioritized for an agent.

        Args:
            agent: The agent.
            behaviors: Behaviors to prioritize (if None, gets all available).

        Returns:
            Behaviors sorted by priority.
        """
        if behaviors is None:
            behaviors = self.get_available_behaviors(agent)

        leadership_config = self._LEADERSHIP_BEHAVIORS.get(
            agent.leadership_type, {}
        )
        prioritized = leadership_config.get("prioritized", [])

        def priority_sort(behavior: Dict[str, Any]) -> int:
            action_type = behavior.get("action_type", "")
            constraints = behavior.get("constraints", [])

            if "priority_high" in constraints or action_type in prioritized:
                return 0
            elif "priority_medium" in constraints:
                return 1
            else:
                return 2

        return sorted(behaviors, key=priority_sort)

    def filter_by_constraints(
        self,
        agent: Agent,
        behaviors: List[Dict[str, Any]],
        constraints: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Filter behaviors by custom constraints.

        Args:
            agent: The agent.
            behaviors: Behaviors to filter.
            constraints: Constraint dictionary.

        Returns:
            Filtered behaviors.
        """
        filtered = []

        max_resource_cost = constraints.get("max_resource_cost", 100)
        min_moral_impact = constraints.get("min_moral_impact", -100)
        max_moral_impact = constraints.get("max_moral_impact", 100)
        allowed_types = constraints.get("allowed_types", None)

        for behavior in behaviors:
            resource_cost = behavior.get("resource_cost", 50)
            if resource_cost > max_resource_cost:
                continue

            moral_impact = behavior.get("moral_impact", 0)
            if not (min_moral_impact <= moral_impact <= max_moral_impact):
                continue

            if allowed_types:
                action_type = behavior.get("action_type")
                if action_type not in allowed_types:
                    continue

            filtered.append(behavior)

        return filtered

    def get_behavior_recommendations(
        self,
        agent: Agent,
        situation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get recommended behaviors for an agent.

        Args:
            agent: The agent.
            situation: Current situation.

        Returns:
            Dictionary with recommendations and rationale.
        """
        if situation is None:
            situation = {}

        behaviors = self.get_available_behaviors(agent, situation)
        prioritized = self.get_prioritized_behaviors(agent, behaviors)

        top_recommendations = prioritized[:3]

        rationale = self._generate_recommendation_rationale(
            agent, top_recommendations, situation
        )

        return {
            "agent_id": agent.agent_id,
            "recommendations": top_recommendations,
            "total_available": len(behaviors),
            "rationale": rationale,
        }

    def _generate_recommendation_rationale(
        self,
        agent: Agent,
        recommendations: List[Dict[str, Any]],
        situation: Dict[str, Any],
    ) -> str:
        """Generate rationale for behavior recommendations."""
        if not recommendations:
            return "No behaviors available for current situation."

        leadership_type = agent.leadership_type.value

        leadership_rationale = {
            LeadershipType.WANGDAO.value: (
                "As a Wangdao leader, prioritize diplomatic engagement, "
                "moral persuasion, and peaceful conflict resolution."
            ),
            LeadershipType.HEGEMON.value: (
                "As a Hegemon, prioritize maintaining system stability, "
                "building alliances, and establishing norms."
            ),
            LeadershipType.QIANGQUAN.value: (
                "As a Qiangquan leader, prioritize maximizing power and "
                "economic interests."
            ),
            LeadershipType.HUNYONG.value: (
                "As a Hunyong leader, prioritize maintaining relations "
                "and avoiding direct confrontation."
            ),
        }

        base = leadership_rationale.get(leadership_type, "Follow leadership type principles.")

        if situation.get("in_crisis", False):
            base += " In crisis, focus on actions that can stabilize situation."

        if recommendations:
            actions = [r.get("action_type", "") for r in recommendations[:2]]
            base += f" Recommended actions: {', '.join(actions)}."

        return base
