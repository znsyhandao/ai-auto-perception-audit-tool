#!/usr/bin/env python3
"""
OpenClaw娴嬭瘯妗嗘灦鑷姩鍔犺浇鍣?寤鸿娣诲姞鍒癘penClaw鍚姩鑴氭湰鎴栨瘡娆′細璇濆紑濮嬫椂杩愯
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_testing_framework():
    """璁剧疆娴嬭瘯妗嗘灦"""
    
    print("馃敡 OpenClaw娴嬭瘯妗嗘灦鑷姩鍔犺浇")
    print("=" * 60)
    
    # 1. 妫EUR鏌ュ伐浣滅┖闂寸洰褰?    workspace_dir = Path.home() / ".openclaw" / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"宸ヤ綔绌洪棿: {workspace_dir}")
    
    # 2. 妫EUR鏌ユ祴璇曟鏋舵枃浠舵槸鍚﹀瓨鍦?    required_files = [
        "TESTING_FRAMEWORK.md",
        "security_scanner.py",
        "release_checklist.py"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = workspace_dir / file
        if not file_path.exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"鈿狅笍  缂哄皯娴嬭瘯妗嗘灦鏂囦欢: {', '.join(missing_files)}")
        print("姝ｅ湪灏濊瘯浠庡浠芥仮澶?..")
        
        # 灏濊瘯浠庡浠芥仮澶?        backup_dir = Path.home() / "OpenClaw_TestingFramework"
        restore_script = backup_dir / "restore_testing_framework.py"
        
        if restore_script.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(restore_script)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print("鉁?娴嬭瘯妗嗘灦鎭㈠鎴愬姛")
                else:
                    print(f"鉂?鎭㈠澶辫触: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("鉂?鎭㈠瓒呮椂")
                return False
            except Exception as e:
                print(f"鉂?鎭㈠閿欒: {e}")
                return False
        else:
            print(f"鉂?鎭㈠鑴氭湰涓嶅瓨鍦? {restore_script}")
            print("璇锋墜鍔ㄨ繍琛屾仮澶嶆垨閲嶆柊鍒涘缓娴嬭瘯妗嗘灦")
            return False
    else:
        print("鉁?娴嬭瘯妗嗘灦鏂囦欢瀹屾暣")
    
    # 3. 娣诲姞宸ヤ綔绌洪棿鍒癙ython璺緞
    if str(workspace_dir) not in sys.path:
        sys.path.insert(0, str(workspace_dir))
        print(f"鉁?娣诲姞宸ヤ綔绌洪棿鍒癙ython璺緞")
    
    # 4. 璁剧疆鐜鍙橀噺
    os.environ['OPENCLAW_TEST_FRAMEWORK'] = 'enabled'
    os.environ['OPENCLAW_SECURITY_SCANNER'] = str(workspace_dir / 'security_scanner.py')
    os.environ['OPENCLAW_RELEASE_CHECKLIST'] = str(workspace_dir / 'release_checklist.py')
    
    print("鉁?璁剧疆鐜鍙橀噺")
    
    # 5. 鍒涘缓蹇嵎鍛戒护
    create_quick_commands(workspace_dir)
    
    # 6. 楠岃瘉妗嗘灦鍙敤鎬?    if verify_framework():
        print("\n馃帀 娴嬭瘯妗嗘灦鍔犺浇瀹屾垚锛?)
        print_usage_guide()
        return True
    else:
        print("\n鈿狅笍  妗嗘灦鍔犺浇瀹屾垚锛屼絾楠岃瘉澶辫触")
        return False

def create_quick_commands(workspace_dir: Path):
    """鍒涘缓蹇嵎鍛戒护"""
    
    # 鍒涘缓鎵瑰鐞嗘枃浠讹紙Windows锛?    if sys.platform == "win32":
        bat_content = f'''@echo off
echo OpenClaw娴嬭瘯妗嗘灦蹇嵎鍛戒护
echo.
echo 鍙敤鍛戒护:
echo   scan-skill    - 瀹夊叏妫EUR鏌ユ妧鑳界洰褰?echo   check-release - 杩愯鍙戝竷妫EUR鏌?echo   test-help     - 鏄剧ず娴嬭瘯妗嗘灦甯姪
echo.
'''
        
        bat_path = workspace_dir / "test_commands.bat"
        with open(bat_path, 'w', encoding='gbk') as f:
            f.write(bat_content)
        
        # 鍒涘缓PowerShell鑴氭湰
        ps_content = f'''# OpenClaw娴嬭瘯妗嗘灦PowerShell鍛戒护

function Scan-Skill {{
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    
    python "{workspace_dir / 'security_scanner.py'}" $Path
}}

function Check-Release {{
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    
    python "{workspace_dir / 'release_checklist.py'}" $Path
}}

function Test-Help {{
    Get-Content "{workspace_dir / 'TESTING_FRAMEWORK.md'}" -TotalCount 50
}}

Write-Host "OpenClaw娴嬭瘯妗嗘灦鍛戒护宸插姞杞?
Write-Host "鍙敤鍛戒护: Scan-Skill, Check-Release, Test-Help"
'''
        
        ps_path = workspace_dir / "test_commands.ps1"
        with open(ps_path, 'w', encoding='utf-8') as f:
            f.write(ps_content)
        
        print("鉁?鍒涘缓Windows蹇嵎鍛戒护")

def verify_framework():
    """楠岃瘉妗嗘灦鍙敤鎬?""
    
    try:
        # 灏濊瘯瀵煎叆瀹夊叏妫EUR鏌ユā鍧?        import importlib.util
        
        # 妫EUR鏌ecurity_scanner.py
        scanner_path = Path.home() / ".openclaw" / "workspace" / "security_scanner.py"
        if scanner_path.exists():
            spec = importlib.util.spec_from_file_location("security_scanner", scanner_path)
            if spec and spec.loader:
                print("鉁?security_scanner.py 鍙鍏?)
            else:
                print("鈿狅笍  security_scanner.py 瀵煎叆澶辫触")
                return False
        else:
            print("鉂?security_scanner.py 涓嶅瓨鍦?)
            return False
        
        # 妫EUR鏌elease_checklist.py
        checklist_path = Path.home() / ".openclaw" / "workspace" / "release_checklist.py"
        if checklist_path.exists():
            spec = importlib.util.spec_from_file_location("release_checklist", checklist_path)
            if spec and spec.loader:
                print("鉁?release_checklist.py 鍙鍏?)
            else:
                print("鈿狅笍  release_checklist.py 瀵煎叆澶辫触")
                return False
        else:
            print("鉂?release_checklist.py 涓嶅瓨鍦?)
            return False
        
        return True
        
    except Exception as e:
        print(f"鉂?妗嗘灦楠岃瘉閿欒: {e}")
        return False

def print_usage_guide():
    """鎵撳嵃浣跨敤鎸囧崡"""
    
    print("\n馃摎 浣跨敤鎸囧崡:")
    print("=" * 40)
    
    print("\n1. 瀹夊叏妫EUR鏌ユ妧鑳?")
    print("   python security_scanner.py <鎶EUR鑳界洰褰?")
    print("   绀轰緥: python security_scanner.py ./my-skill")
    
    print("\n2. 杩愯鍙戝竷妫EUR鏌?")
    print("   python release_checklist.py <鎶EUR鑳界洰褰?")
    print("   绀轰緥: python release_checklist.py ./my-skill")
    
    print("\n3. 鏌ョ湅娴嬭瘯妗嗘灦鏂囨。:")
    print("   闃呰 TESTING_FRAMEWORK.md")
    
    print("\n4. 蹇EUR熷懡浠?(Windows PowerShell):")
    print("   Scan-Skill -Path ./my-skill")
    print("   Check-Release -Path ./my-skill")
    print("   Test-Help")
    
    print("\n馃挕 鎻愮ず:")
    print("   鈥?姣忔鍙戝竷鎶EUR鑳藉墠蹇呴』杩愯瀹夊叏妫EUR鏌?)
    print("   鈥?鎵EUR鏈夋鏌ラEUR氳繃鍚庢墠鑳藉彂甯冨埌ClawHub")
    print("   鈥?瀹氭湡澶囦唤娴嬭瘯妗嗘灦鍒板畨鍏ㄤ綅缃?)

def main():
    """涓诲嚱鏁?""
    success = setup_testing_framework()
    
    if success:
        print("\n馃殌 娴嬭瘯妗嗘灦宸插氨缁紝鍙互寮EUR濮嬪畨鍏ㄦ鏌ワ紒")
        sys.exit(0)
    else:
        print("\n鉂?娴嬭瘯妗嗘灦鍔犺浇澶辫触")
        print("璇锋鏌?")
        print("1. 澶囦唤鏂囦欢鏄惁瀛樺湪")
        print("2. 宸ヤ綔绌洪棿鐩綍鏉冮檺")
        print("3. Python鐜閰嶇疆")
        sys.exit(1)

if __name__ == "__main__":
    main()
