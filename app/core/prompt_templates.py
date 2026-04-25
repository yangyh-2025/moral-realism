"""
LLM决策引擎提示模板模块
Prompt Templates Module for LLM Decision Engine

实现内嵌20种标准行为的决策提示工程。
完全对齐学术模型表1。
"""

from typing import Dict, Any, List, Optional

class PromptTemplates:
    """Centralized prompt template management for LLM decision engine."""

    # ============ System Prompt Templates ============
    # These templates define the role, rules, and output format requirements

    # System role template
    SYSTEM_ROLE_TEMPLATE = """
你是{agent_name}的国家领导集体集体，所属区域为{region}。
基于克莱因综合国力方程，该国初始综合国力得分为{initial_total_power}，当前当前综合国力得分为{current_total_power}，实力层级为{power_level}。
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
7. 在进行成本收益分析和行为选择时，**必须考虑地理位置和战略关系因素**：
   - 地理位置：同一区域的国家存在地缘政治互动，需评估区域合作潜力、地缘竞争风险、区域影响力等因素；
   - 战略关系：对盟友关系国家优先选择合作类行为，对战争/冲突关系国家应谨慎评估对抗行为风险，战略关系直接影响行为的成本收益计算；
   - 在成本收益分析中必须显式说明地理位置和战略关系对决策的影响。
"""

    # Output requirements template (for system prompt)
    OUTPUT_REQUIREMENTS_TEMPLATE = """
【输出要求】
1. 必须输出结构化JSON格式，禁止额外文本、禁止解释说明、禁止markdown格式；
2. 必须包含每一项行为的成本收益分析，明确净收益计算逻辑，必须包含行为对应的国力变化影响；
3. 必须为每一项行为指定明确的目标对象国（agent_id），目标国必须存在于当前体系内；
4. 可选择1-5项行为，禁止选择无收益的行为，禁止选择列表外的行为；
5. 必须填写action_id、action_name、action_category，且必须与允许行为列表完全一致。
6. 每一项行为的成本收益分析必须包含以下维度：
   - 行为对应的国力变化影响（成本和收益）
   - 地理位置因素：目标国是否在同一区域、地缘政治影响评估
   - 战略关系因素：与目标国的战略关系类型及其对行为选择的影响
   - 综合净收益：基于国力变化、地理位置和战略关系的整体评估
7. 每一项行为必须同时生成该行为的具体执行内容（action_content字段）
   - 具体内容应当符合行为类型的特征（如"发表公开声明"需要生成具体声明文本）
   - 内容应体现发起国的领导类型偏好
   - 内容应考虑与目标国的战略关系状态
   - 内容长度50-200字，具体、明确、有现实感
"""

    # System prompt template (combines role, rules, and output requirements)
    SYSTEM_PROMPT_TEMPLATE = """{system_role}{core_rules}

{output_requirements}
"""

    # ============ User Prompt Templates ============
    # These templates provide the task context and data

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

    # User prompt template (task description + context + data)
    USER_PROMPT_TEMPLATE = """
【任务描述】
你需要在当前国际政治环境下，作为{agent_name}的国家领导集体，基于上述核心规则和全量信息池，做出符合国家利益的最优决策。

请从下方允许执行的行为列表中选择1-5项行为，并为每项行为提供详细的成本收益分析。

{info_pool}{actions_list}

【JSON输出格式示例】
{json_example}
"""

    # Leader type rules mapping
    LEADER_TYPE_RULES = {
        "王道型": "国家利益优先，坚守国际道义；公平正义、言行一致、维护战略信誉、避免双重标准、不滥用强制手段；禁止执行所有不尊重主权的高烈度对抗行为，仅可执行尊重主权的合作类、外交类行为，不得偏离国家客观利益",
        "霸权型": "自身国家利益绝对优先，兼顾道义工具性；双重标准执行国际规范、通过规则构建获取超额利益、以自身利益为核心适用规则；禁止执行极端暴力与强制类行为，可执行双重标准的外交、经济类对抗行为，不得偏离国家客观利益",
        "强权型": "本国利益最大化，完全忽视道义；以军事/强制手段为核心工具、无视国际规范、不重视战略信誉、不惜破坏现有秩序；仅禁止非常规大规模暴力行为，优先选择高烈度强制行为实现利益，不得偏离国家客观利益",
        "昏庸型": "个人利益优先，可牺牲国家利益；决策以决策者个人利益为核心，可制定损害国家利益的政策，无固定策略偏好；唯一可主动偏离国家客观利益的类型，无行为禁止约束，可执行20项行为集中的所有行为"
    }


    # JSON output format template
    JSON_OUTPUT_TEMPLATE = {
        "decision_reason": "整体决策的核心逻辑与成本收益总览",
        "actions": [
            {
                "action_id": "行为ID",
                "action_category": "行为分类",
                "action_name": "行为名称，必须与列表完全一致",
                "target_agent_id": "目标国家ID",
                "cost_benefit_analysis": "该行为的成本、预期收益、净收益分析详情，必须包含国力变化影响",
                "action_content": "该行为的具体执行内容，如声明文本、协议概要、援助规模等，50-200字"
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
                f"发起国力变化:{action['initiator_power_change']} | "
                f"目标国力变化:{action['target_power_change']} | "
                f"简介:{action['action_desc']}"
            )
            table_lines.append(line)

        return "\n".join(table_lines)

    @classmethod
    def build_system_prompt(
        cls,
        agent_info: Dict[str, Any],
        leader_type: str
    ) -> str:
        """
        Build system prompt for decision making.

        System prompt defines role, rules, and output format requirements.

        Args:
            agent_info: Agent information including name, region, power, etc.
            leader_type: Leader type of agent

        Returns:
            System prompt string
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

        # Build system prompt
        system_prompt = cls.SYSTEM_PROMPT_TEMPLATE.format(
            system_role=system_role,
            core_rules=core_rules,
            output_requirements=cls.OUTPUT_REQUIREMENTS_TEMPLATE
        )

        return system_prompt.strip()

    @classmethod
    def build_user_prompt(
        cls,
        agent_info: Dict[str, Any],
        allowed_actions: List[Dict[str, Any]],
        info_pool: Dict[str, Any]
    ) -> str:
        """
        Build user prompt for decision making.

        User prompt provides task context, information pool, and action list.

        Args:
            agent_info: Agent information including name, region, power, etc.
            allowed_actions: List of allowed action configurations
            info_pool: Information pool with all agents, history, etc.

        Returns:
            User prompt string
        """
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

        # Build JSON format example
        import json
        json_example = json.dumps(cls.JSON_OUTPUT_TEMPLATE, ensure_ascii=False, indent=2)

        # Build user prompt
        user_prompt = cls.USER_PROMPT_TEMPLATE.format(
            agent_name=agent_info.get('agent_name', ''),
            info_pool=info_pool_section,
            actions_list=actions_list,
            json_example=json_example
        )

        return user_prompt.strip()

    @classmethod
    def build_follower_system_prompt(
        cls,
        agent_name: str,
        current_total_power: float,
        power_level: str
    ) -> str:
        """
        构建追随决策的系统提示词

        Args:
            agent_name: 智能体名称
            current_total_power: 当前国力
            power_level: 实力层级

        Returns:
            系统提示词字符串
        """
        return cls.FOLLOWER_SYSTEM_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            current_total_power=current_total_power,
            power_level=power_level
        ).strip()

    @classmethod
    def build_follower_user_prompt(
        cls,
        info_pool: Dict[str, Any],
        decision_type: str,  # 'participation' 或 'vote'
        leader_candidates_info: Optional[str] = None
    ) -> str:
        """
        构建追随决策的用户提示词

        Args:
            info_pool: 格式化后的信息池字典
            decision_type: 决策类型
            leader_candidates_info: 参选者信息（仅投票决策需要）

        Returns:
            用户提示词字符串
        """
        if decision_type == 'participation':
            additional_context = cls.LEADERSHIP_PARTICIPATION_CONTEXT
            decision_requirement = "请决定是否参与本轮国际领导竞争。"
            output_format = cls.LEADERSHIP_PARTICIPATION_OUTPUT
        elif decision_type == 'vote':
            additional_context = cls.FOLLOWER_VOTE_CONTEXT.format(
                leader_candidates_info=leader_candidates_info or "无参选者"
            )
            decision_requirement = "请选择一个国家作为追随对象，或选择中立。"
            output_format = cls.FOLLOWER_VOTE_OUTPUT
        else:
            raise ValueError(f"未知的决策类型: {decision_type}")

        return cls.FOLLOWER_USER_PROMPT_TEMPLATE.format(
            all_agent_info=info_pool.get('all_agent_info', '无数据'),
            history_action_records=info_pool.get('history_action_records', '无数据'),
            history_power_data=info_pool.get('history_power_data', '无数据'),
            last_round_order_info=info_pool.get('last_round_order_info', '无数据'),
            additional_context=additional_context,
            decision_requirement=decision_requirement,
            output_format=output_format
        ).strip()

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

        This method combines system and user prompts for backward compatibility.

        Args:
            agent_info: Agent information including name, region, power, etc.
            allowed_actions: List of allowed action configurations
            info_pool: Information pool with all agents, history, etc.
            leader_type: Leader type of agent

        Returns:
            Complete decision prompt string
        """
        system_prompt = cls.build_system_prompt(agent_info, leader_type)
        user_prompt = cls.build_user_prompt(agent_info, allowed_actions, info_pool)

        return system_prompt + "\n\n" + user_prompt

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
            required_fields = ['action_id', 'action_category', 'action_name', 'target_agent_id', 'cost_benefit_analysis', 'action_content']
            for field in required_fields:
                if field not in action:
                    return False, f"行为{i+1}缺少必需字段: {field}"

        return True, ""

    # 领导竞争参与决策提示模板
    LEADERSHIP_PARTICIPATION_TEMPLATE = """
【领导竞争参与决策】
你是{agent_name}的国家领导集体，当前综合国力为{current_total_power}，实力层级为{power_level}。

【当前国际体系状态】
体系内所有国家信息：{all_agent_info}
上一轮国际秩序类型：{last_order_type}
上一轮领导状况：{last_leader_info}

【决策要求】
请决定是否参与本轮国际领导竞争：
- 选择"参与"：如果希望参与国际领导竞争，争取成为体系领导者
- 选择"不参与"：如果不想参与领导竞争，保持现状或仅作为追随者

【输出要求】
必须输出JSON格式：{{"decision": "参与"或"不参与", "reason": "决策理由"}}
"""

    # 追随投票决策提示模板
    FOLLOWER_VOTE_TEMPLATE = """
【追随投票决策】
你是{agent_name}的国家领导集体，当前综合国力为{current_total_power}，实力层级为{power_level}。

【当前国际体系状态】
体系内所有国家信息：{all_agent_info}
上一轮国际秩序类型：{last_order_type}

【本轮领导竞争参选者】
以下国家决定参与本轮国际领导竞争：
{leader_candidates_info}

【决策要求】
请选择一个国家作为追随对象，或选择"中立"：
- 选择某个参选者：如果你希望追随该国家，在follower_agent_id字段填写该国家ID
- 选择"中立"：如果你不想追随任何国家，在follower_agent_id字段填写null

【输出要求】
必须输出JSON格式：
{{
    "follower_agent_id": <国家ID或null>,
    "follower_agent_name": <国家名称或"中立">,
    "reason": "决策理由"
}}
"""


# 追随决策的系统提示词模板（角色、规则、输出要求）
    FOLLOWER_SYSTEM_PROMPT_TEMPLATE = """
你是一个{agent_name}的国家领导集体，当前综合国力为{current_total_power}，实力层级为{power_level}。

【角色设定】
你需要代表国家做出追随相关的重要决策。

【决策规则】
1. 基于全量信息池中的所有信息做出理性决策
2. 考虑战略关系对追随选择的影响
3. 考虑历史互动模式对决策的指导作用
4. 考虑国力变化趋势对战略选择的影响

【输出要求】
- 必须严格按照JSON格式输出
- reason字段应简洁明了，说明决策的主要依据
"""

# 追随决策的用户提示词模板（任务、上下文、数据）
    FOLLOWER_USER_PROMPT_TEMPLATE = """
【任务】
请根据以下信息做出决策：

【全量信息池】
1. 当前体系内所有国家信息（含战略关系）：
{all_agent_info}

2. 历史轮次互动行为记录：
{history_action_records}

3. 历史轮次各国国力变化数据：
{history_power_data}

4. 上一轮体系追随关系与国际秩序类型：
{last_round_order_info}

{additional_context}

【决策要求】
{decision_requirement}

【输出格式】
{output_format}
"""

# 领导竞争参与决策的额外上下文
    LEADERSHIP_PARTICIPATION_CONTEXT = """
【领导竞争参与决策】
请决定是否参与本轮国际领导竞争：
- 选择"参与"：如果希望参与国际领导竞争，争取成为体系领导者
- 选择"不参与"：如果不想参与领导竞争，保持现状或仅作为追随者
"""

    LEADERSHIP_PARTICIPATION_OUTPUT = """
必须输出JSON格式：{{"decision": "参与"或"不参与", "reason": "决策理由"}}
"""

# 追随投票决策的额外上下文
    FOLLOWER_VOTE_CONTEXT = """
【追随投票决策】
本轮领导竞争参选者：
{leader_candidates_info}

请选择一个国家作为追随对象，或选择"中立"：
- 选择某个参选者：如果你希望追随该国家，在follower_agent_id字段填写该国家ID
- 选择"中立"：如果你不想追随任何国家，在follower_agent_id字段填写null
"""

    FOLLOWER_VOTE_OUTPUT = """
必须输出JSON格式：
{{
    "follower_agent_id": <国家ID或null>,
    "follower_agent_name": <国家名称或"中立">,
    "reason": "决策理由"
}}
"""


# Standard 20 GDELT interaction behaviors for reference - 使用学术文档完整描述
STANDARD_BEHAVIORS = [
    {
        "action_id": 1,
        "action_name": "发表公开声明",
        "action_en_name": "MAKE PUBLIC STATEMENT",
        "action_category": "外交手段",
        "action_desc": "行为方针对目标方发表各类公开声明，涵盖拒绝评论、发表正负向评论、考量政策选项、承认/宣示/否认责任、开展象征性行动、表达共情评论、传递共识等所有未另行分类的公开言语表述行为，是基础的二元言语互动行为",
        "respect_sov": True,
        "initiator_power_change": 0,
        "target_power_change": 0,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 2,
        "action_name": "呼吁/请求",
        "action_en_name": "APPEAL",
        "action_category": "外交手段",
        "action_desc": "行为方向目标方提出各类诉求与请求，包括呼吁开展经济/军事/司法/情报领域合作、寻求外交政策支持、申请各类援助、呼吁政治改革/对方做出让步，以及请求开展谈判、调解、争端解决等所有未另行分类的诉求表达行为",
        "respect_sov": True,
        "initiator_power_change": 0.1,
        "target_power_change": 0,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 3,
        "action_name": "表达合作意向",
        "action_en_name": "EXPRESS INTENT TO COOPERATE",
        "action_category": "外交手段",
        "action_desc": "行为方明确表达与目标方未来开展合作的意愿，涵盖表达各领域合作意向、承诺提供各类援助、表达实施政治改革的意愿、承诺做出让步，以及表达参与谈判、调解、争端解决的意向等所有未另行分类的合作意愿表达行为",
        "respect_sov": True,
        "initiator_power_change": 0.2,
        "target_power_change": 0.1,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 4,
        "action_name": "协商/磋商",
        "action_en_name": "CONSULT",
        "action_category": "外交手段",
        "action_desc": "行为方与目标方开展双向沟通协商，包括电话沟通、出访、接待来访、第三方地点会面、开展调解、进行谈判等所有未另行分类的主体间平等磋商互动行为",
        "respect_sov": True,
        "initiator_power_change": 0.3,
        "target_power_change": 0.3,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 5,
        "action_name": "开展外交合作",
        "action_en_name": "ENGAGE IN DIPLOMATIC COOPERATION",
        "action_category": "外交手段",
        "action_desc": "行为方与目标方开展官方外交层面的合作互动，涵盖赞扬/背书、口头辩护、为对方声援、授予外交承认、正式道歉、宽恕、签署正式协议等所有未另行分类的外交合作行为",
        "respect_sov": True,
        "initiator_power_change": 0.4,
        "target_power_change": 0.4,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 6,
        "action_name": "开展实质性合作",
        "action_en_name": "ENGAGE IN MATERIAL COOPERATION",
        "action_category": "经济手段",
        "action_desc": "行为方与目标方开展实体层面的实质性合作，包括经济合作、军事合作、司法合作、情报/信息共享等所有未另行分类的、非言语的实际合作行动",
        "respect_sov": True,
        "initiator_power_change": 0.5,
        "target_power_change": 0.5,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 7,
        "action_name": "提供援助",
        "action_en_name": "PROVIDE AID",
        "action_category": "经济手段",
        "action_desc": "行为方针对目标方提供各类援助支持，涵盖经济援助、军事援助、人道主义援助、军事保护/维和行动，以及授予庇护等所有未另行分类的援助提供行为",
        "respect_sov": True,
        "initiator_power_change": 0.2,
        "target_power_change": 0.6,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 8,
        "action_name": "让步/屈服",
        "action_en_name": "YIELD",
        "action_category": "外交手段",
        "action_desc": "行为方向目标方做出妥协与让步，包括放宽行政制裁、缓和异议管控、接受政治改革诉求、归还/释放人员与财产、放宽经济制裁、允许国际介入、军事行动降级、宣布停火、撤军/军事投降等所有未另行分类的让步行为",
        "respect_sov": True,
        "initiator_power_change": -0.5,
        "target_power_change": 0.5,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 9,
        "action_name": "调查",
        "action_en_name": "INVESTIGATE",
        "action_category": "信息手段",
        "action_desc": "行为方针对目标方开展各类官方调查活动，涵盖犯罪/腐败调查、人权侵犯调查、军事行动调查、战争罪调查等所有未另行分类的调查行为",
        "respect_sov": False,
        "initiator_power_change": -0.1,
        "target_power_change": -0.2,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 10,
        "action_name": "要求/索要",
        "action_en_name": "DEMAND",
        "action_category": "外交手段",
        "action_desc": "行为方向目标方提出各类强制性要求，包括要求对方开展合作、提供援助、实施政治改革、做出让步，以及要求对方进行谈判、调解、争端解决等所有未另行分类的、具有强制诉求属性的行为",
        "respect_sov": False,
        "initiator_power_change": -0.2,
        "target_power_change": -0.1,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 11,
        "action_name": "表达不满/不赞成",
        "action_en_name": "DISAPPROVE",
        "action_category": "外交手段",
        "action_desc": "行为方向目标方表达负面态度与异议，涵盖批评/谴责、各类指控、煽动反对、正式投诉、提起诉讼、司法定罪等所有未另行分类的不赞成不赞成行为",
        "respect_sov": False,
        "initiator_power_change": 0,
        "target_power_change": -0.1,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 12,
        "action_name": "拒绝",
        "action_en_name": "REJECT",
        "action_category": "外交手段",
        "action_desc": "行为方拒绝目标方提出的各类诉求与提议，包括拒绝合作、拒绝援助/改革诉求、拒绝做出让步、拒绝谈判/调解/争端解决方案、违背规范/法律、行使否决权等所有未另行分类的拒绝行为",
        "respect_sov": True,
        "initiator_power_change": 0.1,
        "target_power_change": -0.1,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 13,
        "action_name": "威胁",
        "action_en_name": "THREATEN",
        "action_category": "信息手段",
        "action_desc": "行为方向目标方发出各类威胁性表述，涵盖非武力制裁威胁、行政制裁威胁、煽动抗议/镇压威胁、中断谈判/调解威胁、军事武力威胁、发出最后通牒等所有未另行分类的威胁行为",
        "respect_sov": False,
        "initiator_power_change": -0.3,
        "target_power_change": -0.2,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 14,
        "action_name": "抗议",
        "action_en_name": "PROTEST",
        "action_category": "外交手段",
        "action_desc": "行为方针对目标方开展各类政治异议与抗议行动，涵盖集会示威、绝食抗议、罢工/抵制、封锁道路、暴力抗议/骚乱等所有未另行分类的集体政治抗议行为",
        "respect_sov": False,
        "initiator_power_change": -0.4,
        "target_power_change": -0.3,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 15,
        "action_name": "展示军事姿态",
        "action_en_name": "EXHIBIT MILITARY POSTURE",
        "action_category": "军事手段",
        "action_desc": "行为方针对目标方展示军警力量与军事威慑姿态，包括提升警察/军事警戒级别、动员/增强警察/武装/网络军事力量等所有未实际使用武力、仅做力量展示的行为",
        "respect_sov": False,
        "initiator_power_change": -0.2,
        "target_power_change": -0.3,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 16,
        "action_name": "降级关系",
        "action_en_name": "REDUCE RELATIONS",
        "action_category": "外交手段",
        "action_desc": "行为方针对目标方降级双边互动关系，涵盖降级/断绝外交关系、削减/ari止各类援助、实施禁运/抵制/制裁、中断谈判/调解、驱逐/撤出相关人员与机构等所有未另行分类的关系降级行为",
        "respect_sov": True,
        "initiator_power_change": -0.1,
        "target_power_change": -0.4,
        "is_initiative": True,
        "is_response": True
    },
    {
        "action_id": 17,
        "action_name": "胁迫/强制",
        "action_en_name": "COERCE",
        "action_category": "军事手段",
        "action_desc": "行为方针对目标方实施强制性胁迫行动，涵盖扣押/损毁财产、实施行政制裁、逮捕/拘留、驱逐个人、暴力镇压、网络攻击等所有未另行分类的强制胁迫行为",
        "respect_sov": False,
        "initiator_power_change": -0.5,
        "target_power_change": -0.6,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 18,
        "action_name": "攻击/袭击",
        "action_en_name": "ASSAULT",
        "action_category": "军事手段",
        "action_desc": "行为方针对目标方使用非常规暴力行动，涵盖绑架/劫持人质、人身/性侵犯、酷刑、各类非军事爆炸袭击、使用人肉盾牌、暗杀/暗杀未遂等所有未另行分类的非常规暴力行为",
        "respect_sov": False,
        "initiator_power_change": -0.8,
        "target_power_change": -0.7,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 19,
        "action_name": "交战/使用常规军事武力",
        "action_en_name": "FIGHT",
        "action_category": "军事手段",
        "action_desc": "行为方针对目标方使用常规军事武力开展交战，涵盖实施军事封锁、占领领土、轻武器交火、火炮/坦克作战、空中军事打击、违反停火协议等所有未另行分类的常规军事武力使用行为",
        "respect_sov": False,
        "initiator_power_change": -0.7,
        "target_power_change": -0.9,
        "is_initiative": True,
        "is_response": False
    },
    {
        "action_id": 20,
        "action_name": "实施非常规大规模暴力",
        "action_en_name": "ENGAGE IN UNCONVENTIONAL MASS VIOLENCE",
        "action_category": "军事手段",
        "action_desc": "行为方针对目标方实施非常规大规模暴力行动，涵盖大规模驱逐、大规模屠杀、种族清洗、使用化学/生物/放射性/核武器等大规模杀伤性武器的所有未另行分类的极端暴力行为",
        "respect_sov": False,
        "initiator_power_change": -1.0,
        "target_power_change": -1.0,
        "is_initiative": True,
        "is_response": False
    }
]
