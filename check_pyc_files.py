#!/usr/bin/env python3
"""检查.pyc文件"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_pyc_files.py <path>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 查找.pyc文件
    pyc_files = list(skill_path.rglob("*.pyc"))
    pycache_dirs = list(skill_path.rglob("__pycache__"))
    
    print(f"检查: {skill_path}")
    print("-" * 80)
    
    if pyc_files:
        print(f"发现 {len(pyc_files)} 个.pyc文件:")
        for pyc_file in pyc_files:
            print(f"  ❌ {pyc_file.relative_to(skill_path)}")
        
        print(f"\n建议删除:")
        for pyc_file in pyc_files:
            print(f"  del \"{pyc_file}\"")
        
        return False
    else:
        print("✅ 没有发现.pyc文件")
    
    if pycache_dirs:
        print(f"\n发现 {len(pycache_dirs)} 个__pycache__目录:")
        for pycache_dir in pycache_dirs:
            print(f"  ❌ {pycache_dir.relative_to(skill_path)}")
        
        print(f"\n建议删除:")
        for pycache_dir in pycache_dirs:
            print(f"  rmdir /s /q \"{pycache_dir}\"")
        
        return False
    else:
        print("✅ 没有发现__pycache__目录")
    
    print("-" * 80)
    print("✅ 所有检查通过")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)