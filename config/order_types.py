"""
国际秩序类型配置模块 - 对应技术方案4.1.2节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from enum import Enum

class InternationalOrderType(str, Enum):
    """国际秩序类型枚举"""
    HEGEMONIC = "hegemonic"              # 霸权秩序
    BALANCE_OF_POWER = "balance_of_power" # 均势秩序
    RULE_BASED = "rule_based"            # 规则/制度秩序
    DISORDER = "disorder"                # 无秩序型
    MIXED = "mixed"                      # 混合型秩序

# 国际秩序类型中文映射
ORDER_TYPE_CN = {
    InternationalOrderType.HEGEMONIC: "霸权秩序",
    InternationalOrderType.BALANCE_OF_POWER: "均势秩序",
    InternationalOrderType.RULE_BASED: "规则/制度秩序",
    InternationalOrderType.DISORDER: "无秩序型",
    InternationalOrderType.MIXED: "混合型秩序"
}
