"""
Unit tests for Observation module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from typing import Dict, List

try:
    from observation.metrics import SimulationMetrics, AgentMetrics, RoundMetrics
    from observation.analytics import SimulationAnalytics
    from observation.decision_engine import DecisionEngine
    from observation.experiments import ExperimentFramework, Experiment
    from observation.workflow import ObservationWorkflow
    OBSERVATION_AVAILABLE = True
except ImportError:
    OBSERVATION_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not OBSERVATION_AVAILABLE,
    reason="Observation module not available"
)


@pytest.mark.unit
class TestSimulationMetrics:
    """Test SimulationMetrics class"""

    @pytest.fixture
    def metrics(self):
        return SimulationMetrics()

    def test_metrics_initialization(self, metrics):
        """Test metrics initialization"""
        assert metrics.total_rounds == 0
        assert metrics.total_decisions == 0
        assert metrics.total_interactions == 0

    def test_record_round(self, metrics):
        """Test recording round"""
        metrics.record_round(round_number=1, duration=10.5)

        assert metrics.total_rounds == 1
        assert len(metrics.rounds) == 1

    def test_record_decision(self, metrics):
        """Test recording decision"""
        metrics.record_decision(
            agent_id="test_agent",
            decision_type="test_action",
            success=True
        )

        assert metrics.total_decisions == 1

    def test_record_interaction(self, metrics):
        """Test recording interaction"""
        metrics.record_interaction(
            source_agent="agent_a",
            target_agent="agent_b",
            interaction_type="send_message"
        )

        assert metrics.total_interactions == 1

    def test_get_summary(self, metrics):
        """Test getting summary"""
        metrics.record_round(round_number=1, duration=10.0)
        metrics.record_round(round_number=2, duration=12.0)

        summary = metrics.get_summary()

        assert summary["total_rounds"] == 2
        assert summary["avg_round_duration"] == 11.0


@pytest.mark.unit
class TestAgentMetrics:
    """Test AgentMetrics dataclass"""

    def test_agent_metrics_creation(self):
        """Test creating agent metrics"""
        if OBSERVATION_AVAILABLE:
            metrics = AgentMetrics(
                agent_id="test_agent",
                agent_name="Test Country",
                total_decisions=10,
                successful_decisions=8,
                total_interactions=15,
                avg_decision_time=1.5
            )

            assert metrics.agent_id == "test_agent"
            assert metrics.agent_name == "Test Country"
            assert metrics.total_decisions == 10
            assert metrics.successful_decisions == 8

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        if OBSERVATION_AVAILABLE:
            metrics = AgentMetrics(
                agent_id="test",
                agent_name="Test",
                total_decisions=10,
                successful_decisions=8,
                total_interactions=15,
                avg_decision_time=1.5
            )

            success_rate = metrics.successful_decisions / metrics.total_decisions
            assert success_rate == 0.8


@pytest.mark.unit
class TestRoundMetrics:
    """Test RoundMetrics dataclass"""

    def test_round_metrics_creation(self):
        """Test creating round metrics"""
        if OBSERVATION_AVAILABLE:
            metrics = RoundMetrics(
                round_number=1,
                start_time="2026-03-14T00:00:00Z",
                end_time="2026-03-14T00:01:00Z",
                duration=60.0,
                decisions_count=5,
                interactions_count=10,
                events_count=2
            )

            assert metrics.round_number == 1
            assert metrics.duration == 60.0


@pytest.mark.unit
class TestSimulationAnalytics:
    """Test SimulationAnalytics class"""

    @pytest.fixture
    def analytics(self):
        """Create analytics instance"""
        if OBSERVATION_AVAILABLE:
            return SimulationAnalytics()

    def test_analytics_initialization(self, analytics):
        """Test analytics initialization"""
        if OBSERVATION_AVAILABLE:
            assert isinstance(analytics.data, dict)

    def test_add_data_point(self, analytics):
        """Test adding data point"""
        if OBSERVATION_AVAILABLE:
            analytics.add_data_point(
                metric_name="test_metric",
                value=10.0,
                round_number=1,
                agent_id="test_agent"
            )

            assert "test_metric" in analytics.data

    def test_calculate_statistics(self, analytics):
        """Test calculating statistics"""
        if OBSERVATION_AVAILABLE:
            # Add data points
            for i in range(10):
                analytics.add_data_point("test_metric", i, i, f"agent_{i % 3}")

            stats = analytics.calculate_statistics("test_metric")

            assert "mean" in stats
            assert "min" in stats
            assert "max" in stats
            assert "std" in stats

    def test_get_trend_analysis(self, analytics):
        """Test getting trend analysis"""
        if OBSERVATION_AVAILABLE:
            # Add time series data
            for i in range(10):
                analytics.add_data_point("trend_metric", i * 0.5, i, "test_agent")

            trend = analytics.get_trend_analysis("trend_metric")

            assert isinstance(trend, dict)
            assert "direction" in trend


@pytest.mark.unit
class TestDecisionEngine:
    """Test DecisionEngine class"""

    @pytest.fixture
    def engine(self):
        """Create decision engine"""
        if OBSERVATION_AVAILABLE:
            return DecisionEngine()

    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        if OBSERVATION_AVAILABLE:
            assert isinstance(engine._decisions, list)

    def test_record_decision(self, engine):
        """Test recording decision"""
        if OBSERVATION_AVAILABLE:
            engine.record_decision(
                agent_id="test_agent",
                decision={"type": "test_action"},
                timestamp="2026-03-14T00:00:00Z",
                round_number=1
            )

            assert len(engine._decisions) == 1

    def test_get_agent_decisions(self, engine):
        """Test getting agent decisions"""
        if OBSERVATION_AVAILABLE:
            engine.record_decision("agent_a", {"type": "action1"}, "2026-03-14T00:00:00Z", 1)
            engine.record_decision("agent_b", {"type": "action2"}, "2026-03-14T00:00:01:00Z", 1)
            engine.record_decision("agent_a", {"type": "action3"}, "2026-03-14T00:00:02:00Z", 2)

            agent_a_decisions = engine.get_agent_decisions("agent_a")

            assert len(agent_a_decisions) == 2

    def test_get_decision_count(self, engine):
        """Test getting decision count"""
        if OBSERVATION_AVAILABLE:
            for i in range(5):
                engine.record_decision(f"agent_{i % 3}", {"type": f"action_{i}"}, "2026-03-14T00:00:00Z", 1)

            count = engine.get_decision_count()
            assert count == 5


@pytest.mark.unit
class TestExperimentFramework:
    """Test ExperimentFramework class"""

    @pytest.fixture
    def framework(self):
        """Create experiment framework"""
        if OBSERVATION_AVAILABLE:
            return ExperimentFramework()

    def test_framework_initialization(self, framework):
        """Test framework initialization"""
        if OBSERVATION_AVAILABLE:
            assert isinstance(framework._experiments, dict)

    def test_create_experiment(self, framework):
        """Test creating experiment"""
        if OBSERVATION_AVAILABLE:
            exp_id = framework.create_experiment(
                name="Test Experiment",
                description="Test description",
                config={}
            )

            assert exp_id in framework._experiments

    def test_run_experiment(self, framework):
        """Test running experiment"""
        if OBSERVATION_AVAILABLE:
            exp_id = framework.create_experiment("Test", "Test", {})

            results = framework.run_experiment(exp_id)

            assert isinstance(results, dict)
            assert "success" in results

    def test_compare_experiments(self, framework):
        """Test comparing experiments"""
        if OBSERVATION_AVAILABLE:
            exp1_id = framework.create_experiment("Exp1", "Test1", {})
            exp2_id = framework.create_experiment("Exp2", "Test2", {})

            comparison = framework.compare_experiments(exp1_id, exp2_id)

            assert isinstance(comparison, dict)
            assert "experiment1" in comparison
            assert "experiment2" in comparison


@pytest.mark.unit
class TestExperiment:
    """Test Experiment dataclass"""

    def test_experiment_creation(self):
        """Test creating experiment"""
        if OBSERVATION_AVAILABLE:
            experiment = Experiment(
                experiment_id="test_exp",
                name="Test Experiment",
                description="Test",
                config={},
                status="running",
                start_time="2026-03-14T00:00:00Z",
                results=None
            )

            assert experiment.experiment_id == "test_exp"
            assert experiment.name == "Test Experiment"
            assert experiment.status == "running"


@pytest.mark.unit
class TestObservationWorkflow:
    """Test ObservationWorkflow class"""

    @pytest.fixture
    def workflow(self):
        """Create observation workflow
        """
        if OBSERVATION_AVAILABLE:
            return ObservationWorkflow()

    def test_workflow_initialization(self, workflow):
        """Test workflow initialization"""
        if OBSERVATION_AVAILABLE:
            assert isinstance(workflow._data_points, list)

    def test_start_observation(self, workflow):
        """Test starting observation"""
        if OBSERVATION_AVAILABLE:
            workflow.start_observation(
                simulation_id="test_sim",
                round_number=1
            )

            assert workflow._is_observing is True

    def test_stop_observation(self, workflow):
        """Test stopping observation"""
        if OBSERVATION_AVAILABLE:
            workflow.start_observation("test_sim", 1)
            workflow.stop_observation()

            assert workflow._is_observing is False

    def test_record_event(self, workflow):
        """Test recording event"""
        if OBSERVATION_AVAILABLE:
            workflow.record_event(
                event_type="decision",
                data={"agent_id": "test"},
                timestamp="2026-03-14T00:00:00Z"
            )

            assert len(workflow._data_points) == 1

    def test_get_observations(self, workflow):
        """Test getting observations"""
        if OBSERVATION_AVAILABLE:
            workflow.record_event("test", {}, "2026-03-14T00:00:00Z")

            observations = workflow.get_observations()

            assert isinstance(observations, list)
            assert len(observations) == 1
