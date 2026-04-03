@echo off
echo Enterprise Integration Deployment
echo ================================

echo 1. Building mathematical audit service...
docker build -t mathematical-audit:enterprise -f microservices/mathematical-audit-service/Dockerfile microservices/mathematical-audit-service

if errorlevel 1 (
    echo Build failed
    exit /b 1
)

echo 2. Starting services...
docker-compose -f enterprise_integration/docker-compose.yml up -d

echo 3. Waiting for service to start...
timeout /t 10 /nobreak >nul

echo 4. Testing service...
python enterprise_integration/integration_test.py

if errorlevel 1 (
    echo Integration test failed
    exit /b 1
)

echo ================================
echo DEPLOYMENT SUCCESSFUL
echo ================================
echo Service: http://localhost:8010
echo Health:  http://localhost:8010/health
echo Docs:    http://localhost:8010/docs
echo ================================
