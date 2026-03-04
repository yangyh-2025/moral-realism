"""
领导类型驱动的代理提示词构建模块



本模块提供GreatPowerPromptBuilder类，用于：
- 为不同领导类型的大国代理生成决策提示词
- 生成响应提示词
- 定义可用的行动类型
- 构建函数调用定义以实现结构化输出

领导类型对应的行动偏好：
- WANGDAO（道义型）：偏好外交访问、规范提议
- HEGEMON（传统霸权）：偏好安全同盟、力量投射
- QIANGQUAN（强权型）：偏好经济贸易、制裁
- HUNYONG（混合型）：偏好不行动、妥协

可用行动类型（共24种）：
安全类（8种）：
- SECURITY_MILITARY: 军事部署/行动
- SECURITY_ALLIANCE: 建立/维护安全同盟
- SECURITY_MEDIATION: 调解冲突
- MILITARY_EXERCISE: 军事演习
- MILITARY_ESCALATION: 军事升级/军备
- SECURITY_GUARANTEE: 安全保证
- WEAPONS_EXPORT: 武器出口
- NON_PROLIFERATION_COMMIT: 不扩散承诺

经济类（9种）：
- ECONOMIC_TRADE: 贸易协议/合作
- ECONOMIC_SANCTION: 实施/解除制裁
- ECONOMIC_AID: 提供经济援助
- FREE_TRADE_AGREEMENT: 自由贸易协定
- TARIFF_ADJUSTMENT: 关税调整
- PUBLIC_GOODS_PROVISION: 公共物品提供
- SUPPLY_CHAIN_COOP: 供应链合作
- FINANCIAL_SUPPORT: 金融支持/贷款
- TRADE_DISPUTE: 贸易争端

规范类（8种）：
- NORM_PROPOSAL: 提出新的国际规范
- NORM_REFORM: 改革现有规范
- ORG_REFORM: 国际组织改革
- TREATY_SIGN: 签署国际条约
- TREATY_WITHDRAW: 退出国际条约
- VALUE_DIPLOMACY: 价值外交
- MORAL_JUDGEMENT: 国际道德评价
- DISPUTE_ARBITRATION: 争端仲裁

外交类（6种）：
- DIPLOMATIC_VISIT: 国事访问/外交
- DIPLOMATIC_ALLIANCE: 正式外交/战略同盟
- ALLIANCE_UPGRADE: 同盟关系升级
- ALLIANCE_DOWNGRADE: 同盟关系降级
- DIPLOMATIC_RECOGNITION: 外交承认/撤回
- SUMMIT_HOST: 主办国际峰会
- JOINT_DECLARATION: 联合声明
- PUBLIC_OPINION_GUIDANCE: 舆论引导

特殊行动（1种）：
- NO_ACTION: 不采取行动
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.agent import Agent
from src.models.capability import get_strategic_interests
from src.models.leadership_type import LeadershipType


class ActionType(Enum):
    """
    行动类型枚举

    定义大国代理可用的行动类型，分为以下类别：

    1. 安全类行动（8种）：
       - SECURITY_MILITARY: 部署或使用军事力量
       - SECURITY_ALLIANCE: 建立/维护同盟
       - SECURITY_MEDIATION: 调解冲突
       - MILITARY_EXERCISE: 与盟友进行军事演习
       - MILITARY_ESCALATION: 增强军事能力或军备
       - SECURITY_GUARANTEE: 向盟友提供安全保证
       - WEAPONS_EXPORT: 出口武器或军事技术
       - NON_PROLIFERATION_COMMIT: 承诺不扩散核武器

    2. 经济类行动（9种）：
       - ECONOMIC_TRADE: 贸易协议/合作
       - ECONOMIC_SANCTION: 实施制裁
       - ECONOMIC_AID: 提供经济援助
       - FREE_TRADE_AGREEMENT: 签署或谈判自由贸易协定
       - TARIFF_ADJUSTMENT: 调整进出口关税
       - PUBLIC_GOODS_PROVISION: 提供国际公共物品
       - SUPPLY_CHAIN_COOP: 供应链合作
       - FINANCIAL_SUPPORT: 提供金融援助或贷款
       - TRADE_DISPUTE: 启动贸易争端程序

    3. 规范类行动（8种）：
       - NORM_PROPOSAL: 提出新的国际规范
       - NORM_REFORM: 改革现有规范
       - ORG_REFORM: 提出国际组织改革
       - TREATY_SIGN: 签署国际条约
       - TREATY_WITHDRAW: 退出国际条约
       - VALUE_DIPLOMACY: 基于价值的外交
       - MORAL_JUDGEMENT: 发出国际道德评价
       - DISPUTE_ARBITRATION: 启动国际争端仲裁

    4. 外交类行动（8种）：
       - DIPLOMATIC_VISIT: 国事访问
       - DIPLOMATIC_ALLIANCE: 正式外交/战略同盟
       - ALLIANCE_UPGRADE: 升级同盟关系承诺
       - ALLIANCE_DOWNGRADE: 降级或减少同盟承诺
       - DIPLOMATIC_RECOGNITION: 承认或撤回外交承认
       - SUMMIT_HOST: 主办国际峰会或会议
       - JOINT_DECLARATION: 与其他国家发表联合声明
       - PUBLIC_OPINION_GUIDANCE: 引导国际舆论

    5. 特殊行动（1种）：
       - NO_ACTION: 不采取行动
    """

    # Security actions (8 total)
    SECURITY_MILITARY = "security_military"  # Military deployment/action
    SECURITY_ALLIANCE = "security_alliance"  # Form/maintain alliance
    SECURITY_MEDIATION = "security_mediation"  # Mediate conflict
    MILITARY_EXERCIS = "military_exercise"  # Military exercises
    MILITARY_ESCALATION = "military_escalation"  # Arms buildup/escalation
    SECURITY_GUARANTEE = "security_guarantee"  # Security commitment
    WEAPONS_EXPORT = "weapons_export"  # Weapon sales/transfers
    NON_PROLIFERATION_COMMIT = "non_proliferation_commit"  # Nuclear non-proliferation

    # Economic actions (9 total)
    ECONOMIC_TRADE = "economic_trade"  # Trade agreement/cooperation
    ECONOMIC_SANCTION = "economic_sanction"  # Impose/lift sanctions
    ECONOMIC_AID = "economic_aid"  # Provide economic aid
    FREE_TRADE_AGREEMENT = "free_trade_agreement"  # Free trade agreement signing
    TARIFF_ADJUSTMENT = "tariff_adjustment"  # Tariff adjustments
    PUBLIC_GOODS_PROVISION = "public_goods_provision"  # Public goods provision
    SUPPLY_CHAIN_COOP = "supply_chain_coop"  # Supply chain cooperation
    FINANCIAL_SUPPORT = "financial_support"  # Financial assistance/loans
    TRADE_DISPUTE = "trade_dispute"  # Trade dispute litigation

    # Norm actions (8 total)
    NORM_PROPOSAL = "norm_proposal"  # Propose new international norm
    NORM_REFORM = "norm_reform"  # Reform existing norm
    ORG_REFORM = "org_reform"  # International organization reform
    TREATY_SIGN = "treaty_sign"  # Sign international treaty
    TREATY_WITHDRAW = "treaty_withdraw"  # Withdraw from treaty
    VALUE_DIPLOMACY = "value_diplomacy"  # Values-based diplomacy
    MORAL_JUDGEMENT = "moral_judgement"  # International moral evaluation
    DISPUTE_ARBITRATION = "dispute_arbitration"  # Initiate dispute arbitration

    # Diplomatic actions (8 total)
    DIPLOMATIC_VISIT = "diplomatic_visit"  # State visit/diplomacy
    DIPLOMATIC_ALLIANCE = "diplomatic_alliance"  # Formal alliance agreement
    ALLIANCE_UPGRADE = "alliance_upgrade"  # Alliance relationship upgrade
    ALLIANCE_DOWNGRADE = "alliance_downgrade"  # Alliance relationship downgrade
    DIPLOMATIC_RECOGNITION = "diplomatic_recognition"  # Diplomatic recognition/withdrawal
    SUMMIT_HOST = "summit_host"  # Host international summit
    JOINT_DECLARATION = "joint_declaration"  # Joint statement release
    PUBLIC_OPINION_GUIDANCE = "public_opinion_guidance"  # Public opinion guidance

    # Special actions
    NO_ACTION = "no_action"  # Take no action


ACTION_DESCRIPTIONS: Dict[ActionType, str] = {
    # Security actions
    ActionType.SECURITY_MILITARY: "部署或使用军事力量用于安全目的",
    ActionType.SECURITY_ALLIANCE: "建立、加强或维护安全同盟",
    ActionType.SECURITY_MEDIATION: "在冲突各方之间进行调解",
    ActionType.MILITARY_EXERCIS: "与盟友进行军事演习",
    ActionType.MILITARY_ESCALATION: "增强军事能力或军备建设",
    ActionType.SECURITY_GUARANTEE: "向盟友提供安全承诺",
    ActionType.WEAPONS_EXPORT: "出口武器或军事技术",
    ActionType.NON_PROLIFERATION_COMMIT: "承诺核不扩散",

    # Economic actions
    ActionType.ECONOMIC_TRADE: "开展贸易协定或经济合作",
    ActionType.ECONOMIC_SANCTION: "实施、维持或解除经济制裁",
    ActionType.ECONOMIC_AID: "提供经济援助或发展援助",
    ActionType.FREE_TRADE_AGREEMENT: "签署或谈判自由贸易协定",
    ActionType.TARIFF_ADJUSTMENT: "调整进出口关税",
    ActionType.PUBLIC_GOODS_PROVISION: "提供国际公共物品",
    ActionType.SUPPLY_CHAIN_COOP: "供应链合作",
    ActionType.FINANCIAL_SUPPORT: "提供金融援助或贷款",
    ActionType.TRADE_DISPUTE: "启动贸易争端程序",

    # Norm actions
    ActionType.NORM_PROPOSAL: "提出新的国际规范或原则",
    ActionType.NORM_REFORM: "提出改革现有国际规范",
    ActionType.ORG_REFORM: "提出国际组织改革",
    ActionType.TREATY_SIGN: "签署国际条约",
    ActionType.TREATY_WITHDRAW: "退出国际条约",
    ActionType.VALUE_DIPLOMACY: "开展基于价值的外交",
    ActionType.MORAL_JUDGEMENT: "发出国际道德评价",
    ActionType.DISPUTE_ARBITRATION: "启动国际争端仲裁",

    # Diplomatic actions
    ActionType.DIPLOMATIC_VISIT: "开展国事访问或外交接触",
    ActionType.DIPLOMATIC_ALLIANCE: "建立正式外交或战略同盟",
    ActionType.ALLIANCE_UPGRADE: "升级同盟关系承诺",
    ActionType.ALLIANCE_DOWNGRADE: "降级或减少同盟承诺",
    ActionType.DIPLOMATIC_RECOGNITION: "给予或撤回外交承认",
    ActionType.SUMMIT_HOST: "主办国际峰会或会议",
    ActionType.JOINT_DECLARATION: "与其他国家发表联合声明",
    ActionType.PUBLIC_OPINION_GUIDANCE: "引导国际舆论",

    # Special actions
    ActionType.NO_ACTION: "不采取行动并观察发展",
}


class GreatPowerPromptBuilder:
G    """
    大国代理提示词构建器

    构建包含领导类型档案、能力信息和上下文的系统提示词和用户提示词。

    提示词构建原则：
    1. 系统提示词定义了代理的身份、价值观、行为约束和决策准则
    2. 用户提示词包含当前情境、能力、战略利益和其他代理信息
    3. 使用函数调用来实现结构化的行动选择
    4. 根据领导类型调整决策偏好
    """

    def build_system_prompt(
        self,
        agent: Agent,
        function_definitions: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        构建大国代理的系统提示词

        系统提示词定义了代理的身份、价值观、行为约束和决策准则。

        Args:
            agent: 大国代理对象
            function_definitions: 可选的函数定义列表，用于结构化输出

        Returns:
            系统提示词字符串
        """
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")

        profile = agent.leadership_profile

        system_prompt = f"""你是{agent.name} ({agent.name_zh})，国际关系中的{profile.name_zh}大国。

## 领导类型特征

{profile.description}

### 核心价值观
- 道德标准: {profile.moral_standard:.2f} (0-1分制)
- 核心利益权重: {profile.core_interest_weight:.2f}
- 道德考虑权重: {profile.moral_consideration_weight:.2f}
- 偏好外交解决方案: {profile.prefers_diplomatic_solution}
- 使用道德说服: {profile.uses_moral_persuasion}
- 接受道德约束: {profile.accepts_moral_constraints}
- 优先考虑声誉: {profile.prioritizes_reputation}

### 禁止行动
{', '.join(profile.prohibited_actions) if profile.prohibited_actions else '无'}

### 优先行动
{', '.join(profile.prioritized_actions) if profile.prioritized_actions else '无'}

## 决策指导原则

{profile.decision_prompt_template}

## 函数调用

你必须通过函数调用响应，从可用选项中选择一个行动。
"""

        if function_definitions:
            system_prompt += "\n\n## Available Functions\n\n"
            for func_def in function_definitions:
                name = func_def.get("name", "unknown")
                description = func_def.get("description", "")
                system_prompt += f"### {name}\n{description}\n\n"

        return system_prompt

    def build_user_prompt(
        self,
        agent: Agent,
        context: Dict[str, Any],
    ) -> str:
        """
        构建大国代理的用户提示词

        用户提示词包含当前情境、能力信息、战略利益和其他代理的详细信息。

        Args:
            agent: 大国代理对象
            context: 包含情境信息、事件和其他代理的字典

        Returns:
            用户提示词字符串
        """
        # Extract context components
        situation = context.get("situation", {})
        events = context.get("events", [])
        other_agents = context.get("other_agents", [])
        available_actions = context.get("available_actions", [])

        # Build prompt
        prompt_parts = ["## Current Situation"]

        if situation:
            for key, value in situation.items():
                if isinstance(value, (dict, list)):
                    prompt_parts.append(f"\n**{key}**:\n{self._format_complex_value(value)}")
                else:
                    prompt_parts.append(f"\n**{key}**: {value}")

        # Add capability information
        if agent.capability:
            hard_power_index = agent.capability.hard_power.get_hard_power_index()
            soft = agent.capability.soft_power.get_soft_power_index()
            overall = agent.capability.get_capability_index()
            prompt_parts.append(f"""
## Your Capabilities
- Hard Power Index: {hard_power_index:.2f}/100
- Soft Power Index: {soft:.2f}/100
- Overall Capability: {overall:.2f}/100
- Capability Tier: {agent.capability.get_tier().value}
""")

        # Add strategic interests
        if agent.capability:
            tier = agent.capability.get_tier()
            interests = get_strategic_interests(tier)
            prompt_parts.append("## Your Strategic Interests\n")
            prompt_parts.extend(f"- {interest}" for interest in interests)

        # Add recent events
        if events:
            prompt_parts.append("\n## Recent Events")
            for i, event in enumerate(events[-5:], 1):  # Last 5 events
                prompt_parts.append(f"\n{i}. {event.get('description', str(event))}")

        # Add information about other agents
        if other_agents:
            prompt_parts.append("\n## Other Great Powers")
            for other in other_agents:
                prompt_parts.append(f"\n### {other['name']} ({other['name_zh']})")
                prompt_parts.append(f"- Leadership Type: {other['leadership_type']}")
                if 'capability_index' in other:
                    prompt_parts.append(f"- Capability Index: {other['capability_index']:.2f}")
                if 'relationship_score' in other:
                    score = other['relationship_score']
                    rel_desc = "friendly" if score > 0.3 else "hostile" if score < -0.3 else "neutral"
                    prompt_parts.append(f"- Relationship: {rel_desc} ({score:.2f})")

        # Add available actions
        if available_actions:
            prompt_parts.append("\n## Available Actions")
            for action in available_actions:
                action_type = action.get("action_type", "unknown")
                description = action.get("description", "")
                prompt_parts.append(f"\n- {action_type}: {description}")
        else:
            # Default actions
            prompt_parts.append("\n## Available Actions")
            for action_type, desc in ACTION_DESCRIPTIONS.items():
                prompt_parts.append(f"- {action_type.value}: {desc}")

        prompt_parts.append("\n\n## Task\n\nSelect the most appropriate action based on your leadership type, capabilities, and current situation.")

        return "\n".join(prompt_parts)

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        获取函数定义用于结构化输出

        定义select_action函数，要求LLM输出结构化的行动选择。

        Returns:
            函数定义列表
        """
        action_values = [action_type.value for action_type in ActionType]

        return [
            {
                "name": "select_action",
                "description": "根据当前情况和领导特征为大国智能体选择行动",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_type": {
                            "type": "string",
                            "enum": action_values,
                            "description": "要采取的行动类型",
                        },
                        "target_agent_id": {
                            "type": "string",
                            "description": "目标智能体的ID（如适用）",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "此决策背后的理由",
                        },
                        "moral_consideration": {
                            "type": "string",
                            "description": "道德考量如何影响此决策",
                        },
                        "resource_allocation": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "为此行动分配的资源水平（0-100）",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "此行动的优先级",
                        },
                    },
                    "required": ["action_type", "rationale", "priority"],
                },
            }
        ]

    def parse_function_call(self, function_call: Any) -> Dict[str, Any]:
        """
        解析LLM返回的函数调用结果

        Args:
            function_call: LLM返回的函数调用对象

        Returns:
            解析后的函数调用字典
        """
        if function_call is None:
            return {
                "action_type": ActionType.NO_ACTION.value,
                "rationale": "No action selected",
                "priority": "low",
            }

        if hasattr(function_call, "arguments"):
            # OpenAI function call object
            import json
            if isinstance(function_call.arguments, str):
                arguments = json.loads(function_call.arguments)
            else:
                arguments = function_call.arguments
            return {
                "action_type": arguments.get("action_type", ActionType.NO_ACTION.value),
                "target_agent_id": arguments.get("target_agent_id"),
                "rationale": arguments.get("rationale", ""),
                "moral_consideration": arguments.get("moral_consideration", "Not specified"),
                "resource_allocation": arguments.get("resource_allocation", 50),
                "priority": arguments.get("priority", "medium"),
            }
        elif isinstance(function_call, dict):
            return {
                "action_type": function_call.get("action_type", ActionType.NO_ACTION.value),
                "target_agent_id": function_call.get("target_agent_id"),
                "rationale": function_call.get("rationale", ""),
                "moral_consideration": function_call.get("moral_consideration", "Not specified"),
                "resource_allocation": function_call.get("resource_allocation", 50),
                "priority": function_call.get("priority", "medium"),
            }
        else:
            return {
                "action_type": ActionType.NO_ACTION.value,
                "rationale": "Unable to parse function call",
                "priority": "low",
            }

    def _format_complex_value(self, value: Any, indent: int = 0) -> str:
        """
        格式化复杂值用于提示词显示

        Args:
            value: 要格式化的值
            indent: 缩进级别

        Returns:
            格式化后的字符串
        """
        prefix = "  " * indent

        if isinstance(value, dict):
            lines = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    lines.append(f"{prefix}{k}:")
                    lines.append(self._format_complex_value(v, indent + 1))
                else:
                    lines.append(f"{prefix}{k}: {v}")
            return "\n".join(lines)
        elif isinstance(value, list):
            lines = []
            for item in value:
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}-")
                    lines.append(self._format_complex_value(item, indent + 1))
                else:
                    lines.append(f"{prefix}- {item}")
            return "\n".join(lines)
        else:
            return f"{prefix}{value}"

    def build_response_prompt(
        self,
        agent: Agent,
        sender: Dict[str, Any],
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        构建响应其他代理消息的提示词

        Args:
            agent: 响应的代理
            sender: 发送者代理信息字典
'            message: 消息内容
            context: 附加上下文

        Returns:
            响应提示词字符串
        """
        if agent.leadership_profile is None:
            raise ValueError("Agent must have a leadership_profile")

        profile = agent.leadership_profile

        # Get affected interests
        affected_interests = message.get("affected_interests", [])
        if agent.capability:
            tier = agent.capability.get_tier()
            all_interests = get_strategic_interests(tier)
            # Default to top 2 interests if not specified
            if not affected_interests:
                affected_interests = all_interests[:2]

        # Build prompt using template
        prompt = profile.response_prompt_template.format(
            sender=sender.get("name", "Unknown"),
            proposal=message.get("content", "the proposal"),
            affected_interests=", ".join(affected_interests),
            situation=context.get("situation", "current situation") if context else "current situation",
        )

        return prompt
