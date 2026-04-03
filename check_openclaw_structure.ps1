# OpenClaw Skill Structure Validation Tool
# Based on 2026-03-24 AISkinX lesson: Validate skill files follow OpenClaw specification

param(
    [string]$SkillDir = ".",
    [switch]$Verbose = $false
)

function Write-Info {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "[INFO] $Message" -ForegroundColor Gray
    }
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Main function
function Main {
    Write-Host "=== OpenClaw Skill Structure Validation ===" -ForegroundColor Cyan
    Write-Host "Version: 1.0.0 (Based on 2026-03-24 AISkinX lesson)" -ForegroundColor Gray
    Write-Host "Directory: $SkillDir" -ForegroundColor Gray
    Write-Host "Goal: Validate skill files follow OpenClaw specification" -ForegroundColor Yellow
    Write-Host "=" * 60
    
    if (-not (Test-Path $SkillDir)) {
        Write-Error "Directory does not exist: $SkillDir"
        exit 1
    }
    
    # Find skill files (usually named skill.py or containing skill)
    $skillFiles = Get-ChildItem $SkillDir -Filter "*skill*.py" -Recurse -ErrorAction SilentlyContinue
    
    if ($skillFiles.Count -eq 0) {
        Write-Warning "No skill files found (*skill*.py)"
        Write-Info "Trying to find other Python main files..."
        $skillFiles = Get-ChildItem $SkillDir -Filter "*.py" -Recurse | Where-Object {
            $_.Name -notmatch "test|check|verify|validator|utils"
        } | Select-Object -First 3
    }
    
    if ($skillFiles.Count -eq 0) {
        Write-Error "No Python main files found"
        exit 1
    }
    
    Write-Info "Found $($skillFiles.Count) files to check"
    
    $allPassed = $true
    $results = @()
    
    foreach ($file in $skillFiles) {
        Write-Host "`nChecking file: $($file.Name)" -ForegroundColor White
        
        $result = Check-OpenClaw-Skill-Structure $file.FullName $file.Name
        $results += $result
        
        if (-not $result.Passed) {
            $allPassed = $false
        }
    }
    
    # Output summary
    Write-Summary $results $allPassed
}

# Check OpenClaw skill structure
function Check-OpenClaw-Skill-Structure {
    param($FilePath, $FileName)
    
    if (-not (Test-Path $FilePath)) {
        Write-Error "File does not exist: $FilePath"
        return @{FileName=$FileName; Passed=$false; Issues=@("File does not exist")}
    }
    
    try {
        $content = Get-Content $FilePath -Raw -Encoding UTF8
        $lines = $content -split "`n"
        
        Write-Info "File size: $($content.Length) characters, $($lines.Count) lines"
        
        # Check required structure elements
        $checks = @(
            # Core structure (required)
            @{Pattern="class.*Skill\b"; Description="Skill class definition"; Required=$true; Score=30},
            @{Pattern="def handle\("; Description="handle method"; Required=$true; Score=25},
            @{Pattern="def setup\("; Description="setup method"; Required=$true; Score=25},
            @{Pattern="create_skill"; Description="create_skill function"; Required=$true; Score=20},
            
            # Good practices (recommended)
            @{Pattern="from typing import|import typing"; Description="Type hints"; Required=$false; Score=5},
            @{Pattern="__init__"; Description="Initialization method"; Required=$false; Score=5},
            @{Pattern="self\.name\s*="; Description="Skill name property"; Required=$false; Score=5},
            @{Pattern="self\.version\s*="; Description="Version property"; Required=$false; Score=5},
            @{Pattern="self\.description\s*="; Description="Description property"; Required=$false; Score=5}
        )
        
        $issues = @()
        $score = 0
        $maxScore = 0
        
        foreach ($check in $checks) {
            $maxScore += $check.Score
            
            if ($content -match $check.Pattern) {
                $score += $check.Score
                Write-Success "$($check.Description)"
            } elseif ($check.Required) {
                Write-Error "Missing $($check.Description)"
                $issues += "Missing $($check.Description)"
            } else {
                Write-Warning "No $($check.Description) (optional)"
            }
        }
        
        # Calculate pass rate
        $passRate = if ($maxScore -gt 0) { [math]::Round(($score / $maxScore) * 100, 1) } else { 0 }
        
        # Additional check: file beginning
        Write-Info "`nFile beginning check:" -ForegroundColor White
        $firstLines = $lines[0..[math]::Min(10, $lines.Count - 1)] -join "`n"
        
        if ($firstLines -match "^#!/usr/bin/env python3") {
            Write-Success "Has Python shebang"
        } else {
            Write-Warning "No Python shebang (optional)"
        }
        
        if ($firstLines -match '"""|"""') {
            Write-Success "Has docstring"
        } else {
            Write-Warning "No docstring (optional)"
        }
        
        # Determine if passed
        $passed = ($issues.Count -eq 0) -and ($passRate -ge 80)
        
        Write-Host "`n=== $FileName Check Results ===" -ForegroundColor Cyan
        Write-Host "  Structure score: $score/$maxScore ($passRate%)" -ForegroundColor $(if ($passRate -ge 80) { "Green" } else { "Red" })
        Write-Host "  Issues count: $($issues.Count)" -ForegroundColor $(if ($issues.Count -eq 0) { "Green" } else { "Red" })
        Write-Host "  Pass status: $(if ($passed) { '[OK] Passed' } else { '[ERROR] Failed' })" -ForegroundColor $(if ($passed) { "Green" } else { "Red" })
        
        return @{
            FileName = $FileName
            Passed = $passed
            Score = $score
            MaxScore = $maxScore
            PassRate = $passRate
            Issues = $issues
        }
        
    } catch {
        Write-Error "Failed to check file: $FileName, Error: $_"
        return @{FileName=$FileName; Passed=$false; Issues=@("Check failed: $_")}
    }
}

# Output summary
function Write-Summary {
    param($Results, $AllPassed)
    
    Write-Host "`n=== Skill Structure Validation Summary ===" -ForegroundColor Cyan
    Write-Host "=" * 60
    
    $totalFiles = $Results.Count
    $passedFiles = ($Results | Where-Object { $_.Passed }).Count
    $failedFiles = $totalFiles - $passedFiles
    
    Write-Host "Files checked: $totalFiles" -ForegroundColor White
    Write-Host "Files passed: $passedFiles" -ForegroundColor $(if ($passedFiles -eq $totalFiles) { "Green" } else { "White" })
    Write-Host "Files failed: $failedFiles" -ForegroundColor $(if ($failedFiles -eq 0) { "Green" } else { "Red" })
    
    # Show detailed results
    foreach ($result in $Results) {
        $status = if ($result.Passed) { "[OK]" } else { "[ERROR]" }
        Write-Host "`n$status $($result.FileName): $($result.PassRate)%" -ForegroundColor $(if ($result.Passed) { "Green" } else { "Red" })
        
        if ($result.Issues.Count -gt 0) {
            Write-Host "  Issues:" -ForegroundColor Yellow
            foreach ($issue in $result.Issues) {
                Write-Host "    - $issue" -ForegroundColor White
            }
        }
    }
    
    if ($AllPassed) {
        Write-Host "`n[SUCCESS] All skill files follow OpenClaw specification!" -ForegroundColor Green
        Write-Host "   Skill structure complete, can run normally in OpenClaw" -ForegroundColor Green
    } else {
        Write-Host "`n[ERROR] Some skill files do not follow OpenClaw specification" -ForegroundColor Red
        
        Write-Host "`n[SUGGESTION] Fix recommendations:" -ForegroundColor Cyan
        Write-Host "  1. Ensure there is class *Skill definition" -ForegroundColor White
        Write-Host "  2. Add def handle() method to process commands" -ForegroundColor White
        Write-Host "  3. Add def setup() method for setup" -ForegroundColor White
        Write-Host "  4. Add create_skill() function to create instance" -ForegroundColor White
        Write-Host "  5. Refactor code following OpenClaw skill template" -ForegroundColor White
        
        Write-Host "`n[NOTE] OpenClaw skill template key points:" -ForegroundColor Yellow
        Write-Host "  class MySkill:" -ForegroundColor Gray
        Write-Host "      def __init__(self):" -ForegroundColor Gray
        Write-Host "          self.name = 'skill-name'" -ForegroundColor Gray
        Write-Host "          self.version = '1.0.0'" -ForegroundColor Gray
        Write-Host "      " -ForegroundColor Gray
        Write-Host "      def setup(self, context):" -ForegroundColor Gray
        Write-Host "          pass" -ForegroundColor Gray
        Write-Host "      " -ForegroundColor Gray
        Write-Host "      def handle(self, command, args, context):" -ForegroundColor Gray
        Write-Host "          pass" -ForegroundColor Gray
        Write-Host "  " -ForegroundColor Gray
        Write-Host "  def create_skill():" -ForegroundColor Gray
        Write-Host "      return MySkill()" -ForegroundColor Gray
    }
}

# Run main function
Main