"""
LLM决策引擎提示模板模块
Prompt Templates Module for LLM Decision Engine

实现内嵌20种标准行为的决策提示工程。
完全对齐学术模型表1。
"""

from typing import Dict, Any, List, Optional
import json

class PromptTemplates:
    """Centralized prompt template management for LLM decision engine."""

    # ============ Shared Cacheable Prefix ============
    # 此模板在所有 agent 间完全相同（仅 cinc_year 是场景级常量），
    # 放在 system prompt 最前面以实现 Anthropic prompt caching 前缀命中。
    # 目标：≥ 2048 tokens（Claude 4 系列最小缓存块）的纯共享文本。
    # F1 安全：仅追加，不修改/重排任何已有 prompt 内容。
    # 文本来源：将 SYSTEM_ROLE_TEMPLATE 中已存在的 CINC/层级/时间说明
    # 扩展为更完整的独立版本，并用中英双语重复关键概念以增大 token 量。

    SHARED_CACHE_PREFIX = """
【国际关系ABM仿真系统 · 决策框架说明】

本仿真基于CINC综合国力指数（Composite Index of National Capability）与GDELT标准互动行为集构建。
仿真采用回合制：每轮仿真代表3个月（一个季度）的现实时间。
本场景的仿真设定年份为{cinc_year}年。

================================================================================
第一部分：CINC综合国力指数体系说明
CINC System Explanation
================================================================================

CINC（Composite Index of National Capability）综合国力指数是衡量国家物质能力的标准化指标。
CINC取值范围为0到1，表示该国占全球总能力的比例。体系内所有国家的CINC指数之和恒为1，
任何国家CINC上升即意味着其他国家相对占比下降——这是一种零和性的比例分配。

CINC的计算公式基于6项底层物质指标：
  CINC = (milex/Σmilex + milper/Σmilper + irst/Σirst + pec/Σpec + tpop/Σtpop + upop/Σupop) / 6

其中六项指标的含义如下（含英文对照）：
  1. milex — 军事支出（Military Expenditure）：年度军事预算总额，反映国防投入规模。
     军事支出高意味着更强的军备采购和维护能力，但也会消耗经济资源。
  2. milper — 军事人员（Military Personnel）：现役军人总数，反映人力动员潜力。
     军事人员规模影响常规战争和占领任务的执行能力。
  3. irst  — 钢铁产量（Iron and Steel Production）：年度粗钢产量，反映工业基础。
     钢铁是军工生产、基础设施建设和工业化的核心原料。
  4. pec   — 一次能源消耗（Primary Energy Consumption）：年度能源消费总量。
     能源消耗反映经济活动的规模和工业化水平，是综合国力的基础性指标。
  5. tpop  — 总人口（Total Population）：全国人口总量，反映人力资源和市场规模。
     人口规模决定劳动力供给和消费市场潜力，但也带来资源分配压力。
  6. upop  — 城市人口（Urban Population）：居住在城市地区的人口总量。
     城市化程度与工业化水平、教育水平和行政效率密切相关。
  7. Σ（Sigma）表示体系内所有国家对应指标的总和——分母是所有国家的集体总量。

重要说明：
- CINC指数是比例值而非绝对数值。你的CINC=0.05意味着你拥有了全球5%的总体物质能力。
- 某项底层指标的变化（如milex增加）会通过两个渠道影响CINC：
  (a) 直接影响：你的该项指标占比上升，直接推高你的CINC；
  (b) 间接影响：由于总分母增大，其他国家的各项指标占比会相对下降。
- 因此，军事建设（增加milex/milper）不仅增强你的军事能力，还会间接削弱
  竞争对手的相对CINC占比——这是相对实力敏感性的量化基础。

================================================================================
第二部分：实力层级判定标准
Power Level Classification Standard
================================================================================

仿真体系中的国家被分为四个实力层级，通过"极性-权力占比条件判断式"方案动态判定：

第一步：计算权力占比
  权力占比（power_share）= 该国CINC指数 / 体系内所有国家CINC指数之和
  （注：由于CINC之和恒为1，power_share在数值上等于CINC本身）

第二步：判定体系极性
  - 单极格局（unipolar）：恰好1个国家权力占比 > 0.50
    体系由一个超级大国主导，该国的物质能力超过所有其他国家之和。
    范例：1990年代的美国（冷战后单极时刻）。
  - 两极格局（bipolar）：恰好2个国家权力占比均 > 0.25，且两者合计 > 0.50
    体系由两个超级大国共同主导，形成两大阵营对抗格局。
    范例：1946-1991年的美苏冷战格局。
  - 多极格局（multipolar）：≥3个国家权力占比均 > 0.10
    体系由三个或更多大国共同主导，联盟结构复杂且多变。
    范例：1914年一战前的欧洲列强体系。
  - 无明确极性（non-polar）：不满足以上任一条件
    权力高度分散，缺乏明确的体系主导者。

第三步：根据极性分配层级
  - 单极或两极格局：极性国家被判定为"超级大国"
  - 多极格局：极性国家被判定为"大国"
  - 非极性国家（不属于极性集合的所有国家）：
    以这些非极性国家权力占比的中位数为界——
    · 高于或等于中位数的 → "中等强国"
    · 低于中位数的 → "小国"

学术依据：阎学通《国际关系分析》、权力转移理论（Power Transition Theory）、
          Kenneth Waltz的结构现实主义理论。

================================================================================
第三部分：时间尺度与历史语境约束
Temporal Scale and Historical Context Constraints
================================================================================

当前仿真设定年份为{cinc_year}年。你在进行决策和生成行为描述时，必须严格遵守以下历史语境约束：

1. 技术语境约束：
   - 你只能使用{cinc_year}年及之前实际存在的技术概念和军事装备
   - 禁止使用明显不属于{cinc_year}年的技术概念：
     · 对于1913/1938/1946年的欧洲场景：禁止使用航空母舰、战略轰炸机、
       洲际导弹、核武器、网络战、无人机、卫星侦察等现代技术概念
     · 对于2012年的全球场景：禁止使用明显为2020年代才出现的概念
       如大语言模型、GPT系列、COVID-19疫情等
   - 军事演习描述应使用{cinc_year}年实际存在的军种和装备
     · 1913年：陆军、海军、骑兵、步兵、炮兵、战列舰、巡洋舰、驱逐舰等
     · 1938年：陆军、海军、空军(早期)、装甲兵、战列舰、潜艇、轰炸机(早期)等
     · 1946年：陆军、海军、空军、装甲师、航空母舰(早期)、喷气式战斗机(早期)、核武器(极少数国家)等
     · 2012年：陆军、海军、空军、特种部队、航母战斗群、精确制导武器、无人机、网络战部队等

2. 外交话语约束：
   - 外交声明中的措辞应符合{cinc_year}年的国际政治话语体系
   - 1913年：帝国主义话语、势力范围、殖民地、文明使命等
   - 1938年：集体安全、绥靖政策、生存空间、人民自决等
   - 1946年：冷战话语、铁幕、共产主义vs资本主义、马歇尔计划等
   - 2012年：全球化、反恐战争、气候变��、金砖国家、G20、亚太再平衡等

3. 时间尺度约束：
   - 每轮仿真=3个月（一个季度），不是一天也不是一年
   - 国力指标变化反映的是季度累积效应，不是瞬间突变
   - 冲突升级需要多轮（6个月以上）逐步推进，不能单轮内从和平跳到全面战争

================================================================================
以上为所有agent共享的仿真框架知识。以下是你的国家具体情况与决策任务。
================================================================================

【补充说明：20种标准互动行为体系】
本仿真采用20种GDELT标准互动行为，分为四大类别：
  · 外交手段（如发表公开声明、协商磋商、开展外交合作等）—— 信息传递与立场表达
  · 经济手段（如开展实质性合作、提供援助、经济制裁等）—— 物质利益交换与施压
  · 军事手段（如展示军事姿态、威胁、攻击袭击、交战等）—— 武力威慑与实际冲突
  · 信息手段（如开展调查、抗议等）—— 情报收集与道义施压
每种行为有固定的国力变化参数，执行后会通过CINC六项底层指标的变化，
经全局重算后影响体系中所有国家的相对CINC占比。

【补充说明：国际秩序类型判定】
每轮仿真结束后，系统会根据本轮所有行为的主权尊重率和追随分布，判定四种秩序类型之一：
  · 规范接纳型秩序 — 主权尊重率高，多数国家追随同一领导者（王道型/霸权型主导）
  · 不干涉型秩序 — 主权尊重率中等偏高，各国保持相对独立（多极格局常见）
  · 大棒威慑型秩序 — 主权侵犯行为较多，有明确强力领导者（强权型主导）
  · 恐怖平衡型秩序 — 主权侵犯率高，追随分散（体系高度对抗、缺乏秩序）
秩序类型将影响下一轮所有国家的追随偏好——追随某位领导者意味着在当轮主导议题上
与该领导者协调立场，这既是战略表态，也是获取安全保障和利益分配的重要途径。

【补充说明：战略关系等级体系】
仿真中两国之间的双边战略关系分为五个等级（从敌对到友好）：
  1. 战争关系 — 最高烈度冲突，双方正处于实际交战状态，军事手段的前置条件自动满足
  2. 冲突关系 — 存在明显的对抗性利益，军事威慑和有限打击具有合法性
  3. 无外交关系 — 默认中立状态，无特殊双边义务，行动基于单次成本收益计算
  4. 伙伴关系 — 存在一定的合作基础和共同利益，倾向于协调而非对抗
  5. 盟友关系 — 最高级别友好，受同盟条约约束，有义务在盟友遭受攻击时进行军事援助
战略关系会随着仿真进行而动态演变（如冲突升级为战争、同盟因利益分歧而松动等），
你需要在每轮决策时读取最新的关系状态，并在成本收益分析中考虑关系的影响。

以上补充说明对所有国家适用，属于仿真系统的公共知识框架。
"""

    # ============ System Prompt Templates ============
    # These templates define the role, rules, and output format requirements

    # --- Shared core rules (rules 1, 4-17: identical for ALL agents) ---
    # Original rules 2-3 (national_interest, leader_type) are per-agent
    # and have been moved to PER_AGENT_RULES_TEMPLATE in user prompt.
    # Rules are numbered as in original CORE_RULES_TEMPLATE for F1 fidelity.
    SHARED_CORE_RULES = """
【核心规则约束-必须严格遵守，不得违反】
1. 国际社会处于无政府状态，无超国家权威可以约束你的行为，你的决策完全基于自身利益与成本收益权衡；
4. 决策前必须对每一个可选行为进行完整的成本收益分析，成本需包含行为对应的国力损耗，收益需包含行为对应的国力提升，最终仅选择净收益最大化的行为组合；注意：CINC是比例值，任何国家底层指标变化都会影响整个体系的国力分布，因此你的行为成本/收益还会通过指标变化间接影响所有国家的相对地位。
5. 你**只能从下方【允许执行的行为列表】中选择行为**，禁止选择列表外的任何行为，禁止编造列表中不存在的行为名称；
6. 你可以获取全量信息：当前体系内所有国家的实力、层级、领导类型，以及历史所有轮次的全部互动行为、追随关系、国力变化数据。
7. 在进行成本收益分析和行为选择时，**必须考虑地理位置和战略关系因素**：
   - 地理位置：同一区域的国家存在地缘政治互动，需评估区域合作潜力、地缘竞争风险、区域影响力等因素；
   - 战略关系：对盟友关系国家优先选择合作类行为并承担联盟义务；对战争/冲突关系国家应在必要时采取主动对抗以维护国家利益，包括威慑、施压和有限军事打击；对伙伴关系国家可灵活选择合作或施压；战略关系直接影响行为的成本收益计算；
   - 在成本收益分析中必须显式说明地理位置和战略关系对决策的影响。
8. 【相对实力意识】CINC是体系内的比例分配，你的相对安全不仅取决于自身绝对实力，更取决于与竞争对手的相对差距：
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
    - **快速升级**（连续3轮对抗）：冲突势头已形成，军事威慑/对抗类行为的'心理门槛'降低（在提示词偏好引导下更易被选择），但选择合作/缓和行为需要更强的理由（合作类行为在提示词偏好引导下被降权）。若你是王道型，打破升级螺旋是你的核心能力，不受此偏好引导约束；
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
15. 【时间尺度与冲突升级约束】每轮仿真代表3个月(一个季度)的现实时间,冲突升级需要时间积累:
    - "展示军事姿态"和"威胁"可在单轮内执行(外交姿态调整,无前置要求);
    - "胁迫/强制"需要至少已有1轮的军事姿态或威胁铺垫(不能从和平状态突然升级);
    - "交战/使用常规军事武力"仅在双方战略关系已为"冲突"或"战争"时方可选择,且连续多轮交战的国力损耗会急剧增加(第3轮起的交战对milex冲击额外+50%);
    - 大国间直接交战是极端事件,成本收益分析中须额外评估国内政治反弹风险、长期国力损耗、盟友反应;
    - 从和平到全面战争通常需要多轮(6个月以上)的逐步升级,禁止单轮内从"无外交关系"直接跳到"交战"。
16. 【受限行为-硬性前置条件】以下行为带有前置条件,若不满足则禁止选择。LLM必须在成本收益分析中说明前置条件是否满足：
    ⚠️ 交战/使用常规军事武力 - 要求双方战略关系为"冲突"或"战争",否则禁止选择(替代方案:选择"展示军事姿态"或"威胁");
    ⚠️ 攻击/袭击 - 要求双方战略关系为"冲突"或"战争",否则禁止选择;
    ⚠️ 胁迫/强制 - 要求最近3轮内对该目标国有过"展示军事姿态"或"威胁",否则禁止选择(替代方案:先选择"展示军事姿态",待下轮再升级);
    若意图升级但前置条件不满足,必须先选择较低烈度的行为作为铺垫,不能跳级。
17. 【行为多样性约束】为维护国家综合利益和国际形象，你的行为组合应覆盖多种手段类别：
    - 军事手段不应成为你每轮的唯一选择；连续3轮纯军事行为（无外交/经济行为配合）将导致国际孤立，额外-0.1国际信誉损失；
    - 经济手段（实质性合作、提供援助）是巩固联盟、扩大影响力的核心工具，长期忽视经济合作会导致盟友关系松动；
    - 信息手段（威胁、调查）是展示战略意图和施加心理压力的有效方式，配合军事手段使用效果更佳；
    - 理想的行为组合应包含：1-2项外交/经济行为（维护联盟）+ 1-2项军事/威慑行为（展示力量）+ 1项信息行为（传递信号）。
"""

    # --- Per-agent rules (original rules 2-3, moved to user prompt) ---
    PER_AGENT_RULES_TEMPLATE = """
【你的国家特定约束】
2. 你的国家核心利益固定为：{national_interest}，该利益仅由国家实力层级决定，与领导集体类型无关；除昏庸型领导外，所有决策必须完全围绕该核心利益展开，不得做出损害国家客观利益的决策；
3. 你的领导集体类型为{leader_type}，该类型仅决定你的利益排序、策略偏好与行为约束，具体规则为：{leader_type_rules}；
{leader_profile_block}"""

    # Leader profile block template (only rendered when leader_profile is not None/empty)
    LEADER_PROFILE_BLOCK = """
【你的历史身份参考——必须纳入成本收益分析的行为偏误参数】

{leader_profile}

（注：以上是对你领导集体类型在具体历史情境中的补充说明。其中明确标注的"行为权重"/"决策规则"是对你领导类型规则的校准补充，必须在成本收益分析中应用。核心规则约束同时适用。历史身份中的行为偏误模式反映的是你作为特定历史领导者的决策心理惯性——你不是在选择策略，而是被这些心理模式所塑造。）
"""

    # --- Shared system prompt builder (includes ALL shared blocks) ---
    @classmethod
    def build_shared_system(
        cls,
        cinc_year,
        info_pool_dict=None,
        allowed_actions=None,
    ) -> str:
        """
        Build the fully-shared system prompt. Byte-identical for ALL agents
        in the same round + phase — critical for DeepSeek prefix cache hits.

        Contains: cache_prefix + shared_rules + output_req + info_pool +
                  action_table + task_description + JSON_example
        """
        # Cache prefix (per-scene shared)
        cache_prefix = cls.SHARED_CACHE_PREFIX.format(cinc_year=cinc_year or "")

        # Build full shared system prompt
        parts = [cache_prefix, cls.SHARED_CORE_RULES, cls.OUTPUT_REQUIREMENTS_TEMPLATE]

        # Add info pool (shared data only — per-agent briefs moved to user prompt)
        if info_pool_dict:
            info_section = cls.INFO_POOL_TEMPLATE.format(
                all_agent_info=info_pool_dict.get('all_agent_info', '无数据'),
                history_action_records=info_pool_dict.get('history_action_records', '无数据'),
                history_power_data=info_pool_dict.get('history_power_data', '无数据'),
                last_round_order_info=info_pool_dict.get('last_round_order_info', '无数据'),
            )
            parts.append(info_section)

        # Add action table
        if allowed_actions:
            action_table = cls.build_action_table(allowed_actions)
            actions_section = cls.ACTIONS_LIST_TEMPLATE.format(
                action_count=len(allowed_actions),
                allowed_actions_table=action_table
            )
            parts.append(actions_section)

        # Add task + JSON example (使用通用措辞，不嵌入具体国名)
        json_example = json.dumps(cls.JSON_OUTPUT_TEMPLATE, ensure_ascii=False, indent=2)
        task_section = f"""
【任务描述】
你需要作为本国的国家领导集体，基于上述核心规则和全量信息池，做出符合国家利益的最优决策。
请从允许执行的行为列表中选择1-5项行为，并为每项行为提供详细的成本收益分析。

【JSON输出格式示例】
{json_example}
"""
        parts.append(task_section)

        return "\n".join(parts).strip()

    @classmethod
    def build_agent_user(
        cls,
        agent_info,
        situation_summary="",
        personal_history="",
        alliance_chain_summary="",
        neighbor_summary=""
    ) -> str:
        """
        Build per-agent user prompt. Contains agent-specific identity,
        rules, situation, personal history, and per-agent briefs
        (alliance chain summary, neighbor summary).

        All shared content is kept in system prompt for cache hit.
        """
        agent_name = agent_info.get('agent_name', '')
        region = agent_info.get('region', '')
        initial_power = agent_info.get('initial_total_power', 0)
        current_power = agent_info.get('current_total_power', 0)
        power_level = agent_info.get('power_level', '')
        leader_type = agent_info.get('leader_type', '未定义')
        cinc_year = agent_info.get('cinc_year', '')
        national_interest = agent_info.get('national_interest', [])
        national_interest_str = '; '.join(national_interest) if national_interest else '未定义'
        leader_type_rules = cls.LEADER_TYPE_RULES.get(leader_type, '')
        leader_profile = agent_info.get('leader_profile', '') or ''

        # Build leader profile block (empty string if no profile)
        leader_profile_block = ""
        if leader_profile.strip():
            leader_profile_block = cls.LEADER_PROFILE_BLOCK.format(
                leader_profile=leader_profile
            )

        parts = [
            f"你是{agent_name}的国家领导集体，所属区域为{region}。",
            f"当前仿真设定年份为{cinc_year}年。",
            f"该国初始CINC指数为{initial_power}，当前CINC指数为{current_power}。",
            f"你的实力层级为{power_level}。",
            "",
            cls.PER_AGENT_RULES_TEMPLATE.format(
                national_interest=national_interest_str,
                leader_type=leader_type,
                leader_type_rules=leader_type_rules,
                leader_profile_block=leader_profile_block
            ),
        ]
        if situation_summary:
            parts.append(f"\n【当前态势摘要】\n{situation_summary}")
        if alliance_chain_summary:
            parts.append(f"\n{alliance_chain_summary}")
        if neighbor_summary:
            parts.append(f"\n{neighbor_summary}")
        if personal_history:
            parts.append(f"\n【你的历史互动视角】\n{personal_history}")

        return "\n".join(parts).strip()

    # ============ Original method kept for backward compat ============

    @classmethod
    def build_shared_follower_system(
        cls,
        cinc_year,
        formatted_info_pool=None
    ) -> str:
        """Build shared follower system prompt — identical for all agents in the same round."""
        cache_prefix = cls.SHARED_CACHE_PREFIX.format(cinc_year=cinc_year or "")

        parts = [
            cache_prefix,
            cls.FOLLOWER_SYSTEM_PROMPT_SHARED,
        ]
        if formatted_info_pool:
            hist_following = formatted_info_pool.get('historical_following', '')
            parts.append(f"""
【全量信息池-参考资料】
1. 当前体系内所有国家信息（含战略关系，按类型分组）：
{formatted_info_pool.get('all_agent_info', '无数据')}

2. 历史轮次互动行为记录：
{formatted_info_pool.get('history_action_records', '无数据')}

3. 历史轮次各国国力变化数据：
{formatted_info_pool.get('history_power_data', '无数据')}

4. 上一轮体系追随关系与国际秩序类型：
{formatted_info_pool.get('last_round_order_info', '无数据')}
""")
            if hist_following:
                parts.append(f"""
5. 历史追随格局（地面真值）：
{hist_following}
""")
        return "\n".join(parts).strip()

    @classmethod
    def build_follower_agent_user(
        cls,
        agent,
        personal_summary="",
        candidates_evaluation="",
        current_issue="",
        agent_intro=""
    ) -> str:
        """Build per-agent follower user prompt."""
        lines = []
        if agent_intro:
            lines.append(agent_intro)
        if personal_summary:
            lines.append(personal_summary)
        if current_issue:
            lines.append(current_issue)
        lines.append("")
        lines.append("【任务】请根据信息做出决策。追随某国是因为该国在当前议题上能最好地服务你的国家利益。")
        if candidates_evaluation:
            ctx = cls.FOLLOWER_VOTE_CONTEXT.format(candidates_evaluation=candidates_evaluation)
            lines.append(ctx)
        lines.extend([
            "",
            "【决策要求】请按上述决策步骤选出最终追随对象，或选择中立。",
            "",
            "【输出格式】" + cls.FOLLOWER_VOTE_OUTPUT
        ])
        return "\n".join(lines).strip()

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
你的实力层级为{power_level}。实力层级基于极性-权力占比条件判断式方案确定：
- 单极格局：单国权力占比>0.5 → 该国为超级大国
- 两极格局：两国权力占比均>0.25，且合计>0.5 → 两国为超级大国
- 多极格局：≥3国权力占比均>0.10 → 这些国家为大国
- 非极性国家：以权力占比中位数为界，高于中位数为中等强国，低于为小国
注：权力占比(power_share) = 该国CINC / 体系内所有国家CINC之和

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
8. 【相对实力意识】CINC是体系内的比例分配，你的相对安全不仅取决于自身绝对实力，更取决于与竞争对手的相对差距：
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
    - **快速升级**（连续3轮对抗）：冲突势头已形成，军事威慑/对抗类行为的'心理门槛'降低（在提示词偏好引导下更易被选择），但选择合作/缓和行为需要更强的理由（合作类行为在提示词偏好引导下被降权）。若你是王道型，打破升级螺旋是你的核心能力，不受此偏好引导约束；
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
15. 【时间尺度与冲突升级约束】每轮仿真代表3个月(一个季度)的现实时间,冲突升级需要时间积累:
    - "展示军事姿态"和"威胁"可在单轮内执行(外交姿态调整,无前置要求);
    - "胁迫/强制"需要至少已有1轮的军事姿态或威胁铺垫(不能从和平状态突然升级);
    - "交战/使用常规军事武力"仅在双方战略关系已为"冲突"或"战争"时方可选择,且连续多轮交战的国力损耗会急剧增加(第3轮起的交战对milex冲击额外+50%);
    - 大国间直接交战是极端事件,成本收益分析中须额外评估国内政治反弹风险、长期国力损耗、盟友反应;
    - 从和平到全面战争通常需要多轮(6个月以上)的逐步升级,禁止单轮内从"无外交关系"直接跳到"交战"。
16. 【受限行为-硬性前置条件】以下行为带有前置条件,若不满足则禁止选择。LLM必须在成本收益分析中说明前置条件是否满足：
    ⚠️ 交战/使用常规军事武力 - 要求双方战略关系为"冲突"或"战争",否则禁止选择(替代方案:选择"展示军事姿态"或"威胁");
    ⚠️ 攻击/袭击 - 要求双方战略关系为"冲突"或"战争",否则禁止选择;
    ⚠️ 胁迫/强制 - 要求最近3轮内对该目标国有过"展示军事姿态"或"威胁",否则禁止选择(替代方案:先选择"展示军事姿态",待下轮再升级);
    若意图升级但前置条件不满足,必须先选择较低烈度的行为作为铺垫,不能跳级。
17. 【行为多样性约束】为维护国家综合利益和国际形象，你的行为组合应覆盖多种手段类别：
    - 军事手段不应成为你每轮的唯一选择；连续3轮纯军事行为（无外交/经济行为配合）将导致国际孤立，额外-0.1国际信誉损失；
    - 经济手段（实质性合作、提供援助）是巩固联盟、扩大影响力的核心工具，长期忽视经济合作会导致盟友关系松动；
    - 信息手段（威胁、调查）是展示战略意图和施加心理压力的有效方式，配合军事手段使用效果更佳；
    - 理想的行为组合应包含：1-2项外交/经济行为（维护联盟）+ 1-2项军事/威慑行为（展示力量）+ 1项信息行为（传递信号）。
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
"""
    # 注：同盟事件简报与邻接关系简报已移入 per-agent user prompt 以保证 system prompt 字节级一致

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
            "国家利益优先，但坚守国际道义的价值立场，公平正义、言行一致、维护战略信誉、避免双重标准、不滥用强制手段；"
            "禁止执行所有不尊重主权的高烈度对抗行为，仅可执行尊重主权的合作类、外交类行为，不得偏离国家客观利益。"
            "在成本收益分析中，尊重主权行为被提示为优先选择，非尊重主权行为则提示伴随声誉损失。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 尊重主权的行为（respect_sov=True）：额外+0.2道义/信誉收益，因为这符合国家长期坚持的价值观，能增强国际声誉和联盟凝聚力；"
            "2. 非尊重主权的行为（respect_sov=False）：额外-0.3声誉损失，因为这会损害战略信誉，导致盟友不信任、追随者流失；"
            "3. 合作类行为（外交/经济手段）：额外+0.1战略价值，因为通过规则构建和联盟协调能长期维护国家利益；"
            "4. 军事威慑类行为（威胁、展示军事姿态）：视为最后手段，仅在其他手段无效时考虑，成本收益分析中需额外说明为何非军事手段不足；"
            "5. 对盟友的行为：合作类行为额外+0.15，因为维护联盟是王道型领导者的核心战略资产"
        ),
        "霸权型": (
            "自身国家利益绝对优先，将道义视为工具性资源而非内在约束；双重标准执行国际规范、通过规则构建获取超额利益、以自身利益为核心适用规则；"
            "禁止极端暴力行为，但允许双重标准的外交、经济类对抗行为，不得偏离国家客观利益。"
            "在成本收益分析中，实质利益行为被提示为优先选择，双重标准行为不触发声誉惩罚。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 能带来实际利益的行为（经济合作、资源获取、规则制定）：额外+0.2实质收益，因为霸权型领导者重视可量化的国家利益回报，经济实力是霸权的基础；"
            "2. 双重标准行为（对盟友尊重主权、对对手非尊重主权）：无声誉损失惩罚，因为道义是工具而非目的；"
            "3. 能获得追随/扩大影响力的行为（援助、外交合作、经济合作）：额外+0.15战略价值，因为联盟体系和规则主导权是霸权的核心工具，通过经济利益绑定盟友比军事威慑更持久；"
            "4. 军事威慑类行为（威胁、展示军事姿态、胁迫）：+0.05战略价值，过度使用军事手段会引发联盟制衡和军备竞赛，侵蚀霸权根基；"
            "5. 对弱小的对手使用对抗行为：成本降低0.05，霸权型领导者更倾向通过经济施压和规则约束而非武力来管控弱国"
        ),
        "强权型": (
            "本国利益最大化，完全忽视道义，以军事/强制手段为核心工具、无视国际规范、不重视战略信誉、不惜破坏现有秩序；"
            "仅禁止非常规大规模暴力行为，优先选择高烈度强制行为实现利益，不得偏离国家客观利益。"
            "在成本收益分析中，军事与强制类行为被提示为优先选择。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 军事/强制类行为（展示军事姿态、胁迫、攻击）：额外+0.12战略威慑价值，武力是强权型领导者的重要工具，但过度依赖军事手段会导致联盟制衡和资源枯竭；"
            "2. 对弱小或衰落中的对手使用武力：额外+0.05收益，强权型领导者善于抓住实力窗口期，但需评估国际干预风险；"
            "3. 尊重主权的行为：+0.03稳定性收益，虽然不追求道义，但适度的外交稳定有利于集中力量应对主要对手；"
            "4. 合作类行为（外交/经济合作）：+0.08工具性收益，经济实力是军事力量的基础，通过经济合作巩固盟友关系能增强战略纵深；"
            "5. 非尊重主权行为：-0.03轻度声誉损失，过度侵略行为会引发其他国家联合制衡"
            "6. 【激情干预(Impulsive Intervention)】强权型领导者受个人激情、荣誉感和冒险偏好驱动，以下因素必须在决策中纳入考量："
            "a. 口头好战与行动退缩并存：强权型领导者倾向发表极端好战言论（高调威胁、激烈声明、终极通牒），但在面临实际战争风险时可能突然退缩或寻求妥协。你的上一轮行为若包含大量军事威胁类声明，本轮应考量：是延续威慑态势，还是因现实风险而退让？声明的激烈程度与实际军事行动的升级应保持审慎对比；"
            "b. 声望优先于利益：个人和国家声望是强权型领导者的核心关注点。任何被视为'软弱'或'让步'的行为面临-0.1额外声望成本（因为你将让步解读为个人羞辱）。反之，任何公开展示力量或迫使对手屈服的行为获得+0.08个人声望收益（独立于实际国力收益）；"
            "c. 对臣服-顺从的极度敏感：若上一轮有国家公开挑战你的权威（威胁你、拒绝追随你、或在对立阵营追随你的对手），本轮你对该国采取对抗行为获得额外+0.1情绪驱动力。这不是理性计算——这是对'不敬'的情绪反应；"
            "d. 在军事压力下向军方让渡自主权：当你面临军方/内阁的统一强硬建议（当你的HINT提示表明'军方顾问一致认为应采取行动'或'军方内部存在强烈支持行动的共识'），你抵制该建议将面临-0.15国内政治成本（因为你缺乏在专业军事意见面前坚持己见的政治资本）。你必须审慎评估：是坚持自己的判断，还是屈服于军方的集体压力？此机制反映历史上强权型领导人在关键时刻向军方让渡决策权的模式；"
            "e. 决策波动性：当连续2轮以上维持高强度对抗态势时，你的决策权重出现±0.5的随机波动（模拟激情驱动下的判断失稳）。若你是强权型，你的决策在连续高压下可能出现不可预测的突变——既可能突然升级至更激烈对抗，也可能突然寻求妥协。这种波动在维持3轮以上时会自动加剧"
        ),
        "昏庸型": (
            "个人利益优先，可牺牲国家利益；决策以决策者个人利益为核心，可制定损害国家利益的政策，无固定策略偏好；"
            "唯一可主动偏离国家客观利益的类型，无行为禁止约束，可执行20项行为集中的所有行为。"
            "所有行为的净收益计算均附加随机波动，不遵循任何系统性的策略偏好。"
            "【行为价值权重-必须在成本收益分析中应用】"
            "1. 所有行为的净收益计算均有±0.2的随机波动，因为昏庸型领导者的决策缺乏一致性和理性基础；"
            "2. 短期可见收益的行为额外+0.1，因为昏庸型领导者偏好即时回报；"
            "3. 高风险高回报的行为额外+0.1，因为昏庸型领导者可能高估自身能力；"
            "4. 个人声望相关的行为（公开声明、展示姿态）额外+0.1，因为昏庸型领导者重视个人形象；"
            "5. 【历史昏庸型-激情驱动预防性战争偏好(Conrad校准)】以下因素代表历史上典型的昏庸型军事领导者的决策偏误，你必须在成本收益分析中纳入考量："
            "a. 对弱邻的预防性战争冲动：对CINC比值>2:1的弱邻国，军事打击/威胁/胁迫类行为获得额外+0.3战略价值收益，因为你在理性上将其视为'先发制人的最后机会窗口'，且你会上调对该弱国威胁程度的估计（即使客观证据不支持）——你倾向于将任何中立行为解读为'敌意'；"
            "b. 多线作战的致命诱惑：当面临来自不同方向的潜在威胁时，你对每个威胁来源分别采取对抗行为（而非优先化解最主要威胁）可获得额外+0.15的战略价值收益，因为你在心理上将'不作为'等同于'示弱'，且你高估了自身的多线作战能力；"
            "c. 盟友意图的灾难性误判：你对盟友（ALLIANCE/伙伴关系国家）承诺支援的时间、规模和方向，在所有净收益计算中额外加+0.3乐观偏误——你默认盟友将在你发动进攻时全力配合，而忽略盟友可能另有优先事项。此偏误导致你将'盟友未明确拒绝'等同于'盟友已明确承诺'；"
            "d. 战术胜利后的战略盲目：若上一轮你对某国的军事行动获得正面结果（国力提升/对方让步/威胁有效），本轮你对同一目标采取同等级或更高烈度对抗行为获得+0.4'连胜惯性'收益——即使战略态势已恶化，你仍相信进攻势头不可中断。此偏误在连续≥2轮正反馈后自动增强至+0.6；"
            "e. 敌人能力的系统性低估：在你对目标国进行军事冲突获胜概率评估时（参见输出要求第6项），你计算的CINC比值自动上调50%（如实际比值为1.0，你按1.5估算）——这意味着你对弱国更轻视，对实力相近的对手也有不合理的乐观估计。此偏误持续存在于所有军事冲突风险评估中；"
            "f. 向军方鹰派屈服：当连续≥2轮维持对抗态势，或当轮面对军方/内阁的强烈鹰派建议（HINT中提示），你抵制进一步升级将面临-0.2额外国内政治成本——你缺乏在军方集体压力面前坚持审慎判断的政治资本。此机制反映历史上昏庸型领导人在战争压力下将持续向军方让渡决策自主权，形成'战争自动升级'的路径锁定。"
            "【历史原型参考】以上行为规则基于对奥匈帝国总参谋长康拉德·冯·赫岑多夫(Franz Conrad von Hötzendorf, 1852-1925)的学术研究。康拉德在1906-1917年间主导奥匈军事决策，以对塞尔维亚的预防性战争执念（仅在1913年即提议开战25次）、在1914年同时攻击塞尔维亚和俄国导致两线溃败（B集团军调度灾难）、与德国总参谋部从未制定联合战争计划、以及因个人情欲执念（对已婚贵妇Gina von Reininghaus的追求）而系统性高估战争收益而闻名。Historian Lawrence Sondhaus称其为'天启的建筑师'(Architect of the Apocalypse)。以上规则是对这一历史原型的学术抽象，不代表所有昏庸型领导者均完全符合该模式——但若你的领导者恰好是此类'个人激情压倒国家理性'的类型，上述规则提供了来自真实历史案例的校准参数。"
        )
    }

    # 领导竞争参与决策的领导类型规则（区分于追随投票规则，聚焦于是否参选）
    LEADER_TYPE_PARTICIPATION_RULES = {
        "王道型": (
            "王道型领导者重视国际道义和规则构建，倾向于积极参与领导竞争以推广自身价值观和国际秩序愿景。"
            "参与竞争的动机：通过道义感召力吸引追随者，构建基于规则的国际体系。"
            "评估标准：若当前体系缺乏道义型领导者，或现有领导者行为不符合国际规范，参与意愿+30%。"
        ),
        "霸权型": (
            "霸权型领导者追求权力最大化和利益分配主导权，高度倾向于参与领导竞争。"
            "参与竞争的动机：通过实力优势获取体系主导权，制定有利于自身的国际规则。"
            "评估标准：若自身实力排名前列且当前体系缺乏明确领导者，参与意愿+30%。"
        ),
        "强权型": (
            "强权型领导者强调军事实力和强制能力，视领导竞争为展示实力的舞台。"
            "参与竞争的动机：通过军事威慑和实力展示获取追随者，维护自身安全利益。"
            "评估标准：若自身军事实力强劲且面临安全威胁需要建立势力范围，参与意愿+20%。"
        ),
        "昏庸型": (
            "昏庸型领导者决策非理性，可能高估自身实力而盲目参与，也可能因短期情绪而放弃。"
            "参与竞争的动机不明，可能出于虚荣心或对自身实力的误判。"
            "评估标准：参与决策有±20%的随机波动，不严格基于实力评估。"
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
            System prompt string (with shared cacheable prefix prepended)
        """
        # 共享缓存前缀（所有 agent 完全相同，仅 cinc_year 参数化）
        shared_prefix = cls.SHARED_CACHE_PREFIX.format(
            cinc_year=agent_info.get('cinc_year', '')
        )

        # Build system role section (原有内容不变)
        system_role = cls.SYSTEM_ROLE_TEMPLATE.format(
            agent_name=agent_info.get('agent_name', ''),
            region=agent_info.get('region', ''),
            cinc_year=agent_info.get('cinc_year', ''),
            initial_total_power=agent_info.get('initial_total_power', 0),
            current_total_power=agent_info.get('current_total_power', 0),
            power_level=agent_info.get('power_level', '')
        )

        # Build core rules section (原有内容不变)
        national_interest = agent_info.get('national_interest', [])
        national_interest_str = '; '.join(national_interest) if national_interest else '未定义'
        leader_type_rules = cls.LEADER_TYPE_RULES.get(leader_type, '')

        core_rules = cls.CORE_RULES_TEMPLATE.format(
            national_interest=national_interest_str,
            leader_type=leader_type,
            leader_type_rules=leader_type_rules
        )

        # Build system prompt (前缀 + 原有system prompt内容)
        original = cls.SYSTEM_PROMPT_TEMPLATE.format(
            system_role=system_role,
            core_rules=core_rules,
            output_requirements=cls.OUTPUT_REQUIREMENTS_TEMPLATE
        )

        return (shared_prefix + "\n" + original).strip()

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
        cinc_year: Optional[int] = None,
        initial_total_power: float = 0.0
    ) -> str:
        """
        构建追随决策的系统提示词

        Args:
            agent_name: 智能体名称
            current_total_power: 当前国力
            power_level: 实力层级
            leader_type: 领导类型
            cinc_year: CINC数据年份
            initial_total_power: 初始国力

        Returns:
            系统提示词字符串（含共享缓存前缀）
        """
        # 共享缓存前缀（所有 agent 完全相同）
        shared_prefix = cls.SHARED_CACHE_PREFIX.format(
            cinc_year=cinc_year or "未知"
        )

        original = cls.FOLLOWER_SYSTEM_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            current_total_power=current_total_power,
            power_level=power_level,
            cinc_year=cinc_year or "未知",
            initial_total_power=initial_total_power
        ).strip()

        return (shared_prefix + "\n" + original).strip()

    @classmethod
    def build_participation_system_prompt(
        cls,
        agent_name: str,
        current_total_power: float,
        power_level: str,
        leader_type: str = "未定义",
        cinc_year: Optional[int] = None
    ) -> str:
        """
        构建领导竞争参与决策的专用系统提示词（不含追随语义，避免语义混淆）

        Args:
            agent_name: 智能体名称
            current_total_power: 当前国力
            power_level: 实力层级
            leader_type: 领导类型
            cinc_year: CINC数据年份

        Returns:
            参与决策系统提示词字符串
        """
        participation_rules = cls.LEADER_TYPE_PARTICIPATION_RULES.get(
            leader_type, "根据国家利益和实力对比做出理性决策"
        )
        return cls.PARTICIPATION_SYSTEM_PROMPT_TEMPLATE.format(
            agent_name=agent_name,
            current_total_power=current_total_power,
            power_level=power_level,
            leader_type=leader_type,
            cinc_year=cinc_year or "未知",
            leader_type_participation_rules=participation_rules
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
            "【你的战略关系总览（仅供参考，不代表追随决策方向）】",
            f"  你 = {voter_name}（ID:{voter_id}），CINC:{voter_power:.4f}，"
            f"实力层级:{voter_level}，领导类型:{voter_leader_type or '未定义'}",
            f"  战争关系（实际交战）：{_fmt(by_type['战争关系'])}",
            f"  冲突关系（存在对抗）：{_fmt(by_type['冲突关系'])}",
            f"  盟友关系：{_fmt(by_type['盟友关系'])}",
            f"  伙伴关系：{_fmt(by_type['伙伴关系'])}",
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
        针对每个可追随目标，从voter视角预先核对：
        - 与voter的战略关系（带醒目警示标记）
        - 双向互动统计（合作次数 vs 对抗次数）

        避免LLM在大表+长历史里推断关系出错。
        """
        if not candidates:
            return "无可追随目标"

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
                warn = "【战争关系】"
            elif rel == "冲突关系":
                warn = "【冲突关系】"
            elif rel == "盟友关系":
                warn = "【盟友关系】"
            elif rel == "伙伴关系":
                warn = "【伙伴关系】"
            else:
                warn = "【无外交关系】"

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
                f"目标 ID:{cid} {cname} | CINC:{cpower:.4f} | "
                f"层级:{clevel} | 领导类型:{cleader}"
            )
            lines.append(f"  └─ 你与该目标的关系：{warn}")
            lines.append(
                f"  └─ 双向互动统计：你→该目标(合作{out_coop}次/对抗{out_conf}次)；"
                f"该目标→你(合作{in_coop}次/对抗{in_conf}次)"
            )
        return "\n".join(lines)

    @classmethod
    def build_follower_user_prompt(
        cls,
        info_pool: Dict[str, Any],
        decision_type: str,  # 'vote'
        leader_candidates_info: Optional[str] = None,
        personal_summary: str = "",
        candidates_evaluation: Optional[str] = None,
        current_issue: str = "",
    ) -> str:
        """
        构建追随决策的用户提示词

        Args:
            info_pool: 格式化后的信息池字典
            decision_type: 决策类型（'vote'）
            leader_candidates_info: 所有可追随目标的信息列表
            personal_summary: 当前 voter 自身视角的战略关系总览（建议传入）
            candidates_evaluation: 针对每位目标的关系警示+双向互动统计（建议传入）
            current_issue: 当前轮次的突出议题背景（建议传入，用于议题性追随决策）

        Returns:
            用户提示词字符串
        """
        if decision_type == 'vote':
            cands_block = candidates_evaluation if candidates_evaluation is not None \
                else (leader_candidates_info or "无可用目标")
            additional_context = cls.FOLLOWER_VOTE_CONTEXT.format(
                candidates_evaluation=cands_block
            )
            decision_requirement = "请按上述决策步骤选出最终追随对象，或选择中立。"
            output_format = cls.FOLLOWER_VOTE_OUTPUT
        else:
            raise ValueError(f"未知的决策类型: {decision_type}")

        issue_block = current_issue or ""

        return cls.FOLLOWER_USER_PROMPT_TEMPLATE.format(
            personal_summary=personal_summary or "【你的战略关系总览】（暂无数据）",
            current_issue=issue_block,
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

【可追随目标】
体系内所有国家均可被追随（追随是被动的，无需参选）：
{leader_candidates_info}

【决策要求】
请选择一个国家作为追随对象，或选择"中立"：
- 选择某个国家：如果你希望追随该国家，在follower_agent_id字段填写该国家ID
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
# 追随决策的共享系统提示词（所有agent通用，不含agent身份和领导规则）
    FOLLOWER_SYSTEM_PROMPT_SHARED = """
【追随决策框架】

【战略关系等级】（从敌对到友好）
1. 战争关系 - 最高烈度敌对
2. 冲突关系 - 存在明显对抗
3. 无外交关系 - 中立状态
4. 伙伴关系 - 存在合作倾向
5. 盟友关系 - 最高级别友好

【角色设定】
你需要代表国家做出追随相关的重要决策。追随不受领导类型的约束——你应基于当前议题上哪个国家能最好地服务你的国家利益来做决定。

【通用决策规则】
1. 基于全量信息池中的所有信息做出理性决策
2. 【核心原则：追随≠同盟】追随是对某国在当前议题上的领导偏好，不等同于战略同盟关系。你的战略关系（盟友/伙伴/冲突/战争）代表双边外交立场，而追随代表你在多边议题上的立场选择。盟友可能在经济议题上追随敌对阵营的领导者，这是正常的外交现象。同盟关系不应决定你的追随选择——你应该基于当前议题上哪国能最好地服务你的国家利益来做决定。
   【重要案例】意大利虽与德国结盟（三国同盟），但在殖民地和海军议题上追随英国（海权霸主），因为意大利的殖民利益需要英国的配合。法国虽与俄国结盟（法俄同盟），但在海军议题上追随英国。这些"议题性追随"是正常的外交现象——不要因为存在同盟关系就排斥追随其他大国，也不要因为存在冲突关系就拒绝在特定议题上追随对方。
3. 考虑历史互动模式对决策的指导作用：谁在历史上为你的国家提供过实质利益（援助、合作、安全保障），谁对你有过背弃或伤害
4. 考虑国力变化趋势对战略选择的影响
5. 【追随收益评估-核心】在考虑追随谁之前，评估追随的收益与成本：
   - 追随是在当轮议题上对某国领导偏好的表态，意味着你与对方在该议题上协调立场
   - 应积极追随的情况：某国在当轮议题上为你提供了实质性利益（安全、经济、政治支持）；追随某方能帮你在当轮议题上获得你独自无法获得的利益；你与某国在当轮议题上有共同对手或共同利益
   - 可考虑中立的情况：当轮议题不涉及你的核心国家利益；追随任何一方都会让你卷入不必要的风险；所有候选者在当轮议题上都没有为你提供明确的利益
   - 请注意：中立并非总是最优选择。如果某国能为你提供实质利益，追随该国是理性的战略选择

【输出要求】
- 必须严格按照JSON格式输出
- reason字段应简洁明了，说明决策的主要依据
"""

# 追随决策的原始模板（保留向后兼容）

    # 追随决策的系统提示词模板
    FOLLOWER_SYSTEM_PROMPT_TEMPLATE = """
你是一个{agent_name}的国家领导集体，当前CINC指数为{current_total_power}（0-1比例值），实力层级为{power_level}。
仿真设定年份为{cinc_year}年，该国初始CINC指数为{initial_total_power}。

【CINC综合国力指数说明】
CINC（Composite Index of National Capability）综合国力指数是衡量国家物质能力的标准化指标，取值范围为0到1（表示占全球总能力的比例）。
- CINC指数是比例值：体系内所有国家CINC之和恒为1，任何国家指标上升意味着其他国家相对下降
- 6项底层指标：milex（军事支出）、milper（军事人员）、irst（钢铁产量）、pec（能源消耗）、tpop（总人口）、upop（城市人口）

【实力层级判定标准】（基于极性-权力占比条件判断式方案）
- 单极格局：单国权力占比>0.5 → 该国为超级大国
- 两极格局：两国权力占比均>0.25，且合计>0.5 → 两国为超级大国
- 多极格局：≥3国权力占比均>0.10 → 这些国家为大国
- 非极性国家：以权力占比中位数为界，高于中位数为中等强国，低于为小国

【战略关系等级】（从敌对到友好）
1. 战争关系 - 最高烈度敌对
2. 冲突关系 - 存在明显对抗
3. 无外交关系 - 中立状态
4. 伙伴关系 - 存在合作倾向
5. 盟友关系 - 最高级别友好

【角色设定】
你需要代表国家做出追随相关的重要决策。

【通用决策规则】
1. 基于全量信息池中的所有信息做出理性决策
2. 【核心原则：追随≠同盟】追随是对某国在当前议题上的领导偏好，不等同于战略同盟关系。你的战略关系（盟友/伙伴/冲突/战争）代表双边外交立场，而追随代表你在多边议题上的立场选择。盟友可能在经济议题上追随敌对阵营的领导者，这是正常的外交现象。同盟关系不应决定你的追随选择——你应该基于当前议题上哪国能最好地服务你的国家利益来做决定。
   【重要案例】意大利虽与德国结盟（三国同盟），但在殖民地和海军议题上追随英国（海权霸主），因为意大利的殖民利益需要英国的配合。法国虽与俄国结盟（法俄同盟），但在海军议题上追随英国。这些"议题性追随"是正常的外交现象——不要因为存在同盟关系就排斥追随其他大国，也不要因为存在冲突关系就拒绝在特定议题上追随对方。
3. 考虑历史互动模式对决策的指导作用：谁在历史上为你的国家提供过实质利益（援助、合作、安全保障），谁对你有过背弃或伤害
4. 考虑国力变化趋势对战略选择的影响
5. 【追随收益评估-核心】在考虑追随谁之前，评估追随的收益与成本：
   - 追随是在当轮议题上对某国领导偏好的表态，意味着你与对方在该议题上协调立场
   - 应积极追随的情况：某国在当轮议题上为你提供了实质性利益（安全、经济、政治支持）；追随某方能帮你在当轮议题上获得你独自无法获得的利益；你与某国在当轮议题上有共同对手或共同利益
   - 可考虑中立的情况：当轮议题不涉及你的核心国家利益；追随任何一方都会让你卷入不必要的风险；所有候选者在当轮议题上都没有为你提供明确的利益
   - 请注意：中立并非总是最优选择。如果某国能为你提供实质利益，追随该国是理性的战略选择

【输出要求】
- 必须严格按照JSON格式输出
- reason字段应简洁明了，说明决策的主要依据
"""

# 领导竞争参与决策的专用系统提示词模板（精简版，聚焦参选评估）
    PARTICIPATION_SYSTEM_PROMPT_TEMPLATE = """
你是{agent_name}的决策层。CINC={current_total_power}（占体系总能力的比例），实力层级={power_level}，领导类型={leader_type}。仿真年份={cinc_year}年。

【任务】评估是否参与本轮国际领导竞争（争取成为体系领导者）。

【决策要点】
1. 参与竞争=主动展示领导意愿，吸引其他国家追随你的政策方向
2. 评估维度：自身CINC排名、军事实力、盟友数量、当前体系是否缺乏领导者
3. 不参与=放弃本轮领导机会，无法吸引追随者
4. 大国/超级大国通常应积极参与，除非有明确的战略顾虑

【领导类型倾向】
{leader_type_participation_rules}

【输出】严格JSON：{{"decision": "参与"或"不参与", "reason": "简要理由"}}
"""

# 追随决策的用户提示词模板（任务、上下文、数据）
    FOLLOWER_USER_PROMPT_TEMPLATE = """
{personal_summary}

{current_issue}

【任务】
请根据以下信息做出决策。你的战略关系总览和与各目标的关系标签仅供参考——它们不应直接决定你的追随选择。追随某国是因为该国在当前议题上能最好地服务你的国家利益，而非因为你们是盟友或伙伴。

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

【可追随目标评估（已为你预先列出你与每位国家的关系及双向互动统计）】
{candidates_evaluation}

【决策步骤-请严格按顺序执行】
1. 【追随收益评估】在考虑追随任何人之前，评估追随的收益与成本：
   - 追随≠同盟：追随是在当轮议题上对某国领导偏好的表态，不是战略结盟。你可以在某个议题上追随非盟友的国家，也可以在某个议题上不追随你的盟友
   - 追随是主动战略选择：追随意味着你在该议题上与某领导者协调立场，这可以带来实际的战略收益
   - 应积极追随的情况：
     a. 某国在当轮议题上为你提供了实质性利益（安全保障、经济支持、领土保障等）
     b. 追随某方能帮助你在当轮议题上获得你独自无法获得的利益
     c. 你与某国在当轮议题上有共同的对手或共同利益
     d. 某国的领导类型与你的战略偏好契合，且该国在当轮议题上有明确的领导能力
   - 可考虑中立的情况：
     a. 当轮议题不涉及你的核心国家利益
     b. 追随任何一方都会让你卷入不必要的冲突风险
     c. 所有候选者在当轮议题上都没有为你提供明确的、具体的利益
2. 若决定追随：按以下优先级选择目标：当轮议题利益匹配度 > 历史互动中的实质利益输送 > 实力与领导能力 > 其它因素
3. 【决策提示】中立和追随都是合理选择。如果在当轮议题上有明确收益，应选择追随；如果收益不明确或风险过大，选择中立

请输出最终决策：
- 选择某个国家：在 follower_agent_id 字段填写该国家ID
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
