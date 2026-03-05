"""
模拟控制API集成测试

测试模拟相关的API端点：
- POST /api/v1/simulation/start
- POST /api/v1/simulation/pause
- POST /api/v1/simulation/resume
- POST /api/v1/simulation/stop
- GET /api/v1/simulation/status
"""
import pytest
from unittest.mock import Mock, AsyncMock


@pytest.mark.integration
class TestSimulationAPI:
    """模拟控制API测试"""

    def test_start_simulation(self, mock_async_client):
        """测试启动模拟API"""
        response = mock_async_client.post("/api/v1/simulation/start", json={
            "total_rounds": 10,
            "agents": []
        })

        assert response.status_code == 200

    def test_pause_simulation(self, mock_async_client):
        """测试暂停模拟API"""
        response = mock_async_client.post("/api/v1/simulation/pause")

        assert response.status_code == 200

    def test_resume_simulation(self, mock_async_client):
        """测试恢复模拟API"""
        response = mock_async_client.post("/api/v1/simulation/resume")

        assert response.status_code == 200

    def test_stop_simulation(self, mock_async_client):
        """测试停止模拟API"""
        response = mock_async_client.post("/api/v1/simulation/stop")

        assert response.status_code == 200

    def test_get_simulation_status(self, mock_async_client):
        """测试获取模拟状态API"""
        response = mock_async_client.get("/api/v1/simulation/status")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
