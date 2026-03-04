"""
Metrics calculator for the moral realism ABM system.

This module provides MetricsCalculator which computes all simulation metrics
including agent-level metrics (capability, moral, success) and system-level
metrics (power concentration, order stability, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.environment.rule_environment import RuleEnvironment, MoralDimension
from src.models.agent import Agent
from src.models.capability import Capability, CapabilityTier


@dataclass
class AgentMetrics:
    """Metrics for a single agent."""

    agent_id: str
    name: str
    leadership_type: str
    capability_metrics: Dict[str, Any] = field(default_factory=dict)
    moral_metrics: Dict[str, Any] = field(default_factory=dict)
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    history_timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "leadership_type": self.leadership_type,
            "capability_metrics": self.capability_metrics,
            "moral_metrics": self.moral_metrics,
            "success_metrics": self.success_metrics,
            "history_timestamp": self.history_timestamp.isoformat(),
        }


@dataclass
class SystemMetrics:
    """System-level metrics for the simulation."""

    pattern_type: str  # unipolar, bipolar, multipolar
    power_concentration: float  # HHI index (0-1)
    order_stability: float  # 0-100 scale
    norm_consensus: float  # 0-100 scale
    public_goods_level: float  # 0-100 scale
    order_type: str  # OrderType enum value
    analysis_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_type": self.pattern_type,
            "power_concentration": self.power_concentration,
            "order_stability": self.order_stability,
            "norm_consensus": self.norm_consensus,
            "public_goods_level": self.public_goods_level,
            "order_type": self.order_type,
            "analysis_details": self.analysis_details,
        }


class MetricsCalculator:
    """
    Calculate all simulation metrics.

    This class coordinates calculation of agent-level and system-level metrics,
    integrating data from multiple sources including agents, rule environment,
    and interaction history.
    """

    def __init__(
        self,
        rule_environment: Optional[RuleEnvironment] = None,
    ) -> None:
        """
        Initialize the metrics calculator.

        Args:
            rule_environment: Rule environment for moral evaluation.
        """
        self.rule_environment = rule_environment or RuleEnvironment()

    def calculate_all_metrics(
        self,
        agents: Dict[str, Agent],
        state: Optional[Dict[str, Any]] = None,
        round_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate all metrics for the current simulation state.

        Args:
            agents: Dictionary mapping agent IDs to Agent instances.
            state: Simulation state dictionary.
            round_result: Results from the current round.

        Returns:
            Dictionary containing all metrics.
        """
        state = state or {}
        round_result = round_result or {}

        # Calculate agent metrics
        agent_metrics = {}
        for agent_id, agent in agents.items():
            agent_metrics[agent_id] = self._calculate_agent_metrics(
                agent,
                self.rule_environment,
                state,
                round_result,
            )

        # Calculate system metrics
        agent_list = list(agents.values())
        system_metrics = self._calculate_system_metrics(
            agent_list,
            self.rule_environment,
            state,
            round_result,
        )

        # Determine pattern type
        pattern_type = self._calculate_pattern_type(agent_list)

        return {
            "timestamp": datetime.now().isoformat(),
            "round": round_result.get("round", 0),
            "agent_metrics": {
                agent_id: metrics.to_dict()
                for agent_id, metrics in agent_metrics.items()
            },
            "system_metrics": system_metrics.to_dict(),
            "pattern_type": pattern_type,
            "agent_count": len(agents),
        }

    def _calculate_agent_metrics(
        self,
        agent: Agent,
        rule_env: RuleEnvironment,
        state: Dict[str, Any],
        round_result: Dict[str, Any],
    ) -> AgentMetrics:
        """
        Calculate metrics for a single agent.

        Args:
            agent: The agent to calculate metrics for.
            rule_env: Rule environment for moral evaluation.
            state: Simulation state.
            round_result: Current round results.

        Returns:
            AgentMetrics instance.
        """
        # Capability metrics
        capability_metrics = self._calculate_capability_metrics(agent)

        # Moral metrics
        moral_metrics = self._calculate_moral_metrics(agent, rule_env, state, round_result)

        # Success metrics
        success_metrics = self._calculate_success_metrics(agent, state, round_result)

        return AgentMetrics(
            agent_id=agent.agent_id,
            name=agent.name,
            leadership_type=agent.leadership_type.value,
            capability_metrics=capability_metrics,
            moral_metrics=moral_metrics,
            success_metrics=success_metrics,
        )

    def _calculate_capability_metrics(self, agent: Agent) -> Dict[str, Any]:
        """
        Calculate capability metrics for an agent.

        Args:
            agent: The agent.

        Returns:
            Dictionary of capability metrics.
        """
        if agent.capability is None:
            return {
                "hard_power_index": 0.0,
                "soft_power_index": 0.0,
                "capability_index": 0.0,
                "tier": "unknown",
            }

        hard_power = agent.capability.hard_power
        soft_power = agent.capability.soft_power

        return {
            "hard_power_index": hard_power.get_hard_power_index(),
            "soft_power_index": soft_power.get_soft_power_index(),
            "capability_index": agent.capability.get_capability_index(),
            "tier": agent.capability.get_tier().value,
            "hard_power_details": {
                "military_capability": hard_power.military_capability,
                "nuclear_capability": hard_power.nuclear_capability,
                "conventional_forces": hard_power.conventional_forces,
                "force_projection": hard_power.force_projection,
                "gdp_share": hard_power.gdp_share,
                "economic_growth": hard_power.economic_growth,
                "trade_volume": hard_power.trade_volume,
                "financial_influence": hard_power.financial_influence,
                "technology_level": hard_power.technology_level,
                "military_technology": hard_power.military_technology,
                "innovation_capacity": hard_power.innovation_capacity,
            },
            "soft_power_details": {
                "discourse_power": soft_power.discourse_power,
                "narrative_control": soft_power.narrative_control,
                "media_influence": soft_power.media_influence,
                "allies_count": soft_power.allies_count,
                "ally_strength": soft_power.ally_strength,
                "network_position": soft_power.network_position,
                "diplomatic_support": soft_power.diplomatic_support,
                "moral_legitimacy": soft_power.moral_legitimacy,
                "cultural_influence": soft_power.cultural_influence,
                "un_influence": soft_power.un_influence,
                "institutional_leadership": soft_power.institutional_leadership,
            },
        }

    def _calculate_moral_metrics(
        self,
        agent: Agent,
        rule_env: RuleEnvironment,
        state: Dict[str, Any],
        round_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate moral metrics for an agent.

        Args:
            agent: The agent.
            rule_env: Rule environment.
            state: Simulation state.
            round_result: Current round results.

        Returns:
            Dictionary of moral metrics.
        """
        # Get actions from agent history
        history = agent.get_history()
        actions = []
        for entry in history:
            if entry.metadata:
                actions.append({
                    "type": entry.event_type,
                    "content": entry.content,
                    **entry.metadata,
                })

        # Evaluate moral level using rule environment
        moral_evaluations = rule_env.evaluate_moral_level(
            agent_id=agent.agent_id,
            actions=actions,
            interactions=[],  # Will be populated from interaction manager later
        )

        # Calculate overall moral index
        moral_index = rule_env.calculate_moral_level_index(moral_evaluations)

        # Build dimension scores
        dimension_scores = {
            eval.dimension.value: {
                "score": eval.score,
                "justification": eval.justification,
            }
            for eval in moral_evaluations
        }

        return {
            "moral_index": moral_index,
            "dimension_scores": dimension_scores,
            "respect_for_norms": dimension_scores.get("respect_for_norms", {}).get("score", 50.0),
            "humanitarian_concern": dimension_scores.get("humanitarian_concern", {}).get("score", 50.0),
            "peaceful_resolution": dimension_scores.get("peaceful_resolution", {}).get("score", 50.0),
            "international_cooperation": dimension_scores.get("international_cooperation", {}).get("score", 50.0),
            "justice_and_fairness": dimension_scores.get("justice_and_fairness", {}).get("score", 50.0),
        }

    def _calculate_success_metrics(
        self,
        agent: Agent,
        state: Dict[str, Any],
        round_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate success metrics for an agent.

        Args:
            agent: The agent.
            state: Simulation state.
            round_result: Current round results.

        Returns:
            Dictionary of success metrics.
        """
        # Count successful actions from history
        history = agent.get_history()
        total_actions = len(history)
        successful_actions = sum(
            1 for entry in history
            if entry.metadata.get("success", True) if entry.metadata
        )

        success_rate = successful_actions / total_actions if total_actions > 0 else 1.0

        # Calculate relationship quality
        total_relations = len(agent.relations)
        if total_relations > 0:
            avg_relationship = sum(agent.relations.values()) / total_relations
        else:
            avg_relationship = 0.0

        friendly_count = sum(1 for score in agent.relations.values() if score > 0.3)
        hostile_count = sum(1 for score in agent.relations.values() if score < -0.3)

        return {
            "success_rate": success_rate,
            "total_actions": total_actions,
            "successful_actions": successful_actions,
            "avg_relationship": avg_relationship,
            "friendly_relations": friendly_count,
            "hostile_relations": hostile_count,
            "neutral_relations": total_relations - friendly_count - hostile_count,
        }

    def _calculate_system_metrics(
        self,
        agents: List[Agent],
        rule_env: RuleEnvironment,
        state: Dict[str, Any],
        round_result: Dict[str, Any],
    ) -> SystemMetrics:
        """
        Calculate system-level metrics.

        Args:
            agents: List of all agents.
            rule_env: Rule environment.
            state: Simulation state.
            round_result: Current round results.

        Returns:
            SystemMetrics instance.
        """
        if not agents:
            return SystemMetrics(
                pattern_type="empty",
                power_concentration=0.0,
                order_stability=0.0,
                norm_consensus=0.0,
                public_goods_level=0.0,
                order_type="anarchic_disorder",
            )

        # Calculate power distribution
        power_distribution = self._get_power_distribution(agents)

        # Power concentration (HHI)
        power_concentration = self._calculate_power_concentration(agents)

        # Order stability
        order_stability = self._calculate_order_stability(agents, rule_env)

        # Norm consensus
        norm_consensus = self._calculate_norm_consensus(agents, rule_env)

        # Public goods level
        public_goods_level = self._calculate_public_goods_level(agents, rule_env)

        # Check order evolution
        norm_authorities = {
            "respect_for_norms": norm_consensus,
            "international_law": norm_consensus,
        }
        conflict_levels = self._get_conflict_levels(agents)

        order_type, analysis_details = rule_env.check_order_evolution(
            power_distribution=power_distribution,
            norm_authorities=norm_authorities,
            conflict_levels=conflict_levels,
        )

        return SystemMetrics(
            pattern_type=self._calculate_pattern_type(agents),
            power_concentration=power_concentration,
            order_stability=order_stability,
            norm_consensus=norm_consensus,
            public_goods_level=public_goods_level,
            order_type=order_type.value,
            analysis_details={
                "order_analysis": analysis_details,
                "power_distribution": power_distribution,
            },
        )

    def _get_power_distribution(self, agents: List[Agent]) -> Dict[str, float]:
        """
        Calculate power distribution as shares.

        Args:
            agents: List of agents.

        Returns:
            Dictionary mapping agent IDs to power shares (0-1).
        """
        total_power = 0.0
        powers = {}

        for agent in agents:
            if agent.capability:
                power = agent.capability.get_capability_index()
            else:
                power = 0.0
            powers[agent.agent_id] = power
            total_power += power

        # Normalize to shares
        if total_power > 0:
            return {
                agent_id: power / total_power
                for agent_id, power in powers.items()
            }
        return powers

    def _get_conflict_levels(self, agents: List[Agent]) -> Dict[str, float]:
        """
        Calculate conflict levels between agents.

        Args:
            agents: List of agents.

        Returns:
            Dictionary mapping agent pairs to conflict levels.
        """
        conflict_levels = {}
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i + 1:]:
                # Conflict level is inversely related to relationship score
                relationship = agent1.get_relationship(agent2.agent_id)
                conflict = (1.0 - relationship) * 50  # Scale to 0-100
                key = f"{agent1.agent_id}_{agent2.agent_id}"
                conflict_levels[key] = conflict

        return conflict_levels

    def _calculate_pattern_type(self, agents: List[Agent]) -> str:
        """
        Determine the international system pattern type.

        Args:
            agents: List of agents.

        Returns:
            Pattern type: "unipolar", "bipolar", or "multipolar".
        """
        if not agents:
            return "empty"

        # Sort agents by capability
        agent_powers = []
        for agent in agents:
            if agent.capability:
                power = agent.capability.get_capability_index()
            else:
                power = 0.0
            agent_powers.append((agent.agent_id, power))

        agent_powers.sort(key=lambda x: x[1], reverse=True)

        if len(agent_powers) < 2:
            return "unipolar"

        # Check for unipolar: one agent has > 50% of power
        total_power = sum(power for _, power in agent_powers)
        top_power = agent_powers[0][1]

        if total_power > 0 and top_power / total_power > 0.5:
            return "unipolar"

        # Check for bipolar: top two agents have > 70% and similar power
        top_two_power = agent_powers[0][1] + agent_powers[1][1]

        if total_power > 0 and top_two_power / total_power > 0.7:
            # Check if top two are roughly equal (within 20%)
            ratio = min(agent_powers[0][1], agent_powers[1][1]) / max(agent_powers[0][1], agent_powers[1][1])
            if ratio > 0.8:
                return "bipolar"

        # Otherwise multipolar
        return "multipolar"

    def _calculate_power_concentration(self, agents: List[Agent]) -> float:
        """
        Calculate power concentration using HHI (Herfindahl-Hirschman Index).

        Args:
            agents: List of agents.

        Returns:
            HHI index (0-1), where higher values indicate more concentration.
        """
        if not agents:
            return 0.0

        power_distribution = self._get_power_distribution(agents)

        # HHI = sum of squared market shares
        hhi = sum(share ** 2 for share in power_distribution.values())

        return hhi

    def _calculate_order_stability(self, agents: List[Agent], rule_env: RuleEnvironment) -> float:
        """
        Calculate order stability score.

        Args:
            agents: List of agents.
            rule_env: Rule environment.

        Returns:
            Stability score (0-100).
        """
        if not agents:
            return 0.0

        # Factors contributing to stability:
        # 1. Low conflict levels
        # 2. High norm consensus
        # 3. Stable power distribution (not too concentrated, not too dispersed)

        # Conflict level (inverse of stability contribution)
        conflict_levels = self._get_conflict_levels(agents)
        avg_conflict = sum(conflict_levels.values()) / len(conflict_levels) if conflict_levels else 50
        conflict_factor = (100 - avg_conflict) * 0.3

        # Norm consensus factor
        norm_consensus = self._calculate_norm_consensus(agents, rule_env)
        norm_factor = norm_consensus * 0.4

        # Power distribution factor (moderate concentration is stabilizing)
        power_concentration = self._calculate_power_concentration(agents)
        # Optimal concentration is around 0.25-0.35
        if 0.25 <= power_concentration <= 0.35:
            distribution_factor = 100.0
        else:
            # Penalty for deviation from optimal
            deviation = abs(power_concentration - 0.3)
            distribution_factor = 100.0 - deviation * 100

        stability = conflict_factor + norm_factor + distribution_factor * 0.3
        return max(0.0, min(100.0, stability))

    def _calculate_norm_consensus(self, agents: List[Agent], rule_env: RuleEnvironment) -> float:
        """
        Calculate norm consensus across agents.

        Args:
            agents: List of agents.
            rule_env: Rule environment.

        Returns:
            Consensus score (0-100).
        """
        if not agents:
            return 0.0

        # Calculate average moral index across all agents
        moral_indices = []

        for agent in agents:
            metrics = self._calculate_moral_metrics(agent, rule_env, {}, {})
            moral_indices.append(metrics.get("moral_index", 50.0))

        # Average moral index as proxy for norm consensus
        avg_moral = sum(moral_indices) / len(moral_indices) if moral_indices else 50.0

        return max(0.0, min(100.0, avg_moral))

    def _calculate_public_goods_level(self, agents: List[Agent], rule_env: RuleEnvironment) -> float:
        """
        Calculate level of public goods provision.

        Args:
            agents: List of agents.
            rule_env: Rule environment.

        Returns:
            Public goods level (0-100).
        """
        if not agents:
            return 0.0

        # Public goods provision is related to:
        # 1. International cooperation
        # 2. Humanitarian concern
        # 3. Peaceful resolution preference

        cooperation_scores = []
        humanitarian_scores = []
        peaceful_scores = []

        for agent in agents:
            metrics = self._calculate_moral_metrics(agent, rule_env, {}, {})
            cooperation_scores.append(metrics.get("international_cooperation", 50.0))
            humanitarian_scores.append(metrics.get("humanitarian_concern", 50.0))
            peaceful_scores.append(metrics.get("peaceful_resolution", 50.0))

        avg_cooperation = sum(cooperation_scores) / len(cooperation_scores) if cooperation_scores else 50.0
        avg_humanitarian = sum(humanitarian_scores) / len(humanitarian_scores) if humanitarian_scores else 50.0
        avg_peaceful = sum(peaceful_scores) / len(peaceful_scores) if peaceful_scores else 50.0

        # Weighted average
        public_goods_level = (
            avg_cooperation * 0.4 +
            avg_humanitarian * 0.3 +
            avg_peaceful * 0.3
        )

        return max(0.0, min(100.0, public_goods_level))
