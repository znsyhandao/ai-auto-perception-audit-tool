#!/usr/bin/env python3
"""简单编码检查"""

import sys
from pathlib import Path

def try_read_file(file_path):
    """尝试读取文件"""
    encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return encoding, True, None
        except UnicodeDecodeError as e:
            last_error = e
    
    return None, False, str(last_error)

def main():
    if len(sys.argv) != 2:
        print("用法: python simple_encoding_check.py <路径>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 只检查主要的.md文件，忽略备份
    main_files = [
        skill_path / "CHANGELOG.md",
        skill_path / "README.md",
        skill_path / "SKILL.md",
        skill_path / "RELEASE_NOTES.md"
    ]
    
    print("检查主要文件编码...")
    print("-" * 80)
    
    for file_path in main_files:
        if file_path.exists():
            encoding, success, error = try_read_file(file_path)
            
            if success:
                print(f"✅ {file_path.name}: {encoding}")
            else:
                print(f"❌ {file_path.name}: 无法读取 ({error})")
        else:
            print(f"⚠️  {file_path.name}: 文件不存在")
    
    print("-" * 80)
    
    # 检查是否有备份文件
    backup_files = list(skill_path.rglob("*backup*.md")) + list(skill_path.rglob("*OLD*.md"))
    
    if backup_files:
        print(f"\n发现 {len(backup_files)} 个备份文件:")
        for backup in backup_files[:5]:  # 只显示前5个
            print(f"  - {backup.name}")
        
        if len(backup_files) > 5:
            print(f"  ... 还有 {len(backup_files) - 5} 个")
        
        print("\n建议删除备份文件:")
        print("  del \"D:\\openclaw\\releases\\AISleepGen_2.4.1\\*backup*.md\"")
        print("  del \"D:\\openclaw\\releases\\AISleepGen_2.4.1\\*OLD*.md\"")

if __name__ == "__main__":
    main()