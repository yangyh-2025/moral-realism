"""
Power Update Module

This module implements dynamic power updates following the Klein equation:
Pp = (C + E + M) × (S + W)

Constraints:
- Per-action power change ≤10 points (hard constraint)
- Round-based power aggregation: sum all initiator + target changes
- Automatic power level recalculation after updates
- Power history recording
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# Import enums from agent_base to maintain consistency
from .agent_base import PowerLevelEnumEnum

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PowerHistoryEntry:
    """Power history entry for an agent"""
    history_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[int] = None
    agent_id: int = 0
    round_id: Optional[int] = None
    round_num: int = 0
    round_start_power: float = 0.0
    round_end_power: float = 0.0
    round_change_value: float = 0.0
    round_change_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PowerUpdateResult:
    """Result of a power update operation"""
    agent_id: int
    agent_name: str
    start_power: float
    end_power: float
    change_value: float
    change_rate: float
    old_power_level: PowerLevelEnum
    new_power_level: PowerLevelEnum
    action_count: int = 0
    initiator_changes: List[Tuple[int, int]] = field(default_factory=list)  # (action_id, change)
    target_changes: List[Tuple[int, int]] = field(default_factory=list)  # (action_id, change)


class PowerUpdateError(Exception):
    """Power update error"""
    pass


class PowerUpdateEngine:
    """
    Power update engine

    Implements dynamic power updates following the Klein equation with
    strict constraints on per-action power changes.
    """

    def __init__(
        self,
        max_action_change: int = 10,
        enable_logging: bool = True
    ):
        """
        Initialize power update engine

        Args:
            max_action_change: Maximum power change per action (hard constraint)
            enable_logging: Enable detailed logging
        """
        self.max_action_change = max_action_change
        self.enable_logging = enable_logging
        self._agents: Dict[int, Agent] = {}
        self._power_history: Dict[int, List[PowerHistoryEntry]] = {}
        self._current_round = 0

        logger.info(
            f"PowerUpdateEngine initialized with max_action_change={max_action_change}"
        )

    def load_agents(self, agents: List[Agent]) -> None:
        """
        Load agents

        Args:
            agents: List of agents
        """
        self._agents = {agent.agent_id: agent for agent in agents}
        for agent in agents:
            self._power_history[agent.agent_id] = []

        logger.info(f"Loaded {len(agents)} agents")

    def set_round(self, round_num: int) -> None:
        """
        Set current round number

        Args:
            round_num: Round number
        """
        self._current_round = round_num
        logger.info(f"Set round to {round_num}")

    def _validate_action_power_change(
        self,
        action_record: ActionRecord
    ) -> None:
        """
        Validate that action power changes respect the hard constraint

        Args:
            action_record: Action record to validate

        Raises:
            PowerUpdateError: If constraint is violated
        """
        initiator_change = abs(action_record.initiator_power_change)
        target_change = abs(action_record.target_power_change)

        if initiator_change > self.max_action_change:
            raise PowerUpdateError(
                f"Action {action_record.action_name} (ID: {action_record.action_id}) "
                f"initiator power change {initiator_change} exceeds maximum "
                f"allowed change {self.max_action_change}"
            )

        if target_change > self.max_action_change:
            raise PowerUpdateError(
                f"Action {action_record.action_name} (ID: {action_record.action_id}) "
                f"target power change {target_change} exceeds maximum "
                f"allowed change {self.max_action_change}"
            )

    def _calculate_agent_round_change(
        self,
        agent_id: int,
        action_records: List[ActionRecord]
    ) -> Tuple[float, List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Calculate total power change for an agent in a round

        Args:
            agent_id: Agent ID
            action_records: List of action records for the round

        Returns:
            Tuple of (total_change, initiator_changes, target_changes)
        """
        total_change = 0.0
        initiator_changes = []
        target_changes = []

        for record in action_records:
            if not record.is_valid:
                continue

            # Validate action power changes
            try:
                self._validate_action_power_change(record)
            except PowerUpdateError as e:
                logger.error(f"Validation error for action {record.action_id}: {e}")
                raise

            # Add initiator change if agent is the source
            if record.source_agent_id == agent_id:
                change = record.initiator_power_change
                total_change += change
                initiator_changes.append((record.action_id, change))

            # Add target change if agent is the target
            if record.target_agent_id == agent_id:
                change = record.target_power_change
                total_change += change
                target_changes.append((record.action_id, change))

        return total_change, initiator_changes, target_changes

    def _update_agent_power(
        self,
        agent: Agent,
        power_change: float
    ) -> PowerLevelEnum:
        """
        Update agent's power and recalculate power level

        Args:
            agent: Agent to update
            power_change: Power change value

        Returns:
            Old power level
        """
        old_power_level = agent.power_level
        old_power = agent.current_total_power

        # Apply power change
        agent.current_total_power = old_power + power_change

        # Ensure power doesn't go negative
        if agent.current_total_power < 0:
            logger.warning(
                f"Agent {agent.agent_name} power would go negative. "
                f"Setting to 0 (was {agent.current_total_power})"
            )
            agent.current_total_power = 0.0

        # Recalculate power level
        agent.power_level = agent.determine_power_level()

        new_power_level = agent.power_level

        if self.enable_logging:
            logger.info(
                f"Agent {agent.agent_name} power updated: "
                f"{old_power:.2f} -> {agent.current_total_power:.2f} "
                f"(change: {power_change:.2f}), "
                f"level: {old_power_level.value} -> {new_power_level.value}"
            )

        return old_power_level

    def _calculate_change_rate(
        self,
        start_power: float,
        end_power: float
    ) -> float:
        """
        Calculate power change rate (percentage)

        Args:
            start_power: Starting power
            end_power: Ending power

        Returns:
            Change rate as percentage
        """
        if start_power == 0:
            return 0.0 if end_power == 0 else 100.0

        return ((end_power - start_power) / start_power) * 100.0

    def _create_power_history_entry(
        self,
        agent_id: int,
        start_power: float,
        end_power: float,
        change_value: float,
        change_rate: float
    ) -> PowerHistoryEntry:
        """
        Create a power history entry

        Args:
            agent_id: Agent ID
            start_power: Starting power
            end_power: Ending power
            change_value: Power change value
            change_rate: Power change rate

        Returns:
            Power history entry
        """
        entry = PowerHistoryEntry(
            agent_id=agent_id,
            round_num=self._current_round,
            round_start_power=start_power,
            round_end_power=end_power,
            round_change_value=change_value,
            round_change_rate=change_rate
        )

        self._power_history[agent_id].append(entry)

        if self.enable_logging:
            logger.info(
                f"Power history entry created for agent {agent_id}: "
                f"round {self._current_round}, "
                f"{start_power:.2f} -> {end_power:.2f} "
                f"(rate: {change_rate:.2f}%)"
            )

        return entry

    def update_round_power(
        self,
        action_records: List[ActionRecord],
        validate_only: bool = False
    ) -> List[PowerUpdateResult]:
        """
        Update power for all agents based on action records

        Args:
            action_records: List of action records for the round
            validate_only: If True, only validate without applying changes

        Returns:
            List of power update results for all agents

        Raises:
            PowerUpdateError: If validation fails
        """
        if self.enable_logging:
            logger.info(
                f"Updating power for round {self._current_round} "
                f"with {len(action_records)} action records"
            )

        results = []

        # Calculate changes for all agents first (validation phase)
        agent_changes: Dict[int, Tuple[float, List[Tuple[int, int]], List[Tuple[int, int]]]] = {}

        for agent_id, agent in self._agents.items():
            try:
                change_value, initiator_changes, target_changes = (
                    self._calculate_agent_round_change(agent_id, action_records)
                )
                agent_changes[agent_id] = (change_value, initiator_changes, target_changes)

                if self.enable_logging:
                    logger.info(
                        f"Agent {agent.agent_name} calculated change: {change_value:.2f} "
                        f"({len(initiator_changes)} initiator, {len(target_changes)} target)"
                    )

            except PowerUpdateError as e:
                logger.error(f"Power change calculation failed for agent {agent_id}: {e}")
                raise

        # If validation only, return results without applying changes
        if validate_only:
            for agent_id, (change_value, initiator_changes, target_changes) in agent_changes.items():
                agent = self._agents[agent_id]
                end_power = agent.current_total_power + change_value
                change_rate = self._calculate_change_rate(
                    agent.current_total_power,
                    end_power
                )

                result = PowerUpdateResult(
                    agent_id=agent_id,
                    agent_name=agent.agent_name,
                    start_power=agent.current_total_power,
                    end_power=end_power,
                    change_value=change_value,
                    change_rate=change_rate,
                    old_power_level=agent.power_level,
                    new_power_level=agent.determine_power_level(),
                    action_count=len(initiator_changes) + len(target_changes),
                    initiator_changes=initiator_changes,
                    target_changes=target_changes
                )
                results.append(result)

            return results

        # Apply changes to all agents
        for agent_id, (change_value, initiator_changes, target_changes) in agent_changes.items():
            agent = self._agents[agent_id]
            start_power = agent.current_total_power

            # Update agent power
            old_power_level = self._update_agent_power(agent, change_value)
            end_power = agent.current_total_power

            # Calculate change rate
            change_rate = self._calculate_change_rate(start_power, end_power)

            # Create power history entry
            self._create_power_history_entry(
                agent_id,
                start_power,
                end_power,
                change_value,
                change_rate
            )

            # Create result
            result = PowerUpdateResult(
                agent_id=agent_id,
                agent_name=agent.agent_name,
                start_power=start_power,
                end_power=end_power,
                change_value=change_value,
                change_rate=change_rate,
                old_power_level=old_power_level,
                new_power_level=agent.power_level,
                action_count=len(initiator_changes) + len(target_changes),
                initiator_changes=initiator_changes,
                target_changes=target_changes
            )
            results.append(result)

        if self.enable_logging:
            logger.info(
                f"Power update completed for round {self._current_round}: "
                f"{len(results)} agents updated"
            )

        return results

    def get_agent_power_history(
        self,
        agent_id: int,
        round_range: Optional[Tuple[int, int]] = None
    ) -> List[PowerHistoryEntry]:
        """
        Get power history for an agent

        Args:
            agent_id: Agent ID
            round_range: Optional tuple of (start_round, end_round)

        Returns:
            List of power history entries
        """
        if agent_id not in self._power_history:
            logger.warning(f"No power history for agent {agent_id}")
            return []

        history = self._power_history[agent_id]

        if round_range:
            start_round, end_round = round_range
            history = [
                entry for entry in history
                if start_round <= entry.round_num <= end_round
            ]

        return history

    def get_all_power_history(
        self,
        round_range: Optional[Tuple[int, int]] = None
    ) -> Dict[int, List[PowerHistoryEntry]]:
        """
        Get power history for all agents

        Args:
            round_range: Optional tuple of (start_round, end_round)

        Returns:
            Dictionary mapping agent IDs to power history
        """
        result = {}

        for agent_id in self._power_history:
            result[agent_id] = self.get_agent_power_history(agent_id, round_range)

        return result

    def get_agent_current_power(self, agent_id: int) -> Optional[float]:
        """
        Get current power for an agent

        Args:
            agent_id: Agent ID

        Returns:
            Current power or None if agent not found
        """
        if agent_id not in self._agents:
            return None

        return self._agents[agent_id].current_total_power

    def get_agent_power_level(self, agent_id: int) -> Optional[PowerLevelEnum]:
        """
        Get current power level for an agent

        Args:
            agent_id: Agent ID

        Returns:
            Current power level or None if agent not found
        """
        if agent_id not in self._agents:
            return None

        return self._agents[agent_id].power_level

    def get_power_statistics(self) -> Dict[str, any]:
        """
        Get power statistics for all agents

        Returns:
            Dictionary with power statistics
        """
        stats = {
            'round_num': self._current_round,
            'total_agents': len(self._agents),
            'agents': {}
        }

        for agent_id, agent in self._agents.items():
            history = self._power_history[agent_id]

            stats['agents'][agent_id] = {
                'agent_name': agent.agent_name,
                'initial_power': agent.initial_total_power,
                'current_power': agent.current_total_power,
                'power_level': agent.power_level.value,
                'total_change': agent.current_total_power - agent.initial_total_power,
                'change_rate': self._calculate_change_rate(
                    agent.initial_total_power,
                    agent.current_total_power
                ),
                'history_count': len(history)
            }

        return stats

    def reset_round(self) -> None:
        """
        Reset current round without clearing power history
        """
        self._current_round = 0
        logger.info("Round reset to 0")

    def clear_power_history(self, agent_id: Optional[int] = None) -> None:
        """
        Clear power history

        Args:
            agent_id: Optional agent ID to reset. If None, reset all agents.
        """
        if agent_id:
            if agent_id in self._power_history:
                self._power_history[agent_id] = []
                logger.info(f"Cleared power history for agent {agent_id}")
        else:
            for agent_id in self._power_history:
                self._power_history[agent_id] = []
            logger.info("Cleared power history for all agents")

    def validate_klein_equation(self, agent: Agent) -> bool:
        """
        Validate that an agent's initial power follows the Klein equation

        Args:
            agent: Agent to validate

        Returns:
            True if valid, False otherwise
        """
        expected_power = agent.calculate_power()
        actual_power = agent.initial_total_power

        # Allow for small floating point differences
        is_valid = abs(expected_power - actual_power) < 0.01

        if not is_valid:
            logger.warning(
                f"Klein equation validation failed for agent {agent.agent_name}: "
                f"expected {expected_power:.2f}, got {actual_power:.2f}"
            )

        return is_valid

    def validate_all_klein_equations(self) -> Dict[int, bool]:
        """
        Validate Klein equation for all agents

        Returns:
            Dictionary mapping agent IDs to validation results
        """
        results = {}

        for agent_id, agent in self._agents.items():
            results[agent_id] = self.validate_klein_equation(agent)

        return results
