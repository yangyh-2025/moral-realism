"""
实力计算系统 - 对应技术方案3.3.1节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import numpy as np


class PowerTier(str, Enum):
    """
    实力层级枚举 - 采用正态分布方法动态划分

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    SUPERPOWER = "superpower"    # 超级大国
    GREAT_POWER = "great_power"    # 大国
    MIDDLE_POWER = "middle_power"  # 中等强国
    SMALL_POWER = "small_power"    # 小国


@dataclass
class PowerMetrics:
    """
    实力指标 - 克莱因方程五要素模型

    克莱因方程公式：P = (C + E + M) × (S + W)

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    # 物质要素子指标
    critical_mass: float          # C - 基本实体 0-100分
    economic_capability: float    # E - 经济实力 0-200分
    military_capability: float    # M - 军事实力 0-200分

    # 精神要素子指标
    strategic_purpose: float      # S - 战略目标 0.5-1分
    national_will: float          # W - 国家意志 0.5-1分

    def calculate_material_power(self) -> float:
        """计算物质要素实力 (C+E+M)"""
        return self.critical_mass + self.economic_capability + self.military_capability

    def calculate_spiritual_power(self) -> float:
        """计算精神要素实力 (S+W)"""
        return self.strategic_purpose + self.national_will

    def calculate_comprehensive_power(self) -> float:
        """计算综合实力指数 - 克莱因方程"""
        # P = (C + E + M) × (S + W)
        material_power = self.calculate_material_power()
        spiritual_power = self.calculate_spiritual_power()
        return material_power * spiritual_power


class PowerTierClassifier:
    """
    实力层级分类器 - 基于正态分布方法

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    @staticmethod
    def classify_all(power_metrics_list: List[PowerMetrics]) -> List[PowerTier]:
        """
        对所有智能体的实力进行批量分类

        步骤：
        1. 计算所有智能体的克莱因P得分：P = (C + E + M) × (S + W)
        2. 计算样本均值 μ 和标准差 σ
        3. 对每个智能体标准化为 z 分数：z = (P - μ) / σ
        4. 根据z分数分类

        Args:
            power_metrics_list: 所有智能体的PowerMetrics列表

        Returns:
            对应的实力层级列表
        """
        # 步骤1: 计算所有P得分
        power_scores = [pm.calculate_comprehensive_power() for pm in power_metrics_list]

        if len(power_scores) == 0:
            return []

        # 步骤2: 计算均值和标准差
        mu = np.mean(power_scores)
        sigma = np.std(power_scores)

        # 避免除以零（如果所有智能体实力相同）
        if sigma < 1e-10:
            sigma = 1.0

        # 步骤3-4: 根据z分数分类
        tiers = []
        for score in power_scores:
            z = (score - mu) / sigma
            tier = PowerTierClassifier._classify_by_z_score(z)
            tiers.append(tier)

        return tiers

    @staticmethod
    def _classify_by_z_score(z: float) -> PowerTier:
        """
        根据z分数分类（基于标准正态分布）

        | 层级 | z分数范围 | 理论比例 |
        |------|-----------|----------|
        | 超级大国 | z > 2.0 | ≈ 2.28% |
        | 大国 | 1.5 < z ≤ 2.0 | ≈ 4.41% |
        | 中等强国 | 0.5 < z ≤ 1.5 | ≈ 24.17% |
        | 小国 | z ≤ 0.5 | ≈ 69.15% |

        Args:
            z: 标准化后的z分数

        Returns:
            实力层级
        """
        if z > 2.0:
            return PowerTier.SUPERPOWER
        elif z > 1.5:
            return PowerTier.GREAT_POWER
        elif z > 0.5:
            return PowerTier.MIDDLE_POWER
        else:
            return PowerTier.SMALL_POWER
