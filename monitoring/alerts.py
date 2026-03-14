"""
告警规则配置

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from dataclasses import dataclass
from typing import Callable, List
from enum import Enum


class AlertSeverity(Enum):
    """告警严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """告警规则"""
    name: str
    metric_name: str
    condition: Callable[[float], bool]
    severity: AlertSeverity
    message_template: str


# 预定义告警规则
ALERT_RULES: List[AlertRule] = [
    AlertRule(
        name="high_memory_usage",
        metric_name="memory_usage_percent",
        condition=lambda x: x > 80,
        severity=AlertSeverity.WARNING,
        message_template="内存使用率过高: {value}%"
    ),
    AlertRule(
        name="high_cpu_usage",
        metric_name="cpu_usage_percent",
        condition=lambda x: x > 90,
        severity=AlertSeverity.CRITICAL,
        message_template="CPU使用率过高: {value}%"
    ),
    AlertRule(
        name="api_latency_high",
        metric_name="api_response_time_ms",
        condition=lambda x: x > 1000,
        severity=AlertSeverity.WARNING,
        message_template="API响应时间过长: {value}ms"
    ),
]


def check_alerts(metrics: List[float], rules: List[AlertRule]) -> List[str]:
    """
    检查告警

    Args:
        metrics: 指标值
        rules: 告警规则

    Returns:
        告警消息列表
    """
    alerts = []

    for metric, rule in zip(metrics, rules):
        if rule.condition(metric):
            alert_message = rule.message_template.format(value=metric)
            alerts.append(alert_message)

    return alerts
