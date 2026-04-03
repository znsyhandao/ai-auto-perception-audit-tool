#!/usr/bin/env python3
"""简单版本修复 - 只修复版本号，不更新CHANGELOG"""

import json
import re
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Simple version fix - ensuring all files are 2.4.1")
    print("=" * 80)
    
    # 1. 检查当前版本
    versions = {}
    
    # skill.py
    skill_file = skill_path / "skill.py"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
        versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
    
    # package.json
    pkg_file = skill_path / "package.json"
    if pkg_file.exists():
        with open(pkg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        versions["package.json"] = data.get('version', 'NOT_FOUND')
    
    # SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    if skill_md_file.exists():
        with open(skill_md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'Version:\s*([\d.]+)', content)
        versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
    
    # skill_info.json
    info_file = skill_path / "skill_info.json"
    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        versions["skill_info.json"] = data.get('version', 'NOT_FOUND')
    
    print("\nCurrent versions:")
    for filename, version in versions.items():
        print(f"  {filename}: {version}")
    
    # 2. 检查是否都是2.4.1
    all_2_4_1 = all(v == '2.4.1' for v in versions.values())
    
    if all_2_4_1:
        print("\n✅ All files are already 2.4.1")
    else:
        print(f"\n❌ Not all files are 2.4.1")
        
        # 修复不一致的文件
        print("\nFixing inconsistencies...")
        
        # 如果package.json不是2.4.1，修复它
        if versions.get("package.json") != '2.4.1':
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['version'] = '2.4.1'
            with open(pkg_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("  Fixed package.json")
        
        # 如果skill_info.json不是2.4.1，修复它
        if versions.get("skill_info.json") != '2.4.1':
            with open(info_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['version'] = '2.4.1'
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("  Fixed skill_info.json")
        
        # 如果SKILL.md不是2.4.1，修复它
        if versions.get("SKILL.md") != '2.4.1':
            with open(skill_md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('Version: 2.4.0', 'Version: 2.4.1')
            content = content.replace('v2.4.0', 'v2.4.1')
            with open(skill_md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("  Fixed SKILL.md")
        
        print("\n✅ All inconsistencies fixed")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()