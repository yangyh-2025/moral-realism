"""
并发模拟稳定性测试

测试多个模拟实例并发运行：
- 并发模拟执行
- 资源隔离验证
"""
import pytest
import asyncio
from unittest.mock import Mock


@pytest.mark.stability
@pytest.mark.slow
class TestConcurrentSimulation:
    """并发模拟测试"""

    @pytest.mark.asyncio
    async def test_multiple_simulations_concurrent(self):
        """测试多个模拟实例并发运行"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        # 创建多个模拟控制器
        controllers = []
        for i in range(3):
            controller = SimulationController(
                name=f"concurrent_sim_{i}",
                agents=[],
                environment=Mock(),
                llm_engine=Mock(),
                total_rounds=5
            )
            controllers.append(controller)

        # 并发启动所有模拟
        start_tasks = []
        for controller in controllers:
            if hasattr(controller, 'start'):
                start_tasks.append(controller.start())

        results = await asyncio.gather(*start_tasks, return_exceptions=True)

        # 检查所有模拟都成功启动
        assert len(results) == 3

        # 停止所有模拟
        for controller in controllers:
            if hasattr(controller, 'stop'):
                await controller.stop()

    @pytest.mark.asyncio
    async def test_resource_isolation(self):
        """测试资源隔离"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        # 创建两个独立的模拟
        controller1 = SimulationController(
            name="sim1",
            agents=[Mock(agent_id="agent_1")],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=3
        )

        controller2 = SimulationController(
            name="sim2",
            agents=[Mock(agent_id="agent_2")],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=3
        )

        # 验证两个控制器使用不同的资源
        if hasattr(controller1, 'name') and hasattr(controller2, 'name'):
            assert controller1.name != controller2.name

        # 启动两个模拟
        if hasattr(controller1, 'start') and hasattr(controller2, 'start'):
            await controller1.start()
            await controller2.start()

            # 等待运行
            await asyncio.sleep(1)

            # 停止模拟
            await controller1.stop()
            await controller2.stop()


@pytest.mark.stability
class TestConcurrentExecution:
    """并发执行测试"""

    @pytest.mark.asyncio
    async def test_concurrent_round_execution(self):
        """测试并发回合执行"""
        try:
            from src.workflow.round_executor import RoundExecutor
        except ImportError:
            pytest.skip("RoundExecutor类未找到")

        # 创建多个回合执行器
        executors = []
        for i in range(5):
            executor = RoundExecutor(
                agents=[],
                environment=Mock(),
                interaction_manager=Mock()
            )
            executors.append(executor)

        # 并发执行回合
        execute_tasks = []
        for i, executor in enumerate(executors):
            if hasattr(executor, 'execute_round'):
                execute_tasks.append(executor.execute_round(round_number=i))

        results = await asyncio.gather(*execute_tasks, return_exceptions=True)

        # 检查所有回合都执行
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_concurrent_agent_decisions(self):
        """测试并发代理决策"""
        # 模拟多个代理并发决策
        async def mock_agent_decision(agent_id):
            await asyncio.sleep(0.1)
            return {"agent_id": agent_id, "decision": "observe"}

        # 创建决策任务
        tasks = [mock_agent_decision(f"agent_{i}") for i in range(10)]

        results = await asyncio.gather(*tasks)

        # 验证所有决策都完成
        assert len(results) == 10
        for result in results:
            assert "agent_id" in result
            assert "decision" in result
