# 🔍 ClawHub规范检查脚本
# 基于2026-03-24 install.bat重复错误教训
# 用途：检查技能发布包是否符合ClawHub规范

param(
    [string]$SkillDir = ".",
    [switch]$Fix = $false,
    [switch]$Verbose = $false
)

function Write-Info {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "ℹ️  $Message" -ForegroundColor Gray
    }
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Section {
    param([string]$Title)
    Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
    Write-Host "🔍 $Title" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
}

# 主函数
function Main {
    Write-Host "🚀 ClawHub规范检查" -ForegroundColor Cyan
    Write-Host "版本: 1.0.0 (基于2026-03-24 install.bat教训)" -ForegroundColor Gray
    Write-Host "检查目录: $SkillDir" -ForegroundColor Gray
    Write-Host "修复模式: $Fix" -ForegroundColor Gray
    Write-Host "详细模式: $Verbose" -ForegroundColor Gray
    
    # 检查目录是否存在
    if (-not (Test-Path $SkillDir)) {
        Write-Error "目录不存在: $SkillDir"
        exit 1
    }
    
    # 切换到目录
    $originalDir = Get-Location
    try {
        Set-Location $SkillDir
        Write-Info "切换到目录: $(Get-Location)"
        
        # 运行所有检查
        $results = @{
            RequiredFiles = Check-RequiredFiles
            ProhibitedFiles = Check-ProhibitedFiles
            FileTypes = Check-FileTypes
            PackageJson = Check-PackageJson
            SkillStructure = Check-SkillStructure
            InstallInstructions = Check-InstallInstructions
        }
        
        # 输出总结
        Write-Summary $results
        
        # 如果需要修复
        if ($Fix) {
            Apply-Fixes $results
        }
        
    } finally {
        Set-Location $originalDir
    }
}

# 检查必需文件
function Check-RequiredFiles {
    Write-Section "必需文件检查"
    
    $requiredFiles = @(
        @{Name = "skill.py"; Description = "主技能文件"},
        @{Name = "config.yaml"; Description = "配置文件"},
        @{Name = "SKILL.md"; Description = "技能文档"},
        @{Name = "package.json"; Description = "ClawHub包配置"}
    )
    
    $missingFiles = @()
    $foundFiles = @()
    
    foreach ($file in $requiredFiles) {
        $fileName = $file.Name
        $description = $file.Description
        
        # 尝试查找文件（可能名称不同）
        $found = $false
        $actualFile = $null
        
        # 检查确切文件名
        if (Test-Path $fileName) {
            $found = $true
            $actualFile = $fileName
        } else {
            # 检查可能的变体
            $possibleNames = @()
            if ($fileName -eq "skill.py") {
                $possibleNames = @("skill_ascii_fixed.py", "main.py", "skill_fixed.py")
            } elseif ($fileName -eq "config.yaml") {
                $possibleNames = @("config.yml", "configuration.yaml")
            } elseif ($fileName -eq "SKILL.md") {
                $possibleNames = @("README.md", "DOCUMENTATION.md")
            }
            
            foreach ($possibleName in $possibleNames) {
                if (Test-Path $possibleName) {
                    $found = $true
                    $actualFile = $possibleName
                    break
                }
            }
        }
        
        if ($found) {
            Write-Success "$description: $actualFile"
            $foundFiles += @{Name = $fileName; Actual = $actualFile; Description = $description}
        } else {
            Write-Error "$description: $fileName (缺失)"
            $missingFiles += @{Name = $fileName; Description = $description}
        }
    }
    
    return @{
        Missing = $missingFiles
        Found = $foundFiles
        Passed = ($missingFiles.Count -eq 0)
    }
}

# 检查禁止文件
function Check-ProhibitedFiles {
    Write-Section "禁止文件检查"
    
    $prohibitedPatterns = @(
        @{Pattern = "install.bat"; Description = "Windows安装脚本"},
        @{Pattern = "install.sh"; Description = "Linux/macOS安装脚本"},
        @{Pattern = "setup.py"; Description = "Python安装脚本"},
        @{Pattern = "*.exe"; Description = "可执行文件"},
        @{Pattern = "*.dll"; Description = "动态链接库"},
        @{Pattern = "*.so"; Description = "共享库"},
        @{Pattern = "*.bin"; Description = "二进制文件"}
    )
    
    $foundFiles = @()
    
    foreach ($item in $prohibitedPatterns) {
        $pattern = $item.Pattern
        $description = $item.Description
        
        $files = Get-ChildItem -Path . -Filter $pattern -Recurse -ErrorAction SilentlyContinue | 
                 Where-Object { -not $_.PSIsContainer }
        
        if ($files) {
            foreach ($file in $files) {
                $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "")
                Write-Error "$description: $relativePath"
                $foundFiles += @{
                    Path = $relativePath
                    Description = $description
                    Pattern = $pattern
                }
            }
        } else {
            Write-Success "无 $description"
        }
    }
    
    return @{
        Found = $foundFiles
        Passed = ($foundFiles.Count -eq 0)
    }
}

# 检查文件类型
function Check-FileTypes {
    Write-Section "文件类型检查"
    
    $allowedExtensions = @(
        ".py", ".yaml", ".yml", ".json", 
        ".md", ".txt", ".rst", 
        ".png", ".jpg", ".jpeg", ".gif", ".svg",  # 图像文件
        ".csv", ".tsv"  # 数据文件
    )
    
    $allFiles = Get-ChildItem -Path . -File -Recurse | 
                Where-Object { -not $_.PSIsContainer }
    
    $unexpectedFiles = @()
    
    foreach ($file in $allFiles) {
        $extension = $file.Extension.ToLower()
        $relativePath = $file.FullName.Replace((Get-Location).Path + "\", "")
        
        if ($extension -notin $allowedExtensions) {
            # 检查是否是特殊文件（如.gitignore等）
            $specialFiles = @(".gitignore", ".gitattributes", ".editorconfig", ".pre-commit-config.yaml")
            if ($file.Name -notin $specialFiles) {
                Write-Warning "非常见文件类型: $relativePath ($extension)"
                $unexpectedFiles += @{
                    Path = $relativePath
                    Extension = $extension
                }
            } else {
                Write-Info "特殊文件: $relativePath"
            }
        } else {
            Write-Info "允许的文件: $relativePath ($extension)"
        }
    }
    
    if ($unexpectedFiles.Count -eq 0) {
        Write-Success "所有文件类型符合规范"
    }
    
    return @{
        Unexpected = $unexpectedFiles
        Passed = ($unexpectedFiles.Count -eq 0)
    }
}

# 检查package.json
function Check-PackageJson {
    Write-Section "package.json检查"
    
    if (-not (Test-Path "package.json")) {
        Write-Error "package.json文件缺失"
        return @{Passed = $false; Issues = @("文件缺失")}
    }
    
    try {
        $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
        $issues = @()
        
        # 检查必需字段
        $requiredFields = @("name", "version", "description", "author", "license", "main")
        foreach ($field in $requiredFields) {
            if (-not $packageJson.PSObject.Properties[$field]) {
                $issues += "缺少必需字段: $field"
                Write-Error "缺少必需字段: $field"
            } else {
                Write-Success "字段存在: $field = $($packageJson.$field)"
            }
        }
        
        # 检查权限声明
        if (-not $packageJson.permissions) {
            $issues += "缺少permissions字段"
            Write-Warning "建议添加permissions字段"
        } else {
            Write-Success "权限声明: $($packageJson.permissions -join ', ')"
        }
        
        # 检查安全声明
        if (-not $packageJson.security) {
            $issues += "缺少security字段"
            Write-Warning "建议添加security字段"
        } else {
            Write-Success "安全声明存在"
        }
        
        return @{
            Passed = ($issues.Count -eq 0)
            Issues = $issues
            Package = $packageJson
        }
        
    } catch {
        Write-Error "package.json解析失败: $_"
        return @{Passed = $false; Issues = @("解析失败: $_")}
    }
}

# 检查技能结构
function Check-SkillStructure {
    Write-Section "技能结构检查"
    
    $issues = @()
    
    # 检查是否有__pycache__目录
    if (Test-Path "__pycache__") {
        $issues += "发现__pycache__目录"
        Write-Error "发现__pycache__目录，应该删除"
    } else {
        Write-Success "无__pycache__目录"
    }
    
    # 检查是否有.venv目录
    if (Test-Path ".venv") {
        $issues += "发现.venv目录"
        Write-Error "发现.venv目录，应该删除"
    } else {
        Write-Success "无.venv目录"
    }
    
    # 检查是否有测试目录
    if (Test-Path "tests") {
        Write-Warning "发现tests目录，ClawHub可能会扫描"
    }
    
    # 检查文件数量
    $fileCount = (Get-ChildItem -File -Recurse | Measure-Object).Count
    Write-Info "总文件数: $fileCount"
    
    if ($fileCount -gt 50) {
        Write-Warning "文件数量较多 ($fileCount)，考虑简化"
    }
    
    return @{
        Passed = ($issues.Count -eq 0)
        Issues = $issues
        FileCount = $fileCount
    }
}

# 检查安装说明
function Check-InstallInstructions {
    Write-Section "安装说明检查"
    
    $skillMdPath = "SKILL.md"
    if (-not (Test-Path $skillMdPath)) {
        $skillMdPath = "README.md"
    }
    
    if (-not (Test-Path $skillMdPath)) {
        Write-Warning "未找到SKILL.md或README.md"
        return @{Passed = $false; Issues = @("未找到安装说明文档")}
    }
    
    $content = Get-Content $skillMdPath -Raw
    $issues = @()
    
    # 检查是否包含openclaw安装命令
    if ($content -notmatch "openclaw skill install") {
        $issues += "安装说明未包含'openclaw skill install'"
        Write-Warning "建议添加openclaw skill install命令"
    } else {
        Write-Success "包含openclaw安装命令"
    }
    
    # 检查是否包含install.bat
    if ($content -match "install\.bat") {
        $issues += "文档中提到了install.bat（已过时）"
        Write-Error "文档中提到了install.bat，应该使用openclaw命令"
    }
    
    return @{
        Passed = ($issues.Count -eq 0)
        Issues = $issues
        Document = $skillMdPath
    }
}

# 输出总结
function Write-Summary {
    param($results)
    
    Write-Section "检查结果总结"
    
    $totalChecks = $results.Count
    $passedChecks = ($results.Values | Where-Object { $_.Passed }).Count
    
    Write-Host "📊 检查统计:" -ForegroundColor Cyan
    Write-Host "  总检查项: $totalChecks" -ForegroundColor White
    Write-Host "  通过项: $passedChecks" -ForegroundColor Green
    Write-Host "  失败项: $($totalChecks - $passedChecks)" -ForegroundColor Red
    
    # 详细结果
    foreach ($key in $results.Keys) {
        $result = $results[$key]
        $status = if ($result.Passed) { "✅" } else { "❌" }
        Write-Host "  $status $key" -ForegroundColor $(if ($result.Passed) { "Green" } else { "Red" })
    }
    
    # 总体评价
    if ($passedChecks -eq $totalChecks) {
        Write-Host "`n🎉 所有检查通过！符合ClawHub规范。" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  部分检查未通过，需要修复。" -ForegroundColor Yellow
        
        # 显示具体问题
        foreach ($key in $results.Keys) {
            $result = $results[$key]
            if (-not $result.Passed -and $result.Issues) {
                Write-Host "  $key 问题:" -ForegroundColor Yellow
                foreach ($issue in $result.Issues) {
                    Write-Host "    - $issue" -ForegroundColor White
                }
            }
        }
        
        Write-Host "`n💡 修复建议:" -ForegroundColor Cyan
        Write-Host "  1. 运行检查时添加 -Fix 参数尝试自动修复" -ForegroundColor White
        Write-Host "  2. 手动修复上述问题" -ForegroundColor White
        Write-Host "  3. 重新运行检查验证修复" -ForegroundColor White
    }
}

# 应用修复
function Apply-Fixes {
    param($results)
    
    Write-Section "应用修复"
    
    # 修复禁止文件
    $prohibitedResult = $results.ProhibitedFiles
    if (-not $prohibitedResult.Passed -and $prohibitedResult.Found) {
        Write-Host "🗑️ 删除禁止文件..." -ForegroundColor Yellow
        foreach ($file in $prohibitedResult.Found) {
            $path = $file.Path
            if (Test-Path $path) {
                Remove-Item -Path $path -Force -ErrorAction SilentlyContinue
                if (Test-Path $path) {
                    Write-Error "删除失败: $path"
                } else {
                    Write-Success "已删除: $path"
                }
            }
        }
    }
    
    # 修复package.json
    $packageResult = $results.PackageJson
    if (-not $packageResult.Passed -and $packageResult.Package) {
        Write-Host "📝 修复package.json..." -ForegroundColor Yellow
        
        $package = $packageResult.Package
        
        # 确保有permissions字段
        if (-not $package.permissions) {
            $package | Add-Member -NotePropertyName "permissions" -NotePropertyValue @("filesystem") -Force
            Write-Success "添加permissions字段"
        }
        
        # 确保有security字段
        if (-not $package.security) {
            $package | Add-Member -NotePropertyName "security" -NotePropertyValue @{
                network_access = $false
                local_only = $true
                privacy_friendly = $true
            } -Force
            Write-Success "添加security字段"
        }
        
        # 保存
        $package | ConvertTo-Json -Depth 10 | Out-File "package.json" -Encoding UTF8
        Write-Success "package.json已更新"
    }
    
    Write-Host "`n🔧 修复完成，请重新运行检查验证。" -ForegroundColor Green
}

# 运行主函数
Main