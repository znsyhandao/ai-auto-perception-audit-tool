# simple_ultimate_audit.ps1
# Simplified Ultimate ClawHub Audit Tool

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\simple_audit"
)

Write-Host "=== Simple Ultimate ClawHub Audit ===" -ForegroundColor Cyan
Write-Host "Audit Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Skill Directory: $SkillDir"
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Check if skill directory exists
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] Skill directory not found: $SkillDir" -ForegroundColor Red
    exit 1
}

# Initialize results
$results = @{
    "checks" = @()
    "passed" = 0
    "failed" = 0
    "critical_issues" = @()
    "warnings" = @()
}

function Add-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Message,
        [bool]$Critical = $false
    )
    
    $check = @{
        "name" = $Name
        "passed" = $Passed
        "message" = $Message
        "critical" = $Critical
    }
    
    $results.checks += $check
    
    if ($Passed) {
        $results.passed++
        Write-Host "  [PASS] $Name" -ForegroundColor Green
    } else {
        $results.failed++
        if ($Critical) {
            Write-Host "  [FAIL] $Name (Critical)" -ForegroundColor Red
            $results.critical_issues += $Name
        } else {
            Write-Host "  [WARN] $Name" -ForegroundColor Yellow
            $results.warnings += $Name
        }
    }
}

# ============================================
# 1. Required Files Check
# ============================================
Write-Host "`n1. Required Files Check" -ForegroundColor Yellow

$requiredFiles = @("skill.py", "config.yaml", "SKILL.md", "package.json")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    $exists = Test-Path $filePath
    Add-Check -Name "File: $file" -Passed $exists -Message "$file $(if($exists){'exists'}else{'not found'})" -Critical $true
}

# ============================================
# 2. Version Consistency Check (CRITICAL)
# ============================================
Write-Host "`n2. Version Consistency Check" -ForegroundColor Yellow

$versions = @{}
$filesToCheck = @("config.yaml", "package.json", "skill.py", "SKILL.md")

foreach ($file in $filesToCheck) {
    $filePath = Join-Path $SkillDir $file
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        
        if ($file -eq "config.yaml") {
            if ($content -match "version:\s*['\""]?([\d\.]+)['\""]?") {
                $versions[$file] = $matches[1]
            }
        } elseif ($file -eq "package.json") {
            if ($content -match '"version":\s*"([\d\.]+)"') {
                $versions[$file] = $matches[1]
            }
        } elseif ($file -eq "skill.py") {
            if ($content -match "version\s*=\s*['\""]([\d\.]+)['\""]") {
                $versions[$file] = $matches[1]
            }
        } elseif ($file -eq "SKILL.md") {
            if ($content -match "version[:\s]+([\d\.]+)") {
                $versions[$file] = $matches[1]
            }
        }
    }
}

if ($versions.Count -gt 0) {
    # Check if all versions are the same
    $firstVersion = $versions.Values | Select-Object -First 1
    $allSame = $true
    $different = @()
    
    foreach ($file in $versions.Keys) {
        if ($versions[$file] -ne $firstVersion) {
            $allSame = $false
            $different += "${file}: $($versions[$file])"
        }
    }
    
    Add-Check -Name "Version numbers consistent" -Passed $allSame -Message "Versions: $(if($allSame){'all same'}else{'different: ' + ($different -join ', ')})" -Critical $true
    
    # Check version format
    $isValidFormat = $firstVersion -match "^\d+\.\d+\.\d+$"
    Add-Check -Name "Version format valid" -Passed $isValidFormat -Message "Version format: $firstVersion" -Critical $false
} else {
    Add-Check -Name "Version numbers found" -Passed $false -Message "No version numbers found" -Critical $true
}

# ============================================
# 3. Security Check
# ============================================
Write-Host "`n3. Security Check" -ForegroundColor Yellow

$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    
    # Check for network code
    $hasNetwork = $skillContent -match "import requests|import urllib|import socket|import http\.client"
    Add-Check -Name "No network code" -Passed (-not $hasNetwork) -Message "Network code: $(if($hasNetwork){'found'}else{'not found'})" -Critical $true
    
    # Check for dangerous functions
    $hasDangerous = $skillContent -match "subprocess\.|os\.system|eval\(|exec\(|__import__\("
    Add-Check -Name "No dangerous functions" -Passed (-not $hasDangerous) -Message "Dangerous functions: $(if($hasDangerous){'found'}else{'not found'})" -Critical $true
}

# ============================================
# 4. Link Check (CRITICAL)
# ============================================
Write-Host "`n4. Link Check" -ForegroundColor Yellow

$allLinks = @()
$mdFiles = Get-ChildItem -Path $SkillDir -Filter "*.md" -File

foreach ($file in $mdFiles) {
    $content = Get-Content $file.FullName -Raw
    $urlMatches = [regex]::Matches($content, 'https?://[^\s<>"''\)]+')
    foreach ($match in $urlMatches) {
        $allLinks += @{
            "file" = $file.Name
            "url" = $match.Value
        }
    }
}

# Check package.json for links
$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        if ($packageJson.repository -and $packageJson.repository.url) {
            $allLinks += @{
                "file" = "package.json"
                "url" = $packageJson.repository.url
            }
        }
        
        if ($packageJson.homepage) {
            $allLinks += @{
                "file" = "package.json"
                "url" = $packageJson.homepage
            }
        }
    } catch {
        # Ignore error
    }
}

# Check for placeholder links
$placeholderLinks = @()
foreach ($link in $allLinks) {
    if ($link.url -match 'example\.com|placeholder|TODO|FIXME|your-username|your-repo') {
        $placeholderLinks += "$($link.file): $($link.url)"
    }
}

Add-Check -Name "No placeholder links" -Passed ($placeholderLinks.Count -eq 0) -Message "Placeholder links: $(if($placeholderLinks.Count -eq 0){'none'}else{'found: ' + ($placeholderLinks -join ', ')})" -Critical $true

# ============================================
# 5. Documentation Check
# ============================================
Write-Host "`n5. Documentation Check" -ForegroundColor Yellow

$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $content = Get-Content $skillMdPath -Raw
    $hasSecurity = $content -match "Security|Safety"
    Add-Check -Name "SKILL.md has security section" -Passed $hasSecurity -Message "Security section: $(if($hasSecurity){'found'}else{'not found'})" -Critical $false
}

$readmePath = Join-Path $SkillDir "README.md"
Add-Check -Name "README.md exists" -Passed (Test-Path $readmePath) -Message "README.md: $(if(Test-Path $readmePath){'exists'}else{'not found'})" -Critical $false

$changelogPath = Join-Path $SkillDir "CHANGELOG.md"
Add-Check -Name "CHANGELOG.md exists" -Passed (Test-Path $changelogPath) -Message "CHANGELOG.md: $(if(Test-Path $changelogPath){'exists'}else{'not found'})" -Critical $false

# ============================================
# 6. License Check
# ============================================
Write-Host "`n6. License Check" -ForegroundColor Yellow

$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "^LICENSE|^LICENCE|^license|^licence"
}

Add-Check -Name "License file exists" -Passed ($licenseFiles.Count -gt 0) -Message "License file: $(if($licenseFiles.Count -gt 0){'found'}else{'not found'})" -Critical $false

# ============================================
# Generate Report
# ============================================

$totalChecks = $results.checks.Count
$score = if ($totalChecks -gt 0) { [math]::Round(($results.passed / $totalChecks) * 100, 2) } else { 0 }

Write-Host "`n=== Audit Summary ===" -ForegroundColor Cyan
Write-Host "Total checks: $totalChecks"
Write-Host "Passed: $($results.passed)"
Write-Host "Failed: $($results.failed)"
Write-Host "Compliance score: $score%"

if ($results.critical_issues.Count -gt 0) {
    Write-Host "`n❌ Critical Issues (Must Fix):" -ForegroundColor Red
    foreach ($issue in $results.critical_issues) {
        Write-Host "  • $issue" -ForegroundColor Red
    }
}

if ($results.warnings.Count -gt 0) {
    Write-Host "`n⚠️  Warnings (Recommended to Fix):" -ForegroundColor Yellow
    foreach ($warning in $results.warnings) {
        Write-Host "  • $warning" -ForegroundColor Yellow
    }
}

# Generate JSON report
$reportFile = Join-Path $OutputDir "simple_audit_report.json"
$results | ConvertTo-Json -Depth 5 | Set-Content -Path $reportFile

Write-Host "`nReport saved to: $reportFile" -ForegroundColor Cyan

# Final recommendation
Write-Host "`n=== Final Recommendation ===" -ForegroundColor Cyan

if ($score -ge 95) {
    Write-Host "✅ Excellent! Ready for ClawHub publication." -ForegroundColor Green
} elseif ($score -ge 85) {
    Write-Host "⚠️  Good, but fix critical issues first." -ForegroundColor Yellow
} elseif ($score -ge 70) {
    Write-Host "❌ Needs improvement before publishing." -ForegroundColor Red
} else {
    Write-Host "🚫 Major improvements needed." -ForegroundColor DarkRed
}

Write-Host "`nAudit completed." -ForegroundColor White