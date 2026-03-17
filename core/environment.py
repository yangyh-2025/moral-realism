"""
环境仿真引擎 - 管理仿真环境状态

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Callable, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import heapq
from enum import IntEnum
import logging
from collections import deque
import threading

logger = logging.getLogger(__name__)


class EventPriority(IntEnum):
    """事件优先级枚举"""
    CRITICAL = 0  # 紧急事件（如战争、重大危机）
    HIGH = 1      # 高优先级（如重大外交事件）
    NORMAL = 2    # 正常优先级（如常规事件）
    LOW = 3       # 低优先级（如通知类事件）

@dataclass(order=True)
class Event:
    """事件数据类"""
    # 用于优先队列排序的标识符（越小优先级越高）
    _priority_index: int = field(compare=True)
    event_id: str = field(compare=False)
    event_type: str = field(compare=False)  # 'periodic' | 'random' | 'user_defined' | 'natural' | 'economic' | 'technical'
    name: str = field(compare=False)
    description: str = field(compare=False)
    participants: List[str] = field(compare=False, default_factory=list)  # 涉及的智能体ID
    impact_level: float = field(compare=False, default=0.5)  # 影响级别 0-1
    priority: EventPriority = field(compare=False, default=EventPriority.NORMAL)
    timestamp: datetime = field(compare=False, default_factory=datetime.now)
    cancelled: bool = field(compare=False, default=False)
    callback: Optional[Callable] = field(compare=False, default=None)  # 事件触发时的回调函数
    metadata: Dict[str, Any] = field(compare=False, default_factory=dict)  # 额外元数据

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
    # 新增：季节信息
    season: str = "spring"  # 'spring', 'summer', 'fall', 'winter'
    # 新增：事件冷却期追踪 {event_type: last_round}
    event_cooldowns: Dict[str, int] = field(default_factory=dict)

class EventScheduler:
    """
    事件调度器 - 使用优先队列管理事件

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        self._event_queue: List[Event] = []  # 优先队列
        self._priority_counter = 0  # 优先级计数器
        self._scheduled_events: Dict[str, Event] = {}  # 已调度事件映射
        self._execution_stats: Dict[str, int] = {
            "total_scheduled": 0,
            "total_executed": 0,
            "total_cancelled": 0,
            "total_delayed": 0
        }
        self._lock = threading.Lock()  # 线程锁

    def schedule(self, event: Event) -> str:
        """调度事件"""
        with self._lock:
            if event.cancelled:
                logger.warning(f"Event {event.event_id} is already cancelled, not scheduling")
                return event.event_id

            if event.event_id in self._scheduled_events:
                logger.warning(f"Event {event.event_id} already scheduled, updating")
                self._cancel_internal(event.event_id)

            # 使用优先级计数器确保相同优先级事件按插入顺序处理
            priority_index = (event.priority.value, self._priority_counter)
            event._priority_index = priority_index[0]

            heapq.heappush(self._event_queue, event)
            self._scheduled_events[event.event_id] = event
            self._priority_counter += 1
            self._execution_stats["total_scheduled"] += 1

            logger.debug(f"Scheduled event: {event.event_id} with priority {event.priority.name}")
            return event.event_id

    def schedule_delayed(
        self,
        event: Event,
        delay_rounds: int,
        current_round: int
    ) -> str:
        """调度延迟事件"""
        event.metadata["target_round"] = current_round + delay_rounds
        event.metadata["delayed_until"] = delay_rounds
        return self.schedule(event)

    def _cancel_internal(self, event_id: str) -> bool:
        """内部取消事件（不获取锁）"""
        if event_id in self._scheduled_events:
            self._scheduled_events[event_id].cancelled = True
            del self._scheduled_events[event_id]
            self._execution_stats["total_cancelled"] += 1
            logger.info(f"Cancelled event: {event_id}")
            return True
        return False

    def cancel(self, event_id: str) -> bool:
        """取消事件"""
        with self._lock:
            return self._cancel_internal(event_id)

    def execute_next(
        self,
        current_round: int,
        context: Optional[Dict] = None
    ) -> Optional[Event]:
        """执行下一个事件"""
        with self._lock:
            # 清理已取消的事件
            while self._event_queue and self._event_queue[0].cancelled:
                cancelled_event = heapq.heappop(self._event_queue)
                logger.debug(f"Removed cancelled event from queue: {cancelled_event.event_id}")

            if not self._event_queue:
                return None

            # 检查延迟事件
            next_event = self._event_queue[0]
            target_round = next_event.metadata.get("target_round", current_round)

            if target_round > current_round:
                logger.debug(f"Next event {next_event.event_id} scheduled for round {target_round}, current {current_round}")
                return None

            # 执行事件
            event = heapq.heappop(self._event_queue)
            if event.event_id in self._scheduled_events:
                del self._scheduled_events[event.event_id]
            self._execution_stats["total_executed"] += 1

            logger.info(f"Executing event: {event.event_id}")

            # 执行回调（在锁外执行，避免回调持有锁过久）
            if event.callback is not None:
                try:
                    event.callback(event, context)
                except Exception as e:
                    logger.error(f"Error executing callback for event {event.event_id}: {e}")

            return event

    def get_pending_count(self) -> int:
        """获取待处理事件数量"""
        return len(self._event_queue)

    def get_stats(self) -> Dict[str, int]:
        """获取调度器统计信息"""
        return self._execution_stats.copy()

    def clear(self):
        """清空调度器"""
        self._event_queue.clear()
        self._scheduled_events.clear()


class EnvironmentEngine:
    """
    环境仿真引擎

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, initial_round: int = 0, seed: Optional[int] = None):
        self.state = EnvironmentState(current_round=initial_round)
        self._scheduler = EventScheduler()
        self._initialize_default_norms()
        self._season_cycle = ["spring", "summer", "fall", "winter"]
        self._seed = seed

        # 事件重叠处理策略
        self._overlap_policy = "merge"  # 'merge', 'replace', 'queue', 'ignore'

        # 周期性事件配置
        self._periodic_configs = {
            "election": {"interval": 4, "priority": EventPriority.NORMAL},
            "power_update": {"interval": 1, "priority": EventPriority.LOW},
            "economic_cycle": {"interval": 8, "priority": EventPriority.HIGH},
            "seasonal": {"interval": 1, "priority": EventPriority.LOW},
        }

        # 事件冷却期配置（单位：回合数）
        self._cooldown_configs = {
            "election": 4,
            "power_update": 1,
            "economic_cycle": 8,
            "natural_disaster": 12,
            "crisis": 20
        }

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

    def _update_season(self):
        """更新季节信息"""
        round_index = self.state.current_round % 4
        self.state.season = self._season_cycle[round_index]
        logger.debug(f"Season updated to: {self.state.season}")

    def _check_cooldown(self, event_type: str) -> bool:
        """检查事件是否在冷却期"""
        if event_type not in self._cooldown_configs:
            return True

        cooldown_rounds = self._cooldown_configs[event_type]
        last_trigger = self.state.event_cooldowns.get(event_type, -cooldown_rounds)

        if self.state.current_round - last_trigger >= cooldown_rounds:
            self.state.event_cooldowns[event_type] = self.state.current_round
            return True
        return False

    def update_round(self) -> int:
        """更新仿真轮次"""
        self.state.current_round += 1
        self._update_season()
        return self.state.current_round

    def trigger_periodic_events(self, agent_ids: List[str]) -> List[Event]:
        """触发周期性事件（完整实现）"""
        events = []

        # 1. 选举周期事件（每4年）
        if self.state.current_round % 4 == 0 and self._check_cooldown("election"):
            event = Event(
                _priority_index=EventPriority.NORMAL.value,
                event_id=f"election_{self.state.current_round}",
                event_type="periodic",
                name="领导换届",
                description="国家领导层换届选举",
                participants=agent_ids,
                impact_level=0.5,
                priority=EventPriority.NORMAL,
                metadata={"round": self.state.current_round, "type": "election"}
            )
            events.append(event)

        # 2. 领导变更事件（选举后的随机回合）
        if self.state.current_round % 4 == 1:
            event = Event(
                _priority_index=EventPriority.HIGH.value,
                event_id=f"leadership_change_{self.state.current_round}",
                event_type="periodic",
                name="领导变更",
                description="新领导层上任，外交政策可能调整",
                participants=agent_ids,
                impact_level=0.4,
                priority=EventPriority.HIGH,
                metadata={"round": self.state.current_round, "type": "leadership_change"}
            )
            events.append(event)

        # 3. 季节性事件（每回合）
        season_event = Event(
            _priority_index=EventPriority.LOW.value,
            event_id=f"seasonal_{self.state.season}_{self.state.current_round}",
            event_type="periodic",
            name=f"季节更替-{self.state.season}",
            description=f"进入{self.state.season}，可能影响经济活动和资源分配",
            participants=[],
            impact_level=0.2,
            priority=EventPriority.LOW,
            metadata={"season": self.state.season, "round": self.state.current_round}
        )
        events.append(season_event)

        # 4. 经济周期事件（每8年）
        cycle_phase = (self.state.current_round % 8) // 2  # 0-3
        cycle_names = ["经济复苏", "经济繁荣", "经济衰退", "经济萧条"]

        if self.state.current_round % 2 == 0 and self._check_cooldown("economic_cycle"):
            event = Event(
                _priority_index=EventPriority.HIGH.value,
                event_id=f"economic_cycle_{self.state.current_round}",
                event_type="periodic",
                name=f"经济周期-{cycle_names[cycle_phase]}",
                description=f"全球经济进入{cycle_names[cycle_phase]}阶段",
                participants=agent_ids,
                impact_level=0.6 if cycle_phase >= 2 else 0.4,
                priority=EventPriority.HIGH,
                metadata={
                    "round": self.state.current_round,
                    "cycle_phase": cycle_phase,
                    "cycle_name": cycle_names[cycle_phase]
                }
            )
            events.append(event)

        # 5. 年度实力更新（每回合）
        if self._check_cooldown("power_update"):
            event = Event(
                _priority_index=EventPriority.LOW.value,
                event_id=f"power_update_{self.state.current_round}",
                event_type="periodic",
                name="实力数据年度更新",
                description="各国实力数据年度更新",
                participants=agent_ids,
                impact_level=0.3,
                priority=EventPriority.LOW,
                metadata={"round": self.state.current_round, "type": "power_update"}
            )
            events.append(event)

        # 调度所有事件
        for event in events:
            self._scheduler.schedule(event)

        self.state.active_events.extend(events)
        return events

    def trigger_random_events(
        self,
        agent_ids: List[str],
        probability: float = 0.1,
        use_advanced_generator: bool = False,
        agent_power_levels: Optional[Dict[str, str]] = None
    ) -> List[Event]:
        """
        触发随机事件

        Args:
            agent_ids: 智能体ID列表
            probability: 触发概率
            use_advanced_generator: 是否使用高级事件生成器
            agent_power_levels: 智能体实力层级映射（用于高级生成器）

        Returns:
            生成的事件列表
        """
        import random
        events = []

        if use_advanced_generator and agent_power_levels:
            # 使用高级事件生成器
            try:
                from core.event_generator import EventGenerator

                # 确保有生成器实例
                if not hasattr(self, '_event_generator'):
                    self._event_generator = EventGenerator(seed=self._seed)

                # 批量生成事件
                events = self._event_generator.generate_batch(
                    agent_ids,
                    agent_power_levels,
                    self.state.season,
                    self.state.current_round,
                    max_events=3
                )

                # 调度事件
                for event in events:
                    self._scheduler.schedule(event)

                self.state.active_events.extend(events)
                return events

            except ImportError:
                logger.warning("Advanced event generator not available, using simple generator")

        # 简单随机事件生成（后备方案）
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

            # 确定优先级
            if impact_level > 0.7:
                priority = EventPriority.HIGH
            elif impact_level > 0.5:
                priority = EventPriority.NORMAL
            else:
                priority = EventPriority.LOW

            event = Event(
                _priority_index=priority.value,
                event_id=f"random_{event_type}_{self.state.current_round}",
                event_type=event_type,
                name=name,
                description=f"随机触发事件: {name}",
                participants=participants,
                impact_level=impact_level,
                priority=priority,
                metadata={"round": self.state.current_round, "type": event_type}
            )
            events.append(event)
            self._scheduler.schedule(event)

        self.state.active_events.extend(events)
        return events

    def add_user_event(self, event: Event) -> None:
        """添加用户自定义事件"""
        self.state.active_events.append(event)

    def clear_active_events(self) -> None:
        """清空当前活跃事件，移入历史"""
        self.state.event_history.extend(self.state.active_events)
        self.state.active_events = []

    def schedule_event(self, event: Event) -> str:
        """调度单个事件"""
        return self._scheduler.schedule(event)

    def schedule_delayed_event(
        self,
        event: Event,
        delay_rounds: int
    ) -> str:
        """调度延迟事件"""
        return self._scheduler.schedule_delayed(
            event,
            delay_rounds,
            self.state.current_round
        )

    def cancel_event(self, event_id: str) -> bool:
        """取消事件"""
        return self._scheduler.cancel(event_id)

    def execute_scheduled_events(self, context: Optional[Dict] = None) -> List[Event]:
        """执行所有到期的调度事件"""
        executed_events = []
        while True:
            event = self._scheduler.execute_next(
                self.state.current_round,
                context or {}
            )
            if event is None:
                break
            executed_events.append(event)
        return executed_events

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """获取事件调度器统计信息"""
        return {
            "stats": self._scheduler.get_stats(),
            "pending_events": self._scheduler.get_pending_count()
        }

    def set_overlap_policy(self, policy: str):
        """
        设置事件重叠处理策略

        Args:
            policy: 'merge' - 合并重叠事件
                    'replace' - 替换旧事件
                    'queue' - 按顺序处理
                    'ignore' - 忽略
        """
        if policy in ["merge", "replace", "queue", "ignore"]:
            self._overlap_policy = policy
        else:
            raise ValueError(f"Invalid overlap policy: {policy}")

    def calculate_event_impact(
        self,
        event: Event,
        all_agent_ids: List[str],
        agent_positions: Optional[Dict[str, Tuple[float, float]]] = None,
        relationships: Optional[Dict[str, Dict[str, float]]] = None,
        agent_power_levels: Optional[Dict[str, float]] = None,
        propagation_model: str = "hybrid"
    ) -> Optional[Dict[str, Any]]:
        """
        计算事件影响

        Args:
            event: 事件对象
            all_agent_ids: 所有智能体ID列表
            agent_positions: 智能体位置映射（可选）
            relationships: 关系矩阵（可选）
            agent_power_levels: 智能体实力级别（可选）
            propagation_model: 传播模型 ('distance_based', 'relationship_based', 'hybrid')

        Returns:
            影响报告字典，如果影响模型不可加载则返回None
        """
        try:
            from core.event_impact import EventImpactModel, PropagationModel

            # 确保有影响模型实例
            if not hasattr(self, '_impact_model'):
                self._impact_model = EventImpactModel()

            # 转换传播模型
            model_map = {
                "distance_based": PropagationModel.DISTANCE_BASED,
                "relationship_based": PropagationModel.RELATIONSHIP_BASED,
                "hybrid": PropagationModel.HYBRID
            }
            model = model_map.get(propagation_model, PropagationModel.HYBRID)

            # 计算影响
            report = self._impact_model.calculate_impact(
                event,
                all_agent_ids,
                agent_positions,
                relationships,
                agent_power_levels,
                model
            )

            # 返回影响报告的字典表示
            return {
                "event_id": report.event_id,
                "event_name": report.event_name,
                "directly_affected": report.directly_affected,
                "influence_count": len(report.influenced_agents),
                "global_metrics": {
                    "norm_validity_change": report.global_metrics.norm_validity_change,
                    "conflict_level_change": report.global_metrics.conflict_level_change,
                    "overall_stability_change": report.global_metrics.overall_stability_change
                },
                "propagation_paths": report.propagation_paths,
                "heatmap_data": report.heat_map_data,
                "summary": self._impact_model.get_impact_summary(report)
            }

        except ImportError:
            logger.warning("Event impact model not available")
            return None

    def get_impact_history(self, limit: int = 10) -> List[Dict]:
        """
        获取事件影响历史

        Args:
            limit: 返回记录数

        Returns:
            历史记录列表
        """
        try:
            from core.event_impact import EventImpactModel

            if not hasattr(self, '_impact_model'):
                self._impact_model = EventImpactModel()

            return self._impact_model.analyze_historical_impact(limit)

        except ImportError:
            logger.warning("Event impact model not available")
            return []

    def get_full_state(self) -> Dict:
        """获取完整环境状态"""
        return {
            "current_round": self.state.current_round,
            "current_date": self.state.current_date.isoformat(),
            "season": self.state.season,
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
                    "description": e.description if not hasattr(e.description, 'description') else e.description.description,
                    "participants": e.participants,
                    "impact_level": e.impact_level,
                    "priority": e.priority.name
                }
                for e in self.state.active_events
            ],
            "scheduler_stats": self.get_scheduler_stats()
        }
