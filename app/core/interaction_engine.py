"""
Interaction Execution Engine Module

This module implements the interaction execution logic for the ABM simulation,
following the academic model's interaction mechanism with two-phase execution:
- Initiative phase: Superpowers and great powers initiate actions
- Response phase: All agents respond to actions targeting them

Constraints:
- Superpowers/great powers: Can initiate all permitted actions
- Middle powers/small states: Only passive (low-intensity non-hostile actions)
- Full validation: behavior set, basic rules, compliance checks
- Async execution support with configurable concurrency
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class ActionStage(Enum):
    """Action execution stage"""
    INITIATIVE = "initiative"
    RESPONSE = "response"


class PowerLevel(str, Enum):
    """Power level enumeration"""
    SUPERPOWER = "超级大国"
    GREAT_POWER = "大国"
    MIDDLE_POWER = "中等强国"
    SMALL_STATE = "小国"


class LeaderType(str, Enum):
    """Leadership type enumeration"""
    KINGLY = "王道型"
    HEGEMONIC = "霸权型"
    TYRANICAL = "强权型"
    INEPT = "昏庸型"


@dataclass
class ActionConfig:
    """Action configuration from the 20 standard actions"""
    action_id: int
    action_name: str
    action_en_name: str
    action_category: str
    action_desc: str
    respect_sov: bool
    initiator_power_change: int
    target_power_change: int
    is_initiative: bool
    is_response: bool
    allowed_initiator_level: List[str]
    allowed_responder_level: List[str]
    forbidden_leader_type: List[str]


@dataclass
class Agent:
    """Agent (country) representation"""
    agent_id: int
    agent_name: str
    region: str
    c_score: float
    e_score: float
    m_score: float
    s_score: float
    w_score: float
    initial_total_power: float
    current_total_power: float
    power_level: PowerLevel
    leader_type: Optional[LeaderType] = None
    allowed_actions: Dict[str, List[ActionConfig]] = field(default_factory=dict)

    def calculate_power(self) -> float:
        """Calculate total power using Klein equation"""
        return (self.c_score + self.e_score + self.m_score) * (self.s_score + self.w_score)

    def determine_power_level(self) -> PowerLevel:
        """Determine power level based on total power"""
        power = self.current_total_power
        if power >= 500:
            return PowerLevel.SUPERPOWER
        elif power >= 200:
            return PowerLevel.GREAT_POWER
        elif power >= 100:
            return PowerLevel.MIDDLE_POWER
        else:
            return PowerLevel.SMALL_STATE


@dataclass
class ActionRecord:
    """Record of an executed action"""
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_id: Optional[int] = None
    round_id: Optional[int] = None
    round_num: int = 0
    action_stage: ActionStage = ActionStage.INITIATIVE
    source_agent_id: int = 0
    target_agent_id: int = 0
    action_id: int = 0
    action_category: str = ""
    action_name: str = ""
    respect_sov: bool = False
    initiator_power_change: int = 0
    target_power_change: int = 0
    decision_detail: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)


class ValidationError(Exception):
    """Validation error for actions"""
    pass


class InteractionEngine:
    """
    Main interaction execution engine

    Implements two-phase interaction execution:
    1. Initiative phase: Superpowers/great powers initiate actions
    2. Response phase: All agents respond to actions targeting them
    """

    def __init__(
        self,
        max_concurrency: int = 5,
        enable_logging: bool = True
    ):
        """
        Initialize interaction engine

        Args:
            max_concurrency: Maximum concurrent async operations
            enable_logging: Enable detailed logging
        """
        self.max_concurrency = max_concurrency
        self.enable_logging = enable_logging
        self._action_config: Dict[int, ActionConfig] = {}
        self._agents: Dict[int, Agent] = {}
        self._current_round = 0
        self._initiative_records: List[ActionRecord] = []
        self._response_records: List[ActionRecord] = []

        logger.info(f"InteractionEngine initialized with max_concurrency={max_concurrency}")

    def load_action_configs(self, actions: List[ActionConfig]) -> None:
        """
        Load action configurations

        Args:
            actions: List of action configurations
        """
        self._action_config = {action.action_id: action for action in actions}
        logger.info(f"Loaded {len(actions)} action configurations")

    def load_agents(self, agents: List[Agent]) -> None:
        """
        Load agents

        Args:
            agents: List of agents
        """
        self._agents = {agent.agent_id: agent.agent_id for agent in agents}
        logger.info(f"Loaded {len(agents)} agents")

    def set_round(self, round_num: int) -> None:
        """
        Set current round number

        Args:
            round_num: Round number
        """
        self._current_round = round_num
        self._initiative_records = []
        self._response_records = []
        logger.info(f"Set round to {round_num}")

    def _can_initiate_action(self, agent: Agent, action: ActionConfig) -> bool:
        """
        Check if agent can initiate an action

        Args:
            agent: Agent attempting to initiate action
            action: Action to initiate

        Returns:
            True if agent can initiate the action
        """
        # Check power level permission
        if agent.power_level.value not in action.allowed_initiator_level:
            return False

        # Check leader type restriction
        if agent.leader_type and agent.leader_type.value in action.forbidden_leader_type:
            return False

        # Check if action is initiative type
        if not action.is_initiative:
            return False

        return True

    def _can_respond_to_action(self, agent: Agent, action: ActionConfig) -> bool:
        """
        Check if agent can respond with an action

        Args:
            agent: Agent attempting to respond
            action: Action to respond with

        Returns:
            True if agent can respond with the action
        """
        # Check power level permission for response
        if agent.power_level.value not in action.allowed_responder_level:
            return False

        # Check leader type restriction
        if agent.leader_type and agent.leader_type.value in action.forbidden_leader_type:
            return False

        # Check if action is response type
        if not action.is_response:
            return False

        return True

    def _validate_initiative_phase_action(
        self,
        agent: Agent,
        action: ActionConfig,
        target_agent_id: int
    ) -> List[str]:
        """
        Validate an initiative phase action

        Args:
            agent: Initiating agent
            action: Action to initiate
            target_agent_id: Target agent ID

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate target exists
        if target_agent_id not in self._agents:
            errors.append(f"Target agent {target_agent_id} does not exist")

        # Validate agent can initiate
        if not self._can_initiate_action(agent, action):
            errors.append(
                f"Agent {agent.agent_name} (level: {agent.power_level.value}) "
                f"cannot initiate action {action.action_name}"
            )

        # Validate middle/small states only use low-intensity non-hostile actions
        if agent.power_level in [PowerLevel.MIDDLE_POWER, PowerLevel.SMALL_STATE]:
            # Middle/small states should only use low-intensity actions
            # High-intensity actions are those with significant negative power changes
            if abs(action.initiator_power_change) > 3 or abs(action.target_power_change) > 3:
                errors.append(
                    f"Middle/small state {agent.agent_name} cannot initiate "
                    f"high-intensity action {action.action_name}"
                )

        return errors

    def _validate_response_phase_action(
        self,
        agent: Agent,
        action: ActionConfig,
        target_agent_id: int
    ) -> List[str]:
        """
        Validate a response phase action

        Args:
            agent: Responding agent
            action: Action to respond with
            target_agent_id: Target agent ID (initiator)

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Validate target exists
        if target_agent_id not in self._agents:
            errors.append(f"Target agent {target_agent_id} does not exist")

        # Validate agent can respond
        if not self._can_respond_to_action(agent, action):
            errors.append(
                f"Agent {agent.agent_name} (level: {agent.power_level.value}) "
                f"cannot respond with action {action.action_name}"
            )

        return errors

    def _execute_agent_initiative_phase(
        self,
        agent: Agent,
        target_agents: List[Agent],
        action_generator: Any
    ) -> List[ActionRecord]:
        """
        Execute initiative phase for a single agent

        Args:
            agent: Agent to execute initiative phase for
            target_agents: List of potential target agents
            action_generator: Function to generate actions (e.g., LLM call)

        Returns:
            List of action records
        """
        records = []

        if self.enable_logging:
            logger.info(f"Executing initiative phase for agent {agent.agent_name}")

        try:
            # Generate actions using the provided generator (e.g., LLM)
            generated_actions = action_generator(agent, target_agents, ActionStage.INITIATIVE)

            for action_data in generated_actions:
                try:
                    # Get action config
                    action_id = action_data.get('action_id')
                    if action_id not in self._action_config:
                        logger.warning(f"Invalid action_id {action_id} in generated actions")
                        continue

                    action = self._action_config[action_id]
                    target_agent_id = action_data.get('target_agent_id')

                    # Create action record
                    record = ActionRecord(
                        round_num=self._current_round,
                        action_stage=ActionStage.INITIATIVE,
                        source_agent_id=agent.agent_id,
                        target_agent_id=target_agent_id,
                        action_id=action.action_id,
                        action_category=action.action_category,
                        action_name=action.action_name,
                        respect_sov=action.respect_sov,
                        initiator_power_change=action.initiator_power_change,
                        target_power_change=action.target_power_change,
                        decision_detail=action_data.get('decision_detail')
                    )

                    # Validate action
                    errors = self._validate_initiative_phase_action(agent, action, target_agent_id)
                    if errors:
                        record.is_valid = False
                        record.validation_errors = errors
                        logger.warning(
                            f"Validation failed for action {action.action_name}: "
                            f"{', '.join(errors)}"
                        )
                    else:
                        record.is_valid = True
                        if self.enable_logging:
                            logger.info(
                                f"Valid initiative action: {agent.agent_name} -> "
                                f"{action.action_name} -> {target_agent_id}"
                            )

                    records.append(record)

                except Exception as e:
                    logger.error(f"Error processing action for agent {agent.agent_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in initiative phase for agent {agent.agent_name}: {e}")

        return records

    def _execute_agent_response_phase(
        self,
        agent: Agent,
        initiator_records: List[ActionRecord],
        action_generator: Any
    ) -> List[ActionRecord]:
        """
        Execute response phase for a single agent

        Args:
            agent: Agent to execute response phase for
            initiator_records: Records of actions targeting this agent
            action_generator: Function to generate actions (e.g., LLM call)

        Returns:
            List of action records
        """
        records = []

        if self.enable_logging:
            logger.info(f"Executing response phase for agent {agent.agent_name}")

        try:
            # Filter actions that target this agent
            targeting_actions = [
                record for record in initiator_records
                if record.target_agent_id == agent.agent_id and record.is_valid
            ]

            if not targeting_actions:
                # No actions targeting this agent, skip response
                if self.enable_logging:
                    logger.info(f"No actions targeting agent {agent.agent_name}")
                return records

            # Generate responses using the provided generator
            generated_responses = action_generator(
                agent,
                targeting_actions,
                ActionStage.RESPONSE
            )

            for response_data in generated_responses:
                try:
                    # Get action config
                    action_id = response_data.get('action_id')
                    if action_id not in self._action_config:
                        logger.warning(f"Invalid action_id {action_id} in generated responses")
                        continue

                    action = self._action_config[action_id]
                    target_agent_id = response_data.get('target_agent_id')

                    # Create action record
                    record = ActionRecord(
                        round_num=self._current_round,
                        action_stage=ActionStage.RESPONSE,
                        source_agent_id=agent.agent_id,
                        target_agent_id=target_agent_id,
                        action_id=action.action_id,
                        action_category=action.action_category,
                        action_name=action.action_name,
                        respect_sov=action.respect_sov,
                        initiator_power_change=action.initiator_power_change,
                        target_power_change=action.target_power_change,
                        decision_detail=response_data.get('decision_detail')
                    )

                    # Validate response
                    errors = self._validate_response_phase_action(agent, action, target_agent_id)
                    if errors:
                        record.is_valid = False
                        record.validation_errors = errors
                        logger.warning(
                            f"Validation failed for response {action.action_name}: "
                            f"{', '.join(errors)}"
                        )
                    else:
                        record.is_valid = True
                        if self.enable_logging:
                            logger.info(
                                f"Valid response action: {agent.agent_name} -> "
                                f"{action.action_name} -> {target_agent_id}"
                            )

                    records.append(record)

                except Exception as e:
                    logger.error(f"Error processing response for agent {agent.agent_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error in response phase for agent {agent.agent_name}: {e}")

        return records

    async def _execute_initiative_phase_async(
        self,
        agents: List[Agent],
        action_generator: Any
    ) -> List[ActionRecord]:
        """
        Async execute initiative phase for all agents

        Args:
            agents: List of all agents
            action_generator: Function to generate actions

        Returns:
            List of all action records
        """
        all_records = []

        # Separate agents by power level
        superpowers_great_powers = [
            agent for agent in agents
            if agent.power_level in [PowerLevel.SUPERPOWER, PowerLevel.GREAT_POWER]
        ]
        middle_small = [
            agent for agent in agents
            if agent.power_level in [PowerLevel.MIDDLE_POWER, PowerLevel.SMALL_STATE]
        ]

        if self.enable_logging:
            logger.info(
                f"Initiative phase: {len(superpowers_great_powers)} superpowers/great powers, "
                f"{len(middle_small)} middle/small states"
            )

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def execute_with_semaphore(agent: Agent, other_agents: List[Agent]) -> List[ActionRecord]:
            async with semaphore:
                # Run initiative phase in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    self._execute_agent_initiative_phase,
                    agent,
                    other_agents,
                    action_generator
                )

        # Execute superpowers and great powers first (they can initiate all actions)
        tasks = [
            execute_with_semaphore(agent, agents)
            for agent in superpowers_great_powers
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in initiative phase task: {result}")
            else:
                all_records.extend(result)

        # Execute middle and small states (only low-intensity non-hostile actions)
        tasks = [
            execute_with_semaphore(agent, agents)
            for agent in middle_small
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in initiative phase task: {result}")
            else:
                all_records.extend(result)

        # Store valid records only
        self._initiative_records = [r for r in all_records if r.is_valid]

        if self.enable_logging:
            logger.info(
                f"Initiative phase completed: {len(self._initiative_records)} valid actions"
            )

        return all_records

    async def _execute_response_phase_async(
        self,
        agents: List[Agent],
        action_generator: Any
    ) -> List[ActionRecord]:
        """
        Async execute response phase for all agents

        Args:
            agents: List of all agents
            action_generator: Function to generate actions

        Returns:
            List of all action records
        """
        all_records = []

        if self.enable_logging:
            logger.info(f"Response phase: {len(agents)} agents to process")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def execute_with_semaphore(agent: Agent) -> List[ActionRecord]:
            async with semaphore:
                # Run response phase in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    self._execute_agent_response_phase,
                    agent,
                    self._initiative_records,
                    action_generator
                )

        # Execute response phase for all agents
        tasks = [execute_with_semaphore(agent) for agent in agents]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error in response phase task: {result}")
            else:
                all_records.extend(result)

        # Store valid records only
        self._response_records = [r for r in all_records if r.is_valid]

        if self.enable_logging:
            logger.info(
                f"Response phase completed: {len(self._response_records)} valid responses"
            )

        return all_records

    def execute_initiative_phase(
        self,
        agents: List[Agent],
        action_generator: Any
    ) -> List[ActionRecord]:
        """
        Execute initiative phase (synchronous wrapper)

        Args:
            agents: List of all agents
            action_generator: Function to generate actions

        Returns:
            List of all action records
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._execute_initiative_phase_async(agents, action_generator)
            )
        finally:
            loop.close()

    def execute_response_phase(
        self,
        agents: List[Agent],
        action_generator: Any
    ) -> List[ActionRecord]:
        """
        Execute response phase (synchronous wrapper)

        Args:
            agents: List of all agents
            action_generator: Function to generate actions

        Returns:
            List of all action records
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self._execute_response_phase_async(agents, action_generator)
            )
        finally:
            loop.close()

    async def execute_round_async(
        self,
        agents: List[Agent],
        action_generator: Any
    ) -> Dict[str, List[ActionRecord]]:
        """
        Execute a complete interaction round (async)

        Args:
            agents: List of all agents
            action_generator: Function to generate actions

        Returns:
            Dictionary with 'initiative' and 'response' action records
        """
        if self.enable_logging:
            logger.info(f"Starting interaction round {self._current_round}")

        # Execute initiative phase
        initiative_records = await self._execute_initiative_phase_async(
            agents,
            action_generator
        )

        # Execute response phase
        response_records = await self._execute_response_phase_async(
            agents,
            action_generator
        )

        if self.enable_logging:
            logger.info(
                f"Round {self._current_round} completed: "
                f"{len(self._initiative_records)} initiative actions, "
                f"{len(self._response_records)} responses"
            )

        return {
            'initiative': initiative_records,
            'response': response_records
        }

    def execute_round(
        self,
        agents: List[Agent],
        action_generator: Any
    ) -> Dict[str, List[ActionRecord]]:
        """
        Execute a complete interaction round (synchronous wrapper)

        Args:
            agents: List of all agents
            action_generator: Function to generate actions

        Returns:
            Dictionary with 'initiative' and 'response' action records
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.execute_round_async(agents, action_generator)
            )
        finally:
            loop.close()

    def get_valid_records(self) -> List[ActionRecord]:
        """
        Get all valid action records for the current round

        Returns:
            List of valid action records
        """
        return self._initiative_records + self._response_records

    def get_initiative_records(self) -> List[ActionRecord]:
        """
        Get initiative phase records

        Returns:
            List of initiative phase records
        """
        return self._initiative_records

    def get_response_records(self) -> List[ActionRecord]:
        """
        Get response phase records

        Returns:
            List of response phase records
        """
        return self._response_records

    def get_records_by_agent(self, agent_id: int) -> List[ActionRecord]:
        """
        Get all records for a specific agent

        Args:
            agent_id: Agent ID

        Returns:
            List of action records for the agent
        """
        all_records = self.get_valid_records()
        return [
            record for record in all_records
            if record.source_agent_id == agent_id or record.target_agent_id == agent_id
        ]

    def get_records_by_target(self, target_agent_id: int) -> List[ActionRecord]:
        """
        Get all records targeting a specific agent

        Args:
            target_agent_id: Target agent ID

        Returns:
            List of action records targeting the agent
        """
        return [
            record for record in self.get_valid_records()
            if record.target_agent_id == target_agent_id
        ]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current round

        Returns:
            Dictionary with round statistics
        """
        valid_records = self.get_valid_records()

        respect_sov_count = sum(1 for r in valid_records if r.respect_sov)
        respect_sov_ratio = respect_sov_count / len(valid_records) if valid_records else 0.0

        initiative_count = len(self._initiative_records)
        response_count = len(self._response_records)

        return {
            'round_num': self._current_round,
            'total_actions': len(valid_records),
            'initiative_actions': initiative_count,
            'response_actions': response_count,
            'respect_sov_count': respect_sov_count,
            'respect_sov_ratio': respect_sov_ratio,
            'invalid_actions': len(valid_records) - len(self._initiative_records) - len(self._response_records)
        }


def create_default_action_generator() -> Any:
    """
    Create a default mock action generator for testing

    Returns:
        Mock action generator function
    """
    def mock_generator(agent: Agent, others: List[Agent], stage: ActionStage) -> List[Dict]:
        """Mock generator that returns no actions"""
        return []

    return mock_generator
