"""
Visualization panels for moral realism ABM system.

This module provides rendering functions for the four core visualization panels:
- Capability panel (实力格局)
- Moral panel (道义水平)
- Interaction panel (互动结果)
- Order panel (国际秩序)
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Any, Dict, List, Optional


# Panel state management
if "panel_state" not in st.session_state:
    st.session_state.panel_state = {
        "selected_agent": None,
        "chart_type": "line",
        "show_annotations": True,
    }


def render_capability_panel(
    metrics_data: Dict[str, Any],
    system_trends: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> None:
    """
    Render the capability/power distribution panel.

    Displays:
    - Capability index time series for all agents
    - Radar chart comparing agents across capability dimensions
    - Power distribution pie chart
    - Tier distribution summary

    Args:
        metrics_data: Current metrics data.
        system_trends: Historical trends data from DataStorage.
    """
    st.subheader("实力格局", divider=True)

    if not metrics_data:
        st.warning("暂无数据可显示")
        return

    # Layout: main time series chart on top, comparison charts below
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("##### 实力指数时序图")

        # Extract agent capability data
        agent_metrics = metrics_data.get("agent_metrics", {})
        if agent_metrics:
            names = []
            capability_indices = []
            colors = px.colors.qualitative.Set1[:len(agent_metrics)]

            for agent_id, data in agent_metrics.items():
                name = data.get("name", agent_id)
                names.append(name)
                capability_indices.append(data.get("capability_metrics", {}).get("capability_index", 0))

            # Create bar chart for current values
            fig = px.bar(
                x=names,
                y=capability_indices,
                color=names,
                color_discrete_sequence=colors,
                title="当前实力指数对比",
                labels={"x": "智能体", "y": "实力指数"},
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                yaxis_range=[0, 100],
            )
            st.plotly_chart(fig, use_container_width=True)

        # Show time series if trends data available
        if system_trends and "agent_trends" in system_trends:
            st.markdown("##### 实力指数历史趋势")

            agent_trends = system_trends["agent_trends"]
            if agent_trends:
                fig_trend = go.Figure()

                for agent_id, trend_data in agent_trends.items():
                    if "capability" in trend_data:
                        data_points = trend_data["capability"]
                        rounds = [d.get("round", i) for i, d in enumerate(data_points)]
                        values = [d.get("value", 0) for d in data_points]

                        fig_trend.add_trace(go.Scatter(
                            x=rounds,
                            y=values,
                            mode='lines+markers',
                            name=agent_id,
                            line=dict(width=2),
                        ))

                fig_trend.update_layout(
                    title="实力指数历史变化",
                    xaxis_title="轮数",
                    yaxis_title="实力指数",
                    hovermode='x unified',
                    height=400,
                )
                st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.markdown("##### 实力分布")

        if agent_metrics:
            # Create distribution data
            tiers = {"T0_超级大国": 0, "T1_大国": 0, "T2_地区强国": 0, "T3_中等国家": 0, "T4_小国": 0}

            for data in agent_metrics.values():
                tier = data.get("capability_metrics", {}).get("tier", "unknown")
                if tier in tiers:
                    tiers[tier] += 1

            # Create pie chart
            tiers_df = pd.DataFrame({
                "层级": list(tiers.keys()),
                "数量": list(tiers.values())
            }).query("数量 > 0")

            if not tiers_df.empty:
                fig_pie = px.pie(
                    tiers_df,
                    values="数量",
                    names="层级",
                    title="实力层级分布",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_pie.update_layout(height=300400)
                st.plotly_chart(fig_pie, use_container_width=True)

                # Display tier summary
                with st.expander("层级说明"):
                    st.markdown("""
                    - **T0_超级大国**: 实力指数 > 90
                    - **T1_大国**: 70 < 实力指数 ≤ 90
                    - **T2_地区强国**: 50 < 实力指数 ≤ 70
                    - **T3_中等国家**: 30 < 实力指数 ≤ 50
                    - **T4_小国**: 实力指数 ≤ 30
                    """)

    # Radar chart for capability dimensions
    st.markdown("##### 实力维度雷达图")

    if agent_metrics:
        selected_agent = st.selectbox(
            "选择智能体",
            options=list(agent_metrics.keys()),
            format_func=lambda x: agent_metrics[x].get("name", x),
            key="capability_agent_select",
        )

        if selected_agent in agent_metrics:
            data = agent_metrics[selected_agent]
            cap_metrics = data.get("capability_metrics", {})

            hard_details = cap_metrics.get("hard_power_details", {})
            soft_details = cap_metrics.get("soft_power_details", {})

            # Create radar chart data
            categories = [
                "军事能力", "核能力", "常规力量", "兵力投送",
                "经济总量", "经济增长", "贸易规模", "金融影响力",
                "技术水平", "创新能力", "话语权", "叙事控制",
                "媒体影响", "联盟数量", "网络地位", "外交支持",
                "道义合法性", "文化影响", "联合国影响", "制度领导力"
            ]

            values = [
                hard_details.get("military_capability", 0),
                hard_details.get("nuclear_capability", 0),
                hard_details.get("conventional_forces", 0),
                hard_details.get("force_projection", 0),
                hard_details.get("gdp_share", 0),
                hard_details.get("economic_growth", 0),
                hard_details.get("trade_volume", 0),
                hard_details.get("financial_influence", 0),
                hard_details.get("technology_level", 0),
                hard_details.get("innovation_capacity", 0),
                soft_details.get("discourse_power", 0),
                soft_details.get("narrative_control", 0),
                soft_details.get("media_influence", 0),
                soft_details.get("allies_count", 0) * 10,  # Scale to 0-100
                soft_details.get("network_position", 0),
                soft_details.get("diplomatic_support", 0),
                soft_details.get("moral_legitimacy", 0),
                soft_details.get("cultural_influence", 0),
                soft_details.get("un_influence", 0),
                soft_details.get("institutional_leadership", 0),
            ]

            fig_radar = go.Figure()

            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=data.get("name", selected_agent),
            ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                height=500,
            )

            st.plotly_chart(fig_radar, use_container_width=True)


def render_moral_panel(
    metrics_data: Dict[str, Any],
    system_trends: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> None:
    """
    Render the moral level panel.

    Displays:
    - Moral index time series for all agents
    - Radar chart comparing agents across moral dimensions
    - Dimension scores breakdown
    - Leadership type comparison

    Args:
        metrics_data: Current metrics data.
        system_trends: Historical trends data from DataStorage.
    """
    st.subheader("道义水平", divider=True)

    if not metrics_data:
        st.warning("暂无数据可显示")
        return

    agent_metrics = metrics_data.get("agent_metrics", {})

    if not agent_metrics:
        st.warning("暂无智能体数据")
        return

    # Layout: main chart on left, details on right
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("##### 道义指数对比")

        names = []
        moral_indices = []
        leadership_types = []

        for agent_id, data in agent_metrics.items():
            names.append(data.get("name", agent_id))
            moral_metrics = data.get("moral_metrics", {})
            moral_indices.append(moral_metrics.get("moral_index", 0))
            leadership_types.append(data.get("leadership_type", "unknown"))

        # Create scatter plot colored by leadership type
        fig = px.scatter(
            x=names,
            y=moral_indices,
            color=leadership_types,
            title="道义指数分布（按领导类型）",
            labels={"x": "智能体", "y": "道义指数"},
            color_discrete_map={
                "realist": "red",
                "liberal": "blue",
                "constructivist": "green",
                "moral_realist": "purple",
            },
        )
        fig.update_traces(marker=dict(size=12))
        fig.update_layout(
            yaxis_range=[0, 100],
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Show time series if trends data available
        if system_trends and "agent_trends" in system_trends:
            st.markdown("##### 道义指数历史趋势")

            agent_trends = system_trends["agent_trends"]
            if agent_trends:
                fig_trend = go.Figure()

                for agent_id, trend_data in agent_trends.items():
                    if "moral" in trend_data:
                        data_points = trend_data["moral"]
                        rounds = [d.get("round", i) for i, d in enumerate(data_points)]
                        values = [d.get("value", 0) for d in data_points]

                        fig_trend.add_trace(go.Scatter(
                            x=rounds,
                            y=values,
                            mode='lines+markers',
                            name=agent_id,
                            line=dict(width=2),
                        ))

                fig_trend.update_layout(
                    title="道义指数历史变化",
                    xaxis_title="轮数",
                    yaxis_title="道义指数",
                    hovermode='x unified',
                    height=400,
                )
                st.plotly_chart(fig_trend, use_container_width=True)

    with col2:
        st.markdown("##### 道义维度评分")

        selected_agent = st.selectbox(
            "选择智能体",
            options=list(agent_metrics.keys()),
            format_func=lambda x: agent_metrics[x].get("name", x),
            key="moral_agent_select",
        )

        if selected_agent in agent_metrics:
            data = agent_metrics[selected_agent]
            moral_metrics = data.get("moral_metrics", {})
            dimension_scores = moral_metrics.get("dimension_scores", {})

            if dimension_scores:
                # Create metric cards
                for dimension, score_data in dimension_scores.items():
                    score = score_data.get("score", 0)
                    justification = score_data.get("justification", "")

                    st.metric(
                        label=dimension.replace("_", " ").title(),
                        value=f"{score:.1f}",
                    )

                    if justification and st.session_state.panel_state.get("show_annotations", True):
                        with st.expander("说明"):
                            st.text(justification)


def render_interaction_panel(
    metrics_data: Dict[str, Any],
    interactions_data: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Render the interaction results panel.

    Displays:
    - Interaction heatmap between agents
    - Relationship network graph
    - Action type distribution
    - Success rate summary

    Args:
        metrics_data: Current metrics data.
        interactions_data: List of interaction records.
    """
    st.subheader("互动结果", divider=True)

    if not metrics_data:
        st.warning("暂无数据可显示")
        return

    agent_metrics = metrics_data.get("agent_metrics", {})

    if not agent_metrics:
        st.warning("暂无智能体数据")
        return

    # Layout: heatmap and network side by side
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("##### 互动热度矩阵")

        # Build heatmap data from success metrics
        agent_ids = list(agent_metrics.keys())
        agent_names = [agent_metrics[aid].get("name", aid) for aid in agent_ids]

        # Create heatmap from relationship data
        heatmap_data = []

        for i, agent_id in enumerate(agent_ids):
            success_metrics = agent_metrics[agent_id].get("success_metrics", {})
            avg_rel = success_metrics.get("avg_relationship", 0)
            friendly = success_metrics.get("friendly_relations", 0)
            hostile = success_metrics.get("hostile_relations", 0)
            neutral = success_metrics.get("neutral_relations", 0)

            heatmap_data.append({
                "agent": agent_names[i],
                "友好关系": friendly,
                "敌对关系": hostile,
                "中立关系": neutral,
                "平均关系值": avg_rel,
            })

        if heatmap_data:
            df = pd.DataFrame(heatmap_data)
            st.dataframe(df, use_container_width=True)

            # Show normalized heatmap
            st.markdown("##### 关系热力图")

            fig_heat = px.imshow(
                [[friendly, hostile, neutral] for _, friendly, hostile, neutral in
                 [(d["友好关系"], d["敌对关系"], d["中立关系"]) for d in heatmap_data]],
                x=["友好", "敌对", "中立"],
                y=agent_names,
                color_continuous_scale="RdYlGn",
                title="智能体关系类型分布",
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    with col2:
        st.markdown("##### 互动统计")

        total_friendly = sum(d["友好关系"] for d in heatmap_data)
        total_hostile = sum(d["敌对关系"] for d in heatmap_data)
        total_neutral = sum(d["中立关系"] for d in heatmap_data)

        st.metric("友好互动总数", total_friendly, delta_color="normal")
        st.metric("敌对互动总数", total_hostile, delta_color="inverse")
        st.metric("中立互动总数", total_neutral)

        if interactions_data:
            st.markdown("##### 行动类型分布")

            # Count action types
            action_counts = {}
            for interaction in interactions_data:
                action_type = interaction.get("action_type", "unknown")
                action_counts[action_type] = action_counts.get(action_type, 0) + 1

            if action_counts:
                fig_action = px.pie(
                    values=list(action_counts.values()),
                    names=list(action_counts.keys()),
                    title="行动类型分布",
                )
                st.plotly_chart(fig_action, use_container_width=True)


def render_order_panel(
    metrics_data: Dict[str, Any],
    system_trends: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> None:
    """
    Render the international order panel.

    Displays:
    - System metrics time series (power concentration, stability, etc.)
    - Order type evolution
    - Pattern type indicator
    - Order stability gauge

    Args:
        metrics_data: Current metrics data.
        system_trends: Historical trends data from DataStorage.
    """
    st.subheader("国际秩序", divider=True)

    if not metrics_data:
        st.warning("暂无数据可显示")
        return

    system_metrics = metrics_data.get("system_metrics", {})

    if not system_metrics:
        st.warning("暂无系统指标数据")
        return

    # Current system metrics
    pattern_type = metrics_data.get("pattern_type", "unknown")
    power_concentration = system_metrics.get("power_concentration", 0)
    order_stability = system_metrics.get("order_stability", 0)
    norm_consensus = system_metrics.get("norm_consensus", 0)
    public_goods_level = system_metrics.get("public_goods_level", 0)
    order_type = system_metrics.get("order_type", "unknown")

    # Display current state cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "权力集中度",
            f"{power_concentration:.3f}",
            help="HHI指数，越接近1表示权力越集中"
        )

    with col2:
        stability_delta = None
        if st.session_state.get("prev_order_stability") is not None:
            stability_delta = order_stability - st.session_state.prev_order_stability

        st.metric(
            "秩序稳定性",
            f"{order_stability:.1f}",
            delta=f"{stability_delta:+.1f}" if stability_delta is not None else None,
        )
        st.session_state.prev_order_stability = order_stability

    with col3:
        st.metric(
            "规范共识度",
            f"{norm_consensus:.1f}",
            help="各智能体对国际规范的共识程度"
        )

    with col4:
        st.metric(
            "公共物品水平",
            f"{public_goods_level:.1f}",
            help="国际公共物品的提供水平"
        )

    # Pattern type display
    st.markdown("##### 国际格局类型")

    pattern_colors = {
        "unipolar": "#e74c3c",
        "bipolar": "#f39c12",
        "multipolar": "#27ae60",
        "unknown": "#95a5a6",
    }

    st.markdown(f"""
    <div style="background-color: {pattern_colors.get(pattern_type, '#95a5a6')};
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin: 20px 0;">
        {pattern_type.upper().replace('_', ' ')}
    </div>
    """, unsafe_allow_html=True)

    # Order type evolution
    if system_trends and "order_type" in system_trends:
        st.markdown("##### 秩序类型演变")

        order_type_data = system_trends["order_type"]
        if order_type_data:
            # Count order type occurrences
            from collections import Counter
            order_counts = Counter([d["value"] for d in order_type_data])

            fig_order = px.bar(
                x=list(order_counts.keys()),
                y=list(order_counts.values()),
                title="秩序类型出现频率",
                labels={"x": "秩序类型", "y": "轮数"},
            )
            fig_order.update_layout(height=400)
            st.plotly_chart(fig_order, use_container_width=True)

    # System metrics trends
    if system_trends:
        st.markdown("##### 系统指标历史趋势")

        selected_metric = st.selectbox(
            "选择指标",
            options=["power_concentration", "order_stability", "norm_consensus", "public_goods_level"],
            format_func=lambda x: {
                "power_concentration": "权力集中度",
                "order_stability": "秩序稳定性",
                "norm_consensus": "规范共识度",
                "public_goods_level": "公共物品水平",
            }.get(x, x),
            key="order_metric_select",
        )

        if selected_metric in system_trends:
            data = system_trends[selected_metric]
            if data:
                fig = go.Figure()

                rounds = [d.get("round", i) for i, d in enumerate(data)]
                values = [d.get("value", 0) for d in data]

                fig.add_trace(go.Scatter(
                    x=rounds,
                    y=values,
                    mode='lines+markers',
                    fill='tozeroy',
                    fillcolor='rgba(52, 152, 219, 0.2)',
                    line=dict(color='#3498db', width=2),
                ))

                fig.update_layout(
                    title={
                        "power_concentration": "权力集中度趋势",
                        "order_stability": "秩序稳定性趋势",
                        "norm_consensus": "规范共识度趋势",
                        "public_goods_level": "公共物品水平趋势",
                    }.get(selected_metric, selected_metric),
                    xaxis_title="轮数",
                    yaxis_title="值",
                    height=400,
                )
                st.plotly_chart(fig, use_container_width=True)


def render_sidebar_controls() -> Dict[str, Any]:
    """
    Render sidebar controls for simulation management.

    Returns:
        Dictionary of control states and values.
    """
    st.sidebar.title("仿真控制")

    # Simulation parameters
    st.sidebar.markdown("### 仿真参数")

    max_rounds = st.sidebar.number_input(
        "最大轮数",
        min_value=1,
        max_value=1000,
        value=50,
        step=10,
    )

    event_probability = st.sidebar.slider(
        "事件概率",
        min_value=0.0,
        max=1.0,
        value=0.1,
        step=0.05,
    )

    checkpoint_interval = st.sidebar.number_input(
        "检查点间隔",
        min_value=0,
        max_value=100,
        value=10,
        help="0表示不自动保存检查点",
    )

    # Simulation control buttons
    st.sidebar.markdown("### 仿真控制")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        start_button = st.button("开始", type="primary")
    with col2:
        pause_button = st.button("暂停")

    stop_button = st.sidebar.button("停止", type="secondary")

    reset_button = st.sidebar.button("重置")

    # Checkpoint management
    st.sidebar.markdown("### 检查点管理")

    checkpoint_dir = st.sidebar.text_input(
        "检查点目录",
        value="data/checkpoints",
    )

    load_checkpoint = st.sidebar.selectbox(
        "加载检查点",
        options=["无"],
    )

    # Refresh checkpoints list
    if st.sidebar.button("刷新检查点列表"):
        # This would trigger a checkpoint list refresh
        pass

    # Display options
    st.sidebar.markdown("### 显示选项")

    show_annotations = st.sidebar.checkbox(
        "显示注释",
        value=True,
    )

    auto_refresh = st.sidebar.checkbox(
        "自动刷新",
        value=True,
    )

    refresh_interval = st.sidebar.slider(
        "刷新间隔 (秒)",
        min_value=1,
        max_value=10,
        value=2,
    )

    return {
        "max_rounds": max_rounds,
        "event_probability": event_probability,
        "checkpoint_interval": checkpoint_interval,
        "checkpoint_dir": checkpoint_dir,
        "start": start_button,
        "pause": pause_button,
        "stop": stop_button,
        "reset": reset_button,
        "load_checkpoint": load_checkpoint if load_checkpoint != "无" else None,
        "show_annotations": show_annotations,
        "auto_refresh": auto_refresh,
        "refresh_interval": refresh_interval,
    }


def render_status_bar(
    status: str,
    current_round: int,
    total_rounds: int,
    stats: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Render status bar with simulation status.

    Args:
        status: Current simulation status string.
        current_round: Current round number.
        total_rounds: Total rounds to execute.
        stats: Optional statistics dictionary.
    """
    # Status indicators
    status_colors = {
        "running": "🟢 运行中",
        "paused": "🟡 已暂停",
        "stopped": "🔴 已停止",
        "completed": "✅ 已完成",
        "error": "❌ 错误",
        "ready": "⏳ 就绪",
    }

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.write(status_colors.get(status, f"⚪ {status}"))

    with col2:
        st.write(f"轮数: {current_round}/{total_rounds}")

    with col3:
        progress = current_round / total_rounds if total_rounds > 0 else 0
        st.progress(progress)

    with col4:
        if stats:
            execution_time = stats.get("total_execution_time", 0)
            st.write(f"耗时: {execution_time:.1f}秒")
