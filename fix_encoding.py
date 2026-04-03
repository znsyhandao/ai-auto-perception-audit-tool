#!/usr/bin/env python3
"""修复文件编码"""

import sys
from pathlib import Path

def fix_file_encoding(file_path):
    """修复文件编码"""
    try:
        # 尝试用不同编码读取
        encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
        content = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print(f"无法读取: {file_path.name}")
            return False
        
        # 用UTF-8写回
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"修复: {file_path.name} ({used_encoding} -> UTF-8)")
        return True
        
    except Exception as e:
        print(f"错误: {file_path.name} - {e}")
        return False

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    # 修复所有.md文件
    md_files = list(skill_path.rglob("*.md"))
    
    print(f"修复 {len(md_files)} 个.md文件...")
    
    fixed_count = 0
    for md_file in md_files:
        if fix_file_encoding(md_file):
            fixed_count += 1
    
    print(f"\n修复完成: {fixed_count}/{len(md_files)} 个文件")

if __name__ == "__main__":
    main()