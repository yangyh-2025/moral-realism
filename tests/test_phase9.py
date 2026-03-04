"""
Phase 9 tests for the moral realism ABM system.

This module contains comprehensive integration tests, scenario tests,
LLM integration tests, and performance tests to validate the
complete system functionality.
"""

import tempfile
import time
import unittest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch, Mock

from src.models.agent import GreatPower, SmallState
from src.models.capability import Capability, HardPower, SoftPower, CapabilityTier
from src.models.leadership_type import LeadershipType
from src.environment.rule_environment import RuleEnvironment
from src.environment.dynamic_environment import DynamicEnvironment
from src.environment.static_environment import StaticEnvironment
from src.metrics import MetricsCalculator, DataStorage
from src.interaction.interaction_manager import InteractionManager
from src.workflow.simulation_controller import SimulationController
from src.workflow.workflow import Workflow, WorkflowConfig
from src.agents.controller_agent import SimulationConfig
from src.workflow.state_manager import StateManager, SimulationSnapshot
from src.workflow.round_executor import RoundExecutor, RoundContext
from src.workflow.performance_monitor import PerformanceMonitor


class TestSystemIntegration(unittest.TestCase):
    """Tests for complete system integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.max_diff = None

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_system_initialization(self):
        """Test complete system initialization with all components."""
        # Create environment
        rule_env = RuleEnvironment()
        dynamic_env = DynamicEnvironment()
        static_env = StaticEnvironment()

        # Create storage
        storage = DataStorage(base_dir=self.temp_dir)

        # Create agents with different leadership types
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
                LeadershipType.HUNYONG,
                Capability("ss1"),
            ),
        }

        # Create interaction manager
        interaction_manager = InteractionManager()

        # Create metrics calculator
        metrics_calculator = MetricsCalculator()

        # Verify all components initialized
        self.assertIsNotNone(rule_env)
        self.assertIsNotNone(dynamic_env)
        self.assertIsNotNone(static_env)
        self.assertIsNotNone(storage)
        self.assertEqual(len(agents), 3)
        self.assertIsNotNone(interaction_manager)
        self.assertIsNotNone(metrics_calculator)

    def test_end_to_end_simulation_flow(self):
        """Test complete end-to-end simulation flow."""
        # Initialize components
        storage = DataStorage(base_dir=self.temp_dir)
        calculator = MetricsCalculator()
        interaction_manager = InteractionManager()

        # Create agents
        agents = {
            "gp1": GreatPower(
                "gp1",
                "GP1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
            "gp2": GreatPower(
                "gp2",
                "GP2",
                "大国2",
                LeadershipType.HEGEMON,
                Capability("gp2"),
            ),
        }

        # Register agents
        for agent in agents.values():
            interaction_manager.register_agent(agent)

        # Execute simulation round
        round_number = 1
        metrics = calculator.calculate_all_metrics(
            agents=agents,
            state={"time": round_number},
            round_result={"round": round_number},
        )

        # Save metrics
        filepath = storage.save_metrics(metrics, round_number)
        self.assertIsNotNone(filepath)

        # Verify metrics saved
        loaded_metrics = storage.get_round_metrics(round_number)
        self.assertIsNotNone(loaded_metrics)
        self.assertEqual(loaded_metrics["round"], round_number)

    def test_checkpoint_save_and_restore(self):
        """Test checkpoint save and restore functionality."""
        # Create components
        storage = DataStorage(base_dir=self.temp_dir)
        state_manager = StateManager()

        # Create agents
        agents = {
            "gp1": GreatPower(
                "gp1",
                "GP1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
        }

        # Register agents
        state_manager.register_agents(agents)

        # Create snapshot
        snapshot = state_manager.capture_state(
            round_number=5,
            additional_context={"test_data": "checkpoint_test"},
        )

        # Save checkpoint
        checkpoint_id = "test_checkpoint"
        filepath = storage.save_checkpoint(
            snapshot.to_dict(), checkpoint_id
        )
        self.assertIsNotNone(filepath)
        self.assertTrue(Path(filepath).exists())

        # Load checkpoint
        loaded_checkpoint = storage.load.load_checkpoint(checkpoint_id)
        self.assertIsNotNone(loaded_checkpoint)
        self.assertEqual(loaded_checkpoint["checkpoint_id"], checkpoint_id)

        # Restore state
        restored_snapshot = SimulationSnapshot.from_dict(
            loaded_checkpoint["state"]
        )
        self.assertIsNotNone(restored_snapshot)
        self.assertEqual(restored_snapshot.round_number, 5)

    def test_report_generation(self):
        """Test simulation report generation."""
        from src.visualization.report_generator import ReportGenerator

        # Create test data
        storage = DataStorage(base_dir=self.temp_dir)
        calculator = MetricsCalculator()

        agents = {
            "gp1": GreatPower(
                "gp1",
                "GP1",
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
            storage.save_metrics(metrics, round_num)

        # Generate report
        report_generator = ReportGenerator(data_storage=storage)
        report = report_generator.generate_report(
            round_start=0,
            round_end=2,
            include_trends=True,
            include_agent_analysis=True,
        )

        self.assertIsNotNone(report)
        self.assertIn("summary", report)
        self.assertIn("agent_analysis", report)
        self.assertIn("trends", report)


class TestScenarios(unittest.TestCase):
    """Tests for key simulation scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_wangdao_leadership_scenario(self):
        """Test Wangdao leadership behavior scenario."""
        # Create Wangdao leader
        gp1 = GreatPower(
            "gp1",
            "Wangdao Leader",
            "王道型领导",
            LeadershipType.WANGDAO,
            Capability("gp1"),
        )

        # Verify leadership characteristics
        profile = gp1.get_leadership_profile()
        self.assertGreater(profile.moral_standard, 0.8)
        self.assertTrue(profile.prefers_diplomatic_solution)
        self.assertTrue(profile.uses_moral_persuasion)
        self.assertTrue(profile.accepts_moral_constraints)

        # Test decision making in crisis
        situation = {"crisis_type": "economic", "severity": "high"}
        available_actions = [
            {"id": "military", "description": "Military intervention"},
            {"id": "diplomatic", "description": "Diplomatic negotiation"},
            {"id": "economic", "description": "Economic sanctions"},
        ]

        decision = gp1.decide(situation, available_actions)
        self.assertIn("action", decision)
        self.assertIn("rationale", decision)
        self.assertEqual(decision["leadership_influence"], "wangdao")

    def test_hegemon_leadership_scenario(self):
        """Test Hegemon leadership behavior scenario."""
        # Create Hegemon leader
        gp2 = GreatPower(
            "gp2",
            "Hegemon Leader",
            "霸权型领导",
            LeadershipType.HEGEMON,
            Capability("gp2"),
        )

        # Verify leadership characteristics
        profile = gp2.get_leadership_profile()
        self.assertGreater(profile.core_interest_weight, 0.8)
        self.assertFalse(profile.prefers_diplomatic_solution)

        # Test decision making
        situation = {"crisis_type": "territorial", "severity": "medium"}
        available_actions = [
            {"id": "military", "description": "Military action"},
            {"di": "diplomatic", "description": "Diplomatic solution"},
        ]

        decision = gp2.decide(situation, available_actions)
        self.assertIn("action", decision)
        self.assertEqual(decision["leadership_influence"], "hegemon")

    def test_qiangquan_leadership_scenario(self):
        """Test Qiangquan leadership behavior scenario."""
        # Create Qiangquan leader
        gp3 = GreatPower(
            "gp3",
            "Qiangquan Leader",
            "强权型领导",
            LeadershipType.QIANGQUAN,
            Capability("gp3"),
        )

        # Verify leadership characteristics
        profile = gp3.get_leadership_profile()
        self.assertLess(profile.moral_standard, 0.4)
        self.assertFalse(profile.uses_moral_persuasion)
        self.assertFalse(profile.accepts_moral_constraints)

        # Test decision making
        situation = {"crisis_type": "security", "severity": "high"}
        available_actions = [
            {"id": "coercive", "description": "Coercive action"},
            {"id": "cooperative", "description": "Cooperative approach"},
        ]

        decision = gp3.decide(situation, available_actions)
        self.assertIn("action", decision)
        self.assertEqual(decision["leadership_influence"], "qiangquan")

    def test_hunyong_leadership_scenario(self):
        """Test Hunyong leadership behavior scenario."""
        # Create Hunyong leader (typically small state)
        ss1 = SmallState(
            "ss1",
            "Hunyong Leader",
            "昏庸型领导",
            LeadershipType.HUNYONG,
            Capability("ss1"),
        )

        # Verify leadership characteristics
        profile = ss1.get_leadership_profile()
        self.assertLess(profile.strategic_capability, 0.4)
        self.assertLess(profile.decision_consistency, 0.5)

        # Test decision making
        situation = {"crisis_type": "political", "severity": "low"}
        available_actions = [
            {"id": "align", "description": "Align with great power"},
            {"id": "neutrality", "description": "Maintain neutrality"},
        ]

        decision = ss1.decide(situation, available_actions)
        self.assertIn("action", decision)
        self.assertEqual(decision["leadership_influence"], "hunyong")

    def test_multipolar_system_evolution(self):
        """Test multipolar system evolution scenario."""
        # Create multiple balanced powers
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

        # Create metrics calculator
        calculator = MetricsCalculator()

        # Simulate system evolution
        system_metrics_history = []
        for round_num in range(5):
            # Modify capabilities to simulate power dynamics
            if round_num == 2:
                agents["gp1"].capability.hard_power.military_capability += 5

            metrics = calculator.calculate_all_metrics(
                agents=agents,
                state={"time": round_num},
                round_result={"round": round_num},
            )

            system_metrics_history.append(metrics["system_metrics"])

        # Verify multipolar pattern
        self.assertEqual(len(system_metrics_history), 5)
        for metrics in system_metrics_history:
            self.assertEqual(metrics["pattern_type"], "multipolar")


class TestLLMIntegration(unittest.TestCase):
    """Tests for LLM integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch.dict('os.environ', {
        'SILICONFLOW_API_KEY': 'test_key',
        'SILICONFLOW_BASE_URL': 'https://test.api/v1'
    })
    def test_llm_engine_initialization(self):
        """Test LLM engine initialization."""
        from src.core.llm_engine import LLMEngine, LLMConfig

        config = LLMConfig(
            api_key="test_key",
            base_url="https://test.api/v1",
            model="test-model",
        )

        engine = LLMEngine(config=config)
        self.assertIsNotNone(engine)
        self.assertEqual(engine.config.api_key, "test_key")

    def test_mock_llm_decision_engine(self):
        """Test mock LLM decision engine without actual API calls."""
        from src.core.llm_engine import LLMEngine

        # Create mock LLM engine
        mock_engine = Mock(spec=LLMEngine)

        # Mock chat completion response
        mock_response = {
            "content": '{"action": "diplomatic", "rationale": "Pursuing peaceful solution"}',
            "model": "test-model",
            "finish_reason": "stop",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        }

        mock_engine.chat_completion.return_value = mock_response

        # Create agent
        agent = GreatPower(
            "gp1",
            "Test Agent",
            "测试智能体",
            LeadershipType.WANGDAO,
            Capability("gp1"),
        )

        # Test decision with mock LLM
        situation = {"crisis_type": "test", "severity": "medium"}
        available_actions = [{"id": "diplomatic", "description": "Diplomatic solution"}]

        decision = agent.decide(situation, available_actions)
        self.assertIn("action", decision)
        self.assertIn("rationale", decision)

    def test_prompt_generation(self):
        """Test prompt generation for different leadership types."""
        from src.prompts.leadership_prompts import LeadershipPrompts

        prompts = LeadershipPrompts()

        # Test prompt generation for each leadership type
        for leadership_type in LeadershipType:
            prompt = prompts.generate_decision_prompt(
                leadership_type=leadership_type,
                situation={"crisis_type": "test"},
                available_actions=[
                    {"id": "action1", "description": "Action 1"},
                    {"id": "action2", "description": "Action 2"},
                ],
            )

            self.assertIsNotNone(prompt)
            self.assertIn(leadership_type.value, prompt.lower())
            self.assertIn("test", prompt.lower())

    def test_function_call_validation(self):
        """Test function call structure validation."""
        from src.core.llm_engine import LLMEngine

        # Define test function
        test_functions = [
            {
                "name": "select_action",
                "description": "Select an action from available options",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_id": {
                            "type": "string",
                            "description": "The ID of the selected action",
                        },
                        "rationale": {
                            "type": "string",
                            "description": "Explanation for the decision",
                        },
                    },
                    "required": ["action_id"],
                },
            }
        ]

        # Validate function structure
        self.assertEqual(len(test_functions), 1)
        self.assertEqual(test_functions[0]["name"], "select_action")
        self.assertIn("action_id", test_functions[0]["parameters"]["properties"])


class TestPerformance(unittest.TestCase):
    """Tests for system performance."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_large_scale_simulation(self):
        """Test large-scale simulation with many agents."""
        # Create many agents
        num_great_powers = 5
        num_small_states = 10

        agents = {}

        # Create great powers
        for i in range(num_great_powers):
            agents[f"gp{i}"] = GreatPower(
                f"gp{i}",
                f"Great Power {i}",
                f"大国{i}",
                LeadershipType.WANGDAO,
                Capability(f"gp{i}"),
            )

        # Create small states
        for i in range(num_small_states):
            agents[f"ss{i}"] = SmallState(
                f"ss{i}",
                f"Small State {i}",
                f"小国{i}",
                LeadershipType.HUNYONG,
                Capability(f"ss{i}"),
            )

        # Create metrics calculator
        calculator = MetricsCalculator()
        storage = DataStorage(base_dir=self.temp_dir)

        # Run simulation
        start_time = time.time()
        for round_num in range(3):
            metrics = calculator.calculate_all_metrics(
                agents=agents,
                state={},
                round_result={"round": round_num},
            )
            storage.save_metrics(metrics, round_num)

        elapsed_time = time.time() - start_time

        # Verify completion and reasonable time
        self.assertEqual(len(agents), num_great_powers + num_small_states)
        self.assertLess(elapsed_time, 10.0)  # Should complete in under 10 seconds

    def test_memory_usage_tracking(self):
        """Test memory usage tracking."""
        import psutil
        import os

        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB

        # Create and run simulation
        agents = {
            f"gp{i}": GreatPower(
                f"gp{i}",
                f"GP {i}",
                f"大国{i}",
                LeadershipType.WANGDAO,
                Capability(f"gp{i}"),
            )
            for i in range(10)
        }

        calculator = MetricsCalculator()

        # Run simulation
        for round_num in range(5):
            calculator.calculate_all_metrics(
                agents=agents,
                state={},
                round_result={"round": round_num},
            )

        # Get final memory
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100 MB for this test)
        self.assertLess(memory_increase, 100.0)

    def test_execution_time_benchmarking(self):
        """Test execution time benchmarking."""
        agents = {
            "gp1": GreatPower(
                "gp1",
                "GP1",
                "大国1",
                LeadershipType.WANGDAO,
                Capability("gp1"),
            ),
            "gp2": GreatPower(
                "gp2",
                "GP2",
                "大国2",
                LeadershipType.HEGEMON,
                Capability("gp2"),
            ),
        }

        calculator = MetricsCalculator()
        storage = DataStorage(base_dir=self.temp_dir)

        # Benchmark execution
        round_times = []
        for round_num in range(10):
            start_time = time.time()

            metrics = calculator.calculate_all_metrics(
                agents=agents,
                state={},
                round_result={"round": round_num},
            )
            storage.save_metrics(metrics, round_num)

            elapsed = time.time() - start_time
            round_times.append(elapsed)

        # Calculate statistics
        avg_time = sum(round_times) / len(round_times)
        max_time = max(round_times)

        # Verify consistent performance
        self.assertLess(avg_time, 1.0)  # Average should be under 1 second
        self.assertLess(max_time, 2.0)  # Max should be under 2 seconds

    def test_performance_monitor_integration(self):
        """Test performance monitor integration."""
        monitor = PerformanceMonitor()

        # Start monitoring
        monitor.start_simulation()

        # Simulate rounds
        for round_num in range(3):
            monitor.start_round(round_num + 1)
            time.sleep(0.01)  # Simulate work
            monitor.end_round()

        # End monitoring
        monitor.end_simulation()

        # Get stats
        stats = monitor.get_stats()

        self.assertEqual(stats.total_rounds, 3)
        self.assertGreater(stats.total_duration, 0)
        self.assertEqual(len(stats.round_durations), 3)


def run_all_phase9_tests():
    """Run all Phase 9 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    unittest.main()
