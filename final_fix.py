#!/usr/bin/env python3
"""最终修复版本问题"""

import json
import re
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Final version fix")
    print("=" * 80)
    
    # 修复所有文件为2.4.1
    print("\n1. Fixing package.json...")
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        pkg = json.load(f)
    pkg['version'] = '2.4.1'
    with open(pkg_file, 'w', encoding='utf-8') as f:
        json.dump(pkg, f, indent=2, ensure_ascii=False)
    print("   Done")
    
    print("\n2. Fixing skill_info.json...")
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
    info['version'] = '2.4.1'
    info['skill_id'] = 'aisleepgen_v2_4_1'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print("   Done")
    
    print("\n3. Fixing SKILL.md...")
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有2.4.0为2.4.1
    content = content.replace('Version: 2.4.0', 'Version: 2.4.1')
    content = content.replace('v2.4.0', 'v2.4.1')
    content = content.replace('2.4.0 (', '2.4.1 (')
    
    with open(skill_md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("   Done")
    
    # 验证
    print("\n" + "=" * 80)
    print("Verification:")
    print("=" * 80)
    
    versions = {}
    
    # skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
        versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
        print(f"skill.py: {versions['skill.py']}")
    
    # package.json
    with open(pkg_file, 'r', encoding='utf-8') as f:
        pkg = json.load(f)
        versions["package.json"] = pkg['version']
        print(f"package.json: {versions['package.json']}")
    
    # SKILL.md
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'Version:\s*([\d.]+)', content)
        versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
        print(f"SKILL.md: {versions['SKILL.md']}")
    
    # skill_info.json
    with open(info_file, 'r', encoding='utf-8') as f:
        info = json.load(f)
        versions["skill_info.json"] = info['version']
        print(f"skill_info.json: {versions['skill_info.json']}")
    
    # 检查一致性
    print("\n" + "=" * 80)
    all_2_4_1 = all(v == '2.4.1' for v in versions.values())
    
    if all_2_4_1:
        print("✅ SUCCESS: All files are 2.4.1")
    else:
        print("❌ FAILURE: Version inconsistency")
        for filename, version in versions.items():
            if version != '2.4.1':
                print(f"   {filename}: {version} (should be 2.4.1)")
    
    print("=" * 80)

if __name__ == "__main__":
    main()