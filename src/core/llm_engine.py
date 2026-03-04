"""
LLM（大语言模型）引擎模块



本模块提供LLMConfig数据类和LLMEngine类，用于：
- 与LLM API交互（特别是硅流动SiliconFlow API）
- 发送聊天完成请求
- 执行函数调用以约束代理行为
- 支持同步和异步调用
- 支持流式输出

主要类：
- LLMConfig: LLM API连接配置（包括base_url、api_key、model等）
- LLMEngine: LLM API交互引擎，提供各种调用方法
"""

from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
import os

from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class LLMConfig:
    """
    LLM（大语言模型）配置类

    配置LLM API连接参数，可从环境变量中读取。

    属性说明：
    - base_url: API基础URL（默认从环境变量SILICONFLOW_BASE_URL读取）
    - api_key: API密钥（默认从环境变量SILICONFLOW_API_KEY读取）
    - model: 使用的模型名称（默认从环境变量SILICONFLOW_MODEL读取）
    - temperature: 生成温度（0-1，控制随机性，默认0.7）
    - max_tokens: 最大生成token数（默认2048）
    - timeout: 请求超时时间（秒，默认60）
    """

    base_url: str = field(
        default_factory=lambda: os.getenv(
            "SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"
        )
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("SILICONFLOW_API_KEY", "")
    )
    model: str = field(
        default_factory=lambda: os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-72B-Instruct")
    )
    temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.7"))
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "2048"))
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("LLM_TIMEOUT", "60"))
    )

    def validate(self) -> None:
        """
        验证配置参数的有效性

        Raises:
            ValueError: 当任何必需参数未设置时抛出异常
        """
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY must be set in environment variables")
        if not self.base_url:
            raise ValueError("SILICONFLOW_BASE_URL must be set")
        if not self.model:
            raise ValueError("SILICONFLOW_MODEL must be set")


class LLMEngine:
    """
    LLM（大语言模型）引擎类

    用于与LLM API交互的引擎，提供同步和异步调用方法。

    支持的方法：
    - chat_completion: 同步聊天完成
    - function_call: 函数调用（用于结构化输出）
    - stream_chat_completion: 同步流式聊天完成
    - async_chat_completion: 异步聊天完成
    - async_stream_chat_completion: 异步流式聊天完成
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """
        初始化LLM引擎

        Args:
            config: LLM配置对象，如果为None则使用环境变量中的默认配置
        """
        self.config = config or LLMConfig()
        self.config.validate()

        # Initialize OpenAI client (compatible with SiliconFlow API)
        # 初始化OpenAI客户端（与SiliconFlow API兼容）
        self.client = OpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.timeout,
        )
        self.async_client = AsyncOpenAI(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            timeout=self.config.timeout,
        )

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        发送聊天完成请求（同步）

        Args:
            messages: 消息列表，每个消息包含'role'和'content'字段
            temperature: 覆盖默认温度值
            max_tokens: 覆盖默认最大token数
            **kwargs: 传递给API的额外参数

        Returns:
            包含响应内容和元数据的字典：
            - content: 生成的文本内容
            - model: 使用的模型
            - finish_reason: 完成原因（如"stop"或"length"）
            - usage: token使用统计
            - raw_response: 原始API响应
        """
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.config.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            **kwargs,
        )

        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "raw_response": response,
        }

    def function_call(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        执行函数调用以约束代理行为（同步）

        此方法用于要求LLM按照预定义的函数schema输出结构化数据，
        可用于控制代理的行为输出格式。

        Args:
            messages: 消息列表
            functions: 函数定义列表，用于结构化输出
            temperature: 覆盖默认温度值
            max_tokens: 覆盖默认最大token数
            **kwargs: 传递给API的额外参数

        Returns:
            包含函数调用结果和元数据的字典：
            - function_call: 函数调用对象
            - model: 使用的模型
            - finish_reason: 完成原因
            - usage: token使用统计
            - raw_response: 原始API响应
        """
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            functions=functions,
            function_call="auto",
            temperature=temperature if temperature is not None else self.config.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            **kwargs,
        )

        message = response.choices[0].message
        function_call = message.function_call if message.function_call else None

        return {
            "function_call": function_call,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "raw_response": response,
        }

    def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        发送流式聊天完成请求（同步）

        适合需要实时显示生成内容的场景。

        Args:
            messages: 消息列表
            temperature: 覆盖默认温度值
            max_tokens: 覆盖默认最大token数
            **kwargs: 传递给API的额外参数

        Returns:
            流式响应块列表，每个块包含：
            - content: 生成的文本块
            - finish_reason: 完成原因
        """
        stream = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.config.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            stream=True,
            **kwargs,
        )

        chunks = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                chunks.append(
                    {
                        "content": chunk.choices[0].delta.content,
                        "finish_reason": chunk.choices[0].finish_reason,
                    }
                )

        return chunks

    async def async_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        发送异步聊天完成请求

        Args:
            messages: 消息列表
            temperature: 覆盖默认温度值
            max_tokens: 覆盖默认最大token数
            **kwargs: 传递给API的额外参数

        Returns:
            包含响应内容和元数据的字典（与chat_completion相同）
        """
        response = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.config.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            **kwargs,
        )

        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "raw_response": response,
        }

    async def async_stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncGenerator[str, None]:
        """
        发送异步流式聊天完成请求

        Args:
            messages: 消息列表
            temperature: 覆盖默认温度值
            max_tokens: 覆盖默认最大token数
            **kwargs: 传递给API的额外参数

        Yields:
            流式响应块的文本内容
        """
        stream = await self.async_client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.config.temperature,
            max_tokens=max_tokens if max_tokens is not None else self.config.max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
