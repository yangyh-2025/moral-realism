# -*- coding: utf-8 -*-
"""
仪表板启动脚本

本脚本用于启动道义现实主义ABM系统的Streamlit可视化仪表板。

主要功能：
- 提供便捷的仪表板启动入口点
- 配置Streamlit服务器参数（端口、地址）
- 集成可视化模块功能

访问地址：
- http://localhost:8501 - 仪表板主界面

使用方法：
1. 直接运行: python run_dashboard.py
2. Streamlit CLI: streamlit run src src/visualization/dashboard.py --server.port 8501
"""
import sys
from pathlib import Path


# 将项目根目录添加到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main() -> None:
    """仪表板主入口函数"""
    import streamlit as st
    from src.visualization.dashboard import Dashboard

    # 运行仪表板
    dashboard = Dashboard()
    dashboard.run()


if __name__ == '__main__':
    # 直接导入并运行仪表板模块
    import streamlit.cli as cli
    import os

    # 设置Streamlit运行命令
    sys.argv = [
        "streamlit",
        "run",
        "src/visualization/dashboard.py",
        "--server.port",
        "8501",
        "--server.address",
        "localhost"
    ]

    cli.main()
