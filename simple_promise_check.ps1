# simple_promise_check.ps1
# Simple promise verification tool

param(
    [string]$SkillDir
)

Write-Host "=== Simple Promise Verification ===" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Check 1: Are there specific promises?
Write-Host "1. Checking for specific promises..." -ForegroundColor Yellow
$hasPromises = $false
$promiseFiles = Get-ChildItem -Path $SkillDir -File -Include *.md, *.txt | Where-Object {
    $_.Name -match "RELEASE|AUDIT|SUMMARY"
}

foreach ($file in $promiseFiles) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "通过审核|通过ClawHub|承诺|保证|100%|Ready for ClawHub") {
        $hasPromises = $true
        Write-Host "  [FOUND] Promises in: $($file.Name)" -ForegroundColor Green
        $lines = $content -split "`n" | Where-Object { $_ -match "通过审核|通过ClawHub|承诺|保证|100%|Ready for ClawHub" }
        foreach ($line in $lines | Select-Object -First 3) {
            Write-Host "    > $line" -ForegroundColor Gray
        }
    }
}

if (-not $hasPromises) {
    Write-Host "  [MISSING] No specific promises found" -ForegroundColor Red
}

# Check 2: Are there audit reports?
Write-Host "`n2. Checking for audit reports..." -ForegroundColor Yellow
$auditReports = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "AUDIT|REPORT"
}

if ($auditReports.Count -gt 0) {
    Write-Host "  [FOUND] $($auditReports.Count) audit reports:" -ForegroundColor Green
    foreach ($report in $auditReports) {
        Write-Host "    - $($report.Name) ($($report.Length) bytes)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [MISSING] No audit reports found" -ForegroundColor Red
}

# Check 3: Check version consistency
Write-Host "`n3. Checking version consistency..." -ForegroundColor Yellow
$versions = @()

# Check config.yaml
$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match 'version:\s*["'']?([0-9]+\.[0-9]+\.[0-9]+)["'']?') {
        $versions += "config.yaml: $($matches[1])"
    }
}

# Check package.json
$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    $packageContent = Get-Content $packagePath -Raw
    if ($packageContent -match '"version"\s*:\s*["'']([0-9]+\.[0-9]+\.[0-9]+)["'']') {
        $versions += "package.json: $($matches[1])"
    }
}

# Check SKILL.md
$skillPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    if ($skillContent -match 'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)') {
        $versions += "SKILL.md: $($matches[1])"
    }
}

if ($versions.Count -ge 2) {
    $uniqueVersions = $versions | ForEach-Object { $_ -replace '.*: ' } | Select-Object -Unique
    if ($uniqueVersions.Count -eq 1) {
        Write-Host "  [PASS] All versions consistent: $($uniqueVersions[0])" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] Version inconsistency:" -ForegroundColor Red
        foreach ($v in $versions) {
            Write-Host "    $v" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  [WARN] Could not extract enough version information" -ForegroundColor Yellow
}

# Check 4: Check license file
Write-Host "`n4. Checking license file..." -ForegroundColor Yellow
$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.BaseName -match "^LICENSE$|^LICENCE$|^license$|^licence$"
}

if ($licenseFiles.Count -gt 0) {
    $licenseFile = $licenseFiles[0]
    $hasValidExtension = $licenseFile.Extension -in @(".txt", ".md")
    
    if ($hasValidExtension) {
        Write-Host "  [PASS] License file has valid extension: $($licenseFile.Name)" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] License file has invalid extension: $($licenseFile.Extension)" -ForegroundColor Red
    }
} else {
    Write-Host "  [FAIL] No license file found" -ForegroundColor Red
}

# Check 5: Check for risk disclosure
Write-Host "`n5. Checking for risk disclosure..." -ForegroundColor Yellow
$hasRiskDisclosure = $false

foreach ($report in $auditReports) {
    $content = Get-Content $report.FullName -Raw
    if ($content -match "风险|风险说明|limitation|Limitation|警告|warning|Warning|unknown|Unknown") {
        $hasRiskDisclosure = $true
        Write-Host "  [FOUND] Risk disclosure in: $($report.Name)" -ForegroundColor Green
        break
    }
}

if (-not $hasRiskDisclosure) {
    Write-Host "  [MISSING] No risk disclosure found" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan

$checks = @(
    @{ name = "Specific promises"; passed = $hasPromises },
    @{ name = "Audit reports"; passed = $auditReports.Count -gt 0 },
    @{ name = "Version consistency"; passed = $versions.Count -ge 2 -and ($versions | ForEach-Object { $_ -replace '.*: ' } | Select-Object -Unique).Count -eq 1 },
    @{ name = "License file"; passed = $licenseFiles.Count -gt 0 -and $licenseFiles[0].Extension -in @(".txt", ".md") },
    @{ name = "Risk disclosure"; passed = $hasRiskDisclosure }
)

$passed = ($checks | Where-Object { $_.passed }).Count
$total = $checks.Count
$score = [math]::Round(($passed / $total) * 100)

Write-Host "Passed: $passed/$total ($score%)" -ForegroundColor White

foreach ($check in $checks) {
    $status = if ($check.passed) { "[PASS]" } else { "[FAIL]" }
    $color = if ($check.passed) { "Green" } else { "Red" }
    Write-Host "  $status $($check.name)" -ForegroundColor $color
}

# Trust level
if ($score -ge 90) {
    Write-Host "`nTrust Level: HIGH" -ForegroundColor Green
    Write-Host "Promises are likely to be fulfilled" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "`nTrust Level: MEDIUM" -ForegroundColor Yellow
    Write-Host "Promises need improvement" -ForegroundColor Yellow
} else {
    Write-Host "`nTrust Level: LOW" -ForegroundColor Red
    Write-Host "Promises are not reliable" -ForegroundColor Red
}

# Improvement suggestions
Write-Host "`nImprovement suggestions:" -ForegroundColor Cyan
if (-not $hasPromises) {
    Write-Host "  • Add specific promise statements" -ForegroundColor Yellow
}
if ($auditReports.Count -eq 0) {
    Write-Host "  • Add audit reports" -ForegroundColor Yellow
}
if ($licenseFiles.Count -eq 0) {
    Write-Host "  • Add license file (LICENSE.txt)" -ForegroundColor Yellow
}
if (-not $hasRiskDisclosure) {
    Write-Host "  • Add risk disclosure" -ForegroundColor Yellow
}

Write-Host "`n=== Check Complete ===" -ForegroundColor Cyan