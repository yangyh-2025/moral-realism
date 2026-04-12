@echo off
chcp 65001 >nul
echo ============================================================
echo    International Order ABM Simulation System
echo ============================================================
echo.
echo Starting FastAPI server...
echo.
echo Server will be available at:
echo   - API: http://localhost:8000
echo   - Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
