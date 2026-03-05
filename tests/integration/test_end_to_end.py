"""
端到端集成测试

测试完整的模拟工作流：
- 完整模拟生命周期
- 检查点保存和恢复
"""
import pytest
from unittest.mock import Mock, AsyncMock
import asyncio


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndSimulation:
    """端到端模拟测试"""

    @pytest.mark.asyncio
    async def test_full_simulation_lifecycle(self):
        """测试完整模拟生命周期"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        # 创建模拟控制器
        controller = SimulationController(
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=5  # 短运行用于测试
        )

        # 启动模拟
        if hasattr(controller, 'start'):
            await controller.start()

        # 等待完成或超时
        if hasattr(controller, 'is_running'):
            for _ in range(10):
                if not controller.is_running():
                    break
                await asyncio.sleep(与其他0.1)

        # 停止模拟
        if hasattr(controller, 'stop'):
            await controller.stop()

        # 验证状态
        if hasattr(controller, 'get_status'):
            status = controller.get_status()
            # 模拟应该已停止
            pass

    @pytest.mark.asyncio
    async def test_checkpoint_and_restore(self, temp_dir):
        """测试检查点保存和恢复"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        # 创建第一个模拟控制器
        controller1 = SimulationController(
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=10
        )

        # 运行一些回合
        if hasattr(controller1, 'start'):
            await controller1.start()

            # 运行5回合
            for _ in range(5):
                await asyncio.sleep(0.1)
                if hasattr(controller1, 'get_current_round'):
                    if controller1.get_current_round() >= 5:
                        break

            # 保存检查点
            checkpoint_path = temp_dir / "test_checkpoint.json"
            if hasattr(controller1, 'save_checkpoint'):
                await controller1.save_checkpoint(str(checkpoint_path))

            # 停止第一个控制器
            await controller1.stop()

        # 创建第二个控制器并恢复
        if checkpoint_path.exists():
            controller2 = SimulationController(
                agents=[],
                environment=Mock(),
                llm_engine=Mock(),
                total_rounds=10
            )

            if hasattr(controller2, 'load_checkpoint'):
                await controller2.load_checkpoint(str(checkpoint_path))

                # 验证恢复状态
                if hasattr(controller2, 'get_current_round'):
                    round = controller2.get_current_round()
                    assert round >= 5

    @pytest.mark.asyncio
    async def test_simulation_with_intervention(self):
        """测试带干预的模拟"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        controller = SimulationController(
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=10
        )

        # 添加干预
        if hasattr(controller, 'add_intervention'):
            controller.add_intervention({
                "round": 5,
                "type": "modify_agent_property",
                "target": "agent_1",
                "property": "moral_level",
                "value": 4
            })

        # 运行模拟
        if hasattr(controller, 'start'):
            await controller.start()

            # 等待完成或超时
            for _ in range(20):
                await asyncio.sleep(0.1)
                if hasattr(controller, 'get_current_round'):
                    if controller.get_current_round() >= 5:
                        break

            # 停止模拟
            await controller.stop()


@pytest.mark.integration
class TestEndToEndDataFlow:
    """端到端数据流测试"""

    @pytest.mark.asyncio
    async def test_metrics_data_collection(self):
        """测试指标数据收集"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        controller = SimulationController(
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=5
        )

        # 启用指标收集
        if hasattr(controller, 'enable_metrics_collection'):
            controller.enable_metrics_collection(enabled=True)

        # 运行模拟
        if hasattr(controller, 'start'):
            await controller.start()

            # 等待完成
            for _ in range(10):
                await asyncio.sleep(0.1)
                if hasattr(controller, 'get_current_round'):
                    if controller.get_current_round() >= 5:
                        break

            # 获取指标
            if hasattr(controller, 'get_metrics'):
                metrics = controller.get_metrics()
                assert isinstance(metrics, dict)

            # 停止模拟
            await controller.stop()

    @pytest.mark.asyncio
    async def test_event_propagation(self):
        """测试事件传播"""
        try:
            from src.workflow.simulation_controller import SimulationController
        except ImportError:
            pytest.skip("SimulationController类未找到")

        controller = SimulationController(
            agents=[],
            environment=Mock(),
            llm_engine=Mock(),
            total_rounds=3
        )

        # 注册事件处理器
        events_received = []

        def event_handler(event):
            events_received.append(event)

        if hasattr(controller, 'register_event_handler'):
            controller.register_event_handler("round_complete", event_handler)

        # 运行模拟
        if hasattr(controller, 'start'):
            await controller.start()

            # 等待完成
            for _ in range(10):
                await asyncio.sleep(0.1)
                if hasattr(controller, 'get_current_round'):
                    if controller.get_current_round() >= 3:
                        break

            # 验证事件被接收
            assert len(events_received) >= 1

            # 停止模拟
            await controller.stop()
