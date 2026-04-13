# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
International Order ABM Simulation System - One-click Startup Script
"""
import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import time
import threading

# Project root directory
PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
API_URL = "http://localhost:8000"
DOCS_URL = f"{API_URL}/docs"


def check_venv():
    """Check if virtual environment exists"""
    if not VENV_PYTHON.exists():
        print("ERROR: Virtual environment does not exist")
        print(f"  Expected path: {VENV_PYTHON}")
        print("  Please run: python -m venv .venv")
        print("  Then run: pip install -r requirements.txt")
        return False
    return True


def check_main_py():
    """Check if main.py exists"""
    main_py = PROJECT_ROOT / "app" / "main.py"
    if not main_py.exists():
        print("ERROR: app/main.py does not exist")
        print(f"  Expected path: {main_py}")
        return False
    return True


def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)  # Wait for server to start
    print()
    print("Server started successfully!")
    print(f"  Opening browser at: {API_URL}")
    print()
    webbrowser.open(API_URL)


def start_server():
    """Start FastAPI server"""
    print("=" * 60)
    print("Starting International Order ABM Simulation System...")
    print("=" * 60)
    print()
    print(f"Project directory: {PROJECT_ROOT}")
    print(f"Python path: {VENV_PYTHON}")
    print(f"API URL: {API_URL}")
    print(f"Docs URL: {DOCS_URL}")
    print()
    print("Starting FastAPI server...")
    print("  Press Ctrl+C to stop the service")
    print("=" * 60)
    print()

    try:
        # Start uvicornicorn server
        cmd = [
            str(VENV_PYTHON),
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
            "--reload"
        ]

        # Open browser in background thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # Run server
        subprocess.run(cmd, cwd=PROJECT_ROOT)

    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("Server stopped")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"Startup failed: {e}")
        print("=" * 60)
        sys.exit(1)


def main():
    """Main function"""
    # Check virtual environment
    if not check_venv():
        sys.exit(1)

    # Check main.py
    if not check_main_py():
        sys.exit(1)

    # Start server
    start_server()


if __name__ == "__main__":
    main()
