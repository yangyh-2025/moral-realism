"""
检查点管理API集成测试

测试检查点相关的API端点：
- POST /api/v1/checkpoints/save
- GET /api/v1/checkpoints/list
- POST /api/v1/checkpoints/load/{checkpoint_id}
"""
import pytest


@pytest.mark.integration
class TestCheckpointsAPI:
    """检查点API测试"""

    def test_save_checkpoint(self, mock_async_client):
        """测试保存检查点API"""
        response = mock_async_client.post("/api/v1/checkpoints/save", json={
            "description": "测试检查点"
        })

        assert response.status_code == 200
        data = response.json()
        assert "checkpoint_id" in data

    def test_list_checkpoints(self, mock_async_client):
        """测试列出检查点API"""
        response = mock_async_client.get("/api/v1/checkpoints/list")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_load_checkpoint(self, mock_async_client):
        """测试加载检查点API"""
        response = mock_async_client.post("/api/v1/checkpoints/load/test_checkpoint_1")

        assert response.status_code in [200, 404]  # 200如果存在，404如果不存在

    def test_delete_checkpoint(self, mock_async_client):
        """测试删除检查点API"""
        response = mock_async_client.delete("/api/v1/checkpoints/test_checkpoint_1")

        assert response.status_code in [200, 404]


class TestCheckpointsAPIValidation:
    """检查点API验证测试"""

    def test_save_checkpoint_without_description(self, mock_async_client):
        """测试保存不带描述的检查点"""
        response = mock_async_client.post("/api/v1/checkpoints/save", json={})

        # 应该成功（描述可能可选）
        assert response.status_code in [200, 422]
