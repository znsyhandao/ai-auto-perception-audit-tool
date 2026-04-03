# audit_architecture.ps1
# 架构合理性维度专项检查工具
# 检查实现路径合理性、组件逻辑一致性、历史清理彻底性

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\architecture_audit",
    [switch]$Verbose = $false
)

Write-Host "=== 架构合理性审核 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "技能目录: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化检查结果
$checkResults = @{
    "implementation_path" = @{}
    "component_consistency" = @{}
    "historical_cleanup" = @{}
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
# 1. 实现路径合理性检查
# ============================================
Write-Host "## 1. 实现路径合理性检查" -ForegroundColor Yellow

# 1.1 检查语言类型
$pythonFiles = Get-ChildItem -Path $SkillDir -Filter "*.py" -File
$jsFiles = Get-ChildItem -Path $SkillDir -Filter "*.js" -File
$otherFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Extension -notin @(".py", ".md", ".yaml", ".yml", ".json", ".txt")
}

$implementationPaths = @()
if ($pythonFiles.Count -gt 0) { $implementationPaths += "Python" }
if ($jsFiles.Count -gt 0) { $implementationPaths += "JavaScript" }
if ($otherFiles.Count -gt 0) { $implementationPaths += "其他($($otherFiles.Count))" }

if ($implementationPaths.Count -eq 1) {
    Add-Check -Category "implementation_path" -CheckName "单一实现路径" `
        -Passed $true `
        -Message "单一实现路径: $($implementationPaths[0])" `
        -FixSuggestion "" `
        -Critical $false
} else {
    Add-Check -Category "implementation_path" -CheckName "单一实现路径" `
        -Passed $false `
        -Message "多实现路径: $($implementationPaths -join ', ')" `
        -FixSuggestion "统一实现路径，避免多语言混合" `
        -Critical $false
}

# 1.2 检查包装器层
$wrapperFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "wrapper|adapter|bridge|proxy|shim"
}

Add-Check -Category "implementation_path" -CheckName "无包装器层" `
    -Passed ($wrapperFiles.Count -eq 0) `
    -Message "包装器文件: $($wrapperFiles.Count) 个" `
    -FixSuggestion "移除不必要的包装器层" `
    -Critical $false

# 1.3 检查执行路径清晰性
$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $hasMainFunction = $skillContent -match "def main\(|if __name__ == '__main__'"
    $hasClearEntry = $skillContent -match "class.*Skill|def handle_"
    
    Add-Check -Category "implementation_path" -CheckName "有清晰入口点" `
        -Passed ($hasMainFunction -or $hasClearEntry) `
        -Message "入口点: $(if($hasMainFunction -or $hasClearEntry){'清晰'}else{'不清晰'})" `
        -FixSuggestion "添加清晰的入口点函数" `
        -Critical $false
}

# ============================================
# 2. 组件逻辑一致性检查
# ============================================
Write-Host "`n## 2. 组件逻辑一致性检查" -ForegroundColor Yellow

# 2.1 检查错误处理一致性
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $hasTryCatch = $skillContent -match "try.*:|except.*:"
    $hasErrorHandling = $skillContent -match "错误处理|error handling"
    
    Add-Check -Category "component_consistency" -CheckName "有错误处理机制" `
        -Passed $hasTryCatch `
        -Message "错误处理: $(if($hasTryCatch){'有'}else{'无'})" `
        -FixSuggestion "添加统一的错误处理机制" `
        -Critical $false
}

# 2.2 检查日志记录一致性
if (Test-Path $skillPath) {
    $hasLogging = $skillContent -match "import logging|import loguru|logger\."
    $hasLogLevels = $skillContent -match "DEBUG|INFO|WARNING|ERROR|CRITICAL"
    
    Add-Check -Category "component_consistency" -CheckName "有日志记录" `
        -Passed $hasLogging `
        -Message "日志记录: $(if($hasLogging){'有'}else{'无'})" `
        -FixSuggestion "添加统一的日志记录机制" `
        -Critical $false
}

# 2.3 检查配置管理一致性
$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath -and Test-Path $skillPath) {
    $hasConfigLoading = $skillContent -match "config\.yaml|load.*config|read.*config"
    
    Add-Check -Category "component_consistency" -CheckName "有配置管理" `
        -Passed $hasConfigLoading `
        -Message "配置管理: $(if($hasConfigLoading){'有'}else{'无'})" `
        -FixSuggestion "添加统一的配置管理机制" `
        -Critical $false
}

# ============================================
# 3. 历史清理彻底性检查
# ============================================
Write-Host "`n## 3. 历史清理彻底性检查" -ForegroundColor Yellow

# 3.1 检查备份文件
$backupFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $_.Name -match "\.backup$|\.old$|_backup|_old|备份"
}

Add-Check -Category "historical_cleanup" -CheckName "无备份文件" `
    -Passed ($backupFiles.Count -eq 0) `
    -Message "备份文件: $($backupFiles.Count) 个" `
    -FixSuggestion "移除所有备份文件" `
    -Critical $false

# 3.2 检查测试文件
$testFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $_.Name -match "^test_|_test\.|\.test\." -and $_.Extension -match "\.py|\.js"
}

Add-Check -Category "historical_cleanup" -CheckName "无测试文件混入" `
    -Passed ($testFiles.Count -eq 0) `
    -Message "测试文件: $($testFiles.Count) 个" `
    -FixSuggestion "移除测试文件或移动到测试目录" `
    -Critical $false

# 3.3 检查临时文件
$tempFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $_.Name -match "\.tmp$|\.temp$|临时|temp"
}

Add-Check -Category "historical_cleanup" -CheckName "无临时文件" `
    -Passed ($tempFiles.Count -eq 0) `
    -Message "临时文件: $($tempFiles.Count) 个" `
    -FixSuggestion "移除所有临时文件" `
    -Critical $false

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
Write-Host "`n=== 架构合理性审核完成 ===" -ForegroundColor Cyan
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

foreach ($category in @("implementation_path", "component_consistency", "historical_cleanup")) {
    $categoryChecks = $checkResults[$category]
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $jsonReport.category_scores[$category] = $categoryScore
    }
}

$jsonFilePath = Join-Path $OutputDir "architecture_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`n详细JSON报告已保存到: $jsonFilePath" -ForegroundColor Cyan

# 最终建议
Write-Host "`n=== 最终建议 ===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "✅ 优秀! 架构合理性符合ClawHub标准" -ForegroundColor Green
    Write-Host "建议: 可以继续其他维度的审核" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "⚠️ 良好，但有改进空间" -ForegroundColor Yellow
    Write-Host "建议: 修复警告问题，提高分数到90%以上" -ForegroundColor Yellow
} else {
    Write-Host "❌ 需要改进" -ForegroundColor Red
    Write-Host "建议: 必须修复严重问题后再发布" -ForegroundColor Red
}

Write-Host "`n审核完成。请查看详细报告获取具体改进建议。" -ForegroundColor White