"""
Visualization components for the moral realism ABM system.

This module provides visualization and reporting capabilities including:
- Dashboard: Real-time Streamlit visualization interface
- ReportGenerator: HTML/PDF report generation
- Panels: Core visualization panel components
"""

from src.visualization.dashboard import Dashboard
from src.visualization.report_generator import ReportGenerator, ReportConfig
from src.visualization.panels import (
    render_capability_panel,
    render_moral_panel,
    render_interaction_panel,
    render_order_panel,
    render_sidebar_controls,
    render_status_bar,
)

__all__ = [
    # Main dashboard
    "Dashboard",
    # Report generation
    "ReportGenerator",
    "ReportConfig",
    # Panel components
    "render_capability_panel",
    "render_moral_panel",
    "render_interaction_panel",
    "render_order_panel",
    "render_sidebar_controls",
    "render_status_bar",
]

