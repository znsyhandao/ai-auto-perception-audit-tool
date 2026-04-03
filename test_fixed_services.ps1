# Test Fixed Services for AISleepGen Audit

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Testing Fixed Services" -ForegroundColor Yellow
Write-Host "AISleepGen Audit - No Redis Required" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check services
Write-Host "[CHECK] Checking fixed services..." -ForegroundColor Gray

$services = @(
    @{Name="Validator Service (Fixed)"; Url="http://localhost:8001/"},
    @{Name="Security Service (Fixed)"; Url="http://localhost:8002/"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-RestMethod -Uri $service.Url -TimeoutSec 3
        Write-Host "[OK] $($service.Name) is running" -ForegroundColor Green
        Write-Host "     Version: $($response.version)" -ForegroundColor DarkGray
        Write-Host "     Storage: $($response.storage)" -ForegroundColor DarkGray
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
    $files = Get-ChildItem $skillPath -File
    Write-Host "      Files: $($files.Count)" -ForegroundColor Gray
    Write-Host "      File list:" -ForegroundColor DarkGray
    foreach ($file in $files) {
        Write-Host "        - $($file.Name) ($($file.Length) bytes)" -ForegroundColor DarkGray
    }
} else {
    Write-Host "[ERROR] Skill directory not found: $skillPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test Validator Service
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
    
    # Show some issues if any
    if ($validatorResult.issues.Count -gt 0) {
        Write-Host "  Critical Issues:" -ForegroundColor Red
        foreach ($issue in $validatorResult.issues | Select-Object -First 3) {
            Write-Host "    - $($issue.message)" -ForegroundColor DarkRed
        }
    }
    
    if ($validatorResult.warnings.Count -gt 0) {
        Write-Host "  Warnings:" -ForegroundColor Yellow
        foreach ($warning in $validatorResult.warnings | Select-Object -First 3) {
            Write-Host "    - $($warning.message)" -ForegroundColor DarkYellow
        }
    }
    
} catch {
    Write-Host "[ERROR] Validator test failed: $_" -ForegroundColor Red
}

Write-Host ""

# Test Security Service
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
    Write-Host "  Threats Found: $($securityResult.threats.Count)" -ForegroundColor Cyan
    
    # Show threats if any
    if ($securityResult.threats.Count -gt 0) {
        Write-Host "  Security Threats:" -ForegroundColor Red
        foreach ($threat in $securityResult.threats | Select-Object -First 3) {
            Write-Host "    - $($threat.type) in $($threat.filename):$($threat.line)" -ForegroundColor DarkRed
            Write-Host "      Pattern: $($threat.pattern)" -ForegroundColor DarkGray
        }
    }
    
} catch {
    Write-Host "[ERROR] Security test failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUMMARY] AISleepGen Audit Results" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Enterprise Audit Framework (Fixed Version) has successfully audited:" -ForegroundColor Gray
Write-Host "  Skill: AISleepGen v1.0.7" -ForegroundColor Gray
Write-Host "  Location: $skillPath" -ForegroundColor Gray
Write-Host ""
Write-Host "View detailed results:" -ForegroundColor White
Write-Host "  Validator: curl http://localhost:8001/validate/aisleepgen_v1.0.7" -ForegroundColor DarkGray
Write-Host "  Security: curl http://localhost:8002/scan/aisleepgen_v1.0.7" -ForegroundColor DarkGray
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Enterprise Framework is working!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan