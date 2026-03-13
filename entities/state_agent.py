"""
大国智能体 - 对应技术方案3.3.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, List, Optional
from entities.base_agent import BaseAgent
from config.validator import LeaderType


class StateAgent(BaseAgent):
    """
    大国智能体 - 对应技术方案3.3.2节

    适用范围：超级大国、大国
    必须配置：leader_type（王道型/霸权型/强权型/昏庸型）

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def _get_core_preferences(self, leader_type: Optional[LeaderType] = None) -> Dict[str, float]:
        """获取核心偏好 - 对应技术方案领导类型偏好表"""
        preferences = {
            LeaderType.WANGDAO: {
                "system_stability": 1.0,
                "national_long_term_interest": 0.9,
                "national_short_term_interest": 0.7,
                "personal_interest": 0.1
            },
            LeaderType.BAQUAN: {
                "national_core_interest": 1.0,
                "alliance_system_interest": 0.9,
                "system_stability": 0.7,
                "personal_interest": 0.2
            },
            LeaderType.QIANGQUAN: {
                "national_short_term_core_interest": 1.0,
                "national_long_term_interest": 0.6,
                "others_interest": 0.1
            },
            LeaderType.HUNYONG: {
                "personal_interest": 1.0,
                "faction_interest": 0.9,
                "national_nominal_interest": 0.5
            }
        }
        return preferences.get(leader_type, {})

    def _get_behavior_boundaries(self, leader_type: Optional[LeaderType] = None) -> List[str]:
        """获取行为边界"""
        boundaries = {
            LeaderType.WANGDAO: [
                "非暴力手段优先",
                "平等协商对话",
                "提供国际公共产品",
                "塑造公平国际规范"
            ],
            LeaderType.BAQUAN: [
                "选择性使用暴力/强制手段",
                "对盟友与对手执行双重标准",
                "主导国际制度",
                "有条件履行国际承诺"
            ],
            LeaderType.QIANGQUAN: [
                "暴力/强制手段优先",
                "无视国际承诺与规则",
                "通过实力压制实现目标",
                "拒绝多边协商与调停"
            ],
            LeaderType.HUNYONG: [
                "决策高度个人化",
                "言行严重不一致",
                "频繁毁约与外交转向",
                "可采取自我伤害行为"
            ]
        }
        return boundaries.get(leader_type, [])
