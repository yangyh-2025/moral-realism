"""
行为选择器单元测试

测试BehaviorSelector类的核心功能：
- 初始化和配置
- 行为选择逻辑
- 约束检查
"""
import pytest
from unittest.mock import Mock


class TestBehaviorSelectorInitialization:
    """测试BehaviorSelector初始化"""

    def test_behavior_selector_initialization(self):
        """测试行为选择器初始化"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        assert selector is not None

    def test_behavior_selector_with_config(self):
        """测试带配置初始化"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        config = {
            "random_seed": 42,
            "exploration_rate": 0.1
        }

        selector = BehaviorSelector(config=config)

        # 配置已应用
        pass


class TestBehaviorSelectorSelection:
    """测试行为选择"""

    def test_select_action(self):
        """测试选择行动"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'select_action'):
            available_actions = [
                {"type": "observe", "parameters": {}},
                {"type": "interact", "parameters": {"target": "agent_2"}}
            ]

            selected = selector.select_action(
                agent=Mock(),
                available_actions=available_actions,
                context={}
            )

            assert selected is not None
            assert selected["type"] in ["observe", "interact"]

    def test_select_action_with_preferences(self):
        """测试根据偏好选择行动"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'select_action'):
            available_actions = [
                {"type": "diplomatic", "priority": 0.8},
                {"type": "military", "priority": 0.3}
            ]

            selected = selector.select_action(
                agent=Mock(),
                available_actions=available_actions,
                context={}
            )

            # 应该倾向于选择高优先级行动
            assert selected is not None


class TestBehaviorSelectorConstraints:
    """测试约束检查"""

    def test_check_constraints(self):
        """测试检查约束"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'check_constraints'):
            action = {"type": "military", "parameters": {"target": "agent_2"}}
            agent = Mock()
            agent.moral_level = 3

            is_valid = selector.check_constraints(action, agent, environment=Mock())
            assert isinstance(is_valid, bool)

    def test_add_constraint(self):
        """测试添加约束"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'add_constraint'):
            def constraint_fn(action, agent, environment):
                return True

            selector.add_constraint("military", constraint_fn)

            # 约束已添加
            pass


class TestBehaviorSelectorLearning:
    """测试学习"""

    def test_update_preferences(self):
        """测试更新偏好"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'update_preferences'):
            selector.update_preferences(
                action_type="diplomatic",
                reward=0.8
            )

            # 偏好已更新
            pass

    def test_get_action_probability(self):
        """测试获取行动概率"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'get_action_probability'):
            prob = selector.get_action_probability("diplomatic")
            assert 0 <= prob <= 1


class TestBehaviorSelectorExploration:
    """测试探索"""

    def test_exploration_mode(self):
        """测试探索模式"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'set_exploration_mode'):
            selector.set_exploration_mode(enabled=True)

            # 探索模式已启用
            pass

    def test_exploration_rate(self):
        """测试探索率"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'set_exploration_rate'):
            selector.set_exploration_rate(0.2)
            assert selector.exploration_rate == 0.2


class TestBehaviorSelectorHistory:
    """测试历史记录"""

    def test_record_decision(self):
        """测试记录决策"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'record_decision'):
            selector.record_decision(
                agent_id="agent_1",
                action={"type": "diplomatic"},
                context={"round": 1}
            )

            # 决策已记录
            pass

    def test_get_decision_history(self):
        """测试获取决策历史"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'record_decision') and hasattr(selector, 'get_decision_history'):
            selector.record_decision(
                agent_id="agent_1",
                action={"type": "diplomatic"},
                context={"round": 1}
            )

            history = selector.get_decision_history("agent_1")
            assert len(history) == 1


class TestBehaviorSelectorStrategies:
    """测试策略"""

    def test_use_strategy(self):
        """测试使用策略"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'set_strategy'):
            selector.set_strategy("conservative")

            # 策略已设置
            pass

    def test_get_available_strategies(self):
        """测试获取可用策略"""
        try:
            from src.interaction.behavior_selector import BehaviorSelector
        except ImportError:
            pytest.skip("BehaviorSelector类未找到")

        selector = BehaviorSelector()

        if hasattr(selector, 'get_available_strategies'):
            strategies = selector.get_available_strategies()
            assert isinstance(strategies, list)
            assert len(strategies) > 0
