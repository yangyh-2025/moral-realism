"""
Prompt模板引擎 - 对应技术方案3.2.3节

提供多场景Prompt模板、变量注入、格式控制等功能。

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field
import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import OrderedDict
from config.leader_types import LeaderType

class PromptTemplate(str, Enum):
    """
    Prompt模板类型枚举

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    LEADER_DECISION = "leader_decision"                      # 领导人决策模板
    STATE_FOLLOWUP = "state_followup"                       # 国家跟进决策模板
    ALLIANCE_INVITATION = "alliance_invitation"              # 联盟邀请模板
    ALLIANCE_RESPONSE = "alliance_response"                  # 联盟响应模板
    GLOBAL_EVENT_RESPONSE = "global_event_response"          # 全球事件响应模板
    FINAL_JUDGMENT = "final_judgment"                      # 最终判断模板
    SITUATION_ASSESSMENT = "situation_assessment"            # 局势评估模板
    POWER_BALANCE_EVALUATION = "power_balance_evaluation"    # 实力平衡评估模板
    INFLUENCE_ANALYSIS = "influence_analysis"               # 影响力分析模板
    RULE_VALIDATION = "rule_validation"                      # 规则验证模板
    CONSTRAINT_CHECK = "constraint_check"                    # 约束检查模板

    # 发言模板类型
    DIPLOMATIC_STATEMENT = "diplomatic_statement"            # 外交声明模板
    ALLIANCE_SPEECH = "alliance_speech"                     # 联盟发言模板
    EVENT_RESPONSE_SPEECH = "event_response_speech"          # 事件响应发言模板
    CRISIS_COMMUNICATION = "crisis_communication"            # 危机沟通模板
    ORG_DECLARATION = "org_declaration"                     # 国际组织声明模板

# 模板类型中文描述
TEMPLATE_DESCRIPTION_CN = {
    PromptTemplate.LEADER_DECISION: "领导人决策模板",
    PromptTemplate.STATE_FOLLOWUP: "国家跟进决策模板",
    PromptTemplate.ALLIANCE_INVITATION: "联盟邀请模板",
    PromptTemplate.ALLIANCE_RESPONSE: "联盟响应模板",
    PromptTemplate.GLOBAL_EVENT_RESPONSE: "全球事件响应模板",
    PromptTemplate.FINAL_JUDGMENT: "最终判断模板",
    PromptTemplate.SITUATION_ASSESSMENT: "局势评估模板",
    PromptTemplate.POWER_BALANCE_EVALUATION: "实力平衡评估模板",
    PromptTemplate.INFLUENCE_ANALYSIS: "影响力分析模板",
    PromptTemplate.RULE_VALIDATION: "规则验证模板",
    PromptTemplate.CONSTRAINT_CHECK: "约束检查模板",
    PromptTemplate.DIPLOMATIC_STATEMENT: "外交声明模板",
    PromptTemplate.ALLIANCE_SPEECH: "联盟发言模板",
    PromptTemplate.EVENT_RESPONSE_SPEECH: "事件响应发言模板",
    PromptTemplate.CRISIS_COMMUNICATION: "危机沟通模板",
    PromptTemplate.ORG_DECLARATION: "国际组织声明模板",
}

class TemplateVersion(BaseModel):
    """
    模板版本信息

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    version: str
    created_at: datetime
    description: str

class TemplateStatistics(BaseModel):
    """
    模板使用统计

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    template_type: PromptTemplate
    call_count: int = 0
    avg_token_count: float = 0.0
    last_used: Optional[datetime] = None
    success_rate: float = 1.0

class PromptBuilder:
    """
    Prompt构建流水线

    支持链式调用，逐步构建复杂Prompt

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, template: PromptTemplate, context: Optional[Dict[str, Any]] = None):
        """
        Args:
            template: 使用的模板类型
            context: 初始上下文变量
        """
        self.template = template
        self.context = context or {}
        self.system_messages = []
        self.memory_context = []
        self.variables = {}
        self._max_tokens = 4096
        self._built = False

    def add_variable(self, key: str, value: Any) -> "PromptBuilder":
        """
        添加单个变量

        Args:
            key: 变量名
            value: 变量值

        Returns:
            self，支持链式调用
        """
        self.variables[key] = value
        return self

    def add_variables(self, variables: Dict[str, Any]) -> "PromptBuilder":
        """
        添加多个变量

        Args:
            variables: 变量字典

        Returns:
            self，支持链式调用
        """
        self.variables.update(variables)
        return self

    def add_system_message(self, content: str) -> "PromptBuilder":
        """
        添加系统消息

        Args:
            content: 系统消息内容

        Returns:
            self，支持链式调用
        """
        self.system_messages.append(content)
        return self

    def add_memory_context(self, memory: List[Dict], max_items: int = 10) -> "PromptBuilder":
        """
        添加记忆上下文

        Args:
            memory: 记忆列表
            max_items: 最大记忆条目数

        Returns:
            self，支持链式调用
        """
        # 只保留最近的记忆条目
        self.memory_context = memory[-max_items:] if memory else []
        return self

    def set_max_tokens(self, max_tokens: int) -> "PromptBuilder":
        """
        设置最大token限制

        Args:
            max_tokens: 最大token数

        Returns:
            self，支持链式调用
        """
        self._max_tokens = max_tokens
        return self

    def build(self) -> str:
        """
        构建最终Prompt

        Returns:
            完整的Prompt字符串
        """
        if self._built:
            raise RuntimeError("Prompt已经构建完成，不能重复调用build()")

        # 合并所有上下文
        full_context = {**self.context, **self.variables}

        # 构建Prompt
        prompt_parts = []

        # 1. 添加系统消息
        if self.system_messages:
            prompt_parts.append("# 系统指令")
            for msg in self.system_messages:
                prompt_parts.append(msg)
            prompt_parts.append("")

        # 2. 添加记忆上下文
        if self.memory_context:
            prompt_parts.append("# 历史记忆")
            for i, mem in enumerate(self.memory_context, 1):
                if isinstance(mem, dict):
                    mem_type = mem.get('type', 'action')
                    content = mem.get('content', '')
                    if mem_type == 'decision':
                        prompt_parts.append(f"[决策{i}] {content}")
                    elif mem_type == 'speech':
                        prompt_parts.append(f"[发言{i}] {content}")
                    elif mem_type == 'action':
                        prompt_parts.append(f"[行动{i}] {content}")
                    else:
                        prompt_parts.append(f"[{i}] {content}")
            prompt_parts.append("")

        # 3. 添加变量内容（按优先级排序）
        variable_order = [
            'agent_name', 'agent_type', 'leader_type', 'power_tier',
            'current_situation', 'available_actions', 'constraints',
            'objective_interests', 'alliances', 'enemies',
            'global_order', 'event_info'
        ]

        added_vars = set()
        for var_name in variable_order:
            if var_name in full_context and var_name not in added_vars:
                value = full_context[var_name]
                formatted_value = self._format_variable(var_name, value)
                if formatted_value:
                    prompt_parts.append(formatted_value)
                    added_vars.add(var_name)

        # 添加其他未排序的变量
        for key, value in full_context.items():
            if key not in added_vars:
                formatted_value = self._format_variable(key, value)
                if formatted_value:
                    prompt_parts.append(formatted_value)

        # 合并为完整Prompt
        full_prompt = "\n".join(prompt_parts)

        # 检查并截断过长的Prompt
        token_count = PromptTemplateEngine.calculate_token_count(full_prompt)
        if token_count > self._max_tokens:
            full_prompt = self._truncate_prompt(full_prompt, self._max_tokens)

        self._built = True
        return full_prompt

    def _format_variable(self, key: str, value: Any) -> Optional[str]:
        """格式化变量内容"""
        if value is None:
            return None

        # 变量名中文映射
        var_labels = {
            'agent_name': '智能体名称',
            'agent_type': '智能体类型',
            'leader_type': '领导类型',
            'power_tier': '实力层级',
            'current_situation': '当前局势',
            'available_actions': '可用行动',
            'constraints': '约束条件',
            'objective_interests': '核心利益',
            'alliances': '盟友关系',
            'enemies': '敌对关系',
            'global_order': '国际秩序',
            'event_info': '事件信息',
            'memory': '历史记忆'
        }

        label = var_labels.get(key, key)

        if isinstance(value, str):
            return f"# {label}\n{value}"
        elif isinstance(value, (list, dict)):
            return f"# {label}\n{json.dumps(value, ensure_ascii=False, indent=2)}"
        elif hasattr(value, 'value'):  # Enum类型
            return f"# {label}\n{value.value}"
        else:
            return f"# {label}\n{str(value)}"

    def _truncate_prompt(self, prompt: str, max_tokens: int) -> str:
        """截断过长的Prompt"""
        lines = prompt.split('\n')
        truncated = []
        current_tokens = 0

        # 倒序遍历，优先保留后面的内容
        for line in reversed(lines):
            line_tokens = PromptTemplateEngine.calculate_token_count(line)
            if current_tokens + line_tokens <= max_tokens * 0.9:  # 保留10%余量
                truncated.append(line)
                current_tokens += line_tokens

        return '\n'.join(reversed(truncated))


class PromptTemplateEngine:
    """
    Prompt模板引擎

    提供模板加载、渲染、缓存、Token计数等功能

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        template_dir: str = "config/prompts/",
        enable_cache: bool = True,
        enable_hot_reload: bool = False
    ):
        """
        Args:
            template_dir: 模板文件目录
            enable_cache: 是否启用模板缓存
            enable_hot_reload: 是否启用热重载（开发环境）
        """
        self.template_dir = Path(template_dir)
        self.enable_cache = enable_cache
        self.enable_hot_reload = enable_hot_reload

        # 模板缓存 {template_type: (content, timestamp)}
        self._template_cache: OrderedDict = OrderedDict()

        # 模板版本信息
        self._template_versions: Dict[PromptTemplate, TemplateVersion] = {}

        # 模板使用统计
        self._statistics: Dict[PromptTemplate, TemplateStatistics] = {}

        # 内置默认模板（如果没有模板文件）
        self._default_templates = self._init_default_templates()

        # 加载所有模板版本信息
        self._load_template_versions()

    def _init_default_templates(self) -> Dict[PromptTemplate, str]:
        """初始化内置默认模板"""
        return {
            PromptTemplate.LEADER_DECISION: self._get_leader_decision_template(),
            PromptTemplate.STATE_FOLLOWUP: self._get_state_followup_template(),
            PromptTemplate.ALLIANCE_INVITATION: self._get_alliance_invitation_template(),
            PromptTemplate.ALLIANCE_RESPONSE: self._get_alliance_response_template(),
            PromptTemplate.GLOBAL_EVENT_RESPONSE: self._get_global_event_response_template(),
            PromptTemplate.FINAL_JUDGMENT: self._get_final_judgment_template(),
            PromptTemplate.SITUATION_ASSESSMENT: self._get_situation_assessment_template(),
            PromptTemplate.POWER_BALANCE_EVALUATION: self._get_power_balance_evaluation_template(),
            PromptTemplate.INFLUENCE_ANALYSIS: self._get_influence_analysis_template(),
            PromptTemplate.RULE_VALIDATION: self._get_rule_validation_template(),
            PromptTemplate.CONSTRAINT_CHECK: self._get_constraint_check_template(),
            PromptTemplate.DIPLOMATIC_STATEMENT: self._get_diplomatic_statement_template(),
            PromptTemplate.ALLIANCE_SPEECH: self._get_alliance_speech_template(),
            PromptTemplate.EVENT_RESPONSE_SPEECH: self._get_event_response_speech_template(),
            PromptTemplate.CRISIS_COMMUNICATION: self._get_crisis_communication_template(),
            PromptTemplate.ORG_DECLARATION: self._get_org_declaration_template(),
        }

    def load_template(self, template_type: PromptTemplate) -> str:
        """
        加载模板文件

        Args:
            template_type: 模板类型

        Returns:
            模板内容字符串
        """
        # 检查缓存
        if self.enable_cache and template_type in self._template_cache:
            cached_content, timestamp = self._template_cache[template_type]
            if not self.enable_hot_reload:
                return cached_content

        # 尝试从文件加载
        template_file = self.template_dir / f"{template_type.value}.txt"
        if template_file.exists():
            content = template_file.read_text(encoding='utf-8')
            # 更新缓存
            if self.enable_cache:
                self._template_cache[template_type] = (content, datetime.now())
            return content

        # 使用内置默认模板
        return self._default_templates.get(template_type, "")

    def render_template(
        self,
        template_type: PromptTemplate,
        context: Dict[str, Any],
        validate_variables: bool = False
    ) -> str:
        """
        渲染模板

        Args:
            template_type: 模板类型
            context: 渲染上下文
            validate_variables: 是否验证变量

        Returns:
            渲染后的字符串
        """
        template = self.load_template(template_type)

        # 更新统计信息
        self._update_statistics(template_type, template)

        # 解析嵌套变量
        resolved_context = self._resolve_nested_variables(context)

        # 验证变量（如果启用）
        if validate_variables:
            self._validate_template_variables(template_type, resolved_context)

        # 渲染模板
        rendered = template

        # 逐步替换变量（支持嵌套）
        max_iterations = 10  # 防止无限循环
        for _ in range(max_iterations):
            prev_rendered = rendered
            rendered = self._replace_variables(rendered, resolved_context)
            if rendered == prev_rendered:
                break

        return rendered

    def _resolve_nested_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析嵌套变量（如 {agent.power.tier}）

        Args:
            context: 原始上下文

        Returns:
            解析后的上下文
        """
        resolved = {}

        def get_nested_value(obj: Any, path: str, default: Any = None) -> Any:
            """获取嵌套属性值"""
            try:
                parts = path.split('.')
                value = obj
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    elif hasattr(value, part):
                        value = getattr(value, part)
                    elif part.isdigit() and isinstance(value, (list, tuple)):
                        value = value[int(part)]
                    else:
                        return default
                return value
            except (AttributeError, KeyError, IndexError, TypeError):
                return default

        # 添加简化的变量访问路径
        if 'agent' in context:
            agent = context['agent']
            resolved['agent.name'] = get_nested_value(agent, 'name', '')
            resolved['agent.type'] = get_nested_value(agent, 'agent_type', '')
            resolved['agent.leader_type'] = get_nested_value(agent, 'leader_type', '')
            resolved['agent.power_tier'] = get_nested_value(agent, 'power_tier', '')
            resolved['agent.power'] = get_nested_value(agent, 'power_metrics', {})

        if 'environment' in context:
            env = context['environment']
            resolved['env.round'] = get_nested_value(env, 'round', 0)
            resolved['env.order'] = get_nested_value(env, 'global_order', '')

        # 合并原始上下文
        resolved.update(context)

        return resolved

    def _replace_variables(self, template: str, context: Dict[str, Any]) -> str:
        """
        替换模板中的变量

        支持 {var} 和 {var.key} 格式
        """
        # 匹配 {variable:default} 格式
        def replace_with_default(match):
            var_expr = match.group(1)
            if ':' in var_expr:
                var_name, default = var_expr.split(':', 1)
                value = context.get(var_name, default)
            else:
                value = context.get(var_expr, match.group(0))

            if value is None:
                return f"{{{var_expr}}}"  # 保留原样

            if isinstance(value, (dict, list)):
                return json.dumps(value, ensure_ascii=False, indent=2)
            return str(value)

        # 使用正则替换所有 {变量}
        return re.sub(r'\{([^{}]+)\}', replace_with_default, template)

    def _validate_template_variables(
        self,
        template_type: PromptTemplate,
        context: Dict[str, Any]
    ) -> None:
        """验证模板所需的变量"""
        # 定义每个模板必需的变量
        required_vars = {
            PromptTemplate.LEADER_DECISION: ['agent_name', 'leader_type', 'current_situation'],
            PromptTemplate.STATE_FOLLOWUP: ['agent_name', 'current_situation'],
            PromptTemplate.ALLIANCE_INVITATION: ['agent_name', 'target_name'],
            PromptTemplate.ALLIANCE_RESPONSE: ['agent_name', 'inviter_name'],
            PromptTemplate.GLOBAL_EVENT_RESPONSE: ['agent_name', 'event_type'],
            PromptTemplate.FINAL_JUDGMENT: ['agent_name'],
            PromptTemplate.SITUATION_ASSESSMENT: ['agent_name'],
            PromptTemplate.POWER_BALANCE_EVALUATION: ['agents'],
            PromptTemplate.INFLUENCE_ANALYSIS: ['agent_name', 'target_name'],
            PromptTemplate.RULE_VALIDATION: ['agent_name', 'leader_type'],
            PromptTemplate.CONSTRAINT_CHECK: ['agent_name'],
        }

        required = required_vars.get(template_type, [])
        missing = [var for var in required if var not in context]

        if missing:
            raise ValueError(
                f"模板 {template_type.value} 缺少必需变量: {', '.join(missing)}"
            )

    @staticmethod
    def calculate_token_count(text: str) -> int:
        """
        计算Token数量（基于DeepSeek-V3.2的tokenizer）

        简化实现：中文字符约等于1.5 token，英文字符约等于0.25 token

        Args:
            text: 待计算的文本

        Returns:
            Token数量
        """
        if not text:
            return 0

        # 统计中文字符和英文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars

        # 简化token计算
        tokens = chinese_chars * 1.5 + other_chars * 0.25

        # 考虑标点和空格
        tokens += len(re.findall(r'[^\w\s]', text)) * 0.3

        return int(tokens)

    def _update_statistics(self, template_type: PromptTemplate, template: str) -> None:
        """更新模板使用统计"""
        if template_type not in self._statistics:
            self._statistics[template_type] = TemplateStatistics(
                template_type=template_type
            )

        stats = self._statistics[template_type]
        stats.call_count += 1
        stats.last_used = datetime.now()

        # 更新平均token数
        token_count = self.calculate_token_count(template)
        stats.avg_token_count = (
            (stats.avg_token_count * (stats.call_count - 1) + token_count) / stats.call_count
        )

    def get_statistics(self, template_type: Optional[PromptTemplate] = None) -> List[TemplateStatistics]:
        """
        获取模板使用统计

        Args:
            template_type: 指定模板类型，None表示返回所有

        Returns:
            统计信息列表
        """
        if template_type:
            return [self._statistics.get(template_type)] if template_type in self._statistics else []
        return list(self._statistics.values())

    def clear_cache(self) -> None:
        """清空模板缓存"""
        self._template_cache.clear()

    def reload_templates(self) -> None:
        """重新加载所有模板（热重载）"""
        self.clear_cache()
        self._load_template_versions()

    def _load_template_versions(self) -> None:
        """加载模板版本信息"""
        version_file = self.template_dir / "versions.json"
        if version_file.exists():
            try:
                versions_data = json.loads(version_file.read_text(encoding='utf-8'))
                for template_type_str, version_info in versions_data.items():
                    try:
                        template_type = PromptTemplate(template_type_str)
                        self._template_versions[template_type] = TemplateVersion(**version_info)
                    except ValueError:
                        continue
            except (json) as e:
                pass

    def save_template_version(
        self,
        template_type: PromptTemplate,
        version: str,
        description: str
    ) -> None:
        """
        保存模板版本信息

        Args:
            template_type: 模板类型
            version: 版本号
            description: 版本描述
        """
        self._template_versions[template_type] = TemplateVersion(
            version=version,
            created_at=datetime.now(),
            description=description
        )

        # 保存到文件
        version_file = self.template_dir / "versions.json"
        versions_data = {}
        for tt, v in self._template_versions.items():
            versions_data[tt.value] = {
                'version': v.version,
                'created_at': v.created_at.isoformat(),
                'description': v.description
            }

        version_file.write_text(json.dumps(versions_data, ensure_ascii=False, indent=2), encoding='utf-8')

    def create_builder(
        self,
        template: PromptTemplate,
        context: Optional[Dict[str, Any]] = None
    ) -> PromptBuilder:
        """
        创建PromptBuilder实例

        Args:
            template: 模板类型
            context: 初始上下文

        Returns:
            PromptBuilder实例
        """
        return PromptBuilder(template, context)

    # ========== 内置默认模板 ==========

    def _get_leader_decision_template(self) -> str:
        """领导人决策模板"""
        return """# 决策任务

你是国际关系模拟仿真系统中的决策助手，代表{agent_name}国家进行决策。

## 领导人角色信息
- 国家名称：{agent_name}
- 领导类型：{leader_type}
- 实力层级：{power_tier}
- 核心利益：{objective_interests}

## 当前局势
{current_situation}

## 可用行动
{available_actions}

## 约束条件
{constraints}

## 决策要求
请根据你的领导类型和当前局势，选择一个合适的行动。在决策前必须考虑：
1. 行动是否符合你的领导类型特点
2. 行动是否有利于维护或增进国家核心利益
3. 行动的可能后果和风险
4. 与盟友的协调需要

请输出你的决策：
"""

    def _get_state_followup_template(self) -> str:
        """国家跟进决策模板"""
        return """# 跟进决策任务

你是国际关系模拟仿真系统中的决策助手，代表{agent_name}国家。

## 当前情况
{current_situation}

## 领导人决策参考
{leader_decision}

## 可选跟进方式
- 支持并响应
- 保持沉默观察
- 公开质疑或反对
- 私下沟通寻求说明
- 提出替代方案

请选择你的跟进方式并说明理由：
"""

    def _get_alliance_invitation_template(self) -> str:
        """联盟邀请模板"""
        return """# 联盟邀请任务

你代表{agent_name}准备邀请{target_name}加入联盟。

## 邀请理由
{invitation_reason}

## 当前联盟情况
{current_alliances}

## 可提供的条件
{offered_conditions}

## 邀请要点
请阐述：
1. 为什么选择{target_name}作为潜在盟友
2. 加入联盟能给对方带来什么利益
3. 联盟的合作方式和承诺
4. 期望对方承担的义务

请起草联盟邀请：
"""

    def _get_alliance_response_template(self) -> str:
        """联盟响应模板"""
        return """# 联盟响应任务

你代表{agent_name}收到了{inviter_name}的联盟邀请。

## 邀请内容
{invitation_content}

## 当前外交立场
{current_stance}

## 决策考虑因素
- 与{inviter_name}的历史关系
- 联盟承诺的可信度
- 加入联盟的收益与风险
- 对现有盟友关系的影响
- 国家核心利益的匹配度

## 响应选项
- 接受邀请，成为盟友
- 有条件接受
- 礼貌拒绝，保持中立
- 明确拒绝，表达保留意见

请做出回应：
"""

    def _get_global_event_response_template(self) -> str:
        """全球事件响应模板"""
        return """# 全球事件响应任务

全球发生了重大事件：{event_name}

## 事件详情
{event_details}

## 事件影响分析
{impact_analysis}

## 你的国家状况
- 国家名称：{agent_name}
- 实力层级：{power_tier}
- 受影响程度：{affected_level}

## 响应策略选项
- 积极参与应对
- 遵循国际协调
- 保持观察，适当表态
- 专注于国内事务

请制定你的响应策略：
"""

    def _get_final_judgment_template(self) -> str:
        """最终判断模板"""
        return """# 最终判断任务

请对本次国际互动进行最终评估判断。

## 智能体
{agent_name}

## 决策过程
{decision_process}

## 执行结果
{execution_result}

## 其他智能体的反应
{other_reactions}

## 评估维度
请从以下维度进行评估：
1. 决策是否符合理性和战略考量
2. 决策是否符合领导类型特征
3. 实际效果与预期是否一致
4. 对国际格局的影响
5. 是否存在更好的替代方案

请输出最终判断和评分（0-100分）：
"""

    def _get_situation_assessment_template(self) -> str:
        """局势评估模板"""
        return """# 局势评估任务

请对当前国际局势进行评估。

## 智能体
{agent_name}

## 当前轮次信息
{round_info}

## 国际环境
{international_environment}

## 评估要求
请分析：
1. 当前国际秩序的主要特征
2. 主要大国之间的力量对比
3. 潜在的冲突与合作机会
4. 对{agent_name}最有利的外交空间
5. 需要警惕的风险因素

请输出局势评估报告：
"""

    def _get_power_balance_evaluation_template(self) -> str:
        """实力平衡评估模板"""
        return """# 实力平衡评估任务

请评估当前国际实力平衡状况。

## 参与智能体
{agents_info}

## 实力对比数据
{power_metrics}

## 评估要点
1. 超级大国的实力差距
2. 大国之间的力量制衡
3. 区域实力分布
4. 实力变化趋势
5. 可能的格局变化

请输出实力平衡评估：
"""

    def _get_influence_analysis_template(self) -> str:
        """影响力分析模板"""
        return """# 影响力分析任务

请分析{agent_name}对{target_name}的影响力。

## 影响方信息
{source_agent}

## 被影响方信息
{target_agent}

## 关系基础
{relationship}

## 影响渠道
- 经济联系：{economic_ties}
- 政治关系：{political_relations}
- 文化交流：{cultural_exchange}
- 军事合作：{military_cooperation}

## 分析内容
请评估：
1. 影响力的强度和范围
2. 主要影响方式和途径
3. 影响的持续性
4. 增强或减弱影响力的建议

请输出影响力分析报告：
"""

    def _get_rule_validation_template(self) -> str:
        """规则验证模板"""
        return """# 规则验证任务

请验证决策是否符合道义现实主义规则。

## 智能体信息
- 国家：{agent_name}
- 领导类型：{leader_type}

## 待验证决策
{decision_to_validate}

## 领导类型规则约束
{leader_type_rules}

## 验证标准
1. 决策是否符合领导类型的道德取向
2. 是否触犯了该领导类型的禁止行为
3. 是否体现了该领导类型的特征偏好
4. 决策与客观利益的匹配度

请输出验证结果：
- 是否通过验证
- 如未通过，指出违规之处
- 建议的修正方向
"""

    def _get_constraint_check_template(self) -> str:
        """约束检查模板"""
        return """# 约束检查任务

请检查决策是否满足系统约束。

## 智能体
{agent_name}

## 待检查决策
{decision_to_check}

## 系统约束
{system_constraints}

## 检查项目
1. 实力变动是否在允许范围内
2. 关系变化是否合理
3. 行动频率是否超限
4. 资源消耗是否可承受

请输出约束检查结果：
"""

    def _get_diplomatic_statement_template(self) -> str:
        """外交声明模板"""
        return """# 外交声明起草

你代表{agent_name}需要发表外交声明。

## 声明背景
{background}

## 声明类型
{statement_type}

## 需要表达的核心观点
{core_points}

## 注意事项
- 语气应符合国际外交惯例
- 明确但不激进
- 为后续行动留有余地
- 体现国家的立场和原则

请起草外交声明：
"""

    def _get_alliance_speech_template(self) -> str:
        """联盟发言模板"""
        return """# 联盟发言起草

你代表{agent_name}在联盟框架内发言。

## 联盟信息
{alliance_info}

## 议题
{topic}

## 你的立场
{position}

## 盟友可能的反应
{allies_reactions}

## 发言要点
1. 表达对联盟的承诺
2. 阐述对议题的观点
3. 呼吁盟友协调行动
4. 展现合作意愿

请起草联盟发言：
"""

    def _get_event_response_speech_template(self) -> str:
        """事件响应发言模板"""
        return """# 事件响应发言起草

针对事件{event_name}，你需要发表回应。

## 事件详情
{event_details}

## 国家立场
{national_position}

## 受影响程度
{impact_level}

## 发言方向
- 表达关切或谴责
- 说明国家应对措施
- 呼吁国际社会行动
- 承担相应责任

请起草事件回应发言：
"""

    def _get_crisis_communication_template(self) -> str:
        """危机沟通模板"""
        return """# 危机沟通起草

你代表{agent_name}面临危机，需要与相关方进行沟通。

## 危机情况
{crisis_situation}

## 沟通对象
{communication_targets}

## 沟通目标
{communication_goals}

## 沟通原则
- 保持冷静和专业
- 准确传达信息
- 寻求理解和合作
- 避免激化矛盾

请起草危机沟通方案：
"""

    def _get_org_declaration_template(self) -> str:
        """国际组织声明模板"""
        return """# 国际组织声明起草

你作为国际组织代表需要发表声明。

## 组织信息
{organization_info}

## 声明主题
{declaration_topic}

## 成员国立场摘要
{member_positions}

## 组织原则
{org_principles}

## 声明要求
- 体现组织的宗旨和原则
- 平衡不同成员国的关切
- 提出建设性的解决方案
- 维护组织的权威性

请起草国际组织声明：
"""


class ScenarioPromptEngine:
    """
    场景化Prompt引擎

    针对不同类型智能体提供适配的Prompt模板

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, template_engine: PromptTemplateEngine):
        """
        Args:
            template_engine: 基础模板引擎
        """
        self.template_engine = template_engine

    def get_prompt_for_agent(
        self,
        agent_type: str,
        power_tier: str,
        template_type: PromptTemplate,
        context: Dict[str, Any]
    ) -> str:
        """
        获取适配智能体类型的Prompt

        Args:
            agent_type: 智能体类型（state/organization）
            power_tier: 实力层级（superpower/great_power/middle_power/small_power）
            template_type: 模板类型
            context: 上下文

        Returns:
            适配的Prompt
        """
        # 根据智能体类型和实力层级选择适配模板
        scenario_modifiers = self._get_scenario_modifiers(agent_type, power_tier)

        # 添加场景修饰到上下文
        enhanced_context = {**context, **scenario_modifiers}

        return self.template_engine.render_template(template_type, enhanced_context)

    def _get_scenario_modifiers(self, agent_type: str, power_tier: str) -> Dict[str, Any]:
        """获取场景修饰符"""
        modifiers = {}

        # 实力层级修饰
        if power_tier == 'superpower':
            modifiers.update({
                'role_description': '作为超级大国，你肩负着维护国际秩序的责任',
                'strategic_focus': '全球战略布局',
                'resource_priority': '优先保障全球影响力'
            })
        elif power_tier == 'great_power':
            modifiers.update({
                'role_description': '作为大国，你在区域事务中有重要话语权',
                'strategic_focus': '区域主导地位',
                'resource_priority': '平衡区域与国际利益'
            })
        elif power_tier == 'middle_power':
            modifiers.update({
                'role_description': '作为中等强国，你寻求在国际事务中发挥积极作用',
                'strategic_focus': '多边合作与平衡',
                'resource_priority': '发展与安全并重'
            })
        elif power_tier == 'small_power':
            modifiers.update({
                'role_description': '作为小国，你需要在大国之间寻求生存空间',
                'strategic_focus': '生存与渐进发展',
                'resource_priority': '确保国家安全和基本利益'
            })

        # 智能体类型修饰
        if agent_type == 'organization':
            modifiers.update({
                'role_description': '作为国际组织，你代表多边利益和共同规范',
                'strategic_focus': '维护国际秩序与多边机制',
                'resource_priority': '促进合作与冲突调解'
            })

        return modifiers


class ABTestingFramework:
    """
    A/B测试框架

    用于测试不同Prompt模板的效果

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        # 存储测试结果
        self._test_results: Dict[str, List[Dict]] = {}

    def create_ab_test(
        self,
        test_name: str,
        template_a: str,
        template_b: str,
        test_contexts: List[Dict]
    ) -> str:
        """
        创建A/B测试

        Args:
            test_name: 测试名称
            template_a: 模板A
            template_b: 模板B
            test_contexts: 测试上下文列表

        Returns:
            测试ID
        """
        test_id = f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self._test_results[test_id] = {
            'name': test_name,
            'template_a': template_a,
            'template_b': template_b,
            'results_a': [],
            'results_b': [],
            'start_time': datetime.now().isoformat()
        }

        return test_id

    def record_result(
        self,
        test_id: str,
        variant: str,
        context: Dict,
        result: Any,
        metrics: Dict
    ) -> None:
        """
        记录测试结果

        Args:
            test_id: 测试ID
            variant: 变体（'a' 或 'b'）
            context: 测试上下文
            result: 输出结果
            metrics: 评估指标
        """
        if test_id not in self._test_results:
            return

        result_key = f'results_{variant}'
        self._test_results[test_id][result_key].append({
            'context': context,
            'result': result,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        })

    def analyze_test(self, test_id: str) -> Dict[str, Any]:
        """
        分析A/B测试结果

        Args:
            test: 测试ID

        Returns:
            分析报告
        """
        if test_id not in self._test_results:
            return {'error': 'Test not found'}

        test_data = self._test_results[test_id]
        results_a = test_data['results_a']
        results_b = test_data['results_b']

        def calc_metrics(results):
            if not results:
                return {'count': 0}
            return {
                'count': len(results),
                'avg_success_rate': sum(r['metrics'].get('success_rate', 0) for r in results) / len(results),
                'avg_quality_score': sum(r['metrics'].get('quality_score', 0) for r in results) / len(results),
                'avg_response_time': sum(r['metrics'].get('response_time', 0) for r in results) / len(results)
            }

        return {
            'test_name': test_data['name'],
            'variant_a': calc_metrics(results_a),
            'variant_b': calc_metrics(results_b),
            'winner': 'a' if results_a and results_b and calc_metrics(results_a)['avg_quality_score'] > calc_metrics(results_b)['avg_quality_score'] else 'b'
        }
