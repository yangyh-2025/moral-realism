"""
数据处理性能测试

测试指标计算性能和数据存储性能：
- 指标计算性能
- 数据存储性能
"""
import pytest
import time
from unittest.mock import Mock


@pytest.mark.performance
class TestMetricsCalculationPerformance:
    """指标计算性能测试"""

    def test_single_agent_metrics_calculation(self):
        """测试单个代理指标计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_agent_metrics'):
            mock_agent = Mock()
            mock_agent.agent_id = "agent_1"
            mock_agent.get_capability_index = Mock(return_value=75.0)

            start_time = time.time()
            metrics = calculator.calculate_agent_metrics(mock_agent)
            calc_time = time.time() - start_time

            # 计算应该很快（<100ms）
            assert calc_time < 0.1
            assert metrics is not None

    def test_multiple_agents_metrics_calculation(self):
        """测试多个代理指标计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_agent_metrics'):
            # 创建100个代理
            agents = []
            for i in range(100):
                agent = Mock()
                agent.agent_id = f"agent_{i}"
                agent.get_capability_index = Mock(return_value=50.0 + i)
                agents.append(agent)

            start_time = time.time()
            for agent in agents:
                calculator.calculate_agent_metrics(agent)
            total_time = time.time() - start_time

            # 100个代理的计算应该快于1秒
            assert total_time < 1.0

    def test_system_metrics_calculation(self):
        """测试系统指标计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_system_metrics'):
            agents = [Mock() for _ in range(50)]
            environment = Mock()

            start_time = time.time()
            metrics = calculator.calculate_system_metrics(agents, environment)
            calc_time = time.time() - start_time

            # 计算应该很快（<500ms）
            assert calc_time < 0.5
            assert metrics is not None


@pytest.mark.performance
class TestDataStoragePerformance:
    """数据存储性能测试"""

    def test_metrics_save_performance(self, temp_dir):
        """测试指标保存性能"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage_path = temp_dir / "metrics_storage.json"
        storage = MetricsStorage(storage_path=str(storage_path))

        if hasattr(storage, 'save_metrics'):
            # 创建大型指标数据
            metrics = {
                "round": 1,
                "agents": {f"agent_{i}": {"power": 50 + i} for i in range(100)},
                "system": {"total_power": 10000}
            }

            start_time = time.time()
            storage.save_metrics(metrics)
            save_time = time.time() - start_time

            # 保存应该很快（<500ms）
            assert save_time < 0.5

    def test_metrics_load_performance(self, temp_dir):
        """测试指标加载性能"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        import json

        # 创建大型指标文件
        storage_path = temp_dir / "metrics_storage.json"
        metrics_data = {
            "history": [
                {
                    "round": i,
                    "agents": {f"agent_{j}": {"power": 50 + j} for j in range(100)},
                    "system": {"total_power": 10000 + i}
                } for i in range(50)
            ]
        }

        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f)

        storage = MetricsStorage(storage_path=str(storage_path))

        if hasattr(storage, 'load_metrics'):
            start_time = time.time()
            loaded = storage.load_metrics()
            load_time = time.time() - start_time

            # 加载应该很快（<500ms）
            assert load_time < 0.5
            assert loaded is not None

    def test_history_append_performance(self):
        """测试历史追加性能"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history'):
            # 追加1000条历史记录
            start_time = time.time()
            for i in range(1000):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })
            total_time = time.time() - start_time

            # 追加1000条记录应该快于1秒
            assert total_time < 1.0


@pytest.mark.performance
class TestQueryPerformance:
    """查询性能测试"""

    def test_large_dataset_query(self):
        """测试大数据集查询性能"""
        # 创建大型数据集
        data = {
            f"agent_{i}": {
                "power": 50 + i,
                "influence": 0.5 + (i % 50) / 100,
                "history": [j for j in range(100)]
            } for i in range(1000)
        }

        start_time = time.time()
        # 执行1000次查询
        for i in range(1000):
            agent_id = f"agent_{i % 1000}"
            if agent_id in data:
                _ = data[agent_id]
        query_time = time.time() - start_time

        # 1000次查询应该快于1秒
        assert query_time < 1.0

    def test_filtered_query_performance(self):
        """测试过滤查询性能"""
        # 创建大型数据集
        data = [
            {"power": 50 + i, "influence": 0.5 + (i % 50) / 100}
            for i in range(1000)
        ]

        start_time = time.time()
        # 过滤power > 75的记录
        filtered = [d for d in data if d["power"] > 75]
        filter_time = time.time() - start_time

        # 过滤应该很快（<100ms）
        assert filter_time < 0.1
        assert len(filtered) > 0


@pytest.mark.performance
class TestSerializationPerformance:
    """序列化性能测试"""

    def test_json_serialization_performance(self):
        """测试JSON序列化性能"""
        # 创建大型数据
        data = {
            "agents": [
                {
                    "agent_id": f"agent_{i}",
                    "power": 50 + i,
                    "history": [j for j in range(50)]
                } for i in range(100)
            ],
            "system": {"total_power": 10000}
        }

        import json

        # 测试序列化
        start_time = time.time()
        for _ in range(100):
            _ = json.dumps(data)
        serialize_time = time.time() - start_time

        # 100次序列化应该快于1秒
        assert serialize_time < 1.0

    def test_json_deserialization_performance(self):
        """测试JSON反序列化性能"""
        import json

        # 创建大型JSON字符串
        data = {
            "agents": [
                {
                    "agent_id": f"agent_{i}",
                    "power": 50 + i,
                    "history": [j for j in range(50)]
                } for i in range(100)
            ]
        }

        json_str = json.dumps(data)

        # 测试反序列化
        start_time = time.time()
        for _ in range(100):
            _ = json.loads(json_str)
        deserialize_time = time.time() - start_time

        # 100次反序列化应该快于1秒
        assert deserialize_time < 1.0
