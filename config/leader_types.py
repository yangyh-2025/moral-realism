# 领导类型配置
"""
定义系统中的领导类型，根据道义现实主义理论，国家领导人在国际关系中的行为模式
受到其类型和道义认知的影响。
"""
from enum import Enum
from typing import List, Optional


class LeaderType(Enum):
    """领导人类型枚举"""
    WANGDAO = "wangdao"      # 王道型 - 强调道德规范、责任感和可持续发展
    BAQUAN = "baquan"         # 霸权型 - 追求权力优势和主导地位
    QIANGQUAN = "qiangquan"   # 强权型 - 注重实力对比，强调现实利益
    HUNYONG = "hunyong"       # 混庸型 - 行为模式混合，难以预测

    @classmethod
    def get_description(cls, leader_type: 'LeaderType') -> str:
        """获取领导类型描述"""
        descriptions = {
            cls.WANGDAO: "王道型领导人强调道德规范、责任感和可持续发展，",
            cls.BAQUAN: "霸权型领导人追求权力优势和主导地位，",
            cls.QIANGQUAN: "强权型领导人注重实力对比，强调现实利益，",
            cls.HUNYONG: "混庸型领导人行为模式混合，难以预测，"
        }
        return descriptions.get(leader_type, "未知类型")

    @classmethod
    def get_behavioral_tendencies(cls, leader_type: 'LeaderType') -> dict:
        """获取领导类型的行为倾向特征"""
        tendencies = {
            cls.WANGDAO: {
                "cooperation_preference": 0.8,      # 合作偏好
                "norm_respect": 0.9,                # 规范尊重
                "long_term_orientation": 0.85,       # 长期导向
                "power_seeking": 0.3,                # 权力追求
                "moral_concern": 0.9                 # 道德关注
            },
            cls.BAQUAN: {
                "cooperation_preference": 0.3,
                "norm_respect": 0.4,
                "long_term_orientation": 0.5,
                "power_seeking": 0.9,
                "moral_concern": 0.2
            },
            cls.QIANGQUAN: {
                "cooperation_preference": 0.4,
                "norm_respect": 0.5,
                "long_term_orientation": 0.6,
                "power_seeking": 0.8,
                "moral_concern": 0.4
            },
            cls.HUNYONG: {
                "cooperation_preference": 0.5,
                "norm_respect": 0.5,
                "long_term_orientation": 0.5,
                "power_seeking": 0.5,
                "moral_concern": 0.5
            }
        }
        return tendencies.get(leader_type, {})
