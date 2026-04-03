#!/usr/bin/env python3
"""最终审核"""

import sys
from pathlib import Path

def check_pyc_files(skill_path):
    """检查.pyc文件"""
    pyc_files = list(skill_path.rglob("*.pyc"))
    pycache_dirs = list(skill_path.rglob("__pycache__"))
    
    if pyc_files or pycache_dirs:
        print(f"❌ 发现 {len(pyc_files)} 个.pyc文件和 {len(pycache_dirs)} 个__pycache__目录")
        return False
    else:
        print("✅ 没有.pyc文件或__pycache__目录")
        return True

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("=" * 80)
    print("最终审核")
    print("=" * 80)
    
    # 检查.pyc文件
    pyc_ok = check_pyc_files(skill_path)
    
    # 检查文件数量
    all_files = list(skill_path.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    dir_count = len([f for f in all_files if f.is_dir()])
    
    print(f"\n文件统计:")
    print(f"  总文件数: {file_count}")
    print(f"  目录数: {dir_count}")
    
    # 检查必需文件
    required_files = ["skill.py", "config.yaml", "SKILL.md", "README.md", "CHANGELOG.md", "LICENSE.txt"]
    missing = []
    
    for filename in required_files:
        if not (skill_path / filename).exists():
            missing.append(filename)
    
    if missing:
        print(f"❌ 缺失文件: {missing}")
        return False
    else:
        print("✅ 所有必需文件存在")
    
    print("=" * 80)
    
    if pyc_ok and not missing:
        print("🎉 所有检查通过！可以发布。")
        return True
    else:
        print("❌ 有检查失败，不能发布。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)