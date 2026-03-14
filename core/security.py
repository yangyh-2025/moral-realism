"""
安全工具函数

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import re
import html
from typing import Any, Dict


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    输入清理

    Args:
        input_str: 输入字符串
        max_length: 最大长度

    Returns:
        清理后的字符串
    """
    if not input_str:
        return ""

    # 限制长度
    input_str = input_str[:max_length]

    # 移除危险字符
    input_str = re.sub(r'[<>"\';]', '', input_str)

    return input_str.strip()


def escape_html(input_str: str) -> str:
    """
    HTML转义（防止XSS）

    Args:
        input_str: 输入字符串

    Returns:
        转义后的字符串
    """
    return html.escape(input_str)


def validate_sql(query: str) -> bool:
    """
    验证SQL查询（防止SQL注入）

    Args:
        query: SQL查询

    Returns:
        是否安全
    """
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'EXEC']
    query_upper = query.upper()

    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False

    return True


def generate_csrf_token() -> str:
    """
    生成CSRF令牌

    Returns:
        CSRF令牌
    """
    import secrets
    return secrets.token_urlsafe(32)
