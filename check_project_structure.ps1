# check_project_structure.ps1
# 检查项目结构是否符合标准化要求
# 基于2026-03-27 AISleepGen项目结构混乱教训

param(
    [string]$ProjectDir,
    [string]$SkillName = "openclaw_skill"
)

Write-Host "=== 项目结构检查 ===" -ForegroundColor Cyan
Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "项目目录: $ProjectDir"
Write-Host "技能名称: $SkillName"
Write-Host ""

# 检查1: 项目目录是否存在
if (-not (Test-Path $ProjectDir)) {
    Write-Host "[错误] 项目目录不存在: $ProjectDir" -ForegroundColor Red
    exit 1
}

# 检查2: 技能目录是否存在
$skillDir = Join-Path $ProjectDir $SkillName
if (-not (Test-Path $skillDir)) {
    Write-Host "[警告] 技能目录不存在: $skillDir" -ForegroundColor Yellow
    Write-Host "  建议: 创建标准化的技能目录结构"
}

# 检查3: 项目根目录文件夹数量
$rootFolders = Get-ChildItem -Path $ProjectDir -Directory | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "检查3: 项目根目录文件夹数量" -ForegroundColor White
Write-Host "  发现: $rootFolders 个文件夹"
if ($rootFolders -gt 20) {
    Write-Host "  [警告] 文件夹数量过多 ($rootFolders > 20)" -ForegroundColor Yellow
    Write-Host "  建议: 整理项目结构，减少不必要的文件夹"
} else {
    Write-Host "  [OK] 文件夹数量合理" -ForegroundColor Green
}

# 检查4: 必需文件检查
Write-Host "`n检查4: 技能必需文件" -ForegroundColor White
$requiredFiles = @(
    "skill.py",
    "config.yaml", 
    "SKILL.md",
    "package.json"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $skillDir $file
    if (Test-Path $filePath) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [缺失] $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

# 检查5: 禁止文件检查
Write-Host "`n检查5: 禁止文件检查" -ForegroundColor White
$prohibitedExtensions = @(".ps1", ".bat", ".exe", ".dll", ".backup", ".pyc")
$prohibitedFiles = Get-ChildItem -Path $skillDir -File | Where-Object {
    $prohibitedExtensions -contains $_.Extension
}

if ($prohibitedFiles.Count -gt 0) {
    Write-Host "  [警告] 发现禁止文件 ($($prohibitedFiles.Count) 个)" -ForegroundColor Yellow
    foreach ($file in $prohibitedFiles) {
        Write-Host "    - $($file.Name)" -ForegroundColor Yellow
    }
    Write-Host "  建议: 发布前移除这些文件"
} else {
    Write-Host "  [OK] 无禁止文件" -ForegroundColor Green
}

# 检查6: 发布文件夹检查
Write-Host "`n检查6: 发布文件夹结构" -ForegroundColor White
$releasesDir = "D:\openclaw\releases"
if (Test-Path $releasesDir) {
    $projectName = Split-Path $ProjectDir -Leaf
    $releaseFolders = Get-ChildItem -Path $releasesDir -Directory | Where-Object { $_.Name -like "*$projectName*" }
    
    if ($releaseFolders.Count -gt 0) {
        Write-Host "  [OK] 发现发布文件夹 ($($releaseFolders.Count) 个)" -ForegroundColor Green
        foreach ($folder in $releaseFolders) {
            Write-Host "    - $($folder.Name)" -ForegroundColor Green
        }
    } else {
        Write-Host "  [警告] 未找到发布文件夹" -ForegroundColor Yellow
        Write-Host "  建议: 在 $releasesDir 创建标准发布文件夹"
    }
} else {
    Write-Host "  [警告] 发布文件夹不存在: $releasesDir" -ForegroundColor Yellow
    Write-Host "  建议: 创建标准发布文件夹结构"
}

# 总结报告
Write-Host "`n=== 检查总结 ===" -ForegroundColor Cyan

$issues = @()
if ($rootFolders -gt 20) { $issues += "文件夹数量过多" }
if ($missingFiles.Count -gt 0) { $issues += "缺失必需文件: $($missingFiles -join ', ')" }
if ($prohibitedFiles.Count -gt 0) { $issues += "存在禁止文件" }

if ($issues.Count -eq 0) {
    Write-Host "[通过] 项目结构良好" -ForegroundColor Green
} else {
    Write-Host "[需要改进] 发现 $($issues.Count) 个问题" -ForegroundColor Yellow
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Yellow
    }
    
    Write-Host "`n改进建议:" -ForegroundColor White
    Write-Host "1. 整理项目结构，减少不必要的文件夹"
    Write-Host "2. 确保所有必需文件存在"
    Write-Host "3. 发布前移除禁止文件"
    Write-Host "4. 使用标准化发布文件夹: $releasesDir"
}

# 生成改进建议文件
$suggestionsFile = Join-Path $ProjectDir "project_structure_suggestions.md"
$suggestions = @"
# 项目结构改进建议
## 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
## 项目: $ProjectDir

## 发现的问题
$($issues -join "`n")

## 具体改进措施

### 1. 整理文件夹结构
- 当前文件夹数量: $rootFolders (建议: < 20)
- 建议合并相关功能的文件夹
- 移除临时文件和缓存目录

### 2. 完善技能文件
$($missingFiles | ForEach-Object { "- 创建缺失文件: $_" })

### 3. 清理禁止文件
$($prohibitedFiles | ForEach-Object { "- 移除: $($_.Name)" })

### 4. 建立发布流程
- 创建发布文件夹: $releasesDir\$((Split-Path $ProjectDir -Leaf))_v版本号
- 创建标准化发布包
- 建立自动化发布脚本

### 5. 基于AISkinX经验
- 应用具体化、可验证、自动化、文档化四个原则
- 创建永久改进记录
- 建立自动化检查工具

## 参考文档
- [PROJECT_STRUCTURE_LESSON.md](D:\OpenClaw_TestingFramework\PROJECT_STRUCTURE_LESSON.md)
- [TESTING_FRAMEWORK.md](D:\OpenClaw_TestingFramework\TESTING_FRAMEWORK.md)
"@

Set-Content -Path $suggestionsFile -Value $suggestions
Write-Host "`n改进建议已保存到: $suggestionsFile" -ForegroundColor Cyan