#!/usr/bin/env python3
"""ASCII版本检查"""

import json
import re
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Checking version 2.4.2 upgrade...")
    print("=" * 80)
    
    # 检查版本
    versions = {}
    
    # skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
    versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
    print(f"skill.py: {versions['skill.py']}")
    
    # config.yaml
    config_file = skill_path / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    versions["config.yaml"] = data.get('skill', {}).get('version', 'NOT_FOUND')
    print(f"config.yaml: {versions['config.yaml']}")
    
    # SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'Version: 2.4.2' in content:
        versions["SKILL.md"] = '2.4.2'
    elif '2.4.2' in content:
        versions["SKILL.md"] = '2.4.2'
    else:
        versions["SKILL.md"] = 'NOT_FOUND'
    print(f"SKILL.md: {versions['SKILL.md']}")
    
    # package.json
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    versions["package.json"] = data.get('version', 'NOT_FOUND')
    print(f"package.json: {versions['package.json']}")
    
    # skill_info.json
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    versions["skill_info.json"] = data.get('version', 'NOT_FOUND')
    print(f"skill_info.json: {versions['skill_info.json']}")
    
    # CHANGELOG.md
    changelog_file = skill_path / "CHANGELOG.md"
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'Current Version: 2.4.2' in content:
        versions["CHANGELOG.md"] = '2.4.2'
    else:
        versions["CHANGELOG.md"] = 'NOT_FOUND'
    print(f"CHANGELOG.md: {versions['CHANGELOG.md']}")
    
    print("=" * 80)
    
    # 检查一致性
    all_2_4_2 = all(v == '2.4.2' for v in versions.values())
    
    if all_2_4_2:
        print("SUCCESS: All files are version 2.4.2")
    else:
        print("ERROR: Version inconsistency")
        for filename, version in versions.items():
            if version != '2.4.2':
                print(f"  {filename}: {version} (should be 2.4.2)")
    
    print("=" * 80)
    
    return 0 if all_2_4_2 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())