"""
领导类型映射工具 - 处理中英文领导类型转换

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Optional
from config.leader_types import LeaderType


# 中文名称 -> LeaderType 枚举映射
CN_TO_LEADER_TYPE = {
    '王道型': LeaderType.WANGDAO,
    '霸权型': LeaderType.BAQUAN,
    '强权型': LeaderType.QIANGQUAN,
    '昏庸型': LeaderType.HUNYONG
}

# LeaderType 枚举 -> 中文名称映射
LEADER_TYPE_TO_CN = {
    LeaderType.WANGDAO: '王道型',
    LeaderType.BAQUAN: '霸权型',
    LeaderType.QIANGQUAN: '强权型',
    LeaderType.HUNYONG: '昏庸型'
}


def parse_leader_type(leader_type_str: Optional[str]) -> Optional[LeaderType]:
    """
    解析领导类型字符串，支持中英文

    Args:
        leader_type_str: 领导类型字符串（中文或英文）

    Returns:
        LeaderType 枚举值，解析失败返回 None
    """
    if not leader_type_str:
        return None

    try:
        # 尝试直接解析（可能是枚举值）
        return LeaderType(leader_type_str)
    except ValueError:
        # 尝试通过中文名称映射
        return CN_TO_LEADER_TYPE.get(leader_type_str)


def get_leader_type_display(leader_type: Optional[LeaderType]) -> str:
    """
    获取领导类型的显示名称（中文）

    Args:
        leader_type: LeaderType 枚举值

    Returns:
        中文名称字符串
    """
    if leader_type is None:
        return '-'
    return LEADER_TYPE_TO_CN.get(leader_type, leader_type.value)
