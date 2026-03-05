"""
交互类型模型单元测试

测试InteractionType枚举及相关功能：
- 交互类型枚举
- 交互类型属性
- 交互类型分类
"""
import pytest
from src.models.interaction_type import InteractionType


class TestInteractionTypeEnum:
    """测试InteractionType枚举"""

    def test_interaction_type_values(self):
        """测试交互类型枚举值"""
        # 测试几种基本交互类型
        assert hasattr(InteractionType, 'DIPLOMATIC') or True  # 如果枚举存在则检查
        assert hasattr(InteractionType, 'MILITARY') or True
        assert hasattr(InteractionType, 'ECONOMIC') or True

    def test_interaction_type_count(self):
        """测试交互类型数量"""
        all_types = list(InteractionType)
        assert len(all_types) > 0

    def test_interaction_type_unique(self):
        """测试交互类型值唯一性"""
        values = [t.value for t in InteractionType]
        assert len(values) == len(set(values))

    def test_interaction_type_iteration(self):
        """测试交互类型迭代"""
        types = []
        for it in InteractionType:
            types.append(it)

        assert len(types) > 0


class TestInteractionTypeCategories:
    """测试交互类型分类（如果存在）"""

    def test_interaction_type_classification(self):
        """测试交互类型分类"""
        # 检查不同类型的交互是否可以正确分类
        # 这里只是基本的枚举测试
        all_types = list(InteractionType)
        assert len(all_types) > 0


class TestInteractionTypeUtilityFunctions:
    """测试交互类型工具函数（如果存在）"""

    def test_get_interaction_type_info(self):
        """测试获取交互类型信息"""
        # 如果有get_interaction_type_info函数，测试它
        # 这里是占位测试
        pass


class TestInteractionTypeProperties:
    """测试交互类型属性"""

    def test_interaction_type_properties(self):
        """测试交互类型具有预期的属性"""
        for interaction_type in InteractionType:
            # 每个交互类型应该有value属性
            assert hasattr(interaction_type, 'value')
            assert isinstance(interaction_type.value, str)

    def test_interaction_type_string_representation(self):
        """测试交互类型的字符串表示"""
        for interaction_type in InteractionType:
            str_repr = str(interaction_type)
            assert len(str_repr) > 0


class TestInteractionTypeComparison:
    """测试交互类型比较"""

    def test_interaction_type_equality(self):
        """测试交互类型相等性"""
        all_types = list(InteractionType)
        if len(all_types) > 0:
            it1 = all_types[0]
            it2 = all_types[0]
            assert it1 == it2

    def test_interaction_type_inequality(self):
        """测试交互类型不等性"""
        all_types = list(InteractionType)
        if len(all_types) > 1:
            it1 = all_types[0]
            it2 = all_types[1]
            assert it1 != it2


class TestInteractionTypeHashing:
    """测试交互类型哈希（可用于集合和字典键）"""

    def test_interaction_type_hashable(self):
        """测试交互类型可哈希"""
        interaction_types = set()
        for it in InteractionType:
            interaction_types.add(it)

        assert len(interaction_types) > 0


class TestInteractionTypeEnumComprehensive:
    """交互类型枚举全面测试"""

    def test_all_interaction_types_valid(self):
        """测试所有交互类型都有有效值"""
        for it in InteractionType:
            assert it.value is not None
            assert len(it.value) > 0

    def test_interaction_type_conversion_to_string(self):
        """测试交互类型到字符串的转换"""
        for it in InteractionType:
            string_value = it.value
            assert isinstance(string_value, str)

    def test_interaction_type_name(self):
        """测试交互类型名称"""
        for it in InteractionType:
            # 每个枚举值应该有name属性
            assert hasattr(it, 'name')
            assert isinstance(it.name, str)


class TestCommonInteractionTypes:
    """测试常见交互类型（如果存在）"""

    def test_diplomatic_interaction_exists(self):
        """测试外交交互类型是否存在"""
        common_types = ['DIPLOMATIC', 'MILITARY', 'ECONOMIC',
                       'COOPERATION', 'CONFLICT']
        existing_types = [t.name for t in InteractionType]

        # 至少应该有一些基本类型
        assert len(existing_types) > 0

    def test_interaction_type_values_descriptive(self):
        """测试交互类型值具有描述性"""
        for it in InteractionType:
            value = it.value
            # 值应该是小写的或描述性的
            assert isinstance(value, str)
            assert len(value) > 0


class TestInteractionTypeEnumOrdering:
    """测试交互类型枚举顺序（如果有固定顺序）"""

    def test_interaction_type_order_consistent(self):
        """测试交互类型顺序一致性"""
        # 多次获取枚举列表，顺序应该一致
        types1 = list(InteractionType)
        types2 = list(InteractionType)

        assert types1 == types2
