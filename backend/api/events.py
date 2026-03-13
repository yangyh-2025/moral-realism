"""
事件管理API路由

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class Event(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    active: bool = False
    affected_agents: List[str] = []
    effects: dict = {}

# 内存存储（简化实现）
events_store: List[Event] = []

@router.get("", response_model=List[Event])
async def get_all_events():
    """获取所有事件"""
    return events_store

@router.get("/{event_id}", response_model=Event)
async def get_event_by_id(event_id: str):
    """根据ID获取事件"""
    for event in events_store:
        if event.id == event_id:
            return event
    raise HTTPException(status_code=404, detail="事件不存在")

@router.post("", response_model=Event)
async def create_event(event: Event):
    """创建事件"""
    events_store.append(event)
    return event

@router.post("/trigger/{event_id}")
async def trigger_event(event_id: str):
    """触发事件"""
    for event in events_store:
        if event.id == event_id:
            event.active = True
            return {"message": "事件已触发", "event": event}
    raise HTTPException(status_code=404, detail="事件不存在")
