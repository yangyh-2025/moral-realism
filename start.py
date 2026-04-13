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
VENV_PYTHON = PROJECT_ROOT / '.venv' / 'Scripts' / 'python.exe'
FRONTEND_DIR = PROJECT_ROOT / 'frontend'
BACKEND_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:3000'
DOCS_URL = f'{BACKEND_URL}/docs'
NPM_CMD = r'C:\Program Files\nodejs\npm.cmd'


def check_venv():
    """Check if virtual environment exists"""
    if not VENV_PYTHON.exists():
        print('ERROR: Virtual environment does not exist')
        print(f'  Expected path: {VENV_PYTHON}')
        print('  Please run: python -m venv .venv')
        print('  Then run: pip install -r requirements.txt')
        return False
    return True


def check_main_py():
    """Check if main.py exists"""
    main_py = PROJECT_ROOT / 'app' / 'main.py'
    if not main_py.exists():
        print('ERROR: app/main.py does not exist')
        print(f'  Expected path: {main_py}')
        return False
    return True


def check_frontend():
    """Check if frontend exists"""
    if not FRONTEND_DIR.exists():
        print('ERROR: frontend directory does not exist')
        print(f'  Expected path: {FRONTEND_DIR}')
        return False
    return True


def check_npm():
    """Check if npm exists"""
    if not os.path.exists(NPM_CMD):
        print('WARNING: npm not found at default path')
        print('  You may need to install Node.js or update NPM_CMD path')
        return False
    return True


def open_browser():
    """Open browser after a short delay"""
    time.sleep(5)  # Wait for both servers to start
    print()
    print('Servers started successfully!')
    print(f'  Backend URL: {BACKEND_URL}')
    print(f'  Frontend URL: {FRONTEND_URL}')
    print(f'  Docs URL: {DOCS_URL}')
    print()
    print(f'Opening browser at: {FRONTEND_URL}')
    print()
    webbrowser.open(FRONTEND_URL)


def start_servers():
    """Start both frontend and backend servers"""
    print('=' * 60)
    print('Starting International Order ABM Simulation System...')
    print('=' * 60)
    print()
    print(f'Project directory: {PROJECT_ROOT}')
    print(f'Python path: {VENV_PYTHON}')
    print(f'Backend URL: {BACKEND_URL}')
    print(f'Frontend URL: {FRONTEND_URL}')
    print(f'Docs URL: {DOCS_URL}')
    print()
    print('Starting backend FastAPI server and frontend Vite server...')
    print('  Press Ctrl+C to stop all services')
    print('=' * 60)
    print()

    try:
        # Start backend server command
        backend_cmd = [
            str(VENV_PYTHON),
            '-m',
            'uvicorn',
            'app.main:app',
            '--host',
            '0.0.0.0',
            '--port',
            '8000',
            '--reload'
        ]

        # Start frontend server command
        frontend_cmd = [
            NPM_CMD,
            'run',
            'dev'
        ]

        # Open browser in background thread
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        print('Starting backend server...')
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        print('Starting frontend server...')
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=FRONTEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        print()
        print('Backend server running on http://localhost:8000')
        print('Frontend server running on http://localhost:3000')
        print()

        # Wait for either process to finish
        processes = [
            ('Backend', backend_process),
            ('Frontend', frontend_process)
        ]

        while True:
            # Check if any process has exited
            for name, process in processes:
                if process.poll() is not None:
                    print()
                    print('=' * 60)
                    print(f'{name} server stopped unexpectedly')
                    print('=' * 60)
                    # Terminate other process
                    for other_name, other_process in processes:
                        if other_process != process and other_process.poll() is None:
                            print(f'Stopping {other_name} server...')
                            other_process.terminate()
                    return

            time.sleep(0.1)

    except KeyboardInterrupt:
        print()
        print('=' * 60)
        print('Stopping all servers...')
        print('=' * 60)

        # Terminate both processes
        try:
            if 'backend_process' in locals():
                backend_process.terminate()
                backend_process.wait(timeout=5)
        except:
            pass

        try:
            if 'frontend_process' in locals():
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
        except:
            pass

        print('All servers stopped')
        print('=' * 60)
    except Exception as e:
        print()
        print('=' * 60)
        print(f'Startup failed: {e}')
        print('=' * 60)
        sys.exit(1)


def main():
    """Main function"""
    # Check virtual environment
    if not check_venv():
        sys.exit(1)

    # Check main.py
    if not check_main_py():
        sys.exit(1)

    # Check frontend
    if not check_frontend():
        sys.exit(1)

    # Check npm (optional, just warning)
    check_npm()

    # Start servers
    start_servers()


if __name__ == '__main__':
    main()
