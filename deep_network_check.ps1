# Deep Network Code Check Tool
# Based on 2026-03-24 AISkinX lesson: Check hidden network code in comments and strings

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
    Write-Host "=== Deep Network Code Check ===" -ForegroundColor Cyan
    Write-Host "Version: 1.0.0 (Based on 2026-03-24 AISkinX lesson)" -ForegroundColor Gray
    Write-Host "Directory: $SkillDir" -ForegroundColor Gray
    Write-Host "Goal: Check all locations for network code (including comments and strings)" -ForegroundColor Yellow
    Write-Host "=" * 60
    
    if (-not (Test-Path $SkillDir)) {
        Write-Error "Directory does not exist: $SkillDir"
        exit 1
    }
    
    # Find all Python files
    $pythonFiles = Get-ChildItem $SkillDir -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
    
    if ($pythonFiles.Count -eq 0) {
        Write-Warning "No Python files found"
        return
    }
    
    Write-Info "Found $($pythonFiles.Count) Python files"
    
    $totalIssues = 0
    $filesWithIssues = @()
    
    foreach ($file in $pythonFiles) {
        Write-Info "Checking file: $($file.Name)"
        
        try {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8
            $issues = Check-File-For-Network-Code $file.Name $content
            
            if ($issues.Count -gt 0) {
                $totalIssues += $issues.Count
                $filesWithIssues += $file.Name
                
                Write-Error "$($file.Name) found $($issues.Count) network code issues"
                
                foreach ($issue in $issues) {
                    Write-Host "  [ERROR] $($issue.Pattern)" -ForegroundColor Red
                    Write-Host "      Location: Line $($issue.Line), Column $($issue.Column)" -ForegroundColor Gray
                    Write-Host "      Context: $($issue.Context)" -ForegroundColor Gray
                }
            } else {
                Write-Success "$($file.Name) no network code"
            }
            
        } catch {
            Write-Error "Failed to check file: $($file.Name), Error: $_"
        }
    }
    
    # Output summary
    Write-Summary $totalIssues $filesWithIssues $pythonFiles.Count
}

# Check file for network code
function Check-File-For-Network-Code {
    param($FileName, $Content)
    
    $issues = @()
    
    # Network code patterns (including in comments and strings)
    $networkPatterns = @(
        # URL patterns
        @{Pattern="http://"; Description="HTTP URL"},
        @{Pattern="https://"; Description="HTTPS URL"},
        @{Pattern="www\."; Description="Website address"},
        @{Pattern="\.com\b"; Description=".com domain"},
        @{Pattern="\.org\b"; Description=".org domain"},
        @{Pattern="\.net\b"; Description=".net domain"},
        
        # Network library imports
        @{Pattern="import requests"; Description="requests library import"},
        @{Pattern="import urllib"; Description="urllib library import"},
        @{Pattern="import socket"; Description="socket library import"},
        @{Pattern="import http\.client"; Description="http.client library import"},
        @{Pattern="import grpc"; Description="gRPC library import"},
        @{Pattern="import websockets"; Description="WebSockets library import"}
    )
    
    # Check line by line for better location
    $lines = $Content -split "`n"
    
    for ($lineNum = 0; $lineNum -lt $lines.Count; $lineNum++) {
        $line = $lines[$lineNum]
        
        foreach ($patternInfo in $networkPatterns) {
            $pattern = $patternInfo.Pattern
            $description = $patternInfo.Description
            
            if ($line -match $pattern) {
                # Found match, record details
                $match = [regex]::Match($line, $pattern)
                
                $issue = @{
                    Pattern = $description
                    Line = $lineNum + 1
                    Column = $match.Index + 1
                    Context = Get-Context $lines $lineNum $match.Index $match.Length
                    FullLine = $line.Trim()
                }
                
                $issues += $issue
            }
        }
    }
    
    return $issues
}

# Get context
function Get-Context {
    param($Lines, $LineNum, $MatchIndex, $MatchLength)
    
    $currentLine = $Lines[$LineNum]
    
    # Get text before and after match in current line
    $start = [Math]::Max(0, $MatchIndex - 20)
    $end = [Math]::Min($currentLine.Length, $MatchIndex + $MatchLength + 20)
    
    $before = if ($start -gt 0) { "..." } else { "" }
    $after = if ($end -lt $currentLine.Length) { "..." } else { "" }
    
    $contextText = $currentLine.Substring($start, $end - $start)
    
    return "${before}${contextText}${after}"
}

# Output summary
function Write-Summary {
    param($TotalIssues, $FilesWithIssues, $TotalFiles)
    
    Write-Host "`n=== Check Results Summary ===" -ForegroundColor Cyan
    Write-Host "=" * 60
    
    Write-Host "Files checked: $TotalFiles" -ForegroundColor White
    Write-Host "Issues found: $TotalIssues" -ForegroundColor $(if ($TotalIssues -eq 0) { "Green" } else { "Red" })
    Write-Host "Files with issues: $($FilesWithIssues.Count)" -ForegroundColor $(if ($FilesWithIssues.Count -eq 0) { "Green" } else { "Red" })
    
    if ($TotalIssues -eq 0) {
        Write-Host "`n[SUCCESS] All files passed deep network code check!" -ForegroundColor Green
        Write-Host "   No hidden network code (including in comments and strings)" -ForegroundColor Green
    } else {
        Write-Host "`n[ERROR] Found network code issues:" -ForegroundColor Red
        
        if ($FilesWithIssues.Count -gt 0) {
            Write-Host "Files with issues:" -ForegroundColor Yellow
            foreach ($file in $FilesWithIssues) {
                Write-Host "  - $file" -ForegroundColor White
            }
        }
        
        Write-Host "`n[SUGGESTION] Fix recommendations:" -ForegroundColor Cyan
        Write-Host "  1. Check example URLs in comments and remove" -ForegroundColor White
        Write-Host "  2. Check network addresses in string constants" -ForegroundColor White
        Write-Host "  3. Check network references in test code" -ForegroundColor White
        Write-Host "  4. Ensure all network library imports are removed" -ForegroundColor White
        Write-Host "  5. Re-run check until all issues fixed" -ForegroundColor White
    }
}

# Run main function
Main