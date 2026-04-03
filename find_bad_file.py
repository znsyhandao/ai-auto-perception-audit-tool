#!/usr/bin/env python3
"""查找有编码问题的文件"""

import sys
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    # 检查所有.md文件
    md_files = list(skill_path.rglob("*.md"))
    
    print(f"Checking {len(md_files)} .md files...")
    
    bad_files = []
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError as e:
            bad_files.append((md_file, e))
    
    if bad_files:
        print(f"\nFound {len(bad_files)} files with encoding issues:")
        for file_path, error in bad_files:
            print(f"\n{file_path.name}:")
            print(f"  Error: {error}")
            
            # 尝试其他编码
            for encoding in ['gbk', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read(100)  # 只读前100字符
                    print(f"  Can read with {encoding}: {content[:50]}...")
                    break
                except:
                    continue
    else:
        print("All files are UTF-8 encoded")

if __name__ == "__main__":
    main()