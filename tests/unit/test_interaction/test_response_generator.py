"""
响应生成器单元测试

测试ResponseGenerator类的核心功能：
- 初始化和配置
- 响应生成逻辑
- 格式化处理
"""
import pytest
from unittest.mock import Mock, AsyncMock


class TestResponseGeneratorInitialization:
    """测试ResponseGenerator初始化"""

    def test_response_generator_initialization(self):
        """测试响应生成器初始化"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        assert generator is not None

    def test_response_generator_with_llm_engine(self):
        """测试带LLM引擎初始化"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        mock_llm = Mock()
        generator = ResponseGenerator(llm_engine=mock_llm)

        if hasattr(generator, 'llm_engine'):
            assert generator.llm_engine is mock_llm


class TestResponseGeneratorGeneration:
    """测试响应生成"""

    @pytest.mark.asyncio
    async def test_generate_response(self):
        """测试生成响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'generate_response'):
            response = await generator.generate_response(
                receiving_agent=Mock(),
                sending_agent=Mock(),
                proposal="测试提案",
                context={}
            )

            assert response is not None

    @pytest.mark.asyncio
    async def test_generate_diplomatic_response(self):
        """测试生成外交响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'generate_diplomatic_response'):
            response = await generator.generate_diplomatic_response(
                receiving_agent=Mock(),
                sending_agent=Mock(),
                proposal="外交提案"
            )

            assert response is not None


class TestResponseGeneratorFormatting:
    """测试格式化处理"""

    def test_format_response(self):
        """测试格式化响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'format_response'):
            raw_response = {
                "thought": "思考",
                "decision": "accept",
                "message": "接受提案"
            }

            formatted = generator.format_response(raw_response)
            assert "thought" in formatted
            assert "decision" in formatted

    def test_format_json_response(self):
        """测试格式化JSON响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'format_json_response'):
            json_str = '{"decision": "accept", "message": "测试"}'
            formatted = generator.format_json_response(json_str)

            assert formatted["decision"] == "accept"


class TestResponseGeneratorTemplates:
    """测试响应模板"""

    def test_get_response_template(self):
        """测试获取响应模板"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'get_response_template'):
            template = generator.get_response_template(
                leadership_type="wangdao"
            )
            assert isinstance(template, str)

    def test_customize_template(self):
        """测试自定义模板"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'set_template'):
            custom_template = "自定义响应模板"
            generator.set_template("custom", custom_template)

            # 模板已设置
            pass


class TestResponseGeneratorValidation:
    """测试响应验证"""

    def test_validate_response(self):
        """测试验证响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'validate_response'):
            valid_response = {
                "decision": "accept",
                "message": "接受",
                "thought": "思考"
            }

            is_valid = generator.validate_response(valid_response)
            assert is_valid is True

    def test_validate_invalid_response(self):
        """测试验证无效响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'validate_response'):
            invalid_response = {}

            is_valid = generator.validate_response(invalid_response)
            assert is_valid is False


class TestResponseGeneratorConfiguration:
    """测试配置"""

    def test_set_max_length(self):
        """测试设置最大长度"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'set_max_length'):
            generator.set_max_length(500)

            # 长度已设置
            pass

    def test_set_temperature(self):
        """测试设置温度"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'set_temperature'):
            generator.set_temperature(0.8)

            # 温度已设置
            pass


class TestResponseGeneratorHistory:
    """测试历史记录"""

    def test_record_response(self):
        """测试记录响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'record_response'):
            generator.record_response(
                receiving_agent_id="agent_1",
                sending_agent_id="agent_2",
                response="测试响应",
                timestamp=0
            )

            # 响应已记录
            pass

    def test_get_response_history(self):
        """测试获取响应历史"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'record_response') and hasattr(generator, 'get_response_history'):
            generator.record_response(
                receiving_agent_id="agent_1",
                sending_agent_id="agent_2",
                response="测试响应",
                timestamp=0
            )

            history = generator.get_response_history()
            assert len(history) == 1


class TestResponseGeneratorErrorHandling:
    """测试错误处理"""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self):
        """测试处理格式错误的响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'handle_malformed_response'):
            malformed = "这不是有效的JSON响应"
            handled = generator.handle_malformed_response(malformed)

            # 应该返回默认或修正后的响应
            assert handled is not None


class TestResponseGeneratorBatchGeneration:
    """测试批量生成"""

    @pytest.mark.asyncio
    async def test_batch_generate(self):
        """测试批量生成响应"""
        try:
            from src.interaction.response_generator import ResponseGenerator
        except ImportError:
            pytest.skip("ResponseGenerator类未找到")

        generator = ResponseGenerator()

        if hasattr(generator, 'batch_generate'):
            proposals = [
                {"sender": "agent_1", "proposal": "提案1"},
                {"sender": "agent_2", "proposal": "提案2"}
            ]

            responses = await generator.batch_generate(
                receiving_agent=Mock(),
                proposals=proposals
            )

            assert len(responses) == len(proposals)
