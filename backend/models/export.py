"""
导出相关数据模型

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ExportFormat(str, Enum):
    """导出格式"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF_REPORT = "pdf_report"


class ExportFilters(BaseModel):
    """导出过滤器"""
    round_start: Optional[int] = None
    round_end: Optional[int] = None
    agent_rounds: Optional[List[str]] = None
    event_types: Optional[List[str]] = None
    include_agents: bool = True
    include_events: bool = True
    include_decisions: bool = True
    include_metrics: bool = True


class ExportRequest(BaseModel):
    """导出请求"""
    simulation_id: str = Field(..., description="仿真ID")
    format: ExportFormat = Field(default=ExportFormat.JSON, description="导出格式")
    filters: Optional[ExportFilters] = None
    filename: Optional[str] = None


class ExportResult(BaseModel):
    """导出结果"""
    success: bool
    message: str
    filename: str
    format: ExportFormat
    size_bytes: int
    record_count: int
