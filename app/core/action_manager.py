"""
互动行为集管理模块
Action Set Management Module

统一管理20项标准互动行为集的加载、权限校验、行为过滤、合法性校验。
100%对齐《模型建构_改了6.docx》表1的20项GDELT标准互动行为集。
"""

from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field

from .klein_equation import PowerLevelEnum
from .agent_base import LeaderTypeEnum


class ActionCategoryEnum(str, Enum):
    """行为分类枚举"""
    DIPLOMATIC = "外交手段"
    ECONOMIC = "经济手段"
    MILITARY = "军事手段"
    INFORMATION = "信息手段"


class ActionConfig(BaseModel):
    """互动行为配置数据模型"""
    action_id: int = Field(description="行为唯一ID")
    action_name: str = Field(description="行为中文名称")
    action_en_name: str = Field(description="行为英文名称")
    action_category: str = Field(description="行为分类")
    action_desc: str = Field(description="行为介绍")
    respect_sov: bool = Field(description="是否尊重主权")
    initiator_power_change: int = Field(description="发起国国力变化值")
    target_power_change: int = Field(description="目标国国力变化值")
    is_initiative: bool = Field(description="是否为发起类行为")
    is_response: bool = Field(description="是否为响应类行为")
    allowed_initiator_level: List[PowerLevelEnum] = Field(description="允许发起该行为的实力层级")
    allowed_responder_level: List[PowerLevelEnum] = Field(description="允许响应该行为的实力层级")
    forbidden_leader_type: List[LeaderTypeEnum] = Field(description="禁止执行该行为的领导类型")


# 20项GDELT标准互动行为集（硬编码，100%对齐学术模型表1）
_STANDARD_ACTIONS: List[ActionConfig] = [
    # 1. 发表公开声明
    ActionConfig(
        action_id=1,
        action_name="发表公开声明",
        action_en_name="MAKE PUBLIC STATEMENT",
        action_category="外交手段",
        action_desc="通过官方渠道发表公开声明或立场表达",
        respect_sov=True,
        initiator_power_change=0,
        target_power_change=0,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 2. 呼吁/请求
    ActionConfig(
        action_id=2,
        action_name="呼吁/请求",
        action_en_name="APPEAL",
        action_category="外交手段",
        action_desc="向其他国家发出呼吁或请求",
        respect_sov=True,
        initiator_power_change=1,
        target_power_change=0,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 3. 表达合作意向
    ActionConfig(
        action_id=3,
        action_name="表达合作意向",
        action_en_name="EXPRESS INTENT TO COOPERATE",
        action_category="外交手段",
        action_desc="明确表达与目标国开展合作的意向",
        respect_sov=True,
        initiator_power_change=2,
        target_power_change=1,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 4. 协商/磋商
    ActionConfig(
        action_id=4,
        action_name="协商/磋商",
        action_en_name="CONSULT",
        action_category="外交手段",
        action_desc="与目标国开展正式协商或磋商",
        respect_sov=True,
        initiator_power_change=3,
        target_power_change=3,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 5. 开展外交合作
    ActionConfig(
        action_id=5,
        action_name="开展外交合作",
        action_en_name="ENGAGE IN DIPLOMATIC COOPERATION",
        action_category="外交手段",
        action_desc="与目标国建立或深化外交合作关系",
        respect_sov=True,
        initiator_power_change=4,
        target_power_change=4,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 6. 开展实质性合作
    ActionConfig(
        action_id=6,
        action_name="开展实质性合作",
        action_en_name="ENGAGE IN MATERIAL COOPERATION",
        action_category="经济手段",
        action_desc="与目标国开展经济、技术等实质性合作",
        respect_sov=True,
        initiator_power_change=5,
        target_power_change=5,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 7. 提供援助
    ActionConfig(
        action_id=7,
        action_name="提供援助",
        action_en_name="PROVIDE AID",
        action_category="经济手段",
        action_desc="向目标国提供经济、人道主义或技术援助",
        respect_sov=True,
        initiator_power_change=2,
        target_power_change=6,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 8. 让步/屈服
    ActionConfig(
        action_id=8,
        action_name="让步/屈服",
        action_en_name="YIELD",
        action_category="外交手段",
        action_desc="在争议中向目标国做出让步或屈服",
        respect_sov=True,
        initiator_power_change=-5,
        target_power_change=5,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 9. 调查
    ActionConfig(
        action_id=9,
        action_name="调查",
        action_en_name="INVESTIGATE",
        action_category="信息手段",
        action_desc="对目标国或其行为进行调查",
        respect_sov=False,
        initiator_power_change=-1,
        target_power_change=-2,
        is_initiative=True,
        is_response=False,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY]
    ),

    # 10. 要求/索要
    ActionConfig(
        action_id=10,
        action_name="要求/索要",
        action_en_name="DEMAND",
        action_category="外交手段",
        action_desc="向目标国提出明确要求或索要",
        respect_sov=False,
        initiator_power_change=-2,
        target_power_change=-1,
        is_initiative=True,
        is_response=False,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY]
    ),

    # 11. 表达不满/不赞成
    ActionConfig(
        action_id=11,
        action_name="表达不满/不赞成",
        action_en_name="DISAPPROVE",
        action_category="外交手段",
        action_desc="公开表达对目标国行为的不满或不赞成",
        respect_sov=False,
        initiator_power_change=0,
        target_power_change=-1,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 12. 拒绝
    ActionConfig(
        action_id=12,
        action_name="拒绝",
        action_en_name="=",
        action_category="外交手段",
        action_desc="拒绝目标国的提议或要求",
        respect_sov=True,
        initiator_power_change=1,
        target_power_change=-1,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 13. 威胁
    ActionConfig(
        action_id=13,
        action_name="威胁",
        action_en_name="THREATEN",
        action_category="外交手段",
        action_desc="向目标国发出威胁性言论或信号",
        respect_sov=False,
        initiator_power_change=-3,
        target_power_change=-2,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY]
    ),

    # 14. 抗议
    ActionConfig(
        action_id=14,
        action_name="抗议",
        action_en_name="PROTEST",
        action_category="外交手段",
        action_desc="对目标国行为正式提出抗议",
        respect_sov=False,
        initiator_power_change=-4,
        target_power_change=-3,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY]
    ),

    # 15. 展示军事姿态
    ActionConfig(
        action_id=15,
        action_name="展示军事姿态",
        action_en_name="EXHIBIT MILITARY POSTURE",
        action_category="军事手段",
        action_desc="通过军事演习或部署展示军事实力",
        respect_sov=False,
        initiator_power_change=-2,
        target_power_change=-3,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY]
    ),

    # 16. 降级关系
    ActionConfig(
        action_id=16,
        action_name="降级关系",
        action_en_name="REDUCE RELATIONS",
        action_category="外交手段",
        action_desc="降低与目标国的外交关系级别",
        respect_sov=True,
        initiator_power_change=-1,
        target_power_change=-4,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[]
    ),

    # 17. 胁迫/强制
    ActionConfig(
        action_id=17,
        action_name="胁迫/强制",
        action_en_name="COERCE",
        action_category="军事手段",
        action_desc="通过压力或强制手段迫使目标国服从",
        respect_sov=False,
        initiator_power_change=-5,
        target_power_change=-6,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY, LeaderTypeEnum.HEGEMONIC]
    ),

    # 18. 攻击/袭击
    ActionConfig(
        action_id=18,
        action_name="攻击/袭击",
        action_en_name="ASSAULT",
        action_category="军事手段",
        action_desc="对目标国发动攻击或军事袭击",
        respect_sov=False,
        initiator_power_change=-8,
        target_power_change=-7,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY, LeaderTypeEnum.HEGEMONIC]
    ),

    # 19. 交战/使用常规军事武力
    ActionConfig(
        action_id=19,
        action_name="交战/使用常规军事武力",
        action_en_name="FIGHT",
        action_category="军事手段",
        action_desc="与目标国发生交战或使用常规军事武力",
        respect_sov=False,
        initiator_power_change=-7,
        target_power_change=-9,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY, LeaderTypeEnum.HEGEMONIC]
    ),

    # 20. 实施非常规大规模暴力
    ActionConfig(
        action_id=20,
        action_name="实施非常规大规模暴力",
        action_en_name="ENGAGE IN UNCONVENTIONAL MASS VIOLENCE",
        action_category="军事手段",
        action_desc="对目标国实施非常规大规模暴力行动",
        respect_sov=False,
        initiator_power_change=-10,
        target_power_change=-10,
        is_initiative=True,
        is_response=True,
        allowed_initiator_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER
        ],
        allowed_responder_level=[
            PowerLevelEnum.SUPERPOWER,
            PowerLevelEnum.GREAT_POWER,
            PowerLevelEnum.MIDDLE_POWER,
            PowerLevelEnum.SMALL_STATE
        ],
        forbidden_leader_type=[LeaderTypeEnum.KINGLY, LeaderTypeEnum.HEGEMONIC, LeaderTypeEnum.TYRANICAL]
    )
]


# 行为缓存
_action_cache: Dict[int, ActionConfig] = {}
_action_initialized = False


def initialize_actions() -> None:
    """
    初始化行为集缓存

    将20项标准互动行为集加载到内存缓存中
    """
    global _action_cache, _action_initialized

    if _action_initialized:
        return

    _action_cache = {action.action_id: action for action in _STANDARD_ACTIONS}
    _action_initialized = True


def get_all_actions() -> List[ActionConfig]:
    """
    获取所有互动行为

    Returns:
        20项标准互动行为列表
    """
    if not _action_initialized:
        initialize_actions()

    return list(_action_cache.values())


def get_action_by_id(action_id: int) -> Optional[ActionConfig]:
    """
    根据行为ID获取行为配置

    Args:
        action_id: 行为ID

    Returns:
        行为配置对象，不存在则返回None
    """
    if not _action_initialized:
        initialize_actions()

    return _action_cache.get(action_id)


def get_action_by_name(action_name: str) -> Optional[ActionConfig]:
    """
    根据行为名称获取行为配置

    Args:
        action_name: 行为中文名称或英文名称

    Returns:
        行为配置对象，不存在则返回None
    """
    if not _action_initialized:
        initialize_actions()

    for action in _action_cache.values():
        if action.action_name == action_name or action.action_en_name == action_name.upper():
            return action

    return None


def filter_actions_by_power_level(
    power_level: PowerLevelEnum,
    leader_type: Optional[LeaderTypeEnum] = None
) -> Dict[str, List[ActionConfig]]:
    """
    根据实力层级和领导类型过滤行为

    Args:
        power_level: 实力层级
        leader_type: 领导类型（可选）

    Returns:
        包含all_allowed、initiative、response的字典
    """
    if not _action_initialized:
        initialize_actions()

    # 按实力层级过滤发起权限
    level_filtered = [
        action for action in _STANDARD_ACTIONS
        if power_level in action.allowed_initiator_level
    ]

    # 按领导类型过滤禁止行为
    if leader_type is not None:
        leader_filtered = [
            action for action in level_filtered
            if leader_type not in action.forbidden_leader_type
        ]
    else:
        leader_filtered = level_filtered

    # 区分发起类/响应类行为
    return {
        "all_allowed": leader_filtered,
        "initiative": [action for action in leader_filtered if action.is_initiative],
        "response": [action for action in leader_filtered if action.is_response]
    }


def validate_action_permission(
    action: ActionConfig,
    power_level: PowerLevelEnum,
    leader_type: Optional[LeaderTypeEnum] = None,
    is_initiative: bool = True
) -> tuple[bool, str]:
    """
    验证行为执行权限

    Args:
        action: 待验证的行为配置
        power_level: 智能体实力层级
        leader_type: 智能体领导类型（可选）
        is_initiative: 是否为发起类行为

    Returns:
        (is_valid: bool, error_message: str)
    """
    # 验证行为是否在标准集内
    if action.action_id not in _action_cache:
        return False, f"行为ID {action.action_id} 不在标准互动行为集内"

    # 验证实力层级权限
    if is_initiative:
        allowed_levels = action.allowed_initiator_level
    else:
        allowed_levels = action.allowed_responder_level

    if power_level not in allowed_levels:
        level_str = "发起" if is_initiative else "响应"
        return False, f"实力层级 {power_level.value} 不允许{level_str}该行为"

    # 验证领导类型约束
    if leader_type is not None and leader_type in action.forbidden_leader_type:
        return False, f"领导类型 {leader_type.value} 禁止执行该行为"

    return True, ""


def validate_action_power_change(action: ActionConfig) -> tuple[bool, str]:
    """
    验证行为国力变化值的合法性

    硬约束：单次行为国力变化绝对值 ≤ 10分

    Args:
        action: 待验证的行为配置

    Returns:
        (is_valid: bool, error_message: str)
    """
    MAX_POWER_CHANGE = 10

    errors = []

    if abs(action.initiator_power_change) > MAX_POWER_CHANGE:
        errors.append(
            f"发起国国力变化值 {action.initiator_power_change} 超出限制（绝对值 ≤ {MAX_POWER_CHANGE}）"
        )

    if abs(action.target_power_change) > MAX_POWER_CHANGE:
        errors.append(
            f"目标国国力变化值 {action.target_power_change} 超出限制（绝对值 ≤ {MAX_POWER_CHANGE}）"
        )

    if errors:
        return False, "; ".join(errors)

    return True, ""


def get_action_statistics() -> Dict[str, any]:
    """
    获取行为集统计信息

    Returns:
        统计信息字典
    """
    if not _action_initialized:
        initialize_actions()

    total_actions = len(_STANDARD_ACTIONS)
    initiative_actions = sum(1 for action in _STANDARD_ACTIONS if action.is_initiative)
    response_actions = sum(1 for action in _STANDARD_ACTIONS if action.is_response)
    respect_sov_actions = sum(1 for action in _STANDARD_ACTIONS if action.respect_sov)

    category_stats = {}
    for action in _STANDARD_ACTIONS:
        category = action.action_category
        category_stats[category] = category_stats.get(category, 0) + 1

    return {
        "total_actions": total_actions,
        "initiative_actions": initiative_actions,
        "response_actions": response_actions,
        "respect_sov_actions": respect_sov_actions,
        "category_distribution": category_stats
    }
