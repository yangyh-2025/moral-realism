"""
代理管理API集成测试

测试代理相关的API端点：
- GET /api/v1/agents
- GET /api/v1/agents/{agent_id}
- POST /api/v1/agents
- PUT /api/v1/agents/{agent_id}
- DELETE /api/v1/agents/{agent_id}
"""
import pytest


@pytest.mark.integration
class TestAgentsAPI:
    """代理管理API测试"""

    def test_get_agents(self, mock_async_client):
        """测试获取代理列表API"""
        response = mock_async_client.get("/api/v1/agents")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_agent_by_id(self, mock_async_client):
        """测试获取单个代理API"""
        response = mock_async_client.get("/api/v1/agents/agent_1")

        assert response.status_code in [200, 404]  # 200如果存在，404如果不存在

    def test_create_agent(self, mock_async_client):
        """测试创建代理API"""
        agent_data = {
            "agent_id": "new_agent",
            "name": "新代理",
            "type": "great_power"
        }

        response = mock_async_client.post("/api/v1/agents", json=agent_data)

        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == "new_agent"

    def test_update_agent(self, mock_async_client):
        """测试更新代理API"""
        update_data = {
            "name": "更新后的代理",
            "moral_level": 4
        }

        response = mock_async_client.put("/api/v1/agents/agent_1", json=update_data)

        assert response.status_code in [200, 404]

    def test_delete_agent(self, mock_async_client):
        """测试删除代理API"""
        response = mock_async_client.delete("/api/v1/agents/agent_1")

        assert response.status_code in [200, 404]


class TestAgentsAPIValidation:
    """代理API验证测试"""

    def test_create_agent_missing_required_fields(self, mock_async_client):
        """测试创建缺少必填字段的代理"""
        invalid_data = {
            "name": "新代理"
            # 缺少agent_id
        }

        response = mock_async_client.post("/api/v1/agents", json=invalid_data)

        assert response.status_code == 422  # 验证错误

    def test_create_agent_invalid_type(self, mock_async_client):
        """测试创建无效类型的代理"""
        invalid_data = {
            "agent_id": "invalid_agent",
            "name": "无效代理",
            "type": "invalid_type"
        }

        response = mock_async_client.post("/api/v1/agents", json=invalid_data)

        assert response.status_code == 422
