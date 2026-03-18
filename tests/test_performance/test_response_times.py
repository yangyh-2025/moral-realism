"""
Performance tests for response times

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""

import pytest
import time
import statistics
from typing import List, Dict
from unittest.mock import Mock, AsyncMock

try:
    from infrastructure.llm.llm_engine import LLMEngine, LLMProvider
    from infrastructure.prompts.prompt_engine import PromptTemplateEngine, PromptTemplate
    from domain.agents.base_agent import DecisionCache
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not ENTITIES_AVAILABLE,
    reason="Entities module not available"
)


@pytest.mark.performance
class TestLLMEngineResponseTime:
    """Test LLM engine response times"""

    @pytest.fixture
    def mock_provider(self):
        """Create mock provider with configurable latency"""
        provider = Mock()

        async def timed_call(*args, **kwargs):
            # Simulate variable latency (50-300ms)
            latency = 0.05 + (hash(str(args)) % 25) / 100.0
            await asyncio.sleep(latency)
            return {
                "choices": [{
                    "message": {
                        "function_call": {
                            "name": "test_action",
                            "arguments": '{"param": "value"}'
                        }
                    }
                }]
            }

        provider.generate = timed_call
        return provider

    @pytest.fixture
    def llm_engine(self, mock_provider):
        """Create LLM engine"""
        return LLMEngine(provider=mock_provider)

    @pytest.mark.asyncio
    async def test_single_decision_response_time(self, llm_engine):
        """Test single decision response time"""
        start_time = time.time()

        decision = await llm_engine.make_decision(
            agent_id="test_agent",
            prompt="Test prompt",
            available_functions=[{"name": "action1"}, {"name": "action2"}],
            prohibited_functions=[]
        )

        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to ms

        # Response time should be reasonable (< 1 second)
        assert response_time < 1000
        assert decision["function"] == "test_action"

    @pytest.mark.asyncio
    async def test_multiple_decisions_average_time(self, llm_engine):
        """Test average decision time for multiple requests"""
        num_decisions = 10
        response_times = []

        for _ in range(num_decisions):
            start_time = time.time()

            await llm_engine.make_decision(
                agent_id="test_agent",
                prompt="Test prompt",
                available_functions=[{"name": "action"}],
                prohibited_functions=[]
            )

            end_time = time.time()
            response_times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        # Average should be reasonable
        assert avg_time < 500  # < 500ms average
        # All requests should complete
        assert len(response_times) == num_decisions
        # Variation should be within expected range
        assert max_time - min_time < 500  # < 500ms spread

    @pytest.mark.asyncio
    async def test_decision_time_statistics(self, llm_engine):
        """Test decision time statistics"""
        num_samples = 50
        times = []

        for _ in range(num_samples):
            start_time = time.time()

            await llm_engine.make_decision(
                agent_id="test_agent",
                prompt="Test prompt",
                available_functions=[{"name": "action"}],
                prohibited_functions=[]
            )

            end_time = time.time()
            times.append(end_time - start_time)

        stats = {
            "mean": statistics.mean(times) * 1000,
            "median": statistics.median(times) * 1000,
            "stdev": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
            "min": min(times) * 1000,
            "max": max(times) * 1000,
            "p95": max(times) * 1000 if len(times) > 1 else 0,
            "p99": max(times) * 1000 if len(times) > 1 else 0,
        }

        # 95th percentile should be fast (< 600ms)
        assert stats["p95"] < 600
        # Mean should be reasonable (< 400ms)
        assert stats["mean"] < 400

    @pytest.mark.asyncio
    async def test_response_time_with_complexity(self, llm_engine):
        """Test response time with varying complexity"""
        complexities = [
            (1, [{"name": "action"}]),  # Simple
            (5, [{"name": f"action_{i}"} for i in range(5)]),  # Medium
            (10, [{"name": f"action_{i}"} for i in range(10)]),  # Complex
        (15, [{"name": f"action_{i}"} for i in range(15)]),  # Very complex
        ]

        for num_functions, functions in complexities:
            start_time = time.time()

            await llm_engine.make_decision(
                agent_id="test_agent",
                prompt="Test prompt",
                available_functions=functions,
                prohibited_functions=[]
            )

            end_time = time.time()
            response_time = (end_time - start_time) * 1000

            # Response time should increase gradually with complexity
            assert response_time < 2000  # Even complex should be under 2 seconds

    @pytest.mark.asyncio
    async def test_response_time_with_cache_hit(self):
        """Test response time with cache hit"""
        # Create provider that simulates cached responses
        cached_provider = Mock()
        cached_provider.generate = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "function_call": {
                        "name": "cached_action",
                        "arguments": '{"param": "value"}'
                    }
                }
            }]
        })

        # Create engine with cache
        llm_engine = LLMEngine(provider=cached_provider)
        llm_engine._cache["test_context"] = {
            "function": "cached_action",
            "arguments": {"param": "value"}
        }

        start_time = time.time()

        # In real scenario, cache lookup would be checked first
        # This test simulates the cache hit path
        cached_decision = llm_engine._cache.get("test_context")

        end_time = time.time()
        lookup_time = (end_time - start_time) * 1000

        # Cache lookup should be very fast
        assert lookup_time < 10  # < 10ms
        assert cached_decision is not None


@pytest.mark.performance
class TestPromptEngineResponseTime:
    """Test prompt engine response times"""

    @pytest.fixture
    def prompt_engine(self):
        """Create prompt template engine"""
        return PromptTemplateEngine(
            template_dir="config/prompts/",
            enable_cache=True
        )

    def test_load_template_response_time(self, prompt_engine):
        """Test template loading response time"""
        templates = [
            PromptTemplate.LEADER_DECISION,
            PromptTemplate.STATE_FOLLOWUP,
            PromptTemplate.ALLIANCE_INVITATION,
            PromptTemplate.FINAL_JUDGMENT
        ]

        times = []
        for template in templates:
            start_time = time.time()
            prompt_engine.load_template(template)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(times)

        # Template loading should be very fast
        assert avg_time < 50  # < 50ms average

    def test_load_template_with_cache_response_time(self, prompt_engine):
        """Test template loading with cache response time"""
        template = PromptTemplate.LEADER_DECISION

        # First load (cold cache)
        start_time = time.time()
        prompt_engine.load_template(template)
        cold_time = (time.time() - start_time) * 1000

        # Second load (warm cache)
        start_time = time.time()
        prompt_engine.load_template(template)
        warm_time = (time.time() - start_time) * 1000

        # Warm cache should be faster
        assert warm_time < cold_time
        # Both should be very fast
        assert cold_time < 100
        assert warm_time < 10

    def test_render_template_response_time(self, prompt_engine):
        """Test template rendering response time"""
        context = {
            "agent_name": "Test Country",
            "leader_type": "wangdao",
            "current_situation": "Peaceful and stable",
            "available_actions": ["action1", "action2", "action3", "action4", "action5"],
            "constraints": ["No use of force", "Respect sovereignty"],
            "objective_interests": ["Stability", "Prosperity"],
            "alliances": ["ally1"],
            "enemies": ["enemy1", "enemy2"]
        }

        times = []
        for _ in range(100):
            start_time = time.time()
            prompt_engine.render_template(
                PromptTemplate.LEADER_DECISION,
                context
            )
            end_time = time.time()
            times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(times)
        max_time = max(times)

        # Rendering should be fast
        assert avg_time < 20  # < 20ms average
        assert max_time < 100  # < 100ms worst case

    def test_token_calculation_response_time(self, prompt_engine):
        """Test token calculation response time"""
        texts = [
            "Short text",
            "Medium length text with some additional content here",
            "Longer text with much more content to test token calculation performance " * 10,
            "Chinese text for testing 令牌计算性能" * 5,
            "Mixed English and Chinese text for testing mixed language token calculation " * 8
        ]

        times = []
        for text in texts:
            start_time = time.time()
            PromptTemplateEngine.calculate_token_count(text)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(times)

        # Token calculation should be fast
        assert avg_time < 5  # < 5ms average


@pytest.mark.performance
class TestDecisionCacheResponseTime:
    """Test decision cache response times"""

    @pytest.fixture
    def cache(self):
        """Create decision cache"""
        return DecisionCache(max_size=1000, ttl=3600)

    def test_cache_lookup_response_time(self, cache):
        """Test cache lookup response time"""
        # Pre-populate cache
        for i in range(100):
            context = {"agent_id": f"agent_{i}", "round": i % 10}
            decision = {"action": f"action_{i}"}
            cache.cache_decision(context, decision, f"agent_{i % 10}")

        # Time lookups
        times = []
        for i in range(1000):
            context = {"agent_id": f"agent_{i % 10}", "round": (i // 100) % 10}
            start_time = time.time()
            cache.get_cached_decision(context)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(times)
        p99_time = max(times) if len(times) > 0 else 0

        # Cache lookups should be very fast
        assert avg_time < 5  # < 5ms average
        assert p99_time < 20  # 99th percentile < 20ms

    def test_cache_write_response_time(self, cache):
        """Test cache write response time"""
        times = []
        for i in range(1000):
            context = {"agent_id": f"agent_{i}", "round": i}
            decision = {"action": f"action_{i}", "nested": {"data": list(range(10))}}

            start_time = time.time()
            cache.cache_decision(context, decision, f"agent_{i % 20}")
            end_time = time.time()
            times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(times)
        max_time = max(times)

        # Cache writes should be fast
        assert avg_time < 10  # < 10ms average
        assert max_time < 50  # < 50ms worst case

    def test_cache_invalidation_response_time(self, cache):
        """Test cache invalidation response time"""
        # Pre-populate cache
        for i in range(100):
            context = {"agent_id": f"agent_{i}", "round": i}
            decision = {"action": f"action_{i}"}
            cache.cache_decision(context, decision, f"agent_{i % 10}")

        times = []
        for i in range(10):
            agent_id = f"agent_{i % 10}"
            start_time = time.time()
            cache.invalidate(agent_id)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)

        avg_time = statistics.mean(times)

        # Invalidation should be fast (O(n) where n = entries per agent)
        assert avg_time < 20  # < 20ms average


@pytest.mark.performance
class TestBenchmarking:
    """Benchmark critical operations"""

    def test_token_count_benchmark(self):
        """Benchmark token count calculation"""
        import timeit

        texts = [
            "Short",
            "Medium length text",
            "Longer text with much more content" * 10,
            "Chinese text for benchmarking" * 5
        ]

        for text in texts:
            time = timeit.timeit(
                lambda: PromptTemplateEngine.calculate_token_count(text),
                number=10000
            )

            # 10,000 iterations should complete quickly
            assert time.total < 1.0  # < 1 second

    def test_hash_calculation_benchmark(self):
        """Benchmark hash calculation (used in cache)"""
        import timeit
        import hashlib
        import json

        contexts = [
            {"agent_id": f"agent_{i}", "round": i, "data": list(range(10))}
            for i in range(1000)
        ]

        def calc_hash(context):
            context_str = json.dumps(context, sort_keys=True, ensure_ascii=False)
            return hashlib.sha256(context_str.encode()).hexdigest()

        time = timeit.timeit(
            lambda: [calc_hash(ctx) for ctx in contexts],
            number=100
        )

        # Should process quickly
        assert time.total < 2.0  # < 2 seconds

    @pytest.mark.asyncio
    async def test_async_overhead_benchmark(self):
        """Benchmark async overhead"""
        import asyncio
        import timeit

        async def sync_task():
            return "result"

        async def async_task():
            await asyncio.sleep(0.001)
            return "result"

        # Benchmark sync async calls
        sync_time = timeit.timeit(
            lambda: asyncio.run(sync_task()),
            number=1000
        )

        # Benchmark async await calls
        async_time = timeit.timeit(
            lambda: asyncio.run(async_task()),
            number=1000
        )

        # Async overhead should be minimal
        # Allow up to 10x overhead (still < 1ms per call)
        assert async_time.total / sync_time.total < 10
