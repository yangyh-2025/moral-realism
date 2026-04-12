import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

print("Starting International Order ABM Simulation System...")
print(f"Python: {VENV_PYTHON}")

cmd = [
    str(VENV_PYTHON),
    "-m",
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]

print("Starting FastAPI server at http://localhost:8000")
print("Press Ctrl+C to stop")
print("-" * 50)

try:
    subprocess.run(cmd, cwd=PROJECT_ROOT)
except KeyboardInterrupt:
    print("\nServer stopped.")
