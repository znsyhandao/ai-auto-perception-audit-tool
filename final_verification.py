#!/usr/bin/env python3
"""最终验证"""

import json
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    target_version = "2.4.2"
    
    print("FINAL VERIFICATION")
    print("=" * 80)
    
    all_ok = True
    
    # 1. skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if f'version = "{target_version}"' in content:
        print(f"✅ skill.py: {target_version}")
    else:
        print(f"❌ skill.py: NOT {target_version}")
        all_ok = False
    
    # 2. package.json
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data['version'] == target_version:
        print(f"✅ package.json: {target_version}")
    else:
        print(f"❌ package.json: {data['version']}")
        all_ok = False
    
    # 3. SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if f'**Version**: {target_version}' in content:
        print(f"✅ SKILL.md: {target_version}")
    else:
        # 检查其他格式
        if target_version in content:
            print(f"⚠️ SKILL.md: contains {target_version} but not in standard format")
        else:
            print(f"❌ SKILL.md: NOT {target_version}")
            all_ok = False
    
    # 4. config.yaml
    config_file = skill_path / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if data['skill']['version'] == target_version:
        print(f"✅ config.yaml: {target_version}")
    else:
        print(f"❌ config.yaml: {data['skill']['version']}")
        all_ok = False
    
    # 5. skill_info.json
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if data['version'] == target_version:
        print(f"✅ skill_info.json: {target_version}")
    else:
        print(f"❌ skill_info.json: {data['version']}")
        all_ok = False
    
    # 6. CHANGELOG.md
    changelog_file = skill_path / "CHANGELOG.md"
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if f'Current Version: {target_version}' in content:
        print(f"✅ CHANGELOG.md: {target_version}")
    else:
        print(f"❌ CHANGELOG.md: NOT {target_version}")
        all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print(f"🎉 SUCCESS: All files are version {target_version}")
    else:
        print(f"❌ FAILURE: Version inconsistency")
    
    print("=" * 80)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())