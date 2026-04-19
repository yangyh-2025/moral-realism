"""
系统配置API模块

该模块提供系统级配置管理接口，包括LLM模型配置、仿真参数、
日志级别等系统配置的获取和更新功能。
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger

from app.services.system_service import get_system_config_service

# 创建路由
router = APIRouter(prefix="/system", tags=["system"])

# 请求/响应模型 - 为了前端兼容性使用驼峰命名
class SystemConfigResponse(BaseModel):
    """系统配置响应模型"""
    llmModelName: str
    llmApiKey: str
    llmApiBase: Optional[str]
    llmTimeout: int
    llmMaxRetries: int
    simulationConcurrency: int
    logLevel: str
    defaultSceneId: Optional[int]

    class Config:
        populate_by_name = True


class UpdateSystemConfigRequest(BaseModel):
    """更新系统配置请求模型"""
    llmModelName: Optional[str] = None
    llmApiKey: Optional[str] = None
    llmApiBase: Optional[str] = None
    llmTimeout: Optional[int] = None
    llmMaxRetries: Optional[int] = None
    simulationConcurrency: Optional[int] = None
    logLevel: Optional[str] = None
    defaultSceneId: Optional[int] = None

    class Config:
        populate_by_name = True


def _config_dict_to_response(config_dict: dict) -> SystemConfigResponse:
    """
    将配置字典转换为响应模型（蛇形命名转驼峰命名）

    Args:
        config_dict: 配置字典（蛇形命名）

    Returns:
        SystemConfigResponse: 系统配置响应模型
    """
    # 安全解析整数的辅助函数
    def safe_int(value, default):
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    # 安全解析可选整数的辅助函数
    def safe_opt_int(value):
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    return SystemConfigResponse(
        llmModelName=config_dict.get("llm_model_name", "gpt-4"),
        llmApiKey=config_dict.get("llm_api_key", ""),
        llmApiBase=config_dict.get("llm_api_base"),
        llmTimeout=safe_int(config_dict.get("llm_timeout"), 60),
        llmMaxRetries=safe_int(config_dict.get("llm_max_retries"), 3),
        simulationConcurrency=safe_int(config_dict.get("simulation_concurrency"), 5),
        logLevel=config_dict.get("log_level", "INFO"),
        defaultSceneId=safe_opt_int(config_dict.get("default_scene_id"))
    )


def _request_dict_to_snake_case(request_dict: dict) -> dict:
    """
    将请求字典从驼峰命名转换为蛇形命名

    Args:
        request_dict: 请求字典（驼峰命名）

    Returns:
        dict: 转换后的字典（蛇形命名）
    """
    mapping = {
        "llmModelName": "llm_model_name",
        "llmApiKey": "llm_api_key",
        "llmApiBase": "llm_api_base",
        "llmTimeout": "llm_timeout",
        "llmMaxRetries": "llm_max_retries",
        "simulationConcurrency": "simulation_concurrency",
        "logLevel": "log_level",
        "defaultSceneId": "default_scene_id"
    }
    return {mapping.get(k, k): v for k, v in request_dict.items()}


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config():
    """
    获取系统配置

    获取当前系统的完整配置信息，包括LLM模型配置、仿真参数、日志级别等。

    Returns:
        SystemConfigResponse: 系统配置信息
    """
    logger.info("Fetching system config")
    service = get_system_config_service()
    config_dict = await service.get_system_config()
    return _config_dict_to_response(config_dict)


@router.put("/config", response_model=SystemConfigResponse)
async def update_system_config(request: UpdateSystemConfigRequest):
    """
    更新系统配置

    更新系统配置信息，支持部分更新（只更新提供的字段）。

    Args:
        request: 更新请求，包含要更新的配置字段

    Returns:
        SystemConfigResponse: 更新后的系统配置
    """
    logger.info(f"Updating system config with: {request.dict(exclude_none=True)}")
    service = get_system_config_service()

    # 将请求转换为字典，排除None值
    updates = request.dict(exclude_none=True)

    # 将驼峰命名转换为蛇形命名以便后端处理
    updates = _request_dict_to_snake_case(updates)

    # 在数据库中更新配置
    config_dict = await service.update_system_config(updates)

    return _config_dict_to_response(config_dict)
