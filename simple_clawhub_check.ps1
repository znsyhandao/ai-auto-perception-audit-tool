# Simple ClawHub Standards Check
# Based on 2026-03-24 install.bat lesson

param([string]$SkillDir = ".")

Write-Host "=== ClawHub Standards Check ===" -ForegroundColor Cyan
Write-Host "Directory: $SkillDir" -ForegroundColor Gray
Write-Host "Date: $(Get-Date)" -ForegroundColor Gray
Write-Host ""

# Check required files
Write-Host "1. Required Files Check:" -ForegroundColor Yellow

$requiredChecks = @(
    @{Name="skill.py"; Found=$false; Actual=""},
    @{Name="config.yaml"; Found=$false; Actual=""},
    @{Name="SKILL.md"; Found=$false; Actual=""},
    @{Name="package.json"; Found=$false; Actual=""}
)

foreach ($check in $requiredChecks) {
    $fileName = $check.Name
    
    # Check exact name
    if (Test-Path "$SkillDir\$fileName") {
        $check.Found = $true
        $check.Actual = $fileName
        Write-Host "  [OK] $fileName" -ForegroundColor Green
    } else {
        # Check alternatives
        $alternatives = @()
        if ($fileName -eq "skill.py") {
            $alternatives = @("skill_ascii_fixed.py", "main.py", "skill_fixed.py")
        } elseif ($fileName -eq "config.yaml") {
            $alternatives = @("config.yml")
        } elseif ($fileName -eq "SKILL.md") {
            $alternatives = @("README.md")
        }
        
        $foundAlt = $false
        foreach ($alt in $alternatives) {
            if (Test-Path "$SkillDir\$alt") {
                $check.Found = $true
                $check.Actual = $alt
                Write-Host "  [OK] $alt (alternative to $fileName)" -ForegroundColor Green
                $foundAlt = $true
                break
            }
        }
        
        if (-not $foundAlt) {
            Write-Host "  [FAIL] $fileName (missing)" -ForegroundColor Red
        }
    }
}

Write-Host ""

# Check prohibited files
Write-Host "2. Prohibited Files Check:" -ForegroundColor Yellow

$prohibitedPatterns = @("install.bat", "install.sh", "setup.py", "*.exe", "*.dll")
$foundProhibited = @()

foreach ($pattern in $prohibitedPatterns) {
    $files = Get-ChildItem -Path $SkillDir -Filter $pattern -Recurse -ErrorAction SilentlyContinue | 
             Where-Object { -not $_.PSIsContainer }
    
    if ($files) {
        foreach ($file in $files) {
            $relativePath = $file.FullName.Replace("$SkillDir\", "")
            Write-Host "  [FAIL] $relativePath (prohibited)" -ForegroundColor Red
            $foundProhibited += $relativePath
        }
    } else {
        Write-Host "  [OK] No $pattern" -ForegroundColor Green
    }
}

Write-Host ""

# Check file count
Write-Host "3. File Count Check:" -ForegroundColor Yellow
$fileCount = (Get-ChildItem -Path $SkillDir -File -Recurse | Measure-Object).Count
Write-Host "  Total files: $fileCount" -ForegroundColor White

if ($fileCount -gt 50) {
    Write-Host "  [WARN] Many files ($fileCount), consider simplifying" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Reasonable file count" -ForegroundColor Green
}

Write-Host ""

# Summary
Write-Host "=== SUMMARY ===" -ForegroundColor Cyan

$missingRequired = ($requiredChecks | Where-Object { -not $_.Found }).Count
$hasProhibited = $foundProhibited.Count -gt 0

if ($missingRequired -eq 0 -and -not $hasProhibited) {
    Write-Host "[PASS] All checks passed!" -ForegroundColor Green
    Write-Host "Ready for ClawHub submission." -ForegroundColor Green
} else {
    Write-Host "[FAIL] Issues found:" -ForegroundColor Red
    
    if ($missingRequired -gt 0) {
        Write-Host "  - Missing $missingRequired required files" -ForegroundColor Red
        foreach ($check in $requiredChecks | Where-Object { -not $_.Found }) {
            Write-Host "    * $($check.Name)" -ForegroundColor White
        }
    }
    
    if ($hasProhibited) {
        Write-Host "  - Found $($foundProhibited.Count) prohibited files" -ForegroundColor Red
        foreach ($file in $foundProhibited) {
            Write-Host "    * $file" -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "Fix these issues before submitting to ClawHub." -ForegroundColor Yellow
}

# List all files for reference
Write-Host ""
Write-Host "=== ALL FILES ===" -ForegroundColor Cyan
Get-ChildItem -Path $SkillDir -File -Recurse | 
    ForEach-Object { 
        $relativePath = $_.FullName.Replace("$SkillDir\", "")
        Write-Host "  $relativePath" -ForegroundColor Gray 
    }