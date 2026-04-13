"""
Decision validation module for LLM-driven decision engine.
Implements three-tier decision validation as per technical spec section 4.2.4.
"""

from typing import Dict, Any, List, Tuple

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
        allowed_ids = {a['action_id'] for a in allowed_actions}
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
                            'target_agent_id', 'cost_benefit_analysis']
            for field in required_fields:
                if field not in action:
                    return False, f"行为 {i+1} 缺少必需字段: {field}"

            # Validate target agent ID
            target_agent_id = action['target_agent_id']
            if not isinstance(target_agent_id, int):
                return False, f"行为 {i+1} 的 target_agent_id 必须是整数"

            if target_agent_id not in all_agent_ids:
                return False, f"行为 {i+1} 的目标国家ID {target_agent_id} 不存在"

            if target_agent_id == agent_id:
                return False, f"行为 {i+1} 不能以自己为目标国家"

            # Validate cost-benefit analysis
            cost_benefit = action['cost_benefit_analysis']
            if not isinstance(cost_benefit, str) or len(cost_benefit.strip()) == 0:
                return False, f"行为 {i+1} 缺少有效的成本收益分析"

        return True, ""

    def validate_compliance(
        self,
        decision: Dict[str, Any],
        agent_info: Dict[str, Any],
        national_interests: List[str],
        action_stage: str = "initiative"
    ) -> Tuple[bool, str]:
        """
        Tier 3: Compliance validation (national interest, leader type constraints).

        Args:
            decision: Decision dict from LLM
            agent_info: Agent information including power level and leader type
            national_interests: List of national interests based on power level
            action_stage: Current action stage ("initiative" or "response")

        Returns:
            Tuple of (is_valid, error_message)
        """
        leader_type = agent_info.get('leader_type')
        power_level = agent_info.get('power_level')

        # Get selected actions
        actions = decision.get('actions', [])

        # Validate leader type constraints
        for action in actions:
            action_id = action['action_id']

            if action_id not in self.behavior_id_map:
                return False, f"行为ID {action_id} 未找到标准行为定义"

            standard_action = self.behavior_id_map[action_id]
            forbidden_types = standard_action.get('forbidden_leader_type', [])

            # Check if leader type is forbidden for this action
            if leader_type and leader_type in forbidden_types:
                return False, (
                    f"{leader_type}领导集体禁止执行行为 '{standard_action['action_name']}'"
                )

            # Validate non-inept leaders cannot deviate from objective national interests
            if leader_type != LeaderTypeEnum.INEPT.value:
                # Check if action aligns with national interests
                action_respects_sov = standard_action.get('respect_sov', True)
                action_power_change = standard_action.get('initiator_power_change', 0)

                # For non-inept leaders, actions that significantly reduce power
                # should be justified in cost-benefit analysis
                if action_power_change < -5:
                    cost_benefit = action.get('cost_benefit_analysis', '')
                    # Check if cost-benefit mentions national interest alignment
                    has_interest_alignment = any(
                        interest in cost_benefit for interest in national_interests
                    )

                    if not has_interest_alignment:
                        return False, (
                            f"非昏庸型领导执行显著损害国力的行为必须"
                            f"在成本收益分析中明确说明与国家利益的关联"
                        )

        # Validate action stage rules
        if action_stage == "initiative":
            # In initiative stage, only certain agent types can initiate
            if power_level in [PowerLevelEnum.MIDDLE_POWER.value, PowerLevelEnum.SMALL_STATE.value]:
                # Medium and small powers can only initiate low-intensity, non-hostile actions
                for action in actions:
                    if action['action_id'] not in self.behavior_id_map:
                        continue

                    standard_action = self.behavior_id_map[action['action_id']]
                    # Check if action is high-intensity or hostile
                    if not standard_action.get('respect_sov', True):
                        # This is a non-respecting-sovereignty action
                        # Medium and small powers should avoid these in initiative stage
                        # unless it's a response
                        cost_benefit = action.get('cost_benefit_analysis', '')
                        if "response" not in cost_benefit.lower():
                            return False, (
                                f"中等强国和小国在发起阶段应避免"
                                f"不尊重主权的高烈度对抗行为"
                            )

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

        # Tier 3: Compliance validation
        is_valid, error = self.validate_compliance(
            decision, agent_info, national_interests, action_stage
        )
        if not is_valid:
            errors.append(f"[Tier 3 合规性校验] {error}")
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
