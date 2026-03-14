"""
Pytest fixtures and configuration
"""
import pytest
import asyncio
from typing import Dict, List, Any, Generator
from unittest.mock import Mock, AsyncMock

# Backend imports (conditional)
try:
    from fastapi.testclient import TestClient
    from backend.main import app
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    app = None

# Core imports
try:
    from core.llm_engine import LLMEngine, LLMProvider, SiliconFlowProvider
    from core.prompt_engine import PromptTemplateEngine, PromptTemplate, PromptBuilder
    from core.environment import EnvironmentEngine, Event
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

# Entity imports
try:
    from entities.base_agent import BaseAgent, DecisionCache, AgentLearning
    from entities.state_agent import StateAgent
    from entities.power_system import PowerMetrics, PowerTier
    from entities.interaction_rules import InteractionRules, Interaction, InteractionType
    from config.leader_types import LeaderType
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False


@pytest.fixture(scope="session")
def event_loop_policy():
    """Create event loop policy for async tests"""
    policy = asyncio.get_event_loop_policy()
    asyncio.set_event_loop_policy(policy)
    return policy


@pytest.fixture
def test_client():
    """FastAPI test client fixture"""
    if not BACKEND_AVAILABLE:
        pytest.skip("Backend not available")
    return TestClient(app)


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing"""
    provider = Mock(spec=LLMProvider)
    provider.generate = AsyncMock(return_value={
        "choices": [{
            "message": {
                "function_call": {
                    "name": "test_action",
                    "arguments": '{"param": "value"}'
                }
            }
        }]
    })
    return provider


@pytest.fixture
def llm_engine(mock_llm_provider):
    """LLM engine with mock provider"""
    if not CORE_AVAILABLE:
        pytest.skip("Core module not available")
    return LLMEngine(provider=mock_llm_provider)


@pytest.fixture
def prompt_engine():
    """Prompt template engine"""
    if not CORE_AVAILABLE:
        pytest.skip("Core module not available")
    return PromptTemplateEngine(
        template_dir="config/prompts/",
        enable_cache=True,
        enable_hot_reload=False
    )


@pytest.fixture
def sample_power_metrics():
    """Sample power metrics for testing"""
    if not ENTITIES_AVAILABLE:
        pytest.skip("Entities module not available")
    return PowerMetrics(
        economic_power=100,
        military_power=80,
        political_power=90,
        diplomatic_power=85
    )


@pytest.fixture
def sample_context():
    """Sample context for testing"""
    return {
        "agent_name": "TestCountry",
        "agent_type": "state",
        "leader_type": "wangdao",
        "power_tier": "great_power",
        "current_situation": "Peaceful",
        "available_actions": ["action1", "action2"],
        "constraints": [],
        "objective_interests": ["stability", "prosperity"],
        "alliances": [],
        "enemies": []
    }


@pytest.fixture
def environment_engine():
    """Environment engine for testing"""
    if not CORE_AVAILABLE:
        pytest.skip("Core module not available")
    return EnvironmentEngine(initial_round=0, seed=42)


@pytest.fixture
def sample_agents():
    """Sample agents data for testing"""
    return [
        {
            "agent_id": "country_a",
            "name": "Country A",
            "region": "Asia",
            "power": 100,
            "leader_type": "wangdao"
        },
        {
            "agent_id": "country_b",
            "name": "Country B",
            "region": "Europe",
            "power": 90,
            "leader_type": "baquan"
        },
        {
            "agent_id": "country_c",
            "name": "Country C",
            "region": "Americas",
            "power": 70,
            "leader_type": "hunyong"
        }
    ]


@pytest.fixture
def sample_relations():
    """Sample relations for testing"""
    return {
        "country_a_country_b": 0.5,
        "country_a_country_c": -0.3,
        "country_b_country_c": 0.2
    }


@pytest.fixture
def interaction_rules():
    """Interaction rules fixture"""
    if not ENTITIES_AVAILABLE:
        pytest.skip("Entities module not available")
    return InteractionRules(config={})


@pytest.fixture
def sample_interaction():
    """Sample interaction for testing"""
    if not ENTITIES_AVAILABLE:
        pytest.skip("Entities module not available")
    return Interaction(
        interaction_id="test_interaction",
        interaction_type=InteractionType.SEND_MESSAGE,
        source_agent="country_a",
        target_agent="country_b",
        parameters={"message": "Hello"},
        timestamp="2026-03-14T00:00:00Z",
        round=1
    )


@pytest.fixture
def sample_event():
    """Sample event for testing"""
    if not CORE_AVAILABLE:
        pytest.skip("Core module not available")
    return Event(
        _priority_index=2,
        event_id="test_event",
        event_type="user_defined",
        name="Test Event",
        description="A test event",
        participants=["country_a"],
        impact_level=0.5
    )


@pytest.fixture
def decision_cache():
    """Decision cache fixture"""
    if not ENTITIES_AVAILABLE:
        pytest.skip("Entities module not available")
    return DecisionCache(max_size=100, ttl=3600)


@pytest.fixture
def agent_learning():
    """Agent learning fixture"""
    if not ENTITIES_AVAILABLE:
        pytest.skip("Entities module not available")
    return AgentLearning(agent_id="test_agent", max_outcomes=1000)


# Async test fixtures
@pytest.fixture
async def async_llm_engine():
    """Async LLM engine fixture"""
    if not CORE_AVAILABLE:
        pytest.skip("Core module not available")
    provider = Mock(spec=LLMProvider)
    provider.generate = AsyncMock(return_value={
        "choices": [{
            "message": {
                "content": "Test response"
            }
            }]
    })
    return LLMEngine(provider=provider)


# Database fixtures (for future use)
@pytest.fixture
def mock_database():
    """Mock database for testing"""
    db = Mock()
    db.connect = Mock()
    db.disconnect = Mock()
    db.query = Mock(return_value=[])
    return db


# Temporary directory fixture
@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for file operations"""
    return tmp_path


# Performance test fixtures
@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing"""
    return {
        "max_response_time": 2.0,  # seconds
        "max_memory_mb": 500,
        "min_requests_per_second": 10
    }


# Configuration fixtures
@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        "llm": {
            "provider": "siliconflow",
            "model": "deepseek-ai/DeepSeek-V3.2",
            "temperature": 0.7,
            "max_tokens": 2000
        },
        "simulation": {
            "max_rounds": 100,
            "timeout": 300
        },
        "agents": {
            "cache_size": 100,
            "cache_ttl": 3600
        }
    }


# WebSocket test fixtures
@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection"""
    ws = Mock()
    ws.accept = AsyncMock()
    ws.send_text = AsyncMock()
    ws.send_json = AsyncMock()
    ws.close = AsyncMock()
    return ws


# Auth test fixtures
@pytest.fixture
def auth_headers():
    """Authentication headers for testing"""
    return {
        "Authorization": "Bearer test_token"
    }


@pytest.fixture
def mock_user():
    """Mock user for authentication tests"""
    return {
        "user_id": "test_user",
        "username": "testuser",
        "role": "admin",
        "permissions": ["read", "write", "delete"]
    }


# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance tests"
    )
    config.addinivalue_line(
        "markers", "security: Security tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
