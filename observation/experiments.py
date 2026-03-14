"""
对照实验管理 - 对应技术方案3.4.3节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field
from datetime import datetime
import numpy as np
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid


class ExperimentType(str, Enum):
    """实验类型"""
    PARAMETER_SWEEP = "parameter_sweep"      # 参数扫描
    AGENT_CONFIGURATION = "agent_configuration"  # 智能体配置变化
    EVENT_SCENARIO = "event_scenario"        # 事件场景
    SENSITIVITY_ANALYSIS = "sensitivity_analysis"  # 敏感性分析


class ExperimentStatus(str, Enum):
    """实验状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExperimentDefinition(BaseModel):
    """实验定义"""
    experiment_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="实验ID")
    experiment_type: ExperimentType = Field(..., description="实验类型")
    name: str = Field(..., description="实验名称")
    description: str = Field(default="", description="实验描述")
    base_config: Dict = Field(default_factory=dict, description="基础配置")
    variations: List[Dict] = Field(default_factory=list, description="变体列表")
    parameters: Dict = Field(default_factory=dict, description="实验参数")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Experiment(BaseModel):
    """实验"""
    experiment_id: str = Field(..., description="实验ID")
    definition: ExperimentDefinition = Field(..., description="实验定义")
    status: ExperimentStatus = Field(default=ExperimentStatus.PENDING, description="状态")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")
    started_at: Optional[str] = Field(None, description="开始时间")
    completed_at: Optional[str] = Field(None, description="完成时间")
    results: Optional[Dict] = Field(None, description="实验结果")
    error: Optional[str] = Field(None, description="错误信息")


class BatchResult(BaseModel):
    """批量结果"""
    experiment_id: str = Field(..., description="实验ID")
    successful: List[str] = Field(default_factory=list, description="成功的实验ID列表")
    failed: List[str] = Field(default_factory=list, description="失败的实验ID列表")
    results: Dict[str, Dict] = Field(default_factory=dict, description="实验结果字典")
    summary: str = Field(default="", description="摘要")
    total_count: int = Field(0, description="总数")
    success_count: int = Field(0, description="成功数")
    failed_count: int = Field(0, description="失败数")


class AnalysisReport(BaseModel):
    """分析报告"""
    experiment_id: str = Field(..., description="实验ID")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")
    statistical_summary: Dict = Field(default_factory=dict, description="统计摘要")
    visualizations: List[Dict] = Field(default_factory=list, description="可视化数据")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Variation(BaseModel):
    """参数变体"""
    name: str = Field(..., description="变体名称")
    parameters: Dict = Field(..., description="参数")
    description: str = Field(default="", description="描述")


class ExperimentFramework:
    """实验框架"""

    def __init__(self, config: Optional[Dict] = None, max_workers: int = 4):
        """
        Args:
            config: 实验配置
            max_workers: 最大工作线程数
        """
        self.config = config or {}
        self._experiments: Dict[str, Experiment] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._simulation_runner: Optional[Callable] = None
        self.results_dir = self.config.get("results_dir", "data/experiments/results")
        os.makedirs(self.results_dir, exist_ok=True)

    def set_simulation_runner(self, runner: Callable):
        """
        设置仿真运行器

        Args:
            runner: 仿真运行函数
        """
        self._simulation_runner = runner

    def define_experiment(
        self,
        experiment_type: ExperimentType,
        name: str,
        base_config: Dict,
        variations: List[Dict],
        description: str = "",
        parameters: Optional[Dict] = None
    ) -> Experiment:
        """
        定义实验

        Args:
            experiment_type: 实验类型
            name: 实验名称
            base_config: 基础配置
            variations: 变体列表
            description: 实验描述
            parameters: 实验参数

        Returns:
            实验
        """
        definition = ExperimentDefinition(
            experiment_type=experiment_type,
            name=name,
            description=description,
            base_config=base_config,
            variations=variations,
            parameters=parameters or {}
        )

        experiment = Experiment(experiment_id=definition.experiment_id, definition=definition)
        self._experiments[experiment.experiment_id] = experiment

        return experiment

    def define_parameter_sweep(
        self,
        name: str,
        base_config: Dict,
        parameter_name: str,
        values: List[float],
        description: str = ""
    ) -> Experiment:
        """
        定义参数扫描实验

        Args:
            name: 实验名称
            base_config: 基础配置
            parameter_name: 参数名称
            values: 参数值列表
            description: 实验描述

        Returns:
            实验
        """
        variations = []
        for i, value in enumerate(values):
            var_config = base_config.copy()
            var_config[parameter_name] = value
            variations.append({
                "name": f"{parameter_name}={value}",
                "config": var_config,
                "value": value
            })

        return self.define_experiment(
            experiment_type=ExperimentType.PARAMETER_SWEEP,
            name=name,
            base_config=base_config,
            variations=variations,
            description=description or f"扫描参数 {parameter_name} 的值"
        )

    def define_sensitivity_analysis(
        self,
        name: str,
        base_config: Dict,
        parameters: Dict[str, List[float]],
        description: str = ""
    ) -> Experiment:
        """
        定义敏感性分析实验

        Args:
            name: 实验名称
            base_config: 基础配置
            parameters: 参数字典 {参数名: [值列表]}
            description: 实验描述

        Returns:
            实验
        """
        variations = []

        # 为每个参数创建变体
        for param_name, param_values in parameters.items():
            for value in param_values:
                var_config = base_config.copy()
                var_config[param_name] = value
                variations.append({
                    "name": f"{param_name}={value}",
                    "config": var_config,
                    "parameter": param_name,
                    "value": value
                })

        return self.define_experiment(
            experiment_type=ExperimentType.SENSITIVITY_ANALYSIS,
            name=name,
            base_config=base_config,
            variations=variations,
            description=description or f"分析参数敏感性"
        )

    def run_experiment(self, experiment: Experiment) -> Dict:
        """
        运行实验

        Args:
            experiment: 实验

        Returns:
            实验结果
        """
        if self._simulation_runner is None:
            raise RuntimeError("仿真运行器未设置，请使用 set_simulation_runner() 设置")

        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.now().isoformat()

        try:
            results = {}

            for variation in experiment.definition.variations:
                var_name = variation.get("name", "unknown")
                var_config = variation.get("config", {})

                # 运行仿真
                sim_result = self._simulation_runner(var_config)
                results[var_name] = sim_result

            experiment.results = results
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.now().isoformat()

            # 保存结果
            self._save_experiment_results(experiment)

            return results

        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.error = str(e)
            experiment.completed_at = datetime.now().isoformat()
            raise

    def run_batch_experiments(self, experiments: List[Experiment]) -> BatchResult:
        """
        批量运行实验

        Args:
            experiments: 实验列表

        Returns:
            批量结果
        """
        batch_id = str(uuid.uuid4())
        successful = []
        failed = []
        results = {}

        # 并行执行实验
        futures = {}
        for experiment in experiments:
            future = self._executor.submit(self.run_experiment, experiment)
            futures[future] = experiment

        for future in as_completed(futures):
            experiment = futures[future]
            try:
                result = future.result()
                successful.append(experiment.experiment_id)
                results[experiment.experiment_id] = result
            except Exception as e:
                failed.append(experiment.experiment_id)
                print(f"实验 {experiment.experiment_id} 失败: {e}")

        summary = f"批量实验完成：成功 {len(successful)}/{len(experiments)}，失败 {len(failed)}/{len(experiments)}"

        return BatchResult(
            experiment_id=batch_id,
            successful=successful,
            failed=failed,
            results=results,
            summary=summary,
            total_count=len(experiments),
            success_count=len(successful),
            failed_count=len(failed)
        )

    def _save_experiment_results(self, experiment: Experiment):
        """保存实验结果"""
        result_file = os.path.join(self.results_dir, f"{experiment.experiment_id}.json")

        result_data = {
            "experiment_id": experiment.experiment_id,
            "name": experiment.definition.name,
            "type": experiment.definition.experiment_type.value,
            "status": experiment.status.value,
            "results": experiment.results,
            "completed_at": experiment.completed_at
        }

        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存实验结果失败: {e}")

    def load_experiment_results(self, experiment_id: str) -> Optional[Dict]:
        """
        加载实验结果

        Args:
            experiment_id: 实验ID

        Returns:
            实验结果
        """
        result_file = os.path.join(self.results_dir, f"{experiment_id}.json")

        if os.path.exists(result_file):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载实验结果失败: {e}")

        return None

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """
        获取实验

        Args:
            experiment_id: 实验ID

        Returns:
            实验
        """
        return self._experiments.get(experiment_id)

    def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[Experiment]:
        """
        列出实验

        Args:
            status: 过滤状态

        Returns:
            实验列表
        """
        experiments = list(self._experiments.values())

        if status:
            experiments = [e for e in experiments if e.status == status]

        return experiments


class ExperimentAnalyzer:
    """实验分析器"""

    def __init__(self):
        pass

    def analyze_results(self, results: List[Dict]) -> AnalysisReport:
        """
        分析结果

        Args:
            results: 结果列表

        Returns:
            分析报告
        """
        if not results:
            return AnalysisReport(key_findings=["没有可分析的结果"])

        report = AnalysisReport()

        # 提取指标值
        metric_values = self._extract_metric_values(results)

        # 统计分析
        for metric_name, values in metric_values.items():
            if values:
                report.statistical_summary[metric_name] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values)),
                    "median": float(np.median(values)),
                    "count": len(values)
                }

        # 生成关键发现
        for metric_name, stats in report.statistical_summary.items():
            cv = stats["std"] / stats["mean"] if stats["mean"] != 0 else 0
            if cv > 0.5:
                report.key_findings.append(
                    f"{metric_name} 的变异系数为 {cv:.2f}，表现出较高的敏感性"
                )
            elif cv < 0.1:
                report.key_findings.append(
                    f"{metric_name} 的变异系数为 {cv:.2f}，相对稳定"
                )

        # 生成可视化数据
        report.visualizations = self._generate_visualizations(metric_values)

        # 生成建议
        report.recommendations = self._generate_recommendations(metric_values, report.statistical_summary)

        return report

    def _extract_metric_values(self, results: List[Dict]) -> Dict[str, List[float]]:
        """提取指标值"""
        metric_values = defaultdict(list)

        for result in results:
            if "metrics" in result:
                metrics = result["metrics"]
                for category, metric_list in metrics.items():
                    for metric in metric_list:
                        name = metric.get("name", "unknown")
                        value = metric.get("value", 0)
                        metric_values[name].append(float(value))

        return dict(metric_values)

    def _generate_visualizations(self, metric_values: Dict[str, List[float]]) -> List[Dict]:
        """生成可视化数据"""
        visualizations = []

        for metric_name, values in metric_values.items():
            if len(values) > 1:
                # 箱线图数据
                visualizations.append({
                    "type": "boxplot",
                    "title": f"{metric_name} 分布",
                    "data": values,
                    "metric": metric_name
                })

                # 折线图数据
                visualizations.append({
                    "type": "line",
                    "title": f"{metric_name} 趋势",
                    "data": {
                        "x": list(range(len(values))),
                        "y": values
                    },
                    "metric": metric_name
                })

        return visualizations

    def _generate_recommendations(
        self,
        metric_values: Dict[str, List[float]],
        statistical_summary: Dict
    ) -> List[str]:
        """生成建议"""
        recommendations = []

        for metric_name, values in metric_values.items():
            stats = statistical_summary.get(metric_name, {})

            # 基于变异系数的建议
            if stats.get("mean", 0) != 0:
                cv = stats.get("std", 0) / stats["mean"]
                if cv > 0.5:
                    recommendations.append(
                        f"{metric_name} 对参数变化敏感，建议进一步分析其影响因素"
                    )

        return recommendations

    def generate_report(self, analysis: AnalysisReport) -> str:
        """
        生成报告

        Args:
            analysis: 分析报告

        Returns:
            报告文本
        """
        report_lines = [
            "=" * 80,
            "实验分析报告",
            "=" * 80,
            f"生成时间: {analysis.generated_at}",
            "",
            "关键发现:",
            "-" * 40
        ]

        for i, finding in enumerate(analysis.key_findings, 1):
            report_lines.append(f"{i}. {finding}")

        report_lines.extend([
            "",
            "统计摘要:",
            "-" * 40
        ])

        for metric_name, stats in analysis.statistical_summary.items():
            report_lines.append(f"\n{metric_name}:")
            report_lines.append(f"  平均值: {stats['mean']:.4f}")
            report_lines.append(f"  标准差: {stats['std']:.4f}")
            report_lines.append(f"  最小值: {stats['min']:.4f}")
            report_lines.append(f"  最大值: {stats['max']:.4f}")
            report_lines.append(f"  中位数: {stats['median']:.4f}")
            report_lines.append(f"  样本数: {stats['count']}")

        if analysis.recommendations:
            report_lines.extend([
                "",
                "建议:",
                "-" * 40
            ])
            for i, rec in enumerate(analysis.recommendations, 1):
                report_lines.append(f"{i}. {rec}")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)

    def export_results(self, results: List[Dict], format: str = "json") -> str:
        """
        导出结果

        Args:
            results: 结果列表
            format: 格式 (json, csv)

        Returns:
            导出文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format format == "json":
            output_dir = "data/experiments/exports"
            os.makedirs(output_dir, exist_ok=True)
            filename = f"results_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)

            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                return filepath
            except Exception as e:
                print(f"导出JSON失败: {e}")
                return ""

        elif format == "csv":
            import csv

            output_dir = "data/experiments/exports"
            os.makedirs(output_dir, exist_ok=True)
            filename = f"results_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)

            try:
                # 收集所有可能的字段
                all_fields = set()
                for result in results:
                    all_fields.update(result.keys())

                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
                    writer.writeheader()
                    writer.writerows(results)

                return filepath
            except Exception as e:
                print(f"导出CSV失败: {e}")
                return ""

        return ""
