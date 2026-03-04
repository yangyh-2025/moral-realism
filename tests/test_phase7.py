"""
Tests for Phase 7: Visualization components.

Tests for:
- ReportGenerator report generation
- Visualization panel rendering functions
- Dashboard initialization
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.visualization.report_generator import ReportGenerator, ReportConfig

# Import streamlit for session state access in tests
import streamlit as st


class TestReportConfig:
    """Tests for ReportConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ReportConfig()

        assert config.title == "道义现实主义ABM仿真报告"
        assert config.author == "Moral Realism ABM System"
        assert config.language == "zh-CN"
        assert config.include_charts is True
        assert config.include_detailed_events is True
        assert config.chart_format == "png"

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ReportConfig(
            title="Custom Report",
            author="Test Author",
            language="en-US",
            include_charts=False,
            chart_format="svg",
        )

        assert config.title == "Custom Report"
        assert config.author == "Test Author"
        assert config.language == "en-US"
        assert config.include_charts is False
        assert config.chart_format == "svg"

    def test_to_dict(self) -> None:
        """Test configuration serialization to dictionary."""
        config = ReportConfig(title="Test Report")
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["title"] == "Test Report"
        assert config_dict["author"] == "Moral Realism ABM System"


class TestReportGenerator:
    """Tests for ReportGenerator class."""

    def test_initialization(self) -> None:
        """Test generator initialization."""
        generator = ReportGenerator()

        assert generator.config.title == "道义现实主义ABM仿真报告"
        assert generator._events == []
        assert generator._charts == []

    def test_initialization_with_config(self) -> None:
        """Test generator initialization with custom config."""
        config = ReportConfig(title="Custom Report")
        generator = ReportGenerator(config)

        assert generator.config.title == "Custom Report"

    def test_add_event(self) -> None:
        """Test adding events to report."""
        generator = ReportGenerator()

        event = {
            "type": "simulation_start",
            "description": "Simulation started",
            "details": {"round": 0},
        }
        generator.add_event(event)

        assert len(generator._events) == 1
        assert generator._events[0]["type"] == "simulation_start"
        assert "timestamp" in generator._events[0]

    def test_add_chart(self) -> None:
        """Test adding charts to report."""
        generator = ReportGenerator()

        chart = {
            "title": "Test Chart",
            "data": {"x": [1, 2, 3], "y": [10, 20, 30]},
            "chart_type": "line",
            "image_data": "fake_base64_data",
        }
        generator.add_chart(chart)

        assert len(generator._charts) == 1
        assert generator._charts[0]["title"] == "Test Chart"

    def test_generate_header(self) -> None:
        """Test HTML header generation."""
        generator = ReportGenerator()
        header = generator._generate_header()

        assert "<!DOCTYPE html>" in header
        assert generator.config.title in header
        assert generator.config.author in header
        assert "<html" in header
        assert "<head>" in header
        assert "<body>" in header

    def test_generate_summary(self) -> None:
        """Test simulation summary section generation."""
        generator = ReportGenerator()

        simulation_data = {
            "config": {
                "max_rounds": 50,
                "agent_count": 3,
                "event_probability": 0.1,
                "checkpoint_interval": 10,
            },
            "state": {
                "status": "running",
                "current_round": 25,
                "total_decisions": 100,
                "total_interactions": 50,
            },
        }

        summary = generator._generate_summary(simulation_data)

        assert "仿真概览" in summary
        assert "50" in summary  # max_rounds
        assert "25" in summary  # current_round
        assert "running" in summary

    def test_generate_initial_states(self) -> None:
        """Test initial states section generation."""
        generator = ReportGenerator()

        simulation_data = {
            "agents": [
                {
                    "agent_id": "agent_1",
                    "name": "大国A",
                    "agent_type": "great_power",
                    "leadership_type": "realist",
                    "capability_index": 85.5,
                    "moral_index": 70.2,
                },
                {
                    "agent_id": "agent_2",
                    "name": "大国B",
                    "agent_type": "great_power",
                    "leadership_type": "liberal",
                    "capability_index": 82.3,
                    "moral_index": 75.8,
                },
            ],
        }

        section = generator._generate_initial_states(simulation_data)

        assert "智能体初始状态" in section
        assert "大国A" in section
        assert "大国B" in section

    def test_generate_metrics_charts(self) -> None:
        """Test metrics charts section generation."""
        generator = ReportGenerator()

        # Add a test chart
        generator.add_chart({
            "title": "Test Chart",
            "image_data": "fake_image_data",
            "chart_type": "line",
        })

        charts_section = generator._generate_metrics_charts()

        assert "指标趋势" in charts_section
        assert "Test Chart" in charts_section

    def test_generate_timeline(self) -> None:
        """Test events timeline section generation."""
        generator = ReportGenerator()

        generator.add_event({
            "type": "event_1",
            "description": "First event",
        })
        generator.add_event({
            "type": "event_2",
            "description": "Second event",
        })

        timeline = generator._generate_timeline()

        assert "关键事件时间线" in timeline
        assert "event_1" in timeline
        assert "event_2" in timeline
        assert "First event" in timeline

    def test_generate_final_state(self) -> None:
        """Test final state section generation."""
        generator = ReportGenerator()

        simulation_data = {
            "final_metrics": {
                "system_metrics": {
                    "order_stability": 75.5,
                    "power_concentration": 0.35,
                    "norm_consensus": 68.2,
                    "public_goods_level": 72.1,
                    "order_type": "realist_hegemony",
                },
            },
        }

        final_state = generator._generate_final_state(simulation_data)

        assert "最终状态分析" in final_state
        assert "75.5" in final_state  # order_stability
        assert "0.35" in final_state  # power_concentration

    def test_generate_complete_report(self) -> None:
        """Test complete HTML report generation."""
        generator = ReportGenerator()

        simulation_data = {
            "config": {"max_rounds": 10},
            "state": {"status": "completed"},
            "agents": [],
            "final_metrics": {},
        }

        # Add events
        generator.add_event({
            "type": "start",
            "description": "Started",
        })

        html = generator.generate(simulation_data)

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert generator.config.title in html
        assert "仿真概览" in html
        assert "关键事件时间线" in html
        assert generator.config.author in html

    def test_clear(self) -> None:
        """Test clearing generator state."""
        generator = ReportGenerator()

        generator.add_event({"type": "test", "description": "Test"})
        generator.add_chart({"title": "Test", "image_data": "data", "chart_type": "line"})

        assert len(generator._events) == 1
        assert len(generator._charts) == 1

        generator.clear()

        assert len(generator._events) == 0
        assert len(generator._charts) == 0

    @patch("builtins.open", create=True)
    def test_save_report(self, mock_open) -> None:
        """Test saving report to file."""
        generator = ReportGenerator()

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        html_content = "<html><body>Test Report</body></html>"
        filepath = generator.save_report(html_content, "/tmp/test_report.html")

        assert filepath == "/tmp/test_report.html"
        mock_file.write.assert_called_once_with(html_content)

    def test_generate_charts_from_metrics(self) -> None:
        """Test chart generation from metrics data."""
        generator = ReportGenerator()

        metrics_data = {
            "system_trends": {
                "power_concentration": [
                    {"round": 0, "value": 0.3},
                    {"round": 1, "value": 0.32},
                    {"round": 2, "value": 0.35},
                ],
                "order_stability": [
                    {"round": 0, "value": 70.0},
                    {"round": 1, "value": 72.0},
                    {"round": 2, "value": 74.0},
                ],
            },
            "agent_trends": {
                "agent_1": {
                    "capability": [
                        {"round": 0, "value": 80.0},
                        {"round": 1, "value": 82.0},
                    ],
                    "moral": [
                        {"round": 0, "value": 70.0},
                        {"round": 1, "value": 72.0},
                    ],
                },
            },
        }

        generator._generate_charts_from_metrics(metrics_data)

        # Should have created charts for system trends and agent trends
        assert len(generator._charts) >= 4  # At least 4 charts created


class TestDashboard:
    """Tests for Dashboard class."""

    def test_initialization(self) -> None:
        """Test dashboard initialization."""
        from src.visualization.dashboard import Dashboard
        with patch("streamlit.set_page_config"):
            dashboard = Dashboard()

            assert dashboard.controller is None
            assert dashboard.data_storage is None
            assert dashboard.metrics_calculator is None
            assert dashboard.report_generator is not None

    def test_initialize_session_state(self) -> None:
        """Test session state initialization."""
        from src.visualization.dashboard import Dashboard
        with patch("streamlit.set_page_config"):
            dashboard = Dashboard()

            dashboard._initialize_session_state()

            # Session state should have required keys
            session_state = st.session_state
            assert "dashboard_initialized" in session_state
            assert "simulation_status" in session_state
            assert "current_round" in session_state

    @staticmethod
    def _get_session_state() -> dict:
        """Helper to get a mock session state."""
        return {
            "dashboard_initialized": True,
            "simulation_status": "ready",
            "current_round": 0,
            "total_rounds": 50,
            "metrics_data": {},
            "system_trends": {},
            "interactions_data": [],
            "agents": {},
            "last_update": 0,
        }


class TestPanelComponents:
    """Tests for visualization panel components."""

    def test_import_panels(self) -> None:
        """Test that all panel functions can be imported."""
        from src.visualization.panels import (
            render_capability_panel,
            render_moral_panel,
            render_interaction_panel,
            render_order_panel,
            render_sidebar_controls,
            render_status_bar,
        )

        assert callable(render_capability_panel)
        assert callable(render_moral_panel)
        assert callable(render_interaction_panel)
        assert callable(render_order_panel)
        assert callable(render_sidebar_controls)
        assert callable(render_status_bar)

    @patch("streamlit.subheader")
    @patch("streamlit.warning")
    def test_capability_panel_with_no_data(self, mock_warning, mock_subheader) -> None:
        """Test capability panel behavior with no data."""
        from src.visualization.panels import render_capability_panel

        render_capability_panel({})

        mock_warning.assert_called_once()

    @patch("streamlit.subheader")
    @patch("streamlit.warning")
    def test_moral_panel_with_no_data(self, mock_warning, mock_subheader) -> None:
        """Test moral panel behavior with no data."""
        from src.visualization.panels import render_moral_panel

        render_moral_panel({})

        mock_warning.assert_called_once()

    @patch("streamlit.subheader")
    @patch("streamlit.warning")
    def test_interaction_panel_with_no_data(self, mock_warning, mock_subheader) -> None:
        """Test interaction panel behavior with no data."""
        from src.visualization.panels import render_interaction_panel

        render_interaction_panel({})

        mock_warning.assert_called_once()

    @patch("streamlit.subheader")
    @patch("streamlit.warning")
    def test_order_panel_with_no_data(self, mock_warning, mock_subheader) -> None:
        """Test order panel behavior with no data."""
        from src.visualization.panels import render_order_panel

        render_order_panel({})

        mock_warning.assert_called_once()

    @patch("streamlit.sidebar.title")
    @patch("streamlit.sidebar.markdown")
    @patch("streamlit.sidebar.number_input")
    @patch("streamlit.sidebar.slider")
    @patch("streamlit.sidebar.button")
    @patch("streamlit.sidebar.checkbox")
    def test_sidebar_controls(self, mock_checkbox, mock_button, mock_slider,
                           mock_number_input, mock_markdown, mock_title) -> None:
        """Test sidebar controls rendering."""
        from src.visualization.panels import render_sidebar_controls

        # Mock return values
        mock_number_input.return_value = 50
        mock_slider.return_value = 0.1
        mock_button.return_value = False
        mock_checkbox.return_value = True

        controls = render_sidebar_controls()

        assert isinstance(controls, dict)
        assert "max_rounds" in controls
        assert "event_probability" in controls
        assert "start" in controls
        assert "pause" in controls
        assert "stop" in controls
        assert "reset" in controls


class TestVisualizationIntegration:
    """Integration tests for visualization components."""

    def test_report_generator_integration(self) -> None:
        """Test ReportGenerator with complete simulation data."""
        generator = ReportGenerator()

        simulation_data = {
            "config": {
                "max_rounds": 100,
                "agent_count": 3,
                "event_probability": 0.15,
                "checkpoint_interval": 20,
            },
            "state": {
                "status": "completed",
                "current_round": 100,
                "total_decisions": 300,
                "total_interactions": 150,
            },
            "agents": [
                {
                    "agent_id": "agent_1",
                    "name": "超级大国",
                    "agent_type": "great_power",
                    "leadership_type": "realist",
                    "capability_index": 90.5,
                    "moral_index": 65.2,
                },
                {
                    "agent_id": "agent_2",
                    "name": "传统大国",
                    "agent_type": "great_power",
                    "leadership_type": "liberal",
                    "capability_index": 82.3,
                    "moral_index": 78.5,
                },
                {
                    "agent_id": "agent_3",
                    "name": "小国",
                    "agent_type": "small_state",
                    "leadership_type": "constructivist",
                    "capability_index": 45.2,
                    "moral_index": 72.8,
                },
            ],
            "final_metrics": {
                "system_metrics": {
                    "pattern_type": "unipolar",
                    "power_concentration": 0.45,
                    "order_stability": 78.5,
                    "norm_consensus": 71.2,
                    "public_goods_level": 74.6,
                    "order_type": "realist_hegemony",
                },
            },
        }

        metrics_data = {
            "system_trends": {
                "power_concentration": [
                    {"round": i, "value": 0.4 + i * 0.001}
                    for i in range(10)
                ],
                "order_stability": [
                    {"round": i, "value": 70.0 + i * 0.5}
                    for i in range(10)
                ],
            },
            "agent_trends": {
                "agent_1": {
                    "capability": [
                        {"round": i, "value": 85.0 + i * 0.5}
                        for i in range(5)
                    ],
                },
            },
        }

        # Add events
        generator.add_event({
            "type": "simulation_start",
            "description": "仿真开始",
            "details": {"timestamp": "2024-01-01T00:00:00"},
        })
        generator.add_event({
            "type": "power_transition",
            "description": "权力结构变化：从两极转向多极",
            "details": {"from": "bipolar", "to": "multipolar", "round": 45},
        })
        generator.add_event({
            "type": "order_evolution",
            "description": "国际秩序演进：规范共识提升",
            "details": {"order_type": "institutional", "round": 78},
        })

        # Generate report
        html = generator.generate(simulation_data, metrics_data)

        # Verify report content
        assert "<!DOCTYPE html>" in html
        assert "仿真概览" in html
        assert "智能体初始状态" in html
        assert "关键事件时间线" in html
        assert "最终状态分析" in html
        assert "超级大国" in html
        assert "传统大国" in html
        assert "小国" in html
        assert "power_transition" in html
        assert "order_evolution" in html
        assert "78.5" in html  # order_stability

    def test_empty_data_handling(self) -> None:
        """Test handling of empty or missing data."""
        generator = ReportGenerator()

        # Generate report with empty data
        html = generator.generate({}, {})

        # Should still produce valid HTML
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html
