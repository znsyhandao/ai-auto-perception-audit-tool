# promise_verification_tool.ps1
# 承诺验证工具 - 确保承诺一一兑现

param(
    [string]$SkillDir,
    [string]$AuditReportPath,
    [switch]$GenerateEvidence = $true
)

Write-Host "=== 承诺验证工具 ===" -ForegroundColor Cyan
Write-Host "目标: 验证审核承诺的可信性和可兑现性" -ForegroundColor Cyan
Write-Host "验证时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "技能目录: $SkillDir" -ForegroundColor Cyan
Write-Host ""

# 检查目录是否存在
if (-not (Test-Path $SkillDir)) {
    Write-Host "[ERROR] 技能目录不存在: $SkillDir" -ForegroundColor Red
    exit 1
}

# 初始化验证结果
$verificationResults = @{
    "metadata" = @{
        "skill_dir" = $SkillDir
        "verification_time" = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        "tool_version" = "1.0"
    }
    "promises" = @()
    "verification_steps" = @()
    "evidence" = @()
    "risks" = @()
    "overall_assessment" = @{
        "promises_verifiable" = $false
        "evidence_complete" = $false
        "risks_disclosed" = $false
        "overall_trust_level" = "unknown"
    }
}

# ============================================
# 步骤1: 检查承诺的明确性
# ============================================
Write-Host "## 步骤1: 检查承诺的明确性" -ForegroundColor Yellow

$promiseChecks = @()

# 检查1: 是否有具体的承诺表述
$hasSpecificPromises = $false
$promiseFiles = Get-ChildItem -Path $SkillDir -Recurse -File -Include *.md, *.txt | Where-Object {
    $_.Name -match "RELEASE|AUDIT|SUMMARY|README"
}

foreach ($file in $promiseFiles) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "通过审核|通过ClawHub|承诺|保证|100%") {
        $hasSpecificPromises = $true
        $promiseChecks += @{
            "file" = $file.Name
            "promise_found" = $true
            "promise_text" = ($content -split "`n" | Where-Object { $_ -match "通过审核|通过ClawHub|承诺|保证|100%" } | Select-Object -First 3)
        }
    }
}

$promiseCheck1 = @{
    "check_name" = "承诺表述明确性"
    "passed" = $hasSpecificPromises
    "message" = if ($hasSpecificPromises) { "找到具体的承诺表述" } else { "未找到具体的承诺表述" }
    "evidence" = $promiseChecks
}

$verificationResults.promises += $promiseCheck1
Write-Host "  $(if ($hasSpecificPromises) { '[PASS]' } else { '[FAIL]' }) 承诺表述明确性" -ForegroundColor $(if ($hasSpecificPromises) { "Green" } else { "Red" })

# ============================================
# 步骤2: 检查检查项的透明度
# ============================================
Write-Host "`n## 步骤2: 检查检查项的透明度" -ForegroundColor Yellow

# 检查是否有检查项清单
$auditReports = Get-ChildItem -Path $SkillDir -Recurse -File | Where-Object {
    $_.Name -match "AUDIT|REPORT|CHECK"
}

$hasChecklist = $false
$checklistDetails = @()

foreach ($report in $auditReports) {
    $content = Get-Content $report.FullName -Raw
    if ($content -match "检查项|check|Check|维度|category") {
        $hasChecklist = $true
        $checklistDetails += @{
            "file" = $report.Name
            "has_checklist" = $true
            "check_count" = ([regex]::Matches($content, "✅|❌|\[PASS\]|\[FAIL\]").Count)
        }
    }
}

$transparencyCheck = @{
    "check_name" = "检查项透明度"
    "passed" = $hasChecklist
    "message" = if ($hasChecklist) { "找到检查项清单" } else { "未找到检查项清单" }
    "evidence" = $checklistDetails
}

$verificationResults.promises += $transparencyCheck
Write-Host "  $(if ($hasChecklist) { '[PASS]' } else { '[FAIL]' }) 检查项透明度" -ForegroundColor $(if ($hasChecklist) { "Green" } else { "Red" })

# ============================================
# 步骤3: 检查验证证据
# ============================================
Write-Host "`n## 步骤3: 检查验证证据" -ForegroundColor Yellow

# 检查验证证据
$evidenceFiles = @()
$evidenceTypes = @()

# 查找各种证据文件
$evidencePatterns = @(
    @{ pattern = ".*\.json$"; type = "JSON报告" },
    @{ pattern = ".*AUDIT.*\.md$"; type = "审核报告" },
    @{ pattern = ".*REPORT.*\.md$"; type = "总结报告" },
    @{ pattern = ".*CHECK.*\.txt$"; type = "检查清单" },
    @{ pattern = ".*LOG.*\.txt$"; type = "日志文件" }
)

foreach ($pattern in $evidencePatterns) {
    $files = Get-ChildItem -Path $SkillDir -Recurse -File | Where-Object {
        $_.Name -match $pattern.pattern
    }
    
    if ($files.Count -gt 0) {
        foreach ($file in $files) {
            $evidenceFiles += @{
                "file" = $file.Name
                "type" = $pattern.type
                "size" = $file.Length
                "modified" = $file.LastWriteTime
            }
            $evidenceTypes += $pattern.type
        }
    }
}

$hasEvidence = $evidenceFiles.Count -ge 3  # 至少需要3种不同类型的证据
$evidenceCheck = @{
    "check_name" = "验证证据完整性"
    "passed" = $hasEvidence
    "message" = if ($hasEvidence) { "找到足够的验证证据 ($($evidenceFiles.Count)个文件)" } else { "验证证据不足 ($($evidenceFiles.Count)个文件)" }
    "evidence" = $evidenceFiles
}

$verificationResults.promises += $evidenceCheck
Write-Host "  $(if ($hasEvidence) { '[PASS]' } else { '[FAIL]' }) 验证证据完整性" -ForegroundColor $(if ($hasEvidence) { "Green" } else { "Red" })

# ============================================
# 步骤4: 检查风险披露
# ============================================
Write-Host "`n## 步骤4: 检查风险披露" -ForegroundColor Yellow

# 检查是否有风险披露
$hasRiskDisclosure = $false
$riskFiles = @()

foreach ($report in $auditReports) {
    $content = Get-Content $report.FullName -Raw
    if ($content -match "风险|风险说明|limitation|Limitation|警告|warning|Warning") {
        $hasRiskDisclosure = $true
        $riskFiles += @{
            "file" = $report.Name
            "has_risk_disclosure" = $true
            "risk_text" = ($content -split "`n" | Where-Object { $_ -match "风险|风险说明|limitation|Limitation|警告|warning|Warning" } | Select-Object -First 3)
        }
    }
}

$riskCheck = @{
    "check_name" = "风险披露完整性"
    "passed" = $hasRiskDisclosure
    "message" = if ($hasRiskDisclosure) { "找到风险披露" } else { "未找到风险披露" }
    "evidence" = $riskFiles
}

$verificationResults.promises += $riskCheck
Write-Host "  $(if ($hasRiskDisclosure) { '[PASS]' } else { '[FAIL]' }) 风险披露完整性" -ForegroundColor $(if ($hasRiskDisclosure) { "Green" } else { "Red" })

# ============================================
# 步骤5: 检查可验证性
# ============================================
Write-Host "`n## 步骤5: 检查可验证性" -ForegroundColor Yellow

# 检查是否有验证步骤
$hasVerificationSteps = $false
$verificationDetails = @()

foreach ($report in $auditReports) {
    $content = Get-Content $report.FullName -Raw
    if ($content -match "验证|verify|Verify|步骤|step|Step|方法|method|Method") {
        $hasVerificationSteps = $true
        $verificationDetails += @{
            "file" = $report.Name
            "has_verification_steps" = $true
            "step_count" = ([regex]::Matches($content, "步骤\d+|Step \d+|^\d+\.").Count)
        }
    }
}

$verifiabilityCheck = @{
    "check_name" = "承诺可验证性"
    "passed" = $hasVerificationSteps
    "message" = if ($hasVerificationSteps) { "找到验证步骤" } else { "未找到验证步骤" }
    "evidence" = $verificationDetails
}

$verificationResults.promises += $verifiabilityCheck
Write-Host "  $(if ($hasVerificationSteps) { '[PASS]' } else { '[FAIL]' }) 承诺可验证性" -ForegroundColor $(if ($hasVerificationSteps) { "Green" } else { "Red" })

# ============================================
# 步骤6: 实际验证关键承诺
# ============================================
Write-Host "`n## 步骤6: 实际验证关键承诺" -ForegroundColor Yellow

$actualVerificationSteps = @()

# 步骤6.1: 验证版本一致性
Write-Host "  6.1 验证版本一致性..." -ForegroundColor Cyan
$versionCheck = @{
    "step" = "版本一致性验证"
    "status" = "pending"
}

try {
    # 检查config.yaml版本
    $configPath = Join-Path $SkillDir "config.yaml"
    if (Test-Path $configPath) {
        $configContent = Get-Content $configPath -Raw
        if ($configContent -match 'version:\s*["'']?([0-9]+\.[0-9]+\.[0-9]+)["'']?') {
            $configVersion = $matches[1]
            $versionCheck.config_version = $configVersion
        }
    }
    
    # 检查package.json版本
    $packagePath = Join-Path $SkillDir "package.json"
    if (Test-Path $packagePath) {
        $packageContent = Get-Content $packagePath -Raw
        if ($packageContent -match '"version"\s*:\s*["'']([0-9]+\.[0-9]+\.[0-9]+)["'']') {
            $packageVersion = $matches[1]
            $versionCheck.package_version = $packageVersion
        }
    }
    
    # 检查SKILL.md版本
    $skillPath = Join-Path $SkillDir "SKILL.md"
    if (Test-Path $skillPath) {
        $skillContent = Get-Content $skillPath -Raw
        if ($skillContent -match 'Version:\s*([0-9]+\.[0-9]+\.[0-9]+)') {
            $skillVersion = $matches[1]
            $versionCheck.skill_version = $skillVersion
        }
    }
    
    # 验证一致性
    $versions = @($configVersion, $packageVersion, $skillVersion) | Where-Object { $_ -ne $null }
    if ($versions.Count -ge 2) {
        $firstVersion = $versions[0]
        $allSame = $true
        foreach ($v in $versions) {
            if ($v -ne $firstVersion) {
                $allSame = $false
                break
            }
        }
        
        $versionCheck.status = if ($allSame) { "passed" } else { "failed" }
        $versionCheck.message = if ($allSame) { "所有版本一致: $firstVersion" } else { "版本不一致: $($versions -join ', ')" }
    } else {
        $versionCheck.status = "failed"
        $versionCheck.message = "无法提取足够的版本信息"
    }
} catch {
    $versionCheck.status = "error"
    $versionCheck.message = "验证过程中出错: $_"
}

$actualVerificationSteps += $versionCheck
Write-Host "    $(if ($versionCheck.status -eq 'passed') { '✅' } else { '❌' }) $($versionCheck.message)" -ForegroundColor $(if ($versionCheck.status -eq 'passed') { "Green" } else { "Red" })

# 步骤6.2: 验证安全合规
Write-Host "  6.2 验证安全合规..." -ForegroundColor Cyan
$securityCheck = @{
    "step" = "安全合规验证"
    "status" = "pending"
}

try {
    # 检查config.yaml安全声明
    if (Test-Path $configPath) {
        $configContent = Get-Content $configPath -Raw
        $hasSecuritySection = $configContent -match 'security:'
        $hasNetworkAccessFalse = $configContent -match 'network_access:\s*false'
        $hasLocalOnlyTrue = $configContent -match 'local_only:\s*true'
        
        $securityCheck.has_security_section = $hasSecuritySection
        $securityCheck.has_network_access_false = $hasNetworkAccessFalse
        $securityCheck.has_local_only_true = $hasLocalOnlyTrue
        
        $securityPassed = $hasSecuritySection -and $hasNetworkAccessFalse -and $hasLocalOnlyTrue
        $securityCheck.status = if ($securityPassed) { "passed" } else { "failed" }
        $securityCheck.message = if ($securityPassed) { "安全声明完整" } else { "安全声明不完整" }
    } else {
        $securityCheck.status = "failed"
        $securityCheck.message = "config.yaml文件不存在"
    }
} catch {
    $securityCheck.status = "error"
    $securityCheck.message = "验证过程中出错: $_"
}

$actualVerificationSteps += $securityCheck
Write-Host "    $(if ($securityCheck.status -eq 'passed') { '✅' } else { '❌' }) $($securityCheck.message)" -ForegroundColor $(if ($securityCheck.status -eq 'passed') { "Green" } else { "Red" })

# 步骤6.3: 验证许可证文件
Write-Host "  6.3 验证许可证文件..." -ForegroundColor Cyan
$licenseCheck = @{
    "step" = "许可证文件验证"
    "status" = "pending"
}

try {
    $licenseFiles = Get-ChildItem -Path $SkillDir -File | Where-Object {
        $_.BaseName -match "^LICENSE$|^LICENCE$|^license$|^licence$"
    }
    
    if ($licenseFiles.Count -gt 0) {
        $licenseFile = $licenseFiles[0]
        $hasValidExtension = $licenseFile.Extension -in @(".txt", ".md")
        $licenseCheck.file_name = $licenseFile.Name
        $licenseCheck.has_valid_extension = $hasValidExtension
        
        # 检查文件内容
        $licenseContent = Get-Content $licenseFile.FullName -Raw
        $hasLicenseContent = $licenseContent -match "MIT License|Apache License|GPL"
        $licenseCheck.has_license_content = $hasLicenseContent
        
        $licensePassed = $hasValidExtension -and $hasLicenseContent
        $licenseCheck.status = if ($licensePassed) { "passed" } else { "failed" }
        $licenseCheck.message = if ($licensePassed) { "许可证文件有效" } else { "许可证文件无效" }
    } else {
        $licenseCheck.status = "failed"
        $licenseCheck.message = "未找到许可证文件"
    }
} catch {
    $licenseCheck.status = "error"
    $licenseCheck.message = "验证过程中出错: $_"
}

$actualVerificationSteps += $licenseCheck
Write-Host "    $(if ($licenseCheck.status -eq 'passed') { '✅' } else { '❌' }) $($licenseCheck.message)" -ForegroundColor $(if ($licenseCheck.status -eq 'passed') { "Green" } else { "Red" })

$verificationResults.verification_steps = $actualVerificationSteps

# ============================================
# 步骤7: 风险评估
# ============================================
Write-Host "`n## 步骤7: 风险评估" -ForegroundColor Yellow

$risks = @()

# 风险1: 检查深度不足
$risks += @{
    "risk_name" = "检查深度不足"
    "risk_level" = "medium"
    "description" = "我们的检查主要是表面检查，缺乏深度代码分析（如AST分析、控制流分析）"
    "impact" = "可能遗漏复杂的安全漏洞"
    "mitigation" = "开发深度分析工具，建立人工复核机制"
}

# 风险2: 未知的ClawHub规则
$risks += @{
    "risk_name" = "未知的ClawHub规则"
    "risk_level" = "high"
    "description" = "ClawHub可能有我们不知道的检查规则"
    "impact" = "即使通过我们的检查，也可能因未知规则而失败"
    "mitigation" = "持续监控ClawHub扫描结果，基于反馈更新框架"
}

# 风险3: 工具准确性
$risks += @{
    "risk_name" = "工具准确性风险"
    "risk_level" = "medium"
    "description" = "我们的检查工具可能有误报或漏报"
    "impact" = "可能错误地通过或拒绝某些检查项"
    "mitigation" = "建立工具测试机制，定期验证工具准确性"
}

# 风险4: 环境差异
$risks += @{
    "risk_name" = "环境差异风险"
    "risk_level" = "low"
    "description" = "我们的检查环境可能与ClawHub的扫描环境不同"
    "impact" = "环境差异可能导致不同的检查结果"
    "mitigation" = "尽量模拟ClawHub的检查环境，记录环境信息"
}

$verificationResults.risks = $risks

# 显示风险评估
foreach ($risk in $risks) {
    $color = if ($risk.risk_level -eq "high") { "Red" } elseif ($risk.risk_level -eq "medium") { "Yellow" } else { "Cyan" }
    Write-Host "  ⚠️  $($risk.risk_name) ($($risk.risk_level)风险)" -ForegroundColor $color
    Write-Host "    描述: $($risk.description)" -ForegroundColor Gray
    Write-Host "    缓解: $($risk.mitigation)" -ForegroundColor Gray
}

# ============================================
# 总体评估
# ============================================
Write-Host "`n## 总体评估" -ForegroundColor Cyan

# 计算通过率
$promiseChecksPassed = ($verificationResults.promises | Where-Object { $_.passed }).Count
$promiseChecksTotal = $verificationResults.promises.Count
$promisePassRate = if ($promiseChecksTotal -gt 0) { [math]::Round(($promiseChecksPassed / $promiseChecksTotal) * 100) } else { 0 }

# 实际验证通过率
$actualStepsPassed = ($actualVerificationSteps | Where-Object { $_.status -eq "passed" }).Count
$actualStepsTotal = $actualVerificationSteps.Count
$actualPassRate = if ($actualStepsTotal -gt 0) { [math]::Round(($actualStepsPassed / $actualStepsTotal) * 100) } else { 0 }

# 总体信任等级
$overallScore = [math]::Round(($promisePassRate * 0.4) + ($actualPassRate * 0.6))
$trustLevel = if ($overallScore -ge 90) { "high" } elseif ($overallScore -ge 70) { "medium" } else { "low" }

# 更新总体评估
$verificationResults.overall_assessment.promises_verifiable = $promisePassRate -ge 80
$verificationResults.overall_assessment.evidence_complete = $hasEvidence
$verificationResults.overall_assessment.risks_disclosed = $hasRiskDisclosure
$verificationResults.overall_assessment.overall_trust_level = $trustLevel
$verificationResults.overall_assessment.promise_pass_rate = $promisePassRate
$verificationResults.overall_assessment.actual_pass_rate = $actualPassRate
$verificationResults.overall_assessment.overall_score = $overallScore

# 显示总体评估结果
Write-Host "承诺检查通过率: $promisePassRate% ($promiseChecksPassed/$promiseChecksTotal)" -ForegroundColor White
Write-Host "实际验证通过率: $actualPassRate% ($actualStepsPassed/$actualStepsTotal)" -ForegroundColor White
Write-Host "总体信任分数: $overallScore%" -ForegroundColor $(if ($overallScore -ge 90) { "Green" } elseif ($overallScore -ge 70) { "Yellow" } else { "Red" })
Write-Host "信任等级: $trustLevel" -ForegroundColor $(if ($trustLevel -eq "high") { "Green" } elseif ($trustLevel -eq "medium") { "Yellow" } else { "Red" })

# 显示具体评估
Write-Host "`n具体评估:" -ForegroundColor Cyan
Write-Host "  $(if ($verificationResults.overall_assessment.promises_verifiable) { '✅' } else { '❌' }) 承诺可验证性: $(if ($verificationResults.overall_assessment.promises_verifiable) { '良好' } else { '不足' })" -ForegroundColor $(if ($verificationResults.overall_assessment.promises_verifiable) { "Green" } else { "Red" })
Write-Host "  $(if ($verificationResults.overall_assessment.evidence_complete) { '✅' } else { '❌' }) 证据完整性: $(if ($verificationResults.overall_assessment.evidence_complete) { '良好' } else { '不足' })" -ForegroundColor $(if ($verificationResults.overall_assessment.evidence_complete) { "Green" } else { "Red" })
Write-Host "  $(if ($verificationResults.overall_assessment.risks_disclosed) { '✅' } else { '❌' }) 风险披露: $(if ($verificationResults.overall_assessment.risks_disclosed) { '良好' } else { '不足' })" -ForegroundColor $(if ($verificationResults.overall_assessment.risks_disclosed) { "Green" } else { "Red" })

# 最终建议
Write-Host "`n=== 最终建议 ===" -ForegroundColor Cyan

if ($trustLevel -eq "high") {
    Write-Host "✅ 建议: 承诺可信度较高，可以依赖" -ForegroundColor Green
    Write-Host "   说明: 承诺表述明确，验证证据充分，风险披露完整" -ForegroundColor Green
} elseif ($trustLevel -eq "medium") {
    Write-Host "⚠️  建议: 承诺可信度中等，需要谨慎" -ForegroundColor Yellow
    Write-Host "   说明: 存在一些改进空间，建议补充验证证据和风险披露" -ForegroundColor Yellow
} else {
    Write-Host "❌ 建议: 承诺可信度较低，不建议依赖" -ForegroundColor Red
    Write-Host "   说明: 承诺表述模糊，验证证据不足，风险披露缺失" -ForegroundColor Red
}

# 改进建议
Write-Host "`n改进建议:" -ForegroundColor Cyan
if (-not $hasSpecificPromises) {
    Write-Host "  • 添加具体的承诺表述" -ForegroundColor Yellow
}
if (-not $hasChecklist) {
    Write-Host "  • 公开检查项清单" -ForegroundColor Yellow
}
if (-not $hasEvidence) {
    Write-Host "  • 补充验证证据" -ForegroundColor Yellow
}
if (-not $hasRiskDisclosure) {
    Write-Host "  • 添加风险披露" -ForegroundColor Yellow
}
if (-not $hasVerificationSteps) {
    Write-Host "  • 提供验证步骤" -ForegroundColor Yellow
}

# 保存验证报告
if ($GenerateEvidence) {
    $reportDir = Join-Path $SkillDir "promise_verification"
    if (-not (Test-Path $reportDir)) {
        New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    }
    
    $reportFile = Join-Path $reportDir "promise_verification_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    $verificationResults | ConvertTo-Json -Depth 5 | Out-File -FilePath $reportFile -Encoding UTF8
    
    Write-Host "`n验证报告已保存到: $reportFile" -ForegroundColor Green
}

Write-Host "`n=== 验证完成 ===" -ForegroundColor Cyan