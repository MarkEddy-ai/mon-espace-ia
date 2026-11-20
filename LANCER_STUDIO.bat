@echo off
cd /d "%~dp0"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m uvicorn app_studio:app --host 0.0.0.0 --port 8000
pause
