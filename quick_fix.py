#!/usr/bin/env python3
"""快速修复版本号"""

import json
import re
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Fixing version numbers...")
    
    # 1. 修复package.json
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        pkg = json.load(f)
    pkg['version'] = '2.4.1'
    pkg['name'] = 'aisleepgen-sleep-health'
    with open(pkg_file, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2, ensure_ascii=False)
    print("Fixed package.json")
    
    # 2. 修复skill_info.json
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    info['version'] = '2.4.1'
    info['skill_id'] = 'aisleepgen_v2.4.1'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("Fixed skill_info.json")
    
    # 3. 修复SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有2.4.0为2.4.1
    content = content.replace('Version: 2.4.0', 'Version: 2.4.1')
    content = content.replace('v2.4.0', 'v2.4.1')
    content = content.replace('2.4.0 (', '2.4.1 (')
    
    with open(skill_md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed SKILL.md")
    
    # 4. 验证
    print("\nVersion verification:")
    
    # skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        skill_content = f.read()
        match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", skill_content)
        skill_version = match.group(1) if match else "NOT_FOUND"
        print(f"skill.py: {skill_version}")
    
    # package.json
    with open(pkg_file, 'r', encoding='utf-8') as f:
        pkg = json.load(f)
        print(f"package.json: {pkg['version']}")
    
    # SKILL.md
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'Version:\s*([\d.]+)', content)
        skill_md_version = match.group(1) if match else "NOT_FOUND"
        print(f"SKILL.md: {skill_md_version}")
    
    # 检查是否一致
    versions = [skill_version, pkg['version'], skill_md_version]
    if all(v == '2.4.1' for v in versions):
        print("\nSUCCESS: All versions are 2.4.1")
    else:
        print(f"\nFAILURE: Versions not consistent: {versions}")

if __name__ == "__main__":
    main()