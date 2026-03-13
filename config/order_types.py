# 国际秩序类型配置
"""
定义系统中的国际秩序类型，反映全球治理结构和权力分配模式。
"""
from enum import Enum
from typing import List, Optional


class InternationalOrderType(Enum):
    """国际秩序类型枚举"""
    HEGEMONIC = "hegemonic"              # 霸权秩序 - 单一霸主主导
    BALANCE_OF_POWER = "balance_of_power"  # 均势秩序 - 多强平衡
    RULE_BASED = "rule_based"              # 规则秩序 - 制度化治理
    DISORDER = "disorder"                  # 无序状态 - 缺乏稳定秩序
    MIXED = "mixed"                        # 混合秩序 - 多种模式并存

    @classmethod
    def get_description(cls, order_type: 'InternationalOrderType') -> str:
        """获取国际秩序类型描述"""
        descriptions = {
            cls.HEGEMONIC: "霸权秩序下，单一超级大国主导国际事务，其他国家在其框架内活动。",
            cls.BALANCE_OF_POWER: "均势秩序下，多个大国相互制衡，形成相对稳定的权力分配。",
            cls.RULE_BASED: "规则秩序下，国际法和制度规范成为主要治理工具，强调程序正义。",
            cls.DISORDER: "无序状态下，缺乏稳定秩序，国家行为更多基于短期利益。",
            cls.MIXED: "混合秩序下，多种治理模式并存，不同地区和领域采用不同规则。"
        }
        return descriptions.get(order_type, "未知秩序类型")

    @classmethod
    def get_stability_metrics(cls, order_type: 'InternationalOrderType') -> dict:
        """获取国际秩序的稳定性指标"""
        metrics = {
            cls.HEGEMONIC: {
                "stability_score": 0.7,
                "conflict_probability": 0.3,
                "cooperation_ease": 0.5,
                "norm_effectiveness": 0.6
            },
            cls.BALANCE_OF_POWER: {
                "stability_score": 0.6,
                "conflict_probability": 0.4,
                "cooperation_ease": 0.4,
                "norm_effectiveness": 0.5
            },
            cls.RULE_BASED: {
                "stability_score": 0.8,
                "conflict_probability": 0.2,
                "cooperation_ease": 0.7,
                "norm_effectiveness": 0.9
            },
            cls.DISORDER: {
                "stability_score": 0.3,
                "conflict_probability": 0.7,
                "cooperation_ease": 0.3,
                "norm_effectiveness": 0.2
            },
            cls.MIXED: {
                "stability_score": 0.5,
                "conflict_probability": 0.5,
                "cooperation_ease": 0.5,
                "norm_effectiveness": 0.5
            }
        }
        return metrics.get(order_type, {})
