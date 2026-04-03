# Enterprise Audit Framework - Simple Startup Script
# Starts all services in separate PowerShell windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Enterprise Audit Framework v3.0" -ForegroundColor Yellow
Write-Host "Simple Startup Script" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Start API Gateway
Write-Host "[1] Starting API Gateway (port 8000)..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD\microservices\api-gateway'; uvicorn main:app --host 0.0.0.0 --port 8000 --reload`"" -WindowStyle Normal
Start-Sleep -Seconds 3

# Start Validator Service
Write-Host "[2] Starting Validator Service (port 8001)..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD\microservices\validator-service'; uvicorn main:app --host 0.0.0.0 --port 8001 --reload`"" -WindowStyle Normal
Start-Sleep -Seconds 2

# Start Security Service
Write-Host "[3] Starting Security Service (port 8002)..." -ForegroundColor Gray
Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$PWD\microservices\security-service'; uvicorn main:app --host 0.0.0.0 --port 8002 --reload`"" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] All services started!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Access the services:" -ForegroundColor White
Write-Host "  API Gateway: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Validator Service: http://localhost:8001" -ForegroundColor Cyan
Write-Host "  Security Service: http://localhost:8002" -ForegroundColor Cyan
Write-Host ""

Write-Host "Test endpoints:" -ForegroundColor White
Write-Host "  curl http://localhost:8000/" -ForegroundColor Gray
Write-Host "  curl http://localhost:8000/health" -ForegroundColor Gray
Write-Host "  curl http://localhost:8001/" -ForegroundColor Gray
Write-Host "  curl http://localhost:8002/" -ForegroundColor Gray
Write-Host ""

Write-Host "Press Enter to open API Gateway in browser..." -ForegroundColor White
Read-Host

# Open browser
Start-Process "http://localhost:8000"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Enterprise Framework is now running!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan