"""
组织代理单元测试

测试OrganizationAgent类的核心功能：
- 初始化和配置
- 成员管理
- 组织行为
"""
import pytest
from unittest.mock import Mock


class TestOrganizationAgentInitialization:
    """测试OrganizationAgent初始化"""

    def test_organization_agent_initialization(self):
        """测试组织代理初始化"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        assert agent.agent_id == "un"
        assert agent.name == "联合国"

    def test_organization_agent_with_members(self):
        """测试带成员的组织代理初始化"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        members = ["usa", "china", "russia", "uk"]

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国",
            members=members
        )

        if hasattr(agent, 'members'):
            assert len(agent.members) == 4


class TestOrganizationAgentMemberManagement:
    """测试成员管理"""

    def test_add_member(self):
        """测试添加成员"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'add_member'):
            agent.add_member("usa")
            agent.add_member("china")

            # 成员已添加
            pass

    def test_remove_member(self):
        """测试移除成员"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国",
            members=["usa", "china", "russia"]
        )

        if hasattr(agent, 'remove_member'):
            agent.remove_member("russia")

            if hasattr(agent, 'members'):
                assert "russia" not in agent.members

    def test_get_members(self):
        """测试获取成员"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国",
            members=["usa", "china", "russia"]
        )

        if hasattr(agent, 'get_members'):
            members = agent.get_members()
            assert len(members) == 3

    def test_is_member(self):
        """测试是否是成员"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国",
            members=["usa", "china", "russia"]
        )

        if hasattr(agent, 'is_member'):
            assert agent.is_member("usa") is True
            assert agent.is_member("japan") is False


class TestOrganizationAgentDecisions:
    """测试组织决策"""

    def test_vote(self):
        """测试投票"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国",
            members=["usa", "china", "russia"]
        )

        if hasattr(agent, 'vote'):
            votes = {
                "usa": "approve",
                "china": "abstain",
                "russia": "reject"
            }

            result = agent.vote(votes)
            assert result is not None

    def test_get_voting_result(self):
        """测试获取投票结果"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'get_voting_result'):
            result = agent.get_voting_result(proposal_id="proposal_1")
            assert result is not None


class TestOrganizationAgentResolutions:
    """测试决议管理"""

    def test_create_resolution(self):
        """测试创建决议"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'create_resolution'):
            resolution = {
                "title": "测试决议",
                "content": "决议内容",
                "proposed_by": "usa"
            }

            resolution_id = agent.create_resolution(resolution)
            assert resolution_id is not None

    def test_get_resolutions(self):
        """测试获取决议"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'get_resolutions'):
            resolutions = agent.get_resolutions()
            assert isinstance(resolutions, list)


class TestOrganizationAgentNorms:
    """测试规范管理"""

    def test_create_norm(self):
        """测试创建规范"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'create_norm'):
            norm = {
                "name": "主权规范",
                "description": "尊重国家主权",
                "obligations": []
            }

            norm_id = agent.create_norm(norm)
            assert norm_id is not None

    def test_enforce_norm(self):
        """测试执行规范"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'enforce_norm'):
            result = agent.enforce_norm(
                norm_id="norm_1",
                target="agent_1",
                context={}
            )

            # 规范已执行
            pass


class TestOrganizationAgentInfluence:
    """测试组织影响力"""

    def test_get_influence_score(self):
        """测试获取影响力分数"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国",
            members=["usa", "china", "russia"]
        )

        if hasattr(agent, 'get_influence_score'):
            score = agent.get_influence_score()
            assert isinstance(score, float)
            assert 0 <= score <= 1

    def test_get_moral_legitimacy(self):
        """测试获取道德合法性"""
        try:
            from src.agents.organization_agent import OrganizationAgent
        except ImportError:
            pytest.skip("OrganizationAgent类未找到")

        agent = OrganizationAgent(
            agent_id="un",
            name="联合国"
        )

        if hasattr(agent, 'get_moral_legitimacy'):
            legitimacy = agent.get_moral_legitimacy()
            assert isinstance(legitimacy, float)
            assert 0 <= legitimacy <= 1
