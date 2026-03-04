"""
International organization agent implementation for moral realism ABM system.

This module implements OrganizationAgent class which models international
organizations with different governance structures and decision rules.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import logging

from src.models.agent import Agent, AgentType
from src.models.leadership_type import LeadershipType
from src.models.capability import Capability


logger = logging.getLogger(__name__)


class OrganizationType(Enum):
    """Types of international organizations."""

    GLOBAL = "global"
    REGIONAL = "regional"
    SECURITY = "security"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"


class DecisionRule(Enum):
    """Decision-making rules for organizations."""

    CONSENSUS = "consensus"
    MAJORITY = "majority"
    LEADER_DECIDES = "leader_decides"
    COALITION = "coalition"


@dataclass
class OrganizationAgent(Agent):
    """
    An international organization agent that makes decisions based on
    organizational type and leadership characteristics.
    """

    # Organization type
    org_type: OrganizationType = field(default=OrganizationType.GLOBAL)

    # Decision-making rule
    decision_rule: DecisionRule = DecisionRule.CONSENSUS

    # Membership management
    member_ids: List[str] = field(default_factory=list)
    great_power_members: Set[str] = field(default_factory=set)

    # Leadership tracking
    dominant_leader: Optional[str] = None

    # Decision history and state
    paralysis_count: int = 0
    consecutive_paralysis: int = 0

    def __post_init__(self) -> None:
        """Initialize agent after dataclass initialization."""
        self.agent_type = AgentType.ORGANIZATION

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
        """Make a decision based on organizational type and leadership."""
        if context is None:
            context = {}

        # Check for paralysis
        paralysis_info = self._check_paralysis(situation, context)

        if paralysis_info["is_paralyzed"]:
            self.consecutive_paralysis += 1
            self.paralysis_count += 1

            decision = {
                "agent_id": self.agent_id,
                "action": "no_action",
                "rationale": paralysis_info["reason"],
                "paralyzed": True,
                "org_type": self.org_type.value,
                "decision_rule": self.decision_rule.value,
            }
        else:
            self.consecutive_paralysis = 0

            # Get leadership type of dominant leader
            leadership_type_str = self._get_dominant_leadership_type(context)

            # Generate decision based on leadership
            decision = self._generate_leadership_based_decision(
                leadership_type_str, situation, available_actions, context
            )

        self.add_history("decision", f"Decided to {decision['action']}", metadata={"decision": decision})
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Respond to messages based on organizational rules."""
        if context is None:
            context = {}

        message_type = message.get("type", "unknown")

        # Default response based on org type
        if self.org_type == OrganizationType.SECURITY:
            content = f"Security organization acknowledges {message_type} from {sender_id}."
        elif self.org_type == OrganizationType.ECONOMIC:
            content = f"Economic organization acknowledges {message_type} from {sender_id}."
        else:
            content = f"Organization acknowledges {message_type} from {sender_id}."

        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": content,
            "message_type": "acknowledgment",
            "org_type": self.org_type.value,
        }

        self.add_history("response", f"Responded to {sender_id}", metadata={"response": response})
        return response

    def _check_paralysis(
        self,
        situation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Detect organizational paralysis due to conflicting leadership types or lack of consensus.
        """
        agents = context.get("agents", {})

        # Check if leader_decides rule and no leader
        if self.decision_rule == DecisionRule.LEADER_DECIDES and self.dominant_leader is None:
            return {
                "is_paralyzed": True,
                "reason": "Leader-based decision rule but no dominant leader set.",
            }

        # Check for for conflicting leadership types among great power
        great_power_leadership_types = set()
        for gp_id in self.great_power_members:
            agent_info = agents.get(gp_id, {})
            lt = agent_info.get("leadership_type", "unknown")
            if lt != "unknown":
                great_power_leadership_types.add(lt)

        # If 3+ different leadership types, organization is paralyzed
        if len(great_power_leadership_types) >= 3:
            return {
                "is_paralyzed": True,
                "reason": f"Too many conflicting leadership types: {great_power_leadership_types}",
            }

        return {"is_paralyzed": False, "reason": "No paralysis detected"}

    def _generate_leadership_based_decision(
        self,
        leadership_type: str,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate decisions based on specific leadership types."""
        if leadership_type == "wangdao":
            return {
                "agent_id": self.agent_id,
                "action": "provide_public_goods",
                "rationale": "Providing public goods under moral leadership",
                "governance_style": "multilateral",
                "moral_authority": True,
                "org_type": self.org_type.value,
            }
        elif leadership_type == "hegemon":
            return {
                "agent_id": self.agent_id,
                "action": "maintain_order",
                "rationale": "Maintaining international order under hegemonic guidance",
                "governance_style": "hegemon_guided",
                "moral_authority": False,
                "org_type": self.org_type.value,
            }
        elif leadership_type == "qiangquan":
            return {
                "agent_id": self.agent_id,
                "action": "enforce_compliance",
                "rationale": "Enforcing compliance through power",
                "governance_style": "coercive",
                "moral_authority": False,
                "org_type": self.org_type.value,
            }
        else:  # hunyong or unknown
            return {
                "agent_id": self.agent_id,
                "action": "maintain_status_quo",
                "rationale": "Seeking compromise and cooperation",
                "governance_style": "balanced",
                "moral_authority": True,
                "org_type": self.org_type.value,
            }

    def _get_dominant_leadership_type(self, context: Dict[str, Any]) -> str:
        """Get leadership type of dominant leader or fallback."""
        if self.dominant_leader:
            agents = context.get("agents", {})
            agent_info = agents.get(self.dominant_leader, {})
            return agent_info.get("leadership_type", "hunyong")
        return "hunyong"

    def add_member(self, agent_id: str, is_great_power: bool = False) -> None:
        """Add an agent to organization."""
        if agent_id not in self.member_ids:
            self.member_ids.append(agent_id)

        if is_great_power:
            self.great_power_members.add(agent_id)

        # Update relation
        self.set_relationship(agent_id, 0.5)

    def remove_member(self, agent_id: str) -> None:
        """Remove an agent from organization."""
        if agent_id in self.member_ids:
            self.member_ids.remove(agent_id)

        if agent_id in self.great_power_members:
            self.great_power_members.remove(agent_id)

    def set_dominant_leader(self, agent_id: str) -> None:
        """Set dominant leader of organization."""
        self.dominant_leader = agent_id

    def get_leadership_summary(self) -> Dict[str, Any]:
        """Get summary of organizational leadership structure."""
        return {
            "dominant_leader": self.dominant_leader,
            "great_power_members": list(self.great_power_members),
            "total_members": len(self.member_ids),
            "decision_rule": self.decision_rule.value,
            "org_type": self.org_type.value,
        }
