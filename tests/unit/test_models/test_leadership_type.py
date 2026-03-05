"""
领导类型模型单元测试

测试LeadershipType枚举、LeadershipProfile类及相关函数：
- 领导类型枚举
- 领导配置文件属性
- 领导配置文件验证
- 领导配置文件获取
- 道德标准比较
"""
import pytest
from src.models.leadership_type import (
    LeadershipType,
    LeadershipProfile,
    LEADERSHIP_PROFILES,
    get_leadership_profile,
    get_all_leadership_types,
    compare_moral_standards,
)


class TestLeadershipTypeEnum:
    """测试LeadershipType枚举"""

    def test_leadership_type_values(self):
        """测试领导类型枚举值"""
        assert LeadershipType.WANGDAO.value == "wangdao"
        assert LeadershipType.HEGEMON.value == "hegemon"
        assert LeadershipType.QIANGQUAN.value == "qiangquan"
        assert LeadershipType.HUNYONG.value == "hunyong"

    def test_leadership_type_count(self):
        """测试领导类型数量"""
        all_types = list(LeadershipType)
        assert len(all_types) == 4

    def test_leadership_type_unique(self):
        """测试领导类型值唯一性"""
        values = [t.value for t in LeadershipType]
        assert len(values) == len(set(values))

    def test_leadership_type_iteration(self):
        """测试领导类型迭代"""
        types = []
        for lt in LeadershipType:
            types.append(lt)

        assert len(types) == 4
        assert LeadershipType.WANGDAO in types
        assert LeadershipType.HEGEMON in types
        assert LeadershipType.QIANGQUAN in types
        assert LeadershipType.HUNYONG in types


class TestLeadershipProfile:
    """测试LeadershipProfile类"""

    def test_leadership_profile_basic_attributes(self):
        """测试领导配置文件基本属性"""
        profile = LeadershipProfile(
            leadership_type=LeadershipType.WANGDAO,
            name="Test Profile",
            name_zh="测试配置",
            description="测试描述",
            moral_standard=0.8,
            core_interest=0.7,
            marginal_interest_weight=0.3,
            moral_consideration_weight=0.8,
            prefers_diplomatic_solution=True,
            uses_moral_persuasion=True,
            accepts_moral_constraints=True,
            prioritizes_reputation=True,
        )

        assert profile.leadership_type == LeadershipType.WANGDAO
        assert profile.name == "Test Profile"
        assert profile.name_zh == "测试配置"
        assert profile.moral_standard == 0.8
        assert profile.prefers_diplomatic_solution is True

    def test_leadership_profile_validation_valid(self):
        """测试有效配置验证"""
        profile = LeadershipProfile(
            leadership_type=LeadershipType.HEGEMON,
            name="Valid Profile",
            name_zh="有效配置",
            description="有效描述",
            moral_standard=0.5,
            core_interest_weight=0.9,
            marginal_interest_weight=0.5,
            moral_consideration_weight=0.4,
            prefers_diplomatic_solution=False,
            uses_moral_persuasion=False,
            accepts_moral_constraints=False,
            prioritizes_reputation=True,
        )
        assert profile.validate() is True

    @pytest.mark.parametrize("attr,value", [
        ("moral_standard", -0.1),
        ("moral_standard", 1.1),
        ("core_interest_weight", -0.1),
        ("core_interest_weight", 1.1),
        ("marginal_interest_weight", -0.1),
        ("marginal_interest_weight", 1.1),
        ("moral_consideration_weight", -0.1),
        ("moral_consideration_weight", 1.1),
    ])
    def test_leadership_profile_validation_invalid(self, attr, value):
        """测试无效配置验证"""
        profile = LeadershipProfile(
            leadership_type=LeadershipType.WANGDAO,
            name="Invalid Profile",
            name_zh="无效配置",
            description="无效描述",
            moral_standard=0.5,
            core_interest_weight=0.5,
            marginal_interest_weight=0.5,
            moral_consideration_weight=0.5,
            prefers_diplomatic_solution=True,
            uses_moral_persuasion=True,
            accepts_moral_constraints=True,
            prioritizes_reputation=True,
        )

        # 使用setattr设置无效值
        setattr(profile, attr, value)

        with pytest.raises(ValueError):
            profile.validate()

    def test_leadership_profile_default_lists(self):
        """测试默认禁止和优先行动列表"""
        profile = LeadershipProfile(
            leadership_type=LeadershipType.WANGDAO,
            name="Default Lists",
            name_zh="默认列表",
            description="测试默认列表",
            moral_standard=0.5,
            core_interest_weight=0.5,
            marginal_interest_weight=0.5,
            moral_consideration_weight=0.5,
            prefers_diplomatic_solution=True,
            uses_moral_persuasion=True,
            accepts_moral_constraints=True,
            prioritizes_reputation=True,
        )

        assert isinstance(profile.prohibited_actions, list)
        assert isinstance(profile.prioritized_actions, list)


class TestWangdaoProfile:
    """测试道义型领导配置文件"""

    def test_wangdao_profile_exists(self):
        """测试道义型配置文件存在"""
        assert LeadershipType.WANGDAO in LEADERSHIP_PROFILES

    def test_wangdao_profile_attributes(self):
        """测试道义型配置文件属性"""
        profile = LEADERSHIP_PROFILES[LeadershipType.WANGDAO]

        assert profile.leadership_type == LeadershipType.WANGDAO
        assert profile.name_zh == "道义型领导"
        assert profile.moral_standard >= 0.8  # 高道德标准
        assert profile.prefers_diplomatic_solution is True
        assert profile.uses_moral_persuasion is True
        assert profile.accepts_moral_constraints is True
        assert profile.prioritizes_reputation is True

    def test_wangdao_profile_prohibited_actions(self):
        """测试道义型禁止行动"""
        profile = LEADERSHIP_PROFILES[LeadershipType.WANGDAO]

        assert "military aggression" in profile.prohibited_actions
        assert "unilateral intervention" in profile.prohibited_actions

    def test_wangdao_profile_prioritized_actions(self):
        """测试道义型优先行动"""
        profile = LEADERSHIP_PROFILES[LeadershipType.WANGDAO]

        assert "multilateral cooperation" in profile.prioritized_actions
        assert "peaceful dispute resolution" in profile.prioritized_actions


class TestHegemonProfile:
    """测试传统霸权配置文件"""

    def test_hegemon_profile_exists(self):
        """测试霸权配置文件存在"""
        assert LeadershipType.HEGEMON in LEADERSHIP_PROFILES

    def test_hegemon_profile_attributes(self):
        """测试霸权配置文件属性"""
        profile = LEADERSHIP_PROFILES[LeadershipType.HEGEMON]

        assert profile.leadership_type == LeadershipType.HEGEMON
        assert profile.name_zh == "传统霸权"
        assert profile.moral_standard >= 0.4 and profile.moral_standard <= 0.6  # 中等道德标准
        assert profile.core_interest_weight >= 0.8  # 高核心利益权重

    def test_hegemon_profile_prioritized_actions(self):
        """测试霸权优先行动"""
        profile = LEADERSHIP_PROFILES[LeadershipType.HEGEMON]

        assert "maintain sphere of influence" in profile.prioritized_actions
        assert "strengthen alliances" in profile.prioritized_actions


class TestQiangquanProfile:
    """测试强权型领导配置文件"""

    def test_qiangquan_profile_exists(self):
        """测试强权型配置文件存在"""
        assert LeadershipType.QIANGQUAN in LEADERSHIP_PROFILES

    def test_qiangquan_profile_attributes(self):
        """测试强权型配置文件属性"""
        profile = LEADERSHIP_PROFILES[LeadershipType.QIANGQUAN]

        assert profile.leadership_type == LeadershipType.QIANGQUAN
        assert profile.name_zh == "强权型领导"
        assert profile.moral_standard <= 0.3  # 低道德标准
        assert profile.core_interest_weight >= 0.9  # 极高核心利益权重
        assert profile.moral_consideration_weight <= 0.2  # 极低道德考虑
        assert profile.prioritizes_reputation is False

    def test_qiangquan_profile_prioritized_actions(self):
        """测试强权型优先行动"""
        profile = LEADERSHIP_PROFILES[LeadershipType.QIANGQUAN]

        assert "maximize national power" in profile.prioritized_actions
        assert "expand influence" in profile.prioritized_actions


class TestHunyongProfile:
    """测试混合型/合作型领导配置文件"""

    def test_hunyong_profile_exists(self):
        """测试混合型配置文件存在"""
        assert LeadershipType.HUNYONG in LEADERSHIP_PROFILES

    def test_hunyong_profile_attributes(self):
        """测试混合型配置文件属性"""
        profile = LEADERSHIP_PROFILES[LeadershipType.HUNYONG]

        assert profile.leadership_type == LeadershipType.HUNYONG
        assert profile.name_zh == "混合型/合作型领导"
        assert profile.moral_standard >= 0.5  # 中等偏上道德标准
        assert profile.prefers_diplomatic_solution is True
        assert profile.accepts_moral_constraints is True

    def test_hunyong_profile_prioritized_actions(self):
        """测试混合型优先行动"""
       ) profile = LEADERSHIP_PROFILES[LeadershipType.HUNYONG]

        assert "compromise and accommodation" in profile.prioritized_actions
        assert "conflict avoidance" in profile.prioritized_actions


class TestGetLeadershipProfile:
    """测试get_leadership_profile函数"""

    def test_get_wangdao_profile(self):
        """测试获取道义型配置文件"""
        profile = get_leadership_profile(LeadershipType.WANGDAO)

        assert profile.leadership_type == LeadershipType.WANGDAO
        assert profile.name_zh == "道义型领导"

    def test_get_hegemon_profile(self):
        """测试获取霸权配置文件"""
        profile = get_leadership_profile(LeadershipType.HEGEMON)

        assert profile.leadership_type == LeadershipType.HEGEMON
        assert profile.name_zh == "传统霸权"

    def test_get_qiangquan_profile(self):
        """测试获取强权型配置文件"""
        profile = get_leadership_profile(LeadershipType.QIANGQUAN)

        assert profile.leadership_type == LeadershipType.QIANGQUAN
        assert profile.name_zh == "强权型领导"

    def test_get_hunyong_profile(self):
        """测试获取混合型配置文件"""
        profile = get_leadership_profile(LeadershipType.HUNYONG)

        assert profile.leadership_type == LeadershipType.HUNYONG
        assert profile.name_zh == "混合型/合作型领导"

    def test_get_invalid_profile(self):
        """测试获取无效配置文件"""
        # 创建一个假的领导类型
        fake_type = "invalid_type"

        with pytest.raises(ValueError, match="Unknown leadership type"):
            get_leadership_profile(fake_type)


class TestGetAllLeadershipTypes:
    """测试get_all_leadership_types函数"""

    def test_get_all_leadership_types_count(self):
        """测试获取所有领导类型数量"""
        all_types = get_all_leadership_types()
        assert len(all_types) == 4

    def test_get_all_leadership_types_content(self):
        """测试获取所有领导类型内容"""
        all_types = get_all_leadership_types()

        assert LeadershipType.WANGDAO in all_types
        assert LeadershipType.HEGEMON in all_types
        assert LeadershipType.QIANGQUAN in all_types
        assert LeadershipType.HUNYONG in all_types

    def test_get_all_leadership_types_type(self):
        """测试返回类型"""
        all_types = get_all_leadership_types()
        assert isinstance(all_types, list)


class TestCompareMoralStandards:
    """测试compare_moral_standards函数"""

    def test_compare_wangdao_qiangquan(self):
        """测试比较道义型和强权型的道德标准"""
        diff = compare_moral_standards(LeadershipType.WANGDAO, LeadershipType.QIANGQUAN)

        assert diff > 0  # 道义型道德标准更高
        assert diff > 0.5  # 差异应该很明显

    def test_compare_qiangquan_wangdao(self):
        """测试比较强权型和道义型的道德标准"""
        diff = compare_moral_standards(LeadershipType.QIANGQUAN, LeadershipType.WANGDAO)

        assert diff < 0  # 强权型道德标准较低
        assert diff < -0.5  # 差异应该很明显

    def test_compare_same_type(self):
        """测试比较相同类型的道德标准"""
        diff = compare_moral_standards(LeadershipType.WANGDAO, LeadershipType.WANGDAO)

        assert diff == 0.0

    def test_compare_wangdao_hegemon(self):
        """测试比较道义型和霸权的道德标准"""
        diff = compare_moral_standards(LeadershipType.WANGDAO, LeadershipType.HEGEMON)

        assert diff > 0  # 道义型道德标准高于霸权

    def test_compare_hegemon_qiangquan(self):
        """测试比较霸权和强权型的道德标准"""
        diff = compare_moral_standards(LeadershipType.HEGEMON, LeadershipType.QIANGQUAN)

        assert diff > 0  # 霸权道德标准高于强权型

    def test_moral_standard_ordering(self):
        """测试道德标准顺序"""
        # 道义型 > 混合型 > 霸权 > 强权型
        wangdao_vs_hegemon = compare_moral_standards(
            LeadershipType.WANGDAO, LeadershipType.HEGEMON
        )
        hegemon_vs_qiangquan = compare_moral_standards(
            LeadershipType.HEGEMON, LeadershipType.QIANGQUAN
        )

        assert wangdao_vs_hegemon > 0
        assert hegemon_vs_qiangquan > 0


class TestProfilePromptTemplates:
    """测试配置文件提示词模板"""

    def test_wangdao_decision_prompt_template(self):
        """测试道义型决策提示词模板"""
        profile = LEADERSHIP_PROFILES[LeadershipType.WANGDAO]

        assert "Wangdao" in profile.decision_prompt_template
        assert "moral principles" in profile.decision_prompt_template
        assert "{situation}" in profile.decision_prompt_template

    def test_hegemon_decision_prompt_template(self):
        """测试霸权决策提示词模板"""
        profile = LEADERSHIP_PROFILES[LeadershipType.HEGEMON]

        assert "Hegemon" in profile.decision_prompt_template
        assert "hegemonic position" in profile.decision_prompt_template
        assert "{situation}" in profile.decision_prompt_template

    def test_qiangquan_decision_prompt_template(self):
        """测试强权型决策提示词模板"""
        profile = LEADERSHIP_PROFILES[LeadershipType.QIANGQUAN]

        assert "Power-seeking" in profile.decision_prompt_template
        assert "maximizing national power" in profile.decision_prompt_template
        assert "{situation}" in profile.decision_prompt_template

    def test_hunyong_decision_prompt_template(self):
        """测试混合型决策提示词模板"""
        profile = LEADERSHIP_PROFILES[LeadershipType.HUNYONG]

        assert "Hunyong" in profile.decision_prompt_template
        assert "avoiding confrontation" in profile.decision_prompt_template
        assert "{situation}" in profile.decision_prompt_template

    def test_response_prompt_template_format(self):
        """测试响应提示词模板格式"""
        for leadership_type in LeadershipType:
            profile = LEADERSHIP_PROFILES[leadership_type]

            assert "{sender}" in profile.response_prompt_template
            assert "{proposal}" in profile.response_prompt_template
            assert "{affected_interests}" in profile.response_prompt_template
