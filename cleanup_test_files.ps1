#!/usr/bin/env pwsh
<#
.SYNOPSIS
娓呯悊鎶€鑳界洰褰曚腑鐨勬祴璇曟枃浠?
.DESCRIPTION
鍩轰簬2026-03-23娴嬭瘯鏂囦欢娣锋穯鏁欒锛岃嚜鍔ㄦ竻鐞嗘妧鑳界洰褰曚腑鐨勬祴璇曟枃浠躲€?杩欎簺鏂囦欢涓嶅簲璇ュ湪鍙戝竷鍖呬腑锛屽彲鑳藉寘鍚綉缁滀唬鐮侊紝浼氳Е鍙慍lawHub瀹夊叏鎵弿璇姤銆?
.PARAMETER SkillDirectory
鎶€鑳界洰褰曡矾寰?
.EXAMPLE
.\cleanup_test_files.ps1 "D:\my-skill"
娓呯悊鎸囧畾鎶€鑳界洰褰曚腑鐨勬祴璇曟枃浠?
.EXAMPLE
.\cleanup_test_files.ps1 "D:\openclaw\releases\skincare-ai-clean"
娓呯悊AISkinX鎶€鑳界洰褰?#>

param(
    [Parameter(Mandatory=$true, HelpMessage="鎶€鑳界洰褰曡矾寰?)]
    [string]$SkillDirectory
)

# 璁剧疆鎺у埗鍙扮紪鐮?[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ("`n" + ("="*60)) -ForegroundColor Cyan
Write-Host "馃Ч 娴嬭瘯鏂囦欢娓呯悊宸ュ叿" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "鍩轰簬2026-03-23娴嬭瘯鏂囦欢娣锋穯鏁欒" -ForegroundColor Yellow
Write-Host "鐩綍: $SkillDirectory" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

# 妫€鏌ョ洰褰曟槸鍚﹀瓨鍦?if (-not (Test-Path $SkillDirectory)) {
    Write-Host "鉂?鐩綍涓嶅瓨鍦? $SkillDirectory" -ForegroundColor Red
    exit 1
}

# 娴嬭瘯鏂囦欢妯″紡锛堝熀浜庝粖澶╃殑鍏蜂綋鏁欒锛?$testPatterns = @(
    "*check*",      # FINAL_CHECK.py, quick_check.py绛?    "*test*",       # simple_test.py, complete_test_suite.py绛?    "*verify*",     # 楠岃瘉鑴氭湰
    "*final*",      # FINAL_COMPREHENSIVE_CHECK.py绛?    "*quick*",      # 蹇€熸鏌ヨ剼鏈?    "*simple*"      # 绠€鍗曟祴璇曡剼鏈?)

# 鐪熸鐨勬妧鑳芥枃浠讹紙涓嶅簲璇ュ垹闄わ級
$skillFiles = @(
    "skill.py",     # 涓绘妧鑳芥枃浠?    "__init__.py"   # 鍖呭垵濮嬪寲鏂囦欢
)

# 鎶€鑳芥ā鍧楃洰褰曪紙涓嶅簲璇ュ垹闄わ級
$skillDirs = @(
    "core",
    "api"
)

$removedFiles = @()
$skippedFiles = @()

Write-Host "`n馃攳 鎵弿娴嬭瘯鏂囦欢..." -ForegroundColor Yellow

foreach ($pattern in $testPatterns) {
    $files = Get-ChildItem $SkillDirectory -Recurse -Filter "$pattern.py" -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $fileName = $file.Name
        $filePath = $file.FullName
        $relativePath = $file.FullName.Replace($SkillDirectory, "").TrimStart("\")
        
        # 妫€鏌ユ槸鍚︽槸鐪熸鐨勬妧鑳芥枃浠?        $isSkillFile = $false
        
        # 1. 妫€鏌ユ枃浠跺悕
        if ($skillFiles -contains $fileName) {
            $isSkillFile = $true
            $reason = "涓绘妧鑳芥枃浠?
        }
        
        # 2. 妫€鏌ユ槸鍚﹀湪鎶€鑳芥ā鍧楃洰褰曚腑
        foreach ($dir in $skillDirs) {
            if ($filePath -match "\\$dir\\") {
                $isSkillFile = $true
                $reason = "鎶€鑳芥ā鍧楁枃浠?($dir/)"
                break
            }
        }
        
        # 3. 妫€鏌ユ枃浠跺唴瀹癸紙濡傛灉鏄痵kill.py锛?        if ($fileName -eq "skill.py") {
            try {
                $content = Get-Content $filePath -TotalCount 10 -ErrorAction Stop
                if ($content -match "class.*Skill" -or $content -match "def create_skill") {
                    $isSkillFile = $true
                    $reason = "鍖呭惈鎶€鑳界被瀹氫箟"
                }
            } catch {
                # 蹇界暐璇诲彇閿欒
            }
        }
        
        if ($isSkillFile) {
            $skippedFiles += @{
                File = $relativePath
                Reason = $reason
            }
            Write-Host "  鈿狅笍  璺宠繃: $relativePath ($reason)" -ForegroundColor Yellow
        } else {
            # 澶囦唤鍒版祴璇曟鏋剁洰褰?            $backupDir = Join-Path $PSScriptRoot "backup_test_files"
            if (-not (Test-Path $backupDir)) {
                New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            }
            
            $backupPath = Join-Path $backupDir $relativePath
            $backupDirPath = Split-Path $backupPath -Parent
            if (-not (Test-Path $backupDirPath)) {
                New-Item -ItemType Directory -Path $backupDirPath -Force | Out-Null
            }
            
            # 澶囦唤鏂囦欢
            Copy-Item $filePath $backupPath -Force
            
            # 鍒犻櫎鍘熸枃浠?            Remove-Item $filePath -Force
            
            $removedFiles += $relativePath
            Write-Host "  鉁?鍒犻櫎: $relativePath (宸插浠藉埌娴嬭瘯妗嗘灦)" -ForegroundColor Green
        }
    }
}

Write-Host ("`n" + ("="*60)) -ForegroundColor Cyan
Write-Host "馃搳 娓呯悊缁撴灉姹囨€? -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

if ($removedFiles.Count -gt 0) {
    Write-Host "鉁?娓呯悊瀹屾垚锛屽垹闄や簡 $($removedFiles.Count) 涓祴璇曟枃浠? -ForegroundColor Green
    Write-Host "`n鍒犻櫎鐨勬枃浠?" -ForegroundColor Yellow
    foreach ($file in $removedFiles) {
        Write-Host "  鈥?$file"
    }
    
    $backupDir = Join-Path $PSScriptRoot "backup_test_files"
    Write-Host "`n馃搧 澶囦唤浣嶇疆: $backupDir" -ForegroundColor Cyan
} else {
    Write-Host "鉁?娌℃湁鍙戠幇闇€瑕佹竻鐞嗙殑娴嬭瘯鏂囦欢" -ForegroundColor Green
}

if ($skippedFiles.Count -gt 0) {
    Write-Host "`n鈿狅笍  璺宠繃鐨勬枃浠讹紙鎶€鑳芥枃浠讹級:" -ForegroundColor Yellow
    foreach ($file in $skippedFiles) {
        Write-Host "  鈥?$($file.File) ($($file.Reason))"
    }
}

# 妫€鏌ユ妧鑳界洰褰曠幇鍦ㄦ槸鍚﹀共鍑€
Write-Host "`n馃攳 鏈€缁堥獙璇?.." -ForegroundColor Yellow
$remainingTestFiles = @()
foreach ($pattern in $testPatterns) {
    $files = Get-ChildItem $SkillDirectory -Recurse -Filter "$pattern.py" -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        # 鍙鏌ラ潪鎶€鑳芥枃浠?        $isSkillFile = $false
        if ($skillFiles -contains $file.Name) {
            $isSkillFile = $true
        }
        foreach ($dir in $skillDirs) {
            if ($file.FullName -match "\\$dir\\") {
                $isSkillFile = $true
                break
            }
        }
        
        if (-not $isSkillFile) {
            $remainingTestFiles += $file.FullName.Replace($SkillDirectory, "").TrimStart("\")
        }
    }
}

if ($remainingTestFiles.Count -eq 0) {
    Write-Host "馃帀 鎶€鑳界洰褰曠幇鍦ㄥ共鍑€锛屾棤娴嬭瘯鏂囦欢锛? -ForegroundColor Green
} else {
    Write-Host "鉂?浠嶇劧鏈夋祴璇曟枃浠?" -ForegroundColor Red
    foreach ($file in $remainingTestFiles) {
        Write-Host "  鈥?$file"
    }
    Write-Host "`n鈿狅笍  璇锋墜鍔ㄦ鏌ヨ繖浜涙枃浠舵槸鍚﹂渶瑕佸垹闄? -ForegroundColor Yellow
}

Write-Host ("`n" + ("="*60)) -ForegroundColor Cyan
Write-Host "馃Ч 娓呯悊瀹屾垚" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n馃搵 寤鸿涓嬩竴姝?" -ForegroundColor Cyan
Write-Host "1. 杩愯澧炲己瀹夊叏妫€鏌? .\enhanced_security_scanner.py `"$SkillDirectory`""
Write-Host "2. 杩愯鍙戝竷妫€鏌ユ竻鍗? .\enhanced_release_checklist.py `"$SkillDirectory`""
Write-Host "3. 鏌ョ湅鍙戝竷鎶ュ憡: $SkillDirectory\RELEASE_REPORT.md"
Write-Host "4. 涓婁紶鍒癈lawHub: https://clawhub.com/upload"

exit 0
