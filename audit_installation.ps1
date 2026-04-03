# audit_installation.ps1
# å®è£åä½¿ç¨ä½éªç»´åº¦ä¸é¡¹æ£æ¥å·¥å?# æ£æ¥å®è£æ¹å¼æ ååãå®è£èæ¬å®å¨æ§ãä½¿ç¨è¯´æå®æ´æ§ãéè¯¯å¤çåå¥½æ?
param(
    [string]$SkillDir,
    [string]$OutputDir = ".\installation_audit",
    [switch]$Verbose = $false
)

Write-Host "=== å®è£åä½¿ç¨ä½éªå®¡æ ?===" -ForegroundColor Cyan
Write-Host "æ£æ¥æ¶é? $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "æè½ç®å½? $SkillDir" -ForegroundColor Cyan
Write-Host "è¾åºç®å½: $OutputDir" -ForegroundColor Cyan
Write-Host ""

# åå»ºè¾åºç®å½
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# åå§åæ£æ¥ç»æ?$checkResults = @{
    "installation_standardization" = @{}
    "installation_security" = @{}
    "usage_documentation" = @{}
    "error_handling" = @{}
    "overall_score" = 0
}

# è¾å©å½æ°
function Add-Check {
    param(
        [string]$Category,
        [string]$CheckName,
        [bool]$Passed,
        [string]$Message,
        [string]$FixSuggestion = "",
        [bool]$Critical = $false
    )
    
    if (-not $checkResults[$Category].ContainsKey($CheckName)) {
        $checkResults[$Category][$CheckName] = @{
            "passed" = $Passed
            "message" = $Message
            "fix_suggestion" = $FixSuggestion
            "critical" = $Critical
        }
    }
    
    if ($Passed) {
        Write-Host "  [PASS] $CheckName" -ForegroundColor Green
    } else {
        if ($Critical) {
            Write-Host "  [FAIL] $CheckName (Critical)" -ForegroundColor Red
        } else {
            Write-Host "  [WARN] $CheckName" -ForegroundColor Yellow
        }
        
        if ($FixSuggestion) {
            Write-Host "      Suggestion: $FixSuggestion" -ForegroundColor Cyan
        }
    }
}

# ============================================
# 1. å®è£æ¹å¼æ ååæ£æ?# ============================================
Write-Host "## 1. å®è£æ¹å¼æ ååæ£æ? -ForegroundColor Yellow

# 1.1 æ£æ¥èªå®ä¹å®è£èæ¬
$customInstallScripts = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $_.Name -match "^install\.(bat|sh|ps1)$" -or $_.Name -match "setup\.(bat|sh|ps1)$"
}

Add-Check -Category "installation_standardization" -CheckName "æ èªå®ä¹å®è£èæ¬" `
    -Passed ($customInstallScripts.Count -eq 0) `
    -Message "åç°èªå®ä¹å®è£èæ? $($customInstallScripts.Count) ä¸? `
    -FixSuggestion "ç§»é¤èªå®ä¹å®è£èæ¬ï¼ä½¿ç¨OpenClawæ åå®è£å½ä»¤" `
    -Critical $true

# 1.2 æ£æ¥SKILL.mdä¸­çå®è£è¯´æ
$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    $hasInstallationSection = $skillMdContent -match "å®è£|Installation"
    $hasStandardCommand = $skillMdContent -match "openclaw skill install|openclaw skills add"
    
    Add-Check -Category "installation_standardization" -CheckName "SKILL.mdæå®è£è¯´æ? `
        -Passed $hasInstallationSection `
        -Message "å®è£è¯´æ: $(if($hasInstallationSection){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?å®è£'ç« è" `
        -Critical $false
    
    Add-Check -Category "installation_standardization" -CheckName "ä½¿ç¨æ åå®è£å½ä»¤" `
        -Passed $hasStandardCommand `
        -Message "æ åå½ä»¤: $(if($hasStandardCommand){'æ?}else{'æ?})" `
        -FixSuggestion "ä½¿ç¨'openclaw skill install'æ åå½ä»¤" `
        -Critical $true
}

# 1.3 æ£æ¥README.mdä¸­çå®è£è¯´æ
$readmePath = Join-Path $SkillDir "README.md"
if (Test-Path $readmePath) {
    $readmeContent = Get-Content $readmePath -Raw
    $hasQuickStart = $readmeContent -match "å¿«éå¼å§|Quick Start|Getting Started"
    $hasInstallSteps = $readmeContent -match "1\..*å®è£|Step 1.*install"
    
    Add-Check -Category "installation_standardization" -CheckName "README.mdæå¿«éå¼å§? `
        -Passed $hasQuickStart `
        -Message "å¿«éå¼å§? $(if($hasQuickStart){'æ?}else{'æ?})" `
        -FixSuggestion "å¨README.mdä¸­æ·»å?å¿«éå¼å§?ç« è" `
        -Critical $false
    
    Add-Check -Category "installation_standardization" -CheckName "README.mdæå®è£æ­¥éª? `
        -Passed $hasInstallSteps `
        -Message "å®è£æ­¥éª¤: $(if($hasInstallSteps){'æ?}else{'æ?})" `
        -FixSuggestion "å¨README.mdä¸­æ·»å ç¼å·çå®è£æ­¥éª¤" `
        -Critical $false
}

# 1.4 æ£æ¥ç¯å¢è¦æ±è¯´æ?if (Test-Path $skillMdPath) {
    $hasEnvRequirements = $skillMdContent -match "ç¯å¢è¦æ±|Requirements|Prerequisites"
    $hasPythonVersion = $skillMdContent -match "Python.*\d+\.\d+" -or $skillMdContent -match "python.*\d+"
    
    Add-Check -Category "installation_standardization" -CheckName "æç¯å¢è¦æ±è¯´æ? `
        -Passed $hasEnvRequirements `
        -Message "ç¯å¢è¦æ±: $(if($hasEnvRequirements){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?ç¯å¢è¦æ±'ç« è" `
        -Critical $false
    
    Add-Check -Category "installation_standardization" -CheckName "æPythonçæ¬è¦æ±" `
        -Passed $hasPythonVersion `
        -Message "Pythonçæ¬: $(if($hasPythonVersion){'æ?}else{'æ?})" `
        -FixSuggestion "æç¡®è¯´ææéçPythonçæ¬" `
        -Critical $false
}

# ============================================
# 2. å®è£èæ¬å®å¨æ§æ£æ?# ============================================
Write-Host "`n## 2. å®è£èæ¬å®å¨æ§æ£æ? -ForegroundColor Yellow

# 2.1 æ£æ¥å±é©å®è£æä½?$dangerousInstallPatterns = @(
    "rm -rf", "del /f", "Remove-Item.*-Force",
    "format", "chmod 777", "sudo.*install",
    "wget.*|", "curl.*|", "powershell.*-EncodedCommand"
)

$dangerousOperations = @()
foreach ($script in $customInstallScripts) {
    try {
        $content = Get-Content $script.FullName -Raw
        foreach ($pattern in $dangerousInstallPatterns) {
            if ($content -match $pattern) {
                $dangerousOperations += "$($script.Name): $pattern"
            }
        }
    } catch {
        # å¿½ç¥æ æ³è¯»åçæä»?    }
}

Add-Check -Category "installation_security" -CheckName "æ å±é©å®è£æä½? `
    -Passed ($dangerousOperations.Count -eq 0) `
    -Message "åç°å±é©æä½: $($dangerousOperations.Count) å¤? `
    -FixSuggestion "ç§»é¤ææå±é©å®è£æä½? $($dangerousOperations -join '; ')" `
    -Critical $true

# 2.2 æ£æ¥æéæå°å
if ($customInstallScripts.Count -gt 0) {
    $elevatedOperations = @()
    foreach ($script in $customInstallScripts) {
        try {
            $content = Get-Content $script.FullName -Raw
            if ($content -match "sudo|RunAsAdministrator|elevated") {
                $elevatedOperations += $script.Name
            }
        } catch {
            # å¿½ç¥æ æ³è¯»åçæä»?        }
    }
    
    Add-Check -Category "installation_security" -CheckName "æéæå°å" `
        -Passed ($elevatedOperations.Count -eq 0) `
        -Message "éè¦ææçæä½: $($elevatedOperations.Count) å¤? `
        -FixSuggestion "é¿åéè¦ç®¡çåæéçå®è£æä½? `
        -Critical $false
}

# 2.3 æ£æ¥ç½ç»ä¸è½½å®å¨æ?$downloadOperations = @()
foreach ($script in $customInstallScripts) {
    try {
        $content = Get-Content $script.FullName -Raw
        if ($content -match "wget|curl|Invoke-WebRequest|Start-BitsTransfer") {
            $downloadOperations += $script.Name
        }
    } catch {
        # å¿½ç¥æ æ³è¯»åçæä»?    }
}

Add-Check -Category "installation_security" -CheckName "æ å±é©ç½ç»ä¸è½? `
    -Passed ($downloadOperations.Count -eq 0) `
    -Message "ç½ç»ä¸è½½æä½: $($downloadOperations.Count) å¤? `
    -FixSuggestion "é¿åå¨å®è£èæ¬ä¸­ä¸è½½æä»¶" `
    -Critical $true

# 2.4 æ£æ¥éè¯¯å¤ç?$hasErrorHandling = $false
foreach ($script in $customInstallScripts) {
    try {
        $content = Get-Content $script.FullName -Raw
        if ($content -match "try.*catch|if.*error|trap|Set-StrictMode") {
            $hasErrorHandling = $true
            break
        }
    } catch {
        # å¿½ç¥æ æ³è¯»åçæä»?    }
}

if ($customInstallScripts.Count -gt 0) {
    Add-Check -Category "installation_security" -CheckName "å®è£èæ¬æéè¯¯å¤ç? `
        -Passed $hasErrorHandling `
        -Message "éè¯¯å¤ç: $(if($hasErrorHandling){'æ?}else{'æ?})" `
        -FixSuggestion "å¨å®è£èæ¬ä¸­æ·»å éè¯¯å¤çæºå¶" `
        -Critical $false
}

# ============================================
# 3. ä½¿ç¨è¯´æå®æ´æ§æ£æ?# ============================================
Write-Host "`n## 3. ä½¿ç¨è¯´æå®æ´æ§æ£æ? -ForegroundColor Yellow

# 3.1 æ£æ¥åºæ¬ä½¿ç¨è¯´æ?if (Test-Path $skillMdPath) {
    $hasBasicUsage = $skillMdContent -match "ç¨æ³|Usage|åºæ¬ä½¿ç¨"
    $hasCommandExamples = $skillMdContent -match "å½ä»¤ç¤ºä¾|Examples|Example commands"
    $hasParameterExplanation = $skillMdContent -match "åæ°|Parameters|Arguments"
    
    Add-Check -Category "usage_documentation" -CheckName "æåºæ¬ç¨æ³è¯´æ? `
        -Passed $hasBasicUsage `
        -Message "åºæ¬ç¨æ³: $(if($hasBasicUsage){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?ç¨æ³'ç« è" `
        -Critical $false
    
    Add-Check -Category "usage_documentation" -CheckName "æå½ä»¤ç¤ºä¾? `
        -Passed $hasCommandExamples `
        -Message "å½ä»¤ç¤ºä¾: $(if($hasCommandExamples){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å å½ä»¤ç¤ºä¾? `
        -Critical $true
    
    Add-Check -Category "usage_documentation" -CheckName "æåæ°è¯´æ? `
        -Passed $hasParameterExplanation `
        -Message "åæ°è¯´æ: $(if($hasParameterExplanation){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å åæ°è¯´æ? `
        -Critical $false
}

# 3.2 æ£æ¥é«çº§ä½¿ç¨è¯´æ?if (Test-Path $skillMdPath) {
    $hasAdvancedUsage = $skillMdContent -match "é«çº§ç¨æ³|Advanced Usage"
    $hasConfigurationGuide = $skillMdContent -match "éç½®|Configuration"
    $hasIntegrationGuide = $skillMdContent -match "éæ|Integration"
    
    Add-Check -Category "usage_documentation" -CheckName "æé«çº§ç¨æ³è¯´æ? `
        -Passed $hasAdvancedUsage `
        -Message "é«çº§ç¨æ³: $(if($hasAdvancedUsage){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?é«çº§ç¨æ³'ç« è" `
        -Critical $false
    
    Add-Check -Category "usage_documentation" -CheckName "æéç½®æå? `
        -Passed $hasConfigurationGuide `
        -Message "éç½®æå: $(if($hasConfigurationGuide){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?éç½®'ç« è" `
        -Critical $false
    
    Add-Check -Category "usage_documentation" -CheckName "æéææå? `
        -Passed $hasIntegrationGuide `
        -Message "éææå: $(if($hasIntegrationGuide){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?éæ'ç« è" `
        -Critical $false
}

# 3.3 æ£æ¥å¸¸è§é®é¢è§£ç­?if (Test-Path $skillMdPath) {
    $hasFAQ = $skillMdContent -match "å¸¸è§é®é¢|FAQ|Frequently Asked Questions"
    $hasTroubleshooting = $skillMdContent -match "æéæé¤|Troubleshooting"
    
    Add-Check -Category "usage_documentation" -CheckName "æå¸¸è§é®é¢è§£ç­? `
        -Passed $hasFAQ `
        -Message "å¸¸è§é®é¢: $(if($hasFAQ){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?å¸¸è§é®é¢'ç« è" `
        -Critical $false
    
    Add-Check -Category "usage_documentation" -CheckName "ææéæé¤æå? `
        -Passed $hasTroubleshooting `
        -Message "æéæé¤: $(if($hasTroubleshooting){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?æéæé¤'ç« è" `
        -Critical $false
}

# 3.4 æ£æ¥ç¨æ·æ¯ææ¸ é?if (Test-Path $skillMdPath) {
    $hasSupportChannels = $skillMdContent -match "æ¯æ|Support|èç³»|Contact"
    $hasIssueReporting = $skillMdContent -match "æ¥åé®é¢|Report Issues|Bug Report"
    
    Add-Check -Category "usage_documentation" -CheckName "æç¨æ·æ¯ææ¸ é? `
        -Passed $hasSupportChannels `
        -Message "æ¯ææ¸ é: $(if($hasSupportChannels){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?æ¯æ'ç« è" `
        -Critical $false
    
    Add-Check -Category "usage_documentation" -CheckName "æé®é¢æ¥åæå? `
        -Passed $hasIssueReporting `
        -Message "é®é¢æ¥å: $(if($hasIssueReporting){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å é®é¢æ¥åæå? `
        -Critical $false
}

# ============================================
# 4. éè¯¯å¤çåå¥½æ§æ£æ?# ============================================
Write-Host "`n## 4. éè¯¯å¤çåå¥½æ§æ£æ? -ForegroundColor Yellow

# 4.1 æ£æ¥skill.pyä¸­çéè¯¯å¤ç
$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $hasTryCatch = $skillContent -match "try.*:|except.*:"
    $hasErrorMessages = $skillContent -match "éè¯¯|error|Error|å¤±è´¥|fail|Fail"
    $hasUserFriendlyErrors = $skillContent -match "è¯·æ£æ¥|Please check|å»ºè®®|å»ºè®®æ?
    
    Add-Check -Category "error_handling" -CheckName "skill.pyæéè¯¯å¤ç? `
        -Passed $hasTryCatch `
        -Message "try-catch: $(if($hasTryCatch){'æ?}else{'æ?})" `
        -FixSuggestion "å¨skill.pyä¸­æ·»å try-catchéè¯¯å¤ç" `
        -Critical $false
    
    Add-Check -Category "error_handling" -CheckName "skill.pyæéè¯¯ä¿¡æ? `
        -Passed $hasErrorMessages `
        -Message "éè¯¯ä¿¡æ¯: $(if($hasErrorMessages){'æ?}else{'æ?})" `
        -FixSuggestion "å¨skill.pyä¸­æ·»å æç¡®çéè¯¯ä¿¡æ¯" `
        -Critical $false
    
    Add-Check -Category "error_handling" -CheckName "skill.pyæåå¥½éè¯¯æç¤? `
        -Passed $hasUserFriendlyErrors `
        -Message "åå¥½æç¤º: $(if($hasUserFriendlyErrors){'æ?}else{'æ?})" `
        -FixSuggestion "å¨éè¯¯ä¿¡æ¯ä¸­æ·»å åå¥½çç¨æ·æç¤? `
        -Critical $false
}

# 4.2 æ£æ¥æ¥å¿è®°å½?if (Test-Path $skillPath) {
    $hasLogging = $skillContent -match "import logging|import loguru|logger\."
    $hasLogLevels = $skillContent -match "DEBUG|INFO|WARNING|ERROR|CRITICAL"
    
    Add-Check -Category "error_handling" -CheckName "ææ¥å¿è®°å½? `
        -Passed $hasLogging `
        -Message "æ¥å¿è®°å½: $(if($hasLogging){'æ?}else{'æ?})" `
        -FixSuggestion "å¨skill.pyä¸­æ·»å æ¥å¿è®°å½? `
        -Critical $false
    
    Add-Check -Category "error_handling" -CheckName "ææ¥å¿çº§å? `
        -Passed $hasLogLevels `
        -        -Message "æ¥å¿çº§å«: $(if($hasLogLevels){'æ?}else{'æ?})" `
        -FixSuggestion "ä½¿ç¨ä¸åçæ¥å¿çº§å«è®°å½ä¸åéè¦æ§çä¿¡æ¯" `
        -Critical $false
}

# 4.3 æ£æ¥è¾å¥éªè¯?if (Test-Path $skillPath) {
    $hasInputValidation = $skillContent -match "assert|if.*not.*:|validate|check.*input"
    $hasTypeChecking = $skillContent -match "isinstance|type\("
    
    Add-Check -Category "error_handling" -CheckName "æè¾å¥éªè¯? `
        -Passed $hasInputValidation `
        -Message "è¾å¥éªè¯: $(if($hasInputValidation){'æ?}else{'æ?})" `
        -FixSuggestion "å¨skill.pyä¸­æ·»å è¾å¥éªè¯? `
        -Critical $false
    
    Add-Check -Category "error_handling" -CheckName "æç±»åæ£æ? `
        -Passed $hasTypeChecking `
        -Message "ç±»åæ£æ? $(if($hasTypeChecking){'æ?}else{'æ?})" `
        -FixSuggestion "å¨skill.pyä¸­æ·»å ç±»åæ£æ? `
        -Critical $false
}

# 4.4 æ£æ¥ææ¡£ä¸­çéè¯¯å¤çè¯´æ?if (Test-Path $skillMdPath) {
    $hasErrorHandlingDoc = $skillMdContent -match "éè¯¯å¤ç|Error Handling"
    $hasCommonErrors = $skillMdContent -match "å¸¸è§éè¯¯|Common Errors"
    
    Add-Check -Category "error_handling" -CheckName "ææ¡£æéè¯¯å¤çè¯´æ? `
        -Passed $hasErrorHandlingDoc `
        -Message "éè¯¯å¤çææ¡£: $(if($hasErrorHandlingDoc){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?éè¯¯å¤ç'ç« è" `
        -Critical $false
    
    Add-Check -Category "error_handling" -CheckName "ææ¡£æå¸¸è§éè¯¯è¯´æ? `
        -Passed $hasCommonErrors `
        -Message "å¸¸è§éè¯¯ææ¡£: $(if($hasCommonErrors){'æ?}else{'æ?})" `
        -FixSuggestion "å¨SKILL.mdä¸­æ·»å?å¸¸è§éè¯¯'ç« è" `
        -Critical $false
}

# ============================================
# è®¡ç®åæ°åçææ¥å?# ============================================

# è®¡ç®åæ°
$totalChecks = 0
$passedChecks = 0

foreach ($category in $checkResults.Keys) {
    if ($category -ne "overall_score") {
        foreach ($checkName in $checkResults[$category].Keys) {
            $totalChecks++
            if ($checkResults[$category][$checkName].passed) {
                $passedChecks++
            }
        }
    }
}

if ($totalChecks -gt 0) {
    $score = [math]::Round(($passedChecks / $totalChecks) * 100, 2)
    $checkResults.overall_score = $score
}

# çææ¥å
Write-Host "`n=== å®è£åä½¿ç¨ä½éªå®¡æ ¸å®æ?===" -ForegroundColor Cyan
Write-Host "æ»ä½åæ°: $score%" -ForegroundColor Cyan
Write-Host "æ£æ¥é¡¹: $passedChecks/$totalChecks éè¿" -ForegroundColor Cyan

# åç±»æ¥å
Write-Host "`n## åç±»åæ°" -ForegroundColor Yellow

$categories = @{
    "installation_standardization" = "å®è£æ¹å¼æ åå?
    "installation_security" = "å®è£èæ¬å®å¨æ?
    "usage_documentation" = "ä½¿ç¨è¯´æå®æ´æ?
    "error_handling" = "éè¯¯å¤çåå¥½æ?
}

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryChecks = $checkResults[$categoryKey]
    
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $color = if ($categoryScore -ge 90) { "Green" } elseif ($categoryScore -ge 70) { "Yellow" } else { "Red" }
        
        Write-Host "  $categoryName: $categoryScore% ($passed/$total)" -ForegroundColor $color
    }
}

# ä¸¥éé®é¢æ¥å
$criticalIssues = @()
foreach ($category in $checkResults.Keys) {
    if ($category -ne "overall_score") {
        foreach ($checkName in $checkResults[$category].Keys) {
            $check = $checkResults[$category][$checkName]
            if (-not $check.passed -and $check.critical) {
                $criticalIssues += "$categoryName: $checkName - $($check.message)"
            }
        }
    }
}

if ($criticalIssues.Count -gt 0) {
    Write-Host "`n## ä¸¥éé®é¢ (å¿é¡»ä¿®å¤)" -ForegroundColor Red
    foreach ($issue in $criticalIssues) {
        Write-Host "  â?$issue" -ForegroundColor Red
    }
}

# è­¦åé®é¢æ¥å
$warningIssues = @()
foreach ($category in $checkResults.Keys) {
    if ($category -ne "overall_score") {
        foreach ($checkName in $checkResults[$category].Keys) {
            $check = $checkResults[$category][$checkName]
            if (-not $check.passed -and -not $check.critical) {
                $warningIssues += "$categoryName: $checkName - $($check.message)"
            }
        }
    }
}

if ($warningIssues.Count -gt 0) {
    Write-Host "`n## è­¦åé®é¢ (å»ºè®®ä¿®å¤)" -ForegroundColor Yellow
    foreach ($issue in $warningIssues) {
        Write-Host "  â ï¸  $issue" -ForegroundColor Yellow
    }
}

# çæJSONæ¥å
$jsonReport = @{
    "audit_summary" = @{
        "skill_directory" = $SkillDir
        "audit_time" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "total_checks" = $totalChecks
        "passed_checks" = $passedChecks
        "overall_score" = $score
        "critical_issues_count" = $criticalIssues.Count
        "warning_issues_count" = $warningIssues.Count
    }
    "category_scores" = @{}
    "detailed_results" = @{}
}

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryChecks = $checkResults[$categoryKey]
    
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $jsonReport.category_scores[$categoryName] = $categoryScore
        
        $detailedChecks = @()
        foreach ($checkName in $categoryChecks.Keys) {
            $check = $categoryChecks[$checkName]
            $detailedChecks += @{
                "check_name" = $checkName
                "passed" = $check.passed
                "message" = $check.message
                "critical" = $check.critical
                "fix_suggestion" = $check.fix_suggestion
            }
        }
        $jsonReport.detailed_results[$categoryName] = $detailedChecks
    }
}

$jsonFilePath = Join-Path $OutputDir "installation_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`nè¯¦ç»JSONæ¥åå·²ä¿å­å°: $jsonFilePath" -ForegroundColor Cyan

# çæMarkdownæ¥å
$mdReport = @"
# å®è£åä½¿ç¨ä½éªå®¡æ ¸æ¥å?
## å®¡æ ¸ä¿¡æ¯
- **æè½ç®å½?*: $SkillDir
- **å®¡æ ¸æ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **å®¡æ ¸å·¥å·**: audit_installation.ps1 v1.0

## æ»ä½è¯å
**æ»ä½åæ°: $score%**

| ææ  | ç»æ |
|------|------|
| æ»æ£æ¥é¡¹ | $totalChecks |
| éè¿é¡?| $passedChecks |
| ä¸¥éé®é¢ | $($criticalIssues.Count) |
| è­¦åé®é¢ | $($warningIssues.Count) |

## åç±»åæ°

| åç±» | åæ° | ç¶æ?|
|------|------|------|
"@

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryScore = $jsonReport.category_scores[$categoryName]
    
    $status = if ($categoryScore -ge 90) { "â?ä¼ç§" } elseif ($categoryScore -ge 70) { "â ï¸ è¯å¥½" } else { "â?éæ¹è¿" }
    
    $mdReport += "| $categoryName | $categoryScore% | $status |`n"
}

$mdReport += @"

## è¯¦ç»æ£æ¥ç»æ?
### 1. å®è£æ¹å¼æ åå?"@

foreach ($check in $checkResults.installation_standardization.Values) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.message)`n"
}

$mdReport += @"

### 2. å®è£èæ¬å®å¨æ?"@

foreach ($check in $checkResults.installation_security.Values) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.message)`n"
}

$mdReport += @"

### 3. ä½¿ç¨è¯´æå®æ´æ?"@

foreach ($check in $checkResults.usage_documentation.Values) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.message)`n"
}

$mdReport += @"

### 4. éè¯¯å¤çåå¥½æ?"@

foreach ($check in $checkResults.error_handling.Values) {
    $status = $check.passed ? "â? : "â?
    $mdReport += "- $status $($check.message)`n"
}

$mdReport += @"

## æ¹è¿å»ºè®®

### ç«å³è¡å¨
"@

if ($criticalIssues.Count -gt 0) {
    $mdReport += "1. **ä¿®å¤ææä¸¥éé®é¢?* ($($criticalIssues.Count) ä¸?`n"
} else {
    $mdReport += "1. â?æ éè¦ç«å³è¡å¨çé®é¢`n"
}

if ($score -lt 90) {
    $mdReport += "2. **æé«æ»ä½åæ°å?0%ä»¥ä¸** (å½å: $score%)`n"
} else {
    $mdReport += "2. â?æ»ä½åæ°è¾¾æ  ($score%)`n"
}

$mdReport += @"

### æä½³å®è·µå»ºè®?1. **ä½¿ç¨æ åå®è£å½ä»¤**: å§ç»ä½¿ç¨`openclaw skill install`æ åå½ä»¤
2. **é¿åèªå®ä¹èæ?*: ä¸è¦åå»ºinstall.batãinstall.shç­èªå®ä¹èæ¬
3. **å®åä½¿ç¨ææ¡£**: ç¡®ä¿æå®æ´çå¿«éå¼å§ãå½ä»¤ç¤ºä¾ãåæ°è¯´æ?4. **åå¥½éè¯¯å¤ç**: æä¾æ¸æ°çéè¯¯ä¿¡æ¯åè§£å³æ¹æ¡
5. **ç¨æ·æ¯ææ¸ é**: æä¾é®é¢æ¥ååæ¯ææ¸ é?
### å®è£ä½éªæ å
- â?**æ åå?*: ä½¿ç¨OpenClawæ åå®è£æµç¨
- â?**å®å¨æ?*: æ å±é©æä½ï¼æéæå°å
- â?**å®æ´æ?*: æå®æ´çä½¿ç¨ææ¡£åç¤ºä¾?- â?**åå¥½æ?*: éè¯¯å¤çåå¥½ï¼æè§£å³æ¹æ¡

## å®¡æ ¸æ¡æ¶çæ¬
- **å·¥å·çæ¬**: audit_installation.ps1 v1.0
- **æ¡æ¶çæ¬**: å®ç¾ClawHubå®¡æ ¸æ¡æ¶ - ç»´åº¦5
- **åå»ºæ¶é´**: 2026-03-27
- **ç®æ **: ç¡®ä¿å®è£åä½¿ç¨ä½éªè¾¾å°ClawHubæ å

---

**æ¥åçææ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**å®¡æ ¸ç»è®º**: $(if($score -ge 90){'â?éè¿'}elseif($score -ge 70){'â ï¸ éè¦æ¹è¿?}else{'â?æªéè¿'})  
**ä¸ä¸æ­?*: $(if($score -ge 90){'å¯ä»¥ç»§ç»­å¶ä»ç»´åº¦å®¡æ ¸'}else{'éè¦ä¿®å¤é®é¢åéæ°å®¡æ ¸'})
"@

$mdFilePath = Join-Path $OutputDir "installation_audit_report.md"
Set-Content -Path $mdFilePath -Value $mdReport
Write-Host "è¯¦ç»Markdownæ¥åå·²ä¿å­å°: $mdFilePath" -ForegroundColor Cyan

# æç»å»ºè®?Write-Host "`n=== æç»å»ºè®?===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "â?ä¼ç§! å®è£åä½¿ç¨ä½éªç¬¦åClawHubæ å" -ForegroundColor Green
    Write-Host "å»ºè®®: å¯ä»¥ç»§ç»­å¶ä»ç»´åº¦çå®¡æ ? -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "â ï¸ è¯å¥½ï¼ä½ææ¹è¿ç©ºé? -ForegroundColor Yellow
    Write-Host "å»ºè®®: ä¿®å¤è­¦åé®é¢ï¼æé«åæ°å°90%ä»¥ä¸" -ForegroundColor Yellow
} else {
    Write-Host "â?éè¦æ¹è¿? -ForegroundColor Red
    Write-Host "å»ºè®®: å¿é¡»ä¿®å¤ä¸¥éé®é¢åååå¸" -ForegroundColor Red
}

Write-Host "`nå®¡æ ¸å®æãè¯·æ¥çè¯¦ç»æ¥åè·åå·ä½æ¹è¿å»ºè®®ã? -ForegroundColor White
