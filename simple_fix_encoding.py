#!/usr/bin/env python3
"""简单修复编码问题"""

import sys
from pathlib import Path

def fix_file_encoding(file_path):
    """修复文件编码"""
    try:
        # 尝试UTF-8读取
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"正常: {file_path.name} - UTF-8")
            return True
        except UnicodeDecodeError:
            # 尝试其他编码
            encodings = ['gbk', 'gb2312', 'latin-1', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # 转换为UTF-8
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"转换: {file_path.name} - {encoding} → UTF-8")
                    return True
                    
                except UnicodeDecodeError:
                    continue
            
            print(f"失败: {file_path.name} - 无法解码")
            return False
            
    except Exception as e:
        print(f"错误: {file_path.name} - {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("用法: python simple_fix_encoding.py <技能路径>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 修复所有.md文件
    md_files = list(skill_path.rglob("*.md"))
    
    print(f"检查 {len(md_files)} 个Markdown文件...")
    
    fixed_count = 0
    for md_file in md_files:
        if fix_file_encoding(md_file):
            fixed_count += 1
    
    print(f"\n修复完成: {fixed_count}/{len(md_files)} 个文件")

if __name__ == "__main__":
    main()