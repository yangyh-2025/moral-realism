"""
Tests for Phase 6: Workflow Integration.

Test suite for the complete ABM simulation workflow, integrating
all components from Phases 1-5.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.environment.rule_environment import RuleEnvironment
from src.metrics import MetricsCalculator, DataStorage
from src.models.agent import GreatPower, SmallState
from src.models.capability import Capability
from src.models.leadership_type import LeadershipType


class TestWorkflowIntegration(unittest.TestCase):
    """Tests for complete workflow integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_simulation_setup(self):
        """Test initial simulation setup."""
        # Create environment
        rule_env = RuleEnvironment()

        # Create agents
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

        # Verify agents created
        self.assertEqual(len(agents), 3)
        self.assertIn("gp1", agents)
        self.assertIn("gp2", agents)
        self.assertIn("ss1", agents)

        # Verify rule environment
        self.assertIsNotNone(rule_env)

    def test_metrics_collection_workflow(self):
        """Test metrics collection across simulation rounds."""
        # Create components
        calculator = MetricsCalculator()
        storage = DataStorage(base_dir=self.temp_dir)

        # Create test agents
        agents = {
            "gp1": GreatPower(
                "gp1",
                "Great Power 1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        }

        # Collect metrics for multiple rounds
        for round_num in range(3):
            metrics = calculator.calculate_all_metrics(
                agents=agents,
                state={"time": round_num},
                round_result={"round": round_num},
            )

            # Save metrics
            filepath = storage.save_metrics(metrics, round_num)
            self.assertIsNotNone(filepath)

            # Verify saved
            loaded = storage.get_round_metrics(round_num)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["round"], round_num)

    def test_checkpoint_save_restore(self):
        """Test checkpoint save and restore workflow."""
        storage = DataStorage(base_dir=self.temp_dir)

        # Create checkpoint data
        checkpoint_data = {
            "agents": ["gp1", "gp2"],
            "round": 5,
            "state": {
                "time": 5,
                "custom_data": "test",
            },
        }

        # Save checkpoint
        filepath = storage.save_checkpoint(checkpoint_data, "test_checkpoint")
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())

        # Restore checkpoint
        restored = storage.load_checkpoint("test_checkpoint")
        self.assertIsNotNone(restored)
        self.assertEqual(restored["checkpoint_id"], "test_checkpoint")
        self.assertEqual(restored["state"], checkpoint_data)

    def test_agent_interactions(self):
        """Test agent interactions in simulation."""
        # Create agents
        gp1 = GreatPower(
            "gp1",
            "Great Power 1",
            "大国1",
            LeadershipType.WANGDAO,
            Capability("gp1"),
        )
        gp2 = GreatPower(
            "gp2",
            "Great Power 2",
            "大国2",
            LeadershipType.HEGEMON,
            Capability("gp2"),
        )

        # Add history entries
        gp1.add_history(
            "diplaiomatic",
            "Diplomatic negotiation with GP2",
            {"target": "gp2", "upholds_norm": True},
        )

        gp2.add_history(
            "diplomatic",
            "Diplomatic negotiation with GP1",
            {"target": "gp1", "upholds_norm": False},
        )

        # Verify history
        self.assertEqual(len(gp1.history), 1)
        self.assertEqual(len(gp2.history), 1)

    def test_system_state_tracking(self):
        """Test system state tracking across rounds."""
        calculator = MetricsCalculator()
        storage = DataStorage(base_dir=self.temp_dir)

        agents = {
            "gp1": GreatPower(
                "gp1",
                "GP1",
                "GP1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        }

        # Track system metrics across rounds
        system_metrics_history = []
        for round_num in range(3):
            metrics = calculator.calculate_all_metrics(
                agents=agents,
                state={"time": round_num},
                round_result={"round": round_num},
            )

            system_metrics_history.append(metrics["system_metrics"])
            storage.save_metrics(metrics, round_num)

        # Verify tracking
        self.assertEqual(len(system_metrics_history), 3)

        # Get trends
        trends = storage.get_system_trends(0, 2)
        self.assertEqual(len(trends["power_concentration"]), 3)


class TestSimulationScenarios(unittest.TestCase):
    """Tests for specific simulation scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unipolar_scenario(self):
        """Test unipolar system scenario."""
        # Single dominant agent
        agents = {
            "gp1": GreatPower(
                "gp1",
                "Dominant Power",
                "主导国",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        }

        calculator = MetricsCalculator()
        metrics = calculator.calculate_all_metrics(
            agents=agents,
            state={},
            round_result={},
        )

        # Should be unipolar
        self.assertEqual(metrics["pattern_type"], "unipolar")

    def test_bipolar_scenario(self):
        """Test bipolar system scenario."""
        # Two balanced great powers
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

        calculator = MetricsCalculator()
        metrics = calculator.calculate_all_metrics(
            agents=agents,
            state={},
            round_result={},
        )

        # Should be bipolar or multipolar depending on balance
        self.assertIn(metrics["pattern_type"], ["bipolar", "multipolar"])

    def test_multipolar_scenario(self):
        """Test multipolar system scenario."""
        # Multiple powers
        agents = {
            f"gp{i}": GreatPower(
                f"gp{i}",
                f"Great Power {i}",
                f"大国{i}",
                LeadershipType.WANGDAO,
                Capability(f"gp{i}"),
            )
            for i in range(4)
        }

        calculator = MetricsCalculator()
        metrics = calculator.calculate_all_metrics(
            agents=agents,
            state={},
            round_result={},
        )

        # Should be multipolar
        self.assertEqual(metrics["pattern_type"], "multipolar")
        self.assertEqual(metrics["agent_count"], 4)


if __name__ == "__main__":
    unittest.main()
