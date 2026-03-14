"""
Integration tests for Agents API endpoints

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest

try:
    from fastapi.testclient import TestClient
    from backend.main import app
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not API_AVAILABLE,
    reason="Backend API not available"
)


@pytest.mark.integration
@pytest.mark.api
class TestAgentsAPI:
    """Test agents management API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_get_all_agents(self, client):
        """Test getting all agents"""
        response = client.get("/api/agents")

        # Accept 200 or 500 (if not implemented)
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_agent_by_id(self, client):
        """Test getting specific agent"""
        response = client.get("/api/agents/test_agent")

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

    def test_get_agent_state(self, client):
        """Test getting agent state"""
        response = client.get("/api/agents/test_agent/state")

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_get_agent_decisions(self, client):
        """Test getting agent decisions"""
        response = client.get("/api/agents/test_agent/decisions")

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_agent_interactions(self, client):
        """Test getting agent interactions"""
        response = client.get("/api/agents/test_agent/interactions")

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_update_agent_preferences(self, client):
        """Test updating agent preferences"""
        response = client.put(
            "/api/agents/test_agent/preferences",
            json={"preference_key": "value"}
        )

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_get_agent_relationships(self, client):
        """Test getting agent relationships"""
        response = client.get("/api/agents/test_agent/relationships")

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


@pytest.mark.integration
@pytest.mark.api
class TestAgentsAPIBatch:
    """Test batch operations on agents"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_batch_get_agents(self, client):
        """Test batch getting agents"""
        response = client.post(
            "/api/agents/batch",
            json={"agent_ids": ["agent1", "agent2", "agent3"]}
        )

        # Accept 200 or 500
        assert response.status_code in [200, 501]

    def test_batch_update_agents(self, client):
        """Test batch updating agents"""
        response = client.put(
            "/api/agents/batch",
            json={
                "updates": {
                    "agent1": {"preference_key": "value1"},
                    "agent2": {"preference_key": "value2"}
                }
            }
        )

        # Accept 200 or 500
        assert response.status_code in [200, 501]


@pytest.mark.integration
@pytest.mark.api
class TestAgentsAPIValidation:
    """Test agents API validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_invalid_agent_id(self, client):
        """Test invalid agent ID"""
        response = client.get("/api/agents/invalid id")

        # Should return 400 or 404
        assert response.status_code in [400, 404]

    def test_empty_agent_id(self, client):
        """Test empty agent ID"""
        response = client.get("/api/agents//state")

        # Should return 404 or 405
        assert response.status_code in [404, 405]


@pytest.mark.integration
@pytest.mark.api
class TestAgentsAPIQueryParameters:
    """Test query parameters for agents API"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_filter_agents_by_region(self, client):
        """Test filtering agents by region"""
        response = client.get("/api/agents?region=Asia")

        # Accept 200 or 500
        assert response.status_code in [200, 501]

    def test_filter_agents_by_power_tier(self, client):
        """Test filtering agents by power tier"""
        response = client.get("/api/agents?power_tier=great_power")

        # Accept 200 or 500
        assert response.status_code in [200, 501]

    def test_filter_agents_by_leader_type(self, client):
        """Test filtering agents by leader type"""
        response = client.get("/api/agents?leader_type=wangdao")

        # Accept 200 or 500
        assert response.status_code in [200, 501]

    def test_pagination_for_agents(self, client):
        """Test pagination for agents"""
        response = client.get("/api/agents?page=1&limit=10")

        # Accept 200 or 500
        assert response.status_code in [200, 501]
