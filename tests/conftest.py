"""
Pytest全局配置和共享fixtures
提供测试所需的通用工具、模拟对象和测试环境配置
"""
import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from typing import Dict, Any, Generator, Optional
from unittest.mock import Mock, AsyncMock, patch
import pytest
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入项目模块（如果可用）
try:
    from src.models.agent_model import Agent
    from src.models.capability import Capability, HardPower, SoftPower
    from src.models.leadership_type import LeadershipType, LeadershipProfile
    from src.models.interaction_type import InteractionType
    from src.environment.rule_environment import RuleEnvironment
    from src.core.llm_engine import LLMEngine, LLMConfig
    from src.workflow.simulation_controller import SimulationController
    from src.interaction.interaction_manager import InteractionManager
    from src.metrics.metrics_calculator import MetricsCalculator
    from src.agents.great_power_agent import GreatPowerAgent
    from src.agents.small_state_agent import SmallStateAgent
    PROJECT_MODULES_AVAILABLE = True
except ImportError:
    PROJECT_MODULES_AVAILABLE = False


# ============================================================================
# Pytest配置和钩子
# ============================================================================

def pytest_configure(config):
    """Pytest配置钩子"""
    # 添加自定义标记
    config.addinivalue_line("markers", "slow: 运行较慢的测试")
    config.addinivalue_line("markers", "security: 安全检查测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "unit: 单元测试")
")
    config.addinivalue_line("markers", "stability: 稳定性测试")


def pytest_collection_modifyitems(config, items):
    """修改测试集合，添加默认标记"""
    for item in items:
        # 根据文件路径添加默认标记
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "stability" in str(item.fspath):
            item.add_marker(pytest.mark.stability)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环，用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# 临时目录和测试环境
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    创建临时测试目录
    测试结束后自动清理
    """
    temp = Path(tempfile.mkdtemp())
    yield temp
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def test_data_dir(temp_dir: Path) -> Path:
    """创建测试数据目录"""
    data_dir = temp_dir / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def test_checkpoints_dir(temp_dir: Path) -> Path:
    """创建测试检查点目录"""
    checkpoints_dir = temp_dir / "checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)
    return checkpoints_dir


@pytest.fixture
def test_logs_dir(temp_dir: Path) -> Path:
    """创建测试日志目录"""
    logs_dir = temp_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


# ============================================================================
# 环境变量和配置
# ============================================================================

@pytest.fixture
def mock_env_vars() -> Generator[Dict[str, str], None, None]:
    """
    设置测试用的环境变量
    自动恢复原始环境变量
    """
    original_env = os.environ.copy()

    test_env = {
        "OPENAI_API_KEY": "test-api-key-12345",
        "OPENAI_API_BASE": "https://api.openai.com/v1",
        "LLM_MODEL": "gpt-4",
        "LLM_TEMPERATURE": "0.7",
        "LLM_MAX_TOKENS": "2000",
        "LOG_LEVEL": "DEBUG",
        "PROJECT_ROOT": str(project_root),
    }

    os.environ.update(test_env)
    yield test_env

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def test_config() -> Dict[str, Any]:
    """提供测试配置"""
    return {
        "simulation": {
            "name": "test_simulation",
            "total_rounds": 10,
            "agents": [],
        },
        "llm": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 60,
        },
        "environment": {
            "type": "rule_based",
            "initial_order_level": 3,
        },
        "metrics": {
            "enabled": True,
            "save_interval": 1,
        },
    }


# ============================================================================
# 模拟对象和Mock
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """模拟LLM API响应"""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "thought": "Test thought",
                        "action": "observe",
                        "parameters": {}
                    })
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        },
        "model": "gpt-4",
    }


@pytest.fixture
def mock_openai_client(mock_llm_response):
    """模拟OpenAI客户端"""
    client = AsyncMock()
    client.chat.completions.create = AsyncMock(return_value=mock_llm_response)
    return client


@pytest.fixture
def mock_llm_engine():
    """模拟LLM引擎"""
    engine = Mock()
    engine.generate = AsyncMock(return_value="test response")
    engine.generate_with_history = AsyncMock(return_value="test response")
    engine.batch_generate = AsyncMock(return_value=["response1", "response2"])
    return engine


@pytest.fixture
def mock_interaction_manager():
    """模拟交互管理器"""
    manager = Mock()
    manager.execute_interaction = AsyncMock(return_value={
        "success": True,
        "message": "Interaction completed"
    })
    manager.broadcast = AsyncMock(return_value={
        "success": True,
        "receivers": ["agent1", "agent2"]
    })
    return manager


@pytest.fixture
def mock_metrics_calculator():
    """模拟指标计算器"""
    calculator = Mock()
    calculator.calculate_agent_metrics = Mock(return_value={
        "power_index": 0.75,
        "influence": 0.6,
        "stability": 0.8
    })
    calculator.calculate_system_metrics = Mock(return_value={
        "total_power": 10.0,
        "power_concentration": 0.4,
        "order_level": 3
    })
    return calculator


# ============================================================================
# 测试代理 fixtures
# ============================================================================

@pytest.fixture
def hard_power():
    """创建测试用的硬实力对象"""
    return HardPower(
        military=85.0,
        economic=75.0,
        technological=80.0,
        population=90.0
    )


@pytest.fixture
def soft_power():
    """创建测试用的软实力对象"""
    return SoftPower(
        cultural=70.0,
        diplomatic=80.0,
        normative=65.0
    )


@pytest.fixture
def capability(hard_power, soft_power):
    """创建测试用的能力对象"""
    return Capability(
        hard_power=hard_power,
        soft_power=soft_power,
        name="测试能力"
    )


@pytest.fixture
def leadership_profile():
    """创建测试用的领导力配置文件"""
    return LeadershipProfile(
        type=LeadershipType.REALIST,
        moral_flexibility=0.3,
        strategic_focus=0.8,
        risk_tolerance=0.5,
        description="现实主义领导力配置文件"
    )


@pytest.fixture
def test_agent_base(capability, leadership_profile):
    """创建测试用的基础代理对象"""
    if not PROJECT_MODULES_AVAILABLE:
        pytest.skip("项目模块不可用")

    return Agent(
        agent_id="test_agent_1",
        name="测试代理",
        capability=capability,
        leadership_profile=leadership_profile,
        initial_moral_level=3
    )


@pytest.fixture
def great_power_agent(capability):
    """创建测试用的大国代理"""
    if not PROJECT_MODULES_AVAILABLE:
        pytest.skip("项目模块不可用")

    profile = LeadershipProfile(
        type=LeadershipType.REALIST,
        moral_flexibility=0.3,
        strategic_focus=0.8,
        risk_tolerance=0.5,
        description="现实主义大国"
    )

    return GreatPowerAgent(
        agent_id="usa",
        name="美国",
        capability=capability,
        leadership_profile=profile,
        initial_moral_level=3,
        interests=["全球领导", "地区安全", "经济繁荣"]
    )


@pytest.fixture
def small_state_agent():
    """创建测试用的小国代理"""
    if not PROJECT_MODULES_AVAILABLE:
        pytest.skip("项目模块不可用")

    capability = Capability(
        hard_power=HardPower(military=40, economic=45, technological=30, population=35),
        soft_power=SoftPower(cultural=50, diplomatic=60, normative=45),
        name="小国能力"
    )

    profile = LeadershipProfile(
        type=LeadershipType.DEFENSIVE,
        moral_flexibility=0.5,
        strategic_focus=0.6,
        risk_tolerance=0.3,
        description="防御性小国"
    )

    return SmallStateAgent(
        agent_id="small_state_1",
        name="小国1",
        capability=capability,
        leadership_profile=profile,
        initial_moral_level=4,
        region="东亚",
        alignment="non_aligned"
    )


@pytest.fixture
def test_agents(great_power_agent, small_state_agent):
    """提供一组测试代理"""
    return [great_power_agent, small_state_agent]


# ============================================================================
# 测试环境 fixtures
# ============================================================================

@pytest.fixture
def rule_environment():
    """创建测试用的规则环境"""
    if not PROJECT_MODULES_AVAILABLE:
        pytest.skip("项目模块不可用")

    return RuleEnvironment(
        name="测试环境",
        initial_order_level=3,
        max_order_level=5,
        min_order_level=1
    )


# ============================================================================
# 测试工作流 fixtures
# ============================================================================

@pytest.fixture
def simulation_controller(test_agents, rule_environment, mock_llm_engine):
    """创建测试用的模拟控制器"""
    if not PROJECT_MODULES_AVAILABLE:
        pytest.skip("项目模块不可用")

    return SimulationController(
        agents=test_agents,
        environment=rule_environment,
        llm_engine=mock_llm_engine,
        total_rounds=10,
        name="test_simulation"
    )


# ============================================================================
# 测试数据 fixtures
# ============================================================================

@pytest.fixture
def sample_agent_data():
    """示例代理数据"""
    return {
        "agent_id": "agent_1",
        "name": "示例代理",
        "capability": {
            "hard_power": {"military": 80, "economic": 75, "technological": 70, "population": 85},
            "soft_power": {"cultural": 65, "diplomatic": 70, "normative": 60}
        },
        "leadership_type": "realist",
        "moral_level": 3,
        "history": []
    }


@pytest.fixture
def sample_metrics_data():
    """示例指标数据"""
    return {
        "round": 1,
        "timestamp": "2024-01-01T00:00:00",
        "agents": {
            "agent_1": {"power_index": 0.75, "influence": 0.6},
            "agent_2": {"power_index": 0.65, "influence": 0.5}
        },
        "system": {
            "total_power": 10.0,
            "power_concentration": 0.4,
            "order_level": 3
        }
    }


@pytest.fixture
def sample_interaction_record():
    """示例交互记录"""
    return {
        "interaction_id": "interaction_1",
        "source": "agent_1",
        "target": "agent_2",
        "type": "diplomatic",
        "content": "外交沟通",
        "timestamp": "2024-01-01T00:00:00",
        "outcome": "success"
    }


# ============================================================================
# 数据库和文件系统模拟
# ============================================================================

@pytest.fixture
def mock_database(temp_dir):
    """模拟数据库"""
    db_file = temp_dir / "test_db.json"

    class MockDatabase:
        def __init__(self, db_path: Path):
            self.db_path = db_path
            self.data = {}
            self._load()

        def _load(self):
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)

        def save(self):
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

        def get(self, key: str, default=None):
            return self.data.get(key, default)

        def set(self, key: str, value: Any):
            self.data[key] = value
            self.save()

        def delete(self, key: str):
            if key in self.data:
                del self.data[key]
                self.save()

    return MockDatabase(db_file)


# ============================================================================
# 网络和API测试fixtures
# ============================================================================

@pytest.fixture
def mock_async_client():
    """模拟异步HTTP客户端"""
    class MockAsyncClient:
        def __init__(self):
            self.requests = []

        async def get(self, url: str, **kwargs):
            self.requests.append({"method": "GET", "url": url, "kwargs": kwargs})
            return MockResponse(200, {"status": "ok"})

        async def post(self, url: str, **kwargs):
            self.requests.append({"method": "POST", "url": url, "kwargs": kwargs})
            return MockResponse(200, {"status": "created"})

        async def put(self, url: str, **kwargs):
            self.requests.append({"method": "PUT", "url": url, "kwargs": kwargs})
            return MockResponse(200, {"status": "updated"})

        async def delete(self, url: str, **kwargs):
            self.requests.append({"method": "DELETE", "url": url, "kwargs": kwargs})
            return MockResponse(200, {"status": "deleted"})

    class MockResponse:
        def __init__(self, status_code: int, json_data: Dict[str, Any]):
            self.status_code = status_code
            self._json_data = json_data

        def json(self):
            return self._json_data

        def text(self):
            return json.dumps(self._json_data)

    return MockAsyncClient()


# ============================================================================
# 跳过条件函数
# ============================================================================

def skip_if_no_openai_key():
    """如果没有OpenAI API密钥则跳过测试"""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("需要OPENAI_API_KEY环境变量")


def skip_if_module_unavailable(module_name: str):
    """如果模块不可用则跳过测试"""
    try:
        __import__(module_name)
    except ImportError:
        pytest.skip(f"需要{module_name}模块")


# ============================================================================
# 辅助函数
# ============================================================================

def create_test_config_file(path: Path, config: Dict[str, Any]) -> None:
    """创建测试配置文件"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def assert_approx_equal(a, b, tol=0.001):
    """断言两个值近似相等（用于浮点数比较）"""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        assert abs(a - b) < tol, f"{a}和{b}相差超过容差{tol}"
    else:
        assert a == b, f"{a}不等于{b}"


def count_test_methods(test_class):
    """计算测试类中的测试方法数量"""
    return sum(1 for name in dir(test_class) if name.startswith('test_'))


# ============================================================================
# 性能测试工具
# ============================================================================

@pytest.fixture
def performance_thresholds():
    """性能测试阈值配置"""
    return {
        "llm_api_timeout": 10.0,  # 秒
        "metrics_calculation_timeout": 1.0,  # 秒
        "interaction_execution_timeout": 5.0,  # 秒
        "max_memory_mb": 500,  # MB
    }


# ============================================================================
# 安全测试工具
# ============================================================================

@pytest.fixture
def security_test_cases():
    """安全测试用例"""
    return {
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
        ],
        "sql_injection": [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT NULL, username, password FROM users--",
        ],
        "xss": [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg/onload=alert('xss')>",
        ],
    }


# ============================================================================
# 稳定性测试工具
# ============================================================================

@pytest.fixture
def stability_test_config():
    """稳定性测试配置"""
    return {
        "long_running_rounds": 50,  # 长运行测试的回合数
        "concurrent_simulations": 3,  # 并发模拟数量
        "memory_check_interval": 10,  # 内存检查间隔（回合）
        "max_execution_time": 300,  # 最大执行时间（秒）
    }
