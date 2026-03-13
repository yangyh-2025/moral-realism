"""
智能体基类与实现 - 对应技术方案3.3.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

from config.validator import LeaderType
from entities.power_system import PowerMetrics, PowerTier

from enum import Enum


class AccessLevel(Enum):
    """记忆访问级别"""
    PUBLIC = "public"           # 公开信息，所有国家可见
    RESTRICTED = "restricted"   # 受限信息，仅相关国家可见
    PRIVATE = "private"          # 私有信息，仅自己可见（领导人决策理由）
    CLASSIFIED = "classified"    # 机密情报，仅限授权国家可见


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

        # 创建正式状态
        self.state = AgentState(
            agent_id=init_data["agent_id"],
            name=name,
            agent_type=self.__class__.__name__,
            region=init_data["region"],
            power_metrics=power_metrics,
            power_tier=self.power_tier,
            leader_type=leader_type,
            core_preferences=self._get_core_preferences(leader_type) if leader_type else {},
            behavior_boundaries=self._get_behavior_boundaries(leader_type) if leader_type else []
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
