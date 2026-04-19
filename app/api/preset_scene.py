"""
预置场景API模块

该模块提供预置仿真场景的管理接口，包括场景列表查询、
场景详情获取以及从预置场景创建仿真项目等功能。
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.services.scene_service import scene_service

# 创建路由
router = APIRouter(prefix="/preset-scene", tags=["preset_scene"])

# 请求/响应模型
class PresetSceneResponse(BaseModel):
    """预置场景响应模型"""
    scene_id: int
    scene_name: str
    scene_desc: str
    total_rounds: int
    agent_config_json: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

class CreateProjectFromSceneRequest(BaseModel):
    """从场景创建项目请求模型"""
    scene_id: int
    project_name: str | None = None
    project_desc: str | None = None

class CreateProjectFromSceneResponse(BaseModel):
    """从场景创建项目响应模型"""
    project_id: int
    project_name: str
    status: str



@router.get("/list", response_model=List[PresetSceneResponse])
async def get_preset_scenes():
    """
    获取所有预置仿真场景列表

    返回系统中所有可用的预置场景配置，包括场景名称、描述、
    总轮数和智能体配置等信息。
    """
    scenes = await scene_service.get_preset_scenes()
    return [PresetSceneResponse(**scene) for scene in scenes]


@router.get("/{scene_id}", response_model=PresetSceneResponse)
async def get_preset_scene(scene_id: int):
    """
    获取单个场景详情

    根据场景ID获取指定预置场景的详细配置信息。

    Args:
        scene_id: 场景ID

    Returns:
        预置场景详细信息

    Raises:
        HTTPException: 场景不存在时返回404错误
    """
    scene = await scene_service.get_preset_scene(scene_id)
    if not scene:
        raise HTTPException(status_code=404, detail="Preset scene not found")
    return PresetSceneResponse(**scene)


@router.post("/{scene_id}/create-project", response_model=CreateProjectFromSceneResponse)
async def create_project_from_scene(scene_id: int, request: CreateProjectFromSceneRequest):
    """
    从预置场景一键创建仿真项目

    使用指定的预置场景配置快速创建一个新的仿真项目，
    包括智能体配置和仿真参数设置。

    Args:
        scene_id: 预置场景ID
        request: 创建项目请求，包含项目名称和描述

    Returns:
        创建的项目信息，包括项目ID、名称和状态

    Raises:
        HTTPException: 场景不存在时返回404错误
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
