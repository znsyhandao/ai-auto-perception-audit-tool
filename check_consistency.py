#!/usr/bin/env python3
"""检查文件夹和ZIP文件的一致性"""

import os
import zipfile
from pathlib import Path

def main():
    releases_dir = Path("D:/openclaw/releases")
    
    print("FOLDER AND ZIP CONSISTENCY CHECK")
    print("=" * 80)
    
    # 检查文件夹
    folder_name = "AISleepGen_2.4.2"
    folder_path = releases_dir / folder_name
    
    if not folder_path.exists():
        print(f"ERROR: Folder does not exist: {folder_path}")
        return 1
    
    print(f"OK: Folder: {folder_name}")
    
    # 检查ZIP文件
    zip_name = "AISleepGen_v2.4.2_clawhub_ready.zip"
    zip_path = releases_dir / zip_name
    
    if not zip_path.exists():
        print(f"ERROR: ZIP file does not exist: {zip_path}")
        return 1
    
    print(f"OK: ZIP file: {zip_name}")
    
    # 检查名称一致性
    print("\nName consistency check:")
    folder_version = folder_name.split("_")[-1]  # 2.4.2
    zip_version = zip_name.split("_")[1].replace("v", "")  # 2.4.2
    
    if folder_version == zip_version:
        print(f"  OK: Folder version: {folder_version}")
        print(f"  OK: ZIP version: {zip_version}")
        print(f"  OK: Versions match")
    else:
        print(f"  ERROR: Folder version: {folder_version}")
        print(f"  ERROR: ZIP version: {zip_version}")
        print(f"  ERROR: Versions do not match")
        return 1
    
    # 检查文件数量一致性
    print("\nFile count consistency:")
    
    # 文件夹中的文件数
    folder_files = list(folder_path.rglob("*"))
    folder_file_count = len([f for f in folder_files if f.is_file()])
    print(f"  Folder files: {folder_file_count}")
    
    # ZIP中的文件数
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zip_file_count = len(zipf.namelist())
            print(f"  ZIP files: {zip_file_count}")
            
            # 检查关键文件
            critical_files = ['skill.py', 'config.yaml', 'SKILL.md', 'package.json']
            print("\n  Critical files in ZIP:")
            all_critical_in_zip = True
            for filename in critical_files:
                if filename in zipf.namelist():
                    print(f"    OK: {filename}")
                else:
                    print(f"    ERROR: {filename} MISSING")
                    all_critical_in_zip = False
            
            if not all_critical_in_zip:
                print("  ERROR: Some critical files missing from ZIP")
                return 1
            
    except Exception as e:
        print(f"  ERROR: Cannot read ZIP file: {e}")
        return 1
    
    # 检查文件数量是否大致匹配
    if abs(folder_file_count - zip_file_count) <= 5:  # 允许少量差异
        print(f"  OK: File counts are consistent")
    else:
        print(f"  ERROR: File count mismatch: folder={folder_file_count}, zip={zip_file_count}")
        return 1
    
    print("\n" + "=" * 80)
    print("SUCCESS: Folder and ZIP are consistent")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())