"""
Agent模型单元测试

测试Agent基类的核心功能：
- 初始化和基本属性
- 历史记录管理
- 关系管理
- 能力层级判定
"""
import pytest
from unittest.mock import Mock, patch


class TestAgentBasicProperties:
    """测试Agent基本属性和初始化"""

    def test_agent_initialization(self, hard_power, soft_power, leadership_profile):
        """测试Agent初始化"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        assert agent.agent_id == "test_agent_1"
        assert agent.name == "测试代理"
        assert agent.moral_level == 3
        assert agent.history == []
        assert agent.relationships == {}

    def test_agent_initialization_with_defaults(self):
        """测试Agent初始化使用默认值"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_2",
            name="默认代理",
            capability=Mock(),
            leadership_profile=Mock()
        )

        assert agent.agent_id == "test_agent_2"
        assert agent.name == "默认代理"
        # 默认道德水平应该是一个有效值
        assert 1 <= agent.moral_level <= 5

    def test_agent_str_representation(self, hard_power, soft_power, leadership_profile):
        """测试Agent的字符串表示"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        str_repr = str(agent)
        assert "test_agent_1" in str_repr
        assert "测试代理" in str_repr


class TestAgentHistoryManagement:
    """测试Agent历史记录管理"""

    def test_add_history(self, hard_power, soft_power, leadership_profile):
        """测试添加历史记录"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        # 添加历史记录
        agent.add_history("action", {"test": "data"})

        assert len(agent.history) == 1
        assert agent.history[0]["action_type"] == "action"
        assert agent.history[0]["data"]["test"] == "data"

    def test_add_multiple_history_records(self, hard_power, soft_power, leadership_profile):
        """测试添加多条历史记录"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        # 添加多条记录
        for i in range(5):
            agent.add_history(f"action_{i}", {"index": i})

        assert len(agent.history) == 5
        for i, record in enumerate(agent.history):
            assert record["action_type"] == f"action_{i}"
            assert record["data"]["index"] == i

    def test_get_history(self, hard_power, soft_power, leadership_profile):
        """测试获取历史记录"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        # 添加添加记录
        agent.add_history("action1", {"key": "value1"})
        agent.add_history("action2", {"key": "value2"})

        history = agent.get_history()
        assert len(history) == 2
        assert history[0]["action_type"] == "action1"
        assert history[1]["action_type"] == "action2"

    def test_get_recent_history(self, hard_power, soft_power, leadership_profile):
        """测试获取最近的N条历史记录"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        # 添加多条记录
        for i in range(10):
            agent.add_history(f"action_{i}", {"index": i})

        # 获取最近3条
        recent = agent.get_recent_history(3)
        assert len(recent) == 3
        assert recent[0]["action_type"] == "action_7"
        assert recent[1]["action_type"] == "action_8"
        assert recent[2]["action_type"] == "action_9"

    def test_get_recent_history_exceeds_total(self, hard_power, soft_power, leadership_profile):
        """测试请求数量超过历史记录总数"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        agent.add_history("action", {"data": "test"})

        # 请求10条，但只有1条
        recent = agent.get_recent_history(10)
        assert len(recent) == 1


class TestAgentRelationshipManagement:
    """测试Agent关系管理"""

    def test_set_relationship(self, hard_power, soft_power, leadership_profile):
        """测试设置关系"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        agent.set_relationship("agent_2", "friendly", 0.8)

        assert "agent_2" in agent.relationships
        assert agent.relationships["agent_2"]["type"] == "friendly"
        assert agent.relationships["agent_2"]["strength"] == 0.8

    def test_get_relationship(self, hard_power, soft_power, leadership_profile):
        """测试获取关系"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        agent.set_relationship("agent_2", "friendly", 0.8)

        relationship = agent.get_relationship("agent_2")
        assert relationship["type"] == "friendly"
        assert relationship["strength"] == 0.8

    def test_get_nonexistent_relationship(self, hard_power, soft_power, leadership_profile):
        """测试获取不存在的关系"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        relationship = agent.get_relationship("nonexistent_agent")
        assert relationship is None

    def test_update_relationship(self, hard_power, soft_power, leadership_profile):
        """测试更新现有关系"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        # 设置初始关系
        agent.set_relationship("agent_2", "neutral", 0.5)

        # 更新关系
        agent.set_relationship("agent_2", "hostile", 0.3)

        relationship = agent.get_relationship("agent_2")
        assert relationship["type"] == "hostile"
        assert relationship["strength"] == 0.3

    def test_is_friendly_with(self, hard_power, soft_power, leadership_profile):
        """测试是否友好"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        agent.set_relationship("agent_2", "friendly", 0.7)

        assert agent.is_friendly_with("agent_2") is True
        assert agent.is_friendly_with("nonexistent") is False

    def test_is_hostile_toward(self, hard_power, soft_power, leadership_profile):
        """测试是否敌对"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        agent.set_relationship("agent_2", "hostile", 0.8)

        assert agent.is_hostile_toward("agent_2") is True
        assert agent.is_hostile_toward("nonexistent") is False


class TestAgentCapabilityMethods:
    """测试Agent能力相关方法"""

    def test_get_capability_tier(self, hard_power, soft_power, leadership_profile, capability):
        """测试获取能力层级"""
        from src.models.agent import Agent

        # Mock capability对象
        mock_capability = Mock()
        mock_capability.get_tier = Mock(return_value="T1_GREAT_POWER")

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=mock_capability,
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        tier = agent.get_capability_tier()
        assert tier == "T1_GREAT_POWER"

    def test_get_summary(self, hard_power, soft_power, leadership_profile):
        """测试获取代理摘要"""
        from src.models.agent import Agent

        # Mock capability和leadership
        mock_capability = Mock()
        mock_capability.get_capability_index = Mock(return_value=75.0)
        mock_capability.get_tier = Mock(return_value="T1_GREAT_POWER")

        mock_leadership = Mock()
        mock_leadership.type = "REALIST"
        mock_leadership.name_zh = "现实主义"

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=mock_capability,
            leadership_profile=mock_leadership,
            initial_moral_level=3
        )

        summary = agent.get_summary()
        assert "agent_id" in summary
        assert summary["agent_id"] == "test_agent_1"
        assert summary["name"] == "测试代理"
        assert summary["moral_level"] == 3


class TestAgentMoralLevel:
    """测试Agent道德水平管理"""

    def test_moral_level_initialization(self, hard_power, soft_power, leadership_profile):
        """测试道德水平初始化"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=4
        )

        assert agent.moral_level == 4

    def test_moral_level_boundary(self, hard_power, soft_power, leadership_profile):
        """测试道德水平边界值"""
        from src.models.agent import Agent

        # 最小值
        agent_min = Agent(
            agent_id="test_min",
            name="最小道德",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=1
        )
        assert agent_min.moral_level == 1

        # 最大值
        agent_max = Agent(
            agent_id="test_max",
            name="最大道德",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=5
        )
        assert agent_max.moral_level == 5

    @pytest.mark.parametrize("invalid_level", [-1, 0, 6, 10])
    def test_invalid_moral_level(self, invalid_level, hard_power, soft_power, leadership_profile):
        """测试无效道德水平"""
        from src.models.agent import Agent

        with pytest.raises(ValueError):
            Agent(
                agent_id="test_invalid",
                name="无效道德",
                capability=Mock(),
                leadership_profile=leadership_profile,
                initial_moral_level=invalid_level
            )


class TestAgentStateManagement:
    """测试Agent状态管理"""

    def test_state_dict(self, hard_power, soft_power, leadership_profile):
        """测试获取状态字典"""
        from src.models.agent import Agent

        agent = Agent(
            agent_id="test_agent_1",
            name="测试代理",
            capability=Mock(),
            leadership_profile=leadership_profile,
            initial_moral_level=3
        )

        state = agent.state_dict()
        assert "agent_id" in state
        assert "name" in state
        assert "moral_level" in state
        assert "history" in state
        assert "relationships" in state
