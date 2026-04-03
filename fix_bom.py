#!/usr/bin/env python3
"""修复BOM标记问题"""

import sys
from pathlib import Path

def remove_bom(file_path):
    """移除BOM标记"""
    try:
        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 检查并移除BOM
        if content.startswith(b'\xef\xbb\xbf'):
            print(f"修复: {file_path.name} - 移除BOM")
            content = content[3:]
            
            # 写回文件
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return True
        else:
            print(f"正常: {file_path.name} - 无BOM")
            return False
            
    except Exception as e:
        print(f"错误: {file_path.name} - {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python fix_bom.py <技能路径>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 修复所有Python文件
    python_files = list(skill_path.rglob("*.py"))
    
    print(f"检查 {len(python_files)} 个Python文件...")
    
    fixed_count = 0
    for py_file in python_files:
        if remove_bom(py_file):
            fixed_count += 1
    
    print(f"\n修复完成: {fixed_count}/{len(python_files)} 个文件")
    
    # 验证修复
    print("\n验证修复...")
    for py_file in python_files[:3]:  # 检查前3个文件
        with open(py_file, 'rb') as f:
            content = f.read()
            if content.startswith(b'\xef\xbb\xbf'):
                print(f"警告: {py_file.name} 仍有BOM")
            else:
                print(f"正常: {py_file.name} 无BOM")

if __name__ == "__main__":
    main()