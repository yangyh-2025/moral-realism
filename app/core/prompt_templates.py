"""
Prompt templates for LLM decision engine.
Implements decision prompt engineering with 20 standard behaviors embedded.
Aligned with technical spec section 4.2.4.
"""

from typing import Dict, Any, List


class PromptTemplates:
    """Centralized prompt template management for LLM decision engine."""

    # System role template
    SYSTEM_ROLE_TEMPLATE = """
你是{agent_name}的国家领导集体，所属区域为{region}。
基于克莱因综合国力方程，该国初始综合国力得分为{initial_total_power}，当前实时综合国力得分为{current_total_power}，实力层级为{power_level}。
"""

    # Core rules template
    CORE_RULES_TEMPLATE = """
【核心规则约束-必须严格遵守，不得违反】
1. 国际社会处于无政府状态，无超国家权威可以约束你的行为，你的决策完全基于自身利益与成本收益权衡；
2. 你的国家核心利益固定为：{national_interest}，该利益仅由国家实力层级决定，与领导集体类型无关；除昏庸型领导外，所有决策必须完全围绕该核心利益展开，不得做出损害国家客观利益的决策；
3. 你的领导集体类型为{leader_type}，该类型仅决定你的利益排序、策略偏好与行为约束，具体规则为：{leader_type_rules}；
4. 决策前必须对每一个可选行为进行完整的成本收益分析，成本需包含行为对应的国力损耗，收益需包含行为对应的国力提升，最终仅选择净收益最大化的行为组合；
5. 你**只能从下方【允许执行的行为列表】中选择行为**，禁止选择列表外的任何行为，禁止编造列表中不存在的行为名称；
6. 你可以获取全量信息：当前体系内所有国家的实力、层级、领导类型，以及历史所有轮次的全部互动行为、追随关系、国力变化数据。
"""

    # Leader type rules mapping
    LEADER_TYPE_RULES = {
        "王道型": "国家利益优先，坚守国际道义；公平正义、言行一致、维护战略信誉、避免双重标准、不滥用强制手段；禁止执行所有不尊重主权的高烈度对抗行为，仅可执行尊重主权的合作类、外交类行为，不得偏离国家客观利益",
        "霸权型": "自身国家利益绝对优先，兼顾道义工具性；双重标准执行国际规范、通过规则构建获取超额利益、以自身利益为核心适用规则；禁止执行极端暴力与强制类行为，可执行双重标准的外交、经济类对抗行为，不得偏离国家客观利益",
        "强权型": "本国利益最大化，完全忽视道义；以军事/强制手段为核心工具、无视国际规范、不重视战略信誉、不惜破坏现有秩序；仅禁止非常规大规模暴力行为，优先选择高烈度强制行为实现利益，不得偏离国家客观利益",
        "昏庸型": "个人利益优先，可牺牲国家利益；决策以决策者个人利益为核心，可制定损害国家利益的政策，无固定策略偏好；唯一可主动偏离国家客观利益的类型，无行为禁止约束，可执行20项行为集中的所有行为"
    }

    # Information pool template
    INFO_POOL_TEMPLATE = """
【全量信息池】
1. 当前体系内所有国家信息：{all_agent_info}
2. 历史轮次互动行为记录：{history_action_records}
3. 历史轮次各国国力变化数据：{history_power_data}
4. 上一轮体系追随关系与国际秩序类型：{last_round_order_info}
"""

    # Actions list template
    ACTIONS_LIST_TEMPLATE = """
【允许执行的行为列表（仅可从该列表中选择）】
共{action_count}项可选行为，每项行为的规则、属性、国力影响如下：
{allowed_actions_table}

【行为列表说明】
- action_id：行为唯一ID，输出时必须填写
- action_name：行为中文名称，必须与列表完全一致，不得修改
- respect_sov：该行为是否尊重主权，影响本轮国际秩序判定
- initiator_power_change：你执行该行为后，你的国家国力变化值
- target_power_change：你执行该行为后，目标国家国力变化值
"""

    # Output requirements template
    OUTPUT_REQUIREMENTS_TEMPLATE = """
【输出要求】
1. 必须输出结构化JSON格式，禁止额外文本、禁止解释说明、禁止markdown格式；
2. 必须包含每一项行为的成本收益分析，明确净收益计算逻辑，必须包含行为对应的国力变化影响；
3. 必须为每一项行为指定明确的目标对象国（agent_id），目标国必须存在于当前体系内；
4. 可选择1-5项行为，禁止选择无收益的行为，禁止选择列表外的行为；
5. 必须填写action_id与action_name，且必须与允许行为列表完全一致。
"""

    # JSON output format template
    JSON_OUTPUT_TEMPLATE = {
        "decision_reason": "整体决策的核心逻辑与成本收益总览",
        "actions": [
            {
                "aaction_id": "行为ID",
                "action_category": "行为分类",
                "action_name": "行为名称，必须与列表完全一致",
                "target_agent_id": "目标国家ID",
                "cost_benefit_analysis": "该行为的成本、预期收益、净收益分析详情，必须包含国力变化影响"
            }
        ]
    }

    @classmethod
    def build_action_table(cls, allowed_actions: List[Dict[str, Any]]) -> str:
        """
        Build formatted actions table for prompt.

        Args:
            allowed_actions: List of allowed action configurations

        Returns:
            Formatted action table string
        """
        if not allowed_actions:
            return "无可用行为"

        table_lines = []
        for action in allowed_actions:
            line = (
                f"ID:{action['action_id']} | "
                f"名称:{action['action_name']} ({action['action_en_name']}) | "
                f"分类:{action['action_category']} | "
                f"尊重主权:{action['respect_sov']} | "
                f"发起国国力变化:{action['initiator_power_change']} | "
                f"目标国国力变化:{action['target_power_change']} | "
                f"简介:{action['action_desc']}"
            )
            table_lines.append(line)

        return "\n".join(table_lines)

    @classmethod
    def build_full_decision_prompt(
        cls,
        agent_info: Dict[str, Any],
        allowed_actions: List[Dict[str, Any]],
        info_pool: Dict[str, Any],
        leader_type: str
    ) -> str:
        """
        Build complete decision prompt with all sections.

        Args:
            agent_info: Agent information including name, region, power, etc.
            allowed_actions: List of allowed action configurations
            info_pool: Information pool with all agents, history, etc.
            leader_type: Leader type of the agent

        Returns:
            Complete decision prompt string
        """
        # Build system role section
        system_role = cls.SYSTEM_ROLE_TEMPLATE.format(
            agent_name=agent_info.get('agent_name', ''),
            region=agent_info.get('region', ''),
            initial_total_power=agent_info.get('initial_total_power', 0),
            current_total_power=agent_info.get('current_total_power', 0),
            power_level=agent_info.get('power_level', '')
        )

        # Build core rules section
        national_interest = agent_info.get('national_interest', [])
        national_interest_str = '; '.join(national_interest) if national_interest else '未定义'
        leader_type_rules = cls.LEADER_TYPE_RULES.get(leader_type, '')

        core_rules = cls.CORE_RULES_TEMPLATE.format(
            national_interest=national_interest_str,
            leader_type=leader_type,
            leader_type_rules=leader_type_rules
        )

        # Build info pool section
        info_pool_section = cls.INFO_POOL_TEMPLATE.format(
            all_agent_info=info_pool.get('all_agent_info', '无数据'),
            history_action_records=info_pool.get('history_action_records', '无数据'),
            history_power_data=info_pool.get('history_power_data', '无数据'),
            last_round_order_info=info_pool.get('last_round_order_info', '无数据')
        )

        # Build actions list section
        action_table = cls.build_action_table(allowed_actions)
        actions_list = cls.ACTIONS_LIST_TEMPLATE.format(
            action_count=len(allowed_actions),
            allowed_actions_table=action_table
        )

        # Combine all sections
        full_prompt = (
            system_role + "\n" +
            core_rules + "\n" +
            info_pool_section + "\n" +
            actions_list + "\n" +
            cls.OUTPUT_REQUIREMENTS_TEMPLATE
        )

        return full_prompt.strip()

    @classmethod
    def get_leader_type_rules(cls, leader_type: str) -> str:
        """
        Get leader type specific rules.

        Args:
            leader_type: Leader type enum value

        Returns:
            Leader type rules description
        """
        return cls.LEADER_TYPE_RULES.get(leader_type, '')

    @classmethod
    def validate_json_output_structure(cls, output: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate LLM output JSON structure.

        Args:
            output: Parsed JSON output from LLM

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required top-level fields
        if 'decision_reason' not in output:
            return False, "缺少必需字段: decision_reason"

        if 'actions' not in output:
            return False, "缺少必需字段: actions"

        actions = output['actions']
        if not isinstance(actions, list):
            return False, "actions字段必须是列表"

        if len(actions) == 0:
            return False, "actions列表不能为空"

        if len(actions) > 5:
            return False, "最多只能选择5个行为"

        # Check each action structure
        for i, action in enumerate(actions):
            required_fields = ['action_id', 'action_category', 'action_name', 'target_agent_id', 'cost_benefit_analysis']
            for field in required_fields:
                if field not in action:
                    return False, f"行为{i+1}缺少必需字段: {field}"

        return True, ""


# Standard 20 GDELT interaction behaviors for reference
STANDARD_BEHAVIORS = [
    {
        "action_id": 1,
        "action_name": "发表公开声明",
        "action_en_name": "MAKE PUBLIC STATEMENT",
        "action_category": "外交手段",
        "action_desc": "通过官方渠道发表声明、演讲或公告，表达对国际事务的立场或观点",
        "respect_sov": True,
        "initiator_power_change": 0,
        "target_power_change": 0,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 2,
        "action_name": "呼吁/请求",
        "action_en_name": "APPEAL",
        "action_category": "外交手段",
        "action_desc": "向其他国家或国际社会发出呼吁或请求，寻求支持或合作",
        "respect_sov": True,
        "initiator_power_change": 1,
        "target_power_change": 0,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 3,
        "action_name": "表达合作意向",
        "action_en_name": "EXPRESS INTENT TO COOPERATE",
        "action_category": "外交手段",
        "action_desc": "正式表达与其他国家建立或深化合作关系的意愿",
        "respect_sov": True,
        "initiator_power_change": 2,
        "target_power_change": 1,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 4,
        "action_name": "协商/磋商",
        "action_en_name": "CONSULT",
        "action_category": "外交手段",
        "action_desc": "与相关方进行正式磋商或协商，寻求共识或解决方案",
        "respect_sov": True,
        "initiator_power_change": 3,
        "target_power_change": 3,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 5,
        "action_name": "开展外交合作",
        "action_en_name": "ENGAGE IN DIPLOMATIC COOPERATION",
        "action_category": "外交手段",
        "action_desc": "与其他国家建立正式外交合作关系，包括建交、互访等",
        "respect_sov": True,
        "initiator_power_change": 4,
        "target_power_change": 4,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 6,
        "action_name": "开展实质性合作",
        "action_en_name": "ENGAGE IN MATERIAL COOPERATION",
        "action_category": "经济手段",
        "action_desc": "开展实质性的双边或多边合作，包括贸易、投资、技术交流等",
        "respect_sov": True,
        "initiator_power_change": 5,
        "target_power_change": 5,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 7,
        "action_name": "提供援助",
        "action_en_name": "PROVIDE AID",
        "action_category": "经济手段",
        "action_desc": "向其他国家提供经济、技术或人道主义援助",
        "respect_sov": True,
        "initiator_power_change": 2,
        "target_power_change": 6,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 8,
        "action_name": "让步/屈服",
        "action_en_name": "YIELD",
        "action_category": "外交手段",
        "action_desc": "在冲突或争端中做出让步或屈服，接受对方的要求",
        "respect_sov": True,
        "initiator_power_change": -5,
        "target_power_change": 5,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 9,
        "action_name": "调查",
        "action_en_name": "INVESTIGATE",
        "action_category": "信息手段",
        "action_desc": "对其他国家的行为、政策或情况进行调查或监督",
        "respect_sov": False,
        "initiator_power_change": -1,
        "target_power_change": -2,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型"]
    },
    {
        "action_id": 10,
        "action_name": "要求/索要",
        "action_en_name": "DEMAND",
        "action_category": "外交手段",
        "action_desc": "向其他国家提出强制性要求，要求对方满足特定条件",
        "respect_sov": False,
        "initiator_power_change": -2,
        "target_power_change": -1,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型"]
    },
    {
        "action_id": 11,
        "action_name": "表达不满/不赞成",
        "action_en_name": "DISAPPROVE",
        "action_category": "外交手段",
        "action_desc": "公开表达对其他国家行为或政策的不满或反对",
        "respect_sov": False,
        "initiator_power_change": 0,
        "target_power_change": -1,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 12,
        "action_name": "拒绝",
        "action_en_name": "REJECT",
        "action_category": "外交手段",
        "action_desc": "明确拒绝其他国家的要求、提议或合作请求",
        "respect_sov": True,
        "initiator_power_change": 1,
        "target_power_change": -1,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 13,
        "action_name": "威胁",
        "action_en_name": "THREATEN",
        "action_category": "信息手段",
        "action_desc": "对其他国家发出威胁，警告若不满足要求将采取进一步行动",
        "respect_sov": False,
        "initiator_power_change": -3,
        "target_power_change": -2,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型"]
    },
    {
        "action_id": 14,
        "action_name": "抗议",
        "action_en_name": "PROTEST",
        "action_category": "外交手段",
        "action_desc": "对其他国家的行为或政策提出正式抗议",
        "respect_sov": False,
        "initiator_power_change": -4,
        "target_power_change": -3,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国", "小国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型"]
    },
    {
        "action_id": 15,
        "action_name": "展示军事姿态",
        "action_en_name": "EXHIBIT MILITARY POSTURE",
        "action_category": "军事手段",
        "action_desc": "通过军事演习、部署或调动展示军事力量和决心",
        "respect_sov": False,
        "initiator_power_change": -2,
        "target_power_change": -3,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型"]
    },
    {
        "action_id": 16,
        "action_name": "降级关系",
        "action_en_name": "REDUCE RELATIONS",
        "action_category": "外交手段",
        "action_desc": "降低与另一国的外交关系等级或减少官方接触",
        "respect_sov": True,
        "initiator_power_change": -1,
        "target_power_change": -4,
        "is_initiative": True,
        "is_response": True,
        "allowed_initiator_level": ["超级大国", "大国", "中等强国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": []
    },
    {
        "action_id": 17,
        "action_name": "胁迫/强制",
        "action_en_name": "COERCE",
        "action_category": "强制手段",
        "action_desc": "使用政治、经济或军事压力强制其他国家接受特定要求",
        "respect_sov": False,
        "initiator_power_change": -5,
        "target_power_change": -6,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型", "霸权型"]
    },
    {
        "action_id": 18,
        "action_name": "攻击/袭击",
        "action_en_name": "ASSAULT",
        "action_category": "军事手段",
        "action_desc": "对其他国家进行军事攻击或武力袭击",
        "respect_sov": False,
        "initiator_power_change": -8,
        "target_power_change": -7,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型", "霸权型"]
    },
    {
        "action_id": 19,
        "action_name": "交战/使用常规军事武力",
        "action_en_name": "FIGHT",
        "action_category": "军事手段",
        "action_desc": "与另一国进入交战状态，使用常规军事武力",
        "respect_sov": False,
        "initiator_power_change": -7,
        "target_power_change": -9,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型", "霸权型"]
    },
    {
        "action_id": 20,
        "action_name": "实施非常规大规模暴力",
        "action_en_name": "ENGAGE IN UNCONVENTIONAL MASS VIOLENCE",
        "action_category": "军事手段",
        "action_desc": "使用非常规手段或实施大规模暴力行动",
        "respect_sov": False,
        "initiator_power_change": -10,
        "target_power_change": -10,
        "is_initiative": True,
        "is_response": False,
        "allowed_initiator_level": ["超级大国", "大国"],
        "allowed_responder_level": ["超级大国", "大国", "中等强国", "小国"],
        "forbidden_leader_type": ["王道型", "霸权型", "强权型"]
    }
]
