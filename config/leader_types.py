"""
领导类型配置模块

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from enum import Enum

class LeaderType(str, Enum):
    """
    领导类型枚举 - 对应技术方案核心设计

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """
    WANGDAO = "wangdao"      # 王道型
    BAQUAN = "baquan"        # 霸权型
    QIANGQUAN = "qiangquan"  # 强权型
    HUNYONG = "hunyong"      # 昏庸型

# 领导类型中文映射
LEADER_TYPE_CN = {
    LeaderType.WANGDAO: "王道型",
    LeaderType.BAQUAN: "霸权型",
    LeaderType.QIANGQUAN: "强权型",
    LeaderType.HUNYONG: "昏庸型"
}

# 领导类型描述
LEADER_TYPE_DESCRIPTION = {
    LeaderType.WANGDAO: "坚持道义，言行一致，优先保障体系公共利益",
    LeaderType.BAQUAN: "选择性运用道义，坚持双重标准，以本国利益为核心",
    LeaderType.QIANGQUAN: "无视道义与国际规范，零和博弈思维，利益最大化",
    LeaderType.HUNYONG: "无固定策略，决策高度个人化、反复无常"
}
