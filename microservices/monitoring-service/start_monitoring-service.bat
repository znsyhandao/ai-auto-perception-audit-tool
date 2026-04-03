@echo off
echo 启动监控服务...
cd /d "%~dp0"
uvicorn main:app --host 0.0.0.0 --port 8006 --reload
pause
