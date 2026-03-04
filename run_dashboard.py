"""
Run script for the Streamlit dashboard.

This script provides a convenient entry point for launching the
moral realism ABM simulation dashboard.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main() -> None:
    """Main entry point for dashboard."""
    import streamlit as st
    from src.visualization.dashboard import Dashboard

    # Run dashboard
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    # Import and run the dashboard module directly
    import streamlit.cli as cli
    import os

    # Set streamlit run command
    sys.argv = ["streamlit", "run", "src/visualization/dashboard.py",
                "--server.port", "8501",
                "--server.address", "localhost"]

    cli.main()
