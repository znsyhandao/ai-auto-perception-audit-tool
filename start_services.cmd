@echo off
echo Starting Enterprise Audit Framework Services...
echo.

echo [1] Starting Validator Service (port 8001)...
start "Validator Service" powershell -NoExit -Command "cd '%~dp0microservices\validator-service'; uvicorn main_fixed:app --host 0.0.0.0 --port 8001 --reload"

echo [2] Starting Security Service (port 8002)...
start "Security Service" powershell -NoExit -Command "cd '%~dp0microservices\security-service'; uvicorn main_fixed:app --host 0.0.0.0 --port 8002 --reload"

echo.
echo Services starting in new windows...
echo Wait 5 seconds, then run: python run_audit_simple.py
echo.
pause