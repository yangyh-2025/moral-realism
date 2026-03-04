"""
Capability and power models for the moral realism ABM system.

This module defines capability tiers, hard power, soft power, and
overall capability metrics for agents in the simulation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class CapabilityTier(Enum):
    """Capability tiers for classifying agent power levels."""

    T0_SUPERPOWER = "t0_superpower"  # 超级大国
    T1_GREAT_POWER = "t1_great_power"  # 大国
    T2_REGIONAL = "t2_regional"  # 区域性大国
    T3_MEDIUM = "t3_medium"  # 中等国家
    T4_SMALL = "t4_small"  # 小国


@dataclass
class HardPower:
    """Represents an agent's hard power capabilities."""

    # Military capabilities (0-100 scale)
    military_capability: float = 50.0  # Overall military strength
    nuclear_capability: float = 0.0  # Nuclear capability presence/strength
    conventional_forces: float = 50.0  # Conventional military strength
    force_projection: float = 50.0  # Ability to project power globally

    # Economic capabilities (0-100 scale)
    gdp_share: float = 2.0  # Share of global GDP
    economic_growth: float = 3.0  # Annual GDP growth rate
    trade_volume: float = 50.0  # Trade volume relative to peers
    financial_influence: float = 50.0  # Control over financial systems

    # Technological capabilities (0-100 scale)
    technology_level: float = 50.0  # Overall technological advancement
    military_technology: float = 50.0  # Military-specific technology
    innovation_capacity: float = 50.0  # R&D and innovation capacity

    # Resource access
    energy_access: float = 50.0  # Access to energy resources
    strategic_materials: float = 50.0  # Access to strategic materials

    def validate(self) -> bool:
        """Validate hard power values are in acceptable ranges."""
        attrs = [
            "military_capability",
            "nuclear_capability",
            "conventional_forces",
            "force_projection",
            "economic_growth",
            "trade_volume",
            "financial_influence",
            "technology_level",
            "military_technology",
            "innovation_capacity",
            "energy_access",
            "strategic_materials",
        ]
        for attr in attrs:
            value = getattr(self, attr)
            if not 0 <= value <= 100:
                raise ValueError(f"{attr} must be between 0 and 100, got {value}")
        if not 0 <= self.gdp_share <= 100:
            raise ValueError(f"gdp_share must be between 0 and 100, got {self.gdp_share}")
        return True

    def get_hard_power_index(self) -> float:
        """
        Calculate the hard power index.

        Returns:
            Hard power index (0-100 scale).
        """
        # Weighted combination of military, economic, and tech factors
        military_score = (
            self.military_capability * 0.3
            + self.nuclear_capability * 0.2
            + self.conventional_forces * 0.3
            + self.force_projection * 0.2
        )
        economic_score = (
            self.gdp_share * 0.3
            + self.trade_volume / 33.33 * 0.3  # Normalize to 0-1
            + self.financial_influence * 0.4
        )
        tech_score = (
            self.technology_level * 0.3
            + self.military_technology * 0.3
            + self.innovation_capacity * 0.4
        )
        resource_score = (self.energy_access + self.strategic_materials) / 2

        # Final weighted index
        hard_power_index = (
            military_score * 0.4
            + economic_score * 0.3
            + tech_score * 0.2
            + resource_score * 0.1
        )
        return min(100.0, max(0.0, hard_power_index))


@dataclass
class SoftPower:
    """Represents an agent's soft power capabilities."""

    # Discourse power (0-100 scale)
    discourse_power: float = 50.0  # Ability to set international agenda
    narrative_control: float = 50.0  # Control over international narratives
    media_influence: float = 50.0  # Media and information influence

    # Alliance relationships
    allies_count: int = 0  # Number of formal allies
    ally_strength: float = 50.0  # Aggregate strength of allies
    network_position: float = 50.0  # Centrality in alliance networks

    # International support (0-100 scale)
    diplomatic_support: float = 50.0  # General diplomatic backing
    moral_legitimacy: float = 50.0  # Moral standing in international community
    cultural_influence: float = 50.0  # Cultural reach and appeal

    # Institutional power
    un_influence: float = 50.0  # Influence in UN and international orgs
    institutional_leadership: float = 50.0  # Leadership in key institutions

    def validate(self) -> bool:
        """Validate soft power values are in acceptable ranges."""
        attrs = [
            "discourse_power",
            "narrative_control",
            "media_influence",
            "ally_strength",
            "network_position",
            "diplomatic_support",
            "moral_legitimacy",
            "cultural_influence",
            "un_influence",
            "institutional_leadership",
        ]
        for attr in attrs:
            value = getattr(self, attr)
            if not 0 <= value <= 100:
                raise ValueError(f"{attr} must be between 0 and 100, got {value}")
        if self.allies_count < 0:
            raise ValueError("allies_count must be non-negative")
        return True

    def get_soft_power_index(self) -> float:
        """
        Calculate the soft power index.

        Returns:
            Soft power index (0-100 scale).
        """
        # Discourse component
        discourse_score = (
            self.discourse_power * 0.4
            + self.narrative_control * 0.3
            + self.media_influence * 0.3
        )

        # Alliance component
        # Normalize allies count (assume max reasonable is ~30)
        allies_normalized = min(1.0, self.allies_count / 30.0) * 100
        alliance_score = (
            allies_normalized * 0.3
            + self.ally_strength * 0.4
            + self.network_position * 0.3
        )

        # Support component
        support_score = (
            self.diplomatic_support * 0.35
            + self.moral_legitimacy * 0.35
            + self.cultural_influence * 0.3
        )

        # Institutional component
        institutional_score = (
            self.un_influence * 0.5
            + self.institutional_leadership * 0.5
        )

        # Final weighted index
        soft_power_index = (
            discourse_score * 0.3
            + alliance_score * 0.3
            + support_score * 0.25
            + institutional_score * 0.15
        )
        return min(100.0, max(0.0, soft_power_index))


@dataclass
class Capability:
    """Represents an agent's overall capability and power."""

    agent_id: str
    hard_power: HardPower = field(default_factory=HardPower)
    soft_power: SoftPower = field(default_factory=SoftPower)
    tier: Optional[CapabilityTier] = None

    # Historical tracking
    history: List[Dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize tier after power values are set."""
        if self.tier is None:
            self.tier = self._determine_tier()

    def validate(self) -> bool:
        """Validate capability components."""
        self.hard_power.validate()
        self.soft_power.validate()
        return True

    def _determine_tier(self) -> CapabilityTier:
        """
        Determine capability tier based on power indices.

        Returns:
            The capability tier.
        """
        hard_index = self.hard_power.get_hard_power_index()
        soft_index = self.soft_power.get_soft_power_index()
        combined_index = (hard_index * 0.7 + soft_index * 0.3)

        if combined_index >= 80:
            return CapabilityTier.T0_SUPERPOWER
        elif combined_index >= 65:
            return CapabilityTier.T1_GREAT_POWER
        elif combined_index >= 45:
            return CapabilityTier.T2_REGIONAL
        elif combined_index >= 25:
            return CapabilityTier.T3_MEDIUM
        else:
            return CapabilityTier.T4_SMALL

    def get_capability_index(self) -> float:
        """
        Calculate the overall capability index.

        Returns:
            Combined capability index (0-100 scale).
        """
        hard_index = self.hard_power.get_hard_power_index()
        soft_index = self.soft_power.get_soft_power_index()

        # Hard power has slightly more weight in overall capability
        combined_index = hard_index * 0.6 + soft_index * 0.4
        return combined_index

    def get_tier(self) -> CapabilityTier:
        """
        Get the capability tier.

        Returns:
            The capability tier.
        """
        return self.tier or self._determine_tier()

    def record_state(self, step: int, context: Optional[Dict] = None) -> None:
        """
        Record the current capability state for historical tracking.

        Args:
            step: Simulation step number.
            context: Additional context information.
        """
        state = {
            "step": step,
            "hard_power_index": self.hard_power.get_hard_power_index(),
            "soft_power_index": self.soft_power.get_soft_power_index(),
            "capability_index": self.get_capability_index(),
            "tier": self.get_tier().value,
            "context": context or {},
        }
        self.history.append(state)

    def get_history(self) -> List[Dict]:
        """
        Get the capability history.

        Returns:
            List of historical capability states.
        """
        return self.history


# Objective strategic interests by capability tier
OBJECTIVE_STRATEGIC_INTERESTS: Dict[CapabilityTier, List[str]] = {
    CapabilityTier.T0_SUPERPOWER: [
        "global hegemony maintenance",
        "global order and rule-setting",
        "global military presence",
        "global alliance leadership",
        "control of strategic chokepoints",
        "technological supremacy",
        "containment of peer competitors",
    ],
    CapabilityTier.T1_GREAT_POWER: [
        "great power status recognition",
        "regional hegemony",
        "global influence projection",
        "security guarantees",
        "economic independence",
        "technological parity",
    ],
    CapabilityTier.T2_REGIONAL: [
        "regional leadership",
        "territorial integrity",
        "economic development",
        "autonomy from great powers",
        "regional security",
    ],
    CapabilityTier.T3_MEDIUM: [
        "sovereignty protection",
        "economic stability",
        "security arrangements",
        "international integration",
    ],
    CapabilityTier.T4_SMALL: [
        "survival",
        "economic viability",
        "security guarantees",
        "development assistance",
    ],
}


def get_strategic_interests(tier: CapabilityTier) -> List[str]:
    """
    Get the objective strategic interests for a capability tier.

    Args:
        tier: The capability tier.

    Returns:
        List of strategic interests.
    """
    return OBJECTIVE_STRATEGIC_INTERESTS.get(tier, [])


def compare_capability(cap1: Capability, cap2: Capability) -> float:
    """
    Compare the capabilities of two agents.

    Args:
        cap1: First agent's capability.
        cap2: Second agent's capability.

    Returns:
        Difference in capability index (cap1 - cap2).
    """
    return cap1.get_capability_index() - cap2.get_capability_index()


def is_power_transition_possible(
    current_capability: Capability,
    target_tier: CapabilityTier,
) -> bool:
    """
    Check if a power transition to the target tier is plausible.

    Args:
        current_capability: Current capability state.
        target_tier: Target capability tier.

    Returns:
        True if transition is plausible, False otherwise.
    """
    current_tier = current_capability.get_tier()
    tier_order = [
        CapabilityTier.T4_SMALL,
        CapabilityTier.T3_MEDIUM,
        CapabilityTier.T2_REGIONAL,
        CapabilityTier.T1_GREAT_POWER,
        CapabilityTier.T0_SUPERPOWER,
    ]

    current_idx = tier_order.index(current_tier)
    target_idx = tier_order.index(target_tier)

    # Allow transitions within 2 tiers (to prevent impossible jumps)
    return abs(current_idx - target_idx) <= 2
