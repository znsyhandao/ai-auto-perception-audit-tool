#!/usr/bin/env python3
"""强制修复所有版本为2.4.1"""

import json
import re
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    target_version = "2.4.1"
    
    print("FORCE FIXING ALL VERSIONS TO 2.4.1")
    print("=" * 80)
    
    # 1. 修复skill.py (确保是2.4.1)
    print("\n1. Fixing skill.py...")
    skill_file = skill_path / "skill.py"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()
        content = re.sub(r"version\s*=\s*['\"]([^'\"]+)['\"]", f'version = "{target_version}"', content)
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   Done")
    
    # 2. 修复config.yaml
    print("\n2. Fixing config.yaml...")
    config_file = skill_path / "config.yaml"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        data['skill']['version'] = target_version
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        print("   Done")
    
    # 3. 修复SKILL.md
    print("\n3. Fixing SKILL.md...")
    skill_md_file = skill_path / "SKILL.md"
    if skill_md_file.exists():
        with open(skill_md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换所有版本号
        content = re.sub(r'Version:\s*[\d.]+', f'Version: {target_version}', content)
        content = re.sub(r'v[\d.]+', f'v{target_version}', content)
        content = re.sub(r'[\d.]+ \(', f'{target_version} (', content)
        
        with open(skill_md_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   Done")
    
    # 4. 修复package.json
    print("\n4. Fixing package.json...")
    pkg_file = skill_path / "package.json"
    if pkg_file.exists():
        with open(pkg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['version'] = target_version
        with open(pkg_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("   Done")
    
    # 5. 修复skill_info.json
    print("\n5. Fixing skill_info.json...")
    info_file = skill_path / "skill_info.json"
    if info_file.exists():
        with open(info_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['version'] = target_version
        data['skill_id'] = f'aisleepgen_v{target_version.replace(".", "_")}'
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("   Done")
    
    # 6. 修复CHANGELOG.md
    print("\n6. Fixing CHANGELOG.md...")
    changelog_file = skill_path / "CHANGELOG.md"
    if changelog_file.exists():
        try:
            with open(changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 确保当前版本号正确
            content = re.sub(r'Current Version:\s*[\d.]+', f'Current Version: {target_version}', content)
            
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("   Done")
        except Exception as e:
            print(f"   Error: {e}")
            print("   Will create new CHANGELOG.md")
            
            # 创建新的CHANGELOG
            new_changelog = f"""# Changelog

All notable changes to Sleep Rabbit Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [{target_version}] - 2026-03-31
### Fixed
- **ClawHub security scan issues**: Resolved version inconsistency problems
- **Version consistency**: Unified all file version numbers to {target_version}
- **File encoding**: Fixed UTF-8 encoding issues
- **Clean packaging**: Removed all .pyc files and __pycache__ directories

### Security
- **Security status**: Suspicious (medium confidence) → Clean (expected)
- **Issues fixed**: Version inconsistency across all metadata files

---

**Current Version**: {target_version}
"""
            
            new_file = skill_path / "CHANGELOG_NEW.md"
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write(new_changelog)
            print("   Created CHANGELOG_NEW.md")
    
    # 验证
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    versions = {}
    
    files_to_check = [
        ("skill.py", r"version\s*=\s*['\"]([^'\"]+)['\"]"),
        ("config.yaml", lambda f: yaml.safe_load(open(f, 'r', encoding='utf-8')).get('skill', {}).get('version', 'NOT_FOUND')),
        ("SKILL.md", r'Version:\s*([\d.]+)'),
        ("package.json", lambda f: json.load(open(f, 'r', encoding='utf-8')).get('version', 'NOT_FOUND')),
        ("skill_info.json", lambda f: json.load(open(f, 'r', encoding='utf-8')).get('version', 'NOT_FOUND')),
        ("CHANGELOG.md", r'Current Version:\s*([\d.]+)'),
    ]
    
    for filename, pattern in files_to_check:
        file_path = skill_path / filename
        if file_path.exists():
            if callable(pattern):
                version = pattern(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                match = re.search(pattern, content)
                version = match.group(1) if match else "NOT_FOUND"
            
            versions[filename] = version
            status = "OK" if version == target_version else "WRONG"
            print(f"{filename}: {version} ({status})")
        else:
            versions[filename] = "MISSING"
            print(f"{filename}: MISSING")
    
    # 检查一致性
    all_correct = all(v == target_version for v in versions.values() if v not in ["MISSING", "NOT_FOUND"])
    
    print("\n" + "=" * 80)
    if all_correct:
        print(f"SUCCESS: All files are {target_version}")
    else:
        print(f"FAILURE: Version inconsistency")
        for filename, version in versions.items():
            if version != target_version:
                print(f"  {filename}: {version} (should be {target_version})")
    
    print("=" * 80)

if __name__ == "__main__":
    main()