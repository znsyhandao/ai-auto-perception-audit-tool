@echo off
echo ==========================================
echo   Enterprise Audit Framework - Start Services
echo ==========================================
echo.

echo [1] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

echo.
echo [2] Checking dependencies...
python -c "import fastapi; import uvicorn; print('Dependencies OK')"
if errorlevel 1 (
    echo WARNING: FastAPI or Uvicorn not installed
    echo Run: pip install fastapi uvicorn
)

echo.
echo [3] Starting 6 microservices...
echo.

REM Start each service in new windows
start "Validator Service" cmd /k "cd /d microservices\validator-service && uvicorn main:app --host 0.0.0.0 --port 8001 --reload"
timeout /t 3 /nobreak >nul

start "Security Service" cmd /k "cd /d microservices\security-service && uvicorn main:app --host 0.0.0.0 --port 8002 --reload"
timeout /t 3 /nobreak >nul

start "Performance Service" cmd /k "cd /d microservices\performance-service && uvicorn main:app --host 0.0.0.0 --port 8003 --reload"
timeout /t 3 /nobreak >nul

start "Compliance Service" cmd /k "cd /d microservices\compliance-service && uvicorn main:app --host 0.0.0.0 --port 8004 --reload"
timeout /t 3 /nobreak >nul

start "Reporting Service" cmd /k "cd /d microservices\reporting-service && uvicorn main:app --host 0.0.0.0 --port 8005 --reload"
timeout /t 3 /nobreak >nul

start "Monitoring Service" cmd /k "cd /d microservices\monitoring-service && uvicorn main:app --host 0.0.0.0 --port 8006 --reload"
timeout /t 3 /nobreak >nul

echo.
echo [4] Waiting for services to start (15 seconds)...
timeout /t 15 /nobreak >nul

echo.
echo ==========================================
echo Services started in separate windows
echo.
echo Service Endpoints:
echo   Validator:    http://localhost:8001
echo   Security:     http://localhost:8002
echo   Performance:  http://localhost:8003
echo   Compliance:   http://localhost:8004
echo   Reporting:    http://localhost:8005
echo   Monitoring:   http://localhost:8006
echo.
echo Monitoring Dashboard: http://localhost:8006/status
echo Web Interface: file://%CD%/dashboard/frontend/index.html
echo Full Audit Test: python run_full_audit.py
echo ==========================================
echo.
pause