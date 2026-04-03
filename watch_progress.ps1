# Watch AISleepGen Audit Progress in Real-time

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AISleepGen Audit Progress Monitor" -ForegroundColor Yellow
Write-Host "Watching validation and security scan" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$skillId = "aisleepgen_v1.0.7"
$checkInterval = 2  # seconds
$dots = 0

Write-Host "[INFO] Monitoring audit for: $skillId" -ForegroundColor Gray
Write-Host "      Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

# Animation while waiting
while ($true) {
    $timestamp = Get-Date -Format "HH:mm:ss"
    
    # Simple animation
    $animation = @(".", "..", "...")[$dots % 3]
    $dots++
    
    Write-Host "[$timestamp] Processing$animation" -ForegroundColor DarkGray -NoNewline
    
    # Try to get validator status
    try {
        $validatorStatus = Invoke-RestMethod -Uri "http://localhost