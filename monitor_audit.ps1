# Monitor AISleepGen Audit Progress

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AISleepGen Audit Monitor" -ForegroundColor Yellow
Write-Host "Real-time progress tracking" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$skillId = "aisleepgen_v1.0.7"
$checkCount = 0

Write-Host "[INFO] Monitoring audit for: $skillId" -ForegroundColor Gray
Write-Host "      Press Ctrl+C to stop monitoring" -ForegroundColor Gray
Write-Host ""

while ($true) {
    $checkCount++
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    Write-Host "[$timestamp] Check #$checkCount" -ForegroundColor DarkGray
    
    # Check Validator Service
    try {
        $validatorStatus = Invoke-RestMethod -Uri "http://localhost:8001/validate/$skillId" -TimeoutSec 3
        Write-Host "  [VALIDATOR] Score: $($validatorStatus.score)" -ForegroundColor Cyan
        if ($validatorStatus.ContainsKey("passed")) {
            Write-Host "          Passed: $($validatorStatus.passed)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "  [VALIDATOR] Not available yet" -ForegroundColor DarkGray
    }
    
    # Check Security Service
    try {
        $securityStatus = Invoke-RestMethod -Uri "http://localhost:8002/scan/$skillId" -TimeoutSec 3
        Write-Host "  [SECURITY] Score: $($securityStatus.security_score)" -ForegroundColor Cyan
        Write-Host "          Risk: $($securityStatus.risk_level)" -ForegroundColor Cyan
    } catch {
        Write-Host "  [SECURITY] Not available yet" -ForegroundColor DarkGray
    }
    
    Write-Host ""
    
    # Check if both services have results
    try {
        $hasValidator = $null -ne (Invoke-RestMethod -Uri "http://localhost:8001/validate/$skillId" -TimeoutSec 3 -ErrorAction SilentlyContinue)
        $hasSecurity = $null -ne (Invoke-RestMethod -Uri "http://localhost:8002/scan/$skillId" -TimeoutSec 3 -ErrorAction SilentlyContinue)
        
        if ($hasValidator -and $hasSecurity) {
            Write-Host "==========================================" -ForegroundColor Green
            Write-Host "[COMPLETE] Audit finished for $skillId!" -ForegroundColor Green
            Write-Host "==========================================" -ForegroundColor Green
            Write-Host ""
            
            # Get final results
            $finalValidator = Invoke-RestMethod -Uri "http://localhost:8001/validate/$skillId" -TimeoutSec 5
            $finalSecurity = Invoke-RestMethod -Uri "http://localhost:8002/scan/$skillId" -TimeoutSec 5
            
            Write-Host "FINAL RESULTS:" -ForegroundColor White
            Write-Host "==============" -ForegroundColor White
            Write-Host ""
            Write-Host "Validator Service:" -ForegroundColor Cyan
            Write-Host "  Score: $($finalValidator.score)/100" -ForegroundColor Gray
            Write-Host "  Passed: $($finalValidator.passed)" -ForegroundColor Gray
            if ($finalValidator.ContainsKey("issues")) {
                Write-Host "  Issues: $($finalValidator.issues.Count)" -ForegroundColor Gray
            }
            if ($finalValidator.ContainsKey("warnings")) {
                Write-Host "  Warnings: $($finalValidator.warnings.Count)" -ForegroundColor Gray
            }
            Write-Host ""
            Write-Host "Security Service:" -ForegroundColor Cyan
            Write-Host "  Security Score: $($finalSecurity.security_score)/100" -ForegroundColor Gray
            Write-Host "  Risk Level: $($finalSecurity.risk_level)" -ForegroundColor Gray
            if ($finalSecurity.ContainsKey("threats")) {
                Write-Host "  Threats: $($finalSecurity.threats.Count)" -ForegroundColor Gray
            }
            if ($finalSecurity.ContainsKey("vulnerabilities")) {
                Write-Host "  Vulnerabilities: $($finalSecurity.vulnerabilities.Count)" -ForegroundColor Gray
            }
            
            Write-Host ""
            Write-Host "View detailed results:" -ForegroundColor White
            Write-Host "  Validator: curl http://localhost:8001/validate/$skillId" -ForegroundColor DarkGray
            Write-Host "  Security: curl http://localhost:8002/scan/$skillId" -ForegroundColor DarkGray
            Write-Host ""
            Write-Host "==========================================" -ForegroundColor Green
            break
        }
    } catch {
        # Continue monitoring
    }
    
    # Wait before next check
    Start-Sleep -Seconds 5
}