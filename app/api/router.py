"""
API路由聚合模块

该模块负责聚合所有子API路由，构建统一的API路由树。
所有API端点都通过/api/v1前缀进行访问。
"""

from fastapi import APIRouter
from .preset_scene import router as preset_scene_router
from .action_config import router as action_config_router
from .simulation import router as simulation_router
from .statistics import router as statistics_router
from .system import router as system_router

# 创建主API路由
api_router = APIRouter(prefix="/api/v1")

# 包含所有子路由
api_router.include_router(preset_scene_router)
api_router.include_router(action_config_router)
api_router.include_router(simulation_router)
api_router.include_router(statistics_router)
api_router.include_router(system_router)

__all__ = ["api_router"]
