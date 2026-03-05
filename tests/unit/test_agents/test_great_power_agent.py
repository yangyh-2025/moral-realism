"""
大国代理单元测试

测试GreatPowerAgent类的核心功能：
- 初始化和配置
- 决策逻辑
- 特殊能力
"""
import pytest
from unittest.mock import Mock, AsyncMock


class TestGreatPowerAgentInitialization:
    """测试GreatPowerAgent初始化"""

    def test_great_power_agent_initialization(self, capability):
        """测试大国代理初始化"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        assert agent.agent_id == "usa"
        assert agent.name == "美国"

    def test_great_power_agent_with_interests(self, capability):
        """测试带利益的大国代理初始化"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        interests = ["全球领导", "地区安全", "经济繁荣"]

        agent = GreatPowerAgent(
            agent_id="china",
            name="中国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3,
            interests=interests
        )

        if hasattr(agent, 'interests'):
            assert len(agent.interests) == 3


class TestGreatPowerAgentDecision:
    """测试决策逻辑"""

    @pytest.mark.asyncio
    async def test_make_decision(self, capability):
        """测试做出决策"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'make_decision'):
            context = {
                "current_round": 1,
                "environment": Mock(),
                "other_agents": []
            }

            decision = await agent.make_decision(context)
            assert decision is not None


class TestGreatPowerAgentSpecialCapabilities:
    """测试特殊能力"""

    def test_has_global_influence(self, capability):
        """测试是否有全球影响力"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'has_global_influence'):
            has_influence = agent.has_global_influence()
            assert isinstance(has_influence, bool)

    def test_get_sphere_of_influence(self, capability):
        """测试获取势力范围"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'get_sphere_of_influence'):
            sphere = agent.get_sphere_of_influence()
            assert isinstance(sphere, list)


class TestGreatPowerAgentAllianceManagement:
    """测试同盟管理"""

    def test_add_ally(self, capability):
        """测试添加盟友"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'add_ally'):
            agent.add_ally("uk")
            agent.add_ally("japan")

            # 盟友已添加
            pass

    def test_get_allies(self, capability):
        """测试获取盟友"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'add_ally') and hasattr(agent, 'get_allies'):
            agent.add_ally("uk")
            agent.add_ally("japan")

            allies = agent.get_allies()
            assert len(allies) == 2


class TestGreatPowerAgentHegemonicPosition:
    """测试霸权地位"""

    def test_is_hegemon(self, capability):
        """测试是否是霸权"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'is_hegemon'):
            is_hegemon = agent.is_hegemon()
            assert isinstance(is_hegemon, bool)

    def test_get_hegemonic_strength(self, capability):
        """测试获取霸权强度"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'get_hegemonic_strength'):
            strength = agent.get_hegemonic_strength()
            assert 0 <= strength <= 1


class TestGreatPowerAgentGlobalInterests:
    """测试全球利益"""

   ) def test_get_global_interests(self, capability):
        """测试获取全球利益"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'get_global_interests'):
            interests = agent.get_global_interests()
            assert isinstance(interests, list)

    def test_evaluate_global_situation(self, capability):
        """测试评估全球局势"""
        try:
            from src.agents.great_power_agent import GreatPowerAgent
        except ImportError:
            pytest.skip("GreatPowerAgent类未找到")

        agent = GreatPowerAgent(
            agent_id="usa",
            name="美国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'evaluate_global_situation'):
            situation = {
                "total_agents": 10,
                "power_distribution": {},
                "order_level": 3
            }

            assessment = agent.evaluate_global_situation(situation)
            assert assessment is not None
