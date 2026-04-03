#!/usr/bin/env pwsh
<#
OpenClaw记忆备份脚本
建议设置为每日定时任务
#>

param(
    [string]$BackupType = "daily"  # daily, weekly, monthly
)

# 配置
$OpenClawWorkspace = "C:\Users\cqs10\.openclaw\workspace"
$BackupRoot = "D:\OpenClaw_TestingFramework"
$LogFile = "$BackupRoot\backup_log.txt"

# 创建日志函数
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Add-Content -Path $LogFile -Value $logEntry
    Write-Host $logEntry
}

# 开始备份
Write-Log "开始记忆备份: $BackupType"
Write-Log "工作空间: $OpenClawWorkspace"
Write-Log "备份位置: $BackupRoot"

# 检查目录
if (-not (Test-Path $OpenClawWorkspace)) {
    Write-Log "工作空间不存在" "ERROR"
    exit 1
}

if (-not (Test-Path $BackupRoot)) {
    Write-Log "备份目录不存在，正在创建" "WARN"
    New-Item -ItemType Directory -Path $BackupRoot -Force
}

# 创建备份目录结构
$backupDirs = @(
    "$BackupRoot\memory",
    "$BackupRoot\memory\daily",
    "$BackupRoot\memory\weekly", 
    "$BackupRoot\memory\monthly",
    "$BackupRoot\memory\archive"
)

foreach ($dir in $backupDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Log "创建目录: $dir"
    }
}

# 备份文件列表
$filesToBackup = @(
    "$OpenClawWorkspace\MEMORY.md",
    "$OpenClawWorkspace\memory\*.md"
)

# 执行备份
$backupDate = Get-Date -Format "yyyy-MM-dd"
$backupTime = Get-Date -Format "HHmmss"
$backupCount = 0
$errorCount = 0

foreach ($filePattern in $filesToBackup) {
    $files = Get-ChildItem -Path $filePattern -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        try {
            # 确定备份位置
            $backupPath = ""
            
            switch ($BackupType) {
                "daily" {
                    $backupPath = "$BackupRoot\memory\daily\$backupDate"
                    $fileName = "$($file.Name).$backupTime.bak"
                }
                "weekly" {
                    $weekNumber = Get-Date -UFormat %V
                    $backupPath = "$BackupRoot\memory\weekly\week-$backupDate-$weekNumber"
                    $fileName = $file.Name
                }
                "monthly" {
                    $month = Get-Date -Format "yyyy-MM"
                    $backupPath = "$BackupRoot\memory\monthly\$month"
                    $fileName = $file.Name
                }
                default {
                    $backupPath = "$BackupRoot\memory\archive"
                    $fileName = "$($file.Name).$backupDate.bak"
                }
            }
            
            # 创建备份目录
            if (-not (Test-Path $backupPath)) {
                New-Item -ItemType Directory -Path $backupPath -Force
            }
            
            # 复制文件
            $destPath = Join-Path $backupPath $fileName
            Copy-Item -Path $file.FullName -Destination $destPath -Force
            
            $backupCount++
            Write-Log "备份: $($file.Name) -> $destPath"
            
        } catch {
            $errorCount++
            Write-Log "备份失败: $($file.Name) - $_" "ERROR"
        }
    }
}

# 清理旧备份（保留策略）
function Cleanup-OldBackups {
    param([string]$Path, [int]$KeepDays)
    
    $cutoffDate = (Get-Date).AddDays(-$KeepDays)
    $oldFiles = Get-ChildItem -Path $Path -Filter "*.bak" -File | 
                Where-Object { $_.LastWriteTime -lt $cutoffDate }
    
    foreach ($file in $oldFiles) {
        try {
            Remove-Item -Path $file.FullName -Force
            Write-Log "清理旧备份: $($file.Name)" "INFO"
        } catch {
            Write-Log "清理失败: $($file.Name)" "WARN"
        }
    }
}

# 应用保留策略
switch ($BackupType) {
    "daily" {
        # 每日备份保留30天
        Cleanup-OldBackups -Path "$BackupRoot\memory\daily\*" -KeepDays 30
    }
    "weekly" {
        # 每周备份保留90天（约3个月）
        Cleanup-OldBackups -Path "$BackupRoot\memory\weekly\*" -KeepDays 90
    }
    "monthly" {
        # 每月备份保留365天（1年）
        Cleanup-OldBackups -Path "$BackupRoot\memory\monthly\*" -KeepDays 365
    }
}

# 生成备份报告
$report = @"
========================================
记忆备份报告
========================================
备份时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
备份类型: $BackupType
工作空间: $OpenClawWorkspace
备份位置: $BackupRoot

统计:
  成功备份: $backupCount 个文件
  备份失败: $errorCount 个文件
  总文件数: $(($backupCount + $errorCount))

备份位置:
  每日备份: $BackupRoot\memory\daily\$backupDate\
  每周备份: $BackupRoot\memory\weekly\*
  每月备份: $BackupRoot\memory\monthly\*
  归档备份: $BackupRoot\memory\archive\

保留策略:
  每日备份: 保留30天
  每周备份: 保留90天  
  每月备份: 保留365天
  归档备份: 永久保留

下次备份:
  每日: 明天同一时间
  每周: 下周日
  每月: 下个月最后一天
========================================
"@

# 保存报告
$reportPath = "$BackupRoot\memory\backup_report_$backupDate.txt"
$report | Out-File -FilePath $reportPath -Encoding UTF8

Write-Log "备份完成: $backupCount 成功, $errorCount 失败"
Write-Log "报告保存: $reportPath"

# 显示报告
Write-Host $report

exit $errorCount