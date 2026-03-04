"""
Systemic interaction layer for moral realism ABM system.

This module implements SystemicInteractionManager class which handles
system-level interactions including international order shaping,
norm evolution, and values competition.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType


logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Types of international orders."""

    MULTIPOLAR = "multipolar"  # 多极
    BIPOLAR = "bipolar"  # 两极
    UNIPOLAR_HEGEMONIC = "unipolar_hegemonic"  # 单极霸权
    HIERARCHICAL = "hierarchical"  # 等级秩序


@dataclass
class Norm:
    """Represents an international norm."""

    norm_id: str
    name: str
    description: str
    category: str  # security, economic, human_rights, etc.
    strength: float  # 0-1, how strongly held
    originator: Optional[str] = None  # agent_id of originating great power
    adoption_level: float = 0.0  # 0-1, level of international adoption
    date_created: datetime = field(default_factory=datetime.now)
    date_modified: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "norm_id": self.norm_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "strength": self.strength,
            "originator": self.originator,
            "adoption_level": self.adoption_level,
            "date_created": self.date_created.isoformat(),
            "date_modified": self.date_modified.isoformat() if self.date_modified else None,
        }


@dataclass
class SystemicEvent:
    """Represents a system-level event."""

    event_id: str
    event_type: str
    description: str
    participants: List[str]
    impact_level: float  # 0-1, systemic impact
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "description": self.description,
            "participants": self.participants,
            "impact_level": self.impact_level,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class SystemicInteractionManager:
    """
    Manages system-level interactions in the ABM simulation.

    Handles:
    - International order shaping
    - Norm evolution and diffusion
    - Values competition
    - Institutional reforms
    """

    def __init__(
        self,
        enable_logging: bool = True,
    ) -> None:
        """
        Initialize systemic interaction manager.

        Args:
            enable_logging: Whether to enable detailed logging.
        """
        self._agents: Dict[str, Agent] = {}
        self._norms: Dict[str, Norm] = {}
        self._systemic_events: List[SystemicEvent] = []
        self._order_history: List[Dict[str, Any]] = []

        self._enable_logging = enable_logging
        self._event_counter = 0

        # Base norms
        self._initialize_base_norms()

    def _initialize_base_norms(self) -> None:
        """Initialize base international norms."""
        base_norms = [
            Norm(
                norm_id="norm_sovereignty",
                name="Sovereignty",
                description="Respect for national sovereignty and territorial integrity",
                category="security",
                strength=0.8,
                adoption_level=0.9,
            ),
            Norm(
                norm_id="norm_non_aggression",
                name="Non-Aggression",
                description="Prohibition of use of force except in self-defense",
                category="security",
                strength=0.85,
                adoption_level=0.85,
            ),
            Norm(
                norm_id="norm_self_determination",
                name="Self-Determination",
                description="Right of peoples to self-determination",
                category="human_rights",
                strength=0.75,
                adoption_level=0.8,
            ),
            Norm(
                norm_id="norm_free_trade",
                name="Free Trade",
                description="Promotion of free and fair trade",
                category="economic",
                strength=0.7,
                adoption_level=0.75,
            ),
            Norm(
                norm_id="norm_human_rights",
                name="Human Rights",
                description="Universal human rights and fundamental freedoms",
                category="human_rights",
                strength=0.8,
                adoption_level=0.8,
            ),
        ]

        for norm in base_norms:
            self._norms[norm.norm_id] = norm

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with systemic manager.

        Args:
            agent: The agent to register.
        """
        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent for systemic interaction: {agent.name}")

    def shape_international_order(
        self,
        round_id: int,
    ) -> Dict[str, Any]:
        """
        Simulate international order shaping by great powers.

        Leadership types influence order shaping:
        - Wangdao: Promotes multipolar, rules-based order
        - Hegemon: Maintains hegemonic order with institutional control
        - Qiangquan: Seeks power concentration and hegemonic order
        - Hunyong: Tends to support status quo

        Args:
            round_id: Current simulation round.

        Returns:
            Dictionary with order analysis and changes.
        """
        # Get all great powers
        great_powers = [
            agent for agent in self._agents.values()
            if agent.agent_type == AgentType.GREAT_POWER
        ]

        if not great_powers:
            return {"order_type": "undefined", "power_distribution": {}}

        # Analyze power distribution
        power_indices = {
            gp.agent_id: gp.capability.get_capability_index() if gp.capability else 50
            for gp in great_powers
        }

        # Determine order type based on power distribution and leadership
        order_type = self._determine_order_type(great_powers, power_indices)

        # Order characteristics
        order_characteristics = self._analyze_order_characteristics(
            great_powers, order_type
        )

        # Record order
        order_record = {
            "round": round_id,
            "order_type": order_type.value,
            "power_indices": power_indices,
            "characteristics": order_characteristics,
            "timestamp": datetime.now().isoformat(),
        }

        self._order_history.append(order_record)

        if self._enable_logging:
            logger.info(
                f"Round {round_id}: International order type = {order_type.value}"
            )

        return order_record

    def _determine_order_type(
        self,
        great_powers: List[Agent],
        power_indices: Dict[str, float],
    ) -> OrderType:
        """
        Determine current international order type.

        Args:
            great_powers: List of great power agents.
            power_indices: Power capability indices.

        Returns:
            The order type.
        """
        if len(great_powers) < 2:
            return OrderType.UNIPOLAR_HEGEMONIC

        # Calculate power concentration
        total_power = sum(power_indices.values())
        max_power = max(power_indices.values())
        power_concentration = max_power / total_power

        # Analyze leadership types
        leadership_types = [
            gp.leadership_type.value if gp.leadership_profile else "unknown"
            for gp in great_powers
        ]

        # Check for hegemon
        if power_concentration > 0.5:
            return OrderType.UNIPOLAR_HEGEMONIC

        # Check for bipolar
        sorted_powers = sorted(power_indices.values(), reverse=True)
        if len(sorted_powers) >= 2 and sorted_powers[0] > sorted_powers[1] * 1.5:
            return OrderType.BIPOLAR

        # Check for multipolar (multiple relatively balanced powers)
        if power_concentration < 0.4 and len(great_powers) >= 3:
            return OrderType.MULTIPOLAR

        # Default: hierarchical
        return OrderType.HIERARCHICAL

    def _analyze_order_characteristics(
        self,
        great_powers: List[Agent],
        order_type: OrderType,
    ) -> Dict[str, Any]:
        """
        Analyze characteristics of the current order.

        Args:
            great_powers: List of great power agents.
            order_type: The order type.

        Returns:
            Dictionary with order characteristics.
        """
        characteristics = {
            "order_type": order_type.value,
            "stability": 0.5,  # Will be calculated
            "norm_consensus": 0.5,  # Will be calculated
            "conflict_level": 0.3,  # Will be calculated
        }

        # Calculate stability based on leadership type distribution
        leadership_profiles = {}
        for gp in great_powers:
            if gp.leadership_profile:
                lt = gp.leadership_profile.leadership_type.value
                leadership_profiles[lt] = leadership_profiles.get(lt, 0) + 1

        total = sum(leadership_profiles.values())

        # Wangdao leadership increases stability
        wangdao_ratio = leadership_profiles.get("wangdao", 0) / total if total > 0 else 0
        hunyong_ratio = leadership_profiles.get("hunyong", 0) / total if total > 0 else 0

        characteristics["stability"] = 0.5 + wangdao_ratio * 0.3 + hunyong_ratio * 0.2

        # Calculate norm consensus
        characteristics["norm_consensus"] = self._calculate_norm_consensus(leadership_profiles)

        # Calculate conflict level
        qiangquan_ratio = leadership_profiles.get("qiangquan", 0) / total if total > 0 else 0
        hegemon_ratio = leadership_profiles.get("hegemon", 0) / total if total > 0 else 0

        characteristics["conflict_level"] = qiangquan_ratio * 0.4 + hegemon_ratio * 0.2

        return characteristics

    def _calculate_norm_consensus(
        self,
        leadership_profiles: Dict[str, int],
    ) -> float:
        """
        Calculate norm consensus level.

        Args:
            leadership_profiles: Count of each leadership type.

        Returns:
            Consensus level (0-1).
        """
        total = sum(leadership_profiles.values())
        if total == 0:
            return 0.5

        # Wangdao and Hunyong contribute to norm consensus
        wangdao = leadership_profiles.get("wangdao", 0)
        hunyong = leadership_profiles.get("hunyong", 0)

        return 0.5 + (wangdao + hunyong) / total * 0.3

    def evolve_international_norms(
        self,
        round_id: int,
    ) -> Dict[str, Any]:
        """
        Simulate evolution of international norms.

        Processes:
        - New norm proposals
        - Norm strengthening/weakening
        - Old norm obsolescence
        - Norm diffusion across the system

        Args:
            round_id: Current simulation round.

        Returns:
            Dictionary with norm evolution results.
        """
        evolution_results = {
            "round": round_id,
            "new_norms": [],
            "strengthened_norms": [],
            "weakened_norms": [],
            "obsolete_norms": [],
        }

        # Get norm proposals from great powers
        norm_proposals = self._collect_norm_proposals()

        # Process each proposal
        for proposal in norm_proposals:
            result = self._process_norm_proposal(proposal, round_id)
            evolution_results["new_norms"].append(result)

        # Strengthen/weaken existing norms
        for norm_id, norm in list(self._norms.items()):
            change = self._evaluate_norm_change(norm, round_id)
            if change > 0:
                norm.strength = min(1.0, norm.strength + 0.05)
                evolution_results["strengthened_norms"].append(norm_id)
            elif change < 0:
                norm.strength = max(0.0, norm.strength - 0.05)
                evolution_results["weakened_norms"].append(norm_id)

        # Check for obsolete norms
        obsolete = self._identify_obsolete_norms()
        for norm_id in obsolete:
            norm = self._norms.pop(norm_id)
            evolution_results["obsolete_norms"].append(norm_id)

        if self._enable_logging:
            logger.info(
                f"Round {round_id}: Norm evolution - "
                f"{len(evolution_results['new_norms'])} new, "
                f"{len(evolution_results['strengthened_norms'])} strengthened, "
                f"{len(evolution_results['obsolete_norms'])} obsolete"
            )

        return evolution_results

    def _collect_norm_proposals(self) -> List[Dict[str, Any]]:
        """
        Collect norm proposals from all agents.

        Returns:
            List of norm proposals.
        """
        proposals = []

        for agent in self._agents.values():
            if agent.agent_type != AgentType.GREAT_POWER:
                continue

            # Check agent history for norm proposals
            history = agent.get_history()
            for entry in history[-10:]:  # Last 10 entries
                if entry.event_type == "norm_proposal" or "norm" in str(entry.event_type).lower():
                    if entry.metadata:
                        proposals.append({
                            "agent_id": agent.agent_id,
                            "leadership_type": agent.leadership_type.value,
                            "proposal": entry.metadata,
                        })

        return proposals

    def _process_norm_proposal(
        self,
        proposal: Dict[str, Any],
        round_id: int,
    ) -> Dict[str, Any]:
        """
        Process a norm proposal.

        Args:
            proposal: The norm proposal.
            round_id: Current round.

        Returns:
            Processing result.
        """
        agent_id = proposal.get("agent_id", "")
        leadership_type = proposal.get("leadership_type", "unknown")
        proposal_data = proposal.get("proposal", {})

        # Calculate adoption based on leadership type
        base_adoption = 0.3  # Base adoption level

        if leadership_type == "wangdao":
            base_adoption += 0.4  # Wangdao norms gain traction
        elif leadership_type == "hegemon":
            base_adoption += 0.3  # Hegemon norms also gain traction
        elif leadership_type == "hunyong":
            base_adoption += 0.1  # Hunyong norms struggle
        # Qiangquan norms get no bonus

        # Create new norm
        norm = Norm(
            norm_id=f"norm_{round_id}_{agent_id}_{len(self._norms)}",
            name=proposal_data.get("name", "Unnamed Norm"),
            description=proposal_data.get("description", ""),
            category=proposal_data.get("category", "general"),
            strength=proposal_data.get("strength", 0.5),
            originator=agent_id,
            adoption_level=base_adoption,
        )

        self._norms[norm.norm_id] = norm

        return {
            "norm_id": norm.norm_id,
            "adoption_level": base_adoption,
            "originator": agent_id,
            "leadership_type": leadership_type,
        }

    def _evaluate_norm_change(self, norm: Norm, round_id: int) -> float:
        """
        Evaluate how a norm should change based on system state.

        Args:
            norm: The norm to evaluate.
            round_id: Current round.

        Returns:
            Change amount (-1 to 1).
        """
        # Base change is zero
        change = 0.0

        # Check if originating agent maintains consistency
        if norm.originator:
            agent = self._agents.get(norm.originator)
            if agent and agent.leadership_profile:
                lt = agent.leadership_profile.leadership_type.value

                # Wangdao norms strengthen over time if maintained
                if lt == "wangdao":
                    change += 0.02
                # Hegemon norms may strengthen
                elif lt == "hegemon":
                    change += 0.01
                # Other norms may weaken
                else:
                    change -= 0.01

        # Check recent events affecting norm
        recent_events = [
            e for e in self._systemic_events[-20:]
            if e.timestamp > (datetime.now().timestamp() - 86400)  # Last day
        ]

        norm_violations = sum(
            1 for e in recent_events
            if norm.norm_id in e.description or norm.category in e.event_type
        )

        if norm_violations > 0:
            change -= norm_violations * 0.05

        return change

    def _identify_obsolete_norms(self) -> List[str]:
        """
        Identify norms that have become obsolete.

        Returns:
            List of obsolete norm IDs.
        """
        obsolete = []

        for norm_id, norm in self._norms.items():
            # Norm is obsolete if strength is very low
            if norm.strength < 0.2:
                obsolete.append(norm_id)
                continue

            # Check age (norms over 50 rounds old may be obsolete)
            # Simplified - use strength as primary indicator

        return obsolete

    def simulate_values_competition(
        self,
        round_id: int,
    ) -> Dict[str, Any]:
        """
        Simulate values-based diplomacy and competition.

        Leadership types influence values competition:
        - Wangdao: Promotes universal values, human rights
        - Hegemon: Promotes liberal democratic values
        - Qiangquan: May challenge universal values
        - Hunyong: Avoids values confrontation

        Args:
            round_id: Current simulation round.

        Returns:
            Dictionary with values competition results.
        """
        # Get great powers
        great_powers = [
            agent for agent in self._agents.values()
            if agent.agent_type == AgentType.GREAT_POWER and agent.leadership_profile
        ]

        if not great_powers:
            return {"values_clusters": {}, "conflicts": []}

        # Identify values clusters
        values_clusters = {
            "universal_humanist": [],  # Wangdao-aligned
            "liberal_democratic": [],  # Hegemon-aligned
            "pragmatic_nationalist": [],  # Qiangquan/Hunyong-aligned
        }

        for gp in great_powers:
            lt = gp.leadership_profile.leadership_type.value

            if lt == "wangdao":
                values_clusters["universal_humanist"].append(gp.agent_id)
            elif lt == "hegemon":
                values_clusters["liberal_democratic"].append(gp.agent_id)
            else:
                values_clusters["pragmatic_nationalist"].append(gp.agent_id)

        # Identify values conflicts
        conflicts = self._identify_values_conflicts(great_powers)

        # Create systemic event
        if conflicts:
            event = SystemicEvent(
                event_id=f"values_conflict_{round_id}",
                event_type="values_competition",
                description=f"Values-based competition between clusters",
                participants=[gp.agent_id for gp in great_powers],
                impact_level=len(conflicts) / len(great_powers),
                metadata={
                    "conflicts": conflicts,
                    "clusters": values_clusters,
                },
            )

            self._systemic_events.append(event)

        if self._enable_logging:
            logger.info(
                f"Round {round_id}: Values competition - "
                f"{len(conflicts)} conflicts identified"
            )

        return {
            "round": round_id,
            "values_clusters": values_clusters,
            "conflicts": conflicts,
            "dominant_cluster": self._identify_dominant_cluster(values_clusters),
        }

    def _identify_values_conflicts(
        self,
        great_powers: List[Agent],
    ) -> List[Dict[str, Any]]:
        """
        Identify values conflicts between great powers.

        Args:
            great_powers: List of great power agents.

        Returns:
            List of conflict descriptions.
        """
        conflicts = []

        for i, gp1 in enumerate(great_powers):
            for gp2 in great_powers[i + 1:]:
                if not gp1.leadership_profile or not gp2.leadership_profile:
                    continue

                lt1 = gp1.leadership_profile.leadership_type.value
                lt2 = gp2.leadership_profile.leadership_type.value

                # Check for incompatible leadership types
                incompatible_pairs = [
                    ("wangdao", "qiangquan"),
                    ("qiangquan", "wangdao"),
                ]

                if (lt1, lt2) in incompatible_pairs:
                    conflicts.append({
                        "agent1": gp1.agent_id,
                        "agent2": gp2.agent_id,
                        "type": "values_incompatibility",
                        "description": f"{lt1} vs {lt2} values conflict",
                    })

        return conflicts

    def _identify_dominant_cluster(
        self,
        values_clusters: Dict[str, List[str]],
    ) -> Optional[str]:
        """
        Identify the dominant values cluster.

        Args:
            values_clusters: Values cluster membership.

        Returns:
            Dominant cluster name or None.
        """
        max_size = 0
        dominant = None

        for cluster_name, members in values_clusters.items():
            if len(members) > max_size:
                max_size = len(members)
                dominant = cluster_name

        return dominant

    def get_system_state(self) -> Dict[str, Any]:
        """
        Get current systemic state summary.

        Returns:
            Dictionary with systemic state information.
        """
        return {
            "norms": {k: v.to_dict() for k, v in self._norms.items()},
            "norm_count": len(self._norms),
            "events": [e.to_dict() for e in self._systemic_events[-10:]],
            "recent_events_count": len(self._systemic_events[-10:]),
            "order_history": self._order_history[-5:] if self._order_history else [],
        }

    def get_norm(self, norm_id: str) -> Optional[Norm]:
        """
        Get a specific norm by ID.

        Args:
            norm_id: The norm ID.

        Returns:
            The norm if found, None otherwise.
        """
        return self._norms.get(norm_id)

    def get_all_norms(self) -> List[Norm]:
        """
        Get all current norms.

        Returns:
            List of all norms.
        """
        return list(self._norms.values())

    def get_norms_by_category(self, category: str) -> List[Norm]:
        """
        Get norms filtered by category.

        Args:
            category: The category to filter by.

        Returns:
            List of norms in the category.
        """
        return [
            norm for norm in self._norms.values()
            if norm.category == category
        ]

    def get_systemic_events(
        self,
        limit: Optional[int] = None,
    ) -> List[SystemicEvent]:
        """
        Get systemic events.

        Args:
            limit: Maximum number of events to return.

From Returns:
            List of systemic events.
        """
        if limit:
            return self._systemic_events[-limit:]
        return self._systemic_events.copy()
