#!/usr/bin/env powershell
<#
Ultimate Audit Suite - ASCII version
Run all audit tools to ensure ClawHub level compliance
#>

param(
    [string]$SkillPath
)

Write-Host "=== Ultimate Audit Suite ===" -ForegroundColor Cyan
Write-Host "Skill Path: $SkillPath" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $SkillPath)) {
    Write-Host "ERROR: Skill path does not exist: $SkillPath" -ForegroundColor Red
    exit 1
}

$allPassed = $true
$results = @()

# 1. Simple ClawHub Check
Write-Host "[1/5] Simple ClawHub Check..." -ForegroundColor Yellow
try {
    $result = .\simple_clawhub_check.ps1 $SkillPath 2>&1
    if ($result -match "\[PASS\]") {
        Write-Host "  PASS" -ForegroundColor Green
        $results += @{Check="Simple ClawHub Check"; Passed=$true}
    } else {
        Write-Host "  FAIL" -ForegroundColor Red
        $results += @{Check="Simple ClawHub Check"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    $results += @{Check="Simple ClawHub Check"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 2. Security Claim Verification
Write-Host "[2/5] Security Claim Verification..." -ForegroundColor Yellow
try {
    $result = python security_claim_verifier_compact.py $SkillPath 2>&1
    if ($result -match "\[SUCCESS\]") {
        Write-Host "  PASS" -ForegroundColor Green
        $results += @{Check="Security Claim Verification"; Passed=$true}
    } else {
        Write-Host "  FAIL" -ForegroundColor Red
        $results += @{Check="Security Claim Verification"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    $results += @{Check="Security Claim Verification"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 3. Document Consistency Check
Write-Host "[3/5] Document Consistency Check..." -ForegroundColor Yellow
try {
    $result = python document_metadata_consistency_compact.py $SkillPath 2>&1
    if ($result -match "\[SUCCESS\]") {
        Write-Host "  PASS" -ForegroundColor Green
        $results += @{Check="Document Consistency Check"; Passed=$true}
    } else {
        Write-Host "  FAIL" -ForegroundColor Red
        $results += @{Check="Document Consistency Check"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    $results += @{Check="Document Consistency Check"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 4. ClawHub Level Audit
Write-Host "[4/5] ClawHub Level Audit..." -ForegroundColor Yellow
try {
    $result = python clawhub_level_audit.py $SkillPath 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PASS" -ForegroundColor Green
        $results += @{Check="ClawHub Level Audit"; Passed=$true}
    } else {
        Write-Host "  FAIL" -ForegroundColor Red
        $results += @{Check="ClawHub Level Audit"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    $results += @{Check="ClawHub Level Audit"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 5. Permanent Audit Framework
Write-Host "[5/5] Permanent Audit Framework..." -ForegroundColor Yellow
try {
    $result = python permanent_audit_ascii.py $SkillPath 2>&1
    if ($result -match "all_passed.*true") {
        Write-Host "  PASS" -ForegroundColor Green
        $results += @{Check="Permanent Audit Framework"; Passed=$true}
    } else {
        Write-Host "  FAIL" -ForegroundColor Red
        $results += @{Check="Permanent Audit Framework"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
    $results += @{Check="Permanent Audit Framework"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# Summary
Write-Host ""
Write-Host "=== Audit Results ===" -ForegroundColor Cyan

$passedCount = ($results | Where-Object { $_.Passed -eq $true }).Count
$totalCount = $results.Count

Write-Host "Passed Checks: $passedCount/$totalCount" -ForegroundColor $(if ($allPassed) { "Green" } else { "Red" })

foreach ($result in $results) {
    $status = if ($result.Passed) { "PASS" } else { "FAIL" }
    Write-Host "  $status $($result.Check)" -ForegroundColor $(if ($result.Passed) { "Green" } else { "Red" })
}

if ($allPassed) {
    Write-Host ""
    Write-Host "SUCCESS: All audits passed! Ready for ClawHub submission." -ForegroundColor Green
    Write-Host "Expected Status: Clean (high confidence)" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "WARNING: Issues found, need to fix before submission." -ForegroundColor Red
    Write-Host "Expected Status: Suspicious (needs fixes)" -ForegroundColor Red
}

exit $(if ($allPassed) { 0 } else { 1 })