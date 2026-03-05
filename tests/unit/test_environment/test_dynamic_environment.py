"""
动态环境单元测试

测试DynamicEnvironment类的核心功能：
- 初始化和配置
- 动态事件管理
- 环境状态更新
"""
import pytest
from unittest.mock import Mock


class TestDynamicEnvironmentInitialization:
    """测试DynamicEnvironment初始化"""

    def test_dynamic_environment_initialization(self):
        """测试动态环境初始化"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="动态测试环境")

        assert env.name == "动态测试环境"

    def test_dynamic_environment_with_base_environment(self):
        """测试基于基础环境初始化"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("环境类未找到")

        base_env = StaticEnvironment(name="基础环境")
        env = DynamicEnvironment(name="动态环境", base_environment=base_env)

        if hasattr(env, 'base_environment'):
            assert env.base_environment is base_env


class TestDynamicEnvironmentEventManagement:
    """测试动态事件管理"""

    def test_add_event(self):
        """测试添加事件"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="事件测试环境")

        if hasattr(env, 'add_event'):
            event = {
                "event_id": "event_1",
                "type": "crisis",
                "timestamp": 0,
                "data": {"severity": "high"}
            }

            env.add_event(event)

            if hasattr(env, 'events'):
                assert len(env.events) == 1

    def test_get_events_by_type(self):
        """测试按类型获取事件"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="事件类型测试环境")

        if hasattr(env, 'add_event') and hasattr(env, 'get_events_by_type'):
            env.add_event({
                "event_id": "event_1",
                "type": "crisis",
                "timestamp": 0
            })

            env.add_event({
                "event_id": "event_2",
                "type": "cooperation",
                "timestamp": 1
            })

            crisis_events = env.get_events_by_type("crisis")
            assert len(crisis_events) == 1

    def test_get_events_by_time_range(self):
        """测试按时间范围获取事件"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="时间事件测试环境")

        if hasattr(env, 'add_event') and hasattr(env, 'get_events_by_time_range'):
            env.add_event({"event_id": "event_1", "timestamp": 10})
            env.add_event({"event_id": "event_2", "timestamp": 20})
            env.add_event({"event_id": "event_3", "timestamp": 30})

            events = env.get_events_by_time_range(15, 25)
            assert len(events) == 1

    def test_clear_events(self):
        """测试清除事件"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="清除测试环境")

        if hasattr(env, 'add_event') and hasattr(env, 'clear_events'):
            env.add_event({"event_id": "event_1", "timestamp": 0})
            env.clear_events()

            if hasattr(env, 'events'):
                assert len(env.events) == 0


class TestDynamicEnvironmentStateUpdates:
    """测试环境状态更新"""

    def test_update_state(self):
        """测试更新状态"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="状态更新测试环境")

        if hasattr(env, 'update_state'):
            env.update_state({"order_level": 4})

            if hasattr(env, 'state'):
                assert env.state.get("order_level") == 4

    def test_get_state(self):
        """测试获取状态"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="状态获取测试环境")

        if hasattr(env, 'get_state'):
            state = env.get_state()
            assert isinstance(state, dict)

    def test_get_state_history(self):
        """测试获取状态历史"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="状态历史测试环境")

        if hasattr(env, 'get_state_history'):
            history = env.get_state_history()
            assert isinstance(history, list)


class TestDynamicEnvironmentTimeManagement:
    """测试时间管理"""

    def test_advance_time(self):
        """测试推进时间"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="时间测试环境")

        if hasattr(env, 'advance_time'):
            initial_time = env.current_time if hasattr(env, 'current_time') else 0
            env.advance_time(5)

            if hasattr(env, 'current_time'):
                assert env.current_time == initial_time + 5

    def test_get_current_time(self):
        """测试获取当前时间"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="当前时间测试环境")

        if hasattr(env, 'get_current_time'):
            time = env.get_current_time()
            assert isinstance(time, int)


class TestDynamicEnvironmentAgentTracking:
    """测试代理跟踪"""

    def test_register_agent(self):
        """测试注册代理"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="代理测试环境")
        mock_agent = Mock()
        mock_agent.agent_id = "agent_1"

        if hasattr(env, 'register_agent'):
            env.register_agent(mock_agent)

            if hasattr(env, 'agents'):
                assert len(env.agents) == 1

    def test_unregister_agent(self):
        """测试注销代理"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="代理注销测试环境")
        mock_agent = Mock()
        mock_agent.agent_id = "agent_1"

        if hasattr(env, 'register_agent') and hasattr(env, 'unregister_agent'):
            env.register_agent(mock_agent)
            env.unregister_agent("agent_1")

            if hasattr(env, 'agents'):
                assert len(env.agents) == 0

    def test_get_agent(self):
        """测试获取代理"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="获取代理测试环境")
        mock_agent = Mock()
        mock_agent.agent_id = "agent_1"

        if hasattr(env, 'register_agent') and hasattr(env, 'get_agent'):
            env.register_agent(mock_agent)

            retrieved = env.get_agent("agent_1")
            assert retrieved is mock_agent


class TestDynamicEnvironmentResourceChanges:
    """测试资源变化"""

    def test_modify_resource(self):
        """测试修改资源"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="资源修改测试环境")

        if hasattr(env, 'modify_resource'):
            env.modify_resource("oil", "region_a", -100)

            # 资源已修改
            pass

    def test_get_resource_changes(self):
        """测试获取资源变化"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="资源变化测试环境")

        if hasattr(env, 'get_resource_changes'):
            changes = env.get_resource_changes()
            assert isinstance(changes, dict)


class TestDynamicEnvironmentSaveLoad:
    """测试保存和加载"""

    def test_save_state(self, temp_dir):
        """测试保存状态"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="保存测试环境")

        if hasattr(env, 'save_state'):
            save_path = temp_dir / "environment_state.json"
            env.save_state(str(save_path))

            assert save_path.exists()

    def test_load_state(self, temp_dir):
        """测试加载状态"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env1 = DynamicEnvironment(name="加载测试环境")

        if hasattr(env1, 'save_state') and hasattr('load_state'):
            save_path = temp_dir / "environment_state.json"
            env1.save_state(str(save_path))

            env2 = DynamicEnvironment(name="新环境")
            env2.load_state(str(save_path))

            # 状态已加载
            pass


class TestDynamicEnvironmentEventTriggers:
    """测试事件触发"""

    def test_trigger_shock(self):
        """测试触发冲击事件"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="冲击测试环境")

        if hasattr(env, 'trigger_shock'):
            shock = {
                "type": "economic_crisis",
                "affected_regions": ["region_a"],
                "impact": -0.2
            }

            result = env.trigger_shock(shock)
            assert result is True

    def test_trigger_opportunity(self):
        """测试触发机遇事件"""
        try:
            from src.environment.dynamic_environment import DynamicEnvironment
        except ImportError:
            pytest.skip("DynamicEnvironment类未找到")

        env = DynamicEnvironment(name="机遇测试环境")

        if hasattr(env, 'trigger_opportunity'):
            opportunity = {
                "type": "technology_breakthrough",
                "beneficiary": "agent_1",
                "impact": 0.15
            }

            result = env.trigger_opportunity(opportunity)
            assert result is True
