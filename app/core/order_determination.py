"""
Order Determination Module

This module implements international order determination based on two dimensions:
- Dimension 1: Sovereign respect ratio ≥60% (respect_sov actions / total actions)
- Dimension 2: System leader existence (leader follower ratio ≥60%)

Four-quadrant order type determination:
- Respect + Leader = Normative Acceptance (规范接纳型)
- Respect + No Leader = Non-Intervention (不干涉型)
- No Respect + Leader = Big Stick Coercion (大棒威慑型)
- No Respect + No Leader = Terror Balance (恐怖平衡型)
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

# Import from interaction engine
from .interaction_engine import (
    ActionRecord,
    Agent,
    PowerLevel
)

# Configure logging
logger = logging.getLogger(__name__)


class OrderType(str, Enum):
    """International order type enumeration"""
    NORMATIVE_ACCEPTANCE = "规范接纳型"
    NON_INTERVENTION = "不干涉型"
    BIG_STICK_COERCION = "大棒威慑型"
    TERROR_BALANCE = "恐怖平衡型"


@dataclass
class FollowerRelation:
    """Follower relation record"""
    relation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[int] = None
    round_id: Optional[int] = None
    round_num: int = 0
    follower_agent_id: int = 0
    leader_agent_id: Optional[int] = None  # None if neutral
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OrderDeterminationResult:
    """Result of order determination"""
    round_num: int
    total_action_count: int
    respect_sov_action_count: int
    respect_sov_ratio: float
    respect_sov_threshold: float = 0.6
    has_leader: bool = False
    leader_agent_id: Optional[int] = None
    leader_agent_name: Optional[str] = None
    leader_follower_ratio: float = 0.0
    leader_threshold: float = 0.6
    order_type: OrderType = OrderType.TERROR_BALANCE
    follower_relations: List[FollowerRelation] = field(default_factory=list)


class OrderDeterminationEngine:
    """
    International order determination engine

    Implements two-dimensional order determination:
    1. Sovereign respect ratio (≥60% threshold)
    2. System leader existence (follower ratio ≥60% threshold)

    Four-quadrant order type determination.
    """

    def __init__(
        self,
        respect_sov_threshold: float = 0.6,
        leader_threshold: float = 0.6,
        enable_logging: bool = True
    ):
        """
        Initialize order determination engine

        Args:
            respect_sov_threshold: Threshold for sovereign respect (default 0.6 = 60%)
            leader_threshold: Threshold for leader follower ratio (default 0.6 = 60%)
            enable_logging: Enable detailed logging
        """
        self.respect_sov_threshold = respect_sov_threshold
        self.leader_threshold = leader_threshold
        self.enable_logging = enable_logging
        self._agents: Dict[int, Agent] = {}
        self._current_round = 0

        logger.info(
            f"OrderDeterminationEngine initialized with "
            f"respect_sov_threshold={respect_sov_threshold}, "
            f"leader_threshold={leader_threshold}"
        )

    def load_agents(self, agents: List[Agent]) -> None:
        """
        Load agents

        Args:
            agents: List of agents
        """
        self._agents = {agent.agent_id: agent for agent in agents}
        logger.info(f"Loaded {len(agents)} agents")

    def set_round(self, round_num: int) -> None:
        """
        Set current round number

        Args:
            round_num: Round number
        """
        self._current_round = round_num
        logger.info(f"Set round to {round_num}")

    def _calculate_respect_sov_ratio(
        self,
        action_records: List[ActionRecord]
    ) -> Tuple[int, float]:
        """
        Calculate sovereign respect ratio

        Args:
            action_records: List of action records

        Returns:
            Tuple of (respect_sov_count, respect_sov_ratio)
        """
        if not action_records:
            return 0, 0.0

        respect_sov_count = sum(1 for record in action_records if record.respect_sov)
        respect_sov_ratio = respect_sov_count / len(action_records)

        if self.enable_logging:
            logger.info(
                f"Sovereign respect calculation: "
                f"{respect_sov_count}/{len(action_records)} actions = "
                f"{respect_sov_ratio:.2%}"
            )

        return respect_sov_count, respect_sov_ratio

    def _determine_leader_candidates(self) -> List[int]:
        """
        Determine which agents can be system leaders

        According to the academic model, only superpowers and great powers
        can participate in international leadership competition.

        Returns:
            List of agent IDs eligible to be leaders
        """
        candidates = []

        for agent_id, agent in self._agents.items():
            # Only superpowers and great powers can be leaders
            if agent.power_level in [PowerLevel.SUPERPOWER, PowerLevel.GREAT_POWER]:
                candidates.append(agent_id)

        if self.enable_logging:
            logger.info(
                f"Leader candidates: {candidates} "
                f"(superpowers and great powers only)"
            )

        return candidates

    def _calculate_follower_relations(
        self,
        follower_decisions: Optional[Dict[int, Optional[int]]] = None
    ) -> List[FollowerRelation]:
        """
        Calculate follower relations based on agent decisions

        Args:
            follower_decisions: Optional dictionary mapping follower agent IDs
                             to leader agent IDs (None for neutral)

        Returns:
            List of follower relations
        """
        relations = []

        # If no decisions provided, create neutral relations for all agents
        if follower_decisions is None:
            for agent_id, agent in self._agents.items():
                relation = FollowerRelation(
                    relation_id=str(agent_id) + "_" + str(self._current_round),
                    round_num=self._current_round,
                    follower_agent_id=agent_id,
                    leader_agent_id=None  # Neutral
                )
                relations.append(relation)
        else:
            for follower_agent_id, leader_agent_id in follower_decisions.items():
                relation = FollowerRelation(
                    relation_id=str(follower_agent_id) + "_" + str(self._current_round),
                    round_num=self._current_round,
                    follower_agent_id=follower_agent_id,
                    leader_agent_id=leader_agent_id
                )
                relations.append(relation)

        if self.enable_logging:
            leader_counts = {}
            for relation in relations:
                if relation.leader_agent_id:
                    leader_counts[relation.leader_agent_id] = (
                        leader_counts.get(relation.leader_agent_id, 0) + 1
                    )
            logger.info(f"Follower relations: {len(relations)} total, leader counts: {leader_counts}")

        return relations

    def _determine_system_leader(
        self,
        follower_relations: List[FollowerRelation]
    ) -> Tuple[bool, Optional[int], float]:
        """
        Determine if a system leader exists

        A system leader exists if a single agent has a follower ratio ≥60%.

        Args:
            follower_relations: List of follower relations

        Returns:
            Tuple of (has_leader, leader_agent_id, follower_ratio)
        """
        if not self._agents:
            return False, None, 0.0

        # Count followers for each leader
        leader_follower_counts: Dict[int, int] = {}
        total_agents = len(self._agents)

        for relation in follower_relations:
            if relation.leader_agent_id is not None:
                leader_follower_counts[relation.leader_agent_id] = (
                    leader_follower_counts.get(relation.leader_agent_id, 0) + 1
                )

        # Find leader with highest follower ratio
        max_follower_count = 0
        leader_agent_id = None

        for agent_id, follower_count in leader_follower_counts.items():
            if follower_count > max_follower_count:
                max_follower_count = follower_count
                leader_agent_id = agent_id

        # Check if follower ratio meets threshold
        follower_ratio = max_follower_count / total_agents if total_agents > 0 else 0.0
        has_leader = follower_ratio >= self.leader_threshold

        if self.enable_logging:
            if has_leader:
                leader_name = self._agents.get(leader_agent_id, Agent(
                    agent_id=0,
                    agent_name="Unknown",
                    region="",
                    c_score=0,
                    e_score=0,
                    m_score=0,
                    s_score=0,
                    w_score=0,
                    initial_total_power=0,
                    current_total_power=0,
                    power_level=PowerLevel.SMALL_STATE
                )).agent_name if leader_agent_id in self._agents else "Unknown"

                logger.info(
                    f"System leader found: {leader_agent_id} ({leader_name}), "
                    f"follower ratio: {follower_ratio:.2%} "
                    f"(threshold: {self.leader_threshold:.2%})"
                )
            else:
                logger.info(
                    f"No system leader found. Max follower ratio: {follower_ratio:.2%} "
                    f"(threshold: {self.leader_threshold:.2%})"
                )

        return has_leader, leader_agent_id, follower_ratio

    def _determine_order_type(
        self,
        respect_sov_ratio: float,
        has_leader: bool
    ) -> OrderType:
        """
        Determine international order type based on two dimensions

        Four-quadrant determination:
        - Respect + Leader = Normative Acceptance
        - Respect + No Leader = Non-Intervention
        - No Respect + Leader = Big Stick Coercion
        - No Respect + No Leader = Terror Balance

        Args:
            respect_sov_ratio: Sovereign respect ratio
            has_leader: Whether a system leader exists

        Returns:
            Order type
        """
        is_respectful = respect_sov_ratio >= self.respect_sov_threshold

        if is_respectful and has_leader:
            order_type = OrderType.NORMATIVE_ACCEPTANCE
        elif is_respectful and not has_leader:
            order_type = OrderType.NON_INTERVENTION
        elif not is_respectful and has_leader:
            order_type = OrderType.BIG_STICK_COERCION
        else:
            order_type = OrderType.TERROR_BALANCE

        if self.enable_logging:
            logger.info(
                f"Order type determined: {order_type.value} "
                f"(respectful: {is_respectful}, has_leader: {has_leader})"
            )

        return order_type

    def determine_order(
        self,
        action_records: List[ActionRecord],
        follower_decisions: Optional[Dict[int, Optional[int]]] = None
    ) -> OrderDeterminationResult:
        """
        Determine international order for the current round

        Args:
            action_records: List of action records for the round
            follower_decisions: Optional dictionary mapping follower agent IDs
                             to leader agent IDs (None for neutral)

        Returns:
            Order determination result
        """
        if self.enable_logging:
            logger.info(
                f"Determining order for round {self._current_round} "
                f"with {len(action_records)} action records"
            )

        # Dimension 1: Sovereign respect ratio
        respect_sov_count, respect_sov_ratio = self._calculate_respect_sov_ratio(
            action_records
        )

        # Dimension 2: System leader existence
        follower_relations = self._calculate_follower_relations(follower_decisions)
        has_leader, leader_agent_id, leader_follower_ratio = self._determine_system_leader(
            follower_relations
        )

        # Determine order type
        order_type = self._determine_order_type(respect_sov_ratio, has_leader)

        # Get leader name if exists
        leader_agent_name = None
        if leader_agent_id and leader_agent_id in self._agents:
            leader_agent_name = self._agents[leader_agent_id].agent_name

        # Create result
        result = OrderDeterminationResult(
            round_num=self._current_round,
            total_action_count=len(action_records),
            respect_sov_action_count=respect_sov_count,
            respect_sov_ratio=respect_sov_ratio,
            respect_sov_threshold=self.respect_sov_threshold,
            has_leader=has_leader,
            leader_agent_id=leader_agent_id,
            leader_agent_name=leader_agent_name,
            leader_follower_ratio=leader_follower_ratio,
            leader_threshold=self.leader_threshold,
            order_type=order_type,
            follower_relations=follower_relations
        )

        if self.enable_logging:
            logger.info(
                f"Order determination complete: {order_type.value}, "
                f"respect ratio: {respect_sov_ratio:.2%}, "
                f"leader follower ratio: {leader_follower_ratio:.2%}"
            )

        return result

    def get_follower_relations_for_agent(
        self,
        agent_id: int,
        round_range: Optional[Tuple[int, int]] = None
    ) -> List[FollowerRelation]:
        """
        Get follower relations for a specific agent

        Args:
            agent_id: Agent ID
            round_range: Optional tuple of (start_round, end_round)

        Returns:
            List of follower relations where agent is follower or leader
        """
        # Note: This method would need access to historical relations
        # For now, return empty list as relations are stored per determination
        if self.enable_logging:
            logger.info(f"Getting follower relations for agent {agent_id}")
        return []

    def validate_thresholds(self) -> Dict[str, bool]:
        """
        Validate that thresholds are within acceptable ranges

        Returns:
            Dictionary with validation results
        """
        results = {
            'respect_sov_threshold_valid': 0.0 <= self.respect_sov_threshold <= 1.0,
            'leader_threshold_valid': 0.0 <= self.leader_threshold <= 1.0,
            'thresholds_equal_to_academic': (
                abs(self.respect_sov_threshold - 0.6) < 0.001 and
                abs(self.leader_threshold - 0.6) < 0.001
            )
        }

        if self.enable_logging:
            logger.info(f"Threshold validation: {results}")

        return results

    def get_order_statistics(self) -> Dict[str, any]:
        """
        Get order determination statistics

        Returns:
            Dictionary with order statistics
        """
        return {
            'current_round': self._current_round,
            'respect_sov_threshold': self.respect_sov_threshold,
            'leader_threshold': self.leader_threshold,
            'total_agents': len(self._agents),
            'eligible_leader_candidates': len(self._determine_leader_candidates()),
            'thresholds_valid': self.validate_thresholds()
        }


def create_sample_action_records(
    round_num: int = 0,
    respect_sov_count: int = 3,
    total_count: int = 5
) -> List[ActionRecord]:
    """
    Create sample action records for testing

    Args:
        round_num: Round number
        respect_sov_count: Number of respect-sovereignty actions
        total_count: Total number of actions

    Returns:
        List of sample action records
    """
    records = []

    for i in range(total_count):
        is_respect = i < respect_sov_count
        record = ActionRecord(
            round_num=round_num,
            action_stage="initiative",
            source_agent_id=1,
            target_agent_id=2,
            action_id=1,
            action_category="diplomatic",
            action_name="Sample Action",
            respect_sov=is_respect,
            initiator_power_change=0,
            target_power_change=0,
            is_valid=True
        )
        records.append(record)

    return records
