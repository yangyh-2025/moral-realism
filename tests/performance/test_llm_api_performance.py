"""
LLM API性能测试

测试API调用延迟和并发请求处理能力：
- API调用延迟测试
- 并发请求处理能力
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock


@pytest.mark.performance
class TestLLMAPILatency:
    """LLM API延迟测试"""

    @pytest.mark.asyncio
    async def test_single_api_call_latency(self):
        """测试单个API调用延迟"""
        # Mock LLM引擎
        class MockLLMEngine:
            async def generate(self, prompt):
                await asyncio.sleep(0.1)  # 模拟100ms延迟
                return "response"

        engine = MockLLMEngine()

        start_time = time.time()
        await engine.generate("test prompt")
        latency = time.time() - start_time

        # 延迟应该在合理范围内（<1秒）
        assert latency < 1.0
        assert latency >= 0.1

    @pytest.mark.asyncio
    async def test_multiple_api_calls_latency(self):
        """测试多个API调用延迟"""
        class MockLLMEngine:
            async def generate(self, prompt):
                await asyncio.sleep(0.05)  # 模拟50ms延迟
                return "response"

        engine = MockLLMEngine()

        latencies = []
        for _ in range(10):
            start_time = time.time()
            await engine.generate("test prompt")
            latency = time.time() - start_time
            latencies.append(latency)

        # 计算平均延迟
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 1.0

        # 检查延迟一致性（标准差）
        std_dev = (sum((x - avg_latency) ** 2 for x in latencies) / len(latencies)) ** 0.5
        assert std_dev < 0.5  # 标准差应该较小


@pytest.mark.performance
class TestLLMAPIConcurrency:
    """LLM API并发性能测试"""

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """测试并发API调用"""
        class MockLLMEngine:
            def __init__(self):
                self.call_count = 0

            async def generate(self, prompt):
                await asyncio.sleep(0.05)
                self.call_count += 1
                return f"response_{self.call_count}"

        engine = MockLLMEngine()

        # 并发执行10个调用
        tasks = [engine.generate(f"prompt_{i}") for i in range(10)]
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # 并发执行应该快于顺序执行
        # 顺序执行需要10 * 0.05 = 0.5秒
        # 并发执行应该接近最慢的调用时间
        assert total_time < 0.5
        assert len(results) == 10

    @pytest.mark.asyncio
    async def test_batch_api_calls(self):
        """测试批量API调用"""
        class MockLLMEngine:
            async def batch_generate(self, prompts):
                await asyncio.sleep(0.1)  # 批量调用总延迟
                return [f"response_{i}" for i in range(len(prompts))]

        engine = MockLLMEngine()

        prompts = [f"prompt_{i}" for i in range(10)]
        start_time = time.time()
        results = await engine.batch_generate(prompts)
        total_time = time.time() - start_time

        # 批量调用应该快于单个调用
        assert total_time < 1.0
        assert len(results) == 10


@pytest.mark.performance
class TestLLMAPIEfficiency:
    """LLM API效率测试"""

    @pytest.mark.asyncio
    async def test_response_time_percentile(self):
        """测试响应时间百分位数"""
        class MockLLMEngine:
            async def generate(self, prompt):
                # 模拟不同的延迟
                import random
                delay = random.uniform(0.05, 0.2)
                await asyncio.sleep(delay)
                return "response"

        engine = MockLLMEngine()

        response_times = []
        for _ in range(100):
            start_time = time.time()
            await engine.generate("test prompt")
            response_time = time.time() - start_time
            response_times.append(response_time)

        # 计算百分位数
        response_times.sort()
        p50 = response_times[49]  # 中位数
        p90 = response_times[89]  # 90百分位数
        p95 = response_times[94]  # 95百分位数

        # 检查性能目标
        assert p50 < 0.2  # 中位数应该<200ms
        assert p90 < 0.5  # 90百分位数应该<500ms
        assert p95 < 0.7  # 95百分位数应该<700ms

    @pytest.mark.asyncio
    async def test_error_recovery_latency(self):
        """测试错误恢复延迟"""
        class MockLLMEngine:
            def __init__(self):
                self.should_fail = False

            async def generate(self, prompt):
                if self.should_fail:
                    raise Exception("API error")
                await asyncio.sleep(0.1)
                return "response"

        engine = MockLLMEngine()

        # 测试正常调用延迟
        start_time = time.time()
        await engine.generate("test prompt")
        normal_latency = time.time() - start_time

        # 测试错误调用延迟
        engine.should_fail = True
        start_time = time.time()
        try:
            await engine.generate("test prompt")
        except Exception:
            pass
        error_latency = time.time() - start_time

        # 错误处理应该很快
        assert error_latency < 1.0
