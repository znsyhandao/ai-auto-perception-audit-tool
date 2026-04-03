@echo off
echo 启动合规检查服务...
cd /d "%~dp0"
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
pause
