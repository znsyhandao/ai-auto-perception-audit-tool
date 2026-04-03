# audit_metadata.ps1
# 元数据完整性维度专项检查工具
# 检查版本一致性、链接真实性、作者信息合理性

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\metadata_audit",
    [switch]$Verbose = $false
)

Write-Host "=== 元数据完整性审核 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "技能目录: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化检查结果
$checkResults = @{
    "version_consistency" = @{}
    "link_validity" = @{}
    "author_info" = @{}
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
# 1. 版本一致性检查 (关键!)
# ============================================
Write-Host "## 1. 版本一致性检查" -ForegroundColor Yellow

# 收集所有文件中的版本号
$versionSources = @()

# 1.1 config.yaml版本号
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

# 1.2 package.json版本号
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

# 1.3 skill.py版本号
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

# 1.4 SKILL.md版本号
$skillMdPath = Join-Path $SkillDir "SKILL.md"
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    if ($skillMdContent -match "版本[：:]\s*([\d\.]+)") {
        $versionSources += @{
            "file" = "SKILL.md"
            "version" = $matches[1]
        }
    }
}

# 1.5 检查版本一致性
if ($versionSources.Count -gt 0) {
    # 获取第一个版本作为基准
    $baseVersion = $versionSources[0].version
    $allSame = $true
    $differentVersions = @()
    
    foreach ($source in $versionSources) {
        if ($source.version -ne $baseVersion) {
            $allSame = $false
            $differentVersions += "$($source.file): $($source.version)"
        }
    }
    
    Add-Check -Category "version_consistency" -CheckName "版本号完全一致" `
        -Passed $allSame -Message "发现不一致版本: $($differentVersions -join '; ')" `
        -FixSuggestion "统一所有文件版本号为: $baseVersion" `
        -Critical $true
    
    # 1.6 版本号格式检查
    $isValidVersion = $baseVersion -match "^\d+\.\d+\.\d+$"
    Add-Check -Category "version_consistency" -CheckName "版本号格式正确" `
        -Passed $isValidVersion -Message "版本号格式: $baseVersion" `
        -FixSuggestion "使用语义化版本: MAJOR.MINOR.PATCH" `
        -Critical $false
} else {
    Add-Check -Category "version_consistency" -CheckName "找到版本号" `
        -Passed $false -Message "未在任何文件中找到版本号" `
        -FixSuggestion "在config.yaml、package.json等文件中添加版本号" `
        -Critical $true
}

# ============================================
# 2. 链接真实性检查 (关键!)
# ============================================
Write-Host "`n## 2. 链接真实性检查" -ForegroundColor Yellow

# 2.1 收集所有链接
$allLinks = @()

# 从README.md收集链接
$readmePath = Join-Path $SkillDir "README.md"
if (Test-Path $readmePath) {
    $readmeContent = Get-Content $readmePath -Raw
    $urlMatches = [regex]::Matches($readmeContent, 'https?://[^\s<>"''\)]+')
    foreach ($match in $urlMatches) {
        $allLinks += @{
            "file" = "README.md"
            "url" = $match.Value
        }
    }
}

# 从SKILL.md收集链接
if (Test-Path $skillMdPath) {
    $skillMdContent = Get-Content $skillMdPath -Raw
    $urlMatches = [regex]::Matches($skillMdContent, 'https?://[^\s<>"''\)]+')
    foreach ($match in $urlMatches) {
        $allLinks += @{
            "file" = "SKILL.md"
            "url" = $match.Value
        }
    }
}

# 从package.json收集链接
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
        # 忽略错误
    }
}

# 2.2 检查链接有效性
$validLinks = 0
$invalidLinks = @()

foreach ($link in $allLinks) {
    $url = $link.url
    
    # 检查URL格式
    $isValidFormat = $url -match '^https?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}'
    
    # 检查是否为占位符
    $isPlaceholder = $url -match 'example\.com|placeholder|TODO|FIXME|your-username|your-repo'
    
    if ($isValidFormat -and (-not $isPlaceholder)) {
        $validLinks++
    } else {
        $invalidLinks += "$($link.file): $url"
    }
}

$totalLinks = $allLinks.Count
$allLinksValid = $invalidLinks.Count -eq 0

Add-Check -Category "link_validity" -CheckName "所有链接真实有效" `
    -Passed $allLinksValid `
    -Message "链接有效性: $validLinks/$totalLinks 有效, 无效: $($invalidLinks.Count)" `
    -FixSuggestion "修复无效链接: $($invalidLinks -join '; ')" `
    -Critical $true

# ============================================
# 3. 作者信息合理性检查
# ============================================
Write-Host "`n## 3. 作者信息合理性检查" -ForegroundColor Yellow

# 3.1 package.json作者信息
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $author = $packageJson.author
        
        if ($author) {
            # 检查作者信息是否合理
            $isValidAuthor = $author -notmatch "test|example|demo|placeholder|TODO|FIXME"
            $isValidAuthor = $isValidAuthor -and $author.Length -ge 2 -and $author.Length -le 100
            
            Add-Check -Category "author_info" -CheckName "作者信息合理" `
                -Passed $isValidAuthor `
                -Message "作者信息: $author" `
                -FixSuggestion "使用真实合理的作者信息" `
                -Critical $false
        } else {
            Add-Check -Category "author_info" -CheckName "有作者信息" `
                -Passed $false -Message "未找到作者信息" `
                -FixSuggestion "在package.json中添加author字段" `
                -Critical $false
        }
    } catch {
        Add-Check -Category "author_info" -CheckName "package.json格式正确" `
            -Passed $false -Message "package.json格式错误" `
            -FixSuggestion "修复package.json的JSON格式" `
            -Critical $true
    }
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
Write-Host "`n=== 元数据完整性审核完成 ===" -ForegroundColor Cyan
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

foreach ($category in @("version_consistency", "link_validity", "author_info")) {
    $categoryChecks = $checkResults[$category]
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $jsonReport.category_scores[$category] = $categoryScore
    }
}

$jsonFilePath = Join-Path $OutputDir "metadata_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`n详细JSON报告已保存到: $jsonFilePath" -ForegroundColor Cyan

# 最终建议
Write-Host "`n=== 最终建议 ===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "✅ 优秀! 元数据完整性符合ClawHub标准" -ForegroundColor Green
    Write-Host "建议: 可以继续其他维度的审核" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "⚠️ 良好，但有改进空间" -ForegroundColor Yellow
    Write-Host "建议: 修复警告问题，提高分数到90%以上" -ForegroundColor Yellow
} else {
    Write-Host "❌ 需要改进" -ForegroundColor Red
    Write-Host "建议: 必须修复严重问题后再发布" -ForegroundColor Red
}

Write-Host "`n审核完成。请查看详细报告获取具体改进建议。" -ForegroundColor White