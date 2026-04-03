#!/usr/bin/env python3
"""检查发布文件夹和ZIP文件"""

import os
import zipfile
from pathlib import Path

def check_release_folder():
    """检查发布文件夹"""
    print("Checking release folder...")
    print("=" * 80)
    
    folder_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    
    if not folder_path.exists():
        print(f"ERROR: Release folder does not exist: {folder_path}")
        return False
    
    print(f"OK: Release folder exists: {folder_path}")
    
    # 检查文件数量
    all_items = list(folder_path.rglob('*'))
    files = [f for f in all_items if f.is_file()]
    dirs = [d for d in all_items if d.is_dir()]
    
    print(f"  Total files: {len(files)}")
    print(f"  Total directories: {len(dirs)}")
    
    # 检查关键文件
    critical_files = [
        'skill.py',
        'config.yaml',
        'SKILL.md',
        'README.md',
        'CHANGELOG.md',
        'package.json',
        'skill_info.json'
    ]
    
    print("\nCritical files check:")
    all_critical_exist = True
    for filename in critical_files:
        file_path = folder_path / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  OK: {filename} ({size} bytes)")
        else:
            print(f"  ERROR: {filename} MISSING")
            all_critical_exist = False
    
    # 检查.pyc文件
    print("\nChecking for .pyc files...")
    pyc_files = list(folder_path.rglob('*.pyc'))
    if pyc_files:
        print(f"  ERROR: Found {len(pyc_files)} .pyc files")
        for pyc in pyc_files[:5]:  # 只显示前5个
            print(f"    {pyc.relative_to(folder_path)}")
        if len(pyc_files) > 5:
            print(f"    ... and {len(pyc_files) - 5} more")
        all_critical_exist = False
    else:
        print("  OK: No .pyc files found")
    
    # 检查__pycache__目录
    print("\nChecking for __pycache__ directories...")
    cache_dirs = list(folder_path.rglob('__pycache__'))
    if cache_dirs:
        print(f"  ERROR: Found {len(cache_dirs)} __pycache__ directories")
        for cache in cache_dirs:
            print(f"    {cache.relative_to(folder_path)}")
        all_critical_exist = False
    else:
        print("  OK: No __pycache__ directories found")
    
    return all_critical_exist

def check_zip_file():
    """检查ZIP文件"""
    print("\n" + "=" * 80)
    print("Checking ZIP file...")
    print("=" * 80)
    
    zip_path = Path("D:/openclaw/releases/AISleepGen_v2.4.1_final_unified.zip")
    
    if not zip_path.exists():
        print(f"ERROR: ZIP file does not exist: {zip_path}")
        
        # 检查其他ZIP文件
        print("\nAvailable ZIP files:")
        releases_dir = Path("D:/openclaw/releases")
        zip_files = list(releases_dir.glob("*.zip"))
        for zip_file in zip_files:
            size = zip_file.stat().st_size
            print(f"  {zip_file.name} ({size} bytes)")
        
        return False
    
    print(f"OK: ZIP file exists: {zip_path}")
    size = zip_path.stat().st_size
    print(f"  Size: {size} bytes ({size/1024:.1f} KB)")
    
    # 检查ZIP内容
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            print(f"  Files in ZIP: {len(file_list)}")
            
            # 检查关键文件
            critical_in_zip = [
                'skill.py',
                'config.yaml',
                'SKILL.md',
                'README.md',
                'CHANGELOG.md',
                'package.json',
                'skill_info.json'
            ]
            
            print("\n  Critical files in ZIP:")
            all_in_zip = True
            for filename in critical_in_zip:
                if filename in file_list:
                    info = zipf.getinfo(filename)
                    print(f"    OK: {filename} ({info.file_size} bytes)")
                else:
                    print(f"    ERROR: {filename} NOT in ZIP")
                    all_in_zip = False
            
            # 检查.pyc文件
            pyc_in_zip = [f for f in file_list if f.endswith('.pyc')]
            if pyc_in_zip:
                print(f"\n  ERROR: Found {len(pyc_in_zip)} .pyc files in ZIP")
                all_in_zip = False
            
            # 检查__pycache__目录
            cache_in_zip = [f for f in file_list if '__pycache__' in f]
            if cache_in_zip:
                print(f"\n  ERROR: Found {len(cache_in_zip)} __pycache__ items in ZIP")
                all_in_zip = False
            
            return all_in_zip
            
    except Exception as e:
        print(f"ERROR: Cannot read ZIP file - {e}")
        return False

def main():
    """主函数"""
    print("RELEASE AUDIT")
    print("=" * 80)
    
    # 检查发布文件夹
    folder_ok = check_release_folder()
    
    # 检查ZIP文件
    zip_ok = check_zip_file()
    
    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)
    
    if folder_ok and zip_ok:
        print("SUCCESS: Both release folder and ZIP file are clean")
        return 0
    else:
        print("FAILURE: Issues found")
        if not folder_ok:
            print("  - Release folder has issues")
        if not zip_ok:
            print("  - ZIP file has issues")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())