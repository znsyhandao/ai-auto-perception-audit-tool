@echo off
REM Enterprise Audit Framework v3.0 - Deployment Script (English)
REM Generated: 2026-03-30

echo ==========================================
echo    Enterprise Audit Framework v3.0
echo    Deployment Script
echo ==========================================
echo.

REM Check Docker
echo [CHECK] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not installed. Please install Docker Desktop for Windows.
    echo Download: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
echo [OK] Docker is installed

REM Check Docker Compose
echo [CHECK] Checking Docker Compose...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose not installed.
    echo Docker Desktop usually includes Docker Compose.
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed

REM Create data directories
echo [DIR] Creating data directories...
if not exist data mkdir data
cd data
mkdir mongodb 2>nul
mkdir redis 2>nul
mkdir timescaledb 2>nul
mkdir neo4j 2>nul
mkdir prometheus 2>nul
mkdir grafana 2>nul
mkdir rabbitmq 2>nul
cd ..
echo [OK] Data directories created

REM Start services
echo [SERVICE] Starting Enterprise Audit Framework services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [OK] Services started

REM Wait for services
echo [WAIT] Waiting for services to start (15 seconds)...
timeout /t 15 /nobreak >nul

REM Check service status
echo [STATUS] Checking service status...
docker-compose ps

echo.
echo ==========================================
echo [SUCCESS] Deployment completed!
echo ==========================================
echo.

echo Access the following services:
echo   API Gateway: http://localhost:8000
echo   Monitoring Dashboard: http://localhost:3000 (admin/enterprise123)
echo   Prometheus: http://localhost:9090
echo   RabbitMQ Management: http://localhost:15672 (admin/enterprise123)
echo.

echo Microservice endpoints:
echo   Validator Service: http://localhost:8001
echo   Security Service: http://localhost:8002
echo   Performance Service: http://localhost:8003
echo   Compliance Service: http://localhost:8004
echo   Reporting Service: http://localhost:8005
echo.

echo Management commands:
echo   View logs: docker-compose logs -f
echo   Restart services: docker-compose restart
echo   Stop services: docker-compose down
echo.

echo Test the framework:
echo   python test_enterprise_framework.py
echo.

echo ==========================================
pause