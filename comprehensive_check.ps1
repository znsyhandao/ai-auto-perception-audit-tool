# AISkinX v1.0.3 全面功能和安全检查
param(
    [string]$SkillDir = "D:\openclaw\releases\AISkinX_v1.0.3"
)

function Write-Result {
    param($Status, $Message)
    if ($Status -eq "PASS") {
        Write-Host "✅ $Message" -ForegroundColor Green
    } elseif ($Status -eq "WARN") {
        Write-Host "⚠️  $Message" -ForegroundColor Yellow
    } else {
        Write-Host "❌ $Message" -ForegroundColor Red
    }
}

function Check-File-Exists {
    param($FilePath, $Description)
    if (Test-Path $FilePath) {
        Write-Result "PASS" "${Description} 存在"
        return $true
    } else {
        Write-Result "FAIL" "${Description} 缺失"
        return $false
    }
}

function Check-No-Network-Code {
    param($FilePath)
    if (-not (Test-Path $FilePath)) { return $false }
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $patterns = @("import requests", "import urllib", "import socket", "http://", "https://")
    
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            Write-Result "FAIL" "${FilePath} 包含网络代码: ${pattern}"
            return $false
        }
    }
    
    Write-Result "PASS" "${FilePath} 无网络代码"
    return $true
}

function Check-No-Dangerous-Functions {
    param($FilePath)
    if (-not (Test-Path $FilePath)) { return $false }
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $patterns = @("subprocess\.", "eval\(", "exec\(", "__import__\(")
    
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            Write-Result "FAIL" "${FilePath} 包含危险函数: ${pattern}"
            return $false
        }
    }
    
    Write-Result "PASS" "${FilePath} 无危险函数"
    return $true
}

function Check-Config-Network {
    param($FilePath)
    if (-not (Test-Path $FilePath)) { return $false }
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $patterns = @("original_api_url", 'world_model_integrator.*model:.*"gpt', "updates.auto_check.*true")
    
    foreach ($pattern in $patterns) {
        if ($content -match $pattern) {
            Write-Result "FAIL" "config.yaml 包含网络配置: ${pattern}"
            return $false
        }
    }
    
    # 检查安全声明
    $hasNetworkAccess = $content -match "network_access:\s*false"
    $hasLocalOnly = $content -match "local_only:\s*true"
    
    if ($hasNetworkAccess -and $hasLocalOnly) {
        Write-Result "PASS" "config.yaml 有正确的安全声明"
        return $true
    } else {
        Write-Result "FAIL" "config.yaml 缺少安全声明"
        return $false
    }
}

function Check-PathValidator {
    param($FilePath)
    if (-not (Test-Path $FilePath)) { return $false }
    
    $content = Get-Content $FilePath -Raw -Encoding UTF8
    $hasParentParent = $content -match "__file__\.parent\.parent"
    $hasCreateTestFile = $content -match "def create_test_file"
    
    if ($hasParentParent) {
        Write-Result "FAIL" "path_validator.py 仍有__file__.parent.parent"
        return $false
    }
    
    if ($hasCreateTestFile) {
        Write-Result "FAIL" "path_validator.py 仍有create_test_file方法"
        return $false
    }
    
    Write-Result "PASS" "path_validator.py 设计正确"
    return $true
}

function Check-Documentation-Encoding {
    param($FilePath)
    if (-not (Test-Path $FilePath)) { return $false }
    
    try {
        $null = Get-Content $FilePath -Encoding UTF8 -ErrorAction Stop
        Write-Result "PASS" "${FilePath} UTF-8编码正常"
        return $true
    } catch {
        Write-Result "FAIL" "${FilePath} 编码问题"
        return $false
    }
}

# 主检查流程
Write-Host "🔍 AISkinX v1.0.3 全面功能和安全检查" -ForegroundColor Cyan
Write-Host "=" * 80
Write-Host "目标：确保ClawHub审核100%通过，无任何问题！" -ForegroundColor Yellow
Write-Host "检查目录: $SkillDir" -ForegroundColor Gray
Write-Host "=" * 80

# 检查结果汇总
$results = @()

# 阶段1: 必需文件检查
Write-Host "`n📁 阶段1: 必需文件检查" -ForegroundColor Cyan
Write-Host "-" * 40

$requiredFiles = @(
    @{Path="skill_ascii_fixed.py"; Desc="主技能文件"},
    @{Path="config.yaml"; Desc="配置文件"},
    @{Path="SKILL.md"; Desc="技能文档"},
    @{Path="package.json"; Desc="包配置"},
    @{Path="README.md"; Desc="项目说明"},
    @{Path="CHANGELOG.md"; Desc="更新日志"},
    @{Path="requirements.txt"; Desc="依赖列表"},
    @{Path="path_validator.py"; Desc="路径验证器"},
    @{Path="api_utils_fixed.py"; Desc="API工具"}
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $SkillDir $file.Path
    $exists = Check-File-Exists $fullPath $file.Desc
    $results += @{Check="文件存在"; File=$file.Path; Passed=$exists}
}

# 阶段2: 禁止文件检查
Write-Host "`n🚫 阶段2: 禁止文件检查" -ForegroundColor Cyan
Write-Host "-" * 40

$prohibitedFiles = @("install.bat", "install.sh", "setup.py")
$hasProhibited = $false

foreach ($file in $prohibitedFiles) {
    $fullPath = Join-Path $SkillDir $file
    if (Test-Path $fullPath) {
        Write-Result "FAIL" "发现禁止文件: ${file}"
        $hasProhibited = $true
    }
}

if (-not $hasProhibited) {
    Write-Result "PASS" "无禁止文件"
}
$results += @{Check="禁止文件"; File="所有"; Passed=(-not $hasProhibited)}

# 阶段3: 代码安全检查
Write-Host "`n🔒 阶段3: 代码安全检查" -ForegroundColor Cyan
Write-Host "-" * 40

$pythonFiles = Get-ChildItem $SkillDir -Filter "*.py" -Recurse -ErrorAction SilentlyContinue

# 3.1 网络代码检查
Write-Host "3.1 网络代码检查..." -ForegroundColor White
$allNoNetwork = $true
foreach ($file in $pythonFiles) {
    $noNetwork = Check-No-Network-Code $file.FullName
    $allNoNetwork = $allNoNetwork -and $noNetwork
}
$results += @{Check="网络代码"; File="所有Python文件"; Passed=$allNoNetwork}

# 3.2 危险函数检查
Write-Host "`n3.2 危险函数检查..." -ForegroundColor White
$allNoDangerous = $true
foreach ($file in $pythonFiles) {
    $noDangerous = Check-No-Dangerous-Functions $file.FullName
    $allNoDangerous = $allNoDangerous -and $noDangerous
}
$results += @{Check="危险函数"; File="所有Python文件"; Passed=$allNoDangerous}

# 3.3 PathValidator检查
Write-Host "`n3.3 PathValidator检查..." -ForegroundColor White
$validatorPath = Join-Path $SkillDir "path_validator.py"
$validatorOk = Check-PathValidator $validatorPath
$results += @{Check="PathValidator设计"; File="path_validator.py"; Passed=$validatorOk}

# 阶段4: 配置检查
Write-Host "`n⚙️ 阶段4: 配置检查" -ForegroundColor Cyan
Write-Host "-" * 40

$configPath = Join-Path $SkillDir "config.yaml"
$configOk = Check-Config-Network $configPath
$results += @{Check="配置网络"; File="config.yaml"; Passed=$configOk}

# 阶段5: 文档检查
Write-Host "`n📄 阶段5: 文档检查" -ForegroundColor Cyan
Write-Host "-" * 40

$docFiles = @("SKILL.md", "README.md", "CHANGELOG.md", "config.yaml")
$allEncodingOk = $true

foreach ($file in $docFiles) {
    $fullPath = Join-Path $SkillDir $file
    $encodingOk = Check-Documentation-Encoding $fullPath
    $allEncodingOk = $allEncodingOk -and $encodingOk
}
$results += @{Check="文档编码"; File="所有文档文件"; Passed=$allEncodingOk}

# 阶段6: 功能检查
Write-Host "`n🔧 阶段6: 功能检查" -ForegroundColor Cyan
Write-Host "-" * 40

# 6.1 检查skill_ascii_fixed.py结构
Write-Host "6.1 主技能文件结构检查..." -ForegroundColor White
$skillPath = Join-Path $SkillDir "skill_ascii_fixed.py"
if (Test-Path $skillPath) {
    $content = Get-Content $skillPath -Raw -Encoding UTF8
    $hasClass = $content -match "class SkincareAISkill"
    $hasHandle = $content -match "def handle\("
    
    if ($hasClass -and $hasHandle) {
        Write-Result "PASS" "skill_ascii_fixed.py 结构完整"
        $results += @{Check="技能结构"; File="skill_ascii_fixed.py"; Passed=$true}
    } else {
        Write-Result "FAIL" "skill_ascii_fixed.py 结构不完整"
        $results += @{Check="技能结构"; File="skill_ascii_fixed.py"; Passed=$false}
    }
}

# 6.2 检查package.json
Write-Host "`n6.2 package.json检查..." -ForegroundColor White
$packagePath = Join-Path $SkillDir "package.json"
if (Test-Path $packagePath) {
    try {
        $content = Get-Content $packagePath -Raw -Encoding UTF8
        $json = $content | ConvertFrom-Json
        
        if ($json.name -and $json.version -and $json.description) {
            Write-Result "PASS" "package.json 结构完整"
            Write-Host "   名称: $($json.name)" -ForegroundColor Gray
            Write-Host "   版本: $($json.version)" -ForegroundColor Gray
            Write-Host "   描述: $($json.description)" -ForegroundColor Gray
            $results += @{Check="包配置"; File="package.json"; Passed=$true}
        } else {
            Write-Result "FAIL" "package.json 缺少必需字段"
            $results += @{Check="包配置"; File="package.json"; Passed=$false}
        }
    } catch {
        Write-Result "FAIL" "package.json JSON解析错误"
        $results += @{Check="包配置"; File="package.json"; Passed=$false}
    }
}

# 总结报告
Write-Host "`n📊 检查结果总结" -ForegroundColor Cyan
Write-Host "=" * 80

$totalChecks = $results.Count
$passedChecks = ($results | Where-Object { $_.Passed }).Count
$failedChecks = $totalChecks - $passedChecks

Write-Host "总检查项: $totalChecks" -ForegroundColor White
Write-Host "通过: $passedChecks" -ForegroundColor $(if ($passedChecks -eq $totalChecks) { "Green" } else { "White" })
Write-Host "失败: $failedChecks" -ForegroundColor $(if ($failedChecks -eq 0) { "Green" } else { "Red" })

# 显示失败项
if ($failedChecks -gt 0) {
    Write-Host "`n❌ 失败项详情:" -ForegroundColor Red
    foreach ($result in $results | Where-Object { -not $_.Passed }) {
        Write-Host "  - $($result.Check): $($result.File)" -ForegroundColor White
    }
}

# 最终结论
Write-Host "`n🎯 最终结论" -ForegroundColor Cyan
Write-Host "=" * 80

if ($failedChecks -eq 0) {
    Write-Host "✅ AISkinX v1.0.3 通过所有检查！" -ForegroundColor Green
    Write-Host "   可以安全提交到ClawHub，预计审核100%通过！" -ForegroundColor Green
    Write-Host "   同样的错误不会犯第二次！" -ForegroundColor Green
} else {
    Write-Host "❌ AISkinX v1.0.3 有 $failedChecks 个问题需要修复" -ForegroundColor Red
    Write-Host "   请修复所有问题后再提交到ClawHub" -ForegroundColor Red
}

# 返回退出码
if ($failedChecks -eq 0) {
    exit 0
} else {
    exit 1
}