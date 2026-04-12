# Preset Scene APIs
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/preset-scene", tags=["preset_scene"])

# Request/Response Models
class PresetSceneResponse(BaseModel):
    scene_id: int
    scene_name: str
    scene_desc: str
    total_rounds: int
    agent_config_json: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

class CreateProjectFromSceneRequest(BaseModel):
    scene_id: int
    project_name: str | None = None
    project_desc: str | None = None

class CreateProjectFromSceneResponse(BaseModel):
    project_id: int
    project_name: str
    status: str



@router.get("/list", response_model=List[PresetSceneResponse])
async def get_preset_scenes():
    """
    获取所有预置仿真场景列表
    """
    # TODO: Implement actual logic to fetch preset scenes from database
    # This is a placeholder implementation
    return [
        PresetSceneResponse(
            scene_id=1,
            scene_name="单极霸权体系",
            scene_desc="模拟单极体系下超级大国霸权维持与新兴大国挑战的动态博弈",
            total_rounds=50,
            agent_config_json='{"agents": []}',
            is_default=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]


@router.get("/{scene_id}", response_model=PresetSceneResponse)
async def get_preset_scene(scene_id: int):
    """
    获取单个场景详情
    """
    # TODO: Implement actual logic to fetch single preset scene
    if scene_id == 1:
        return PresetSceneResponse(
            scene_id=1,
            scene_name="单极霸权体系",
            scene_desc="模拟单极体系下超级大国霸权维持与新兴大国挑战的动态博弈",
            total_rounds=50,
            agent_config_json='{"agents": []}',
            is_default=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    raise HTTPException(status_code=404, detail="Preset scene not found")


@router.post("/{scene_id}/create-project", response_model=CreateProjectFromSceneResponse)
async def create_project_from_scene(request: CreateProjectFromSceneRequest):
    """
    从预置场景一键创建仿真项目
    """
    # TODO: Implement actual logic to create project from preset scene
    return CreateProjectFromSceneResponse(
        project_id=1,
        project_name=request.project_name or f"Project from Scene {request.scene_id}",
        status="未启动"
    )
