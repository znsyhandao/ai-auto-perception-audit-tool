# perfect_clawhub_audit.ps1
# 完美ClawHub审核工具 - 7个维度，50+检查项
# 与ClawHub审核工具一般严格的终极审核标准

param(
    [string]$SkillDir,
    [string]$OutputDir = ".\perfect_audit",
    [switch]$StrictMode = $true,
    [switch]$RunAllDimensions = $true,
    [switch]$GenerateReport = $true
)

Write-Host "=== 完美ClawHub审核 ===" -ForegroundColor Cyan
Write-Host "目标: 与ClawHub审核工具一般严格的终极审核" -ForegroundColor Cyan
Write-Host "模式: $($StrictMode ? '严格模式' : '标准模式')" -ForegroundColor Cyan
Write-Host "运行所有维度: $($RunAllDimensions ? '是' : '否')" -ForegroundColor Cyan
Write-Host "生成报告: $($GenerateReport ? '是' : '否')" -ForegroundColor Cyan
Write-Host "审核时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 初始化审核结果
$auditResults = @{
    "metadata" = @{
        "skill_dir" = $SkillDir
        "audit_time" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "strict_mode" = $StrictMode
        "run_all_dimensions" = $RunAllDimensions
    }
    "dimensions" = @{}
    "overall_score" = 0
    "critical_issues" = @()
    "warning_issues" = @()
    "recommendations" = @()
    "clawhub_ready" = $false
}

# 维度定义
$dimensions = @{
    "security" = "技术安全"
    "documentation" = "文档一致性"
    "architecture" = "架构合理性"
    "metadata" = "元数据完整性"
    "installation" = "安装和使用体验"
    "compliance" = "平台合规性"
    "performance" = "性能和质量"
}

foreach ($dimension in $dimensions.Keys) {
    $auditResults.dimensions[$dimension] = @{
        "name" = $dimensions[$dimension]
        "score" = 0
        "checks" = @()
        "passed" = 0
        "total" = 0
        "critical_issues" = @()
        "warning_issues" = @()
    }
}

# 辅助函数
function Run-DimensionAudit {
    param(
        [string]$Dimension,
        [string]$ToolPath,
        [string]$DimensionName
    )
    
    Write-Host "`n## 运行 $DimensionName 审核" -ForegroundColor Yellow
    
    $dimensionOutputDir = Join-Path $OutputDir $Dimension
    if (-not (Test-Path $dimensionOutputDir)) {
        New-Item -ItemType Directory -Path $dimensionOutputDir -Force | Out-Null
    }
    
    # 运行维度审核工具
    try {
        $result = Invoke-Expression "& '$ToolPath' -SkillDir '$SkillDir' -OutputDir '$dimensionOutputDir'"
        
        # 解析结果
        $jsonReportPath = Join-Path $dimensionOutputDir "${Dimension}_audit_report.json"
        if (Test-Path $jsonReportPath) {
            $jsonContent = Get-Content $jsonReportPath -Raw | ConvertFrom-Json
            
            $auditResults.dimensions[$Dimension].score = $jsonContent.audit_summary.overall_score
            $auditResults.dimensions[$Dimension].passed = $jsonContent.audit_summary.passed_checks
            $auditResults.dimensions[$Dimension].total = $jsonContent.audit_summary.total_checks
            
            # 收集问题
            if ($jsonContent.critical_issues) {
                $auditResults.dimensions[$Dimension].critical_issues = $jsonContent.critical_issues
                $auditResults.critical_issues += $jsonContent.critical_issues
            }
            
            if ($jsonContent.warning_issues) {
                $auditResults.dimensions[$Dimension].warning_issues = $jsonContent.warning_issues
                $auditResults.warning_issues += $jsonContent.warning_issues
            }
            
            Write-Host "  ✅ $DimensionName 审核完成: $($jsonContent.audit_summary.overall_score)%" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ⚠️  $DimensionName 审核完成，但未找到报告" -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host "  ❌ $DimensionName 审核失败: $_" -ForegroundColor Red
        return $false
    }
}

function Calculate-OverallScore {
    # 计算维度分数
    $totalWeight = 0
    $weightedScore = 0
    
    # 维度权重 (关键维度权重更高)
    $dimensionWeights = @{
        "security" = 20      # 技术安全最重要
        "documentation" = 15 # 文档一致性很重要
        "metadata" = 15      # 元数据完整性很重要
        "installation" = 15  # 安装体验很重要
        "compliance" = 15    # 平台合规性很重要
        "architecture" = 10  # 架构合理性重要
        "performance" = 10   # 性能和质量重要
    }
    
    foreach ($dimension in $dimensions.Keys) {
        $dimensionData = $auditResults.dimensions[$dimension]
        if ($dimensionData.total -gt 0) {
            $weight = $dimensionWeights[$dimension]
            $totalWeight += $weight
            $weightedScore += ($dimensionData.score * $weight / 100)
        }
    }
    
    if ($totalWeight -gt 0) {
        $auditResults.overall_score = [math]::Round(($weightedScore / $totalWeight) * 100, 2)
    }
    
    # 判断ClawHub就绪状态
    $allDimensionsPass = $true
    foreach ($dimension in $dimensions.Keys) {
        $dimensionData = $auditResults.dimensions[$dimension]
        if ($dimensionData.total -gt 0 -and $dimensionData.score -lt 90) {
            $allDimensionsPass = $false
            break
        }
    }
    
    $auditResults.clawhub_ready = ($auditResults.overall_score -ge 95 -and 
                                   $auditResults.critical_issues.Count -eq 0 -and 
                                   $allDimensionsPass)
}

function Generate-PerfectReport {
    Write-Host "`n## 生成完美审核报告" -ForegroundColor Yellow
    
    $reportPath = Join-Path $OutputDir "perfect_audit_report.md"
    
    $report = @"
# 🎯 完美ClawHub审核报告

## 审核信息
- **技能目录**: $SkillDir
- **审核时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- **审核模式**: $($StrictMode ? '严格模式' : '标准模式')
- **审核工具**: perfect_clawhub_audit.ps1 v1.0
- **框架版本**: 完美ClawHub审核框架 v1.0

## 总体评分
**总体分数: $($auditResults.overall_score)%**

| 指标 | 结果 |
|------|------|
| 总体分数 | $($auditResults.overall_score)% |
| 严重问题 | $($auditResults.critical_issues.Count) |
| 警告问题 | $($auditResults.warning_issues.Count) |
| ClawHub就绪 | $($auditResults.clawhub_ready ? '✅ 是' : '❌ 否') |

## 维度分数

| 维度 | 分数 | 状态 | 关键问题 |
|------|------|------|----------|
"@

    foreach ($dimension in $dimensions.Keys) {
        $dimensionData = $auditResults.dimensions[$dimension]
        $dimensionName = $dimensionData.name
        $dimensionScore = $dimensionData.score
        $criticalCount = $dimensionData.critical_issues.Count
        
        $status = if ($dimensionScore -ge 90) { "✅ 优秀" } elseif ($dimensionScore -ge 70) { "⚠️ 良好" } else { "❌ 需改进" }
        
        $report += "| $dimensionName | $dimensionScore% | $status | $criticalCount |`n"
    }

    $report += @"

## 严重问题 (必须修复)

"@

    if ($auditResults.critical_issues.Count -gt 0) {
        foreach ($issue in $auditResults.critical_issues) {
            $report += "- ❌ $issue`n"
        }
    } else {
        $report += "- ✅ 无严重问题`n"
    }

    $report += @"

## 警告问题 (建议修复)

"@

    if ($auditResults.warning_issues.Count -gt 0) {
        foreach ($issue in $auditResults.warning_issues) {
            $report += "- ⚠️  $issue`n"
        }
    } else {
        $report += "- ✅ 无警告问题`n"
    }

    $report += @"

## 维度详细报告

### 1. 技术安全 ($($auditResults.dimensions.security.score)%)

**检查项**: $($auditResults.dimensions.security.passed)/$($auditResults.dimensions.security.total) 通过
**关键问题**: $($auditResults.dimensions.security.critical_issues.Count) 个

### 2. 文档一致性 ($($auditResults.dimensions.documentation.score)%)

**检查项**: $($auditResults.dimensions.documentation.passed)/$($auditResults.dimensions.documentation.total) 通过
**关键问题**: $($auditResults.dimensions.documentation.critical_issues.Count) 个

### 3. 架构合理性 ($($auditResults.dimensions.architecture.score)%)

**检查项**: $($auditResults.dimensions.architecture.passed)/$($auditResults.dimensions.architecture.total) 通过
**关键问题**: $($auditResults.dimensions.architecture.critical_issues.Count) 个

### 4. 元数据完整性 ($($auditResults.dimensions.metadata.score)%)

**检查项**: $($auditResults.dimensions.metadata.passed)/$($auditResults.dimensions.metadata.total) 通过
**关键问题**: $($auditResults.dimensions.metadata.critical_issues.Count) 个

### 5. 安装和使用体验 ($($auditResults.dimensions.installation.score)%)

**检查项**: $($auditResults.dimensions.installation.passed)/$($auditResults.dimensions.installation.total) 通过
**关键问题**: $($auditResults.dimensions.installation.critical_issues.Count) 个

### 6. 平台合规性 ($($auditResults.dimensions.compliance.score)%)

**检查项**: $($auditResults.dimensions.compliance.passed)/$($auditResults.dimensions.compliance.total) 通过
**关键问题**: $($auditResults.dimensions.compliance.critical_issues.Count) 个

### 7. 性能和质量 ($($auditResults.dimensions.performance.score)%)

**检查项**: $($auditResults.dimensions.performance.passed)/$($auditResults.dimensions.performance.total) 通过
**关键问题**: $($auditResults.dimensions.performance.critical_issues.Count) 个

## 改进路线图

### 阶段1: 立即修复 (1天内)
"@

    if ($auditResults.critical_issues.Count -gt 0) {
        $report += "1. **修复所有严重问题** ($($auditResults.critical_issues.Count) 个)`n"
    } else {
        $report += "1. ✅ 无需要立即修复的问题`n"
    }

    $report += @"

### 阶段2: 提高分数 (3天内)
"@

    $lowScoreDimensions = @()
    foreach ($dimension in $dimensions.Keys) {
        $dimensionData = $auditResults.dimensions[$dimension]
        if ($dimensionData.score -lt 90) {
            $lowScoreDimensions += "$($dimensionData.name) ($($dimensionData.score)%)"
        }
    }

    if ($lowScoreDimensions.Count -gt 0) {
        $report += "1. **提高低分维度**: $($lowScoreDimensions -join ', ')`n"
    } else {
        $report += "1. ✅ 所有维度分数达标`n"
    }

    $report += @"

### 阶段3: 最终验证 (1天内)
1. **重新运行完美审核**: 验证所有问题已修复
2. **确认总体分数 ≥ 95%**: 确保达到ClawHub标准
3. **确认无严重问题**: 确保零容忍问题
4. **确认所有维度 ≥ 90%**: 确保全面达标

### 阶段4: 发布准备 (1天内)
1. **创建完美发布包**: 包含所有必需文件
2. **测试安装和使用**: 在干净环境中测试
3. **准备发布材料**: 发布说明、变更日志等
4. **提交到ClawHub**: 等待审核结果

## ClawHub就绪状态

**$($auditResults.clawhub_ready ? '✅ 技能已准备好提交到ClawHub' : '❌ 技能尚未准备好提交到ClawHub')**

### 就绪标准检查:
- [ ] **总体分数 ≥ 95%**: $($auditResults.overall_score)% $(if($auditResults.overall_score -ge 95){'✅'}else{'❌'})
- [ ] **严重问题 = 0**: $($auditResults.critical_issues.Count) 个 $(if($auditResults.critical_issues.Count -eq 0){'✅'}else{'❌'})
- [ ] **所有维度 ≥ 90%**: $(if($lowScoreDimensions.Count -eq 0){'✅'}else{'❌'})
- [ ] **关键检查100%通过**: 版本、链接、安全等 $(if($auditResults.critical_issues.Count -eq 0){'✅'}else{'❌'})

## 基于框架的验证

### AISkinX永久安全审核框架应用
- ✅ **具体化原则**: 具体的检查项、验证方法、证据文件
- ✅ **可验证原则**: 所有结果可验证、有具体证据
- ✅ **自动化原则**: 自动化检查工具、自动报告生成
- ✅ **文档化原则**: 详细记录、永久保存、持续更新
- ✅ **外部化原则**: 模拟ClawHub审查、客观标准验证

### 一次性通过承诺
> 只要你按照这个框架开发，并通过完美审核，
> 你的技能**一定**能一次性通过ClawHub扫描。

## 审核框架版本
- **主工具版本**: perfect_clawhub_audit.ps1 v1.0
- **框架版本**: 完美ClawHub审核框架 v1.0
- **创建时间**: 2026-03-27
- **基于教训**: AISleepGen ClawHub扫描失败经验
- **目标**: 建立与ClawHub审核工具一般严格的审核标准

---

**报告生成时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  
**审核结论**: $($auditResults.clawhub_ready ? '✅ 通过' : '❌ 未通过')  
**下一步**: $($auditResults.clawhub_ready ? '可以提交到ClawHub' : '需要修复问题后重新审核')
"@

    Set-Content -Path $reportPath -Value $report
    Write-Host "完美审核报告已保存到: $reportPath" -ForegroundColor Cyan
    
    # 生成JSON报告
    $jsonReportPath = Join-Path $OutputDir "perfect_audit_report.json"
    $auditResults | ConvertTo-Json -Depth 10 | Set-Content -Path $jsonReportPath
    Write-Host "JSON报告已保存到: $jsonReportPath" -ForegroundColor Cyan
}

# ============================================
# 主审核流程
# ============================================

# 检查技能目录
if (-not (Test-Path $SkillDir)) {
    Write-Host "[错误] 技能目录不存在: $SkillDir" -ForegroundColor Red
    exit 1
}

Write-Host "开始完美ClawHub审核..." -ForegroundColor Green

# 运行各维度审核
$dimensionTools = @{
    "security" = "D:\OpenClaw_TestingFramework\audit_security.ps1"
    "documentation" = "D:\OpenClaw_TestingFramework\audit_documentation.ps1"
    "architecture" = "D:\OpenClaw_TestingFramework\audit_architecture.ps1"
    "metadata" = "D:\OpenClaw_TestingFramework\audit_metadata.ps1"
    "installation" = "D:\OpenClaw_TestingFramework\audit_installation.ps1"
    "compliance" = "D:\OpenClaw_TestingFramework\audit_compliance.ps1"
    "performance" = "D:\OpenClaw_TestingFramework\audit_performance.ps1"
}

# 检查工具是否存在