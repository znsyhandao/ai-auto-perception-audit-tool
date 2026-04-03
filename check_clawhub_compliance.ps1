# check_clawhub_compliance.ps1
# ClawHubæ·±åº¦åè§æ£æ¥å·¥å?# åºäº2026-03-27 AISleepGenæ«æå¤±è´¥æè®­
# æ¨¡æClawHubçæ·±åº¦å®å¨æ£æ¥ï¼åæ¬ææ¡£ä¸è´æ§ãæ¶æçç¾ãæ¨¡ææ§è¡ãåå²æ¸ç?
param(
    [string]$SkillDir,
    [string]$OutputDir = ".\clawhub_audit",
    [switch]$FixIssues = $false
)

Write-Host "=== ClawHubæ·±åº¦åè§æ£æ?===" -ForegroundColor Cyan
Write-Host "æ£æ¥æ¶é? $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "æè½ç®å½? $SkillDir"
Write-Host "è¾åºç®å½: $OutputDir"
Write-Host "ä¿®å¤æ¨¡å¼: $($FixIssues ? 'å¯ç¨' : 'ç¦ç¨')"
Write-Host "åºäºæ¡æ¶: AISkinXå¢å¼ºç?v2.0 (ClawHubæè®­)"
Write-Host ""

# åå»ºè¾åºç®å½
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# æ£æ?: æè½ç®å½æ¯å¦å­å?if (-not (Test-Path $SkillDir)) {
    Write-Host "[éè¯¯] æè½ç®å½ä¸å­å¨: $SkillDir" -ForegroundColor Red
    exit 1
}

# åå§åæ£æ¥ç»æ?$checkResults = @{
    "basic_compliance" = @{}
    "documentation_consistency" = @{}
    "architectural_consistency" = @{}
    "simulation_detection" = @{}
    "historical_cleanup" = @{}
    "import_declaration" = @{}
    "overall_score" = 0
}

# æ£æ?: åºç¡åè§æ£æ?(é¶æ®µ1)
Write-Host "## é¶æ®µ1: åºç¡åè§æ£æ? -ForegroundColor Yellow
$basicChecks = @{
    "required_files" = @("skill.py", "config.yaml", "SKILL.md", "package.json")
    "prohibited_extensions" = @(".ps1", ".bat", ".exe", ".dll", ".backup", ".js")
    "max_folder_count" = 20
}

# 2.1 æ£æ¥å¿éæä»¶
Write-Host "`n2.1 å¿éæä»¶æ£æ? -ForegroundColor White
$missingFiles = @()
foreach ($file in $basicChecks.required_files) {
    $filePath = Join-Path $SkillDir $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file" -ForegroundColor Green
        $checkResults.basic_compliance["required_file_$file"] = $true
    } else {
        Write-Host "  [ç¼ºå¤±] $file" -ForegroundColor Red
        $missingFiles += $file
        $checkResults.basic_compliance["required_file_$file"] = $false
    }
}

# 2.2 æ£æ¥ç¦æ­¢æä»?Write-Host "`n2.2 ç¦æ­¢æä»¶æ£æ? -ForegroundColor White
$prohibitedFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $basicChecks.prohibited_extensions -contains $_.Extension
}

if ($prohibitedFiles.Count -eq 0) {
    Write-Host "  [OK] æ ç¦æ­¢æä»? -ForegroundColor Green
    $checkResults.basic_compliance["no_prohibited_files"] = $true
} else {
    Write-Host "  [è­¦å] åç°ç¦æ­¢æä»¶ ($($prohibitedFiles.Count) ä¸?" -ForegroundColor Yellow
    foreach ($file in $prohibitedFiles) {
        Write-Host "    - $($file.Name)" -ForegroundColor Yellow
    }
    $checkResults.basic_compliance["no_prohibited_files"] = $false
    
    # å¦æå¯ç¨ä¿®å¤æ¨¡å¼ï¼å é¤ç¦æ­¢æä»?    if ($FixIssues) {
        Write-Host "  [ä¿®å¤] å é¤ç¦æ­¢æä»¶..." -ForegroundColor Cyan
        $prohibitedFiles | Remove-Item -Force
        Write-Host "  [å®æ] ç¦æ­¢æä»¶å·²å é? -ForegroundColor Green
    }
}

# æ£æ?: ææ¡£ä¸è´æ§æ£æ?(é¶æ®µ2 - æ·±åº¦æ£æ?
Write-Host "`n## é¶æ®µ2: ææ¡£ä¸è´æ§æ£æ?(æ·±åº¦)" -ForegroundColor Yellow

# 3.1 æåææ¡£å£°æ
Write-Host "`n3.1 æåææ¡£å£°æ" -ForegroundColor White
$declarations = @{
    "pure_python" = $false
    "no_shell_commands" = $false
    "real_computations" = $false
    "local_only" = $false
    "no_network" = $false
    "stdlib_only" = $false
}

# ä»SKILL.mdæåå£°æ
$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    
    # æ£æ¥å£°æå³é®è¯
    $declarations.pure_python = $skillMdContent -match "çº¯Python|pure python" -or $skillMdContent -match "æ Node|no node"
    $declarations.no_shell_commands = $skillMdContent -match "æ shell|no shell|æ subprocess|no subprocess"
    $declarations.real_computations = $skillMdContent -match "çå®è®¡ç®|real computation|ç»ä¸æ¨¡æ|no simulation"
    $declarations.local_only = $skillMdContent -match "100%æ¬å°|local only|æ ç½ç»|no network"
    $declarations.no_network = $skillMdContent -match "æ ç½ç»|no network|æ requests|no requests"
    $declarations.stdlib_only = $skillMdContent -match "ä»æ ååº|stdlib only|æ å¤é¨ä¾èµ|no external"
    
    Write-Host "  [ä¿¡æ¯] ä»SKILL.mdæåå£°æ:" -ForegroundColor Cyan
    foreach ($key in $declarations.Keys) {
        $status = $declarations[$key] ? "å£°æå­å¨" : "æªå£°æ?
        Write-Host "    - $key : $status" -ForegroundColor Cyan
        $checkResults.documentation_consistency["declared_$key"] = $declarations[$key]
    }
} else {
    Write-Host "  [éè¯¯] SKILL.mdä¸å­å? -ForegroundColor Red
}

# 3.2 éªè¯ä»£ç å®ç°
Write-Host "`n3.2 éªè¯ä»£ç å®ç°" -ForegroundColor White

# æ£æ¥skill.py
$skillPyPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPyPath) {
    $skillPyContent = Get-Content $skillPyPath -Raw
    
    # éªè¯çº¯Pythonå£°æ
    $jsFiles = Get-ChildItem -Path $SkillDir -Filter "*.js" -File
    $isPurePython = $jsFiles.Count -eq 0
    
    if ($declarations.pure_python) {
        if ($isPurePython) {
            Write-Host "  [OK] çº¯Pythonå£°æéªè¯éè¿" -ForegroundColor Green
            $checkResults.documentation_consistency["verified_pure_python"] = $true
        } else {
            Write-Host "  [çç¾] å£°æçº¯Pythonä½åç°JSæä»¶" -ForegroundColor Red
            $checkResults.documentation_consistency["verified_pure_python"] = $false
        }
    }
    
    # éªè¯æ shellå½ä»¤å£°æ
    $hasSubprocess = $skillPyContent -match "import subprocess|from subprocess"
    if ($declarations.no_shell_commands) {
        if (-not $hasSubprocess) {
            Write-Host "  [OK] æ shellå½ä»¤å£°æéªè¯éè¿" -ForegroundColor Green
            $checkResults.documentation_consistency["verified_no_shell"] = $true
        } else {
            Write-Host "  [çç¾] å£°ææ shellå½ä»¤ä½å¯¼å¥subprocess" -ForegroundColor Red
            $checkResults.documentation_consistency["verified_no_shell"] = $false
        }
    }
    
    # éªè¯æ ç½ç»å£°æ?    $hasNetworkImports = $skillPyContent -match "import requests|import urllib|import socket|import http"
    if ($declarations.no_network) {
        if (-not $hasNetworkImports) {
            Write-Host "  [OK] æ ç½ç»å£°æéªè¯éè¿" -ForegroundColor Green
            $checkResults.documentation_consistency["verified_no_network"] = $true
        } else {
            Write-Host "  [çç¾] å£°ææ ç½ç»ä½å¯¼å¥ç½ç»æ¨¡å" -ForegroundColor Red
            $checkResults.documentation_consistency["verified_no_network"] = $false
        }
    }
    
    # æ£æ¥æ¨¡æå½æ?    $hasSimulation = $skillPyContent -match "simulate|mock|fake|dummy|placeholder"
    if ($declarations.real_computations) {
        if (-not $hasSimulation) {
            Write-Host "  [OK] çå®è®¡ç®å£°æéªè¯éè¿" -ForegroundColor Green
            $checkResults.documentation_consistency["verified_real_computations"] = $true
        } else {
            Write-Host "  [çç¾] å£°æçå®è®¡ç®ä½åç°æ¨¡æå½æ? -ForegroundColor Red
            $checkResults.documentation_consistency["verified_real_computations"] = $false
        }
    }
} else {
    Write-Host "  [éè¯¯] skill.pyä¸å­å? -ForegroundColor Red
}

# æ£æ?: æ¶æä¸è´æ§æ£æ?Write-Host "`n## é¶æ®µ3: æ¶æä¸è´æ§æ£æ? -ForegroundColor Yellow

# 4.1 æ£æ¥å®ç°è·¯å¾?Write-Host "`n4.1 å®ç°è·¯å¾æ£æ? -ForegroundColor White
$implementationPaths = @()

# æ£æ¥è¯­è¨ç±»å
$pythonFiles = Get-ChildItem -Path $SkillDir -Filter "*.py" -File
$jsFiles = Get-ChildItem -Path $SkillDir -Filter "*.js" -File
$otherFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Extension -notin @(".py", ".md", ".yaml", ".yml", ".json", ".txt")
}

if ($pythonFiles.Count -gt 0) { $implementationPaths += "Python" }
if ($jsFiles.Count -gt 0) { $implementationPaths += "JavaScript" }
if ($otherFiles.Count -gt 0) { $implementationPaths += "å¶ä»($($otherFiles.Count))" }

if ($implementationPaths.Count -eq 1) {
    Write-Host "  [OK] åä¸å®ç°è·¯å¾: $($implementationPaths[0])" -ForegroundColor Green
    $checkResults.architectural_consistency["single_implementation"] = $true
} else {
    Write-Host "  [è­¦å] å¤å®ç°è·¯å¾? $($implementationPaths -join ', ')" -ForegroundColor Yellow
    $checkResults.architectural_consistency["single_implementation"] = $false
}

# 4.2 æ£æ¥åè£å¨å±?Write-Host "`n4.2 åè£å¨å±æ£æ? -ForegroundColor White
$wrapperFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "wrapper|adapter|bridge|proxy|shim"
}

if ($wrapperFiles.Count -eq 0) {
    Write-Host "  [OK] æ åè£å¨å±? -ForegroundColor Green
    $checkResults.architectural_consistency["no_wrappers"] = $true
} else {
    Write-Host "  [è­¦å] åç°åè£å¨æä»?($($wrapperFiles.Count) ä¸?" -ForegroundColor Yellow
    foreach ($file in $wrapperFiles) {
        Write-Host "    - $($file.Name)" -ForegroundColor Yellow
    }
    $checkResults.architectural_consistency["no_wrappers"] = $false
}

# æ£æ?: æ¨¡ææ§è¡æ£æ?Write-Host "`n## é¶æ®µ4: æ¨¡ææ§è¡æ£æ? -ForegroundColor Yellow

# 5.1 æ£æ¥æ¨¡æå³é®è¯
Write-Host "`n5.1 æ¨¡æå³é®è¯æ£æ? -ForegroundColor White
$simulationPatterns = @(
    "simulate", "mock", "fake", "dummy", "placeholder",
    "ç¤ºä¾æ°æ®", "æµè¯æ°æ®", "æ¨¡æç»æ", "åæ°æ?
)

$simulationFiles = @()
foreach ($file in (Get-ChildItem -Path $SkillDir -File -Recurse)) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction Stop
        foreach ($pattern in $simulationPatterns) {
            if ($content -match $pattern) {
                $simulationFiles += @{
                    File = $file.Name
                    Pattern = $pattern
                    Line = ($content -split "`n" | Select-String $pattern | Select-Object -First 1).LineNumber
                }
                break
            }
        }
    } catch {
        # è·³è¿äºè¿å¶æä»?    }
}

if ($simulationFiles.Count -eq 0) {
    Write-Host "  [OK] æªåç°æ¨¡ææ§è¡? -ForegroundColor Green
    $checkResults.simulation_detection["no_simulation"] = $true
} else {
    Write-Host "  [è­¦å] åç°æ¨¡ææ§è¡ ($($simulationFiles.Count) å¤?" -ForegroundColor Yellow
    foreach ($sim in $simulationFiles) {
        Write-Host "    - $($sim.File): $($sim.Pattern) (è¡? $($sim.Line))" -ForegroundColor Yellow
    }
    $checkResults.simulation_detection["no_simulation"] = $false
}

# æ£æ?: åå²æ¸çæ£æ?Write-Host "`n## é¶æ®µ5: åå²æ¸çæ£æ? -ForegroundColor Yellow

# 6.1 æ£æ¥å¤ä»½æä»?Write-Host "`n6.1 å¤ä»½æä»¶æ£æ? -ForegroundColor White
$backupFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $_.Name -match "\.backup$|\.old$|_backup|_old|å¤ä»½"
}

if ($backupFiles.Count -eq 0) {
    Write-Host "  [OK] æ å¤ä»½æä»? -ForegroundColor Green
    $checkResults.historical_cleanup["no_backup_files"] = $true
} else {
    Write-Host "  [è­¦å] åç°å¤ä»½æä»¶ ($($backupFiles.Count) ä¸?" -ForegroundColor Yellow
    foreach ($file in $backupFiles) {
        Write-Host "    - $($file.Name)" -ForegroundColor Yellow
    }
    $checkResults.historical_cleanup["no_backup_files"] = $false
    
    # å¦æå¯ç¨ä¿®å¤æ¨¡å¼ï¼å é¤å¤ä»½æä»?    if ($FixIssues) {
        Write-Host "  [ä¿®å¤] å é¤å¤ä»½æä»¶..." -ForegroundColor Cyan
        $backupFiles | Remove-Item -Force
        Write-Host "  [å®æ] å¤ä»½æä»¶å·²å é? -ForegroundColor Green
    }
}

# 6.2 æ£æ¥å±é©ç»ä»?Write-Host "`n6.2 å±é©ç»ä»¶æ£æ? -ForegroundColor White
$dangerousPatterns = @(
    "child_process\.exec", "os\.system", "subprocess\.Popen",
    "eval\(", "exec\(", "compile\("
)

$dangerousFiles = @()
foreach ($file in (Get-ChildItem -Path $SkillDir -File -Recurse -Filter "*.py")) {
    try {
        $content = Get-Content $file.FullName -Raw -ErrorAction Stop
        foreach ($pattern in $dangerousPatterns) {
            if ($content -match $pattern) {
                $dangerousFiles += @{
                    File = $file.Name
                    Pattern = $pattern
                    Line = ($content -split "`n" | Select-String $pattern | Select-Object -First 1).LineNumber
                }
                break
            }
        }
    } catch {
        # è·³è¿æ æ³è¯»åçæä»?    }
}

if ($dangerousFiles.Count -eq 0) {
    Write-Host "  [OK] æ å±é©ç»ä»? -ForegroundColor Green
    $checkResults.historical_cleanup["no_dangerous_components"] = $true
} else {
    Write-Host "  [å±é©] åç°å±é©ç»ä»¶ ($($dangerousFiles.Count) å¤?" -ForegroundColor Red
    foreach ($danger in $dangerousFiles) {
        Write-Host "    - $($danger.File): $($danger.Pattern) (è¡? $($danger.Line))" -ForegroundColor Red
    }
    $checkResults.historical_cleanup["no_dangerous_components"] = $false
}

# æ£æ?: å¯¼å¥å£°ææ£æ?Write-Host "`n## é¶æ®µ6: å¯¼å¥å£°ææ£æ? -ForegroundColor Yellow

# 7.1 æ£æ¥å¯¼å¥è¯­å?Write-Host "`n7.1 å¯¼å¥è¯­å¥åæ" -ForegroundColor White
if (Test-Path $skillPyPath) {
    $importLines = Select-String -Path $skillPyPath -Pattern "^import |^from " | Select-Object -ExpandProperty Line
    
    Write-Host "  [ä¿¡æ¯] åç°å¯¼å¥è¯­å¥ ($($importLines.Count) ä¸?:" -ForegroundColor Cyan
    foreach ($line in $importLines) {
        Write-Host "    - $line" -ForegroundColor Cyan
    }
    
    # æ£æ¥æ ååº vs ç¬¬ä¸æ¹åº
    $stdlibImports = @()
    $thirdpartyImports = @()
    
    # å¸¸è§æ ååº?    $commonStdlib = @("    "os", "sys", "json", "csv", "math", "statistics", "datetime", 
    "time", "pathlib", "typing", "dataclasses", "enum", "collections"
    
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
            $thirdpartyImports += $line
        }
    }
    
    if ($thirdpartyImports.Count -eq 0) {
        Write-Host "  [OK] ä»æ ååºå¯¼å¥" -ForegroundColor Green
        $checkResults.import_declaration["stdlib_only"] = $true
    } else {
        Write-Host "  [ä¿¡æ¯] ç¬¬ä¸æ¹åºå¯¼å¥ ($($thirdpartyImports.Count) ä¸?:" -ForegroundColor Yellow
        foreach ($import in $thirdpartyImports) {
            Write-Host "    - $import" -ForegroundColor Yellow
        }
        $checkResults.import_declaration["stdlib_only"] = $false
    }
}

# çæç»¼åæ¥å
Write-Host "`n=== ç»¼åæ£æ¥æ¥å?===" -ForegroundColor Cyan

# è®¡ç®åæ°
$totalChecks = 0
$passedChecks = 0

foreach ($category in $checkResults.Keys) {
    if ($category -ne "overall_score") {
        foreach ($check in $checkResults[$category].Keys) {
            $totalChecks++
            if ($checkResults[$category][$check] -eq $true) {
                $passedChecks++
            }
        }
    }
}

if ($totalChecks -gt 0) {
    $score = [math]::Round(($passedChecks / $totalChecks) * 100, 2)
    $checkResults.overall_score = $score
}

Write-Host "æ£æ¥å®ææ¶é? $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "æ»æ£æ¥é¡¹: $totalChecks"
Write-Host "éè¿é¡? $passedChecks"
Write-Host "åè§åæ°: $score%"

# åç±»æ¥å
Write-Host "`n## åç±»æ¥å" -ForegroundColor Yellow

$categories = @{
    "basic_compliance" = "åºç¡åè§"
    "documentation_consistency" = "ææ¡£ä¸è´æ?
    "architectural_consistency" = "æ¶æä¸è´æ?
    "simulation_detection" = "æ¨¡ææ§è¡"
    "historical_cleanup" = "åå²æ¸ç"
    "import_declaration" = "å¯¼å¥å£°æ"
}

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryResults = $checkResults[$categoryKey]
    
    if ($categoryResults.Count -gt 0) {
        $passed = ($categoryResults.Values | Where-Object { $_ -eq $true }).Count
        $total = $categoryResults.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        Write-Host "`n$categoryName ($categoryScore%)" -ForegroundColor White
        foreach ($check in $categoryResults.Keys) {
            $status = $categoryResults[$check] ? "â? : "â?
            $checkName = $check -replace "_", " "
            Write-Host "  $status $checkName" -ForegroundColor $($categoryResults[$check] ? "Green" : "Red")
        }
    }
}

# çæè¯¦ç»æ¥åæä»¶
$reportFile = Join-Path $OutputDir "clawhub_compliance_report.md"
$reportContent = @"
# ClawHubæ·±åº¦åè§æ£æ¥æ¥å?
## æ£æ¥ä¿¡æ?- **æ£æ¥æ¶é?*: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **æè½ç®å½?*: $SkillDir
- **æ£æ¥å·¥å?*: check_clawhub_compliance.ps1 v1.0
- **åºäºæ¡æ¶**: AISkinXå¢å¼ºç?v2.0 (ClawHubæè®­)

## æ»ä½è¯å
**åè§åæ°: $score%**

| æ£æ¥ç±»å?| åæ° | ç¶æ?|
|----------|------|------|
"@

foreach ($categoryKey in $categories.Keys) {
    $categoryName = $categories[$categoryKey]
    $categoryResults = $checkResults[$categoryKey]
    
    if ($categoryResults.Count -gt 0) {
        $passed = ($categoryResults.Values | Where-Object { $_ -eq $true }).Count
        $total = $categoryResults.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        $status = $categoryScore -ge 80 ? "â?éè¿" : $categoryScore -ge 60 ? "â ï¸ è­¦å" : "â?å¤±è´¥"
        
        $reportContent += "| $categoryName | $categoryScore% | $status |`n"
    }
}

$reportContent += @"

## è¯¦ç»æ£æ¥ç»æ?
### 1. åºç¡åè§æ£æ?"@

foreach ($check in $checkResults.basic_compliance.Keys) {
    $status = $checkResults.basic_compliance[$check] ? "â?éè¿" : "â?å¤±è´¥"
    $checkName = $check -replace "_", " "
    $reportContent += "- $checkName: $status`n"
}

$reportContent += @"

### 2. ææ¡£ä¸è´æ§æ£æ?"@

foreach ($check in $checkResults.documentation_consistency.Keys) {
    $status = $checkResults.documentation_consistency[$check] ? "â?éè¿" : "â?å¤±è´¥"
    $checkName = $check -replace "_", " "
    $reportContent += "- $checkName: $status`n"
}

$reportContent += @"

### 3. æ¶æä¸è´æ§æ£æ?"@

foreach ($check in $checkResults.architectural_consistency.Keys) {
    $status = $checkResults.architectural_consistency[$check] ? "â?éè¿" : "â?å¤±è´¥"
    $checkName = $check -replace "_", " "
    $reportContent += "- $checkName: $status`n"
}

$reportContent += @"

### 4. æ¨¡ææ§è¡æ£æ?"@

foreach ($check in $checkResults.simulation_detection.Keys) {
    $status = $checkResults.simulation_detection[$check] ? "â?éè¿" : "â?å¤±è´¥"
    $checkName = $check -replace "_", " "
    $reportContent += "- $checkName: $status`n"
}

$reportContent += @"

### 5. åå²æ¸çæ£æ?"@

foreach ($check in $checkResults.historical_cleanup.Keys) {
    $status = $checkResults.historical_cleanup[$check] ? "â?éè¿" : "â?å¤±è´¥"
    $checkName = $check -replace "_", " "
    $reportContent += "- $checkName: $status`n"
}

$reportContent += @"

### 6. å¯¼å¥å£°ææ£æ?"@

foreach ($check in $checkResults.import_declaration.Keys) {
    $status = $checkResults.import_declaration[$check] ? "â?éè¿" : "â?å¤±è´¥"
    $checkName = $check -replace "_", " "
    $reportContent += "- $checkName: $status`n"
}

$reportContent += @"

## åç°çé®é¢?
### ä¸¥éé®é¢ (éè¦ç«å³ä¿®å¤?
"@

# æ¶éä¸¥éé®é¢
$criticalIssues = @()

# æ£æ¥ææ¡£ä¸è´æ§çç?foreach ($check in $checkResults.documentation_consistency.Keys) {
    if ($check -match "^verified_" -and $checkResults.documentation_consistency[$check] -eq $false) {
        $issueName = $check -replace "^verified_", "" -replace "_", " "
        $criticalIssues += "ææ¡£å£°æä¸ä»£ç å®ç°ä¸ä¸è? $issueName"
    }
}

# æ£æ¥å±é©ç»ä»?if ($checkResults.historical_cleanup["no_dangerous_components"] -eq $false) {
    $criticalIssues += "åç°å±é©ç»ä»¶ (child_process.exec, eval, ç­?"
}

# æ£æ¥æ¨¡ææ§è¡?if ($checkResults.simulation_detection["no_simulation"] -eq $false) {
    $criticalIssues += "åç°æ¨¡ææ§è¡å½æ°"
}

if ($criticalIssues.Count -gt 0) {
    foreach ($issue in $criticalIssues) {
        $reportContent += "- â?$issue`n"
    }
} else {
    $reportContent += "- â?æ ä¸¥éé®é¢`n"
}

$reportContent += @"

### è­¦åé®é¢ (å»ºè®®ä¿®å¤)
"@

# æ¶éè­¦åé®é¢
$warningIssues = @()

# æ£æ¥å¤ä»½æä»?if ($checkResults.historical_cleanup["no_backup_files"] -eq $false) {
    $warningIssues += "å­å¨å¤ä»½æä»¶"
}

# æ£æ¥å¤å®ç°è·¯å¾
if ($checkResults.architectural_consistency["single_implementation"] -eq $false) {
    $warningIssues += "å¤å®ç°è·¯å¾ï¼æ¶æä¸ä¸è?
}

# æ£æ¥åè£å¨
if ($checkResults.architectural_consistency["no_wrappers"] -eq $false) {
    $warningIssues += "å­å¨åè£å¨å±"
}

# æ£æ¥ç¦æ­¢æä»?if ($checkResults.basic_compliance["no_prohibited_files"] -eq $false) {
    $warningIssues += "å­å¨ç¦æ­¢æä»¶ (.ps1, .bat, .js ç­?"
}

if ($warningIssues.Count -gt 0) {
    foreach ($issue in $warningIssues) {
        $reportContent += "- â ï¸ $issue`n"
    }
} else {
    $reportContent += "- â?æ è­¦åé®é¢`n"
}

$reportContent += @"

## æ¹è¿å»ºè®®

### ç«å³è¡å¨
"@

if ($criticalIssues.Count -gt 0) {
    $reportContent += "1. **ç«å³ä¿®å¤ææä¸¥éé®é¢?*ï¼ç¹å«æ¯ææ¡£ä¸è´æ§çç¾`n"
    $reportContent += "2. **ç§»é¤ææå±é©ç»ä»?*ï¼ç¡®ä¿ä»£ç å®å¨`n"
    $reportContent += "3. **å é¤æ¨¡ææ§è¡å½æ°**ï¼ç¡®ä¿çå®è®¡ç®`n"
} else {
    $reportContent += "1. â?æ éè¦ç«å³è¡å¨çé®é¢`n"
}

$reportContent += @"

### å»ºè®®æ¹è¿
"@

if ($warningIssues.Count -gt 0) {
    $reportContent += "1. **æ¸çå¤ä»½æä»¶**ï¼ä¿æä»£ç æ´æ´`n"
    $reportContent += "2. **ç»ä¸å®ç°è·¯å¾**ï¼ç¡®ä¿æ¶æä¸è´`n"
    $reportContent += "3. **ç§»é¤åè£å¨å±**ï¼ç®åæ¶æ`n"
    $reportContent += "4. **å é¤ç¦æ­¢æä»¶**ï¼ç¬¦åClawHubè§è`n"
} else {
    $reportContent += "1. â?ä»£ç è´¨éè¯å¥½ï¼ç»§ç»­ä¿æ`n"
}

$reportContent += @"

### é¿æä¼å
1. **å®æè¿è¡æ­¤æ£æ¥å·¥å?*ï¼ç¡®ä¿æç»­åè§?2. **å»ºç«å£°æéªè¯ç©éµ**ï¼ç¡®ä¿ææ¡£ä»£ç ä¸è?3. **å®æ½æ¶æå®¡æ¥**ï¼ç¡®ä¿è®¾è®¡åç?4. **åå»ºèªå¨åæµè¯?*ï¼ç¡®ä¿åè½æ­£ç¡?
## åºäºAISkinXæ¡æ¶çéªè¯?
### åºç¨çåå?- â?**å·ä½ååå?*: å·ä½çæ£æ¥é¡¹åéªè¯æ¹æ³?- â?**å¯éªè¯åå?*: æææ£æ¥ç»æå¯éªè¯
- â?**èªå¨ååå?*: èªå¨åæ£æ¥å·¥å?- â?**ææ¡£ååå?*: è¯¦ç»çæ£æ¥æ¥å?
### æè®­åºç¨
åºäº2026-03-27 ClawHubæ«æå¤±è´¥æè®­ï¼æ­¤å·¥å·æ£æ¥äºï¼?1. ææ¡£å£°æä¸ä»£ç å®ç°çä¸è´æ?2. æ¶æè®¾è®¡çé»è¾ä¸è´æ?3. æ¨¡ææ§è¡çè¯å?4. åå²æä»¶çå½»åºæ¸ç?5. å¯¼å¥è¯­å¥çå£°æéªè¯?
## ä¸ä¸æ­?
### å¦æåæ° < 80%
1. ä»ç»éè¯»æ¥åä¸­çé®é¢
2. æç§æ¹è¿å»ºè®®è¿è¡ä¿®å¤
3. éæ°è¿è¡æ£æ¥å·¥å?4. ç¡®ä¿ææé®é¢è§£å³åååå¸?
### å¦æåæ° >= 80%
1. å®¡æ¥è­¦åé®é¢ï¼èèä¿®å¤
2. è¿è¡å¶ä»åè§æ£æ¥å·¥å?3. åå¤åå¸å°ClawHub
4. çæ§ClawHubæ«æç»æ

### æä½³å®è·?1. **å¼åé¶æ®?*: å®æè¿è¡æ­¤æ£æ?2. **åå¸å?*: å¿é¡»éè¿æææ£æ?3. **ç»´æ¤é¶æ®µ**: æ¯æ¬¡æ´æ°åéæ°æ£æ?4. **å®å¨å®¡è®¡**: æ¯å­£åº¦å¨é¢æ£æ¥ä¸æ¬?
---

**æ¥åçææ¶é´**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**å·¥å·çæ¬**: v1.0 (åºäºClawHubæè®­)  
**æ¡æ¶çæ¬**: AISkinXå¢å¼ºç?v2.0  
**åè§æ å**: ClawHubæ·±åº¦å®å¨æ£æ? 
**ç®æ åæ°**: >= 90% (å»ºè®®), >= 80% (æä½è¦æ±?
"@

Set-Content -Path $reportFile -Value $reportContent
Write-Host "`nè¯¦ç»æ¥åå·²ä¿å­å°: $reportFile" -ForegroundColor Cyan

# çæJSONæ ¼å¼ç»æ
$jsonFile = Join-Path $OutputDir "clawhub_compliance_results.json"
$checkResults | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFile
Write-Host "JSONç»æå·²ä¿å­å°: $jsonFile" -ForegroundColor Cyan

# æç»å»ºè®?Write-Host "`n=== æç»å»ºè®?===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "â?ä¼ç§! æè½ç¬¦åClawHubæ·±åº¦åè§è¦æ±" -ForegroundColor Green
    Write-Host "å»ºè®®: å¯ä»¥åå¤åå¸å°ClawHub" -ForegroundColor Green
} elseif ($score -ge 80) {
    Write-Host "â ï¸ è¯å¥½ï¼ä½ææ¹è¿ç©ºé? -ForegroundColor Yellow
    Write-Host "å»ºè®®: ä¿®å¤è­¦åé®é¢åååå¸" -ForegroundColor Yellow
} elseif ($score -ge 60) {
    Write-Host "â?éè¦æ¹è¿? -ForegroundColor Red
    Write-Host "å»ºè®®: å¿é¡»ä¿®å¤ä¸¥éé®é¢åååå¸" -ForegroundColor Red
} else {
    Write-Host "ð« ä¸ç¬¦åè¦æ±? -ForegroundColor DarkRed
    Write-Host "å»ºè®®: éè¦å¨é¢éæï¼ä¸å»ºè®®åå¸? -ForegroundColor DarkRed
}

Write-Host "`næ£æ¥å®æãè¯·æ¥çè¯¦ç»æ¥åè·åå·ä½æ¹è¿å»ºè®®ã? -ForegroundColor White
