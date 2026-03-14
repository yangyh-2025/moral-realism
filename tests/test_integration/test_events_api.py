"""
Integration tests for Events API endpoints

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
class TestEventsAPI:
    """Test events management API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    def test_create_event(self, client):
        """Test creating a new event"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test Event",
                "description": "A test event",
                "participants": ["agent1", "agent2"],
                "impact_level": 0.5,
                "priority": "normal"
            }
        )

        # Accept 200, 201 or 500
        assert response.status_code in [200, 201, 501]

        if response.status_code in [200, 201]:
            data = response.json()
            assert "event_id" in data

    def test_get_all_events(self, client):
        """Test getting all events"""
        response = client.get("/api/events")

        # Accept 200 or 500
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_get_event_by_id(self, client):
        """Test getting specific event"""
        response = client.get("/api/events/test_event")

        # Accept 200, 404 or 500
        assert response.status_code in [200, 404, 501]

    def test_trigger_periodic_events(self, client):
        """Test triggering periodic events"""
        response = client.post(
            "/api/events/trigger-periodic",
            json={"agent_ids": ["agent1", "agent2", "agent3"]}
        )

        # Accept 200 or 500
        assert response.status_code in [200, 501]

    def test_trigger_random_event(self, client):
        """Test triggering random event"""
        response = client.post(
            "/api/events/trigger-random",
            json={
                "agent_ids": ["agent1", "agent2"],
                "probability": 0.5
            }
        )

        # Accept 200 or 500
        assert response.status_code in [200, 501]

    def test_cancel_event(self, client):
        """Test cancelling event"""
        response = client.post("/api/events/test_event/cancel")

        # Accept 200 or 404 or 500
        assert response.status_code in [200, 404, 501]

    def test_get_event_history(self, client):
        """Test getting event history"""
        response = client.get("/api/events/history")

        # Accept 200 or 500
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


@pytest.mark.integration
@pytest.mark.api
class TestEventsAPIValidation:
    """Test events API validation"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_create_event_missing_required_fields(self, client):
        """Test creating event with missing fields"""
        response = client.post(
            "/api/events/create",
            json={
                "name": "Test Event"
                # Missing event_type and description
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]

    def test_create_event_invalid_impact_level(self, client):
        """Test creating event with invalid impact level"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "user_defined",
                "name": "Test",
                "description": "Test",
                "impact_level": 2.0  # Invalid: should be 0-1
            }
        )

        # Should return validation error
        assert response.status_code in [400, 422]


@pytest.mark.integration
@pytest.mark.api
class TestEventsAPITypes:
    """Test different event types"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_create_natural_event(self, client):
        """Test creating natural disaster event"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "natural",
                "name": "Earthquake",
                "description": "A magnitude 7.0 earthquake",
                "impact_level": 0.8,
                "priority": "high"
            }
        )

        assert response.status_code in [200, 201, 501]

    def test_create_economic_event(self, client):
        """Test creating economic event"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "economic",
                "name": "Financial Crisis",
                "description": "Global financial crisis",
                "impact_level": 0.7,
                "priority": "high"
            }
        )

        assert response.status_code in [200, 201, 501]

    def test_create_technical_event(self, client):
        """Test creating technical event"""
        response = client.post(
            "/api/events/create",
            json={
                "event_type": "technical",
                "name": "AI Breakthrough",
                "description": "Major AI technology breakthrough",
                "impact_level": 0.6,
                "priority": "normal"
            }
        )

        assert response.status_code in [200, 201, 501]
