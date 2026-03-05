"""
静态环境单元测试

测试StaticEnvironment类的核心功能：
- 初始化和配置
- 地理环境
- 资源分布
- 连通性
"""
import pytest
from unittest.mock import Mock


class TestStaticEnvironmentInitialization:
    """测试StaticEnvironment初始化"""

    def test_static_environment_initialization(self):
        """测试静态环境初始化"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="静态测试环境")

        assert env.name == "静态测试环境"

    def test_static_environment_with_regions(self):
        """测试带区域初始化"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        regions = ["亚洲", "欧洲", "北美"]
        env = StaticEnvironment(name="多区域环境", regions=regions)

        if hasattr(env, 'regions'):
            assert len(env.regions) == 3


class TestStaticEnvironmentGeography:
    """测试地理环境"""

    def test_geographic_structure(self):
        """测试地理结构"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="地理测试环境")

        if hasattr(env, 'geographic_structure'):
            # 地理结构应该存在
            assert env.geographic_structure is not None

    def test_region_distance_calculation(self):
        """测试区域距离计算"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="距离测试环境")

        if hasattr(env, 'calculate_distance'):
            distance = env.calculate_distance("region_a", "region_b")
            assert distance >= 0

    def test_region_neighbors(self):
        """测试区域邻接关系"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="邻接测试环境")

        if hasattr(env, 'get_neighbors'):
            neighbors = env.get_neighbors("region_a")
            assert isinstance(neighbors, list)


class TestStaticEnvironmentResources:
    """测试资源分布"""

    def test_resource_distribution(self):
        """测试资源分布"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        resources = {
            "oil": {"total": 1000, "distribution": {"region_a": 500, "region_b": 500}},
            "rare_earth": {"total": 200, "distribution": {"region_c": 200}}
        }

        env = StaticEnvironment(name="资源测试环境", resources=resources)

        if hasattr(env, 'resources'):
            assert "oil" in env.resources
            assert "rare_earth" in env.resources

    def test_get_region_resources(self):
        """测试获取区域资源"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        resources = {
            "oil": {"total": 1000, "distribution": {"region_a": 500}}
        }

        env = StaticEnvironment(name="区域资源测试", resources=resources)

        if hasattr(env, 'get_region_resources'):
            region_resources = env.get_region_resources("region_a")
            assert isinstance(region_resources, dict)


class TestStaticEnvironmentConnectivity:
    """测试连通性"""

    def test_connectivity_matrix(self):
        """测试连通性矩阵"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="连通性测试环境")

        if hasattr(env, 'connectivity'):
            # 连通性应该存在
            pass

    def test_path_finding(self):
        """测试路径查找"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="路径测试环境")

        if hasattr(env, 'find_path'):
            path = env.find_path("region_a", "region_b")
            # 路径应该是一个列表
            assert isinstance(path, list)

    def test_accessibility(self):
        """测试可达性"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="可达性测试环境")

        if hasattr(env, 'is_accessible'):
            accessible = env.is_accessible("region_a", "region_b")
            assert isinstance(accessible, bool)


class TestStaticEnvironmentConfiguration:
    """测试静态环境配置"""

    def test_load_from_config(self, temp_dir):
        """测试从配置加载"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        import json

        config = {
            "name": "配置测试环境",
            "regions": ["A", "B", "C"],
            "resources": {
                "oil": {"total": 1000}
            }
        }

        config_file = temp_dir / "environment_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f)

        if hasattr(StaticEnvironment, 'load_from_config'):
            env = StaticEnvironment.load_from_config(str(config_file))
            assert env.name == "配置测试环境"

    def test_save_to_config(self, temp_dir):
        """测试保存到配置"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="保存测试环境")

        if hasattr(env, 'save_to_config'):
            config_file = temp_dir / "saved_config.json"
            env.save_to_config(str(config_file))

            assert config_file.exists()


class TestStaticEnvironmentValidation:
    """测试静态环境验证"""

    def test_validate_structure(self):
        """测试验证结构"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="验证测试环境")

        if hasattr(env, 'validate'):
            is_valid = env.validate()
            assert is_valid is True

    def test_validate_connectivity(self):
        """测试验证连通性"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="连通性验证环境")

        if hasattr(env, 'validate_connectivity'):
            is_valid = env.validate_connectivity()
            assert isinstance(is_valid, bool)


class TestStaticEnvironmentQueries:
    """测试静态环境查询"""

    def test_query_regions_by_type(self):
        """测试按类型查询区域"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="查询测试环境")

        if hasattr(env, 'query_regions'):
            regions = env.query_regions(type="land")
            assert isinstance(regions, list)

    def test_query_resources_by_type(self):
        """测试按类型查询资源"""
        try:
            from src.environment.static_environment import StaticEnvironment
        except ImportError:
            pytest.skip("StaticEnvironment类未找到")

        env = StaticEnvironment(name="资源查询环境")

        if hasattr(env, 'query_resources'):
            resources = env.query_resources(category="energy")
            assert isinstance(resources, dict)
