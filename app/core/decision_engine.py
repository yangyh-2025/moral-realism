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
    cinc_year: Optional[int] = None


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

        # Extract all agent IDs for retry prompt building (avoid NameError on retry)
        all_agent_ids = [
            a.get('agent_id') for a in info_pool.all_agent_info
            if 'agent_id' in a
        ]

        # Build alliance chain-ganging summary for previous round (Christensen-Snyder)
        project_id = None
        for _a in info_pool.all_agent_info:
            if _a.get('project_id') is not None:
                project_id = _a.get('project_id')
                break
        alliance_chain_summary = await self._build_alliance_chain_summary(
            project_id=project_id,
            agent_id=agent_info.agent_id,
            prev_round=max(0, (info_pool.round_num or 1) - 1),
            strategic_relationships=agent_info.strategic_relationships,
            all_agent_info=info_pool.all_agent_info,
            history_action_records=info_pool.history_action_records,
        )

        # Build neighbor summary for current agent (二元邻接: 从 DB 读)
        neighbor_summary = await self._build_neighbor_summary(
            project_id=project_id,
            agent_info=agent_info,
            all_agent_info=info_pool.all_agent_info,
        )

        # Build system and user prompts
        system_prompt, user_prompt = self._build_prompts_for_llm(
            agent_info,
            stage_allowed_actions,
            info_pool,
            alliance_chain_summary=alliance_chain_summary,
            neighbor_summary=neighbor_summary
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
                    stage=action_stage.value if hasattr(action_stage, 'value') else str(action_stage),
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
                        user_prompt = self._build_retry_prompt(
                            user_prompt, errors, stage_allowed_actions, all_agent_ids
                        )

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
        info_pool: InfoPool,
        alliance_chain_summary: Optional[str] = None,
        neighbor_summary: Optional[str] = None
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
            'national_interest': agent_info.national_interest,
            'cinc_year': agent_info.cinc_year
        }

        # Generate situation summary for the agent
        situation_summary = self._generate_situation_summary(
            agent_info, info_pool
        )

        # Convert info pool to dict
        info_pool_dict = {
            'all_agent_info': self._format_agents_for_prompt(info_pool.all_agent_info),
            'history_action_records': self._format_history_for_prompt(
                info_pool.history_action_records, agent_info.agent_id
            ),
            'history_power_data': self._format_power_data_for_prompt(
                info_pool.history_power_data
            ),
            'last_round_order_info': str(info_pool.last_round_order_info),
            'alliance_chain_summary': alliance_chain_summary or "【上一轮联盟事件简报】上一轮无重要联盟相关事件",
            'neighbor_summary': neighbor_summary or "【邻接关系简报】未提供邻接数据"
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
            info_pool_dict,
            situation_summary=situation_summary
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

    async def _build_neighbor_summary(
        self,
        project_id: Optional[int],
        agent_info: Any,
        all_agent_info: List[Dict[str, Any]],
    ) -> str:
        """从 AgentNeighborService 读邻接关系, 拼成糊名简报字符串(二元: 邻国 / 非邻国)。

        Args:
            project_id: 项目ID(必须, 否则降级)
            agent_info: AgentInfo dataclass 或 dict, 提供 agent_id/region
            all_agent_info: 全量国家信息(用于糊名列表)

        Returns:
            多行简报字符串
        """
        from app.services.agent_neighbor_service import AgentNeighborService
        from app.config.database import db_config

        if isinstance(agent_info, dict):
            self_id = agent_info.get('agent_id')
            self_region = agent_info.get('region', '未知')
        else:
            self_id = getattr(agent_info, 'agent_id', None)
            self_region = getattr(agent_info, 'region', '未知')

        if not project_id or not self_id:
            return '【邻接关系简报】未提供邻接数据'

        try:
            async with db_config.async_session_factory() as session:
                nb_service = AgentNeighborService(session)
                neighbors_map = await nb_service.get_all_neighbors(project_id, self_id)
            # neighbors_map: {other_agent_id: is_neighbor: bool}
        except Exception as e:
            logger.warning(f"_build_neighbor_summary 查询失败: {e}")
            return '【邻接关系简报】查询失败, 已降级'

        # 拼糊名列表
        neighbor_names: List[str] = []
        non_neighbor_names: List[str] = []
        for info in all_agent_info or []:
            if isinstance(info, dict):
                oid = info.get('agent_id')
                name = info.get('agent_name')
            else:
                oid = getattr(info, 'agent_id', None)
                name = getattr(info, 'agent_name', None)
            if oid is None or oid == self_id or not name:
                continue
            if neighbors_map.get(oid, False):
                neighbor_names.append(name)
            else:
                non_neighbor_names.append(name)

        return (
            f"【邻接关系简报】\n"
            f"所属大洲: {self_region}\n"
            f"邻国: {', '.join(neighbor_names) if neighbor_names else '(无)'}\n"
            f"非邻国: {', '.join(non_neighbor_names) if non_neighbor_names else '(无)'}"
        )

    async def _build_alliance_chain_summary(
        self,
        project_id: Optional[int],
        agent_id: int,
        prev_round: int,
        strategic_relationships: Dict[int, str],
        all_agent_info: List[Dict[str, Any]],
        history_action_records: List[Dict[str, Any]]
    ) -> str:
        """
        构建上一轮同盟链式卷入(chain-ganging)事件简报。

        查询逻辑：
        - 找出当前 agent 的盟友/冲突/战争对象（来自 strategic_relationships）
        - 找出上一轮针对这些对象的敌对动作（军事手段或信息手段）
        - 区分「盟友被攻击」与「对手被攻击」两类事件
        - 若 history_action_records 中已包含上一轮记录，则优先用内存数据避免重复查 DB
        - 否则回退到 SQLAlchemy 查询数据库

        Args:
            project_id: 项目ID（用于 DB 回退查询，可为 None）
            agent_id: 当前决策的智能体ID
            prev_round: 上一轮轮次号（round_num - 1）
            strategic_relationships: 当前 agent 与他国的战略关系映射
            all_agent_info: 全量国家信息（用于名称映射 + DB 回退兜底）
            history_action_records: 历史互动记录（含上一轮记录时优先用）

        Returns:
            格式化的事件简报字符串
        """
        # 分组目标
        ally_ids = {tid for tid, rt in (strategic_relationships or {}).items() if rt == "盟友关系"}
        foe_ids = {tid for tid, rt in (strategic_relationships or {}).items() if rt in ("冲突关系", "战争关系")}

        if prev_round <= 0 or (not ally_ids and not foe_ids):
            return "【上一轮联盟事件简报】上一轮无重要联盟相关事件"

        # 名称映射
        name_map = {
            a.get('agent_id'): a.get('agent_name', f"国家{a.get('agent_id')}")
            for a in (all_agent_info or [])
        }

        hostile_categories = {"军事手段", "信息手段"}
        target_set = ally_ids | foe_ids

        # 优先用内存中的历史记录
        prev_round_records: List[Dict[str, Any]] = []
        if history_action_records:
            prev_round_records = [
                r for r in history_action_records
                if r.get('round_num') == prev_round
                and r.get('action_category') in hostile_categories
                and r.get('target_agent_id') in target_set
                and r.get('source_agent_id') != agent_id
            ]

        # 回退：若内存中没有上一轮记录（如外部缓存未携带），用 SQLAlchemy 查 DB
        if not prev_round_records and project_id is not None and history_action_records is not None and not any(
            r.get('round_num') == prev_round for r in history_action_records
        ):
            try:
                from sqlalchemy import select
                from app.config.database import db_config
                from app.models import ActionRecord, AgentConfig

                async for session in db_config.get_session():
                    stmt = (
                        select(ActionRecord, AgentConfig.agent_name)
                        .join(AgentConfig, ActionRecord.source_agent_id == AgentConfig.agent_id)
                        .where(
                            ActionRecord.project_id == project_id,
                            ActionRecord.round_num == prev_round,
                            ActionRecord.action_category.in_(list(hostile_categories)),
                            ActionRecord.target_agent_id.in_(list(target_set)),
                            ActionRecord.source_agent_id != agent_id,
                        )
                    )
                    result = await session.execute(stmt)
                    for ar, src_name in result.all():
                        prev_round_records.append({
                            'source_agent_id': ar.source_agent_id,
                            'target_agent_id': ar.target_agent_id,
                            'action_name': ar.action_name,
                            'action_category': ar.action_category,
                            'round_num': ar.round_num,
                            'source_agent_name': src_name,
                        })
                    break  # 单次拿一个 session 即可
            except Exception as e:
                logger.warning(f"_build_alliance_chain_summary DB回退查询失败: {e}")

        if not prev_round_records:
            return "【上一轮联盟事件简报】上一轮无重要联盟相关事件"

        ally_attack_lines: List[str] = []
        foe_attack_lines: List[str] = []
        for r in prev_round_records:
            src_id = r.get('source_agent_id')
            tgt_id = r.get('target_agent_id')
            action_name = r.get('action_name', '?')
            rnd = r.get('round_num', prev_round)
            src_name = r.get('source_agent_name') or name_map.get(src_id, f"国家{src_id}")
            tgt_name = name_map.get(tgt_id, f"国家{tgt_id}")

            if tgt_id in ally_ids:
                ally_attack_lines.append(
                    f"    * {tgt_name}(ID{tgt_id}) 被 {src_name}(ID{src_id}) 实施「{action_name}」(第{rnd}轮)\n"
                    f"      → 你与 {tgt_name} 是 ALLIANCE 关系, 本轮你对 {src_name} 采取敌对行为额外+0.3收益"
                )
            elif tgt_id in foe_ids:
                foe_attack_lines.append(
                    f"    * {tgt_name}(ID{tgt_id}) 被 {src_name}(ID{src_id}) 实施「{action_name}」(第{rnd}轮)\n"
                    f"      → 你与 {tgt_name} 是 CONFLICT/WAR 关系, 本轮你对 {tgt_name} 施压可获+0.15趁火打劫收益"
                )

        lines = ["【上一轮联盟事件简报】"]
        if ally_attack_lines:
            lines.append("  - 盟友被攻击事件:")
            lines.extend(ally_attack_lines)
        if foe_attack_lines:
            lines.append("  - 对手被攻击事件:")
            lines.extend(foe_attack_lines)
        if len(lines) == 1:
            return "【上一轮联盟事件简报】上一轮无重要联盟相关事件"
        return "\n".join(lines)

    def _build_retry_prompt(
        self,
        original_prompt: str,
        validation_errors: List[str],
        allowed_actions: List[Dict[str, Any]],
        all_agent_ids: List[int]
    ) -> str:
        """
        Build retry prompt with validation errors and valid ID references.

        Args:
            original_prompt: Original decision prompt
            validation_errors: List of validation errors
            allowed_actions: List of allowed actions for reference
            all_agent_ids: List of valid agent IDs

        Returns:
            Retry prompt with error context
        """
        error_summary = "\n".join([f"- {error}" for error in validation_errors])

        valid_action_ids = sorted({a.get('action_id') for a in allowed_actions if a.get('action_id') is not None})
        valid_action_names = sorted({a.get('action_name') for a in allowed_actions if a.get('action_name')})

        retry_instruction = f"""
【上一次决策验证失败，请重新生成决策】

【验证错误列表】
{error_summary}

【有效行为白名单】
- 有效 action_id（必须从中选择）: {valid_action_ids}
- 有效 action_name（必须与之一致）: {valid_action_names}

【有效目标国ID】
- 目标国 agent_id 必须是以下值之一: {sorted(all_agent_ids)}
- 禁止指向不存在国家的ID

【修正要求】
1. 请严格根据上述错误和有效白名单修正你的决策；
2. action_id 必须是白名单中的整数，禁止使用字符串或其他格式；
3. action_name 必须与白名单中的名称完全一致；
4. target_agent_id 必须存在于有效目标国列表中；
5. 确保决策符合你的领导类型约束和国家利益；
6. 确保包含完整的成本收益分析。

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

        # Execute full validation (含新增Tier 3行为前置条件校验)
        is_valid, errors = self.validator.validate_full_decision(
            decision=decision,
            agent_info=agent_dict,
            allowed_actions=allowed_actions,
            all_agent_ids=all_agent_ids,
            national_interests=agent_info.national_interest,
            action_stage=action_stage.value,
            strategic_relationships=agent_info.strategic_relationships,
            action_history=info_pool.history_action_records
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
                f"CINC:{agent.get('current_total_power', 0):.4f} | "
                f"实力层级:{agent.get('power_level', 'N/A')} | "
                f"领导类型:{agent.get('leader_type', 'N/A')} | "
                f"战略关系:{self._format_relationships_for_prompt(agent.get('strategic_relationships', {}))}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _format_relationships_for_prompt(self, relationships: Dict[int, str]) -> str:
        """Format strategic relationships, grouped by type for better readability.

        旧格式：134:盟友关系, 135:战争关系, 136:战争关系, ... （平铺，密集易读漏）
        新格式：[战争:135,136][冲突:][盟友:134][伙伴:137]  （按类型聚合，醒目）
        无外交关系超过5国时折叠为 [中立:共N国]，避免占用大量token。
        """
        logger.debug(f"格式化战略关系输入: {relationships}")
        if not relationships:
            logger.debug("战略关系为空，返回'无'")
            return "无"

        # 按类型分组
        by_type: Dict[str, List[int]] = {}
        for tid, rt in relationships.items():
            by_type.setdefault(rt, []).append(tid)

        # 输出顺序：战争>冲突>盟友>伙伴>中立（重要的放前面）
        ordered_types = [
            ("战争关系", "战争"),
            ("冲突关系", "冲突"),
            ("盟友关系", "盟友"),
            ("伙伴关系", "伙伴"),
            ("无外交关系", "中立"),
        ]

        parts: List[str] = []
        for full_name, short_name in ordered_types:
            ids = by_type.get(full_name)
            if not ids:
                continue
            ids_sorted = sorted(ids)
            if full_name == "无外交关系" and len(ids_sorted) > 5:
                parts.append(f"[{short_name}:共{len(ids_sorted)}国]")
            else:
                parts.append(f"[{short_name}:{','.join(str(i) for i in ids_sorted)}]")

        # 兜底：若有未在已知类型表中的关系（例如未来新增类型），也显示出来
        unknown_types = set(by_type.keys()) - {full for full, _ in ordered_types}
        for rt in sorted(unknown_types):
            ids_sorted = sorted(by_type[rt])
            parts.append(f"[{rt}:{','.join(str(i) for i in ids_sorted)}]")

        result = "".join(parts) if parts else "无"
        logger.debug(f"格式化战略关系输出: {result}")
        return result

    def _format_history_for_prompt(
        self,
        history: List[Dict[str, Any]],
        agent_id: Optional[int] = None
    ) -> str:
        """Format action history for prompt, aggregated by relationship pair.

        历史记录长度控制策略：
        - 最近10轮的记录做详细聚合（按关系对统计 + 最近5条详细记录）
        - 超过10轮的早期记录只做极简统计（关系对级别的合作/对抗次数）

        若 agent_id 为 None（追随决策、关系演变等非单 agent 视角），按 (source, target)
        关系对全局聚合；否则按当前 agent 的 outgoing/incoming 视角聚合。
        """
        if not history:
            return "无历史互动行为记录"

        from collections import defaultdict

        # Categorize actions
        cooperation_actions = {"发表公开声明", "呼吁/请求", "表达合作意向", "协商/磋商",
                               "开展外交合作", "开展实质性合作", "提供援助", "让步/屈服"}

        # 按轮次分组并分离近期/早期记录
        round_groups = defaultdict(list)
        for record in history:
            round_groups[record.get('round_num', 0)].append(record)

        all_rounds = sorted(round_groups.keys())
        recent_rounds_set = set(all_rounds[-10:]) if len(all_rounds) > 10 else set(all_rounds)

        recent_records = [r for r in history if r.get('round_num', 0) in recent_rounds_set]
        older_records = [r for r in history if r.get('round_num', 0) not in recent_rounds_set]

        lines = []

        # ========== 早期记录极简统计 ==========
        if older_records:
            lines.append("【早期互动概要】（仅统计）：")
            pair_stats = defaultdict(lambda: {"cooperation": 0, "conflict": 0})
            for record in older_records:
                src = record.get('source_agent_id')
                tgt = record.get('target_agent_id')
                if src is None or tgt is None:
                    continue
                key = (min(src, tgt), max(src, tgt))
                name = record.get('action_name', '')
                if name in cooperation_actions:
                    pair_stats[key]["cooperation"] += 1
                else:
                    pair_stats[key]["conflict"] += 1

            for (a, b), stats in sorted(pair_stats.items()):
                lines.append(
                    f"  ID{a}<->ID{b}: 合作{stats['cooperation']}次, 对抗{stats['conflict']}次"
                )
            lines.append("")  # 空行分隔

        # ========== 最近10轮详细聚合 ==========
        if recent_records:
            earliest_recent = min(r.get('round_num', 0) for r in recent_records)
            lines.append(f"【最近轮次详细互动】（轮次{earliest_recent}起，共{len(recent_records)}条记录）：")

            if agent_id is not None:
                outgoing = defaultdict(lambda: {"cooperation": 0, "conflict": 0, "actions": []})
                incoming = defaultdict(lambda: {"cooperation": 0, "conflict": 0, "actions": []})

                for record in recent_records:
                    src = record.get('source_agent_id')
                    tgt = record.get('target_agent_id')
                    name = record.get('action_name', '')
                    cat = "cooperation" if name in cooperation_actions else "conflict"

                    if src == agent_id and tgt is not None:
                        outgoing[tgt][cat] += 1
                        outgoing[tgt]["actions"].append(name)
                    elif tgt == agent_id and src is not None:
                        incoming[src][cat] += 1
                        incoming[src]["actions"].append(name)

                if outgoing:
                    lines.append("你作为发起方的互动：")
                    for target_id, stats in sorted(outgoing.items()):
                        action_list = ", ".join(sorted(set(stats["actions"])))
                        lines.append(
                            f"  -> ID{target_id}: 合作类{stats['cooperation']}次, "
                            f"对抗类{stats['conflict']}次 | 行为:{action_list}"
                        )

                if incoming:
                    lines.append("其他国对你发起的互动：")
                    for source_id, stats in sorted(incoming.items()):
                        action_list = ", ".join(sorted(set(stats["actions"])))
                        lines.append(
                            f"  ID{source_id}->你: 合作类{stats['cooperation']}次, "
                            f"对抗类{stats['conflict']}次 | 行为:{action_list}"
                        )
            else:
                pair_stats = defaultdict(lambda: {"cooperation": 0, "conflict": 0, "actions": []})
                for record in recent_records:
                    src = record.get('source_agent_id')
                    tgt = record.get('target_agent_id')
                    if src is None or tgt is None:
                        continue
                    name = record.get('action_name', '')
                    cat = "cooperation" if name in cooperation_actions else "conflict"
                    key = (src, tgt)
                    pair_stats[key][cat] += 1
                    pair_stats[key]["actions"].append(name)

                if pair_stats:
                    lines.append("各关系对互动汇总：")
                    for (src, tgt), stats in sorted(pair_stats.items()):
                        action_list = ", ".join(sorted(set(stats["actions"])))
                        lines.append(
                            f"  ID{src}->ID{tgt}: 合作类{stats['cooperation']}次, "
                            f"对抗类{stats['conflict']}次 | 行为:{action_list}"
                        )

            # 最近5条详细记录（仅在 recent_records 中选取）
            detailed = recent_records[-5:] if len(recent_records) > 5 else recent_records
            if detailed:
                lines.append("最近5条详细记录（含具体内容，供参考）：")
                for record in detailed:
                    content = record.get('action_content', '')
                    content_display = content[:80] + "..." if len(content) > 80 else content
                    line = (
                        f"  轮次{record.get('round_num', 'N/A')}: "
                        f"{record.get('source_agent_id', 'N/A')}->{record.get('target_agent_id', 'N/A')} "
                        f"【{record.get('action_name', 'N/A')}】"
                    )
                    if content_display:
                        line += f" 内容:{content_display}"
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
                f"初始CINC:{data.get('round_start_power', 0):.6f} | "
                f"结束CINC:{data.get('round_end_power', 0):.6f} | "
                f"变化值:{data.get('round_change_value', 0):.6f}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _generate_situation_summary(
        self,
        agent_info: AgentInfo,
        info_pool: InfoPool
    ) -> str:
        """Generate a concise situation summary for the agent's decision context."""
        from collections import Counter

        lines = []
        agent_id = agent_info.agent_id
        current_power = agent_info.current_total_power

        # 1. Self status
        lines.append(f"- 你的当前CINC: {current_power:.4f}, 实力层级: {agent_info.power_level}, 领导类型: {agent_info.leader_type or '未定义'}")

        # 2. Ranking in the system
        if info_pool.all_agent_info:
            sorted_agents = sorted(
                info_pool.all_agent_info,
                key=lambda a: a.get('current_total_power', 0),
                reverse=True
            )
            rank = next(
                (i + 1 for i, a in enumerate(sorted_agents)
                 if a.get('agent_id') == agent_id),
                len(sorted_agents)
            )
            total = len(sorted_agents)
            lines.append(f"- 你的CINC排名: 第{rank}名/共{total}国")

            # Top 3 powers
            top3 = [
                f"ID{a.get('agent_id')}({a.get('agent_name')}): {a.get('current_total_power', 0):.4f}"
                for a in sorted_agents[:3]
            ]
            lines.append(f"- 当前实力前三: {' | '.join(top3)}")

        # 3. 实力矩阵：与各国的CINC对比（用于评估军事冲突获胜概率）
        if info_pool.all_agent_info:
            lines.append("- 【实力矩阵-你与各国的CINC比值（用于评估军事冲突获胜概率）】:")
            for other in info_pool.all_agent_info:
                other_id = other.get('agent_id')
                if other_id == agent_id:
                    continue
                other_power = other.get('current_total_power', 0)
                if other_power > 0 and current_power > 0:
                    ratio = current_power / other_power
                    assessment = "明显强于" if ratio >= 2.0 else ("略强于" if ratio >= 1.0 else ("略弱于" if ratio >= 0.5 else "明显弱于"))
                    win_prob = "极高" if ratio >= 2.0 else ("较高" if ratio >= 1.0 else ("较低" if ratio >= 0.5 else "极低"))
                    lines.append(
                        f"  ID{other_id}({other.get('agent_name')}): 你的CINC/对方CINC={ratio:.2f}, "
                        f"判定为{assessment}对手, 军事冲突获胜概率{win_prob}"
                    )

        # 4. Strategic relationships summary
        own_relationships = agent_info.strategic_relationships or {}
        if own_relationships:
            allies = [f"ID{tid}" for tid, rt in own_relationships.items() if rt == "盟友关系"]
            partners = [f"ID{tid}" for tid, rt in own_relationships.items() if rt == "伙伴关系"]
            conflicts = [f"ID{tid}" for tid, rt in own_relationships.items() if rt == "冲突关系"]
            wars = [f"ID{tid}" for tid, rt in own_relationships.items() if rt == "战争关系"]
            if allies:
                lines.append(f"- 盟友: {', '.join(allies)}")
            if partners:
                lines.append(f"- 伙伴: {', '.join(partners)}")
            if conflicts:
                lines.append(f"- 冲突方: {', '.join(conflicts)}")
            if wars:
                lines.append(f"- 战争方: {', '.join(wars)}")
        else:
            lines.append("- 战略关系: 无")

        # 4. Recent own actions summary (last round)
        own_recent = [
            r for r in info_pool.history_action_records
            if r.get('source_agent_id') == agent_id
        ]
        if own_recent:
            last_round = max(r.get('round_num', 0) for r in own_recent)
            last_actions = [r for r in own_recent if r.get('round_num') == last_round]
            action_names = [r.get('action_name', '?') for r in last_actions]
            targets = [str(r.get('target_agent_id', '?')) for r in last_actions]
            lines.append(f"- 上一轮(R{last_round})你的行为: {' -> '.join(action_names)} | 目标: {', '.join(targets)}")
        else:
            lines.append("- 上一轮你的行为: 无（这是第一轮）")

        # 5. Recent power trend
        own_power = [
            d for d in info_pool.history_power_data
            if d.get('agent_id') == agent_id
        ]
        if own_power:
            recent = own_power[-3:] if len(own_power) > 3 else own_power
            changes = [d.get('round_change_value', 0) for d in recent]
            trend = "上升" if sum(changes) > 0 else ("下降" if sum(changes) < 0 else "持平")
            lines.append(f"- 最近{len(recent)}轮国力趋势: {trend} (变化值: {', '.join(f'{c:+.4f}' for c in changes)})")
        else:
            lines.append("- 国力趋势: 无历史数据")

        # 6. Conflict escalation trajectory (new)
        cooperation_actions = {"发表公开声明", "呼吁/请求", "表达合作意向", "协商/磋商",
                               "开展外交合作", "开展实质性合作", "提供援助", "让步/屈服"}
        dyad_records = {}
        for record in info_pool.history_action_records:
            src = record.get('source_agent_id')
            tgt = record.get('target_agent_id')
            if src == agent_id and tgt is not None:
                dyad_records.setdefault(tgt, []).append(record)
            elif tgt == agent_id and src is not None:
                dyad_records.setdefault(src, []).append(record)

        escalation_lines = []
        for other_id, records in sorted(dyad_records.items()):
            # Sort by round and take last 3 interactions
            sorted_records = sorted(records, key=lambda r: r.get('round_num', 0))
            recent = sorted_records[-3:]
            if len(recent) >= 3:
                action_names = [r.get('action_name', '') for r in recent]
                rounds = [r.get('round_num', '?') for r in recent]
                is_all_conflict = all(name not in cooperation_actions for name in action_names)
                is_all_cooperation = all(name in cooperation_actions for name in action_names)

                if is_all_conflict:
                    escalation_lines.append(
                        f"ID{other_id}: 轮次{rounds[0]}-{rounds[-1]} 连续{len(recent)}轮对抗 "
                        f"({'→'.join(action_names)}), **冲突正在快速升级**"
                    )
                elif is_all_cooperation:
                    escalation_lines.append(
                        f"ID{other_id}: 轮次{rounds[0]}-{rounds[-1]} 连续{len(recent)}轮合作 "
                        f"({'→'.join(action_names)}), 关系稳定缓和"
                    )
                else:
                    escalation_lines.append(
                        f"ID{other_id}: 轮次{rounds[0]}-{rounds[-1]} 混合互动 "
                        f"({'→'.join(action_names)}), 冲突态势不确定"
                    )

        if escalation_lines:
            lines.append("- 【冲突升级轨迹-最近3轮互动模式】:")
            for el in escalation_lines:
                lines.append(f"  {el}")
        else:
            lines.append("- 【冲突升级轨迹】: 历史互动数据不足以判定趋势（至少需要3轮互动）")

        # 7. Order info
        order_info = info_pool.last_round_order_info or {}
        if order_info:
            order_type = order_info.get('order_type', '未确定')
            has_leader = order_info.get('has_leader', False)
            leader_id = order_info.get('leader_agent_id')
            lines.append(f"- 当前秩序: {order_type}, 有领导者: {'是' if has_leader else '否'}{f' (领导者ID:{leader_id})' if leader_id else ''}")

        return "\n".join(lines)


class CostBenefitAnalyzer:
    """Cost-benefit analysis helper for decision engine."""

    # Leader type behavior value weights (aligns with prompt_templates.py LEADER_TYPE_RULES)
    _LEADER_TYPE_WEIGHTS = {
        "王道型": {
            "respect_sov_bonus": 0.2,
            "disrespect_sov_penalty": -0.3,
            "cooperation_bonus": 0.1,
            "military_deterrence_cost": -0.1,
            "ally_bonus": 0.15,
        },
        "霸权型": {
            "material_interest_bonus": 0.15,
            "influence_bonus": 0.1,
            "military_deterrence_bonus": 0.1,
            "weak_opponent_discount": -0.1,
        },
        "强权型": {
            "military_coercion_bonus": 0.2,
            "weak_opponent_bonus": 0.1,
        },
        "昏庸型": {
            "random_variance": 0.2,
            "short_term_bonus": 0.1,
            "high_risk_bonus": 0.1,
            "prestige_bonus": 0.1,
        },
    }

    @staticmethod
    def calculate_net_benefit(
        action_config: Dict[str, Any],
        agent_power: float,
        strategic_importance: float = 1.0,
        leader_type: Optional[str] = None,
        target_power: Optional[float] = None
    ) -> float:
        """
        Calculate net benefit of an action.

        Args:
            action_config: Action configuration
            agent_power: Current agent power
            strategic_importance: Strategic importance multiplier
            leader_type: Optional leader type for behavioral weight adjustment
            target_power: Optional target agent power for military balance adjustment

        Returns:
            Net benefit score
        """
        import random

        # Power change from action
        power_change = action_config.get('initiator_power_change', 0)

        # Relative power impact (normalized by agent power)
        if agent_power > 0:
            relative_impact = power_change / agent_power
        else:
            relative_impact = 0

        # Base net benefit - removed respect_sov penalty to avoid systematic bias toward cooperation
        net_benefit = (power_change + relative_impact * 100) * strategic_importance

        # Apply leader type behavioral weights
        if leader_type and leader_type in CostBenefitAnalyzer._LEADER_TYPE_WEIGHTS:
            weights = CostBenefitAnalyzer._LEADER_TYPE_WEIGHTS[leader_type]

            if leader_type == "王道型":
                if action_config.get('respect_sov', True):
                    net_benefit += weights.get('respect_sov_bonus', 0)
                else:
                    net_benefit += weights.get('disrespect_sov_penalty', 0)
                if action_config.get('action_category') in {'外交手段', '经济手段'}:
                    net_benefit += weights.get('cooperation_bonus', 0)
                if action_config.get('action_name') in {'威胁', '展示军事姿态'}:
                    net_benefit += weights.get('military_deterrence_cost', 0)

            elif leader_type == "霸权型":
                if action_config.get('action_name') in {'开展实质性合作', '提供援助', '开展外交合作'}:
                    net_benefit += weights.get('material_interest_bonus', 0)
                if action_config.get('action_name') in {'威胁', '展示军事姿态', '胁迫/强制'}:
                    net_benefit += weights.get('military_deterrence_bonus', 0)
                if action_config.get('action_category') in {'外交手段', '经济手段'}:
                    net_benefit += weights.get('influence_bonus', 0)

            elif leader_type == "强权型":
                if action_config.get('action_category') == '军事手段':
                    net_benefit += weights.get('military_coercion_bonus', 0)
                if action_config.get('action_name') in {'攻击/袭击', '交战/使用常规军事武力'}:
                    net_benefit += weights.get('weak_opponent_bonus', 0)

            elif leader_type == "昏庸型":
                # Random variance for inept leader type
                variance = weights.get('random_variance', 0)
                net_benefit += random.uniform(-variance, variance)
                if action_config.get('action_name') in {'发表公开声明', '展示军事姿态'}:
                    net_benefit += weights.get('prestige_bonus', 0)

        # Apply military balance adjustment based on power ratio
        # Core logic: military actions against weaker opponents are more profitable (higher win probability)
        if target_power is not None and target_power > 0 and agent_power > 0:
            power_ratio = agent_power / target_power
            action_category = action_config.get('action_category', '')
            action_name = action_config.get('action_name', '')
            military_actions = {'威胁', '展示军事姿态', '胁迫/强制', '攻击/袭击', '交战/使用常规军事武力', '实施非常规大规模暴力'}

            if action_category == '军事手段' or action_name in military_actions:
                if power_ratio >= 2.0:
                    # Significantly stronger -> much higher win probability
                    net_benefit += 0.15
                elif power_ratio >= 1.0:
                    # Moderately stronger -> higher win probability
                    net_benefit += 0.05
                elif power_ratio >= 0.5:
                    # Moderately weaker -> lower win probability, risk of defeat
                    net_benefit -= 0.10
                else:
                    # Significantly weaker -> very low win probability, likely disastrous defeat
                    net_benefit -= 0.25

        return net_benefit

    @staticmethod
    def rank_actions_by_benefit(
        actions: List[Dict[str, Any]],
        agent_power: float,
        leader_type: Optional[str] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank actions by net benefit.

        Args:
            actions: List of action configurations
            agent_power: Current agent power
            leader_type: Optional leader type for behavioral weight adjustment

        Returns:
            List of (action, net_benefit) tuples sorted by benefit
        """
        ranked = []
        for action in actions:
            net_benefit = CostBenefitAnalyzer.calculate_net_benefit(
                action, agent_power, leader_type=leader_type
            )
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
