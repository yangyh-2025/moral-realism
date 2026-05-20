"""
CINC综合国力计算模块
CINC (Composite Index of National Capability) Calculator

使用CINC（Composite Index of National Capability）作为综合国力衡量标准。

CINC计算公式：
cinc = (milex/Σmilex + milper/Σmilper + irst/Σirst + pec/Σpec + tpop/Σtpop + upop/Σupop) / 6

其中Σ为仿真体系内所有国家的对应指标总和。

层级判定（基于CINC在仿真体系内的相对排名）：
- 超级大国: 前5%
- 大国: 5%-15%
- 中等强国: 15%-35%
- 小国: 后65%
"""

from enum import Enum
from typing import List, Dict, Tuple, Any, Optional
from loguru import logger


class PowerLevelEnum(str, Enum):
    """国力层级枚举"""
    SUPERPOWER = "超级大国"
    GREAT_POWER = "大国"
    MIDDLE_POWER = "中等强国"
    SMALL_STATE = "小国"


# CINC使用的6个底层指标
CINC_INDICATORS = ["milex", "milper", "irst", "pec", "tpop", "upop"]


# 层级判定阈值（基于排名分位数）
SUPERPOWER_PERCENTILE = 0.05   # 前5%
GREAT_POWER_PERCENTILE = 0.15  # 前15%
MIDDLE_POWER_PERCENTILE = 0.35 # 前35%
# 后65%为小国


class CINCCalculator:
    """
    CINC计算器

    CINC = (milex/Σmilex + milper/Σmilper + irst/Σirst + pec/Σpec + tpop/Σtpop + upop/Σupop) / 6
    """

    @staticmethod
    def calculate_cinc(
        agent_indicators: Dict[str, float],
        all_agents_indicators: List[Dict[str, float]]
    ) -> float:
        """
        计算单个国家的CINC指数

        Args:
            agent_indicators: 当前国家的6项指标 {"milex": float, "milper": float, ...}
            all_agents_indicators: 仿真体系内所有国家的指标列表

        Returns:
            CINC指数（0-1之间的比例值）
        """
        if not all_agents_indicators:
            return 0.0

        ratios = []
        for ind in CINC_INDICATORS:
            agent_val = float(agent_indicators.get(ind, 0))
            total = sum(float(a.get(ind, 0)) for a in all_agents_indicators)
            if total > 0:
                ratios.append(agent_val / total)
            else:
                # 如果该项指标全体系总和为0，该指标贡献为0
                ratios.append(0.0)

        cinc = sum(ratios) / len(CINC_INDICATORS)
        return round(cinc, 6)

    @staticmethod
    def calculate_all_cincs(
        all_agents_indicators: List[Dict[str, Any]]
    ) -> Dict[Any, float]:
        """
        批量计算仿真体系内所有国家的CINC

        Args:
            all_agents_indicators: 所有国家的指标列表，每项必须包含
                "agent_id"或"id"字段（用作返回字典的key）和6项CINC指标

        Returns:
            字典 {agent_id: cinc_value}
        """
        if not all_agents_indicators:
            return {}

        # 计算各指标的全体系总和
        totals = {}
        for ind in CINC_INDICATORS:
            totals[ind] = sum(float(a.get(ind, 0)) for a in all_agents_indicators)

        result = {}
        for agent in all_agents_indicators:
            agent_id = agent.get("agent_id") or agent.get("id")
            if agent_id is None:
                continue

            ratios = []
            for ind in CINC_INDICATORS:
                if totals[ind] > 0:
                    ratios.append(float(agent.get(ind, 0)) / totals[ind])
                else:
                    ratios.append(0.0)

            cinc = sum(ratios) / len(CINC_INDICATORS)
            result[agent_id] = round(cinc, 6)

        return result

    @staticmethod
    def determine_power_level(
        cinc: float,
        all_cincs: List[float]
    ) -> PowerLevelEnum:
        """
        基于CINC在仿真体系内的相对排名判定国力层级

        排名规则：
        - 前5%（含）: 超级大国
        - 前5%-15%（含）: 大国
        - 前15%-35%（含）: 中等强国
        - 后65%: 小国

        Args:
            cinc: 待判定国家的CINC值
            all_cincs: 仿真体系内所有国家的CINC值列表（含自己）

        Returns:
            PowerLevelEnum
        """
        if not all_cincs:
            return PowerLevelEnum.SMALL_STATE

        # 降序排列
        sorted_cincs = sorted(all_cincs, reverse=True)
        n = len(sorted_cincs)

        # 找到当前cinc的排名位置（用<=以便相同值归到更高层级）
        rank = 0
        for i, c in enumerate(sorted_cincs):
            if cinc >= c - 1e-9:
                rank = i
                break
            rank = i + 1

        percentile = rank / n if n > 0 else 1.0

        if percentile < SUPERPOWER_PERCENTILE:
            return PowerLevelEnum.SUPERPOWER
        elif percentile < GREAT_POWER_PERCENTILE:
            return PowerLevelEnum.GREAT_POWER
        elif percentile < MIDDLE_POWER_PERCENTILE:
            return PowerLevelEnum.MIDDLE_POWER
        else:
            return PowerLevelEnum.SMALL_STATE

    @staticmethod
    def determine_all_power_levels(
        agent_cincs: Dict[Any, float]
    ) -> Dict[Any, PowerLevelEnum]:
        """
        批量判定仿真体系内所有国家的层级

        Args:
            agent_cincs: 字典 {agent_id: cinc}

        Returns:
            字典 {agent_id: PowerLevelEnum}
        """
        if not agent_cincs:
            return {}

        # 按CINC降序排列
        sorted_items = sorted(agent_cincs.items(), key=lambda x: x[1], reverse=True)
        n = len(sorted_items)
        result = {}

        for rank, (agent_id, cinc) in enumerate(sorted_items):
            percentile = rank / n
            if percentile < SUPERPOWER_PERCENTILE:
                result[agent_id] = PowerLevelEnum.SUPERPOWER
            elif percentile < GREAT_POWER_PERCENTILE:
                result[agent_id] = PowerLevelEnum.GREAT_POWER
            elif percentile < MIDDLE_POWER_PERCENTILE:
                result[agent_id] = PowerLevelEnum.MIDDLE_POWER
            else:
                result[agent_id] = PowerLevelEnum.SMALL_STATE

        return result

    @staticmethod
    def get_power_level_description(level: PowerLevelEnum) -> str:
        """获取实力层级的描述信息"""
        descriptions = {
            PowerLevelEnum.SUPERPOWER: "超级大国（CINC排名前5%）",
            PowerLevelEnum.GREAT_POWER: "大国（CINC排名5%-15%）",
            PowerLevelEnum.MIDDLE_POWER: "中等强国（CINC排名15%-35%）",
            PowerLevelEnum.SMALL_STATE: "小国（CINC排名后65%）",
        }
        return descriptions.get(level, "未知层级")


# 便捷函数
def calculate_cinc(
    agent_indicators: Dict[str, float],
    all_agents_indicators: List[Dict[str, float]]
) -> float:
    """计算CINC指数（便捷函数）"""
    return CINCCalculator.calculate_cinc(agent_indicators, all_agents_indicators)


def determine_power_level(cinc: float, all_cincs: List[float]) -> PowerLevelEnum:
    """判定实力层级（便捷函数）"""
    return CINCCalculator.determine_power_level(cinc, all_cincs)


def calculate_all_cincs(all_agents_indicators: List[Dict[str, Any]]) -> Dict[Any, float]:
    """批量计算CINC（便捷函数）"""
    return CINCCalculator.calculate_all_cincs(all_agents_indicators)


def determine_all_power_levels(agent_cincs: Dict[Any, float]) -> Dict[Any, PowerLevelEnum]:
    """批量判定层级（便捷函数）"""
    return CINCCalculator.determine_all_power_levels(agent_cincs)
