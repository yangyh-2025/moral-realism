"""
指标计算模块完善 - 对应技术方案3.4.1节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from enum import Enum
import numpy as np
from collections import defaultdict
from datetime import datetime
import pickle
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# 导入扩展指标计算器
try:
    from application.analysis.order_metrics_calculator import (
        ExtendedEnvironmentMetricsCalculator,
        OrderTypeMetricsCalculator
    )
    _EXTENDED_CALCULATORS_AVAILABLE = True
except ImportError:
    _EXTENDED_CALCULATORS_AVAILABLE = False


class MetricCategory(str, Enum):
    """指标类别"""
    INDEPENDENT = "independent"      # 自变量
    INTERMEDIARY = "intermediary"    # 中介变量
    ENVIRONMENT = "environment"      # 体系环境指标
    DEPENDENT = "dependent"          # 因变量


class Metric(BaseModel):
    """指标"""
    name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    category: str = Field(..., description="指标类别")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    round: int = Field(..., description="所属轮次")
    metadata: Dict = Field(default_factory=dict, description="元数据")


class MetricsResult(BaseModel):
    """指标结果"""
    simulation_id: str = Field(..., description="仿真ID")
    round: int = Field(..., description="轮次")
    metrics: Dict[str, List[Metric]] = Field(default_factory=dict, description="指标字典")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CalculationContext(BaseModel):
    """计算上下文"""
    simulation_id: str = Field(..., description="仿真ID")
    round: int = Field(..., description="当前轮次")
    agents: List[Dict] = Field(default_factory=list, description="智能体状态列表")
    interactions: List[Dict] = Field(default_factory=list, description="互动记录列表")
    events: List[Dict] = Field(default_factory=list, description="事件列表")
    previous_state: Dict = Field(default_factory=dict, description="上一轮状态")


class MetricCalculator(ABC):
    """指标计算器基类"""

    @abstractmethod
    def get_name(self) -> str:
        """获取计算器名称"""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """获取指标类别"""
        pass

    @abstractmethod
    def calculate(self, context: CalculationContext) -> List[Metric]:
        """
        计算指标

        Args:
            context: 计算上下文

        Returns:
            指标列表
        """
        pass

    def get_cache_key(self, context: CalculationContext) -> str:
        """
        获取缓存键

        Args:
            context: 计算上下文

        Returns:
            缓存键
        """
        data_str = json.dumps({
            "calculator": self.get_name(),
            "round": context.round,
            "agents_count": len(context.agents),
            "interactions_count": len(context.interactions),
            "events_count": len(context.events)
        }, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()


class IndependentMetricsCalculator(MetricCalculator):
    """自变量指标计算器"""

    def get_name(self) -> str:
        return "independent_metrics"

    def get_category(self) -> str:
        return MetricCategory.INDEPENDENT.value

    def calculate(self, context: CalculationContext) -> List[Metric]:
        metrics = []
        for agent in context.agents:
            agent_id = agent.get("agent_id", "unknown")

            # 综合实力指数
            comprehensive_power = agent.get("comprehensive_power", 0)
            metrics.append(Metric(
                name=f"{agent_id}_comprehensive_power",
                value=comprehensive_power,
                category=self.get_category(),
                round=context.round,
                metadata={"agent_id": agent_id, "unit": "分"}
            ))

            # 实力增长率
            prev_agents = context.previous_state.get("agents", [])
            prev_agent = next((a for a in prev_agents if a.get("agent_id") == agent_id), None)
            if prev_agent:
                prev_power = prev_agent.get("comprehensive_power", 0)
                growth_rate = ((comprehensive_power - prev_power) / prev_power * 100) if prev_power > 0 else 0
                metrics.append(Metric(
                    name=f"{agent_id}_power_growth_rate",
                    value=growth_rate,
                    category=self.get_category(),
                    round=context.round,
                    metadata={"agent_id": agent_id, "unit": "%"}
                ))

        return metrics


class IntermediaryMetricsCalculator(MetricCalculator):
    """中介变量指标计算器"""

    def get_name(self) -> str:
        return "intermediary_metrics"

    def get_category(self) -> str:
        return MetricCategory.INTERMEDIARY.value

    def calculate(self, context: CalculationContext) -> List[Metric]:
        metrics = []
        interactions = context.interactions

        if not interactions:
            return metrics

        total_interactions = len(interactions)

        # 多边合作偏好
        multilateral_cooperations = sum(
            1 for i in interactions
            if "multilateral" in i.get("interaction_type", "").lower()
        )
        multilateral_preference = (multilateral_cooperations / total_interactions * 100) if total_interactions > 0 else 0
        metrics.append(Metric(
            name="multilateral_cooperation_preference",
            value=multilateral_preference,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "%", "total": total_interactions}
        ))

        # 单边行动比率
        unilateral_actions = sum(
            1 for i in interactions
            if "unilateral" in i.get("interaction_type", "").lower()
        )
        unilateral_ratio = (unilateral_actions / total_interactions * 100) if total_interactions > 0 else 0
        metrics.append(Metric(
            name="unilateral_action_ratio",
            value=unilateral_ratio,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "%"}
        ))

        # 联盟形成率
        alliances = sum(1 for i in interactions if "alliance" in i.get("interaction_type", "").lower())
        alliance_formation_rate = (alliances / total_interactions * 100) if total_interactions > 0 else 0
        metrics.append(Metric(
            name="alliance_formation_rate",
            value=alliance_formation_rate,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "%"}
        ))

        return metrics


class EnvironmentMetricsCalculator(MetricCalculator):
    """体系环境指标计算器"""

    def get_name(self) -> str:
        return "environment_metrics"

    def get_category(self) -> str:
        return MetricCategory.ENVIRONMENT.value

    def calculate(self, context: CalculationContext) -> List[Metric]:
        metrics = []
        events = context.events

        # 国际规范有效性指数
        norms = [e for e in events if e.get("event_type") == "norm"]
        if norms:
            avg_validity = sum(n.get("validity", 0) for n in norms) / len(norms)
            avg_adherence = sum(n.get("adherence_rate", 0) for n in norms) / len(norms)
            norm_effectiveness = (avg_validity * avg_adherence) / 100
        else:
            norm_effectiveness = 0.0

        metrics.append(Metric(
            name="international_norm_effectiveness",
            value=norm_effectiveness,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "分"}
        ))

        # 冲突水平
        conflicts = [e for e in events if e.get("event_type") == "conflict"]
        conflict_level = sum(c.get("severity", 1) for c in conflicts)
        metrics.append(Metric(
            name="conflict_level",
            value=conflict_level,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "分"}
        ))

        # 体系稳定性
        stability_score = 100 - min(conflict_level, 50)
        metrics.append(Metric(
            name="system_stability",
            value=stability_score,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "分"}
        ))

        return metrics


class DependentMetricsCalculator(MetricCalculator):
    """因变量指标计算器"""

    def get_name(self) -> str:
        return "dependent_metrics"

    def get_category(self) -> str:
        return MetricCategory.DEPENDENT.value

    def calculate(self, context: CalculationContext) -> List[Metric]:
        metrics = []
        agent_powers = [a.get("comprehensive_power", 0) for a in context.agents]

        if not agent_powers:
            return metrics

        # 实力集中度指数
        total_power = sum(agent_powers)
        if total_power > 0:
            top3_power = sum(sorted(agent_powers, reverse=True)[:3])
            power_concentration = (top3_power / total_power) * 100
        else:
            power_concentration = 0.0

        metrics.append(Metric(
            name="power_concentration_index",
            value=power_concentration,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "%"}
        ))

        # 实力分布离散度
        if len(agent_powers) > 1:
            power_std = np.std(agent_powers)
            power_mean = np.mean(agent_powers)
            dispersion = (power_std / power_mean * 100) if power_mean > 0 else 0
        else:
            dispersion = 0.0

        metrics.append(Metric(
            name="power_distribution_dispersion",
            value=dispersion,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "%"}
        ))

        return metrics


class MetricsPipeline:
    """指标计算流水线"""

    def __init__(self, calculators: Optional[List[MetricCalculator]] = None, max_workers: int = 4):
        """
        Args:
            calculators: 指标计算器列表
            max_workers: 最大工作线程数
        """
        # 如果没有提供计算器列表，使用默认计算器
        if calculators is None:
            default_calculators = [
                IndependentMetricsCalculator(),
                IntermediaryMetricsCalculator(),
                EnvironmentMetricsCalculator(),
                DependentMetricsCalculator()
            ]
            # 添加扩展计算器（如果可用）
            if _EXTENDED_CALCULATORS_AVAILABLE:
                default_calculators.append(ExtendedEnvironmentMetricsCalculator())
                default_calculators.append(OrderTypeMetricsCalculator())
            self.calculators = default_calculators
        else:
            self.calculators = calculators

        self._cache = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def register_calculator(self, calculator: MetricCalculator):
        """
        注册计算器

        Args:
            calculator: 指标计算器
        """
        if calculator not in self.calculators:
            self.calculators.append(calculator)

    def _calculate_single(self, calculator: MetricCalculator, context: CalculationContext) -> List[Metric]:
        """单个计算器计算"""
        return calculator.calculate(context)

    def calculate_all(self, context: CalculationContext, use_cache: bool = True) -> MetricsResult:
        """
        计算所有指标

        Args:
            context: 计算上下文
            use_cache: 是否使用缓存

        Returns:
            指标结果
        """
        all_metrics = defaultdict(list)

        # 并行计算
        futures = {}
        for calculator in self.calculators:
            cache_key = calculator.get_cache_key(context)

            if use_cache and cache_key in self._cache:
                # 使用缓存
                all_metrics[calculator.get_category()].extend(self._cache[cache_key])
            else:
                # 提交计算任务
                future = self._executor.submit(self._calculate_single, calculator, context)
                futures[future] = (calculator, cache_key)

        # 收集结果
        for future in as_completed(futures):
            calculator, cache_key = futures[future]
            try:
                metrics = future.result()
                if use_cache:
                    self._cache[cache_key] = metrics
                all_metrics[calculator.get_category()].extend(metrics)
            except Exception as e:
                print(f"计算器 {calculator.get_name()} 执行失败: {e}")

        return MetricsResult(
            simulation_id=context.simulation_id,
            round=context.round,
            metrics=dict(all_metrics)
        )

    def calculate_incremental(self, context: CalculationContext) -> MetricsResult:
        """
        增量计算指标

        Args:
            context: 计算上下文

        Returns:
            指标结果
        """
        return self.calculate_all(context, use_cache=False)

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()

    async def calculate_round_metrics(
        self,
        agents: List[Any],
        simulation_id: str,
        round: int,
        interactions: Optional[List[Dict]] = None,
        events: Optional[List[Dict]] = None,
        previous_state: Optional[Dict] = None,
        logger: Optional[Any] = None
    ) -> Dict:
        """
        计算单轮指标（异步方法，用于单轮工作流）

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            round: 当前轮次
            interactions: 互动记录（可选）
            events: 事件列表（可选）
            previous_state: 上一轮状态（可选）
            logger: 日志记录器（可选）

        Returns:
            指标字典
        """
        # 提取智能体状态
        agent_states = []
        for agent in agents:
            if hasattr(agent, 'state'):
                # 对于 BaseAgent 实例
                state_dict = {
                    'agent_id': agent.state.agent_id,
                    'name': agent.state.name,
                    'comprehensive_power': agent.state.power_metrics.calculate_comprehensive_power() if agent.state.power_metrics else 0,
                    'power_metrics': agent.state.power_metrics.__dict__ if agent.state.power_metrics else {},
                    'region': agent.state.region
                }
            agent_states.append(state_dict)

        # 构建计算上下文
        context = CalculationContext(
            simulation_id=simulation_id,
            round=round,
            agents=agent_states,
            interactions=interactions or [],
            events=events or [],
            previous_state=previous_state or {}
        )

        # 计算所有指标
        result = self.calculate_all(context, use_cache=False)

        # 将结果转换为字典格式
        metrics_dict = {}
        for category, metrics in result.metrics.items():
            metrics_dict[category] = [m.dict() if hasattr(m, 'dict') else m for m in metrics]

        # 如果有logger，记录指标到JSON
        if logger and hasattr(logger, 'log_environment_indicators'):
            # 记录环境指标
            env_indicators = metrics_dict.get('environment', [])
            if env_indicators:
                indicators_dict = {}
                for metric in env_indicators:
                    if isinstance(metric, dict):
                        indicators_dict[metric.get('name', '')] = metric.get('value', 0)
                logger.log_environment_indicators(simulation_id, round, indicators_dict)

            # 记录秩序指标
            dependent_metrics = metrics_dict.get('dependent', [])
            if dependent_metrics:
                for metric in dependent_metrics:
                    if isinstance(metric, dict):
                        name = metric.get('name', '')
                        if name == 'international_order_type':
                            order_type = metric.get('metadata', {}).get('order_type', 'unknown')
                            confidence = metric.get('metadata', {}).get('confidence', 0.0)
                            logger.log_order_metrics(simulation_id, round, order_type, confidence, metric.get('metadata', {}))

            # 记录实力指标
            independent_metrics = metrics_dict.get('independent', [])
            if independent_metrics:
                for metric in independent_metrics:
                    if isinstance(metric, dict):
                        name = metric.get('name', '')
                        if '_comprehensive_power' in name:
                            agent_id = metric.get('metadata', {}).get('agent_id', '')
                            agent_name = None
                            for agent in agents:
                                if hasattr(agent, 'state') and agent.state.agent_id == agent_id:
                                    agent_name = agent.state.name
                                    break
                            if agent_name:
                                power_metrics = metric.get('metadata', {})
                                logger.log_power_metrics(
                                    simulation_id=simulation_id,
                                    round=round,
                                    agent_id=agent_id,
                                    agent_name=agent_name,
                                    power_metrics=power_metrics,
                                    comprehensive_power=metric.get('value', 0)
                                )

        return metrics_dict

    def export_metrics_to_json(
        self,
        simulation_id: str,
        metrics_dict: Dict,
        log_dir: str = "logs"
    ) -> None:
        """
        将指标导出到JSON文件（存储在仿真特定的文件夹中）

        Args:
            simulation_id: 仿真ID
            metrics_dict: 指标字典
            log_dir: 日志目录
        """
        try:
            from pathlib import Path
            import os

            # 创建仿真特定的日志文件夹
            sim_log_dir = Path(log_dir) / simulation_id
            sim_log_dir.mkdir(parents=True, exist_ok=True)

            # 导出完整的指标数据
            metrics_file = sim_log_dir / "metrics_summary.json"
            export_data = {
                "simulation_id": simulation_id,
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics_dict
            }

            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            # 导出各分类指标
            for category, metrics in metrics_dict.items():
                if metrics:
                    category_file = sim_log_dir / f"{category}_metrics.json"
                    with open(category_file, 'w', encoding='utf-8') as f:
                        json.dump(metrics, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"导出指标JSON失败: {e}")


class MetricsCache:
    """指标缓存"""

    def __init__(self, cache_dir: str = "data/cache/metrics"):
        """
        Args:
            cache_dir: 缓存目录
        """
        self.cache_dir = cache_dir
        self._cache = {}
        self._timestamps = {}
        os.makedirs(cache_dir, exist_ok=True)

    def get_cached_metrics(self, simulation_id: str, round: int) -> Optional[MetricsResult]:
        """
        获取缓存的指标

        Args:
            simulation_id: 仿真ID
            round: 轮次

        Returns:
            缓存的指标，如果不存在则返回None
        """
        cache_key = f"{simulation_id}_round_{round}"

        # 内存缓存
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 磁盘缓存
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    metrics = pickle.load(f)
                    self._cache[cache_key] = metrics
                    return metrics
            except Exception as e:
                print(f"加载缓存失败: {e}")

        return None

    def cache_metrics(self, simulation_id: str, metrics: MetricsResult):
        """
        缓存指标

        Args:
            simulation_id: 仿真ID
            round: 轮次
            metrics: 指标结果
        """
        cache_key = f"{simulation_id}_round_{round}"

        # 内存缓存
        self._cache[cache_key] = metrics
        self._timestamps[cache_key] = datetime.now().isoformat()

        # 磁盘缓存
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(metrics, f)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def invalidate_cache(self, simulation_id: Optional[str] = None):
        """
        使缓存失效

        Args:
            simulation_id: 仿真ID，如果为None则清空所有缓存
        """
        if simulation_id is None:
            # 清空所有缓存
            self._cache.clear()
            self._timestamps.clear()
        else:
            # 清空特定仿真的缓存
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{simulation_id}_")]
            for key in keys_to_remove:
                del self._cache[key]
                del self._timestamps[key]

    def get_cache_info(self) -> Dict:
        """
        获取缓存信息

        Returns:
            缓存信息字典
        """
        return {
            "memory_cache_size": len(self._cache),
            "cache_keys": list(self._cache.keys()),
            "timestamps": self._timestamps.copy()
        }


class TrendDirection(str, Enum):
    """趋势方向"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class TrendResult(BaseModel):
    """趋势结果"""
    direction: TrendDirection = Field(..., description="趋势方向")
    slope: float = Field(..., description="斜率")
    confidence: float = Field(..., description="置信度")
    description: str = Field(..., description="描述")


class Anomaly(BaseModel):
    """异常"""
    position: int = Field(..., description="位置")
    value: float = Field(..., description="实际值")
    expected_value: float = Field(..., description="期望值")
    severity: float = Field(..., description="严重程度")
    description: str = Field(..., description="描述")


class TrendAnalyzer:
    """趋势分析器"""

    def analyze_trend(self, metrics: List[float], window_size: int = 3) -> TrendResult:
        """
        分析趋势

        Args:
            metrics: 指标序列
            window_size: 窗口大小

        Returns:
            趋势结果
        """
        if len(metrics) < 2:
            return TrendResult(
                direction=TrendDirection.STABLE,
                slope=0.0,
                confidence=0.0,
                description="数据不足，无法分析趋势"
            )

        # 使用移动平均平滑数据
        smoothed = self._moving_average(metrics, window_size) if len(metrics) >= window_size else metrics

        # 计算线性回归斜率
        x = np.arange(len(smoothed))
        y = np.array(smoothed)

        try:
            slope, intercept = np.polyfit(x, y, 1)

            # 计算R²
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            confidence = abs(r_squared)

            # 判断方向
            if abs(slope) < 0.01:
                direction = TrendDirection.STABLE
                description = "趋势稳定"
            elif slope > 0:
                direction = TrendDirection.UP
                description = f"上升趋势，斜率={slope:.4f}"
            else:
                direction = TrendDirection.DOWN
                description = f"下降趋势，斜率={slope:.4f}"

            return TrendResult(
                direction=direction,
                slope=slope,
                confidence=confidence,
                description=description
            )
        except Exception as e:
            return TrendResult(
                direction=TrendDirection.STABLE,
                slope=0.0,
                confidence=0.0,
                description=f"趋势分析失败: {e}"
            )

    def detect_anomalies(self, metrics: List[float], method: str = "zscore", threshold: float = 2.0) -> List[Anomaly]:
        """
        检测异常

        Args:
            metrics: 指标序列
            method: 检测方法 (zscore, iqr, percentile)
            threshold: 阈值

        Returns:
            异常列表
        """
        if len(metrics) < 3:
            return []

        anomalies = []

        if method == "zscore":
            # Z-score方法
            mean = np.mean(metrics)
            std = np.std(metrics)
            if std > 0:
                z_scores = [(m - mean) / std for m in metrics]
                for i, (z, val) in enumerate(zip(z_scores, metrics)):
                    if abs(z) > threshold:
                        severity = min(abs(z) / 3, 1.0)
                        anomalies.append(Anomaly(
                            position=i,
                            value=val,
                            expected_value=mean,
                            severity=severity,
                            description=f"Z-score={z:.2f}，偏离均值{abs(val - mean):.2f}"
                        ))

        elif method == "iqr":
            # IQR方法
            q1, q3 = np.percentile(metrics, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            for i, val in enumerate(metrics):
                if val < lower_bound or val > upper_bound:
                    expected = q1 + iqr / 2
                    severity = min(abs(val - expected) / iqr, 1.0)
                    anomalies.append(Anomaly(
                        position=i,
                        value=val,
                        expected_value=expected,
                        severity=severity,
                        description=f"超出IQR范围[{lower_bound:.2f}, {upper_bound:.2f}]"
                    ))

        elif method == "percentile":
            # 百分位数方法
            lower_percentile = threshold
            upper_percentile = 100 - threshold
            lower_bound = np.percentile(metrics, lower_percentile)
            upper_bound = np.percentile(metrics, upper_percentile)

            for i, val in enumerate(metrics):
                if val < lower_bound or val > upper_bound:
                    expected = np.median(metrics)
                    severity = min(abs(val - expected) / (upper_bound - lower_bound), 1.0)
                    anomalies.append(Anomaly(
                        position=i,
                        value=val,
                        expected_value=expected,
                        severity=severity,
                        description=f"超出百分位数范围[{lower_bound:.2f}, {upper_bound:.2f}]"
                    ))

        return anomalies

    def forecast_trend(self, metrics: List[float], periods: int = 5, method: str = "linear") -> List[float]:
        """
        预测趋势

        Args:
            metrics: 指标序列
            periods: 预测周期数
            method: 预测方法 (linear, moving_average, exponential)

        Returns:
            预测值列表
        """
        if len(metrics) < 2:
            return [metrics[-1]] * periods if metrics else [0.0] * periods

        forecasts = []

        if method == "linear":
            # 线性回归预测
            x = np.arange(len(metrics))
            y = np.array(metrics)
            try:
                slope, intercept = np.polyfit(x, y, 1)
                for i in range(1, periods + 1):
                    forecast = slope * (len(metrics) + i - 1) + intercept
                    forecasts.append(float(forecast))
            except Exception:
                forecasts = [metrics[-1]] * periods

        elif method == "moving_average":
            # 移动平均预测
            window_size = min(len(metrics), 5)
            ma = sum(metrics[-window_size:]) / window_size
            forecasts = [ma] * periods

        elif method == "exponential":
            # 指数平滑预测
            alpha = 0.3
            forecast = metrics[0]
            for val in metrics[1:]:
                forecast = alpha * val + (1 - alpha) * forecast

            for _ in range(periods):
                forecasts.append(forecast)

        else:
            forecasts = [metrics[-1]] * periods

        return forecasts

    def _moving_average(self, data: List[float], window_size: int) -> List[float]:
        """计算移动平均"""
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid').tolist()
