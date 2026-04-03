@echo off
echo ==========================================
echo Enterprise Audit Framework - Start All Services
echo ==========================================
echo.

echo [CHECK] Checking API Gateway...
curl -s http://localhost:8000/ > nul 2>&1
if errorlevel 1 (
    echo [ERROR] API Gateway not running. Please start it first.
    echo Run: .\start_minimal.bat
    pause
    exit /b 1
)
echo [OK] API Gateway is running on http://localhost:8000
echo.

echo [1] Starting Validator Service (port 8001)...
start "Validator Service" powershell -NoExit -Command "cd '%~dp0microservices\validator-service'; uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak > nul

echo [2] Starting Security Service (port 8002)...
start "Security Service" powershell -NoExit -Command "cd '%~dp0microservices\security-service'; uvicorn main:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 3 /nobreak > nul

echo.
echo ==========================================
echo [SUCCESS] All services starting!
echo ==========================================
echo.

echo Access URLs:
echo   API Gateway: http://localhost:8000
echo   Validator Service: http://localhost:8001
echo   Security Service: http://localhost:8002
echo.

echo Test commands:
echo   curl http://localhost:8000/
echo   curl http://localhost:8000/health
echo   curl http://localhost:8001/
echo   curl http://localhost:8002/
echo.

echo Press any key to open API Gateway in browser...
pause > nul

start http://localhost:8000

echo.
echo Enterprise Audit Framework v3.0 is now running!
echo ==========================================