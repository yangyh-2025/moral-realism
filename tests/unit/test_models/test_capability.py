"""
能力模型单元测试

测试Capability、HardPower、SoftPower类的核心功能：
- 初始化和验证
- 能力指数计算
- 能力层级判定
"""
import pytest
from src.models.capability import (
    HardPower,
    SoftPower,
    Capability,
    CapabilityTier,
    compare_capability,
    is_power_transition_possible,
    get_strategic_interests,
)


class TestHardPower:
    """测试HardPower硬实力类"""

    def test_hard_power_initialization_default(self):
        """测试使用默认值初始化HardPower"""
        hp = HardPower()
        assert hp.military_capability == 50.0
        assert hp.gdp_share == 2.0
        assert hp.technology_level == 50.0

    def test_hard_power_initialization_custom(self):
        """测试使用自定义值初始化HardPower"""
        hp = HardPower(
            military_capability=85.0,
            gdp_share=25.0,
            technology_level=90.0
        )
        assert hp.military_capability == 85.0
        assert hp.gdp_share == 25.0
        assert hp.technology_level == 90.0

    def test_hard_power_validation_valid(self):
        """测试有效值的验证"""
        hp = HardPower(
            military_capability=75.0,
            nuclear_capability=50.0,
            conventional_forces=60.0,
            force_projection=70.0,
            gdp_share=15.0,
            economic_growth=3.5,
            trade_volume=80.0,
            financial_influence=65.0,
            technology_level=70.0,
            military_technology=75.0,
            innovation_capacity=80.0,
            energy_access=60.0,
            strategic_materials=55.0
        )
        assert hp.validate() is True

    @pytest.mark.parametrize("attr,value", [
        ("military_capability", -1.0),
        ("military_capability", 101.0),
        ("gdp_share", -1.0),
        ("gdp_share", 101.0),
        ("technology_level", -5.0),
    ])
    def test_hard_power_validation_invalid(self, attr, value):
        """测试无效值的验证"""
        kwargs = {attr: value}
        with pytest.raises(ValueError):
            HardPower(**kwargs)

    def test_get_hard_power_index(self):
        """测试硬权力指数计算"""
        hp = HardPower(
            military_capability=80.0,
            nuclear_capability=70.0,
            conventional_forces=75.0,
            force_projection=85.0,
            gdp_share=20.0,
            economic_growth=4.0,
            trade_volume=80.0,
            financial_influence=75.0,
            technology_level=80.0,
            military_technology=85.0,
            innovation_capacity=80.0,
            energy_access=75.0,
            strategic_materials=70.0
        )

        index = hp.get_hard_power_index()
        assert 0 <= index <= 100
        assert index > 50  # 对于高能力值，指数应该较高

    def test_get_hard_power_index_edge_cases(self):
        """测试硬权力指数边界情况"""
        # 最低能力
        hp_low = HardPower(
            military_capability=0.0,
            gdp_share=0.0,
            technology_level=0.0
        )
        index_low = hp_low.get_hard_power_index()
        assert index_low == 0.0

        # 最高能力
        hp_high = HardPower(
            military_capability=100.0,
            gdp_share=100.0,
            technology_level=100.0,
            nuclear_capability=100.0,
            conventional_forces=100.0,
            force_projection=100.0,
            economic_growth=100.0,
            trade_volume=100.0,
            financial_influence=100.0,
            military_technology=100.0,
            innovation_capacity=100.0,
            energy_access=100.0,
            strategic_materials=100.0
        )
        index_high = hp_high.get_hard_power_index()
        assert index_high <= 100.0


class TestSoftPower:
    """测试SoftPower软实力类"""

    def test_soft_power_initialization_default(self):
        """测试使用默认值初始化SoftPower"""
        sp = SoftPower()
        assert sp.discourse_power == 50.0
        assert sp.allies_count == 0
        assert sp.diplomatic_support == 50.0

    def test_soft_power_initialization_custom(self):
        """测试使用自定义值初始化SoftPower"""
        sp = SoftPower(
            discourse_power=75.0,
            allies_count=10,
            diplomatic_support=80.0
        )
        assert sp.discourse_power == 75.0
        assert sp.allies_count == 10
        assert sp.diplomatic_support == 80.0

    def test_soft_power_validation_valid(self):
        """测试有效值的验证"""
        sp = SoftPower(
            discourse_power=70.0,
            narrative_control=65.0,
            media_influence=60.0,
            allies_count=15,
            ally_strength=70.0,
            network_position=75.0,
            diplomatic_support=80.0,
            moral_legitimacy=75.0,
            cultural_influence=70.0,
            un_influence=65.0,
            institutional_leadership=60.0
        )
        assert sp.validate() is True

    @pytest.mark.parametrize("attr,value", [
        ("discourse_power", -1.0),
        ("discourse_power", 101.0),
        ("allies_count", -1),
    ])
    def test_soft_power_validation_invalid(self, attr, value):
        """测试无效值的验证"""
        kwargs = {attr: value}
        with pytest.raises(ValueError):
            SoftPower(**kwargs)

    def test_get_soft_power_index(self):
        """测试软权力指数计算"""
        sp = SoftPower(
            discourse_power=80.0,
            narrative_control=75.0,
            media_influence=70.0,
            allies_count=20,
            ally_strength=80.0,
            network_position=75.0,
            diplomatic_support=85.0,
            moral_legitimacy=80.0,
            cultural_influence=75.0,
            un_influence=80.0,
            institutional_leadership=75.0
        )

        index = sp.get_soft_power_index()
        assert 0 <= index <= 100
        assert index > 50  # 对于高能力值，指数应该较高

    def test_get_soft_power_index_edge_cases(self):
        """测试软权力指数边界情况"""
        # 最低能力
        sp_low = SoftPower(
            discourse_power=0.0,
            diplomatic_support=0.0,
            cultural_influence=0.0
        )
        index_low = sp_low.get_soft_power_index()
        assert index_low == 0.0

        # 最高能力
        sp_high = SoftPower(
            discourse_power=100.0,
            narrative_control=100.0,
            media_influence=100.0,
            allies_count=100,
            ally_strength=100.0,
            network_position=100.0,
            diplomatic_support=100.0,
            moral_legitimacy=100.0,
            cultural_influence=100.0,
            un_influence=100.0,
            institutional_leadership=100.0
        )
        index_high = sp_high.get_soft_power_index()
        assert index_high <= 100.0


class TestCapability:
    """测试Capability综合能力类"""

    def test_capability_initialization(self):
        """测试Capability初始化"""
        hard = HardPower(military_capability=80.0, gdp_share=20.0, technology_level=75.0)
        soft = SoftPower(discourse_power=70.0, diplomatic_support=75.0)

        cap = Capability(agent_id="test_agent", hard_power=hard, soft_power=soft)

        assert cap.agent_id == "test_agent"
        assert cap.hard_power is hard
        assert cap.soft_power is soft
        assert cap.history == []

    def test_capability_tier_determination(self):
        """测试能力层级自动判定"""
        # 超级大国能力
        cap_superpower = Capability(
            agent_id="superpower",
            hard_power=HardPower(military_capability=95.0, gdp_share=25.0, technology_level=95.0),
            soft_power=SoftPower(discourse_power=90.0, diplomatic_support=90.0, allies_count=30)
        )
        assert cap_superpower.tier == CapabilityTier.T0_SUPERPOWER

        # 小国能力
        cap_small = Capability(
            agent_id="small",
            hard_power=HardPower(military_capability=20.0, gdp_share=1.0, technology_level=20.0),
            soft_power=SoftPower(discourse_power=25.0, diplomatic_support=30.0, allies_count=2)
        )
        assert cap_small.tier == CapabilityTier.T4_SMALL

    def test_get_capability_index(self):
        """测试综合能力指数计算"""
        hard = HardPower(military_capability=80.0, gdp_share=20.0, technology_level=80.0)
        soft = SoftPower(discourse_power=70.0, diplomatic_support=75.0)

        cap = Capability(agent_id="test", hard_power=hard, soft_power=soft)

        index = cap.get_capability_index()
        assert 0 <= index <= 100

    def test_get_tier(self):
        """测试获取能力层级"""
        cap = Capability(agent_id="test")
        tier = cap.get_tier()
        assert isinstance(tier, CapabilityTier)

    def test_record_history(self):
        """测试记录能力历史"""
        cap = Capability(agent_id="test")

        cap.record(1, {"event": "power_increase"})
        cap.record(2, {"event": "power_decrease"})

        history = cap.get_history()
        assert len(history) == 2
        assert history[0]["step"] == 1
        assert history[1]["step"] == 2

    def test_get_history(self):
        """测试获取历史记录"""
        cap = Capability(agent_id="test")

        cap.record(1)
        cap.record(2)

        history = cap.get_history()
        assert len(history) == 2

    def test_validate(self):
        """测试能力验证"""
        cap = Capability(agent_id="test")
        assert cap.validate() is True


class TestCapabilityTier:
    """测试能力层级枚举"""

    def test_capability_tier_values(self):
        """测试能力层级枚举值"""
        tiers = [
            CapabilityTier.T0_SUPERPOWER,
            CapabilityTier.T1_GREAT_POWER,
            CapabilityTier.T2_REGIONAL,
            CapabilityTier.T3_MEDIUM,
            CapabilityTier.T4_SMALL,
        ]

        values = [tier.value for tier in tiers]
        assert len(values) == 5
        assert len(set(values)) == 5  # 所有值唯一

    def test_capability_tier_comparison(self):
        """测试能力层级比较"""
        # 层级顺序：T4 < T3 < T2 < T1 < T0
        tier_order = [
            CapabilityTier.T4_SMALL,
            CapabilityTier.T3_MEDIUM,
            CapabilityTier.T2_REGIONAL,
            CapabilityTier.T1_GREAT_POWER,
            CapabilityTier.T0_SUPERPOWER,
        ]

        # 验证所有层级都在列表中
        all_tiers = list(CapabilityTier)
        for tier in all_tiers:
            assert tier in tier_order


class TestCapabilityComparisons:
    """测试能力比较函数"""

    def test_compare_capability(self):
        """测试比较两个代理的能力"""
        cap1 = Capability(
            agent_id="strong",
            hard_power=HardPower(military_capability=90.0, gdp_share=25.0, technology_level=90.0),
            soft_power=SoftPower(discourse_power=85.0, diplomatic_support=85.0)
        )

        cap2 = Capability(
            agent_id="weak",
            hard_power=HardPower(military_capability=40.0, gdp_share=5.0, technology_level=40.0),
            soft_power=SoftPower(discourse_power=35.0, diplomatic_support=40.0)
        )

        diff = compare_capability(cap1, cap2)
        assert diff > 0  # cap1更强

        # 反向比较
        diff_reverse = compare_capability(cap2, cap1)
        assert diff_reverse < 0  # cap2较弱
        assert diff_reverse == -diff

    def test_compare_equal_capability(self):
        """测试比较相同能力的代理"""
        hard = HardPower(military_capability=60.0, g.gdp_share=10.0, technology_level=60.0)
        soft = SoftPower(discourse_power=55.0, diplomatic_support=60.0)

        cap1 = Capability(agent_id="agent1", hard_power=hard, soft_power=soft)
        cap2 = Capability(agent_id="agent2", hard_power=hard, soft_power=soft)

        diff = compare_capability(cap1, cap2)
        assert diff == 0.0


class TestPowerTransition:
    """测试权力转移检查"""

    def test_is_power_transition_possible_valid(self):
        """测试合理的权力转移"""
        cap = Capability(agent_id="test", tier=CapabilityTier.T2_REGIONAL)

        # 相邻层级转移 - 有效
        assert is_power_transition_possible(cap, CapabilityTier.T1_GREAT_POWER) is True
        assert is_power_transition_possible(cap, CapabilityTier.T3_MEDIUM) is True

        # 跨越一个层级 - 有效
        assert is_power_transition_possible(cap, CapabilityTier.T0_SUPERPOWER) is True
        assert is_power_transition_possible(cap, CapabilityTier.T4_SMALL) is True

    def test_is_power_transition_possible_invalid(self):
        """测试不合理的权力转移"""
        cap_small = Capability(agent_id="small", tier=CapabilityTier.T4_SMALL)

        # 跨越3个层级 - 无效
        assert is_power_transition_possible(cap_small, CapabilityTier.T1_GREAT_POWER) is False

        cap_super = Capability(agent_id="super", tier=CapabilityTier.T0_SUPERPOWER)

        # 跨越3个层级 - 无效
        assert is_power_transition_possible(cap_super, CapabilityTier.T3_MEDIUM) is False

    def test_is_power_transition_possible_same_tier(self):
        """测试相同层级的转移"""
        cap = Capability(agent_id="test", tier=CapabilityTier.T2_REGIONAL)

        # 相同层级 - 有效
        assert is_power_transition_possible(cap, CapabilityTier.T2_REGIONAL) is True


class TestStrategicInterests:
    """测试战略利益获取"""

    def test_get_strategic_interests_all_tiers(self):
        """测试获取所有层级的战略利益"""
        all_tiers = [
            CapabilityTier.T0_SUPERPOWER,
            CapabilityTier.T1_GREAT_POWER,
            CapabilityTier.T2_REGIONAL,
            CapabilityTier.T3_MEDIUM,
            CapabilityTier.T4_SMALL,
        ]

        for tier in all_tiers:
            interests = get_strategic_interests(tier)
            assert isinstance(interests, list)
            assert len(interests) > 0

    def test_get_strategic_interests_content(self):
        """测试战略利益内容"""
        superpower_interests = get_strategic_interests(CapabilityTier.T0_SUPERPOWER)
        assert "global hegemony maintenance" in superpower_interests

        small_interests = get_strategic_interests(CapabilityTier.T4_SMALL)
        assert "survival" in small_interests
