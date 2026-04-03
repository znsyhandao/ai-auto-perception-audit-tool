#!/usr/bin/env python3
"""检查ZIP文件内容"""

import zipfile
import json
import re
from pathlib import Path

def check_zip_version(zip_path):
    """检查ZIP文件中的版本号"""
    print(f"Checking {zip_path.name}...")
    print("-" * 40)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # 检查skill.py版本
            if 'skill.py' in zipf.namelist():
                with zipf.open('skill.py') as f:
                    content = f.read().decode('utf-8')
                    if 'version = "2.4.2"' in content:
                        print("  skill.py: 2.4.2")
                    elif 'version = "2.4.1"' in content:
                        print("  skill.py: 2.4.1")
                    else:
                        print("  skill.py: version not found")
            
            # 检查package.json版本
            if 'package.json' in zipf.namelist():
                with zipf.open('package.json') as f:
                    data = json.load(f)
                    print(f"  package.json: {data.get('version', 'NOT_FOUND')}")
            
            # 检查SKILL.md版本
            if 'SKILL.md' in zipf.namelist():
                with zipf.open('SKILL.md') as f:
                    content = f.read().decode('utf-8')
                    if '**Version**: 2.4.2' in content:
                        print("  SKILL.md: 2.4.2")
                    elif '**Version**: 2.4.1' in content:
                        print("  SKILL.md: 2.4.1")
                    else:
                        print("  SKILL.md: version not found")
            
            # 检查文件数量
            file_count = len(zipf.namelist())
            print(f"  Total files: {file_count}")
            
            # 检查.pyc文件
            pyc_files = [f for f in zipf.namelist() if f.endswith('.pyc')]
            if pyc_files:
                print(f"  WARNING: {len(pyc_files)} .pyc files found")
            else:
                print("  OK: No .pyc files")
            
            return True
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    """主函数"""
    releases_dir = Path("D:/openclaw/releases")
    
    print("ZIP FILES VERSION CHECK")
    print("=" * 80)
    
    # 检查所有ZIP文件
    zip_files = list(releases_dir.glob("*.zip"))
    
    for zip_path in zip_files:
        if check_zip_version(zip_path):
            print()
        else:
            print("  FAILED to check\n")
    
    print("=" * 80)
    
    # 推荐上传的文件
    print("\nRECOMMENDED UPLOAD:")
    latest_zip = releases_dir / "AISleepGen_v2.4.2_clawhub_ready.zip"
    if latest_zip.exists():
        size = latest_zip.stat().st_size
        print(f"  {latest_zip.name} ({size} bytes)")
        print("  This is the latest 2.4.2 version with all fixes")
    else:
        print("  ERROR: Latest ZIP file not found")
    
    print("=" * 80)

if __name__ == "__main__":
    main()