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
            if content_len > 0 and (content_len < 10 or content_len > 500):
                return False, f"行为 {i+1} 的 action_content 长度需在10-500字之间（当前{content_len}字）"

        return True, ""

    def validate_full_decision(
        self,
        decision: Dict[str, Any],
        agent_info: Dict[str, Any],
        allowed_actions: List[Dict[str, Any]],
        all_agent_ids: List[int],
        national_interests: List[str],
        action_stage: str = "initiative"
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
