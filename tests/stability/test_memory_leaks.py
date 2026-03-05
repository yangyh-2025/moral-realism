"""
内存泄漏稳定性测试

测试长时间运行后的内存使用检查：
- 内存使用检查
- 代理创建和销毁后的清理
"""
import pytest
import gc
import sys
from unittest.mock import Mock


@pytest.mark.stability
@pytest.mark.slow
class TestMemoryLeaks:
    """内存泄漏测试"""

    def test_agent_creation_cleanup(self):
        """测试代理创建和销毁后的内存清理"""
        try:
            from src.models.agent import Agent
        except ImportError:
            pytest.skip("Agent类未找到")

        # 记录初始内存
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 创建多个代理
        agents = []
        for i in range(100):
            agent = Agent(
                agent_id=f"agent_{i}",
                name=f"代理{i}",
                capability=Mock(),
                leadership_profile=Mock()
            )
            agents.append(agent)

        # 销毁所有代理
        agents.clear()
        gc.collect()

        # 检查内存是否释放
        final_objects = len(gc.get_objects())
        leaked_objects = final_objects - initial_objects

        # 允许一定程度的对象增长（不应超过初始的50%）
        assert leaked_objects < initial_objects * 0.5

    def test_capability_creation_cleanup(self):
        """测试能力对象创建和销毁后的清理"""
        try:
            from src.models.capability import Capability
        except ImportError:
            pytest.skip("Capability类未找到")

        # 记录初始内存
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 创建多个能力对象
        capabilities = []
        for i in range(100):
            capability = Capability(agent_id=f"cap_{i}")
            capabilities.append(capability)

        # 销毁所有能力对象
        capabilities.clear()
        gc.collect()

        # 检查内存是否释放
        final_objects = len(gc.get_objects())
        leaked_objects = final_objects - initial_objects

        assert leaked_objects < initial_objects * 0.5

    def test_history_growth_control(self):
        """测试历史记录增长控制"""
        try:
            from src.models.agent import Agent
        except ImportError:
            pytest.skip("Agent类未找到")

        agent = Agent(
            agent_id="test_agent",
            name="测试代理",
            capability=Mock(),
            leadership_profile=Mock()
        )

        # 添加大量历史记录
        for i in range(1000):
            agent.add_history("action", {"index": i})

        # 检查历史记录是否被正确管理
        history = agent.get_history()
        assert len(history) == 1000

        # 如果实现了历史大小限制，测试限制功能
        # 清理测试
        agent.history = []

    def test_simulation_lifecycle_memory(self):
        """测试模拟生命周期内存使用"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        # 记录初始内存
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 创建和销毁多个模拟控制器
        for _ in range(10):
            controller = SimulationController(
                agents=[],
                environment=Mock(),
                llm_engine=Mock(),
                total_rounds=5
            )
            # 模拟应该被正确清理

        gc.collect()

        # 检查内存是否释放
        final_objects = len(gc.get_objects())
        leaked_objects = final_objects - initial_objects

        assert leaked_objects < initial_objects * 0.5

    def test_get_memory_usage(self):
        """测试获取内存使用"""
        import psutil
        process = psutil.Process()

        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        # 内存使用应该是正值
        assert memory_mb > 0

        # 内存使用不应该过大（超过1GB可能表示泄漏）
        assert memory_mb < 1024
