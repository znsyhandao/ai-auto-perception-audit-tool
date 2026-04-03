# check_text_files.ps1
# Text File Format Check for ClawHub Compliance
# Based on 2026-03-30 LICENSE file lesson

param(
    [string]$SkillDir,
    [switch]$FixIssues = $false
)

Write-Host "=== Text File Format Check for ClawHub Compliance ===" -ForegroundColor Cyan
Write-Host "Based on 2026-03-30 LICENSE file lesson" -ForegroundColor Cyan
Write-Host "Check Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "Skill Directory: $SkillDir" -ForegroundColor Cyan
Write-Host "Auto Fix: $(if ($FixIssues) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host ""

# Check if directory exists
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] Skill directory not found: $SkillDir" -ForegroundColor Red
    exit 1
}

# Initialize results
$results = @{
    "total_files" = 0
    "files_without_extension" = @()
    "license_file_issues" = @()
    "encoding_issues" = @()
    "binary_files" = @()
    "fixed_issues" = @()
}

# ============================================
# 1. Check all files for extensions
# ============================================
Write-Host "## 1. Checking file extensions..." -ForegroundColor Yellow

$allFiles = Get-ChildItem -Path $SkillDir -Recurse -File
$results.total_files = $allFiles.Count

foreach ($file in $allFiles) {
    # Check for files without extension
    if ([string]::IsNullOrEmpty($file.Extension)) {
        $results.files_without_extension += @{
            "file" = $file.FullName
            "name" = $file.Name
            "directory" = $file.DirectoryName
        }
    }
}

if ($results.files_without_extension.Count -gt 0) {
    Write-Host "  ❌ Found $($results.files_without_extension.Count) files without extension:" -ForegroundColor Red
    foreach ($issue in $results.files_without_extension) {
        Write-Host "    - $($issue.name) (in $($issue.directory))" -ForegroundColor Red
        
        # Auto fix: Add .txt extension for text-like files
        if ($FixIssues) {
            # Check if file appears to be text
            try {
                $content = Get-Content $issue.file -Raw -ErrorAction Stop
                if ($content -match '^[ -~\r\n\t]*$' -or $content -match '[\u4e00-\u9fff]') {
                    # Looks like text, rename to .txt
                    $newName = "$($issue.file).txt"
                    Rename-Item -Path $issue.file -NewName $newName -Force
                    $results.fixed_issues += "Renamed $($issue.name) to $($issue.name).txt"
                    Write-Host "      ✅ Fixed: Renamed to $($issue.name).txt" -ForegroundColor Green
                }
            } catch {
                # File might be binary, don't rename
            }
        }
    }
} else {
    Write-Host "  ✅ All files have extensions" -ForegroundColor Green
}

# ============================================
# 2. Check license file format
# ============================================
Write-Host "`n## 2. Checking license file format..." -ForegroundColor Yellow

$licenseFiles = Get-ChildItem -Path $SkillDir -Recurse -File | Where-Object {
    $_.BaseName -match "^LICENSE$|^LICENCE$|^license$|^licence$"
}

if ($licenseFiles.Count -gt 0) {
    foreach ($file in $licenseFiles) {
        # Check extension
        if ($file.Extension -in @(".txt", ".md")) {
            Write-Host "  ✅ License file has valid extension: $($file.Name)" -ForegroundColor Green
        } else {
            $results.license_file_issues += @{
                "file" = $file.FullName
                "name" = $file.Name
                "issue" = "Invalid extension: $($file.Extension)"
            }
            Write-Host "  ❌ License file has invalid extension: $($file.Name)" -ForegroundColor Red
            Write-Host "    Issue: Should be .txt or .md, but is $($file.Extension)" -ForegroundColor Yellow
            
            # Auto fix: Rename to LICENSE.txt
            if ($FixIssues) {
                $newName = "LICENSE.txt"
                $newPath = Join-Path $file.DirectoryName $newName
                
                # If there's already a LICENSE.txt, remove it first
                if (Test-Path $newPath) {
                    Remove-Item $newPath -Force
                }
                
                Rename-Item -Path $file.FullName -NewName $newName -Force
                $results.fixed_issues += "Renamed license file to LICENSE.txt"
                Write-Host "      ✅ Fixed: Renamed to LICENSE.txt" -ForegroundColor Green
            } else {
                Write-Host "    Fix: Rename to LICENSE.txt" -ForegroundColor Yellow
            }
        }
        
        # Check content is text
        try {
            $content = Get-Content $file.FullName -Raw -ErrorAction Stop
            if ($content -match '[^\x00-\x7F\r\n\t]' -and $content -notmatch '[\u4e00-\u9fff]') {
                # Contains non-ASCII characters that aren't Chinese, might be encoding issue
                $results.license_file_issues += @{
                    "file" = $file.FullName
                    "name" = $file.Name
                    "issue" = "Contains unusual non-ASCII characters"
                }
                Write-Host "    ⚠️  Warning: Contains unusual characters" -ForegroundColor Yellow
            }
        } catch {
            $results.license_file_issues += @{
                "file" = $file.FullName
                "name" = $file.Name
                "issue" = "Cannot read file content"
            }
            Write-Host "    ❌ Cannot read file content (may be binary)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  ⚠️  No license file found" -ForegroundColor Yellow
    $results.license_file_issues += @{
        "file" = ""
        "name" = ""
        "issue" = "No license file found"
    }
}

# ============================================
# 3. Check file encoding (UTF-8 BOM)
# ============================================
Write-Host "`n## 3. Checking file encoding (UTF-8 BOM)..." -ForegroundColor Yellow

$textFiles = Get-ChildItem -Path $SkillDir -Recurse -File -Include *.md, *.txt, *.json, *.yaml, *.yml, *.py, *.js, *.ts
$bomCount = 0

foreach ($file in $textFiles) {
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        
        # Check for UTF-8 BOM (EF BB BF)
        if ($bytes.Count -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $bomCount++
            $results.encoding_issues += @{
                "file" = $file.FullName
                "name" = $file.Name
                "issue" = "Contains UTF-8 BOM"
            }
            Write-Host "  ❌ File contains UTF-8 BOM: $($file.Name)" -ForegroundColor Red
            
            # Auto fix: Remove BOM
            if ($FixIssues) {
                # Read file content without BOM
                $content = [System.Text.Encoding]::UTF8.GetString($bytes, 3, $bytes.Length - 3)
                
                # Save without BOM
                $utf8NoBom = New-Object System.Text.UTF8Encoding $false
                [System.IO.File]::WriteAllText($file.FullName, $content, $utf8NoBom)
                
                $results.fixed_issues += "Removed BOM from $($file.Name)"
                Write-Host "      ✅ Fixed: Removed BOM" -ForegroundColor Green
            } else {
                Write-Host "    Fix: Save as UTF-8 without BOM" -ForegroundColor Yellow
            }
        }
    } catch {
        # Ignore files that can't be read
    }
}

if ($bomCount -eq 0) {
    Write-Host "  ✅ No files with UTF-8 BOM found" -ForegroundColor Green
} else {
    Write-Host "  Found $bomCount files with UTF-8 BOM" -ForegroundColor Red
}

# ============================================
# 4. Check for binary files disguised as text
# ============================================
Write-Host "`n## 4. Checking for binary files..." -ForegroundColor Yellow

$suspiciousFiles = @()
foreach ($file in $textFiles) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction Stop
        
        # Check for null bytes or other binary indicators
        if ($content -match '\x00') {
            $suspiciousFiles += $file
            $results.binary_files += @{
                "file" = $file.FullName
                "name" = $file.Name
                "issue" = "Contains null bytes (binary indicator)"
            }
            Write-Host "  ❌ File contains null bytes (binary): $($file.Name)" -ForegroundColor Red
        }
        
        # Check for very long lines (binary files often have no line breaks)
        $lines = $content -split "`n"
        if ($lines.Count -eq 1 -and $lines[0].Length -gt 1000) {
            $suspiciousFiles += $file
            $results.binary_files += @{
                "file" = $file.FullName
                "name" = $file.Name
                "issue" = "Single very long line (binary indicator)"
            }
            Write-Host "  ⚠️  File has single very long line: $($file.Name)" -ForegroundColor Yellow
        }
    } catch {
        # If we can't read it as text, it's probably binary
        $suspiciousFiles += $file
        $results.binary_files += @{
            "file" = $file.FullName
            "name" = $file.Name
            "issue" = "Cannot read as text (likely binary)"
        }
        Write-Host "  ❌ Cannot read as text (likely binary): $($file.Name)" -ForegroundColor Red
    }
}

if ($suspiciousFiles.Count -eq 0) {
    Write-Host "  ✅ No suspicious binary files found" -ForegroundColor Green
}

# ============================================
# Summary Report
# ============================================
Write-Host "`n=== Summary Report ===" -ForegroundColor Cyan
Write-Host "Total files checked: $($results.total_files)" -ForegroundColor White

$totalIssues = $results.files_without_extension.Count + $results.license_file_issues.Count + 
               $results.encoding_issues.Count + $results.binary_files.Count

if ($totalIssues -eq 0) {
    Write-Host "✅ All checks passed! Ready for ClawHub submission." -ForegroundColor Green
} else {
    Write-Host "Found $totalIssues issues:" -ForegroundColor Yellow
    
    if ($results.files_without_extension.Count -gt 0) {
        Write-Host "  ❌ Files without extension: $($results.files_without_extension.Count)" -ForegroundColor Red
    }
    
    if ($results.license_file_issues.Count -gt 0) {
        Write-Host "  ❌ License file issues: $($results.license_file_issues.Count)" -ForegroundColor Red
    }
    
    if ($results.encoding_issues.Count -gt 0) {
        Write-Host "  ❌ Encoding issues: $($results.encoding_issues.Count)" -ForegroundColor Red
    }
    
    if ($results.binary_files.Count -gt 0) {
        Write-Host "  ❌ Binary file issues: $($results.binary_files.Count)" -ForegroundColor Red
    }
    
    if ($FixIssues -and $results.fixed_issues.Count -gt 0) {
        Write-Host "`n✅ Fixed $($results.fixed_issues.Count) issues:" -ForegroundColor Green
        foreach ($fix in $results.fixed_issues) {
            Write-Host "  - $fix" -ForegroundColor Green
        }
        
        # Re-run check to verify fixes
        Write-Host "`n=== Re-running check to verify fixes ===" -ForegroundColor Cyan
        & $MyInvocation.MyCommand.Path -SkillDir $SkillDir
    } else {
        Write-Host "`n⚠️  Run with -FixIssues parameter to automatically fix issues" -ForegroundColor Yellow
    }
}

# Save detailed report
$reportFile = Join-Path $SkillDir "text_file_check_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$results | ConvertTo-Json -Depth 3 | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "`nDetailed report saved to: $reportFile" -ForegroundColor Cyan

# Return exit code based on issues
if ($totalIssues -eq 0) {
    exit 0
} else {
    exit 1
}