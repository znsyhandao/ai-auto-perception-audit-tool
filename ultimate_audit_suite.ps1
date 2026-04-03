#!/usr/bin/env powershell
<#
终极审核套件 - 根本解决方案
运行所有审核工具，确保达到ClawHub级别
#>

param(
    [string]$SkillPath
)

Write-Host "=== 终极审核套件 ===" -ForegroundColor Cyan
Write-Host "技能路径: $SkillPath" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $SkillPath)) {
    Write-Host "❌ 技能路径不存在: $SkillPath" -ForegroundColor Red
    exit 1
}

$allPassed = $true
$results = @()

# 1. 简单ClawHub检查
Write-Host "[1/5] 简单ClawHub检查..." -ForegroundColor Yellow
try {
    $result = .\simple_clawhub_check.ps1 $SkillPath 2>&1
    if ($result -match "\[PASS\]") {
        Write-Host "  ✅ 通过" -ForegroundColor Green
        $results += @{Check="简单ClawHub检查"; Passed=$true}
    } else {
        Write-Host "  ❌ 失败" -ForegroundColor Red
        $results += @{Check="简单ClawHub检查"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    $results += @{Check="简单ClawHub检查"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 2. 安全声明验证
Write-Host "[2/5] 安全声明验证..." -ForegroundColor Yellow
try {
    $result = python security_claim_verifier_compact.py $SkillPath 2>&1
    if ($result -match "\[SUCCESS\]") {
        Write-Host "  ✅ 通过" -ForegroundColor Green
        $results += @{Check="安全声明验证"; Passed=$true}
    } else {
        Write-Host "  ❌ 失败" -ForegroundColor Red
        $results += @{Check="安全声明验证"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    $results += @{Check="安全声明验证"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 3. 文档一致性检查
Write-Host "[3/5] 文档一致性检查..." -ForegroundColor Yellow
try {
    $result = python document_metadata_consistency_compact.py $SkillPath 2>&1
    if ($result -match "\[SUCCESS\]") {
        Write-Host "  ✅ 通过" -ForegroundColor Green
        $results += @{Check="文档一致性检查"; Passed=$true}
    } else {
        Write-Host "  ❌ 失败" -ForegroundColor Red
        $results += @{Check="文档一致性检查"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    $results += @{Check="文档一致性检查"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 4. ClawHub级别审核
Write-Host "[4/5] ClawHub级别审核..." -ForegroundColor Yellow
try {
    $result = python clawhub_level_audit.py $SkillPath 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ 通过" -ForegroundColor Green
        $results += @{Check="ClawHub级别审核"; Passed=$true}
    } else {
        Write-Host "  ❌ 失败" -ForegroundColor Red
        $results += @{Check="ClawHub级别审核"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    $results += @{Check="ClawHub级别审核"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 5. 永久审核框架
Write-Host "[5/5] 永久审核框架..." -ForegroundColor Yellow
try {
    $result = python permanent_audit_ascii.py $SkillPath 2>&1
    if ($result -match "all_passed.*true") {
        Write-Host "  ✅ 通过" -ForegroundColor Green
        $results += @{Check="永久审核框架"; Passed=$true}
    } else {
        Write-Host "  ❌ 失败" -ForegroundColor Red
        $results += @{Check="永久审核框架"; Passed=$false}
        $allPassed = $false
    }
} catch {
    Write-Host "  ❌ 错误: $_" -ForegroundColor Red
    $results += @{Check="永久审核框架"; Passed=$false; Error=$_.ToString()}
    $allPassed = $false
}

# 总结
Write-Host ""
Write-Host "=== 审核结果 ===" -ForegroundColor Cyan

$passedCount = ($results | Where-Object { $_.Passed -eq $true }).Count
$totalCount = $results.Count

Write-Host "通过检查: $passedCount/$totalCount" -ForegroundColor $(if ($allPassed) { "Green" } else { "Red" })

foreach ($result in $results) {
    $status = if ($result.Passed) { "✅" } else { "❌" }
    Write-Host "  $status $($result.Check)" -ForegroundColor $(if ($result.Passed) { "Green" } else { "Red" })
}

if ($allPassed) {
    Write-Host ""
    Write-Host "🎉 所有审核通过！可以提交到ClawHub。" -ForegroundColor Green
    Write-Host "预期状态: Clean (high confidence)" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ 发现问题，需要修复后再提交。" -ForegroundColor Red
    Write-Host "预期状态: Suspicious (需要修复)" -ForegroundColor Red
}

exit $(if ($allPassed) { 0 } else { 1 })