"""
Report generator for moral realism ABM system.

This module provides ReportGenerator class for generating HTML simulation reports
with embedded charts, summaries, and key events.
"""

import base64
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


# Use non-interactive backend for matplotlib
matplotlib.use('Agg')


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    title: str = "道义现实主义ABM仿真报告"
    author: str = "Moral Realism ABM System"
    language: str = "zh-CN"
    include_charts: bool = True
    include_detailed_events: bool = True
    chart_format: str = "png"  # png, svg

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "include_charts": self.include_charts,
            "include_detailed_events": self.include_detailed_events,
            "chart_format": self.chart_format,
        }


class ReportGenerator:
    """
    Generate simulation reports in HTML format.

    Creates comprehensive reports including:
    - Simulation configuration summary
    - Agent initial states
    - Key events timeline
    - Metric trend charts (embedded as base64)
    - Final state analysis
    """

    def __init__(self, config: Optional[ReportConfig] = None) -> None:
        """
        Initialize report generator.

        Args:
            config: Report configuration options.
        """
        self.config = config or ReportConfig()
        self._events: List[Dict[str, Any]] = []
        self._charts: List[Dict[str, Any]] = []

    def add_event(self, event: Dict[str, Any]) -> None:
        """
        Add an event to the report.

        Args:
            event: Event dictionary with at least 'timestamp', 'type', and 'description'.
        """
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        self._events.append(event)

    def add_chart(self, chart_data: Dict[str, Any]) -> None:
        """
        Add a chart to the report.

        Args:
            chart_data: Chart data dictionary including 'title', 'data', and 'chart_type'.
        """
        if self.config.include_charts:
            self._charts.append(chart_data)

    def generate(
        self,
        simulation_data: Dict[str, Any],
        metrics_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate complete HTML report.

        Args:
            simulation_data: Simulation configuration and state data.
            metrics_data: Optional metrics history data for charts.

        Returns:
            Complete HTML report string.
        """
        # Generate charts if metrics data provided
        if metrics_data and self.config.include_charts:
            self._generate_charts_from_metrics(metrics_data)

        # Build HTML components
        html_parts = [
            self._generate_header(),
            self._generate_summary(simulation_data),
            self._generate_initial_states(simulation_data),
            self._generate_metrics_charts(),
            self._generate_timeline(),
            self._generate_final_state(simulation_data),
            self._generate_footer(),
        ]

        return "\n".join(html_parts)

    def _generate_header(self) -> str:
        """Generate HTML header section."""
        return f"""<!DOCTYPE html>
<html lang="{self.config.language}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #555;
            margin-top: 25px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .header p {{
            color: #666;
            font-size: 14px;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
        }}
        .timeline {{
            position: relative;
            padding-left: 30px;
        }}
        .timeline-item {{
            position: relative;
            margin-bottom: 30px;
            padding-left: 20px;
        }}
        .timeline-item::before {{
            content: '';
            position: absolute;
            left: -9px;
            top: 5px;
            width: 16px;
            height: 16px;
            background-color: #3498db;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 5px rgba(0,0,0,0.2);
        }}
        .timeline-item::after {{
            content: '';
            position: absolute;
            left: -1px;
            top: 21px;
            width: 2px;
            height: calc(100% - 21px);
            background-color: #ddd;
        }}
        .timeline-item:last-child::after {{
            display: none;
        }}
        .timeline-time {{
            color: #999;
            font-size: 12px;
            margin-bottom: 5px;
        }}
        .event-type {{
            display: inline-block;
            padding: 3px 10px;
            background-color: #e9f4ff;
            color: #3498db;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 14px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        .status-completed {{ background-color: #d4edda; color: #155724; }}
        .status-running {{ background-color: #cce5ff; color: #004085; }}
        .status-error {{ background-color: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.config.title}</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>作者: {self.config.author}</p>
        </div>
"""

    def _generate_summary(self, simulation_data: Dict[str, Any]) -> str:
        """Generate simulation summary section."""
        config = simulation_data.get("config", {})
        state = simulation_data.get("state", {})

        status = state.get("status", "unknown")
        status_class = f"status-{status}" if status in ["completed", "running", "error"] else "status-running"

        return f"""
        <div class="section">
            <h2>仿真概览</h2>
            <table>
                <tr>
                    <th>配置项</th>
                    <th>值</th>
                </tr>
                <tr>
                    <td>最大轮数</td>
                    <td>{config.get("max_rounds", "N/A")}</td>
                </tr>
                <tr>
                    <td>智能体数量</td>
                    <td>{config.get("agent_count", "N/A")}</td>
                </tr>
                <tr>
                    <td>事件概率</td>
                    <td>{config.get("event_probability", "N/A")}</td>
                </tr>
                <tr>
                    <td>检查点间隔</td>
                    <td>{config.get("checkpoint_interval", "N/A")}</td>
                </tr>
                <tr>
                    <td>当前轮数</td>
                    <td>{state.get("current_round", "N/A")}</td>
                </tr>
                <tr>
                    <td>状态</td>
                    <td><span class="status-badge {status_class}">{status}</span></td>
                </tr>
                <tr>
                    <td>总决策数</td>
                    <td>{state.get("total_decisions", "N/A")}</td>
                </tr>
                <tr>
                    <td>总互动数</td>
                    <td>{state.get("total_interactions", "N/A")}</td>
                </tr>
            </table>
        </div>
"""

    def _generate_initial_states(self, simulation_data: Dict[str, Any]) -> str:
        """Generate initial agent states section."""
        agents = simulation_data.get("agents", [])

        if not agents:
            return ""

        agent_rows = ""
        for agent in agents:
            agent_rows += f"""
                <tr>
                    <td>{agent.get("name", agent.get("agent_id", "Unknown"))}</td>
                    <td>{agent.get("agent_type", "N/A")}</td>
                    <td>{agent.get("leadership_type", "N/A")}</td>
                    <td>{agent.get("capability_index", 0):.2f}</td>
                    <td>{agent.get("moral_index", 0):.2f}</td>
                </tr>
            """

        return f"""
        <div class="section">
            <h2>智能体初始状态</h2>
            <table>
                <tr>
                    <th>名称</th>
                    <th>类型</th>
                    <th>领导类型</th>
                    <th>实力指数</th>
                    <th>道义指数</th>
                </tr>
                {agent_rows}
            </table>
        </div>
"""

    def _generate_metrics_charts(self) -> str:
        """Generate metrics charts section."""
        if not self._charts:
            return ""

        charts_html = ""
        for chart in self._charts:
            title = chart.get("title", "Chart")
            image_data = chart.get("image_data", "")
            chart_type = chart.get("chart_type", "line")

            if image_data:
                charts_html += f"""
                <div class="chart-container">
                    <h3>{title}</h3>
                    <img src="data:image/png;base64,{image_data}" alt="{title}">
                </div>
                """

        return f"""
        <div class="section">
            <h2>指标趋势</h2>
            {charts_html}
        </div>
"""

    def _generate_timeline(self) -> str:
        """Generate events timeline section."""
        if not self._events:
            return ""

        timeline_html = ""
        for event in self._events:
            timestamp = event.get("timestamp", "")
            event_type = event.get("type", "Unknown")
            description = event.get("description", "")
            details = event.get("details", {})

            details_html = ""
            if details:
                for key, value in details.items():
                    details_html += f"<li><strong>{key}:</strong> {value}</li>"

            timeline_html += f"""
                <div class="timeline-item">
                    <div class="timeline-time">{timestamp}</div>
                    <span class="event-type">{event_type}</span>
                    <p>{description}</p>
                    {f'<ul>{details_html}</ul>' if details_html else ''}
                </div>
            """

        return f"""
        <div class="section">
            <h2>关键事件时间线</h2>
            <div class="timeline">
                {timeline_html}
            </div>
        </div>
"""

    def _generate_final_state(self, simulation_data: Dict[str, Any]) -> str:
        """Generate final state analysis section."""
        final_metrics = simulation_data.get("final_metrics", {})
        system_metrics = final_metrics.get("system_metrics", {})

        if not system_metrics:
            return ""

        return f"""
        <div class="section">
            <h2>最终状态分析</h2>
            <div class="metric-card">
                <div class="metric-value">{system_metrics.get("order_stability", 0):.1f}</div>
                <div class="metric-label">秩序稳定性指数 (0-100)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{system_metrics.get("power_concentration", 0):.3f}</div>
                <div class="metric-label">权力集中度 (HHI指数)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{system_metrics.get("norm_consensus", 0):.1f}</div>
                <div class="metric-label">规范共识度 (0-100)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{system_metrics.get("public_goods_level", 0):.1f}</div>
                <div class="metric-label">公共物品水平 (0-100)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{system_metrics.get("order_type", "unknown")}</div>
                <div class="metric-label">国际秩序体系类型</div>
            </div>
        </div>
"""

    def _generate_footer(self) -> str:
        """Generate HTML footer section."""
        return f"""
        <div class="footer">
            <p>此报告由 {self.config.author} 自动生成</p>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

    def _generate_charts_from_metrics(self, metrics_data: Dict[str, Any]) -> None:
        """
        Generate charts from metrics history data.

        Args:
            metrics_data: Metrics history data from DataStorage.
        """
        # Generate system metrics charts
        system_trends = metrics_data.get("system_trends", {})

        # Power concentration trend
        if "power_concentration" in system_trends:
            self._create_trend_chart(
                title="权力集中度趋势",
                data=system_trends["power_concentration"],
                ylabel="权力集中度 (HHI)",
                color="#3498db"
            )

        # Order stability trend
        if "order_stability" in system_trends:
            self._create_trend_chart(
                title="秩序稳定性趋势",
                data=system_trends["order_stability"],
                ylabel="稳定性指数",
                color="#2ecc71"
            )

        # Norm consensus trend
        if "norm_consensus" in system_trends:
            self._create_trend_chart(
                title="规范共识度趋势",
                data=system_trends["norm_consensus"],
                ylabel="共识度",
                color="#f39c12"
            )

        # Generate agent capability trends
        agent_trends = metrics_data.get("agent_trends", {})
        for agent_id, trend_data in agent_trends.items():
            if "capability" in trend_data:
                self._create_trend_chart(
                    title=f"{agent_id} 实力指数趋势",
                    data=trend_data["capability"],
                    ylabel="实力指数",
                    color="#9b59b6"
                )

            if "moral" in trend_data:
                self._create_trend_chart(
                    title=f"{agent_id} 道义指数趋势",
                    data=trend_data["moral"],
                    ylabel="道义指数",
                    color="#e74c3c"
                )

    def _create_trend_chart(
        self,
        title: str,
        data: List[Dict[str, Any]],
        xlabel: str = "轮数",
        ylabel: str = "值",
        color: str = "#3498db",
    ) -> None:
        """
        Create a trend line chart and add to report.

        Args:
            title: Chart title.
            data: List of dictionaries with 'round' and 'value' keys.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            color: Line color.
        """
        if not data:
            return

        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            rounds = [d.get("round", i) for i, d in enumerate(data)]
            values = [d.get("value", 0) for d in data]

            ax.plot(rounds, values, color=color, linewidth=2, marker='o', markersize=4)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Convert to base64
            buffer = BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close(fig)

            self.add_chart({
                "title": title,
                "image_data": image_data,
                "chart_type": "line",
            })

        except Exception as e:
            print(f"Error creating chart {title}: {e}")

    def save_report(self, html: str, filepath: str) -> Optional[str]:
        """
        Save HTML report to file.

        Args:
            html: HTML content to save.
            filepath: Destination file path.

        Returns:
            Path to saved file, or None if save failed.
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            return filepath
        except Exception as e:
            print(f"Error saving report: {e}")
            return None

    def clear(self) -> None:
        """Clear all events and charts for a new report."""
        self._events.clear()
        self._charts.clear()
