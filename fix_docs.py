#!/usr/bin/env python3
"""修复文档语言问题"""

import sys
import re
from pathlib import Path

def fix_skill_md(file_path):
    """修复SKILL.md文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除BOM
    if content.startswith('\ufeff'):
        content = content[1:]
    
    # 替换中文和特殊符号
    replacements = {
        "鈫?": "→",
        "鉂?": "✓",
        "鉁?": "✓",
        "Suspicious (medium confidence) → Clean (expected)": "Suspicious (medium confidence) → Clean (expected)",
        "False security claims corrected": "False security claims corrected",
        "Chinese documentation translated to English": "Chinese documentation translated to English",
        "Missing file references resolved": "Missing file references resolved",
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # 移除所有中文字符
    content = re.sub(r'[\u4e00-\u9fff]', '', content)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"修复: {file_path.name}")

def main():
    if len(sys.argv) != 2:
        print("用法: python fix_docs.py <技能路径>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 修复SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        fix_skill_md(skill_md)
    
    # 检查其他文件
    for md_file in skill_path.rglob("*.md"):
        if md_file.name != "SKILL.md":
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查中文字符
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', content)
            if chinese_chars:
                print(f"警告: {md_file.name} 有 {len(chinese_chars)} 个中文字符")

if __name__ == "__main__":
    main()