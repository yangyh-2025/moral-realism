"""
Streamlit Dashboard for moral realism ABM system.

This module provides the main Streamlit application for real-time visualization
of the simulation with four core panels and interactive controls.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.visualization.panels import (
    render_capability_panel,
    render_moral_panel,
    render_interaction_panel,
    render_order_panel,
    render_sidebar_controls,
    render_status_bar,
)
from src.visualization.report_generator import ReportGenerator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Dashboard:
    """
    Main Streamlit dashboard application.

    Provides:
    - Real-time simulation visualization
    - Four core panels (capability, moral, interaction, order)
    - Interactive controls (start, pause, stop, load checkpoint)
    - Report generation
    - Auto-refresh mechanism
    """

    def __init__(self) -> None:
        """Initialize dashboard."""
        # Page configuration
        st.set_page_config(
            page_title="道义现实主义ABM仿真系统",
            page_icon="🌍",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        # Custom CSS
        self._apply_custom_styles()

        # Initialize session state
        self._initialize_session_state()

        # Components (will be set when simulation is initialized)
        self.controller = None
        self.data_storage = None
        self.metrics_calculator = None

        # Report generator
        self.report_generator = ReportGenerator()

    def _apply_custom_styles(self) -> None:
        """Apply custom CSS styles to the dashboard."""
        st.markdown("""
        <style>
        .main {
            padding-top: 1rem;
        }
        .stApp {
            background-color: #f0f2f6;
        }
        h1 {
            color: #1e3a5f;
            font-size: 2.5rem;
            font-weight: 700;
        }
        .metric-container {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)

    def _initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        if "dashboard_initialized" not in st.session_state:
            st.session_state.dashboard_initialized = True
            st.session_state.simulation_status = "ready"
            st.session_state.current_round = 0
            st.session_state.total_rounds = 50
            st.session_state.metrics_data = {}
            st.session_state.system_trends = {}
            st.session_state.interactions_data = []
            st.session_state.agents = {}
            st.session_state.last_update = 0

    def run(self) -> None:
        """
        Run the dashboard application.

        This is the main entry point for the Streamlit app.
        """
        try:
            # Render header
            self._render_header()

            # Render sidebar controls
            controls = render_sidebar_controls()

            # Handle control actions
            self._handle_controls(controls)

            # Render status bar
            self._render_status_bar(controls)

            # Render main content tabs
            self._render_main_tabs(controls)

            # Auto-refresh mechanism
            if controls.get("auto_refresh", True) and st.session_state.simulation_status == "running":
                self._auto_refresh(controls)

        except Exception as e:
            logger.error(f"Dashboard error: {e}", exc_info=True)
            st.error(f"仪表板运行错误: {e}")

    def _render_header(self) -> None:
        """Render dashboard header."""
        st.title("🌍 道义现实主义ABM仿真系统")
        st.markdown("""
        <div style="padding: 1rem; background: linear-gradient(90deg, #1e3a5f, #2c5f8c);
                    border-radius: 10px; color: white; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: white;">
                实时可视化仪表板 - Phase 7
            </h3>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.9rem;">
                实力格局 | 道义水平 | 互动结果 | 国际秩序
            </p>
        </div>
        """, unsafe_allow_html=True)

    def _render_status_bar(self, controls: Dict[str, Any]) -> None:
        """Render status bar with simulation information."""
        status = st.session_state.simulation_status
        current_round = st.session_state.current_round
        total_rounds = st.session_state.total_rounds

        render_status_bar(status, current_round, total_rounds)

    def _render_main_tabs(self, controls: Dict[str, Any]) -> None:
        """
        Render main content with tabbed interface.

        Args:
            controls: Current control states.
        """
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 概览",
            "💪 实力格局",
            "⚖️ 道义水平",
            "🤝 互动结果",
            "🏛️ 国际秩序",
        ])

        with tab1:
            self._render_overview_tab(controls)

        with tab2:
            render_capability_panel(
                st.session_state.metrics_data,
                st.session_state.system_trends,
            )

        with tab3:
            render_moral_panel(
                st.session_state.metrics_data,
                st.session_state.system_trends,
            )

        with tab4:
            render_interaction_panel(
                st.session_state.metrics_data,
                st.session_state.interactions_data,
            )

        with tab5:
            render_order_panel(
                st.session_state.metrics_data,
                st.session_state.system_trends,
            )

    def _render_overview_tab(self, controls: Dict[str, Any]) -> None:
        """
        Render overview tab with summary information.

        Args:
            controls: Current control states.
        """
        st.markdown("### 仿真概览")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 系统状态")
            st.markdown(f"""
            - **状态**: {st.session_state.simulation_status}
            - **当前轮数**: {st.session_state.current_round}
            - **总轮数**: {st.session_state.total_rounds}
            - **智能体数量**: {len(st.session_state.agents)}
            """)
            if st.session_state.metrics_data:
                sys_metrics = st.session_state.metrics_data.get("system_metrics", {})
                st.markdown(f"""
                - **格局类型**: {st.session_state.metrics_data.get("pattern_type", "unknown")}
                - **权力集中度**: {sys_metrics.get("power_concentration", 0):.3f}
                - **秩序稳定性**: {sys_metrics.get("order_stability", 0):.1f}
                """)

        with col2:
            st.markdown("#### 报告生成")

            report_format = st.selectbox(
                "报告格式",
                options=["HTML", "JSON"],
                key="report_format_select",
            )

            if st.button("生成报告", key="generate_report_btn"):
                self._generate_report(report_format)

            st.markdown("""
            **功能说明**:

            - 实时监控仿真过程
            - 可视化四大核心指标
            - 支持检查点保存和加载
            - 生成详细仿真报告
            """)

        # Quick metrics display
        if st.session_state.metrics_data:
            st.markdown("#### 快速指标")

            metrics = st.session_state.metrics_data
            sys_metrics = metrics.get("system_metrics", {})

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "权力集中度",
                    f"{sys_metrics.get('power_concentration', 0):.3f}",
                    delta_color="normal"
                )

            with c2:
                st.metric(
                    "秩序稳定性",
                    f"{sys_metrics.get('order_stability', 0):.1f}",
                )

            with c3:
                st.metric(
                    "规范共识度",
                    f"{sys_metrics.get('norm_consensus', 0):.1f}",
                )

            with c4:
                st.metric(
                    "公共物品水平",
                    f"{sys_metrics.get('public_goods_level', 0):.1f}",
                )

    def _handle_controls(self, controls: Dict[str, Any]) -> None:
        """
        Handle user control inputs.

        Args:
            controls: Control states from sidebar.
        """
        # Update total rounds
        if st.session_state.total_rounds != controls["max_rounds"]:
            st.session_state.total_rounds = controls["max_rounds"]

        # Start simulation
        if controls["start"] and st.session_state.simulation_status != "running":
            self._start_simulation(controls)

        # Pause simulation
        if controls["pause"] and st.session_state.simulation_status == "running":
            self._pause_simulation()

        # Stop simulation
        if controls["stop"] and st.session_state.simulation_status in ["running", "paused"]:
            self._stop_simulation()

        # Reset simulation
        if controls["reset"]:
            self._reset_simulation()

        # Load checkpoint
        if controls["load_checkpoint"]:
            self._load_checkpoint(controls["load_checkpoint"])

    def _start_simulation(self, controls: Dict[str, Any]) -> None:
        """
        Start the simulation.

        Args:
            controls: Current control states.
        """
        try:
            if not self._is_simulation_initialized():
                self._initialize_simulation(controls)

            if self.controller:
                success = self.controller.start()
                if success:
                    st.session_state.simulation_status = "running"
                    st.success("仿真已启动")
                else:
                    st.error("仿真启动失败")

        except Exception as e:
            logger.error(f"Error starting simulation: {e}", exc_info=True)
            st.error(f"启动仿真时出错: {e}")

    def _pause_simulation(self) -> None:
        """Pause the simulation."""
        try:
            if self.controller:
                success = self.controller.pause()
                if success:
                    st.session_state.simulation_status = "paused"
                    st.success("仿真已暂停")
                else:
                    st.error("暂停失败")

        except Exception as e:
            logger.error(f"Error pausing simulation: {e}", exc_info=True)
            st.error(f"暂停仿真时出错: {e}")

    def _stop_simulation(self) -> None:
        """Stop the simulation."""
        try:
            if self.controller:
                success = self.controller.stop()
                if success:
                    st.session_state.simulation_status = "stopped"
                    st.success("仿真已停止")
                else:
                    st.error("停止失败")

        except Exception as e:
            logger.error(f"Error stopping simulation: {e}", exc_info=True)
            st.error(f"停止仿真时出错: {e}")

    def _reset_simulation(self) -> None:
        """Reset the simulation to initial state."""
        try:
            st.session_state.simulation_status = "ready"
            st.session_state.current_round = 0
            st.session_state.metrics_data = {}
            st.session_state.system_trends = {}
            st.session_state.interactions_data = []
            st.session_state.agents = {}

            if self.controller:
                self.controller.reset()

            st.success("仿真已重置")
            st.rerun()

        except Exception as e:
            logger.error(f"Error resetting simulation: {e}", exc_info=True)
            st.error(f"重置仿真时出错: {e}")

    def _load_checkpoint(self, checkpoint_id: str) -> None:
        """
        Load a simulation checkpoint.

        Args:
            checkpoint_id: Checkpoint ID to load.
        """
        try:
            if self.controller and self.data_storage:
                success = self.controller.load_checkpoint(checkpoint_id)
                if success:
                    st.session_state.simulation_status = "ready"
                    st.success(f"检查点 {checkpoint_id} 加载成功")
                    self._update_dashboard_data()
                    st.rerun()
                else:
                    st.error(f"加载检查点失败: {checkpoint_id}")

        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}", exc_info=True)
            st.error(f"加载检查点时出错: {e}")

    def _initialize_simulation(self, controls: Dict[str, Any]) -> None:
        """
        Initialize simulation components.

        Args:
            controls: Control states from sidebar.
        """
        try:
            # Import simulation components
            from src.workflow.simulation_controller import SimulationController
            from src.agents.controller_agent import SimulationConfig
            from src.metrics.calculator import MetricsCalculator
            from src.metrics.storage import DataStorage
            from src.environment.rule_environment import RuleEnvironment

            # Create configuration
            config = SimulationConfig(
                max_rounds=controls["max_rounds"],
                event_probability=controls["event_probability"],
                checkpoint_interval=controls["checkpoint_interval"],
                checkpoint_dir=controls["checkpoint_dir"],
            )

            # Initialize components
            self.controller = SimulationController(config)
            self.metrics_calculator = MetricsCalculator(RuleEnvironment())
            self.data_storage = DataStorage(controls["checkpoint_dir"])

            # Set up controller components
            self.controller.set_data_storage(self.data_storage)

            # Initialize default agents for demo
            self._create_demo_agents()

            self.controller.initialize()
            self._update_dashboard_data()

            logger.info("Simulation initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing simulation: {e}", exc_info=True)
            st.error(f"初始化仿真时出错: {e}")

    def _create_demo_agents(self) -> None:
        """Create demo agents for the simulation."""
        try:
            from src.agents import GreatPowerAgent, SmallStateAgent
            from src.models.agent import LeadershipType
            from src.models.capability import Capability, HardPower, SoftPower

            # Create great power agents
            agents = {}

            # Agent 1: Great power with realist leadership
            hard_power1 = HardPower(
                military_capability=90.0,
                nuclear_capability=85.0,
                conventional_forces=88.0,
                force_projection=85.0,
                gdp_share=80.0,
                economic_growth=75.0,
                trade_volume=78.0,
                financial_influence=82.0,
                technology_level=85.0,
                military_technology=88.0,
                innovation_capacity=80.0,
            )
            soft_power1 = SoftPower(
                discourse_power=70.0,
                narrative_control=65.0,
                media_influence=68.0,
                allies_count=5.0,
                ally_strength=70.0,
                network_position=72.0,
                diplomatic_support=75.0,
                moral_legitimacy=60.0,
                cultural_influence=75.0,
                un_influence=80.0,
                institutional_leadership=78.0,
            )
            capability1 = Capability(hard_power=hard_power1, soft_power=soft_power1)

            agent1 = GreatPowerAgent(
                agent_id="agent_1",
                name="大国A",
                leadership_type=LeadershipType.REALIST,
                capability=capability1,
            )
            agents["agent_1"] = agent1

            # Agent 2: Great power with liberal leadership
            hard_power2 = HardPower(
                military_capability=82.0,
                nuclear_capability=78.0,
                conventional_forces=80.0,
                force_projection=78.0,
                gdp_share=75.0,
                economic_growth=70.0,
                trade_volume=72.0,
                financial_influence=75.0,
                technology=80.0,
                military_technology=82.0,
                innovation_capacity=75.0,
            )
            soft_power2 = SoftPower(
                discourse_power=80.0,
                narrative_control=78.0,
                media_influence=82.0,
                allies_count=7.0,
                ally_strength=78.0,
                network_position=80.0,
                diplomatic_support=82.0,
                moral_legitimacy=85.0,
                cultural_influence=85.0,
                un_influence=88.0,
                institutional_leadership=85.0,
            )
            capability2 = Capability(hard_power=hard_power2, soft_power=soft_power2)

            agent2 = GreatPowerAgent(
                agent_id="agent_2",
                name="大国B",
                leadership_type=LeadershipType.LIBERAL,
                capability=capability2,
            )
            agents["agent_2"] = agent2

            # Agent 3: Small state with constructivist leadership
            hard_power3 = HardPower(
                military_capability=40.0,
                nuclear_capability=20.0,
                conventional_forces=35.0,
                force_projection=25.0,
                gdp_share=30.0,
                economic_growth=40.0,
                trade_volume=35.0,
                financial_influence=30.0,
                technology_level=45.0,
                military_technology=40.0,
                innovation_capacity=50.0,
            )
            soft_power3 = SoftPower(
                discourse_power=60.0,
                narrative_control=55.0,
                media_influence=58.0,
                allies_count=3.0,
                ally_strength=50.0,
                network_position=55.0,
                diplomatic_support=60.0,
                moral_legitimacy=70.0,
                cultural_influence=65.0,
                un_influence=65.0,
                institutional_leadership=55.0,
            )
            capability3 = Capability(hard_power=hard_power3, soft_power=soft_power3)

            agent3 = SmallStateAgent(
                agent_id="agent_3",
                name="小国C",
                leadership_type=LeadershipType.CONSTRUCTIVIST,
                capability=capability3,
            )
            agents["agent_3"] = agent3

            # Register agents
            st.session_state.agents = agents
            self.controller.set_agents(agents)

            logger.info(f"Created {len(agents)} demo agents")

        except Exception as e:
            logger.error(f"Error creating demo agents: {e}", exc_info=True)

    def _is_simulation_initialized(self) -> bool:
        """Check if simulation components are initialized."""
        return self.controller is not None and self.metrics_calculator is not None

    def _update_dashboard_data(self) -> None:
        """Update dashboard data from simulation state."""
        try:
            if not self._is_simulation_initialized():
                return

            agents = st.session_state.agents or self.controller._agents
            if not agents:
                return

            # Calculate metrics
            metrics = self.metrics_calculator.calculate_all_metrics(
                agents=agents,
                round_result={"round": st.session_state.current_round}
            )

            st.session_state.metrics_data = metrics
            st.session_state.current_round = metrics.get("round", st.session_state.current_round)

            # Load system trends if data storage available
            if self.data_storage:
                st.session_state.system_trends = self.data_storage.get_system_trends(
                    start_round=0,
                )

        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}", exc_info=True)

    def _auto_refresh(self, controls: Dict[str, Any]) -> None:
        """
        Handle auto-refresh of dashboard data.

        Args:
            controls: Control states from sidebar.
        """
        try:
            # Execute simulation step if running
            if st.session_state.simulation_status == "running" and self.controller:
                result = self.controller.execute_single_round()

                if result:
                    st.session_state.current_round = self.controller.state.current_round

                    # Update metrics
                    self._update_dashboard_data()

                    # Check if simulation completed
                    if st.session_state.current_round >= st.session_state.total_rounds:
                        st.session_state.simulation_status = "completed"
                        self.controller.stop()
                        st.success("仿真已完成！")

                else:
                    st.session_state.simulation_status = "completed"
                    self.controller.stop()
                    st.info("仿真结束")

        except Exception as e:
            logger.error(f"Error in auto-refresh: {e}", exc_info=True)

    def _generate_report(self, format_type: str) -> None:
        """
        Generate and display a simulation report.

        Args:
            format_type: Report format ("HTML" or "JSON").
        """
        try:
            # Prepare simulation data for report
            simulation_data = {
                "config": {
                    "max_rounds": st.session_state.total_rounds,
                    "agent_count": len(st.session_state.agents),
                },
                "state": {
                    "status": st.session_state.simulation_status,
                    "current_round": st.session_state.current_round,
                },
                "agents": [
                    {
                        "agent_id": agent_id,
                        "name": agent.name,
                        "agent_type": agent.agent_type.value,
                        "leadership_type": agent.leadership_type.value,
                        "capability_index": agent.capability.get_capability_index() if agent.capability else 0,
                        "moral_index": 70.0,  # Placeholder
                    }
                    for agent_id, agent in st.session_state.agents.items()
                ],
                "final_metrics": st.session_state.metrics_data,
            }

            if format_type == "HTML":
                html = self.report_generator.generate(
                    simulation_data=simulation_data,
                    metrics_data={"system_trends": st.session_state.system_trends},
                )

                st.markdown("### 生成的报告")
                st.components.v1.html(html, height=800, scrolling=True)

                # Download button
                st.download_button(
                    label="下载HTML报告",
                    data=html,
                    file_name=f"simulation_report_{st.session_state.current_round}.html",
                    mime="text/html",
                )

            elif format_type == "JSON":
                import json
                json_data = json.dumps(simulation_data, indent=2, ensure_ascii=False)

                st.download_button(
                    label="下载JSON报告",
                    data=json_data,
                    file_name=f"simulation_report_{st.session_state.current_round}.json",
                    mime="application/json",
                )

        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            st.error(f"生成报告时出错: {e}")


def main() -> None:
    """Main entry point for the Streamlit application."""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
