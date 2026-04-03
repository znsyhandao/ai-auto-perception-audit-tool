#!/usr/bin/env python3
"""修复所有版本号"""

import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime

def fix_skill_md(file_path):
    """修复SKILL.md"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复版本号
    content = re.sub(r'Version:\s*2\.4\.0', 'Version: 2.4.1', content)
    content = re.sub(r'Version 2\.4\.0', 'Version 2.4.1', content)
    content = re.sub(r'v2\.4\.0', 'v2.4.1', content)
    content = re.sub(r'2\.4\.0 \(', '2.4.1 (', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed: {file_path.name} -> 2.4.1")

def fix_package_json(file_path):
    """修复package.json"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = '2.4.1'
    data['name'] = 'aisleepgen-sleep-health'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed: {file_path.name} -> 2.4.1")

def fix_skill_info_json(file_path):
    """修复skill_info.json"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = '2.4.1'
    data['skill_id'] = 'aisleepgen_v2.4.1'
    data['release_date'] = datetime.now().isoformat()
    data['release_type'] = 'clawhub_compliant_final'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed: {file_path.name} -> 2.4.1")

def fix_config_yaml(file_path):
    """修复config.yaml"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    data['skill']['version'] = '2.4.1'
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    print(f"Fixed: {file_path.name} -> 2.4.1")

def fix_changelog(file_path):
    """修复CHANGELOG.md中的当前版本"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 确保当前版本是2.4.1
    if 'Current Version: 2.4.1' not in content:
        content = re.sub(r'Current Version:\s*[\d.]+', 'Current Version: 2.4.1', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Verified: {file_path.name} current version is 2.4.1")

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    print("=" * 80)
    print("修复所有版本号到2.4.1")
    print("=" * 80)
    
    files_to_fix = [
        (skill_path / "SKILL.md", fix_skill_md),
        (skill_path / "package.json", fix_package_json),
        (skill_path / "skill_info.json", fix_skill_info_json),
        (skill_path / "config.yaml", fix_config_yaml),
        (skill_path / "CHANGELOG.md", fix_changelog),
    ]
    
    for file_path, fix_func in files_to_fix:
        if file_path.exists():
            try:
                fix_func(file_path)
            except Exception as e:
                print(f"Error fixing {file_path.name}: {e}")
        else:
            print(f"Missing: {file_path.name}")
    
    print("\n" + "=" * 80)
    print("验证修复...")
    
    # 验证所有版本
    versions = {}
    
    # skill.py
    skill_file = skill_path / "skill.py"
    if skill_file.exists():
        content = skill_file.read_text(encoding='utf-8')
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
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
        content = skill_md_file.read_text(encoding='utf-8')
        match = re.search(r'Version:\s*([\d.]+)', content)
        versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
    
    print("\n版本检查:")
    all_2_4_1 = True
    for filename, version in versions.items():
        if version == '2.4.1':
            print(f"  ✅ {filename}: {version}")
        else:
            print(f"  ❌ {filename}: {version} (应该是2.4.1)")
            all_2_4_1 = False
    
    if all_2_4_1:
        print("\n✅ 所有版本号已统一为2.4.1")
    else:
        print("\n❌ 版本号不一致，需要手动修复")

if __name__ == "__main__":
    main()