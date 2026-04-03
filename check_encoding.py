#!/usr/bin/env python3
"""检查文件编码"""

import sys
from pathlib import Path
import chardet

def check_file_encoding(file_path):
    """检查文件编码"""
    try:
        # 尝试UTF-8读取
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return "UTF-8", True, None
    except UnicodeDecodeError as e:
        # 检测编码
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
        
        return result['encoding'], False, str(e)

def main():
    if len(sys.argv) != 2:
        print("用法: python check_encoding.py <路径>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 检查所有.md文件
    md_files = list(skill_path.rglob("*.md"))
    
    print(f"检查 {len(md_files)} 个.md文件...")
    print("-" * 80)
    
    problem_files = []
    
    for md_file in md_files:
        encoding, is_utf8, error = check_file_encoding(md_file)
        
        if is_utf8:
            print(f"✅ {md_file.name}: UTF-8")
        else:
            print(f"❌ {md_file.name}: {encoding} (错误: {error})")
            problem_files.append((md_file, encoding, error))
    
    print("-" * 80)
    
    if problem_files:
        print(f"\n发现 {len(problem_files)} 个编码问题:")
        for file_path, encoding, error in problem_files:
            print(f"  - {file_path.name}: {encoding}")
        
        # 修复建议
        print("\n修复建议:")
        print("1. 删除备份文件:")
        for file_path, _, _ in problem_files:
            if "backup" in file_path.name or "OLD" in file_path.name:
                print(f"   del \"{file_path}\"")
        
        print("\n2. 转换编码:")
        for file_path, encoding, _ in problem_files:
            if "backup" not in file_path.name and "OLD" not in file_path.name:
                print(f"   # 转换 {file_path.name} 从 {encoding} 到 UTF-8")
    else:
        print("✅ 所有文件都是UTF-8编码")

if __name__ == "__main__":
    main()