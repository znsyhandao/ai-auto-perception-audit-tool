# fix-skill.ps1
$skillPath = "D:\openclaw\releases\AISleepGen_4.0.4_clarified"
$skillInfoPath = "$skillPath\skill_info.json"

# 备份原文件
Copy-Item $skillInfoPath "$skillInfoPath.backup"

# 读取并修改 skill_info.json
$skillInfo = Get-Content $skillInfoPath -Raw | ConvertFrom-Json

# 添加 source 字段
$skillInfo | Add-Member -MemberType NoteProperty -Name "source" -Value "https://github.com/AISleepGen/aisleepgen-sleep-health" -Force

# 保存
$skillInfo | ConvertTo-Json -Depth 10 | Set-Content $skillInfoPath -Encoding UTF8

Write-Host "✅ 已添加 source 字段到 skill_info.json" -ForegroundColor Green

# 修改 SKILL.md，将链接改为文本
$skillMdPath = "$skillPath\SKILL.md"
$content = Get-Content $skillMdPath -Raw
$content = $content -replace 'https://github\.com/AISleepGen/aisleepgen-sleep-health', 'github.com/AISleepGen/aisleepgen-sleep-health'
$content | Set-Content $skillMdPath -Encoding UTF8

Write-Host "✅ 已修改 SKILL.md 中的链接为纯文本" -ForegroundColor Green

# 修改 README.md
$readmePath = "$skillPath\README.md"
if (Test-Path $readmePath) {
    $content = Get-Content $readmePath -Raw
    $content = $content -replace 'https://github\.com/AISleepGen/aisleepgen-sleep-health', 'github.com/AISleepGen/aisleepgen-sleep-health'
    $content | Set-Content $readmePath -Encoding UTF8
    Write-Host "✅ 已修改 README.md 中的链接为纯文本" -ForegroundColor Green
}

Write-Host "`n修复完成！现在重新审核 skill：" -ForegroundColor Yellow
node D:\OpenClaw_TestingFramework\audit-skill.js $skillPath