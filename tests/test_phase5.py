"""
Tests for Phase 5: Metrics Measurement System.

Test suite for MetricsCalculator, DataStorage, and MetricsAnalyzer.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.environment.rule_environment import (
    RuleEnvironment,
    OrderType,
    MoralDimension,
)
from src.metrics import (
    MetricsCalculator,
    AgentMetrics,
    SystemMetrics,
    DataStorage,
    MetricsAnalyzer,
    TrendAnalysis,
    PowerTransition,
)
from src.models.agent import GreatPower, SmallState
from src.models.capability import Capability, CapabilityTier
from src.models.leadership_type import LeadershipType


class TestMetricsCalculator(unittest.TestCase):
    """Tests for MetricsCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = MetricsCalculator()

    def test_initialization(self):
        """Test calculator initialization."""
        self.assertIsNotNone(self.calculator.rule_environment)
        self.assertIsInstance(self.calculator.rule_environment, RuleEnvironment)

    def test_calculate_all_metrics(self):
        """Test calculating all metrics."""
        # Create test agents
        agents = {
            "gp1": GreatPower(
                "gp1",
                "Great Power 1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
            "gp2": GreatPower(
                "gp2",
                "Great Power 2",
                "大国2",
                LeadershipType.HEGEMON,
                Capability("gp2"),
            ),
        }

        # Calculate metrics
        metrics = self.calculator.calculate_all_metrics(
            agents=agents,
            state={"time": 0},
            round_result={"round": 0},
        )

        # Verify structure
        self.assertIn("timestamp", metrics)
        self.assertIn("round", metrics)
        self.assertEqual(metrics["round"], 0)
        self.assertIn("agent_metrics", metrics)
        self.assertIn("system_metrics", metrics)
        self.assertIn("pattern_type", metrics)
        self.assertIn("agent_count", metrics)
        self.assertEqual(metrics["agent_count"], 2)

        # Verify agent metrics
        self.assertIn("gp1", metrics["agent_metrics"])
        self.assertIn("gp2", metrics["agent_metrics"])

    def test_calculate_agent_metrics(self):
        """Test calculating metrics for a single agent."""
        agent = GreatPower(
            "gp1",
            "Great Power 1",
            "大国1",
            LeadershipType.WANGDAO,
            Capability("gp1"),
        )

        agent_metrics = self.calculator._calculate_agent_metrics(
            agent=agent,
            rule_env=self.calculator.rule_environment,
            state={},
            round_result={},
        )

        # Verify structure
        self.assertEqual(agent_metrics.agent_id, "gp1")
        self.assertEqual(agent_metrics.name, "Great Power 1")
        self.assertEqual(agent_metrics.leadership_type, LeadershipType.WANGDAO.value)
        self.assertIn("hard_power_index", agent_metrics.capability_metrics)
        self.assertIn("moral_index", agent_metrics.moral_metrics)
        self.assertIn("success_rate", agent_metrics.success_metrics)

    def test_calculate_capability_metrics(self):
        """Test capability metrics calculation."""
        agent = GreatPower(
            "gp1",
            "Test Agent",
            "测试",
            LeadershipType.WANGDAO,
            Capability("gp1"),
        )

        metrics = self.calculator._calculate_capability_metrics(agent)

        # Verify all expected keys
        expected_keys = [
            "hard_power_index",
            "soft_power_index",
            "capability_index",
            "tier",
            "hard_power_details",
            "soft_power_details",
        ]
        for key in expected_keys:
            self.assertIn(key, metrics)

        # Verify values are in valid ranges
        self.assertGreaterEqual(metrics["hard_power_index"], 0)
        self.assertLessEqual(metrics["hard_power_index"], 100)
        self.assertGreaterEqual(metrics["soft_power_index"], 0)
        self.assertLessEqual(metrics["soft_power_index"], 100)
        self.assertIn(metrics["tier"], [t.value for t in CapabilityTier])

    def test_calculate_moral_metrics(self):
        """Test moral metrics calculation."""
        agent = GreatPower(
            "gp1",
            "Test Agent",
            "测试",
            LeadershipType.WANGDAO,
            Capability("gp1"),
        )

        # Add some history
        agent.add_history(
            "diplomatic",
            "Diplomatic negotiation",
            {"upholds_norm": True, "type": "diplomatic_negotiation"},
        )

        metrics = self.calculator._calculate_moral_metrics(
            agent=agent,
            rule_env=self.calculator.rule_environment,
            state={},
            round_result={},
        )

        # Verify structure
        self.assertIn("moral_index", metrics)
        self.assertIn("dimension_scores", metrics)
        self.assertIn("respect_for_norms", metrics)
        self.assertIn("humanitarian_concern", metrics)
        self.assertIn("peaceful_resolution", metrics)
        self.assertIn("international_cooperation", metrics)
        self.assertIn("justice_and_fairness", metrics)

        # Verify moral index is in valid range
        self.assertGreaterEqual(metrics["moral_index"], 0)
        self.assertLessEqual(metrics["moral_index"], 100)

    def test_calculate_system_metrics(self):
        """Test system metrics calculation."""
        agents = [
            GreatPower(
                "gp1",
                "Great Power 1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
            SmallState(
                "ss1",
                "Small State 1",
                "小国1",
                LeadershipType.WANGDAO,
                Capability("ss1"),
            ),
        ]

        system_metrics = self.calculator._calculate_system_metrics(
            agents=agents,
            rule_env=self.calculator.rule_environment,
            state={},
            round_result={},
        )

        # Verify structure
        self.assertIsInstance(system_metrics, SystemMetrics)
        self.assertIn(system_metrics.pattern_type, ["unipolar", "bipolar", "multipolar"])
        self.assertGreaterEqual(system_metrics.power_concentration, 0)
        self.assertLessEqual(system_metrics.power_concentration, 1)
        self.assertGreaterEqual(system_metrics.order_stability, 0)
        self.assertLessEqual(system_metrics.order_stability, 100)
        self.assertGreaterEqual(system_metrics.norm_consensus, 0)
        self.assertLessEqual(system_metrics.norm_consensus, 100)

    def test_calculate_pattern_type(self):
        """Test pattern type determination."""
        # Test unipolar (one dominant agent)
        unipolar_agents = [
            GreatPower(
                "gp1",
                "GP1",
                "GP1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        ]
        pattern = self.calculator._calculate_pattern_type(unipolar_agents)
        self.assertEqual(pattern, "unipolar")

        # Test multipolar (multiple balanced agents)
        multipolar_agents = [
            GreatPower(
                f"gp{i}",
                f"GP{i}",
                f"GP{i}",
                LeadershipType.WANGDAO,
                Capability(f"gp{i}"),
            )
            for i in range(4)
        ]
        pattern = self.calculator._calculate_pattern_type(multipolar_agents)
        self.assertEqual(pattern, "multipolar")

    def test_calculate_power_concentration(self):
        """Test HHI power concentration calculation."""
        # Create agents with equal power
        agents = [
            GreatPower(
                f"gp{i}",
                f"GP{i}",
                f"GP{i}",
                LeadershipType.WANGDAO,
                Capability(f"gp{i}"),
            )
            for i in range(5)
        ]

        # With equal power, HHI should be 1/5^2 * 5 = 0.2
        hhi = self.calculator._calculate_power_concentration(agents)
        self.assertAlmostEqual(hhi, 0.2, places=1)

        # With no agents, HHI should be 0
        hhi = self.calculator._calculate_power_concentration([])
        self.assertEqual(hhi, 0.0)

    def test_calculate_order_stability(self):
        """Test order stability calculation."""
        agents = [
            GreatPower(
                "gp1",
                "GP1",
                "GP1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        ]

        stability = self.calculator._calculate_order_stability(
            agents=agents,
            rule_env=self.calculator.rule_environment,
        )

        # Stability should be in valid range
        self.assertGreaterEqual(stability, 0)
        self.assertLessEqual(stability, 100)

    def test_calculate_norm_consensus(self):
        """Test norm consensus calculation."""
        agents = [
            GreatPower(
                "gp1",
                "GP1",
                "GP1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
            GreatPower(
                "gp2",
                "GP2",
                "GP2",
                LeadershipType.WANGDAO,
                Capability("gp2"),
            ),
        ]

        consensus = self.calculator._calculate_norm_consensus(
            agents=agents,
            rule_env=self.calculator.rule_environment,
        )

        # Consensus should be in valid range
        self.assertGreaterEqual(consensus, 0)
        self.assertLessEqual(consensus, 100)

    def test_calculate_public_goods_level(self):
        """Test public goods level calculation."""
        agents = [
            GreatPower(
                "gp1",
                "GP1",
                "GP1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        ]

        level = self.calculator._calculate_public_goods_level(
            agents=agents,
            rule_env=self.calculator.rule_environment,
        )

        # Level should be in valid range
        self.assertGreaterEqual(level, 0)
        self.assertLessEqual(level, 100)


class TestDataStorage(unittest.TestCase):
    """Tests for DataStorage class."""

    def setUp(self):
        """Set up test fixtures with temp directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = DataStorage(base_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test storage initialization."""
        self.assertEqual(self.storage.base_dir, Path(self.temp_dir))
        self.assertEqual(self.storage.storage_format, "json")

        # Verify directories created
        self.assertTrue(
            (Path(self.temp_dir) / "checkpoints").exists()
        )
        self.assertTrue(
            (Path(self.temp_dir) / "outputs").exists()
        )
        self.assertTrue(
            (Path(self.temp_dir) / "exports").exists()
        )

    def test_save_and_load_metrics(self):
        """Test saving and loading metrics."""
        # Create test metrics
        metrics = {
            "timestamp": "2024-01-01T00:00:00",
            "round": 1,
            "agent_metrics": {
                "gp1": {
                    "agent_id": "gp1",
                    "capability_metrics": {"capability_index": 50.0},
                    "moral_metrics": {"moral_index": 50.0},
                    "success_metrics": {"success_rate": 0.5},
                }
            },
            "system_metrics": {
                "power_concentration": 0.5,
                "order_stability": 50.0,
                "norm_consensus": 50.0,
                "public_goods_level": 50.0,
                "order_type": "multipolar",
            },
            "pattern_type": "multipolar",
            "agent_count": 1,
        }

        # Save metrics
        filepath = self.storage.save_metrics(metrics, 1)
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())

        # Load metrics
        loaded = self.storage.get_round_metrics(1)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["round"], 1)

    def test_save_and_load_checkpoint(self):
        """Test saving and loading checkpoints."""
        checkpoint_data = {
            "agents": ["gp1", "gp2"],
            "round": 10,
            "state": {"key": "value"},
        }

        # Save checkpoint
        filepath = self.storage.save_checkpoint(checkpoint_data, "test_checkpoint")
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())

        # Load checkpoint
        loaded = self.storage.load_checkpoint("test_checkpoint")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["checkpoint_id"], "test_checkpoint")
        self.assertEqual(loaded["state"], checkpoint_data)

    def test_save_metrics_csv_format(self):
        """Test saving metrics in CSV format."""
        # Create CSV storage
        csv_storage = DataStorage(base_dir=self.temp_dir, storage_format="csv")

        metrics = {
            "timestamp": "2024-01-01T00:00:00",
            "round": 1,
            "agent_metrics": {
                "gp1": {
                    "agent_id": "gp1",
                    "name": "GP1",
                    "leadership_type": "wangdao",
                    "capability_metrics": {
                        "capability_index": 50.0,
                        "hard_power_index": 50.0,
                        "soft_power_index": 50.0,
                        "tier": "t1_great_power",
                    },
                    "moral_metrics": {
                        "moral_index": 50.0,
                        "respect_for_norms": 50.0,
                        "humanitarian_concern": 50.0,
                        "peaceful_resolution": 50.0,
                        "international_cooperation": 50.0,
                        "justice_and_fairness": 50.0,
                    },
                    "success_metrics": {
                        "success_rate": 0.5,
                        "total_actions": 10,
                        "successful_actions": 5,
                    },
                }
            },
            "system_metrics": {
                "power_concentration": 0.5,
                "order_stability": 50.0,
                "norm_consensus": 50.0,
                "public_goods_level": 50.0,
                "order_type": "multipolar",
            },
            "pattern_type": "multipolar",
            "agent_count": 1,
        }

        # Save metrics (should create CSV files)
        filepath = csv_storage.save_metrics(metrics, 1)
        self.assertIsNotNone(filepath)

        # Verify CSV files created
        exports_dir = Path(self.temp_dir) / "exports"
        self.assertTrue((exports_dir / "system_metrics.csv").exists())
        self.assertTrue((exports_dir / "agents_capability.csv").exists())
        self.assertTrue((exports_dir / "agents_moral.csv").exists())

    def test_export_to_csv(self):
        """Test exporting to CSV file."""
        # First save some data in CSV format
        csv_storage = DataStorage(base_dir=self.temp_dir, storage_format="csv")
        metrics = {
            "timestamp": "2024-01-01T00:00:00",
            "round": 1,
            "agent_metrics": {},
            "system_metrics": {
                "power_concentration": 0.5,
                "order_stability": 50.0,
                "norm_consensus": 50.0,
                "public_goods_level": 50.0,
                "order_type": "multipolar",
            },
            "pattern_type": "multipolar",
            "agent_count": 0,
        }
        csv_storage.save_metrics(metrics, 1)

        # Export to different file
        export_path = os.path.join(self.temp_dir, "exported.csv")
        result = self.storage.export_to_csv("system_metrics", export_path, 0, 1)

        # Verify export
        self.assertIsNotNone(result)
        self.assertTrue(Path(result).exists())

    def test_list_checkpoints(self):
        """Test listing checkpoints."""
        # Save multiple checkpoints
        for i in range(3):
            self.storage.save_checkpoint({"data": f"checkpoint_{i}"}, f"cp{i}")

        checkpoints = self.storage.list_checkpoints()
        # At least some checkpoints should be found
        self.assertGreaterEqual(len(checkpoints), 0)
        # Check for expected checkpoint IDs
        self.assertIn("cp0", checkpoints)
        self.assertIn("cp1", checkpoints)

    def test_get_agent_history(self):
        """Test getting agent history."""
        # Save metrics with agent data
        metrics = {
            "timestamp": "2024-01-01T00:00:00",
            "round": 1,
            "agent_metrics": {
                "gp1": {
                    "agent_id": "gp1",
                    "capability_metrics": {"capability_index": 50.0},
                    "moral_metrics": {"moral_index": 50.0},
                    "success_metrics": {"success_rate": 0.5},
                }
            },
            "system_metrics": {},
            "pattern_type": "multipolar",
            "agent_count": 1,
        }
        self.storage.save_metrics(metrics, 1)

        # Get agent history
        history = self.storage.get_agent_history("gp1")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["agent_id"], "gp1")

        # Get filtered history
        capability_history = self.storage.get_agent_history("gp1", metric_type="capability")
        self.assertEqual(len(capability_history), 1)
        self.assertIn("capability_index", capability_history[0])

    def test_get_system_trends(self):
        """Test getting system trends."""
        # Save multiple rounds of system metrics
        for i in range(5):
            metrics = {
                "timestamp": f"2024-01-0{i+1}T00:00:00",
                "round": i,
                "agent_metrics": {},
                "system_metrics": {
                    "power_concentration": 0.5 + i * 0.05,
                    "order_stability": 50.0 + i,
                    "norm_consensus": 50.0,
                    "public_goods_level": 50.0,
                    "order_type": "multipolar",
                },
                "pattern_type": "multipolar",
                "agent_count": 0,
            }
            self.storage.save_metrics(metrics, i)

        # Get trends
        trends = self.storage.get_system_trends(0, 4)

        # Verify structure
        self.assertIn("power_concentration", trends)
        self.assertIn("order_stability", trends)
        self.assertIn("norm_consensus", trends)
        self.assertEqual(len(trends["power_concentration"]), 5)
        self.assertEqual(len(trends["order_stability"]), 5)

    def test_get_latest_checkpoint(self):
        """Test getting latest checkpoint."""
        # Test with no checkpoints first
        latest = self.storage.get_latest_checkpoint()
        self.assertIsNone(latest)

        # Now save a checkpoint
        self.storage.save_checkpoint({"data": "test"}, "cp0")

        # Should return a checkpoint
        latest = self.storage.get_latest_checkpoint()
        self.assertIsNotNone(latest)
        self.assertEqual(latest, "cp0")


class TestMetricsAnalyzer(unittest.TestCase):
    """Tests for MetricsAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MetricsAnalyzer()

    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertEqual(self.analyzer._threshold_volatile, 15.0)
        self.assertEqual(self.analyzer._threshold_significant, 5.0)

    def test_analyze_capability_trends(self):
        """Test capability trend analysis."""
        # Create sample history
        history = [
            {"round": i, "capability_index": 50.0 + i * 2.0}
            for i in range(10)
        ]

        analysis = self.analyzer.analyze_capability_trends(history, 0, 9)

        # Verify structure
        self.assertEqual(analysis.metric_name, "capability_index")
        self.assertEqual(analysis.start_round, 0)
        self.assertEqual(analysis.end_round, 9)
        self.assertIn(analysis.direction, [
            "increasing", "decreasing", "stable", "volatile"
        ])
        self.assertGreaterEqual(analysis.start_value, 0)
        self.assertGreaterEqual(analysis.end_value, 0)

    def test_analyze_moral_trends(self):
        """Test moral trend analysis."""
        # Create sample history with decreasing trend
        history = [
            {"round": i, "moral_index": 80.0 - i * 1.5}
            for i in range(10)
        ]

        analysis = self.analyzer.analyze_moral_trends(history, 0, 9)

        # Verify structure
        self.assertEqual(analysis.metric_name, "moral_index")
        self.assertEqual(analysis.start_round, 0)
        self.assertEqual(analysis.end_round, 9)
        self.assertIn(analysis.direction, [
            "increasing", "decreasing", "stable", "volatile"
        ])

    def test_detect_power_transitions(self):
        """Test power transition detection."""
        # Create history with tier transitions
        history = [
            {"round": 0, "agent_id": "gp1", "tier": "t3_medium"},
            {"round": 1, "agent_id": "gp1", "tier": "t3_medium"},
            {"round": 2, "agent_id": "gp1", "tier": "t2_regional"},  # Rise
            {"round": 3, "agent_id": "gp1", "tier": "t2_regional"},
            {"round": 4, "agent_id": "gp1", "tier": "t1_great_power"},  # Rise
        ]

        transitions = self.analyzer.detect_power_transitions(history, 0, 4)

        # Verify transitions detected
        self.assertGreaterEqual(len(transitions), 2)

        # Check first transition
        self.assertEqual(transitions[0].agent_id, "gp1")
        self.assertEqual(transitions[0].from_tier, "t3_medium")
        self.assertEqual(transitions[0].to_tier, "t2_regional")
        self.assertEqual(transitions[0].transition_type, "rise")

    def test_analyze_order_evolution(self):
        """Test order evolution analysis."""
        # Create system trends with changing order types
        system_trends = {
            "order_type": [
                {"round": 0, "value": "multipolar"},
                {"round": 1, "value": "multipolar"},
                {"round": 2, "value": "multipolar"},
                {"round": 3, "value": "bipolar"},  # Transition
                {"round": 4, "value": "bipolar"},
            ]
        }

        analysis = self.analyzer.analyze_order_evolution(system_trends, 0, 4)

        # Verify structure
        self.assertEqual(analysis["start_round"], 0)
        self.assertEqual(analysis["end_round"], 4)
        self.assertEqual(analysis["total_rounds"], 5)
        self.assertIn("dominant_order", analysis)
        self.assertGreaterEqual(analysis["stability_score"], 0)
        self.assertLessEqual(analysis["stability_score"], 1)

    def test_compare_leadership_types(self):
        """Test comparing metrics by leadership type."""
        metrics_by_leadership = {
            "wangdao": [
                {"capability_index": 60.0, "moral_index": 80.0, "success_rate": 0.8},
                {"capability_index": 65.0, "moral_index": 85.0, "success_rate": 0.85},
            ],
            "hegemon": [
                {"capability_index": 70.0, "moral_index": 50.0, "success_rate": 0.7},
            ],
        }

        comparison = self.analyzer.compare_leadership_types(metrics_by_leadership)

        # Verify structure
        self.assertIn("wangdao", comparison)
        self.assertIn("hegemon", comparison)

        wangdao_stats = comparison["wangdao"]
        self.assertEqual(wangdao_stats["agent_count"], 2)
        self.assertAlmostEqual(wangdao_stats["avg_capability"], 62.5, places=1)
        self.assertAlmostEqual(wangdao_stats["avg_moral_index"], 82.5, places=1)

    def test_calculate_correlation(self):
        """Test correlation calculation."""
        # Perfect positive correlation
        x1 = [1.0, 2.0, 3.0, 4.0, 5.0]
        y1 = [2.0, 4.0, 6.0, 8.0, 10.0]
        corr1 = self.analyzer.calculate_correlation(x1, y1)
        self.assertGreater(corr1, 0.9)  # Very high positive correlation

        # Perfect negative correlation
        x2 = [1.0, 2.0, 3.0, 4.0, 5.0]
        y2 = [5.0, 4.0, 3.0, 2.0, 1.0]
        corr2 = self.analyzer.calculate_correlation(x2, y2)
        self.assertLess(corr2, -0.9)  # Very high negative correlation

        # No correlation
        x3 = [1.0, 2.0, 3.0, 4.0, 5.0]
        y3 = [2.0, 4.0, 1.0, 3.0, 5.0]
        corr3 = self.analyzer.calculate_correlation(x3, y3)
        self.assertGreaterEqual(corr3, -1.0)
        self.assertLessEqual(corr3, 1.0)

    def test_predict_trend(self):
        """Test trend prediction."""
        # Create increasing trend
        history = [
            {"value": 50.0 + i * 2.0}
            for i in range(10)
        ]

        prediction = self.analyzer.predict_trend("test_metric", history, lookahead=5)

        # Verify structure
        self.assertEqual(prediction["metric_name"], "test_metric")
        self.assertEqual(prediction["lookahead"], 5)
        self.assertEqual(len(prediction["predicted_values"]), 5)
        self.assertGreaterEqual(prediction["confidence"], 0)
        self.assertLessEqual(prediction["confidence"], 1)

        # Predicted values should be increasing
        preds = prediction["predicted_values"]
        self.assertGreater(preds[-1], preds[0])

    def test_get_summary_statistics(self):
        """Test summary statistics calculation."""
        values = [10.0, 20.0, 30.0, 40.0, 50.0]

        stats = self.analyzer.get_summary_statistics(values)

        # Verify structure
        self.assertEqual(stats["count"], 5)
        self.assertEqual(stats["mean"], 30.0)
        self.assertEqual(stats["median"], 30.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 50.0)
        self.assertEqual(stats["range"], 40.0)

    def test_identify_critical_events(self):
        """Test critical event identification."""
        # Create history with a spike
        metrics_history = [
            {
                "system_metrics": {
                    "power_concentration": 0.3 + i * 0.01,
                    "order_stability": 50.0,
                    "norm_consensus": 50.0,
                }
            }
            for i in range(10)
        ]

        # Add a significant spike
        metrics_history[5]["system_metrics"]["power_concentration"] = 0.8

        events = self.analyzer.identify_critical_events(metrics_history, threshold=2.0)

        # Should detect spike
        self.assertGreater(len(events), 0)

        # Verify event structure
        event = events[0]
        self.assertIn("round", event)
        self.assertIn("metric_name", event)
        self.assertIn("value", event)
        self.assertIn("z_score", event)


class TestIntegration(unittest.TestCase):
    """Integration tests for Phase 5 metrics system."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.calculator = MetricsCalculator()
        self.storage = DataStorage(base_dir=self.temp_dir)
        self.analyzer = MetricsAnalyzer()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_metrics_workflow(self):
        """Test complete metrics workflow."""
        # Create test agents
        agents = {
            "gp1": GreatPower(
                "gp1",
                "Great Power 1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
            "gp2": GreatPower(
                "gp2",
                "Great Power 2",
                "大国2",
                LeadershipType.HEGEMON,
                Capability("gp2"),
            ),
            "ss1": SmallState(
                "ss1",
                "Small State 1",
                "小国1",
                LeadershipType.WANGDAO,
                Capability("ss1"),
            ),
        }

        # Simulate multiple rounds
        for round_num in range(5):
            metrics = self.calculator.calculate_all_metrics(
                agents=agents,
                state={"time": round_num},
                round_result={"round": round_num},
            )

            # Save metrics
            filepath = self.storage.save_metrics(metrics, round_num)
            self.assertIsNotNone(filepath)

            # Verify saved
            loaded = self.storage.get_round_metrics(round_num)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["round"], round_num)

        # Verify we can retrieve history
        history = self.storage.get_agent_history("gp1")
        self.assertEqual(len(history), 5)

        # Test system trends
        trends = self.storage.get_system_trends(0, 4)
        self.assertEqual(len(trends["power_concentration"]), 5)

    def test_storage_and_analysis_integration(self):
        """Test integration between storage and analysis."""
        # Create test data
        agents = {
            "gp1": GreatPower(
                "gp1",
                "Test Agent",
                "测试",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        }

        # Generate metrics for multiple rounds
        for round_num in range(10):
            metrics = self.calculator.calculate_all_metrics(
                agents=agents,
                state={"time": round_num},
                round_result={"round": round_num},
            )
            self.storage.save_metrics(metrics, round_num)

        # Get agent history and analyze trends
        history = self.storage.get_agent_history("gp1", metric_type="capability")
        capability_trend = self.analyzer.analyze_capability_trends(history, 0, 9)

        # Verify trend analysis
        self.assertIsInstance(capability_trend, TrendAnalysis)
        self.assertEqual(capability_trend.start_round, 0)
        self.assertEqual(capability_trend.end_round, 9)

        # Get system trends and analyze order evolution
        system_trends = self.storage.get_system_trends(0, 9)
        order_analysis = self.analyzer.analyze_order_evolution(system_trends, 0, 9)

        # Verify order analysis
        self.assertIn("dominant_order", order_analysis)
        self.assertIn("stability_score", order_analysis)

    def test_checkpoint_workflow(self):
        """Test checkpoint save and restore workflow."""
        # Create initial state
        initial_state = {
            "agents": ["gp1", "gp2"],
            "round": 0,
            "custom_data": {"key": "value"},
        }

        # Save checkpoint
        checkpoint_path = self.storage.save_checkpoint(
            initial_state,
            "initial_state"
        )
        self.assertIsNotNone(checkpoint_path)

        # Load checkpoint
        restored = self.storage.load_checkpoint("initial_state")
        self.assertIsNotNone(restored)
        self.assertEqual(restored["checkpoint_id"], "initial_state")
        self.assertEqual(restored["state"], initial_state)


if __name__ == "__main__":
    unittest.main()
