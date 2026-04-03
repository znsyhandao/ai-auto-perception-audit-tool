# audit_documentation.ps1
# 文档一致性维度专项检查工具
# 检查安全声明一致性、功能声明一致性、限制声明一致性

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\documentation_audit",
    [switch]$Verbose = $false
)

Write-Host "=== 文档一致性审核 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "技能目录: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化检查结果
$checkResults = @{
    "security_declarations" = @{}
    "function_declarations" = @{}
    "limitation_declarations" = @{}
    "overall_score" = 0
}

# 辅助函数
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
        $checkResults[$Category][$checkName] = @{
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
# 1. 安全声明一致性检查
# ============================================
Write-Host "## 1. 安全声明一致性检查" -ForegroundColor Yellow

# 1.1 检查SKILL.md中的安全声明
$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    $hasSecuritySection = $skillMdContent -match "安全声明|安全特性|Security"
    $hasNoNetworkClaim = $skillMdContent -match "无网络|no network|local only"
    $hasNoShellClaim = $skillMdContent -match "无shell|no shell|no subprocess"
    $hasRealComputation = $skillMdContent -match "真实计算|real computation|绝不模拟"
    
    Add-Check -Category "security_declarations" -CheckName "SKILL.md有安全声明" `
        -Passed $hasSecuritySection `
        -Message "安全声明章节: $(if($hasSecuritySection){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加安全声明章节" `
        -Critical $true
    
    Add-Check -Category "security_declarations" -CheckName "声明无网络访问" `
        -Passed $hasNoNetworkClaim `
        -Message "无网络声明: $(if($hasNoNetworkClaim){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中声明无网络访问" `
        -Critical $true
    
    Add-Check -Category "security_declarations" -CheckName "声明无shell命令" `
        -Passed $hasNoShellClaim `
        -Message "无shell声明: $(if($hasNoShellClaim){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中声明无shell命令执行" `
        -Critical $true
    
    Add-Check -Category "security_declarations" -CheckName "声明真实计算" `
        -Passed $hasRealComputation `
        -Message "真实计算声明: $(if($hasRealComputation){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中声明所有功能都是真实计算" `
        -Critical $true
}

# 1.2 检查README.md中的安全声明
$readmePath = Join-Path $SkillDir "README.md"
if (Test-Path $readmePath) {
    $readmeContent = Get-Content $readmePath -Raw
    $hasSecurityMention = $readmeContent -match "安全|security|safe"
    
    Add-Check -Category "security_declarations" -CheckName "README.md提及安全" `
        -Passed $hasSecurityMention `
        -Message "安全提及: $(if($hasSecurityMention){'有'}else{'无'})" `
        -FixSuggestion "在README.md中提及安全特性" `
        -Critical $false
}

# ============================================
# 2. 功能声明一致性检查
# ============================================
Write-Host "`n## 2. 功能声明一致性检查" -ForegroundColor Yellow

# 2.1 检查SKILL.md中的功能描述
if (Test-Path $skillMdPath) {
    $hasCommandsSection = $skillMdContent -match "命令|Commands|功能|Features"
    $hasUsageExamples = $skillMdContent -match "用法|Usage|示例|Examples"
    $hasParameters = $skillMdContent -match "参数|Parameters|选项|Options"
    
    Add-Check -Category "function_declarations" -CheckName "SKILL.md有命令说明" `
        -Passed $hasCommandsSection `
        -Message "命令说明: $(if($hasCommandsSection){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加命令说明章节" `
        -Critical $true
    
    Add-Check -Category "function_declarations" -CheckName "SKILL.md有用法示例" `
        -Passed $hasUsageExamples `
        -Message "用法示例: $(if($hasUsageExamples){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加用法示例" `
        -Critical $true
    
    Add-Check -Category "function_declarations" -CheckName "SKILL.md有参数说明" `
        -Passed $hasParameters `
        -Message "参数说明: $(if($hasParameters){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加参数说明" `
        -Critical $false
}

# 2.2 检查README.md中的功能描述
if (Test-Path $readmePath) {
    $hasQuickStart = $readmeContent -match "快速开始|Quick Start|Getting Started"
    $hasFeaturesList = $readmeContent -match "特性|Features|功能"
    
    Add-Check -Category "function_declarations" -CheckName "README.md有快速开始" `
        -Passed $hasQuickStart `
        -Message "快速开始: $(if($hasQuickStart){'有'}else{'无'})" `
        -FixSuggestion "在README.md中添加快速开始章节" `
        -Critical $false
    
    Add-Check -Category "function_declarations" -CheckName "README.md有特性列表" `
        -Passed $hasFeaturesList `
        -Message "特性列表: $(if($hasFeaturesList){'有'}else{'无'})" `
        -FixSuggestion "在README.md中添加特性列表" `
        -Critical $false
}

# ============================================
# 3. 限制声明一致性检查
# ============================================
Write-Host "`n## 3. 限制声明一致性检查" -ForegroundColor Yellow

# 3.1 检查环境要求说明
if (Test-Path $skillMdPath) {
    $hasRequirements = $skillMdContent -match "环境要求|Requirements|Prerequisites"
    $hasPythonVersion = $skillMdContent -match "Python.*\d+\.\d+" -or $skillMdContent -match "python.*\d+"
    $hasDependencies = $skillMdContent -match "依赖|Dependencies|需要安装"
    
    Add-Check -Category "limitation_declarations" -CheckName "SKILL.md有环境要求" `
        -Passed $hasRequirements `
        -Message "环境要求: $(if($hasRequirements){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加环境要求章节" `
        -Critical $false
    
    Add-Check -Category "limitation_declarations" -CheckName "SKILL.md有Python版本要求" `
        -Passed $hasPythonVersion `
        -Message "Python版本: $(if($hasPythonVersion){'有'}else{'无'})" `
        -FixSuggestion "明确说明所需的Python版本" `
        -Critical $false
    
    Add-Check -Category "limitation_declarations" -CheckName "SKILL.md有依赖说明" `
        -Passed $hasDependencies `
        -Message "依赖说明: $(if($hasDependencies){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加依赖说明" `
        -Critical $false
}

# 3.2 检查限制和注意事项
if (Test-Path $skillMdPath) {
    $hasLimitations = $skillMdContent -match "限制|Limitations|注意事项|Notes"
    $hasKnownIssues = $skillMdContent -match "已知问题|Known Issues|问题|Issues"
    
    Add-Check -Category "limitation_declarations" -CheckName "SKILL.md有限制说明" `
        -Passed $hasLimitations `
        -Message "限制说明: $(if($hasLimitations){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加限制说明" `
        -Critical $false
    
    Add-Check -Category "limitation_declarations" -CheckName "SKILL.md有已知问题" `
        -Passed $hasKnownIssues `
        -Message "已知问题: $(if($hasKnownIssues){'有'}else{'无'})" `
        -FixSuggestion "在SKILL.md中添加已知问题" `
        -Critical $false
}

# ============================================
# 计算分数和生成报告
# ============================================

# 计算分数
$totalChecks = 0
$passedChecks = 0
$criticalIssues = @()
$warningIssues = @()

foreach ($category in $checkResults.Keys) {
    if ($category -ne "overall_score") {
        foreach ($checkName in $checkResults[$category].Keys) {
            $totalChecks++
            $check = $checkResults[$category][$checkName]
            
            if ($check.passed) {
                $passedChecks++
            } else {
                if ($check.critical) {
                    $criticalIssues += "$category: $checkName - $($check.message)"
                } else {
                    $warningIssues += "$category: $checkName - $($check.message)"
                }
            }
        }
    }
}

if ($totalChecks -gt 0) {
    $score = [math]::Round(($passedChecks / $totalChecks) * 100, 2)
    $checkResults.overall_score = $score
}

# 生成报告
Write-Host "`n=== 文档一致性审核完成 ===" -ForegroundColor Cyan
Write-Host "总体分数: $score%" -ForegroundColor Cyan
Write-Host "检查项: $passedChecks/$totalChecks 通过" -ForegroundColor Cyan
Write-Host "严重问题: $($criticalIssues.Count) 个" -ForegroundColor $($criticalIssues.Count -eq 0 ? "Green" : "Red")
Write-Host "警告问题: $($warningIssues.Count) 个" -ForegroundColor $($warningIssues.Count -eq 0 ? "Green" : "Yellow")

# 生成JSON报告
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
    "critical_issues" = $criticalIssues
    "warning_issues" = $warningIssues
}

foreach ($category in @("security_declarations", "function_declarations", "limitation_declarations")) {
    $categoryChecks = $checkResults[$category]
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $jsonReport.category_scores[$category] = $categoryScore
    }
}

$jsonFilePath = Join-Path $OutputDir "documentation_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`n详细JSON报告已保存到: $jsonFilePath" -ForegroundColor Cyan

# 最终建议
Write-Host "`n=== 最终建议 ===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "✅ 优秀! 文档一致性符合ClawHub标准" -ForegroundColor Green
    Write-Host "建议: 可以继续其他维度的审核" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "⚠️ 良好，但有改进空间" -ForegroundColor Yellow
    Write-Host "建议: 修复警告问题，提高分数到90%以上" -ForegroundColor Yellow
} else {
    Write-Host "❌ 需要改进" -ForegroundColor Red
    Write-Host "建议: 必须修复严重问题后再发布" -ForegroundColor Red
}

Write-Host "`n审核完成。请查看详细报告获取具体改进建议。" -ForegroundColor White