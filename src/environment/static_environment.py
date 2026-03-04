"""
Static environment module for the moral realism ABM system.

This module defines the static base environment including international
system properties, norms, and initial power distribution.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set
import math


class SystemNature(Enum):
    """The nature of the international system."""

    ANARCHIC = "anarchic"  # 无政府状态
    HIERARCHICAL = "hierarchical"  # 等级制
    MIXED = "mixed"  # 混合状态


class SystemArchitecture(Enum):
    """The architecture of the international system."""

    UNIPOLAR = "unipolar"  # 单极
    BIPOLAR = "bipolar"  # 双极
    MULTIPOLAR = "multipolar"  # 多极
    NONPOLAR = "nonpolar"  # 非极化


class NormCategory(Enum):
    """Categories of international norms."""

    SOVEREIGNTY = "sovereignty"  # 主权规范
    FORCE = "force"  # 武力使用规范
    TREATY = "treaty"  # 条约义务规范
    INTERFERENCE = "interference"  # 干预规范


class PatternType(Enum):
    """Types of international power patterns."""

    HEGEMONIC_STABILITY = "hegemonic_stability"  # 霸权稳定
    BALANCE_OF_POWER = "balance_of_power"  # 均势
    POWER_TRANSITION = "power_transition"  # 权力转移
    MULTIPOLAR_BALANCE = "multipolar_balance"  # 多极平衡


@dataclass
class InternationalNorm:
    """Represents an international norm."""

    name: str
    description: str
    category: NormCategory
    authority: float  # 0-100 scale

    def __post_init__(self) -> None:
        """Validate norm authority is in valid range."""
        if not 0 <= self.authority <= 100:
            raise ValueError(f"Norm authority must be between 0 and 100, got {self.authority}")

    def validate(self) -> bool:
        """Validate norm authority is in valid (should always return True if __post_init__ passed)."""
        return 0 <= self.authority <= 100


@dataclass
class PowerDistribution:
    """Represents the distribution of power among agents."""

    agent_ids: List[str]
    power_shares: List[float]  # Share of total power (sum should be 1.0)

    def __post_init__(self) -> None:
        """Validate power distribution."""
        if len(self.agent_ids) != len(self.power_shares):
            raise ValueError("agent_ids and power_shares must have same length")
        total = sum(self.power_shares)
        if not 0.99 <= total <= 1.01:  # Allow small floating point errors
            raise ValueError(f"Power shares must sum to 1.0, got {total}")

    def get_agent_power_share(self, agent_id: str) -> Optional[float]:
        """Get the power share for a specific agent."""
        try:
            idx = self.agent_ids.index(agent_id)
            return self.power_shares[idx]
        except ValueError:
            return None

    def calculate_hhi(self) -> float:
        """Calculate the Herfindahl-Hirschman Index (HHI)."""
        return sum(share * 100 * share * 100 for share in self.power_shares)


class StaticEnvironment:
    """
    Static base environment for the simulation.

    Manages the fixed and relatively stable properties of the international
    system including system nature, architecture, norms, and power distribution.
    """

    def __init__(
        self,
        system_nature: SystemNature = SystemNature.ANARCHIC,
        system_architecture: Optional[SystemArchitecture] = None,
        power_distribution: Optional[PowerDistribution] = None,
    ) -> None:
        """
        Initialize the static environment.

        Args:
            system_nature: The nature of the international system.
            system_architecture: The architecture (will be auto-determined if None).
            power_distribution: Initial power distribution (will be initialized if None).
        """
        self.system_nature = system_nature
        self._system_architecture = system_architecture

        # Initialize norms
        self._norms: List[InternationalNorm] = []
        self._initialize_base_norms()

        # Initialize power distribution
        if power_distribution is None:
            self.power_distribution: Optional[PowerDistribution] = None
        else:
            self.power_distribution = power_distribution

    def _initialize_base_norms(self) -> None:
        """Initialize the base set of international norms."""
        base_norms = [
            # Sovereignty norms
            InternationalNorm(
                name="sovereign_equality",
                description="所有国家主权平等",
                category=NormCategory.SOVEREIGNTY,
                authority=85.0,
            ),
            InternationalNorm(
                name="territorial_integrity",
                description="国家领土完整不可侵犯",
                category=NormCategory.SOVEREIGNTY,
                authority=90.0,
            ),
            InternationalNorm(
                name="political_independence",
                description="国家政治独立自主",
                category=NormCategory.SOVEREIGNTY,
                authority=80.0,
            ),
            # Force norms
            InternationalNorm(
                name="prohibition_of_force",
                description="禁止在国际关系中使用武力",
                category=NormCategory.FORCE,
                authority=75.0,
            ),
            InternationalNorm(
                name="self_defense",
                description="国家享有单独或集体自卫的固有权利",
                category=NormCategory.FORCE,
                authority=95.0,
            ),
            InternationalNorm(
                name="non_proliferation",
                description="防止大规模杀伤性武器扩散",
                category=NormCategory.FORCE,
                authority=70.0,
            ),
            # Treaty norms
            InternationalNorm(
                name="pacta_sunt_servanda",
                description="条约必须遵守",
                category=NormCategory.TREATY,
                authority=80.0,
            ),
            InternationalNorm(
                name="good_faith",
                description="善意履行国际义务",
                category=NormCategory.TREATY,
                authority=75.0,
            ),
            # Interference norms
            InternationalNorm(
                name="non_interference",
                description="不干涉内政原则",
                category=NormCategory.INTERFERENCE,
                authority=65.0,
            ),
            InternationalNorm(
                name="humanitarian_intervention",
                description="人道主义干预例外情况",
                category=NormCategory.INTERFERENCE,
                authority=40.0,
            ),
        ]

        self._norms = base_norms

    def initialize_power_distribution(
        self,
        architecture: SystemArchitecture,
        agent_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize power distribution based on system architecture.

        Args:
            architecture: The desired system architecture.
            agent_ids: List of agent IDs. If None, uses provided architecture
                        to create a default distribution.
        """
        self._system_architecture = architecture

        if agent_ids is None:
            # Create default agent IDs based on architecture
            if architecture == SystemArchitecture.UNIPOLAR:
                agent_ids = ["hegemon", "state1", "state2", "state3"]
            elif architecture == SystemArchitecture.BIPOLAR:
                agent_ids = ["pole1", "pole2", "state1", "state2"]
            else:  # MULTIPOLAR or NONPOLAR
                agent_ids = ["great1", "great2", "great3", "state1", "state2", "state3"]

        # Create power shares based on architecture
        if architecture == SystemArchitecture.UNIPOLAR:
            # Hegemon has dominant power
            power_shares = [0.50, 0.15, 0.20, 0.15]
        elif architecture == SystemArchitecture.BIPOLAR:
            # Two poles with roughly equal power
            power_shares = [0.35, 0.35, 0.15, 0.15]
        elif architecture == SystemArchitecture.MULTIPOLAR:
            # Multiple great powers with balanced power
            n_great = min(3, len(agent_ids) - 1)
            great_share = 0.6 / n_great
            remaining_agents = len(agent_ids) - n_great
            small_share = 0.4 / remaining_agents if remaining_agents > 0 else 0
            power_shares = [great_share] * n_great + [small_share] * remaining_agents
        else:  # NONPOLAR
            # Relatively evenly distributed
            n = len(agent_ids)
            power_shares = [1.0 / n] * n

        # Adjust if agent count differs
        if len(agent_ids) != len(power_shares):
            if len(agent_ids) > len(power_shares):
                # Add small shares
                extra = len(agent_ids) - len(power_shares)
                power_shares.extend([0.05] * extra)
                # Normalize
                total = sum(power_shares)
                power_shares = [s / total for s in power_shares]
            else:
                # Trim and normalize
                power_shares = power_shares[: len(agent_ids)]
                total = sum(power_shares)
                power_shares = [s / total for s in power_shares]

        self.power_distribution = PowerDistribution(
            agent_ids=agent_ids,
            power_shares=power_shares,
        )

    def calculate_pattern_type(self) -> PatternType:
        """
        Calculate the type of international power pattern.

        Returns:
            The pattern type based on current power distribution.
        """
        if self.power_distribution is None:
            return PatternType.BALANCE_OF_POWER

        hhi = self.power_distribution.calculate_hhi()
        max_share = max(self.power_distribution.power_shares)

        if hhi > 3000 or max_share > 0.45:
            return PatternType.HEGEMONIC_STABILITY
        elif 1500 <= hhi <= 2500 and max_share > 0.30:
            return PatternType.POWER_TRANSITION
        elif 1500 <= hhi <= 2500:
            return PatternType.BALANCE_OF_POWER
        else:
            return PatternType.MULTIPOLAR_BALANCE

    def calculate_power_concentration(self) -> Dict[str, float]:
        """
        Calculate power concentration metrics.

        Returns:
            Dictionary containing various concentration metrics:
            - hhi: Herfindahl-Hirschman Index
            - top1_share: Share of top power holder
            - top3_share: Share of top 3 power holders
            - gini: Gini coefficient
        """
        if self.power_distribution is None:
            return {"hhi": 0.0, "top1_share": 0.0, "top3_share": 0.0, "gini": 0.0}

        shares = sorted(self.power_distribution.power_shares, reverse=True)

        # HHI
        hhi = self.power_distribution.calculate_hhi()

        # Top 1 share
        top1_share = shares[0] if shares else 0.0

        # Top 3 share
        top3_share = sum(shares[:3])

        # Gini coefficient
        n = len(shares)
        if n == 0:
            gini = 0.0
        elif n == 1:
            gini = 0.0
        else:
            shares_sorted = sorted(shares)
            cumulative = 0.0
            for i, share in enumerate(shares_sorted):
                cumulative += (i + 1) * share
            gini = (2 * cumulative - n - 1) / n

        return {
            "hhi": hhi,
            "top1_share": top1_share,
            "top3_share": top3_share,
            "gini": gini,
        }

    def get_norms_by_category(self, category: NormCategory) -> List[InternationalNorm]:
        """
        Get norms by category.

        Args:
            category: The norm category.

        Returns:
            List of norms in the specified category.
        """
        return [norm for norm in self._norms if norm.category == category]

    def get_norm(self, name: str) -> Optional[InternationalNorm]:
        """
        Get a specific norm by name.

        Args:
            name: The norm name.

        Returns:
            The norm if found, None otherwise.
        """
        for norm in self._norms:
            if norm.name == name:
                return norm
        return None

    @property
    def system_architecture(self) -> Optional[SystemArchitecture]:
        """Get the system architecture."""
        return self._system_architecture

    @property
    def norms(self) -> List[InternationalNorm]:
        """Get all international norms."""
        return self._norms.copy()

    def add_norm(self, norm: InternationalNorm) -> None:
        """
        Add a new norm to the environment.

        Args:
            norm: The norm to add.
        """
        norm.validate()
        self._norms.append(norm)

    def remove_norm(self, name: str) -> bool:
        """
        Remove a norm from the environment.

        Args:
            name: The norm name to remove.

        Returns:
            True if norm was removed, False if not found.
        """
        for i, norm in enumerate(self._norms):
            if norm.name == name:
                self._norms.pop(i)
                return True
        return False

    def update_norm_authority(self, name: str, new_authority: float) -> bool:
        """
        Update the authority of a norm.

        Args:
            name: The norm name.
            new_authority: The new authority level (0-100).

        Returns:
            True if norm was updated, False if not found.
        """
        norm = self.get_norm(name)
        if norm:
            norm.authority = new_authority
            norm.validate()
            return True
        return False

    def get_system_summary(self) -> Dict:
        """
        Get a summary of the static environment.

        Returns:
            Dictionary containing system properties.
        """
        return {
            "system_nature": self.system_nature.value if self.system_nature else None,
            "system_architecture": self._system_architecture.value if self._system_architecture else None,
            "norm_count": len(self._norms),
            "pattern_type": self.calculate_pattern_type().value,
            "power_concentration": self.calculate_power_concentration(),
        }
