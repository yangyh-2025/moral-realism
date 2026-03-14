"""
事件管理API路由 - 事件触发、配置和历史查询

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter()


class EventType(str, Enum):
    """事件类型"""
    PERIODIC = "periodic"
    RANDOM = "random"
    USER_DEFINED = "user_defined"


class Event(BaseModel):
    """事件"""
    id: str
    simulation_id: Optional[str] = None
    event_type: EventType
    name: str
    description: Optional[str] = None
    active: bool = False
    affected_agents: List[str] = []
    effects: Dict[str, Any] = {}
    probability: float = 0.0
    timestamp: Optional[datetime] = None
    created_at: datetime


class EventConfig(BaseModel):
    """事件配置"""
    random_event_prob: float = Field(default=0.1, ge=0.0, le=1.0)
    periodic_events_enabled: bool = True
    user_event_validation: bool = True
    auto_trigger_threshold: int = 5


class TriggerRequest(BaseModel):
    """事件触发请求"""
    event_id: str
    simulation_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class EventResult(BaseModel):
    """事件触发结果"""
    event_id: str
    success: bool
    message: str
    effects: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


# 内存存储
_events_store: Dict[str, Event] = {}
_event_config = EventConfig()


@router.get("/events", response_model=List[Event])
async def list_events(simulation_id: Optional[str] = None):
    """
    列出所有事件

    Args:
        simulation_id: 按仿真ID筛选

    Returns:
        List[Event]: 事件列表
    """
    events = list(_events_store.values())

    if simulation_id:
        events = [e for e in events if e.simulation_id == simulation_id]

    return events


@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """
    获取事件详情

    Args:
        event_id: 事件ID

    Returns:
        Event: 事件详情
    """
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail=f"事件 {event_id} 不存在")

    return _events_store[event_id]


@router.post("/events", response_model=Event)
async def create_event(event: Event):
    """
    创建事件

    Args:
        event: 事件数据

    Returns:
        Event: 创建的事件
    """
    if not event.id:
        event.id = str(uuid.uuid4())

    if not event.created_at:
        event.created_at = datetime.now()

    _events_store[event.id] = event
    return event


@router.post("/events/trigger", response_model=EventResult)
async def trigger_event(request: TriggerRequest):
    """
    触发事件

    Args:
        request: 触发请求

    Returns:
        EventResult: 触发结果
    """
    if request.event_id not in _events_store:
        raise HTTPException(status_code=404, detail=f"事件 {request.event_id} 不存在")

    event = _events_store[request.event_id]

    # 验证事件是否属于指定仿真
    if event.simulation_id and event.simulation_id != request.simulation_id:
        raise HTTPException(
            status_code=400,
            detail=f"事件不属于仿真 {request.simulation_id}"
        )

    # 激活事件
    event.active = True
    event.timestamp = datetime.now()

    # 在实际实现中，这里会执行事件效果
    effects = {
        "affected_agents": event.affected_agents,
        "applied_effects": event.effects,
        "parameters": request.parameters
    }

    return EventResult(
        event_id=request.event_id,
        success=True,
        message=f"事件 {event.name} 已触发",
        effects=effects,
        timestamp=datetime.now()
    )


@router.post("/events/config", response_model=EventConfig)
async def update_event_config(config: EventConfig):
    """
    更新事件配置

    Args:
        config: 新的配置

    Returns:
        EventConfig: 更新后的配置
    """
    global _event_config
    _event_config = config
    return _event_config


@router.get("/events/config", response_model=EventConfig)
async def get_event_config():
    """
    获取事件配置

    Returns:
        EventConfig: 当前配置
    """
    return _event_config


@router.get("/events/history/{simulation_id}", response_model=List[Event])
async def get_event_history(
    simulation_id: str,
    event_type: Optional[EventType] = None,
    limit: int = 100
):
    """
    获取事件历史

    Args:
        simulation_id: 仿真ID
        event_type: 按事件类型筛选
        limit: 返回数量限制

    Returns:
        List[Event]: 事件历史列表
    """
    events = [
        e for e in _events_store.values()
        if e.simulation_id == simulation_id and e.active
    ]

    if event_type:
        events = [e for e in events if e.event_type == event_type]

    # 按时间排序（最新的在前）
    events.sort(key=lambda e: e.timestamp or e.created_at, reverse=True)

    return events[:limit]


@router.put("/events/{event_id}")
async def update_event(event_id: str, event: Event):
    """
    更新事件

    Args:
        event_id: 事件ID
        event: 新的事件数据

    Returns:
        Event: 更新后的事件
    """
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail=f"事件 {event_id} 不存在")

    # 保持原有的ID和创建时间
    event.id = event_id
    event.created_at = _events_store[event_id].created_at

    _events_store[event_id] = event
    return event


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """
    删除事件

    Args:
        event_id: 事件ID
    """
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail=f"事件 {event_id} 不存在")

    del _events_store[event_id]
    return {"message": f"事件 {event_id} 已删除"}


@router.post("/events/batch", response_model=List[Event])
async def create_events_batch(events: List[Event]):
    """
    批量创建事件

    Args:
        events: 事件列表

    Returns:
        List[Event]: 创建的事件列表
    """
    created_events = []

    for event in events:
        if not event.id:
            event.id = str(uuid.uuid4())

        if not event.created_at:
            event.created_at = datetime.now()

        _events_store[event.id] = event
        created_events.append(event)

    return created_events


@router.post("/events/{event_id}/activate")
async def activate_event(event_id: str):
    """
    激活事件

    Args:
        event_id: 事件ID
    """
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail=f"事件 {event_id} 不存在")

    _events_store[event_id].active = True
    _events_store[event_id].timestamp = datetime.now()

    return {"message": f"事件 {event_id} 已激活"}


@router.post("/events/{event_id}/deactivate")
async def deactivate_event(event_id: str):
    """
    停用事件

    Args:
        event_id: 事件ID
    """
    if event_id not in _events_store:
        raise HTTPException(status_code=404, detail=f"事件 {event_id} 不存在")

    _events_store[event_id].active = False

    return {"message": f"事件 {event_id} 已停用"}
