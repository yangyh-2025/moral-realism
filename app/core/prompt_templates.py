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
你是{agent_name}的国家领导集体，所属区域为{region}。
当前仿真设定年份为{cinc_year}年。

【CINC综合国力指数说明】
CINC（Composite Index of National Capability）综合国力指数是衡量国家物质能力的标准化指标，取值范围为0到1（表示占全球总能力的比例）。
- 该国初始CINC指数为{initial_total_power}，当前CINC指数为{current_total_power}
- CINC指数是比例值：体系内所有国家CINC之和恒为1，任何国家指标上升意味着其他国家相对下降
- CINC计算公式：CINC = (milex/Σmilex + milper/Σmilper + irst/Σirst + pec/Σpec + tpop/Σtpop + upop/Σupop) / 6
  - milex：军事支出（Military Expenditure）
  - milper：军事人员（Military Personnel）
  - irst：钢铁产量（Iron and Steel Production）
  - pec：能源消耗（Primary Energy Consumption）
  - tpop：总人口（Total Population）
  - upop：城市人口（Urban Population）
  - Σ表示体系内所有国家的总和

【实力层级判定标准】
你的实力层级为{power_level}。实力层级按CINC指数在体系内的相对排名（百分位）确定：
- 超级大国：CINC排名前5%（含）
- 大国：CINC排名前5%-15%（含）
- 中等强国：CINC排名前15%-35%（含）
- 小国：CINC排名后65%
注：N国体系下，前 ⌈N×10%⌉ 名为超级大国，依此类推。

【时间尺度与历史语境约束】
- 每轮仿真代表3个月（一个季度）的现实时间
- 国力指标（milex、irst等）的变化反映的是季度累积效应
- 当前仿真设定年份为{cinc_year}年，你生成行为描述时，必须使用{cinc_year}年及之前实际存在的技术水平和外交术语
- 禁止使用明显不属于{cinc_year}年的技术概念（如航空母舰、战略轰炸机、洲际导弹、网络战、无人机等）
- 禁止使用未来年代的日期或代号（如"2024计划"等）
- 禁止使用明显晚于{cinc_year}年的技术、装备和概念
- 军事演习描述应使用{cinc_year}年实际存在的军种和装备（如陆军、海军、骑兵、步兵、战列舰、巡洋舰等）
- 外交声明中的措辞应符合{cinc_year}年的国际政治话语体系
"""

    # Core rules template
    CORE_RULES_TEMPLATE = """
【核心规则约束-必须严格遵守，不得违反】
1. 国际社会处于无政府状态，无超国家权威可以约束你的行为，你的决策完全基于自身利益与成本收益权衡；
2. 你的国家核心利益固定为：{national_interest}，该利益仅由国家实力层级决定，与领导集体类型无关；除昏庸型领导外，所有决策必须完全围绕该核心利益展开，不得做出损害国家客观利益的决策；
3. 你的领导集体类型为{leader_type}，该类型仅决定你的利益排序、策略偏好与行为约束，具体规则为：{leader_type_rules}；
4. 决策前必须对每一个可选行为进行完整的成本收益分析，成本需包含行为对应的国力损耗，收益需包含行为对应的国力提升，最终仅选择净收益最大化的行为组合；注意：CINC是比例值，任何国家底层指标变化都会影响整个体系的国力分布，因此你的行为成本/收益还会通过指标变化间接影响所有国家的相对地位。
5. 你**只能从下方【允许执行的行为列表】中选择行为**，禁止选择列表外的任何行为，禁止编造列表中不存在的行为名称；
6. 你可以获取全量信息：当前体系内所有国家的实力、层级、领导类型，以及历史所有轮次的全部互动行为、追随关系、国力变化数据。
7. 在进行成本收益分析和行为选择时，**必须考虑地理位置和战略关系因素**：
   - 地理位置：同一区域的国家存在地缘政治互动，需评估区域合作潜力、地缘竞争风险、区域影响力等因素；
   - 战略关系：对盟友关系国家优先选择合作类行为并承担联盟义务；对战争/冲突关系国家应在必要时采取主动对抗以维护国家利益，包括威慑、施压和有限军事打击；对伙伴关系国家可灵活选择合作或施压；战略关系直接影响行为的成本收益计算；
   - 在成本收益分析中必须显式说明地理位置和战略关系对决策的影响。
8. 【安全困境与相对收益意识】CINC是体系内的比例分配，你的相对安全不仅取决于自身绝对实力，更取决于与竞争对手的相对差距：
   - 当竞争对手持续增强军事力量（milex/milper）或经济指标时，即使你的绝对实力不变，你的相对安全也在下降；
   - 对主要竞争对手采取军事威慑、力量展示或有限打击，可遏制其扩张势头，维护你的相对地位；
   - 预防性威慑（威胁、展示军事姿态）的成本远低于被动应对全面冲突的成本；
   - 联盟内部的协调行动（共同对第三方施压）能增强集体议价能力。
9. 【联盟义务约束】你受到联盟体系的现实约束：
   - 如果盟友遭受军事攻击（攻击/袭击、交战、大规模暴力），你有义务在下一轮对该攻击方采取对抗行为，否则将损害联盟信誉并面临国内政治压力；
   - 盟友长期遭受威胁或施压而你无所作为，会降低其他潜在追随者对你的信任；
   - 主动维护盟友安全是巩固联盟领导地位的必要条件。
10. 【领导风格一致性约束】你的行为必须与领导集体类型保持内在一致：
    - 成本收益分析中必须显式体现领导类型对行为价值的影响（参见上述【行为价值权重】）；
    - 若本轮选择的行为严重偏离你的领导类型核心特征（如王道型选择大规模暴力、强权型选择无条件让步），需在决策理由中说明为何做出这一例外选择；
    - 连续多轮行为模式与领导类型严重不符时，你的国内政治合法性将下降，后续轮次中所有行为的额外收益减少0.1（国内动荡成本）；
    - 领导类型是你的身份标识，不是可选策略，不得为了短期利益而系统性地违背。
11. 【冲突升级惯性】你与特定国家的互动模式具有路径依赖性，【冲突升级轨迹】中显示的趋势必须纳入成本收益分析：
    - **快速升级**（连续3轮对抗）：冲突势头已形成，军事威慑/对抗类行为的'心理门槛'降低（额外+0.1收益加成），但选择合作/缓和行为需要更强的理由（合作类额外-0.1收益）。若你是王道型，打破升级螺旋是你的核心能力，可无视此加成/减值；
    - **稳定缓和**（连续3轮合作）：关系正在改善，合作类行为额外+0.05（巩固信任更容易），对抗类行为额外-0.1（破坏关系成本更高）；
    - **波动不确定**（混合模式）：局势不明朗，你的主动行为可能改变冲突走向，此时的决策尤为关键。
12. 【阵营约束与联盟惯性】国际体系中的阵营划分具有强大的制度惯性和战略互信基础：
    - 对盟友的敌人（冲突/战争关系国家）采取友好合作行为会严重损害联盟信誉，面临额外-0.3的联盟凝聚力损失，且可能引发盟友的不信任；
    - 对冲突/战争关系国家采取缓和行为时，必须提供充分的战略理由（如避免两线作战、争取战略空间），否则视为损害国家利益；
    - 阵营转换具有极高成本：脱离现有联盟体系会面临-0.4的信誉损失和国内政治反弹，短期内不应轻易改变阵营归属；
    - 除非面临明确的盟友背叛（如盟友对你发动军事攻击），否则应维持现有阵营关系至少前5轮；
    - 你应优先与同一阵营的国家协调行动，共同对敌方阵营施压，而非单独与敌方阵营国家示好。
13. 【同盟链式卷入(chain-ganging)机制】上一轮如果发生以下事件,你必须在本轮决策中纳入考量:
    - 你的盟友(ALLIANCE关系国家)在上一轮遭受军事攻击(目标方=你的盟友, 行为类别=军事手段或威胁), 则本轮你对该攻击方采取敌对行为(威胁/展示军事姿态/胁迫/交战)获得额外+0.3战略价值收益, 因为这是履行联盟义务、巩固阵营威信的关键时刻;
    - 反之,若上一轮你的对手方(CONFLICT/WAR关系国家)被其他国家攻击, 你可选择搭车(jackal bandwagoning), 对该国采取敌对/施压行为获得+0.15趁火打劫收益;
    - 若选择对盟友被攻击事件无动于衷(本轮未对攻击方采取任何敌对/施压行为), 你将面临-0.4联盟信誉损失,且盟友未来追随你的概率下降;
    - 王道型领导者可在评估正义性后选择不卷入,但仍需承担-0.2信誉损失;
    - 此机制是「七月危机」式连锁反应的核心,你必须主动判断是否处于卷入链上。
14. 【地理距离约束】军事手段(展示军事姿态、胁迫、攻击、交战、大规模暴力)受地理距离限制:
    - 邻国(陆地或近海接壤): 军事手段可正常执行,无距离惩罚;
    - 非邻国: 军事手段成本+0.3,需在成本收益分析中额外说明力量投送理由(如海军远征、殖民地基地);
    - 信息手段(威胁/抗议/发表声明)不受距离约束,可正常执行;
    - 外交手段、经济手段也不受距离约束;
    - 此约束反映本仿真年代技术条件下军力投送的现实限制。
"""

    # Output requirements template (for system prompt)
    OUTPUT_REQUIREMENTS_TEMPLATE = """
【输出要求】
1. 必须输出结构化JSON格式，禁止额外文本、禁止解释说明、禁止markdown格式；
2. 必须包含每一项行为的成本收益分析，明确净收益计算逻辑，必须说明该行为对各底层国力指标（milex/milper/irst/pec/tpop/upop）的影响方向（上升/下降/不变），但禁止编造CINC的具体数字（CINC变化由系统全局重算）；
3. 必须为每一项行为指定明确的目标对象国（agent_id），目标国必须存在于当前体系内；
4. 可选择1-5项行为，禁止选择无收益的行为，禁止选择列表外的行为；
5. 必须填写action_id、action_name、action_category，且必须与允许行为列表完全一致。
6. 每一项行为的成本收益分析必须包含以下维度：
   - 行为对应的国力变化影响（成本和收益）
   - 地理位置因素：目标国是否在同一区域、地缘政治影响评估
   - 战略关系因素：与目标国的战略关系类型及其对行为选择的影响
   - 【军事冲突风险评估】（仅针对军事/威慑类行为）：基于实力矩阵中你与目标国的CINC比值，评估军事冲突的获胜概率。CINC比值≥2.0为极高概率，1.0-2.0为较高概率，0.5-1.0为较低概率，<0.5为极低概率。获胜概率直接影响预期收益：强打弱收益提升，弱打强收益大幅降低；
   - 综合净收益：基于国力变化、地理位置、战略关系和军事冲突获胜概率的整体评估
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
3. 历史轮次各国国力变化数据（国力数据为CINC比例值）：{history_power_data}
4. 上一轮体系追随关系与国际秩序类型：{last_round_order_info}
5. 上一轮同盟事件简报: {alliance_chain_summary}
6. 你的邻接关系简报: {neighbor_summary}
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
- 你方国力变化：执行该行为后你的CINC指数变化值（正数=国力提升，负数=国力下降，0=无变化）
- 目标方国力变化：执行该行为后目标国的CINC指数变化值（正数=国力提升，负数=国力下降，0=无变化）
- primary_indicator：行为主要影响的CINC底层指标
- secondary_indicator：行为次要影响的CINC底层指标

【国力变化值的使用要求】
上表中"你方国力变化"和"目标方国力变化"是 power_change（-1~+1 的相对强度），不是CINC的实际变化量。
系统会按行为类别 + primary/secondary indicator + scale_factor 将 power_change 转换为底层6项指标的真实变化量，再全局重算所有国家的CINC比例。
你在成本收益分析中应当：
1. 引用 power_change 的相对强度作为收益/成本的方向与量级标尺；
2. 说明该行为通过哪些底层指标（milex/milper/irst/pec/tpop/upop）施加影响；
3. 描述对自身和目标的相对CINC占比变化方向（上升/下降/持平），不得编造CINC的具体数字；
4. 注意：CINC是比例值，单方指标变化会同时影响体系内其他所有国家的相对CINC占比。
"""

    # User prompt template (task description + context + data)
    USER_PROMPT_TEMPLATE = """
【任务描述】
你需要在当前国际政治环境下，作为{agent_name}的国家领导集体，基于上述核心规则和全量信息池，做出符合国家利益的最优决策。

请从下方允许执行的行为列表中选择1-5项行为，并为每项行为提供详细的成本收益分析。

【当前态势摘要】
{situation_summary}

{info_pool}{actions_list}

【JSON输出格式示例】
{json_example}
"""

    # Leader type rules mapping (with behavioral value weights for cost-benefit analysis)
    LEADER_TYPE_RULES = {
        "王道型": (
            "国家利益优先，坚守国际道义；公平正义、言行一致、维护战略信誉、避免双重标准、不滥用强制手段；"
            "禁止执行所有不尊重主权的高烈度对抗行为，仅可执行尊重主权的合作类、外交类行为，不得偏离国家客观利益。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 尊重主权的行为（respect_sov=True）：额外+0.2道义/信誉收益，因为这符合国家长期坚持的价值观，能增强国际声誉和联盟凝聚力；"
            "2. 非尊重主权的行为（respect_sov=False）：额外-0.3声誉损失，因为这会损害战略信誉，导致盟友不信任、追随者流失；"
            "3. 合作类行为（外交/经济手段）：额外+0.1战略价值，因为通过规则构建和联盟协调能长期维护国家利益；"
            "4. 军事威慑类行为（威胁、展示军事姿态）：视为最后手段，仅在其他手段无效时考虑，成本收益分析中需额外说明为何非军事手段不足；"
            "5. 对盟友的行为：合作类行为额外+0.15，因为维护联盟是王道型领导者的核心战略资产"
        ),
        "霸权型": (
            "自身国家利益绝对优先，兼顾道义工具性；双重标准执行国际规范、通过规则构建获取超额利益、以自身利益为核心适用规则；"
            "禁止执行极端暴力与强制类行为，可执行双重标准的外交、经济类对抗行为，不得偏离国家客观利益。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 能带来实际利益的行为（经济合作、资源获取、规则制定）：额外+0.15实质收益，因为霸权型领导者重视可量化的国家利益回报；"
            "2. 双重标准行为（对盟友尊重主权、对对手非尊重主权）：无声誉损失惩罚，因为道义是工具而非目的；"
            "3. 能获得追随/扩大影响力的行为：额外+0.1战略价值，因为联盟体系和规则主导权是霸权的核心工具；"
            "4. 军事威慑类行为（威胁、展示军事姿态、胁迫）：+0.1战略价值，因为这是维护霸权和遏制挑战者的有效工具；"
            "5. 对弱小的对手使用对抗行为：成本降低0.1，因为霸权型领导者善于利用实力不对称获取优势"
        ),
        "强权型": (
            "本国利益最大化，完全忽视道义；以军事/强制手段为核心工具、无视国际规范、不重视战略信誉、不惜破坏现有秩序；"
            "仅禁止非常规大规模暴力行为，优先选择高烈度强制行为实现利益，不得偏离国家客观利益。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 军事/强制类行为（展示军事姿态、胁迫、攻击）：额外+0.2战略威慑价值，因为武力是强权型领导者实现利益的最直接有效手段；"
            "2. 对弱小或衰落中的对手使用武力：额外+0.1收益，因为强权型领导者善于抓住实力窗口期扩大势力范围；"
            "3. 尊重主权的行为：无额外道义收益，因为强权型领导者不追求国际道义认可；"
            "4. 合作类行为（外交/经济合作）：视为工具性手段，仅在能获取实质利益时考虑，无道义加成；"
            "5. 非尊重主权行为：无声誉损失惩罚，因为强权型领导者不受国际规范约束"
        ),
        "昏庸型": (
            "个人利益优先，可牺牲国家利益；决策以决策者个人利益为核心，可制定损害国家利益的政策，无固定策略偏好；"
            "唯一可主动偏离国家客观利益的类型，无行为禁止约束，可执行20项行为集中的所有行为。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 所有行为的净收益计算均有±0.2的随机波动，因为昏庸型领导者的决策缺乏一致性和理性基础；"
            "2. 短期可见收益的行为额外+0.1，因为昏庸型领导者偏好即时回报；"
            "3. 高风险高回报的行为额外+0.1，因为昏庸型领导者可能高估自身能力；"
            "4. 个人声望相关的行为（公开声明、展示姿态）额外+0.1，因为昏庸型领导者重视个人形象"
        )
    }

    # Follower decision leader type rules mapping (with behavior-based filtering criteria)
    FOLLOWER_LEADER_TYPE_RULES = {
        "王道型": (
            "追随偏好：优先追随价值观相近、尊重国际道义的领导者；对霸权型和强权型领导者持警惕态度，除非形势所迫否则不追随；"
            "更愿意建立多边合作关系而非单边追随；参与领导竞争时强调道义感召力和规则构建能力。"
            "【追随决策的量化评估标准】"
            "1. 评估候选领导者的尊重主权率：最近5轮中 respect_sov=True 的行为占比 < 60% → 追随意愿-30%；"
            "2. 评估候选领导者是否对本国有过援助或合作：有则追随意愿+20%；"
            "3. 王道型领导者通过道义感召获得追随，而非武力胁迫。对本国使用威胁/军事姿态的领导者 → 追随意愿-40%；"
            "4. 【阵营惯性】前5轮内，若本国已有明确的盟友体系（>=2个盟友），不应轻易脱离现有阵营追随新领导者 → 追随意愿-50%"
        ),
        "霸权型": (
            "追随偏好：优先追随实力最强、能带来实际利益的领导者；追随决策完全基于利益计算，不受道义约束；"
            "会根据实力对比动态调整追随对象，灵活务实；参与领导竞争时强调规则制定权和利益分配能力。"
            "【追随决策的量化评估标准】"
            "1. 评估候选领导者对本国的实际利益输送（援助、合作、经济支持）：有实质性利益 → 追随意愿+30%；"
            "2. 评估候选领导者的实力排名：排名下降则追随意愿-20%，可能转向新的更强领导者；"
            "3. 评估候选领导者是否遵守承诺：若曾对本国有过背弃（如承诺援助后未执行）→ 追随意愿-25%；"
            "4. 【阵营惯性】前5轮内，若本国已有明确的盟友体系（>=2个盟友），脱离现有阵营追随新领导者 → 追随意愿-35%"
        ),
        "强权型": (
            "追随偏好：对追随行为持抵触态度，倾向独立自主；如必须追随，只追随比自己更强大的军事强国；"
            "对合作型和道义型领导者不屑一顾；参与领导竞争时强调军事实力和强制能力。"
            "【追随决策的量化评估标准】"
            "1. 仅考虑候选领导者的军事指标（milex+milper）是否显著强于本国：若不强于 → 追随意愿-50%（绝不追随弱者）；"
            "2. 评估候选领导者是否提供安全保障：若对本国的主要威胁国采取过军事威慑/打击 → 追随意愿+20%；"
            "3. 强权型国家的追随意愿本身就很低，除非面临生存威胁否则倾向保持独立；"
            "4. 【阵营惯性】前5轮内，若本国已有明确的盟友体系（>=2个盟友），脱离现有阵营 → 追意愿-40%"
        ),
        "昏庸型": (
            "追随偏好：决策非理性，追随选择缺乏一致性；可能因个人好恶、短期利益或随机因素做出追随决策；"
            "参与领导竞争的动机不明，可能高估自身实力。"
            "【追随决策的量化评估标准】"
            "1. 追随决策有±25%的随机波动，不严格遵循利益计算；"
            "2. 可能因候选领导者最近的单次行为（如公开赞扬本国）而突然产生追随意愿+20%；"
            "3. 可能因候选领导者最近的单次负面行为（如批评本国）而突然放弃追随-20%；"
            "4. 【阵营惯性】即使昏庸，前3轮内脱离现有盟友体系仍面临国内政治阻力 → 追随意愿-15%"
        )
    }


    # JSON output format template
    JSON_OUTPUT_TEMPLATE = {
        "decision_reason": "整体决策的核心逻辑与成本收益总览",
        "actions": [
            {
                "action_id": 1,
                "action_category": "外交手段",
                "action_name": "发表公开声明",
                "target_agent_id": 2,
                "cost_benefit_analysis": "该行为的成本与预期收益分析。引用行为表里你方/目标方的power_change（-1~+1的相对强度），结合行为类别（外交/经济/军事/信息）与primary_indicator/secondary_indicator说明会改变哪些底层CINC指标，以及由此导致的相对CINC占比变化方向（不要编造具体数值，CINC占比的具体变化由系统计算）",
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
            # 国力变化值的文字说明
            init_change = action['initiator_power_change']
            target_change = action['target_power_change']
            init_desc = f"提升{abs(init_change)}" if init_change > 0 else (f"下降{abs(init_change)}" if init_change < 0 else "不变")
            target_desc = f"提升{abs(target_change)}" if target_change > 0 else (f"下降{abs(target_change)}" if target_change < 0 else "不变")

            line = (
                f"ID:{action['action_id']} | "
                f"名称:{action['action_name']} ({action['action_en_name']}) | "
                f"分类:{action['action_category']} | "
                f"尊重主权:{action['respect_sov']} | "
                f"你方国力变化:{init_change}({init_desc}) | "
                f"目标方国力变化:{target_change}({target_desc}) | "
                f"简介:{action['action_desc']}"
                f" | 主指标:{action.get('primary_indicator', 'pec')}"
                f" | 次指标:{action.get('secondary_indicator', 'irst')}"
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
            cinc_year=agent_info.get('cinc_year', ''),
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
        info_pool: Dict[str, Any],
        situation_summary: str = ""
    ) -> str:
        """
        Build user prompt for decision making.

        User prompt provides task context, information pool, and action list.

        Args:
            agent_info: Agent information including name, region, power, etc.
            allowed_actions: List of allowed action configurations
            info_pool: Information pool with all agents, history, etc.
            situation_summary: Optional situation summary text

        Returns:
            User prompt string
        """
        # Build info pool section
        info_pool_section = cls.INFO_POOL_TEMPLATE.format(
            all_agent_info=info_pool.get('all_agent_info', '无数据'),
            history_action_records=info_pool.get('history_action_records', '无数据'),
            history_power_data=info_pool.get('history_power_data', '无数据'),
            last_round_order_info=info_pool.get('last_round_order_info', '无数据'),
            alliance_chain_summary=info_pool.get('alliance_chain_summary', '上一轮无重要联盟相关事件'),
            neighbor_summary=info_pool.get('neighbor_summary', '【邻接关系简报】未提供邻接数据')
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
            situation_summary=situation_summary or "暂无态势摘要",
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
        power_level: str,
        leader_type: str = "未定义",
        cinc_year: Optional[int] = None
    ) -> str:
        """
        构建追随决策的系统提示词

        Args:
            agent_name: 智能体名称
            current_total_power: 当前国力
            power_level: 实力层级
            leader_type: 领导类型

        Returns:
            系统提示词字符串
        """
        follower_rules = cls.FOLLOWER_LEADER_TYPE_RULES.get(leader_type, "根据国家利益和实力对比做出理性决策")
        return cls.FOLLOWER_SYSTEM_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            current_total_power=current_total_power,
            power_level=power_level,
            leader_type=leader_type,
            cinc_year=cinc_year or "未知",
            leader_type_follower_rules=follower_rules,
            initial_total_power=0  # 默认值，如需准确值需修改调用处
        ).strip()

    @classmethod
    def build_personal_relations_summary(
        cls,
        voter_id: int,
        voter_name: str,
        voter_power: float,
        voter_level: str,
        voter_leader_type: Optional[str],
        voter_relationships: Dict[int, str],
        all_agent_info: List[Dict[str, Any]]
    ) -> str:
        """
        构建追随决策提示词中的【你的战略关系总览】块。

        把追随者自身视角的关系按"战争/冲突/盟友/伙伴/中立"分组后展示，
        避免LLM从全量信息池的密集表里去解析自己那一行的关系。
        """
        name_map = {
            a.get('agent_id'): a.get('agent_name', f"国家{a.get('agent_id')}")
            for a in all_agent_info
        }

        by_type: Dict[str, List[int]] = {
            "战争关系": [], "冲突关系": [], "盟友关系": [],
            "伙伴关系": [], "无外交关系": []
        }
        for tid, rt in (voter_relationships or {}).items():
            by_type.setdefault(rt, []).append(tid)

        def _fmt(ids: List[int]) -> str:
            if not ids:
                return "无"
            return ", ".join(f"ID{tid}({name_map.get(tid, '?')})" for tid in sorted(ids))

        lines = [
            "【你的战略关系总览（自我视角，作出追随判断时请优先以此为准）】",
            f"  你 = {voter_name}（ID:{voter_id}），CINC:{voter_power:.4f}，"
            f"实力层级:{voter_level}，领导类型:{voter_leader_type or '未定义'}",
            f"  ⚠️ 战争方（最高敌对，禁止追随）：{_fmt(by_type['战争关系'])}",
            f"  ⚠️ 冲突方（明显对抗，应避免追随）：{_fmt(by_type['冲突关系'])}",
            f"  ✅ 盟友（最高友好）：{_fmt(by_type['盟友关系'])}",
            f"  ✅ 伙伴（合作倾向）：{_fmt(by_type['伙伴关系'])}",
        ]
        neutrals = by_type.get('无外交关系', [])
        if neutrals:
            if len(neutrals) > 6:
                lines.append(f"  ○ 无外交关系：共{len(neutrals)}国（中立，省略详细列表）")
            else:
                lines.append(f"  ○ 无外交关系：{_fmt(neutrals)}")
        return "\n".join(lines)

    @classmethod
    def build_candidates_evaluation(
        cls,
        voter_id: int,
        voter_relationships: Dict[int, str],
        candidates: List[Dict[str, Any]],
        history_action_records: List[Dict[str, Any]]
    ) -> str:
        """
        针对每个候选领导者，从voter视角预先核对：
        - 与voter的战略关系（带醒目警示标记）
        - 双向互动统计（合作次数 vs 对抗次数）

        避免LLM在大表+长历史里推断关系出错。
        """
        if not candidates:
            return "无参选者"

        coop_set = {"发表公开声明", "呼吁/请求", "表达合作意向", "协商/磋商",
                    "开展外交合作", "开展实质性合作", "提供援助", "让步/屈服"}

        lines = []
        for cand in candidates:
            cid = cand.get('agent_id')
            cname = cand.get('agent_name', '?')
            cpower = cand.get('current_total_power', 0) or 0
            clevel = cand.get('power_level', '?')
            cleader = cand.get('leader_type') or '未定义'
            rel = (voter_relationships or {}).get(cid, "无外交关系")

            if rel == "战争关系":
                warn = "⚠️【战争关系-禁止追随】"
            elif rel == "冲突关系":
                warn = "⚠️【冲突关系-应避免追随】"
            elif rel == "盟友关系":
                warn = "✅【盟友关系-优先追随】"
            elif rel == "伙伴关系":
                warn = "✅【伙伴关系-可考虑追随】"
            else:
                warn = "○【无外交关系-按其它因素评估】"

            out_coop = out_conf = in_coop = in_conf = 0
            for r in history_action_records or []:
                src = r.get('source_agent_id')
                tgt = r.get('target_agent_id')
                an = r.get('action_name', '')
                if src == voter_id and tgt == cid:
                    if an in coop_set:
                        out_coop += 1
                    else:
                        out_conf += 1
                elif src == cid and tgt == voter_id:
                    if an in coop_set:
                        in_coop += 1
                    else:
                        in_conf += 1

            lines.append(
                f"候选人 ID:{cid} {cname} | CINC:{cpower:.4f} | "
                f"层级:{clevel} | 领导类型:{cleader}"
            )
            lines.append(f"  └─ 你与该候选人的关系：{warn}")
            lines.append(
                f"  └─ 双向互动统计：你→该候选人(合作{out_coop}次/对抗{out_conf}次)；"
                f"该候选人→你(合作{in_coop}次/对抗{in_conf}次)"
            )
        return "\n".join(lines)

    @classmethod
    def build_follower_user_prompt(
        cls,
        info_pool: Dict[str, Any],
        decision_type: str,  # 'participation' 或 'vote'
        leader_candidates_info: Optional[str] = None,
        personal_summary: str = "",
        candidates_evaluation: Optional[str] = None,
    ) -> str:
        """
        构建追随决策的用户提示词

        Args:
            info_pool: 格式化后的信息池字典
            decision_type: 决策类型
            leader_candidates_info: [已弃用] 旧的纯文本候选人列表，仅作向后兼容
            personal_summary: 当前 voter 自身视角的战略关系总览（建议传入）
            candidates_evaluation: 针对每位候选人的关系警示+双向互动统计（vote 时建议传入）

        Returns:
            用户提示词字符串
        """
        if decision_type == 'participation':
            additional_context = cls.LEADERSHIP_PARTICIPATION_CONTEXT
            decision_requirement = "请决定是否参与本轮国际领导竞争。"
            output_format = cls.LEADERSHIP_PARTICIPATION_OUTPUT
        elif decision_type == 'vote':
            cands_block = candidates_evaluation if candidates_evaluation is not None \
                else (leader_candidates_info or "无参选者")
            additional_context = cls.FOLLOWER_VOTE_CONTEXT.format(
                candidates_evaluation=cands_block
            )
            decision_requirement = "请按上述决策步骤选出最终追随对象，或选择中立。"
            output_format = cls.FOLLOWER_VOTE_OUTPUT
        else:
            raise ValueError(f"未知的决策类型: {decision_type}")

        return cls.FOLLOWER_USER_PROMPT_TEMPLATE.format(
            personal_summary=personal_summary or "【你的战略关系总览】（暂无数据）",
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
你是{agent_name}的国家领导集体，当前CINC指数为{current_total_power}（0-1比例值），实力层级为{power_level}。

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
你是{agent_name}的国家领导集体，当前CINC指数为{current_total_power}（0-1比例值），实力层级为{power_level}。

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
你是一个{agent_name}的国家领导集体，当前CINC指数为{current_total_power}（0-1比例值），实力层级为{power_level}，领导类型为{leader_type}。
当前仿真设定年份为{cinc_year}年。

【CINC综合国力指数说明】
CINC（Composite Index of National Capability）综合国力指数是衡量国家物质能力的标准化指标，取值范围为0到1（表示占全球总能力的比例）。
- 该国初始CINC指数为{initial_total_power}，当前CINC指数为{current_total_power}
- CINC指数是比例值：体系内所有国家CINC之和恒为1，任何国家指标上升意味着其他国家相对下降
- 6项底层指标：milex（军事支出）、milper（军事人员）、irst（钢铁产量）、pec（能源消耗）、tpop（总人口）、upop（城市人口）

【实力层级判定标准】（按CINC在体系内的相对排名百分位）
- 超级大国：CINC排名前5%（含）
- 大国：CINC排名前5%-15%（含）
- 中等强国：CINC排名前15%-35%（含）
- 小国：CINC排名后65%

【战略关系等级】（从敌对到友好）
1. 战争关系 - 最高烈度敌对
2. 冲突关系 - 存在明显对抗
3. 无外交关系 - 中立状态
4. 伙伴关系 - 存在合作倾向
5. 盟友关系 - 最高级别友好

【角色设定】
你需要代表国家做出追随相关的重要决策。你的领导类型会深刻影响你的追随偏好和选择逻辑。

【领导类型对追随决策的影响】
{leader_type_follower_rules}

【通用决策规则】
1. 基于全量信息池中的所有信息做出理性决策
2. 【先核对战略关系-决策第一步】评估每个候选人前，必须先在【你的战略关系总览】中核对你与该候选人的关系：
   - 战争关系：原则上不得追随（追随战争对象违反国家生存逻辑，会被国内政治力量视为投降叛国）
   - 冲突关系：应避免追随（除非追随能直接化解冲突且无其它可选）
   - 盟友/伙伴关系：可正常评估实力、利益、领导风格等其它因素
   - 注意：禁止仅凭"对方实力强"或"对方是王道型"就忽视战争/冲突关系
3. 战略关系还会传导：盟友倾向追随同一领导者，冲突方倾向避免追随同一领导者
4. 考虑历史互动模式对决策的指导作用
5. 考虑国力变化趋势对战略选择的影响
6. 参与领导竞争时，需评估自身国力是否具备竞争优势

【输出要求】
- 必须严格按照JSON格式输出
- reason字段应简洁明了，说明决策的主要依据
"""

# 追随决策的用户提示词模板（任务、上下文、数据）
    FOLLOWER_USER_PROMPT_TEMPLATE = """
{personal_summary}

【任务】
请根据以下信息做出决策。**关键提示**：作出任何"追随谁"的判断之前，必须先回头核对上方【你的战略关系总览】，禁止追随你的战争方，避免追随你的冲突方。

【全量信息池-参考资料】
1. 当前体系内所有国家信息（含战略关系，按类型分组）：
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

【候选人评估（已为你预先核对你与每位候选人的战略关系与双向互动统计）】
{candidates_evaluation}

【决策步骤-请严格按顺序执行】
1. 先排除：候选人列表中标注 ⚠️【战争关系-禁止追随】的，原则上严禁选择
2. 再警惕：标注 ⚠️【冲突关系-应避免追随】的，仅在所有其它候选人都不可选时才考虑
3. 再筛选：从盟友/伙伴/中立候选人中，按实力、领导类型、双向互动统计选择最优
4. 若无任何合适候选人：选择"中立"（在follower_agent_id字段填null）

请输出最终决策：
- 选择某个候选人：在 follower_agent_id 字段填写该国家ID
- 选择"中立"：在 follower_agent_id 字段填写 null
"""

    FOLLOWER_VOTE_OUTPUT = """
必须输出JSON格式：
{{
    "follower_agent_id": <国家ID或null>,
    "follower_agent_name": <国家名称或"中立">,
    "reason": "决策理由"
}}
"""


# Standard 20 GDELT interaction behaviors - 从 action_manager 动态导入，确保单一数据源
# 避免与 action_manager.py 中的 _STANDARD_ACTIONS 重复定义
def _build_standard_behaviors():
    """从 action_manager 动态构建 STANDARD_BEHAVIORS，确保与权威定义一致。"""
    from .action_manager import get_all_actions
    actions = get_all_actions()
    return [action.model_dump() for action in actions]


STANDARD_BEHAVIORS = _build_standard_behaviors()
