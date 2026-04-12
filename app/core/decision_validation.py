"""
决策验证模块
Decision Validation Module

为LLM驱动的决策引擎实现三层决策验证机制。
完全对齐技术规范第4.2.4节。
"""

from typing import Dict, Any, List, Tuple

from loguru import logger

# Import enums from agent_base to avoid duplication
from .agent_base import PowerLevelEnum, LeaderTypeEnum


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DecisionValidator:
    """Three-tier decision validation for LLM decisions."""

    def __init__(self, standard_behaviors: List[Dict[str, Any]]):
        """
        Initialize validator with standard 20 behaviors.

        Args:
            standard_behaviors: List of 20 standard GDELT behaviors
        """
        self.standard_behaviors = standard_behaviors
        self.behavior_id_map = {b['action_id']: b for b in standard_behaviors}
        self.behavior_name_map = {b['action_name']: b for b in standard_behaviors}

    def validate_behavior_set(
        self,
        action_id: int,
        action_name: str,
        allowed_actions: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Tier 1: Validate behavior is in standard 20-behavior set.

        Args:
            action_id: Action ID from LLM decision
            action_name: Action name from LLM decision
            allowed_actions: List of actions allowed for this agent

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Convert action_id to int if it's a string (LLM sometimes returns strings)
        try:
            action_id = int(action_id)
        except (ValueError, TypeError):
            return False, f"行为ID {action_id} 格式无效，必须为整数"

        # Debug logging
        logger.debug(
            f"validate_behavior_set: action_id={action_id}, action_name='{action_name}', "
            f"behavior_id_map has {len(self.behavior_id_map)} items, "
            f"behavior_name_map has {len(self.behavior_name_map)} items, "
            f"allowed_actions has {len(allowed_actions)} items"
        )

        # Check if action ID exists in standard set
        if action_id not in self.behavior_id_map:
            return False, f"行为ID {action_id} 不在20项标准行为集内"

        # Check if action name exists in standard set
        if action_name not in self.behavior_name_map:
            return False, f"行为名称 '{action_name}' 不在20项标准行为集内"

        # Check if ID and name match
        standard_action = self.behavior_id_map[action_id]
        if standard_action['action_name'] != action_name:
            return False, f"行为ID {action_id} 与行为名称 '{action_name}' 不匹配"

        # Check if action is in allowed list for this agent
        allowed_ids = {int(a['action_id']) if isinstance(a['action_id'], str) else a['action_id'] for a in allowed_actions}
        if action_id not in allowed_ids:
            return False, f"行为ID {action_id} 不在该智能体的允许行为列表内"

        return True, ""

    def validate_basic(
        self,
        decision: Dict[str, Any],
        agent_id: int,
        all_agent_ids: List[int],
        action_stage: str = "initiative"
    ) -> Tuple[bool, str]:
        """
        Tier 2: Basic validation (format, target agent, permissions).

        Args:
            decision: Decision dict from LLM
            agent_id: ID of agent making decision
            all_agent_ids: List of all valid agent IDs in system
            action_stage: Current action stage ("initiative" or "response")

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate decision structure
        if 'actions' not in decision:
            return False, "决策中缺少 'actions' 字段"

        actions = decision['actions']
        if not isinstance(actions, list):
            return False, "'actions' 字段必须是列表"

        if len(actions) == 0:
            return False, "必须至少选择一个行为"

        if len(actions) > 5:
            return False, "最多只能选择5个行为"

        # Validate each action
        for i, action in enumerate(actions):
            # Check required fields
            required_fields = ['action_id', 'action_category', 'action_name',
                            'target_agent_id', 'cost_benefit_analysis', 'action_content']
            for field in required_fields:
                if field not in action:
                    return False, f"行为 {i+1} 缺少必需字段: {field}"

            # Validate target agent ID
            target_agent_id = action['target_agent_id']
            # Convert to int if it's a string
            try:
                target_agent_id = int(target_agent_id)
            except (ValueError, TypeError):
                return False, f"行为 {i+1} 的 target_agent_id 必须是整数"

            if target_agent_id not in all_agent_ids:
                return False, f"行为 {i+1} 的目标国家ID {target_agent_id} 不存在"

            if target_agent_id == agent_id:
                return False, f"行为 {i+1} 不能以自己为目标国家"

            # Validate cost-benefit analysis
            cost_benefit = action['cost_benefit_analysis']
            if not isinstance(cost_benefit, str) or len(cost_benefit.strip()) == 0:
                return False, f"行为 {i+1} 缺少有效的成本收益分析"

            # Validate action_content
            action_content = action.get('action_content', '')
            if not isinstance(action_content, str):
                return False, f"行为 {i+1} 的 action_content 必须是字符串"
            content_len = len(action_content.strip())
            if content_len == 0:
                return False, f"行为 {i+1} 缺少 action_content（具体执行内容）"
            if content_len < 50 or content_len > 300:
                return False, f"行为 {i+1} 的 action_content 长度需在50-300字之间（当前{content_len}字）"

        return True, ""

    def validate_action_prerequisites(
        self,
        action: Dict[str, Any],
        strategic_relationships: Dict[int, str],
        action_history: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        验证行为是否满足前置条件（关系状态、历史互动等）。

        Args:
            action: 行为字典，包含 action_id, action_name, target_agent_id
            strategic_relationships: 当前agent与各国的战略关系映射 {target_id: relationship_type}
            action_history: 历史行为记录列表

        Returns:
            Tuple of (is_valid, error_message)
        """
        action_id = action.get('action_id')
        target_id = action.get('target_agent_id')

        # 获取行为名称
        standard_action = self.behavior_id_map.get(action_id)
        if not standard_action:
            return True, ""  # 不在标准行为集中，由validate_behavior_set处理
        action_name = standard_action.get('action_name', '')

        rel = strategic_relationships.get(target_id, "无外交关系")

        # 规则1: 交战/使用常规军事武力 仅在冲突/战争关系下可选
        if action_name == "交战/使用常规军事武力":
            if rel not in ["冲突关系", "战争关系"]:
                return False, (
                    f"交战行为要求与目标国(ID:{target_id})的关系为冲突或战争，"
                    f"当前关系为'{rel}'。请先选择'展示军事姿态'或'威胁'铺垫。"
                )

        # 规则2: 攻击/袭击 仅在冲突/战争关系下可选
        if action_name == "攻击/袭击":
            if rel not in ["冲突关系", "战争关系"]:
                return False, (
                    f"攻击行为要求与目标国(ID:{target_id})的关系为冲突或战争，"
                    f"当前关系为'{rel}'。"
                )

        # 规则3: 胁迫/强制 需要至少1轮的展示军事姿态或威胁铺垫
        if action_name == "胁迫/强制":
            # 检查最近5轮是否有对目标国的军事姿态或威胁
            recent_prelude = [
                r for r in action_history
                if r.get('target_agent_id') == target_id
                and r.get('action_name') in ['展示军事姿态', '威胁']
            ]
            if not recent_prelude:
                return False, (
                    f"胁迫/强制行为需要对目标国(ID:{target_id})"
                    f"有过'展示军事姿态'或'威胁'作为铺垫。请先选择较低烈度行为。"
                )

        return True, ""

    def validate_full_decision(
        self,
        decision: Dict[str, Any],
        agent_info: Dict[str, Any],
        allowed_actions: List[Dict[str, Any]],
        all_agent_ids: List[int],
        national_interests: List[str],
        action_stage: str = "initiative",
        strategic_relationships: Dict[int, str] = None,
        action_history: List[Dict[str, Any]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Execute full three-tier validation.

        Args:
            decision: Decision dict from LLM
            agent_info: Agent information
            allowed_actions: List of actions allowed for this agent
            all_agent_ids: List of all valid agent IDs
            national_interests: List of national interests
            action_stage: Current action stage
            strategic_relationships: 当前agent与各国的战略关系映射
            action_history: 历史行为记录列表

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Tier 1: Behavior set validation
        for action in decision.get('actions', []):
            action_id = action.get('action_id')
            action_name = action.get('action_name')

            is_valid, error = self.validate_behavior_set(
                action_id, action_name, allowed_actions
            )
            if not is_valid:
                errors.append(f"[Tier 1 行为集校验] {error}")

        if errors:
            return False, errors

        # Tier 2: Basic validation
        agent_id = agent_info.get('agent_id')
        is_valid, error = self.validate_basic(
            decision, agent_id, all_agent_ids, action_stage
        )
        if not is_valid:
            errors.append(f"[Tier 2 基础校验] {error}")
            return False, errors

        # Tier 3: Action prerequisites validation (新增)
        if strategic_relationships and action_history is not None:
            for action in decision.get('actions', []):
                is_valid, error = self.validate_action_prerequisites(
                    action, strategic_relationships, action_history
                )
                if not is_valid:
                    errors.append(f"[Tier 3 前置条件校验] {error}")

            if errors:
                return False, errors

        return True, []


class ComplianceChecker:
    """Helper class for compliance checking rules."""

    @staticmethod
    def can_leader_execute_action(
        leader_type: str,
        action_config: Dict[str, Any]
    ) -> bool:
        """
        Check if leader type can execute action based on forbidden types.

        Args:
            leader_type: Leader type enum value
            action_config: Action configuration dict

        Returns:
            True if leader can execute action
        """
        forbidden_types = action_config.get('forbidden_leader_type', [])
        return leader_type not in forbidden_types

    @staticmethod
    def is_action_aligned_with_national_interest(
        action_config: Dict[str, Any],
        national_interests: List[str]
    ) -> bool:
        """
        Check if action aligns with national interests.

        Args:
            action_config: Action configuration dict
            national_interests: List of national interests

        Returns:
            True if action aligns with interests
        """
        # Respect sovereignty actions generally align with interests
        if action_config.get('respect_sov', False):
            return True

        # Power-positive actions align with interests
        if action_config.get('initiator_power_change', 0) > 0:
            return True

        # Other actions need context-specific judgment
        return False

    @staticmethod
    def get_stage_rules(action_stage: str) -> Dict[str, Any]:
        """
        Get validation rules for specific action stage.

        Args:
            action_stage: "initiative" or "response"

        Returns:
            Dict of stage-specific rules
        """
        if action_stage == "initiative":
            return {
                "allow_high_intensity": ["超级大国", "大国"],
                "max_action_count": 5,
                "require_target_agent": True
            }
        elif action_stage == "response":
            return {
                "allow_high_intensity": ["超级大国", "大国", "中等强国"],
                "max_action_count": 3,
                "require_target_agent": True
            }
        else:
            return {}
