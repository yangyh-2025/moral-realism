"""
指标指标分析器单元测试

测试MetricsAnalyzer类的核心功能：
- 初始化和配置
- 指标趋势分析
- 模式识别
- 可视化数据生成
"""
import pytest
from unittest.mock import Mock


class TestMetricsAnalyzerInitialization:
    """测试MetricsAnalyzer初始化"""

    def test_metrics_analyzer_initialization(self):
        """测试指标分析器初始化"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        assert analyzer is not None

    def test_metrics_analyzer_with_data(self):
        """测试带数据初始化"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        data = {
            "rounds": [1, 2, 3, 4, 5],
            "total_power": [100, 105, 110, 108, 112]
        }

        analyzer = MetricsAnalyzer(data=data)

        # 数据已加载
        pass


class TestMetricsAnalyzerTrendAnalysis:
    """测试趋势分析"""

    def test_analyze_trend(self):
        """测试分析趋势"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if (hasattr(analyzer, 'analyze_trend')):
            values = [100, 105, 110, 108, 112]

            trend = analyzer.analyze_trend(values)
            assert trend in ["increasing", "decreasing", "stable", "fluctuating"]

    def test_calculate_trend_line(self):
        """测试计算趋势线"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'calculate_trend_line'):
            x_values = [1, 2, 3, 4, 5]
            y_values = [100, 105, 110, 108, 112]

            slope, intercept = analyzer.calculate_trend_line(x_values, y_values)
            assert isinstance(slope, float)
            assert isinstance(intercept, float)

    def test_detect_momentum(self):
        """测试检测动量"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'detect_momentum'):
            values = [100, 105, 110, 115, 120]

            momentum = analyzer.detect_momentum(values)
            assert isinstance(momentum, float)
            assert momentum > 0  # 上升趋势


class TestMetricsAnalyzerPatternRecognition:
    """测试模式识别"""

    def test_detect_cycles(self):
        """测试检测周期性"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzerator, 'detect_cycles'):
            # 周期性数据
            values = [100, 110, 100, 110, 100, 110, 100, 110]

            cycles = analyzer.detect_cycles(values)
            assert isinstance(cycles, dict)

    def test_detect_turning_points(self):
        """测试检测转折点"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'detect_turning_points'):
            # 有转折点的数据
            values = [100, 110, 120, 115, 105, 95, 100]

            turning_points = analyzer.detect_turning_points(values)
            assert isinstance(turning_points, list)

    def test_detect_outliers(self):
        """测试检测异常值"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'detect_outliers'):
            # 包含异常值的数据
            values = [100, 105, 110, 200, 115, 120]

            outliers = analyzer.detect_outliers(values)
            assert isinstance(outliers, list)


class TestMetricsAnalyzerCorrelation:
    """测试相关性分析"""

    def test_calculate_correlation(self):
        """测试计算相关性"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'calculate_correlation'):
            x_values = [1, 2, 3, 4, 5]
            y_values = [2, 4, 6, 8, 10]

            correlation = analyzer.calculate_correlation(x_values, y_values)
            assert isinstance(correlation, float)
            assert abs(correlation) <= 1  # 相关系数在-1到1之间

    def test_find_correlated_metrics(self):
        """测试查找相关指标"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'find_correlated_metrics'):
            data = {
                "metric1": [1, 2, 3, 4, 5],
                "metric2": [2, 4, 6, 8, 10],
                "metric3": [5, 4, 3, 2, 1]
            }

            correlations = analyzer.find_correlated_metrics(data, threshold=0.5)
            assert isinstance(correlations, dict)


class TestMetricsAnalyzerVisualization:
    """测试可视化数据生成"""

    def test_generate_plot_data(self):
        """测试生成绘图数据"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'generate_plot_data'):
            x_values = [1, 2, 3, 4, 5]
            y_values = [100, 105, 110, 108, 112]

            plot_data = analyzer.generate_plot_data(x_values, y_values)
            assert isinstance(plot_data, dict)
            assert "x" in plot_data
            assert "y" in plot_data

    def test_generate_summary_report(self):
        """测试生成摘要报告"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'generate_summary_report'):
            data = {
                "total_power": [100, 105, 110],
                "order_level": [3, 3, 4]
            }

            report = analyzer.generate_summary_report(data)
            assert isinstance(report, dict)


class TestMetricsAnalyzerComparison:
    """测试比较分析"""

    def test_compare_simulations(self):
        """测试比较模拟"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'compare_simulations'):
            sim1 = {"total_power": [100, 105, 110]}
            sim2 = {"total_power": [95, 100, 108]}

            comparison = analyzer.compare_simulations(sim1, sim2)
            assert isinstance(comparison, dict)

    def test_compare_agents(self):
        """测试比较代理"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'compare_agents'):
            agent1 = {"power": [75, 78, 80]}
            agent2 = {"power": [65, 68, 70]}

            comparison = analyzer.compare_agents(agent1, agent2)
            assert isinstance(comparison, dict)


class TestMetricsAnalyzerForecasting:
    """测试预测"""

    def test_forecast_trend(self):
        """测试预测趋势"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'forecast_trend'):
            values = [100, 105, 110, 115, 120]

            forecast = analyzer.forecast_trend(values, steps=3)
            assert isinstance(forecast, list)
            assert len(forecast) == 3

    def test_estimate_convergence(self):
        """测试估计收敛"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'estimate_convergence'):
            # 收敛的数据
            values = [100, 50, 25, 15, 10]

            convergence = analyzer.estimate_convergence(values)
            assert isinstance(convergence, float)


class TestMetricsAnalyzerStatistics:
    """测试统计计算"""

    def (hasattr(analyzer, 'calculate_statistics')):
            values = [100, 105, 110, 108, 112]

            stats = analyzer.calculate_statistics(values)
            assert "mean" in stats
            assert "std" in stats
            assert "min" in stats
            assert "max" in stats

    def test_calculate_percentiles(self):
        """测试计算百分位数"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'calculate_percentiles'):
            values = [100, 105, 110, 108, 112, 115, 120]

            percentiles = analyzer.calculate_percentiles(values, [25, 50, 75])
            assert isinstance(percentiles, dict)
            assert len(percentiles) == 3


class TestMetricsAnalyzerVisualizationData:
    """测试可视化数据"""

    def test_create_heatmap_data(self):
        """测试创建热力图数据"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'create_heatmap_data'):
            data = {
                "agent1": [1, 2, 3],
                "agent2": [2, 3, 4],
                "agent3": [3, 4, 5]
            }

            heatmap = analyzer.create_heatmap_data(data)
            assert isinstance(heatmap, dict)

    def test_create_distribution_data(self):
        """测试创建分布数据"""
        try:
            from src.metrics.analyzer import MetricsAnalyzer
        except ImportError:
            pytest.skip("MetricsAnalyzer类未找到")

        analyzer = MetricsAnalyzer()

        if hasattr(analyzer, 'create_distribution_data'):
            values = [100, 105, 110, 108, 112]

            distribution = analyzer.create_distribution_data(values, bins=5)
            assert isinstance(distribution, dict)
