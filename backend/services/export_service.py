"""
数据导出服务 - 处理导出业务逻辑

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException
import io
import json
import csv
import re

from backend.models.export import ExportFormat, ExportFilters, ExportResult


class ExportService:
    """
    数据导出服务

    Git提交用户名: yangyh-2025
    Git提交邮箱: yangyuhang2667@163.com
    """

    def __init__(self):
        # 模拟数据存储（实际应用中从数据库获取）
        self._simulations_data: Dict[str, Dict[str, Any]] = {}

    async def _get_simulation_data(self, simulation_id: str) -> Dict[str, Any]:
        """
        获取仿真数据（模拟）

        Args:
            simulation_id: 仿真ID

        Returns:
            Dict: 仿真数据
        """
        # 在实际实现中，这里会从数据库查询数据
        if simulation_id not in self._simulations_data:
            # 返回示例数据
            self._simulations_data[simulation_id] = {
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

        return self._simulations_data[simulation_id]

    async def _apply_filters(self, data: Dict[str, Any], filters: ExportFilters) -> Dict[str, Any]:
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

            if filters.agent_rounds:
                filtered["agents"] = [
                    a for a in filtered["agents"]
                    if a.get("id") in filters.agent_rounds
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
        self._simulations_data[f"_export_{filename}"] = {"data": json_data, "format": "json"}

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
        self._simulations_data[f"_export_{filename}"] = {"data": csv_data, "format": "csv"}

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
        self._simulations_data[f"_export_{filename}"] = {"data": json_data, "format": "excel"}

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
        self._simulations_data[f"_export_{filename}"] = {"data": json_data, "format": "pdf"}

        return ExportResult(
            success=True,
            message="PDF报告生成成功（需要安装reportlab）",
            filename=filename,
            format=ExportFormat.PDF_REPORT,
            size_bytes=len(json_data.encode("utf-8")),
            record_count=total_records
        )

    def validate_filename(self, filename: str) -> bool:
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

        # 检查文件名格式（只允许字母、数字、、连字符和点）
        pattern = r'^[a-zA-Z0-9_\-\.]+$'
        if not re.match(pattern, filename):
            return False

        return True

    async def export_simulation_data(
        self,
        simulation_id: str,
        format: ExportFormat = ExportFormat.JSON,
        filters: Optional[ExportFilters] = None
    ) -> ExportResult:
        """
        导出仿真数据

        Args:
            simulation_id: 仿真ID
            format: 导出格式
            filters: 导出过滤器

        Returns:
            ExportResult: 导出结果
        """
        if filters is None:
            filters = ExportFilters()

        data = await self._get_simulation_data(simulation_id)
        filtered_data = await self._apply_filters(data, filters)

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
