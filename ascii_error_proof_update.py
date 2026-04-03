#!/usr/bin/env python3
"""
ASCII防错版本更新 - 无Unicode字符
"""

import sys
import json
import yaml
import re
import shutil
from pathlib import Path
from datetime import datetime

def main():
    if len(sys.argv) != 3:
        print("Usage: python ascii_error_proof_update.py <skill_path> <new_version>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    new_version = sys.argv[2]
    
    print("=" * 80)
    print("ERROR-PROOF VERSION UPDATE")
    print("=" * 80)
    print(f"Skill path: {skill_path}")
    print(f"New version: {new_version}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 验证版本号格式
    if not re.match(r'^\d+\.\d+\.\d+$', new_version):
        print("ERROR: Invalid version format")
        sys.exit(1)
    
    # 备份文件
    backups = {}
    files_to_update = [
        "skill.py",
        "config.yaml", 
        "SKILL.md",
        "README.md",
        "CHANGELOG.md",
        "package.json",
        "skill_info.json"
    ]
    
    print("\n[1] BACKING UP FILES")
    for filename in files_to_update:
        file_path = skill_path / filename
        if file_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.parent / f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
            shutil.copy2(file_path, backup_path)
            backups[str(file_path)] = backup_path
            print(f"  BACKUP: {filename}")
    
    try:
        # 更新所有文件
        print("\n[2] UPDATING FILES")
        
        # 1. skill.py
        print("\n  Updating skill.py...")
        skill_file = skill_path / "skill.py"
        if skill_file.exists():
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'version\s*=\s*["\']([^"\']+)["\']', f'version = "{new_version}"', content)
            with open(skill_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("    OK")
        
        # 2. config.yaml
        print("\n  Updating config.yaml...")
        config_file = skill_path / "config.yaml"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            data['skill']['version'] = new_version
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            print("    OK")
        
        # 3. SKILL.md
        print("\n  Updating SKILL.md...")
        skill_md_file = skill_path / "SKILL.md"
        if skill_md_file.exists():
            with open(skill_md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'Version:\s*[\d.]+', f'Version: {new_version}', content)
            content = re.sub(r'v[\d.]+', f'v{new_version}', content)
            with open(skill_md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("    OK")
        
        # 4. package.json
        print("\n  Updating package.json...")
        pkg_file = skill_path / "package.json"
        if pkg_file.exists():
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['version'] = new_version
            with open(pkg_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("    OK")
        
        # 5. skill_info.json
        print("\n  Updating skill_info.json...")
        info_file = skill_path / "skill_info.json"
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['version'] = new_version
            data['skill_id'] = f'aisleepgen_v{new_version.replace(".", "_")}'
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("    OK")
        
        # 6. CHANGELOG.md
        print("\n  Updating CHANGELOG.md...")
        changelog_file = skill_path / "CHANGELOG.md"
        if changelog_file.exists():
            with open(changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()
            content = re.sub(r'Current Version:\s*[\d.]+', f'Current Version: {new_version}', content)
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print("    OK")
        
        # 验证所有更新
        print("\n[3] VERIFYING ALL UPDATES")
        
        versions = {}
        
        # skill.py
        if skill_file.exists():
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            versions["skill.py"] = match.group(1) if match else "NOT_FOUND"
        
        # config.yaml
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            versions["config.yaml"] = data.get('skill', {}).get('version', 'NOT_FOUND')
        
        # SKILL.md
        if skill_md_file.exists():
            with open(skill_md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'Version:\s*([\d.]+)', content)
            versions["SKILL.md"] = match.group(1) if match else "NOT_FOUND"
        
        # package.json
        if pkg_file.exists():
            with open(pkg_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            versions["package.json"] = data.get('version', 'NOT_FOUND')
        
        print("\n  Version check:")
        all_correct = True
        for filename, version in versions.items():
            if version == new_version:
                print(f"    PASS: {filename} = {version}")
            else:
                print(f"    FAIL: {filename} = {version} (expected {new_version})")
                all_correct = False
        
        if not all_correct:
            raise Exception("Version inconsistency detected")
        
        print("\n" + "=" * 80)
        print("SUCCESS: All versions updated to " + new_version)
        print("=" * 80)
        
        # 生成报告
        report = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "skill_path": str(skill_path),
            "new_version": new_version,
            "versions": versions
        }
        
        report_file = skill_path.parent / f"version_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved: {report_file}")
        
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"FAILURE: {e}")
        print("=" * 80)
        
        # 回滚
        print("\n[ROLLBACK] Restoring backups...")
        for original_path, backup_path in backups.items():
            original_path = Path(original_path)
            backup_path = Path(backup_path)
            if backup_path.exists():
                shutil.copy2(backup_path, original_path)
                print(f"  RESTORED: {original_path.name}")
        
        print("\nAll changes rolled back")
        sys.exit(1)

if __name__ == "__main__":
    main()