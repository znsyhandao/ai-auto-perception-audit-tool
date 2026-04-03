# Monitor AISleepGen Audit Progress

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AISleepGen Audit Progress Monitor" -ForegroundColor Yellow
Write-Host "Real-time status tracking" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$skillId = "aisleepgen_v1.0.7"
$startTime = Get-Date
$status = "processing"

Write-Host "[START] Audit started at: $startTime" -ForegroundColor Gray
Write-Host "[SKILL] AISleepGen v1.0.7" -ForegroundColor Gray
Write-Host "[PATH] D:\openclaw\releases\AISleepGen\v1.0.7_fixed" -ForegroundColor Gray
Write-Host ""

# Check initial status
Write-Host "[CHECK] Checking services..." -ForegroundColor Gray

try {
    $validatorHealth = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 2
    Write-Host "  [VALIDATOR] Status: $($validatorHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "  [VALIDATOR] Not responding" -ForegroundColor Red
}

try {
    $securityHealth = Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 2
    Write-Host "  [SECURITY] Status: $($securityHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "  [SECURITY] Not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "[WAIT] Waiting for validation to complete..." -ForegroundColor Gray
Write-Host "      This may take 10-30 seconds..." -ForegroundColor DarkGray
Write-Host ""

# Wait for validation
$maxWait = 60  # seconds
$elapsed = 0

while ($elapsed -lt $maxWait) {
    $currentTime = Get-Date
    $elapsed = [math]::Round(($currentTime - $startTime).TotalSeconds)
    
    Write-Host "[$elapsed s] Checking validation status..." -ForegroundColor DarkGray -NoNewline
    
    try {
        # Try to get validation result
        $validatorResult = Invoke-RestMethod -Uri "http://localhost:8001/validate/$skillId" -TimeoutSec 2 -ErrorAction SilentlyContinue
        
        if ($validatorResult) {
            Write-Host " [COMPLETE]" -ForegroundColor Green
            Write-Host ""
            Write-Host "[VALIDATION RESULTS]" -ForegroundColor Cyan
            Write-Host "====================" -ForegroundColor Cyan
            Write-Host "Score: $($validatorResult.score)/100" -ForegroundColor White
            Write-Host "Passed: $($validatorResult.passed)" -ForegroundColor White
            Write-Host "Timestamp: $($validatorResult.timestamp)" -ForegroundColor Gray
            
            # Now check security scan
            Write-Host ""
            Write-Host "[WAIT] Starting security scan..." -ForegroundColor Gray
            
            # Submit security scan request
            $securityRequest = @{
                skill_id = $skillId
                skill_path = "D:\openclaw\releases\AISleepGen\v1.0.7_fixed"
                scan_depth = "standard"
            } | ConvertTo-Json
            
            try {
                $securityResponse = Invoke-RestMethod -Uri "http://localhost:8002/scan" `
                    -Method Post `
                    -Body $securityRequest `
                    -ContentType "application/json" `
                    -TimeoutSec 30
                
                Write-Host "[SECURITY SCAN STARTED]" -ForegroundColor Green
                
                # Wait for security results
                Write-Host "[WAIT] Waiting for security scan (10-20 seconds)..." -ForegroundColor Gray
                Start-Sleep -Seconds 10
                
                # Get security results
                $securityResult = Invoke-RestMethod -Uri "http://localhost:8002/scan/$skillId" -TimeoutSec 5
                
                Write-Host ""
                Write-Host "[SECURITY RESULTS]" -ForegroundColor Cyan
                Write-Host "==================" -ForegroundColor Cyan
                Write-Host "Security Score: $($securityResult.security_score)/100" -ForegroundColor White
                Write-Host "Risk Level: $($securityResult.risk_level)" -ForegroundColor White
                Write-Host "Threats: $($securityResult.threat_count)" -ForegroundColor White
                
                Write-Host ""
                Write-Host "==========================================" -ForegroundColor Green
                Write-Host "[SUCCESS] AISleepGen Audit Complete!" -ForegroundColor Green
                Write-Host "==========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Total time: $elapsed seconds" -ForegroundColor Gray
                Write-Host ""
                Write-Host "View detailed results:" -ForegroundColor White
                Write-Host "  Validator: curl http://localhost:8001/validate/$skillId" -ForegroundColor DarkGray
                Write-Host "  Security: curl http://localhost:8002/scan/$skillId" -ForegroundColor DarkGray
                Write-Host ""
                Write-Host "Enterprise Audit Framework v3.0 is working!" -ForegroundColor Cyan
                
                exit 0
                
            } catch {
                Write-Host "[ERROR] Security scan failed: $_" -ForegroundColor Red
                exit 1
            }
            
            break
        }
        
    } catch {
        # Validation not ready yet
    }
    
    Write-Host " [PENDING]" -ForegroundColor Yellow
    
    # Wait before next check
    Start-Sleep -Seconds 3
}

Write-Host ""
Write-Host "[TIMEOUT] Validation took too long ($maxWait seconds)" -ForegroundColor Red
Write-Host ""
Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
Write-Host "1. Check validator service logs" -ForegroundColor Gray
Write-Host "2. Ensure skill path is accessible" -ForegroundColor Gray
Write-Host "3. Restart validator service" -ForegroundColor Gray
Write-Host ""
Write-Host "Validator service command:" -ForegroundColor White
Write-Host '  cd "D:\OpenClaw_TestingFramework\microservices\validator-service"' -ForegroundColor DarkGray
Write-Host '  uvicorn main_fixed:app --host 0.0.0.0 --port 8001 --reload' -ForegroundColor DarkGray

exit 1