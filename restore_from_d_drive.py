#!/usr/bin/env python3
"""
OpenClaw测试框架 - D盘专用恢复脚本
专门为D盘备份位置优化
"""

import os
import sys
import shutil
import platform
from pathlib import Path

def check_d_drive():
    """检查D盘"""
    print("[DETAILS] 检查D盘...")
    
    d_drive = Path("D:/")
    if not d_drive.exists():
        print("[ERROR] D盘不存在")
        return None
    
    backup_dir = d_drive / "OpenClaw_TestingFramework"
    if not backup_dir.exists():
        print(f"[ERROR] 备份目录不存在: {backup_dir}")
        return None
    
    print(f"[OK] D盘备份目录: {backup_dir}")
    return backup_dir

def get_openclaw_workspace():
    """获取OpenClaw工作空间路径"""
    system = platform.system()
    
    if system == "Windows":
        workspace = Path.home() / ".openclaw" / "workspace"
    elif system == "Linux" or system == "Darwin":
        workspace = Path.home() / ".openclaw" / "workspace"
    else:
        print(f"[WARN]  未知系统: {system}")
        workspace = Path.home() / ".openclaw" / "workspace"
    
    return workspace

def restore_framework(backup_dir: Path, workspace: Path):
    """恢复测试框架"""
    print(f"[WRENCH] 恢复测试框架...")
    print(f"  从: {backup_dir}")
    print(f"  到: {workspace}")
    
    # 确保工作空间目录存在
    workspace.mkdir(parents=True, exist_ok=True)
    
    # 要恢复的文件列表
    files_to_restore = [
        "TESTING_FRAMEWORK.md",
        "security_scanner.py",
        "release_checklist.py",
        "memory/2026-03-23.md",
        "MEMORY.md"
    ]
    
    restored = 0
    errors = 0
    
    for file_rel in files_to_restore:
        source = backup_dir / file_rel
        dest = workspace / file_rel
        
        # 确保目标目录存在
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        if source.exists():
            try:
                shutil.copy2(source, dest)
                print(f"  [OK] {file_rel}")
                restored += 1
            except Exception as e:
                print(f"  [ERROR] {file_rel}: {e}")
                errors += 1
        else:
            print(f"  [WARN]  {file_rel}: 源文件不存在")
    
    return restored, errors

def create_quick_access():
    """创建快速访问"""
    print("[LINK] 创建快速访问...")
    
    # 创建批处理文件
    bat_content = '''@echo off
echo OpenClaw测试框架 - 快速命令
echo.
echo 可用命令:
echo   scan-skill <目录>    - 安全检查
echo   check-release <目录> - 发布检查
echo   test-help           - 显示帮助
echo.
if "%1"=="scan-skill" (
    if "%2"=="" (
        echo 用法: scan-skill <技能目录>
    ) else (
        python "%~dp0security_scanner.py" "%2"
    )
) else if "%1"=="check-release" (
    if "%2"=="" (
        echo 用法: check-release <技能目录>
    ) else (
        python "%~dp0release_checklist.py" "%2"
    )
) else if "%1"=="test-help" (
    type "%~dp0TESTING_FRAMEWORK.md" | more
) else (
    echo 未知命令，使用: scan-skill, check-release, test-help
)
'''
    
    workspace = get_openclaw_workspace()
    bat_path = workspace / "test_framework.bat"
    
    with open(bat_path, 'w', encoding='gbk') as f:
        f.write(bat_content)
    
    print(f"  [OK] 创建快速命令: {bat_path}")
    
    # 创建说明文件
    readme_content = f"""# OpenClaw测试框架

## [FOLDER] 位置
- 工作空间: {workspace}
- D盘备份: D:\\OpenClaw_TestingFramework

## [LAUNCH] 快速使用

### 安全检查:
```bash
python security_scanner.py <技能目录>
```

### 发布检查:
```bash
python release_checklist.py <技能目录>
```

### 批处理命令:
```bash
test_framework.bat scan-skill <目录>
test_framework.bat check-release <目录>
test_framework.bat test-help
```

## 🔄 恢复说明

如果重新安装OpenClaw，运行:
```bash
python D:\\OpenClaw_TestingFramework\\restore_from_d_drive.py
```

或双击: D:\\OpenClaw_TestingFramework\\setup_drive_d.bat

## [TELEPHONE_RECEIVER] 支持

- 备份位置: D:\\OpenClaw_TestingFramework\\
- 恢复脚本: restore_from_d_drive.py
- 设置脚本: setup_drive_d.bat
- 完整指南: BACKUP_AND_RESTORE_GUIDE.md
"""
    
    readme_path = workspace / "TEST_FRAMEWORK_README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  [OK] 创建说明文档: {readme_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw测试框架 - D盘恢复工具")
    print("=" * 60)
    
    # 检查D盘
    backup_dir = check_d_drive()
    if not backup_dir:
        print("[ERROR] 无法访问D盘备份")
        sys.exit(1)
    
    # 获取工作空间
    workspace = get_openclaw_workspace()
    print(f"[FOLDER] OpenClaw工作空间: {workspace}")
    
    # 恢复文件
    restored, errors = restore_framework(backup_dir, workspace)
    
    print()
    print("[DASHBOARD] 恢复结果:")
    print(f"  成功: {restored} 个文件")
    print(f"  失败: {errors} 个文件")
    
    if errors > 0:
        print("[WARN]  有文件恢复失败，请检查")
    
    # 创建快速访问
    create_quick_access()
    
    print()
    print("=" * 60)
    print("[CELEBRATE] 恢复完成！")
    print()
    print("[IDEA] 下一步:")
    print("  1. 运行安全检查: python security_scanner.py --help")
    print("  2. 查看框架文档: type TEST_FRAMEWORK_README.md")
    print("  3. 使用快速命令: test_framework.bat")
    print()
    print("[FOLDER] 备份位置: D:\\OpenClaw_TestingFramework\\")
    print("[WRENCH] 恢复脚本: restore_from_d_drive.py")
    print("[LAUNCH] 设置脚本: setup_drive_d.bat")
    print("=" * 60)
    
    sys.exit(0 if errors == 0 else 1)

if __name__ == "__main__":
    main()