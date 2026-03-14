"""
Prompt template engine tests

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.prompt_engine import (
    PromptTemplate,
    PromptBuilder,
    PromptTemplateEngine,
    ScenarioPromptEngine,
    ABTestingFramework,
    TEMPLATE_DESCRIPTION_CN
)
from config.agent_templates import (
    AgentTemplateType,
    AgentTemplateConfig,
    MultiLanguageTemplateManager,
    TemplateQualityMetrics
)


class TestPromptTemplateEnum(unittest.TestCase):
    """Test PromptTemplate enum"""

    def test_all_template_types_defined(self):
        """Verify all template types are defined"""
        self.assertIsNotNone(PromptTemplate.LEADER_DECISION.value)
        self.assertIsNotNone(PromptTemplate.GLOBAL_EVENT_RESPONSE.value)
        self.assertIsNotNone(PromptTemplate.FINAL_JUDGMENT.value)

    def test_template_descriptions_exist(self):
        """Verify template descriptions exist"""
        self.assertGreater(len(TEMPLATE_DESCRIPTION_CN), 0)


class TestPromptBuilder(unittest.TestCase):
    """Test PromptBuilder chain calls"""

    def test_chain_calling(self):
        """Test chain calling"""
        builder = PromptBuilder(
            PromptTemplate.LEADER_DECISION,
            {"agent_name": "China"}
        )

        result = (
            builder
            .add_variable("power_tier", "superpower")
            .add_variable("leader_type", "wangdao")
            .add_system_message("You are a decision assistant.")
            .build()
        )

        self.assertIn("China", result)
        self.assertIn("superpower", result)

    def test_add_variables_multiple(self):
        """Test batch adding variables"""
        builder = PromptBuilder(PromptTemplate.LEADER_DECISION)

        result = builder.add_variables({
            "agent_name": "USA",
            "power_tier": "superpower"
        }).build()

        self.assertIn("USA", result)
        self.assertIn("superpower", result)

    def test_memory_context(self):
        """Test memory context"""
        builder = PromptBuilder(PromptTemplate.LEADER_DECISION)

        memory = [
            {"type": "decision", "content": "Made alliance"},
            {"type": "speech", "content": "Speech about trade"}
        ]

        result = builder.add_memory_context(memory, max_items=2).build()
        # Check that memory content is included
        self.assertIn("Made alliance", result)


class TestPromptTemplateEngine(unittest.TestCase):
    """Test PromptTemplateEngine"""

    def setUp(self):
        """Set up test environment"""
        self.engine = PromptTemplateEngine(
            template_dir=str(Path(__file__).parent.parent / "config" / "prompts"),
            enable_cache=True
        )

    def test_load_template(self):
        """Test template loading"""
        template = self.engine.load_template(PromptTemplate.LEADER_DECISION)
        self.assertIsNotNone(template)
        self.assertGreater(len(template), 0)

    def test_render_template(self):
        """Test template rendering"""
        context = {
            "agent_name": "TestCountry",
            "leader_type": "wangdao",
            "power_tier": "great_power",
            "current_situation": "Peaceful",
            "available_actions": [],
            "constraints": "None"
        }

        rendered = self.engine.render_template(
            PromptTemplate.LEADER_DECISION,
            context
        )

        self.assertIn("TestCountry", rendered)

    def test_token_count_calculation(self):
        """Test token count calculation"""
        text = "This is English. This is Chinese text."

        token_count = PromptTemplateEngine.calculate_token_count(text)
        self.assertGreater(token_count, 0)

    def test_template_statistics(self):
        """Test template usage statistics"""
        context = {
            "agent_name": "Test",
            "leader_type": "wangdao",
            "current_situation": "Test situation"
        }
        for i in range(3):
            self.engine.render_template(PromptTemplate.LEADER_DECISION, context)

        stats = self.engine.get_statistics(PromptTemplate.LEADER_DECISION)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].call_count, 3)


class TestScenarioPromptEngine(unittest.TestCase):
    """Test scenario-based prompt engine"""

    def setUp(self):
        """Set up test environment"""
        base_engine = PromptTemplateEngine(
            template_dir=str(Path(__file__).parent.parent / "config" / "prompts")
        )
        self.scenario_engine = ScenarioPromptEngine(base_engine)

    def test_get_prompt_for_agent(self):
        """Test getting adapted prompts for agents"""
        context = {
            "agent_name": "TestCountry",
            "leader_type": "wangdao",
            "current_situation": "Test situation"
        }

        prompt = self.scenario_engine.get_prompt_for_agent(
            "state", "superpower", PromptTemplate.LEADER_DECISION, context
        )
        self.assertIn("TestCountry", prompt)


class TestAgentTemplateConfig(unittest.TestCase):
    """Test agent template configuration"""

    def test_all_configs_defined(self):
        """Test all template configs are defined"""
        self.assertIn("role_description", AgentTemplateConfig.SUPERPOWER_CONFIG)
        self.assertIn("strategic_focus", AgentTemplateConfig.GREAT_POWER_CONFIG)

    def test_get_template_config(self):
        """Test getting template configuration"""
        config = AgentTemplateConfig.get_template_config(AgentTemplateType.SUPERPOWER)
        self.assertIn("role_description", config)


class TestMultiLanguageTemplateManager(unittest.TestCase):
    """Test multi-language template manager"""

    def test_term_standardization(self):
        """Test term standardization"""
        zh_term = MultiLanguageTemplateManager.standardize_term("hegemonic", "zh")
        self.assertIn("霸权", zh_term)


class TestABTestingFramework(unittest.TestCase):
    """Test A/B testing framework"""

    def setUp(self):
        """Set up test environment"""
        self.ab_tester = ABTestingFramework()

    def test_create_ab_test(self):
        """Test creating A/B test"""
        test_id = self.ab_tester.create_ab_test(
            "test_template_comparison",
            "Template A content",
            "Template B content",
            []
        )
        self.assertIsNotNone(test_id)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPromptTemplateEnum))
    suite.addTests(loader.loadTestsFromTestCase(TestPromptBuilder))
    suite.addTests(loader.loadTestsFromTestCase(TestPromptTemplateEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestScenarioPromptEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentTemplateConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestMultiLanguageTemplateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestABTestingFramework))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
