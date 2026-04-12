"""
全局 LLM 并发控制模块

所有仿真项目共享一个全局 asyncio.Semaphore，
确保同时进行的 LLM API 调用总数不超过上限（默认 500）。
"""

import asyncio
from typing import Optional
from loguru import logger


class GlobalLLMConcurrency:
    """全局 LLM 并发信号量，跨项目共享"""

    def __init__(self, max_concurrent: int = 500):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max_concurrent = max_concurrent

    @property
    def total(self) -> int:
        return self._max_concurrent

    @property
    def used(self) -> int:
        """当前已占用的槽位数"""
        # Semaphore._value 是剩余槽位；locked 返回已占用近似值
        return max(0, self._max_concurrent - self._semaphore._value)

    async def acquire(self):
        await self._semaphore.acquire()

    def release(self):
        self._semaphore.release()

    def set_max(self, new_max: int):
        """动态调整上限（注意：仅对新 acquire 生效，已持有的不移除）"""
        if new_max < 1:
            raise ValueError("最大并发数必须 >= 1")
        old_max = self._max_concurrent
        delta = new_max - old_max
        if delta > 0:
            # 增大上限：释放额外槽位
            self._semaphore._value += delta
        elif delta < 0:
            # 减小上限：减少可用槽位（不阻塞已持有者）
            self._semaphore._value = max(1, self._semaphore._value + delta)
        self._max_concurrent = new_max
        logger.info(f"全局 LLM 并发上限调整为: {new_max}")


# 全局单例
_instance: Optional[GlobalLLMConcurrency] = None


def get_global_llm_concurrency() -> GlobalLLMConcurrency:
    """获取全局 LLM 并发控制单例"""
    global _instance
    if _instance is None:
        _instance = GlobalLLMConcurrency()
    return _instance


async def init_global_llm_concurrency(max_concurrent: int = 500):
    """初始化全局 LLM 并发控制（启动时调用，可传入配置值）"""
    global _instance
    _instance = GlobalLLMConcurrency(max_concurrent=max_concurrent)
    logger.info(f"全局 LLM 并发控制已初始化: max={max_concurrent}")
    return _instance
