# ultimate_clawhub_audit_fixed.ps1
# Fixed version with text file format checks
# Based on 2026-03-30 LICENSE file lesson

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\ultimate_audit_fixed",
    [switch]$StrictMode = $true,
    [switch]$AutoFix = $false
)

Write-Host "=== Ultimate ClawHub Audit (Fixed) ===" -ForegroundColor Cyan
Write-Host "Goal: Ensure skill 100% passes ClawHub scan on first try" -ForegroundColor Cyan
Write-Host "Mode: $(if ($StrictMode) { 'Strict Mode' } else { 'Standard Mode' })" -ForegroundColor Cyan
Write-Host "Auto Fix: $(if ($AutoFix) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host "Audit Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Check if directory exists
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] Skill directory not found: $SkillDir" -ForegroundColor Red
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Initialize audit results
$auditResults = @{
    "metadata" = @{
        "skill_dir" = $SkillDir
        "audit_time" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "strict_mode" = $StrictMode
        "auto_fix" = $AutoFix
    }
    "categories" = @{}
    "score" = @{
        "total" = 0
        "passed" = 0
        "percentage" = 0
    }
    "critical_issues" = @()
    "warning_issues" = @()
    "recommendations" = @()
}

# Category definitions
$categories = @{
    "file_structure" = "File Structure"
    "version_consistency" = "Version Consistency"
    "security_compliance" = "Security Compliance"
    "documentation_quality" = "Documentation Quality"
    "metadata_validation" = "Metadata Validation"
    "link_validation" = "Link Validation"
    "code_quality" = "Code Quality"
    "dependency_validation" = "Dependency Validation"
    "license_compliance" = "License Compliance"
    "text_file_format" = "Text File Format"  # NEW: Added for LICENSE file lesson
    "clawhub_specific" = "ClawHub Specific Requirements"
}

foreach ($category in $categories.Keys) {
    $auditResults.categories[$category] = @{
        "checks" = @()
        "passed" = 0
        "total" = 0
        "score" = 0
    }
}

# Helper function
function Add-CheckResult {
    param(
        [string]$Category,
        [string]$CheckName,
        [bool]$Passed,
        [string]$Message,
        [string]$FixSuggestion = "",
        [bool]$Critical = $false
    )
    
    $checkResult = @{
        "name" = $CheckName
        "passed" = $Passed
        "message" = $Message
        "fix_suggestion" = $FixSuggestion
        "critical" = $Critical
        "timestamp" = Get-Date -Format 'HH:mm:ss'
    }
    
    $auditResults.categories[$Category].checks += $checkResult
    $auditResults.categories[$Category].total++
    
    if ($Passed) {
        $auditResults.categories[$Category].passed++
        Write-Host "  [PASS] $CheckName" -ForegroundColor Green
    } else {
        if ($Critical) {
            Write-Host "  [FAIL] $CheckName (Critical)" -ForegroundColor Red
            $auditResults.critical_issues += "${Category}: $Message"
        } else {
            Write-Host "  [WARN] $CheckName" -ForegroundColor Yellow
            $auditResults.warning_issues += "${Category}: $Message"
        }
        
        if ($FixSuggestion) {
            Write-Host "    Fix: $FixSuggestion" -ForegroundColor Cyan
        }
    }
}

# ============================================
# 1. File Structure Check
# ============================================
Write-Host "`n## 1. File Structure Check" -ForegroundColor Yellow

$requiredFiles = @("SKILL.md", "README.md", "CHANGELOG.md", "config.yaml", "package.json", "skill.py", "requirements.txt")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    $exists = Test-Path $filePath
    
    Add-CheckResult -Category "file_structure" -CheckName "File: $file" `
        -Passed $exists -Message "$file $(if($exists){'exists'}else{'not found'})" `
        -FixSuggestion "Add missing file: $file" `
        -Critical $true
}

# ============================================
# 2. Version Consistency Check
# ============================================
Write-Host "`n## 2. Version Consistency Check" -ForegroundColor Yellow

$versionFiles = @("config.yaml", "package.json", "SKILL.md")
$versions = @()

foreach ($file in $versionFiles) {
    $filePath = Join-Path $SkillDir $file
    if (Test-Path $filePath) {
        $content = Get-Content $filePath -Raw
        
        if ($file -eq "config.yaml") {
            # Extract version from config.yaml
            if ($content -match 'version:\s*["'']?([0-9]+\.[0-9]+\.[0-9]+)["'']?') {
                $versions += @{
                    File = $file
                    Version = $matches[1]
                }
            }
        } elseif ($file -eq "package.json") {
            # Extract version from package.json
            if ($content -match '"version"\s*:\s*["'']([0-9]+\.[0-9]+\.[0-9]+)["'']') {
                $versions += @{
                    File = $file
                    Version = $matches[1]
                }
            }
        } elseif ($file -eq "SKILL.md") {
            # Extract version from SKILL.md
            if ($content -match 'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)') {
                $versions += @{
                    File = $file
                    Version = $matches[1]
                }
            }
        }
    }
}

# Check consistency
if ($versions.Count -ge 2) {
    $firstVersion = $versions[0].Version
    $allSame = $true
    foreach ($v in $versions) {
        if ($v.Version -ne $firstVersion) {
            $allSame = $false
            break
        }
    }
    
    $versionString = ""
    foreach ($v in $versions) {
        $versionString += "$($v.File)=$($v.Version), "
    }
    $versionString = $versionString.TrimEnd(", ")
    
    Add-CheckResult -Category "version_consistency" -CheckName "Version consistency" `
        -Passed $allSame -Message "Versions: $versionString" `
        -FixSuggestion "Make all version numbers consistent" `
        -Critical $true
} else {
    Add-CheckResult -Category "version_consistency" -CheckName "Version consistency" `
        -Passed $false -Message "Could not extract versions from files" `
        -FixSuggestion "Add version numbers to config.yaml, package.json, and SKILL.md" `
        -Critical $true
}

# ============================================
# 3. Security Compliance Check
# ============================================
Write-Host "`n## 3. Security Compliance Check" -ForegroundColor Yellow

# Check config.yaml security declarations
$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    
    # Check for security section
    $hasSecuritySection = $configContent -match 'security:'
    $hasNetworkAccessFalse = $configContent -match 'network_access:\s*false'
    $hasLocalOnlyTrue = $configContent -match 'local_only:\s*true'
    
    Add-CheckResult -Category "security_compliance" -CheckName "config.yaml security section" `
        -Passed $hasSecuritySection -Message "Security section: $(if($hasSecuritySection){'found'}else{'not found'})" `
        -FixSuggestion "Add security section to config.yaml" `
        -Critical $true
    
    Add-CheckResult -Category "security_compliance" -CheckName "config.yaml network_access: false" `
        -Passed $hasNetworkAccessFalse -Message "network_access: false $(if($hasNetworkAccessFalse){'found'}else{'not found'})" `
        -FixSuggestion "Add network_access: false to security section" `
        -Critical $true
    
    Add-CheckResult -Category "security_compliance" -CheckName "config.yaml local_only: true" `
        -Passed $hasLocalOnlyTrue -Message "local_only: true $(if($hasLocalOnlyTrue){'found'}else{'not found'})" `
        -FixSuggestion "Add local_only: true to security section" `
        -Critical $true
}

# ============================================
# 4. Documentation Quality Check
# ============================================
Write-Host "`n## 4. Documentation Quality Check" -ForegroundColor Yellow

$docFiles = @("SKILL.md", "README.md", "CHANGELOG.md")
foreach ($doc in $docFiles) {
    $docPath = Join-Path $SkillDir $doc
    $exists = Test-Path $docPath
    
    Add-CheckResult -Category "documentation_quality" -CheckName "Document: $doc" `
        -Passed $exists -Message "$doc $(if($exists){'exists'}else{'not found'})" `
        -FixSuggestion "Add missing documentation: $doc" `
        -Critical $false
}

# ============================================
# 5. Metadata Validation
# ============================================
Write-Host "`n## 5. Metadata Validation" -ForegroundColor Yellow

$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        $hasName = ![string]::IsNullOrEmpty($packageJson.name)
        $hasDescription = ![string]::IsNullOrEmpty($packageJson.description)
        $hasAuthor = $null -ne $packageJson.author
        $hasLicense = ![string]::IsNullOrEmpty($packageJson.license)
        
        $metadataComplete = $hasName -and $hasDescription -and $hasAuthor -and $hasLicense
        
        Add-CheckResult -Category "metadata_validation" -CheckName "package.json metadata completeness" `
            -Passed $metadataComplete -Message "Metadata completeness: Name=$hasName, Description=$hasDescription, Author=$hasAuthor, License=$hasLicense" `
            -FixSuggestion "Complete all metadata fields in package.json" `
            -Critical $true
    } catch {
        Add-CheckResult -Category "metadata_validation" -CheckName "package.json metadata completeness" `
            -Passed $false -Message "Cannot parse package.json" `
            -FixSuggestion "Fix package.json syntax errors" `
            -Critical $true
    }
}

# ============================================
# 6. Link Validation
# ============================================
Write-Host "`n## 6. Link Validation" -ForegroundColor Yellow

if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        # Check author URL
        $hasAuthorUrl = $false
        if ($packageJson.author -and $packageJson.author.url) {
            $hasAuthorUrl = $packageJson.author.url -match '^https?://'
            $isPlaceholder = $packageJson.author.url -match 'example\.com|placeholder|TODO'
            
            Add-CheckResult -Category "link_validation" -CheckName "Author URL format" `
                -Passed $hasAuthorUrl -Message "Author URL: $(if($hasAuthorUrl){'valid format'}else{'invalid or missing'})" `
                -FixSuggestion "Add valid author URL to package.json" `
                -Critical $false
            
            Add-CheckResult -Category "link_validation" -CheckName "Author URL not placeholder" `
                -Passed (-not $isPlaceholder) -Message "Author URL placeholder: $isPlaceholder" `
                -FixSuggestion "Replace placeholder URL with real URL" `
                -Critical $true
        }
    } catch {
        # Ignore errors
    }
}

# ============================================
# 7. Code Quality Check
# ============================================
Write-Host "`n## 7. Code Quality Check" -ForegroundColor Yellow

$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    
    # Check for dangerous imports
    $hasDangerousImports = $skillContent -match 'import\s+subprocess|import\s+os\.system|from\s+os\s+import\s+system'
    
    Add-CheckResult -Category "code_quality" -CheckName "No dangerous imports in skill.py" `
        -Passed (-not $hasDangerousImports) -Message "Dangerous imports: $(if($hasDangerousImports){'found'}else{'not found'})" `
        -FixSuggestion "Remove dangerous imports (subprocess, os.system)" `
        -Critical $true
}

# ============================================
# 8. Dependency Validation
# ============================================
Write-Host "`n## 8. Dependency Validation" -ForegroundColor Yellow

$requirementsPath = Join-Path $SkillDir "requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath
    
    # Check if requirements.txt is empty or only has comments
    $hasRealDependencies = $false
    foreach ($line in $requirementsContent) {
        $trimmedLine = $line.Trim()
        if ($trimmedLine -ne "" -and -not $trimmedLine.StartsWith("#")) {
            $hasRealDependencies = $true
            break
        }
    }
    
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txt has real dependencies" `
        -Passed $hasRealDependencies -Message "Real dependencies: $(if($hasRealDependencies){'found'}else{'not found'})" `
        -FixSuggestion "Add dependencies to requirements.txt or remove the file" `
        -Critical $false
}

# ============================================
# 9. License Compliance
# ============================================
Write-Host "`n## 9. License Compliance" -ForegroundColor Yellow

# 9.1 License file check
$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "^LICENSE|^LICENCE|^license|^licence"
}

Add-CheckResult -Category "license_compliance" -CheckName "License file exists" `
    -Passed ($licenseFiles.Count -gt 0) `
    -Message "License file: $(if($licenseFiles.Count -gt 0){'found'}else{'not found'})" `
    -FixSuggestion "Add LICENSE file with appropriate license" `
    -Critical $false

# 9.2 package.json license field
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasLicenseField = ![string]::IsNullOrEmpty($packageJson.license)
        
        Add-CheckResult -Category "license_compliance" -CheckName "package.json license field" `
            -Passed $hasLicenseField `
            -Message "package.json license: $(if($hasLicenseField){$packageJson.license}else{'missing'})" `
            -FixSuggestion "Add license field to package.json" `
            -Critical $false
    } catch {
        # Ignore error
    }
}

# ============================================
# 10. Text File Format Check (NEW: Based on LICENSE file lesson)
# ============================================
Write-Host "`n## 10. Text File Format Check" -ForegroundColor Yellow
Write-Host "Based on 2026-03-30 LICENSE file lesson" -ForegroundColor Cyan

# 10.1 Check all files have extensions
$allFiles = Get-ChildItem -Path $SkillDir -Recurse -File
$filesWithoutExtension = @()
foreach ($file in $allFiles) {
    if ([string]::IsNullOrEmpty($file.Extension)) {
        $filesWithoutExtension += $file.Name
    }
}

Add-CheckResult -Category "text_file_format" -CheckName "All files have extensions" `
    -Passed ($filesWithoutExtension.Count -eq 0) `
    -Message "Files without extension: $($filesWithoutExtension.Count)" `
    -FixSuggestion "Add extensions to files: $($filesWithoutExtension -join ', ')" `
    -Critical $true  # This is critical for ClawHub "non-text files" warning

# 10.2 Check license file format specifically
if ($licenseFiles.Count -gt 0) {
    $licenseFile = $licenseFiles[0]
    
    # Check license file extension
    $hasValidLicenseExtension = $licenseFile.Extension -in @(".txt", ".md")
    
    Add-CheckResult -Category "text_file_format" -CheckName "License file has valid extension (.txt or .md)" `
        -Passed $hasValidLicenseExtension `
        -Message "License file extension: $($licenseFile.Extension)" `
        -FixSuggestion "Rename LICENSE to LICENSE.txt or LICENSE.md" `
        -Critical $true  # This causes ClawHub "non-text files" warning
    
    # Check license file encoding (UTF-8 BOM)
    try {
        $bytes = [System.IO.File]::ReadAllBytes($licenseFile.FullName)
        $hasBOM = $bytes.Count -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
        
        Add-CheckResult -Category "text_file_format" -CheckName "License file encoding (no UTF-8 BOM)" `
            -Passed (-not $hasBOM) `
            -Message "License file BOM: $(if($hasBOM){'has BOM'}else{'no BOM'})" `
            -FixSuggestion "Save license file as UTF-8 without BOM" `
            -Critical $false
    } catch {
        # Ignore error
    }
}

# 10.3 Check for UTF-8 BOM in all text files
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

Add-CheckResult -Category "text_file_format" -CheckName "No UTF-8 BOM in text files" `
    -Passed ($bomFiles.Count -eq 0) `
    -Message "Files with UTF-8 BOM: $($bomFiles.Count)" `
    -FixSuggestion "Save files as UTF-8 without BOM: $($bomFiles -join ', ')" `
    -Critical $false

# ============================================
# 11. ClawHub Specific Requirements
# ============================================
Write-Host "`n## 11. ClawHub Specific Requirements" -ForegroundColor Yellow

# 11.1 Skill name check
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $skillName = $packageJson.name
        
        # Check name is reasonable
        $isValidName = $skillName -match "^[a-z0-9\-]+$" -and $skillName.Length -ge 3 -and $skillName.Length -le 50
        $isNotPlaceholder = $skillName -notmatch "test|example|demo|placeholder|TODO"
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "Skill name format" `
            -Passed $isValidName -Message "Skill name: $skillName" `
            -FixSuggestion "Skill name should be lowercase with hyphens, 3-50 chars" `
            -Critical $true
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "Skill name not placeholder" `
            -Passed $isNotPlaceholder -Message "Placeholder check: $(if($isNotPlaceholder){'not placeholder'}else{'placeholder'})" `
            -FixSuggestion "Use real skill name, not placeholder" `
            -Critical $true
    } catch {
        # Ignore error
    }
}

# ============================================
# Generate Summary Report
# ============================================
Write-Host "`n=== Audit Summary ===" -ForegroundColor Cyan

# Calculate scores
$totalChecks = 0
$passedChecks = 0
$criticalIssues = 0

foreach ($category in $categories.Keys) {
    $categoryData = $auditResults.categories[$category]
    if ($categoryData.total -gt 0) {
        $categoryScore = [math]::Round(($categoryData.passed / $categoryData.total) * 100)
        $auditResults.categories[$category].score = $categoryScore
        
        $totalChecks += $categoryData.total
        $passedChecks += $categoryData.passed
        
        # Count critical issues in this category
        foreach ($check in $categoryData.checks) {
            if (-not $check.passed -and $check.critical) {
                $criticalIssues++
            }
        }
        
        # Display category score
        $color = if ($categoryScore -ge 90) { "Green" } elseif ($categoryScore -ge 70) { "Yellow" } else { "Red" }
        Write-Host "$($categories[$category]): $categoryScore%" -ForegroundColor $color
    }
}

$overallScore = if ($totalChecks -gt 0) { [math]::Round(($passedChecks / $totalChecks) * 100) } else { 0 }
$auditResults.score.total = $totalChecks
$auditResults.score.passed = $passedChecks
$auditResults.score.percentage = $overallScore

Write-Host "`nOverall Score: $overallScore%" -ForegroundColor $(if ($overallScore -ge 95) { "Green" } elseif ($overallScore -ge 80) { "Yellow" } else { "Red" })
Write-Host "Total Checks: $totalChecks" -ForegroundColor White
Write-Host "Passed Checks: $passedChecks" -ForegroundColor Green
Write-Host "Critical Issues: $criticalIssues" -ForegroundColor $(if ($criticalIssues -eq 0) { "Green" } else { "Red" })

# Final recommendation
if ($overallScore -ge 95 -and $criticalIssues -eq 0) {
    Write-Host "`n✅ RECOMMENDATION: Ready for ClawHub submission!" -ForegroundColor Green
    Write-Host "   Expected ClawHub result: Clean (high confidence)" -ForegroundColor Green
} elseif ($overallScore -ge 80) {
    Write-Host "`n⚠️  RECOMMENDATION: Needs improvement before submission" -ForegroundColor Yellow
    Write-Host "   Fix critical issues first" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ RECOMMENDATION: Not ready for ClawHub" -ForegroundColor Red
    Write-Host "   Major improvements needed" -ForegroundColor Red
}

# Display critical issues if any
if ($auditResults.critical_issues.Count -gt 0) {
    Write-Host "`n❌ Critical Issues (Must Fix):" -ForegroundColor Red
    foreach ($issue in $auditResults.critical_issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

# Display warnings if any
if ($auditResults.warning_issues.Count -gt 0) {
    Write-Host "`n⚠️  Warnings (Recommended to Fix):" -ForegroundColor Yellow
    foreach ($issue in $auditResults.warning_issues) {
        Write-Host "  - $issue" -ForegroundColor Yellow
    }
}

# Save report
$reportFile = Join-Path $OutputDir "ultimate_audit_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$auditResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`nDetailed report saved to: $reportFile" -ForegroundColor Cyan
Write-Host "=== Audit Complete ===" -ForegroundColor Cyan