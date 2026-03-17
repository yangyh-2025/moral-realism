"""
数据导出API路由 - 支持多种格式的数据导出

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import io
import json
import csv
import re

router = APIRouter()


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

    agent_ids: Optional[List[str]] = None
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


# 模拟数据存储（实际应用中从数据库获取）
_simulations_data: Dict[str, Dict[str, Any]] = {}


async def _get_simulation_data(simulation_id: str) -> Dict[str, Any]:
    """
    获取仿真数据（模拟）

    Args:
        simulation_id: 仿真ID

    Returns:
        Dict: 仿真数据
    """
    # 在实际实现中，这里会从数据库查询数据
    if simulation_id not in _simulations_data:
        # 返回示例数据
        _simulations_data[simulation_id] = {
            "simulation_id": simulation_id,
            "config": {
                "total_rounds": 100,
                "round_duration_months": 6
            },
            "agents": [],
            "events": [],
            "decisions": [],
            "metrics": []
        }

    return _simulations_data[simulation_id]


async def _apply_filters(data: Dict[str, Any], filters: ExportFilters) -> Dict[str, Any]:
    """
    应用过滤器

    Args:
        data: 原始数据
        filters: 过滤器

    Returns:
        Dict: 过滤后的数据
    """
    filtered = {}

    if filters.include_agents:
        filtered["agents"] = data.get("agents", [])

        if filters.agent_ids:
            filtered["agents"] = [
                a for a in filtered["agents"]
                if a.get("id") in filters.agent_ids
            ]

    if filters.include_events:
        filtered["events"] = data.get("events", [])

        if filters.event_types:
            filtered["events"] = [
                e for e in filtered["events"]
                if e.get("type") in filters.event_types
            ]

    if filters.include_decisions:
        filtered["decisions"] = data.get("decisions", [])

    if filters.include_metrics:
        filtered["metrics"] = data.get("metrics", [])

    return filtered


class ExportService:
    """
    数据导出服务

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    async def export_simulation_data(
        self,
        simulation_id: str,
        format: ExportFormat,
        filters: Optional[ExportFilters] = None
    ) -> ExportResult:
        """
        导出仿真数据

        Args:
            simulation_id: 仿真ID
            format: 导出格式
            filters: 过滤器

        Returns:
            ExportResult: 导出结果
        """
        if filters is None:
            filters = ExportFilters()

        data = await _get_simulation_data(simulation_id)
        filtered_data = await _apply_filters(data, filters)

        if format == ExportFormat.JSON:
            return await self._export_json(simulation_id, filtered_data)
        elif format == ExportFormat.CSV:
            return await self._export_csv(simulation_id, filtered_data)
        elif format == ExportFormat.EXCEL:
            return await self._export_excel(simulation_id, filtered_data)
        elif format == ExportFormat.PDF_REPORT:
            return await self._export_pdf_report(simulation_id, filtered_data)
        else:
            raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")

    async def _export_json(
        self,
        simulation_id: str,
        data: Dict[str, Any]
    ) -> ExportResult:
        """导出为JSON格式"""
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        size_bytes = len(json_data.encode("utf-8"))

        record_count = (
            len(data.get("agents", [])) +
            len(data.get("events", [])) +
            len(data.get("decisions", [])) +
            len(data.get("metrics", []))
        )

        filename = f"simulation_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # 存储导出数据
        _simulations_data[f"_export_{filename}"] = {"data": json_data, "format": "json"}

        return ExportResult(
            success=True,
            message="数据导出成功",
            filename=filename,
            format=ExportFormat.JSON,
            size_bytes=size_bytes,
            record_count=record_count
        )

    async def _export_csv(
        self,
        simulation_id: str,
        data: Dict[str, Any]
    ) -> ExportResult:
        """导出为CSV格式"""
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入各类型数据的CSV
        sections = []
        total_records = 0

        if "agents" in data and data["agents"]:
            sections.append(("agents", data["agents"]))
            total_records += len(data["agents"])

        if "events" in data and data["events"]:
            sections.append(("events", data["events"]))
            total_records += len(data["events"])

        if "decisions" in data and data["decisions"]:
            sections.append(("decisions", data["decisions"]))
            total_records += len(data["decisions"])

        for section_name, records in sections:
            writer.writerow([f"--- {section_name} ---"])
            if records:
                # 获取所有字段名
                headers = set()
                for record in records:
                    if isinstance(record, dict):
                        headers.update(record.keys())
                writer.writerow(list(headers))

                # 写入数据
                for record in records:
                    if isinstance(record, dict):
                        row = [str(record.get(h, "")) for h in headers]
                        writer.writerow(row)

            writer.writerow([])  # 空行分隔

        csv_data = output.getvalue()
        size_bytes = len(csv_data.encode("utf-8"))

        filename = f"simulation_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # 存储导出数据
        _simulations_data[f"_export_{filename}"] = {"data": csv_data, "format": "csv"}

        return ExportResult(
            success=True,
            message="数据导出成功",
            filename=filename,
            format=ExportFormat.CSV,
            size_bytes=size_bytes,
            record_count=total_records
        )

    async def _export_excel(
        self,
        simulation_id: str,
        data: Dict[str, Any]
    ) -> ExportResult:
        """导出为Excel格式（简化实现，实际需要openpyxl）"""
        # 简化实现：返回JSON格式的标记
        json_data = json.dumps(data, indent=2, ensure_ascii=False)

        total_records = (
            len(data.get("agents", [])) +
            len(data.get("events", [])) +
            len(data.get("decisions", [])) +
            len(data.get("metrics", []))
        )

        filename = f"simulation_{simulation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        # 在实际实现中，这里会使用openpyxl生成Excel文件
        # 这里简化为存储JSON数据
        _simulations_data[f"_export_{filename}"] = {"data": json_data, "format": "excel"}

        return ExportResult(
            success=True,
            message="数据导出成功（Excel格式需要安装openpyxl）",
            filename=filename,
            format=ExportFormat.EXCEL,
            size_bytes=len(json_data.encode("utf-8")),
            record_count=total_records
        )

    async def _export_pdf_report(
        self,
        simulation_id: str,
        data: Dict[str, Any]
    ) -> ExportResult:
        """导出为PDF报告（简化实现）"""
        # 简化实现：返回JSON格式的标记
        json_data = json.dumps(data, indent=2, ensure_ascii=False)

        total_records = (
            len(data.get("agents", [])) +
            len(data.get("events", [])) +
            len(data.get("decisions", [])) +
            len(data.get("metrics", []))
        )

        filename = f"simulation_{simulation_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # 在实际实现中，这里会使用reportlab或fpdf生成PDF
        _simulations_data[f"_export_{filename}"] = {"data": json_data, "format": "pdf"}

        return ExportResult(
            success=True,
            message="PDF报告生成成功（需要安装reportlab）",
            filename=filename,
            format=ExportFormat.PDF_REPORT,
            size_bytes=len(json_data.encode("utf-8")),
            record_count=total_records
        )


_export_service = ExportService()


def validate_filename(filename: str) -> bool:
    """
    验证文件名安全性，防止路径遍历攻击

    Args:
        filename: 文件名

    Returns:
        是否安全
    """
    # 检查文件名是否为空
    if not filename:
        return False

    # 检查文件名长度
    if len(filename) > 255:
        return False

    # 检查是否包含路径遍历字符
    if ".." in filename or "/" in filename or "\\" in filename:
        return False

    # 检查文件名格式（只允许字母、数字、下划线、连字符和点）
    pattern = r'^[a-zA-Z0-9_\-\.]+$'
    if not re.match(pattern, filename):
        return False

    return True


@router.post("/simulation/{simulation_id}", response_model=ExportResult)
async def export_simulation(
    simulation_id: str,
    format: ExportFormat = ExportFormat.JSON,
    filters: Optional[ExportFilters] = None
):
    """
    导出仿真数据

    Args:
        simulation_id: 仿真ID
        format: 导出格式
        filters: 过滤器

    Returns:
        ExportResult: 导出结果
    """
    return await _export_service.export_simulation_data(
        simulation_id=simulation_id,
        format=format,
        filters=filters
    )


@router.post("/", response_model=ExportResult)
async def export_data(request: ExportRequest):
    """
    导出数据（通用接口）

    Args:
        request: 导出请求

    Returns:
        ExportResult: 导出结果
    """
    return await _export_service.export_simulation_data(
        simulation_id=request.simulation_id,
        format=request.format,
        filters=request.filters
    )


@router.get("/download/{filename}")
async def download_export(filename: str):
    """
    下载导出的文件

    Args:
        filename: 文件名

    Returns:
        FileResponse: 文件响应
    """
    try:
        # 验证文件名
        if not validate_filename(filename):
            raise HTTPException(status_code=400, detail="Invalid filename")

        export_key = f"_export_{filename}"

        if export_key not in _simulations_data:
            raise HTTPException(status_code=404, detail=f"导出文件 {filename} 不存在")

        export_data = _simulations_data[export_key]
        data = export_data["data"]
        fmt = export_data["format"]

        if fmt == "json":
            media_type = "application/json"
        elif fmt == "csv":
            media_type = "text/csv"
        elif fmt == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif fmt == "pdf":
            media_type = "application/pdf"
        else:
            media_type = "application/octet-stream"

        # 将字符串转换为字节流
        if isinstance(data, str):
            byte_data = data.encode("utf-8")
        else:
            byte_data = data

        return StreamingResponse(
            io.BytesIO(byte_data),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件下载失败: {str(e)}")


@router.get("/templates")
async def get_export_templates():
    """
    获取导出模板

    Returns:
        Dict: 可用的导出模板
    """
    return {
        "templates": [
            {
                "id": "full_report",
                "name": "完整报告",
                "description": "包含所有数据的完整报告",
                "format": "pdf_report",
                "filters": {
                    "include_agents": True,
                    "include_events": True,
                    "include_decisions": True,
                    "include_metrics": True
                }
            },
            {
                "id": "agents_only",
                "name": "仅智能体数据",
                "description": "只包含智能体数据",
                "format": "csv",
                "filters": {
                    "include_agents": True,
                    "include_events": False,
                    "include_decisions": False,
                    "include_metrics": False
                }
            },
            {
                "id": "decisions_summary",
                "name": "决策摘要",
                "description": "智能体决策记录摘要",
                "format": "json",
                "filters": {
                    "include_agents": False,
                    "include_events": False,
                    "include_decisions": True,
                    "include_metrics": True
                }
            }
        ]
    }


@router.get("/formats")
async def get_export_formats():
    """
    获取支持的导出格式

    Returns:
        Dict: 支持的格式列表
    """
    return {
        "formats": [
            {
                "value": "json",
                "name": "JSON",
                "description": "JSON格式，结构化数据"
            },
            {
                "value": "csv",
                "name": "CSV",
                "description": "逗号分隔值格式，适合Excel打开"
            },
            {
                "value": "excel",
                "name": "Excel",
                "description": "Excel文件格式（需要openpyxl）"
            },
            {
                "value": "pdf_report",
                "name": "PDF报告",
                "description": "PDF格式报告（需要reportlab）"
            }
        ]
    }
