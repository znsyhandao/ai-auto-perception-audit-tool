@echo off
echo 启动报告生成服务...
cd /d "%~dp0"
uvicorn main:app --host 0.0.0.0 --port 8005 --reload
pause
