"""
LLM驱动的决策引擎模块
LLM-driven Decision Engine Module

实现基于大语言模型的智能体决策，包含成本收益分析和三层验证机制。
完全对齐技术规范第4.2.4节。
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

from loguru import logger

try:
    from .prompt_templates import PromptTemplates, STANDARD_BEHAVIORS
    from .decision_validation import DecisionValidator, ValidationError
    from ..services.llm_service import LLMService, LLMConfig, get_llm_service
except ImportError:
    from app.core.prompt_templates import PromptTemplates, STANDARD_BEHAVIORS
    from app.core.decision_validation import DecisionValidator, ValidationError
    from app.services.llm_service import LLMService, LLMConfig, get_llm_service

# Import enums from agent_base and action_record to avoid duplication
from .agent_base import PowerLevelEnum, LeaderTypeEnum
from ..models.action_record import ActionStageEnum


@dataclass
class AgentInfo:
    """智能体决策信息类"""
    agent_id: int
    agent_name: str
    region: str
    initial_total_power: float
    current_total_power: float
    power_level: str
    leader_type: Optional[str] = None
    national_interest: List[str] = field(default_factory=list)
    allowed_actions: List[Dict[str, Any]] = field(default_factory=list)
    strategic_relationships: Dict[int, str] = field(default_factory=dict)


@dataclass
class InfoPool:
    """智能体决策信息池类"""
    all_agent_info: List[Dict[str, Any]] = field(default_factory=list)
    history_action_records: List[Dict[str, Any]] = field(default_factory=list)
    history_power_data: List[Dict[str, Any]] = field(default_factory=list)
    last_round_order_info: Dict[str, Any] = field(default_factory=dict)
    round_num: int = 1  # 当前轮次


@dataclass
class DecisionResult:
    """LLM决策结果类"""
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
    领导集体LLM驱动决策引擎

    实现功能：
    - LLM驱动的决策模拟
    - 包含20种标准行为的决策提示工程
    - 策略选择的成本收益分析
    - 三层决策验证机制
    """

    # 类级别的 logger 引用
    logger = logger

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        max_retries: int = 3,
        log_manager: Optional[Any] = None
    ):
        """
        Initialize decision engine.

        Args:
            llm_service: LLM service instance
            max_retries: Maximum retries for failed validation
            log_manager: Optional log manager instance for logging LLM calls
        """
        self.llm_service = llm_service or get_llm_service()
        self.max_retries = max_retries
        self.validator = DecisionValidator(STANDARD_BEHAVIORS)
        self.log_manager = log_manager

        # Debug: log validator initialization
        logger.debug(
            f"DecisionEngine initialized: validator.behavior_id_map has {len(self.validator.behavior_id_map)} items, "
            f"keys: {sorted(self.validator.behavior_id_map.keys())}"
        )

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
        from loguru import logger as _logger
        start_time = time.time()

        _logger.info(
            f"Generating decision for {agent_info.agent_name} "
            f"(ID: {agent_info.agent_id}, Stage: {action_stage})"
        )

        # Prepare allowed actions based on stage
        stage_allowed_actions = self._filter_actions_by_stage(
            agent_info.allowed_actions,
            action_stage
        )

        # Build system and user prompts
        system_prompt, user_prompt = self._build_prompts_for_llm(
            agent_info,
            stage_allowed_actions,
            info_pool
        )

        result = DecisionResult(success=False)

        # Retry loop for validation failures
        for retry in range(self.max_retries + 1):
            try:
                retry_time = time.time()

                # Call LLM with separated system and user prompts
                llm_response = await self.llm_service.call_llm_async(
                    user_prompt,
                    system_prompt=system_prompt,
                    log_manager=self.log_manager,
                    log_category="interaction",
                    agent_id=agent_info.agent_id,
                    agent_name=agent_info.agent_name,
                    stage=str(action_stage),
                    round_num=info_pool.round_num
                )
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
                    _logger.info(
                        f"Decision for {agent_info.agent_name} validated successfully "
                        f"(Retry {retry}/{self.max_retries})"
                    )
                    break
                else:
                    result.validation_errors = errors
                    # Debug: log more details
                    _logger.warning(
                        f"Decision validation failed for {agent_info.agent_name}: {errors}. "
                        f"Retry {retry}/{self.max_retries}. "
                        f"Allowed action IDs: {[a.get('action_id') for a in stage_allowed_actions[:5]]}...{len(stage_allowed_actions)} total. "
                        f"LLM response action IDs: {[a.get('action_id') for a in llm_response.get('actions', [])]}"
                    )

                    # Update user prompt with validation error for retry
                    if retry < self.max_retries:
                        user_prompt = self._build_retry_prompt(user_prompt, errors)

            except Exception as e:
                _logger.error(
                    f"Decision generation failed for {agent_info.agent_name}: {e}"
                )
                result.validation_errors.append(f"LLM调用失败: {str(e)}")

                if retry < self.max_retries:
                    await asyncio.sleep(1)  # Brief delay before retry
                else:
                    break

        result.total_time = time.time() - start_time

        if not result.success:
            _logger.error(
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

    def _build_prompts_for_llm(
        self,
        agent_info: AgentInfo,
        allowed_actions: List[Dict[str, Any]],
        info_pool: InfoPool
    ) -> tuple[str, str]:
        """
        Build system and user prompts for LLM.

        Args:
            agent_info: Agent information
            allowed_actions: Allowed actions for this stage
            info_pool: Information pool

        Returns:
            Tuple of (system_prompt, user_prompt)
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

        # Debug: 验证战略关系是否在info_pool中
        logger.debug(f"InfoPool中的agent_info示例: {info_pool.all_agent_info[0] if info_pool.all_agent_info else 'empty'}")
        if info_pool.all_agent_info:
            for agent in info_pool.all_agent_info[:3]:  # 只打印前3个
                logger.debug(f"  Agent {agent.get('agent_id')} 战略关系: {agent.get('strategic_relationships', {})}")

        # Build system prompt (role, rules, output requirements)
        system_prompt = PromptTemplates.build_system_prompt(
            agent_dict,
            agent_info.leader_type or "未定义"
        )

        # Build user prompt (task, context, data)
        user_prompt = PromptTemplates.build_user_prompt(
            agent_dict,
            allowed_actions,
            info_pool_dict
        )

        return system_prompt, user_prompt

    def _build_decision_prompt(
        self,
        agent_info: AgentInfo,
        allowed_actions: List[Dict[str, Any]],
        info_pool: InfoPool
    ) -> str:
        """
        Build decision prompt using templates.

        This method combines system and user prompts for backward compatibility
        (e.g., for retry scenarios).

        Args:
            agent_info: Agent information
            allowed_actions: Allowed actions for this stage
            info_pool: Information pool

        Returns:
            Complete decision prompt
        """
        system_prompt, user_prompt = self._build_prompts_for_llm(
            agent_info,
            allowed_actions,
            info_pool
        )

        return system_prompt + "\n\n" + user_prompt

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
                f"领导类型:{agent.get('leader_type', 'N/A')} | "
                f"战略关系:{self._format_relationships_for_prompt(agent.get('strategic_relationships', {}))}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _format_relationships_for_prompt(self, relationships: Dict[int, str]) -> str:
        """Format strategic relationships for prompt."""
        logger.debug(f"格式化战略关系输入: {relationships}")
        if not relationships:
            logger.debug("战略关系为空，返回'无'")
            return "无"

        items = []
        for target_id, rel_type in sorted(relationships.items()):
            items.append(f"{target_id}:{rel_type}")

        result = ", ".join(items[:10])
        logger.debug(f"格式化战略关系输出: {result}")
        return result

    def _format_history_for_prompt(
        self,
        history: List[Dict[str, Any]]
    ) -> str:
        """Format action history for prompt."""
        if not history:
            return "无历史互动行为记录"

        lines = []
        for record in history:
            line = (
                f"轮次:{record.get('round_num', 'N/A')} | "
                f"发起国:{record.get('source_agent_id', 'N/A')} | "
                f"目标国:{record.get('target_agent_id', 'N/A')} | "
                f"行为:{record.get('action_name', 'N/A')} | "
                f"尊重主权:{record.get('respect_sov', 'N/A')}"
            )
            content = record.get('action_content', '')
            if content:
                line += f" | 内容:{content}"
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
    max_retries: int = 3,
    log_manager: Optional[Any] = None
) -> DecisionEngine:
    """
    Get or create global decision engine instance.

    Args:
        llm_service: Optional LLM service
        max_retries: Maximum validation retries
        log_manager: Optional log manager instance

    Returns:
        DecisionEngine instance
    """
    global _decision_engine

    if _decision_engine is None:
        _decision_engine = DecisionEngine(llm_service, max_retries, log_manager)
    else:
        # Update log_manager if provided
        if log_manager is not None:
            _decision_engine.log_manager = log_manager

    return _decision_engine


def reset_decision_engine():
    """Reset global decision engine instance."""
    global _decision_engine
    _decision_engine = None
    logger.info("Decision engine reset")
