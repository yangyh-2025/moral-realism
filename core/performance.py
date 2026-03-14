"""
性能优化工具

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import asyncio
import time
from typing import Optional, Dict, Any, List, Callable, TypeVar, Generic
from functools import wraps
from contextlib import asynccontextmanager
from collections import OrderedDict
from datetime import datetime, timedelta
import hashlib
import json

T = TypeVar('T')


class LRUAsyncCache(Generic[T]):
    """
    异步LRU缓存

    线程安全的LRU缓存实现，用于缓存计算结果
    """

    def __init__(self, maxsize: int = 128, ttl: Optional[int] = None):
        """
        Args:
            maxsize: 最大缓存大小
            ttl: 缓存存活时间（秒），None表示不过期
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[T]:
        """获取缓存值"""
        async with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # 检查是否过期
            if self.ttl is not None:
                if time.time() - entry['timestamp'] > self.ttl:
                    del self._cache[key]
                    return None

            # 移到末尾（最近使用）
            self._cache.move_to_end(key)
            return entry['value']

    async def set(self, key: str, value: T) -> None:
        """设置缓存值"""
        async with self._lock:
            # 如果已存在，删除旧值
            if key in self._cache:
                del self._cache[key]

            # 如果已满，删除最久未使用的
            elif len(self._cache) >= self.maxsize:
                self._cache.popitem(last=False)

            # 添加新值
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }

    async def delete(self, key: str) -> None:
        """删除缓存值"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            self._cache.clear()

    async def size(self) -> int:
        """获取缓存大小"""
        async with self._lock:
            return len(self._cache)


class MultiLevelCache(Generic[T]):
    """
    多级缓存

    实现内存缓存 + 可选的持久化缓存（如Redis）
    """

    def __init__(self, maxsize: int = 128, ttl: Optional[int] = None):
        self.memory_cache = LRUAsyncCache(maxsize=maxsize, ttl=ttl)
        self.ttl = ttl

    async def get(self, key: str) -> Optional[T]:
        """从缓存获取值（先查内存，再查持久化）"""
        # 先查内存缓存
        value = await self.memory_cache.get(key)
        if value is not None:
            return value

        # 可以在这里添加持久化缓存查询（如Redis）
        # value = await self._get_from_persistent_cache(key)
        # if value is not None:
        #     await self.memory_cache.set(key, value)
        #     return value

        return None

    async def set(self, key: str, value: T) -> None:
        """设置缓存值（写入内存和持久化）"""
        await self.memory_cache.set(key, value)

        # 可以在这里添加持久化缓存写入
        # await self._set_to_persistent_cache(key, value)

    async def delete(self, key: str) -> None:
        """删除缓存值"""
        await self.memory_cache.delete(key)

    async def clear(self) -> None:
        """清空所有缓存"""
        await self.memory_cache.clear()


# 全局缓存实例
_llm_response_cache = MultiLevelCache(maxsize=256, ttl=3600)  # LLM响应缓存（1小时）
_query_result_cache = MultiLevelCache(maxsize=512, ttl=300)  # 查询结果缓存（5分钟）


async def cached_llm_call(cache_key: str, cache_ttl: Optional[int] = None) -> Callable:
    """
    LLM调用缓存装饰器

    Args:
        cache_key: 缓存键生成函数或字符串
        cache_ttl: 缓存存活时间（秒）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            if callable(cache_key):
                key = str(cache_key(*args, **kwargs))
            else:
                key = cache_key

            # 尝试从缓存获取
            cached_result = await _llm_response_cache.get(key)
            if cached_result is not None:
                return cached_result

            # 执行原函数
            result = await func(*args, **kwargs)

            # 缓存结果
            await _llm_response_cache.set(key, result)

            return result
        return wrapper
    return decorator


def async_lru_cache(maxsize: int = 128):
    """
    异步LRU缓存装饰器

    Args:
        maxsize: 最大缓存大小
    """
    cache = LRUAsyncCache(maxsize=maxsize)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 生成缓存键
            key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            key_hash = hashlib.md5(key.encode()).hexdigest()

            # 尝试从缓存获取
            cached_result = await cache.get(key_hash)
            if cached_result is not None:
                return cached_result

            # 执行原函数
            result = await func(*args, **kwargs)

            # 缓存结果
            await cache.set(key_hash, result)

            return result
        return wrapper
    return decorator


class AsyncLockPool:
    """
    异步锁池

    用于管理多个资源的并发访问
    """

    def __init__(self, max_workers: int = 10):
        """
        Args:
            max_workers: 最大并发数
        """
        self.semaphore = asyncio.Semaphore(max_workers)
        self.active_tasks: Dict[str, asyncio.Task] = {}

    async def run_task(self, task_id: str, coro) -> Any:
        """
        运行任务（受信号量限制）

        Args:
            task_id: 任务ID
            coro: 协程对象

        Returns:
            任务执行结果
        """
        async with self.semaphore:
            task = asyncio.create_task(coro)
            self.active_tasks[task_id] = task

            try:
                result = await task
                return result
            finally:
                del self.active_tasks[task_id]

    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            return True
        return False

    def get_active_count(self) -> int:
        """获取活跃任务数"""
        return len(self.active_tasks)


async def parallel_execute(tasks: List[Callable], max_concurrency: int = 5) -> List[Any]:
    """
    并行执行多个任务

    Args:
        tasks: 任务列表（协程或可调用对象）
        max_concurrency: 最大并发数

    Returns:
        任务结果列表
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_with_one_at_a_time(task):
        async with semaphore:
            if asyncio.iscoroutine(task):
                return await task
            elif callable(task):
                result = task()
                if asyncio.iscoroutine(result):
                    return await result
                return result

    tasks = [run_with_one_at_a_time(task) for task in tasks]
    return await asyncio.gather(*tasks, return_exceptions=True)


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    异步重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 退避因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise e from last_exception
        return wrapper
    return decorator


class PerformanceMonitor:
    """
    性能监控器

    用于监控函数执行时间和调用次数
    """

    def __init__(self):
        self._metrics: Dict[str, Dict[str, Any]] = {}

    def track(self, name: str):
        """装饰器：跟踪函数性能"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    self._record_success(name, time.time() - start_time)
                    return result
                except Exception as e:
                    self._record_failure(name, time.time() - start_time)
                    raise e

            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self._record_success(name, time.time() - start_time)
                    return result
                except Exception as e:
                    self._record_failure(name, time.time() - start_time)
                    raise e

            # 检测函数是否是协程
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

    def _record_success(self, name: str, duration: float) -> None:
        """记录成功调用"""
        if name not in self._metrics:
            self._metrics[name] = {
                'calls': 0,
                'successes': 0,
                'failures': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }

        self._metrics[name]['calls'] += 1
        self._metrics[name]['successes'] += 1
        self._metrics[name]['total_time'] += duration
        self._metrics[name]['min_time'] = min(self._metrics[name]['min_time'], duration)
        self._metrics[name]['max_time'] = max(self._metrics[name]['max_time'], duration)

    def _record_failure(self, name: str, duration: float) -> None:
        """记录失败调用"""
        if name not in self._metrics:
            self._metrics[name] = {
                'calls': 0,
                'successes': 0,
                'failures': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }

        self._metrics[name]['calls'] += 1
        self._metrics[name]['failures'] += 1

    def get_metrics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """获取性能指标"""
        if name:
            return self._metrics.get(name, {})

        result = {}
        for func_name, metrics in self._metrics.items():
            if metrics['calls'] > 0:
                result[func_name] = {
                    **metrics,
                    'avg_time': metrics['total_time'] / metrics['calls'],
                    'success_rate': metrics['successes'] / metrics['calls'] if metrics['calls'] > 0 else 0
                }
        return result

    def reset(self) -> None:
        """重置所有指标"""
        self._metrics.clear()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


class ObjectPool(Generic[T]):
    """
    对象池

    用于重用昂贵对象，减少内存分配
    """

    def __init__(self, factory: Callable[[], T], maxsize: int = 10):
        """
        Args:
            factory: 对象创建函数
            maxsize: 最大对象数
        """
        self._factory = factory
        self._maxsize = maxsize
        self._pool: List[T] = []
        self._in_use: set = set()

    def acquire(self) -> T:
        """获取对象"""
        if self._pool:
            obj = self._pool.pop()
            self._in_use.add(id(obj))
            return obj
        return self._factory()

    def release(self, obj: T) -> None:
        """释放对象"""
        obj_id = id(obj)
        if obj_id in self._in_use:
            self._in_use.remove(obj_id)

            if len(self._pool) < self._maxsize:
                self._pool.append(obj)

    @asynccontextmanager
    async def acquire_async(self):
        """异步获取对象（上下文管理器）"""
        obj = self.acquire()
        try:
            yield obj
        finally:
            self.release(obj)


def paginate(data: List[T], page: int, page_size: int) -> Dict[str, Any]:
    """
    分页函数

    Args:
        data: 数据列表
        page: 页码（从1开始）
        page_size: 每页大小

    Returns:
        分页结果
    """
    total = len(data)
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 1

    # 边界检查
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return {
        'data': data[start_idx:end_idx],
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


async def batch_process(items: List[Any], batch_size: int, process_fn: Callable) -> List[Any]:
    """
    批量处理

    Args:
        items: 项目列表
        batch_size: 批次大小
        process_fn: 处理函数

    Returns:
        处理结果列表
    """
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await parallel_execute([process_fn(item) for item in batch])
        results.extend(batch_results)

    return results
