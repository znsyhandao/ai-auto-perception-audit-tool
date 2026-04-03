#!/usr/bin/env python3
"""手动修复到2.4.2"""

import json
import re
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    target_version = "2.4.2"
    
    print("MANUAL FIX TO 2.4.2")
    print("=" * 80)
    
    # 1. skill.py
    print("\n1. Fixing skill.py...")
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换版本号
    content = re.sub(r'version\s*=\s*["\']2\.4\.1["\']', f'version = "{target_version}"', content)
    
    with open(skill_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("   Done")
    
    # 2. config.yaml
    print("\n2. Fixing config.yaml...")
    config_file = skill_path / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    data['skill']['version'] = target_version
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    print("   Done")
    
    # 3. SKILL.md
    print("\n3. Fixing SKILL.md...")
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有2.4.1为2.4.2
    content = content.replace('Version: 2.4.1', f'Version: {target_version}')
    content = content.replace('v2.4.1', f'v{target_version}')
    content = content.replace('2.4.1 (', f'{target_version} (')
    
    with open(skill_md_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("   Done")
    
    # 4. package.json
    print("\n4. Fixing package.json...")
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = target_version
    
    with open(pkg_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("   Done")
    
    # 5. skill_info.json
    print("\n5. Fixing skill_info.json...")
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['version'] = target_version
    data['skill_id'] = f'aisleepgen_v{target_version.replace(".", "_")}'
    
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("   Done")
    
    # 6. CHANGELOG.md (已经修复了)
    print("\n6. CHANGELOG.md already fixed")
    
    # 验证
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    
    # 快速检查
    checks = [
        ("skill.py", lambda: 'version = "2.4.2"' in open(skill_file, 'r', encoding='utf-8').read()),
        ("package.json", lambda: json.load(open(pkg_file, 'r', encoding='utf-8'))['version'] == target_version),
        ("SKILL.md", lambda: f'Version: {target_version}' in open(skill_md_file, 'r', encoding='utf-8').read()),
        ("config.yaml", lambda: yaml.safe_load(open(config_file, 'r', encoding='utf-8'))['skill']['version'] == target_version),
        ("skill_info.json", lambda: json.load(open(info_file, 'r', encoding='utf-8'))['version'] == target_version),
        ("CHANGELOG.md", lambda: f'Current Version: {target_version}' in open(skill_path / "CHANGELOG.md", 'r', encoding='utf-8').read()),
    ]
    
    all_ok = True
    for filename, check_func in checks:
        try:
            if check_func():
                print(f"OK: {filename}")
            else:
                print(f"ERROR: {filename}")
                all_ok = False
        except Exception as e:
            print(f"ERROR: {filename} - {e}")
            all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print(f"SUCCESS: All files are {target_version}")
    else:
        print(f"FAILURE: Some files not updated")
    
    print("=" * 80)

if __name__ == "__main__":
    main()