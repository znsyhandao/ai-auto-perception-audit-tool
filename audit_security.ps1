# audit_security.ps1
# 技术安全维度专项检查工具
# 检查代码安全、配置安全、依赖安全

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\security_audit",
    [switch]$Verbose = $false
)

Write-Host "=== 技术安全审核 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "技能目录: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化检查结果
$checkResults = @{
    "code_security" = @{}
    "config_security" = @{}
    "dependency_security" = @{}
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
# 1. 代码安全检查
# ============================================
Write-Host "## 1. 代码安全检查" -ForegroundColor Yellow

# 1.1 检查网络代码
$skillPath = Join-Path $SkillDir "skill.py"
if (Test-Path $skillPath) {
    $skillContent = Get-Content $skillPath -Raw
    $networkPatterns = @("import requests", "import urllib", "import socket", "import http\.client")
    $networkIssues = @()
    
    foreach ($pattern in $networkPatterns) {
        if ($skillContent -match $pattern) {
            $networkIssues += $pattern
        }
    }
    
    Add-Check -Category "code_security" -CheckName "无网络代码" `
        -Passed ($networkIssues.Count -eq 0) `
        -Message "发现网络代码: $($networkIssues.Count) 处" `
        -FixSuggestion "移除所有网络相关导入: $($networkIssues -join ', ')" `
        -Critical $true
}

# 1.2 检查危险函数
if (Test-Path $skillPath) {
    $dangerousPatterns = @("subprocess\.", "os\.system", "eval\(", "exec\(", "__import__\(")
    $dangerousIssues = @()
    
    foreach ($pattern in $dangerousPatterns) {
        if ($skillContent -match $pattern) {
            $dangerousIssues += $pattern
        }
    }
    
    Add-Check -Category "code_security" -CheckName "无危险函数" `
        -Passed ($dangerousIssues.Count -eq 0) `
        -Message "发现危险函数: $($dangerousIssues.Count) 处" `
        -FixSuggestion "移除所有危险函数调用: $($dangerousIssues -join ', ')" `
        -Critical $true
}

# 1.3 检查路径安全
if (Test-Path $skillPath) {
    $pathPatterns = @("\.\./", "\.\.\\", "上级目录", "遍历.*目录")
    $pathIssues = @()
    
    foreach ($pattern in $pathPatterns) {
        if ($skillContent -match $pattern) {
            $pathIssues += $pattern
        }
    }
    
    Add-Check -Category "code_security" -CheckName "无路径遍历漏洞" `
        -Passed ($pathIssues.Count -eq 0) `
        -Message "发现路径遍历风险: $($pathIssues.Count) 处" `
        -FixSuggestion "修复路径遍历漏洞: $($pathIssues -join ', ')" `
        -Critical $true
}

# 1.4 检查文件操作安全
if (Test-Path $skillPath) {
    $filePatterns = @("open\(.*['\""]w['\""]", "open\(.*['\""]a['\""]", "shutil\.")
    $fileIssues = @()
    
    foreach ($pattern in $filePatterns) {
        if ($skillContent -match $pattern) {
            $fileIssues += $pattern
        }
    }
    
    Add-Check -Category "code_security" -CheckName "文件操作安全" `
        -Passed ($fileIssues.Count -eq 0) `
        -Message "发现文件操作: $($fileIssues.Count) 处" `
        -FixSuggestion "确保文件操作有权限检查" `
        -Critical $false
}

# ============================================
# 2. 配置安全检查
# ============================================
Write-Host "`n## 2. 配置安全检查" -ForegroundColor Yellow

# 2.1 检查config.yaml安全声明
$configPath = Join-Path $SkillDir "config.yaml"
if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    $hasSecuritySection = $configContent -match "security:"
    $hasNetworkAccessFalse = $configContent -match "network_access:\s*false"
    $hasLocalOnlyTrue = $configContent -match "local_only:\s*true"
    $hasPrivacyFriendly = $configContent -match "privacy_friendly:\s*true"
    
    Add-Check -Category "config_security" -CheckName "config.yaml有安全声明" `
        -Passed $hasSecuritySection `
        -Message "安全声明: $(if($hasSecuritySection){'有'}else{'无'})" `
        -FixSuggestion "在config.yaml中添加security部分" `
        -Critical $true
    
    Add-Check -Category "config_security" -CheckName "网络访问声明正确" `
        -Passed $hasNetworkAccessFalse `
        -Message "网络访问: $(if($hasNetworkAccessFalse){'false'}else{'未声明或true'})" `
        -FixSuggestion "设置network_access: false" `
        -Critical $true
    
    Add-Check -Category "config_security" -CheckName "本地处理声明正确" `
        -Passed $hasLocalOnlyTrue `
        -Message "本地处理: $(if($hasLocalOnlyTrue){'true'}else{'未声明或false'})" `
        -FixSuggestion "设置local_only: true" `
        -Critical $true
    
    Add-Check -Category "config_security" -CheckName "隐私友好声明正确" `
        -Passed $hasPrivacyFriendly `
        -Message "隐私友好: $(if($hasPrivacyFriendly){'true'}else{'未声明或false'})" `
        -FixSuggestion "设置privacy_friendly: true" `
        -Critical $false
}

# 2.2 检查危险配置
if (Test-Path $configPath) {
    $dangerousConfigs = @(
        "original_api_url", "world_model_integrator", "updates\.auto_check",
        "external_apis", "http://", "https://", "api.*url", "database.*enabled: true"
    )
    $dangerousFound = @()
    
    foreach ($pattern in $dangerousConfigs) {
        if ($configContent -match $pattern) {
            $dangerousFound += $pattern
        }
    }
    
    Add-Check -Category "config_security" -CheckName "无危险配置" `
        -Passed ($dangerousFound.Count -eq 0) `
        -Message "发现危险配置: $($dangerousFound.Count) 处" `
        -FixSuggestion "移除危险配置: $($dangerousFound -join ', ')" `
        -Critical $true
}

# ============================================
# 3. 依赖安全检查
# ============================================
Write-Host "`n## 3. 依赖安全检查" -ForegroundColor Yellow

# 3.1 检查requirements.txt
$requirementsPath = Join-Path $SkillDir "requirements.txt"
if (Test-Path $requirementsPath) {
    $requirementsContent = Get-Content $requirementsPath
    $hasRequirements = $requirementsContent.Count -gt 0
    
    Add-Check -Category "dependency_security" -CheckName "requirements.txt存在" `
        -Passed $hasRequirements `
        -Message "requirements.txt: $(if($hasRequirements){'有内容'}else{'空文件'})" `
        -FixSuggestion "添加依赖或删除requirements.txt" `
        -Critical $false
    
    # 检查危险依赖
    $dangerousDeps = @("requests", "urllib3", "paramiko", "fabric", "ansible")
    $dangerousFound = @()
    
    foreach ($line in $requirementsContent) {
        foreach ($dep in $dangerousDeps) {
            if ($line -match $dep) {
                $dangerousFound += $dep
            }
        }
    }
    
    if ($hasRequirements) {
        Add-Check -Category "dependency_security" -CheckName "无危险依赖" `
            -Passed ($dangerousFound.Count -eq 0) `
            -Message "发现危险依赖: $($dangerousFound.Count) 个" `
            -FixSuggestion "移除危险依赖: $($dangerousFound -join ', ')" `
            -Critical $true
    }
} else {
    Add-Check -Category "dependency_security" -CheckName "requirements.txt存在" `
        -Passed $false -Message "requirements.txt不存在" `
        -FixSuggestion "创建requirements.txt文件" `
        -Critical $false
}

# 3.2 检查依赖版本
if (Test-Path $requirementsPath -and (Test-Path $requirementsPath) -and $requirementsContent.Count -gt 0) {
    $validVersions = 0
    $invalidVersions = @()
    
    foreach ($line in $requirementsContent) {
        $trimmed = $line.Trim()
        if (-not [string]::IsNullOrEmpty($trimmed) -and -not $trimmed.StartsWith("#")) {
            # 检查版本格式
            if ($trimmed -match '^[a-zA-Z0-9_\-\[\]]+([>=<~!].*)?$') {
                $validVersions++
            } else {
                $invalidVersions += $trimmed
            }
        }
    }
    
    Add-Check -Category "dependency_security" -CheckName "依赖版本格式正确" `
        -Passed ($invalidVersions.Count -eq 0) `
        -Message "依赖版本: $validVersions 有效, $($invalidVersions.Count) 无效" `
        -FixSuggestion "修复无效依赖格式: $($invalidVersions -join ', ')" `
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
Write-Host "`n=== 技术安全审核完成 ===" -ForegroundColor Cyan
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
    "detailed_results" = @{}
}

foreach ($category in @("code_security", "config_security", "dependency_security")) {
    $categoryChecks = $checkResults[$category]
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $jsonReport.category_scores[$category] = $categoryScore
        
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
        $jsonReport.detailed_results[$category] = $detailedChecks
    }
}

$jsonFilePath = Join-Path $OutputDir "security_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`n详细JSON报告已保存到: $jsonFilePath" -ForegroundColor Cyan

# 最终建议
Write-Host "`n=== 最终建议 ===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "✅ 优秀! 技术安全符合ClawHub标准" -ForegroundColor Green
    Write-Host "建议: 可以继续其他维度的审核" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "⚠️ 良好，但有改进空间" -ForegroundColor Yellow
    Write-Host "建议: 修复警告问题，提高分数到90%以上" -ForegroundColor Yellow
} else {
    Write-Host "❌ 需要改进" -ForegroundColor Red
    Write-Host "建议: 必须修复严重问题后再发布" -ForegroundColor Red
}

Write-Host "`n审核完成。请查看详细报告获取具体改进建议。" -ForegroundColor White