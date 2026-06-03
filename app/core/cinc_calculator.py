"""
CINC综合国力计算模块
CINC (Composite Index of National Capability) Calculator

使用CINC（Composite Index of National Capability）作为综合国力衡量标准。

CINC计算公式：
cinc = (milex/Σmilex + milper/Σmilper + irst/Σirst + pec/Σpec + tpop/Σtpop + upop/Σupop) / 6

其中Σ为仿真体系内所有国家的对应指标总和。

层级判定（基于极性-权力占比条件判断式方案）：
=======================================================================
核心思路：先判断体系极性（单极/两极/多极），再根据对应格局的权力占比阈值判定层级。

极性判定标准（基于权力占比 power_share = cinc_i / Σcinc）：
- 单极格局：1个国家权力占比 > 0.5
- 两极格局：2个国家权力占比均 > 0.25，且两者合计 > 0.5
- 多极格局：≥3个国家权力占比均 > 0.15

层级分类：
- 单极格局：该国为超级大国
- 两极格局：两国均为超级大国
- 多极格局：权力占比 > 0.15 的国家为大国
- 非极性国家：以非极性国家权力占比的中位数为界，高于中位数为中等强国，否则为小国

学术依据：阎学通《国际关系分析》、权力转移理论
=======================================================================
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

# ========================================================================
# 极性判定阈值（基于权力占比，非百分位）
# 学术依据：阎学通《国际关系分析》、权力转移理论
# ========================================================================
UNIPOLAR_THRESHOLD = 0.5    # 单极：单国权力占比 > 0.5
BIPOLAR_THRESHOLD = 0.25    # 两极：两国权力占比均 > 0.25
MULTIPOLAR_THRESHOLD = 0.10 # 多极：三国及以上权力占比均 > 0.10
# 注：阈值需适配多国体系。19国仿真中权力高度分散，前3国权力占比
# 典型为19%/15%/11%，原阈值0.15会导致第3名（11%）被排除、
# 体系突变为非极性、所有大国消失、追随机制崩溃。0.10为经验安全值。


class CINCCalculator:
    """
    CINC计算器

    CINC = (milex/Σmilex + milper/Σmilper + irst/Σirst + pec/Σpec + tpop/Σtpop + upop/Σupop) / 6

    层级判定采用极性-权力占比条件判断式方案：
    1. 计算各国权力占比（power_share = cinc / Σcinc）
    2. 判定体系极性（单极/两极/多极）
    3. 根据极性类型和权力占比阈值判定各国层级
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
    def _calculate_power_shares(agent_cincs: Dict[Any, float]) -> Dict[Any, float]:
        """
        计算各国权力占比（power_share = cinc_i / Σcinc）

        Args:
            agent_cincs: 字典 {agent_id: cinc}

        Returns:
            字典 {agent_id: power_share}
        """
        total_cinc = sum(agent_cincs.values())
        if total_cinc <= 0:
            return {aid: 0.0 for aid in agent_cincs}
        return {aid: cinc / total_cinc for aid, cinc in agent_cincs.items()}

    @staticmethod
    def _detect_polarity(power_shares: Dict[Any, float]) -> Tuple[str, set]:
        """
        检测国际体系极性

        判定标准（基于权力占比）：
        - 单极格局：1个国家权力占比 > 0.5
        - 两极格局：2个国家权力占比均 > 0.25，且两者合计 > 0.5
        - 多极格局：≥3个国家权力占比均 > 0.15

        Args:
            power_shares: 字典 {agent_id: power_share}

        Returns:
            Tuple of (polarity_type, polar_state_ids)
            polarity_type: "unipolar", "bipolar", "multipolar", "non_polar"
            polar_state_ids: 极性国家ID集合
        """
        sorted_shares = sorted(power_shares.items(), key=lambda x: x[1], reverse=True)

        # 检测单极
        if sorted_shares and sorted_shares[0][1] > UNIPOLAR_THRESHOLD:
            return "unipolar", {sorted_shares[0][0]}

        # 检测两极
        if (len(sorted_shares) >= 2
                and sorted_shares[0][1] > BIPOLAR_THRESHOLD
                and sorted_shares[1][1] > BIPOLAR_THRESHOLD
                and (sorted_shares[0][1] + sorted_shares[1][1]) > 0.5):
            return "bipolar", {sorted_shares[0][0], sorted_shares[1][0]}

        # 检测多极
        multipolar_ids = set()
        for aid, share in sorted_shares:
            if share > MULTIPOLAR_THRESHOLD:
                multipolar_ids.add(aid)
        if len(multipolar_ids) >= 3:
            return "multipolar", multipolar_ids

        # 无法判定为明确极性
        return "non_polar", set()

    @staticmethod
    def determine_power_level(
        cinc: float,
        all_cincs: List[float]
    ) -> PowerLevelEnum:
        """
        基于极性-权力占比方案判定国力层级

        流程：
        1. 从all_cincs重建agent_cincs字典（此方法为兼容旧接口保留）
        2. 计算权力占比
        3. 检测极性
        4. 根据极性和权力占比判定层级

        Args:
            cinc: 待判定国家的CINC值
            all_cincs: 仿真体系内所有国家的CINC值列表（含自己）

        Returns:
            PowerLevelEnum
        """
        if not all_cincs:
            return PowerLevelEnum.SMALL_STATE

        # 重建agent_cincs字典（用索引作为key）
        agent_cincs = {i: c for i, c in enumerate(all_cincs)}
        power_shares = CINCCalculator._calculate_power_shares(agent_cincs)
        polarity, polar_ids = CINCCalculator._detect_polarity(power_shares)

        # 找到当前cinc对应的agent_id
        # 由于all_cincs是列表，需要找到cinc在其中的位置
        target_id = None
        for aid, c in agent_cincs.items():
            if abs(c - cinc) < 1e-9:
                target_id = aid
                break
        if target_id is None:
            target_id = 0  # fallback

        target_share = power_shares.get(target_id, 0.0)

        # 根据极性判定层级
        if polarity == "unipolar" and target_id in polar_ids:
            return PowerLevelEnum.SUPERPOWER
        elif polarity == "bipolar" and target_id in polar_ids:
            return PowerLevelEnum.SUPERPOWER
        elif polarity == "multipolar" and target_id in polar_ids:
            return PowerLevelEnum.GREAT_POWER
        else:
            # 非极性国家：以中位数为界
            non_polar_shares = [
                share for aid, share in power_shares.items()
                if aid not in polar_ids
            ]
            if not non_polar_shares:
                return PowerLevelEnum.SMALL_STATE
            median_share = sorted(non_polar_shares)[len(non_polar_shares) // 2]
            if target_share >= median_share:
                return PowerLevelEnum.MIDDLE_POWER
            else:
                return PowerLevelEnum.SMALL_STATE

    @staticmethod
    def determine_all_power_levels(
        agent_cincs: Dict[Any, float]
    ) -> Dict[Any, PowerLevelEnum]:
        """
        批量判定仿真体系内所有国家的层级

        使用极性-权力占比条件判断式方案：
        1. 计算各国权力占比
        2. 检测体系极性（单极/两极/多极）
        3. 根据极性类型和权力占比阈值判定各国层级

        Args:
            agent_cincs: 字典 {agent_id: cinc}

        Returns:
            字典 {agent_id: PowerLevelEnum}
        """
        if not agent_cincs:
            return {}

        # Step 1: 计算权力占比
        power_shares = CINCCalculator._calculate_power_shares(agent_cincs)

        # Step 2: 检测极性
        polarity, polar_ids = CINCCalculator._detect_polarity(power_shares)

        logger.info(
            f"极性检测: {polarity}, "
            f"极性国家: {[f'ID{k}(share={power_shares[k]:.4f})' for k in polar_ids]}"
        )

        # Step 3: 根据极性判定层级
        result = {}

        if polarity in ("unipolar", "bipolar"):
            # 单极/两极：极性国家为超级大国，其余以中位数为界
            non_polar_shares = sorted([
                share for aid, share in power_shares.items()
                if aid not in polar_ids
            ])
            if non_polar_shares:
                median_share = non_polar_shares[len(non_polar_shares) // 2]
            else:
                median_share = 0.0

            for aid in agent_cincs:
                if aid in polar_ids:
                    result[aid] = PowerLevelEnum.SUPERPOWER
                elif power_shares[aid] >= median_share:
                    result[aid] = PowerLevelEnum.MIDDLE_POWER
                else:
                    result[aid] = PowerLevelEnum.SMALL_STATE

        elif polarity == "multipolar":
            # 多极：极性国家为大国，其余以中位数为界
            non_polar_shares = sorted([
                share for aid, share in power_shares.items()
                if aid not in polar_ids
            ])

            if non_polar_shares:
                median_share = non_polar_shares[len(non_polar_shares) // 2]
            else:
                median_share = 0.0

            for aid in agent_cincs:
                if aid in polar_ids:
                    result[aid] = PowerLevelEnum.GREAT_POWER
                elif power_shares[aid] >= median_share:
                    result[aid] = PowerLevelEnum.MIDDLE_POWER
                else:
                    result[aid] = PowerLevelEnum.SMALL_STATE

        else:
            # 无明确极性：以中位数为界分为中等强国和小国
            # 但必须保证至少有大国存在，否则追随机制会崩溃
            sorted_shares = sorted(power_shares.items(), key=lambda x: x[1], reverse=True)
            n = len(sorted_shares)
            if n == 0:
                return {}
            median_idx = n // 2
            for rank, (aid, share) in enumerate(sorted_shares):
                if rank <= median_idx:
                    result[aid] = PowerLevelEnum.MIDDLE_POWER
                else:
                    result[aid] = PowerLevelEnum.SMALL_STATE

            # 非极性回退: 若无大国/超级大国，将Top2提升为大国
            has_big = any(
                v in (PowerLevelEnum.GREAT_POWER, PowerLevelEnum.SUPERPOWER)
                for v in result.values()
            )
            if not has_big and n >= 2:
                for rank, (aid, share) in enumerate(sorted_shares[:2]):
                    result[aid] = PowerLevelEnum.GREAT_POWER
                logger.warning(
                    "非极性格局且无大国: 已将Top2提升为大国以保证追随机制可用"
                )

        # 记录分类结果
        level_counts = {}
        for level in PowerLevelEnum:
            count = sum(1 for v in result.values() if v == level)
            if count > 0:
                level_counts[level.value] = count
        logger.info(f"层级分类结果: {level_counts}")

        return result

    @staticmethod
    def get_power_level_description(level: PowerLevelEnum) -> str:
        """获取实力层级的描述信息（极性-权力占比方案）"""
        descriptions = {
            PowerLevelEnum.SUPERPOWER: (
                "超级大国（极性国家：单极权力占比>0.5，或两极权力占比>0.25）"
            ),
            PowerLevelEnum.GREAT_POWER: (
                "大国（多极格局极性国家：权力占比>0.15）"
            ),
            PowerLevelEnum.MIDDLE_POWER: (
                "中等强国（非极性国家中权力占比≥中位数）"
            ),
            PowerLevelEnum.SMALL_STATE: (
                "小国（非极性国家中权力占比<中位数）"
            ),
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
