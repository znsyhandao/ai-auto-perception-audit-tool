#!/usr/bin/env python3
"""ASCII最终检查"""

import json
import yaml
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    target_version = "2.4.2"
    
    print("FINAL VERIFICATION")
    print("=" * 80)
    
    results = []
    
    # 1. skill.py
    skill_file = skill_path / "skill.py"
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()
    results.append(("skill.py", f'version = "{target_version}"' in content))
    
    # 2. package.json
    pkg_file = skill_path / "package.json"
    with open(pkg_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results.append(("package.json", data['version'] == target_version))
    
    # 3. SKILL.md
    skill_md_file = skill_path / "SKILL.md"
    with open(skill_md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    results.append(("SKILL.md", f'**Version**: {target_version}' in content))
    
    # 4. config.yaml
    config_file = skill_path / "config.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    results.append(("config.yaml", data['skill']['version'] == target_version))
    
    # 5. skill_info.json
    info_file = skill_path / "skill_info.json"
    with open(info_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    results.append(("skill_info.json", data['version'] == target_version))
    
    # 6. CHANGELOG.md
    changelog_file = skill_path / "CHANGELOG.md"
    with open(changelog_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # 检查两种格式
    ok = f'Current Version: {target_version}' in content or f'**Current Version**: {target_version}' in content
    results.append(("CHANGELOG.md", ok))
    
    # 打印结果
    all_ok = True
    for filename, ok in results:
        status = "OK" if ok else "ERROR"
        print(f"{filename}: {status}")
        if not ok:
            all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print(f"SUCCESS: All files are version {target_version}")
    else:
        print(f"FAILURE: Version inconsistency")
        # 显示具体错误
        for filename, ok in results:
            if not ok:
                print(f"  {filename} is not {target_version}")
    
    print("=" * 80)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())