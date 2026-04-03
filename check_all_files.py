#!/usr/bin/env python3
"""检查所有文件状态"""

import os
import json
import re
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Checking all files status...")
    print("=" * 80)
    
    # 检查所有关键文件
    critical_files = [
        "skill.py",
        "config.yaml",
        "SKILL.md",
        "README.md",
        "CHANGELOG.md",
        "package.json",
        "skill_info.json"
    ]
    
    print("\n1. File existence and access:")
    all_exist = True
    for filename in critical_files:
        file_path = skill_path / filename
        if file_path.exists():
            try:
                # 测试读取
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)
                # 测试写入
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write('')
                print(f"   ✅ {filename}: Exists and accessible")
            except Exception as e:
                print(f"   ❌ {filename}: Exists but not accessible - {e}")
                all_exist = False
        else:
            print(f"   ❌ {filename}: Does not exist")
            all_exist = False
    
    if not all_exist:
        print("\nERROR: Some files missing or not accessible")
        return 1
    
    print("\n2. Version consistency:")
    
    versions = {}
    
    # skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
    versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
    print(f"   skill.py: {versions['skill.py']}")
    
    # config.yaml
    config_file = skill_path / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    versions["config.yaml"] = data.get('skill', {}).get('version', 'NOT_FOUND')
    print(f"   config.yaml: {versions['config.yaml']}")
    
    # SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # 查找版本号
    if 'Version: 2.4.1' in content:
        versions["SKILL.md"] = '2.4.1'
    elif '2.4.1' in content:
        versions["SKILL.md"] = '2.4.1'
    else:
        versions["SKILL.md"] = 'NOT_FOUND'
    print(f"   SKILL.md: {versions['SKILL.md']}")
    
    # package.json
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    versions["package.json"] = data.get('version', 'NOT_FOUND')
    print(f"   package.json: {versions['package.json']}")
    
    # skill_info.json
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    versions["skill_info.json"] = data.get('version', 'NOT_FOUND')
    print(f"   skill_info.json: {versions['skill_info.json']}")
    
    # CHANGELOG.md
    changelog_file = skill_path / "CHANGELOG.md"
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'Current Version: 2.4.1' in content:
        versions["CHANGELOG.md"] = '2.4.1'
    else:
        versions["CHANGELOG.md"] = 'NOT_FOUND'
    print(f"   CHANGELOG.md: {versions['CHANGELOG.md']}")
    
    # 检查一致性
    print("\n3. Version consistency check:")
    unique_versions = set(versions.values())
    
    if len(unique_versions) == 1 and '2.4.1' in unique_versions:
        print(f"   ✅ All files are version 2.4.1")
        consistent = True
    else:
        print(f"   ❌ Version inconsistency:")
        for filename, version in versions.items():
            print(f"      {filename}: {version}")
        consistent = False
    
    print("\n" + "=" * 80)
    if all_exist and consistent:
        print("SUCCESS: All files exist, accessible, and version consistent")
        return 0
    else:
        print("FAILURE: Some issues found")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())