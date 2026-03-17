"""
智能体基类与实现 - 对应技术方案3.3.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib
import time

from config.leader_types import LeaderType
from domain.power.power_metrics import PowerMetrics, PowerTier

from enum import Enum


class AccessLevel(Enum):
    """记忆访问级别"""
    PUBLIC = "public"           # 公开信息，所有国家可见
    RESTRICTED = "restricted"   # 受限信息，仅相关国家可见
    PRIVATE = "private"          # 私有信息，仅自己可见（领导人决策理由）
    CLASSIFIED = "classified"    # 机密情报，仅限授权国家可见


class DecisionPriority(Enum):
    """决策优先级"""
    EMERGENCY = 5  # 紧急，需要立即处理
    HIGH = 4       # 高优先级
    MEDIUM = 3     # 中等优先级
    LOW = 2        # 低优先级
    ROUTINE = 1    # 常规处理


class DecisionCache:
    """
    决策缓存 - 实现LRU缓存淘汰和TTL过期机制

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        初始化决策缓存

        Args:
            max_size: 缓存最大条目数（LRU淘汰阈值）
            ttl: 缓存生存时间（秒）
        """
        self._cache = {}           # context_hash -> decision
        self._timestamps = {}      # context_hash -> creation_time
        self._access_times = {}    # context_hash -> last_access_time
        self._agent_mapping = {}  # agent_id -> [context_hash1, context_hash2, ...]
        self.max_size = max_size
        self.ttl = ttl

    def _calculate_context_hash(self, context: Dict) -> str:
        """
        计算上下文哈希

        Args:
            context: 上下文字典

        Returns:
            SHA256哈希值
        """
        context_str = json.dumps(context, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(context_str.encode()).hexdigest()

    def _is_expired(self, context_hash: str) -> bool:
        """
        检查缓存是否过期

        Args:
            context_hash: 上下文哈希

        Returns:
            是否过期
        """
        if context_hash not in self._timestamps:
            return True
        return (time.time() - self._timestamps[context_hash]) > self.ttl

    def _evict_lru(self) -> None:
        """
        LRU缓存淘汰 - 移除最久未访问的条目
        """
        if not self._cache:
            return

        # 找到最久未访问的条目
        lru_hash = min(self._access_times, key=lambda k: self._access_times[k])

        # 从agent_mapping中移除
        for agent_id in self._agent_mapping:
            if lru_hash in self._agent_mapping[agent_id]:
                self._agent_mapping[agent_id].remove(lru_hash)
                if not self._agent_mapping[agent_id]:
                    del self._agent_mapping[agent_id]
                break

        # 移除条目
        del self._cache[lru_hash]
        del self._timestamps[lru_hash]
        del self._access_times[lru_hash]

    def cache_decision(self, context: Dict, decision: Dict, agent_id: str) -> None:
        """
        缓存决策

        Args:
            context: 上下文
            decision: 决策结果
            agent_id: 智能体ID（用于失效策略）
        """
        context_hash = self._calculate_context_hash(context)
        current_time = time.time()

        # 如果缓存已满，执行LRU淘汰
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        # 缓存决策
        self._cache[context_hash] = decision
        self._timestamps[context_hash] = current_time
        self._access_times[context_hash] = current_time

        # 更新agent_mapping
        if agent_id not in self._agent_mapping:
            self._agent_mapping[agent_id] = []
        if context_hash not in self._agent_mapping[agent_id]:
            self._agent_mapping[agent_id].append(context(context_hash))

    def get_cached_decision(self, context: Dict) -> Optional[Dict]:
        """
        获取缓存的决策

        Args:
            context: 上下文

        Returns:
            缓存的决策，如果不存在或已过期则返回None
        """
        context_hash = self._calculate_context_hash(context)

        # 检查是否过期
        if self._is_expired(context_hash):
            return None

        # 检查是否存在
        if context_hash not in self._cache:
            return None

        # 更新访问时间
        self._access_times[context_hash] = time.time()

        # 返回缓存的决策（深拷贝避免外部修改）
        return json.loads(json.dumps(self._cache[context_hash]))

    def invalidate(self, agent_id: str) -> None:
        """
        使特定智能体的缓存失效

        Args:
            agent_id: 智能体ID
        """
        if agent_id not in self._agent_mapping:
            return

        # 移除该智能体的所有缓存
        for context_hash in self._agent_mapping[agent_id]:
            if context_hash in self._cache:
                del self._cache[context_hash]
            if context_hash in self._timestamps:
                del self._timestamps[context_hash]
            if context_hash in self._access_times:
                del self._access_times[context_hash]

        del self._agent_mapping[agent_id]

    def clear_all(self) -> None:
        """清空所有缓存"""
        self._cache.clear()
        self._timestamps.clear()
        self._access_times.clear()
        self._agent_mapping.clear()

    def get_stats(self) -> Dict:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "agent_count": len(self._agent_mapping)
        }


class ConsistencyReport:
    """
    一致性报告

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        is_consistent: bool,
        issues: List[str] = None,
        confidence_score: float = 0.0
    ):
        self.is_consistent = is_consistent
        self.issues = issues if issues is not None else []
        self.confidence_score = confidence_score

    def add_issue(self, issue: str) -> None:
        """
        添加一致性问题

        Args:
            issue: 问题描述
        """
        self.issues.append(issue)
        self.is_consistent = False

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "is_consistent": self.is_consistent,
            "issues": self.issues,
            "confidence_score": self.confidence_score
        }


class AgentLearning:
    """
    智能体学习机制 - 记录决策结果并更新偏好

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, agent_id: str, max_outcomes: int = 1000):
        """
        初始化学习机制

        Args:
            agent_id: 智能体ID
            max_outcomes: 最大记录的结果数
        """
        self.agent_id = agent_id
        self._outcomes = []          # [(decision, outcome, timestamp), ...]
        self._preferences = {}        # preference_key -> score
        self.max_outcomes = max_outcomes

    def record_outcome(self, decision: Dict, outcome: Dict) -> None:
        """
        记录决策结果

        Args:
            decision: 决策
            outcome: 结果，应包含success和details字段
        """
        timestamp = datetime.now().isoformat()

        self._outcomes.append({
            "decision": decision,
            "outcome": outcome,
            "timestamp": timestamp
        })

        # 限制历史记录数量
        if len(self._outcomes) > self.max_outcomes:
            self._outcomes = self._outcomes[-self.max_outcomes:]

        # 如果结果成功，增强相关偏好
        if outcome.get("success", False):
            self._update_preferences_from_success(decision, outcome)

    def _update_preferences_from_success(self, decision: Dict, outcome: Dict) -> None:
        """
        从成功结果中更新偏好

        Args:
            decision: 决策
            outcome: 结果
        """
        # 提取决策类型
        decision_type = decision.get("type", "unknown")
        preference_key = f"decision_type:{decision_type}"

        # 增强偏好（使用指数加权平均）
        current_score = self._preferences.get(preference_key, 0.5)
        success_weight = outcome.get("success_weight", 0.1)
        new_score = current_score * 0.9 + success_weight * 0.1

        # 限制在0-1范围内
        self._preferences[preference_key] = max(0.0, min(1.0, new_score))

        # 更新目标智能体偏好
        if "target_agent" in decision:
            target_agent = decision["target_agent"]
            target_key = f"target_agent:{target_agent}"
            current_target_score = self._preferences.get(target_key, 0.5)
            self._preferences[target_key] = current_target_score * 0.9 + 0.05 * 0.1

    def update_preferences(self, feedback: Dict) -> None:
        """
        更新偏好

        Args:
            feedback: 反馈信息，包含preference_key和adjustment
        """
        preference_key = feedback.get("preference_key")
        adjustment = feedback.get("adjustment", 0.0)

        if preference_key is None:
            return

        current_score = self._preferences.get(preference_key, 0.5)
        new_score = current_score + adjustment

        # 限制在0-1范围内
        self._preferences[preference_key] = max(0.0, min(1.0, new_score))

    def get_learned_preferences(self) -> Dict[str, float]:
        """
        获取学习到的偏好

        Returns:
            偏好字典
        """
        return self._preferences.copy()

    def get_outcome_history(self, limit: int = 10) -> List[Dict]:
        """
        获取最近的结果历史

        Args:
            limit: 返回数量限制

        Returns:
            结果列表
        """
        return self._outcomes[-limit:]

    def get_success_rate(self, decision_type: str = None) -> float:
        """
        获取决策成功率

        Args:
            decision_type: 决策类型，None表示所有类型

        Returns:
            成功率（0-1）
        """
        if not self._outcomes:
            return 0.0

        filtered_outcomes = self._outcomes
        if decision_type:
            filtered_outcomes = [
                o for o in self._outcomes
                if o["decision"].get("type") == decision_type
            ]

        if not filtered_outcomes:
            return 0.0

        success_count = sum(
            1 for o in filtered_outcomes
            if o["outcome"].get("success", False)
        )

        return success_count / len(filtered_outcomes)


@dataclass
class AgentState:
    """
    智能体状态

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    agent_id: str
    name: str
    agent_type: str
    region: str

    # 实力属性
    power_metrics: PowerMetrics
    power_tier: PowerTier

    # 领导属性
    leader_type: Optional[LeaderType] = None
    core_preferences: Dict[str, float] = field(default_factory=dict)
    behavior_boundaries: List[str] = field(default_factory=list)

    # 统计数据
    decision_count: int = 0
    function_call_history: Dict[str, int] = field(default_factory=dict)
    strategic_reputation: float = 100.0  # 战略信誉度

    # 客观战略利益
    objective_interest: str = ""

    # 决策缓存和学习机制
    decision_cache: Optional[DecisionCache] = None
    learning: Optional[AgentLearning] = None


class BaseAgent(ABC):
    """
    智能体基类 - 支持两步初始化流程

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        region: str,
        power_metrics: PowerMetrics
    ):
        """
        第一步初始化：创建国家智能体的基本实例

        Args:
            agent_id: 智能体唯一ID（代表国家）
            name: 国家名称
            region: 国家所属区域
            power_metrics: 国家的实力指标数据
        """
        # 保存原始配置，等待实力层级计算后初始化状态
        self._init_config = {
            "agent_id": agent_id,
            "name": name,
            "region": region,
            "power_metrics": power_metrics,
            "leader_type": None  # 初始设为None，等待配置
        }

        # 临时状态占位
        self.state = None
        self.power_tier = None
        self._is_initialized = False

    def set_leader_type(self, leader_type: Optional[LeaderType]) -> None:
        """
        设置领导人类型（在国家实力层级确定后调用）

        Args:
            leader_type: 领导人类型
        """
        if self.power_tier is None:
            raise ValueError("必须先完成国家实力层级计算，才能设置领导人类型")

        if self._is_initialized:
            raise ValueError("智能体已完成初始化，无法再设置领导人类型")

        if self.power_tier in [PowerTier.SUPERPOWER, PowerTier.GREAT_POWER]:
            if leader_type is None:
                raise ValueError(
                    f"{self._init_config['name']}({self.power_tier.value})是超级大国或大国，"
                    "必须配置了导类型"
                )
            self._init_config["leader_type"] = leader_type
        elif self.power_tier in [PowerTier.MIDDLE_POWER, PowerTier.SMALL_POWER]:
            if leader_type is not None:
                raise ValueError(
                    f"{self._init_config['name']}({self.power_tier.value})是中等强国或小国，"
                    "不需要配置了导类型"
                )
            self._init_config["leader_type"] = None

    def complete_initialization(self) -> None:
        """
        完成最终初始化（在设置了导类型后调用）

        必须按顺序调用：
        1. __init__()
        2. calculate_power_tier()
        3. set_leader_type() (如需要)
        4. complete_initialization()
        """
        if self.power_tier is None:
            raise ValueError("必须先调用 calculate_power_tier() 计算实力层级")

        if self._is_initialized:
            raise ValueError("智能体已完成初始化")

        init_data = self._init_config
        power_metrics = init_data["power_metrics"]
        leader_type = init_data["leader_type"]
        name = init_data["name"]
        agent_id = init_data["agent_id"]

        # 创建决策缓存和学习机制
        decision_cache = DecisionCache(max_size=100, ttl=3600)
        learning = AgentLearning(agent_id=agent_id, max_outcomes=1000)

        # 创建正式状态
        self.state = AgentState(
            agent_id=agent_id,
            name=name,
            agent_type=self.__class__.__name__,
            region=init_data["region"],
            power_metrics=power_metrics,
            power_tier=self.power_tier,
            leader_type=leader_type,
            core_preferences=self._get_core_preferences(leader_type) if leader_type else {},
            behavior_boundaries=self._get_behavior_boundaries(leader_type) if leader_type else [],
            decision_cache=decision_cache,
            learning=learning
        )

        self._is_initialized = True

    @abstractmethod
    def _get_core_preferences(self, leader_type: Optional[LeaderType] = None) -> Dict[str, float]:
        """获取核心偏好"""
        pass

    @abstractmethod
    def _get_behavior_boundaries(self, leader_type: Optional[LeaderType] = None) -> List[str]:
        """获取行为边界"""
        pass

    def get_available_functions(self) -> List[Dict]:
        """获取可用函数列表"""
        # 基础行为选择集
        base_functions = [
            {"name": "military_exercise", "description": "进行军事演习"},
            {"name": "military_alliance", "description": "建立军事同盟"},
            {"name": "security_guarantee", "description": "提供安全保障承诺"},
            {"name": "free_trade_agreement", "description": "签署自贸协定"},
            {"name": "economic_sanctions", "description": "实施经济制裁"},
            {"name": "economic_aid", "description": "提供经济援助"},
            {"name": "international_norm_proposal", "description": "提出国际规范"},
            {"name": "treaty_signing", "description": "签署国际条约"},
            {"name": "treaty_withdrawal", "description": "退出国际条约"},
            {"name": "diplomatic_visit", "description": "外交访问"},
            {"name": "upgrade_alliance", "description": "升级盟友关系"},
            {"name": "diplomatic_recognition", "description": "外交承认/断交"},
            {"name": "use_military_force", "description": "率先使用武力"},
            {"name": "unilateral_sanctions", "description": "单边制裁"},
            {"name": "unilateral_treaty_withdrawal", "description": "单方面毁约"},
            {"name": "international_mediation", "description": "主动开展国际调停"}
        ]
        return base_functions

    def get_prohibited_functions(self) -> Set[str]:
        """获取禁止使用的函数"""
        from core.validator import RuleValidator

        if not self.state or not self.state.leader_type:
            return set()

        if self.state.leader_type == LeaderType.WANGDAO:
            return RuleValidator.WANGDAO_FORBIDDEN
        elif self.state.leader_type == LeaderType.BAQUAN:
            return RuleValidator.BAQUAN_FORBIDDEN
        elif self.state.leader_type == LeaderType.QIANGQUAN:
            return RuleValidator.QIANGQUAN_FORBIDDEN
        else:  # HUNYONG
            return set()

    def get_state_dict(self) -> Dict:
        """获取状态字典"""
        return {
            "agent_id": self.state.agent_id,
            "name": self.state.name,
            "agent_type": self.state.agent_type,
            "region": self.state.region,
            "power_tier": self.state.power_tier.value,
            "comprehensive_power": self.state.power_metrics.calculate_comprehensive_power(),
            "leader_type": self.state.leader_type.value if self.state.leader_type else None,
            "decision_count": self.state.decision_count,
            "strategic_reputation": self.state.strategic_reputation
        }

    def evaluate_decision_priority(self, situation: Dict) -> DecisionPriority:
        """
        评估决策优先级

        Args:
            situation: 当前局势，包含威胁、机会、时间敏感度等信息

        Returns:
            决策优先级
        """
        # 检查紧急威胁
        threat_level = situation.get("threat_level", 0.0)
        if threat_level >= 0.9:
            return DecisionPriority.EMERGENCY

        # 检查重大威胁
        if threat_level >= 0.7:
            return DecisionPriority.HIGH

        # 检查重要机会
        opportunity_level = situation.get("opportunity_level", 0.0)
        if opportunity_level >= 0.8:
            return DecisionPriority.HIGH

        # 检查时间敏感度
        time_sensitivity = situation.get("time_sensitivity", 0.0)
        if time_sensitivity >= 0.7:
            return DecisionPriority.MEDIUM

        # 检查常规机会
        if opportunity_level >= 0.5:
            return DecisionPriority.MEDIUM

        # 检查中等威胁
        if threat_level >= 0.4:
            return DecisionPriority.LOW

        # 默认常规优先级
        return DecisionPriority.ROUTINE

    def check_decision_consistency(
        self,
        new_decision: Dict,
        recent_decisions: List[Dict]
    ) -> ConsistencyReport:
        """
        检查决策一致性

        Args:
            new_decision: 新决策
            recent_decisions: 近期决策列表

        Returns:
            一致性报告
        """
        report = ConsistencyReport(is_consistent=True, confidence_score=1.0)

        if not recent_decisions:
            return report

        new_decision_type = new_decision.get("type")
        new_target = new_decision.get("target_agent")

        # 检查与近期决策的冲突
        for i, old_decision in enumerate(recent_decisions[-5:]):  # 只检查最近5个决策
            old_decision_type = old_decision.get("type")
            old_target = old_decision.get("target_agent")

            # 检查目标冲突
            if new_target and old_target:
                if new_target == old_target:
                    # 同一目标的决策类型冲突检测
                    conflicting_pairs = [
                        ("economic_aid", "economic_sanctions"),
                        ("upgrade_alliance", "diplomatic_recognition"),
                        ("treaty_signing", "treaty_withdrawal")
                    ]

                    for type1, type2 in conflicting_pairs:
                        if (new_decision_type == type1 and old_decision_type == type2) or \
                           (new_decision_type == type2 and old_decision_type == type1):
                            report.add_issue(
                                f"与最近第{len(recent_decisions)-i}个决策冲突："
                                f"对同一目标{new_target}同时采取{type1}和{type2}"
                            )
                            report.confidence_score -= 0.2

        # 确保置信度不低于0
        report.confidence_score = max(0.0, report.confidence_score)

        return report

    def get_decision_cache(self) -> Optional[DecisionCache]:
        """
        获取决策缓存

        Returns:
            决策缓存实例
        """
        return self.state.decision_cache if self.state else None

    def get_learning(self) -> Optional[AgentLearning]:
        """
        获取学习机制

        Returns:
            学习机制实例
        """
        return self.state.learning if self.state else None
