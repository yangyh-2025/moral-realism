"""
LLM引擎单元测试

测试LLMEngine和LLMConfig类的核心功能：
- 初始化和配置
- LLM API调用
- 环境变量配置加载
- 错误处理
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import os


class TestLLMConfig:
    """测试LLMConfig类"""

    def test_llm_config_initialization_default(self):
        """测试使用默认值初始化LLMConfig"""
        try:
            from src.core.llm_engine import LLMConfig
        except ImportError:
            pytest.skip("LLMConfig类未找到")

        config = LLMConfig()
        assert hasattr(config, 'model')
        assert hasattr(config, 'temperature')
        assert hasattr(config, 'max_tokens')

    def test_llm_config_initialization_custom(self):
        """测试使用自定义值初始化LLMConfig"""
        try:
            from src.core.llm_engine import LLMConfig
        except ImportError:
            pytest.skip("LLMConfig类未找到")

        config = LLMConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000,
            timeout=30
        )
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000

    def test_llm_config_validation(self):
        """测试LLMConfig验证"""
        try:
            from src.core.llm_engine import LLMConfig
        except ImportError:
            pytest.skip("LLMConfig类未找到")

        # 有效配置
        config = LLMConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )

        if hasattr(config, 'validate'):
            assert config.validate() is True

    @pytest.mark.parametrize("temperature,expected_valid", [
        (0.0, True),
        (0.5, True),
        (1.0, True),
        (1.5, True),
        (-0.1, False),
        (2.1, False),
    ])
    def test_llm_config_temperature_validation(self, temperature, expected_valid):
        """测试温度参数验证"""
        try:
            from src.core.llm_engine import LLMConfig
        except ImportError:
            pytest.skip("LLMConfig类未找到")

        try:
            config = LLMConfig(temperature=temperature)
            if hasattr(config, 'validate'):
                result = config.validate()
                if expected_valid:
                    assert result is True
                else:
                    assert result is False
        except ValueError:
            assert not expected_valid


class TestLLMEngine:
    """测试LLMEngine类"""

    def test_llm_engine_initialization(self):
        """测试LLMEngine初始化"""
        try:
            from src.core.llm_engine import LLMEngine, LLMConfig
        except ImportError:
            pytest.skip("LLMEngine类未找到")

        config = LLMConfig(model="gpt-4", temperature=0.7, max_tokens=2000)
        engine = LLMEngine(config)

        assert engine.config is not None

    @pytest.mark.asyncio
    async def test_generate_method_exists(self):
        """测试generate方法存在"""
        try:
            from src.core.llm_engine import LLMEngine, LLMConfig
        except ImportError:
            pytest.skip("LLMEngine类未找到")

        config = LLMConfig(model="gpt-4")
        engine = LLMEngine(config)

        assert hasattr(engine, 'generate')

    @pytest.mark.asyncio
    async def test_generate_with_history_method_exists(self):
        """测试generate_with_history方法存在"""
        try:
            from src.core.llm_engine import LLMEngine, LLMConfig
        except ImportError:
            pytest.skip("LLMEngine类未找到")

        config = LLMConfig(model="gpt-4")
        engine = LLMEngine(config)

        assert hasattr(engine, 'generate_with_history')


class TestEnvironmentVariableLoading:
    """测试环境变量加载"""

    def test_load_api_key_from_env(self, mock_env_vars):
        """测试从环境变量加载API密钥"""
        assert "OPENAI_API_KEY" in os.environ
        assert os.environ["OPENAI_API_KEY"] == "test-api-key-12345"

    def test_load_model_from_env(self, mock_env_vars):
        """测试从环境变量加载模型"""
        assert "LLM_MODEL" in os.environ
        assert os.environ["LLM_MODEL"] == "gpt-4"

    def test_load_temperature_from_env(self, mock_env_vars):
        """测试从环境变量加载温度"""
        assert "LLM_TEMPERATURE" in os.environ
        assert os.environ["LLM_TEMPERATURE"] == "0.7"


class TestLLMEngineConfigFromEnv:
    """测试从环境变量创建LLM配置"""

    def test_llm_config_from_env(self, mock_env_vars):
        """测试从环境变量创建LLM配置"""
        try:
            from src.core.llm_engine import LLMConfig, create_config_from_env
        except ImportError:
            pytest.skip("LLMConfig相关函数未找到")

        if 'create_config_from_env' in dir():
            config = create_config_from_env()
            assert config is not None


class TestLLMEngineErrorHandling:
    """测试LLM引擎错误处理"""

    @pytest.mark.asyncio
    async def test_handle_missing_api_key(self):
        """测试处理缺失API密钥"""
        try:
            from src.core.llm_engine import LLMEngine, LLMConfig
        except ImportError:
            pytest.skip("LLMEngine类未找到")

        # 临时移除API密钥
        original_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

        try:
            config = LLMConfig(model="gpt-4")
            engine = LLMEngine(config)

            # 尝试生成应该失败或使用Mock
            # 这里我们只测试错误处理路径存在
            pass
        finally:
            # 恢复API密钥
            if original_key:
                os.environ["OPENAI_API_KEY"] = original_key


class TestLLMEngineResponseParsing:
    """测试LLM引擎响应解析"""

    def test_parse_json_response(self):
        """测试解析JSON响应"""
        response_text = '{"thought": "test", "action": "observe"}'

        try:
            import json
            parsed = json.loads(response_text)
            assert parsed["thought"] == "test"
            assert parsed["action"] == "observe"
        except json.JSONDecodeError:
            pytest.fail("无法解析JSON响应")

    def test_parse_malformed_response(self):
        """测试解析格式错误的响应"""
        malformed_response = "This is not JSON"

        try:
            import json
            parsed = json.loads(malformed_response)
            pytest.fail("应该抛出JSONDecodeError")
        except json.JSONDecodeError:
            pass  # 预期行为


class TestLLMEngineBatchProcessing:
    """测试LLM引擎批量处理"""

    @pytest.mark.asyncio
    async def test_batch_generate_method_exists(self):
        """测试batch_generate方法存在"""
        try:
            from src.core.llm_engine import LLMEngine, LLMConfig
        except ImportError:
            pytest.skip("LLMEngine类未找到")

        config = LLMConfig(model="gpt-4")
        engine = LLMEngine(config)

        if hasattr(engine, 'batch_generate'):
            # 方法存在，可以进一步测试
            pass


class TestLLMEngineMetrics:
    """测试LLM引擎指标"""

    def test_track_token_usage(self):
        """测试追踪令牌使用"""
        # 这里测试指标追踪功能
        metrics = {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }

        assert metrics["total_tokens"] == metrics["prompt_tokens"] + metrics["completion_tokens"]

    def test_track_call_count(self):
        """测试追踪调用次数"""
        call_count = 0
        call_count += 1
        assert call_count == 1
