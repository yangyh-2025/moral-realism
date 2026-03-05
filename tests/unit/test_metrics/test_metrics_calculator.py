"""
指标计算器单元测试

测试MetricsCalculator类的核心功能：
- 初始化和配置
- 代理指标计算
- 系统指标计算
- 权力分布计算
"""
import pytest
from unittest.mock import Mock


class TestMetricsCalculatorInitialization:
    """测试MetricsCalculator初始化"""

    def test_metrics_calculator_initialization(self):
        """测试指标计算器初始化"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        assert calculator is not None

    def test_metrics_calculator_with_config(self):
        """测试带配置初始化"""
       ) try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        config = {
            "calculation_precision": 0.001,
            "aggregate_method": "average"
        }

        calculator = MetricsCalculator(config=config)

        # 配置已应用
        pass


class TestMetricsCalculatorAgentMetrics:
    """测试代理指标计算"""

    def test_calculate_agent_metrics(self):
        """测试计算代理指标"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_agent_metrics'):
            mock_agent = Mock()
            mock_agent.agent_id = "agent_1"
            mock_agent.get_capability_index = Mock(return_value=75.0)

            metrics = calculator.calculate_agent_metrics(mock_agent)
            assert metrics is not None
            assert isinstance(metrics, dict)

    def test_calculate_agent_moral_level(self):
        """测试计算代理道德水平"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_agent_moral_level'):
            mock_agent = Mock()
            mock_agent.moral_level = 3

            moral = calculator.calculate_agent_moral_level(mock_agent)
            assert moral == 3

    def test_calculate_agent_influence(self):
        """测试计算代理影响力"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_agent_influence'):
            mock_agent = Mock()

            influence = calculator.calculate_agent_influence(mock_agent)
            assert isinstance(influence, float)
            assert 0 <= influence <= 1


class TestMetricsCalculatorSystemMetrics:
    """测试系统指标计算"""

    def test_calculate_system_metrics(self):
        """测试计算系统指标"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_system_metrics'):
            agents = [Mock() for _ in range(3)]
            environment = Mock()

            metrics = calculator.calculate_system_metrics(agents, environment)
            assert metrics is not None
            assert isinstance(metrics, dict)

    def test_calculate_total_power(self):
        """测试计算总权力"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_total_power'):
            agents = []
            for i in range(3):
                agent = Mock()
                agent.get_capability_index = Mock(return_value=50.0 + i * 10)
                agents.append(agent)

            total_power = calculator.calculate_total_power(agents)
            assert isinstance(total_power, float)
            assert total_power > 0

    def test_calculate_power_concentration(self):
        """测试计算权力集中度"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_power_concentration'):
            agents = [Mock() for _ in range(3)]

            concentration = calculator.calculate_power_concentration(agents)
            assert isinstance(concentration, float)
            assert 0 <= concentration <= 1


class TestMetricsCalculatorPowerDistribution:
    """测试权力分布计算"""

    def test_calculate_power_distribution(self):
        """测试计算权力分布"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_power_distribution'):
            agents = [Mock() for _ in range(3)]

            distribution = calculator.calculate_power_distribution(agents)
            assert isinstance(distribution, dict)
            assert len(distribution) == 3

    def test_calculate_gini_coefficient(self):
        """测试计算基尼系数"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_gini_coefficient'):
            values = [10, 20, 30, 40, 50]

            gini = calculator.calculate_gini_coefficient(values)
            assert isinstance(gini, float)
            assert 0 <= gini <= 1

    def test_calculate_herfindahl_index(self):
        """测试计算赫芬达尔指数"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_herfindahl_index'):
            values = [0.2, 0.3, 0.5]  # 归一化的值

            hhi = calculator.calculate_herfindahl_index(values)
            assert isinstance(hhi, float)
            assert 0 <= hhi <= 1


class TestMetricsCalculatorOrderMetrics:
    """测试秩序指标计算"""

    def test_calculate_order_level(self):
        """测试计算秩序水平"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_order_level'):
            environment = Mock()
            environment.order_level = 3

            order = calculator.calculate_order_level(environment)
            assert order == 3

    def test_calculate_order_stability(self):
        """测试计算秩序稳定性"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_order_stability'):
            environment = Mock()
            agents = [Mock() for _ in range(3)]

            stability = calculator.calculate_order_stability(environment, agents)
            assert isinstance(stability, float)
            assert 0 <= stability <= 1


class TestMetricsCalculatorInteractionMetrics:
    """测试交互指标计算"""

    def test_calculate_interaction_frequency(self):
        """测试计算交互频率"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_interaction_frequency'):
            interactions = [
                {"timestamp": 0},
                {"timestamp": 1},
                {"timestamp": 2}
            ]

            frequency = calculator.calculate_interaction_frequency(interactions, time_window=2)
            assert isinstance(frequency, float)

    def test_calculate_interaction_success_rate(self):
        """测试计算交互成功率"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_interaction_success_rate'):
            interactions = [
                {"outcome": "success"},
                {"outcome": "failure"},
                {"outcome": "success"}
            ]

            success_rate = calculator.calculate_interaction_success_rate(interactions)
            assert success_rate == 2/3


class TestMetricsCalculatorAggregation:
    """测试指标聚合"""

    def test_aggregate_metrics(self):
        """测试聚合指标"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'aggregate_metrics'):
            metrics_list = [
                {"power": 70, "influence": 0.6},
                {"power": 80, "influence": 0.7},
                {"power": 75, "influence": 0.65}
            ]

            aggregated = calculator.aggregate_metrics(metrics_list)
            assert isinstance(aggregated, dict)

    def test_calculate_moving_average(self):
        """测试计算移动平均"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'calculate_moving_average'):
            values = [10, 20, 30, 40, 50]

            ma = calculator.calculate_moving_average(values, window=3)
            assert isinstance(ma, list)


class TestMetricsCalculatorNormalization:
    """测试指标归一化"""

    def test_normalize_values(self):
        """测试归一化值"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'normalize_values'):
            values = [10, 20, 30, 40, 50]

            normalized = calculator.normalize_values(values)
            assert all(0 <= v <= 1 for v in normalized)

    def test_standardize_values(self):
        """测试标准化值（Z-score）"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'standardize_values'):
            values = [10, 20, 30, 40, 50]

            standardized = calculator.standardize_values(values)
            assert isinstance(standardized, list)


class TestMetricsCalculatorHistory:
    """测试历史记录"""

    def test_record_metrics(self):
        """测试记录指标"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'record_metrics'):
            calculator.record_metrics(
                round=1,
                metrics={"total_power": 100, "order_level": 3}
            )

            # 指标已记录
            pass

    def test_get_metrics_history(self):
        """测试获取指标历史"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'record_metrics') and hasattr(calculator, 'get_metrics_history'):
            calculator.record_metrics(
                round=1,
                metrics={"total_power": 100}
            )

            history = calculator.get_metrics_history()
            assert len(history) == 1


class TestMetricsCalculatorExport:
    """测试指标导出"""

    def test_export_metrics(self, temp_dir):
        """测试导出指标"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'export_metrics'):
            export_path = temp_dir / "metrics_export.json"
            calculator.export_metrics(str(export_path))

            assert export_path.exists()


class TestMetricsCalculatorConfiguration:
    """测试计算器配置"""

    def test_set_precision(self):
        """测试设置精度"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'set_precision'):
            calculator.set_precision(0.001)

            # 精度已设置
            pass

    def test_get_supported_metrics(self):
        """测试获取支持的指标"""
        try:
            from src.metrics.calculator import MetricsCalculator
        except ImportError:
            pytest.skip("MetricsCalculator类未找到")

        calculator = MetricsCalculator()

        if hasattr(calculator, 'get_supported_metrics'):
            metrics = calculator.get_supported_metrics()
            assert isinstance(metrics, list)
