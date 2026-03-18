"""
Unit tests for Prompt Engine module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from pathlib import Path
from typing import Dict, Any
import json
import tempfile
import os

try:
    from infrastructure.prompts.prompt_engine import (
        PromptTemplateEngine,
        PromptBuilder,
        PromptTemplate,
        TemplateVersion,
        TemplateStatistics,
        ScenarioPromptEngine,
        ABTestingFramework,
        TEMPLATE_DESCRIPTION_CN
    )
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not CORE_AVAILABLE,
    reason="Core module not available"
)


@pytest.mark.unit
class TestPromptTemplate:
    """Test PromptTemplate enum"""

    def test_template_values(self):
        """Test all template types have values"""
        templates = [
            PromptTemplate.LEADER_DECISION,
            PromptTemplate.STATE_FOLLOWUP,
            PromptTemplate.ALLIANCE_INVITATION,
            PromptTemplate.ALLIANCE_RESPONSE,
            PromptTemplate.GLOBAL_EVENT_RESPONSE,
            PromptTemplate.FINAL_JUDGMENT,
            PromptTemplate.SITUATION_ASSESSMENT,
            PromptTemplate.POWER_BALANCE_EVALUATION,
            PromptTemplate.INFLUENCE_ANALYSIS,
            PromptTemplate.RULE_VALIDATION,
            PromptTemplate.CONSTRAINT_CHECK,
        ]

        for template in templates:
            assert isinstance(template.value, str)
            assert len(template.value) > 0

    def test_speech_templates(self):
        """Test speech template types"""
        templates = [
            PromptTemplate.DIPLOMATIC_STATEMENT,
            PromptTemplate.ALLIANCE_SPEECH,
            PromptTemplate.EVENT_RESPONSE_SPEECH,
            PromptTemplate.CRISIS_COMMUNICATION,
            PromptTemplate.ORG_DECLARATION,
        ]

        for template in templates:
            assert isinstance(template.value, str)
            assert len(template.value) > 0

    def test_template_descriptions(self):
        """Test all templates have Chinese descriptions"""
        assert PromptTemplate.LEADER_DECISION in TEMPLATE_DESCRIPTION_CN
        assert PromptTemplate.STATE_FOLLOWUP in TEMPLATE_DESCRIPTION_CN
        assert len(TEMPLATE_DESCRIPTION_CN) > 10


@pytest.mark.unit
class TestPromptBuilder:
    """Test PromptBuilder class"""

    @pytest.fixture
    def builder(self):
        """Create prompt builder"""
        return PromptBuilder(
            template=PromptTemplate.LEADER_DECISION,
            context={"agent_name": "TestCountry"}
        )

    def test_builder_initialization(self, builder):
        """Test builder initialization"""
        assert builder.template == PromptTemplate.LEADER_DECISION
        assert builder.context == {"agent_name": "TestCountry"}
        assert builder.variables == {}
        assert builder.system_messages == []
        assert builder.memory_context == []

    def test_add_variable(self, builder):
        """Test adding single variable"""
        result = builder.add_variable("test_key", "test_value")
        assert result is builder  # Test chain
        assert builder.variables["test_key"] == "test_value"

    def test_add_variables(self, builder):
        """Test adding multiple variables"""
        vars_to_add = {"key1": "value1", "key2": "value2"}
        result = builder.add_variables(vars_to_add)
        assert result is builder
        assert builder.variables == vars_to_add

    def test_add_system_message(self, builder):
        """Test adding system message"""
        result = builder.add_system_message("System instruction")
        assert result is builder
        assert len(builder.system_messages) == 1
        assert builder.system_messages[0] == "System instruction"

    def test_add_memory_context(self, builder):
        """Test adding memory context"""
        memory = [
            {"type": "decision", "content": "Made decision X"},
            {"type": "speech", "content": "Spoke about Y"}
        ]
        result = builder.add_memory_context(memory)
        assert result is builder
        assert len(builder.memory_context) == 2

    def test_add_memory_context_with_limit(self, builder):
        """Test memory context with limit"""
        memory = [
            {"type": "action", "content": f"Action {i}"}
            for i in range(20)
        ]
        builder.add_memory_context(memory, max_items=5)
        assert len(builder.memory_context) == 5

    def test_set_max_tokens(self, builder):
        """Test setting max tokens"""
        result = builder.set_max_tokens(2048)
        assert result is builder
        assert builder._max_tokens == 2048

    def test_build_simple(self, builder):
        """Test building simple prompt"""
        builder.add_variable("leader_type", "wangdao")
        builder.add_variable("current_situation", "Peaceful")

        prompt = builder.build()

        assert "TestCountry" in prompt
        assert "wangdao" in prompt
        assert "Peaceful" in prompt

    def test_build_reuse_protection(self, builder):
        """Test that build() can only be called once"""
        builder.build()
        with pytest.raises(RuntimeError, match="已经构建完成"):
            builder.build()

    def test_build_with_system_messages(self, builder):
        """Test building with system messages"""
        builder.add_system_message("You are a diplomatic assistant")
        builder.add_system_message("Follow international law")

        prompt = builder.build()
        assert "# 系统指令" in prompt
        assert "diplomatic assistant" in prompt
        assert "international law" in prompt

    def test_build_with_memory_context(self, builder):
        """Test building with memory context"""
        memory = [
            {"type": "decision", "content": "Decided to send aid"},
            {"type": "speech", "content": "Spoke about peace"}
        ]
        builder.add_memory_context(memory)

        prompt = builder.build()
        assert "# 历史记忆" in prompt
        assert "Decided to send aid" in prompt
        assert "Spoke about peace" in prompt

    def test_build_chaining(self):
        """Test method chaining"""
        prompt = (PromptBuilder(PromptTemplate.LEADER_DECISION, {})
                  .add_variable("agent_name", "China")
                  .add_variable("leader_type", "wangdao")
                  .add_system_message("Be diplomatic")
                  .build())

        assert "China" in prompt
        assert "wangdao" in prompt
        assert "diplomatic" in prompt


@pytest.mark.unit
class TestPromptTemplateEngine:
    """Test PromptTemplateEngine class"""

    @pytest.fixture
    def engine(self, tmp_path):
        """Create prompt template engine"""
        return PromptTemplateEngine(
            template_dir=str(tmp_path / "prompts"),
            enable_cache=True,
            enable_hot_reload=False
        )

    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert isinstance(engine._template_cache, dict)
        assert isinstance(engine._template_versions, dict)
        assert isinstance(engine._statistics, dict)
        assert len(engine._default_templates) > 0

    def test_load_template_from_defaults(self, engine):
        """Test loading default templates"""
        template = engine.load_template(PromptTemplate.LEADER_DECISION)
        assert isinstance(template, str)
        assert len(template) > 0
        assert "决策任务" in template

    def test_load_template_all_types(self, engine):
        """Test loading all template types"""
        templates = [
            PromptTemplate.LEADER_DECISION,
            PromptTemplate.STATE_FOLLOWUP,
            PromptTemplate.ALLIANCE_INVITATION,
            PromptTemplate.FINAL_JUDGMENT
        ]

        for template_type in templates:
            template = engine.load_template(template_type)
            assert isinstance(template, str)
            assert len(template) > 0

    def test_cache_enabled(self, engine):
        """Test that caching works when enabled"""
        # First load
        template1 = engine.load_template(PromptTemplate.LEADER_DECISION)

        # Modify cache and reload
        cache_entry = engine._template_cache.get(PromptTemplate.LEADER_DECISION)
        assert cache_entry is not None

        # Second load should use cache
        template2 = engine.load_template(PromptTemplate.LEADER_DECISION)
        assert template1 == template2

    def test_clear_cache(self, engine):
        """Test clearing cache"""
        engine.load_template(PromptTemplate.LEADER_DECISION)
        assert len(engine._template_cache) > 0

        engine.clear_cache()
        assert len(engine._template_cache) == 0

    def test_calculate_token_count(self):
        """Test token count calculation"""
        # Test empty string
        assert PromptTemplateEngine.calculate_token_count("") == 0

        # Test English text
        english = "This is a test sentence with some words."
        tokens = PromptTemplateEngine.calculate_token_count(english)
        assert tokens > 0

        # Test Chinese text
        chinese = "这是一个测试句子，包含一些汉字。"
        tokens = PromptTemplateEngine.calculate_token_count(chinese)
        assert tokens > 0

        # Chinese should have more tokens per character
        english_tokens = PromptTemplateEngine.calculate_token_count("hello")
        chinese_tokens = PromptTemplateEngine.calculate_token_count("你好")
        assert chinese_tokens > english_tokens

    def test_render_template_simple(self, engine):
        """Test simple template rendering"""
        context = {
            "agent_name": "TestCountry",
            "leader_type": "wangdao",
            "current_situation": "Stable"
        }

        rendered = engine.render_template(
            PromptTemplate.LEADER_DECISION,
            context
        )

        assert "TestCountry" in rendered
        assert "wangdao" in rendered
        assert "Stable" in rendered

    def test_render_template_with_validation(self, engine):
        """Test template rendering with validation"""
        context = {
            "agent_name": "TestCountry",
            "leader_type": "wangdao",
            "current_situation": "Stable"
        }

        # Should not raise
        rendered = engine.render_template(
            PromptTemplate.LEADER_DECISION,
            context,
            validate_variables=True
        )

        assert len(rendered) > 0

    def test_render_template_missing_required_vars(self, engine):
        """Test rendering with missing required variables"""
        context = {
            "agent_name": "TestCountry"
            # Missing leader_type and current_situation
        }

        with pytest.raises(ValueError, match="缺少必需变量"):
            engine.render_template(
                PromptTemplate.LEADER_DECISION,
                context,
                validate_variables=True
            )

    def test_get_statistics(self, engine):
        """Test getting template statistics"""
        # Use a template
        engine.render_template(
            PromptTemplate.LEADER_DECISION,
            {"agent_name": "Test", "leader_type": "wangdao", "current_situation": "OK"}
        )

        stats = engine.get_statistics(PromptTemplate.LEADER_DECISION)
        assert len(stats) == 1
        assert stats[0].call_count == 1
        assert stats[0].last_used is not None

    def test_get_statistics_all(self, engine):
        """Test getting all statistics"""
        engine.render_template(
            PromptTemplate.LEADER_DECISION,
            {"agent_name": "Test", "leader_type": "wangdao", "current_situation": "OK"}
        )

        stats = engine.get_statistics()
        assert len(stats) >= 1

    def test_reload_templates(self, engine):
        """Test reloading templates"""
        # Load a template
        engine.load_template(PromptTemplate.LEADER_DECISION)
        assert len(engine._template_cache) > 0

        # Reload
        engine.reload_templates()
        assert len(engine._template_cache) == 0

    def test_create_builder(self, engine):
        """Test creating PromptBuilder"""
        context = {"agent_name": "Test"}
        builder = engine.create_builder(PromptTemplate.LEADER_DECISION, context)

        assert isinstance(builder, PromptBuilder)
        assert builder.template == PromptTemplate.LEADER_DECISION
        assert builder.context == context


@pytest.mark.unit
class TestScenarioPromptEngine:
    """Test ScenarioPromptEngine class"""

    @pytest.fixture
    def scenario_engine(self, tmp_path):
        """Create scenario prompt engine"""
        base_engine = PromptTemplateEngine(
            template_dir=str(tmp_path / "prompts"),
            enable_cache=True
        )
        return ScenarioPromptEngine(base_engine)

    def test_scenario_engine_initialization(self, scenario_engine):
        """Test initialization"""
        assert scenario_engine.template_engine is not None

    def test_get_prompt_for_agent_superpower(self, scenario_engine):
        """Test getting prompt for superpower agent"""
        context = {"agent_name": "SuperPower"}
        prompt = scenario_engine.get_prompt_for_agent(
            agent_type="state",
            power_tier="superpower",
            template_type=PromptTemplate.LEADER_DECISION,
            context=context
        )

        assert "SuperPower" in prompt
        # Check for superpower scenario modifiers
        assert "超级大国" in prompt

    def test_get_prompt_for_agent_small_power(self, scenario_engine):
        """Test getting prompt for small power agent"""
        context = {"agent_name": "SmallPower"}
        prompt = scenario_engine.get_prompt_for_agent(
            agent_type="state",
            power_tier="small_power",
            template_type=PromptTemplate.LEADER_DECISION,
            context=context
        )

        assert "SmallPower" in prompt
        # Check for small power scenario modifiers
        assert "小国" in prompt

    def test_get_prompt_for_agent_organization(self, scenario_engine):
        """Test getting prompt for organization agent"""
        context = {"agent_name": "UN"}
        prompt = scenario_engine.get_prompt_for_agent(
            agent_type="organization",
            power_tier="superpower",
            template_type=PromptTemplate.LEADER_DECISION,
            context=context
        )

        assert "UN" in prompt
        # Check for organization scenario modifiers
        assert "国际组织" in prompt


@pytest.mark.unit
class TestABTestingFramework:
    """Test ABTestingFramework class"""

    @pytest.fixture
    def ab_framework(self):
        """Create AB testing framework"""
        return ABTestingFramework()

    def test_framework_initialization(self, ab_framework):
        """Test initialization"""
        assert isinstance(ab_framework._test_results, dict)

    def test_create_ab_test(self, ab_framework):
        """Test creating AB test"""
        template_a = "Template A: {variable}"
        template_b = "Template B: {variable}"
        contexts = [{"variable": "value1"}, {"variable": "value2"}]

        test_id = ab_framework.create_ab_test(
            test_name="test_prompt_comparison",
            template_a=template_a,
            template_b=template_b,
            test_contexts=contexts
        )

        assert test_id.startswith("test_prompt_comparison_")
        assert test_id in ab_framework._test_results

    def test_record_result(self, ab_framework):
        """Test recording test result"""
        test_id = ab_framework.create_ab_test(
            test_name="test",
            template_a="A",
            template_b="B",
            test_contexts=[]
        )

        ab_framework.record_result(
            test_id=test_id,
            variant="a",
            context={"key": "value"},
            result={"output": "result"},
            metrics={"success_rate": 0.9, "quality_score": 0.85}
        )

        test_data = ab_framework._test_results[test_id]
        assert len(test_data["results_a"]) == 1
        assert test_data["results_a"][0]["metrics"]["success_rate"] == 0.9

    def test_analyze_test(self, ab_framework):
        """Test analyzing AB test"""
        test_id = ab_framework.create_ab_test(
            test_name="test",
            template_a="A",
            template_b="B",
            test_contexts=[]
        )

        # Record results
        ab_framework.record_result(
            test_id=test_id,
            variant="a",
            context={},
            result={},
            metrics={"success_rate": 0.9, "quality_score": 0.85, "response_time": 1.0}
        )

        ab_framework.record_result(
            test_id=test_id,
            variant="b",
            context={},
            result={},
            metrics={"success_rate": 0.8, "quality_score": 0.75, "response_time": 1.5}
        )

        analysis = ab_framework.analyze_test(test_id)

        assert analysis["test_name"] == "test"
        assert "variant_a" in analysis
        assert "variant_b" in analysis
        assert analysis["variant_a"]["avg_quality_score"] == 0.85
        assert analysis["variant_b"]["avg_quality_score"] == 0.75
        # Variant A should win (higher quality score)
        assert analysis["winner"] == "a"

    def test_analyze_test_nonexistent(self, ab_framework):
        """Test analyzing nonexistent test"""
        analysis = ab_framework.analyze_test("nonexistent")
        assert "error" in analysis
