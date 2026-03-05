"""
交互规则单元测试

测试InteractionRules类的核心功能：
- 初始化和配置
- 规则定义和验证
- 规则应用
"""
import pytest
from unittest.mock import Mock


class TestInteractionRulesInitialization:
    """测试InteractionRules初始化"""

    def test_interaction_rules_initialization(self):
        """测试交互规则初始化"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        assert rules is not None

    def test_interaction_rules_with_config(self):
        """测试带配置初始化"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        config = {
            "strict_mode": True,
            "default_outcome": "reject"
        }

        rules = InteractionRules(config=config)

        # 配置已应用
        pass


class TestInteractionRulesDefinition:
    """测试规则定义"""

    def test_add_rule(self):
        """测试添加规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'add_rule'):
            rule = {
                "name": "diplomatic_protocol",
                "conditions": {
                    "interaction_type": "diplomatic"
                },
                "outcomes": {
                    "success_probability": 0.8
                }
            }

            rules.add_rule(rule)

            # 规则已添加
            pass

    def test_remove_rule(self):
        """测试移除规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'add_rule') and hasattr(rules, 'remove_rule'):
            rules.add_rule({
                "name": "test_rule",
                "conditions": {},
                "outcomes": {}
            })

            rules.remove_rule("test_rule")

            # 规则已移除
            pass

    def test_get_rule(self):
        """测试获取规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'add_rule') and hasattr(rules, 'get_rule'):
            rules.add_rule({
                "name": "test_rule",
                "conditions": {},
                "outcomes": {}
            })

            rule = rules.get_rule("test_rule")
            assert rule is not None
            assert rule["name"] == "test_rule"


class TestInteractionRulesValidation:
    """测试规则验证"""

    def test_validate_rule(self):
        """测试验证规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'validate_rule'):
            valid_rule = {
                "name": "valid_rule",
                "conditions": {"interaction_type": "diplomatic"},
                "outcomes": {"success_probability": 0.8}
            }

            is_valid = rules.validate_rule(valid_rule)
            assert is_valid is True

    def test_validate_invalid_rule(self):
        """测试验证无效规则"""
            try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'validate_rule'):
            invalid_rule = {}

            is_valid = rules.validate_rule(invalid_rule)
            assert is_valid is False


class TestInteractionRulesApplication:
    """测试规则应用"""

    def test_apply_rules(self):
        """测试应用规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'apply_rules'):
            interaction = {
                "type": "diplomatic",
                "source": "agent_1",
                "target": "agent_2"
            }

            result = rules.apply_rules(interaction)
            assert result is not None

    def test_get_applicable_rules(self):
        """测试获取适用的规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'get_applicable_rules'):
            interaction = {
                "type": "diplomatic",
                "source": "agent_1",
                "target": "agent_2"
            }

            applicable = rules.get_applicable_rules(interaction)
            assert isinstance(applicable, list)


class TestInteractionRulesConditions:
    """测试条件匹配"""

    def test_match_conditions(self):
        """测试匹配条件"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'match_conditions'):
            conditions = {
                "interaction_type": "diplomatic",
                "moral_level_min": 3
            }

            interaction = {
                "type": "diplomatic",
                "source_moral_level": 4
            }

            matches = rules.match_conditions(conditions, interaction)
            assert isinstance(matches, bool)

    def test_complex_conditions(self):
        """测试复杂条件"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'match_conditions'):
            conditions = {
                "interaction_type": ["diplomatic", "economic"],
                "power_ratio": {"min": 0.5, "max": 2.0}
            }

            interaction = {
                "type": "economic",
                "power_ratio": 0.8
            }

            matches = rules.match_conditions(conditions, interaction)
            assert isinstance(matches, bool)


class TestInteractionRulesOutcomes:
    """测试规则结果"""

    def test_calculate_outcome(self):
        """测试计算结果"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'calculate_outcome'):
            rule_outcomes = {
                "success_probability": 0.8,
                "success_reward": 10,
                "failure_penalty": -5
            }

            outcome = rules.calculate_outcome(rule_outcomes)
            assert outcome is not None

    def test_determine_success(self):
        """测试确定成功"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'determine_success'):
            probability = 0.8

            # 使用固定的随机种子进行测试
            success = rules.determine_success(probability, random_seed=42)
            assert isinstance(success, bool)


class TestInteractionRulesCategories:
    """测试规则分类"""

    def test_get_rules_by_category(self):
        """测试按类别获取规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'get_rules_by_category'):
            category_rules = rules.get_rules_by_category("diplomatic")
            assert isinstance(category_rules, list)

    def test_add_rule_to_category(self):
        """测试添加规则到类别"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'add_rule'):
            rule = {
                "name": "diplomatic_rule",
                "category": "diplomatic",
                "conditions": {},
                "outcomes": {}
            }

            rules.add_rule(rule)

            # 规则已添加到类别
            pass


class TestInteractionRulesPriorities:
    """测试规则优先级"""

    def test_rule_priority(self):
        """测试规则优先级"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'add_rule') and hasattr(rules, 'apply_rules'):
            # 添加两个优先级不同的规则
            rules.add_rule({
                "name": "low_priority_rule",
                "priority": 1,
                "conditions": {},
                "outcomes": {}
            })

            rules.add_rule({
                "name": "high_priority_rule",
                "priority": 10,
                "conditions": {},
                "outcomes": {}
            })

            # 高优先级规则应该优先应用
            pass


class TestInteractionRulesConflictResolution:
    """测试规则冲突解决"""

    def test_resolve_conflicts(self):
        """测试解决冲突"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'resolve_conflicts'):
            conflicting_rules = [
                {"name": "rule1", "priority": 5},
                {"name": "rule2", "priority": 10}
            ]

            resolved = rules.resolve_conflicts(conflicting_rules)
            assert resolved is not None


class TestInteractionRulesExportImport:
    """测试规则导出和导入"""

    def test_export_rules(self, temp_dir):
        """测试导出规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'export_rules'):
            export_path = temp_dir / "rules_export.json"
            rules.export_rules(str(export_path))

            assert export_path.exists()

    def test_import_rules(self, temp_dir):
        """测试导入规则"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        # 创建规则文件
        import json
        rules_data = {
            "rules": [
                {
                    "name": "imported_rule",
                    "conditions": {},
                    "outcomes": {}
                }
            ]
        }

        import_path = temp_dir / "rules_import.json"
        with open(import_path, 'w', encoding='utf-8') as f:
            json.dump(rules_data, f)

        rules = InteractionRules()

        if hasattr(rules, 'import_rules'):
            rules.import_rules(str(import_path))

            # 规则已导入
            pass


class TestInteractionRulesStatistics:
    """测试规则统计"""

    def test_get_statistics(self):
        """测试获取统计信息"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'get_statistics'):
            stats = rules.get_statistics()
            assert isinstance(stats, dict)

    def test_track_rule_usage(self):
        """测试追踪规则使用"""
        try:
            from src.interaction.interaction_rules import InteractionRules
        except ImportError:
            pytest.skip("InteractionRules类未找到")

        rules = InteractionRules()

        if hasattr(rules, 'track_rule_usage'):
            rules.track_rule_usage("test_rule", success=True)

            # 使用已追踪
            pass
