"""
并行仿真流程 - 支持批量实验和对比分析

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import asyncio
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json

from application.workflows.multi_round import MultiRoundWorkflow
from application.analysis.experiments import ExperimentManager


@dataclass
class ParallelSimulationConfig:
    """并行仿真配置"""
    simulation_id: str
    config_variants: List[Dict]  # 多个配置变体
    max_concurrent: int = 3  # 最大并发数
    timeout: int = 3600  # 超时时间（秒）
    name: Optional[str] = None  # 实验名称
    description: Optional[str] = None  # 实验描述


@dataclass
class ParallelResult:
    """并行仿真结果"""
    simulation_id: str
    config: Dict
    status: str  # success, failed, timeout
    result: Optional[Dict] = None
    error: Optional[str] = None
    duration: float = 0.0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


@dataclass
class ParallelProgress:
    """并行仿真进度"""
    batch_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    running_tasks: int
    success_rate: float
    eta_seconds: Optional[float] = None


class ParallelSimulationWorkflow:
    """并行仿真工作流"""

    def __init__(self, max_concurrent: int = 3):
        """
        Args:
            max_concurrent: 最大并发数
        """
        self.workflow = MultiRoundWorkflow()
        self.experiment_manager = ExperimentManager()
        self._tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, ParallelResult] = {}
        self._max_concurrent = max_concurrent
        self._start_time: Optional[datetime] = None

    async def execute(
        self,
        config: ParallelSimulationConfig,
        progress_callback: Optional[Callable] = None,
        round_func: Optional[Callable] = None,
        agents_factory: Optional[Callable] = None
    ) -> List[ParallelResult]:
        """
        执行并行仿真

        Args:
            config: 并行仿真配置
            progress_callback: 进度回调函数
            round_func: 单轮执行函数
            agents_factory: 智能体工厂函数

        Returns:
            并行结果列表
        """
        self._start_time = datetime.now()
        results = []
        semaphore = asyncio.Semaphore(config.max_concurrent)

        async def run_single(variant_index: int, variant_config: Dict) -> ParallelResult:
            async with semaphore:
                sim_id = f"{config.simulation_id}_variant_{variant_index}"
                start_time = datetime.now()

                try:
                    # 更新进度
                    if progress_callback:
                        progress_callback({
                            "type": "task_started",
                            "simulation_id": sim_id,
                            "variant_index": variant_index,
                            "total_variants": len(config.config_variants),
                            "config": variant_config
                        })

                    # 创建智能体
                    agents = []
                    if agents_factory:
                        agents = agents_factory(variant_config)

                    # 执行仿真
                    result = await asyncio.wait_for(
                        self.workflow.execute(
                            agents=agents,
                            simulation_id=sim_id,
                            total_rounds=variant_config.get("total_rounds", 100),
                            start_round=variant_config.get("start_round", 0),
                            round_func=round_func,
                            checkpoint_interval=variant_config.get("checkpoint_interval", 10)
                        ),
                        timeout=config.timeout
                    )

                    duration = (datetime.now() - start_time).total_seconds()

                    parallel_result = ParallelResult(
                        simulation_id=sim_id,
                        config=variant_config,
                        status="success",
                        result=result,
                        duration=duration,
                        started_at=start_time.isoformat(),
                        completed_at=datetime.now().isoformat(),
                        metadata={
                            "variant_index": variant_index,
                            "batch_id": config.simulation_id
                        }
                    )

                    # 更新进度
                    if progress_callback:
                        progress_callback({
                            "type": "task_completed",
                            "simulation_id": sim_id,
                            "result": parallel_result
                        })

                    return parallel_result

                except asyncio.TimeoutError:
                    duration = (datetime.now() - start_time).total_seconds()
                    parallel_result = ParallelResult(
                        simulation_id=sim_id,
                        config=variant_config,
                        status="timeout",
                        error="Simulation timeout",
                        duration=duration,
                        started_at=start_time.isoformat(),
                        completed_at=datetime.now().isoformat(),
                        metadata={
                            "variant_index": variant_index,
                            "batch_id": config.simulation_id
                        }
                    )

                    if progress_callback:
                        progress_callback({
                            "type": "task_failed",
                            "simulation_id": sim_id,
                            "result": parallel_result
                        })

                    return parallel_result

                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    parallel_result = ParallelResult(
                        simulation_id=sim_id,
                        config=variant_config,
                        status="failed",
                        error=str(e),
                        duration=duration,
                        started_at=start_time.isoformat(),
                        completed_at=datetime.now().isoformat(),
                        metadata={
                            "variant_index": variant_index,
                            "batch_id": config.simulation_id
                        }
                    )

                    if progress_callback:
                        progress_callback({
                            "type": "task_failed",
                            "simulation_id": sim_id,
                            "result": parallel_result
                        })

                    return parallel_result

        # 创建所有任务
        tasks = [
            run_single(idx, cfg)
            for idx, cfg in enumerate(config.config_variants)
        ]

        # 执行并跟踪进度
        completed = 0
        for task in asyncio.as_completed(tasks):
            result = await task
            results.append(result)
            self._results[result.simulation_id] = result
            completed += 1

            # 更新进度
            if progress_callback:
                progress_callback({
                    "type": "batch_progress",
                    "batch_id": config.simulation_id,
                    "completed": completed,
                    "total": len(config.config_variants),
                    "progress": (completed / len(config.config_variants)) * 100
                })

        # 保存实验结果
        if config.name:
            self._save_experiment_results(config, results)

        return results

    def _save_experiment_results(
        self,
        config: ParallelSimulationConfig,
        results: List[ParallelResult]
    ):
        """
        保存实验结果

        Args:
            config: 并行仿真配置
            results: 结果列表
        """
        experiment_data = {
            "batch_id": config.simulation_id,
            "name": config.name,
            "description": config.description,
            "config_variants": config.config_variants,
            "results": [
                {
                    "simulation_id": r.simulation_id,
                    "status": r.status,
                    "duration": r.duration,
                    "config": r.config,
                    "metadata": r.metadata
                }
                for r in results
            ],
            "created_at": datetime.now().isoformat()
        }

        # 保存到文件
        import os
        output_dir = "data/experiments"
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.join(output_dir, f"{config.simulation_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)

    def cancel(self, simulation_id: str) -> bool:
        """
        取消指定仿真

        Args:
            simulation_id: 仿真ID

        Returns:
            是否成功取消
        """
        if simulation_id in self._tasks:
            self._tasks[simulation_id].cancel()
            return True
        return False

    def cancel_all(self) -> int:
        """
        取消所有仿真

        Returns:
            取消的数量
        """
        count = 0
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
                count += 1
        return count

    def get_result(self, simulation_id: str) -> Optional[ParallelResult]:
        """
        获取指定仿真结果

        Args:
            simulation_id: 仿真ID

        Returns:
            仿真结果，如果不存在则返回None
        """
        return self._results.get(simulation_id)

    def get_all_results(self) -> List[ParallelResult]:
        """
        获取所有结果

        Returns:
            结果列表
        """
        return list(self._results.values())

    def aggregate_results(self, results: List[ParallelResult]) -> Dict:
        """
        聚合结果进行统计分析

        Args:
            results: 并行结果列表

        Returns:
            聚合统计结果
        """
        successful = [r for r in results if r.status == "success"]
        failed = [r for r in results if r.status != "success"]

        durations = [r.duration for r in results if r.duration > 0]

        return {
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results) if results else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "results": successful,
            "errors": failed
        }

    def compare_results(
        self,
        results: List[ParallelResult],
        metrics: List[str]
    ) -> Dict:
        """
        比较不同配置的结果

        Args:
            results: 结果列表
            metrics: 要比较的指标列表

        Returns:
            比较结果
        """
        comparison = []

        for i, result in enumerate(results):
            if result.status == "success" and result.result:
                comparison.append({
                    "variant_index": i,
                    "simulation_id": result.simulation_id,
                    "config": result.config,
                    "metrics": {}
                })

                # 提取指标
                for metric in metrics:
                    value = self._extract_metric(result.result, metric)
                    comparison[-1]["metrics"][metric] = value

        # 计算统计信息
        for metric in metrics:
            values = [r["metrics"].get(metric, 0) for r in comparison]

            if values:
                comparison.append({
                    "type": "statistic",
                    "metric": metric,
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "std": self._calculate_std(values) if len(values) > 1 else 0
                })

        return {
            "comparison": comparison,
            "metrics_compared": metrics
        }

    def _extract_metric(self, result: Dict, metric_path: str) -> Any:
        """
        从结果中提取指标

        Args:
            result: 结果字典
            metric_path: 指标路径（如 "metrics.economic_capability"）

        Returns:
            指标值
        """
        keys = metric_path.split(".")
        value = result

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None

        return value

    def _calculate_std(self, values: List[float]) -> float:
        """
        计算标准差

        Args:
            values: 数值列表

        Returns:
            标准差
        """
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)

        return variance ** 0.5

    def get_progress(self, batch_id: str) -> ParallelProgress:
        """
        获取批次进度

        Args:
            batch_id: 批次ID

        Returns:
            进度信息
        """
        batch_results = [
            r for r in self._results.values()
            if r.metadata.get("batch_id") == batch_id
        ]

        if not batch_results:
            return ParallelProgress(
                batch_id=batch_id,
                total_tasks=0,
                completed_tasks=0,
                failed_tasks=0,
                running_tasks=0,
                success_rate=0.0
            )

        total = len(batch_results)
        completed = sum(1 for r in batch_results if r.status in ["success", "failed", "timeout"])
        failed = sum(1 for r in batch_results if r.status != "success")
        running = total - completed
        success_rate = (completed - failed) / total if total > 0 else 0

        # 计算预计剩余时间
        eta = None
        if self._start_time and completed > 0:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            avg_time = elapsed / completed
            eta = avg_time * (total - completed)

        return ParallelProgress(
            batch_id=batch_id,
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=failed,
            running_tasks=running,
            success_rate=success_rate,
            eta_seconds=eta
        )


def create_parameter_sweep(
    base_config: Dict,
    parameter_name: str,
    values: List[Any]
) -> List[Dict]:
    """
    创建参数扫描配置

    Args:
        base_config: 基础配置
        parameter_name: 参数名称
        values: 参数值列表

    Returns:
        配置变体列表
    """
    variants = []

    for value in values:
        variant = base_config.copy()
        variant[parameter_name] = value
        variants.append(variant)

    return variants


def create_grid_search(
    base_config: Dict,
    parameter_grid: Dict[str, List[Any]]
) -> List[Dict]:
    """
    创建网格搜索配置

    Args:
        base_config: 基础配置
        parameter_grid: 参数网格 {参数名: [值1, 值2, ...]}

    Returns:
        配置变体列表
    """
    import itertools

    # 获取所有参数名和值
    param_names = list(parameter_grid.keys())
    param_values = list(parameter_grid.values())

    # 生成所有组合
    combinations = list(itertools.product(*param_values))

    variants = []
    for combo in combinations:
        variant = base_config.copy()
        for param_name, value in zip(param_names, combo):
            variant[param_name] = value
        variants.append(variant)

    return variants
