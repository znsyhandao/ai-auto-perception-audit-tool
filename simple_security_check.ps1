# 简化版安全检查 - PowerShell版本
param(
    [Parameter(Mandatory=$true)]
    [string]$Directory
)

function Write-Section {
    param([string]$Title, [int]$Level=1)
    if ($Level -eq 1) {
        Write-Host "`n" + ("="*60) -ForegroundColor Cyan
        Write-Host "🔍 $Title" -ForegroundColor Cyan
        Write-Host ("="*60) -ForegroundColor Cyan
    } else {
        Write-Host "`n📋 $Title" -ForegroundColor Yellow
        Write-Host ("-"*40) -ForegroundColor Yellow
    }
}

function Test-FileEncoding {
    param([string]$FilePath)
    try {
        $content = Get-Content $FilePath -Encoding UTF8 -TotalCount 10 -ErrorAction Stop
        if ($content -match "[一-龥]") {
            return $true, "UTF-8正常，中文显示正确"
        } else {
            $size = (Get-Item $FilePath).Length
            return $true, "UTF-8编码，无中文字符 (${size}字节)"
        }
    } catch [System.Text.DecoderFallbackException] {
        return $false, "编码错误，不是有效的UTF-8"
    } catch {
        return $false, "读取失败: $_"
    }
}

function Test-ConfigYaml {
    param([string]$FilePath)
    try {
        $content = Get-Content $FilePath -Raw -ErrorAction Stop
        
        # 检查危险配置
        $dangerousPatterns = @(
            "original_api_url",
            "world_model_integrator", 
            'model: "gpt-',
            "updates.auto_check: true",
            "external_apis",
            "http://",
            "https://"
        )
        
        foreach ($pattern in $dangerousPatterns) {
            if ($content -match $pattern) {
                return $false, "发现危险配置: $pattern"
            }
        }
        
        # 检查安全声明
        if ($content -match "network_access: false" -and $content -match "local_only: true") {
            return $true, "config.yaml干净，有安全声明"
        } else {
            return $false, "缺少安全声明"
        }
    } catch {
        return $false, "读取失败: $_"
    }
}

function Test-NetworkCode {
    param([string]$Directory)
    $networkPatterns = @(
        "import requests",
        "import urllib",
        "import socket",
        "import http.client",
        "requests.",
        "urllib.",
        "http.client.",
        "socket."
    )
    
    $found = $false
    Get-ChildItem $Directory -Recurse -Filter *.py | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        foreach ($pattern in $networkPatterns) {
            if ($content -match $pattern) {
                Write-Host "❌ $($_.Name): 发现网络代码 - $pattern" -ForegroundColor Red
                $found = $true
            }
        }
    }
    
    if (-not $found) {
        return $true, "无网络代码"
    } else {
        return $false, "发现网络代码"
    }
}

function Test-DangerousFunctions {
    param([string]$Directory)
    $dangerousPatterns = @(
        "subprocess.",
        "os.system(",
        "eval(",
        "exec(",
        "__import__("
    )
    
    $found = $false
    Get-ChildItem $Directory -Recurse -Filter *.py | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        foreach ($pattern in $dangerousPatterns) {
            if ($content -match [regex]::Escape($pattern)) {
                Write-Host "❌ $($_.Name): 发现危险函数 - $pattern" -ForegroundColor Red
                $found = $true
            }
        }
    }
    
    if (-not $found) {
        return $true, "无危险函数"
    } else {
        return $false, "发现危险函数"
    }
}

# 主检查
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "🔍 简化版安全检查 - PowerShell版本" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "检查目录: $Directory" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

$results = @()

# 1. 文件编码检查
Write-Section "1. 文件编码检查"
$files = @("skill.py", "README.md", "SKILL.md", "CHANGELOG.md", "config.yaml")
foreach ($file in $files) {
    $path = Join-Path $Directory $file
    if (Test-Path $path) {
        $passed, $message = Test-FileEncoding $path
        if ($passed) {
            Write-Host "✅ $file: $message" -ForegroundColor Green
        } else {
            Write-Host "❌ $file: $message" -ForegroundColor Red
        }
        $results += @{File=$file; Passed=$passed}
    } else {
        Write-Host "⚠️  $file: 文件不存在" -ForegroundColor Yellow
    }
}

# 2. config.yaml检查
Write-Section "2. config.yaml安全检查"
$configPath = Join-Path $Directory "config.yaml"
if (Test-Path $configPath) {
    $passed, $message = Test-ConfigYaml $configPath
    if ($passed) {
        Write-Host "✅ $message" -ForegroundColor Green
    } else {
        Write-Host "❌ $message" -ForegroundColor Red
    }
    $results += @{File="config.yaml"; Passed=$passed}
} else {
    Write-Host "❌ config.yaml文件不存在" -ForegroundColor Red
}

# 3. 网络代码检查
Write-Section "3. 网络代码检查"
$passed, $message = Test-NetworkCode $Directory
if ($passed) {
    Write-Host "✅ $message" -ForegroundColor Green
} else {
    Write-Host "❌ $message" -ForegroundColor Red
}
$results += @{File="网络代码"; Passed=$passed}

# 4. 危险函数检查
Write-Section "4. 危险函数检查"
$passed, $message = Test-DangerousFunctions $Directory
if ($passed) {
    Write-Host "✅ $message" -ForegroundColor Green
} else {
    Write-Host "❌ $message" -ForegroundColor Red
}
$results += @{File="危险函数"; Passed=$passed}

# 结果汇总
Write-Section "📊 检查结果汇总"
$passedCount = ($results | Where-Object { $_.Passed -eq $true }).Count
$totalCount = $results.Count

foreach ($result in $results) {
    $status = if ($result.Passed) { "✅ 通过" } else { "❌ 失败" }
    Write-Host "$status - $($result.File)"
}

Write-Host "`n🎯 总体结果: $passedCount/$totalCount 通过" -ForegroundColor Cyan

if ($passedCount -eq $totalCount) {
    Write-Host "`n🎉 🎉 🎉 所有检查通过！可以安全发布 🎉 🎉 🎉" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ ❌ ❌ 检查未通过，需要修复问题 ❌ ❌ ❌" -ForegroundColor Red
    exit 1
}
