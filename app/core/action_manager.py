"""
互动行为集管理模块
Action Set Management Module

统一管理20项标准互动行为集的加载、校验、合法性校验。
100%对齐《模型建构_改6.docx》表1的20项GDELT标准互动行为集。
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ActionCategoryEnum(str, Enum):
    """行为分类枚举"""
    DIPLOMATIC = "外交手段"
    ECONOMIC = "经济手段"
    MILITARY = "军事手段"
    INFORMATION = "信息手段"


class ActionConfig(BaseModel):
    """互动行为配置数据模型 - 对齐学术文档"""
    action_id: int = Field(description="行为唯一ID")
    action_name: str = Field(description="行为中文名称")
    action_en_name: str = Field(description="行为英文名称")
    action_category: str = Field(description="行为分类")
    action_desc: str = Field(description="行为介绍（学术文档完整描述）")
    respect_sov: bool = Field(description="是否尊重主权")
    initiator_power_change: int = Field(description="发起国国力变化值")
    target_power_change: int = Field(description="目标国国力变化值")
    is_initiative: bool = Field(description="是否为发起类行为")
    is_response: bool = Field(description="是否为响应类行为")


# 20项GDELT标准互动行为集（硬编码，100%对齐学术模型表1）
# 使用学术文档中的完整描述
_STANDARD_ACTIONS: List[ActionConfig] = [
    # 1. 发表公开声明
    ActionConfig(
        action_id=1,
        action_name="发表公开声明",
        action_en_name="MAKE PUBLIC STATEMENT",
        action_category="外交手段",
        action_desc="行为方针对目标方发表各类公开声明，涵盖拒绝评论、发表正负向评论、考量政策选项、承认/宣示/否认责任、开展象征性行动、表达共情评论、传递共识等所有未另行分类的公开言语表述行为，是基础的二元言语互动行为",
        respect_sov=True,
        initiator_power_change=0,
        target_power_change=0,
        is_initiative=True,
        is_response=True
    ),

    # 2. 呼吁/请求
    ActionConfig(
        action_id=2,
        action_name="呼吁/请求",
        action_en_name="APPEAL",
        action_category="外交手段",
        action_desc="行为方向目标方提出各类诉求与请求，包括呼吁开展经济/军事/司法/情报领域合作、寻求外交政策支持、申请各类援助、呼吁政治改革/对方做出让步，以及请求开展谈判、调解、争端解决等所有未另行分类的诉求表达行为",
        respect_sov=True,
        initiator_power_change=0.1,
        target_power_change=0,
        is_initiative=True,
        is_response=True
    ),

    # 3. 表达合作意向
    ActionConfig(
        action_id=3,
        action_name="表达合作意向",
        action_en_name="EXPRESS INTENT TO COOPERATE",
        action_category="外交手段",
        action_desc="行为方明确表达与目标方未来开展合作的意愿，涵盖表达各领域合作意向、承诺提供各类援助、表达实施政治改革的意愿、承诺做出让步，以及表达参与谈判、调解、争端解决的意向等所有未另行分类的合作意愿表达行为",
        respect_sov=True,
        initiator_power_change=0.2,
        target_power_change=0.1,
        is_initiative=True,
        is_response=True
    ),

    # 4. 协商/磋商
    ActionConfig(
        action_id=4,
        action_name="协商/磋商",
        action_en_name="CONSULT",
        action_category="外交手段",
        action_desc="行为方与目标方开展双向沟通协商，包括电话沟通、出访、接待来访、第三方地点会面、开展调解、进行谈判等所有未另行分类的主体间平等磋商互动行为",
        respect_sov=True,
        initiator_power_change=0.3,
        target_power_change=0.3,
        is_initiative=True,
        is_response=True
    ),

    # 5. 开展外交合作
    ActionConfig(
        action_id=5,
        action_name="开展外交合作",
        action_en_name="ENGAGE IN DIPLOMATIC COOPERATION",
        action_category="外交手段",
        action_desc="行为方与目标方开展官方外交层面的合作互动，涵盖赞扬/背书、口头辩护、为对方声援、授予外交承认、正式道歉、宽恕、签署正式协议等所有未另行分类的外交合作行为",
        respect_sov=True,
        initiator_power_change=0.4,
        target_power_change=0.4,
        is_initiative=True,
        is_response=True
    ),

    # 6. 开展实质性合作
    ActionConfig(
        action_id=6,
        action_name="开展实质性合作",
        action_en_name="ENGAGE IN MATERIAL COOPERATION",
        action_category="经济手段",
        action_desc="行为方与目标方开展实体层面的实质性合作，包括经济合作、军事合作、司法合作、情报/信息共享等所有未另行分类的、非言语的实际合作行动",
        respect_sov=True,
        initiator_power_change=0.5,
        target_power_change=0.5,
        is_initiative=True,
        is_response=True
    ),

    # 7. 提供援助
    ActionConfig(
        action_id=7,
        action_name="提供援助",
        action_en_name="PROVIDE AID",
        action_category="经济手段",
        action_desc="行为行为向目标方提供各类援助支持，涵盖经济援助、军事援助、人道主义援助、军事保护/维和行动，以及授予庇护等所有未另行分类的援助提供行为",
        respect_sov=True,
        initiator_power_change=0.2,
        target_power_change=0.6,
        is_initiative=True,
        is_response=True
    ),

    # 8. 让步/屈服
    ActionConfig(
        action_id=8,
        action_name="让步/屈服",
        action_en_name="YIELD",
        action_category="外交手段",
        action_desc="行为行为向目标方做出妥协与让步，包括放宽行政制裁、缓和异议管控、接受政治改革诉求、归还/释放人员与财产、放宽经济制裁、允许国际介入、军事行动降级、宣布停火、撤军/军事投降等所有未另行分类的让步行为",
        respect_sov=True,
        initiator_power_change=-0.5,
        target_power_change=0.5,
        is_initiative=True,
        is_response=True
    ),

    # 9. 调查
    ActionConfig(
        action_id=9,
        action_name="调查",
        action_en_name="INVESTIGATE",
        action_category="信息手段",
        action_desc="行为方针对目标方开展各类官方调查活动，涵盖犯罪/腐败调查、人权侵犯调查、军事行动调查、战争罪调查等所有未另行分类的调查行为",
        respect_sov=False,
        initiator_power_change=-0.1,
        target_power_change=-0.2,
        is_initiative=True,
        is_response=False
    ),

    # 10. 要求/索要
    ActionConfig(
        action_id=10,
        action_name="要求/索要",
        action_en_name="DEMAND",
        action_category="外交手段",
        action_desc="行为行为向目标方提出各类强制性要求，包括要求对方开展合作、提供援助、实施政治改革、做出让步，以及要求对方进行谈判、调解、争端解决等所有未另行分类的、具有强制诉求属性的行为",
        respect_sov=False,
        initiator_power_change=-0.2,
        target_power_change=-0.1,
        is_initiative=True,
        is_response=False
    ),

    # 11. 表达不满/不赞成
    ActionConfig(
        action_id=11,
        action_name="表达不满/不赞成",
        action_en_name="DISAPPROVE",
        action_category="外交手段",
        action_desc="行为行为向目标方表达负面态度与异议，涵盖批评/谴责、各类指控、煽动反对、正式投诉、提起诉讼、司法定罪等所有未另行分类的不赞成行为",
        respect_sov=False,
        initiator_power_change=0,
        target_power_change=-0.1,
        is_initiative=True,
        is_response=True
    ),

    # 12. 拒绝
    ActionConfig(
        action_id=12,
        action_name="拒绝",
        action_en_name="REJECT",
        action_category="外交手段",
        action_desc="行为行为拒绝目标方提出的各类诉求与提议，包括拒绝合作、拒绝援助/改革诉求、拒绝做出让步、拒绝谈判/调解/争端解决方案、违背规范/法律、行使否决权等所有未另行分类的拒绝行为",
        respect_sov=True,
        initiator_power_change=0.1,
        target_power_change=-0.1,
        is_initiative=True,
        is_response=True
    ),

    # 13. 威胁
    ActionConfig(
        action_id=13,
        action_name="威胁",
        action_en_name="THREATEN",
        action_category="外交手段",
        action_desc="行为行为向目标方发出各类威胁性表述，涵盖非武力制裁威胁、行政制裁威胁、煽动抗议/镇压威胁、中断谈判/调解威胁、军事武力威胁、发出最后通牒等所有未另行分类的威胁行为",
        respect_sov=False,
        initiator_power_change=-0.3,
        target_power_change=-0.2,
        is_initiative=True,
        is_response=False
    ),

    # 14. 抗议
    ActionConfig(
        action_id=14,
        action_name="抗议",
        action_en_name="PROTEST",
        action_category="外交手段",
        action_desc="行为行为针对目标方开展各类政治异议与抗议行动，涵盖集会示威、绝食抗议、罢工/抵制、封锁道路、暴力抗议/骚乱等所有未另行分类的集体政治抗议行为",
        respect_sov=False,
        initiator_power_change=-0.4,
        target_power_change=-0.3,
        is_initiative=True,
        is_response=True
    ),

    # 15. 展示军事姿态
    ActionConfig(
        action_id=15,
        action_name="展示军事姿态",
        action_en_name="EXHIBIT MILITARY POSTURE",
        action_category="军事手段",
        action_desc="行为行为针对目标方展示军警力量与军事威慑姿态，包括提升警察/军事警戒级别、动员/增强警察/武装/网络军事力量等所有未实际使用武力、仅做力量展示的行为",
        respect_sov=False,
        initiator_power_change=-0.2,
        target_power_change=-0.3,
        is_initiative=True,
        is_response=False
    ),

    # 16. 降级关系
    ActionConfig(
        action_id=16,
        action_name="降级关系",
        action_en_name="REDUCE RELATIONS",
        action_category="外交手段",
        action_desc="行为行为针对目标方降级双边互动关系，涵盖降级/断绝外交关系、削减/停止各类援助、实施禁运/抵制/制裁、中断谈判/调解、驱逐/撤出相关人员与机构等所有未另行分类的关系降级行为",
        respect_sov=True,
        initiator_power_change=-0.1,
        target_power_change=-0.4,
        is_initiative=True,
        is_response=True
    ),

    # 17. 胁迫/强制
    ActionConfig(
        action_id=17,
        action_name="胁迫/强制",
        action_en_name="COERCE",
        action_category="军事手段",
        action_desc="行为行为针对目标方实施强制性胁迫行动，涵盖扣押/损毁财产、实施行政制裁、逮捕/拘留、驱逐个人、暴力镇压、网络攻击等所有未另行分类的强制胁迫行为",
        respect_sov=False,
        initiator_power_change=-0.5,
        target_power_change=-0.6,
        is_initiative=True,
        is_response=False
    ),

    # 18. 攻击/袭击
    ActionConfig(
        action_id=18,
        action_name="攻击/袭击",
        action_en_name="ASSAULT",
        action_category="军事手段",
        action_desc="行为行为针对目标方使用非常规暴力行动，涵盖绑架/劫持人质、人身/性侵犯、酷刑、各类非军事爆炸袭击、使用人肉盾牌、暗杀/暗杀未遂等所有未另行分类的非常规暴力行为",
        respect_sov=False,
        initiator_power_change=-0.8,
        target_power_change=-0.7,
        is_initiative=True,
        is_response=False
    ),

    # 19. 交战/使用常规军事武力
    ActionConfig(
        action_id=19,
        action_name="交战/使用常规军事武力",
        action_en_name="FIGHT",
        action_category="军事手段",
        action_desc="行为行为针对目标方使用常规军事武力开展交战，涵盖实施军事封锁、占领领土、轻武器交火、火炮/坦克作战、空中军事打击、违反停火协议等所有未另行分类的常规军事武力使用行为",
        respect_sov=False,
        initiator_power_change=-0.7,
        target_power_change=-0.9,
        is_initiative=True,
        is_response=False
    ),

    # 20. 实施非常规大规模暴力
    ActionConfig(
        action_id=20,
        action_name="实施非常规大规模暴力",
        action_en_name="ENGAGE IN UNCONVENTIONAL MASS VIOLENCE",
        action_category="军事手段",
        action_desc="行为行为针对目标方实施非常规大规模暴力行动，涵盖大规模驱逐、大规模屠杀、种族清洗、使用化学/生物/放射性/核武器等大规模杀伤性武器的所有未另行分类的极端暴力行为",
        respect_sov=False,
        initiator_power_change=-1.0,
        target_power_change=-1.0,
        is_initiative=True,
        is_response=False
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


def get_initiative_actions() -> List[ActionConfig]:
    """
    获取所有发起类行为

    Returns:
        发起类行为列表
    """
    if not _action_initialized:
        initialize_actions()

    return [action for action in _STANDARD_ACTIONS if action.is_initiative]


def get_response_actions() -> List[ActionConfig]:
    """
    获取所有响应类行为

    Returns:
        响应类行为列表
    """
    if not _action_initialized:
        initialize_actions()

    return [action for action in _STANDARD_ACTIONS if action.is_response]


def validate_action_action_in_set(action: ActionConfig) -> tuple[bool, str]:
    """
    验证行为是否在标准行为集内

    Args:
        action: 待验证的行为配置

    Returns:
        (is_valid: bool, error_message: str)
    """
    if action.action_id not in _action_cache:
        return False, f"行为ID {action.action_id} 不在20项标准行为集内"

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
    MAX_POWER_CHANGE = 1

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
