# System Config APIs
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from loguru import logger

from app.services.system_service import get_system_config_service

router = APIRouter(prefix="/system", tags=["system"])

# Request/Response Models
class SystemConfigResponse(BaseModel):
    llm_model_name: str
    llm_api_key: str
    llm_api_base: Optional[str]
    llm_timeout: int
    llm_max_retries: int
    simulation_concurrency: int
    log_level: str
    default_scene_id: Optional[int]


class UpdateSystemConfigRequest(BaseModel):
    llm_model_name: Optional[str] = None
    llm_api_key: Optional[str] = None
    llm_api_base: Optional[str] = None
    llm_timeout: Optional[int] = None
    llm_max_retries: Optional[int] = None
    simulation_concurrency: Optional[int] = None
    log_level: Optional[str] = None
    default_scene_id: Optional[int] = None


def _config_dict_to_response(config_dict: dict) -> SystemConfigResponse:
    """Convert config dict to response model"""
    # Helper to safely parse int
    def safe_int(value, default):
        try:
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    # Helper to safely parse optional int
    def safe_opt_int(value):
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    return SystemConfigResponse(
        llm_model_name=config_dict.get("llm_model_name", "gpt-4"),
        llm_api_key=config_dict.get("llm_api_key", ""),
        llm_api_base=config_dict.get("llm_api_base"),
        llm_timeout=safe_int(config_dict.get("llm_timeout"), 60),
        llm_max_retries=safe_int(config_dict.get("llm_max_retries"), 3),
        simulation_concurrency=safe_int(config_dict.get("simulation_concurrency"), 5),
        log_level=config_dict.get("log_level", "INFO"),
        default_scene_id=safe_opt_int(config_dict.get("default_scene_id"))
    )


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config():
    """
    获取系统配置
    """
    logger.info("Fetching system config")
    service = get_system_config_service()
    config_dict = await service.get_system_config()
    return _config_dict_to_response(config_dict)


@router.put("/config", response_model=SystemConfigResponse)
async def update_system_config(request: UpdateSystemConfigRequest):
    """
    更新系统配置
    """
    logger.info(f"Updating system config with: {request.dict(exclude_none=True)}")
    service = get_system_config_service()

    # Convert request to dict, excluding None values
    updates = request.dict(exclude_none=True)

    # Update config in database
    config_dict = await service.update_system_config(updates)

    return _config_dict_to_response(config_dict)
