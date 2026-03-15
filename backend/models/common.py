"""
通用数据模型

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误消息")
    code: str = Field(..., description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    status_code: int = Field(400, description="HTTP状态码")


class SuccessResponse(BaseModel):
    """成功响应"""
    success: bool = Field(True, description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")


class Event(BaseModel):
    """事件模型"""
    event_id: str = Field(..., description="事件ID")
    event_type: str = Field(..., description="事件类型")
    name: str = Field(..., description="事件名称")
    description: str = Field(..., description="事件描述")
    participants: List[str] = Field(default_factory=list, description="参与者列表")
    impact_level: float = Field(0.5, ge=0, le=1, description="影响级别")
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class Metric(BaseModel):
    """指标模型"""
    name: str = Field(..., description="指标名称")
    value: float = Field(..., description="指标值")
    category: str = Field(..., description="指标类别")
    timestamp: Optional[datetime] = Field(None, description="时间戳")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class PaginatedResponse(BaseModel):
    """分页响应"""
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")
    data: List[Any] = Field(default_factory=list, description="数据列表")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    uptime: float = Field(..., description="运行时间（秒）")
    database: str = Field(..., description="数据库状态")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="依赖状态")
