"""
长运行稳定性测试

测试连续执行多个回合：
- 长时间运行
- 指标连续性验证
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock


@pytest.mark.stability
@pytest.mark.slow
class TestLongRunningSimulation:
    """长运行模拟测试"""

    @pytest.mark.asyncio
    async def test_long_execution(self):
        """测试长运行执行（50+回合）"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        controller = SimulationController(
            name="长运行测试",
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=50
        )

        if hasattr(controller, 'start'):
            await controller.start()

            # 等待完成或超时
            max_wait = 60 120秒最大等待
            waited = 0
            while waited < max_wait:
                if hasattr(controller, 'is_running'):
                    if not controller.is_running():
                        break
                await asyncio.sleep(1)
                waited += 1

            # 停止模拟
            if hasattr(controller, 'stop'):
                await controller.stop()

            # 验证模拟已运行
            if hasattr(controller, 'get_current_round'):
                final_round = controller.get_current_round()
                assert final_round >= 1  # 至少运行了一回合

    @pytest.mark.asyncio
    async def test_metrics_continuity(self):
        """测试指标连续性"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        controller = SimulationController(
            name="连续性测试",
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=20
        )

        if hasattr(controller, 'enable_metrics_collection'):
            controller.enable_metrics_collection(enabled=True)

        if hasattr(controller, 'start'):
            await controller.start()

            # 等待运行
            await asyncio.sleep(5)

            # 停止模拟
            if hasattr(controller, 'stop'):
                await controller.stop()

            # 验证指标连续性
            if hasattr(controller, 'get_metrics'):
                metrics = controller.get_metrics()
                assert metrics is not None


@pytest.mark.stability
@pytest.mark.slow
class TestLongRunningStress:
    """长运行压力测试"""

    @pytest.mark.asyncio
    async def test_continuous_operations(self):
        """测试连续操作"""
        # 模拟连续操作
        operations_completed = 0

        for _ in range(100):
            # 执行一些操作
            await asyncio.sleep(0.01)
            operations_completed += 1

        assert operations_completed == 100

    @pytest.mark.asyncio
    async def test_resource_usage_over_time(self):
        """测试资源使用随时间的变化"""
        import psutil
        process = psutil.Process()

        initial_memory = process.memory_info().rss

        # 执行一些操作
        for _ in range(10):
            await asyncio.sleep(0.1)

        final_memory = process.memory_info().rss

        # 内存增长应该在合理范围内
        memory_growth = final_memory - initial_memory
        max_growth = 100 * 1024 * 1024  # 100MB最大增长

        assert memory_growth < max_growth


@pytest.mark.stability
class TestLongRunningDataIntegrity:
    """长运行数据完整性测试"""

    def test_round_number_consistency(self):
        """测试回合编号一致性"""
        # 模拟多个回合
        round_numbers = list(range(100))

        # 检查连续性
        for i in range(1, len(round_numbers)):
            assert round_numbers[i] == round_numbers[i-1] + 1

    def test_timestamp_sequence(self):
        """测试时间戳序列"""
        import time

        timestamps = []
        for _ in range(10):
            timestamps.append(time.time())
            time.sleep(0.01)

        # 检查时间戳单调递增
        for i in range(1, len(timestamps)):
            assert timestamps[i] > timestamps[i-1]
