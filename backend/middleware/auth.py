"""
认证中间件

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from typing import Optional
import os

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# 配置的API密钥 - 从环境变量读取
VALID_API_KEYS = []
if os.getenv("VALID_API_KEYS"):
    VALID_API_KEYS = [key.strip() for key in os.getenv("VALID_API_KEYS").split(",") if key.strip()]


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """
    验证API密钥

    Args:
        api_key: API密钥

    Returns:
        验证后的密钥

    Raises:
        HTTPException: 密钥无效
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required"
        )

    if api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

    return api_key
