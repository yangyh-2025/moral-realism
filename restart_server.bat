@echo off
echo Killing Python processes...
taskkill /F /IM python.exe
timeout /t 2 /nobreak

echo Starting server...
cd /d "C:\Users\yangy\myfile\PAPER\moral-ABM\python"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
