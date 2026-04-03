# simple_audit_with_text_check.ps1
# Simple audit tool with text file format checks
# Based on 2026-03-30 LICENSE file lesson

param(
    [string]$SkillDir
)

Write-Host "=== Simple Audit with Text File Check ===" -ForegroundColor Cyan
Write-Host "Based on 2026-03-30 LICENSE file lesson" -ForegroundColor Cyan
Write-Host "Audit Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "Skill Directory: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# Check if directory exists
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] Skill directory not found: $SkillDir" -ForegroundColor Red
    exit 1
}

# Initialize results
$results = @{
    "checks" = @()
    "total" = 0
    "passed" = 0
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
    $results.total++
    
    if ($Passed) {
        $results.passed++
        Write-Host "  [PASS] $Name" -ForegroundColor Green
    } else {
        if ($Critical) {
            Write-Host "  [FAIL] $Name (Critical)" -ForegroundColor Red
            $results.critical_issues += $Message
        } else {
            Write-Host "  [WARN] $Name" -ForegroundColor Yellow
            $results.warnings += $Message
        }
    }
}

# ============================================
# 1. Basic File Structure
# ============================================
Write-Host "`n## 1. Basic File Structure" -ForegroundColor Yellow

$requiredFiles = @("SKILL.md", "README.md", "CHANGELOG.md", "config.yaml", "package.json", "skill.py")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    $exists = Test-Path $filePath
    
    Add-Check -Name "File: $file" -Passed $exists `
        -Message "$file $(if($exists){'exists'}else{'not found'})" -Critical $true
}

# ============================================
# 2. Version Consistency
# ============================================
Write-Host "`n## 2. Version Consistency" -ForegroundColor Yellow

$versions = @()
$versionFiles = @("config.yaml", "package.json", "SKILL.md")

foreach ($file in $versionFiles) {
    $filePath = Join-Path $SkillDir $file
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        
        if ($file -eq "config.yaml" -and $content -match 'version:\s*["'']?([0-9]+\.[0-9]+\.[0-9]+)["'']?') {
            $versions += $matches[1]
        }
        elseif ($file -eq "package.json" -and $content -match '"version"\s*:\s*["'']([0-9]+\.[0-9]+\.[0-9]+)["'']') {
            $versions += $matches[1]
        }
        elseif ($file -eq "SKILL.md" -and $content -match 'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)') {
            $versions += $matches[1]
        }
    }
}

if ($versions.Count -ge 2) {
    $firstVersion = $versions[0]
    $allSame = $true
    foreach ($v in $versions) {
        if ($v -ne $firstVersion) {
            $allSame = $false
            break
        }
    }
    
    Add-Check -Name "Version consistency" -Passed $allSame `
        -Message "Versions: $($versions -join ', ')" -Critical $true
} else {
    Add-Check -Name "Version consistency" -Passed $false `
        -Message "Could not extract versions" -Critical $true
}

# ============================================
# 3. Text File Format Check (NEW: Based on LICENSE lesson)
# ============================================
Write-Host "`n## 3. Text File Format Check" -ForegroundColor Yellow
Write-Host "Based on 2026-03-30 LICENSE file lesson" -ForegroundColor Cyan

# 3.1 Check all files have extensions
$allFiles = Get-ChildItem -Path $SkillDir -Recurse -File
$filesWithoutExtension = @()
foreach ($file in $allFiles) {
    if ([string]::IsNullOrEmpty($file.Extension)) {
        $filesWithoutExtension += $file.Name
    }
}

Add-Check -Name "All files have extensions" -Passed ($filesWithoutExtension.Count -eq 0) `
    -Message "Files without extension: $($filesWithoutExtension.Count)" -Critical $true

# 3.2 Check license file specifically
$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.BaseName -match "^LICENSE$|^LICENCE$|^license$|^licence$"
}

if ($licenseFiles.Count -gt 0) {
    $licenseFile = $licenseFiles[0]
    
    # Check license file extension
    $hasValidExtension = $licenseFile.Extension -in @(".txt", ".md")
    
    Add-Check -Name "License file has valid extension (.txt or .md)" -Passed $hasValidExtension `
        -Message "License file extension: $($licenseFile.Extension)" -Critical $true
    
    # Check for UTF-8 BOM
    try {
        $bytes = [System.IO.File]::ReadAllBytes($licenseFile.FullName)
        $hasBOM = $bytes.Count -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
        
        Add-Check -Name "License file encoding (no UTF-8 BOM)" -Passed (-not $hasBOM) `
            -Message "License file BOM: $(if($hasBOM){'has BOM'}else{'no BOM'})" -Critical $false
    } catch {
        # Ignore error
    }
} else {
    Add-Check -Name "License file exists" -Passed $false `
        -Message "No license file found" -Critical $false
}

# 3.3 Check for UTF-8 BOM in all text files
$textFiles = Get-ChildItem -Path $SkillDir -Recurse -File -Include *.md, *.txt, *.json, *.yaml, *.yml, *.py, *.js
$bomFiles = @()
foreach ($file in $textFiles) {
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        if ($bytes.Count -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $bomFiles += $file.Name
        }
    } catch {
        # Ignore error
    }
}

Add-Check -Name "No UTF-8 BOM in text files" -Passed ($bomFiles.Count -eq 0) `
    -Message "Files with UTF-8 BOM: $($bomFiles.Count)" -Critical $false

# ============================================
# 4. Security Check
# ============================================
Write-Host "`n## 4. Security Check" -ForegroundColor Yellow

$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    
    $hasSecuritySection = $configContent -match 'security:'
    $hasNetworkAccessFalse = $configContent -match 'network_access:\s*false'
    $hasLocalOnlyTrue = $configContent -match 'local_only:\s*true'
    
    Add-Check -Name "config.yaml security section" -Passed $hasSecuritySection `
        -Message "Security section: $(if($hasSecuritySection){'found'}else{'not found'})" -Critical $true
    
    Add-Check -Name "config.yaml network_access: false" -Passed $hasNetworkAccessFalse `
        -Message "network_access: false $(if($hasNetworkAccessFalse){'found'}else{'not found'})" -Critical $true
    
    Add-Check -Name "config.yaml local_only: true" -Passed $hasLocalOnlyTrue `
        -Message "local_only: true $(if($hasLocalOnlyTrue){'found'}else{'not found'})" -Critical $true
}

# ============================================
# 5. Package.json Check
# ============================================
Write-Host "`n## 5. Package.json Check" -ForegroundColor Yellow

$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        $hasName = ![string]::IsNullOrEmpty($packageJson.name)
        $hasDescription = ![string]::IsNullOrEmpty($packageJson.description)
        $hasAuthor = $null -ne $packageJson.author
        $hasLicense = ![string]::IsNullOrEmpty($packageJson.license)
        
        $metadataComplete = $hasName -and $hasDescription -and $hasAuthor -and $hasLicense
        
        Add-Check -Name "package.json metadata completeness" -Passed $metadataComplete `
            -Message "Name=$hasName, Description=$hasDescription, Author=$hasAuthor, License=$hasLicense" -Critical $true
    } catch {
        Add-Check -Name "package.json metadata completeness" -Passed $false `
            -Message "Cannot parse package.json" -Critical $true
    }
}

# ============================================
# Summary
# ============================================
Write-Host "`n=== Audit Summary ===" -ForegroundColor Cyan

$score = if ($results.total -gt 0) { [math]::Round(($results.passed / $results.total) * 100) } else { 0 }

Write-Host "Total Checks: $($results.total)" -ForegroundColor White
Write-Host "Passed Checks: $($results.passed)" -ForegroundColor Green
Write-Host "Overall Score: $score%" -ForegroundColor $(if ($score -ge 95) { "Green" } elseif ($score -ge 80) { "Yellow" } else { "Red" })
Write-Host "Critical Issues: $($results.critical_issues.Count)" -ForegroundColor $(if ($results.critical_issues.Count -eq 0) { "Green" } else { "Red" })

# Display critical issues
if ($results.critical_issues.Count -gt 0) {
    Write-Host "`n❌ Critical Issues (Must Fix):" -ForegroundColor Red
    foreach ($issue in $results.critical_issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

# Display warnings
if ($results.warnings.Count -gt 0) {
    Write-Host "`n⚠️  Warnings (Recommended to Fix):" -ForegroundColor Yellow
    foreach ($issue in $results.warnings) {
        Write-Host "  - $issue" -ForegroundColor Yellow
    }
}

# Final recommendation
if ($score -ge 95 -and $results.critical_issues.Count -eq 0) {
    Write-Host "`n✅ RECOMMENDATION: Ready for ClawHub submission!" -ForegroundColor Green
    Write-Host "   Expected ClawHub result: Clean (high confidence)" -ForegroundColor Green
} elseif ($score -ge 80) {
    Write-Host "`n⚠️  RECOMMENDATION: Needs improvement before submission" -ForegroundColor Yellow
    Write-Host "   Fix critical issues first" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ RECOMMENDATION: Not ready for ClawHub" -ForegroundColor Red
    Write-Host "   Major improvements needed" -ForegroundColor Red
}

# Save report
$reportFile = Join-Path $SkillDir "simple_audit_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`nReport saved to: $reportFile" -ForegroundColor Cyan
Write-Host "=== Audit Complete ===" -ForegroundColor Cyan