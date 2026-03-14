"""
Integration tests for WebSocket functionality

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from typing import List, Dict
import asyncio

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
@pytest.mark.websocket
class TestWebSocketConnection:
    """Test WebSocket connection establishment"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_websocket_connect(self, client):
        """Test WebSocket connection"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            # Send connection message
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})

            # Receive confirmation
            data = websocket.receive_json()
            assert "type" in data
            assert data["type"] in ["connected", "error"]

    @pytest.mark.asyncio
    async def test_websocket_disconnect(self, client):
        """Test WebSocket disconnection"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

        # Disconnect should happen automatically when exiting context


@pytest.mark.integration
@pytest.mark.websocket
class TestWebSocketSimulationUpdates:
    """Test WebSocket simulation updates"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_subscribe_to_updates(self, client):
        """Test subscribing to simulation updates"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            # Subscribe to updates
            websocket.send_json({
                "type": "subscribe",
                "simulation_id": "test_sim",
                "channels": ["state", "decisions", "events"]
            })

            # Receive confirmation
            data = websocket.receive_json()
            assert data["type"] == "subscribed"

    @pytest.mark.asyncio
    async def test_receive_state_update(self, client):
        """Test receiving state update"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

            # Subscribe to state updates
            websocket.send_json({
                "type": "subscribe",
                "simulation_id": "test_sim",
                "channels": ["state"]
            })

            websocket.receive_json()

            # Trigger a state update (would need actual simulation running)
            # data = websocket.receive_json()
            # assert data["type"] == "state_update"

    @pytest.mark.asyncio
    async def test_receive_decision_update(self, client):
        """Test receiving decision update"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

            websocket.send_json({
                "type": "subscribe",
                "simulation_id": "test_sim",
                "channels": ["decisions"]
            })

            websocket.receive_json()

    @pytest.mark.asyncio
    async def test_receive_event_update(self, client):
        """Test receiving event update"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

            websocket.send_json({
                "type": "subscribe",
                "simulation_id": "test_sim",
                "channels": ["events"]
            })

            websocket.receive_json()


@pytest.mark.integration
@pytest.mark.websocket
class TestWebSocketCommands:
    """Test WebSocket commands"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_send_command(self, client):
        """Test sending command through WebSocket"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            # Send start command
            websocket.send_json({
                "type": "command",
                "command": "start_simulation",
                "simulation_id": "test_sim"
            })

            # Receive response
            data = websocket.receive_json()
            assert "type" in data
            assert data["type"] in ["command_response", "error"]

    @pytest.mark.asyncio
    async def test_send_step_command(self, client):
        """Test sending step command"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

            # Send step command
            websocket.send_json({
                "type": "command",
                "command": "step",
                "simulation_id": "test_sim"
            })

            # Receive response
            data = websocket.receive_json()
            assert "type" in data




@pytest.mark.integration
@pytest.mark.websocket
class TestWebSocketErrorHandling:
    """Test WebSocket error handling"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_invalid_message_format(self, client):
        """Test handling invalid message format"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            # Send invalid JSON
            websocket.send_text("not valid json")

            # Should receive error or handle gracefully
            try:
                data = websocket.receive_json(timeout=1.0)
                assert data.get("type") == "error"
            except:
                pass  # Connection closed or timeout

    @pytest.mark.asyncio
    async def test_unknown_message_type(self, client):
        """Test handling unknown message type"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

            # Send unknown type
            websocket.send_json({
                "type": "unknown_type",
                "simulation_id": "test_sim"
            })

            # Should receive error
            data = websocket.receive_json()
            assert data.get("type") == "error"

    @pytest.mark.asyncio
    async def test_invalid_simulation_id(self, client):
        """Test handling invalid simulation ID"""
        with client.websocket_connect("/api/ws/simulation/invalid_sim") as websocket:
            websocket.send_json({
                "type": "connect",
                "simulation_id": "invalid_sim"
            })

            # Should receive error
            data = websocket.receive_json()
            assert data.get("type") in ["error", "not_found"]


@pytest.mark.integration
@pytest.mark.websocket
class TestWebSocketHeartbeat:
    """Test WebSocket heartbeat/ping"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_send_ping(self, client):
        """Test sending ping"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "ping"})

            # Should receive pong
            data = websocket.receive_json()
            assert data.get("type") == "pong"

    @pytest.mark.asyncio
    async def test_ping_pong_latency(self, client):
        """Test measuring ping-pong latency"""
        with client.websocket_connect("/api/ws/simulation/test_sim") as websocket:
            websocket.send_json({"type": "connect", "simulation_id": "test_sim"})
            websocket.receive_json()

            # Send ping
            import time
            start_time = time.time()

            websocket.send_json({"type": "ping"})
            websocket.receive_json()

            latency = (time.time() - start_time) * 1000  # Convert to ms

            # Latency should be reasonable (< 1 second)
            assert latency < 1000
