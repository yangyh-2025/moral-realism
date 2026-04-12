# Main Router - Aggregates all API routers
from fastapi import APIRouter
from .preset_scene import router as preset_scene_router
from .action_config import router as action_config_router
from .simulation import router as simulation_router
from .statistics import router as statistics_router
from .system import router as system_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
api_router.include_router(preset_scene_router)
api_router.include_router(action_config_router)
api_router.include_router(simulation_router)
api_router.include_router(statistics_router)
api_router.include_router(system_router)

__all__ = ["api_router"]
