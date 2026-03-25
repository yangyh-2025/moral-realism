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
import sys
from datetime import datetime

# 彩色日志输出
class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '33m',          # 黄色
        'ERROR': '\033[31m',       # 红色
        'CRITICAL': '\033[35m',     # 紫色
        'REQUEST': '\033[33m',     # 黄色 - LLM请求
        'RESPONSE': '\033[34m',    # 蓝色 - LLM响应
        'AGENT': '\033[35m',       # 紫色 - 智能体信息
        'RESET': '\033[0m'
    }

    def format(self, record):
        if hasattr(record, 'color_type'):
            color = self.COLORS.get(record.color_type, '')
            reset = self.COLORS['RESET']
            message = super().format(record)
            return f"{color}{message}{reset}"
        return super().format(record)

# 设置详细日志记录器
llm_logger = logging.getLogger('llm_monitor')
llm_logger.setLevel(logging.DEBUG)
llm_logger.propagate = False  # 不传播到父logger

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S'))
llm_logger.addHandler(console_handler)

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
        model: str = "deepseek-ai/DeepSeek-V3.2",
        event_pusher=None,
        simulation_id=None
    ):
        # 支持单个API-key或多个API-key
        self.api_keys = [api_key] if isinstance(api_key, str) else api_key
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
        # 轮替调用索引
        self._current_key_index = 0
        # 轮替调用
        self._key_lock = asyncio.Lock()
        # WebSocket事件推送器
        self.event_pusher = event_pusher
        self.simulation_id = simulation_id

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
        use_rotation: bool = True,  # 是否使用轮替调用
        agent_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        round: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        调用SiliconFlow API生成决策

        Args:
            prompt: 提示词
            functions: 可用函数列表
            temperature: 温度参数
            max_tokens: 最大token数
            use_rotation: 是否使用API-key轮替（步骤2设为False，其他步骤设为True）
            agent_id: 智能体ID（用于日志）
            agent_name: 智能体名称（用于日志）
            round: 当前轮次（用于日志）
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

        # 打印LLM请求日志
        agent_info = f"{agent_name or agent_id or 'Unknown'}"
        if agent_id or agent_name:
            llm_logger.info(f"\n{'='*80}")
            llm_logger.info(f"【LLM请求】智能体: {agent_info} | 轮次: {round or '-'} | 模型: {self.model}")
            llm_logger.info(f"{'='*80}")

        # 显示system消息
        llm_logger.info(f"System消息: {system_message['content']}")

        # 显示完整的提示词
        llm_logger.debug(f"User提示词: {prompt}")

        # 显示可用函数
        if functions:
            func_names = [f.get('name', '') for f in functions]
            llm_logger.debug(f"可用函数: {', '.join(func_names)}")

        request_time = datetime.now().isoformat()

        # 记录LLM请求到增强日志系统
        if agent_id and agent_name and self.simulation_id:
            try:
                # 获取增强日志记录器（使用仿真特定的日志文件夹）
                from infrastructure.logging.logging_config import get_enhanced_logger
                enhanced_logger = get_enhanced_logger(
                    simulation_id=self.simulation_id,
                    log_dir="logs"
                )

                # 记录到JSON文件（包含完整提示词）
                if hasattr(enhanced_logger, 'log_llm_request'):
                    enhanced_logger.log_llm_request(
                        simulation_id=self.simulation_id,
                        agent_id=agent_id,
                        agent_name=agent_name,
                        round=round,
                        prompt=prompt,  # 完整提示词
                        functions=functions,  # 完整函数定义
                        model=self.model,
                        system_message=system_message['content']  # system消息
                    )

            except Exception as e:
                llm_logger.debug(f"记录LLM请求日志失败: {e}")

            # 推送LLM请求日志到前端（如果有event_pusher）
            llm_logger.info(f"检查请求日志推送条件: event_pusher={self.event_pusher is not None}, simulation_id={self.simulation_id}")
            if self.event_pusher and self.simulation_id:
                try:
                    # 构建请求内容
                    request_parts = []
                    request_parts.append(f"模型: {self.model}")
                    request_parts.append(f"System消息: {system_message['content']}")
                    request_parts.append(f"User提示词: {prompt}")
                    if functions:
                        func_names = [f.get('name', '') for f in functions]
                        request_parts.append(f"可用函数: {', '.join(func_names)}")

                    request_content = '\n'.join(request_parts)
                    llm_logger.info(f"准备推送LLM请求日志: agent={agent_name}, round={round}")
                    asyncio.create_task(
                        self.event_pusher.push_llm_log(
                            self.simulation_id,
                            agent_id,
                            agent_name,
                            'request',
                            request_content,
                            round
                        )
                    )
                    llm_logger.info(f"已调用asyncio.create_task推送LLM请求日志: agent={agent_name}, round={round}")
                except Exception as e:
                    llm_logger.error(f"推送LLM请求日志失败: {e}")
            else:
                llm_logger.warning(f"无法推送LLM请求日志: event_pusher={self.event_pusher is not None}, simulation_id={self.simulation_id}")

        response = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        # 打印LLM响应日志
        if agent_id or agent_name:
            llm_logger.info(f"【LLM响应】智能体: {agent_info} | 状态: {response.status_code}")

            # 提取并显示决策内容
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})

                # 检查tool_calls
                if 'tool_calls' in message and message['tool_calls']:
                    for tool_call in message['tool_calls']:
                        if 'function' in tool_call:
                            func = tool_call['function']
                            llm_logger.info(f"  → 决策函数: {func.get('name', 'N/A')}")

                            try:
                                args = json.loads(func.get('arguments', '{}'))
                                if args:
                                    llm_logger.debug(f"  → 参数: {args}")
                            except (json.JSONDecodeError, TypeError):
                                pass

                # 检查function_call（旧版）
                elif 'function_call' in message:
                    func_call = message['function_call']
                    llm_logger.info(f"  → 决策函数: {func_call.get('name', 'N/A')}")

                    try:
                        args = json.loads(func_call.get('arguments', '{}'))
                        if args:
                            llm_logger.debug(f"  → 参数: {args}")
                    except (json.JSONDecodeError, TypeError):
                        pass

                # 显示文本响应（如果有）
                content = message.get('content', '')
                if content:
                    llm_logger.debug(f"  → 内容: {content}")

            # 显示token使用情况
            if 'usage' in result:
                usage = result['usage']
                llm_logger.info(f"  → Token使用: 输入={usage.get('prompt_tokens', 0)} | 输出={usage.get('completion_tokens', 0)} | 总计={usage.get('total_tokens', 0)}")

            llm_logger.info(f"{'='*80}\n")

            # 记录LLM响应到增强日志系统
            if agent_id and agent_name and self.simulation_id:
                try:
                    # 获取增强日志记录器（使用仿真特定的日志文件夹）
                    from infrastructure.logging.logging_config import get_enhanced_logger
                    enhanced_logger = get_enhanced_logger(
                        simulation_id=self.simulation_id,
                        log_dir="logs"
                    )

                    # 提取响应信息
                    function_name = None
                    function_args = None
                    content_full = ""
                    usage_info = None
                    tool_calls = []

                    if 'choices' in result and len(result['choices']) > 0:
                        message = result['choices'][0].get('message', {})
                        if 'tool_calls' in message and message['tool_calls']:
                            for tool_call in message['tool_calls']:
                                if 'function' in tool_call:
                                    func = tool_call['function']
                                    function_name = func.get('name', '')
                                    try:
                                        function_args = json.loads(func.get('arguments', '{}'))
                                    except (json.JSONDecodeError, TypeError):
                                        function_args = {}
                                    # 记录所有工具调用
                                    tool_calls.append({
                                        'function': function_name,
                                        'arguments': function_args
                                    })
                        elif 'function_call' in message:
                            func_call = message['function_call']
                            function_name = func_call.get('name', '')
                            try:
                                function_args = json.loads(func_call.get('arguments', '{}'))
                            except Exception:
                                function_args = {}
                            tool_calls.append({
                                'function': function_name,
                                'arguments': function_args
                            })

                        content = message.get('content', '')
                        content_full = content

                    if 'usage' in result:
                        usage_info = result['usage']

                    # 记录到JSON文件（包含完整响应信息）
                    if hasattr(enhanced_logger, 'log_llm_response'):
                        # 记录每个工具调用
                        for tc in tool_calls:
                            enhanced_logger.log_llm_response(
                                simulation_id=self.simulation_id,
                                agent_id=agent_id,
                                agent_name=agent_name,
                                round=round,
                                function_name=tc.get('function'),
                                function_args=tc.get('arguments'),
                                content=content_full,
                                usage=usage_info,
                                status_code=response.status_code
                            )
                except Exception as e:
                    llm_logger.debug(f"记录LLM响应日志失败: {e}")

            # 推送LLM响应日志到前端（如果有event_pusher）
            if self.event_pusher and agent_id and agent_name and self.simulation_id:
                try:
                    content_parts = []
                    if 'choices' in result and len(result['choices']) > 0:
                        message = result['choices'][0].get('message', {})
                        if 'tool_calls' in message and message['tool_calls']:
                            for tool_call in message['tool_calls']:
                                if 'function' in tool_call:
                                    func = tool_call['function']
                                    content_parts.append(f"决策函数: {func.get('name', 'N/A')}")
                                    try:
                                        args = json.loads(func.get('arguments', '{}'))
                                        if args:
                                            content_parts.append(f"参数: {args}")
                                    except (json.JSONDecodeError, TypeError):
                                        pass
                        elif 'function_call' in message:
                            func_call = message['function_call']
                            content_parts.append(f"决策函数: {func_call.get('name', 'N/A')}")
                            try:
                                args = json.loads(func_call.get('arguments', '{}'))
                                if args:
                                    content_parts.append(f"参数: {args}")
                            except (json.JSONDecodeError, TypeError):
                                pass
                        content = message.get('content', '')
                        if content:
                            content_parts.append(f"内容: {content}")

                    if 'usage' in result:
                        usage = result['usage']
                        content_parts.append(f"Token使用: 输入={usage.get('prompt_tokens', 0)} | 输出={usage.get('completion_tokens', 0)} | 总计={usage.get('total_tokens', 0)}")

                    content = '\n'.join(content_parts)
                    asyncio.create_task(
                        self.event_pusher.push_llm_log(
                            self.simulation_id,
                            agent_id,
                            agent_name,
                            'response',
                            content,
                            round
                        )
                    )
                except Exception as e:
                    llm_logger.debug(f"推送LLM响应日志失败: {e}")

        return result

class LLMEngine:
    """
    LLM决策引擎 - 统一接口

    Git提交用户用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self, provider: LLMProvider, event_pusher=None, simulation_id=None):
        self.provider = provider
        self._cache = {}  # 简单缓存
        self._call_count = 0
        self.event_pusher = event_pusher  # WebSocket事件推送器
        self.simulation_id = simulation_id  # 当前仿真ID
        # 将 event_pusher 和 simulation_id 传递给 provider
        if hasattr(provider, 'event_pusher'):
            provider.event_pusher = event_pusher
        if hasattr(provider, 'simulation_id'):
            provider.simulation_id = simulation_id

    async def make_decision(
        self,
        agent_id: str,
        prompt: str,
        available_functions: List[Dict],
        prohibited_functions: List[str],
        use_rotation: bool = True,  # 是否使用API-key轮替调用
        agent_name: Optional[str] = None,
        round: Optional[int] = None
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
            agent_name: 智能体名称（用于日志）
            round: 当前轮次（用于日志）

        Returns:
            包含函数调用和参数的决策结果
        """
        # 过滤掉禁止使用的函数（添加类型检查防止KeyError）
        filtered_functions = [
            f for f in available_functions
            if isinstance(f, dict) and 'name' in f and f['name'] not in prohibited_functions
        ]

        # 生成决策（传递use_rotation参数和日志参数）
        result = await self.provider.generate(
            prompt=prompt,
            functions=filtered_functions,
            temperature=0.7,
            max_tokens=2000,
            use_rotation=use_rotation,
            agent_id=agent_id,
            agent_name=agent_name,
            round=round
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
