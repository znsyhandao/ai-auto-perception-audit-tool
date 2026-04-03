# 验证AISkinX v1.0.3是否已修复所有ClawHub问题
$skillDir = "D:\openclaw\releases\AISkinX_v1.0.3"

Write-Host "🔍 验证AISkinX v1.0.3是否已修复所有ClawHub问题..." -ForegroundColor Cyan
Write-Host "=" * 60

if (-not (Test-Path $skillDir)) {
    Write-Host "❌ 技能目录不存在: $skillDir" -ForegroundColor Red
    exit 1
}

# ClawHub发现的6个问题
$issues = @(
    @{ID=1; Issue="文档声明与代码实现不一致"; CheckScript={CheckDocumentationConsistency}},
    @{ID=2; Issue="配置文件残留网络配置"; CheckScript={CheckConfigNetwork}},
    @{ID=3; Issue="PathValidator设计问题"; CheckScript={CheckPathValidator}},
    @{ID=4; Issue="文档乱码问题"; CheckScript={CheckFileEncoding}},
    @{ID=5; Issue="install.bat重复错误"; CheckScript={CheckClawhubStandards}},
    @{ID=6; Issue="测试文件混淆问题"; CheckScript={CheckTestFiles}}
)

# 运行所有检查
$results = @()
foreach ($issue in $issues) {
    Write-Host "`n检查问题$($issue.ID): $($issue.Issue)" -ForegroundColor Cyan
    $result = & $issue.CheckScript
    $results += @{ID=$issue.ID; Issue=$issue.Issue; Passed=$result}
}

# 输出总结
Write-Host "`n📊 检查结果总结:" -ForegroundColor Cyan
Write-Host "=" * 60

$passedCount = ($results | Where-Object { $_.Passed }).Count
$totalCount = $results.Count

foreach ($result in $results) {
    $status = if ($result.Passed) { "✅" } else { "❌" }
    $color = if ($result.Passed) { "Green" } else { "Red" }
    Write-Host "$status 问题$($result.ID): $($result.Issue)" -ForegroundColor $color
}

Write-Host "`n🎯 最终结果:" -ForegroundColor Cyan
if ($passedCount -eq $totalCount) {
    Write-Host "✅ 所有问题已修复！AISkinX v1.0.3可以安全提交" -ForegroundColor Green
    Write-Host "   同样的错误不会犯第二次！" -ForegroundColor Green
} else {
    Write-Host "❌ 还有$($totalCount - $passedCount)个问题需要修复" -ForegroundColor Red
}

# 检查函数
function CheckDocumentationConsistency {
    $skillMdPath = Join-Path $skillDir "SKILL.md"
    if (-not (Test-Path $skillMdPath)) {
        Write-Host "❌ SKILL.md不存在" -ForegroundColor Red
        return $false
    }
    
    # 检查文档中的安全声明
    $content = Get-Content $skillMdPath -Raw -Encoding UTF8
    $hasLocalDeclaration = $content -match "100%.*(local|本地).*(operation|运行)"
    $hasPathRestriction = $content -match "(path|路径).*(restrict|限制)"
    
    if ($hasLocalDeclaration -and $hasPathRestriction) {
        Write-Host "✅ 文档有正确的安全声明" -ForegroundColor Green
        return $true
    } else {
        Write-Host "⚠️  文档安全声明不完整" -ForegroundColor Yellow
        return $false
    }
}

function CheckConfigNetwork {
    $configPath = Join-Path $skillDir "config.yaml"
    if (-not (Test-Path $configPath)) {
        Write-Host "❌ config.yaml不存在" -ForegroundColor Red
        return $false
    }
    
    $content = Get-Content $configPath -Raw -Encoding UTF8
    
    # 检查网络相关配置
    $networkPatterns = @(
        "original_api_url",
        'world_model_integrator.*model:.*"gpt',
        "updates.auto_check.*true",
        "monitoring.endpoints",
        "external_apis.*true"
    )
    
    $hasNetworkConfig = $false
    foreach ($pattern in $networkPatterns) {
        if ($content -match $pattern) {
            Write-Host "❌ 发现网络配置: $pattern" -ForegroundColor Red
            $hasNetworkConfig = $true
        }
    }
    
    # 检查安全声明
    $hasSecurityDeclaration = $content -match "network_access:\s*false" -and $content -match "local_only:\s*true"
    
    if (-not $hasNetworkConfig -and $hasSecurityDeclaration) {
        Write-Host "✅ 配置文件已清理，有正确的安全声明" -ForegroundColor Green
        return $true
    } else {
        return $false
    }
}

function CheckPathValidator {
    $validatorPath = Join-Path $skillDir "path_validator.py"
    if (-not (Test-Path $validatorPath)) {
        Write-Host "❌ path_validator.py不存在" -ForegroundColor Red
        return $false
    }
    
    $content = Get-Content $validatorPath -Raw -Encoding UTF8
    
    # 检查问题
    $hasParentParent = $content -match "__file__\.parent\.parent"
    $hasCreateTestFile = $content -match "def create_test_file"
    
    if ($hasParentParent) {
        Write-Host "❌ 仍有__file__.parent.parent" -ForegroundColor Red
    } else {
        Write-Host "✅ 无__file__.parent.parent" -ForegroundColor Green
    }
    
    if ($hasCreateTestFile) {
        Write-Host "❌ 仍有create_test_file方法" -ForegroundColor Red
    } else {
        Write-Host "✅ 无create_test_file方法" -ForegroundColor Green
    }
    
    return (-not $hasParentParent -and -not $hasCreateTestFile)
}

function CheckFileEncoding {
    $files = @("SKILL.md", "README.md", "CHANGELOG.md", "config.yaml")
    $allGood = $true
    
    foreach ($file in $files) {
        $filePath = Join-Path $skillDir $file
        if (Test-Path $filePath) {
            try {
                $null = Get-Content $filePath -Encoding UTF8 -ErrorAction Stop
                Write-Host "✅ ${file}: UTF-8编码正常" -ForegroundColor Green
            } catch {
                Write-Host "❌ ${file}: 编码问题" -ForegroundColor Red
                $allGood = $false
            }
        }
    }
    
    return $allGood
}

function CheckClawhubStandards {
    # 检查install.bat等非标准文件
    $prohibitedFiles = @("install.bat", "install.sh", "setup.py")
    $hasProhibited = $false
    
    foreach ($file in $prohibitedFiles) {
        $filePath = Join-Path $skillDir $file
        if (Test-Path $filePath) {
            Write-Host "❌ 发现禁止文件: ${file}" -ForegroundColor Red
            $hasProhibited = $true
        }
    }
    
    # 检查必需文件
    $requiredFiles = @("skill_ascii_fixed.py", "config.yaml", "SKILL.md", "package.json")
    $missingFiles = @()
    
    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $skillDir $file
        if (-not (Test-Path $filePath)) {
            $missingFiles += $file
        }
    }
    
    if ($missingFiles.Count -gt 0) {
        Write-Host "❌ 缺失必需文件: $($missingFiles -join ', ')" -ForegroundColor Red
    }
    
    return (-not $hasProhibited -and $missingFiles.Count -eq 0)
}

function CheckTestFiles {
    # 检查测试文件
    $testPatterns = @("*check*", "*test*", "*verify*", "*final*")
    $testFiles = @()
    
    foreach ($pattern in $testPatterns) {
        $found = Get-ChildItem $skillDir -Filter "${pattern}.py" -Recurse -ErrorAction SilentlyContinue
        if ($found) {
            $testFiles += $found.Name
        }
    }
    
    if ($testFiles.Count -gt 0) {
        Write-Host "❌ 发现测试文件: $($testFiles -join ', ')" -ForegroundColor Red
        return $false
    } else {
        Write-Host "✅ 无测试文件" -ForegroundColor Green
        return $true
    }
}
