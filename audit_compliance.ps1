# audit_compliance.ps1
# 平台合规性维度专项检查工具
# 检查ClawHub特定要求、许可证合规性、发布合规性

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\compliance_audit",
    [switch]$Verbose = $false
)

Write-Host "=== 平台合规性审核 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "技能目录: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化检查结果
$checkResults = @{
    "clawhub_requirements" = @{}
    "license_compliance" = @{}
    "release_compliance" = @{}
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
# 1. ClawHub特定要求检查
# ============================================
Write-Host "## 1. ClawHub特定要求检查" -ForegroundColor Yellow

# 1.1 检查技能名称格式
$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $skillName = $packageJson.name
        
        # 检查技能名称格式
        $isValidName = $skillName -match '^[a-z0-9\-]+$' -and $skillName.Length -ge 3 -and $skillName.Length -le 50
        $isNotPlaceholder = $skillName -notmatch 'test|example|demo|placeholder|my-skill'
        
        Add-Check -Category "clawhub_requirements" -CheckName "技能名称格式正确" `
            -Passed ($isValidName -and $isNotPlaceholder) `
            -Message "技能名称: $skillName" `
            -FixSuggestion "使用小写字母、数字和连字符，避免占位符名称" `
            -Critical $true
    } catch {
        Add-Check -Category "clawhub_requirements" -CheckName "package.json格式正确" `
            -Passed $false -Message "package.json格式错误" `
            -FixSuggestion "修复package.json的JSON格式" `
            -Critical $true
    }
}

# 1.2 检查技能描述
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $description = $packageJson.description
        
        $hasDescription = ![string]::IsNullOrEmpty($description)
        $descriptionLength = if ($hasDescription) { $description.Length } else { 0 }
        $isValidDescription = $hasDescription -and $descriptionLength -ge 10 -and $descriptionLength -le 200
        
        Add-Check -Category "clawhub_requirements" -CheckName "技能描述合理" `
            -Passed $isValidDescription `
            -Message "描述长度: $descriptionLength 字符" `
            -FixSuggestion "描述应在10-200字符之间，清晰说明技能功能" `
            -Critical $true
    } catch {
        # 忽略错误，已在前面检查
    }
}

# 1.3 检查技能分类
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasCategories = $packageJson.categories -and $packageJson.categories.Count -gt 0
        
        Add-Check -Category "clawhub_requirements" -CheckName "技能分类设置" `
            -Passed $hasCategories `
            -Message "技能分类: $(if($hasCategories){'已设置'}else{'未设置'})" `
            -FixSuggestion "在package.json中添加categories字段" `
            -Critical $false
    } catch {
        # 忽略错误
    }
}

# 1.4 检查技能图标
$iconFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "icon|logo" -and $_.Extension -match "\.png|\.jpg|\.jpeg|\.svg"
}

Add-Check -Category "clawhub_requirements" -CheckName "技能图标存在" `
    -Passed ($iconFiles.Count -gt 0) `
    -Message "图标文件: $($iconFiles.Count) 个" `
    -FixSuggestion "添加技能图标文件 (icon.png/icon.svg)" `
    -Critical $false

# ============================================
# 2. 许可证合规性检查
# ============================================
Write-Host "`n## 2. 许可证合规性检查" -ForegroundColor Yellow

# 2.1 检查许可证文件
$licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
    $_.Name -match "^LICENSE|^LICENCE|^license|^licence"
}

Add-Check -Category "license_compliance" -CheckName "许可证文件存在" `
    -Passed ($licenseFiles.Count -gt 0) `
    -Message "许可证文件: $($licenseFiles.Count) 个" `
    -FixSuggestion "添加LICENSE文件" `
    -Critical $true

# 2.2 检查package.json许可证字段
if (Test-Path $packagePath) {
    try {
        $packageJson = Get-Content $packagePath -Raw | ConvertFrom-Json
        $hasLicenseField = ![string]::IsNullOrEmpty($packageJson.license)
        
        Add-Check -Category "license_compliance" -CheckName "package.json许可证字段" `
            -Passed $hasLicenseField `
            -Message "package.json许可证字段: $(if($hasLicenseField){'存在'}else{'缺失'})" `
            -FixSuggestion "在package.json中添加license字段" `
            -Critical $true
        
        # 检查许可证类型
        if ($hasLicenseField) {
            $validLicenses = @("MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "ISC", "Unlicense")
            $isValidLicense = $validLicenses -contains $packageJson.license
            
            Add-Check -Category "license_compliance" -CheckName "许可证类型有效" `
                -Passed $isValidLicense `
                -Message "许可证类型: $($packageJson.license)" `
                -FixSuggestion "使用标准许可证类型: MIT, Apache-2.0等" `
                -Critical $false
        }
    } catch {
        # 忽略错误
    }
}

# ============================================
# 3. 发布合规性检查
# ============================================
Write-Host "`n## 3. 发布合规性检查" -ForegroundColor Yellow

# 3.1 检查文件数量
$totalFiles = (Get-ChildItem -Path $SkillDir -File -Recurse | Measure-Object).Count
Add-Check -Category "release_compliance" -CheckName "文件数量合理" `
    -Passed ($totalFiles -le 50) `
    -Message "总文件数: $totalFiles (建议 ≤ 50)" `
    -FixSuggestion "减少不必要的文件，保持简洁" `
    -Critical $false

# 3.2 检查文件大小
$largeFiles = Get-ChildItem -Path $SkillDir -File -Recurse | Where-Object {
    $_.Length -gt 10MB  # 10MB以上为大文件
}

Add-Check -Category "release_compliance" -CheckName "无过大文件" `
    -Passed ($largeFiles.Count -eq 0) `
    -Message "过大文件: $($largeFiles.Count) 个 (>10MB)" `
    -FixSuggestion "压缩或移除过大文件" `
    -Critical $false

# 3.3 检查必需文件
$requiredFiles = @("skill.py", "config.yaml", "SKILL.md", "package.json")
$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $SkillDir $file
    if (-not (Test-Path $filePath)) {
        $missingFiles += $file
    }
}

Add-Check -Category "release_compliance" -CheckName "必需文件齐全" `
    -Passed ($missingFiles.Count -eq 0) `
    -Message "缺失文件: $($missingFiles.Count) 个" `
    -FixSuggestion "添加缺失文件: $($missingFiles -join ', ')" `
    -Critical $true

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
Write-Host "`n=== 平台合规性审核完成 ===" -ForegroundColor Cyan
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

foreach ($category in @("clawhub_requirements", "license_compliance", "release_compliance")) {
    $categoryChecks = $checkResults[$category]
    if ($categoryChecks.Count -gt 0) {
        $passed = ($categoryChecks.Values | Where-Object { $_.passed }).Count
        $total = $categoryChecks.Count
        $categoryScore = $total -gt 0 ? [math]::Round(($passed / $total) * 100, 2) : 0
        
        $jsonReport.category_scores[$category] = $categoryScore
    }
}

$jsonFilePath = Join-Path $OutputDir "compliance_audit_report.json"
$jsonReport | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonFilePath
Write-Host "`n详细JSON报告已保存到: $jsonFilePath" -ForegroundColor Cyan

# 最终建议
Write-Host "`n=== 最终建议 ===" -ForegroundColor Cyan

if ($score -ge 90) {
    Write-Host "✅ 优秀! 平台合规性符合ClawHub标准" -ForegroundColor Green
    Write-Host "建议: 可以继续其他维度的审核" -ForegroundColor Green
} elseif ($score -ge 70) {
    Write-Host "⚠️ 良好，但有改进空间" -ForegroundColor Yellow
    Write-Host "建议: 修复警告问题，提高分数到90%以上" -ForegroundColor Yellow
} else {
    Write-Host "❌ 需要改进" -ForegroundColor Red
    Write-Host "建议: 必须修复严重问题后再发布" -ForegroundColor Red
}

Write-Host "`n审核完成。请查看详细报告获取具体改进建议。" -ForegroundColor White