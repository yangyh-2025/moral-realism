"""
LLM Engine for the moral realism realism system.

This module provides the LLMConfig dataclass and LLMEngine class for
interacting with LLM APIs, specifically SiliconFlow API.
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
    """Configuration for LLM API connections."""

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
        """Validate the configuration."""
        if not self.api_key:
            raise ValueError("SILICONFLOW_API_KEY must be set in environment variables")
        if not self.base_url:
            raise ValueError("SILICONFLOW_BASE_URL must be set")
        if not self.model:
            raise ValueError("SILICONFLOW_MODEL must be set")


class LLMEngine:
    """Engine for interacting with LLM APIs."""

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """
        Initialize the LLM engine.

        Args:
            config: LLM configuration. If None, uses default from environment.
        """
        self.config = config or LLMConfig()
        self.config.validate()

        # Initialize OpenAI client (compatible with SiliconFlow API)
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
        Send a chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Override default temperature.
            max_tokens: Override default max_tokens.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            Dictionary containing the response content and metadata.
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
        Perform a function call to constrain agent behavior.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            functions: List of function definitions for structured output.
            temperature: Override default temperature.
            max_tokens: Override default max_tokens.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            Dictionary containing the function call result and metadata.
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
        Send a streaming chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Override default temperature.
            max_tokens: Override default max_tokens.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            List of streaming response chunks.
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
        Send an async chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Override default temperature.
            max_tokens: Override default max_tokens.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            Dictionary containing the response content and metadata.
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
        Send an async streaming chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Override default temperature.
            max_tokens: Override default max_tokens.
            **kwargs: Additional parameters to pass to the API.

        Yields:
            Streaming response chunks.
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
