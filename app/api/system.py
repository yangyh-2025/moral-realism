# System Config APIs
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

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


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config():
    """
    获取系统配置
    """
    # TODO: Implement actual logic to fetch system config from database
    return SystemConfigResponse(
        llm_model_name="gpt-4",
        llm_api_key="",
        llm_api_base=None,
        llm_timeout=120,
        llm_max_retries=3,
        simulation_concurrency=5,
        log_level="INFO",
        default_scene_id=1
    )


@router.put("/config", response_model=SystemConfigResponse)
async def update_system_config(request: UpdateSystemConfigRequest):
    """
    更新系统配置
    """
    # TODO: Implement actual logic to update system config
    return SystemConfigResponse(
        llm_model_name="gpt-4",
        llm_api_key="",
        llm_api_base=None,
        llm_timeout=120,
        llm_max_retries=3,
        simulation_concurrency=5,
        log_level="INFO",
        default_scene_id=1
    )
