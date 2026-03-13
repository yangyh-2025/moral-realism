"""
事件配置模块 - 对应技术方案事件管理

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel
from typing import List, Dict, Any

class EventConfig(BaseModel):
    """事件配置"""
    random_event_probability: float = 0.1
    enable_user_events: bool = True
    periodic_events: Dict[str, Any] = {}
    random_events: List[Dict[str, Any]] = []

# 默认周期事件
DEFAULT_PERIODIC_EVENTS = {
    "leader_rotation": {
        "interval": 4,
        "name": "领导换届",
        "description": "国家领导层换届"
    },
    "power_update": {
        "interval": 1,
        "name": "实力数据年度更新",
        "description": "各国实力数据更新"
    }
}

# 默认随机事件
DEFAULT_RANDOM_EVENTS = [
    {
        "type": "regional_conflict",
        "name": "区域军事冲突",
        "impact_level": 0.8
    },
    {
        "type": "economic_crisis",
        "name": "经济危机",
        "impact_level": 0.6
    },
    {
        "type": "territorial_dispute",
        "name": "领土争端",
        "impact_level": 0.5
    },
    {
        "type": "ally_betrayal",
        "name": "盟友背叛",
        "impact_level": 0.7
    },
    {
        "type": "public_health_crisis",
        "name": "公共卫生危机",
        "impact_level": 0.4
    }
]
