# Preset Scene APIs
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.services.scene_service import scene_service

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
    scenes = await scene_service.get_preset_scenes()
    return [PresetSceneResponse(**scene) for scene in scenes]


@router.get("/{scene_id}", response_model=PresetSceneResponse)
async def get_preset_scene(scene_id: int):
    """
    获取单个场景详情
    """
    scene = await scene_service.get_preset_scene(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Preset scene not found")
    return PresetSceneResponse(**scene)


@router.post("/{scene_id}/create-project", response_model=CreateProjectFromSceneResponse)
async def create_project_from_scene(scene_id: int, request: CreateProjectFromSceneRequest):
    """
    从预置场景一键创建仿真项目
    """
    project = await scene_service.create_project_from_scene(
        scene_id=scene_id,
        project_name=request.project_name,
        project_desc=request.project_desc
    )

    if not project:
        raise HTTPException(status_code=404, detail="Preset scene not found")

    return CreateProjectFromSceneResponse(
        project_id=project["project_id"],
        project_name=project["project_name"],
        status=project["status"]
    )
