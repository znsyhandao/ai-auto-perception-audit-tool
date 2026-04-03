@echo off
echo 启动性能分析服务...
cd /d "%~dp0"
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
pause
