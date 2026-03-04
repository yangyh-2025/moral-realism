
import pytest
from src.models.agent import AgentType
from src.models.leadership_type import LeadershipType
from src.agents.great_power_agent import GreatPowerAgent

class TestGreatPowerAgent:
    def test_initialization(self):
        agent = GreatPowerAgent(
            agent_id='gp1',
            name='Great Power 1',
            name_zh='大国1',
            agent_type=AgentType.GREAT_POWER,
            leadership_type=LeadershipType.WANGDAO,
        )
        assert agent.agent_id == 'gp1'
        assert agent.agent_type == AgentType.GREAT_POWER
        assert agent.leadership_type == LeadershipType.WANGDAO
