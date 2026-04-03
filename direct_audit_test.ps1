# Direct Audit Test - Bypass API Gateway if needed

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Direct AISleepGen Audit Test" -ForegroundColor Yellow
Write-Host "Using Validator and Security Services directly" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check services
Write-Host "[CHECK] Checking services..." -ForegroundColor Gray

$services = @(
    @{Name="Validator Service"; Url="http://localhost:8001/"},
    @{Name="Security Service"; Url="http://localhost:8002/"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-RestMethod -Uri $service.Url -TimeoutSec 3
        Write-Host "[OK] $($service.Name) is running" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] $($service.Name) is not responding" -ForegroundColor Red
        exit 1
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

# Test 1: Validator Service
Write-Host "[TEST 1] Testing Validator Service..." -ForegroundColor Gray
try {
    $validatorRequest = @{
        skill_id = "aisleepgen_v1.0.7"
        skill_path = $skillPath
        validation_type = "full"
    } | ConvertTo-Json
    
    Write-Host "  Submitting validation request..." -ForegroundColor DarkGray
    $validatorResult = Invoke-RestMethod -Uri "http://localhost:8001/validate" `
        -Method Post `
        -Body $validatorRequest `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "[SUCCESS] Validation completed!" -ForegroundColor Green
    Write-Host "  Score: $($validatorResult.score)/100" -ForegroundColor Cyan
    Write-Host "  Passed: $($validatorResult.passed)" -ForegroundColor Cyan
    Write-Host "  Issues: $($validatorResult.issues.Count)" -ForegroundColor Cyan
    Write-Host "  Warnings: $($validatorResult.warnings.Count)" -ForegroundColor Cyan
    
} catch {
    Write-Host "[ERROR] Validator test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test 2: Security Service
Write-Host "[TEST 2] Testing Security Service..." -ForegroundColor Gray
try {
    $securityRequest = @{
        skill_id = "aisleepgen_v1.0.7"
        skill_path = $skillPath
        scan_depth = "standard"
    } | ConvertTo-Json
    
    Write-Host "  Submitting security scan..." -ForegroundColor DarkGray
    $securityResult = Invoke-RestMethod -Uri "http://localhost:8002/scan" `
        -Method Post `
        -Body $securityRequest `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "[SUCCESS] Security scan completed!" -ForegroundColor Green
    Write-Host "  Security Score: $($securityResult.security_score)/100" -ForegroundColor Cyan
    Write-Host "  Risk Level: $($securityResult.risk_level)" -ForegroundColor Cyan
    Write-Host "  Threats: $($securityResult.threats.Count)" -ForegroundColor Cyan
    Write-Host "  Vulnerabilities: $($securityResult.vulnerabilities.Count)" -ForegroundColor Cyan
    
} catch {
    Write-Host "[ERROR] Security test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUMMARY] Direct Audit Results" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "AISleepGen v1.0.7 has been audited by:" -ForegroundColor Gray
Write-Host "  1. Validator Service - Basic structure and compliance" -ForegroundColor Gray
Write-Host "  2. Security Service - AI-driven security analysis" -ForegroundColor Gray
Write-Host ""
Write-Host "View detailed results:" -ForegroundColor Gray
Write-Host "  Validator: curl http://localhost:8001/validate/aisleepgen_v1.0.7" -ForegroundColor DarkGray
Write-Host "  Security: curl http://localhost:8002/scan/aisleepgen_v1.0.7" -ForegroundColor DarkGray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Direct audit completed!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan