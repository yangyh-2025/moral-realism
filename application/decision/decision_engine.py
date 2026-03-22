"""
决策引擎 - 协调智能体决策，处理决策冲突，执行决策逻辑

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional, Any, Set
import asyncio
from datetime import datetime

from domain.agents.base_agent import BaseAgent
from infrastructure.validation.validator import RuleValidator, ValidationResult
from infrastructure.logging.logger import DecisionReasoning, EnhancedLogger


class DecisionEngine:
    """
    决策引擎 - 协调智能体决策，处理决策冲突，执行决策逻辑

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        llm_engine: Any,
        validator: RuleValidator,
        storage: Any,
        logger: EnhancedLogger
    ):
        """
        初始化决策引擎

        Args:
            llm_engine: LLM引擎实例
            validator: 规则验证器
            storage: 存储引擎
            logger: 增强日志记录器
        """
        self.llm_engine = llm_engine
        self.validator = validator
        self.storage = storage
        self.logger = logger
        self.max_retries = 3
        self._conflict_resolution_strategies = {
            'priority': self._resolve_by_priority,
            'negotiation': self._resolve_by_negotiation,
            'random': self._resolve_by_random
        }

    async def generate_decision_for_agent(
        self,
        agent: BaseAgent,
        environment_state: Dict,
        simulation_id: str,
        round: int,
        use_rotation: bool = True
    ) -> Dict:
        """
        为单个智能体生成决策

        Args:
            agent: 智能体实例
            environment_state: 环境状态
            simulation_id: 仿真ID
            round: 当前轮次
            use_rotation: 是否使用API-key轮替调用

        Returns:
            决策结果
        """
        available_functions = agent.get_available_functions()
        prohibited_functions = agent.get_prohibited_functions()

        # 获取智能体当前状态
        agent_state = {
            'agent_id': agent.state.agent_id,
            'name': agent.state.name,
            'power_tier': agent.state.power_tier.value if agent.state.power_tier else 'unknown',
            'power': agent.state.power_metrics.calculate_comprehensive_power() if agent.state.power_metrics else 0,
            'region': agent.state.region
        }

        # 构建提示词
        prompt = self._build_decision_prompt(
            agent_state=agent_state,
            environment_state=environment_state,
            available_functions=available_functions,
            prohibited_functions=prohibited_functions
        )

        for attempt in range(self.max_retries):
            try:
                # 调用LLM生成决策
                llm_result = await self.llm_engine.make_decision(
                    agent_id=agent.state.agent_id,
                    prompt=prompt,
                    available_functions=available_functions,
                    prohibited_functions=prohibited_functions,
                    use_rotation=use_rotation
                )

                # 验证决策
                validation_result = self.validator.validate_decision(
                    leader_type=agent.state.leader_type,
                    function_name=llm_result.get('function', ''),
                    function_args=llm_result.get('arguments', {}),
                    objective_interest=getattr(agent.state, 'objective_interest', ''),
                    current_power=agent.state.power_metrics.calculate_comprehensive_power() if agent.state.power_metrics else 0
                )

                if validation_result.is_valid:
                    # 决策有效，记录并返回
                    function_name = llm_result.get('function', '')
                    function_args = llm_result.get('arguments', {})

                    # 创建决策理由记录
                    reasoning = DecisionReasoning(
                        decision_id=f"decision_{agent.state.agent_id}_{round}_{attempt}",
                        agent_id=agent.state.agent_id,
                        round=round,
                        situation_analysis=llm_result.get('reasoning', {}).get('situation_analysis', ''),
                        strategic_consideration=llm_result.get('reasoning', {}).get('strategic_consideration', ''),
                        expected_outcome=llm_result.get('reasoning', {}).get('expected_outcome', ''),
                        alternatives=llm_result.get('reasoning', {}).get('alternatives', []),
                        full_reasoning=llm_result.get('reasoning', {}).get('full_reasoning', '')
                    )

                    decision = {
                        'agent_id': agent.state.agent_id,
                        'function': function_name,
                        'arguments': function_args,
                        'validation': {'is_valid': True},
                        'reasoning': reasoning,
                        'attempt': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }

                    # 更新智能体状态
                    agent.record_decision(function_name, function_args)

                    # 记录决策日志
                    self.logger.log_decision(
                        simulation_id=simulation_id,
                        round=round,
                        agent_id=agent.state.agent_id,
                        decision_type=function_name,
                        decision_content=str(function_args),
                        reasoning=reasoning,
                        metadata={'attempt': attempt + 1}
                    )

                    # 保存决策记录
                    if hasattr(self.storage, 'save_decision'):
                        self.storage.save_decision(
                            simulation_id=simulation_id,
                            round=round,
                            agent_id=agent.state.agent_id,
                            function_name=function_name,
                            function_args=function_args,
                            validation_result={'is_valid': True},
                            reasoning={
                                'situation_analysis': reasoning.situation_analysis,
                                'strategic_consideration': reasoning.strategic_consideration,
                                'expected_outcome': reasoning.expected_outcome,
                                'alternatives': reasoning.alternatives,
                                'full_reasoning': reasoning.full_reasoning
                            }
                        )

                    return decision
                else:
                    # 决策无效，记录错误
                    if attempt == self.max_retries - 1:
                        return {
                            'agent_id': agent.state.agent_id,
                            'function': None,
                            'error': validation_result.error_message,
                            'validation': {
                                'is_valid': False,
                                'error': validation_result.error_message
                            },
                            'attempt': attempt + 1,
                            'timestamp': datetime.now().isoformat()
                        }

            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        'agent_id': agent.state.agent_id,
                        'function': None,
                        'error': str(e),
                        'attempt': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }

        return {
            'agent_id': agent.state.agent_id,
            'function': None,
            'error': 'Max retries exceeded',
            'timestamp': datetime.now().isoformat()
        }

    async def generate_decisions_for_all_agents(
        self,
        agents: List[BaseAgent],
        environment_state: Dict,
        simulation_id: str,
        round: int,
        use_rotation: bool = False
    ) -> List[Dict]:
        """
        并行生成所有智能体的决策

        Args:
            agents: 智能体列表
            environment_state: 环境状态
            simulation_id: 仿真ID
            round: 当前轮次
            use_rotation: 是否使用API-key轮替调用

        Returns:
            决策结果列表
        """
        tasks = [
            self.generate_decision_for_agent(
                agent=agent,
                environment_state=environment_state,
                simulation_id=simulation_id,
                round=round,
                use_rotation=use_rotation
            )
            for agent in agents
        ]

        return await asyncio.gather(*tasks)

    def detect_conflicts(self, decisions: List[Dict]) -> List[Dict]:
        """
        检测决策冲突

        Args:
            decisions: 决策列表

        Returns:
            冲突列表
        """
        conflicts = []

        # 检查相互冲突的决策
        for i, decision_a in enumerate(decisions):
            for j, decision_b in enumerate(decisions):
                if i >= j:
                    continue

                conflict = self._check_decision_conflict(decision_a, decision_b)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def _check_decision_conflict(self, decision_a: Dict, decision_b: Dict) -> Optional[Dict]:
        """检查两个决策之间是否存在冲突"""
        function_a = decision_a.get('function')
        function_b = decision_b.get('function')

        if not function_a or not function_b:
            return None

        # 检查目标冲突
        args_a = decision_a.get('arguments', {})
        args_b = decision_b.get('arguments', {})

        target_a = args_a.get('target')
        target_b = args_b.get('target')

        # 如果两个决策都是针对同一个目标的相反行动
        if target_a == target_b:
            if function_a == 'use_military_force' and function_b == 'seek_protection':
                return {
                    'type': 'target_conflict',
                    'decisions': [decision_a['agent_id'], decision_b['agent_id']],
                    'target': target_a,
                    'description': f"针对同一目标{target_a}存在冲突决策"
                }

        # 检查资源冲突
        if function_a == function_b and function_a in ['military_alliance', 'security_guarantee']:
            if target_a == target_b:
                return {
                    'type': 'resource_conflict',
                    'decisions': [decision_a['agent_id'], decision_b['agent_id']],
                    'target': target_a,
                    'description': f"多个智能体试图建立同一联盟关系"
                }

        return None

    def resolve_conflicts(
        self,
        decisions: List[Dict],
        conflicts: List[Dict],
        strategy: str = 'priority'
    ) -> List[Dict]:
        """
        解决决策冲突

        Args:
            decisions: 决策列表
            conflicts: 冲突列表
            strategy: 解决策略 (priority, negotiation, random)

        Returns:
            解决冲突后的决策列表
            """
        if not conflicts:
            return decisions

        resolver = self._conflict_resolution_strategies.get(strategy, self._resolve_by_priority)
        return resolver(decisions, conflicts)

    def _resolve_by_priority(self, decisions: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """基于优先级解决冲突"""
        agent_priority = {}

        for decision in decisions:
            agent_id = decision['agent_id']
            # 根据实力分配优先级
            power = decision.get('power', 0)
            agent_priority[agent_id] = power

        resolved_decisions = []
        removed_agent_ids = set()

        for conflict in conflicts:
            # 找出冲突中优先级最低的决策
            involved_agents = conflict['decisions']
            lowest_priority_agent = min(involved_agents, key=lambda x: agent_priority.get(x, 0))
            removed_agent_ids.add(lowest_priority_agent)

        # 保留未被移除的决策
        for decision in decisions:
            if decision['agent_id'] not in removed_agent_ids:
                resolved_decisions.append(decision)
            else:
                # 将冲突决策标记为已解决
                decision['status'] = 'conflict_resolved'
                decision['resolution'] = 'removed_due_to_conflict'

        return resolved_decisions + removed_agent_ids

    def _resolve_by_negotiation(self, decisions: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """基于协商解决冲突"""
        # 简化实现：将冲突决策的参数进行合并
        for conflict in conflicts:
            if conflict['type'] == 'resource_conflict':
                # 找到涉及的所有决策
                involved_decisions = [
                    d for d in decisions
                    if d['agent_id'] in conflict['decisions']
                ]

                if involved_decisions:
                    # 保留第一个决策，修改其参数
                    primary_decision = involved_decisions[0]
                    primary_decision['arguments']['is_joint'] = True
                    primary_decision['arguments']['participants'] = conflict['decisions']

                    # 标记其他决策为已合并
                    for decision in involved_decisions[1:]:
                        decision['status'] = 'merged'
                        decision['merged_into'] = primary_decision['agent_id']

        return decisions

    def _resolve_by_random(self, decisions: List[Dict], conflicts: List[Dict]) -> List[Dict]:
        """随机选择解决冲突"""
        import random
        removed_agent_ids = set()

        for conflict in conflicts:
            involved_agents = conflict['decisions']
            # 随机选择保留哪个决策
            kept_agent = random.choice(involved_agents)
            removed = [agent for agent in involved_agents if agent != kept_agent]
            removed_agent_ids.update(removed)

        resolved_decisions = []
        for decision in decisions:
            if decision['agent_id'] not in removed_agent_ids:
                resolved_decisions.append(decision)
            else:
                decision['status'] = 'conflict_resolved'
                decision['resolution'] = 'randomly_removed'

        return resolved_decisions + [d for d in decisions if d['agent_id'] in removed_agent_ids]

    def _build_decision_prompt(
        self,
        agent_state: Dict,
        environment_state: Dict,
        available_functions: List[Dict],
        prohibited_functions: Set[str]
    ) -> str:
        """
        构建决策提示词

        Args:
            agent_state: 智能体状态
            environment_state: 环境状态
            available_functions: 可用函数列表 (List[Dict], 每个字典包含 name 和 description)
            prohibited_functions: 禁止函数列表 (Set[str])

        Returns:
            提示词
        """
        prompt = f"""
你是{agent_state['name']}的决策者。

## 当前状态
- 国家ID: {agent_state['agent_id']}
- 实力层级: {agent_state['power_tier']}
- 综合国力: {agent_state['power']:.2f}
- 所属区域: {agent_state['region']}

## 可用行动
{', '.join([f.get('name', '') for f in available_functions])}

## 禁止行动
{', '.join(list(prohibited_functions)) if prohibited_functions else '无'}

## 环境状态
{self._format_environment_state(environment_state)}

## 任务
根据当前局势，选择一个合适的行动并给出详细理由。你的决策必须道守以下要求：
1. 不能选择禁止行动
2. 只能从可用行动中选择
3. 提供完整的决策理由，包括局势分析、战略考量、预期结果和替代方案

请以JSON格式返回你的决策：
{{
    "function": "行动名称",
    "arguments": {{"参数名": "参数值"}},
    "reasoning": {{
        "situation_analysis": "局势分析",
        "strategic_consideration": "战略考量",
        "expected_outcome": "预期结果",
        "alternatives": ["替代方案1", "替代方案2"],
        "full_reasoning": "完整决策理由"
    }}
}}
"""
        return prompt

    def _format_environment_state(self, environment_state: Dict) -> str:
        """格式化环境状态"""
        formatted = []

        if 'agents' in environment_state:
            formatted.append("### 其他国家情况")
            for agent in environment_state['agents'][:10]:  # 限制显示数量
                formatted.append(f"- {agent.get('name', agent.get('agent_id'))}: 实力={agent.get('power', 0):.2f}")

        if 'active_events' in environment_state:
            formatted.append("\n### 当前事件")
            for event in environment_state['active_events']:
                formatted.append(f"- {event.get('description', '未知事件')}")

        if 'alliances' in environment_state:
            formatted.append("\n### 现有联盟")
            for alliance in environment_state['alliances'][:5]:
                formatted.append(f"- {alliance.get('type', '未知联盟')}")

        return '\n'.join(formatted) if formatted else "暂无特殊环境信息"
