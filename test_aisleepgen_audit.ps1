# AISleepGen Skill Audit Test Script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AISleepGen Skill Audit Test" -ForegroundColor Yellow
Write-Host "Enterprise Audit Framework v3.0" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if services are running
Write-Host "[CHECK] Checking services..." -ForegroundColor Gray

$services = @(
    @{Name="API Gateway"; Url="http://localhost:8000/"},
    @{Name="Validator Service"; Url="http://localhost:8001/"},
    @{Name="Security Service"; Url="http://localhost:8002/"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-RestMethod -Uri $service.Url -TimeoutSec 3
        Write-Host "[OK] $($service.Name) is running" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] $($service.Name) is not responding" -ForegroundColor Yellow
    }
}

Write-Host ""

# AISleepGen skill path
$skillPath = "D:\openclaw\releases\AISleepGen\v1.0.7_fixed"
Write-Host "[INFO] Skill to audit: $skillPath" -ForegroundColor Gray

# Check if skill exists
if (Test-Path $skillPath) {
    Write-Host "[OK] Skill directory exists" -ForegroundColor Green
    $fileCount = (Get-ChildItem $skillPath -File | Measure-Object).Count
    Write-Host "      Files: $fileCount" -ForegroundColor Gray
} else {
    Write-Host "[ERROR] Skill directory not found: $skillPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create audit request
Write-Host "[AUDIT] Creating audit request..." -ForegroundColor Gray

$auditRequest = @{
    skill_id = "aisleepgen_v1.0.7"
    skill_path = $skillPath
    priority = "normal"
    callback_url = $null
    metadata = @{
        project = "AISleepGen"
        version = "1.0.7"
        type = "sleep_health_skill"
    }
} | ConvertTo-Json

Write-Host "Request data:" -ForegroundColor Gray
Write-Host $auditRequest -ForegroundColor DarkGray
Write-Host ""

# Submit audit request
try {
    Write-Host "[POST] Submitting to API Gateway..." -ForegroundColor Gray
    $response = Invoke-RestMethod -Uri "http://localhost:8000/audit" `
        -Method Post `
        -Body $auditRequest `
        -ContentType "application/json" `
        -TimeoutSec 10
    
    Write-Host "[SUCCESS] Audit task created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Audit ID: $($response.audit_id)" -ForegroundColor Cyan
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
    Write-Host "Message: $($response.message)" -ForegroundColor Cyan
    Write-Host "Created: $($response.created_at)" -ForegroundColor Cyan
    
    # Get audit status
    Write-Host ""
    Write-Host "[STATUS] Getting audit status..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
    
    $statusUrl = "http://localhost:8000/audit/$($response.audit_id)"
    $status = Invoke-RestMethod -Uri $statusUrl -TimeoutSec 5
    
    Write-Host "Current status: $($status.status)" -ForegroundColor Cyan
    Write-Host "Estimated time: $($status.estimated_time) seconds" -ForegroundColor Cyan
    
} catch {
    Write-Host "[ERROR] Failed to create audit: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[NEXT STEPS]" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Monitor audit progress:" -ForegroundColor Gray
Write-Host "   curl http://localhost:8000/audit/$($response.audit_id)" -ForegroundColor DarkGray
Write-Host ""
Write-Host "2. Check validator results:" -ForegroundColor Gray
Write-Host "   curl http://localhost:8001/validate/aisleepgen_v1.0.7" -ForegroundColor DarkGray
Write-Host ""
Write-Host "3. Check security scan results:" -ForegroundColor Gray
Write-Host "   curl http://localhost:8002/scan/aisleepgen_v1.0.7" -ForegroundColor DarkGray
Write-Host ""
Write-Host "4. View all audit tasks:" -ForegroundColor Gray
Write-Host "   curl http://localhost:8000/audit" -ForegroundColor DarkGray
Write-Host ""
Write-Host "5. Open API Gateway in browser:" -ForegroundColor Gray
Write-Host "   start http://localhost:8000" -ForegroundColor DarkGray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] AISleepGen audit initiated!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan