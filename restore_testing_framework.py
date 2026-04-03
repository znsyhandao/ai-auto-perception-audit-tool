#!/usr/bin/env python3
"""
OpenClaw测试框架恢复脚本
在重新安装OpenClaw后运行此脚本恢复测试框架
"""

import os
import shutil
import sys
from pathlib import Path

def restore_testing_framework():
    """恢复测试框架"""
    
    # 备份目录（修改为您实际的备份路径）
    backup_dir = r"D:\\OpenClaw_TestingFramework"
    
    # OpenClaw工作空间目录
    workspace_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace")
    
    print("[WRENCH] OpenClaw测试框架恢复工具")
    print("=" * 60)
    print(f"备份目录: {backup_dir}")
    print(f"工作空间: {workspace_dir}")
    print()
    
    # 检查备份目录是否存在
    if not os.path.exists(backup_dir):
        print(f"[ERROR] 备份目录不存在: {backup_dir}")
        print("请确保备份目录存在并包含测试框架文件")
        return False
    
    # 创建工作空间目录（如果不存在）
    os.makedirs(workspace_dir, exist_ok=True)
    
    # 要恢复的文件列表
    files_to_restore = [
        "TESTING_FRAMEWORK.md",
        "security_scanner.py",
        "release_checklist.py",
        "memory/2026-03-23.md",
        "MEMORY.md"
    ]
    
    restored_count = 0
    error_count = 0
    
    for file_rel in files_to_restore:
        source_path = os.path.join(backup_dir, file_rel)
        dest_path = os.path.join(workspace_dir, file_rel)
        
        # 确保目标目录存在
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, dest_path)
                print(f"[OK] 恢复: {file_rel}")
                restored_count += 1
            except Exception as e:
                print(f"[ERROR] 恢复失败 {file_rel}: {e}")
                error_count += 1
        else:
            print(f"[WARN]  备份文件不存在: {file_rel}")
    
    print()
    print("[DASHBOARD] 恢复统计:")
    print(f"  成功恢复: {restored_count} 个文件")
    print(f"  恢复失败: {error_count} 个文件")
    print(f"  总文件数: {len(files_to_restore)}")
    
    if error_count == 0:
        print("\n[CELEBRATE] 测试框架恢复完成！")
        print("现在可以:")
        print("1. 使用 security_scanner.py 检查技能安全")
        print("2. 使用 release_checklist.py 运行发布检查")
        print("3. 遵循 TESTING_FRAMEWORK.md 的发布流程")
        return True
    else:
        print("\n[WARN]  恢复完成，但有错误")
        return False

def create_quick_setup_script():
    """创建快速设置脚本"""
    setup_script = r'''#!/usr/bin/env python3
"""
OpenClaw测试框架快速设置
在每次OpenClaw会话开始时运行
"""

import os
import sys

# 添加测试工具到PATH
workspace_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace")
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

print("[WRENCH] OpenClaw测试框架已加载")
print("可用工具:")
print("  - security_scanner.py - 安全检查")
print("  - release_checklist.py - 发布检查")
print("  - TESTING_FRAMEWORK.md - 测试框架文档")

# 设置环境变量
os.environ['OPENCLAW_TEST_FRAMEWORK'] = 'enabled'
'''

    setup_path = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "setup_testing.py")
    with open(setup_path, 'w', encoding='utf-8') as f:
        f.write(setup_script)
    
    print(f"[OK] 创建快速设置脚本: {setup_path}")
    return setup_path

if __name__ == "__main__":
    success = restore_testing_framework()
    
    if success:
        setup_script = create_quick_setup_script()
        print(f"\n[IDEA] 建议:")
        print(f"1. 将 {setup_script} 添加到OpenClaw启动脚本")
        print(f"2. 或每次会话开始时运行: python {setup_script}")
    
    sys.exit(0 if success else 1)

