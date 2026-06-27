"""
仿真管理API模块

该模块提供仿真项目的完整生命周期管理接口，包括项目创建、智能体配置、
仿真控制和数据查询等功能，是整个系统的核心API入口。
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
import io
from datetime import datetime

from app.services.project_service import project_service
from app.services.agent_service import agent_service, AgentConfig
from app.services.simulation_service import simulation_service
from app.models import ActionRecord, AgentConfig as AgentConfigModel, FollowerRelation, SimulationRound
from sqlalchemy import select
from app.config.database import db_config

# 创建路由
router = APIRouter(prefix="/simulation", tags=["simulation"])

# 请求/响应模型
class ProjectResponse(BaseModel):
    """项目响应模型"""
    project_id: int
    project_name: str
    project_desc: Optional[str]
    scene_source: str
    total_rounds: int
    current_round: int
    status: str
    respect_sov_threshold: float
    leader_threshold: float
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime

class CreateProjectRequest(BaseModel):
    """创建项目请求模型"""
    project_name: str
    project_desc: Optional[str] = None
    total_rounds: int = 50
    scene_source: str = "自定义"

class AgentConfigRequest(BaseModel):
    """智能体配置请求模型 (CINC版)

    使用CINC（Composite Index of National Capability）底层指标。
    CINC指数是基于6项底层指标在体系内总和的占比计算的（0-1比例值）。
    """
    agent_name: str
    region: str
    milex: float = 0
    milper: float = 0
    irst: float = 0
    pec: float = 0
    tpop: float = 0
    upop: float = 0
    country_code: Optional[int] = None
    cinc_year: Optional[int] = None
    leader_type: Optional[str] = None

class AgentResponse(BaseModel):
    """智能体响应模型 (CINC版)

    initial_total_power 和 current_total_power 现为 CINC指数（0-1比例值）。
    power_level 按CINC在仿真体系内的相对排名动态判定。
    """
    agent_id: int
    agent_name: str
    region: str
    milex: float
    milper: float
    irst: float
    pec: float
    tpop: float
    upop: float
    country_code: Optional[int] = None
    cinc_year: Optional[int] = None
    initial_total_power: float
    current_total_power: float
    power_level: str
    leader_type: Optional[str]

class ActionRecordResponse(BaseModel):
    """行为记录响应模型"""
    record_id: int
    project_id: int
    round_num: int
    action_stage: str
    source_agent_id: int
    source_agent_name: Optional[str]
    target_agent_id: int
    target_agent_name: Optional[str]
    action_id: int
    action_name: str
    action_category: str
    respect_sov: bool
    initiator_power_change: float
    target_power_change: float
    decision_detail: Optional[str]
    action_content: Optional[str]

class FollowerRelationResponse(BaseModel):
    """追随者关系响应模型"""
    relation_id: int
    follower_agent_id: int
    follower_agent_name: Optional[str]
    leader_agent_id: Optional[int]
    leader_agent_name: Optional[str]

class RoundDetailResponse(BaseModel):
    """单轮详情响应模型"""
    round_num: int
    actions: List[ActionRecordResponse]
    total_actions: int
    respect_sov_actions: int
    has_leader: bool
    follower_relations: List[FollowerRelationResponse]
    leader_agent_id: Optional[int]
    leader_follower_ratio: Optional[float]
    order_type: Optional[str]


# 项目管理API
@router.get("/project/list")
async def get_projects(
    status: Optional[str] = Query(None, description="状态筛选"),
    scene_source: Optional[str] = Query(None, description="场景来源筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索(项目名/描述)"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort: str = Query("updated_at_desc", description="排序字段,如 created_at_desc"),
):
    """
    获取仿真项目列表（支持分页、筛选、排序）

    Args:
        status: 状态筛选（可选）
        scene_source: 场景来源筛选（可选）
        keyword: 关键词搜索（匹配项目名或描述）（可选）
        page: 页码（从1开始）
        size: 每页条数
        sort: 排序字段，格式为 "field_desc" 或 "field_asc"

    Returns:
        dict: {"total": int, "items": List[dict]}
    """
    result = await project_service.get_projects(
        status_filter=status,
        scene_source=scene_source,
        keyword=keyword,
        page=page,
        size=size,
        sort=sort,
    )
    return result


@router.post("/project", response_model=ProjectResponse)
async def create_project(request: CreateProjectRequest):
    """
    创建自定义仿真项目

    创建一个新的仿真项目，支持自定义项目名称、描述、总轮数和场景来源。

    Args:
        request: 创建项目请求

    Returns:
        ProjectResponse: 新创建的项目信息
    """
    project = await project_service.create_project(
        project_name=request.project_name,
        project_desc=request.project_desc,
        total_rounds=request.total_rounds,
        scene_source=request.scene_source
    )
    return ProjectResponse(**project)


@router.get("/project/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """
    获取项目详情

    根据项目ID获取项目的完整信息，包括项目配置、智能体列表和仿真状态。

    Args:
        project_id: 项目ID

    Returns:
        ProjectResponse: 项目详情

    Raises:
        HTTPException: 项目不存在时返回404错误
    """
    project = await project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project)


@router.put("/project/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, request: CreateProjectRequest):
    """
    更新项目基础信息

    更新项目的基本信息，包括项目名称、描述、总轮数和场景来源。

    Args:
        project_id: 项目ID
        request: 更新请求

    Returns:
        ProjectResponse: 更新后的项目信息

    Raises:
        HTTPException: 项目不存在时返回404错误
    """
    project = await project_service.update_project(
        project_id,
        project_name=request.project_name,
        project_desc=request.project_desc,
        total_rounds=request.total_rounds,
        scene_source=request.scene_source
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**project)


@router.delete("/project/{project_id}")
async def delete_project(project_id: int):
    """
    删除仿真项目

    删除指定的仿真项目，包括项目配置、关联数据和 logs 目录。

    Args:
        project_id: 项目ID

    Returns:
        dict: 删除成功消息

    Raises:
        HTTPException: 项目不存在时返回404错误
    """
    success = await project_service.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted successfully"}


@router.get("/project/{project_id}/export")
async def export_project(project_id: int):
    """
    导出项目数据

    将指定项目的所有数据和日志打包为 ZIP 下载。

    Args:
        project_id: 项目ID

    Returns:
        StreamingResponse: ZIP 文件流

    Raises:
        HTTPException: 项目不存在时返回404错误
    """
    zip_bytes = await project_service.export_project(project_id)
    if zip_bytes is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return StreamingResponse(
        io.BytesIO(zip_bytes),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="simulation_{project_id}_export.zip"'
        },
    )


# 智能体配置API
@router.post("/project/{project_id}/agent", response_model=AgentResponse)
async def add_agent(project_id: int, request: AgentConfigRequest):
    """
    为项目添加智能体

    为指定项目添加新的智能体，配置智能体的基本属性和初始状态。

    Args:
        project_id: 项目ID
        request: 智能体配置请求

    Returns:
        AgentResponse: 新添加的智能体信息

    Raises:
        HTTPException: 配置无效时返回400错误
    """
    try:
        config = AgentConfig(
            agent_name=request.agent_name,
            region=request.region,
            milex=request.milex,
            milper=request.milper,
            irst=request.irst,
            pec=request.pec,
            tpop=request.tpop,
            upop=request.upop,
            country_code=request.country_code,
            cinc_year=request.cinc_year,
            leader_type=request.leader_type
        )
        agent = await agent_service.add_agent(project_id, config)
        return AgentResponse(**agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/project/{project_id}/agent/list", response_model=List[AgentResponse])
async def get_agents(project_id: int):
    """
    获取项目智能体列表

    获取指定项目的所有智能体配置信息。

    Args:
        project_id: 项目ID

    Returns:
        List[AgentResponse]: 智能体列表
    """
    agents = await agent_service.get_agents(project_id)
    return [AgentResponse(**a) for a in agents]


@router.get("/project/{project_id}/agent/{agent_id}", response_model=AgentResponse)
async def get_agent(project_id: int, agent_id: int):
    """
    获取智能体详情

    获取指定智能体的详细配置信息和状态。

    Args:
        project_id: 项目ID
        agent_id: 智能体ID

    Returns:
        AgentResponse: 智能体详情

    Raises:
        HTTPException: 智能体不存在时返回404错误
    """
    agent = await agent_service.get_agent(project_id, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**agent)


@router.put("/project/{project_id}/agent/{agent_id}", response_model=AgentResponse)
async def update_agent(project_id: int, agent_id: int, request: AgentConfigRequest):
    """
    更新智能体初始配置

    更新智能体的初始配置信息。

    Args:
        project_id: 项目ID
        agent_id: 智能体ID
        request: 更新请求

    Returns:
        AgentResponse: 更新后的智能体信息

    Raises:
        HTTPException: 智能体不存在时返回404错误，配置无效时返回400错误
    """
    try:
        config = AgentConfig(
            agent_name=request.agent_name,
            region=request.region,
            milex=request.milex,
            milper=request.milper,
            irst=request.irst,
            pec=request.pec,
            tpop=request.tpop,
            upop=request.upop,
            country_code=request.country_code,
            cinc_year=request.cinc_year,
            leader_type=request.leader_type
        )
        agent = await agent_service.update_agent(project_id, agent_id, config)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentResponse(**agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/project/{project_id}/agent/{agent_id}")
async def delete_agent(project_id: int, agent_id: int):
    """
    删除智能体

    删除项目中的指定智能体。

    Args:
        project_id: 项目ID
        agent_id: 智能体ID

    Returns:
        dict: 删除成功消息

    Raises:
        HTTPException: 智能体不存在时返回404错误
    """
    success = await agent_service.delete_agent(project_id, agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}


# 仿真控制API
@router.post("/{project_id}/start")
async def start_simulation(project_id: int):
    """
    启动仿真项目

    启动指定项目的仿真运行。

    Args:
        project_id: 项目ID

    Returns:
        dict: 启动结果
    """
    try:
        result = await simulation_service.start_simulation(project_id)
        print(f">>> [DIAG] API start_simulation 返回: {result}", flush=True)
        return result
    except Exception as e:
        print(f">>> [DIAG] API start_simulation 异常: {e}", flush=True)
        raise


@router.post("/{project_id}/step")
async def step_simulation(project_id: int):
    """
    单步执行一轮仿真

    单步执行一轮仿真，用于调试和观察仿真过程。

    Args:
        project_id: 项目ID

    Returns:
        dict: 执行结果
    """
    result = await simulation_service.step_simulation(project_id)
    return result


@router.post("/{project_id}/pause")
async def pause_simulation(project_id: int):
    """
    暂停仿真

    暂停正在运行的仿真。

    Args:
        project_id: 项目ID

    Returns:
        dict: 暂停结果
    """
    result = await simulation_service.pause_simulation(project_id)
    return result


@router.post("/{project_id}/resume")
async def resume_simulation(project_id: int):
    """
    继续仿真

    继续暂停的仿真运行。

    Args:
        project_id: 项目ID

    Returns:
        dict: 继续结果
    """
    result = await simulation_service.resume_simulation(project_id)
    return result


@router.post("/{project_id}/stop")
async def stop_simulation(project_id: int):
    """
    终止仿真

    终止正在运行的仿真。

    Args:
        project_id: 项目ID

    Returns:
        dict: 终止结果
    """
    result = await simulation_service.stop_simulation(project_id)
    return result


@router.post("/{project_id}/reset")
async def reset_simulation(project_id: int):
    """
    重置仿真

    重置仿真项目到初始状态。

    Args:
        project_id: 项目ID

    Returns:
        dict: 重置结果
    """
    result = await simulation_service.reset_simulation(project_id)
    return result


@router.get("/running-status")
async def get_running_status():
    """
    获取所有运行中/暂停项目的实时状态摘要

    返回每个活跃项目的进度信息和全局LLM并发使用量。
    用于前端多项目监控面板。
    """
    from app.core.llm_concurrency import get_global_llm_concurrency

    result = await project_service.get_projects(
        page=1, size=100, sort="updated_at_desc"
    )
    all_projects = result.get("items", [])

    active_statuses = {"运行中", "暂停"}
    active_projects = [
        {
            "project_id": p.get("project_id"),
            "project_name": p.get("project_name", ""),
            "status": p.get("status", ""),
            "current_round": p.get("current_round", 0),
            "total_rounds": p.get("total_rounds", 0),
            "scene_source": p.get("scene_source", ""),
        }
        for p in all_projects
        if p.get("status") in active_statuses
    ]

    global_llm = get_global_llm_concurrency()
    concurrency = {
        "used": global_llm.used,
        "total": global_llm.total,
    }

    return {
        "projects": active_projects,
        "global_concurrency": concurrency,
    }


@router.get("/{project_id}/round/{round_num}", response_model=RoundDetailResponse)
async def get_round_detail(project_id: int, round_num: int):
    """
    获取指定轮次的详细行为记录

    获取指定轮次的完整仿真数据，包括行为记录、智能体状态和秩序特征。

    Args:
        project_id: 项目ID
        round_num: 轮次号

    Returns:
        RoundDetailResponse: 单轮详情
    """
    async for session in db_config.get_session():
        # 查询行为记录
        result = await session.execute(
            select(ActionRecord)
            .where(ActionRecord.project_id == project_id)
            .where(ActionRecord.round_num == round_num)
        )
        records = result.scalars().all()

        # 获取智能体名称映射
        agents_result = await session.execute(
            select(AgentConfigModel).where(AgentConfigModel.project_id == project_id)
        )
        agents = agents_result.scalars().all()
        agent_names = {agent.agent_id: agent.agent_name for agent in agents}

        # 获取追随者关系
        follower_relations_result = await session.execute(
            select(FollowerRelation)
            .where(FollowerRelation.project_id == project_id)
            .where(FollowerRelation.round_num == round_num)
        )
        follower_relations = follower_relations_result.scalars().all()

        # 查询轮次记录获取领导者信息
        round_result = await session.execute(
            select(SimulationRound)
            .where(SimulationRound.project_id == project_id)
            .where(SimulationRound.round_num == round_num)
        )
        round_record = round_result.scalar_one_or_none()

        # 构建响应
        action_responses = []
        respect_sov_count = 0

        for record in records:
            source_name = agent_names.get(record.source_agent_id, f"Agent_{record.source_agent_id}")
            target_name = agent_names.get(record.target_agent_id, f"Agent_{record.target_agent_id}")

            # 统计尊重主权行为（Boolean字段直接使用）
            if record.respect_sov:
                respect_sov_count += 1

            action_responses.append(ActionRecordResponse(
                record_id=record.record_id,
                project_id=record.project_id,
                round_num=record.round_num,
                action_stage=record.action_stage,
                source_agent_id=record.source_agent_id,
                source_agent_name=source_name,
                target_agent_id=record.target_agent_id,
                target_agent_name=target_name,
                action_id=record.action_id,
                action_name=record.action_name,
                action_category=record.action_category,
                respect_sov=record.respect_sov,
                initiator_power_change=record.initiator_power_change,
                target_power_change=record.target_power_change,
                decision_detail=record.decision_detail,
                action_content=record.action_content
            ))

        # 构建追随者关系响应
        follower_relation_responses = []
        leader_agent_id = None
        leader_count = 0

        for relation in follower_relations:
            follower_name = agent_names.get(relation.follower_agent_id, f"Agent_{relation.follower_agent_id}")
            leader_name = agent_names.get(relation.leader_agent_id, "中立") if relation.leader_agent_id else "中立"

            follower_relation_responses.append(FollowerRelationResponse(
                relation_id=relation.relation_id,
                follower_agent_id=relation.follower_agent_id,
                follower_agent_name=follower_name,
                leader_agent_id=relation.leader_agent_id,
                leader_agent_name=leader_name
            ))

            # 统计领导者
            if relation.leader_agent_id:
                if leader_agent_id is None:
                    leader_agent_id = relation.leader_agent_id
                if relation.leader_agent_id == leader_agent_id:
                    leader_count += 1

        # 计算领导追随者比例
        total_agents = len(agents)
        leader_follower_ratio = round(leader_count / total_agents, 2) if total_agents > 0 else 0

        return RoundDetailResponse(
            round_num=round_num,
            actions=action_responses,
            total_actions=len(action_responses),
            respect_sov_actions=respect_sov_count,
            has_leader=round_record.has_leader if round_record else False,
            follower_relations=follower_relation_responses,
            leader_agent_id=round_record.leader_agent_id if round_record else leader_agent_id,
            leader_follower_ratio=round_record.leader_follower_ratio if round_record else leader_follower_ratio,
            order_type=round_record.order_type if round_record else None
        )


@router.get("/project/{project_id}/round/{round_num}/llm-prompts")
async def get_llm_prompts(project_id: int, round_num: int):
    """
    获取指定轮次的LLM调用日志（汇总4类LLM调用）。

    覆盖类别：
    - interaction        行动决策（主动/响应）
    - following          追随决策（参与+投票）
    - goal_evaluation    战略目标评估
    - relationship_evolution  战略关系演变

    每条返回项额外注入 `category` 字段，前端可据此分组/打标。

    Args:
        project_id: 项目ID
        round_num: 轮次编号

    Returns:
        List of LLM call logs, each tagged with `category`.
    """
    import json
    from pathlib import Path

    # 类别 -> 日志文件名
    category_files = {
        "interaction": "llm_interaction.log",
        "following": "llm_following.log",
        "goal_evaluation": "llm_goal_evaluation.log",
        "relationship_evolution": "llm_relationship_evolution.log",
    }

    base_dir = Path(f"logs/{project_id}")
    if not base_dir.exists():
        return []

    prompts = []
    for category, filename in category_files.items():
        log_file = base_dir / filename
        if not log_file.exists():
            continue
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        log_entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if log_entry.get('round_num') != round_num:
                        continue
                    log_entry['category'] = category
                    prompts.append(log_entry)
        except Exception:
            # 单个文件读取失败不影响其它类别
            continue

    # 按时间戳排序，便于前端按发生顺序展示
    prompts.sort(key=lambda e: e.get('timestamp', ''))
    return prompts
