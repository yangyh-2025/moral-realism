"""
LLM service for ABM simulation.
Handles LLM model configuration, API calls, and response parsing.
Aligned with technical spec section 4.2.4.
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
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: str = "openai"
    model_name: str = "gpt-4"
    api_key: str = ""
    api_base: str = ""  # Optional custom API base URL
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds


class LLMService:
    """Service for LLM operations with retry logic and error handling."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM service.

        Args:
            config: LLM configuration (uses env vars if not provided)
        """
        self.config = config or self._load_default_config()
        self._client: Optional[AsyncOpenAI] = None
        self._initialize_client()

    def _load_default_config(self) -> LLMConfig:
        """
        Load default configuration from environment variables.

        Returns:
            LLMConfig with values from environment
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
        """Initialize OpenAI async client."""
        try:
            client_kwargs = {
                "api_key": self.config.api_key,
                "timeout": self.config.timeout
            }

            if self.config.api_base:
                client_kwargs["base_url"] = self.config.api_base

            self._client = AsyncOpenAI(**client_kwargs)
            logger.info(f"LLM client initialized: {self.config.provider}/{self.config.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise LLMError(f"LLM client initialization failed: {e}")

    def update_config(self, new_config: LLMConfig):
        """
        Update LLM configuration and reinitialize client.

        Args:
            new_config: New LLM configuration
        """
        self.config = new_config
        self._initialize_client()
        logger.info("LLM configuration updated")

    async def call_llm_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Async LLM call with retry logic.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON response from LLM

        Raises:
            LLMError: If all retries fail
        """
        for attempt in range(self.config.max_retries):
            try:
                response = await self._single_llm_call(prompt, system_prompt)
                return response
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")

                if attempt < self.config.max_retries - 1:
                    # Wait before retry with exponential backoff
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.config.max_retries} LLM retry attempts failed")
                    raise LLMError(f"LLM call failed after {self.config.max_retries} retries: {e}")

    async def _single_llm_call(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Single LLM API call.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Parsed JSON response

        Raises:
            Exception: If API call fails
        """
        if not self._client:
            raise LLMError("LLM client not initialized")

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Make API call
        logger.debug(f"Calling LLM with model: {self.config.model_name}")
        response = await self._client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            response_format={"type": "json_object"}  # Force JSON output
        )

        # Extract response text
        response_text = response.choices[0].message.content
        logger.debug(f"LLM raw response: {response_text[:200]}...")

        # Parse JSON
        try:
            parsed_response = json.loads(response_text)
            logger.info("LLM response parsed successfully")
            return parsed_response
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.error(f"Raw response: {response_text}")
            raise LLMError(f"Invalid JSON response from LLM: {e}")

    async def call_llm_batch_async(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Batch LLM calls with concurrency control.

        Args:
            prompts: List of prompts
            system_prompt: Optional system prompt
            max_concurrent: Maximum concurrent calls

        Returns:
            List of parsed JSON responses
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_call(prompt: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.call_llm_async(prompt, system_prompt)

        logger.info(f"Starting batch LLM calls: {len(prompts)} prompts, max_concurrent={max_concurrent}")
        results = await asyncio.gather(*[limited_call(p) for p in prompts], return_exceptions=True)

        # Check for errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch call {i} failed: {result}")
                results[i] = {"error": str(result)}

        logger.info(f"Batch LLM calls completed: {len(results)} results")
        return results

    def parse_decision_response(
        self,
        response_text: str,
        validate_structure: bool = True
    ) -> Dict[str, Any]:
        """
        Parse LLM decision response.

        Args:
            response_text: Raw response text from LLM
            validate_structure: Whether to validate JSON structure

        Returns:
            Parsed decision dict

        Raises:
            LLMError: If parsing or validation fails
        """
        try:
            # Try to find JSON in response (in case of extra text)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')

            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end + 1]
                parsed = json.loads(json_text)
            else:
                # Try to parse entire response as JSON
                parsed = json.loads(response_text)

            # Basic structure validation
            if validate_structure:
                if 'decision_reason' not in parsed:
                    raise ValueError("Missing required field: decision_reason")
                if 'actions' not in parsed:
                    raise ValueError("Missing required field: actions")

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            raise LLMError(f"Failed to parse LLM JSON response: {e}")
        except ValueError as e:
            logger.error(f"Response validation failed: {e}")
            raise LLMError(f"Invalid response structure: {e}")

    @staticmethod
    def format_error_response(error: str) -> Dict[str, Any]:
        """
        Format error response for failed LLM calls.

        Args:
            error: Error message

        Returns:
            Error response dict
        """
        return {
            "decision_reason": f"决策生成失败: {error}",
            "actions": [],
            "error": error
        }


class PromptManager:
    """Manager for prompt templates and prompt engineering."""

    def __init__(self):
        """Initialize prompt manager."""
        self.templates = {}
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default prompt templates."""
        self.templates = {
            "decision": self._get_decision_template(),
            "validation_error": self._get_validation_error_template()
        }

    def _get_decision_template(self) -> str:
        """Get decision prompt template."""
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
        """Get validation error retry template."""
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
        Get prompt template by name.

        Args:
            template_name: Template name

        Returns:
            Template string

        Raises:
            KeyError: If template not found
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found")
        return self.templates[template_name]

    def add_template(self, name: str, template: str):
        """
        Add or update a prompt template.

        Args:
            name: Template name
            template: Template string
        """
        self.templates[name] = template
        logger.info(f"Prompt template added/updated: {name}")


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service(config: Optional[LLMConfig] = None) -> LLMService:
    """
    Get or create global LLM service instance.

    Args:
        config: Optional LLM configuration

    Returns:
        LLMService instance
    """
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService(config)
    elif config is not None:
        _llm_service.update_config(config)

    return _llm_service


def reset_llm_service():
    """Reset global LLM service instance."""
    global _llm_service
    _llm_service = None
    logger.info("LLM service reset")
