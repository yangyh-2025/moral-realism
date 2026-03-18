"""
Performance tests for concurrent decision making

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
import asyncio
import time
from typing import List, Dict
from unittest.mock import Mock, AsyncMock
import psutil
import gc

try:
    from infrastructure.llm.llm_engine import LLMEngine, LLMProvider
    from domain.agents.base_agent import BaseAgent, DecisionCache
    from domain.power.power_metrics import PowerMetrics
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not ENTITIES_AVAILABLE,
    reason="Entities module not available"
)


@pytest.mark.performance
class TestConcurrentDecisionMaking:
    """Test concurrent decision making performance"""

    @pytest.fixture
    def mock_provider(self):
        """Create mock LLM provider with realistic latency"""
        provider = Mock()
        provider.generate = AsyncMock()

        async def simulate_api_call(*args, **kwargs):
            # Simulate realistic API latency (100-500ms)
            await asyncio.sleep(0.1 + (asyncio.get_event_loop().time() % 0.4))
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

        provider.generate = simulate_api_call
        return provider

    @pytest.fixture
    def llm_engine(self, mock_provider):
        """Create LLM engine"""
        return LLMEngine(provider=mock_provider)

    @pytest.fixture
    def sample_agents(self):
        """Create sample agents"""
        return [
            {"agent_id": f"agent_{i}", "name": f"Agent {i}"}
            for i in range(10)
        ]

    @pytest.mark.asyncio
    async def test_sequential_decision_making(self, llm_engine, sample_agents):
        """Test sequential decision making performance"""
        start_time = time.time()

        decisions = []
        for agent in sample_agents:
            decision = await llm_engine.make_decision(
                agent_id=agent["agent_id"],
                prompt=f"Decision for {agent['name']}",
                available_functions=[{"name": "action1"}, {"name": "action2"}],
                prohibited_functions=[]
            )
            decisions.append(decision)

        end_time = time.time()
        total_time = end_time - start_time

        # Sequential should take roughly num_agents * latency
        assert total_time > 0
        assert len(decisions) == len(sample_agents)

    @pytest.mark.asyncio
    async def test_concurrent_decision_making(self, llm_engine, sample_agents):
        """Test concurrent decision making performance"""
        start_time = time.time()

        # Create tasks for all agents
        tasks = [
            llm_engine.make_decision(
                agent_id=agent["agent_id"],
                prompt=f"Decision for {agent['name']}",
                available_functions=[{"name": "action1"}, {"name": "action2"}],
                prohibited_functions=[]
            )
            for agent in sample_agents
        ]

        # Execute concurrently
        decisions = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Concurrent should be much faster than sequential
        # With 10 agents and ~250ms latency each, sequential would be ~2.5s
        # Concurrent should be closer to max latency (~500ms)
        assert total_time > 0
        assert len(decisions) == len(sample_agents)
        assert total_time < 2.0  # Should complete within 2 seconds

    @pytest.mark.asyncio
    async def test_concurrent_with_many_agents(self, llm_engine):
        """Test concurrent decisions with many agents"""
        num_agents = 50
        agents = [{"agent_id": f"agent_{i}"} for i in range(num_agents)]

        start_time = time.time()

        tasks = [
            llm_engine.make_decision(
                agent_id=agent["agent_id"],
                prompt=f"Decision {i}",
                available_functions=[{"name": "action1"}],
                prohibited_functions=[]
            )
            for i, agent in enumerate(agents)
        ]

        decisions = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # Even with 50 agents, should complete reasonably fast
        assert len(decisions) == num_agents
        assert total_time < 5.0  # Should complete within 5 seconds

    @pytest.mark.asyncio
    async def test_concurrent_with_rate_limiting(self, sample_agents):
        """Test concurrent decisions rate limiting"""
        # Create slower provider
        slow_provider = Mock()
        slow_provider.generate = AsyncMock()

        async def slow_api_call(*args, **kwargs):
            await asyncio.sleep(0.5)  # 500ms latency
            return {
                "choices": [{
                    "message": {
                        "function_call": {
                            "name": "test_action",
                            "arguments": "{}"
                        }
                    }
                }]
            }

        slow_provider.generate = slow_api_call

        engine = LLMEngine(provider=slow_provider)

        # Use semaphore to limit concurrency
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

        async def limited_decision(agent_id, prompt):
            async with semaphore:
                return await engine.make_decision(
                    agent_id=agent_id,
                    prompt=prompt,
                    available_functions=[{"name": "action1"}],
                    prohibited_functions=[]
                )

        start_time = time.time()

        tasks = [limited_decision(agent["agent_id"], f"Test {i}")
                for i, agent in enumerate(sample_agents)]

        decisions = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # With 10 agents, 500ms each, semaphore of 5
        # Should take roughly 2 * (10/5) = 2 seconds
        assert len(decisions) == len(sample_agents)
        assert total_time < 4.0

    @pytest.mark.asyncio
    async def test_concurrent_error_handling(self, llm_engine, sample_agents):
        """Test concurrent decision making with errors"""
        # Make some requests fail
        fail_count = 0

        async def failing_generate(*args, **kwargs):
            nonlocal fail_count
            fail_count += 1
            if fail_count % 3 == 0:  # Every 3rd request fails
                raise Exception("Simulated API error")
            await asyncio.sleep(0.1)
            return {
                "choices": [{
                    "message": {
                        "function_call": {
                            "name": "test_action",
                            "arguments": "{}"
                        }
                    }
                }]
            }

        llm_engine.provider.generate = failing_generate

        tasks = [
            llm_engine.make_decision(
                agent_id=agent["agent_id"],
                prompt=f"Test {i}",
                available_functions=[{"name": "action1"}],
                prohibited_functions=[]
            )
            for i, agent in enumerate(sample_agents)
        ]

        # Some should fail
        results = []
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(("success", result))
            except Exception as e:
                results.append(("error", str(e)))

        # Should have both successes and failures
        successes = sum(1 for status, _ in results if status == "success")
        failures = sum(1 for status, _ in results if status == "error")

        assert successes > 0
        assert failures > 0
        assert len(results) == len(sample_agents)


@pytest.mark.performance
class TestMemoryUsageDuringConcurrency:
    """Test memory usage during concurrent operations"""

    @pytest.fixture
    def mock_provider(self):
        provider = Mock()

        async def quick_call(*args, **kwargs):
            await asyncio.sleep(0.05)  # 50ms
            return {
                "choices": [{
                    "message": {
                        "function_call": {
                            "name": "test_action",
                            "arguments": "{}"
                        }
                    }
                }]
            }

        provider.generate = quick_call
        return provider

    @pytest.mark.asyncio
    async def test_memory_growth_concurrent_decisions(self, mock_provider):
        """Test memory growth during concurrent decisions"""
        gc.collect()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        engine = LLMEngine(provider=mock_provider)

        # Make many concurrent decisions
        num_iterations = 10
        num_agents = 20

        for iteration in range(num_iterations):
            agents = [{"agent_id": f"agent_{i}_{iteration}"} for i in range(num_agents)]

            tasks = [
                engine.make_decision(
                    agent_id=agent["agent_id"],
                    prompt=f"Decision {i}",
                    available_functions=[{"name": "action1"}],
                    prohibited_functions=[]
                )
                for i, agent in enumerate(agents)
            ]

            await asyncio.gather(*tasks)

            # Force garbage collection
            gc.collect()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory

        # Memory growth should be reasonable (< 100MB)
        assert memory_growth < 100

    @pytest.mark.asyncio
    async def test_cache_memory_efficiency(self, mock_provider):
        """Test memory efficiency with caching"""
        gc.collect()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024

        engine = LLMEngine(provider=mock_provider)

        # Make many decisions with repeated context
        num_requests = 100

        tasks = [
            engine.make_decision(
                agent_id="test_agent",
                prompt="Same prompt",  # Repeated context
                available_functions=[{"name": "action1"}],
                prohibited_functions=[]
            )
            for _ in range(num_requests)
        ]

        await asyncio.gather(*tasks)

        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_used = final_memory - initial_memory

        # With caching, memory usage should be efficient
        # Even 100 identical requests should not use much memory
        assert memory_used < 50


@pytest.mark.performance
@pytest.mark.slow
class TestStressTest:
    """Stress tests for concurrent operations"""

    @pytest.fixture
    def mock_provider(self):
        provider = Mock()

        async def quick_call(*args, **kwargs):
            await asyncio.sleep(0.01)  # 10ms
            return {
                "choices": [{
                    "message": {
                        "function_call": {
                            "name": "test_action",
                            "arguments": "{}"
                        }
                    }
                }]
            }

        provider.generate = quick_call
        return provider

    @pytest.mark.asyncio
    async def test_high_concurrency_decisions(self, mock_provider):
        """Test high concurrency decision making"""
        engine = LLMEngine(provider=mock_provider)

        num_agents = 100
        agents = [{"agent_id": f"agent_{i}"} for i in range(num_agents)]

        start_time = time.time()

        tasks = [
            engine.make_decision(
                agent_id=agent["agent_id"],
                prompt=f"Decision {i}",
                available_functions=[{"name": "action1"}],
                prohibited_functions=[]
            )
            for i, agent in enumerate(agents)
        ]

        decisions = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        assert len(decisions) == num_agents

        # With 100 concurrent requests and 10ms each,
        # should complete in roughly 100ms plus overhead
        # Allow for system overhead
        assert total_time < 3.0

    @pytest.mark.asyncio
    async def test_burst_decisions(self, mock_provider):
        """Test burst pattern of decisions"""
        engine = LLMEngine(provider=mock_provider)

        # Simulate burst traffic
        num_bursts = 10
        agents_per_burst = 20

        total_start_time = time.time()

        for burst in range(num_bursts):
            agents = [{"agent_id": f"agent_{burst}_{i}"} for i in range(agents_per_burst)]

            tasks = [
                engine.make_decision(
                    agent_id=agent["agent_id"],
                    prompt=f"Decision {burst}_{i}",
                    available_functions=[{"name": "action1"}],
                    prohibited_functions=[]
                )
                for i, agent in enumerate(agents)
            ]

            await asyncio.gather(*tasks)

            # Small delay between bursts
            await asyncio.sleep(0.05)

        total_end_time = time.time()
        total_time = total_end_time - total_start_time

        total_requests = num_bursts * agents_per_burst

        # Calculate requests per second
        rps = total_requests / total_time

        # Should handle at least 100 RPS
        assert rps > 100
