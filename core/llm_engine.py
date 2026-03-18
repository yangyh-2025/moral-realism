"""
LLM决策引擎 - 对应技术方案3.2.1节

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
import asyncio
import httpx
import json
import logging
from config.settings import Constants

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """LLM提供者抽象基类"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        functions: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        pass

class SiliconFlowProvider(LLMProvider):
    """
    SiliconFlow平台提供者（使用DeepSeek-V3.2模型）

    支持多API-key轮替调用，规避速率限制：
    1. 步骤2（各领导人决策并行进行）：多个API-key同时调用
    2. 其他步骤：多个API-key轮替调用

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(
        self,
        api_key: Union[str, List[str]],
        base_url: str = "https://api.siliconflow.cn/v1",
        model: str = "deepseek-ai/DeepSeek-V3.2"
    ):
        # 支持单个API-key或多个API-key
        self.api_keys = [api_key] if isinstance(api_key, str) else api_key
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=Constants.HTTP_TIMEOUT)
        # 轮替调用索引
        self._current_key_index = 0
        # 轮替调用锁
        self._key_lock = asyncio.Lock()

    async def close(self) -> None:
        """正确关闭HTTP客户端"""
        if self.client is not None:
            await self.client.aclose()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    def _get_next_api_key(self) -> str:
        """轮替获取下一个API-key"""
        key = self.api_keys[self._current_key_index]
        self._current_key_index = (self._current_key_index + 1) % len(self.api_keys)
        return key

    async def generate(
        self,
        prompt: str,
        functions: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        use_rotation: bool = True  # 是否使用轮替调用
    ) -> Dict[str, Any]:
        """
        调用SiliconFlow API生成决策

        Args:
            prompt: 提示词
            functions: 可用函数列表
            temperature: 温度参数
            max_tokens: 最大token数
            use_rotation: 是否使用API-key轮替（步骤2设为False，其他步骤设为True）
        """
        # 选择API-key
        if use_rotation:
            async with self._key_lock:
                current_key = self._get_next_api_key()
        else:
            # 并行调用时，直接使用当前key索引对应的API-key
            async with self._key_lock:
                current_key = self.api_keys[self._current_key_index % len(self.api_keys)]
                self._current_key_index += 1

        headers = {
            "Authorization": f"Bearer {current_key}",
            "Content-Type": "application/json"
        }

        # 构建系统消息，要求LLM输出决策理由
        system_message = {
            "role": "system",
            "content": "你是国际关系模拟仿真系统中的智能决策助手。"
        }

        payload = {
            "model": self.model,
            "messages": [system_message, {"role": "user", "content": prompt}],
            "functions": functions if functions else None,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f"LLM API调用成功: model={self.model}")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"LLM API调用失败: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"LLM API调用异常: {type(e).__name__} - {str(e)}")
            raise

class LLMEngine:
    """
    LLM决策引擎 - 统一接口

    Git提交用户用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self._cache = {}  # 简单缓存
        self._call_count = 0

    async def make_decision(
        self,
        agent_id: str,
        prompt: str,
        available_functions: List[Dict],
        prohibited_functions: List[str],
        use_rotation: bool = True  # 是否使用API-key轮替调用
    ) -> Dict[str, Any]:
        """
        生成智能体决策

        Args:
            agent_id: 智能体ID
            prompt: 完整的决策提示
            available_functions: 可用函数列表
            prohibited_functions: 禁止使用的函数列表
            use_rotation: 是否使用API-key轮替调用
                - False：步骤2并行决策，多个API-key同时调用
                - True：其他步骤，API-key轮替调用规避速率限制

        Returns:
            包含函数调用和参数的决策结果
        """
        # 过滤掉禁止使用的函数（添加类型检查防止KeyError）
        filtered_functions = [
            f for f in available_functions
            if isinstance(f, dict) and 'name' in f and f['name'] not in prohibited_functions
        ]

        # 生成决策（传递use_rotation参数）
        result = await self.provider.generate(
            prompt=prompt,
            functions=filtered_functions,
            temperature=0.7,
            max_tokens=2000,
            use_rotation=use_rotation
        )

        self._call_count += 1

        # 提取函数调用（兼容新版和旧版API）
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0].get('message', {})
            # 新版API使用tool_calls
            if 'tool_calls' in message and message['tool_calls']:
                tool_call = message['tool_calls'][0]
                if 'function' in tool_call:
                    function_call = tool_call['function']
                    try:
                        arguments = json.loads(function_call.get('arguments', '{}'))
                        if not isinstance(arguments, dict):
                            arguments = {}
                    except (json.JSONDecodeError, TypeError):
                        arguments = {}
                    return {
                        'function': function_call.get('name'),
                        'arguments': arguments
                    }
            # 旧版API使用function_call
            elif 'function_call' in message:
                function_call = message['function_call']
                try:
                    arguments = json.loads(function_call.get('arguments', '{}'))
                    if not isinstance(arguments, dict):
                        arguments = {}
                except (json.JSONDecodeError, TypeError):
                    arguments = {}
                return {
                    'function': function_call.get('name'),
                    'arguments': arguments
                }

        # 如果没有函数调用，返回原始文本
        return {
            'function': None,
            'text': result.get('choices', [{}])[0].get('message', {}).get('content', '')
        }
