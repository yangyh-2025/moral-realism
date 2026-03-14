"""
智能体模板配置模块 - 为不同类型智能体提供适配的Prompt模板

支持：
- 大国智能体决策模板
- 小国智能体生存策略模板
- 国际组织协调模板
- 区域大国领导模板

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, Any
from enum import Enum

class AgentTemplateType(str, Enum):
    """
    智能体模板类型

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    GREAT_POWER = "great_power"                # 大国模板
    SMALL_POWER = "small_power"                # 小国模板
    INTERNATIONAL_ORG = "international_org"   # 国际组织模板
    REGIONAL_POWER = "regional_power"          # 区域大国模板
    SUPERPOWER = "superpower"                # 超级大国模板
    MIDDLE_POWER = "middle_power"            # 中等强国模板

class AgentTemplateConfig:
    """
    智能体模板配置

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    # 超级大国模板配置
    SUPERPOWER_CONFIG = {
        "role_description": "作为超级大国，你对国际秩序负有特殊责任",
        "strategic_focus": "全球战略布局和秩序维护",
        "resource_priority": "优先保障全球影响力和领导地位",
        "decision_scope": "全球范围内的决策",
        "concerns": [
            "维护全球领导地位",
            "防范新兴对手崛起",
            "提供国际公共产品",
            "塑造符合自身利益的国际秩序"
        ],
        "capabilities": [
            "全球军事投送能力",
            "广泛的外交网络",
            "主导国际组织和机制",
            "影响全球金融体系"
        ],
        "constraints": [
            "需要承担高昂的全球责任",
            "面临多方面竞争和制衡",
            "行动成本高且影响面广",
            "需要维持盟友体系"
        ]
    }

    # 大国模板配置
    GREAT_POWER_CONFIG = {
        "role_description": "作为大国，你在区域和全球事务中发挥重要作用",
        "strategic_focus": "区域主导地位和全球影响力",
        "resource_priority": "平衡区域利益与国际影响",
        "decision_scope": "区域和全球层面的决策",
        "concerns": [
            "维护区域主导地位",
            "在全球事务中发声",
            "防范区域挑战者",
            "在超级大国间保持自主"
        ],
        "capabilities": [
            "区域军事影响力",
            "重要外交地位",
            "参与全球治理",
            "影响区域经济合作"
        ],
        "constraints": [
            "面临超级大国竞争",
            "需要平衡区域关系",
            "资源投入成本较高",
            "决策影响范围有限"
        ]
    }

    # 中等强国模板配置
    MIDDLE_POWER_CONFIG = {
        "role_description": "作为中等强国，你寻求在国际事务中发挥积极作用",
        "strategic_focus": "多边合作与平衡外交",
        "resource_priority": "发展与安全并重",
        "decision_scope": "国际事务中的积极参与",
        "concerns": [
            "在多边机制中发挥作用",
            "推动议题设置和议程",
            "在大国间保持平衡",
            "提升国际地位和影响力"
        ],
        "capabilities": [
            "特定领域的专业能力",
            "多边外交技巧",
            "议题联盟能力",
            "区域协调作用"
        ],
        "constraints": [
            "资源相对有限",
            "依赖多边合作",
            "在大国博弈中自主性受限",
            "影响力领域相对窄"
        ]
    }

    # 小国模板配置
    SMALL_POWER_CONFIG = {
        "role_description": "作为小国，你需要在大国之间寻求生存和发展空间",
        "strategic_focus": "生存安全与渐进发展",
        "resource_priority": "确保国家安全和基本利益",
        "decision_scope": "适度的外交参与",
        "concerns": [
            "维护国家主权和安全",
            "确保经济生存与发展",
            "在大国间保持平衡",
            "寻求盟友或保护伞"
        ],
        "capabilities": [
            "灵活的外交转向",
            "在特定领域提供价值",
            "多边联盟参与",
            "影响大国议程的能力"
        ],
        "constraints": [
            "资源严重受限",
            "在国际事务中被动",
            "高度依赖大国关系",
            "面临被边缘化风险"
        ]
    }

    # 区域大国模板配置
    REGIONAL_POWER_CONFIG = {
        "role_description": "作为区域大国，你在本地区具有重要影响力",
        "strategic_focus": "区域领导与稳定",
        "resource_priority": "保障区域安全和利益",
        "decision_scope": "区域层面的主导决策",
        "concerns": [
            "维护区域领导地位",
            "防范区域外部干预",
            "管理区域矛盾",
            "参与全球事务但不失区域重心"
        ],
        "capabilities": [
            "区域军事优势",
            "区域经济主导",
            "区域外交影响力",
            "区域事务塑造能力"
        ],
        "constraints": [
            "面临全球大国的竞争",
            "区域挑战者的制衡",
            "资源集中于区域",
            "全球影响力相对有限"
        ]
    }

    # 国际组织模板配置
    INTERNATIONAL_ORG_CONFIG = {
        "role_description": "作为国际组织，你代表多边利益和共同规范",
        "strategic_focus": "维护国际秩序与多边机制",
        "resource_priority": "促进合作与冲突调解",
        "decision_scope": "多边框架内的协调决策",
        "concerns": [
            "维护国际法和国际规范",
            "促进国际合作",
            "调解国际冲突",
            "提供全球公共产品"
        ],
        "capabilities": [
            "多边协调平台",
            "规范制定和推广",
            "冲突调解机制",
            "国际合作促进"
        ],
        "constraints": [
            "依赖成员国的支持",
            "决策需要共识",
            "执行能力有限",
            "面临主权制约"
        ]
    }

    @staticmethod
    def get_template_config(template_type: AgentTemplateType) -> Dict[str, Any]:
        """
        获取模板配置

        Args:
            template_type: 模板类型

        Returns:
            模板配置字典
        """
        configs = {
            AgentTemplateType.SUPERPOWER: AgentTemplateConfig.SUPERPOWER_CONFIG,
            AgentTemplateType.GREAT_POWER: AgentTemplateConfig.GREAT_POWER_CONFIG,
            AgentTemplateType.MIDDLE_POWER: AgentTemplateConfig.MIDDLE_POWER_CONFIG,
            AgentTemplateType.SMALL_POWER: AgentTemplateConfig.SMALL_POWER_CONFIG,
            AgentTemplateType.REGIONAL_POWER: AgentTemplateConfig.REGIONAL_POWER_CONFIG,
            AgentTemplateType.INTERNATIONAL_ORG: AgentTemplateConfig.INTERNATIONAL_ORG_CONFIG,
        }
        return configs.get(template_type, {})


class MultiLanguageTemplateManager:
    """
    多语言模板管理器

    支持中英文模板对照、术语标准化、文化适应调整

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    # 术语标准化映射（英文 -> 中文）
    TERM_STANDARDIZATION = {
        "hegemonic": "霸权秩序",
        "balance of power": "均势秩序",
        "rule based": "规则/制度秩序",
        "disorder": "无秩序",
        "mixed order": "混合秩序",
        "great power": "大国",
        "superpower": "超级大国",
        "middle power": "中等强国",
        "small power": "小国",
        "alliance": "联盟",
        "sanction": "制裁",
        "intervention": "干预",
        "cooperation": "合作",
        "mediation": "调解",
        "deterrence": "威慑",
        "containment": "遏制",
        "engagement": "接触"
    }

    # 术语标准化映射（中文 -> 英文）
    TERM_STANDARDIZATION_ZH_EN = {v: k for k, v in TERM_STANDARDIZATION.items()}

    @staticmethod
    def standardize_term(term: str, target_lang: str = "zh") -> str:
        """
        标准化术语

        Args:
            term: 原始术语
            target_lang: 目标语言（zh/en）

        Returns:
            标准化后的术语
        """
        if target_lang == "zh":
            return MultiLanguageTemplateManager.TERM_STANDARDIZATION.get(
                term.lower(), term
            )
        else:
            return MultiLanguageTemplateManager.TERM_STANDARDIZATION_ZH_EN.get(
                term, term
            )

    @staticmethod
    def get_template_variants(template_name: str) -> Dict[str, str]:
        """
        获取模板的多语言变体

        Args:
            template_name: 模板名称

        Returns:
            多语言变体字典
        """
        # 这里可以返回不同语言的模板版本
        # 实际实现中可以从文件加载
        return {
            "zh": f"[中文模板] {template_name}",
            "en": f"[English Template] {template_name}"
        }


class TemplateQualityMetrics:
    """
    模板质量评估指标

    用于A/B测试和持续优化

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        self._template_results: Dict[str, list] = {}

    def record_result(
        self,
        template_name: str,
        success: bool,
        quality_score: float,
        response_time: float,
        token_usage: int
    ) -> None:
        """
        记录模板使用结果

        Args:
            template_name: 模板名称
            success: 是否成功
            quality_score: 质量评分（0-1）
            response_time: 响应时间（秒）
            token_usage: Token使用量
        """
        if template_name not in self._template_results:
            self._template_results[template_name] = []

        self._template_results[template_name].append({
            "success": success,
            "quality_score": quality_score,
            "response_time": response_time,
            "token_usage": token_usage,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        })

    def get_template_metrics(self, template_name: str) -> Dict[str, Any]:
        """
        获取模板的评估指标

        Args:
            template_name: 模板名称

        Returns:
            评估指标字典
        """
        if template_name not in self._template_results:
            return {
                "template_name": template_name,
                "total_calls": 0,
                "success_rate": 0.0,
                "avg_quality_score": 0.0,
                "avg_response_time": 0.0,
                "avg_token_usage": 0.0
            }

        results = self._template_results[template_name]
        total_calls = len(results)
        success_count = sum(1 for r in results if r["success"])

        return {
            "template_name": template_name,
            "total_calls": total_calls,
            "success_rate": success_count / total_calls if total_calls > 0 else 0.0,
            "avg_quality_score": sum(r["quality_score"] for r in results) / total_calls if total_calls > 0 else 0.0,
            "avg_response_time": sum(r["response_time"] for r in results) / total_calls if total_calls > 0 else 0.0,
            "avg_token_usage": sum(r["token_usage"] for r in results) / total_calls if total_calls > 0 else 0.0
        }

    def compare_templates(self, template_a: str, template_b: str) -> Dict[str, Any]:
        """
        比较两个模板的效果

        Args:
            template_a: 模板A名称
            template_b: 模板B名称

        Returns:
            比较结果
        """
        metrics_a = self.get_template_metrics(template_a)
        metrics_b = self.get_template_metrics(template_b)

        # 计算综合得分（可调整权重）
        def calculate_score(metrics):
            return (
                metrics["success_rate"] * 0.3 +
                metrics["avg_quality_score"] * 0.5 +
                (1 - min(metrics["avg_response_time"] / 10, 1)) * 0.2
            )

        score_a = calculate_score(metrics_a)
        score_b = calculate_score(metrics_b)

        return {
            "template_a": metrics_a,
            "template_b": metrics_b,
            "winner": template_a if score_a > score_b else template_b,
            "score_difference": score_a - score_b,
            "recommendation": (
                f"推荐使用 {template_a}，综合得分更高" if score_a > score_b
                else f"推荐使用 {template_b}，综合得分更高"
            )
        }
