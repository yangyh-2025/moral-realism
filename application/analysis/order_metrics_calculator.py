"""
秩序类型指标计算器 - 扩展指标计算系统

添加秩序判定所需的新指标计算器

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from collections import defaultdict
import logging

from application.analysis.metrics import MetricCalculator, CalculationContext, Metric, MetricCategory
from domain.analysis.order_evaluation import OrderEvaluator, OrderEvaluationContext, OrderEvaluationResult, ORDER_TYPE_CN

logger = logging.getLogger(__name__)


class ExtendedEnvironmentMetricsCalculator(MetricCalculator):
    """
    扩展环境指标计算器

    添加秩序判定所需的新指标：
    - 制度化程度指数
    - 有效联盟数量

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def get_name(self) -> str:
        return "extended_environment_metrics"

    def get_category(self) -> str:
        return MetricCategory.ENVIRONMENT.value

    def calculate(self, context: CalculationContext) -> List[Metric]:
        """
        计算扩展环境指标

        Args:
            context: 计算上下文

        Returns:
            指标列表
        """
        metrics = []
        events = context.events
        interactions = context.interactions

        # 1. 制度化程度指数计算
        institutionalization_index = self._calculate_institutionalization_index(events)
        metrics.append(Metric(
            name="institutionalization_index",
            value=institutionalization_index,
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "%", "description": "制度化程度指数"}
        ))

        # 2. 有效联盟数量统计
        alliance_count = self._count_effective_alliances(interactions)
        metrics.append(Metric(
            name="alliance_count",
            value=float(alliance_count),
            category=self.get_category(),
            round=context.round,
            metadata={"unit": "个", "description": "有效联盟数量"}
        ))

        return metrics

    def _calculate_institutionalization_index(self, events: List[Dict]) -> float:
        """
        计算制度化程度指数

        基于国际机构、条约和多边机制的活跃程度

        Args:
            events: 事件列表

        Returns:
            制度化程度指数 (0-100)
        """
        # 统计不同类型的制度化事件
        institution_events = [
            e for e in events
            if e.get("event_type") in ["institution", "treaty", "multilateral_organ"]
        ]

        if not institution_events:
            return 0.0

        # 基础分数：每个制度化事件贡献一定分数
        base_score = len(institution_events) * 10.0

        # 根据事件有效性进行调整
        total_validity = 0.0
        for event in institution_events:
            validity = event.get("validity", 50.0)  # 默认中等有效性
            adherence = event.get("adherence_rate", 50.0)
            total_validity += (validity * adherence) / 100.0

        if len(institution_events) > 0:
            avg_validity = total_validity / len(institution_events)
        else:
            avg_validity = 0.0

        # 综合得分
        institutionalization = (base_score + avg_validity) / 2.0

        # 限制在0-100范围内
        return max(0.0, min(100.0, institutionalization))

    def _count_effective_alliances(self, interactions: List[Dict]) -> int:
        """
        统计有效联盟数量

        统计当前活跃的、具有约束力的联盟

        Args:
            interactions: 互动列表

        Returns:
            有效联盟数量
        """
        # 统计形成联盟的互动
        alliance_interactions = [
            i for i in interactions
            if "alliance" in i.get("interaction_type", "").lower()
            and i.get("outcome", {}).get("success", False)
        ]

        # 使用集合去重（通过参与方）
        unique_alliances = set()
        for interaction in alliance_interactions:
            initiator = interaction.get("initiator_id")
            target = interaction.get("target_id")
            if initiator and target:
                # 排序以确保同一对智能体只计数一次
                alliance_pair = tuple(sorted([initiator, target]))
                unique_alliances.add(alliance_pair)

        return len(unique_alliances)


class OrderTypeMetricsCalculator(MetricCalculator):
    """
    秩序类型指标计算器

    集成OrderEvaluator计算当前国际秩序类型

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, evaluator: Optional[OrderEvaluator] = None):
        """
        初始化计算器

        Args:
            evaluator: 秩序评估器，默认创建新实例
        """
        self.evaluator = evaluator or OrderEvaluator()

    def get_name(self) -> str:
        return "order_type_metrics"

    def get_category(self) -> str:
        return "dependent"  # 作为因变量指标

    def calculate(self, context: CalculationContext) -> List[Metric]:
        """
        计算秩序类型指标

        Args:
            context: 计算上下文

        Returns:
            指标列表
        """
        metrics = []

        try:
            # 构建评估上下文
            eval_context = self._build_evaluation_context(context)

            # 执行评估
            result = self.evaluator.evaluate(eval_context)

            # 添加秩序类型指标
            metrics.append(Metric(
                name="international_order_type",
                value=self._order_type_to_numeric(result.order_type),
                category=self.get_category(),
                round=context.round,
                metadata={
                    "order_type": result.order_type,
                    "confidence": result.confidence,
                    "reasoning": result.reasoning,
                    "indicators": result.indicators,
                    "description": "国际秩序类型"
                }
            ))

            # 添加置信度指标
            metrics.append(Metric(
                name="order_evaluation_confidence",
                value=result.confidence * 100.0,  # 转换为百分比
                category=self.get_category(),
                round=context.round,
                metadata={"unit": "%", "description": "秩序判定置信度"}
            ))

            logger.debug(
                f"秩序类型计算完成: 轮次={context.round}, "
                f"类型={result.order_type}, 置信度={result.confidence:.2f}"
            )

        except Exception as e:
            logger.error(f"秩序类型计算失败: {e}", exc_info=True)
            # 添加失败标记指标
            metrics.append(Metric(
                name="international_order_type",
                value=0.0,
                category=self.get_category(),
                round=context.round,
                metadata={
                    "order_type": "未判定",
                    "confidence": 0.0,
                    "error": str(e),
                    "description": "国际秩序类型（计算失败）"
                }
            ))

        return metrics

    def _build_evaluation_context(self, context: CalculationContext) -> OrderEvaluationContext:
        """
        从指标计算上下文构建秩序评估上下文

        Args:
            context: 指标计算上下文

        Returns:
            秩序评估上下文
        """
        # 从智能体数据计算实力
        agent_powers = [a.get("comprehensive_power", 0) for a in context.agents]

        # 计算实力集中度
        if agent_powers:
            total_power = sum(agent_powers)
            if total_power > 0:
                top3_power = sum(sorted(agent_powers, reverse=True)[:3])
                power_concentration = (top3_power / total_power) * 100
            else:
                power_concentration = 0.0
        else:
            power_concentration = 0.0

        # 从事件数据提取其他指标（需要先计算基础指标）
        norm_effectiveness = 0.0
        conflict_level = 0.0
        institutionalization = 0.0

        for event in context.events:
            if event.get("event_type") == "norm":
                # 规范有效性
                validity = event.get("validity", 0)
                adherence = event.get("adherence_rate", 0)
                norm_effectiveness = (norm_effectiveness + (validity * adherence) / 100.0) / 2.0

            elif event.get("event_type") == "conflict":
                # 冲突水平
                conflict_level += event.get("severity", 1)

            elif event.get("event_type") in ["institution", "treaty", "multilateral_organ"]:
                # 制度化程度
                validity = event.get("validity", 50)
                institutionalization = (institutionalization + validity) / 2.0

        # 统计联盟数量
        alliance_count = sum(
            1 for i in context.interactions
            if "alliance" in i.get("interaction_type", "").lower()
            and i.get("outcome", {}).get("success", False)
        )

        return OrderEvaluationContext(
            power_concentration_index=power_concentration,
            international_norm_effectiveness=norm_effectiveness,
            conflict_level=conflict_level,
            alliance_count=alliance_count,
            institutionalization_index=institutionalization
        )

    def _order_type_to_numeric(self, order_type: str) -> float:
        """
        将秩序类型转换为数值表示

        用于趋势分析

        Args:
            order_type: 秩序类型字符串

        Returns:
            数值表示
        """
        order_to_num = {
            "霸权秩序": 1.0,
            "均势秩序": 2.0,
            "规则/制度秩序": 3.0,
            "混合型秩序": 4.0,
            "无秩序型": 5.0,
            "未判定": 0.0
        }
        return order_to_num.get(order_type, 0.0)

    def get_latest_evaluation_result(self) -> Optional[OrderEvaluationResult]:
        """
        获取最新的评估结果

        Returns:
            最新的评估结果，如果没有则返回None
        """
        # 在实际实现中，可以缓存最近的评估结果
        # 这里暂时返回None
        return None
