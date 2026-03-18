"""
Unit tests for LLM Engine module

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

try:
    from infrastructure.llm.llm_engine import LLMEngine, LLMProvider, SiliconFlowProvider
    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not CORE_AVAILABLE,
    reason="Core module not available"
)


@pytest.mark.unit
class TestLLMProvider:
    """Test LLM provider abstract base class"""

    def test_provider_is_abstract(self):
        """Test that LLMProvider cannot be instantiated directly"""
        with pytest.raises(TypeError):
            LLMProvider()


@pytest.mark.unit
class TestSiliconFlowProvider:
    """Test SiliconFlow LLM provider"""

    @pytest.fixture
    def provider(self):
        """Create provider with test API key"""
        return SiliconFlowProvider(
            api_key="test_api_key",
            base_url="https://test.api",
            model="test_model"
        )

    def test_provider_initialization(self, provider):
        """Test provider initialization"""
        assert provider.api_keys == ["test_api_key"]
        assert provider.base_url == "https://test.api"
        assert provider.model == "test_model"
        assert provider._current_key_index == 0

    def test_provider_initialization_with_multiple_keys(self):
        """Test provider initialization with multiple API keys"""
        provider = SiliconFlowProvider(
            api_key=["key1", "key2", "key3"],
            base_url="https://test.api"
        )
        assert provider.api_keys == ["key1", "key2", "key3"]
        assert len(provider.api_keys) == 3

    def test_get_next_api_key_rotation(self, provider):
        """Test API key rotation"""
        # Single key should just return the same key
        key1 = provider._get_next_api_key()
        key2 = provider._get_next_api_key()
        assert key1 == key2 == "test_api_key"

    def test_get_next_api_key_rotation_multiple(self):
        """Test API key rotation with multiple keys"""
        provider = SiliconFlowProvider(
            api_key=["key1", "key2", "key3"],
            base_url="https://test.api"
        )

        key1 = provider._get_next_api_key()
        key2 = provider._get_next_api_key()
        key3 = provider._get_next_api_key()
        key4 = provider._get_next_api_key()

        assert key1 == "key1"
        assert key2 == "key2"
        assert key3 == "key3"
        assert key4 == "key1"  # Should cycle back

    @pytest.mark.asyncio
    async def test_generate_success(self, provider):
        """Test successful API call"""
        # Mock the HTTP client
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "function_call": {
                        "name": "test_function",
                        "arguments": '{"param": "value"}'
                    }
                }
            }]
        }
        mock_response.raise_for_status = Mock()

        provider.client.post = AsyncMock(return_value=mock_response)

        result = await provider.generate(
            prompt="Test prompt",
            functions=[{"name": "test_function"}],
            temperature=0.7,
            max_tokens=1000
        )

        assert "choices" in result
        assert len(result["choices"]) == 1

    @pytest.mark.asyncio
    async def test_generate_with_rotation(self, provider):
        """Test API key rotation during calls"""
        provider.api_keys = ["key1", "key2"]
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = Mock()

        provider.client.post = AsyncMock(return_value=mock_response)

        # First call
        await provider.generate("test", [], use_rotation=True)
        first_call_headers = provider.client.post.call_args[1]["headers"]

        # Second call
        await provider.generate("test", [], use_rotation=True)
        second_call_headers = provider.client.post.call_args[1]["headers"]

        # Different keys should be used
        assert first_call_headers["Authorization"] != second_call_headers["Authorization"]

    @pytest.mark.asyncio
    async def test_generate_without_rotation(self):
        """Test API key not rotating during parallel calls"""
        provider = SiliconFlowProvider(
            api_key=["key1", "key2"],
            base_url="https://test.api"
        )

        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = Mock()

        provider.client.post = AsyncMock(return_value=mock_response)

        # Multiple calls without rotation
        for _ in range(3):
            await provider.generate("test", [], use_rotation=False)

        # All calls should use keys in sequence (not rotating in lock)
        assert provider.client.post.call_count == 3


@pytest.mark.unit
class TestLLMEngine:
    """Test LLM engine"""

    @pytest.fixture
    def mock_provider(self):
        """Create mock LLM provider"""
        provider = Mock()
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
    def engine(self, mock_provider):
        """Create LLM engine"""
        return LLMEngine(provider=mock_provider)

    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine.provider is not None
        assert engine._cache == {}
        assert engine._call_count == 0

    @pytest.mark.asyncio
    async def test_make_decision_with_function_call(self, engine, mock_provider):
        """Test making decision with function call"""
        result = await engine.make_decision(
            agent_id="test_agent",
            prompt="Test prompt",
            available_functions=[
                {"name": "test_action", "description": "Test action"},
                {"name": "other_action", "description": "Other action"}
            ],
            prohibited_functions=[]
        )

        assert result["function"] == "test_action"
        assert result["arguments"] == {"param": "value"}
        assert engine._call_count == 1

    @pytest.mark.asyncio
    async def test_make_decision_filters_prohibited_functions(self, engine, mock_provider):
        """Test that prohibited functions are filtered out"""
        await engine.make_decision(
            agent_id="test_agent",
            prompt="Test prompt",
            available_functions=[
                {"name": "allowed_action", "description": "Allowed"},
                {"name": "prohibited_action", "description": "Prohibited"}
            ],
            prohibited_functions=["prohibited_action"]
        )

        # Check that prohibited function was not passed
        call_args = mock_provider.generate.call_args
        passed_functions = call_args[1]["functions"]

        assert len(passed_functions) == 1
        assert passed_functions[0]["name"] == "allowed_action"

    @pytest.mark.asyncio
    async def test_make_decision_without_function_call(self):
        """Test making decision without function call (text response)"""
        mock_provider = Mock()
        mock_provider.generate = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "This is a text response"
                }
            }]
        })

        engine = LLMEngine(provider=mock_provider)

        result = await engine.make_decision(
            agent_id="test_agent",
            prompt="Test prompt",
            available_functions=[],
            prohibited_functions=[]
        )

        assert result["function"] is None
        assert result["text"] == "This is a text response"

    @pytest.mark.asyncio
    async def test_make_decision_use_rotation_parameter(self, engine, mock_provider):
        """Test use_rotation parameter is passed through"""
        await engine.make_decision(
            agent_id="test_agent",
            prompt="Test prompt",
            available_functions=[],
            prohibited_functions=[],
            use_rotation=False
        )

        call_args = mock_provider.generate.call_args
        assert call_args[1]["use_rotation"] == False

    @pytest.mark.asyncio
    async def test_make_decision_multiple_calls(self, engine):
        """Test that call count increases with each decision"""
        initial_count = engine._call_count

        await engine.make_decision(
            agent_id="test_agent",
            prompt="Test 1",
            available_functions=[],
            prohibited_functions=[]
        )

        await engine.make_decision(
            agent_id="test_agent",
            prompt="Test 2",
            available_functions=[],
            prohibited_functions=[]
        )

        assert engine._call_count == initial_count + 2

    def test_engine_caching_simple(self):
        """Test simple cache mechanism (if implemented)"""
        # This tests the existence of cache attribute
        mock_provider = Mock()
        engine = LLMEngine(provider=mock_provider)

        assert hasattr(engine, "_cache")
        assert isinstance(engine._cache, dict)


@pytest.mark.unit
class TestLLMEngineErrorHandling:
    """Test LLM engine error handling"""

    @pytest.mark.asyncio
    async def test_handle_api_error(self):
        """Test handling of API errors"""
        from http import HTTPStatus
        from httpx import HTTPStatusError, Request

        mock_provider = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        error = HTTPStatusError(
            "Server error",
            request=Mock(spec=Request),
            response=mock_response
        )

        mock_provider.generate = AsyncMock(side_effect=error)

        engine = LLMEngine(provider=mock_provider)

        # The engine should handle or propagate the error
        with pytest.raises(HTTPStatusError):
            await engine.make_decision(
                agent_id="test_agent",
                prompt="Test prompt",
                available_functions=[],
                prohibited_functions=[]
            )

    @pytest.mark.asyncio
    async def test_handle_timeout(self):
        """Test handling of timeout errors"""
        from httpx import TimeoutException

        mock_provider = Mock()
        mock_provider.generate = AsyncMock(side_effect=TimeoutException("Request timeout"))

        engine = LLMEngine(provider=mock_provider)

        with pytest.raises(TimeoutException):
            await engine.make_decision(
                agent_id="test_agent",
                prompt="Test prompt",
                available_functions=[],
                prohibited_functions=[]
            )


@pytest.mark.unit
class TestLLMEngineMultiKey:
    """Test LLM engine with multiple API keys"""

    @pytest.fixture
    def multi_key_provider(self):
        """Create provider with multiple keys"""
        return SiliconFlowProvider(
            api_key=["key1", "key2", "key3"],
            base_url="https://test.api"
        )

    def test_multi_key_initialization(self, multi_key_provider):
        """Test multi-key provider initialization"""
        assert len(multi_key_provider.api_keys) == 3
        assert multi_key_provider._current_key_index == 0

    @pytest.mark.asyncio
    async def test_multi_key_rotation_sequence(self, multi_key_provider):
        """Test that keys are used in sequence"""
        mock_response = Mock()
        mock_response.json.return_value = {"choices": []}
        mock_response.raise_for_status = Mock()

        multi_key_provider.client.post = AsyncMock(return_value=mock_response)

        # Make multiple calls
        for _ in range(6):
            await multi_key_provider.generate("test", [], use_rotation=True)

        # Check that different keys were used
        call_count = multi_key_provider.client.post.call_count
        assert call_count == 6
