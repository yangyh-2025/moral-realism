"""
环境仿真引擎 - 管理仿真环境状态

GitGit提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class Event:
    """事件数据类"""
    event_id: str
    event_type: str  # 'periodic' | 'random' | 'user_defined'
    name: str
    description: str
    participants: List[str]  # 涉及的智能体ID
    impact_level: float  # 影响级别 0-1
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class InternationalNorm:
    """国际规范数据类"""
    norm_id: str
    name: str
    description: str
    validity: float  # 有效性 0-100
    adherence_rate: float  # 遵守率 0-1

@dataclass
class EnvironmentState:
    """环境状态数据类"""
    current_round: int = 0
    current_date: datetime = field(default_factory=datetime.now)
    norms: List[InternationalNorm] = field(default_factory=list)
    active_events: List[Event] = field(default_factory=list)
    event_history: List[Event] = field(default_factory=list)

class EnvironmentEngine:
    """
    环境仿真引擎

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, initial_round: int = 0):
        self.state = EnvironmentState(current_round=initial_round)
        self._initialize_default_norms()

    def _initialize_default_norms(self):
        """初始化默认国际规范"""
        default_norms = [
            InternationalNorm(
                norm_id="sovereign_equality",
                name="主权平等原则",
                description="所有国家主权平等",
                validity=100.0,
                adherence_rate=1.0
            ),
            InternationalNorm(
                norm_id="no_use_of_force",
                name="不使用武力原则",
                description="禁止在国际关系中使用武力",
                validity=100.0,
                adherence_rate=1.0
            ),
            InternationalNorm(
                norm_id="pacta_sunt_servanda",
                name="条约必须信守原则",
                description="条约必须遵守",
                validity=100.0,
                adherence_rate=1.0
            ),
            InternationalNorm(
                norm_id="non_intervention",
                name="不干涉内政原则",
                description="不干涉他国内政",
                validity=100.0,
                adherence_rate=1.0
            )
        ]
        self.state.norms = default_norms

    def update_round(self) -> int:
        """更新仿真轮次"""
        self.state.current_round += 1
        return self.state.current_round

    def trigger_periodic_events(self, agent_ids: List[str]) -> List[Event]:
        """触发周期性事件"""
        events = []
        current_round = self.state.current_round

        # 领导换届事件（每4年）
        if current_round % 4 == 0:
            event = Event(
                event_id=f"leader_election_{current_round}",
                event_type="periodic",
                name="领导换届",
                description="国家领导层换届",
                participants=agent_ids,
                impact_level=0.5
            )
            events.append(event)

        # 年度实力更新
        event = Event(
            event_id=f"power_update_{current_round}",
            event_type="periodic",
            name="实力数据年度更新",
            description="各国实力数据更新",
            participants=agent_ids,
            impact_level=0.3
        )
        events.append(event)

        self.state.active_events.extend(events)
        return events

    def trigger_random_events(
        self,
        agent_ids: List[str],
        probability: float = 0.1
    ) -> List[Event]:
        """触发随机事件"""
        import random
        events = []

        if random.random() < probability:
            event_types = [
                ("regional_conflict", "区域军事冲突", 0.8),
                ("economic_crisis", "经济危机", 0.6),
                ("territorial_dispute", "领土争端", 0.5),
                ("ally_betrayal", "盟友背叛", 0.7),
                ("public_health_crisis", "公共卫生危机", 0.4)
            ]

            event_type, name, impact_level = random.choice(event_types)

            # 随机选择参与方
            participants = random.sample(
                agent_ids,
                min(3, len(agent_ids))
            )

            event = Event(
                event_id=f"random_{event_type}_{self.state.current_round}",
                event_type="random",
                name=name,
                description=f"随机触发事件: {name}",
                participants=participants,
                impact_level=impact_level
            )
            events.append(event)

        self.state.active_events.extend(events)
        return events

    def add_user_event(self, event: Event) -> None:
        """添加用户自定义事件"""
        self.state.active_events.append(event)

    def clear_active_events(self) -> None:
        """清空当前活跃事件，移入历史"""
        self.state.event_history.extend(self.state.active_events)
        self.state.active_events = []

    def get_full_state(self) -> Dict:
        """获取完整环境状态"""
        return {
            "current_round": self.state.current_round,
            "current_date": self.state.current_date.isoformat(),
            "norms": [
                {
                    "id": n.norm_id,
                    "name": n.name,
                    "validity": n.validity,
                    "adherence_rate": n.adherence_rate
                }
                for n in self.state.norms
            ],
            "active_events": [
                {
                    "id": e.event_id,
                    "type": e.event_type,
                    "name": e.name,
                    "description": e.description,
                    "participants": e.participants,
                    "impact_level": e.impact_level
                }
                for e in self.state.active_events
            ]
        }
