# Documentation Consistency Check Script
# Based on 2026-03-24 AISkinX documentation consistency lesson

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
    Write-Host "馃殌 Documentation Consistency Check" -ForegroundColor Cyan
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
        SkillMdExists = Check-SkillMdExists
        SecurityDeclarations = Check-SecurityDeclarations
        CodeConsistency = Check-CodeConsistency
        ConfigurationConsistency = Check-ConfigurationConsistency
        ExamplesConsistency = Check-ExamplesConsistency
    }
    
    # Output summary
    Write-Summary $results
    
    # Apply fixes if needed
    if ($Fix) {
        Apply-Fixes $results
    }
}

# Check if SKILL.md exists
function Check-SkillMdExists {
    Write-Section "SKILL.md Existence Check"
    
    $skillPath = Join-Path $SkillDir "SKILL.md"
    if (Test-Path $skillPath) {
        Write-Success "SKILL.md exists"
        return @{Passed = $true; Path = $skillPath}
    } else {
        Write-Error "SKILL.md does not exist"
        return @{Passed = $false; Path = $null}
    }
}

# Check security declarations in SKILL.md
function Check-SecurityDeclarations {
    Write-Section "Security Declarations Check"
    
    $skillPath = Join-Path $SkillDir "SKILL.md"
    if (-not (Test-Path $skillPath)) {
        Write-Error "SKILL.md not found, skipping declarations check"
        return @{Passed = $false; Declarations = @()}
    }
    
    try {
        $content = Get-Content $skillPath -Raw -Encoding UTF8
        $declarations = @()
        
        # Common security declarations to check
        $declarationPatterns = @(
            @{Pattern = "100%[^\w]*(local|鏈湴)[^\w]*(operation|杩愯)"; Description = "100% local operation"},
            @{Pattern = "(path|璺緞)[^\w]*(restrict|闄愬埗|access|璁块棶)"; Description = "Path access restriction"},
            @{Pattern = "(no network|鏃犵綉缁?[^\w]*(access|璁块棶)"; Description = "No network access"},
            @{Pattern = "(privacy|闅愮)[^\w]*(friendly|鍙嬪ソ)"; Description = "Privacy friendly"},
            @{Pattern = "(local only|浠呮湰鍦皘鏈湴杩愯)"; Description = "Local only operation"},
            @{Pattern = "(no external API|鏃犲閮ˋPI)"; Description = "No external API"},
            @{Pattern = "(file access|鏂囦欢璁块棶)[^\w]*(restrict|闄愬埗)"; Description = "File access restriction"}
        )
        
        foreach ($pattern in $declarationPatterns) {
            if ($content -match $pattern.Pattern) {
                Write-Info "Found declaration: $($pattern.Description)"
                $declarations += $pattern.Description
            }
        }
        
        if ($declarations.Count -gt 0) {
            Write-Success "Found $($declarations.Count) security declarations"
            return @{Passed = $true; Declarations = $declarations}
        } else {
            Write-Warning "No security declarations found in SKILL.md"
            return @{Passed = $true; Declarations = @()}
        }
        
    } catch {
        Write-Error "Failed to read SKILL.md: $_"
        return @{Passed = $false; Declarations = @()}
    }
}

# Check if code supports the declarations
function Check-CodeConsistency {
    Write-Section "Code Consistency Check"
    
    $skillPath = Join-Path $SkillDir "SKILL.md"
    if (-not (Test-Path $skillPath)) {
        Write-Error "SKILL.md not found, skipping code consistency check"
        return @{Passed = $false; Issues = @("SKILL.md missing")}
    }
    
    try {
        $content = Get-Content $skillPath -Raw -Encoding UTF8
        $codeFiles = Get-ChildItem $SkillDir -Filter "*.py" -Recurse -ErrorAction SilentlyContinue
        $issues = @()
        
        # Check for network access declaration
        if ($content -match "100%[^\w]*(local|鏈湴)|(no network|鏃犵綉缁?") {
            Write-Info "Checking network access consistency..."
            
            $hasNetworkCode = $false
            foreach ($file in $codeFiles) {
                $codeContent = Get-Content $file.FullName -Raw -Encoding UTF8
                if ($codeContent -match "import requests|import urllib|import socket|import http\.client|http://|https://") {
                    $hasNetworkCode = $true
                    Write-Error "Found network code in: $($file.Name)"
                    $issues += "Network code found but declared as local-only"
                    break
                }
            }
            
            if (-not $hasNetworkCode) {
                Write-Success "No network code found (consistent with declaration)"
            }
        }
        
        # Check for path restriction declaration
        if ($content -match "(path|璺緞)[^\w]*(restrict|闄愬埗)") {
            Write-Info "Checking path restriction consistency..."
            
            $hasPathValidation = $false
            foreach ($file in $codeFiles) {
                $codeContent = Get-Content $file.FullName -Raw -Encoding UTF8
                if ($codeContent -match "path_validator|is_safe_path|validate.*path|check.*path") {
                    $hasPathValidation = $true
                    Write-Success "Found path validation in: $($file.Name)"
                    break
                }
            }
            
            if (-not $hasPathValidation) {
                Write-Error "No path validation found (inconsistent with declaration)"
                $issues += "Path restriction declared but no validation code found"
            }
        }
        
        # Check for dangerous functions
        Write-Info "Checking for dangerous functions..."
        $dangerousFunctions = @("subprocess\.", "eval\(", "exec\(", "__import__\(")
        $foundDangerous = @()
        
        foreach ($file in $codeFiles) {
            $codeContent = Get-Content $file.FullName -Raw -Encoding UTF8
            foreach ($func in $dangerousFunctions) {
                if ($codeContent -match $func) {
                    $foundDangerous += "$func in $($file.Name)"
                }
            }
        }
        
        if ($foundDangerous.Count -gt 0) {
            Write-Warning "Found dangerous functions:"
            foreach ($func in $foundDangerous) {
                Write-Host "  鈿狅笍  $func" -ForegroundColor Yellow
            }
            $issues += "Found dangerous functions: $($foundDangerous -join ', ')"
        } else {
            Write-Success "No dangerous functions found"
        }
        
        return @{
            Passed = ($issues.Count -eq 0)
            Issues = $issues
            CodeFileCount = $codeFiles.Count
        }
        
    } catch {
        Write-Error "Failed to check code consistency: $_"
        return @{Passed = $false; Issues = @("Check failed: $_")}
    }
}

# Check configuration consistency
function Check-ConfigurationConsistency {
    Write-Section "Configuration Consistency Check"
    
    $configPath = Join-Path $SkillDir "config.yaml"
    if (-not (Test-Path $configPath)) {
        Write-Warning "config.yaml not found"
        return @{Passed = $true; Issues = @()}
    }
    
    try {
        $configContent = Get-Content $configPath -Raw -Encoding UTF8
        $issues = @()
        
        # Check for security declarations in config
        if ($configContent -notmatch "security:") {
            Write-Warning "No security section in config.yaml"
            $issues += "Missing security section in config"
        } else {
            Write-Success "Security section found in config.yaml"
            
            # Check specific security settings
            if ($configContent -notmatch "network_access:\s*false") {
                Write-Warning "network_access: false not found in config"
                $issues += "Missing network_access: false in config"
            } else {
                Write-Success "network_access: false found"
            }
            
            if ($configContent -notmatch "local_only:\s*true") {
                Write-Warning "local_only: true not found in config"
                $issues += "Missing local_only: true in config"
            } else {
                Write-Success "local_only: true found"
            }
        }
        
        return @{
            Passed = ($issues.Count -eq 0)
            Issues = $issues
        }
        
    } catch {
        Write-Error "Failed to read config.yaml: $_"
        return @{Passed = $false; Issues = @("Failed to read config: $_")}
    }
}

# Check examples consistency
function Check-ExamplesConsistency {
    Write-Section "Examples Consistency Check"
    
    $skillPath = Join-Path $SkillDir "SKILL.md"
    if (-not (Test-Path $skillPath)) {
        return @{Passed = $true; Issues = @()}
    }
    
    try {
        $content = Get-Content $skillPath -Raw -Encoding UTF8
        $issues = @()
        
        # Check for code blocks with examples
        if ($content -match '```(bash|powershell|python|json)') {
            Write-Info "Found code examples in SKILL.md"
            
            # Extract and check example commands
            $examplePattern = '```(?:bash|powershell)\s*\n([^`]+)\n```'
            $matches = [regex]::Matches($content, $examplePattern)
            
            foreach ($match in $matches) {
                $example = $match.Groups[1].Value.Trim()
                Write-Info "Example: $example"
                
                # Check if example uses correct command format
                if ($example -match 'openclaw skill') {
                    Write-Success "Example uses openclaw command"
                } elseif ($example -match 'install\.bat|install\.sh') {
                    Write-Error "Example uses install.bat/install.sh (deprecated)"
                    $issues += "Deprecated install script in example: $example"
                }
            }
        } else {
            Write-Warning "No code examples found in SKILL.md"
        }
        
        return @{
            Passed = ($issues.Count -eq 0)
            Issues = $issues
            ExampleCount = $matches.Count
        }
        
    } catch {
        Write-Error "Failed to check examples: $_"
        return @{Passed = $false; Issues = @("Failed to check examples: $_")}
    }
}

# Output summary
function Write-Summary {
    param($results)
    
    Write-Section "Check Results Summary"
    
    $totalChecks = $results.Count
    $passedChecks = ($results.Values | Where-Object { $_.Passed }).Count
    
    Write-Host "馃搳 Check Statistics:" -ForegroundColor Cyan
    Write-Host "  Total checks: $totalChecks" -ForegroundColor White
    Write-Host "  Passed: $passedChecks" -ForegroundColor Green
    Write-Host "  Failed: $($totalChecks - $passedChecks)" -ForegroundColor Red
    
    # Detailed results
    foreach ($key in $results.Keys) {
        $result = $results[$key]
        $status = if ($result.Passed) { "✅" } else { "❌" }
        Write-Host "  $status $key" -ForegroundColor $(if ($result.Passed) { "Green" } else { "Red" })
    }
    
    # Overall evaluation
    if ($passedChecks -eq $totalChecks) {
        Write-Host "`n馃帀 All documentation consistency checks passed!" -ForegroundColor Green
        Write-Host "Documentation is consistent with code implementation." -ForegroundColor Green
    } else {
        Write-Host "`n鈿狅笍  Documentation consistency issues found:" -ForegroundColor Yellow
        
        # Show specific issues
        foreach ($key in $results.Keys) {
            $result = $results[$key]
            if (-not $result.Passed -and $result.Issues) {
                Write-Host "  $key issues:" -ForegroundColor Yellow
                foreach ($issue in $result.Issues) {
                    Write-Host "    - $issue" -ForegroundColor White
                }
            }
        }
        
        Write-Host "`n馃挕 Fix suggestions:" -ForegroundColor Cyan
        Write-Host "  1. Run with -Fix parameter to attempt automatic fixes" -ForegroundColor White
        Write-Host "  2. Review and update SKILL.md to match code implementation" -ForegroundColor White
        Write-Host "  3. Ensure config.yaml has correct security declarations" -ForegroundColor White
        Write-Host "  4. Update examples to use current command formats" -ForegroundColor White
    }
}

# Apply fixes
function Apply-Fixes {
    param($results)
    
    Write-Section "Applying Fixes"
    
    # Fix configuration if needed
    $configResult = $results.ConfigurationConsistency
    if (-not $configResult.Passed) {
        Write-Host "馃敡 Fixing configuration..." -ForegroundColor Yellow
        
        $configPath = Join-Path $SkillDir "config.yaml"
        if (Test-Path $configPath) {
            $configContent = Get-Content $configPath -Raw -Encoding UTF8
            
            # Add security section if missing
            if ($configContent -notmatch "security:") {
                $configContent += "`n`nsecurity:`n  network_access: false`n  local_only: true`n  privacy_friendly: true`n"
                $configContent | Out-File -FilePath $configPath -Encoding UTF8
                Write-Success "Added security section to config.yaml"
            }
            
            # Ensure network_access: false
            if ($configContent -notmatch "network_access:\s*false") {
                $configContent = $configContent -replace "security:", "security:`n  network_access: false"
                $configContent | Out-File -FilePath $configPath -Encoding UTF8
                Write-Success "Added network_access: false to config.yaml"
            }
        }
    }
    
    # Fix examples if needed
    $examplesResult = $results.ExamplesConsistency
    if (-not $examplesResult.Passed -and $examplesResult.Issues) {
        Write-Host "馃敡 Fixing examples..." -ForegroundColor Yellow
        
        $skillPath = Join-Path $SkillDir "SKILL.md"
        if (Test-Path $skillPath) {
            $content = Get-Content $skillPath -Raw -Encoding UTF8
            
            # Replace install.bat/sh with openclaw commands
            $fixedContent = $content -replace 'install\.bat', 'openclaw skill install'
            $fixedContent = $fixedContent -replace 'install\.sh', 'openclaw skill install'
            
            if ($content -ne $fixedContent) {
                $fixedContent | Out-File -FilePath $skillPath -Encoding UTF8
                Write-Success "Updated examples in SKILL.md"
            }
        }
    }
    
    Write-Host "`n馃敡 Fixes applied. Please review and run check again." -ForegroundColor Green
}

# Run main function
Main
