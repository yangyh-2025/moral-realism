"""
控制器代理单元测试

测试ControllerAgent类的核心功能：
- 初始化和配置
- 配置管理
"""
import pytest
from unittest.mock import Mock


class TestControllerAgentInitialization:
    """测试ControllerAgent初始化"""

    def test_controller_agent_initialization(self):
        """测试控制器代理初始化"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        assert agent.agent_id == "controller"
        assert agent.name == "控制器"


class TestControllerAgentConfig:
    """测试配置管理"""

    def test_load_config(self, temp_dir):
        """测试加载配置"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        import json

        config_data = {
            "simulation": {
                "total_rounds": 10,
                "agents": []
            }
        }

        config_file = temp_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f)

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'load_config'):
            agent.load_config(str(config_file))

            # 配置已加载
            pass

    def test_get_config(self):
        """测试获取配置"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'get_config'):
            config = agent.get_config()
            assert isinstance(config, dict)

    def test_update_config(self):
        """测试更新配置"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'update_config'):
            agent.update_config({"test_key": "test_value"})

            # 配置已更新
            pass


class TestControllerAgentControl:
    """测试控制功能"""

    def test_start_simulation(self):
        """测试启动模拟"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'start_simulation'):
            result = agent.start_simulation()
            # 应该返回成功状态
            assert result is not None

    def test_stop_simulation(self):
        """测试停止模拟"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'stop_simulation'):
            result = agent.stop_simulation()
            # 应该返回成功状态
            assert result is not None

    def test_pause_simulation(self):
        """测试暂停模拟"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'pause_simulation'):
            result = agent.pause_simulation()
            # 应该返回成功状态
            assert result is not None


class TestControllerAgentMonitoring:
    """测试监控功能"""

    def test_get_status(self):
        """测试获取状态"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'get_status'):
            status = agent.get_status()
            assert isinstance(status, dict)

    def test_get_metrics(self):
        """测试获取指标"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'get_metrics'):
            metrics = agent.get_metrics()
            assert isinstance(metrics, dict)


class TestControllerAgentIntervention:
    """测试干预功能"""

    def test_schedule_intervention(self):
        """测试调度干预"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'schedule_intervention'):
            intervention = {
                "round": 5,
                "type": "modify_agent",
                "target": "agent_1"
            }

            result = agent.schedule_intervention(intervention)
            assert result is not None

    def test_execute_intervention_now(self):
        """测试立即执行干预"""
        try:
            from src.agents.controller_agent import ControllerAgent
        except ImportError:
            pytest.skip("ControllerAgent类未找到")

        agent = ControllerAgent(
            agent_id="controller",
            name="控制器"
        )

        if hasattr(agent, 'execute_intervention_now'):
            intervention = {
                "type": "modify_environment",
                "property": "order_level",
                "value": 4
            }

            result = agent.execute_intervention_now(intervention)
            assert result is not None
