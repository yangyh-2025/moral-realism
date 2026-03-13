"""
数据追溯分析 - 对应技术方案3.4.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import numpy as np
from collections import defaultdict
import uuid


class CausalFactor(BaseModel):
    """因果因素"""
    factor_id: str = Field(..., description="因素ID")
    factor_type: str = Field(..., description="因素类型")
    description: str = Field(..., description="描述")
    contribution: float = Field(..., description="贡献度")
    evidence: List[str] = Field(default_factory=list, description="证据列表")


class CausalChain(BaseModel):
    """因果链"""
    chain_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="因果链ID")
    start_event: Dict = Field(..., description="起始事件")
    end_event: Dict = Field(..., description="结束事件")
    factors: List[CausalFactor] = Field(default_factory=list, description="因果因素列表")
    total_contribution: float = Field(0.0, description="总贡献度")
    visualization_data: Dict = Field(default_factory=dict, description="可视化数据")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class InfluenceScore(BaseModel):
    """影响力评分"""
    agent_id: str = Field(..., description="智能体ID")
    total_influence: float = Field(..., description="总影响力")
    influence_breakdown: Dict[str, float] = Field(default_factory=dict, description="影响力分解")
    most_influential_actions: List[Dict] = Field(default_factory=list, description="最有影响力的行动")
    influence_rank: int = Field(0, description="影响力排名")


class ImpactAnalysis(BaseModel):
    """影响分析"""
    event_id: str = Field(..., description="事件ID")
    event_type: str = Field(..., description="事件类型")
    affected_agents: List[str] = Field(default_factory=list, description="受影响的智能体")
    impact_magnitude: Dict[str, float] = Field(default_factory=dict, description="影响幅度")
    duration: int = Field(0, description="持续轮次")
    propagation_path: List[str] = Field(default_factory=list, description="传播路径")


class HeatmapData(BaseModel):
    """热力图数据"""
    matrix: List[List[float]] = Field(..., description="热力图矩阵")
    row_labels: List[str] = Field(..., description="行标签")
    col_labels: List[str] = Field(..., description="列标签")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CausalTracer:
    """因果追溯器"""

    def __init__(self):
        self._decision_history: Dict[str, Dict] = {}
        self._outcome_history: Dict[str, Dict] = {}

    def record_decision(self, decision_id: str, decision_data: Dict):
        """
        记录决策

        Args:
            decision_id: 决策ID
            decision_data: 决策数据
        """
        self._decision_history[decision_id] = decision_data

    def record_outcome(self, outcome_id: str, outcome_data: Dict):
        """
        记录结果

        Args:
            outcome_id: 结果ID
            outcome_data: 结果数据
        """
        self._outcome_history[outcome_id] = outcome_data

    def trace_decision_outcome(self, decision_id: str) -> CausalChain:
        """
        追溯决策结果

        Args:
            decision_id: 决策ID

        Returns:
            因果链
        """
        decision = self._decision_history.get(decision_id)
        if not decision:
            raise ValueError(f"决策 {decision_id} 不存在")

        # 查找相关结果
        related_outcomes = []
        for outcome_id, outcome in self._outcome_history.items():
            if outcome.get("decision_id") == decision_id:
                related_outcomes.append(outcome)

        if not related_outcomes:
            return CausalChain(
                start_event=decision,
                end_event={"error": "未找到相关结果"},
                factors=[],
                total_contribution=0.0
            )

        # 使用最后一个结果
        outcome = related_outcomes[-1]

        # 分析因果因素
        factors = self._analyze_causal_factors(decision, outcome)

        # 计算总贡献度
        total_contribution = sum(f.contribution for f in factors)

        # 生成可视化数据
        visualization_data = self._generate_causal_visualization(decision, outcome, factors)

        return CausalChain(
            start_event=decision,
            end_event=outcome,
            factors=factors,
            total_contribution=total_contribution,
            visualization_data=visualization_data
        )

    def _analyze_causal_factors(self, decision: Dict, outcome: Dict) -> List[CausalFactor]:
        """分析因果因素"""
        factors = []

        # 分析决策参数的影响
        decision_params = decision.get("parameters", {})
        for param_name, param_value in decision_params.items():
            contribution = abs(float(param_value)) * 0.1 if isinstance(param_value, (int, float)) else 0.1

            factors.append(CausalFactor(
                factor_id=f"{param_name}_factor",
                factor_type="parameter",
                description=f"参数 {param_name} = {param_value}",
                contribution=min(contribution, 1.0),
                evidence=[f"决策中使用了参数 {param_name}"]
            ))

        # 分析环境因素的影响
        decision_context = decision.get("context", {})
        for context_key, context_value in decision_context.items():
            context_contribution = 0.05

            factors.append(CausalFactor(
                factor_id=f"{context_key}_context",
                factor_type="context",
                description=f"上下文 {context_key}",
                contribution=context_contribution,
                evidence=[f"决策上下文中包含 {context_key}"]
            ))

        # 归一化贡献度
        total = sum(f.contribution for f in factors)
        if total > 0:
            for f in factors:
                f.contribution = f.contribution / total

        return factors

    def _generate_causal_visualization(
        self,
        decision: Dict,
        outcome: Dict,
        factors: List[CausalFactor]
    ) -> Dict:
        """生成因果可视化数据"""
        nodes = [
            {
                "id": "decision",
                "label": f"决策: {decision.get('type', 'unknown')}",
                "type": "decision"
            },
            {
                "id": "outcome",
                "label": f"结果: {outcome.get('type', 'unknown')}",
                "type": "outcome"
            }
        ]

        edges = []

        # 添加因果因素节点
        for i, factor in enumerate(factors):
            factor_id = f"factor_{i}"
            nodes.append({
                "id": factor_id,
                "label": factor.description,
                "type": "factor",
                "value": factor.contribution
            })
            edges.append({
                "source": "decision",
                "target": factor_id,
                "weight": factor.contribution
            })
            edges.append({
                "source": factor_id,
                "target": "outcome",
                "weight": factor.contribution
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "layout": "hierarchical"
        }

    def find_root_causes(self, outcome_id: str, depth: int = 3) -> List[CausalFactor]:
        """
        查找根本原因

        Args:
            outcome_id: 结果ID
            depth: 追溯深度

        Returns:
            因果因素列表
        """
        outcome = self._outcome_history.get(outcome_id)
        if not outcome:
            raise ValueError(f"结果 {outcome_id} 不存在")

        root_causes = []

        # 递归追溯
        self._trace_backwards(outcome, depth, root_causes)

        return root_causes

    def _trace_backwards(self, event: Dict, depth: int, causes: List[CausalFactor]):
        """向后追溯"""
        if depth <= 0:
            return

        # 查找导致当前事件的决策
        decision_id = event.get("decision_id")
        if decision_id:
            decision = self._decision_history.get(decision_id)
            if decision:
                # 添加决策为根因
                contribution = 1.0 / (depth + 1)
                causes.append(CausalFactor(
                    factor_id=f"decision_{decision_id}",
                    factor_type="decision",
                    description=f"决策 {decision.get('type', 'unknown')}",
                    contribution=contribution,
                    evidence=["决策追溯"]
                ))

                # 继续追溯决策的前因
                self._trace_backwards(decision, depth - 1, causes)

    def visualize_causal_chain(self, chain: CausalChain) -> Dict:
        """
        可视化因果链

        Args:
            chain: 因果链

        Returns:
            可视化数据
        """
        return chain.visualization_data


class InfluenceAnalyzer:
    """影响力分析器"""

    def __init__(self):
        self._action_history: List[Dict] = []
        self._agent_states: Dict[str, List[Dict]] = defaultdict(list)
        self._event_history: List[Dict] = []

    def record_action(self, action: Dict):
        """
        记录行动

        Args:
            action: 行动数据
        """
        self._action_history.append(action)

    def record_agent_state(self, agent_id: str, state: Dict):
        """
        记录智能体状态

        Args:
            agent_id: 智能体ID
            state: 状态数据
        """
        self._agent_states[agent_id].append(state)

    def record_event(self, event: Dict):
        """
        记录事件

        Args:
            event: 事件数据
        """
        self._event_history.append(event)

    def calculate_agent_influence(
        self,
        agent_id: str,
        simulation_id: Optional[str] = None
    ) -> InfluenceScore:
        """
        计算智能体影响力

        Args:
            agent_id: 智能体ID
            simulation_id: 仿真ID

        Returns:
            影响力评分
        """
        # 筛选智能体的行动
        agent_actions = [
            a for a in self._action_history
            if a.get("agent_id") == agent_id
            and (simulation_id is None or a.get("simulation_id") == simulation_id)
        ]

        # 计算影响力分解
        influence_breakdown = {
            "action_count": len(agent_actions),
            "action_diversity": self._calculate_action_diversity(agent_actions),
            "success_rate": self._calculate_success_rate(agent_actions),
            "impact_score": self._calculate_impact_score(agent_id, agent_actions)
        }

        # 计算总影响力
        total_influence = sum(influence_breakdown.values()) / len(influence_breakdown)

        # 找出最有影响力的行动
        most_influential_actions = sorted(
            agent_actions,
            key=lambda a: a.get("impact_score", 0),
            reverse=True
        )[:5]

        return InfluenceScore(
            agent_id=agent_id,
            total_influence=total_influence,
            influence_breakdown=influence_breakdown,
            most_influential_actions=most_influential_actions,
            influence_rank=0  # 将在排序后计算
        )

    def _calculate_action_diversity(self, actions: List[Dict]) -> float:
        """计算行动多样性"""
        action_types = set(a.get("action_type", "unknown") for a in actions)
        return len(action_types) * 0.1  # 归一化

    def _calculate_success_rate(self, actions: List[Dict]) -> float:
        """计算成功率"""
        if not actions:
            return 0.0

        successful = sum(1 for a in actions if a.get("success", False))
        return successful / len(actions)

    def _calculate_impact_score(self, agent_id: str, actions: List[Dict]) -> float:
        """计算影响分数"""
        impact_scores = []

        for action in actions:
            # 基于事件响应计算影响
            action_id = action.get("action_id")
            related_events = [
                e for e in self._event_history
                if e.get("action_id") == action_id
            ]

            if related_events:
                # 计算事件影响的总和
                event_impact = sum(e.get("severity", "1") for e in related_events) / len(related_events)
                impact_scores.append(event_impact)

        return np.mean(impact_scores) if impact_scores else 0.0

    def calculate_all_agent_influences(
        self,
        simulation_id: Optional[str] = None
    ) -> List[InfluenceScore]:
        """
        计算所有智能体影响力

        Args:
            simulation_id: 仿真ID

        Returns:
            影响力评分列表
        """
        # 获取所有智能体ID
        agent_ids = set(a.get("agent_id") for a in self._action_history)

        # 计算每个智能体的影响力
        influences = []
        for agent_id in agent_ids:
            if agent_id:
                influence = self.calculate_agent_influence(agent_id, simulation_id)
                influences.append(influence)

        # 按影响力排序并分配排名
        influences.sort(key=lambda x: x.total_influence, reverse=True)
        for rank, influence in enumerate(influences, 1):
            influence.influence_rank = rank

        return influences

    def calculate_event_impact(self, event_id: str) -> ImpactAnalysis:
        """
        计算事件影响

        Args:
            event_id: 事件ID

        Returns:
            影响分析
        """
        event = next(
            (e for e in self._event_history if e.get("event_id") == event_id),
            None
        )

        if not event:
            raise ValueError(f"事件 {event_id} 不存在")

        # 查找受影响的智能体
        affected_agents = event.get("affected_agents", [])

        # 计算影响幅度
        impact_magnitude = event.get("impact", {})

        # 计算持续轮次
        duration = event.get("duration", 1)

        # 追溯传播路径
        propagation_path = self._trace_propagation(event)

        return ImpactAnalysis(
            event_id=event_id,
            event_type=event.get("event_type", "unknown"),
            affected_agents=affected_agents,
            impact_magnitude=impact_magnitude,
            duration=duration,
            propagation_path=propagation_path
        )

    def _trace_propagation(self, event: Dict) -> List[str]:
        """追溯传播路径"""
        path = [event.get("event_id", "unknown")]

        # 查找相关事件
        event_id = event.get("event_id")
        related_events = [
            e for e in self._event_history
            if event_id in e.get("parent_events", [])
        ]

        for related in related_events:
            path.extend(self._trace_propagation(related))

        return path

    def generate_influence_heatmap(
        self,
        simulation_id: Optional[str] = None
    ) -> HeatmapData:
        """
        生成影响力热力图

        Args:
            simulation_id: 仿真ID

        Returns:
            热力图数据
        """
        # 计算所有智能体影响力
        influences = self.calculate_all_agent_influences(simulation_id)

        if not influences:
            return HeatmapData(
                matrix=[[]],
                row_labels=[],
                col_labels=[]
            )

        # 获取智能体ID列表
        agent_ids = [inf.agent_id for inf in influences]

        # 构建热力图矩阵（智能体对智能体的影响）
        n = len(agent_ids)
        matrix = [[0.0] * n for _ in range(n)]

        # 填充矩阵
        for i, agent_i in enumerate(agent_ids):
            for j, agent_j in enumerate(agent_ids):
                if i == j:
                    # 对角线：自影响
                    influence = next(
                        (inf for inf in influences if inf.agent_id == agent_i),
                        None
                    )
                    if influence:
                        matrix[i][j] = influence.total_influence
                else:
                    # 非对角线：相互影响
                    mutual_impact = self._calculate_mutual_impact(agent_i, agent_j)
                    matrix[i][j] = mutual_impact

        return HeatmapData(
            matrix=matrix,
            row_labels=agent_ids,
            col_labels=agent_ids
        )

    def _calculate_mutual_impact(self, agent_i: str, agent_j: str) -> float:
        """计算智能体间的相互影响"""
        # 查找两个智能体之间的互动
        mutual_actions = [
            a for a in self._action_history
            if (
                (a.get("agent_id") == agent_i and a.get("target_agent") == agent_j) or
                (a.get("agent_id") == agent_j and a.get("target_agent") == agent_i)
            )
        ]

        if not mutual_actions:
            return 0.0

        # 计算影响的平均值
        impacts = [a.get("impact_score", 0.5) for a in mutual_actions]
        return np.mean(impacts)


class ComparisonReport(BaseModel):
    """对比报告"""
    simulation_ids: List[str] = Field(..., description="仿真ID列表")
    metrics_comparison: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="指标对比"
    )
    key_differences: List[Dict] = Field(default_factory=list, description="关键差异")
    summary: str = Field(default="", description="摘要")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ScenarioComparison(BaseModel):
    """场景对比"""
    scenario_name: str = Field(..., description="场景名称")
    base_simulation: str = Field(..., description="基准仿真")
    test_simulation: str = Field(..., description="测试仿真")
    differences: Dict = Field(default_factory=dict, description="差异")
    insights: List[str] = Field(default_factory=list, description="洞察")


class Chart(BaseModel):
    """图表"""
    chart_type: str = Field(..., description="图表类型")
    title: str = Field(..., description="标题")
    data: Dict = Field(..., description="数据")
    format: str = Field(default="json", description="格式")


class ComparisonAnalyzer:
    """对比分析器"""

    def __init__(self):
        self._simulation_results: Dict[str, Dict] = {}

    def add_simulation_result(self, simulation_id: str, result: Dict):
        """
        添加仿真结果

        Args:
            simulation_id: 仿真ID
            result: 结果数据
        """
        self._simulation_results[simulation_id] = result

    def compare_simulations(self, sim_ids: List[str]) -> ComparisonReport:
        """
        对比多次仿真

        Args:
            sim_ids: 仿真ID列表

        Returns:
            对比报告
        """
        if len(sim_ids) < 2:
            raise ValueError("至少需要两个仿真结果才能进行对比")

        # 收集所有指标
        metrics_comparison = defaultdict(dict)

        for sim_id in sim_ids:
            result = self._simulation_results.get(sim_id)
            if result and "metrics" in result:
                metrics = result["metrics"]
                for category, metric_list in metrics.items():
                    for metric in metric_list:
                        name = metric.get("name", "unknown")
                        value = metric.get("value", 0)
                        metrics_comparison[name][sim_id] = float(value)

        # 找出关键差异
        key_differences = self._find_key_differences(metrics_comparison, sim_ids)

        # 生成摘要
        summary = self._generate_comparison_summary(metrics_comparison, key_differences)

        return ComparisonReport(
            simulation_ids=sim_ids,
            metrics_comparison=dict(metrics_comparison),
            key_differences=key_differences,
            summary=summary
        )

    def _find_key_differences(
        self,
        metrics_comparison: Dict[str, Dict[str, float]],
        sim_ids: List[str]
    ) -> List[Dict]:
        """找出关键差异"""
        key_differences = []

        for metric_name, values in metrics_comparison.items():
            if len(values) < 2:
                continue

            # 计算极差
            values_list = list(values.values())
            max_diff = max(values_list) - min(values_list)

            # 计算变异系数
            mean = np.mean(values_list)
            cv = (np.std(values_list) / mean) if mean != 0 else 0

            # 如果差异显著，记录
            if cv > 0.2:  # 变异系数大于20%
                key_differences.append({
                    "metric": metric_name,
                    "values": values,
                    "max_diff": max_diff,
                    "coefficient_of_variation": cv,
                    "best_simulation": max(values, key=values.get),
                    "worst_simulation": min(values, key=values.get)
                })

        # 按变异系数排序
        key_differences.sort(key=lambda x: x["coefficient_of_variation"], reverse=True)

        return key_differences

    def _generate_comparison_summary(
        self,
        metrics_comparison: Dict[str, Dict[str, float]],
        key_differences: List[Dict]
    ) -> str:
        """生成对比摘要"""
        if not key_differences:
            return "各仿真结果差异不大，表现稳定。"

        top_diff = key_differences[0]
        metric_name = top_diff["metric"]
        best_sim = top_diff["best_simulation"]
        worst_sim = top_diff["worst_simulation"]
        cv = top_diff["coefficient_of_variation"]

        return (
            f"最显著的差异出现在 {metric_name} 指标上，"
            f"变异系数为 {cv:.2%}。"
            f"表现最好的是 {best_sim}，"
            f"最差的是 {worst_sim}。"
        )

    def compare_scenarios(self, scenario_id: str) -> ScenarioComparison:
        """
        对比场景

        Args:
            scenario_id: 场景ID

        Returns:
            场景对比
        """
        # 假设场景ID格式为 "scenario_base_vs_test"
        # 提取基准和测试仿真ID
        if "_vs_" in scenario_id:
            base_sim, test_sim = scenario_id.split("_vs_", 1)
        else:
            base_sim = f"{scenario_id}_base"
            test_sim = f"{scenario_id}_test"

        # 对比两个仿真
        report = self.compare_simulations([base_sim, test_sim])

        # 生成洞察
        insights = self._generate_scenario_insights(report)

        # 提取差异
        differences = {
            "key_differences": report.key_differences,
            "metrics_comparison": report.metrics_comparison
        }

        return ScenarioComparison(
            scenario_name=scenario_id,
            base_simulation=base_sim,
            test_simulation=test_sim,
            differences=differences,
            insights=insights
        )

    def _generate_scenario_insights(self, report: ComparisonReport) -> List[str]:
        """生成场景洞察"""
        insights = []

        for diff in report.key_differences[:5]:  # 只取前最显著的差异
            metric = diff["metric"]
            cv = diff["coefficient_of_variation"]
            best = diff["best_simulation"]
            worst = diff["worst_simulation"]

            insights.append(
                f"{metric} 在不同场景下差异较大（CV={cv:.2%}），"
                f"{best} 表现优于 {worst}"
            )

        return insights

    def generate_comparison_charts(self, comparison: ComparisonReport) -> List[Chart]:
        """
        生成对比图表

        Args:
            comparison: 对比报告

        Returns:
            图表列表
        """
        charts = []

        # 为每个关键差异生成柱状图
        for diff in comparison.key_differences[:10]:
            metric_name = diff["metric"]
            values = diff["values"]

            charts.append(Chart(
                chart_type="bar",
                title=f"{metric_name} 对比",
                data={
                    "labels": list(values.keys()),
                    "values": list(values.values())
                }
            ))

        return charts

    def export_comparison(self, comparison: ComparisonReport, filepath: str) -> bool:
        """
        导出对比报告

        Args:
            comparison: 对比报告
            filepath: 文件路径

        Returns:
            是否成功
        """
        try:
            import json

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(comparison.model_dump(), f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"导出对比报告失败: {e}")
            return False
