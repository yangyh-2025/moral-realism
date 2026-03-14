"""
速率限制中间件

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import Request, HTTPException, status
from collections import defaultdict
import time
from typing import Dict

class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """
        检查是否允许请求

        Args:
            client_id: 客户端ID

        Returns:
            是否允许
        """
        now = time.time()
        requests = self.requests[client_id]

        # 移除过期的请求
        self.requests[client_id] = [
            r for r in requests
            if now - r < self.window_seconds
        ]

        # 检查请求次数
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        self.requests[client_id].append(now)
        return True


# 全局限速器实例
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


async def check_rate_limit(request: Request):
    """
    检查速率限制

    Args:
        request: 请求对象

    Raises:
        HTTPException: 超出速率限制
    """
    client_id = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
