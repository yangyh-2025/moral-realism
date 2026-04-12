"""
克莱因国力方程计算模块
Klein National Power Equation Module

完全对齐克莱因综合国力方程官方计算规则、分值区间与层级判定标准。
"""

from enum import Enum
from typing import Tuple


class PowerLevelEnum(str, Enum):
    """国力层级枚举"""
    SUPERPOWER = "超级大国"
    GREAT_POWER = "大国"
    MIDDLE_POWER = "中等强国"
    SMALL_STATE = "小国"


class KleinEquation:
    """
    克莱因国力方程计算器

    公式: Pp = (C + E + M) × (S + W)

    其中:
    - C (Critical Mass): 基本实体, 0-100分, 官方满分100分
    - E (Economic Capability): 经济实力, 0-200分, 官方满分200分
    - M (Military Capability): 军事实力, 0-200分, 官方满分200分
    - S (Strategic Purpose): 战略目的, 0-2, 官方标准值0.5
    - W (Will to Pursue National Strategy): 国家战略意志, 0-2, 官方标准值0.5
    """

    # 分值区间定义
    MIN_C_SCORE = 0
    MAX_C_SCORE = 100
    MIN_E_SCORE = 0
    MAX_E_SCORE = 200
    MIN_M_SCORE = 0
    MAX_M_SCORE = 200
    MIN_S_SCORE = 0
    MAX_S_SCORE = 2
    MIN_W_SCORE = 0
    MAX_W_SCORE = 2

    # 国力层级阈值
    SUPERPOWER_THRESHOLD = 500  # 超级大国: ≥500
    GREAT_POWER_THRESHOLD = 200  # 大国: 200-500
    MIDDLE_POWER_THRESHOLD = 100  # 中等强国: 100-200
    # 小国: <100

    @staticmethod
    def validate_scores(
        c_score: float,
        e_score: float,
        m_score: float,
        s_score: float,
        w_score: float
    ) -> Tuple[bool, str]:
        """
        验证克莱因方程指标分值的合法性

        Args:
            c_score: 基本实体得分
            e_score: 经济实力得分
            m_score: 军事实力得分
            s_score: 战略目的系数
            w_score: 国家战略意志系数

        Returns:
            (is_valid: bool, error_message: str)
        """
        errors = []

        if not (KleinEquation.MIN_C_SCORE <= c_score <= KleinEquation.MAX_C_SCORE):
            errors.append(f"C得分{c_score}超出区间[{KleinEquation.MIN_C_SCORE}, {KleinEquation.MAX_C_SCORE}]")

        if not (KleinEquation.MIN_E_SCORE <= e_score <= KleinEquation.MAX_E_SCORE):
            errors.append(f"E得分{e_score}超出区间[{KleinEquation.MIN_E_SCORE}, {KleinEquation.MAX_E_SCORE}]")

        if not (KleinEquation.MIN_M_SCORE <= m_score <= KleinEquation.MAX_M_SCORE):
            errors.append(f"M得分{m_score}超出区间[{KleinEquation.MIN_M_SCORE}, {KleinEquation.MAX_M_SCORE}]")

        if not (KleinEquation.MIN_S_SCORE <= s_score <= KleinEquation.MAX_S_SCORE):
            errors.append(f"S系数{s_score}超出区间[{KleinEquation.MIN_S_SCORE}, {KleinEquation.MAX_S_SCORE}]")

        if not (KleinEquation.MIN_W_SCORE <= w_score <= KleinEquation.MAX_W_SCORE):
            errors.append(f"W系数{w_score}超出区间[{KleinEquation.MIN_W_SCORE}, {KleinEquation.MAX_W_SCORE}]")

        if errors:
            return False, "; ".join(errors)

        return True, ""

    @staticmethod
    def calculate_power(
        c_score: float,
        e_score: float,
        m_score: float,
        s_score: float,
        w_score: float
    ) -> float:
        """
        计算克莱因综合国力

        公式: Pp = (C + E + M) × (S + W)

        Args:
            c_score: 基本实体得分
            e_score: 经济实力得分
            m_score: 军事实力得分
            s_score: 战略目的系数
            w_score: 国家战略意志系数

        Returns:
            综合国力得分
        """
        is_valid, error_msg = KleinEquation.validate_scores(c_score, e_score, m_score, s_score, w_score)
        if not is_valid:
            raise ValueError(f"克莱因方程指标不合法: {error_msg}")

        material_factor = c_score + e_score + m_score
        spiritual_factor = s_score + w_score
        total_power = material_factor * spiritual_factor

        return total_power

    @staticmethod
    def determine_power_level(power: float) -> PowerLevelEnum:
        """
        根据综合国力判定实力层级

        Args:
            power: 综合国力得分

        Returns:
            实力层级枚举

        层级判定规则:
        - 超级大国: power ≥ 500
        - 大国: 200 ≤ power < 500
        - 中等强国: 100 ≤ power < 200
        - 小国: power < 100
        """
        if power >= KleinEquation.SUPERPOWER_THRESHOLD:
            return PowerLevelEnum.SUPERPOWER
        elif power >= KleinEquation.GREAT_POWER_THRESHOLD:
            return PowerLevelEnum.GREAT_POWER
        elif power >= KleinEquation.MIDDLE_POWER_THRESHOLD:
            return PowerLevelEnum.MIDDLE_POWER
        else:
            return PowerLevelEnum.SMALL_STATE

    @staticmethod
    def get_power_level_description(level: PowerLevelEnum) -> str:
        """
        获取实力层级的描述信息

        Args:
            level: 实力层级枚举

        Returns:
            层级描述字符串
        """
        descriptions = {
            PowerLevelEnum.SUPERPOWER: f"超级大国 (≥{KleinEquation.SUPERPOWER_THRESHOLD}分)",
            PowerLevelEnum.GREAT_POWER: f"大国 ({KleinEquation.GREAT_POWER_THRESHOLD}-{KleinEquation.SUPERPOWER_THRESHOLD}分)",
            PowerLevelEnum.MIDDLE_POWER: f"中等强国 ({KleinEquation.MIDDLE_POWER_THRESHOLD}-{KleinEquation.GREAT_POWER_THRESHOLD}分)",
            PowerLevelEnum.SMALL_STATE: f"小国 (<{KleinEquation.MIDDLE_POWER_THRESHOLD}分)"
        }
        return descriptions.get(level, "未知层级")


# 便捷函数
def calculate_klein_power(
    c_score: float,
    e_score: float,
    m_score: float,
    s_score: float,
    w_score: float
) -> float:
    """
    计算克莱因综合国力（便捷函数）

    Args:
        c_score: 基本实体得分
        e_score: 经济实力得分
        m_score: 军事实力得分
        s_score: 战略目的系数
        w_score: 国家战略意志系数

    Returns:
        综合国力得分
    """
    return KleinEquation.calculate_power(c_score, e_score, m_score, s_score, w_score)


def determine_power_level(power: float) -> PowerLevelEnum:
    """
    判定实力层级（便捷函数）

    Args:
        power: 综合国力得分

    Returns:
        实力层级枚举
    """
    return KleinEquation.determine_power_level(power)
