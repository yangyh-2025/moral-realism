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

    注意：此函数仅提供基础保护，强烈建议使用参数化查询来防止SQL注入。
    对于关键操作，应使用ORM或参数化查询而非字符串拼接。

    Args:
        query: SQL查询

    Returns:
        是否安全
    """
    if not query or not isinstance(query, str):
        return False

    query_upper = query.upper()

    # 检测注释绕过的注入
    if '--' in query or '/*' in query or '*/' in query:
        return False

    # 检测危险操作（使用正则确保匹配完整单词，避免误报）
    dangerous_keywords = [
        r'\bDROP\b',
        r'\bDELETE\b(?!.*\bFROM\b.*\bWHERE\b)',  # 允许有WHERE的DELETE
        r'\bTRUNCATE\b',
        r'\bALTER\b',
        r'\bEXEC\b',
        r'\bEXECUTE\b',
        r'\bINSERT\s+INTO\b',
        r'\bUPDATE\b(?!.*\bSET\b.*\bWHERE\b)'  # 允许有WHERE的UPDATE
    ]

    for pattern in dangerous_keywords:
        if re.search(pattern, query_upper):
            return False

    # 检测UNION注入
    if re.search(r'\bUNION\b.*\bSELECT\b', query_upper):
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
