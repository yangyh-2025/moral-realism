"""
数据导出API路由 - 支持多种格式的数据导出

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from backend.models.export import ExportFormat, ExportFilters, ExportRequest, ExportResult
from backend.services.export_service import ExportService

router = APIRouter()

# 初始化导出服务
_export_service = ExportService()


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
        if not _export_service.validate_filename(filename):
            raise HTTPException(status_code=400, detail="Invalid filename")

        export_key = f"_export_{filename}"

        if export_key not in _export_service._simulations_data:
            raise HTTPException(status_code=404, detail=f"导出文件 {filename} 不存在")

        export_data = _export_service._simulations_data[export_key]
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
