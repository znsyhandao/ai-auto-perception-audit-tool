#!/usr/bin/env python3
"""直接检查文件"""

import json
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Direct file check")
    print("=" * 80)
    
    # skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'version = "2.4.2"' in content:
            print("skill.py: 2.4.2")
        elif 'version = "2.4.1"' in content:
            print("skill.py: 2.4.1")
        else:
            print("skill.py: version not found")
    
    # package.json
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"package.json: {data['version']}")
    
    # SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Version: 2.4.2' in content:
            print("SKILL.md: 2.4.2")
        elif 'Version: 2.4.1' in content:
            print("SKILL.md: 2.4.1")
        else:
            print("SKILL.md: version not found")
    
    # config.yaml
    config_file = skill_path / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'version: 2.4.2' in content:
            print("config.yaml: 2.4.2")
        elif 'version: 2.4.1' in content:
            print("config.yaml: 2.4.1")
        else:
            print("config.yaml: version not found")
    
    # skill_info.json
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"skill_info.json: {data['version']}")
    
    # CHANGELOG.md
    changelog_file = skill_path / "CHANGELOG.md"
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Current Version: 2.4.2' in content:
            print("CHANGELOG.md: 2.4.2")
        elif 'Current Version: 2.4.1' in content:
            print("CHANGELOG.md: 2.4.1")
        else:
            print("CHANGELOG.md: version not found")
    
    print("=" * 80)

if __name__ == "__main__":
    main()