"""
能力与权力模型模块

本模块定义了道义现实主义ABM系统中代理（Agent）的能力层级、硬权力、软权力
以及综合能力指标。

核心概念：
- 能力层级（CapabilityTier）：根据综合能力将国家划分为5个等级
- 硬权力（HardPower）：军事、经济、技术等物质性能力
- 软权力（SoftPower）：话语权、外交支持、文化影响力等非物质性能力
- 综合能力（Capability）：硬权力与软权力的加权组合

使用场景：
1. 初始化国家代理时设置其能力等级
2. 在决策过程中考虑能力差距对互动的影响
3. 跟踪能力变化，检测权力转移
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class CapabilityTier(Enum):
    """
    能力层级枚举

    根据国家的综合能力水平将其划分为5个层级：
    - T0_SUPERPOWER: 超级大国（如美国）
    - T1_GREAT_POWER: 大国（如中国、俄罗斯）
    - T2_REGIONAL: 区域性大国（如德国、印度）
    - T3_MEDIUM: 中等国家（如韩国、瑞典）
    - T4_SMALL: 小国（如新加坡、冰岛）

    层级划分基于综合能力指数（硬权力70% + 软权力30%）：
    - T0: 综合指数 >= 80
    - T1: 65 <= 综合指数 < 80
    - T2: 45 <= 综合指数 < 65
    - T3: 25 <= 综合指数 < 45
    - T4: 综合指数 < 25
    """

    T0_SUPERPOWER = "t0_superpower"  # 超级大国
    T1_GREAT_POWER = "t1_great_power"  # 大国
    T2_REGIONAL = "t2_regional"  # 区域性大国
    T3_MEDIUM = "t3_medium"  # 中等国家
    T4_SMALL = "t4_small"  # 小国


@dataclass
class HardPower:
    """
    硬权力类

    表示一个国家的物质性能力，包括军事、经济、技术等可量化的硬实力。

    属性说明：
    1. 军事能力维度：
       - military_capability: 综合军事实力
       - nuclear_capability: 核能力存在度和强度
       - conventional_forces: 常规军事力量
       - force_projection: 全球力量投送能力

    2. 经济能力维度：
       - gdp_share: 全球GDP占比（百分比）
       - economic_growth: 年GDP增长率
       - trade_volume: 贸易量（相对同级）
       - financial_influence: 金融系统控制力

    3. 技术能力维度：
       - technology_level: 综合技术水平
       - military_technology: 军事技术水平
       - innovation_capacity: 研发创新能力

    4. 资源获取能力：
       - energy_access: 能源资源获取能力
       - strategic_materials: 战略材料获取能力

    所有分数值属性的范围为0-100，用于能力计算和比较。
    """

    # 军事能力维度 (0-100分制)
    military_capability: float = 50.0  # 综合军事实力
    nuclear_capability: float = 0.0  # 核能力存在度/强度
    conventional_forces: float = 50.0  # 常规军事力量
    force_projection: float = 50.0  # 全球力量投送能力

    # 经济能力维度 (0-100分制，gdp_share除外)
    gdp_share: float = 2.0  # 全球GDP占比（百分比）
    economic_growth: float = 3.0  # 年GDP增长率
    trade_volume: float = 50.0  # 相对同级的贸易量
    financial_influence: float = 50.0  # 金融系统控制力

    # 技术能力维度 (0-100分制)
    technology_level: float = 50.0  # 综合技术水平技术水平
    military_technology: float = 50.0  # 军事专用技术
    innovation_capacity: float = 50.0  # 研发和创新能力

    # 资源获取能力 (0-100分制)
    energy_access: float = 50.0  # 能源资源获取
    strategic_materials: float = 50.0  # 战略材料获取

    def __post_init__(self) -> None:
        """初始化后验证硬权力值是否在有效范围内"""
        self.validate()

    def validate(self) -> bool:
        """
        验证硬权力值是否在可接受范围内

        验证规则：
        - 所有评分属性（0-100）：必须在0到100之间
        - gdp_share：必须在0到100之间（表示全球占比百分比）

        Returns:
            bool: 验证通过返回True

        Raises:
            ValueError: 当任何属性超出有效范围时抛出异常
        """
        attrs = [
            "military_capability",
            "nuclear_capability",
            "conventional_forces",
            "force_projection",
            "economic_growth",
            "trade_volume",
            "financial_influence",
            "technology_level",
            "military_technology",
            "innovation_capacity",
            "energy_access",
            "strategic_materials",
        ]
        for attr in attrs:
            value = getattr(self, attr)
            if not 0 <= value <= 100:
                raise ValueError(f"{attr} must be between 0 and 100, got {value}")
        if not 0 <= self.gdp_share <= 100:
            raise ValueError(f"gdp_share must be between 0 and 100, got {self.gdp_share}")
        return True

    def get_hard_power_index(self) -> float:
        """
        计算硬权力指数

        硬权力指数是各维度能力的加权组合：

        计算公式：
        1. 军事得分 = 军事实力×0.3 + 核能力×0.2 + 常规力量×0.3 + 力量投送×0.2
        2. 经济得分 = GDP占比×0.3 + 贸易量×0.3 + 金融影响力×0.4
           （注：贸易量需归一化到0-100范围）
        3. 技术得分 = 技术水平×0.3 + 军事技术×0.3 + 创新能力×0.4
        4. 资源得分 = (能源获取 + 战略材料) / 2

        最终硬权力指数 = 军事得分×0.4 + 经济得分×0.3 + 技术得分×0.2 + 资源得分×0.1

        Returns:
            float: 硬权力指数（0-100分制）
        """
        # 军事得分计算
        military_score = (
            self.military_capability * 0.3
            + self.nuclear_capability * 0.2
            + self.conventional_forces * 0.3
            + self.force_projection * 0.2
        )
        # 经济得分计算
        economic_score = (
            self.gdp_share * 0.3
            + self.trade_volume / 33.33 * 0.3  # 归一化到0-1
            + self.financial_influence * 0.4
        )
        # 技术得分计算
        tech_score = (
            self.technology_level * 0.3
            + self.military_technology * 0.3
            + self.innovation_capacity * 0.4
        )
        # 资源得分计算
        resource_score = (self.energy_access + self.strategic_materials) / 2

        # 最终加权指数
        hard_power_index = (
            military_score * 0.4
            + economic_score * 0.3
            + tech_score * 0.2
            + resource_score * 0.1
        )
        return min(100.0, max(0.0, hard_power_index))


@dataclass
class SoftPower:
    """
    软权力类

    表示一个国家的非物质性能力，包括话语权、外交支持、文化影响力等软实力。

    属性说明：
    1. 话语权维度：
       - discourse_power: 设置国际议题的能力
       - narrative_control: 控制国际叙事的能力
       - media_influence: 媒体和信息影响力

    2. 同盟关系维度：
       - allies_count: 正式盟友数量
       - ally_strength: 盟友的综合实力
       - network_position: 在同盟网络中的中心地位

    3. 国际支持维度：
       - diplomatic_support: 一般外交支持度
       - moral_legitimacy: 在国际社会的道德地位
       - cultural_influence: 文化的传播力和吸引力

    4. 制度性权力维度：
       - un_influence: 在联合国及国际组织中的影响力
       - institutional_leadership: 在关键机构中的领导地位

    所有分数值属性的范围为0-100，用于能力计算和比较。
    """

    # 话语权维度 (0-100分制)
    discourse_power: float = 50.0  # 设置国际议题的能力
    narrative_control: float = 50.0  # 控制国际叙事的能力
    media_influence: float = 50.0  # 媒体和信息影响力

    # 同盟关系维度
    allies_count: int = 0.0  # 正式盟友数量
    ally_strength: float = 50.0  # 盟友的综合实力
    network_position: float = 50.0  # 在同盟网络中的中心地位

    # 国际支持维度 (0-100分制)
    diplomatic_support: float = 50.0  # 一般外交支持度
    moral_legitimacy: float = 50.0  # 在国际社会的道德地位
    cultural_influence: float = 50.0  # 文化的传播力和吸引力

    # 制度性权力维度 (0-100分制)
    un_influence: float = 50.0  # 在联合国及国际组织中的影响力
    institutional_leadership: float = 50.0  # 在关键机构中的领导地位

    def __post_init__(self) -> None:
        """初始化后验证软权力值是否在有效范围内"""
        self.validate()

    def validate(self) -> bool:
        """
        验证软权力值是否在可接受范围内

        验证规则：
        - 所有评分属性（0-100）：必须在0到100之间
        - allies_count：必须为非负整数

        Returns:
            bool: 验证通过返回True

        Raises:
            ValueError: 当任何属性超出有效范围时抛出异常
        """
        attrs = [
            "discourse_power",
            "narrative_control",
            "media_influence",
            "ally_strength",
            "network_position",
            "diplomatic_support",
            "moral_legitimacy",
            "cultural_influence",
            "un_influence",
            "institutional_leadership",
        ]
        for attr in attrs:
            value = getattr(self, attr)
            if not 0 <= value <= 100:
                raise ValueError(f"{attr} must be between 0 and 100, got {value}")
        if self.allies_count < 0:
            raise ValueError("allies_count must be non-negative")
        return True

    def get_soft_power_index(self) -> float:
        """
        计算软权力指数

        软权力指数是各维度能力的加权组合：

        计算公式：
        1. 话语得分 = 话语权×0.4 + 叙事控制×0.3 + 媒体影响×0.3
        2. 同盟得分 = 盟友数(归一化)×0.3 + 盟友实力×0.4 + 网络地位×0.3
           （注：盟友数按max(30)归一化到0-100）
        3. 支持得分 = 外交支持×0.35 + 道德地位×0.35 + 文化影响×0.3
        4. 制度得分 = 联合国影响×0.5 + 机构领导×0.5

        最终软权力指数 = 话语×0.3 + 同盟×0.3 + 支持×0.25 + 制度×0.15

        Returns:
            float: 软权力指数（0-100分制）
        """
        # 话语得分计算
        discourse_score = (
            self.discourse_power * 0.4
            + self.narrative_control * 0.3
            + self.media_influence * 0.3
        )

        # 同盟得分计算
        # 将盟友数归一化（假设合理的最大值约为30）
        allies_normalized = min(1.0, self.allies_count / 30.0) * 100
        alliance_score = (
            allies_normalized * 0.3
            + self.ally_strength * 0.4
            + self.network_position * 0.3
        )

        # 支持得分计算
        support_score = (
            self.diplomatic_support * 0.35
            + self.moral_legitimacy * 0.35
            + self.cultural_influence * 0.3
        )

        # 制度得分计算
        institutional_score = (
            self.un_influence * 0.5
            + self.institutional_leadership * 0.5
        )

        # 最终加权指数
        soft_power_index = (
            discourse_score * 0.3
            + alliance_score * 0.3
            + support_score * 0.25
            + institutional_score * 0.15
        )
        return min(100.0, max(0.0, soft_power_index))


@dataclass
class Capability:
    """
    综合能力类

    表示一个国家的综合国力，由硬权力和软权力组成。

    属性说明：
    - agent_id: 代理唯一标识符
    - hard_power: 硬实力对象（军事、经济、技术等）
    - soft_power: 软实力对象（话语权、外交、文化等）
    - tier: 能力层级（自动根据综合指数判定）
    - history: 能力历史记录，用于跟踪能力变化

    能力判定规则：
    综合指数 = 硬权力指数×0.7 + 软权力指数×0.3
    - T0_SUPERPOWER: 综合指数 >= 80
    - T1_GREAT_POWER: 65 <= 综合指数 < 80
    - T2_REGIONAL: 45 <= 综合指数 < 65
    - T3_MEDIUM: 25 <= 综合指数 < 45
    - T4_SMALL: 综合指数 < 25
    """

    agent_id: str  # 代理唯一标识符
    hard_power: HardPower = field(default_factory=HardPower)  # 硬实力
    soft_power: SoftPower = field(default_factory=SoftPower)  # 软实力
    tier: Optional[CapabilityTier] = None  # 能力层级（自动判定）

    # 历史追踪
    history: List[Dict] = field(default_factory=list)  # 能力变化历史

    def __post_init__(self) -> None:
        """初始化后根据能力值确定能力层级"""
        if self.tier is None:
            self.tier = self._determine_tier()

    def validate(self) -> bool:
        """
        验证能力组件的有效性

        Returns:
            bool: 验证通过返回True
        """
        self.hard_power.validate()
        self.soft_power.validate()
        return True

    def _determine_tier(self) -> CapabilityTier:
        """
        根据能力指数确定能力层级

        判定规则：
        综合指数 = 硬权力指数×0.7 + 软权力指数×0.3

        - T0_SUPERPOWER: 综合指数 >= 80
        - T1_GREAT_POWER: 65 <= 综合指数 < 80
        - T2_REGIONAL: 45 <= 综合指数 < 65
        - T3_MEDIUM: 25 <= 综合指数 < 45
        - T4_SMALL: 综合指数 < 25

        Returns:
            CapabilityTier: 确定的能力层级
        """
        hard_index = self.hard_power.get_hard_power_index()
        soft_index = self.soft_power.get_soft_power_index()
        combined_index = (hard_index * 0.7 + soft_index * 0.3)

        if combined_index >= 80:
            return CapabilityTier.T0_SUPERPOWER
        elif combined_index >= 65:
            return CapabilityTier.T1_GREAT_POWER
        elif combined_index >= 45:
            return CapabilityTier.T2_REGIONAL
        elif combined_index >= 25:
            return CapabilityTier.T3_MEDIUM
        else:
            return CapabilityTier.T4_SMALL

    def get_capability_index(self) -> float:
        """
        计算综合能力指数

        综合能力指数是硬权力和软权力的加权组合。
        硬权力权重略高（0.6），软权力权重为0.4。

        Returns:
            float: 综合能力指数（0-100分制）
        """
        hard_index = self.hard_power.get_hard_power_index()
        soft_index = self.soft_power.get_soft_power_index()

        # 硬权力在综合能力中的权重略高
        combined_index = hard_index * 0.6 + soft_index * 0.4
        return combined_index

    def get_tier(self) -> CapabilityTier:
        """
        获取能力层级

        Returns:
            CapabilityTier: 当前能力层级
        """
        return self.tier or self._determine_tier()

    def record(self, step: int, context: Optional[Dict] = None) -> None:
        """
        记录当前能力状态到历史记录

        Args:
            step: 模拟步数
            context: 附加上下文信息
        """
        state = {
            "step": step,
            "hard_power_index": self.hard_power.get_hard_power_index(),
            "soft_power_index": self.soft_power.get_soft_power_index(),
            "capability_index": self.get_capability_index(),
            "tier": self.get_tier().value,
            "context": context or {},
        }
        self.history.append(state)

    def get_history(self) -> List[Dict]:
        """
        获取能力历史记录

        Returns:
            List[Dict]: 历史能力状态列表
        """
        return self.history


# 各能力层级对应的客观战略利益
# 根据道义现实主义理论，不同能力的国家有不同的战略利益
OBJECTIVE_STRATEGIC_INTERESTS: Dict[CapabilityTier, List[str]] = {
    CapabilityTier.T0_SUPERPOWER: [
        "global hegemony maintenance",  # 维护全球霸权
        "global order and rule-setting",  # 全球秩序和规则制定
        "global military presence",  # 全球军事存在
        "global alliance leadership",  # 全球同盟领导
        "control of strategic chokepoints",  # 控制战略要地
        "technological supremacy",  # 技术优势
        "containment of peer competitors",  # 遏制同等竞争者
    ],
    CapabilityTier.T1_GREAT_POWER: [
        "great power status recognition",  # 大国地位承认
        "regional hegemony",  # 区域霸权
        "global influence projection",  # 全球影响力投送
        "security guarantees",  # 安全保障
        "economic independence",  # 经济独立
        "technological parity",  # 技术均势
    ],
    CapabilityTier.T2_REGIONAL: [
        "regional leadership",  # 区域区域领导
        "territorial integrity",  # 领土完整
        "economic development",  # 经济发展
        "autonomy from great powers",  # 对大国的自主性
        "regional security",  # 区域安全
    ],
    CapabilityTier.T3_MEDIUM: [
        "sovereignty protection",  # 主权保护
        "economic stability",  # 经济稳定
        "security arrangements",  # 安全安排
        "international integration",  # 国际融入
    ],
    CapabilityTier.T4_SMALL: [
        "survival",  # 生存
        "economic viability",  # 经济生存能力
        "security guarantees",  # 安全保障
        "development assistance",  # 发展援助
    ],
}


def get_strategic_interests(tier: CapabilityTier) -> List[str]:
    """
    获取指定能力层级的客观战略利益

    根据道义现实主义理论，不同能力的国家有不同的客观战略利益。
    这些利益是基于国家能力水平而客观存在的。

    Args:
        tier: 能力层级

    Returns:
        List[str]: 战略利益列表

    Examples:
        >>> get_strategic_interests(CapabilityTier.T0_SUPERPOWER)
        ["global hegemony maintenance", "global order and rule-setting", ...]
    """
    return OBJECTIVE_STRATEGIC_INTERESTS.get(tier, [])


def compare_capability(cap1: Capability, cap2: Capability) -> float:
    """
    比较两个代理的能力差距

    Args:
        cap1: 第一个代理的能力
        cap2: 第二个代理的能力

    Returns:
        float: 能力指数差值（cap1 - cap2）
               正值表示cap1更强，负值表示cap2更强

    Examples:
        >>> cap1 = Capability("A")
        >>> cap2 = Capability("B")
        >>> diff = compare_capability(cap1, cap2)
        >>> if diff > 10: print("A明显强于B")
    """
    return cap1.get_capability_index() - cap2.get_capability_index()


def is_power_transition_possible(
    current_capability: Capability,
    target_tier: CapabilityTier,
) -> bool:
    """
    检查权力转移至目标层级是否合理

    防止模拟中出现不合理的快速权力跃升或衰落。
    规定每次最多跨越2个能力层级。

    Args:
        current_capability: 当前能力状态
        target_tier: 目标能力层级

    Returns:
        bool: 如果转移合理则返回True，否则返回False

    Examples:
        >>> current = Capability("small_state")
        >>> # 小国直接变为超级大国不合理
        >>> is_power_transition_possible(current, CapabilityTier.T0_SUPERPOWER)
        False
    """
    current_tier = current_capability.get_tier()
    tier_order = [
        CapabilityTier.T4_SMALL,
        CapabilityTier.T3_MEDIUM,
        CapabilityTier.T2_REGIONAL,
        CapabilityTier.T1_GREAT_POWER,
        CapabilityTier.T0_SUPERPOWER,
    ]

    current_idx = tier_order.index(current_tier)
    target_idx = tier_order.index(target_tier)

    # 允许最多跨越2个层级（防止不合理的跳跃）
    return abs(current_idx - target_idx) <= 2
