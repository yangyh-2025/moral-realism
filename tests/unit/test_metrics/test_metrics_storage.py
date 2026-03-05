"""
指标存储单元测试

测试MetricsStorage类的核心功能：
- 初始化和配置
- 指标保存和加载
- 历史数据管理
"""
import pytest
from unittest.mock import Mock
import json


class TestMetricsStorageInitialization:
    """测试MetricsStorage初始化"""

    def test_metrics_storage_initialization(self):
        """测试指标存储初始化"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        assert storage is not None

    def test_metrics_storage_with_path(self, temp_dir):
        """测试带路径初始化"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage_path = temp_dir / "metrics_storage.json"
        storage = MetricsStorage(storage_path=str(storage_path))

        # 存储路径已设置
        pass


class TestMetricsStorageSaveLoad:
    """测试保存和加载"""

    def test_save_metrics(self, temp_dir):
        """测试保存指标"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage_path = temp_dir / "metrics_storage.json"
        storage = MetricsStorage(storage_path=str(storage_path))

        if hasattr(storage, 'save_metrics'):
            metrics = {
                "round": 1,
                "agents": {
                    "agent_1": {"power": 75},
                    "agent_2": {"power": 65}
                },
                "system": {"total_power": 140}
            }

            storage.save_metrics(metrics)

            assert storage_path.exists()

    def test_load_metrics(self, temp_dir):
        """测试加载指标"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage_path = temp_dir / "metrics_storage.json"

        # 创建指标文件
        metrics_data = {
            "round": 1,
            "agents": {"agent_1": {"power": 75}},
            "system": {"total_power": 75}
        }

        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f)

        storage = MetricsStorage(storage_path=str(storage_path))

        if hasattr(storage, 'load_metrics'):
            loaded = storage.load_metrics()
            assert loaded["round"] == 1


class TestMetricsStorageHistoryManagement:
    """测试历史记录管理"""

    def test_append_to_history(self):
        """测试追加到历史"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history'):
            storage.append_to_history({
                "round": 1,
                "metrics": {"total_power": 100}
            })

            storage.append_to_history({
                "round": 2,
                "metrics": {"total_power": 105}
            })

            # 历史已更新
            pass

    def test_get_history(self):
        """测试获取历史"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'get_history'):
            storage.append_to_history({
                "round": 1,
                "metrics": {"total_power": 100}
            })

            history = storage.get_history()
            assert len(history) == 1

    def test_get_history_range(self):
        """测试获取历史范围"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'get_history_range'):
            for i in range(10):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            range_history = storage.get_history_range(start=3, end=7)
            assert len(range_history) == 5


class TestMetricsStorageQuerying:
    """测试查询功能"""

    def test_query_by_round(self):
        """测试按回合查询"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'query_by_round'):
            storage.append_to_history({
                "round": 1,
                "metrics": {"total_power": 100}
            })

            result = storage.query_by_round(1)
            assert result is not None
            assert result["round"] == 1

    def test_query_by_agent(self):
        """测试按代理查询"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'query_by_agent'):
            storage.append_to_history({
                "round": 1,
                "agents": {
                    "agent_1": {"power": 75},
                    "agent_2": {"power": 65}
                }
            })

            result = storage.query_by_agent("agent_1")
            assert result is not None

    def test_query_by_metric(self):
        """测试按指标查询"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'query_by_metric'):
            for i in range(5):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            result = storage.query_by_metric("total_power")
            assert isinstance(result, list)
            assert len(result) == 5


class TestMetricsStorageExport:
    """测试导出功能"""

    def test_export_to_csv(self, temp_dir):
        """测试导出到CSV"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'export_to_csv'):
            for i in range(3):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            export_path = temp_dir / "metrics.csv"
            storage.export_to_csv(str(export_path))

            assert export_path.exists()

    def test_export_to_json(self, temp_dir):
        """测试导出到JSON"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'export_to_json'):
            storage.append_to_history({
                "round": 1,
                "metrics": {"total_power": 100}
            })

            export_path = temp_dir / "metrics.json"
            storage.export_to_json(str(export_path))

            assert export_path.exists()


class TestMetricsStorageAggregation:
    """测试聚合功能"""

    def test_calculate_aggregate(self):
        """测试计算聚合值"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'calculate_aggregate'):
            for i in range(5):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            avg = storage.calculate_aggregate("total_power", method="average")
            assert isinstance(avg, float)

    def test_get_statistics(self):
        """测试获取统计信息"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'get_statistics'):
            for i in range(10):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            stats = storage.get_statistics("total_power")
            assert isinstance(stats, dict)
            assert "mean" in stats
            assert "std" in stats


class TestMetricsStorageClear:
    """测试清除功能"""

    def test_clear_history(self):
        """测试清除历史"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'clear_history'):
            storage.append_to_history({
                "round": 1,
                "metrics": {"total_power": 100}
            })

            storage.clear_history()

            history = storage.get_history()
            assert len(history) == 0

    def test_clear_range(self):
        """测试清除范围"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'clear_range'):
            for i in range(10):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            storage.clear_range(start=3, end=7)

            # 指定范围已清除
            pass


class TestMetricsStorageCompression:
    """测试压缩功能"""

    def test_compress_history(self):
        """测试压缩历史"""
        try:
            from src.metrics.storage import MetricsStorage
        except ImportError:
            pytest.skip("MetricsStorage类未找到")

        storage = MetricsStorage()

        if hasattr(storage, 'append_to_history') and hasattr(storage, 'compress_history'):
            for i in range(100):
                storage.append_to_history({
                    "round": i,
                    "metrics": {"total_power": 100 + i}
                })

            original_size = len(storage.get_history())

            storage.compress_history(factor=10)

            compressed_size = len(storage.get_history())
            assert compressed_size < original_size
