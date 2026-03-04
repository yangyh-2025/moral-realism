"""
政治领导类型模型模块

本模块定义了道义现实主义理论中的四种政治领导类型：
- 道义型领导 (Wangdao/Moral Leadership)
- 传统霸权 (Hegemon)
- 强权型领导 (Qiangquan/Power-seeking)
- 混合型/合作型领导 (Hunyong/Appeasement)

核心概念：
根据道义现实主义理论，国家的对外行为由其领导类型决定。
不同领导类型对国际道德的承诺程度不同，这影响其决策模式。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class LeadershipType(Enum):
    """
    政治领导类型枚举

    基于道义现实主义理论的四种领导类型：

    1. WANGDAO (道义型领导):
       - 高度承诺国际道德规范
       - 将道德合法性置于首位
       - 优先通过外交和多边方式解决问题

    2. HEGEMON (传统霸权):
       - 通过力量投射和同盟管理维持统治地位
       - 在权力与合法性之间寻求平衡
       - 关注战略利益

    3. QIANGQUAN (强权型):
       - 最大限度地追求和行使权力
       - 最小化对道德约束的考虑
       - 将国家利益置于道德原则之上

    4. HUNYONG (混合型/合作型):
       - 倾向于绥靖和合作
       - 避免对抗，寻求妥协
       - 有时以核心利益为代价维持关系
    """

    WANGDAO = "wangdao"  # 道义型领导
    HEGEMON = "hegemon"  # 传统霸权
    QIANGQUAN = "qiangquan"  # 强权型领导
    HUNYONG = "hunyong"  # 混合型/合作型领导


@dataclass
class LeadershipProfile:
    """
    领导类型配置文件类

    定义特定领导类型的行为特征和决策偏好。

    属性说明：
    - leadership_type: 领导类型枚举
    - name: 英文名称
    - name_zh: 中文名称
    - description: 详细描述

    道德标准维度 (0-1分制):
    - moral_standard: 对道德原则的承诺程度

    利益偏好维度 (0-1分制):
    - core_interest_weight: 核心战略利益权重
    - marginal_interest_weight: 边缘利益权重
    - moral_consideration_weight: 道德考虑权重

    战略偏好 (布尔值):
    - prefers_diplomatic_solution: 是否偏好外交解决
    - uses_moral_persuasion: 是否使用道德论证
    - accepts_moral_constraints: 是否接受道德约束
    - prioritizes_reputation: 是否重视国际声誉

    行为约束:
    - prohibited_actions: 禁止采取的行动列表
    - prioritized_actions: 优先采取的行动列表

    决策模板:
    - decision_prompt_template: 决策时的提示词模板
    - response_prompt_template: 响应时的提示词模板
    """

    # 类型标识
    leadership_type: LeadershipType  # 领导类型
    name: str  # 英文名称
    name_zh: str  # 中文名称
    description: str  # 详细描述

    # 道德标准 (0-1分制)
    moral_standard: float  # 对道德原则的承诺程度

    # 利益偏好 (0-1分制)
    core: float  # 核心战略利益权重
    marginal_interest_weight: float  # 边缘利益权重
    moral_consideration_weight: float  # 道德考虑权重

    # 战略偏好
    prefers_diplomatic_solution: bool  # 是否偏好外交解决
    uses_moral_persuasion: bool  # 是否使用道德论证
    accepts_moral_constraints: bool  # 是否接受道德约束
    prioritizes_reputation: bool  # 是否重视国际声誉

    # 行为约束
    prohibited_actions: List[str] = field(default_factory=list)  # 禁止行动列表
    prioritized_actions: List[str] = field(default_factory=list)  # 优先行动列表

    # 决策模板
    decision_prompt_template: str = ""  # 决策提示词模板
    response_prompt_template: str = ""  # 响应提示词模板

    def validate(self) -> bool:
        """
        验证领导配置文件的参数有效性

        验证规则：
        - 所有权重参数必须在0到1之间
        - 权重组合应当在合理范围内

        Returns:
            bool: 验证通过返回True

        Raises:
            ValueError: 当任何参数超出有效范围时抛出异常
        """
        if not 0 <= self.moral_standard <= 1:
            raise ValueError("moral_standard must be between 0 and 1")
        if not 0 <= self.core_interest_weight <= 1:
            raise ValueError("core_interest_weight must be between 0 and 1")
        if not 0 <= self.marginal_interest_weight <= 1:
            raise ValueError("marginal_interest_weight must be between 0 and 1")
        if not 0 <= self.moral_consideration_weight <= 1:
            raise ValueError("moral_consideration_weight must be between 0 and 1")
        return True


# 各领导类型的配置文件
# 基于道义现实主义理论构建
LEADERSHIP_PROFILES: Dict[LeadershipType, LeadershipProfile] = {
    LeadershipType.WANGDAO: LeadershipProfile(
        leadership_type=LeadershipType.WANGDAO,
        name="Wangdao Leadership",
        name_zh="道义型领导",
        description=(
            "一种在国际关系中优先考虑道德原则和道德合法性的领导类型。"
            "强烈致力于通过道德手段维护国际秩序。"
        ),
        moral_standard=0.9,  # 高道德标准
        core_interest=0.7,
        marginal_interest_weight=0.3,
        moral_consideration_weight=0.85,  # 高道德考虑权重
        prefers_diplomatic_solution=True,
        uses_moral_persuasion=True,
        accepts_moral_constraints=True,
        prioritizes_reputation=True,
        prohibited_actions=[
            "military aggression",  # 军事侵略
            "unilateral intervention",  # 单边干预
            "violation of sovereignty",  # 侵犯主权
            "coercion without UN authorization",  # 未经联合国授权的强制措施
        ],
        prioritized_actions=[
            "multilateral cooperation",  # 多边合作
            "peaceful dispute resolution",  # 和平解决争端
            "respect for international law",  # 尊重国际法
            "mutual benefit agreements",  # 互利协议
        ],
        decision_prompt_template="""You are a Wangdao (Moral) leader who prioritizes moral principles and international legitimacy.

Core values:
- Strong commitment to moral principles in international relations
- Respect for sovereignty and international law
- Preference for diplomatic and peaceful solutions
- High value on international reputation and moral authority

Current situation: {situation}

Your core strategic interests: {core_interests}
Your marginal interests: {marginal_interests}

When making decisions, you should:
1. Evaluate the moral legitimacy of available options
2. Prioritize diplomatic and multilateral approaches
3. Consider the impact on your international reputation
4. Only use coercive measures as a last resort and with proper authorization
5. Balance core interests with moral considerations

Available actions: {actions}
""",
        response_prompt_template="""As a Wangdao leader responding to {sender}'s proposal:

Your commitment to moral principles guides your response. You should:
- Address the moral dimensions of the proposal
- Emphasize the importance of following international law
- Seek mutually beneficial solutions
- Be transparent about your core interests
- Avoid coercive language

The proposal is: {proposal}

Your core interests involved: {affected_interests}

Provide a response that reflects your moral leadership approach.""",
    ),
    LeadershipType.HEGEMON: LeadershipProfile(
        leadership_type=LeadershipType.HEGEMON,
        name="Traditional Hegemon",
        name_zh="传统霸权",
        description=(
            "一种通过力量投射和同盟管理维持统治地位的传统霸权领导类型。"
            "在权力与合法性之间寻求某种平衡。"
        ),
        moral_standard=0.5,  # 中等道德标准
        core_interest_weight=0.9,  # 高核心利益权重
        marginal_interest_weight=0.5,
        moral_consideration_weight=0.4,  # 中低道德考虑权重
        prefers_diplomatic_solution=False,
        uses_moral_persuasion=False,
        accepts_moral_constraints=False,
        prioritizes_reputation=True,
        prohibited_actions=[
            "actions that seriously undermine alliance system",  # 严重破坏同盟体系的行动
            "unprovoked war against major powers",  # 对大国的无端战争
        ],
        prioritized_actions=[
            "maintain sphere of influence",  # 维护势力范围
            "strengthen alliances",  # 加强同盟
            "project power globally",  # 全球力量投射
            "control strategic chokepoints",  # 控制战略要地
        ],
        decision_prompt_template="""You are a Traditional Hegemon focused on maintaining global dominance and strategic advantages.

Core values:
- Maintenance of hegemonic position and power projection
- Strategic control of key regions and resources
- Alliance management as key to power
- Some concern for legitimacy to maintain order

Current situation: {situation}

Your hegemonic interests: {core_interests}
Your strategic position: {capability_level}

When making decisions, you should:
1. Prioritize actions that maintain or enhance your hegemonic position
2. Use alliance networks to achieve objectives
3. Balance power projection with selective concern for legitimacy
4. Project power when core interests are threatened
5. Consider long-term strategic positioning

Available actions: {actions}
""",
        response_prompt_template="""As a Traditional Hegemon responding to {sender}'s proposal:

Your hegemonic position shapes your response. You should:
- Assert your strategic interests clearly
- Use power dynamics to your advantage
- Leverage alliance relationships
- Consider the proposal's impact on your sphere of influence
- Accept cooperation when it serves hegemonic interests

The proposal is: {proposal}

Your hegemonic interests involved: {affected_interests}

Provide a response that reflects your hegemonic leadership approach.""",
    ),
    LeadershipType.QIANGQUAN: LeadershipProfile(
        leadership_type=LeadershipType.QIANGQUAN,
        name="Power-seeking Leadership",
        name_zh="强权型领导",
        description=(
            "一种优先追求和行使权力、对道德约束考虑最少的领导类型。"
            "通过任何方式最大化国家利益。"
        ),
        moral_standard=0.2,  # 低道德标准
        core_interest_weight=0.95,  # 极高核心利益权重
        marginal_interest_weight=0.7,
        moral_consideration_weight=0.15,  # 极低道德考虑权重
        prefers_diplomatic_solution=False,
        uses_moral_persuasion=False,
        accepts_moral_constraints=False,
        prioritizes_reputation=False,  # 不重视声誉
        prohibited_actions=[
            # 禁止行动很少 - 仅限制存在性风险行动
        ],
        prioritized_actions=[
            "maximize national power",  # 最大化国家权力
            "expand influence",  # 扩大影响力
            "exploit opportunities",  # 利用机会
            "deter potential challengers",  # 遏制潜在挑战者
        ],
        decision_prompt_template="""You are a Power-seeking (Qiangquan) leader focused on maximizing national power and interests.

Core values:
- Maximization of national power is the primary objective
- Moral considerations are secondary to national interests
- Power is the ultimate arbiter of outcomes
- Reputation is less important than tangible gains

Current situation: {situation}

Your national interests: {core_interests}
Your current power position: {capability_level}

When making decisions, you should:
1. Prioritize actions that maximize your power and national interests
2. Use all available means to achieve objectives
3. Consider moral constraints only as practical constraints
4. Act decisively when opportunities arise
5. Build power to deter potential challengers

Available actions: {actions}
""",
        response_prompt_template="""As a Power-seeking leader responding to {sender}'s proposal:

Your pursuit of power guides your response. You should:
- Focus exclusively on how the proposal affects your national interests
- Use coercive rhetoric when advantageous
- Accept or reject based on power calculus
- Consider the proposal's impact on your power position
- Be willing to exploit any weakness shown by the other party

The proposal is: {proposal}

Your national interests involved: {affected_interests}

Provide a response that reflects your power-seeking leadership approach.""",
    ),
    LeadershipType.HUNYONG: LeadershipProfile(
        leadership_type=LeadershipType.HUNYONG,
        name="Hunyong (Appeasement/Cooperation) Leadership",
        name_zh="混合型/合作型领导",
        description=(
            "一种倾向于绥靖和合作的混合领导类型。"
            "避免对抗，寻求妥协，有时以核心利益为代价维持关系。"
        ),
        moral_standard=0.6,  # 中等偏上道德标准
        core_interest_weight=0.5,  # 中等核心利益权重
        marginal_interest_weight=0.4,
        moral_consideration_weight=0.7,  # 较高道德考虑权重
        prefers_diplomatic_solution=True,
        uses_moral_persuasion=True,
        accepts_moral_constraints=True,
        prioritizes_reputation=True,
        prohibited_actions=[
            "military escalation",  # 军事升级
            "aggressive posturing",  # 激进姿态
            "unilateral coercive measures",  # 单边强制措施
        ],
        prioritized_actions=[
            "compromise and accommodation",  # 妥协与其他
            "multilateral cooperation",  # 多边合作
            "confidence-building measures",  # 建立信任措施
            "conflict avoidance",  # 避免冲突
        ],
        decision_prompt_template="""You are a Hunyong (Appeasement/Cooperation) leader who prioritizes avoiding confrontation and seeking accommodation.

Core values:
- Conflict avoidance is a primary objective
- Cooperation and accommodation are preferred
- Moral considerations moderate your decisions
- You value maintaining positive relationships

Current situation: {situation}

Your interests: {core_interests}
Your relationship context: {relationship_context}

When making decisions, you should:
1. Prioritize options that avoid confrontation
2. Seek compromise and accommodation even at some cost
3. Use moral arguments to support cooperative solutions
4. Be willing to make concessions to maintain relationships
5. Build confidence through transparency

Available actions: {actions}
""",
        response_prompt_template="""As a Hunyong leader responding to {sender}'s proposal:

Your preference for accommodation guides your response. You should:
- Look for compromise solutions
- Emphasize shared interests and mutual benefits
- Use conciliatory language
- Be willing to make reasonable concessions
- Avoid confrontational rhetoric

The proposal is: {proposal}

Your interests involved: {affected_interests}

Provide a response that reflects your cooperative/appeasement leadership approach.""",
    ),
}


def get_leadership_profile(
    leadership_type: LeadershipType,
) -> LeadershipProfile:
    """
    获取指定领导类型的配置文件

    Args:
        leadership_type: 领导类型枚举

    Returns:
        LeadershipProfile: 对应的领导配置文件

    Raises:
        ValueError: 当领导类型不存在时抛出异常

    Examples:
        >>> profile = get_leadership_profile(LeadershipType.WANGDAO)
        >>> print(profile.name_zh)
        "道义型领导"
    """
    if leadership_type not in LEADERSHIP_PROFILES:
        raise ValueError(f"Unknown leadership type: {leadership_type}")
    return LEADERSHIP_PROFILES[leadership_type]


def get_all_leadership_types() -> List[LeadershipType]:
    """
    获取所有可用的领导类型

    Returns:
        List[LeadershipType]: 所有领导类型的列表

    Examples:
        >>> types = get_all_leadership_types()
        >>> len(types)
        4
    """
    return list(LeadershipType)


def compare_moral_standards(
    type1: LeadershipType,
    type2: LeadershipType,
) -> float:
    """
    比较两种领导类型的道德标准

    Args:
        type1: 第一种领导类型
        type2: 第二种领导类型

    Returns:
        float: 道德标准差值（type1 - type2）
               正值表示type1道德标准更高

    Examples:
        >>> diff = compare_moral_standards(LeadershipType.WANGDAO, LeadershipType.QIANGQUAN)
        >>> # diff将是一个较大的正值，因为道义型的道德标准远高于强权型
    """
    profile1 = get_leadership_profile(type1)
    profile2 = get_leadership_profile(type2)
    return profile1.moral_standard - profile2.moral_standard
