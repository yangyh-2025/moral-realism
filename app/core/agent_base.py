"""
智能体核心模块
Agent Core Module

定义智能体的核心属性、行为能力、利益偏好，严格遵循学术模型假设2、3。
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from .klein_equation import PowerLevelEnum, calculate_klein_power, determine_power_level


class RegionEnum(str, Enum):
    """所属区域枚举"""
    AFRICA = "非洲"
    AMERICA = "美洲"
    ASIA = "亚洲"
    EUROPE = "欧洲"
    OCEANIA = "大洋洲"


class LeaderTypeEnum(str, Enum):
    """领导集体类型枚举"""
    KINGLY = "王道型"
    HEGEMONIC = "霸权型"
    TYRANICAL = "强权型"
    INEPT = "昏庸型"


class ActionConfig(BaseModel):
    """互动行为配置数据模型 - 对齐学术文档"""
    action_id: int
    action_name: str
    action_en_name: str
    action_category: str
    action_desc: str
    respect_sov: bool
    initiator_power_change: float
    target_power_change: float
    is_initiative: bool
    is_response: bool


class AgentBase(BaseModel):
    """
    智能体基类

    完全对齐学术模型设定，包含所有核心属性和行为能力。
    """

    # 基础属性
    agent_id: int = Field(description="智能体唯一ID")
    agent_name: str = Field(description="国家名称")
    region: RegionEnum = Field(description="所属区域")

    # 克莱因国力方程一级初始指标，仿真全程固定
    c_score: float = Field(
        ge=0,
        le=100,
        description="基本实体初始得分，克莱因官方满分100分"
    )
    e_score: float = Field(
        ge=0,
        le=200,
        description="经济实力初始得分，克莱因官方满分200分"
    )
    m_score: float = Field(
        ge=0,
        le=200,
        description="军事实力初始得分，克莱因官方满分200分"
    )
    s_score: float = Field(
        ge=0,
        le=2,
        description="战略目的对数，克莱因标准值0.5"
    )
    w_score: float = Field(
        ge=0,
        le=2,
        description="国家战略意志对数，克莱因标准值0.5"
    )

    # 只读自动计算字段（由model_post_init初始化）
    initial_total_power: float = Field(
        default=0.0,
        description="克莱因初始综合国力，自动计算"
    )
    current_total_power: float = Field(
        default=0.0,
        description="实时综合国力，每轮更新"
    )
    power_level: PowerLevelEnum = Field(
        default=PowerLevelEnum.SMALL_STATE,
        description="综合国力层级，自动计算，每轮更新"
    )

    # 领导集体类型（仅超级大国/大国可配置）
    leader_type: Optional[LeaderTypeEnum] = Field(
        default=None,
        description="仅超级大国/大国可设置，仿真全程固定"
    )

    # 国家利益偏好（由实力层级决定，与领导类型无关）
    national_interest: List[str] = Field(
        default_factory=list,
        description="由实力层级决定的国家利益偏好"
    )

    # 允许执行的行为列表（简化为区分发起/响应）
    allowed_actions: Dict[str, List[ActionConfig]] = Field(
        default_factory=lambda: {
            "all_allowed": [],
            "initiative": [],
            "response": []
        },
        description="允许执行的20项标准行为列表，按发起/响应分类"
    )

    @field_validator("leader_type")
    @classmethod
    def validate_leader_type_permission(cls, v: Optional[LeaderTypeEnum], info) -> Optional[LeaderTypeEnum]:
        """
        领导类型合法性校验：仅超级大国/大国可配置

        Args:
            v: 领导类型值
            info: 字段验证上下文

        Returns:
            验证后的领导类型值

        Raises:
            ValueError: 如果中小国家设置了领导类型
        """
        if v is not None:
            # 总是重新计算power_level以确保准确性
            data = info.data
            c_score = data.get("c_score", 0)
            e_score = data.get("e_score", 0)
            m_score = data.get("m_score", 0)
            s_score = data.get("s_score", 0)
            w_score = data.get("w_score", 0)

            power = calculate_klein_power(c_score, e_score, m_score, s_score, w_score)
            power_level = determine_power_level(power)

            if power_level not in [PowerLevelEnum.SUPERPOWER, PowerLevelEnum.GREAT_POWER]:
                raise ValueError(
                    "仅超级大国与大国可配置领导集体类型，中小国家禁止设置该字段"
                )

        return v

    def model_post_init(self, __context) -> None:
        """
        模型初始化后自动执行的计算

        计算初始综合国力、判定实力层级、映射国家利益、生成允许行为列表
        """
        # 计算初始综合国力
        self.initial_total_power = self._calculate_initial_power()

        # 初始化实时综合国力
        self.current_total_power = self.initial_total_power

        # 判定实力层级
        self.power_level = self._calculate_power_level(self.current_total_power)

        # 映射国家利益偏好
        self.national_interest = self._get_national_interest()

        # 生成允许执行的行为列表（简化为区分发起/响应，无限制过滤）
        self.allowed_actions = self._get_allowed_actions()

    def _calculate_initial_power(self) -> float:
        """
        计算初始综合国力

        Returns:
            综合国力得分
        """
        return calculate_klein_power(
            self.c_score,
            self.e_score,
            self.m_score,
            self.s_score,
            self.w_score
        )

    def _calculate_power_level(self, power: float) -> PowerLevelEnum:
        """
        根据综合国力判定实力层级

        Args:
            power: 综合国力得分

        Returns:
            实力层级枚举
        """
        return determine_power_level(power)

    def _get_national_interest(self) -> List[str]:
        """
        获取国家利益偏好（100%对齐学术模型）

        国家利益仅由实力层级决定，与领导类型无关。

        Returns:
            国家利益偏好列表
        """
        interest_mapping = {
            PowerLevelEnum.SUPERPOWER: [
                "争夺全球绝对领导权",
                "维护全球体系主导权",
                "巩固全球盟友/伙伴追随体系",
                "垄断国际规则制定权",
                "遏制新兴大国的系统性挑战"
            ],
            PowerLevelEnum.GREAT_POWER: [
                "提升全球话语权",
                "扩大国际影响力",
                "争取国际规则制定权",
                "保障本国核心安全与经济利益",
                "争夺区域/全球领导权"
            ],
            PowerLevelEnum.MIDDLE_POWER: [
                "维护区域影响力",
                "保障主权与领土安全",
                "实现经济稳定发展",
                "规避大国冲突波及",
                "在大国博弈中实现自身利益最大化"
            ],
            PowerLevelEnum.SMALL_STATE: [
                "保障国家生存与主权独立",
                "获取外部经济援助与安全保障",
                "避免卷入区域或全球冲突",
                "最大化生存安全收益"
            ]
        }

        return interest_mapping.get(self.power_level, [])

    def _get_allowed_actions(self) -> Dict[str, List[ActionConfig]]:
        """
        获取允许执行的行为列表（简化版本，无限制过滤）

        所有智能体都可以发起所有符合行为类型（发起/响应）的行为。

        Returns:
            包含all_allowed、initiative、response的字典
        """
        from .action_manager import get_all_actions

        all_actions = get_all_actions()

        # 区分发起类/响应类行为，无任何过滤
        return {
            "all_allowed": all_actions,
            "initiative": [action for action in all_actions if action.is_initiative],
            "response": [action for action in all_actions if action.is_response]
        }

    def update_power(self, power_change: float) -> None:
        """
        更新实时综合国力

        Args:
            power_change: 国力变化值（可正可负）
        """
        self.current_total_power += power_change
        self.power_level = self._calculate_power_level(self.current_total_power)

    def reset_to_initial(self) -> None:
        """
        重置到初始状态
        """
        self.current_total_power = self.initial_total_power
        self.power_level = self._calculate_power_level(self.current_total_power)

    def get_leader_type_rules(self) -> Dict[str, any]:
        """
        获取领导类型的行为规则（100%对齐学术模型）

        Returns:
            包含领导类型规则的字典
        """
        if self.leader_type is None:
            return {
                "type": "无领导类型",
                "interest_ordering": "国家利益优先",
                "strategy_preference": "生存与发展优先",
                "core_behavior_constraints": "无特殊约束"
            }

        rules_mapping = {
            LeaderTypeEnum.KINGLY: {
                "type": "王道型",
                "interest_ordering": "国家利益优先，坚守国际道义",
                "strategy_preference": "公平正义、言行一致、维护战略信誉、避免双重标准、不滥用强制手段",
                "core_behavior_constraints": "禁止执行所有不尊重主权的高烈度对抗行为，仅可执行尊重主权的合作类、外交类行为，不得偏离国家客观利益"
            },
            LeaderTypeEnum.HEGEMONIC: {
                "type": "霸权型",
                "interest_ordering": "自身国家利益绝对优先，兼顾道义工具性",
                "strategy_preference": "双重标准执行国际规范、通过规则构建获取超额利益、以自身利益为核心适用规则",
                "core_behavior_constraints": "禁止执行极端暴力与强制类行为，可执行双重标准的外交、经济类对抗行为，不得偏离国家客观利益"
            },
            LeaderTypeEnum.TYRANICAL: {
                "type": "强权型",
                "interest_ordering": "本国利益最大化，完全忽视道义",
                "strategy_preference": "以军事/强制手段为核心工具、无视国际规范、不重视战略信誉、不惜破坏现有秩序",
                "core_behavior_constraints": "仅禁止非常规大规模暴力行为，优先选择高烈度强制行为实现利益，不得偏离国家客观利益"
            },
            LeaderTypeEnum.INEPT: {
                "type": "昏庸型",
                "interest_ordering": "个人利益优先，可牺牲国家利益",
                "strategy_preference": "决策以决策者个人利益为核心，可制定损害国家利益的政策，无固定策略偏好",
                "core_behavior_constraints": "唯一可主动偏离国家客观利益的类型，无行为禁止约束，可执行20项行为集中的所有行为"
            }
        }

        return rules_mapping.get(self.leader_type, {})

    def to_dict(self) -> Dict[str, any]:
        """
        转换为字典格式

        Returns:
            智能体属性字典
        """
        return self.model_dump()
