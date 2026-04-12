"""
LLM-driven decision engine for ABM simulation.
Implements decision-making with cost-benefit analysis and three-tier validation.
Aligned with technical spec section 4.2.4.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from loguru import logger

try:
    from .prompt_templates import PromptTemplates, STANDARD_BEHAVIORS
    from .decision_validation import DecisionValidator, ValidationError
    from ..services.llm_service import LLMService, LLMConfig, get_llm_service
except ImportError:
    from app.core.prompt_templates import PromptTemplates, STANDARD_BEHAVIORS
    from app.core.decision_validation import DecisionValidator, ValidationError
    from app.services.llm_service import LLMService, LLMConfig, get_llm_service


class ActionStageEnum(str, Enum):
    """Action stage enumeration."""
    INITIATIVE = "initiative"  # 发起阶段
    RESPONSE = "response"  # 响应阶段


class PowerLevelEnum(str, Enum):
    """Power level enumeration."""
    SUPERPOWER = "超级大国"
    GREAT_POWER = "大国"
    MIDDLE_POWER = "中等强国"
    SMALL_STATE = "小国"


class LeaderTypeEnum(str, Enum):
    """Leader type enumeration."""
    KINGLY = "王道型"
    HEGEMONIC = "霸权型"
    TYRANICAL = "强权型"
    INEPT = "昏庸型"


@dataclass
class AgentInfo:
    """Agent information for decision making."""
    agent_id: int
    agent_name: str
    region: str
    initial_total_power: float
    current_total_power: float
    power_level: str
    leader_type: Optional[str] = None
    national_interest: List[str] = field(default_factory=list)
    allowed_actions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class InfoPool:
    """Information pool for agent decision making."""
    all_agent_info: List[Dict[str, Any]] = field(default_factory=list)
    history_action_records: List[Dict[str, Any]] = field(default_factory=list)
    history_power_data: List[Dict[str, Any]] = field(default_factory=list)
    last_round_order_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    """Decision result from LLM."""
    success: bool
    decision: Optional[Dict[str, Any]] = None
    validation_errors: List[str] = field(default_factory=list)
    llm_raw_response: Optional[str] = None
    llm_parse_time: float = 0.0
    validation_time: float = 0.0
    total_time: float = 0.0
    retry_count: int = 0


class DecisionEngine:
    """
    LLM-driven decision engine for leader collectives.

    Implements:
    - LLM-driven decision simulation
    - Decision prompt engineering with 20 standard behaviors
    - Cost-benefit analysis for strategy selection
    - Three-tier decision validation
    """

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        max_retries: int = 3
    ):
        """
        Initialize decision engine.

        Args:
            llm_service: LLM service instance
            max_retries: Maximum retries for failed validation
        """
        self.llm_service = llm_service or get_llm_service()
        self.max_retries = max_retries
        self.validator = DecisionValidator(STANDARD_BEHAVIORS)

    async def make_decision(
        self,
        agent_info: AgentInfo,
        info_pool: InfoPool,
        action_stage: ActionStageEnum = ActionStageEnum.INITIATIVE
    ) -> DecisionResult:
        """
        Make decision for an agent using LLM with cost-benefit analysis.

        Args:
            agent_info: Agent information
            info_pool: Information pool
            action_stage: Current action stage

        Returns:
            DecisionResult with decision and validation status
        """
        import time
        start_time = time.time()

        logger.info(
            f"Generating decision for {agent_info.agent_name} "
            f"(ID: {agent_info.agent_id}, Stage: {action_stage})"
        )

        # Prepare allowed actions based on stage
        stage_allowed_actions = self._filter_actions_by_stage(
            agent_info.allowed_actions,
            action_stage
        )

        # Build prompt
        prompt = self._build_decision_prompt(
            agent_info,
            stage_allowed_actions,
            info_pool
        )

        result = DecisionResult(success=False)

        # Retry loop for validation failures
        for retry in range(self.max_retries + 1):
            try:
                retry_time = time.time()

                # Call LLM
                llm_response = await self.llm_service.call_llm_async(prompt)
                result.llm_raw_response = str(llm_response)
                result.llm_parse_time = time.time() - retry_time
                result.retry_count = retry

                # Validate decision
                validation_start = time.time()
                is_valid, errors = self._validate_decision(
                    llm_response,
                    agent_info,
                    stage_allowed_actions,
                    info_pool,
                    action_stage
                )
                result.validation_time = time.time() - validation_start

                if is_valid:
                    result.success = True
                    result.decision = llm_response
                    logger.info(
                        f"Decision for {agent_info.agent_name} validated successfully "
                        f"(Retry {retry}/{self.max_retries})"
                    )
                    break
                else:
                    result.validation_errors = errors
                    logger.warning(
                        f"Decision validation failed for {agent_info.agent_name}: {errors}. "
                        f"Retry {retry}/{self.max_retries}"
                    )

                    # Update prompt with validation error for retry
                    if retry < self.max_retries:
                        prompt = self._build_retry_prompt(prompt, errors)

            except Exception as e:
                logger.error(
                    f"Decision generation failed for {agent_info.agent_name}: {e}"
                )
                result.validation_errors.append(f"LLM调用失败: {str(e)}")

                if retry < self.max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    break

        result.total_time = time.time() - start_time

        if not result.success:
            logger.error(
                f"Failed to generate valid decision for {agent_info.agent_name} "
                f"after {result.retry_count + 1} attempts"
            )

        return result

    async def make_decisions_batch(
        self,
        agents_info: List[AgentInfo],
        info_pool: InfoPool,
        action_stage: ActionStageEnum = ActionStageEnum.INITIATIVE,
        max_concurrent: int = 5
    ) -> List[DecisionResult]:
        """
        Make decisions for multiple agents concurrently.

        Args:
            agents_info: List of agent information
            info_pool: Information pool
            action_stage: Current action stage
            max_concurrent: Maximum concurrent decisions

        Returns:
            List of DecisionResults
        """
        logger.info(
            f"Generating batch decisions for {len(agents_info)} agents "
            f"(Stage: {action_stage}, Max concurrent: {max_concurrent})"
        )

        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_decision(agent_info: AgentInfo) -> DecisionResult:
            async with semaphore:
                return await self.make_decision(agent_info, info_pool, action_stage)

        # Execute concurrently with semaphore
        results = await asyncio.gather(
            *[limited_decision(agent) for agent in agents_info],
            return_exceptions=True
        )

        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch decision {i} failed: {result}")
                results[i] = DecisionResult(
                    success=False,
                    validation_errors=[str(result)]
                )

        successful_count = sum(1 for r in results if r.success)
        logger.info(
            f"Batch decisions completed: {successful_count}/{len(results)} successful"
        )

        return results

    def _filter_actions_by_stage(
        self,
        actions: List[Dict[str, Any]],
        action_stage: ActionStageEnum
    ) -> List[Dict[str, Any]]:
        """
        Filter allowed actions by action stage.

        Args:
            actions: List of all allowed actions
            action_stage: Current action stage

        Returns:
            Filtered list of actions
        """
        if action_stage == ActionStageEnum.INITIATIVE:
            return [a for a in actions if a.get('is_initiative', False)]
        elif action_stage == ActionStageEnum.RESPONSE:
            return [a for a in actions if a.get('is_response', False)]
        else:
            return []

    def _build_decision_prompt(
        self,
        agent_info: AgentInfo,
        allowed_actions: List[Dict[str, Any]],
        info_pool: InfoPool
    ) -> str:
        """
        Build decision prompt using templates.

        Args:
            agent_info: Agent information
            allowed_actions: Allowed actions for this stage
            info_pool: Information pool

        Returns:
            Complete decision prompt
        """
        # Convert agent info to dict for template
        agent_dict = {
            'agent_name': agent_info.agent_name,
            'region': agent_info.region,
            'initial_total_power': agent_info.initial_total_power,
            'current_total_power': agent_info.current_total_power,
            'power_level': agent_info.power_level,
            'leader_type': agent_info.leader_type or "未定义",
            'national_interest': agent_info.national_interest
        }

        # Convert info pool to dict
        info_pool_dict = {
            'all_agent_info': self._format_agents_for_prompt(info_pool.all_agent_info),
            'history_action_records': self._format_history_for_prompt(
                info_pool.history_action_records
            ),
            'history_power_data': self._format_power_data_for_prompt(
                info_pool.history_power_data
            ),
            'last_round_order_info': str(info_pool.last_round_order_info)
        }

        # Build full prompt
        prompt = PromptTemplates.build_full_decision_prompt(
            agent_dict,
            allowed_actions,
            info_pool_dict,
            agent_info.leader_type or "未定义"
        )

        return prompt

    def _build_retry_prompt(
        self,
        original_prompt: str,
        validation_errors: List[str]
    ) -> str:
        """
        Build retry prompt with validation errors.

        Args:
            original_prompt: Original decision prompt
            validation_errors: List of validation errors

        Returns:
            Retry prompt with error context
        """
        error_summary = "\n".join([f"- {error}" for error in validation_errors])

        retry_instruction = f"""
【上一次决策验证失败，请重新生成决策】

【验证错误列表】
{error_summary}

【修正要求】
1. 请根据上述错误修正你的决策；
2. 确保所有选择的行为都在允许的行为列表内；
3. 确保目标国家ID正确且存在于系统中；
4. 确保决策符合你的领导类型约束和国家利益；
5. 确保包含完整的成本收益分析。

请重新生成JSON格式的决策结果，确保所有字段正确且符合约束。
"""

        return original_prompt + retry_instruction

    def _validate_decision(
        self,
        decision: Dict[str, Any],
        agent_info: AgentInfo,
        allowed_actions: List[Dict[str, Any]],
        info_pool: InfoPool,
        action_stage: ActionStageEnum
    ) -> Tuple[bool, List[str]]:
        """
        Validate decision using three-tier validation.

        Args:
            decision: LLM-generated decision
            agent_info: Agent information
            allowed_actions: Allowed actions
            info_pool: Information pool
            action_stage: Current action stage

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        # Convert agent info to dict
        agent_dict = {
            'agent_id': agent_info.agent_id,
            'power_level': agent_info.power_level,
            'leader_type': agent_info.leader_type
        }

        # Get all agent IDs
        all_agent_ids = [
            agent.get('agent_id') for agent in info_pool.all_agent_info
            if 'agent_id' in agent
        ]

        # Execute full validation
        is_valid, errors = self.validator.validate_full_decision(
            decision=decision,
            agent_info=agent_dict,
            allowed_actions=allowed_actions,
            all_agent_ids=all_agent_ids,
            national_interests=agent_info.national_interest,
            action_stage=action_stage.value
        )

        return is_valid, errors

    def _format_agents_for_prompt(
        self,
        agents: List[Dict[str, Any]]
    ) -> str:
        """Format agents list for prompt."""
        if not agents:
            return "无其他国家信息"

        lines = []
        for agent in agents:
            line = (
                f"ID:{agent.get('agent_id', 'N/A')} | "
                f"名称:{agent.get('agent_name', 'N/A')} | "
                f"区域:{agent.get('region', 'N/A')} | "
                f"综合国力:{agent.get('current_total_power', 0):.1f} | "
                f"实力层级:{agent.get('power_level', 'N/A')} | "
                f"领导类型:{agent.get('leader_type', 'N/A')}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _format_history_for_prompt(
        self,
        history: List[Dict[str, Any]]
    ) -> str:
        """Format action history for prompt."""
        if not history:
            return "无历史互动行为记录"

        # Show last 20 actions to avoid token limit
        recent_history = history[-20:] if len(history) > 20 else history

        lines = []
        for record in recent_history:
            line = (
                f"轮次:{record.get('round_num', 'N/A')} | "
                f"发起国:{record.get('source_agent_id', 'N/A')} | "
                f"目标国:{record.get('target_agent_id', 'N/A')} | "
                f"行为:{record.get('action_name', 'N/A')} | "
                f"尊重主权:{record.get('respect_sov', 'N/A')}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _format_power_data_for_prompt(
        self,
        power_data: List[Dict[str, Any]]
    ) -> str:
        """Format power history for prompt."""
        if not power_data:
            return "无国力变化历史"

        # Show last 10 rounds
        recent_data = power_data[-10:] if len(power_data) > 10 else power_data

        lines = []
        for data in recent_data:
            line = (
                f"轮次:{data.get('round_num', 'N/A')} | "
                f"国家ID:{data.get('agent_id', 'N/A')} | "
                f"初始国力:{data.get('round_start_power', 0):.1f} | "
                f"结束国力:{data.get('round_end_power', 0):.1f} | "
                f"变化值:{data.get('round_change_value', 0):.1f}"
            )
            lines.append(line)

        return "\n".join(lines)


class CostBenefitAnalyzer:
    """Cost-benefit analysis helper for decision engine."""

    @staticmethod
    def calculate_net_benefit(
        action_config: Dict[str, Any],
        agent_power: float,
        strategic_importance: float = 1.0
    ) -> float:
        """
        Calculate net benefit of an action.

        Args:
            action_config: Action configuration
            agent_power: Current agent power
            strategic_importance: Strategic importance multiplier

        Returns:
            Net benefit score
        """
        # Power change from action
        power_change = action_config.get('initiator_power_change', 0)

        # Relative power impact (normalized by agent power)
        if agent_power > 0:
            relative_impact = power_change / agent_power
        else:
            relative_impact = 0

        # Strategic benefit (respect sovereignty is beneficial for certain contexts)
        strategic_benefit = 1.0 if action_config.get('respect_sov', True) else 0.5

        # Combined net benefit
        net_benefit = (power_change + relative_impact * 100) * strategic_benefit * strategic_importance

        return net_benefit

    @staticmethod
    def rank_actions_by_benefit(
        actions: List[Dict[str, Any]],
        agent_power: float
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank actions by net benefit.

        Args:
            actions: List of action configurations
            agent_power: Current agent power

        Returns:
            List of (action, net_benefit) tuples sorted by benefit
        """
        ranked = []
        for action in actions:
            net_benefit = CostBenefitAnalyzer.calculate_net_benefit(action, agent_power)
            ranked.append((action, net_benefit))

        # Sort by net benefit descending
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked


# Global decision engine instance
_decision_engine: Optional[DecisionEngine] = None


def get_decision_engine(
    llm_service: Optional[LLMService] = None,
    max_retries: int = 3
) -> DecisionEngine:
    """
    Get or create global decision engine instance.

    Args:
        llm_service: Optional LLM service
        max_retries: Maximum validation retries

    Returns:
        DecisionEngine instance
    """
    global _decision_engine

    if _decision_engine is None:
        _decision_engine = DecisionEngine(llm_service, max_retries)

    return _decision_engine


def reset_decision_engine():
    """Reset global decision engine instance."""
    global _decision_engine
    _decision_engine = None
    logger.info("Decision engine reset")
