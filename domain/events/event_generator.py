"""
随机事件生成器 - 管理随机事件的生成

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from collections import defaultdict

from domain.environment.environment_engine import Event, EventPriority

logger = logging.getLogger(__name__)


class EventType(Enum):
    """事件类型枚举"""
    NATURAL_DISASTER = "natural_disaster"  # 自然灾害
    ECONOMIC_CRISIS = "economic_crisis"    # 经济危机
    TECHNICAL_BREAKTHROUGH = "technical_breakthrough"  # 技术突破
    DIPLOMATIC_EVENT = "diplomatic_event"  # 外交事件
    REGIONAL_CONFLICT = "regional_conflict"  # 区域冲突
    TERRITORIAL_DISPUTE = "territorial_dispute"  # 领土争端
    ALLY_BETRAYAL = "ally_betrayal"  # 盟友背叛
    PUBLIC_HEALTH_CRISIS = "public_health_crisis"  # 公共卫生危机


class Season(Enum):
    """季节枚举"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


@dataclass
class EventTypeConfig:
    """事件类型配置"""
    event_type: EventType
    base_probability: float  # 基础概率 0-1
    great_power_factor: float  # 大国概率调整因子
    small_power_factor: float  # 小国概率调整因子
    season_factors: Dict[str, float]  # 季节调整因子
    cooldown_rounds: int  # 冷却期（回合数）
    impact_range: Tuple[float, float]  # 影响范围
    name: str
    description_template: str


class EventGenerator:
    """
    随机事件生成器

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, seed: Optional[int] = None):
        """
        初始化事件生成器

        Args:
            seed: 随机种子，用于结果可复现
        """
        self._random = random.Random(seed)
        self._seed = seed
        self._event_cooldowns: Dict[str, int] = {}  # {event_type: last_round}
        self._generation_stats: Dict[str, int] = defaultdict(int)

        # 事件类型配置
        self._event_configs = {
            EventType.NATURAL_DISASTER: EventTypeConfig(
                event_type=EventType.NATURAL_DISASTER,
                base_probability=0.05,
                great_power_factor=0.8,  # 大国遭受概率稍低
                small_power_factor=1.2,  # 小国更脆弱
                season_factors={
                    "spring": 1.0,
                    "summer": 0.8,
                    "fall": 1.2,
                    "winter": 1.5  # 冬季自然灾害概率更高
                },
                cooldown_rounds=12,
                impact_range=(0.6, 0.9),
                name="自然灾害",
                description_template="{agent}遭受{disaster_type}，基础设施受损"
            ),
            EventType.ECONOMIC_CRISIS: EventTypeConfig(
                event_type=EventType.ECONOMIC_CRISIS,
                base_probability=0.03,
                great_power_factor=1.3,  # 大国经济影响更大
                small_power_factor=0.7,
                season_factors={
                    "spring": 0.9,
                    "summer": 1.0,
                    "fall": 1.1,
                    "winter": 1.2
                },
                cooldown_rounds=20,
                impact_range=(0.5, 0.8),
                name="经济危机",
                description_template="{agent}遭遇{crisis_type}，经济严重衰退"
            ),
            EventType.TECHNICAL_BREAKTHROUGH: EventTypeConfig(
                event_type=EventType.TECHNICAL_BREAKTHROUGH,
                base_probability=0.02,
                great_power_factor=1.5,  # 大国技术突破概率更高
                small_power_factor=0.5,
                season_factors={
                    "spring": 1.0,
                    "summer": 0.9,
                    "fall": 1.1,
                    "winter": 1.0
                },
                cooldown_rounds=15,
                impact_range=(0.4, 0.7),
                name="技术突破",
                description_template="{agent}在{tech_field}取得重大突破"
            ),
            EventType.DIPLOMATIC_EVENT: EventTypeConfig(
                event_type=EventType.DIPLOMATIC_EVENT,
                base_probability=0.08,
                great_power_factor=1.2,
                small_power_factor=0.8,
                season_factors={
                    "spring": 1.1,
                    "summer": 1.0,
                    "fall": 1.0,
                    "winter": 0.9
                },
                cooldown_rounds=8,
                impact_range=(0.3, 0.6),
                name="外交事件",
                description_template="{agent}与其他国家发生{diplomatic_type}"
            ),
            EventType.REGIONAL_CONFLICT: EventTypeConfig(
                event_type=EventType.REGIONAL_CONFLICT,
                base_probability=0.04,
                great_power_factor=1.1,
                small_power_factor=0.9,
                season_factors={
                    "spring": 1.0,
                    "summer": 1.2,
                    "fall": 1.0,
                    "winter": 0.8
                },
                cooldown_rounds=15,
                impact_range=(0.7, 0.9),
                name="区域军事冲突",
                description_template="{agent}卷入区域军事冲突"
            ),
            EventType.TERRITORIAL_DISPUTE: EventTypeConfig(
                event_type=EventType.TERRITORIAL_DISPUTE,
                base_probability=0.06,
                great_power_factor=1.0,
                small_power_factor=1.0,
                season_factors={
                    "spring": 1.0,
                    "summer": 1.0,
                    "fall": 1.0,
                    "winter": 1.0
                },
                cooldown_rounds=10,
                impact_range=(0.4, 0.7),
                name="领土争端",
                description_template="{agent}与邻国发生领土争端"
            ),
            EventType.ALLY_BETRAYAL: EventTypeConfig(
                event_type=EventType.ALLY_BETRAYAL,
                base_probability=0.03,
                great_power_factor=1.2,
                small_power_factor=0.8,
                season_factors={
                    "spring": 1.0,
                    "summer": 1.0,
                    "fall": 1.0,
                    "winter": 1.0
                },
                cooldown_rounds=18,
                impact_range=(0.6, 0.8),
                name="盟友背叛",
                description_template="{agent}的盟友背叛了联盟"
            ),
            EventType.PUBLIC_HEALTH_CRISIS: EventTypeConfig(
                event_type=EventType.PUBLIC_HEALTH_CRISIS,
                base_probability=0.02,
                great_power_factor=1.0,
                small_power_factor=1.0,
                season_factors={
                    "spring": 1.2,  # 春季传染病高发
                    "summer": 0.8,
                    "fall": 1.1,
                    "winter": 1.3
                },
                cooldown_rounds=25,
                impact_range=(0.5, 0.8),
                name="公共卫生危机",
                description_template="{agent}遭遇{health_issue}危机"
            ),
        }

        # 子类型配置
        self._subtypes = {
            EventType.NATURAL_DISASTER: ["地震", "洪水", "干旱", "飓风", "森林火灾"],
            EventType.ECONOMIC_CRISIS: ["金融危机", "货币贬值", "贸易制裁", "债务危机"],
            EventType.TECHNICAL_BREAKTHROUGH: ["人工智能", "量子计算", "生物技术", "新能源", "航天技术"],
            EventType.DIPLOMATIC_EVENT: ["外交抗议", "联合声明", "互访", "贸易协定", "制裁"],
            EventType.REGIONAL_CONFLICT: ["边境冲突", "代理人战争", "内战外溢"],
            EventType.TERRITORIAL_DISPUTE: ["边界争议", "岛屿主权", "海洋权益"],
            EventType.ALLY_BETRAYAL: ["退出联盟", "倒戈", "秘密协议"],
            EventType.PUBLIC_HEALTH_CRISIS: ["大流行病", "食品污染", "环境污染"],
        }

    def _calculate_adjusted_probability(
        self,
        event_type: EventType,
        agent_power_level: str,  # 'great_power' or 'small_power'
        season: str,
        current_round: int
    ) -> float:
        """计算调整后的概率"""
        config = self._event_configs[event_type]

        # 基础概率
        probability = config.base_probability

        # 实力层级调整
        if agent_power_level == "great_power":
            probability *= config.great_power_factor
        else:
            probability *= config.small_power_factor

        # 季节调整
        season_factor = config.season_factors.get(season, 1.0)
        probability *= season_factor

        # 冷却期检查
        last_round = self._event_cooldowns.get(event_type.value, -config.cooldown_rounds)
        if current_round - last_round < config.cooldown_rounds:
            probability = 0  # 冷却期内不触发

        return min(probability, 1.0)  # 确保不超过1

    def _check_and_update_cooldown(
        self,
        event_type: EventType,
        current_round: int
    ) -> bool:
        """检查并更新冷却期"""
        config = self._event_configs[event_type]
        last_round = self._event_cooldowns.get(event_type.value, -config.cooldown_rounds)

        if current_round - last_round >= config.cooldown_rounds:
            self._event_cooldowns[event_type.value] = current_round
            return True
        return False

    def _generate_impact_level(self, event_type: EventType) -> float:
        """生成影响级别"""
        config = self._event_configs[event_type]
        min_impact, max_impact = config.impact_range
        return self._random.uniform(min_impact, max_impact)

    def _select_subtype(self, event_type: EventType) -> str:
        """随机选择子类型"""
        subtypes = self._subtypes.get(event_type, [])
        return self._random.choice(subtypes) if subtypes else ""

    def generate_event(
        self,
        agent_ids: List[str],
        agent_power_levels: Dict[str, str],  # {agent_id: 'great_power' | 'small_power'}
        season: str,
        current_round: int,
        force_type: Optional[EventType] = None
    ) -> Optional[Event]:
        """
        生成随机事件

        Args:
            agent_ids: 可选智能体ID列表
            agent_power_levels: 智能体实力层级映射
            season: 当前季节
            current_round: 当前回合
            force_type: 强制生成的事件类型（用于测试）

        Returns:
            Event对象或None
        """
        event_type = force_type

        if event_type is None:
            # 随机选择事件类型
            available_types = list(self._event_configs.keys())
            event_type = self._random.choice(available_types)

        # 检查冷却期
        if not self._check_and_update_cooldown(event_type, current_round):
            return None

        # 选择受影响的智能体
        if not agent_ids:
            return None

        selected_agent = self._random.choice(agent_ids)
        agent_power_level = agent_power_levels.get(selected_agent, "small_power")

        # 计算概率
        probability = self._calculate_adjusted_probability(
            event_type,
            agent_power_level,
            season,
            current_round
        )

        if self._random.random() > probability:
            return None

        # 生成事件
        config = self._event_configs[event_type]
        subtype = self._select_subtype(event_type)
        impact_level = self._generate_impact_level(event_type)

        description = config.description_template.format(
            agent=selected_agent,
            disaster_type=subtype if event_type == EventType.NATURAL_DISASTER else "",
            crisis_type=subtype if event_type == EventType.ECONOMIC_CRISIS else "",
            tech_field=subtype if event_type == EventType.TECHNICAL_BREAKTHROUGH else "",
            diplomatic_type=subtype if event_type == EventType.DIPLOMATIC_EVENT else "",
            health_issue=subtype if event_type == EventType.PUBLIC_HEALTH_CRISIS else ""
        ).strip()

        # 确定优先级
        if impact_level > 0.7:
            priority = EventPriority.HIGH
        elif impact_level > 0.5:
            priority = EventPriority.NORMAL
        else:
            priority = EventPriority.LOW

        event = Event(
            _priority_index=priority.value,
            event_id=f"{event_type.value}_{current_round}_{self._random.randint(1000, 9999)}",
            event_type=event_type.value,
            name=config.name,
            description=description,
            participants=[selected_agent],
            impact_level=impact_level,
            priority=priority,
            metadata={
                "round": current_round,
                "type": event_type.value,
                "subtype": subtype,
                "agent_power_level": agent_power_level
            }
        )

        self._generation_stats[event_type.value] += 1
        logger.info(f"Generated event: {event.event_id} - {event.name}")

        return event

    def generate_batch(
        self,
        agent_ids: List[str],
        agent_power_levels: Dict[str, str],
        season: str,
        current_round: int,
        max_events: int = 3
    ) -> List[Event]:
        """
        批量生成事件

        Args:
            agent_ids: 可选智能体ID列表
            agent_power_levels: 智能体实力层级映射
            season: 当前季节
            current_round: 当前回合
            max_events: 最大生成事件数

        Returns:
            事件列表
        """
        events = []

        for _ in range(max_events):
            event = self.generate_event(
                agent_ids,
                agent_power_levels,
                season,
                current_round
            )
            if event:
                events.append(event)

        return events

    def set_probability_adjustment(
        self,
        event_type: EventType,
        base_probability: Optional[float] = None,
        great_power_factor: Optional[float] = None,
        small_power_factor: Optional[float] = None
    ) -> None:
        """
        动态调整事件概率

        Args:
            event_type: 事件类型
            base_probability: 基础概率（可选）
            great_power_factor: 大国调整因子（可选）
            small_power_factor: 小国调整因子（可选）
）
        """
        if event_type not in self._event_configs:
            raise ValueError(f"Unknown event type: {event_type}")

        config = self._event_configs[event_type]

        if base_probability is not None:
            config.base_probability = base_probability
        if great_power_factor is not None:
            config.great_power_factor = great_power_factor
        if small_power_factor is not None:
            config.small_power_factor = small_power_factor

        logger.debug(f"Updated probability for {event_type.value}")

    def get_generation_stats(self) -> Dict[str, int]:
        """获取生成统计信息"""
        return dict(self._generation_stats)

    def reset_cooldown(self, event_type: Optional[EventType] = None) -> None:
        """
        重置冷却期

        Args:
            event_type: 要重置的事件类型，None表示重置所有
        """
        if event_type is None:
            self._event_cooldowns.clear()
        else:
            self._event_cooldowns.pop(event_type.value, None)

    def get_seed(self) -> Optional[int]:
        """获取随机种子"""
        return self._seed

    def reseed(self, seed: int) -> None:
        """重新设置随机种子"""
        self._seed = seed
        self._random.seed(seed)
        logger.info(f"Reseeded with: {seed}")
