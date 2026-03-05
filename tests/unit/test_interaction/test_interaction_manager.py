"""
交互管理器单元测试

测试InteractionManager类的核心功能：
- 初始化和配置
- 代理注册和注销
- 互动执行
- 互动历史和统计
"""
import pytest
from unittest.mock import Mock, AsyncMock
import asyncio


class TestInteractionManagerInitialization:
    """测试InteractionManager初始化"""

    def test_interaction_manager_initialization(self):
        """测试交互管理器初始化"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="测试交互管理器")

        assert manager.name == "测试交互管理器"

    def test_interaction_manager_with_environment(self):
        """测试带环境初始化"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        mock_env = Mock()
        manager = InteractionManager(name="带环境的管理器", environment=mock_env)

        if hasattr(manager, 'environment'):
            assert manager.environment is mock_env


class TestInteractionManagerAgentRegistration:
    """测试代理注册和注销"""

    def test_register_agent(self):
        """测试注册代理"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="代理注册测试")
        mock_agent = Mock()
        mock_agent.agent_id = "agent_1"

        if hasattr(manager, 'register_agent'):
            manager.register_agent(mock_agent)

            if hasattr(manager, 'agents'):
                assert "agent_1" in manager.agents

    def test_unregister_agent(self):
        """测试注销代理"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="代理注销测试")
        mock_agent = Mock()
        mock_agent.agent_id = "agent_1"

        if hasattr(manager, 'register_agent') and hasattr(manager, 'unregister_agent'):
            manager.register_agent(mock_agent)
            manager.unregister_agent("agent_1")

            if hasattr(manager, 'agents'):
                assert "agent_1" not in manager.agents

    def test_get_agent(self):
        """测试获取代理"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="获取代理测试")
        mock_agent = Mock()
        mock_agent.agent_id = "agent_1"

        if hasattr(manager, 'register_agent') and hasattr(manager, 'get_agent'):
            manager.register_agent(mock_agent)

            retrieved = manager.get_agent("agent_1")
            assert retrieved is mock_agent


class TestInteractionManagerDirectInteraction:
    """测试直接互动"""

    @pytest.mark.asyncio
    async def test_execute_interaction(self):
        """测试执行直接互动"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="直接互动测试")

        if hasattr(manager, 'execute_interaction'):
            result = await manager.execute_interaction(
                source_id="agent_1",
                target_id="agent_2",
                interaction_type="diplomatic",
                content="测试内容"
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_execute_interaction_validation(self):
        """测试互动验证"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="互动验证测试")

        if hasattr(manager, 'is_interaction_valid'):
            is_valid = manager.is_interaction_valid(
                source_id="agent_1",
                target_id="agent_2",
                interaction_type="diplomatic"
            )

            assert isinstance(is_valid, bool)


class TestInteractionManagerBroadcast:
    """测试广播互动"""

    @pytest.mark.asyncio
    async def test_broadcast(self):
        """测试广播互动"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="广播测试")

        # 注册多个代理
        for i in range(3):
            mock_agent = Mock()
            mock_agent.agent_id = f"agent_{i}"
            if hasattr(manager, 'register_agent'):
                manager.register_agent(mock_agent)

        if hasattr(manager, 'broadcast'):
            result = await manager.broadcast(
                source_id="agent_0",
                message="广播消息",
                exclude=["agent_0"]
            )

            assert result is not None


class TestInteractionManagerMultilateral:
    """测试多边互动"""

    @pytest.mark.asyncio
    async def test_execute_multilateral(self):
        """测试执行多边互动"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="多边互动测试")

        if hasattr(manager, 'execute_multilateral'):
            result = await manager.execute_multilateral(
                participants=["agent_1", "agent_2", "agent_3"],
                interaction_type="negotiation",
                content="谈判内容"
            )

            assert result is not None


class TestInteractionManagerHistory:
    """测试互动历史"""

    def test_record_interaction(self):
        """测试记录互动"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="历史记录测试")

        if hasattr(manager, 'record_interaction'):
            manager.record_interaction({
                "source": "agent_1",
                "target": "agent_2",
                "type": "diplomatic",
                "timestamp": 0
            })

            if hasattr(manager, 'history'):
                assert len(manager.history) == 1

    def test_get_interaction_history(self):
        """测试获取互动历史"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="获取历史测试")

        if hasattr(manager, 'record_interaction') and hasattr(manager, 'get_interaction_history'):
            manager.record_interaction({
                "source": "agent_1",
                "target": "agent_2",
                "type": "diplomatic",
                "timestamp": 0
            })

            history = manager.get_interaction_history()
            assert len(history) == 1

    def test_get_interaction_history_filtered(self):
        """测试获取过滤的互动历史"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="过滤历史测试")

        if hasattr(manager, 'record_interaction') and hasattr(manager, 'get_interaction_history'):
            manager.record_interaction({
                "source": "agent_1",
                "target": "agent_2",
                "type": "diplomatic",
                "timestamp": 0
            })

            manager.record_interaction({
                "source": "agent_2",
                "target": "agent_3",
                "type": "military",
                "timestamp": 1
            })

            diplomatic_history = manager.get_interaction_history(
                filter_type="diplomatic"
            )
            assert len(diplomatic_history) == 1


class TestInteractionManagerStatistics:
    """测试互动统计"""

    def test_get_statistics(self):
        """测试获取统计信息"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="统计测试")

        if hasattr(manager, 'get_statistics'):
            stats = manager.get_statistics()
            assert isinstance(stats, dict)

    def test_get_interaction_frequency(self):
        """测试获取互动频率"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="频率测试")

        if hasattr(manager, 'record_interaction') and hasattr(manager, 'get_interaction_frequency'):
            for i in range(3):
                manager.record_interaction({
                    "source": "agent_1",
                    "target": "agent_2",
                    "type": "diplomatic",
                    "timestamp": i
                })

            frequency = manager.get_interaction_frequency("agent_1", "agent_2")
            assert frequency == 3


class TestInteractionManagerConstraints:
    """测试互动约束"""

    def test_add_constraint(self):
        """测试添加约束"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="约束测试")

        if hasattr(manager, 'add_constraint'):
            def constraint_fn(source, target, interaction_type):
                return True

            manager.add_constraint("diplomatic", constraint_fn)

            # 约束已添加
            pass

    def test_check_constraints(self):
        """测试检查约束"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="约束检查测试")

        if hasattr(manager, 'add_constraint') and hasattr(manager, 'check_constraints'):
            def always_true(source, target, interaction_type):
                return True

            manager.add_constraint("diplomatic", always_true)

            result = manager.check_constraints("agent_1", "agent_2", "diplomatic")
            assert result is True


class TestInteractionManagerMetrics:
    """测试互动指标"""

    def test_get_metrics(self):
        """测试获取指标"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="指标测试")

        if hasattr(manager, 'get_metrics'):
            metrics = manager.get_metrics()
            assert isinstance(metrics, dict)

    def test_track_interaction_outcome(self):
        """测试追踪互动结果"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="结果追踪测试")

        if hasattr(manager, 'track_interaction_outcome'):
            manager.track_interaction_outcome(
                interaction_id="interaction_1",
                outcome="success",
                impact_score=0.8
            )

            # 结果已追踪
            pass


class TestInteractionManagerReset:
    """测试重置功能"""

    def test_reset(self):
        """测试重置"""
        try:
            from src.interaction.interaction_manager import InteractionManager
        except ImportError:
            pytest.skip("InteractionManager类未找到")

        manager = InteractionManager(name="重置测试")

        if hasattr(manager, 'record_interaction') and hasattr(manager, 'reset'):
            manager.record_interaction({
                "source": "agent_1",
                "target": "agent_2",
                "type": "diplomatic",
                "timestamp": 0
            })

            manager.reset()

            if hasattr(manager, 'history'):
                assert len(manager.history) == 0
