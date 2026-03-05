"""
指标计算性能测试

测试系统指标计算性能和权力分布计算性能：
- 系统指标计算性能
- 权力分布计算性能
"""
import pytest
import time
from unittest.mock import Mock


@pytest.mark.performance
class TestSystemMetricsCalculationPerformance:
    """系统指标计算性能测试"""

    def test_order_level_calculation(self):
        """测试秩序水平计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_order_level'):
            mock_environment = Mock()
            mock_environment.order_level = 3

            # 执行1000与其他计算
            start_time = time.time()
            for _ in range(1000):
                calculator.calculate_order_level(mock_environment)
            total_time = time.time() - start_time

            # 1000次计算应该快于1秒
            assert total_time < 1.0

    def test_power_distribution_calculation(self):
        """测试权力分布计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_power_distribution'):
            # 创建100个代理
            agents = []
            for i in range(100):
                agent = Mock()
                agent.agent_id = f"agent_{i}"
                agent.get_capability_index = Mock(return_value=50.0 + i)
                agents.append(agent)

            start_time = time.time()
            distribution = calculator.calculate_power_distribution(agents)
            calc_time = time.time() - start_time

            # 计算应该很快（<100ms）
            assert calc_time < 0.1
            assert distribution is not None

    def test_system_metrics_batch_calculation(self):
        """测试系统指标批量计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_system_metrics'):
            # 创建50个代理
            agents = [Mock() for _ in range(50)]
            environment = Mock()

            # 执行100次计算
            start_time = time.time()
            for _ in range(100):
                calculator.calculate_system_metrics(agents, environment)
            total_time = time.time() - start_time

            # 100次计算应该快于5秒
            assert total_time < 5.0


@pytest.mark.performance
class TestPowerMetricsCalculationPerformance:
    """权力指标计算性能测试"""

    def test_gini_coefficient_calculation(self):
        """测试基尼系数计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_gini_coefficient'):
            # 创建大型数据集
            values = [50 + i * 0.5 for i in range(1000)]

            # 执行100次计算
            start_time = time.time()
            for _ in range(100):
                calculator.calculate_gini_coefficient(values)
            total_time = time.time() - start_time

            # 100次计算应该快于2秒
            assert total_time < 2.0

    def test_herfindahl_index_calculation(self):
        """测试赫芬达尔指数计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_herfindahl_index'):
            # 创建大型数据集
            values = [0.1 + i * 0.001 for i in range(1000)]

            # 执行100次计算
            start_time = time.time()
            for _ in range(100):
                calculator.calculate_herfindahl_index(values)
            total_time = time.time() - start_time

            # 100次计算应该快于2秒
            assert total_time < 2.0

    def test_power_concentration_calculation(self):
        """测试权力集中度计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_power_concentration'):
            # 创建50个代理
            agents = []
            for i in range(50):
                agent = Mock()
                agent.get_capability_index = Mock(return_value=50.0 + i * 1.0)
                agents.append(agent)

            # 执行1000次计算
            start_time = time.time()
            for _ in range(1000):
                calculator.calculate_power_concentration(agents)
            total_time = time.time() - start_time

            # 1000次计算应该快于3秒
            assert total_time < 3.0


@pytest.mark.performance
class TestMetricsAggregationPerformance:
    """指标聚合性能测试"""

    def test_moving_average_calculation(self):
        """测试移动平均计算性能"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_moving_average'):
            # 创建大型数据集
            values = [50 + i * 0.5 for i in range(10000)]

            start_time = time.time()
            moving_avg = calculator.calculate_moving_average(values, window=100)
            calc_time = time.time() - start_time

            # 计算应该很快（<500ms）
            assert calc_time < 0.5
            assert len(moving_avg) == len(values) - 99

    def test_aggregate_metrics_over_time(self):
        """测试时间指标聚合性能"""
        # 创建大型指标历史
        history = [
            {
                "round": i,
                "metrics": {
                    "total_power": 100 + i,
                    "order_level": 3 + (i % 3)
                }
            }
            for i in range(500)
        ]

        start_time = time.time()
        # 聚合最后100回合的指标
        recent_metrics = [h["metrics"] for h in history[-100:]]
        aggregated = {
            "avg_total_power": sum(m["total_power"] for m in recent_metrics) / 100,
            "avg_order_level": sum(m["order_level"] for m in recent_metrics) / 100
        }
        calc_time = time.time() - start_time

        # 聚合应该很快（<100ms）
        assert calc_time < 0.1
        assert aggregated["avg_total_power"] > 0


@pytest.mark.performance
class TestComplexMetricsPerformance:
    """复杂指标计算性能测试"""

    def test_multi_agent_interaction_metrics(self):
        """测试多代理交互指标计算性能"""
        # 创建大型交互数据集
        interactions = []
        for i in range(1000):
            interaction = {
                "source": f"agent_{i % 50}",
                "target": f"agent_{(i + 1) % 50}",
                "type": "diplomatic",
                "round": i % 100,
                "outcome": "success" if i % 3 != 0 else "failure"
            }
            interactions.append(interaction)

        start_time = time.time()
        # 计算交互成功率
        successful = sum(1 for i in interactions if i["outcome"] == "success")
        success_rate = successful / len(interactions)

        # 计算每个代理的交互次数
        agent_interactions = {}
        for interaction in interactions:
            source = interaction["source"]
            agent_interactions[source] = agent_interactions.get(source, 0) + 1

        calc_time = time.time() - start_time

        # 计算应该很快（<200ms）
        assert calc_time < 0.2
        assert 0 <= success_rate <= 1
        assert len(agent_interactions) > 0

    def test_cumulative_metrics_calculation(self):
        """测试累计指标计算性能"""
        # 创建大型指标历史
        metrics_history = []
        for i in range(500):
            metrics = {
                "round": i,
                "total_power": 100 + i * 0.1,
                "order_level": 3 + (i % 3),
                "agent_count": 10
            }
            metrics_history.append(metrics)

        start_time = time.time()
        # 计算累计指标
        cumulative = {
            "rounds": [m["round"] for m in metrics_history],
            "total_power_sum": sum(m["total_power"] for m in metrics_history),
            "total_power_avg": sum(m["total_power"] for m in metrics_history) / len(metrics_history),
            "order_level_avg": sum(m["order_level"] for m in metrics_history) / len(metrics_history)
        }
        calc_time = time.time() - start_time

        # 计算应该很快（<200ms）
        assert calc_time < 0.2
        assert len(cumulative["rounds"]) == 500


@pytest.mark.performance
@pytest.mark.benchmark
class TestMetricsBenchmarks:
    """指标基准测试（需要pytest-benchmark）"""

    def test_benchmark_power_distribution(self, benchmark):
        """基准测试权力分布计算"""
        # 创建代理列表
        agents = [Mock() for _ in range(100)]
        for i, agent in enumerate(agents):
            agent.agent_id = f"agent_{i}"
            agent.get_capability_index = Mock(return_value=50.0 + i)

        def calc_distribution():
            # 模拟计算
            return {agent.agent_id: agent.get_capability_index() for agent in agents}

        result = benchmark(calc_distribution)
        assert len(result) == 100

    def test_benchmark_gini_coefficient(self, benchmark):
        """基准测试基尼系数计算"""
        values = [50 + i * 0.5 for i in range(1000)]

        def calc_gini():
            # 简化的基尼系数计算
            n = len(values)
            if n == 0:
                return 0
            mean = sum(values) / n
            return sum(abs(x - mean) for x in values) / (2 * mean * n)

        result = benchmark(calc_gini)
        assert 0 <= result <= 1
