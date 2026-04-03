#!/usr/bin/env pwsh
<#
设置OpenClaw记忆备份计划任务
#>

# 配置
$BackupScript = "D:\OpenClaw_TestingFramework\backup_memory.ps1"
$TaskName = "OpenClawMemoryBackup"

# 检查脚本是否存在
if (-not (Test-Path $BackupScript)) {
    Write-Host "❌ 备份脚本不存在: $BackupScript"
    exit 1
}

Write-Host "🔧 设置OpenClaw记忆备份计划任务"
Write-Host "备份脚本: $BackupScript"
Write-Host "任务名称: $TaskName"
Write-Host ""

# 1. 创建每日备份任务（晚上10点）
Write-Host "📅 创建每日备份任务（22:00）..."
$dailyAction = New-ScheduledTaskAction -Execute "PowerShell" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BackupScript`" -BackupType daily"
$dailyTrigger = New-ScheduledTaskTrigger -Daily -At "22:00"
$dailySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName "$TaskName-Daily" -Action $dailyAction -Trigger $dailyTrigger -Settings $dailySettings -Description "OpenClaw每日记忆备份" -Force
    Write-Host "✅ 每日备份任务创建成功"
} catch {
    Write-Host "❌ 每日备份任务创建失败: $_"
}

# 2. 创建每周备份任务（周日晚上11点）
Write-Host "`n📅 创建每周备份任务（周日23:00）..."
$weeklyAction = New-ScheduledTaskAction -Execute "PowerShell" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BackupScript`" -BackupType weekly"
$weeklyTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "23:00"
$weeklySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

try {
    Register-ScheduledTask -TaskName "$TaskName-Weekly" -Action $weeklyAction -Trigger $weeklyTrigger -Settings $weeklySettings -Description "OpenClaw每周记忆备份" -Force
    Write-Host "✅ 每周备份任务创建成功"
} catch {
    Write-Host "❌ 每周备份任务创建失败: $_"
}

# 3. 创建每月备份任务（每月最后一天晚上11:30）
Write-Host "`n📅 创建每月备份任务（每月最后一天23:30）..."
$monthlyAction = New-ScheduledTaskAction -Execute "PowerShell" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$BackupScript`" -BackupType monthly"
$monthlyTrigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 31 -At "23:30"  # 31日触发，2月等会自动调整
$monthlySettings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

try {
    Register-ScheduledTask -TaskName "$TaskName-Monthly" -Action $monthlyAction -Trigger $monthlyTrigger -Settings $monthlySettings -Description "OpenClaw每月记忆备份" -Force
    Write-Host "✅ 每月备份任务创建成功"
} catch {
    Write-Host "❌ 每月备份任务创建失败: $_"
}

# 4. 创建手动备份快捷方式
Write-Host "`n🔗 创建手动备份快捷方式..."
$shortcutPath = "$env:USERPROFILE\Desktop\OpenClaw记忆备份.lnk"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "PowerShell"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$BackupScript`""
$Shortcut.WorkingDirectory = "D:\OpenClaw_TestingFramework"
$Shortcut.Description = "手动运行OpenClaw记忆备份"
$Shortcut.Save()

Write-Host "✅ 桌面快捷方式创建成功: $shortcutPath"

# 5. 显示任务状态
Write-Host "`n📋 备份任务状态:"
Write-Host "=" * 40

$tasks = @("$TaskName-Daily", "$TaskName-Weekly", "$TaskName-Monthly")

foreach ($task in $tasks) {
    try {
        $taskInfo = Get-ScheduledTask -TaskName $task -ErrorAction Stop
        $state = $taskInfo.State
        $nextRun = $taskInfo | Get-ScheduledTaskInfo | Select-Object -ExpandProperty NextRunTime
        
        Write-Host "任务: $task"
        Write-Host "  状态: $state"
        Write-Host "  下次运行: $nextRun"
        Write-Host ""
    } catch {
        Write-Host "任务: $task"
        Write-Host "  状态: 未找到"
        Write-Host ""
    }
}

# 6. 创建验证脚本
Write-Host "`n🔍 创建备份验证脚本..."
$verifyScript = @'
#!/usr/bin/env pwsh
<#
OpenClaw记忆备份验证脚本
#>

$BackupRoot = "D:\OpenClaw_TestingFramework"
$LogFile = "$BackupRoot\backup_log.txt"

Write-Host "🔍 OpenClaw记忆备份验证"
Write-Host "=" * 40

# 检查备份目录
$backupDirs = @(
    "$BackupRoot\memory",
    "$BackupRoot\memory\daily",
    "$BackupRoot\memory\weekly",
    "$BackupRoot\memory\monthly",
    "$BackupRoot\memory\archive"
)

foreach ($dir in $backupDirs) {
    if (Test-Path $dir) {
        $fileCount = (Get-ChildItem -Path $dir -File -Recurse -ErrorAction SilentlyContinue).Count
        Write-Host "✅ $dir - $fileCount 个文件"
    } else {
        Write-Host "❌ $dir - 目录不存在"
    }
}

# 检查日志文件
if (Test-Path $LogFile) {
    $lastLog = Get-Content $LogFile -Tail 5
    Write-Host "`n📝 最近日志:"
    $lastLog | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "`n⚠️  日志文件不存在"
}

# 检查计划任务
Write-Host "`n📅 计划任务状态:"
$tasks = Get-ScheduledTask | Where-Object { $_.TaskName -like "*OpenClawMemoryBackup*" }

if ($tasks) {
    foreach ($task in $tasks) {
        $info = $task | Get-ScheduledTaskInfo
        Write-Host "  $($task.TaskName): $($task.State) - 下次运行: $($info.NextRunTime)"
    }
} else {
    Write-Host "  ⚠️  未找到备份计划任务"
}

Write-Host "`n💡 建议:"
Write-Host "  1. 每日检查备份日志"
Write-Host "  2. 每月验证备份完整性"
Write-Host "  3. 定期清理旧备份"
Write-Host "`n验证完成!"
'@

$verifyScriptPath = "$BackupRoot\verify_backup.ps1"
$verifyScript | Out-File -FilePath $verifyScriptPath -Encoding UTF8
Write-Host "✅ 验证脚本创建成功: $verifyScriptPath"

Write-Host "`n🎉 备份系统设置完成!"
Write-Host "`n💡 使用建议:"
Write-Host "  1. 每日检查: 运行 $verifyScriptPath"
Write-Host "  2. 手动备份: 双击桌面快捷方式"
Write-Host "  3. 查看日志: $BackupRoot\backup_log.txt"
Write-Host "  4. 修改配置: 编辑 $BackupScript"