"""
LLM服务模块 - 为ABM仿真提供大语言模型支持
负责LLM模型配置、API调用和响应解析
与技术规范第4.2.4节对齐
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

import openai
from openai import AsyncOpenAI
from loguru import logger


class LLMProviderEnum(str, Enum):
    """支持的LLM服务提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class LLMError(Exception):
    """LLM相关错误的自定义异常类"""
    pass


@dataclass
class LLMConfig:
    """
    LLM配置数据类

    存储LLM服务的所有配置参数，包括：
    - 提供商和模型选择
    - API认证信息
    - 调用参数（最大令牌数、温度等）
    - 重试策略配置
    """
    provider: str = "openai"  # LLM服务提供商
    model_name: str = "gpt-4"  # 模型名称
    api_key: str = ""  # API密钥
    api_base: str = ""  # 可选的自定义API基础URL
    max_tokens: int = 2000  # 最大生成令牌数
    temperature: float = 0.7  # 温度参数（控制随机性）
    timeout: int = 60  # 超时时间（秒）
    max_retries: int = 3  # 最大重试次数
    retry_delay: float = 1.0  # 重试延迟（秒）


class LLMService:
    """
    LLM服务类 - 提供LLM操作功能，包含重试逻辑和错误处理

    主要功能：
    - 初始化和配置LLM客户端
    - 执行异步LLM调用（带重试）
    - 批量LLM调用（带并发控制）
    - 响应解析和验证
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        初始化LLM服务

        Args:
            config: LLM配置对象，如果未提供则从环境变量加载
        """
        self.config = config or self._load_default_config()
        self._client: Optional[AsyncOpenAI] = None
        self._initialize_client()

    def _load_default_config(self) -> LLMConfig:
        """
        从环境变量加载默认配置

        环境变量列表：
        - LLM_PROVIDER: 服务提供商
        - LLM_MODEL: 模型名称
        - OPENAI_API_KEY: API密钥
        - OPENAI_API_BASE: API基础URL
        - LLM_MAX_TOKENS: 最大令牌数
        - LLM_TEMPERATURE: 温度参数
        - LLM_TIMEOUT: 超时时间
        - LLM_MAX_RETRIES: 最大重试次数
        - LLM_RETRY_DELAY: 重试延迟

        Returns:
            从环境变量构建的LLMConfig对象
        """
        return LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "openai"),
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            api_base=os.getenv("OPENAI_API_BASE", ""),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            timeout=int(os.getenv("LLM_TIMEOUT", "60")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("LLM_RETRY_DELAY", "1.0"))
        )

    def _initialize_client(self):
        """
        初始化OpenAI异步客户端

        根据配置创建AsyncOpenAI客户端实例，
        并记录初始化日志。
        """
        try:
            client_kwargs = {
                "api_key": self.config.api_key,
                "timeout": self.config.timeout
            }

            # 如果配置了自定义API基础URL，则使用它
            if self.config.api_base:
                client_kwargs["base_url"] = self.config.api_base

            self._client = AsyncOpenAI(**client_kwargs)
            logger.info(f"LLM客户端初始化完成: {self.config.provider}/{self.config.model_name}")
        except Exception as e:
            logger.error(f"LLM客户端初始化失败: {e}")
            raise LLMError(f"LLM客户端初始化失败: {e}")

    def update_config(self, new_config: LLMConfig):
        """
        更新LLM配置并重新初始化客户端

        Args:
            new_config: 新的LLM配置对象
        """
        self.config = new_config
        self._initialize_client()
        logger.info("LLM配置已更新")

    async def call_llm_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        异步LLM调用，带重试逻辑

        使用指数退避重试策略，在失败时自动重试。

        Args:
            prompt: 用户提示词
            system_prompt: 可选的系统提示词

        Returns:
            解析后的JSON响应字典

        Raises:
            LLMError: 当所有重试都失败时抛出
        """
        # 循环尝试配置的最大重试次数
        for attempt in range(self.config.max_retries):
            try:
                response = await self._single_llm_call(prompt, system_prompt)
                return response
            except Exception as e:
                logger.warning(f"LLM调用第 {attempt + 1} 次尝试失败: {e}")

                if attempt < self.config.max_retries - 1:
                    # 使用指数退避算法计算延迟时间
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.info(f"将在 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"所有 {self.config.max_retries} 次LLM重试尝试都失败了")
                    raise LLMError(f"LLM调用在 {self.config.max_retries} 次重试后失败: {e}")

    async def _single_llm_call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        单次LLM API调用

        构建消息、调用API、解析响应的完整流程。

        Args:
            prompt: 用户提示词
            system_prompt: 可选的系统提示词

        Returns:
            解析后的JSON响应

        Raises:
            Exception: 当API调用失败时抛出
        """
        if not self._client:
            raise LLMError("LLM客户端未初始化")

        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 执行API调用
        logger.debug(f"使用模型调用LLM: {self.config.model_name}")
        response = await self._client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            response_format={"type": "json_object"}  # 强制JSON格式输出
        )

        # 提取响应文本
        response_text = response.choices[0].message.content
        logger.debug(f"LLM原始响应: {response_text[:200]}...")

        # 解析JSON响应
        try:
            parsed_response = json.loads(response_text)
            logger.info("LLM响应解析成功")
            return parsed_response
        except json.JSONDecodeError as e:
            logger.error(f"解析LLM JSON响应失败: {e}")
            logger.error(f"原始响应: {response_text}")
            raise LLMError(f"LLM返回的JSON格式无效: {e}")

    async def call_llm_batch_async(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量LLM调用，带并发控制

        使用信号量限制同时进行的API调用数量，
        避免超过API速率限制。

        Args:
            prompts: 提示词列表
            system_prompt: 可选的系统提示词
            max_concurrent: 最大并发调用数

        Returns:
            解析后的JSON响应列表（顺序与输入对应）
        """
        # 创建信号量用于并发控制
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_call(prompt: str) -> Dict[str, Any]:
            """受信号量限制的单个LLM调用"""
            async with semaphore:
                return await self.call_llm_async(prompt, system_prompt)

        logger.info(f"开始批量LLM调用: {len(prompts)} 个提示词, 最大并发={max_concurrent}")
        # 并发执行所有调用，异常不会中断整个批次
        results = await asyncio.gather(*[limited_call(p) for p in prompts], return_exceptions=True)

        # 检查并处理错误结果
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"批次调用 {i} 失败: {result}")
                results[i] = {"error": str(result)}

        logger.info(f"批量LLM调用完成: {len(results)} 个结果")
        return results

    def parse_decision_response(
        self,
        response_text: str,
        validate_structure: bool = True
    ) -> Dict[str, Any]:
        """
        解析LLM决策响应

        处理可能包含额外文本的响应，尝试从中提取JSON。

        Args:
            response_text: LLM返回的原始响应文本
            validate_structure: 是否验证JSON结构

        Returns:
            解析后的决策字典

        Raises:
            LLMError: 当解析或验证失败时抛出
        """
        try:
            # 尝试在响应中找到JSON（可能有额外文本）
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end + 1]
                parsed = json.loads(json_text)
            else:
                # 尝试将整个响应解析为JSON
                parsed = json.loads(response_text)

            # 基本结构验证
            if validate_structure:
                if 'decision_reason' not in parsed:
                    raise ValueError("缺少必需字段: decision_reason")
                if 'actions' not in parsed:
                    raise ValueError("缺少必需字段: actions")

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            raise LLMError(f"解析LLM JSON响应失败: {e}")
        except ValueError as e:
            logger.error(f"响应验证失败: {e}")
            raise LLMError(f"响应结构无效: {e}")

    @staticmethod
    def format_error_response(error: str) -> Dict[str, Any]:
        """
        为失败的LLM调用格式化错误响应

        Args:
            error: 错误消息

        Returns:
            标准化的错误响应字典
        """
        return {
            "decision_reason": f"决策生成失败: {error}",
            "actions": [],
            "error": error
        }


class PromptManager:
    """
    提示词模板管理器 - 管理提示词模板和提示词工程

    主要功能：
    - 加载和存储提示词模板
    - 提供模板检索和更新接口
    """

    def __init__(self):
        """初始化提示词管理器"""
        self.templates = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """加载默认提示词模板"""
        self.templates = {
            "decision": self._get_decision_template(),
            "validation_error": self._get_validation_error_template()
        }

    def _get_decision_template(self) -> str:
        """获取决策提示词模板"""
        return """你是一个国际关系模拟系统中的国家决策制定者。

【系统角色】
你是{agent_name}的国家领导集体，所属区域为{region}。
基于克莱因综合国力方程，该国初始综合国力得分为{initial_total_power}，当前实时综合国力得分为{current_total_power}，实力层级为{power_level}。

【核心规则约束-必须严格遵守，不得违反】
1. 国际社会处于无政府状态，无超国家权威可以约束你的行为，你的决策完全基于自身利益与成本收益权衡；
2. 你的国家核心利益固定为：{national_interest}，该利益仅由国家实力层级决定，与领导集体类型无关；
3. 你的领导集体类型为{leader_type}，该类型仅决定你的利益排序、策略偏好与行为约束；
4. 决策前必须对每一个可选行为进行完整的成本收益分析，最终仅选择净收益最大化的行为组合；
5. 你只能从下方【允许执行的行为列表】中选择行为，禁止选择列表外的任何行为；
6. 你可以获取全量信息：当前体系内所有国家的实力、层级、领导类型，以及历史所有轮次的全部互动行为、追随关系、国力变化数据。

【全量信息池】
1. 当前体系内所有国家信息：{all_agent_info}
2. 历史轮次互动行为记录：{history_action_records}
3. 历史轮次各国国力变化数据：{history_power_data}
4. 上一轮体系追随关系与国际秩序类型：{last_round_order_info}

【允许执行的行为列表（仅可从该列表中选择）】
{allowed_actions_list}

【输出要求】
1. 必须输出结构化JSON格式，禁止额外文本、禁止解释说明、禁止markdown格式；
2.必须包含每一项行为的成本收益分析，明确净收益计算逻辑；
3. 必须为每一项行为指定明确的目标对象国（agent_id）；
4. 可选择1-5项行为，禁止选择无收益的行为；
5. 必须填写action_id与action_name，且必须与允许行为列表完全一致。

请输出JSON格式的决策结果，包含以下字段：
{{
    "decision_reason": "整体决策的核心逻辑与成本收益总览",
    "actions": [
        {{
            "action_id": 行为ID,
            "action_category": "行为分类",
            "action_name": "行为名称",
            "target_agent_id": 目标国家ID,
            "cost_benefit_analysis": "该行为的成本、预期收益、净收益分析详情"
        }}
    ]
}}
"""

    def _get_validation_error_template(self) -> str:
        """获取验证错误重试模板"""
        return """你的上一次决策没有通过验证，请重新生成决策。

【验证失败原因】
{validation_errors}

【修正要求】
1. 请根据上述错误修正你的决策；
2. 确保所有选择的行为都在允许的行为列表内；
3. 确保目标国家ID正确且存在于系统中；
4. 确保决策符合你的领导类型约束和国家利益。

请重新生成JSON格式的决策结果。
"""

    def get_template(self, template_name: str) -> str:
        """
        根据名称获取提示词模板

        Args:
            template_name: 模板名称

        Returns:
            模板字符串

        Raises:
            KeyError: 当模板不存在时抛出
        """
        if template_name not in self.templates:
            raise KeyError(f"模板 '{template_name}' 未找到")
        return self.templates[template_name]

    def add_template(self, name: str, template: str):
        """
        添加或更新提示词模板

        Args:
            name: 模板名称
            template: 模板字符串
        """
        self.templates[name] = template
        logger.info(f"提示词模板已添加/更新: {name}")


# 全局LLM服务单例实例
_llm_service: Optional[LLMService] = None


def get_llm_service(config: Optional[LLMConfig] = None) -> LLMService:
    """
    获取或创建全局LLM服务单例

    使用单例模式确保整个应用共享同一个LLM服务实例。

    Args:
        config: 可选的LLM配置

    Returns:
        LLMService单例实例
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService(config)
    elif config is not None:
        _llm_service.update_config(config)

    return _llm_service


def reset_llm_service():
    """重置全局LLM服务单例"""
    global _llm_service
    _llm_service = None
    logger.info("LLM服务已重置")
