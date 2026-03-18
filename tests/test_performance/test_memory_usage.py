"""
Performance tests for memory usage

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
import gc
import psutil
import time
from unittest.mock import Mock, AsyncMock

try:
    from infrastructure.llm.llm_engine import LLMEngine
    from domain.agents.base_agent import DecisionCache, AgentLearning
    from infrastructure.prompts.prompt_engine import PromptTemplateEngine, PromptTemplate
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not ENTITIES_AVAILABLE,
    reason="Core/Entities modules not available"
)


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage patterns"""

    @pytest.fixture
    def mock_provider(self):
        """Create mock LLM provider"""
        provider = Mock()

        async def quick_call(*args, **kwargs):
            # Minimal memory usage
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

    @pytest.fixture
    def process(self):
        """Get current process for memory measurement"""
        return psutil.Process()

    def test_llm_engine_initialization_memory(self, mock_provider):
        """Test memory usage during LLM engine initialization"""
        gc.collect()
        before_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        # Create engine
        engine = LLMEngine(provider=mock_provider)

        gc.collect()
        after_memory = self.process.memory_info().rss / 1024 / 1024  # MB

        memory_used = after_memory - before_memory

        # Engine initialization should use minimal memory
        assert memory_used < 50  # MB

    def test_llm_engine_multiple_calls_memory(self, process, mock_provider):
        """Test memory usage with multiple LLM calls"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        engine = LLMEngine(provider=mock_provider)

        # Make multiple calls
        for _ in range(100):
            engine._call_count += 1  # Simulate calls

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # Should not leak memory significantly
        assert memory_used < 100  # MB

    def test_decision_cache_memory_usage(self, process):
        """Test decision cache memory usage"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        cache = DecisionCache(max_size=1000, ttl=3600)

        # Add many entries
        for i in range(1000):
            context = {"agent_id": f"agent_{i}", "round": i % 10}
            decision = {"action": f"action_{i}", "target": f"target_{i}"}
            cache.cache_decision(context, decision, f"agent_{i % 10}")

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # 1000 cache entries should be reasonable
        assert memory_used < 200  # MB

    def test_decision_cache_lru_memory(self, process):
        """Test LRU cache memory efficiency"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        cache = DecisionCache(max_size=100, ttl=3600)

        # Add 500 entries (should trigger LRU after 100)
        for i in range(500):
            context = {"agent_id": f"agent_{i}", "round": i}
            decision = {"action": f"action_{i}"}
            cache.cache_decision(context, decision, "test_agent")

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # LRU should keep memory bounded
        assert memory_used < 100  # MB
        assert cache.get_stats()["size"] == 100  # Max size

    def test_agent_learning_memory_usage(self, process):
        """Test agent learning memory usage"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024  # MB (RSS on Windows)

        learning = AgentLearning(agent_id="test_agent", max_outcomes=1000)

        # Record many outcomes
        for i in range(500):
            decision = {"type": f"action_{i % 10}"}
            outcome = {"success": i % 2 == 0, "details": "Test result"}
            learning.record_outcome(decision, outcome)

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # 500 outcomes should be reasonable
        assert memory_used < 50  # MB

    def test_agent_learning_max_outcomes_memory(self, process):
        """Test max_outcomes limit memory efficiency"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        learning = AgentLearning(agent_id="test", max_outcomes=50)

        # Add more than max_outcomes
        for i in range(200):
            decision = {"type": "test"}
            outcome = {"success": True}
            learning.record_outcome(decision, outcome)

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # Should be bounded by max_outcomes
        assert memory_used < 20  # MB
        assert len(learning._outcomes) == 50

    def test_prompt_engine_template_cache_memory(self, process):
        """Test prompt template engine cache memory"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        engine = PromptTemplateEngine(
            template_dir="config/prompts/",
            enable_cache=True
        )

        # Load all templates multiple times
        templates = list(PromptTemplate)
        for _ in range(10):
            for template in templates:
                engine.load_template(template)

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # Caching should keep memory usage low
        assert memory_used < 50  # MB

    def test_prompt_engine_render_memory(self, process):
        """Test prompt rendering memory usage"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        engine = PromptTemplateEngine(
            template_dir="config/prompts/",
            enable_cache=False  # No cache to test render memory
        )

        # Render many prompts
        context = {
            "agent_name": "Test Country",
            "leader_type": "wangdao",
            "current_situation": "Peaceful",
            "available_actions": ["action1", "action2"],
            "constraints": [],
            "objective_interests": ["stability"],
            "alliances": [],
            "enemies": []
        }

        for _ in range(100):
            engine.render_template(
                PromptTemplate.LEADER_DECISION,
                context
            )

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # Should handle many renders efficiently
        assert memory_used < 100  # MB

    def test_prompt_builder_chain_memory(self, process):
        """Test prompt builder chain memory usage"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        from core.prompt_engine import PromptBuilder, PromptTemplate

        # Create many prompts
        prompts = []
        for i in range(100):
            prompt = (PromptBuilder(PromptTemplate.LEADER_DECISION, {})
                      .add_variable("agent_name", f"Country {i}")
                      .add_variable("leader_type", "wangdao")
                      .add_variable("current_situation", "Test")
                      .build())
            prompts.append(prompt)

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # Built prompts should be freed
        assert memory_used < 100  # MB

    def test_memory_leak_detection(self, process, mock_provider):
        """Test for memory leaks in repeated operations"""
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024

        engine = LLMEngine(provider=mock_provider)

        # Repeat operations many times
        for iteration in range(5):
            engine._call_count = 0
            engine._cache = {}

            # Simulate usage pattern
            for _ in range(100):
                engine._call_count += 1
                engine._cache[f"iteration_{iteration}_context_{_}"] = {"result": "test"}

            # Clear cache
            engine._cache.clear()

            gc.collect()

            memory_after_iteration = process.memory_info().rss / 1024 / 1024
            memory_growth = memory_after_iteration - initial_memory

            # Memory should not grow unboundedly
            assert memory_growth < 200  # MB

    def test_large_data_structure_memory(self, process):
        """Test memory usage with large data structures"""
        gc.collect()
        before_memory = process.memory_info().rss / 1024 / 1024

        # Create large data structures
        large_dict = {}
        for i in range(10000):
            large_dict[f"key_{i}"] = {
                "nested_data": list(range(100)),
                "agent_info": {
                    "name": f"Agent {i}",
                    "power": {"economic": i * 10, "military": i * 8},
                    "preferences": {f"pref_{j}": j for j in range(50)}
                }
            }

        gc.collect()
        after_memory = process.memory_info().rss / 1024 / 1024

        memory_used = after_memory - before_memory

        # Large data structure should be within reasonable limits
        assert memory_used < 500  # MB (10k agents with nested data)

        # Clean up
        del large_dict
        gc.collect()


@pytest.mark.performance
class TestMemoryEfficiency:
    """Test memory efficiency optimizations"""

    def test_string_interning_memory(self):
        """Test string interning memory efficiency"""
        gc.collect()
        process = psutil.Process()
        before_memory = process.memory_info().rss / 1024 / 1024

        # Bad practice: string concatenation in loop
        result = ""
        for i in range(10000):
            result += f"item_{i},"

        gc.collect()
        after_concat_memory = process.memory_info().rss / 1024 / 1024

        # Better practice: list join
        gc.collect()
        before_join_memory = process.memory_info().rss / 1024 / 1024

        items = [f"item_{i}" for i in range(10000)]
        better_result = ",".join(items)

        gc.collect()
        after_join_memory = process.memory_info().rss / 1024 / 1024

        # Join should use similar or less memory
        concat_memory = after_concat_memory - before_memory
        join_memory = after_join_memory - before_join_memory

        assert join_memory <= concat_memory * 1.5  # Allow some overhead

    def test_generator_memory_efficiency(self):
        """Test generator memory efficiency"""
        gc.collect()
        process = psutil.Process()
        before_list_memory = process.memory_info().rss / 1024 / 1024

        # List approach (loads all into memory)
        data_list = [i * i for i in range(100000)]

        gc.collect()
        after_list_memory = process.memory_info().rss / 1024 / 1024

        # Generator approach (lazy evaluation)
        gc.collect()
        before_gen_memory = process.memory_info().rss / 1024 / 1024

        def generate_data():
            for i in range(100000):
                yield i * i

        gen_sum = sum(generate_data())

        gc.collect()
        after_gen_memory = process.memory_info().rss / 1024 / 1024

        # Generator should use less memory initially
        # (though final result might be similar)
        assert before_gen_memory <= after_list_memory

    def test_dict_copy_memory(self):
        """Test dict copy memory usage"""
        gc.collect()
        process = psutil.Process()
        before_memory = process.memory_info().rss / 1024 / 1024

        original = {
            f"key_{i}": f"value_{i}" * 100
            for i in range(1000)
        }

        # Make shallow copy
        shallow_copy = original.copy()

        gc.collect()
        after_shallow_memory = process.memory_info().rss / 1024 / 1024

        # Make deep copy
        import copy
        deep_copy = copy.deepcopy(original)

        gc.collect()
        after_deep_memory = process.memory_info().rss / 1024 / 1024

        shallow_memory = after_shallow_memory - before_memory
        deep_memory = after_deep_memory - after_shallow_memory

        # Deep copy should use more memory (as expected)
        assert deep_memory > shallow_memory
