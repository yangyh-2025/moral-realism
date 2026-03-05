"""
指标查询API集成测试

测试指标相关的API端点：
- GET /api/v1/metrics/current
- GET /api/v1/metrics/history
- GET /api/v1/metrics/system
"""
import pytest


@pytest.mark.integration
class TestMetricsAPI:
    """指标API测试"""

    def test_get_current_metrics(self, mock_async_client):
        """测试获取当前指标API"""
        response = mock_async_client.get("/api/v1/metrics/current")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_metrics_history(self, mock_async_client):
        """测试获取指标历史API"""
        response = mock_async_client.get("/api/v1/metrics/history?rounds=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_system_metrics(self, mock_async_client):
        """测试获取系统指标API"""
        response = mock_async_client.get("/api/v1/metrics/system")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_agent_metrics(self, mock_async_client):
        """测试获取代理指标API"""
        response = mock_async_client.get("/api/v1/metrics/agents/agent_1")

        assert response.status_code in [200, 404]  # 200如果存在，404如果不存在


class TestMetricsAPIFilters:
    """指标API过滤测试"""

    def test_filter_by_round_range(self, mock_async_client):
        """测试按回合范围过滤"""
        response = mock_async_client.get("/api/v1/metrics/history?start=5&end=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filter_by_metric_type(self, mock_async_client):
        """测试按指标类型过滤"""
        response = mock_async_client.get("/api/v1/metrics/current?types=power,influence")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
