"""
Rule environment module for the moral realism ABM system.

This module defines the rule constraint environment that validates
capability changes, evaluates moral levels, and checks order evolution rules.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class OrderType(Enum):
    """Types of international order."""

    HEGEMONIC_ORDER = "hegemonic_order"  # 霸权秩序
    BALANCE_OF_POWER = "balance_of_power"  # 均势秩序
    CONCERT_OF_POWERS = "concert_of_powers"  # 大国协调
    ANARCHIC_DISORDER = "anarchic_disorder"  # 无政府混乱
    MULTIPOLAR_BALANCE = "multipolar_balance"  # 多极平衡


class MoralDimension(Enum):
    """Dimensions of moral evaluation."""

    RESPECT_FOR_NORMS = "respect_for_norms"  # 尊重规范
    HUMANITARIAN_CONCERN = "humanitarian_concern"  # 人道主义关怀
    PEACEFUL_RESOLUTION = "peaceful_resolution"  # 和平解决争端
    INTERNATIONAL_COOPERATION = "international_cooperation"  # 国际合作
    JUSTICE_AND_FAIRNESS = "justice_and_fairness"  # 正义与公平


@dataclass
class CapabilityChangeRule:
    """Rules for validating capability changes."""

    max_single_step_change: float = 20.0  # Maximum change per step
    max_absolute_power_gain: float = 30.0  # Maximum absolute power gain
    power_decay_factor: float = 0.95  # Power decay over time

    def validate_change(self, old_value: float, new_value: float) -> Tuple[bool, str]:
        """
        Validate a capability value change.

        Args:
            old_value: The old capability value.
            new_value: The new capability value.

        Returns:
            Tuple of (is_valid, reason).
        """
        change = abs(new_value - old_value)

        if change > self.max_single_step_change:
            return False, f"Change {change} exceeds maximum single step change {self.max_single_step_change}"

        if new_value < 0:
            return False, "New value cannot be negative"

        if new_value > 100:
            return False, f"New value {new_value} exceeds maximum 100"

        return True, "Valid"


@dataclass
class MoralEvaluation:
    """Result of moral evaluation."""

    dimension: MoralDimension
    score: float  # 0-100 scale
    justification: str


class RuleEnvironment:
    """
    Rule constraint environment for the simulation.

    Validates capability changes, evaluates moral levels across multiple
    dimensions, and checks international order evolution rules.
    """

    def __init__(self, capability_change_rule: Optional[CapabilityChangeRule] = None) -> None:
        """
        Initialize the rule environment.

        Args:
            capability_change_rule: Custom capability change rules.
        """
        self.capability_change_rule = (
            capability_change_rule if capability_change_rule else CapabilityChangeRule()
        )

        # Moral dimension weights for overall index calculation
        self._moral_weights = {
            MoralDimension.RESPECT_FOR_NORMS: 0.25,
            MoralDimension.HUMANITARIAN_CONCERN: 0.15,
            MoralDimension.PEACEFUL_RESOLUTION: 0.25,
            MoralDimension.INTERNATIONAL_COOPERATION: 0.20,
            MoralDimension.JUSTICE_AND_FAIRNESS: 0.15,
        }

    def validate_capability_change(
        self,
        agent_id: str,
        old_capability: float,
        new_capability: float,
        context: Optional[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        Validate a capability change for an agent.

        Args:
            agent_id: The agent ID.
            old_capability: The old capability value.
            new_capability: The new capability value.
            context: Additional context information.

        Returns:
            Tuple of (is_valid, reason).
        """
        context = context or {}

        # Validate basic change rules
        is_valid, reason = self.capability_change_rule.validate_change(
            old_capability, new_capability
        )
        if not is_valid:
            return False, reason

        # Check for unrealistic gains (heuristic)
        if new_capability > old_capability:
            gain = new_capability - old_capability
            if gain > self.capability_change_rule.max_absolute_power_gain:
                return False, f"Power gain {gain} exceeds maximum {self.capability_change_rule.max_absolute_power_gain}"

        # Validate against context-specific rules
        if context.get("in_crisis", False):
            # During crisis, power gains are more restricted
            if new_capability > old_capability + 10:
                return False, "Power gains restricted during crisis"

        return True, "Valid"

    def evaluate_moral_level(
        self,
        agent_id: str,
        actions: List[Dict],
        interactions: List[Dict],
    ) -> List[MoralEvaluation]:
        """
        Evaluate moral level across all 5 dimensions.

        Args:
            agent_id: The agent ID.
            actions: List of actions taken by the agent.
            interactions: List of interactions involving the agent.

        Returns:
            List of moral evaluations for each dimension.
        """
        evaluations = []

        # Respect for norms
        respect_score = self._evaluate_respect_for_norms(actions, interactions)
        evaluations.append(
            MoralEvaluation(
                dimension=MoralDimension.RESPECT_FOR_NORMS,
                score=respect_score,
                justification=self._get_justification(MoralDimension.RESPECT_FOR_NORMS, respect_score),
            )
        )

        # Humanitarian concern
        humanitarian_score = self._evaluate_humanitarian_concern(actions, interactions)
        evaluations.append(
            MoralEvaluation(
                dimension=MoralDimension.HUMANITARIAN_CONCERN,
                score=humanitarian_score,
                justification=self._get_justification(MoralDimension.HUMANITARIAN_CONCERN, humanitarian_score),
            )
        )

        # Peaceful resolution
        peaceful_score = self._evaluate_peaceful_resolution(actions, interactions)
        evaluations.append(
            MoralEvaluation(
                dimension=MoralDimension.PEACEFUL_RESOLUTION,
                score=peaceful_score,
                justification=self._get_justification(MoralDimension.PEACEFUL_RESOLUTION, peaceful_score),
            )
        )

        # International cooperation
        cooperation_score = self._evaluate_international_cooperation(actions, interactions)
        evaluations.append(
            MoralEvaluation(
                dimension=MoralDimension.INTERNATIONAL_COOPERATION,
                score=cooperation_score,
                justification=self._get_justification(MoralDimension.INTERNATIONAL_COOPERATION, cooperation_score),
            )
        )

        # Justice and fairness
        justice_score = self._evaluate_justice_and_fairness(actions, interactions)
        evaluations.append(
            MoralEvaluation(
                dimension=MoralDimension.JUSTICE_AND_FAIRNESS,
                score=justice_score,
                justification=self._get_justification(MoralDimension.JUSTICE_AND_FAIRNESS, justice_score),
            )
        )

        return evaluations

    def calculate_moral_level_index(self, evaluations: List[MoralEvaluation]) -> float:
        """
        Calculate the overall moral level index from evaluations.

        Args:
            evaluations: List of moral evaluations.

        Returns:
            Overall moral level index (0-100).
        """
        total_score = 0.0
        total_weight = 0.0

        for evaluation in evaluations:
            weight = self._moral_weights.get(evaluation.dimension, 0.2)
            total_score += evaluation.score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_score / total_weight

    def check_order_evolution(
        self,
        power_distribution: Dict[str, float],
        norm_authorities: Dict[str, float],
        conflict_levels: Dict[str, float],
    ) -> Tuple[OrderType, Dict]:
        """
        Check international order evolution.

        Args:
            power_distribution: Dictionary mapping agent IDs to power shares.
            norm_authorities: Dictionary mapping norm names to authority levels.
            conflict_levels: Dictionary mapping agent pairs to conflict levels.

        Returns:
            Tuple of (order_type, analysis_details).
        """
        # Calculate power concentration
        power_values = sorted(power_distribution.values(), reverse=True)
        top_share = power_values[0] if power_values else 0
        top3_share = sum(power_values[:3])

        # Calculate norm strength
        avg_norm_authority = sum(norm_authorities.values()) / len(norm_authorities) if norm_authorities else 50

        # Calculate conflict level
        avg_conflict = sum(conflict_levels.values()) / len(conflict_levels) if conflict_levels else 30

        # Determine order type
        order_type = self.determine_order_type(
            top_share=top_share,
            top3_share=top3_share,
            norm_authority=avg_norm_authority,
            conflict_level=avg_conflict,
        )

        # Analysis details
        analysis = {
            "power_concentration": {
                "top_share": top_share,
                "top3_share": top3_share,
            },
            "norm_strength": avg_norm_authority,
            "conflict_level": avg_conflict,
            "stability_score": self._calculate_stability_score(
                norm_authority=avg_norm_authority,
                conflict_level=avg_conflict,
                power_concentration=top_share,
            ),
        }

        return order_type, analysis

    def determine_order_type(
        self,
        top_share: float,
        top3_share: float,
        norm_authority: float,
        conflict_level: float,
    ) -> OrderType:
        """
        Determine the type of international order.

        Args:
            top_share: Power share of top agent.
            top3_share: Power share of top 3 agents.
            norm_authority: Average norm authority (0-100).
            conflict_level: Average conflict level (0-100).

        Returns:
            The order type.
        """
        # Hegemonic order: single dominant power
        if top_share > 0.45 and norm_authority > 50:
            return OrderType.HEGEMONIC_ORDER

        # Balance of power: two roughly equal powers
        if top_share < 0.40 and top3_share > 0.70 and conflict_level < 50:
            return OrderType.BALANCE_OF_POWER

        # Concert of powers: multiple powers cooperate
        if top3_share > 0.60 and norm_authority > 60 and conflict_level < 40:
            return OrderType.CONCERT_OF_POWERS

        # Multipolar balance: multiple powers without strong coordination
        if top_share < 0.35 and top3_share > 0.55:
            return OrderType.MULTIPOLAR_BALANCE

        # Default to anarchic disorder
        return OrderType.ANARCHIC_DISORDER

    # Private helper methods for moral evaluation

    def _evaluate_respect_for_norms(self, actions: List[Dict], interactions: List[Dict]) -> float:
        """Evaluate respect for international norms."""
        if not actions and not interactions:
            return 50.0  # Neutral score

        score = 70.0  # Start with positive assumption

        # Check actions for norm violations
        for action in actions:
            if action.get("violates_norm", False):
                score -= 15 * action.get("severity", 0.5)
            elif action.get("upholds_norm", False):
                score += 5 * action.get("strength", 0.5)

        # Check interactions
        for interaction in interactions:
            if interaction.get("type") == "norm_violation":
                score -= 10
            elif interaction.get("type") == "norm_compliance":
                score += 5

        return max(0.0, min(100.0, score))

    def _evaluate_humanitarian_concern(self, actions: List[Dict], interactions: List[Dict]) -> float:
        """Evaluate humanitarian concern."""
        if not actions and not interactions:
            return 50.0

        score = 60.0
        humanitarian_actions = 0

        for action in actions:
            if action.get("type") == "humanitarian_aid":
                score += 10
                humanitarian_actions += 1
            elif action.get("type") == "disregard_humanitarian":
                score -= 20

        for interaction in interactions:
            if interaction.get("type") == "humanitarian_cooperation":
                score += 8
            elif interaction.get("type") == "humanitarian_violation":
                score -= 25

        # Bonus for consistent humanitarian engagement
        if humanitarian_actions > 2:
            score += 5

        return max(0.0, min(100.0, score))

    def _evaluate_peaceful_resolution(self, actions: List[Dict], interactions: List[Dict]) -> float:
        """Evaluate preference for peaceful resolution."""
        if not actions and not interactions:
            return 50.0

        score = 65.0
        peaceful_actions = 0
        aggressive_actions = 0

        for action in actions:
            if action.get("type") == "diplomatic_negotiation":
                score += 8
                peaceful_actions += 1
            elif action.get("type") == "military_action":
                score -= 20
                aggressive_actions += 1

        for interaction in interactions:
            if interaction.get("type") == "peaceful_resolution":
                score += 10
                peaceful_actions += 1
            elif interaction.get("type") == "force_confrontation":
                score -= 25
                aggressive_actions += 1

        # Heavy penalty for military escalation
        if aggressive_actions > 2:
            score -= 15

        return max(0.0, min(100.0, score))

    def _evaluate_international_cooperation(self, actions: List[Dict], interactions: List[Dict]) -> float:
        """Evaluate international cooperation."""
        if not actions and not interactions:
            return 50.0

        score = 60.0
        cooperative_actions = 0

        for action in actions:
            if action.get("type") == "cooperation":
                score += 8
                cooperative_actions += 1
            elif action.get("type") == "isolationism":
                score -= 10

        for interaction in interactions:
            if interaction.get("type") == "alliance":
                score += 5
            elif interaction.get("type") == "multilateral_action":
                score += 10
            elif interaction.get("type") == "unilateral_action":
                score -= 5

        # Bonus for multilateral engagement
        if cooperative_actions > 2:
            score += 5

        return max(0.0, min(100.0, score))

    def _evaluate_justice_and_fairness(self, actions: List[Dict], interactions: List[Dict]) -> float:
        """Evaluate justice and fairness."""
        if not actions and not interactions:
            return 50.0

        score = 55.0
        fair_actions = 0

        for action in actions:
            if action.get("type") == "fair_mediation":
                score += 10
                fair_actions += 1
            elif action.get("type") == "unfair_advantage":
                score -= 20
            elif action.get("type") == "resource_sharing":
                score += 8

        for interaction in interactions:
            if interaction.get("type") == "fair_negotiation":
                score += 7
            elif interaction.get("type") == "coercive_action":
                score -= 15

        return max(0.0, min(100.0, score))

    def _get_justification(self, dimension: MoralDimension, score: float) -> str:
        """Get justification text for moral dimension score."""
        if score >= 80:
            return f"Excellent: Strong commitment to {dimension.value}"
        elif score >= 60:
            return f"Good: Generally respects {dimension.value}"
        elif score >= 40:
            return f"Moderate: Mixed record on {dimension.value}"
        elif score >= 20:
            return f"Poor: Limited respect for {dimension.value}"
        else:
            return f"Very Poor: Systematic violations of {dimension.value}"

    def _calculate_stability_score(
        self,
        norm_authority: float,
        conflict_level: float,
        power_concentration: float,
    ) -> float:
        """
        Calculate system stability score.

        Args:
            norm_authority: Average norm authority (0-100).
            conflict_level: Average conflict level (0-100).
            power_concentration: Top power share (0-1).

        Returns:
            Stability score (0-100).
        """
        # High norm authority contributes to stability
        norm_factor = norm_authority * 0.4

        # Low conflict contributes to stability
        conflict_factor = (100 - conflict_level) * 0.3

        # Moderate power concentration can be stabilizing, but extreme is not
        if power_concentration > 0.5:
            concentration_factor = 100 - (power_concentration - 0.5) * 100 * 0.3
        else:
            concentration_factor = 100 - (0.5 - power_concentration) * 100 * 0.3

        stability = norm_factor + conflict_factor + concentration_factor
        return max(0.0, min(100.0, stability))

    def set_moral_weight(self, dimension: MoralDimension, weight: float) -> None:
        """
        Set the weight for a moral dimension.

        Args:
            dimension: The moral dimension.
            weight: The weight to set (0-1).
        """
        if not 0 <= weight <= 1:
            raise ValueError(f"Weight must be between 0 and 1, got {weight}")
        self._moral_weights[dimension] = weight

    def normalize_moral_weights(self) -> None:
        """Normalize moral weights to sum to 1."""
        total = sum(self._moral_weights.values())
        if total == 0:
            return
        for dimension in self._moral_weights:
            self._moral_weights[dimension] /= total

    def get_environment_summary(self) -> Dict:
        """
        Get a summary of the rule environment.

        Returns:
            Dictionary containing environment configuration.
        """
        return {
            "max_single_step_change": self.capability_change_rule.max_single_step_change,
            "max_absolute_power_gain": self.capability_change_rule.max_absolute_power_gain,
            "power_decay_factor": self.capability_change_rule.power_decay_factor,
            "moral_weights": {dim.value: weight for dim, weight in self._moral_weights.items()},
        }
