@echo off
echo 启动增强版API网关...
cd /d "%~dp0"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
