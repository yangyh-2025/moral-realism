"""
监控指标收集

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import time


@dataclass
class Metric:
    """指标数据类"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str]


class MetricsCollector:
    """指标收集器"""

    def __init__(self):
        self._metrics: List[Metric] = []

    def record(
        self,
        name: str,
        value: float,
        tags: Dict[str, str] = None
    ):
        """记录指标"""
        metric = Metric(
            name=name,
            value=value,
            timestamp=datetime.now(),
            tags=tags or {}
        )
        self._metrics.append(metric)

    def get_metrics(
        self,
        name: str = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[Metric]:
        """获取指标"""
        metrics = self._metrics

        if name:
            metrics = [m for m in metrics if m.name == name]

        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]

        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]

        return metrics


class Timer:
    """计时器上下文管理器"""

    def __init__(self, collector: MetricsCollector, name: str, tags: Dict[str, str] = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.collector.record(self.name, duration, self.tags)


# 全局指标收集器
metrics_collector = MetricsCollector()
