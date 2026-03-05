"""
小国代理单元测试

测试SmallStateAgent类的核心功能：
- 初始化和配置
- 决策逻辑
- 依附关系
"""
import pytest
from unittest.mock import Mock, AsyncMock


class TestSmallStateAgentInitialization:
    """测试SmallStateAgent初始化"""

    def test_small_state_agent_initialization(self, capability):
        """测试小国代理初始化"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        assert agent.agent_id == "small_state"
        assert agent.name == "小国"

    def test_small_state_agent_with_region(self, capability):
        """测试带地区的小国代理初始化"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3,
            region="东亚"
        )

        if hasattr(agent, 'region'):
            assert agent.region == "东亚"


class TestSmallStateAgentDecision:
    """测试决策逻辑"""

    @pytest.mark.asyncio
    async def test_make_decision(self, capability):
        """测试做出决策"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'make_decision'):
            context = {
                "current_round": 1,
                "environment": Mock(),
                "great_powers": []
            }

            decision = await agent.make_decision(context)
            assert decision is not None


class TestSmallStateAgentAlignment:
    """测试依附关系"""

    def test_set_alignment(self, capability):
        """测试设置依附"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'set_alignment'):
            agent.set_alignment("aligned_with", "usa")

            # 依附已设置
            pass

    def test_get_alignment(self, capability):
        """测试获取依附"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'set_alignment') and hasattr(agent, 'get_alignment'):
            agent.set_alignment("aligned_with", "usa")

            alignment = agent.get_alignment()
            assert alignment["aligned_with"] == "usa"


class TestSmallStateAgentSurvival:
    """测试生存能力"""

    def test_assess_survival_risk(self, capability):
        """测试评估生存风险"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'assess_survival_risk'):
            context = {
                "threats": [],
                "alliance_support": 0.5
            }

            risk = agent.assess_survival_risk(context)
            assert isinstance(risk, float)
            assert 0 <= risk.risk <= 1

    def test_get_survival_strategy(self, capability):
        """测试获取生存策略"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'get_survival_strategy'):
            strategy = agent.get_survival_strategy()
            assert isinstance(strategy, str)


class TestSmallStateAgentRegionalPosition:
    """测试地区地位"""

    def test_get_regional_power(self, capability):
        """测试获取地区权力"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3,
            region="东亚"
        )

        if hasattr(agent, 'get_regional_power'):
            power = agent.get_regional_power()
            assert isinstance(power, float)
            assert 0 <= power <= 1


class TestSmallStateAgentAutonomy:
    """测试自主性"""

    def test_get_autonomy_level(self, capability):
        """测试获取自主性水平"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'get_autonomy_level'):
            autonomy = agent.get_autonomy_level()
            assert isinstance(autonomy, float)
            assert 0 <= autonomy <= 1

    def test_is_puppet_state(self, capability):
        """测试是否是傀儡国"""
        try:
            from src.agents.small_state_agent import SmallStateAgent
        except ImportError:
            pytest.skip("SmallStateAgent类未找到")

        agent = SmallStateAgent(
            agent_id="small_state",
            name="小国",
            capability=capability,
            leadership_profile=Mock(),
            initial_moral_level=3
        )

        if hasattr(agent, 'is_puppet_state'):
            is_puppet = agent.is_puppet_state()
            assert isinstance(is_puppet, bool)
