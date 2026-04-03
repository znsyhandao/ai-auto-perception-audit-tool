# ultimate_clawhub_audit_en.ps1
# Ultimate ClawHub Audit Tool - Ensure 100% one-time pass
# Based on 2026-03-27 AISleepGen scanning failure lessons

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\ultimate_audit",
    [switch]$StrictMode = $true,
    [switch]$AutoFix = $false
)

Write-Host "=== Ultimate ClawHub Audit ===" -ForegroundColor Cyan
Write-Host "Goal: Ensure skill 100% passes ClawHub scan on first try" -ForegroundColor Cyan
Write-Host "Mode: $($StrictMode ? 'Strict Mode' : 'Standard Mode')" -ForegroundColor Cyan
Write-Host "Auto Fix: $($AutoFix ? 'Enabled' : 'Disabled')" -ForegroundColor Cyan
Write-Host "Audit Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Check 1: Skill directory exists
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] Skill directory not found: $SkillDir" -ForegroundColor Red
    exit 1
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
    "clawhub_specific" = "ClawHub Specific"
}

foreach ($category in $categories.Keys) {
    $auditResults.categories[$category] = @{
        "checks" = @()
        "passed" = 0
        "total" = 0
        "score" = 0
    }
}

# Helper functions
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
            $auditResults.critical_issues += "${Category}: ${Message}"
        } else {
            Write-Host "  [WARN] $CheckName" -ForegroundColor Yellow
            $auditResults.warning_issues += "${Category}: ${Message}"
        }
        
        if ($FixSuggestion) {
            Write-Host "      Suggestion: $FixSuggestion" -ForegroundColor Cyan
            $auditResults.recommendations += $FixSuggestion
        }
    }
}

function Calculate-Scores {
    # Calculate category scores
    foreach ($category in $auditResults.categories.Keys) {
        $cat = $auditResults.categories[$category]
        if ($cat.total -gt 0) {
            $cat.score = [math]::Round(($cat.passed / $cat.total) * 100, 2)
        }
    }
    
    # Calculate overall score
    $totalChecks = 0
    $passedChecks = 0
    
    foreach ($category in $auditResults.categories.Keys) {
        $totalChecks += $auditResults.categories[$category].total
        $passedChecks += $auditResults.categories[$category].passed
    }
    
    if ($totalChecks -gt 0) {
        $auditResults.score.total = $totalChecks
        $auditResults.score.passed = $passedChecks
        $auditResults.score.percentage = [math]::Round(($passedChecks / $totalChecks) * 100, 2)
    }
}

# ============================================
# 1. File Structure Check
# ============================================
Write-Host "## 1. File Structure Check" -ForegroundColor Yellow

# 1.1 Required files check
$requiredFiles = @("skill.py", "config.yaml", "SKILL.md", "package.json")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    $exists = Test-Path $filePath
    
    Add-CheckResult -Category "file_structure" -CheckName "Required file: $file" `
        -Passed $exists -Message "$file $(if($exists){'exists'}else{'not found'})" `
        -FixSuggestion "Create $file file" -Critical $true
}

# 1.2 Prohibited files check
$prohibitedExtensions = @(".ps1", ".bat", ".exe", ".dll", ".backup", ".tmp", ".log")
$prohibitedFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $prohibitedExtensions -contains $_.Extension
}

Add-CheckResult -Category "file_structure" -CheckName "No prohibited files" `
    -Passed ($prohibitedFiles.Count -eq 0) `
    -Message "Found $($prohibitedFiles.Count) prohibited files" `
    -FixSuggestion "Remove all prohibited files: $($prohibitedFiles.Name -join ', ')" `
    -Critical $true

# 1.3 File count check
$totalFiles = (Get-ChildItem -Path $SkillDir -File -Recurse | Measure-Object).Count
Add-CheckResult -Category "file_structure" -CheckName "Reasonable file count" `
    -Passed ($totalFiles -le 50) `
    -Message "Total files: $totalFiles (recommended 鈮?50)" `
    -FixSuggestion "Reduce unnecessary files, keep it clean"

# ============================================
# 2. Version Consistency Check (CRITICAL!)
# ============================================
Write-Host "`n## 2. Version Consistency Check" -ForegroundColor Yellow

# Collect version numbers from all files
$versionSources = @()

# 2.1 config.yaml version
$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match "version:\s*['\""]?([\d\.]+)['\""]?") {
        $versionSources += @{
            "file" = "config.yaml"
            "version" = $matches[1]
        }
    }
}

# 2.2 package.json version
$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    $packageContent = Get-Content $packagePath -Raw
    if ($packageContent -match '"version":\s*"([\d\.]+)"') {
        $versionSources += @{
            "file" = "package.json"
            "version" = $matches[1]
        }
    }
}

# 2.3 skill.py version
$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    if ($skillContent -match "version\s*=\s*['\""]([\d\.]+)['\""]") {
        $versionSources += @{
            "file" = "skill.py"
            "version" = $matches[1]
        }
    }
}

# 2.4 SKILL.md version
$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    if ($skillMdContent -match "version[:\s]+([\d\.]+)") {
        $versionSources += @{
            "file" = "SKILL.md"
            "version" = $matches[1]
        }
    }
}

# 2.5 Check version consistency
if ($versionSources.Count -gt 0) {
    # Get first version as baseline
    $baseVersion = $versionSources[0].version
    $allSame = $true
    $differentVersions = @()
    
    foreach ($source in $versionSources) {
        if ($source.version -ne $baseVersion) {
            $allSame = $false
            $differentVersions += "$($source.file): $($source.version)"
        }
    }
    
    Add-CheckResult -Category "version_consistency" -CheckName "Version numbers consistent" `
        -Passed $allSame -Message "Found inconsistent versions: $($differentVersions -join '; ')" `
        -FixSuggestion "Unify all file versions to: $baseVersion" `
        -Critical $true
    
    # 2.6 Version format check
    $isValidVersion = $baseVersion -match "^\d+\.\d+\.\d+$"
    Add-CheckResult -Category "version_consistency" -CheckName "Version format valid" `
        -Passed $isValidVersion -Message "Version format: $baseVersion" `
        -FixSuggestion "Use semantic versioning: MAJOR.MINOR.PATCH" `
        -Critical $false
} else {
    Add-CheckResult -Category "version_consistency" -CheckName "Version numbers found" `
        -Passed $false -Message "No version numbers found in any files" `
        -FixSuggestion "Add version numbers to config.yaml, package.json, etc." `
        -Critical $true
}

# ============================================
# 3. Security Compliance Check
# ============================================
Write-Host "`n## 3. Security Compliance Check" -ForegroundColor Yellow

# 3.1 Network code check
$networkPatterns = @("import requests", "import urllib", "import socket", "import http\.client")
$networkIssues = @()

if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    foreach ($pattern in $networkPatterns) {
        if ($skillContent -match $pattern) {
            $networkIssues += $pattern
        }
    }
}

Add-CheckResult -Category "security_compliance" -CheckName "No network code" `
    -Passed ($networkIssues.Count -eq 0) `
    -Message "Found network code: $($networkIssues -join ', ')" `
    -FixSuggestion "Remove all network-related imports" `
    -Critical $true

# 3.2 Dangerous functions check
$dangerousPatterns = @("subprocess\.", "os\.system", "eval\(", "exec\(", "__import__\(")
$dangerousIssues = @()

if (Test-Path $skillPath) {
    foreach ($pattern in $dangerousPatterns) {
        if ($skillContent -match $pattern) {
            $dangerousIssues += $pattern
        }
    }
}

Add-CheckResult -Category "security_compliance" -CheckName "No dangerous functions" `
    -Passed ($dangerousIssues.Count -eq 0) `
    -Message "Found dangerous functions: $($dangerousIssues -join ', ')" `
    -FixSuggestion "Remove all dangerous function calls" `
    -Critical $true

# 3.3 config.yaml security declarations
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    $hasSecuritySection = $configContent -match "security:"
    $hasNetworkAccessFalse = $configContent -match "network_access:\s*false"
    $hasLocalOnlyTrue = $configContent -match "local_only:\s*true"
    
    Add-CheckResult -Category "security_compliance" -CheckName "config.yaml security declarations" `
        -Passed ($hasSecuritySection -and $hasNetworkAccessFalse -and $hasLocalOnlyTrue) `
        -Message "Security declarations: $(if($hasSecuritySection){'has security section'}else{'no security section'})" `
        -FixSuggestion "Add complete security declarations to config.yaml" `
        -Critical $true
}

# ============================================
# 4. Documentation Quality Check
# ============================================
Write-Host "`n## 4. Documentation Quality Check" -ForegroundColor Yellow

# 4.1 SKILL.md completeness
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    $hasOverview = $skillMdContent -match "Overview|Introduction"
    $hasSecurity = $skillMdContent -match "Security|Safety"
    $hasUsage = $skillMdContent -match "Usage|Examples|How to use"
    $hasCommands = $skillMdContent -match "Commands|Features|Functions"
    
    $docComplete = $hasOverview -and $hasSecurity -and $hasUsage -and $hasCommands
    
    Add-CheckResult -Category "documentation_quality" -CheckName "SKILL.md completeness" `
        -Passed $docComplete `
        -Message "Documentation completeness: Overview=$hasOverview, Security=$hasSecurity, Usage=$hasUsage, Commands=$hasCommands" `
        -FixSuggestion "Complete SKILL.md with all required sections" `
        -Critical $false
}

# 4.2 README.md existence
$readmePath = Join-Path $SkillDir "README.md"
Add-CheckResult -Category "documentation_quality" -CheckName "README.md exists" `
    -Passed (Test-Path $readmePath) `
    -Message "README.md $(if(Test-Path $readmePath){'exists'}else{'not found'})" `
    -FixSuggestion "Create README.md file" `
    -Critical $false

# 4.3 CHANGELOG.md existence
$changelogPath = Join-Path $SkillDir "CHANGELOG.md"
Add-CheckResult -Category "documentation_quality" -CheckName "CHANGELOG.md exists" `
    -Passed (Test-Path $changelogPath) `
    -Message "CHANGELOG.md $(if(Test-Path $changelogPath){'exists'}else{'not found'})" `
    -FixSuggestion "Create CHANGELOG.md to record version changes" `
    -Critical $false

# ============================================
# 5. Metadata Validation
# ============================================
Write-Host "`n## 5. Metadata Validation" -ForegroundColor Yellow

# 5.1 package.json basic info
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        $hasName = ![string]::IsNullOrEmpty($packageJson.name)
        $hasDescription = ![string]::IsNullOrEmpty($packageJson.description)
        $hasAuthor = ![string]::IsNullOrEmpty($packageJson.author)
        $hasLicense = ![string]::IsNullOrEmpty($packageJson.license)
        
        $metadataComplete = $hasName -and $hasDescription -and $hasAuthor -and $hasLicense
        
        Add-CheckResult -Category "metadata_validation" -CheckName "package.json basic info" `
            -Passed $metadataComplete `
            -Message "Metadata completeness: Name=$hasName, Description=$hasDescription, Author=$hasAuthor, License=$hasLicense" `
            -FixSuggestion "Complete basic info in package.json" `
            -Critical $true
    } catch {
        Add-CheckResult -Category "metadata_validation" -CheckName "package.json format valid" `
            -Passed $false -Message "package.json format error: $_" `
            -FixSuggestion "Fix package.json JSON format" `
            -Critical $true
    }
}

# 5.2 Author info validity
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $author = $packageJson.author
        
        # Check if author info is reasonable
        $isValidAuthor = $author -notmatch "test|example|demo|placeholder|TODO|FIXME"
        $isValidAuthor = $isValidAuthor -and $author.Length -ge 2 -and $author.Length -le 100
        
        Add-CheckResult -Category "metadata_validation" -CheckName "Author info reasonable" `
            -Passed $isValidAuthor `
            -Message "Author info: $author" `
            -FixSuggestion "Use real and reasonable author information" `
            -Critical $false
    } catch {
        # Ignore error, already checked above
    }
}

# ============================================
# 6. Link Validation (CRITICAL!)
# ============================================
Write-Host "`n## 6. Link Validation" -ForegroundColor Yellow

# 6.1 Collect all links
$allLinks = @()

# Collect links from README.md
if (Test-Path $readmePath) {
    $readmeContent = Get-Content $readmePath -Raw
    $urlMatches = [regex]::Matches($readmeContent, 'https?://[^\s<>"''\)]+')
    foreach ($match in $urlMatches) {
        $allLinks += @{
            "file" = "README.md"
            "url" = $match.Value
            "context" = $match.Value.Substring(0, [math]::Min(50, $match.Value.Length))
        }
    }
}

# Collect links from SKILL.md
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    $urlMatches = [regex]::Matches($skillMdContent, 'https?://[^\s<>"''\)]+')
    foreach ($match in $urlMatches) {
        $allLinks += @{
            "file" = "SKILL.md"
            "url" = $match.Value
            "context" = $match.Value.Substring(0, [math]::Min(50, $match.Value.Length))
        }
    }
}

# Collect links from package.json
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        if ($packageJson.repository -and $packageJson.repository.url) {
            $allLinks += @{
                "file" = "package.json"
                "url" = $packageJson.repository.url
                "context" = "repository"
            }
        }
        
        if ($packageJson.homepage) {
            $allLinks += @{
                "file" = "package.json"
                "url" = $packageJson.homepage
                "context" = "homepage"
            }
        }
        
        if ($packageJson.bugs -and $packageJson.bugs.url) {
            $allLinks += @{
                "file" = "package.json"
                "url" = $packageJson.bugs.url
                "context" = "bugs"
            }
        }
    } catch {
        # Ignore error
    }
}

# 6.2 Check link validity
$validLinks = 0
$invalidLinks = @()

foreach ($link in $allLinks) {
    $url = $link.url
    
    # Check URL format
    $isValidFormat = $url -match '^https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}'
    
    # Check if placeholder
    $isPlaceholder = $url -match 'example\.com|placeholder|TODO|FIXME|your-username|your-repo'
    
    if ($isValidFormat -and (-not $isPlaceholder)) {
        $validLinks++
    } else {
        $invalidLinks += "$($link.file): $url ($($link.context))"
    }
}

$totalLinks = $allLinks.Count
$allLinksValid = $invalidLinks.Count -eq 0

Add-CheckResult -Category "link_validation" -CheckName "All links real and valid" `
    -Passed $allLinksValid `
    -Message "Link validity: $validLinks/$totalLinks valid, invalid: $($invalidLinks.Count)" `
    -FixSuggestion "Fix invalid links: $($invalidLinks -join '; ')" `
    -Critical $true

# 6.3 GitHub link specific check
$githubLinks = $allLinks | Where-Object { $_.url -match 'github\.com' }
if ($githubLinks.Count -gt 0) {
    $validGithubLinks = $githubLinks | Where-Object { 
        $_.url -match 'github\.com/[a-zA-Z0-9\-]+/[a-zA-Z0-9\-]+'
    }
    
    Add-CheckResult -Category "link_validation" -CheckName "GitHub links format correct" `
        -Passed ($validGithubLinks.Count -eq $githubLinks.Count) `
        -Message "GitHub links: $($validGithubLinks.Count)/$($githubLinks.Count) format correct" `
        -FixSuggestion "Ensure GitHub links format: https://github.com/username/repository" `
        -Critical $false
}

# ============================================
# 7. Code Quality Check
# ============================================
Write-Host "`n## 7. Code Quality Check" -ForegroundColor Yellow

# 7.1 Python syntax check
if (Test-Path $skillPath) {
    try {
        # Try to check syntax by importing
        $pythonCheck = python -m py_compile $skillPath 2>&1
        $syntaxValid = $LASTEXITCODE -eq 0
        
        Add-CheckResult -Category "code_quality" -CheckName "Python syntax correct" `
            -Passed $syntaxValid `
            -Message "Python syntax check: $(if($syntaxValid){'passed'}else{'failed'})" `
            -FixSuggestion "Fix Python syntax errors: $pythonCheck" `
            -Critical $true
    } catch {
        Add-CheckResult -Category "code_quality" -CheckName "Python syntax check" `
            -Passed $false -Message "Cannot execute Python syntax check" `
            -FixSuggestion "Manually check Python syntax" `
            -Critical $false
    }
}

# 7.2 Import module check
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $importLines = Select-String -Path $skillPath -Pattern "^import |^from " | Select-Object -ExpandProperty Line
    
    # Check stdlib vs third-party imports
    $stdlibImports = @()
    $externalImports = @()
    
    $commonStdlib = @("os", "sys", "json", "csv", "math", "statistics", "datetime", 
                     "time", "pathlib", "typing", "dataclasses", "enum", "collections",
                     "re", "hashlib", "base64", "random", "fractions", "decimal")
    
    foreach ($line in $importLines) {
        $isStdlib = $false
        foreach ($stdlib in $commonStdlib) {
            if ($line -match "\b$stdlib\b") {
                $isStdlib = $true
                break
            }
        }
        
        if ($isStdlib) {
            $stdlibImports += $line
        } else {
            $externalImports += $line
        }
    }
    
    $hasExternalImports = $externalImports.Count -gt 0
    
    Add-CheckResult -Category "code_quality" -CheckName "Only stdlib imports (as declared)" `
        -Passed (-not $hasExternalImports) `
        -Message "Import analysis: stdlib=$($stdlibImports.Count), external=$($externalImports.Count)" `
        -FixSuggestion "Remove external dependency imports: $($externalImports -join '; ')" `
        -Critical $false
}

# 7.3 Code comments check
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $totalLines = ($skillContent -split "`n").Count
    $commentLines = (Select-String -Path $skillPath -Pattern "^#|^\s*#" | Measure-Object).Count
    
    $commentRatio = if ($totalLines -gt 0) { [math]::Round(($commentLines / $totalLines) * 100, 2) } else { 0 }
    $hasGoodComments = $commentRatio -ge 10  # At least 10% comments
    
    Add-CheckResult -Category "code_quality" -CheckName "Sufficient code comments" `
        -Passed $hasGoodComments `
        -Message "Code comment ratio: $commentRatio% ($commentLines/$totalLines lines)" `
        -FixSuggestion "Add more code comments, target 鈮?0%" `
        -Critical $false
}

# ============================================
# 8. Dependency Validation
# ============================================
Write-Host "`n## 8. Dependency Validation" -ForegroundColor Yellow

# 8.1 requirements.txt check
$requirementsPath = Join-Path $SkillDir "requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath
    $hasRequirements = $requirementsContent.Count -gt 0
    
    # Check for external dependencies
    $hasExternalDeps = $false
    foreach ($line in $requirementsContent) {
        $line = $line.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $hasExternalDeps = $true
            break
        }
    }
    
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txt dependency declarations" `
        -Passed $hasRequirements `
        -Message "requirements.txt: $(if($hasRequirements){'has dependencies'}else{'empty or none'})" `
        -FixSuggestion "If external dependencies, declare in requirements.txt" `
        -Critical $false
    
    # If declares "stdlib only", should not have external dependencies
    if (Test-Path $skillMdPath) {
        $skillMdContent = Get-Content $skillMdPath -Raw
        $declaresStdlibOnly = $skillMdContent -match "stdlib only|no external dependencies|standard library only"
        
        if ($declaresStdlibOnly -and $hasExternalDeps) {
            Add-CheckResult -Category "dependency_validation" -CheckName "Declarations match dependencies" `
                -Passed $false `
                -Message "Declares 'stdlib only' but requirements.txt has external dependencies" `
                -FixSuggestion "Either remove external dependencies or modify declaration" `
                -Critical $true
        }
    }
} else {
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txt exists" `
        -Passed $false `
        -Message "requirements.txt not found" `
        -FixSuggestion "Create requirements.txt file (can be empty)" `
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
# 10. ClawHub Specific Requirements
# ============================================
Write-Host "`n## 10. ClawHub Specific Requirements" -ForegroundColor Yellow

# 10.1 Skill name check
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $skillName = $packageJson.name
        
        # Check name is reasonable
        $isValidName = $skillName -match "^[a-z0-9\-]+$" -and $skillName.Length -ge 3 -and $skillName.Length -le 50
        $isNotPlaceholder = $skillName -notmatch "test|example|demo|placeholder|TODO"
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "Skill name format correct" `
            -Passed ($isValidName -and $isNotPlaceholder) `
            -Message "Skill name: $skillName" `
            -FixSuggestion "Use lowercase letters, numbers, hyphens, avoid placeholders" `
            -Critical $true
    } catch {
        # Ignore error
    }
}

# 10.2 Skill description check
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $description = $packageJson.description
        
        # Check description is reasonable
        $hasDescription = ![string]::IsNullOrEmpty($description)
        $descriptionLength = if ($description) { $description.Length } else { 0 }
        $isValidDescription = $hasDescription -and $descriptionLength -ge 10 -and $descriptionLength -le 200
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "Skill description reasonable" `
            -Passed $isValidDescription `
            -Message "Description length: $descriptionLength characters" `
            -FixSuggestion "Provide meaningful description (10-200 characters)" `
            -Critical $false
    } catch {
        # Ignore error
    }
}

# 10.3 Skill categories check
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasCategories = $packageJson.categories -and $packageJson.categories.Count -gt 0
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "Skill categories set" `
            -Passed $hasCategories `
            -Message "Skill categories: $(if($hasCategories){'set'}else{'not set'})" `
            -FixSuggestion "Add categories field to package.json" `
            -Critical $false
    } catch {
        # Ignore error
    }
}

# ============================================
# Calculate Scores and Generate Report
# ============================================

# Calculate scores
Calculate-Scores

# Generate detailed report
Write-Host "`n=== Ultimate Audit Report ===" -ForegroundColor Cyan
Write-Host "Audit completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Overall compliance score: $($auditResults.score.percentage)%"
Write-Host "Total checks: $($auditResults.score.total)"
Write-Host "Passed checks: $($auditResults.score.passed)"
Write-Host "Failed checks: $($auditResults.score.total - $auditResults.score.passed)"

# Category report
Write-Host "`n## Category Scores" -ForegroundColor Yellow
foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $auditResults.categories[$categoryKey].score
    
    $color = if ($categoryScore -ge 90) { "Green" } 
             elseif ($categoryScore -ge 70) { "Yellow" } 
             else { "Red" }
    
    Write-Host "$categoryName: $categoryScore%" -ForegroundColor $color
}

# Critical issues report
if ($auditResults.critical_issues.Count -gt 0) {
    Write-Host "`n## 鉂?Critical Issues (Must Fix)" -ForegroundColor Red
    foreach ($issue in $auditResults.critical_issues) {
        Write-Host "  鈥?$issue" -ForegroundColor Red
    }
} else {
    Write-Host "`n## 鉁?No Critical Issues" -ForegroundColor Green
}

# Warning issues report
if ($auditResults.warning_issues.Count -gt 0) {
    Write-Host "`n## 鈿狅笍  Warning Issues (Recommended to Fix)" -ForegroundColor Yellow
    foreach ($issue in $auditResults.warning_issues) {
        Write-Host "  鈥?$issue" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n## 鉁?No Warning Issues" -ForegroundColor Green
}

# Recommendations report
if ($auditResults.recommendations.Count -gt 0) {
    Write-Host "`n## 馃挕 Improvement Recommendations" -ForegroundColor Cyan
    $uniqueRecommendations = $auditResults.recommendations | Select-Object -Unique
    foreach ($rec in $uniqueRecommendations) {
        Write-Host "  鈥?$rec" -ForegroundColor Cyan
    }
}

# Generate JSON report
$reportFile = Join-Path $OutputDir "ultimate_audit_report.json"
$auditResults | ConvertTo-Json -Depth 10 | Set-Content -Path $reportFile

# Generate Markdown report
$mdReport = @"
# Ultimate ClawHub Audit Report

## Audit Information
- **Audit Time**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **Skill Directory**: $SkillDir
- **Audit Mode**: $($StrictMode ? 'Strict' : 'Standard')
- **Auto Fix**: $($AutoFix ? 'Enabled' : 'Disabled')

## Overall Score
**Compliance Score: $($auditResults.score.percentage)%**

| Check Category | Score | Status |
|----------------|-------|--------|
"@

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $auditResults.categories[$categoryKey].score
    $status = if ($categoryScore -
ge 90) { "鉁?Excellent" } 
              elseif ($categoryScore -ge 70) { "鈿狅笍  Good" } 
              else { "鉂?Needs Improvement" }
    
    $mdReport += "| $categoryName | $categoryScore% | $status |`n"
}

$mdReport += @"

## Detailed Check Results

### Critical Issues (Must Fix)
"@

if ($auditResults.critical_issues.Count -gt 0) {
    foreach ($issue in $auditResults.critical_issues) {
        $mdReport += "- 鉂?$issue`n"
    }
} else {
    $mdReport += "- 鉁?No critical issues`n"
}

$mdReport += @"

### Warning Issues (Recommended to Fix)
"@

if ($auditResults.warning_issues.Count -gt 0) {
    foreach ($issue in $auditResults.warning_issues) {
        $mdReport += "- 鈿狅笍  $issue`n"
    }
} else {
    $mdReport += "- 鉁?No warning issues`n"
}

$mdReport += @"

### Improvement Recommendations
"@

if ($auditResults.recommendations.Count -gt 0) {
    $uniqueRecommendations = $auditResults.recommendations | Select-Object -Unique
    foreach ($rec in $uniqueRecommendations) {
        $mdReport += "- 馃挕 $rec`n"
    }
} else {
    $mdReport += "- 鉁?No improvement recommendations`n"
}

$mdReport += @"

## Key Findings

### 1. Version Consistency
"@

if ($versionSources.Count -gt 0) {
    $mdReport += "Found version numbers in: `n"
    foreach ($source in $versionSources) {
        $mdReport += "- $($source.file): $($source.version)`n"
    }
}

$mdReport += @"

### 2. Link Validation
- Total links: $totalLinks
- Valid links: $validLinks
- Invalid links: $($invalidLinks.Count)

### 3. Security Compliance
- Network code: $($networkIssues.Count) instances
- Dangerous functions: $($dangerousIssues.Count) instances
- Security declarations: $(if($hasSecuritySection){'complete'}else{'missing'})

## Audit Conclusion

"@

if ($auditResults.score.percentage -ge 95) {
    $mdReport += "**鉁?Excellent! Skill highly complies with ClawHub requirements, expected to pass on first try.**`n`n"
    $mdReport += "Recommendation: Can be directly published to ClawHub."
} elseif ($auditResults.score.percentage -ge 85) {
    $mdReport += "**鈿狅笍  Good, but needs some fixes.**`n`n"
    $mdReport += "Recommendation: Fix all critical issues before publishing."
} elseif ($auditResults.score.percentage -ge 70) {
    $mdReport += "**鉂?Needs improvement, multiple issues found.**`n`n"
    $mdReport += "Recommendation: Fix all issues comprehensively before publishing."
} else {
    $mdReport += "**馃毇 Does not meet requirements, needs major improvements.**`n`n"
    $mdReport += "Recommendation: Redesign skill to meet all requirements."
}

$mdReport += @"

## Keys to One-Time ClawHub Pass

Based on this audit, to ensure one-time ClawHub pass:

1. **Version consistency**: All file versions must be 100% consistent
2. **Link validity**: All links must be real and accessible, no placeholders
3. **Security declarations**: config.yaml must have complete security declarations
4. **No network code**: Completely remove all network-related code
5. **Documentation completeness**: All required documents must be complete
6. **Metadata reasonableness**: Author, description, etc. must be real and reasonable
7. **Code quality**: Syntax correct, sufficient comments
8. **License compliance**: Have appropriate license file

## Next Steps

### If score 鈮?95%
1. Prepare publishing materials
2. Upload to ClawHub
3. Monitor review results

### If score 85-94%
1. Fix all critical issues
2. Fix major warning issues
3. Re-run audit
4. Ensure score 鈮?95%

### If score < 85%
1. Review all issues comprehensively
2. Create fix plan
3. Fix issues one by one
4. Re-run audit until target reached

---

**Report Generated**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**Audit Tool Version**: v1.0 (Ultimate Edition)  
**Target Score**: 鈮?95% (Ensure one-time pass)  
**Audit Standard**: ClawHub Deep Compliance + One-Time Pass Requirements
"@

$mdReportFile = Join-Path $OutputDir "ultimate_audit_report.md"
Set-Content -Path $mdReportFile -Value $mdReport

Write-Host "`nDetailed reports saved to:" -ForegroundColor Cyan
Write-Host "  JSON Report: $reportFile" -ForegroundColor Cyan
Write-Host "  Markdown Report: $mdReportFile" -ForegroundColor Cyan

# Final recommendation
Write-Host "`n=== Final Recommendation ===" -ForegroundColor Cyan

if ($auditResults.score.percentage -ge 95) {
    Write-Host "馃帀 Congratulations! Skill highly complies with ClawHub requirements!" -ForegroundColor Green
    Write-Host "Recommendation: Can be directly published to ClawHub, expected to pass on first try." -ForegroundColor Green
} elseif ($auditResults.score.percentage -ge 85) {
    Write-Host "鈿狅笍  Good, but needs some fixes." -ForegroundColor Yellow
    Write-Host "Recommendation: Fix all critical issues before publishing." -ForegroundColor Yellow
} elseif ($auditResults.score.percentage -ge 70) {
    Write-Host "鉂?Needs improvement, multiple issues found." -ForegroundColor Red
    Write-Host "Recommendation: Fix all issues comprehensively before publishing." -ForegroundColor Red
} else {
    Write-Host "馃毇 Does not meet requirements, needs major improvements." -ForegroundColor DarkRed
    Write-Host "Recommendation: Redesign skill to meet all requirements." -ForegroundColor DarkRed
}

Write-Host "`nAudit completed. Please review detailed reports for specific improvement suggestions." -ForegroundColor White
Write-Host "Goal: Ensure skill passes ClawHub review on first try!" -ForegroundColor Cyan
