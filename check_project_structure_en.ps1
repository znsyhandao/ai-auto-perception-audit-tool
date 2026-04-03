# check_project_structure_en.ps1
# Check if project structure meets standardization requirements
# Based on 2026-03-27 AISleepGen project structure chaos lesson

param(
    [string]$ProjectDir,
    [string]$SkillName = "openclaw_skill"
)

Write-Host "=== Project Structure Check ===" -ForegroundColor Cyan
Write-Host "Check Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Project Directory: $ProjectDir"
Write-Host "Skill Name: $SkillName"
Write-Host ""

# Check 1: Does project directory exist?
if (-not (Test-Path $ProjectDir)) {
    Write-Host "[ERROR] Project directory does not exist: $ProjectDir" -ForegroundColor Red
    exit 1
}

# Check 2: Does skill directory exist?
$skillDir = Join-Path $ProjectDir $SkillName
if (-not (Test-Path $skillDir)) {
    Write-Host "[WARNING] Skill directory does not exist: $skillDir" -ForegroundColor Yellow
    Write-Host "  Suggestion: Create standardized skill directory structure"
}

# Check 3: Number of folders in project root
$rootFolders = Get-ChildItem -Path $ProjectDir -Directory | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "Check 3: Number of folders in project root" -ForegroundColor White
Write-Host "  Found: $rootFolders folders"
if ($rootFolders -gt 20) {
    Write-Host "  [WARNING] Too many folders ($rootFolders > 20)" -ForegroundColor Yellow
    Write-Host "  Suggestion: Organize project structure, reduce unnecessary folders"
} else {
    Write-Host "  [OK] Reasonable number of folders" -ForegroundColor Green
}

# Check 4: Required files check
Write-Host "`nCheck 4: Skill required files" -ForegroundColor White
$requiredFiles = @(
    "skill.py",
    "config.yaml", 
    "SKILL.md",
    "package.json"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $skillDir $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

# Check 5: Prohibited files check
Write-Host "`nCheck 5: Prohibited files check" -ForegroundColor White
$prohibitedExtensions = @(".ps1", ".bat", ".exe", ".dll", ".backup", ".pyc")
$prohibitedFiles = Get-ChildItem -Path $skillDir -File | Where-Object {
    $prohibitedExtensions -contains $_.Extension
}

if ($prohibitedFiles.Count -gt 0) {
    Write-Host "  [WARNING] Found prohibited files ($($prohibitedFiles.Count) files)" -ForegroundColor Yellow
    foreach ($file in $prohibitedFiles) {
        Write-Host "    - $($file.Name)" -ForegroundColor Yellow
    }
    Write-Host "  Suggestion: Remove these files before release"
} else {
    Write-Host "  [OK] No prohibited files" -ForegroundColor Green
}

# Check 6: Release folder structure check
Write-Host "`nCheck 6: Release folder structure" -ForegroundColor White
$releasesDir = "D:\openclaw\releases"
if (Test-Path $releasesDir) {
    $projectName = Split-Path $ProjectDir -Leaf
    $releaseFolders = Get-ChildItem -Path $releasesDir -Directory | Where-Object { $_.Name -like "*$projectName*" }
    
    if ($releaseFolders.Count -gt 0) {
        Write-Host "  [OK] Found release folders ($($releaseFolders.Count) folders)" -ForegroundColor Green
        foreach ($folder in $releaseFolders) {
            Write-Host "    - $($folder.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "  [WARNING] No release folders found" -ForegroundColor Yellow
        Write-Host "  Suggestion: Create standard release folder in $releasesDir"
    }
} else {
    Write-Host "  [WARNING] Release folder does not exist: $releasesDir" -ForegroundColor Yellow
    Write-Host "  Suggestion: Create standard release folder structure"
}

# Summary report
Write-Host "`n=== Check Summary ===" -ForegroundColor Cyan

$issues = @()
if ($rootFolders -gt 20) { $issues += "Too many folders" }
if ($missingFiles.Count -gt 0) { $issues += "Missing required files: $($missingFiles -join ', ')" }
if ($prohibitedFiles.Count -gt 0) { $issues += "Prohibited files found" }

if ($issues.Count -eq 0) {
    Write-Host "[PASS] Project structure is good" -ForegroundColor Green
} else {
    Write-Host "[NEEDS IMPROVEMENT] Found $($issues.Count) issues" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Yellow
    }
    
    Write-Host "`nImprovement Suggestions:" -ForegroundColor White
    Write-Host "1. Organize project structure, reduce unnecessary folders"
    Write-Host "2. Ensure all required files exist"
    Write-Host "3. Remove prohibited files before release"
    Write-Host "4. Use standardized release folder: $releasesDir"
}

# Generate improvement suggestions file
$suggestionsFile = Join-Path $ProjectDir "project_structure_suggestions.md"
$suggestions = @"
# Project Structure Improvement Suggestions
## Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
## Project: $ProjectDir

## Issues Found
$($issues -join "`n")

## Specific Improvement Measures

### 1. Organize Folder Structure
- Current folder count: $rootFolders (Recommended: < 20)
- Suggest merging related function folders
- Remove temporary files and cache directories

### 2. Complete Skill Files
$($missingFiles | ForEach-Object { "- Create missing file: $_" })

### 3. Clean Prohibited Files
$($prohibitedFiles | ForEach-Object { "- Remove: $($_.Name)" })

### 4. Establish Release Process
- Create release folder: $releasesDir\$((Split-Path $ProjectDir -Leaf))_vVersion
- Create standardized release package
- Establish automated release scripts

### 5. Based on AISkinX Experience
- Apply four principles: Specific, Verifiable, Automated, Documented
- Create permanent improvement records
- Establish automated check tools

## Reference Documents
- [PROJECT_STRUCTURE_LESSON.md](D:\OpenClaw_TestingFramework\PROJECT_STRUCTURE_LESSON.md)
- [TESTING_FRAMEWORK.md](D:\OpenClaw_TestingFramework\TESTING_FRAMEWORK.md)
"@

Set-Content -Path $suggestionsFile -Value $suggestions
Write-Host "`nImprovement suggestions saved to: $suggestionsFile" -ForegroundColor Cyan