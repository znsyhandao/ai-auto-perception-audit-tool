#!/usr/bin/env python3
"""检查干净的ZIP包"""

import zipfile
import json
from pathlib import Path

def main():
    zip_path = Path("D:/openclaw/releases/AISleepGen_v2.4.2_clean.zip")
    
    print(f"Checking clean ZIP: {zip_path.name}")
    print("=" * 80)
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        all_files = zipf.namelist()
        
        print(f"Total files: {len(all_files)}")
        
        # 检查备份文件
        backup_keywords = ['backup', 'atomic_backup', '_old', '_new', '~']
        backup_files = []
        
        for filename in all_files:
            filename_lower = filename.lower()
            if any(keyword in filename_lower for keyword in backup_keywords):
                backup_files.append(filename)
        
        if backup_files:
            print(f"ERROR: Found {len(backup_files)} backup files")
            for file in backup_files[:5]:
                print(f"  {file}")
            if len(backup_files) > 5:
                print(f"  ... and {len(backup_files) - 5} more")
        else:
            print("OK: No backup files found")
        
        # 检查关键文件
        critical_files = ['skill.py', 'config.yaml', 'SKILL.md', 'package.json', 'skill_info.json', 'CHANGELOG.md']
        missing_files = []
        
        for filename in critical_files:
            if filename not in all_files:
                missing_files.append(filename)
        
        if missing_files:
            print(f"ERROR: Missing critical files: {missing_files}")
        else:
            print("OK: All critical files present")
        
        # 检查版本
        print("\nVersion check:")
        
        if 'skill.py' in all_files:
            with zipf.open('skill.py') as f:
                content = f.read().decode('utf-8')
                if 'version = "2.4.2"' in content:
                    print("  skill.py: 2.4.2")
                else:
                    print("  skill.py: NOT 2.4.2")
        
        if 'package.json' in all_files:
            with zipf.open('package.json') as f:
                data = json.load(f)
                version = data.get('version', 'NOT_FOUND')
                if version == '2.4.2':
                    print(f"  package.json: {version}")
                else:
                    print(f"  package.json: {version} (should be 2.4.2)")
        
        if 'SKILL.md' in all_files:
            with zipf.open('SKILL.md') as f:
                content = f.read().decode('utf-8')
                if '**Version**: 2.4.2' in content:
                    print("  SKILL.md: 2.4.2")
                else:
                    print("  SKILL.md: NOT 2.4.2")
        
        # 检查依赖声明
        print("\nDependency declaration check:")
        if 'package.json' in all_files:
            with zipf.open('package.json') as f:
                data = json.load(f)
                
                # 检查是否有optional_advanced_dependencies
                if 'optional_advanced_dependencies' in data:
                    print("  OK: Has optional_advanced_dependencies field")
                    deps = data['optional_advanced_dependencies']
                    print(f"  Optional deps: {list(deps.keys())}")
                else:
                    print("  WARNING: No optional_advanced_dependencies field")
                
                # 检查security声明
                if 'security' in data:
                    security = data['security']
                    if 'optional_advanced_features' in security:
                        print("  OK: Security has optional_advanced_features")
                    else:
                        print("  WARNING: Security missing optional_advanced_features")
    
    print("\n" + "=" * 80)
    print("Clean ZIP check completed")
    print("=" * 80)

if __name__ == "__main__":
    main()