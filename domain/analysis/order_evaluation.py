"""
国际秩序评估核心模块 - 对应技术方案4.1.2节

提供国际秩序类型判定的核心逻辑

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OrderEvaluationThresholds(BaseModel):
    """
    秩序评估阈值配置

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    # 实力集中度阈值
    power_concentration_high: float = Field(default=60.0, description="高实力集中度阈值 (>60为高)")
    power_concentration_low: float = Field(default=30.0, description="低实力集中度阈值 (>30为中等)")

    # 规范有效性阈值（注意：使用严格大于而非大于等于）
    norm_effectiveness_high: float = Field(default=60.0, description="高规范有效性阈值 (>60为高)")
    norm_effectiveness_medium: float = Field(default=30.0, description="中等规范有效性阈值 (>30为中等)")
    norm_effectiveness_low: float = Field(default=30.0, description="低规范有效性阈值 (<30为低)")

    # 冲突水平阈值
    conflict_level_high: float = Field(default=60.0, description="高冲突水平阈值 (>60为高)")

    # 联盟数量阈值
    min_alliances_for_balance: int = Field(default=2, description="均势秩序最小联盟数 (>=2)")

    # 制度化程度阈值（注意：使用严格大于而非大于等于）
    institutionalization_high: float = Field(default=60.0, description="高制度化程度阈值 (>60为高)")

    # 置信度阈值
    min_confidence: float = Field(default=0.3, description="最小置信度阈值")


class OrderEvaluationResult(BaseModel):
    """
    秩序评估结果

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    order_type: str = Field(..., description="秩序类型")
    confidence: float = Field(..., ge=0.0, le=1.0, description="判定置信度")
    indicators: Dict[str, float] = Field(default_factory=dict, description="指标值")
    reasoning: str = Field(default="", description="判定理由")
    timestamp: str = Field(default_factory=lambda: __import__('datetime').datetime.now().isoformat())


@dataclass
class OrderEvaluationContext:
    """
    秩序评估上下文

    包含判定所需的所有指标数据

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    # 实力指标
    power_concentration_index: float = 0.0  # 实力集中度指数 (%)

    # 规范指标
    international_norm_effectiveness: float = 0.0  # 国际规范有效性指数 (分)

    # 冲突指标
    conflict_level: float = 0.0  # 冲突水平 (分)

    # 联盟指标
    alliance_count: int = 0  # 有效联盟数量

    # 制度指标
    institutionalization_index: float = 0.0  # 制度化程度指数 (%)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "power_concentration_index": self.power_concentration_index,
            "international_norm_effectiveness": self.international_norm_effectiveness,
            "conflict_level": self.conflict_level,
            "alliance_count": self.alliance_count,
            "institutionalization_index": self.institutionalization_index
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrderEvaluationContext':
        """从字典创建"""
        return cls(
            power_concentration_index=data.get("power_concentration_index", 0.0),
            international_norm_effectiveness=data.get("international_norm_effectiveness", 0.0),
            conflict_level=data.get("conflict_level", 0.0),
            alliance_count=data.get("alliance_count", 0),
            institutionalization_index=data.get("institutionalization_index", 0.0)
        )


class OrderEvaluator:
    """
    国际秩序评估器

    基于多项指标判定当前的国际秩序类型

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, thresholds: Optional[OrderEvaluationThresholds] = None):
        """
        初始化评估器

        Args:
            thresholds: 评估阈值配置，默认使用标准阈值
        """
        self.thresholds = thresholds or OrderEvaluationThresholds()

    def evaluate(self, context: OrderEvaluationContext) -> OrderEvaluationResult:
        """
        评估国际秩序类型

        Args:
            context: 评估上下文

        Returns:
            评估结果
        """
        try:
            # 确定秩序类型
            order_type = self._determine_order_type(context)

            # 计算置信度
            confidence = self._calculate_confidence(context, order_type)

            # 生成判定理由
            reasoning = self._generate_reasoning(context, order_type, confidence)

            # 构建结果
            result = OrderEvaluationResult(
                order_type=order_type,
                confidence=confidence,
                indicators=context.to_dict(),
                reasoning=reasoning
            )

            logger.debug(
                f"秩序评估完成: 类型={order_type}, 置信度={confidence:.2f}, "
                f"理由={reasoning}"
            )

            return result

        except Exception as e:
            logger.error(f"秩序评估失败: {e}", exc_info=True)
            # 返回默认的未判定状态
            return OrderEvaluationResult(
                order_type="未判定",
                confidence=0.0,
                indicators=context.to_dict(),
                reasoning=f"评估失败: {str(e)}"
            )

    def _determine_order_type(self, context: OrderEvaluationContext) -> str:
        """
        判定秩序类型

        判定规则（按优先级）：
        1. 无秩序型：冲突水平 > 60 且 规范有效性 < 30
        2. 霸权秩序：实力集中度 > 60 且 规范有效性 > 30
        3. 规则/制度秩序：规范有效性 > 60 且 制度化程度 > 60
        4. 均势秩序：30 < 实力集中度 < 60 且 联盟数量 >= 2 且 规范有效性 > 30
        5. 混合型秩序：具备至少2种秩序类型的部分特征
        6. 默认：无秩序型

        Args:
            context: 评估上下文

        Returns:
            秩序类型字符串
        """
        t = self.thresholds

        # 无秩序型判定：高冲突、低规范有效性
        if context.conflict_level > t.conflict_level_high and \
           context.international_norm_effectiveness < t.norm_effectiveness_low:
            return "无秩序型"

        # 霸权秩序判定：高实力集中度、中等规范有效性
        if context.power_concentration_index > t.power_concentration_high and \
           context.international_norm_effectiveness > t.norm_effectiveness_medium:
            return "霸权秩序"

        # 规则/制度秩序判定：高规范有效性、高制度化程度
        if context.international_norm_effectiveness > t.norm_effectiveness_high and \
           context.institutionalization_index > t.institutionalization_high:
            return "规则/制度秩序"

        # 均势秩序判定：中等实力集中度、一定联盟数量、中等规范有效性
        if (t.power_concentration_low < context.power_concentration_index < t.power_concentration_high and \
            context.alliance_count >= t.min_alliances_for_balance and \
            context.international_norm_effectiveness > t.norm_effectiveness_medium):
            return "均势秩序"

        # 混合型秩序判定：具备至少2种秩序类型的部分特征
        # 混合型：多种秩序特征并存，体系没有明确的单一秩序类型
        satisfied_features = self._count_mixed_order_features(context, t)

        if satisfied_features >= 2:  # 至少具备2种特征才判定为混合型
            return "混合型秩序"

        # 默认返回无秩序型
        return "无秩序型"

    def _count_mixed_order_features(
        self,
        context: OrderEvaluationContext,
        thresholds: OrderEvaluationThresholds
    ) -> int:
        """
        统计混合型秩序中具备的特征数量

        Args:
            context: 评估上下文
            thresholds: 阈值配置

        Returns:
            满足的特征数量 (0-4)
        """
        features = 0

        # 特征1：规则/制度秩序部分特征（高规范有效性或高制度化程度）
        # 单独高规范或高制度都表示存在规则性
        has_rule_feature = (
            context.international_norm_effectiveness > 40 or  # 规范有效性中等偏上
            context.institutionalization_index > 40          # 制度化程度中等偏上
        )

        # 特征2：霸权秩序部分特征（高实力集中度）
        has_hegemonic_feature = (
            context.power_concentration_index > 50  # 实力集中度中等偏上
        )

        # 特征3：均势秩序部分特征（存在联盟或中等实力分布）
        has_balance_feature = (
            context.alliance_count >= 1 or                     # 存在联盟
            (30 < context.power_concentration_index < 70)      # 实力相对分散
        )

        # 特征4：体系相对稳定（低冲突）
        has_stability_feature = (
            context.conflict_level < 50  # 冲突水平中等偏低
        )

        features = sum([
            has_rule_feature,
            has_hegemonic_feature,
            has_balance_feature,
            has_stability_feature
        ])

        return features

    def _calculate_confidence(self, context: OrderEvaluationContext, order_type: str) -> float:
        """
        计算判定置信度

        基于指标的"强度"计算置信度

        Args:
            context: 评估上下文
            order_type: 秩序类型

        Returns:
            置信度 (0.0 - 1.0)
        """
        # 基础置信度
        base_confidence = 0.5

        # 根据秩序类型计算置信度
        if order_type == "无秩序型":
            # 无秩序型：冲突水平越高，规范有效性越低，置信度越高
            conflict_strength = min(context.conflict_level / 100, 1.0)
            norm_weakness = 1.0 - min(context.international_norm_effectiveness / 100, 1.0)
            confidence = (conflict_strength + norm_weakness) / 2

        elif order_type == "规则/制度秩序":
            # 规则秩序：规范有效性和制度化程度越高，置信度越高
            norm_strength = min(context.international_norm_effectiveness / 100, 1.0)
            inst_strength = min(context.institutionalization_index / 100, 1.0)
            confidence = (norm_strength + inst_strength) / 2

        elif order_type == "霸权秩序":
            # 霸权秩序：实力集中度越高，置信度越高
            power_strength = min(context.power_concentration_index / 100, 1.0)
            confidence = power_strength

        elif order_type == "均势秩序":
            # 均势秩序：联盟数量和规范有效性影响置信度
            alliance_strength = min(context.alliance_count / 5, 1.0)  # 假设5个联盟为满值
            norm_strength = min(context.international_norm_effectiveness / 100, 1.0)
            confidence = (alliance_strength + norm_strength) / 2

        elif order_type == "混合型秩序":
            # 混合型：基于满足的特征数量计算置信度
            # 特征越多，混合型的判定越可靠
            mixed_features = self._count_mixed_order_features(context, self.thresholds)
            confidence = min(mixed_features / 4.0, 1.0)  # 最多4个特征

        else:
            # 默认
            confidence = base_confidence

        return max(0.0, min(1.0, confidence))

    def _generate_reasoning(
        self,
        context: OrderEvaluationContext,
        order_type: str,
        confidence: float
    ) -> str:
        """
        生成判定理由

        Args:
            context: 评估上下文
            order_type: 秩序类型
            confidence: 置信度

        Returns:
            理由字符串
        """
        parts = []

        # 添加指标描述
        parts.append(f"实力集中度: {context.power_concentration_index:.1f}%")
        parts.append(f"规范有效性: {context.international_norm_effectiveness:.1f}分")
        parts.append(f"冲突水平: {context.conflict_level:.1f}分")
        parts.append(f"联盟数量: {context.alliance_count}")
        parts.append(f"制度化程度: {context.institutionalization_index:.1f}%")

        # 添加判定逻辑
        if order_type == "无秩序型":
            parts.append("判定理由: 高冲突水平且规范有效性低，体系处于无序状态")

        elif order_type == "规则/制度秩序":
            parts.append("判定理由: 高规范有效性和制度化程度，符合规则秩序特征")

        elif order_type == "霸权秩序":
            parts.append("判定理由: 高实力集中度表明存在单一主导国，符合霸权秩序特征")

        elif order_type == "均势秩序":
            parts.append("判定理由: 中等实力集中度配合多边联盟，符合均势秩序特征")

        elif order_type == "混合型秩序":
            parts.append("判定理由: 多项秩序特征部分满足，呈现混合状态")

        else:
            parts.append("判定理由: 无法明确判定秩序类型")

        # 添加置信度
        parts.append(f"置信度: {confidence:.2f}")

        return "; ".join(parts)

    def update_thresholds(self, thresholds: OrderEvaluationThresholds):
        """
        更新评估阈值

        Args:
            thresholds: 新的阈值配置
        """
        self.thresholds = thresholds
        logger.info("秩序评估阈值已更新")
