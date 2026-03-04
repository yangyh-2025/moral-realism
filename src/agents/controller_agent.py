"""
Controller agent implementation for moral realism ABM system.

This module implements ControllerAgent class which manages simulation
workflow and orchestrates agent interactions.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability


logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for simulation parameters."""

    max_rounds: int = 100
    event_probability: float = 0.2
    checkpoint_interval: int = 10
    checkpoint_dir: str = "./data/checkpoints"
    log_level: str = "INFO"


@dataclass
class ControllerState:
    """State tracking for controller agent."""

    current_round: int = 0
    is_running: bool = False
    is_paused: bool = False
    total_decisions: int = 0
    total_interactions: int = 0
    event_count: int = 0


@dataclass
class ControllerAgent(Agent):
    """
    A controller agent that manages simulation workflow and
    orchestrates agent interactions.
    """

    # Simulation configuration
    config: SimulationConfig = field(default_factory=SimulationConfig)

    # Controller state tracking
    state: ControllerState = field(default_factory=ControllerState)

    # Agent management
    great_powers: Dict[str, Any] = field(default_factory=dict)
    small_states: Dict[str, Any] = field(default_factory=dict)
    organizations: Dict[str, Any] = field(default_factory=dict)
    all_agents: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize agent after dataclass initialization."""
        self.agent_type = AgentType.CONTROLLER

        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        self.relations[self.agent_id] = 1.0

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make simulation control decisions."""
        if context is None:
            context = {}

        action = situation.get("action", "continue")
        decision = {
            "agent_id": self.agent_id,
            "action": action,
            "rationale": f"Controller decision: {action}",
            "current_round": self.state.current_round,
            "is_running": self.state.is_running,
        }

        self.add_history("decision", f"Decided to {action}", metadata={"decision": decision})
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Respond to simulation control messages."""
        if context is None:
            context = {}

        message_type = message.get("type", "unknown")

        content = f"Controller acknowledges {message_type} from {sender_id}."

        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": "acknowledgment",
            "current_round": self.state.current_round,
        }

        self.add_history("response", f"Responded to {sender_id}", metadata={"response": response})
        return response
        return response

    def _create_agent(self, agent_config: Dict[str, Any]) -> None:
        """Create an agent instance from configuration."""
        agent_type = agent_config.get("agent_type")
        agent_id = agent_config.get("agent_id")

        if agent_type == "great_power":
            from src.agents.great_power_agent import GreatPowerAgent

            agent = GreatPowerAgent(
                agent_id=agent_id,
                name=agent_config.get("name", agent_id),
                name_zh=agent_config.get("name_zh", agent_id),
                leadership_type=LeadershipType(agent_config.get("leadership_type", "wangdao")),
            )
            self.great_powers[agent_id] = agent
            self.all_agents[agent_id] = agent

        elif agent_type == "small_state":
            from src.agents.small_state_agent import SmallStateAgent

            agent = SmallStateAgent(
                agent_id=agent_id,
                name=agent_config.get("name", agent_id),
                name_zh=agent_config.get("name_zh", agent_id),
                leadership_type=LeadershipType(agent_config.get("leadership_type", "hunyong")),
            )
            self.small_states[agent_id] = agent
            self.all_agents[agent_id] = agent

        elif agent_type == "organization":
            from src.agents.organization_agent import (
                OrganizationAgent,
                OrganizationType,
                DecisionRule,
            )

            org_type_str = agent_config.get("org_type", "global")
            org_type = OrganizationType(org_type_str)

            decision_rule_str = agent_config.get("decision_rule", "consensus")
            decision_rule = DecisionRule(decision_rule_str)

            agent = OrganizationAgent(
                agent_id=agent_id,
                name=agent_config.get("name", agent_id),
                name_zh=agent_config.get("name_zh", agent_id),
                leadership_type=LeadershipType(agent_config.get("leadership_type", "hegemon")),
                org_type=org_type,
                decision_rule=decision_rule,
            )
            self.organizations[agent_id] = agent
            self.all_agents[agent_id] = agent

    def start_simulation(self) -> None:
        """Start simulation."""
        self.state.is_running = True
        self.state.is_paused = False
        logger.info(f"Simulation started. Max rounds: {self.config.max_rounds}")

    def pause_simulation(self) -> None:
        """Pause simulation."""
        self.state.is_paused = True
        logger.info("Simulation paused")

    def resume_simulation(self) -> None:
        """Resume simulation."""
        self.state.is_paused = False
        logger.info("Simulation resumed")

    def stop_simulation(self) -> None:
        """Stop simulation."""
        self.state.is_running = False
        self.state.is_paused = False
        logger.info("Simulation stopped")

    def execute_round(self) -> None:
        """Execute a single simulation round."""
        if not self.state.is_running or self.state.is_paused:
            return

        # Increment round
        self.state.current_round += 1

        # Execute agent decisions
        for agent_id, agent in self.all_agents.items():
            situation = {"round": self.state.current_round}
            available_actions = []
            context = {
                "agents": {aid: a.get_summary() for aid, a in self.all_agents.items()},
                "great_powers": {
                    aid: {"leadership_type": a.leadership_type.value, "name": a.name}
                    for aid, a in self.great_powers.items()
                },
            }

            decision = agent.decide(situation, available_actions, context)
            self.state.total_decisions += 1

        logger.info(f"Round {self.state.current_round} completed")

    def advance_round(self) -> None:
        """Advance to next round."""
        self.state.current_round += 1
        logger.info(f"Advanced to round {self.state.current_round}")

    def get_simulation_state(self) -> Dict[str, Any]:
        """Get complete simulation state summary."""
        return {
            "current_round": self.state.current_round,
            "max_rounds": self.config.max_rounds,
            "is_running": self.state.is_running,
            "is_paused": self.state.is_paused,
            "great_power_count": len(self.great_powers),
            "small_state_count": len(self.small_states),
            "organization_count": len(self.organizations),
            "total_agents": len(self.all_agents),
            "total_decisions": self.state.total_decisions,
            "total_interactions": self.state.total_interactions,
            "event_count": self.state.event_count,
        }
