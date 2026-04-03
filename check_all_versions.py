#!/usr/bin/env python3
"""检查所有文件版本"""

import json
import re
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("Checking all file versions...")
    print("=" * 80)
    
    versions = {}
    
    # 1. skill.py
    skill_file = skill_path / "skill.py"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r"version\s*=\s*['\"]([^'\"]+)['\"]", content)
        versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
        print(f"skill.py: {versions['skill.py']}")
    
    # 2. config.yaml
    config_file = skill_path / "config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        versions["config.yaml"] = data.get('skill', {}).get('version', 'NOT_FOUND')
        print(f"config.yaml: {versions['config.yaml']}")
    
    # 3. SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    if skill_md_file.exists():
        with open(skill_md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'Version:\s*([\d.]+)', content)
        versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
        print(f"SKILL.md: {versions['SKILL.md']}")
    
    # 4. package.json
    pkg_file = skill_path / "package.json"
    if pkg_file.exists():
        with open(pkg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        versions["package.json"] = data.get('version', 'NOT_FOUND')
        print(f"package.json: {versions['package.json']}")
    
    # 5. skill_info.json
    info_file = skill_path / "skill_info.json"
    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        versions["skill_info.json"] = data.get('version', 'NOT_FOUND')
        print(f"skill_info.json: {versions['skill_info.json']}")
    
    # 6. CHANGELOG.md
    changelog_file = skill_path / "CHANGELOG.md"
    if changelog_file.exists():
        with open(changelog_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'Current Version:\s*([\d.]+)', content)
        versions["CHANGELOG.md"] = match.group(1) if match else "NOT_FOUND"
        print(f"CHANGELOG.md: {versions['CHANGELOG.md']}")
    
    print("=" * 80)
    
    # 检查一致性
    unique_versions = set(versions.values())
    print(f"Unique versions found: {unique_versions}")
    
    if len(unique_versions) == 1:
        version = list(unique_versions)[0]
        print(f"✅ All files are version: {version}")
    else:
        print("❌ Version inconsistency:")
        for filename, version in versions.items():
            print(f"   {filename}: {version}")

if __name__ == "__main__":
    main()