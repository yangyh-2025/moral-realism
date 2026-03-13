# 事件概率配置
"""
定义系统中随机事件的概率配置和事件类型。
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum


class EventType(Enum):
    """事件类型枚举"""
    NATURAL_DISASTER = "natural_disaster"      # 自然灾害
    ECONOMIC_CRISIS = "economic_crisis"        # 经济危机
    TECHNOLOGY_BREAKTHROUGH = "tech_breakthrough"  # 技术突破
    DIPLOMATIC_INCIDENT = "diplomatic_incident"  # 外交事件
    RESOURCE_DISCOVERY = "resource_discovery"  # 资源发现
    LEADERSHIP_CHANGE = "leadership_change"    # 领导人更替
    PANDEMIC = "pandemic"                        # 流行病
    TERRORIST_ATTACK = "terrorist_attack"        # 恐怖袭击


class EventConfig(BaseModel):
    """事件配置类"""

    # 基础概率配置
    base_event_probability: float = Field(default=0.1, ge=0, le=1,
                                          description="每回合发生随机事件的基准概率")

    # 各事件类型的权重
    event_weights: Dict[str, float] = Field(
        default={
            EventType.NATURAL_DISASTER.value: 0.15,
            EventType.ECONOMIC_CRISIS.value: 0.20,
            EventType.TECHNOLOGY_BREAKTHROUGH.value: 0.10,
            EventType.DIPLOMATIC_INCIDENT.value: 0.25,
            EventType.RESOURCE_DISCOVERY.value: 0.10,
            EventType.LEADERSHIP_CHANGE.value: 0.05,
            EventType.PANDEMIC.value: 0.08,
            EventType.TERRORIST_ATTACK.value: 0.07
        },
        description="各类事件的相对权重"
    )

    # 事件影响范围配置
    max_impact_severity: float = Field(default=1.0, ge=0, le=1,
                                        description="事件最大影响严重程度")

    # 事件持续时间（回合数）
    event_duration_range: tuple[int, int] = Field(default=(1, 5),
                                                    description="事件持续时间的范围")

    # 事件影响的国家数量范围
    affected_agents_range: tuple[int, int] = Field(default=(1, 3),
                                                     description="事件影响的国家数量范围")

    # 是否启用事件系统
    events_enabled: bool = Field(default=True, description="是否启用随机事件系统")

    def get_event_probability(self, event_type: EventType) -> float:
        """获取特定事件的发生概率"""
        base_prob = self.base_event_probability
        weight = self.event_weights.get(event_type.value, 0.1)
        total_weight = sum(self.event_weights.values())
        return base_prob * (weight / total_weight)

    def get_event_impact(self, event_type: EventType) -> Dict[str, Any]:
        """生成事件影响参数"""
        import random
        return {
            "severity": random.uniform(0.3, self.max_impact_severity),
            "duration": random.randint(*self.event_duration_range),
            "affected_count": random.randint(*self.affected_agents_range)
        }

    def get_available_events(self) -> List[EventType]:
        """获取所有可用的事件类型"""
        return list(EventType)

    def update_event_weight(self, event_type: EventType, new_weight: float):
        """更新事件类型的权重"""
        self.event_weights[event_type.value] = new_weight
