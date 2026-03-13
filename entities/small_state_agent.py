"""
小国智能体 - 对应技术方案3.3.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List
from entities.base_agent import BaseAgent


class SmallStateAgent(BaseAgent):
    """
    小国智能体 - 对应技术方案3.3.2节

    适用范围：小国
    特点：不需要配置leader_type，决策逻辑由战略立场和核心生存利益驱动

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def _get_core_preferences(self, leader_type=None) -> Dict[str, float]:
        """小国核心偏好"""
        return {
            "sovereignty_security": 1.0,
            "economic_development": 0.9,
            "avoid_conflict_spillover": 0.8,
            "favorable_external_environment": 0.7
        }

    def _get_behavior_boundaries(self, leader_type=None) -> List[str]:
        """小国行为边界"""
        return [
            "以大国行为带来的收益/风险为核心决策依据",
            "优先选择能保障自身核心利益的策略",
            "通过选边、结盟、投票影响大国软实力"
        ]
