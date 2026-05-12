"""
LLM 调用记录查询 API

提供按项目、类型、轮次、agent 等多维度筛选查询 LLM 调用记录的能力。
列表接口返回摘要（不含全文 prompt/response），详情接口返回完整内容。
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import desc, func, or_, select

from app.config.database import db_config
from app.models.agent_config import AgentConfig
from app.models.llm_call_log import LLMCallLog

router = APIRouter(prefix="/llm-calls", tags=["llm-calls"])


@router.get("/project/{project_id}")
async def get_llm_calls(
    project_id: int,
    call_type: Optional[str] = Query(None, description="LLM调用类型:llm_interaction / llm_following / llm_goal_evaluation / llm_relationship_evolution"),
    phase: Optional[str] = Query(None, description="阶段:initiative / response"),
    agent_id: Optional[int] = Query(None, description="发起方 Agent ID"),
    round_num: Optional[int] = Query(None, description="轮次编号"),
    status: Optional[str] = Query(None, description="状态:success / failed / timeout / retried"),
    keyword: Optional[str] = Query(None, description="关键词搜索(prompt/response)"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页条数"),
    sort: str = Query("created_at_desc", description="排序字段"),
):
    """
    查询指定项目的 LLM 调用记录列表

    列表只返回摘要（不含 prompt/response 全文），节省带宽。
    详情请调用 /llm-calls/{call_id}。
    """
    async for session in db_config.get_session():
        # 计数
        count_query = select(func.count()).select_from(LLMCallLog).where(
            LLMCallLog.project_id == project_id
        )
        query = select(LLMCallLog).where(LLMCallLog.project_id == project_id)

        # 筛选
        if call_type:
            count_query = count_query.where(LLMCallLog.call_type == call_type)
            query = query.where(LLMCallLog.call_type == call_type)
        if phase:
            count_query = count_query.where(LLMCallLog.phase == phase)
            query = query.where(LLMCallLog.phase == phase)
        if agent_id is not None:
            count_query = count_query.where(LLMCallLog.agent_id == agent_id)
            query = query.where(LLMCallLog.agent_id == agent_id)
        if round_num is not None:
            count_query = count_query.where(LLMCallLog.round_num == round_num)
            query = query.where(LLMCallLog.round_num == round_num)
        if status:
            count_query = count_query.where(LLMCallLog.status == status)
            query = query.where(LLMCallLog.status == status)
        if keyword:
            like = f"%{keyword}%"
            count_query = count_query.where(
                or_(LLMCallLog.prompt_full.ilike(like), LLMCallLog.response_full.ilike(like))
            )
            query = query.where(
                or_(LLMCallLog.prompt_full.ilike(like), LLMCallLog.response_full.ilike(like))
            )

        # 排序
        sort_field, sort_dir = sort.rsplit("_", 1) if "_" in sort else ("created_at", "desc")
        sort_col = getattr(LLMCallLog, sort_field, LLMCallLog.created_at)
        if sort_dir == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(desc(sort_col))

        # 总数
        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0

        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        result = await session.execute(query)
        calls = result.scalars().all()

        # 获取 agent 名称映射
        agent_ids = set()
        for c in calls:
            if c.agent_id:
                agent_ids.add(c.agent_id)
            if c.target_agent_id:
                agent_ids.add(c.target_agent_id)

        agent_names: Dict[int, str] = {}
        if agent_ids:
            agent_res = await session.execute(
                select(AgentConfig.agent_id, AgentConfig.agent_name).where(
                    AgentConfig.agent_id.in_(list(agent_ids))
                )
            )
            for row in agent_res.all():
                agent_names[row[0]] = row[1]

        items = []
        for c in calls:
            items.append({
                "call_id": c.call_id,
                "project_id": c.project_id,
                "round_num": c.round_num,
                "call_type": c.call_type,
                "phase": c.phase,
                "agent_id": c.agent_id,
                "agent_name": agent_names.get(c.agent_id),
                "target_agent_id": c.target_agent_id,
                "target_agent_name": agent_names.get(c.target_agent_id),
                "model_name": c.model_name,
                "tokens": (
                    f"{c.prompt_tokens or 0}+{c.completion_tokens or 0}"
                    if c.prompt_tokens or c.completion_tokens
                    else None
                ),
                "latency_ms": c.latency_ms,
                "status": c.status,
                "created_at": c.created_at,
            })

        return {"total": total, "items": items}


@router.get("/{call_id}")
async def get_llm_call_detail(call_id: int) -> Dict[str, Any]:
    """
    获取单条 LLM 调用详情

    返回完整的 prompt、response 和 parsed 结果。
    """
    async for session in db_config.get_session():
        result = await session.execute(
            select(LLMCallLog).where(LLMCallLog.call_id == call_id)
        )
        call = result.scalar_one_or_none()

        if not call:
            raise HTTPException(status_code=404, detail="LLM call not found")

        # agent 名称
        agent_name = None
        target_name = None
        if call.agent_id:
            a = await session.execute(
                select(AgentConfig.agent_name).where(AgentConfig.agent_id == call.agent_id)
            )
            agent_name = a.scalar_one_or_none()
        if call.target_agent_id:
            t = await session.execute(
                select(AgentConfig.agent_name).where(AgentConfig.agent_id == call.target_agent_id)
            )
            target_name = t.scalar_one_or_none()

        return {
            "call_id": call.call_id,
            "project_id": call.project_id,
            "round_num": call.round_num,
            "call_type": call.call_type,
            "phase": call.phase,
            "agent_id": call.agent_id,
            "agent_name": agent_name,
            "target_agent_id": call.target_agent_id,
            "target_agent_name": target_name,
            "model_name": call.model_name,
            "prompt_full": call.prompt_full,
            "response_full": call.response_full,
            "response_parsed": call.response_parsed,
            "prompt_tokens": call.prompt_tokens,
            "completion_tokens": call.completion_tokens,
            "latency_ms": call.latency_ms,
            "status": call.status,
            "error_message": call.error_message,
            "created_at": call.created_at,
        }
