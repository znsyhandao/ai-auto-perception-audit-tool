# File Encoding Check Script
# Based on 2026-03-24 AISkinX documentation encoding lesson

param(
    [string]$SkillDir = ".",
    [switch]$Fix = $false,
    [switch]$Verbose = $false
)

function Write-Info {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "鈩癸笍  $Message" -ForegroundColor Gray
    }
}

function Write-Success {
    param([string]$Message)
    Write-Host "鉁?$Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "鈿狅笍  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "鉂?$Message" -ForegroundColor Red
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
    Write-Host "馃攳 $Title" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

# Main function
function Main {
    Write-Host "馃殌 File Encoding Check" -ForegroundColor Cyan
    Write-Host "Version: 1.0.0 (Based on 2026-03-24 AISkinX lesson)" -ForegroundColor Gray
    Write-Host "Directory: $SkillDir" -ForegroundColor Gray
    Write-Host "Fix mode: $Fix" -ForegroundColor Gray
    
    # Check directory exists
    if (-not (Test-Path $SkillDir)) {
        Write-Error "Directory does not exist: $SkillDir"
        exit 1
    }
    
    # Run all checks
    $results = @{
        DocumentFiles = Check-DocumentFiles
        CriticalFiles = Check-CriticalFiles
        PythonFiles = Check-PythonFiles
        ConfigurationFiles = Check-ConfigurationFiles
        AsciiSafety = Check-AsciiSafety
    }
    
    # Output summary
    Write-Summary $results
    
    # Apply fixes if needed
    if ($Fix) {
        Apply-Fixes $results
    }
}

# Check document files encoding
function Check-DocumentFiles {
    Write-Section "Document Files Encoding Check"
    
    $documentExtensions = @('.md', '.txt', '.rst', '.adoc')
    $documentFiles = Get-ChildItem $SkillDir -Include $documentExtensions -Recurse -ErrorAction SilentlyContinue
    
    if ($documentFiles.Count -eq 0) {
        Write-Warning "No document files found"
        return @{Passed = $true; Files = @(); Issues = @()}
    }
    
    Write-Info "Found $($documentFiles.Count) document files"
    
    $encodingIssues = @()
    $validFiles = @()
    
    foreach ($file in $documentFiles) {
        $filePath = $file.FullName
        $fileName = $file.Name
        
        try {
            # Try to read with UTF-8
            $null = Get-Content $filePath -Encoding UTF8 -ErrorAction Stop
            Write-Success "${fileName}: UTF-8 encoding OK"
            $validFiles += $fileName
        } catch [System.Text.DecoderFallbackException] {
            Write-Error "${fileName}: Not UTF-8 encoding"
            $encodingIssues += @{
                File = $fileName
                Path = $filePath
                Issue = "Not UTF-8 encoding"
            }
        } catch {
            Write-Error "${fileName}: Encoding error - $_"
            $encodingIssues += @{
                File = $fileName
                Path = $filePath
                Issue = "Encoding error: $_"
            }
        }
    }
    
    return @{
        Passed = ($encodingIssues.Count -eq 0)
        Files = $validFiles
        Issues = $encodingIssues
        TotalFiles = $documentFiles.Count
    }
}

# Check critical files
function Check-CriticalFiles {
    Write-Section "Critical Files Check"
    
    $criticalFiles = @(
        @{Name = "SKILL.md"; Description = "Skill documentation"},
        @{Name = "README.md"; Description = "Project readme"},
        @{Name = "CHANGELOG.md"; Description = "Change log"},
        @{Name = "config.yaml"; Description = "Configuration file"},
        @{Name = "package.json"; Description = "Package configuration"}
    )
    
    $missingFiles = @()
    $encodingIssues = @()
    $foundFiles = @()
    
    foreach ($file in $criticalFiles) {
        $fileName = $file.Name
        $description = $file.Description
        $filePath = Join-Path $SkillDir $fileName
        
        if (Test-Path $filePath) {
            try {
                # Try to read with UTF-8
                $null = Get-Content $filePath -Encoding UTF8 -ErrorAction Stop
                Write-Success "${description}: $fileName (UTF-8 OK)"
                $foundFiles += $fileName
            } catch {
                Write-Error "${description}: $fileName (Encoding issue)"
                $encodingIssues += @{
                    File = $fileName
                    Description = $description
                    Issue = "Encoding error"
                }
            }
        } else {
            Write-Warning "${description}: $fileName (Missing)"
            $missingFiles += @{
                File = $fileName
                Description = $description
            }
        }
    }
    
    return @{
        Passed = ($missingFiles.Count -eq 0 -and $encodingIssues.Count -eq 0)
        Missing = $missingFiles
        EncodingIssues = $encodingIssues
        Found = $foundFiles
    }
}

# Check Python files encoding
function Check-PythonFiles {
    Write-Section "Python Files Encoding Check"
    
    $pythonFiles = Get-ChildItem $SkillDir -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
    
    if ($pythonFiles.Count -eq 0) {
        Write-Warning "No Python files found"
        return @{Passed = $true; Files = @(); Issues = @()}
    }
    
    Write-Info "Found $($pythonFiles.Count) Python files"
    
    $encodingIssues = @()
    $validFiles = @()
    
    foreach ($file in $pythonFiles) {
        $filePath = $file.FullName
        $fileName = $file.Name
        
        try {
            # Python files should be UTF-8 or ASCII
            $content = Get-Content $filePath -Raw -Encoding UTF8 -ErrorAction Stop
            
            # Check for encoding declaration
            if ($content -match '^#.*coding[:=]\s*([-\w.]+)') {
                $declaredEncoding = $matches[1]
                Write-Info "${fileName}: Encoding declared as $declaredEncoding"
            }
            
            Write-Success "${fileName}: UTF-8 encoding OK"
            $validFiles += $fileName
            
        } catch {
            Write-Error "${fileName}: Encoding error - $_"
            $encodingIssues += @{
                File = $fileName
                Path = $filePath
                Issue = "Encoding error: $_"
            }
        }
    }
    
    return @{
        Passed = ($encodingIssues.Count -eq 0)
        Files = $validFiles
        Issues = $encodingIssues
        TotalFiles = $pythonFiles.Count
    }
}

# Check configuration files
function Check-ConfigurationFiles {
    Write-Section "Configuration Files Check"
    
    $configExtensions = @('.yaml', '.yml', '.json', '.toml', '.ini')
    $configFiles = Get-ChildItem $SkillDir -Include $configExtensions -Recurse -ErrorAction SilentlyContinue
    
    if ($configFiles.Count -eq 0) {
        Write-Info "No configuration files found"
        return @{Passed = $true; Files = @(); Issues = @()}
    }
    
    Write-Info "Found $($configFiles.Count) configuration files"
    
    $encodingIssues = @()
    $validFiles = @()
    
    foreach ($file in $configFiles) {
        $filePath = $file.FullName
        $fileName = $file.Name
        
        try {
            # Configuration files should be UTF-8
            $null = Get-Content $filePath -Encoding UTF8 -ErrorAction Stop
            
            # Additional check for JSON files
            if ($file.Extension -eq '.json') {
                $content = Get-Content $filePath -Raw -Encoding UTF8
                $null = $content | ConvertFrom-Json -ErrorAction Stop
                Write-Success "${fileName}: Valid JSON (UTF-8)"
            } else {
                Write-Success "${fileName}: UTF-8 encoding OK"
            }
            
            $validFiles += $fileName
            
        } catch {
            Write-Error "${fileName}: Encoding/format error - $_"
            $encodingIssues += @{
                File = $fileName
                Path = $filePath
                Issue = "Encoding/format error: $_"
            }
        }
    }
    
    return @{
        Passed = ($encodingIssues.Count -eq 0)
        Files = $validFiles
        Issues = $encodingIssues
        TotalFiles = $configFiles.Count
    }
}

# Check ASCII safety for critical files
function Check-AsciiSafety {
    Write-Section "ASCII Safety Check"
    
    $criticalFiles = @("CHANGELOG.md", "README.md", "SKILL.md")
    $asciiIssues = @()
    $safeFiles = @()
    
    foreach ($fileName in $criticalFiles) {
        $filePath = Join-Path $SkillDir $fileName
        
        if (-not (Test-Path $filePath)) {
            Write-Info "${fileName}: Not found (skipping ASCII check)"
            continue
        }
        
        try {
            $content = Get-Content $filePath -Raw -Encoding UTF8
            
            # Check if content is ASCII-safe
            $isAsciiSafe = $content -match '^[\x00-\x7F]*$'
            
            if ($isAsciiSafe) {
                Write-Success "${fileName}: ASCII-safe"
                $safeFiles += $fileName
            } else {
                $nonAsciiCount = ($content.ToCharArray() | Where-Object { [int]$_ -gt 127 }).Count
                Write-Warning "$fileName: Contains $nonAsciiCount non-ASCII characters"
                $asciiIssues += @{
                    File = $fileName
                    NonAsciiCount = $nonAsciiCount
                }
            }
            
        } catch {
            Write-Error "${fileName}: Failed to check ASCII safety - $_"
            $asciiIssues += @{
                File = $fileName
                Issue = "Check failed: $_"
            }
        }
    }
    
    # Recommendation based on findings
    if ($asciiIssues.Count -gt 0) {
        Write-Host "`n馃挕 Recommendation:" -ForegroundColor Cyan
        Write-Host "  Consider using English ASCII for CHANGELOG.md to avoid encoding issues" -ForegroundColor White
        Write-Host "  This ensures compatibility across all platforms and terminals" -ForegroundColor White
    }
    
    return @{
        Passed = ($asciiIssues.Count -eq 0)
        SafeFiles = $safeFiles
        Issues = $asciiIssues
        CriticalFileCount = $criticalFiles.Count
    }
}

# Output summary
function Write-Summary {
    param($results)
    
    Write-Section "Encoding Check Results Summary"
    
    $totalChecks = $results.Count
    $passedChecks = ($results.Values | Where-Object { $_.Passed }).Count
    
    Write-Host "馃搳 Check Statistics:" -ForegroundColor Cyan
    Write-Host "  Total checks: $totalChecks" -ForegroundColor White
    Write-Host "  Passed: $passedChecks" -ForegroundColor Green
    Write-Host "  Failed: $($totalChecks - $passedChecks)" -ForegroundColor Red
    
    # Detailed results
    foreach ($key in $results.Keys) {
        $result = $results[$key]
        $status = if ($result.Passed) { "鉁? } else { "鉂? }
        Write-Host "  $status $key" -ForegroundColor $(if ($result.Passed) { "Green" } else { "Red" })
    }
    
    # Count total issues
    $totalIssues = 0
    foreach ($result in $results.Values) {
        if ($result.Issues) {
            $totalIssues += $result.Issues.Count
        }
        if ($result.Missing) {
            $totalIssues += $result.Missing.Count
        }
        if ($result.EncodingIssues) {
            $totalIssues += $result.EncodingIssues.Count
        }
    }
    
    if ($totalIssues -eq 0) {
        Write-Host "`n馃帀 All encoding checks passed!" -ForegroundColor Green
        Write-Host "All files use proper UTF-8 encoding." -ForegroundColor Green
    } else {
        Write-Host "`n鈿狅笍  Encoding issues found ($totalIssues total):" -ForegroundColor Yellow
        
        # Show specific issues
        foreach ($key in $results.Keys) {
            $result = $results[$key]
            
            if ($result.Missing -and $result.Missing.Count -gt 0) {
                Write-Host "  Missing files ($key):" -ForegroundColor Yellow
                foreach ($missing in $result.Missing) {
                    Write-Host "    - $($missing.File) ($($missing.Description))" -ForegroundColor White
                }
            }
            
            if ($result.Issues -and $result.Issues.Count -gt 0) {
                Write-Host "  Encoding issues ($key):" -ForegroundColor Yellow
                foreach ($issue in $result.Issues) {
                    Write-Host "    - $($issue.File): $($issue.Issue)" -ForegroundColor White
                }
            }
            
            if ($result.EncodingIssues -and $result.EncodingIssues.Count -gt 0) {
                Write-Host "  Critical file issues ($key):" -ForegroundColor Yellow
                foreach ($issue in $result.EncodingIssues) {
                    Write-Host "    - $($issue.File) ($($issue.Description)): $($issue.Issue)" -ForegroundColor White
                }
            }
        }
        
        Write-Host "`n馃挕 Fix suggestions:" -ForegroundColor Cyan
        Write-Host "  1. Run with -Fix parameter to attempt automatic encoding fixes" -ForegroundColor White
        Write-Host "  2. Convert non-UTF-8 files to UTF-8 encoding" -ForegroundColor White
        Write-Host "  3. Consider using English ASCII for critical files (CHANGELOG.md)" -ForegroundColor White
        Write-Host "  4. Ensure all new files are saved as UTF-8" -ForegroundColor White
    }
}

# Apply fixes
function Apply-Fixes {
    param($results)
    
    Write-Section "Applying Encoding Fixes"
    
    $fixedCount = 0
    
    # Fix document files
    $docResult = $results.DocumentFiles
    if (-not $docResult.Passed -and $docResult.Issues) {
        Write-Host "馃敡 Fixing document files..." -ForegroundColor Yellow
        
        foreach ($issue in $docResult.Issues) {
            $filePath = $issue.Path
            $fileName = $issue.File
            
            try {
                # Read file with default encoding and save as UTF-8
                $content = Get-Content $filePath -Raw
                $content | Out-File -FilePath $filePath -Encoding UTF8 -Force
                Write-Success "Fixed encoding for: $fileName"
                $fixedCount++
            } catch {
                Write-Error "Failed to fix encoding for $fileName: $_"
            }
        }
    }
    
    # Fix critical files
    $criticalResult = $results.CriticalFiles
    if (-not $criticalResult.Passed -and $criticalResult.EncodingIssues) {
        Write-Host "馃敡 Fixing critical files..." -ForegroundColor Yellow
        
        foreach ($issue in $criticalResult.EncodingIssues) {
            $filePath = Join-Path $SkillDir $issue.File
            
            if (Test-Path $filePath) {
                try {
                    $content = Get-Content $filePath -Raw
                    $content | Out-File -FilePath $filePath -Encoding UTF8 -Force
                    Write-Success "Fixed encoding for: $($issue.File)"
                    $fixedCount++
                } catch {
                    Write-Error "Failed to fix encoding for $($issue.File): $_"
                }
            }
        }
    }
    
    # Convert CHANGELOG.md to ASCII if needed
    $asciiResult = $results.AsciiSafety
    if (-not $asciiResult.Passed) {
        Write-Host "馃敡 Considering ASCII conversion for CHANGELOG.md..." -ForegroundColor Yellow
        
        $changelogPath = Join-Path $SkillDir "CHANGELOG.md"
        if (Test-Path $changelogPath) {
            $content = Get-Content $changelogPath -Raw -Encoding UTF8
            
            # Check if it's already English (simple check)
            $englishWordCount = ($content -split '\s+' | Where-Object { $_ -match '^[A-Za-z]+$' }).Count
            $totalWordCount = ($content -split '\s+').Count
            
            if ($englishWordCount / $totalWordCount -gt 0.7) {
                Write-Info "CHANGELOG.md appears to be mostly English"
            } else {
                Write-Warning "CHANGELOG.md contains significant non-English text"
                Write-Host "  Consider creating an English ASCII version for better compatibility" -ForegroundColor White
            }
        }
    }
    
    if ($fixedCount -gt 0) {
        Write-Host "`n馃敡 Fixed $fixedCount files. Please review and run check again." -ForegroundColor Green
    } else {
        Write-Host "`n鈩癸笍  No encoding fixes were needed or could be applied automatically." -ForegroundColor Cyan
        Write-Host "   Some issues may require manual intervention
