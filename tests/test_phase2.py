
import pytest
from src.models.agent import AgentType
from src.models.leadership_type import LeadershipType
from src.agents.great_power_agent import GreatPowerAgent, Commitment
from src.agents.small_state_agent import SmallStateAgent, StrategicStance
from src.agents.organization_agent import OrganizationAgent, OrganizationType, DecisionRule
from src.agents.controller_agent import ControllerAgent, SimulationConfig, ControllerState

class TestGreatPowerAgent:
    def test_initialization(self):
        agent = GreatPowerAgent(
            agent_id="gp1",
            name="Great Power 1",
            name_zh="大国1",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.WANGDAO,
        )
        assert agent.agent_id == "gp1"
        assert agent.agent_type == AgentType.GREAT_POWER

    def test_commitment_management(self):
        agent = GreatPowerAgent(
            agent_id="gp1",
            name="Great Power 1",
            name_zh="大国1",
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.WANGDAO,
        )
        commitment = Commitment(commitment_id="c1", description="Test", start_round=1)
        agent.commitments.append(commitment)
        assert len(agent.get_active_commitments()) == 1

class TestSmallStateAgent:
    def test_initialization(self):
        agent = SmallStateAgent(
            agent_id="ss1",
            name="Small State 1",
            name_zh="小国1",
            agent_type=AgentType.SMALL_STATE,
            leadership_type=LeadershipType.HUNYONG,
        )
        assert agent.agent_id == "ss1"
        assert agent.agent_type == AgentType.SMALL_STATE

class TestOrganizationAgent:
    def test_initialization(self):
        agent = OrganizationAgent(
            agent_id="org1",
            name="Test Org",
            name_zh="测试组织",
            agent_type=AgentType.ORGANIZATION,
            leadership_type=LeadershipType.HEGEMON,
            org_type=OrganizationType.GLOBAL,
        )
        assert agent.agent_id == "org1"
        assert agent.agent_type == AgentType.ORGANIZATION

    def test_member_management(self):
        agent = OrganizationAgent(
            agent_id="org1",
            name="Test Org",
            name_zh="测试组织",
            agent_type=AgentType.ORGANIZATION,
            leadership_type=LeadershipType.HEGEMON,
            org_type=OrganizationType.GLOBAL,
        )
        agent.add_member("gp1", is_great_power=True)
        agent.add_member("ss1", is_great_power=False)
        assert "gp1" in agent.great_power_members
        assert "ss1" in agent.member_ids

class TestControllerAgent:
    def test_initialization(self):
        config = SimulationConfig(max_rounds=50)
        controller = ControllerAgent(
            agent_id="controller",
            name="Controller",
            name_zh="控制器",
            agent_type=AgentType.CONTROLLER,
            leadership_type=LeadershipType.HEGEMON,
            config=config,
        )
        assert controller.agent_id == "controller"
        assert controller.agent_type == AgentType.CONTROLLER
        assert controller.config.max_rounds == 50

    def test_simulation_config_defaults(self):
        config = SimulationConfig()
        assert config.max_rounds == 100
        assert config.event_probability == 0.2

    def test_controller_state_defaults(self):
        state = ControllerState()
        assert state.current_round == 0
        assert state.is_running is False
        assert state.is_paused is False
