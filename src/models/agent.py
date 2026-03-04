"""
代理（Agent）模型模块

本模块定义了道义现实主义ABM系统中的基础代理类和代理类型。
代理代表国际体系中的国家或其他行为体。

核心概念：
- AgentType: 代理类型（大国、小国、国际组织、控制者）
- Agent: 代理抽象基类，定义所有代理必须实现的核心接口
- HistoryEntry: 代理历史记录条目

使用场景：
1. 创建不同类型的国家代理
2. 管理代理的状态、能力、历史记录
3. 处理代理之间的互动和决策
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.capability import Capability
from src.models.leadership_type import LeadershipType, LeadershipProfile


class AgentType(Enum):
    """
    代理类型枚举

    定义模拟中不同类型的代理：

    1. GREAT_POWER (大国):
       - 具有全球影响力
       - 可以在全球范围投射力量
       - 拥有广泛的行动选项

    2. SMALL_STATE (小国):
       - 能力有限
       - 选项受限
       - 需要战略性地做出选择

    3. ORGANIZATION (国际组织):
       - 如联合国、世界贸易组织等
       - 具有规则制定和监督功能
       - 提供合作平台

    4. CONTROLLER (控制者/实验者):
       - 代表系统外的观察者或干预者
       - 可以注入外部事件或约束
    """

    GREAT_POWER = "great_power"  # 大国
    SMALL_STATE = "small_state"  # 小国
    ORGANIZATION = "organization"  # 国际组织
    CONTROLLER = "controller"  # 控制者/实验者


class InteractionType(Enum):
    """
    互动类型枚举

    定义代理之间可能发生的互动类型：

    1. DIPLOMATIC (外交沟通): 通过外交渠道进行的正式沟通
    2. ECONOMIC (经济互动): 经济合作、贸易或制裁
    3. MILITARY (军事互动): 军事行动、演习或威慑
    4. COERCIVE (强制措施): 非军事强制手段
    5. COOPERATIVE (合作项目): 多边合作或共同倡议
    """

    DIPLOMATIC = "diplomatic"  # 外交沟通
    ECONOMIC = "economic"  # 经济合作/制裁
    MILITARY = "military"  # 军事互动
    COERCIVE = "coercive"  # 强制措施
    COOPERATIVE = "cooperative"  # 合作项目


@dataclass
class HistoryEntry:
    """
    代理历史记录条目类

    记录代理在模拟过程中的关键事件和决策。

    属性说明：
    - timestamp: 事件发生的时间戳
    - event_type: 事件类型（如"decision"、"response"、"interaction"）
    - content: 事件内容描述
    - metadata: 附加的元数据字典，用于存储事件相关的详细信息
    """

    timestamp: datetime  # 时间戳
    event_type: str  # 事件类型
    content: str  # 事件内容
    metadata: Dict[str, Any] = field(default_factory=dict)  # 附加元数据

    def __init__(
        self,
        timestamp: datetime,
        event_type: str,
        content: str,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """
        初始化历史记录条目，支持字符串时间戳的自动转换

        Args:
            timestamp: 时间戳（datetime对象或ISO格式字符串）
            event_type: 事件类型
            content: 事件内容描述
            metadata: 附加元数据（可选）
        """
        # 处理字符串时间戳的转换
        if isinstance(timestamp, str):
            from datetime import datetime as dt
            self.timestamp = dt.fromisoformat(timestamp)
        else:
            self.timestamp = timestamp
        self.event_type = event_type
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        将历史记录条目转换为字典格式

        Returns:
            Dict[str, Any]: 包含时间戳、事件类型、内容和元数据的字典

        Examples:
            >>> entry = HistoryEntry(datetime.now(), "decision", "内容")
            >>> entry_dict = entry.to_dict()
            >>> entry_dict["event_type"]
            "decision"
        """
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "content": self.content,
            "metadata": self.metadata,
        }


@dataclass
class Agent(ABC):
    """
    代理抽象基类

    定义了所有代理必须实现的核心结构和接口。
    具体代理类型（大国、小国等）应该继承此类。

    核心属性：
    - 基本标识: agent_id, name, name_zh, agent_type
    - 领导特征: leadership_type, leadership_profile
    - 能力与权力: capability
    - 状态与状态: is_active, is_alive
    - 历史追踪: history, max_history_length
    - 关系管理: relations
    - 自定义属性: attributes

    核心方法（需子类实现）:
    - decide(): 根据当前情况做出决策
    - respond(): 响应其他代理的消息

    工具方法：
    - add_history(): 添加历史记录
    - get_history(): 获取历史记录
    - set_relationship/get_relationship(): 管理与其它代理的关系
    - is_friendly_with/is()hostile_toward(): 检查关系状态
    """

    # 基本标识
    agent_id: str  # 代理唯一标识符
    name: str  # 代理英文名称
    name_zh: str  # 代理中文名称
    agent_type: AgentType  # 代理类型

    # 领导特征
    leadership_type: LeadershipType  # 领导类型
    leadership_profile: Optional[LeadershipProfile] = None  # 领导配置文件

    # 能力与权力
    capability: Optional[Capability] = None  # 综合能力

    # 状态与状态
    is_active: bool = True  # 是否活跃（可参与互动）
    is_alive: bool = True  # 是否存活（尚未被移除）

    # 历史追踪
    history: List[HistoryEntry] = field(default_factory=list)  # 历史记录
    max_history_length: int = 1000  # 最大历史记录长度

    # 与其他代理的关系
    # 字典格式：agent_id -> relationship_score (-1到1)
    # -1: 完全敌对，1: 完全友好，0: 中立
    relations: Dict[str, float] = field(default_factory=dict)

    # 自定义属性，特定代理类型使用
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        初始化后的处理

        自动加载领导配置文件和能力对象。
        """
        if self.leadership_profile is None:
            from src.models.leadership_type import get_leadership_profile
            self.leadership_profile = get_leadership_profile(self.leadership_type)

        if self.capability is None:
            self.capability = Capability(agent_id=self.agent_id)

        # 初始化与自己的关系（总是友好的）
        self.relations[self.agent_id] = 1.0

    @abstractmethod
    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        根据当前情况做出决策

        这是每个代理必须实现的核心决策方法。
        决策应该反映代理的领导类型、利益和能力水平。

        Args:
            situation: 当前情况的描述
                       例如："局势描述"或具体的危机场景
            available_actions: 可用行动的列表
                               每个行动包含id、description等信息
            context: 决策的附加上下文信息（可选）

        Returns:
            Dict[str, Any]: 包含决策和理由的字典
                - action: 选择的行动ID
                - rationale: 决策理由
                - leadership_influence: 领导类型的影响

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        pass

    @abstractmethod
    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        响应来自其他代理的消息

        Args:
            sender_id: 发送消息的代理ID
            message: 消息内容和元数据
                      例如：{"type": "proposal", "content": "..."}
            context: 响应生成的附加上下文信息（可选）

        Returns:
            Dict[str, Any]: 包含响应的字典
                - sender_id: 发送者ID（自己的ID）
                - receiver_id: 接收者ID
                - content: 响应内容
                - leadership_influence: 领导类型的影响

        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        pass

    def add_history(
        self,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        向代理的历史记录中添加一个条目

        Args:
            event_type: 事件类型（如"decision"、"response"、"interaction"）
            content: 事件内容描述
            metadata: 事件的附加元数据（可选）

        Examples:
            >>> agent.add_history("decision", "决定采取外交行动",
            ...                 {"action_id": "action_001", "rationale": "..."})
        """
        entry = HistoryEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            content=content,
            metadata=metadata or {},
        )
        self.history.append(entry)

        # 维护最大历史记录长度
        if len(self.history) > self.max_history_length:
            self.history = self.history[-self.max_history_length:]

    def get_history(self, event_type: Optional[str] = None) -> List[HistoryEntry]:
        """
        获取代理的历史记录，可按事件类型筛选

        Args:
            event_type: 如果指定，只返回该类型的事件（可选）

        Returns:
            List[HistoryEntry]: 历史记录条目列表

        Examples:
            >>> # 获取所有历史记录
            >>> all_history = agent.get_history()
            >>> # 只获取决策历史
            >>> decisions = agent.get_history("decision")
        """
        if event_type is None:
            return self.history.copy()
        return [entry for entry in self.history if entry.event_type == event_type]

    def get_recent_history(self, n: int = 10) -> List[HistoryEntry]:
        """
        获取最近n条历史记录

        Args:
            n: 要返回的最近条目数，默认为10

        Returns:
            List[HistoryEntry]: 最近的历史记录条目列表

        Examples:
            >>> recent = agent.get_recent_history(5)
            >>> # 返回最近5条记录
        """
        return self.history[-n:] if len(self.history) >= n else self.history.copy()

    def set_relationship(self, target_id: str, score: float) -> None:
        """
        设置与另一个代理的关系分数

        Args:
            target_id: 目标代理的ID
            score: 关系分数（-1到1）
                   -1: 完全敌对
                   0: 中立
                   1: 完全友好

        Raises:
            ValueError: 如果分数超出[-1, 1]范围

        Examples:
            >>> agent.set_relationship("other_agent", 0.5)  # 设置为较友好关系
        """
        score = max(-1.0, min(1.0, score))
        self.relations[target_id] = score

    def get_relationship(self, target_id: str) -> float:
        """
        获取与另一个代理的关系分数

        Args:
            target_id: 目标代理的ID

        Returns:
            float: 关系分数（-1到1），默认为0（中立）

        Examples:
            >>> score = agent.get_relationship("other_agent")
            >>> if score > 0: print("友好关系")
        """
        return self.relations.get(target_id, 0.0)

    def is_friendly_with(self, target_id: str) -> bool:
        """
        检查与另一个代理是否为友好关系

        Args:
            target_id: 目标代理的ID

        Returns:
            bool: 如果关系友好（分数>0.3）则返回True

        Examples:
            >>> if agent.is_friendly_with("other_agent"):
            ...     # 执行友好合作行为
        """
        return self.get_relationship(target_id) > 0.3

    def is_hostile_toward(self, target_id: str) -> bool:
        """
        检查与另一个代理是否为敌对关系

        Args:
            target_id: 目标代理的ID

        Returns:
            bool: 如果关系敌对（分数<-0.3）则返回True

        Examples:
            >>> if agent.is_hostile_toward("other_agent"):
            ...     # 执行防御或对抗行为
        """
        return self.get_relationship(target_id) < -0.3

    def get_capability_tier(self) -> str:
        """
        获取代理的能力层级作为字符串

        Returns:
            str: 能力层级字符串值

        Examples:
            >>> tier = agent.get_capability_tier()
            >>> print(f"当前能力层级: {tier}")
        """
        if self.capability is None:
            return "unknown"
        return self.capability.get_tier().value

    def get_summary(self) -> Dict[str, Any]:
        """
        获取代理当前状态的摘要信息

        Returns:
            Dict[str, Any]: 包含代理摘要信息的字典
                - agent_id: 代理ID
                - name: 英文名称
                - name_zh: 中文名称
                - agent_type: 代理类型
                - leadership_type: 领导类型
                - leadership_name: 领导类型名称
                - capability_tier: 能力层级
                - capability_index: 能力指数
                - is_active: 是否活跃
                - is_alive: 是否存活
                - history_length: 历史记录长度
                - relations_count: 关系数量

        Examples:
            >>> summary = agent.get_summary()
            >>> print(f"{summary['name_zh']} - 能力: {summary['capability_tier']}")
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "name_zh": self.name_zh,
            "agent_type": self.agent_type.value,
            "leadership_type": self.leadership_type.value,
            "leadership_name": self.leadership_profile.name if self.leadership_profile else None,
            "capability_tier": self.get_capability_tier(),
            "capability_index": self.capability.get_capability_index() if self.capability else None,
            "is_active": self.is_active,
            "is_alive": self.is_alive,
            "history_length": len(self.history),
            "relations_count": len(self.relations),
        }


@dataclass
class GreatPower(Agent):
    """
    大国代理类

    具有重要全球影响力的国家代理。

    特征：
    - 能力层级通常为T0或T1
    - 拥有广泛的行动选项
    - 考虑全球战略影响
    - 可以在全球范围投射力量

    决策逻辑：
    - 考虑全球战略影响
    - 拥有比小国更广泛的行动选项
    - 可以影响国际规则和制度
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_zh: str,
        leadership_type: LeadershipType,
        capability: Optional[Capability] = None,
    ) -> None:
        """
        初始化大国代理

        Args:
            agent_id: 代理唯一标识符
            name: 英文名称
            name_zh: 中文名称
            leadership_type: 领导类型
            capability: 能力对象（可选，会自动创建默认值）
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            name_zh=name_zh,
            agent_type=AgentType.GREAT_POWER,
            leadership_type=leadership_type,
            capability=capability,
        )

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        作为大国做出决策

        大国考虑全球战略影响，拥有更广泛的行动选择。

        Args:
            situation: 当前情况描述
            available_actions: 可用行动列表
            context: 附加上下文

        Returns:
            Dict[str, Any]: 决策结果

        Note:
            此方法将在后续阶段通过LLM集成实现。
            当前实现为简单占位符。
        """
        # 此方法将在后续阶段通过LLM集成实现
        decision = {
            "action": available_actions[0]["id"] if available_actions else "no_action",
            "rationale": "Decision made based on great power interests",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("decision", f"Decided to take action: {decision['action']}")
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        作为大国做出响应

        大国从强势地位做出回应，考虑其响应的全球影响。

        Args:
            sender_id: 发送者ID
            message: 消息内容
            context: 附加上下文

        Returns:
            Dict[str, Any]: 响应结果

        Note:
            此方法将在后续阶段通过LLM集成实现。
            当前实现为简单占位符。
        """
        # 此方法将在后续阶段通过LLM集成实现
        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": "Response from great power",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("response", f"Responded to {sender_id}")
        return response


@dataclass
class SmallState(Agent):
    """
    小国代理类

    能力有限的国家代理。

    特征：
    - 能力层级通常为T3或T4
    - 行动选项有限
    - 需要战略性地做出选择
    - 避免与强国直接对抗

    决策逻辑：
    - 考虑能力差距
    - 寻求生存和发展的机会
    - 倾向于与大国合作或保持中立
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_zh: str,
        leadership_type: LeadershipType,
        capability: Optional[Capability] = None,
    ) -> None:
        """
        初始化小国代理

        Args:
            agent_id: 代理唯一标识符
            name: 英文名称
            name_zh: 中文名称
            leadership_type: 领导类型
            capability: 能力对象（可选，会自动创建默认值）
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            name_zh=name_zh,
            agent_type=AgentType.SMALL_STATE,
            leadership_type=leadership_type,
            capability=capability,
        )

    def decide(
        self,
        situation: Dict[str, Any],
        available_actions: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        作为小国做出决策

        小国选项有限，需要在选择上保持战略性。

        Args:
            situation: 当前情况描述
            available_actions: 可用行动列表
            context: 附加上下文

        Returns:
            Dict[str, Any]: 决策结果

        Note:
            此方法将在后续阶段通过LLM集成实现。
            当前实现为简单占位符。
        """
        # 此方法将在后续阶段通过LLM集成实现
        decision = {
            "action": available_actions[0]["id"] if available_actions else "no_action",
            "rationale": "Decision made with limited options",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("decision", f"Decided to take action: {decision['action']}")
        return decision

    def respond(
        self,
        sender_id: str,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        作为小国做出响应

        小国必须谨慎回应，以避免激怒更强大的国家。

        Args:
            sender_id: 发送者ID
            message: 消息内容
            context: 附加上下文

        Returns:
            Dict[str, Any]: 响应结果

        Note:
            此方法将在后续阶段通过LLM集成实现。
            当前实现为简单占位符。
        """
        # 此方法将在后续阶段通过LLM集成实现
        response = {
            "sender_id": self.agent_id,
            "receiver_id": sender_id,
            "content": "Response from small state",
            "leadership_influence": self.leadership_type.value,
        }
        self.add_history("response", f"Responded to {sender_id}")
        return response
