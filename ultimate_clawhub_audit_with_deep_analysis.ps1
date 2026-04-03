# ultimate_clawhub_audit_with_deep_analysis.ps1
# 终极ClawHub审核工具 - 集成深度分析
# 版本: v2.0 (包含5个深度分析工具)

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\ultimate_audit_deep",
    [switch]$StrictMode = $true,
    [switch]$AutoFix = $false,
    [switch]$DeepAnalysis = $true
)

Write-Host "=== Ultimate ClawHub Audit with Deep Analysis ===" -ForegroundColor Cyan
Write-Host "Version: 2.0 (Integrated 5 Deep Analysis Tools)" -ForegroundColor Cyan
Write-Host "Goal: Ensure skill 100% passes ClawHub scan with deep code analysis" -ForegroundColor Cyan
Write-Host "Mode: $(if ($StrictMode) { 'Strict Mode' } else { 'Standard Mode' })" -ForegroundColor Cyan
Write-Host "Deep Analysis: $(if ($DeepAnalysis) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host "Auto Fix: $(if ($AutoFix) { 'Enabled' } else { 'Disabled' })" -ForegroundColor Cyan
Write-Host "Audit Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# 检查目录是否存在
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] Skill directory does not exist: $SkillDir" -ForegroundColor Red
    exit 1
}

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化审核结果
$auditResults = @{
    "metadata" = @{
        "skill_dir" = $SkillDir
        "audit_time" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "version" = "2.0"
        "strict_mode" = $StrictMode
        "deep_analysis" = $DeepAnalysis
    }
    "categories" = @{}
    "deep_analysis" = @{
        "enabled" = $DeepAnalysis
        "tools" = @()
        "results" = @()
    }
    "overall_score" = 0
    "critical_issues" = @()
    "warning_issues" = @()
    "recommendation" = ""
    "clawhub_ready" = $false
}

# 添加检查结果函数
function Add-CheckResult {
    param(
        [string]$Category,
        [string]$CheckName,
        [bool]$Passed,
        [string]$Message,
        [string]$FixSuggestion = "",
        [bool]$Critical = $false
    )
    
    if (-not $auditResults.categories.ContainsKey($Category)) {
        $auditResults.categories[$Category] = @{
            "total" = 0
            "passed" = 0
            "failed" = 0
            "checks" = @()
        }
    }
    
    $checkResult = @{
        "name" = $CheckName
        "passed" = $Passed
        "message" = $Message
        "fix_suggestion" = $FixSuggestion
        "critical" = $Critical
    }
    
    $auditResults.categories[$Category].total++
    $auditResults.categories[$Category].checks += $checkResult
    
    if ($Passed) {
        $auditResults.categories[$Category].passed++
        Write-Host "  [PASS] $CheckName" -ForegroundColor Green
    } else {
        $auditResults.categories[$Category].failed++
        if ($Critical) {
            Write-Host "  [FAIL] $CheckName (Critical)" -ForegroundColor Red
            $auditResults.critical_issues += "$Category: $Message"
        } else {
            Write-Host "  [WARN] $CheckName" -ForegroundColor Yellow
            $auditResults.warning_issues += "$Category: $Message"
        }
        
        if ($FixSuggestion) {
            Write-Host "    Fix: $FixSuggestion" -ForegroundColor Cyan
        }
    }
}

# ============================================
# 1. 基础文件结构检查
# ============================================
Write-Host "## 1. Basic File Structure Check" -ForegroundColor Yellow

$requiredFiles = @(
    "SKILL.md",
    "README.md", 
    "CHANGELOG.md",
    "config.yaml",
    "package.json",
    "skill.py"
)

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    $exists = Test-Path $filePath
    
    Add-CheckResult -Category "file_structure" -CheckName "File: $file" `
        -Passed $exists -Message "File $file $(if($exists){'exists'}else{'does not exist'})" `
        -FixSuggestion "Add $file to the skill directory" `
        -Critical $true
}

# ============================================
# 2. 版本一致性检查
# ============================================
Write-Host "`n## 2. Version Consistency Check" -ForegroundColor Yellow

$versions = @()

# 检查config.yaml版本
$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match 'version:\s*["'']?([0-9]+\.[0-9]+\.[0-9]+)["'']?') {
        $versions += @{ "File" = "config.yaml"; "Version" = $matches[1] }
    }
}

# 检查package.json版本
$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    $packageContent = Get-Content $packagePath -Raw
    if ($packageContent -match '"version"\s*:\s*["'']([0-9]+\.[0-9]+\.[0-9]+)["'']') {
        $versions += @{ "File" = "package.json"; "Version" = $matches[1] }
    }
}

# 检查SKILL.md版本
$skillPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    if ($skillContent -match 'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)') {
        $versions += @{ "File" = "SKILL.md"; "Version" = $matches[1] }
    }
}

if ($versions.Count -ge 2) {
    $firstVersion = $versions[0].Version
    $allSame = $true
    foreach ($v in $versions) {
        if ($v.Version -ne $firstVersion) {
            $allSame = $false
            break
        }
    }
    
    $versionMessage = "Versions: $($versions | ForEach-Object { "$($_.File)=$($_.Version)" } -join ', ')"
    Add-CheckResult -Category "version_consistency" -CheckName "Version consistency" `
        -Passed $allSame -Message $versionMessage `
        -FixSuggestion "Make all version numbers consistent" `
        -Critical $true
} else {
    Add-CheckResult -Category "version_consistency" -CheckName "Version consistency" `
        -Passed $false -Message "Could not extract versions from files" `
        -FixSuggestion "Add version fields to config.yaml, package.json, and SKILL.md" `
        -Critical $true
}

# ============================================
# 3. 安全合规检查
# ============================================
Write-Host "`n## 3. Security Compliance Check" -ForegroundColor Yellow

# 检查config.yaml安全声明
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    
    $hasSecuritySection = $configContent -match 'security:'
    Add-CheckResult -Category "security" -CheckName "config.yaml security section" `
        -Passed $hasSecuritySection -Message "Security section $(if($hasSecuritySection){'found'}else{'not found'})" `
        -FixSuggestion "Add security section to config.yaml" `
        -Critical $true
    
    $hasNetworkAccessFalse = $configContent -match 'network_access:\s*false'
    Add-CheckResult -Category "security" -CheckName "config.yaml network_access: false" `
        -Passed $hasNetworkAccessFalse -Message "network_access: false $(if($hasNetworkAccessFalse){'found'}else{'not found'})" `
        -FixSuggestion "Set network_access: false in config.yaml" `
        -Critical $true
    
    $hasLocalOnlyTrue = $configContent -match 'local_only:\s*true'
    Add-CheckResult -Category "security" -CheckName "config.yaml local_only: true" `
        -Passed $hasLocalOnlyTrue -Message "local_only: true $(if($hasLocalOnlyTrue){'found'}else{'not found'})" `
        -FixSuggestion "Set local_only: true in config.yaml" `
        -Critical $true
}

# ============================================
# 4. 文档质量检查
# ============================================
Write-Host "`n## 4. Documentation Quality Check" -ForegroundColor Yellow

# 检查SKILL.md完整性
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    
    $requiredSections = @(
        "# Skill Name",
        "## Description", 
        "## Commands",
        "## Installation",
        "## Configuration"
    )
    
    foreach ($section in $requiredSections) {
        $hasSection = $skillContent -match [regex]::Escape($section)
        Add-CheckResult -Category "documentation" -CheckName "SKILL.md section: $section" `
            -Passed $hasSection -Message "Section $section $(if($hasSection){'found'}else{'not found'})" `
            -FixSuggestion "Add $section section to SKILL.md" `
            -Critical $false
    }
}

# ============================================
# 5. 元数据验证
# ============================================
Write-Host "`n## 5. Metadata Validation" -ForegroundColor Yellow

if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath | ConvertFrom-Json
        
        $hasName = -not [string]::IsNullOrEmpty($packageJson.name)
        $hasDescription = -not [string]::IsNullOrEmpty($packageJson.description)
        $hasAuthor = -not [string]::IsNullOrEmpty($packageJson.author)
        $hasLicense = -not [string]::IsNullOrEmpty($packageJson.license)
        
        Add-CheckResult -Category "metadata" -CheckName "Package name" `
            -Passed $hasName -Message "Package name: $(if($hasName){'found'}else{'not found'})" `
            -FixSuggestion "Add name field to package.json" `
            -Critical $true
        
        Add-CheckResult -Category "metadata" -CheckName "Package description" `
            -Passed $hasDescription -Message "Package description: $(if($hasDescription){'found'}else{'not found'})" `
            -FixSuggestion "Add description field to package.json" `
            -Critical $true
        
        Add-CheckResult -Category "metadata" -CheckName "Package author" `
            -Passed $hasAuthor -Message "Package author: $(if($hasAuthor){'found'}else{'not found'})" `
            -FixSuggestion "Add author field to package.json" `
            -Critical $true
        
        Add-CheckResult -Category "metadata" -CheckName "Package license" `
            -Passed $hasLicense -Message "Package license: $(if($hasLicense){'found'}else{'not found'})" `
            -FixSuggestion "Add license field to package.json" `
            -Critical $true
        
    } catch {
        Add-CheckResult -Category "metadata" -CheckName "Package.json parse" `
            -Passed $false -Message "Failed to parse package.json: $_" `
            -FixSuggestion "Fix package.json format" `
            -Critical $true
    }
}

# ============================================
# 6. 链接验证
# ============================================
Write-Host "`n## 6. Link Validation" -ForegroundColor Yellow

if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath | ConvertFrom-Json
        
        if ($packageJson.author -and $packageJson.author.url) {
            $githubUrl = $packageJson.author.url
            $isValidGithubUrl = $githubUrl -match '^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$'
            
            Add-CheckResult -Category "links" -CheckName "GitHub URL format" `
                -Passed $isValidGithubUrl -Message "GitHub URL: $githubUrl" `
                -FixSuggestion "Use valid GitHub URL format: https://github.com/username/repository" `
                -Critical $true
        } else {
            Add-CheckResult -Category "links" -CheckName "GitHub URL" `
                -Passed $false -Message "No GitHub URL found" `
                -FixSuggestion "Add author.url field with GitHub URL" `
                -Critical $true
        }
        
    } catch {
        Add-CheckResult -Category "links" -CheckName "Link validation" `
            -Passed $false -Message "Failed to validate links: $_" `
            -FixSuggestion "Fix package.json format" `
            -Critical $true
    }
}

# ============================================
# 7. 代码质量检查
# ============================================
Write-Host "`n## 7. Code Quality Check" -ForegroundColor Yellow

$skillPyPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPyPath) {
    # 检查Python语法
    try {
        python -m py_compile $skillPyPath 2>&1 | Out-Null
        Add-CheckResult -Category "code_quality" -CheckName "Python syntax" `
            -Passed $true -Message "Python syntax is valid" `
            -FixSuggestion "" -Critical $true
    } catch {
        Add-CheckResult -Category "code_quality" -CheckName "Python syntax" `
            -Passed $false -Message "Python syntax error: $_" `
            -FixSuggestion "Fix Python syntax errors" `
            -Critical $true
    }
    
    # 检查危险导入
    $skillContent = Get-Content $skillPyPath -Raw
    $dangerousImports = @('subprocess', 'os.system', 'eval', 'exec', '__import__')
    
    foreach ($import in $dangerousImports) {
        $hasDangerousImport = $skillContent -match "import.*$import|from.*$import"
        if ($hasDangerousImport) {
            Add-CheckResult -Category "code_quality" -CheckName "Dangerous import: $import" `
                -Passed $false -Message "Found dangerous import: $import" `
                -FixSuggestion "Remove or secure usage of $import" `
                -Critical $true
        }
    }
}

# ============================================
# 8. 依赖验证
# ============================================
Write-Host "`n## 8. Dependency Validation" -ForegroundColor Yellow

$requirementsPath = Join-Path $SkillDir "requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath
    $hasRequirements = $requirementsContent.Count -gt 0
    
    Add-CheckResult -Category "dependencies" -CheckName "Requirements.txt" `
        -Passed $hasRequirements -Message "Requirements.txt $(if($hasRequirements){'has content'}else{'is empty'})" `
        -FixSuggestion "Add dependencies to requirements.txt" `
        -Critical $false
} else {
    Add-CheckResult -Category "dependencies" -CheckName "Requirements.txt" `
        -Passed $false -Message "Requirements.txt not found" `
        -FixSuggestion "Create requirements.txt file" `
        -Critical $false
}

# ============================================
# 9. 许可证合规
# ============================================
Write-Host "`n## 9. License Compliance" -ForegroundColor Yellow

$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "^LICENSE|^LICENCE|^license|^licence"
}

Add-CheckResult -Category "license" -CheckName "License file exists" `
    -Passed ($licenseFiles.Count -gt 0) -Message "License file: $(if($licenseFiles.Count -gt 0){'found'}else{'not found'})" `
    -FixSuggestion "Add LICENSE.txt or LICENSE.md file" `
    -Critical $true

if ($licenseFiles.Count -gt 0) {
    $licenseFile = $licenseFiles[0]
    $hasValidExtension = $licenseFile.Extension -in @(".txt", ".md")
    
    Add-CheckResult -Category "license" -CheckName "License file extension" `
        -Passed $hasValidExtension -Message "License file extension: $($licenseFile.Extension)" `
        -FixSuggestion "Use .txt or .md extension for license file" `
        -Critical $false
}

# ============================================
# 10. 文本文件格式检查
# ============================================
Write-Host "`n## 10. Text File Format Check" -ForegroundColor Yellow

# 检查所有文件扩展名
$allFiles = Get-ChildItem -Path $SkillDir -File -Recurse
$filesWithoutExtension = $allFiles | Where-Object { $_.Extension -eq "" }

Add-CheckResult -Category "file_format" -CheckName "Files without extension" `
    -Passed ($filesWithoutExtension.Count -eq 0) -Message "Files without extension: $($filesWithoutExtension.Count)" `
    -FixSuggestion "Add proper extensions to all files" `
    -Critical $false

# 检查许可证文件格式
if ($licenseFiles.Count -gt 0) {
    $licenseFile = $licenseFiles[0]
    $isTextFile = $licenseFile.Extension -in @(".txt", ".md")
    
    Add-CheckResult -Category "file_format" -CheckName "License file is text file" `
        -Passed $isTextFile -Message "License file: $($licenseFile.Name)" `
        -FixSuggestion "Use LICENSE.txt or LICENSE.md (not LICENSE without extension)" `
        -Critical $true
}

# ============================================
# 11. 深度代码分析 (如果启用)
# ============================================
if ($DeepAnalysis) {
    Write-Host "`n## 11. Deep Code Analysis" -ForegroundColor Magenta
    Write-Host "Running 5 deep analysis tools..." -ForegroundColor Magenta
    
    # 检查Python环境
    $pythonAvailable = $false
    try {
        python --version 2>&1 | Out-Null
        $pythonAvailable = $true
    } catch {
        $pythonAvailable = $false
    }
    
    if (-not $pythonAvailable) {
        Write-Host "  [WARN] Python not available, skipping deep analysis" -ForegroundColor Yellow
        $auditResults.deep_analysis.enabled = $false
    } else {
        # 运行深度分析套件
        $deepAnalysisScript = Join-Path $PSScriptRoot "deep_analysis_suite.py"
        if (Test-Path $deepAnalysisScript) {
            Write-Host "  Running deep analysis suite..." -ForegroundColor Cyan
            
            try {
                # 运行深度分析
                $requirementsPath = Join-Path $SkillDir "requirements.txt"
                $requirementsArg = ""
                if (Test-Path $requirementsPath) {
                    $requirementsArg = "-r `"$requirementsPath`""
                }
                
                $pythonCommand = "python `"$deepAnalysisScript`" `"$SkillDir`" $requirementsArg"
                $deepResult = Invoke-Expression $pythonCommand 2>&1
                
                # 解析结果
                $deepReportFile = Get-ChildItem -Path . -Filter "deep_analysis_report_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
                
                if ($deepReportFile -and (Test-Path $deepReportFile.FullName)) {
                    $deepReport = Get-Content $deepReportFile.FullName | ConvertFrom-Json
                    
                    # 添加深度分析结果
                    $auditResults.deep_analysis.results = $deepReport
                    
                    # 根据深度分析结果添加检查
                    if ($deepReport.stats.total_issues -gt 0) {
                        Add-CheckResult -Category "deep_analysis" -CheckName "Deep analysis issues" `
                            -Passed $false -Message "Found $($deepReport.stats.total_issues) deep analysis issues (H:$($deepReport.stats.high_issues)/M:$($deepReport.stats.medium_issues)/L:$($deepReport.stats.low_issues))" `
                            -FixSuggestion "Review deep analysis report for details" `
                            -Critical ($deepReport.stats.high_issues -gt 0)
                        
                        # 添加工具详情
                        foreach ($tool in @("ast", "control_flow", "third_party", "data_flow", "performance")) {
                            if ($deepReport.tool_reports.$tool -and $deepReport.tool_reports.$tool.stats) {
                                $toolStats = $deepReport.tool_reports.$tool.stats
                                if ($toolStats.total -gt 0) {
                                    Add-CheckResult -Category "deep_analysis" -CheckName "$tool analysis" `
                                        -Passed $false -Message "$tool: $($toolStats.total) issues" `
                                        -FixSuggestion "" -Critical $false
                                }
                            }
                        }
                    } else {
                        Add-CheckResult -Category "deep_analysis" -CheckName "Deep analysis" `
                            -Passed $true -Message "No deep analysis issues found" `
                            -FixSuggestion "" -Critical $false
                    }
                    
                    Write-Host "  [OK] Deep analysis completed" -ForegroundColor Green
                } else {
                    Write-Host "  [WARN] Deep analysis report not found" -ForegroundColor Yellow
                }
                
            } catch {
                Write-Host "  [ERROR] Deep analysis failed: $_" -ForegroundColor Red
                Add-CheckResult -Category "deep_analysis" -CheckName "Deep analysis execution" `
                    -Passed $false -Message "Deep analysis failed: $_" `
                    -FixSuggestion "Check Python environment and analysis tools" `
                    -Critical $false
            }
        } else {
            Write-Host "  [WARN] Deep analysis suite not found at: $deepAnalysisScript" -ForegroundColor Yellow
            $auditResults.deep_analysis.enabled = $false
        }
    }
}

# ============================================
# 计算总体分数
# ============================================
Write-Host "`n## Calculating Overall Score" -ForegroundColor Cyan

$totalChecks = 0
$passedChecks = 0
$criticalFailed = 0

foreach ($category in $auditResults.categories.Keys) {
    $categoryData = $auditResults.categories[$category]
    $totalChecks += $categoryData.total
    $passedChecks += $categoryData.passed
    
    # 统计关键失败
    foreach ($check in $categoryData.checks) {
        if (-not $check.passed -and $check.critical) {
            $criticalFailed++
        }
    }
}

if ($totalChecks -gt 0) {
    $overallScore = [math]::Round(($passedChecks / $totalChecks) * 100)
} else {
    $overallScore = 0
}

$auditResults.overall_score = $overallScore

# 确定ClawHub就绪状态
$clawhubReady = ($overallScore -ge 95) -and ($criticalFailed -eq 0)
$auditResults.clawhub_ready = $clawhubReady

# 生成建议
if ($clawhubReady) {
    $auditResults.recommendation = "Ready for ClawHub submission! Expected result: Clean (high confidence)"
} elseif ($overallScore -ge 80 -and $criticalFailed -eq 0) {
    $auditResults.recommendation = "Almost ready. Fix warnings before submission."
} else {
    $auditResults.recommendation = "Not ready. Fix critical issues first."
}

# ============================================
# 生成最终报告
# ============================================
Write-Host "`n=== Final Audit Report ===" -ForegroundColor Cyan
Write-Host "Overall Score: $overallScore%" -ForegroundColor White
Write-Host "Total Checks: $totalChecks" -ForegroundColor White
Write-Host "Passed Checks: $passedChecks" -ForegroundColor Green
Write-Host "Failed Checks: $($totalChecks - $passedChecks)" -ForegroundColor $(if (($totalChecks - $passedChecks) -eq 0) { "Green" } else { "Red" })
Write-Host "Critical Issues: $criticalFailed" -ForegroundColor $(if ($criticalFailed -eq 0) { "Green" } else { "Red" })
Write-Host "ClawHub Ready: $(if ($clawhubReady) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($clawhubReady) { "Green" } else { "Red" })
Write-Host "Recommendation: $($auditResults.recommendation)" -ForegroundColor Cyan

# 显示类别详情
Write-Host "`nCategory Details:" -ForegroundColor Cyan
foreach ($category in ($auditResults.categories.Keys | Sort-Object)) {
    $categoryData = $auditResults.categories[$category]
    $categoryScore = if ($categoryData.total -gt 0) { [math]::Round(($categoryData.passed / $categoryData.total) * 100) } else { 0 }
    $color = if ($categoryScore -ge 90) { "Green" } elseif ($categoryScore -ge 70) { "Yellow" } else { "Red" }
    
    Write-Host "  $category : $categoryScore% ($($categoryData.passed)/$($categoryData.total))" -ForegroundColor $color
}

# 显示关键问题
if ($auditResults.critical_issues.Count -gt 0) {
    Write-Host "`nCritical Issues:" -ForegroundColor Red
    foreach ($issue in $auditResults.critical_issues) {
        Write-Host "  • $issue" -ForegroundColor Red
    }
}

# 显示警告
if ($auditResults.warning_issues.Count -gt 0) {
    Write-Host "`nWarnings:" -ForegroundColor Yellow
    foreach ($warning in $auditResults.warning_issues) {
        Write-Host "  • $warning" -ForegroundColor Yellow
    }
}

# 深度分析摘要
if ($DeepAnalysis -and $auditResults.deep_analysis.enabled -and $auditResults.deep_analysis.results) {
    $deepReport = $auditResults.deep_analysis.results
    Write-Host "`nDeep Analysis Summary:" -ForegroundColor Magenta
    Write-Host "  Quality Score: $($deepReport.quality_assessment.score)/100 ($($deepReport.quality_assessment.level))" -ForegroundColor Magenta
    Write-Host "  Total Issues: $($deepReport.stats.total_issues)" -ForegroundColor Magenta
    Write-Host "  Recommendation: $($deepReport.quality_assessment.recommendation)" -ForegroundColor Magenta
}

# 保存报告
$reportFile = Join-Path $OutputDir "audit_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$auditResults | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8

Write-Host "`nAudit report saved to: $reportFile" -ForegroundColor Green
Write-Host "`n=== Audit Complete ===" -ForegroundColor Cyan

# 返回退出码
if ($clawhubReady) {
    exit 0
} else {
    exit 1
}