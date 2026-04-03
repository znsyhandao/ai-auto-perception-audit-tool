# ultimate_clawhub_audit.ps1
# ç»æClawHubå®¡æ ¸å·¥å· - ç¡®ä¿100%ä¸æ¬¡æ§éè¿
# åºäº2026-03-27æææè®­åç»éª

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\ultimate_audit",
    [switch]$StrictMode = $true,
    [switch]$AutoFix = $false
)

Write-Host "=== ç»æClawHubå®¡æ ¸ ===" -ForegroundColor Cyan
Write-Host "ç®æ : ç¡®ä¿æè?00%ä¸æ¬¡æ§éè¿ClawHubæ«æ" -ForegroundColor Cyan
Write-Host "æ¨¡å¼: $($StrictMode ? 'ä¸¥æ ¼æ¨¡å¼' : 'æ åæ¨¡å¼')" -ForegroundColor Cyan
Write-Host "èªå¨ä¿®å¤: $($AutoFix ? 'å¯ç¨' : 'ç¦ç¨')" -ForegroundColor Cyan
Write-Host "æ£æ¥æ¶é? $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# åå»ºè¾åºç®å½
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# åå§åå®¡æ ¸ç»æ?$auditResults = @{
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

# åç±»å®ä¹
$categories = @{
    "file_structure" = "æä»¶ç»æ"
    "version_consistency" = "çæ¬ä¸è´æ?
    "security_compliance" = "å®å¨åè§"
    "documentation_quality" = "ææ¡£è´¨é"
    "metadata_validation" = "åæ°æ®éªè¯?
    "link_validation" = "é¾æ¥éªè¯"
    "code_quality" = "ä»£ç è´¨é"
    "dependency_validation" = "ä¾èµéªè¯"
    "license_compliance" = "è®¸å¯è¯åè§?
    "clawhub_specific" = "ClawHubç¹å®è¦æ±"
}

foreach ($category in $categories.Keys) {
    $auditResults.categories[$category] = @{
        "checks" = @()
        "passed" = 0
        "total" = 0
        "score" = 0
    }
}

# è¾å©å½æ°
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
        Write-Host "  â?$CheckName" -ForegroundColor Green
    } else {
        if ($Critical) {
            Write-Host "  â?$CheckName (ä¸¥é)" -ForegroundColor Red
            $auditResults.critical_issues += "$Category: $Message"
        } else {
            Write-Host "  â ï¸  $CheckName" -ForegroundColor Yellow
            $auditResults.warning_issues += "$Category: $Message"
        }
        
        if ($FixSuggestion) {
            Write-Host "     å»ºè®®: $FixSuggestion" -ForegroundColor Cyan
            $auditResults.recommendations += $FixSuggestion
        }
    }
}

function Calculate-Scores {
    # è®¡ç®åç±»åæ°
    foreach ($category in $auditResults.categories.Keys) {
        $cat = $auditResults.categories[$category]
        if ($cat.total -gt 0) {
            $cat.score = [math]::Round(($cat.passed / $cat.total) * 100, 2)
        }
    }
    
    # è®¡ç®æ»ä½åæ°
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
# 1. æä»¶ç»ææ£æ?# ============================================
Write-Host "## 1. æä»¶ç»ææ£æ? -ForegroundColor Yellow

# 1.1 å¿éæä»¶æ£æ?$requiredFiles = @("skill.py", "config.yaml", "SKILL.md", "package.json")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    $exists = Test-Path $filePath
    
    Add-CheckResult -Category "file_structure" -CheckName "å¿éæä»¶: $file" `
        -Passed $exists -Message "$file $(if($exists){'å­å¨'}else{'ä¸å­å?})" `
        -FixSuggestion "åå»º $file æä»¶" -Critical $true
}

# 1.2 ç¦æ­¢æä»¶æ£æ?$prohibitedExtensions = @(".ps1", ".bat", ".exe", ".dll", ".backup", ".tmp", ".log")
$prohibitedFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $prohibitedExtensions -contains $_.Extension
}

Add-CheckResult -Category "file_structure" -CheckName "æ ç¦æ­¢æä»? `
    -Passed ($prohibitedFiles.Count -eq 0) `
    -Message "åç° $($prohibitedFiles.Count) ä¸ªç¦æ­¢æä»? `
    -FixSuggestion "å é¤ææç¦æ­¢æä»? $($prohibitedFiles.Name -join ', ')" `
    -Critical $true

# 1.3 æä»¶æ°éæ£æ?$totalFiles = (Get-ChildItem -Path $SkillDir -File -Recurse | Measure-Object).Count
Add-CheckResult -Category "file_structure" -CheckName "æä»¶æ°éåç" `
    -Passed ($totalFiles -le 50) `
    -Message "æ»æä»¶æ°: $totalFiles (å»ºè®® â?50)" `
    -FixSuggestion "åå°ä¸å¿è¦çæä»¶ï¼ä¿æç®æ´?

# ============================================
# 2. çæ¬ä¸è´æ§æ£æ?(å³é®ï¼?
# ============================================
Write-Host "`n## 2. çæ¬ä¸è´æ§æ£æ? -ForegroundColor Yellow

# æ¶éæææä»¶ä¸­ççæ¬å·
$versionSources = @()

# 2.1 config.yamlçæ¬å?$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match "version:\s*['\""]?([\d\.]+)['\""]?") {
        $versionSources += @{
            "file" = "config.yaml"
            "version" = $matches[1]
            "line" = ($configContent -split "`n" | Select-String "version:" | Select-Object -First 1).LineNumber
        }
    }
}

# 2.2 package.jsonçæ¬å?$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    $packageContent = Get-Content $packagePath -Raw
    if ($packageContent -match '"version":\s*"([\d\.]+)"') {
        $versionSources += @{
            "file" = "package.json"
            "version" = $matches[1]
        }
    }
}

# 2.3 skill.pyçæ¬å?$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    if ($skillContent -match "version\s*=\s*['\""]([\d\.]+)['\""]") {
        $versionSources += @{
            "file" = "skill.py"
            "version" = $matches[1]
        }
    }
}

# 2.4 SKILL.mdçæ¬å?$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    if ($skillMdContent -match "çæ¬[ï¼?]\s*([\d\.]+)") {
        $versionSources += @{
            "file" = "SKILL.md"
            "version" = $matches[1]
        }
    }
}

# 2.5 æ£æ¥çæ¬ä¸è´æ?if ($versionSources.Count -gt 0) {
    # è·åç¬¬ä¸ä¸ªçæ¬ä½ä¸ºåºå?    $baseVersion = $versionSources[0].version
    $allSame = $true
    $differentVersions = @()
    
    foreach ($source in $versionSources) {
        if ($source.version -ne $baseVersion) {
            $allSame = $false
            $differentVersions += "$($source.file): $($source.version)"
        }
    }
    
    Add-CheckResult -Category "version_consistency" -CheckName "çæ¬å·å®å¨ä¸è? `
        -Passed $allSame -Message "åç°ä¸ä¸è´çæ? $($differentVersions -join '; ')" `
        -FixSuggestion "ç»ä¸æææä»¶çæ¬å·ä¸? $baseVersion" `
        -Critical $true
    
    # 2.6 çæ¬å·æ ¼å¼æ£æ?    $isValidVersion = $baseVersion -match "^\d+\.\d+\.\d+$"
    Add-CheckResult -Category "version_consistency" -CheckName "çæ¬å·æ ¼å¼æ­£ç¡? `
        -Passed $isValidVersion -Message "çæ¬å·æ ¼å¼? $baseVersion" `
        -FixSuggestion "ä½¿ç¨è¯­ä¹åçæ? MAJOR.MINOR.PATCH" `
        -Critical $false
} else {
    Add-CheckResult -Category "version_consistency" -CheckName "æ¾å°çæ¬å? `
        -Passed $false -Message "æªå¨ä»»ä½æä»¶ä¸­æ¾å°çæ¬å·" `
        -FixSuggestion "å¨config.yamlãpackage.jsonç­æä»¶ä¸­æ·»å çæ¬å? `
        -Critical $true
}

# ============================================
# 3. å®å¨åè§æ£æ?# ============================================
Write-Host "`n## 3. å®å¨åè§æ£æ? -ForegroundColor Yellow

# 3.1 ç½ç»ä»£ç æ£æ?$networkPatterns = @("import requests", "import urllib", "import socket", "import http\.client")
$networkIssues = @()

if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    foreach ($pattern in $networkPatterns) {
        if ($skillContent -match $pattern) {
            $networkIssues += $pattern
        }
    }
}

Add-CheckResult -Category "security_compliance" -CheckName "æ ç½ç»ä»£ç ? `
    -Passed ($networkIssues.Count -eq 0) `
    -Message "åç°ç½ç»ä»£ç : $($networkIssues -join ', ')" `
    -FixSuggestion "ç§»é¤ææç½ç»ç¸å³å¯¼å? `
    -Critical $true

# 3.2 å±é©å½æ°æ£æ?$dangerousPatterns = @("subprocess\.", "os\.system", "eval\(", "exec\(", "__import__\(")
$dangerousIssues = @()

if (Test-Path $skillPath) {
    foreach ($pattern in $dangerousPatterns) {
        if ($skillContent -match $pattern) {
            $dangerousIssues += $pattern
        }
    }
}

Add-CheckResult -Category "security_compliance" -CheckName "æ å±é©å½æ? `
    -Passed ($dangerousIssues.Count -eq 0) `
    -Message "åç°å±é©å½æ°: $($dangerousIssues -join ', ')" `
    -FixSuggestion "ç§»é¤ææå±é©å½æ°è°ç? `
    -Critical $true

# 3.3 config.yamlå®å¨å£°æ
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    $hasSecuritySection = $configContent -match "security:"
    $hasNetworkAccessFalse = $configContent -match "network_access:\s*false"
    $hasLocalOnlyTrue = $configContent -match "local_only:\s*true"
    
    Add-CheckResult -Category "security_compliance" -CheckName "config.yamlå®å¨å£°æ" `
        -Passed ($hasSecuritySection -and $hasNetworkAccessFalse -and $hasLocalOnlyTrue) `
        -Message "å®å¨å£°æå®æ´æ? $(if($hasSecuritySection){'æsecurityè?}else{'æ securityè?})" `
        -FixSuggestion "å¨config.yamlä¸­æ·»å å®æ´çsecurityå£°æ" `
        -Critical $true
}

# ============================================
# 4. ææ¡£è´¨éæ£æ?# ============================================
Write-Host "`n## 4. ææ¡£è´¨éæ£æ? -ForegroundColor Yellow

# 4.1 SKILL.mdå®æ´æ?if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    $hasOverview = $skillMdContent -match "æè½æ¦è¿°|æ¦è¿°"
    $hasSecurity = $skillMdContent -match "å®å¨å£°æ|å®å¨ç¹æ?
    $hasUsage = $skillMdContent -match "ç¨æ³|ä½¿ç¨|ç¤ºä¾"
    $hasCommands = $skillMdContent -match "å½ä»¤|åè½"
    
    $docComplete = $hasOverview -and $hasSecurity -and $hasUsage -and $hasCommands
    
    Add-CheckResult -Category "documentation_quality" -CheckName "SKILL.mdå®æ´æ? `
        -Passed $docComplete `
        -Message "ææ¡£å®æ´æ? æ¦è¿°=$hasOverview, å®å¨=$hasSecurity, ç¨æ³=$hasUsage, å½ä»¤=$hasCommands" `
        -FixSuggestion "å®åSKILL.mdææ¡£ï¼åå«ææå¿éç« è" `
        -Critical $false
}

# 4.2 README.mdå­å¨æ?$readmePath = Join-Path $SkillDir "README.md"
Add-CheckResult -Category "documentation_quality" -CheckName "README.mdå­å¨" `
    -Passed (Test-Path $readmePath) `
    -Message "README.md $(if(Test-Path $readmePath){'å­å¨'}else{'ä¸å­å?})" `
    -FixSuggestion "åå»ºREADME.mdæä»¶" `
    -Critical $false

# 4.3 CHANGELOG.mdå­å¨æ?$changelogPath = Join-Path $SkillDir "CHANGELOG.md"
Add-CheckResult -Category "documentation_quality" -CheckName "CHANGELOG.mdå­å¨" `
    -Passed (Test-Path $changelogPath) `
    -Message "CHANGELOG.md $(if(Test-Path $changelogPath){'å­å¨'}else{'ä¸å­å?})" `
    -FixSuggestion "åå»ºCHANGELOG.mdè®°å½çæ¬åæ´" `
    -Critical $false

# ============================================
# 5. åæ°æ®éªè¯?# ============================================
Write-Host "`n## 5. åæ°æ®éªè¯? -ForegroundColor Yellow

# 5.1 package.jsonåºæ¬ä¿¡æ¯
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        
        $hasName = ![string]::IsNullOrEmpty($packageJson.name)
        $hasDescription = ![string]::IsNullOrEmpty($packageJson.description)
        $hasAuthor        $hasAuthor = ![string]::IsNullOrEmpty($packageJson.author)
        $hasLicense = ![string]::IsNullOrEmpty($packageJson.license)
        
        $metadataComplete = $hasName -and $hasDescription -and $hasAuthor -and $hasLicense
        
        Add-CheckResult -Category "metadata_validation" -CheckName "package.jsonåºæ¬ä¿¡æ¯" `
            -Passed $metadataComplete `
            -Message "åæ°æ®å®æ´æ? åç§°=$hasName, æè¿°=$hasDescription, ä½è?$hasAuthor, è®¸å¯è¯?$hasLicense" `
            -FixSuggestion "å®åpackage.jsonä¸­çåºæ¬ä¿¡æ¯" `
            -Critical $true
    } catch {
        Add-CheckResult -Category "metadata_validation" -CheckName "package.jsonæ ¼å¼æ­£ç¡®" `
            -Passed $false -Message "package.jsonæ ¼å¼éè¯¯: $_" `
            -FixSuggestion "ä¿®å¤package.jsonçJSONæ ¼å¼" `
            -Critical $true
    }
}

# 5.2 ä½èä¿¡æ¯åçæ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $author = $packageJson.author
        
        # æ£æ¥ä½èä¿¡æ¯æ¯å¦åç?        $isValidAuthor = $author -notmatch "test|example|demo|placeholder|TODO|FIXME"
        $isValidAuthor = $isValidAuthor -and $author.Length -ge 2 -and $author.Length -le 100
        
        Add-CheckResult -Category "metadata_validation" -CheckName "ä½èä¿¡æ¯åç? `
            -Passed $isValidAuthor `
            -Message "ä½èä¿¡æ? $author" `
            -FixSuggestion "ä½¿ç¨çå®åççä½èä¿¡æ? `
            -Critical $false
    } catch {
        # å¿½ç¥éè¯¯ï¼å·²å¨åé¢æ£æ?    }
}

# ============================================
# 6. é¾æ¥éªè¯ (å³é®ï¼?
# ============================================
Write-Host "`n## 6. é¾æ¥éªè¯" -ForegroundColor Yellow

# 6.1 æ¶éææé¾æ?$allLinks = @()

# ä»README.mdæ¶éé¾æ¥
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

# ä»SKILL.mdæ¶éé¾æ¥
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

# ä»package.jsonæ¶éé¾æ¥
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
        # å¿½ç¥éè¯¯
    }
}

# 6.2 æ£æ¥é¾æ¥æææ?$validLinks = 0
$invalidLinks = @()

foreach ($link in $allLinks) {
    $url = $link.url
    
    # æ£æ¥URLæ ¼å¼
    $isValidFormat = $url -match '^https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}'
    
    # æ£æ¥æ¯å¦ä¸ºå ä½ç¬?    $isPlaceholder = $url -match 'example\.com|placeholder|TODO|FIXME|your-username|your-repo'
    
    if ($isValidFormat -and (-not $isPlaceholder)) {
        $validLinks++
    } else {
        $invalidLinks += "$($link.file): $url ($($link.context))"
    }
}

$totalLinks = $allLinks.Count
$allLinksValid = $invalidLinks.Count -eq 0

Add-CheckResult -Category "link_validation" -CheckName "ææé¾æ¥çå®ææ? `
    -Passed $allLinksValid `
    -Message "é¾æ¥æææ? $validLinks/$totalLinks ææ, æ æ: $($invalidLinks.Count)" `
    -FixSuggestion "ä¿®å¤æ æé¾æ¥: $($invalidLinks -join '; ')" `
    -Critical $true

# 6.3 GitHubé¾æ¥ç¹å®æ£æ?$githubLinks = $allLinks | Where-Object { $_.url -match 'github\.com' }
if ($githubLinks.Count -gt 0) {
    $validGithubLinks = $githubLinks | Where-Object { 
        $_.url -match 'github\.com/[a-zA-Z0-9\-]+/[a-zA-Z0-9\-]+'
    }
    
    Add-CheckResult -Category "link_validation" -CheckName "GitHubé¾æ¥æ ¼å¼æ­£ç¡®" `
        -Passed ($validGithubLinks.Count -eq $githubLinks.Count) `
        -Message "GitHubé¾æ¥: $($validGithubLinks.Count)/$($githubLinks.Count) æ ¼å¼æ­£ç¡®" `
        -FixSuggestion "ç¡®ä¿GitHubé¾æ¥æ ¼å¼ä¸? https://github.com/username/repository" `
        -Critical $false
}

# ============================================
# 7. ä»£ç è´¨éæ£æ?# ============================================
Write-Host "`n## 7. ä»£ç è´¨éæ£æ? -ForegroundColor Yellow

# 7.1 Pythonè¯­æ³æ£æ?if (Test-Path $skillPath) {
    try {
        # å°è¯å¯¼å¥æ¨¡åæ£æ¥è¯­æ³?        $pythonCheck = python -m py_compile $skillPath 2>&1
        $syntaxValid = $LASTEXITCODE -eq 0
        
        Add-CheckResult -Category "code_quality" -CheckName "Pythonè¯­æ³æ­£ç¡®" `
            -Passed $syntaxValid `
            -Message "Pythonè¯­æ³æ£æ? $(if($syntaxValid){'éè¿'}else{'å¤±è´¥'})" `
            -FixSuggestion "ä¿®å¤Pythonè¯­æ³éè¯¯: $pythonCheck" `
            -Critical $true
    } catch {
        Add-CheckResult -Category "code_quality" -CheckName "Pythonè¯­æ³æ£æ? `
            -Passed $false -Message "æ æ³æ§è¡Pythonè¯­æ³æ£æ? `
            -FixSuggestion "æå¨æ£æ¥Pythonè¯­æ³" `
            -Critical $false
    }
}

# 7.2 å¯¼å¥æ¨¡åæ£æ?if (Test-Path $skillPath
        $skillContent = Get-Content $skillPath -Raw
        $importLines = Select-String -Path $skillPath -Pattern "^import |^from " | Select-Object -ExpandProperty Line
        
        # æ£æ¥æ ååºå¯¼å¥
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
        
        Add-CheckResult -Category "code_quality" -CheckName "ä»æ ååºå¯¼å¥ï¼å¦å£°æï¼? `
            -Passed (-not $hasExternalImports) `
            -Message "å¯¼å¥åæ: æ ååº?$($stdlibImports.Count), å¤é¨=$($externalImports.Count)" `
            -FixSuggestion "ç§»é¤å¤é¨ä¾èµå¯¼å¥: $($externalImports -join '; ')" `
            -Critical $false
    }
}

# 7.3 ä»£ç æ³¨éæ£æ?if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $totalLines = ($skillContent -split "`n").Count
    $commentLines = (Select-String -Path $skillPath -Pattern "^#|^\s*#" | Measure-Object).Count
    
    $commentRatio = if ($totalLines -gt 0) { [math]::Round(($commentLines / $totalLines) * 100, 2) } else { 0 }
    $hasGoodComments = $commentRatio -ge 10  # è³å°10%çæ³¨é?    
    Add-CheckResult -Category "code_quality" -CheckName "ä»£ç æ³¨éåå" `
        -Passed $hasGoodComments `
        -Message "ä»£ç æ³¨éç? $commentRatio% ($commentLines/$totalLines è¡?" `
        -FixSuggestion "æ·»å æ´å¤ä»£ç æ³¨éï¼ç®æ â¥10%" `
        -Critical $false
}

# ============================================
# 8. ä¾èµéªè¯
# ============================================
Write-Host "`n## 8. ä¾èµéªè¯" -ForegroundColor Yellow

# 8.1 requirements.txtæ£æ?$requirementsPath = Join-Path $SkillDir "requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath
    $hasRequirements = $requirementsContent.Count -gt 0
    
    # æ£æ¥æ¯å¦æå¤é¨ä¾èµ
    $hasExternalDeps = $false
    foreach ($line in $requirementsContent) {
        $line = $line.Trim()
        if ($line -and -not $line.StartsWith("#")) {
            $hasExternalDeps = $true
            break
        }
    }
    
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txtä¾èµå£°æ" `
        -Passed $hasRequirements `
        -Message "requirements.txt: $(if($hasRequirements){'æä¾èµå£°æ?}else{'ç©ºææ?})" `
        -FixSuggestion "å¦æå¤é¨ä¾èµï¼å¨requirements.txtä¸­å£°æ? `
        -Critical $false
    
    # å¦æå£°æ"ä»æ ååº"ï¼åä¸åºæå¤é¨ä¾èµ?    if (Test-Path $skillMdPath) {
        $skillMdContent = Get-Content $skillMdPath -Raw
        $declaresStdlibOnly = $skillMdContent -match "ä»æ ååº|stdlib only|æ å¤é¨ä¾èµ?
        
        if ($declaresStdlibOnly -and $hasExternalDeps) {
            Add-CheckResult -Category "dependency_validation" -CheckName "å£°æä¸ä¾èµä¸è? `
                -Passed $false `
                -Message "å£°æ'ä»æ ååº'ä½requirements.txtæå¤é¨ä¾èµ? `
                -FixSuggestion "è¦ä¹ç§»é¤å¤é¨ä¾èµï¼è¦ä¹ä¿®æ¹å£°æ? `
                -Critical $true
        }
    }
} else {
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txtå­å¨" `
        -Passed $false `
        -Message "requirements.txtä¸å­å? `
        -FixSuggestion "åå»ºrequirements.txtæä»¶ï¼å¯ä¸ºç©ºï¼? `
        -Critical $false
}

# ============================================
# 9. è®¸å¯è¯åè§?# ============================================
Write-Host "`n## 9. è®¸å¯è¯åè§? -ForegroundColor Yellow

# 9.1 è®¸å¯è¯æä»¶æ£æ?$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "^LICENSE|^LICENCE|^license|^licence"
}

Add-CheckResult -Category "license_compliance" -CheckName "è®¸å¯è¯æä»¶å­å? `
    -Passed ($licenseFiles.Count -gt 0) `
    -Message "è®¸å¯è¯æä»? $(if($licenseFiles.Count -gt 0){'æ¾å°'}else{'æªæ¾å?})" `
    -FixSuggestion "æ·»å LICENSEæä»¶ï¼éæ©åéè®¸å¯è¯" `
    -Critical $false

# 9.2 package.jsonè®¸å¯è¯å­æ®?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasLicenseField = ![string]::IsNullOrEmpty($packageJson.license)
        
        Add-CheckResult -Category "license_compliance" -CheckName "package.jsonè®¸å¯è¯å­æ®? `
            -Passed $hasLicenseField `
            -Message "package.jsonè®¸å¯è¯? $(if($hasLicenseField){$packageJson.license}else{'ç¼ºå¤±'})" `
            -FixSuggestion "å¨package.jsonä¸­æ·»å licenseå­æ®µ" `
            -Critical $false
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# ============================================
# 10. ClawHubç¹å®è¦æ±
# ============================================
Write-Host "`n## 10. ClawHubç¹å®è¦æ±" -ForegroundColor Yellow

# 10.1 æè½åç§°æ£æ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $skillName = $packageJson.name
        
        # æ£æ¥åç§°æ¯å¦åç?        $isValidName = $skillName -match "^[a-z0-9\-]+$" -and $skillName.Length -ge 3 -and $skillName.Length -le 50
        $isNotPlaceholder = $skillName -notmatch "test|example|demo|placeholder|TODO"
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "æè½åç§°æ ¼å¼æ­£ç¡? `
            -Passed ($isValidName -and $isNotPlaceholder) `
            -Message "æè½åç§? $skillName" `
            -FixSuggestion "ä½¿ç¨å°åå­æ¯ãæ°å­åè¿å­ç¬¦ï¼é¿åå ä½ç¬? `
            -Critical $true
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# 10.2 æè½æè¿°æ£æ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $description = $packageJson.description
        
        # æ£æ¥æè¿°æ¯å¦åç?        $hasDescription = ![string]::IsNullOrEmpty($description)
        $descriptionLength = if ($description) { $description.Length } else { 0 }
        $isValidDescription = $hasDescription -and $descriptionLength -ge 10 -and $descriptionLength -le 200
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "æè½æè¿°åç? `
            -Passed $isValidDescription `
            -Message "æè¿°é¿åº¦: $descriptionLength å­ç¬¦" `
            -FixSuggestion "æä¾10-200å­ç¬¦çææä¹æè¿°" `
            -Critical $false
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# 10.3 æè½åç±»æ£æ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasCategories = $packageJson.categories -and $packageJson.categories.Count -gt 0
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "æè½åç±»è®¾ç½? `
            -Passed $hasCategories `
            -Message "æè½åç±? $(if($hasCategories){'å·²è®¾ç½?}else{'æªè®¾ç½?})" `
            -FixSuggestion "å¨package.jsonä¸­æ·»å categorieså­æ®µ" `
            -Critical $false
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# ============================================
# è®¡ç®åæ°åçææ¥å?# ============================================

# è®¡ç®åæ°
Calculate-Scores

# çæè¯¦ç»æ¥å
Write-Host "`n=== ç»æå®¡æ ¸æ¥å ===" -ForegroundColor Cyan
Write-Host "å®¡æ ¸å®ææ¶é´: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "æ»ä½åè§åæ°: $($auditResults.score.percentage)%"
Write-Host "æ£æ¥é¡¹æ»æ°: $($auditResults.score.total)"
Write-Host "éè¿é¡? $($auditResults.score.passed)"
Write-Host "å¤±è´¥é¡? $($auditResults.score.total - $auditResults.score.passed)"

# åç±»æ¥å
Write-Host "`n## åç±»åæ°" -ForegroundColor Yellow
foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $auditResults.categories[$categoryKey].score
    
    $color = if ($categoryScore -ge 90) { "Green" } 
             elseif ($categoryScore -ge 70) { "Yellow" } 
             else { "Red" }
    
    Write-Host "$categoryName: $categoryScore%" -ForegroundColor $color
}

# ä¸¥éé®é¢æ¥å
if ($auditResults.critical_issues.Count -gt 0) {
    Write-Host "`n## â?ä¸¥éé®é¢ (å¿é¡»ä¿®å¤)" -ForegroundColor Red
    foreach ($issue in $auditResults.critical_issues) {
        Write-Host "  â?$issue" -ForegroundColor Red
    }
} else {
    Write-Host "`n## â?æ ä¸¥éé®é¢? -ForegroundColor Green
}

# è­¦åé®é¢æ¥å
if ($auditResults.warning_issues.Count -gt 0) {
    Write-Host "`n## â ï¸  è­¦åé®é¢ (å»ºè®®ä¿®å¤)" -ForegroundColor Yellow
    foreach ($issue in $auditResults.warning_issues) {
        Write-Host "  â?$issue" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n## â?æ è­¦åé®é¢? -ForegroundColor Green
}

# å»ºè®®æ¥å
if ($auditResults.recommendations.Count -gt 0) {
    Write-Host "`n## ð¡ æ¹è¿å»ºè®®" -ForegroundColor Cyan
    $uniqueRecommendations = $auditResults.recommendations | Select-Object -Unique
    foreach ($rec in $uniqueRecommendations) {
        Write-Host "  â?$rec" -ForegroundColor Cyan
    }
}

# çæJSONæ¥å
$reportFile = Join-Path $OutputDir "ultimate_audit_report.json"
$auditResults | ConvertTo-Json -Depth 10 | Set-Content -Path $reportFile

# çæMarkdownæ¥å
$mdReport = @"
# ç»æClawHubå®¡æ ¸æ¥å

## å®¡æ ¸ä¿¡æ¯
- **å®¡æ ¸æ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **æè½ç®å½?*: $SkillDir
- **å®¡æ ¸æ¨¡å¼**: $($StrictMode ? 'ä¸¥æ ¼' : 'æ å')
- **èªå¨ä¿®å¤**: $($AutoFix ? 'å¯ç¨' : 'ç¦ç¨')

## æ»ä½è¯å
**åè§åæ°: $($auditResults.score.percentage)%**

| æ£æ¥ç±»å?| åæ° | ç¶æ?|
|----------|------|------|
"@

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $auditResults.categories[$categoryKey].score
    $status = if ($categoryScore -ge 90) { "â?ä¼ç§" } 
              elseif ($categoryScore -ge 70) { "â ï¸  è¯å¥½" } 
              else { "â?éæ¹è¿" }
    
    $mdReport += "| $categoryName | $categoryScore% | $status |`n"
}

$mdReport += @"

## è¯¦ç»æ£æ¥ç»æ?
### ä¸¥éé®é¢ (å¿é¡»ä¿®å¤)
"@

if ($auditResults.critical_issues.Count -gt 0) {
    foreach ($issue in $auditResults.critical_issues) {
        $mdReport += "- â?$issue`n"
    }
} else {
    $mdReport += "- â?æ ä¸¥éé®é¢`n"
}

$mdReport += @"

### è­¦åé®é¢ (å»ºè®®ä¿®å¤)
"@

if ($auditResults.warning_issues.Count -gt 0) {
    foreach ($issue in $auditResults.warning_issues) {
        $mdReport += "- â ï¸  $issue`n"
    }
} else {
    $mdReport += "- â?æ è­¦åé®é¢`n"
}

$mdReport += @"

### æ¹è¿å»ºè®®
"@

if ($auditResults.recommendations.Count -gt 0) {
    $uniqueRecommendations = $auditResults.recommendations | Select-Object -Unique
    foreach ($rec in $uniqueRecommendations) {
        $mdReport += "- ð¡ $rec`n"
    }
} else {
    $mdReport += "- â?æ æ¹è¿å»ºè®®`n"
}

$mdReport += @"

## å³é®åç°

### 1. çæ¬ä¸è´æ?"@

if ($versionSources.Count -gt 0) {
    $mdReport += "åç°çæ¬å·æ¥æº? `n"
    foreach ($source in $versionSources) {
        $mdReport += "- $($source.file): $($source.version)`n"
    }
}

$mdReport += @"

### 2. é¾æ¥éªè¯
- æ»é¾æ¥æ°: $totalLinks
- ææé¾æ¥: $validLinks
- æ æé¾æ¥: $($invalidLinks.Count)

### 3. å®å¨åè§
- ç½ç»ä»£ç : $($networkIssues.Count) å¤?- å±é©å½æ°: $($dangerousIssues.Count) å¤?- å®å¨å£°æ: $(if($hasSecuritySection){'å®æ´'}else{'ç¼ºå¤±'})

## å®¡æ ¸ç»è®º

"@

if ($auditResults.score.percentage -ge 95) {
    $mdReport += "**â?ä¼ç§ï¼æè½é«åº¦ç¬¦åClawHubè¦æ±ï¼é¢è®¡è½ä¸æ¬¡æ§éè¿å®¡æ ¸ã?*`n`n"
    $mdReport += "å»ºè®®: å¯ä»¥ç´æ¥åå¸å°ClawHubã?
} elseif ($auditResults.score.percentage -ge 85) {
    $mdReport += "**â ï¸  è¯å¥½ï¼ä½éè¦ä¿®å¤ä¸äºé®é¢ã?*`n`n"
    $mdReport += "å»ºè®®: ä¿®å¤ææä¸¥éé®é¢åååå¸ã?
} elseif ($auditResults.score.percentage -ge 70) {
    $mdReport += "**â?éè¦æ¹è¿ï¼å­å¨è¾å¤é®é¢ã?*`n`n"
    $mdReport += "å»ºè®®: å¨é¢ä¿®å¤é®é¢ï¼éæ°å®¡æ ¸åååå¸ã?
} else {
    $mdReport += "**ð« ä¸ç¬¦åè¦æ±ï¼éè¦éå¤§æ¹è¿ã?*`n`n"
    $mdReport += "å»ºè®®: éæ°è®¾è®¡æè½ï¼ç¡®ä¿ç¬¦åææè¦æ±ã?
}

$mdReport += @"

## ä¸æ¬¡æ§éè¿ClawHubçå³é?
åºäºæ¬æ¬¡å®¡æ ¸ï¼ç¡®ä¿ä¸æ¬¡æ§éè¿ClawHubéè¦ï¼

1. **çæ¬å®å¨ä¸è?*: æææä»¶çæ¬å·å¿é¡»100%ä¸è?2. **é¾æ¥çå®ææ**: ææé¾æ¥å¿é¡»çå®å¯è®¿é®ï¼æ å ä½ç¬?3. **å®å¨å£°æå®æ´**: config.yamlå¿é¡»æå®æ´å®å¨å£°æ?4. **æ ç½ç»ä»£ç ?*: å½»åºç§»é¤ææç½ç»ç¸å³ä»£ç ?5. **ææ¡£å®æ´æ?*: ææå¿éææ¡£å®æ´æ ç¼ºå¤?6. **åæ°æ®åç?*: ä½èãæè¿°ç­ä¿¡æ¯çå®åç
7. **ä»£ç è´¨é**: è¯­æ³æ­£ç¡®ï¼æ³¨éåå?8. **è®¸å¯è¯åè§?*: æåéçè®¸å¯è¯æä»?
## ä¸ä¸æ­¥è¡å?
### å¦æåæ° â?95%
1. ç´æ¥åå¤åå¸ææ
2. ä¸ä¼ å°ClawHub
3. çæ§å®¡æ ¸ç»æ

### å¦æåæ° 85-94%
1. ä¿®å¤ææä¸¥éé®é¢?2. ä¿®å¤ä¸»è¦è­¦åé®é¢
3. éæ°è¿è¡å®¡æ ¸
4. ç¡®ä¿åæ° â?95%

### å¦æåæ° < 85%
1. å¨é¢å®¡æ¥ææé®é¢?2. å¶å®ä¿®å¤è®¡å
3. éé¡¹ä¿®å¤é®é¢
4. éæ°è¿è¡å®¡æ ¸ç´å°è¾¾æ 

---

**æ¥åçææ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**å®¡æ ¸å·¥å·çæ¬**: v1.0 (ç»æç?  
**ç®æ åæ°**: â?95% (ç¡®ä¿ä¸æ¬¡æ§éè¿)  
**å®¡æ ¸æ å**: ClawHubæ·±åº¦åè§ + ä¸æ¬¡æ§éè¿è¦æ±
"@

$mdReportFile = Join-Path $OutputDir "ultimate_audit_report.md"
Set-Content -Path $mdReportFile -Value $mdReport

Write-Host "`nè¯¦ç»æ¥åå·²ä¿å­å°:" -ForegroundColor Cyan
Write-Host "  JSONæ¥å: $reportFile" -ForegroundColor Cyan
Write-Host "  Markdownæ¥å: $mdReportFile" -ForegroundColor Cyan

# æç»å»ºè®?Write-Host "`n=== æç»å»ºè®?===" -ForegroundColor Cyan

if ($auditResults.score.percentage -ge 95) {
    Write-Host "ð æ­åï¼æè½é«åº¦ç¬¦åClawHubè¦æ±ï¼? -ForegroundColor Green
    Write-H
) {
    $skillContent = Get-Content $skillPath -Raw
    $importLines = Select-String -Path $skillPath -Pattern "^import |^from " | Select-Object -ExpandProperty Line
    
    # æ£æ¥æ ååºå¯¼å¥
    $stdlibImports = @()
    $thirdPartyImports = @()
    
    $commonStdlib = @("os", "sys", "json", "csv", "math", "statistics", "datetime", 
                     "time", "pathlib", "typing", "dataclasses", "enum", "collections")
    
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
            $thirdPartyImports += $line
        }
    }
    
    $hasOnlyStdlib = $thirdPartyImports.Count -eq 0
    
    Add-CheckResult -Category "code_quality" -CheckName "ä»æ ååºå¯¼å¥" `
        -Passed $hasOnlyStdlib `
        -Message "å¯¼å¥åæ: æ ååº?$($stdlibImports.Count), ç¬¬ä¸æ?$($thirdPartyImports.Count)" `
        -FixSuggestion "ç§»é¤ç¬¬ä¸æ¹åºå¯¼å¥: $($thirdPartyImports -join '; ')" `
        -Critical $false
}

# 7.3 ä»£ç æ³¨éæ£æ?if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $totalLines = ($skillContent -split "`n").Count
    $commentLines = ($skillContent -split "`n" | Where-Object { $_ -match "^#|^\s*#" }).Count
    
    $commentRatio = if ($totalLines -gt 0) { [math]::Round(($commentLines / $totalLines) * 100, 2) } else { 0 }
    $hasReasonableComments = $commentRatio -ge 10 -and $commentRatio -le 40
    
    Add-CheckResult -Category "code_quality" -CheckName "ä»£ç æ³¨éåç" `
        -Passed $hasReasonableComments `
        -Message "æ³¨éæ¯ä¾: $commentRatio% ($commentLines/$totalLines è¡?" `
        -FixSuggestion "è°æ´æ³¨éæ¯ä¾å?0-40%ä¹é´" `
        -Critical $false
}

# ============================================
# 8. ä¾èµéªè¯
# ============================================
Write-Host "`n## 8. ä¾èµéªè¯" -ForegroundColor Yellow

# 8.1 requirements.txtæ£æ?$requirementsPath = Join-Path $SkillDir "requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath
    $hasRequirements = $requirementsContent.Count -gt 0
    
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txtéç©º" `
        -Passed $hasRequirements `
        -Message "requirements.txt: $(if($hasRequirements){'æåå®?}else{'ç©ºæä»?})" `
        -FixSuggestion "æ·»å ä¾èµæå é¤requirements.txt" `
        -Critical $false
    
    # æ£æ¥ä¾èµæ ¼å¼?    $validDeps = 0
    $invalidDeps = @()
    
    foreach ($line in $requirementsContent) {
        $trimmed = $line.Trim()
        if (-not [string]::IsNullOrEmpty($trimmed) -and -not $trimmed.StartsWith("#")) {
            # æ£æ¥æ¯å¦ä¸ºææçååæ ¼å¼?            if ($trimmed -match '^[a-zA-Z0-9_\-\[\]]+([>=<~!].*)?$') {
                $validDeps++
            } else {
                $invalidDeps += $trimmed
            }
        }
    }
    
    if ($hasRequirements) {
        Add-CheckResult -Category "dependency_validation" -CheckName "ä¾èµæ ¼å¼æ­£ç¡®" `
            -Passed ($invalidDeps.Count -eq 0) `
            -Message "ä¾èµæ ¼å¼: $validDeps ææ, $($invalidDeps.Count) æ æ" `
            -FixSuggestion "ä¿®å¤æ æä¾èµæ ¼å¼: $($invalidDeps -join ', ')" `
            -Critical $false
    }
} else {
    Add-CheckResult -Category "dependency_validation" -CheckName "requirements.txtå­å¨" `
        -Passed $false -Message "requirements.txtä¸å­å? `
        -FixSuggestion "åå»ºrequirements.txtæä»¶ï¼å³ä½¿ä¸ºç©ºï¼" `
        -Critical $false
}

# ============================================
# 9. è®¸å¯è¯åè§æ£æ?# ============================================
Write-Host "`n## 9. è®¸å¯è¯åè§æ£æ? -ForegroundColor Yellow

# 9.1 è®¸å¯è¯æä»¶æ£æ?$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "^LICENSE|^LICENCE|^license|^licence"
}

Add-CheckResult -Category "license_compliance" -CheckName "è®¸å¯è¯æä»¶å­å? `
    -Passed ($licenseFiles.Count -gt 0) `
    -Message "è®¸å¯è¯æä»? $($licenseFiles.Count) ä¸? `
    -FixSuggestion "æ·»å LICENSEæä»¶" `
    -Critical $true

# 9.2 package.jsonè®¸å¯è¯å­æ®?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasLicenseField = ![string]::IsNullOrEmpty($packageJson.license)
        
        Add-CheckResult -Category "license_compliance" -CheckName "package.jsonè®¸å¯è¯å­æ®? `
            -Passed $hasLicenseField `
            -Message "package.jsonè®¸å¯è¯å­æ®? $(if($hasLicenseField){'å­å¨'}else{'ç¼ºå¤±'})" `
            -FixSuggestion "å¨package.jsonä¸­æ·»å licenseå­æ®µ" `
            -Critical $true
        
        # æ£æ¥è®¸å¯è¯ç±»å
        if ($hasLicenseField) {
            $validLicenses = @("MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC", "Unlicense")
            $isValidLicense = $validLicenses -contains $packageJson.license
            
            Add-CheckResult -Category "license_compliance" -CheckName "è®¸å¯è¯ç±»åææ? `
                -Passed $isValidLicense `
                -Message "è®¸å¯è¯ç±»å? $($packageJson.license)" `
                -FixSuggestion "ä½¿ç¨æ åè®¸å¯è¯ç±»å? MIT, Apache-2.0ç­? `
                -Critical $false
        }
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# ============================================
# 10. ClawHubç¹å®è¦æ±æ£æ?# ============================================
Write-Host "`n## 10. ClawHubç¹å®è¦æ±æ£æ? -ForegroundColor Yellow

# 10.1 æè½åç§°æ£æ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $skillName = $packageJson.name
        
        # æ£æ¥æè½åç§°æ ¼å¼?        $isValidName = $skillName -match '^[a-z0-9\-]+$' -and $skillName.Length -ge 3 -and $skillName.Length -le 50
        $isNotPlaceholder = $skillName -notmatch 'test|example|demo|placeholder|my-skill'
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "æè½åç§°æ ¼å¼æ­£ç¡? `
            -Passed ($isValidName -and $isNotPlaceholder) `
            -Message "æè½åç§? $skillName" `
            -FixSuggestion "ä½¿ç¨å°åå­æ¯ãæ°å­åè¿å­ç¬¦ï¼é¿åå ä½ç¬¦åç§? `
            -Critical $true
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# 10.2 æè½æè¿°æ£æ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $description = $packageJson.description
        
        $hasDescription = ![string]::IsNullOrEmpty($description)
        $descriptionLength = if ($hasDescription) { $description.Length } else { 0 }
        $isValidDescription = $hasDescription -and $descriptionLength -ge 10 -and $descriptionLength -le 200
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "æè½æè¿°åç? `
            -Passed $isValidDescription `
            -Message "æè¿°é¿åº¦: $descriptionLength å­ç¬¦" `
            -FixSuggestion "æè¿°åºå¨10-200å­ç¬¦ä¹é´ï¼æ¸æ°è¯´ææè½åè? `
            -Critical $true
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# 10.3 æè½åç±»æ£æ?if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasCategories = $packageJson.categories -and $packageJson.categories.Count -gt 0
        
        Add-CheckResult -Category "clawhub_specific" -CheckName "æè½åç±»è®¾ç½? `
            -Passed $hasCategories `
            -Message "æè½åç±? $(if($hasCategories){'å·²è®¾ç½?}else{'æªè®¾ç½?})" `
            -FixSuggestion "å¨package.jsonä¸­æ·»å categorieså­æ®µ" `
            -Critical $false
    } catch {
        # å¿½ç¥éè¯¯
    }
}

# 10.4 æè½å¾æ æ£æ?$iconFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "icon|logo" -and $_.Extension -match "\.png|\.jpg|\.jpeg|\.svg"
}

Add-CheckResult -Category "clawhub_specific" -CheckName "æè½å¾æ å­å? `
    -Passed ($iconFiles.Count -gt 0) `
    -Message "å¾æ æä»¶: $($iconFiles.Count) ä¸? `
    -FixSuggestion "æ·»å æè½å¾æ æä»?(icon.png/icon.svg)" `
    -Critical $false

# ============================================
# è®¡ç®åæ°åçææ¥å?# ============================================

# è®¡ç®åæ°
Calculate-Scores

# çæè¯¦ç»æ¥å
Write-Host "`n=== å®¡æ ¸å®æ ===" -ForegroundColor Cyan
Write-Host "æ»ä½åæ°: $($auditResults.score.percentage)%" -ForegroundColor Cyan
Write-Host "æ£æ¥é¡¹: $($auditResults.score.passed)/$($auditResults.score.total) éè¿" -ForegroundColor Cyan
Write-Host "ä¸¥éé®é¢: $($auditResults.critical_issues.Count) ä¸? -ForegroundColor $($auditResults.critical_issues.Count -eq 0 ? "Green" : "Red")
Write-Host "è­¦åé®é¢: $($auditResults.warning_issues.Count) ä¸? -ForegroundColor $($auditResults.warning_issues.Count -eq 0 ? "Green" : "Yellow")

# åç±»æ¥å
Write-Host "`n## åç±»åæ°" -ForegroundColor Yellow
foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $auditResults.categories[$categoryKey].score
    $passed = $auditResults.categories[$categoryKey].passed
    $total = $auditResults.categories[$categoryKey].total
    
    $color = if ($categoryScore -ge 90) { "Green" } elseif ($categoryScore -ge 70) { "Yellow" } else { "Red" }
    
    Write-Host "  $categoryName: $categoryScore% ($passed/$total)" -ForegroundColor $color
}

# ä¸¥éé®é¢æ¥å
if ($auditResults.critical_issues.Count -gt 0) {
    Write-Host "`n## ä¸¥éé®é¢ (å¿é¡»ä¿®å¤)" -ForegroundColor Red
    foreach ($issue in $auditResults.critical_issues) {
        Write-Host "  â?$issue" -ForegroundColor Red
    }
}

# è­¦åé®é¢æ¥å
if ($auditResults.warning_issues.Count -gt 0) {
    Write-Host "`n## è­¦åé®é¢ (å»ºè®®ä¿®å¤)" -ForegroundColor Yellow
    foreach ($issue in $auditResults.warning_issues) {
        Write-Host "  â ï¸  $issue" -ForegroundColor Yellow
    }
}

# å»ºè®®æ¥å
if ($auditResults.recommendations.Count -gt 0) {
    Write-Host "`n## æ¹è¿å»ºè®®" -ForegroundColor Cyan
    $uniqueRecommendations = $auditResults.recommendations | Select-Object -Unique
    foreach ($recommendation in $uniqueRecommendations) {
        Write-Host "  ð¡ $recommendation" -ForegroundColor Cyan
    }
}

# çæJSONæ¥å
$jsonReport = @{
    "audit_summary" = @{
        "skill_directory" = $SkillDir
        "audit_time" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "total_checks" = $auditResults.score.total
        "passed_checks" = $auditResults.score.passed
        "overall_score" = $auditResults.score.percentage
        "critical_issues_count" = $auditResults.critical_issues.Count
        "warning_issues_count" = $auditResults.warning_issues.Count
        "clawhub_ready" = ($auditResults.score.percentage -ge 95 -and $auditResults.critical_issues.Count -eq 0)
    }
    "category_scores" = @{}
    "critical_issues" = $auditResults.critical_issues
    "warning_issues" = $auditResults.warning_issues
    "recommendations" = ($auditResults.recommendations | Select-Object -Unique)
    "detailed_results" = @{}
}

foreach ($categoryKey in $categories.Keys) {
    $jsonReport.category_scores[$categories[$categoryKey]] = $auditResults.categories[$categoryKey].score
    
    $detailedChecks = @()
    foreach ($check in $auditResults.categories[$categoryKey].checks) {
        $detailedChecks += @{
            "check_name" = $check.name
            "passed" = $check.passed
            "message" = $check.message
            "critical" = $check.critical
            "timestamp" = $check.timestamp
        }
    }
    $jsonReport.detailed_results[$categories[$categoryKey]] = $detailedChecks
}

$jsonFilePath = Join-Path $OutputDir "ultimate_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`nè¯¦ç»JSONæ¥åå·²ä¿å­å°: $jsonFilePath" -ForegroundColor Cyan

# çæMarkdownæ¥å
$mdReport = @"
# ç»æClawHubå®¡æ ¸æ¥å

## å®¡æ ¸ä¿¡æ¯
- **æè½ç®å½?*: $SkillDir
- **å®¡æ ¸æ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **å®¡æ ¸æ¨¡å¼**: $($StrictMode ? 'ä¸¥æ ¼æ¨¡å¼' : 'æ åæ¨¡å¼')
- **èªå¨ä¿®å¤**: $($AutoFix ? 'å¯ç¨' : 'ç¦ç¨')

## æ»ä½è¯å
**æ»ä½åæ°: $($auditResults.score.percentage)%**

| ææ  | ç»æ |
|------|------|
| æ»æ£æ¥é¡¹ | $($auditResults.score.total) |
| éè¿é¡?| $($auditResults.score.passed) |
| ä¸¥éé®é¢ | $($auditResults.critical_issues.Count) |
| è­¦åé®é¢ | $($auditResults.warning_issues.Count) |
| ClawHubå°±ç»ª | $($jsonReport.audit_summary.clawhub_ready ? 'â?æ? : 'â?å?) |

## åç±»åæ°

| åç±» | åæ° | ç¶æ?|
|------|------|------|
"@

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $auditResults.categories[$categoryKey].score
    $passed = $auditResults.categories[$categoryKey].passed
    $total = $auditResults.categories[$categoryKey].total
    
    $status = if ($categoryScore -ge 90) { "â?ä¼ç§" } elseif ($categoryScore -ge 70) { "â ï¸ è¯å¥½" } else { "â?éæ¹è¿" }
    
    $mdReport += "| $categoryName | $categoryScore% ($passed/$total) | $status |`n"
}

$mdReport += @"

## ä¸¥éé®é¢ (å¿é¡»ä¿®å¤)

"@

if ($auditResults.critical_issues.Count -gt 0) {
    foreach ($issue in $auditResults.critical_issues) {
        $mdReport += "- â?$issue`n"
    }
} else {
    $mdReport += "- â?æ ä¸¥éé®é¢`n"
}

$mdReport += @"

## è­¦åé®é¢ (å»ºè®®ä¿®å¤)

"@

if ($auditResults.warning_issues.Count -gt 0) {
    foreach ($issue in $auditResults.warning_issues) {
        $mdReport += "- â ï¸  $issue`n"
    }
} else {
    $mdReport += "- â?æ è­¦åé®é¢`n"
}

$mdReport += @"

## æ¹è¿å»ºè®®

"@

$uniqueRecommendations = $auditResults.recommendations | Select-Object -Unique
if ($uniqueRecommendations.Count -gt 0) {
    foreach ($recommendation in $uniqueRecommendations) {
        $mdReport += "- ð¡ $recommendation`n"
    }
} else {
    $mdReport += "- â?æ æ¹è¿å»ºè®®`n"
}

$mdReport += @"

## è¯¦ç»æ£æ¥ç»æ?
### 1. æä»¶ç»ææ£æ?"@

foreach ($check in $auditResults.categories.file_structure.checks) {
    $status = $check.passed ? "

â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 2. çæ¬ä¸è´æ§æ£æ?"@

foreach ($check in $auditResults.categories.version_consistency.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 3. å®å¨åè§æ£æ?"@

foreach ($check in $auditResults.categories.security_compliance.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 4. ææ¡£è´¨éæ£æ?"@

foreach ($check in $auditResults.categories.documentation_quality.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 5. åæ°æ®éªè¯?"@

foreach ($check in $auditResults.categories.metadata_validation.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 6. é¾æ¥éªè¯
"@

foreach ($check in $auditResults.categories.link_validation.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 7. ä»£ç è´¨éæ£æ?"@

foreach ($check in $auditResults.categories.code_quality.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 8. ä¾èµéªè¯
"@

foreach ($check in $auditResults.categories.dependency_validation.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 9. è®¸å¯è¯åè§æ£æ?"@

foreach ($check in $auditResults.categories.license_compliance.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

### 10. ClawHubç¹å®è¦æ±æ£æ?"@

foreach ($check in $auditResults.categories.clawhub_specific.checks) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.name): $($check.message)`n"
}

$mdReport += @"

## ClawHubå°±ç»ªç¶æ?
**$($jsonReport.audit_summary.clawhub_ready ? 'â?æè½å·²åå¤å¥½æäº¤å°ClawHub' : 'â?æè½å°æªåå¤å¥½æäº¤å°ClawHub')**

### åå¸åå¿é¡»å®æ?
"@

if ($auditResults.critical_issues.Count -gt 0) {
    $mdReport += "1. **ä¿®å¤ææä¸¥éé®é¢?* ($($auditResults.critical_issues.Count) ä¸?`n"
} else {
    $mdReport += "1. â?æ ä¸¥éé®é¢`n"
}

if ($auditResults.score.percentage -lt 95) {
    $mdReport += "2. **æé«æ»ä½åæ°å?5%ä»¥ä¸** (å½å: $($auditResults.score.percentage)%)`n"
} else {
    $mdReport += "2. â?æ»ä½åæ°è¾¾æ  ($($auditResults.score.percentage)%)`n"
}

$mdReport += @"
3. **è¿è¡æç»éªè¯?*: ä¿®å¤é®é¢åéæ°è¿è¡æ­¤å®¡æ ¸å·¥å·
4. **çæåå¸å?*: åå»ºZIPæ ¼å¼çåå¸å
5. **æµè¯å®è£**: å¨å¹²åç¯å¢ä¸­æµè¯æè½å®è£?6. **æäº¤å°ClawHub**: ä¸ä¼ å¹¶ç­å¾æ«æç»æ?
## åºäºç»éªçå»ºè®?
### 1. çæ¬ç®¡çæä½³å®è·?- ä½¿ç¨è¯­ä¹åçæ? MAJOR.MINOR.PATCH
- æææä»¶çæ¬å·å¿é¡»å®å¨ä¸è?- æ¯æ¬¡åå¸æ´æ°CHANGELOG.md
- çæ¬å·éå¢è§åæç¡®

### 2. é¾æ¥ç®¡çæä½³å®è·?- ææé¾æ¥å¿é¡»çå®ææ?- GitHubé¾æ¥æ ¼å¼æ­£ç¡®
- é¿åå ä½ç¬¦é¾æ?- å®ææ£æ¥é¾æ¥æææ?
### 3. å®å¨åè§æä½³å®è·?- 100%æ¬å°å¤çï¼æ ç½ç»ä»£ç 
- æç¡®çå®å¨å£°æ?- æå°æéåå?- å®æå®å¨å®¡æ¥

### 4. ææ¡£è´¨éæä½³å®è·?- å®æ´çæè½ææ¡?- æ¸æ°çå®è£è¯´æ?- è¯¦ç»çä½¿ç¨ç¤ºä¾?- å®æ´çAPIææ¡£

### 5. ä»£ç è´¨éæä½³å®è·?- ç¬¦åPEP8æ å
- éå½çä»£ç æ³¨é?- å®æ´çç±»åæç¤?- å¥å£®çéè¯¯å¤ç?
## å®¡æ ¸æ¡æ¶çæ¬
- **å·¥å·çæ¬**: ultimate_clawhub_audit.ps1 v1.0
- **æ¡æ¶çæ¬**: AISkinXå¢å¼ºç?v2.0 + ClawHubæè®­
- **åå»ºæ¶é´**: 2026-03-27
- **æ´æ°è®°å½**: åºäºAISleepGen ClawHubæ«æå¤±è´¥ç»éª
- **ç®æ **: ç¡®ä¿100%ä¸æ¬¡æ§éè¿ClawHubæ«æ

---

**æ¥åçææ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**å®¡æ ¸ç»è®º**: $($jsonReport.audit_summary.clawhub_ready ? 'â?éè¿' : 'â?æªéè¿')  
**ä¸ä¸æ­?*: $($jsonReport.audit_summary.clawhub_ready ? 'å¯ä»¥æäº¤å°ClawHub' : 'éè¦ä¿®å¤é®é¢åéæ°å®¡æ ¸')
"@

$mdFilePath = Join-Path $OutputDir "ultimate_audit_report.md"
Set-Content -Path $mdFilePath -Value $mdReport
Write-Host "è¯¦ç»Markdownæ¥åå·²ä¿å­å°: $mdFilePath" -ForegroundColor Cyan

# æç»ç»è®?Write-Host "`n=== æç»ç»è®?===" -ForegroundColor Cyan

if ($jsonReport.audit_summary.clawhub_ready) {
    Write-Host "â?æ­åï¼æè½å·²åå¤å¥½æäº¤å°ClawHub" -ForegroundColor Green
    Write-Host "å»ºè®®: å¯ä»¥ç´æ¥åå»ºåå¸åå¹¶æäº¤" -ForegroundColor Green
} else {
    if ($auditResults.critical_issues.Count -gt 0) {
        Write-Host "â?æè½å°æªåå¤å¥½ï¼æä¸¥éé®é¢éè¦ä¿®å¤? -ForegroundColor Red
        Write-Host "å»ºè®®: åä¿®å¤ææä¸¥éé®é¢ï¼ç¶åéæ°è¿è¡å®¡æ ¸" -ForegroundColor Red
    } elseif ($auditResults.score.percentage -lt 95) {
        Write-Host "â ï¸  æè½æ¥è¿å°±ç»ªï¼ä½åæ°æªè¾¾æ " -ForegroundColor Yellow
        Write-Host "å»ºè®®: ä¿®å¤è­¦åé®é¢ï¼æé«åæ°å°95%ä»¥ä¸" -ForegroundColor Yellow
    } else {
        Write-Host "â?æªç¥ç¶æï¼è¯·æ£æ¥è¯¦ç»æ¥å? -ForegroundColor Gray
    }
}

Write-Host "`nå®¡æ ¸å®æãè¯·æ¥çè¯¦ç»æ¥åè·åå·ä½ä¿¡æ¯ã? -ForegroundColor White
