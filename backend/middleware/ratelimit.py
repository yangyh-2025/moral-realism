"""
速率限制中间件

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import Request, HTTPException, status
from collections import defaultdict
import time
import asyncio
from typing import Dict
from config.settings import Constants

class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int = None, window_seconds: int = None):
        self.max_requests = max_requests or Constants.RATE_LIMIT_MAX_REQUESTS
        self.window_seconds = window_seconds or Constants.RATE_LIMIT_WINDOW
        self.requests: Dict[str, list] = defaultdict(list)
        self._last_cleanup = time.time()
        self._cleanup_interval = Constants.RATE_LIMIT_CLEANUP_INTERVAL
        self._cleanup_task = None

    def _cleanup_expired_clients(self) -> None:
        """定期清理过期客户端"""
        now = time.time()
        expired_clients = []

        for client_id, requests in list(self.requests.items()):
            # 移除过期的请求
            self.requests[client_id] = [r for r in requests if now - r < self.window_seconds]

            # 如果没有有效请求，标记为过期
            if not self.requests[client_id]:
                expired_clients.append(client_id)

        # 删除过期客户端
        for client_id in expired_clients:
            if client_id in self.requests:
                del self.requests[client_id]

        self._last_cleanup = now

    def is_allowed(self, client_id: str) -> bool:
        """
        检查是否允许请求

        Args:
            client_id: 客户端ID

        Returns:
            是否允许
        """
        now = time.time()

        # 定期清理（每小时）
        if now - self._last_cleanup > self._cleanup_interval:
            self._cleanup_expired_clients()
            self._cleanup_expired_clients()

        requests = self.requests[client_id]

        # 移除过期的请求
        self.requests[client_id] = [
            r for r in requests
            if now - r < self.window_seconds
        ]

        # 清理长时间未访问的客户端
        if len(self.requests[client_id]) == 0:
            del self.requests[client_id]
            return True

        # 检查请求次数
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        self.requests[client_id].append(now)
        return True

    async def start_cleanup_task(self) -> None:
        """启动后台清理任务"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self) -> None:
        """后台清理循环"""
        try:
            while True:
                await asyncio.sleep(self._cleanup_interval)
                self._cleanup_expired_clients()
        except asyncio.CancelledError:
            pass

    async def stop_cleanup_task(self) -> None:
        """停止后台清理任务"""
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    def clear_all(self) -> None:
        """清空所有请求记录"""
        self.requests.clear()


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
