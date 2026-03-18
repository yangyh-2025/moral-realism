"""
规则校验引擎 - 验证所有行为符合道义现实主义规则

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from config.leader_types import LeaderType
from config.settings import Constants

@dataclass
class ValidationResult:
    """
    校验结果

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    is_valid: bool
    error_message: str
    corrected_function: Optional[str] = None
    corrected_args: Optional[Dict] = None

class RuleValidator:
    """
    规则校验引擎

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    # 王道型绝对禁止的函数
    WANGDAO_FORBIDDEN = {
        'use_military_force',
        'unilateral_sanctions',
        'unilateral_treaty_withdrawal',
        'double_standard_action',
        'sacrifice_ally_interest'
    }

    # 霸权型绝对禁止的函数
    BAQUAN_FORBIDDEN = {
        'full_equal_negotiation',
        'unconditionally_follow_all_norms',
        'sacrifice_core_interest_for_stability'
    }

    # 强权型绝对禁止的函数
    QIANGQUAN_FORBIDDEN = {
        'international_mediation',
        'provide_public_goods',
        'equal_multilateral_cooperation',
        'follow_unfavorable_norms'
    }

    # 昏庸型无禁止项

    @staticmethod
    def validate_decision(
        leader_type: LeaderType,
        function_name: str,
        function_args: Dict,
        objective_interest: str,
        current_power: float
    ) -> ValidationResult:
        """
        验证决策是否符合规则

        Args:
            leader_type: 领导类型
            function_name: 函数名
            function_args: 函数参数
            objective_interest: 客观战略利益
            current_power: 当前实力

        Returns:
            校验结果
        """
        # 1. 校验函数调用权限
        func_validation = RuleValidator._validate_function_permission(
            leader_type, function_name
        )
        if not func_validation.is_valid:
            return func_validation

        # 2. 校验实力变动约束
        if 'power_change' in function_args:
            power_change = function_args['power_change']
            # 添加类型检查
            if not isinstance(power_change, (int, float)):
                return ValidationResult(
                    False,
                    f"power_change必须是数字类型，当前类型: {type(power_change).__name__}"
                )
            power_change_validation = RuleValidator._validate_power_change(
                current_power,
                power_change
            )
            if not power_change_validation.is_valid:
                return power_change_validation

        # 3. 校验战略匹配度（非昏庸型）
        if leader_type != LeaderType.HUNYONG:
            match_validation = RuleValidator._validate_strategic_match(
                function_name,
                function_args,
                objective_interest,
                leader_type
            )
            if not match_validation.is_valid:
                return match_validation

        return ValidationResult(True, "")

    @staticmethod
    def _validate_function_permission(
        leader_type: LeaderType,
        function_name: str
    ) -> ValidationResult:
        """校验函数调用权限"""
        forbidden_set = None

        if leader_type == LeaderType.WANGDAO:
            forbidden_set = RuleValidator.WANGDAO_FORBIDDEN
        elif leader_type == LeaderType.BAQUAN:
            forbidden_set = RuleValidator.BAQUAN_FORBIDDEN
        elif leader_type == LeaderType.QIANGQUAN:
            forbidden_set = RuleValidator.QIANGQUAN_FORBIDDEN
        elif leader_type == LeaderType.HUNYONG:
            # 昏庸型无禁止项
            return ValidationResult(True, "")

        if forbidden_set and function_name in forbidden_set:
            return ValidationResult(
                False,
                f"{leader_type.value}型领导禁止使用函数: {function_name}"
            )

        return ValidationResult(True, "")

    @staticmethod
    def _validate_power_change(
        current_power: float,
        power_change: float
    ) -> ValidationResult:
        """校验实力变动约束（5年不超过5%）"""
        max_allowed_change = Constants.MAX_ALLOWED_POWER_CHANGE

        if abs(power_change) > max_allowed_change:
            return ValidationResult(
                False,
                f"实力变动超出约束: {power_change}% > {max_allowed_change}%"
            )

        return ValidationResult(True, "")

    @staticmethod
    def _validate_strategic_match(
        function_name: str,
        function_args: Dict,
        objective_interest: str,
        leader_type: LeaderType
    ) -> ValidationResult:
        """校验战略匹配度"""
        # 简化实现：根据函数名和客观利益的匹配度计算
        match_score = RuleValidator._calculate_match_score(
            function_name, objective_interest
        )

        if match_score < Constants.MIN_STRATEGIC_MATCH_SCORE:
            return ValidationResult(
                False,
                f"决策与客观利益匹配度过低: {match_score:.2f}"
            )

        return ValidationResult(True, "")

    @staticmethod
    def _calculate_match_score(
        function_name: str,
        objective_interest: str
    ) -> float:
        """计算决策与客观利益的匹配度（简化实现）"""
        # 简化实现，返回默认匹配度
        return 0.5
