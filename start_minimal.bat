@echo off
echo ==========================================
echo Enterprise Audit Framework - Minimal Start
echo ==========================================
echo.

echo [1] Installing missing dependencies...
pip install httpx prometheus-client structlog > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

echo.
echo [2] Starting API Gateway on port 8000...
echo    Open browser to: http://localhost:8000
echo    Press Ctrl+C to stop
echo.

cd microservices\api-gateway
uvicorn main:app --host 0.0.0.0 --port 8000 --reload