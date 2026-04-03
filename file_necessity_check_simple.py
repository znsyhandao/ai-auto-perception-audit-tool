#!/usr/bin/env python3
"""
文件必要性检查工具 - 简单版本（无Unicode字符）
"""

import os
import zipfile
import sys

def check_file_necessity(zip_path):
    print("=" * 80)
    print("File Necessity Check Tool")
    print("=" * 80)
    
    if not os.path.exists(zip_path):
        print(f"[ERROR] ZIP file not found: {zip_path}")
        return False
    
    zip_size = os.path.getsize(zip_path) / 1024
    print(f"Checking: {zip_path}")
    print(f"Size: {zip_size:.1f} KB")
    
    # 问题文件类型
    problematic_files = {
        '.ps1': 'PowerShell scripts',
        '.bat': 'Batch files',
        '.exe': 'Executable files',
        '.dll': 'DLL files',
        '.sh': 'Shell scripts',
    }
    
    found_problems = []
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        total_files = len(zipf.namelist())
        print(f"Total files in ZIP: {total_files}")
        
        print(f"\nScanning for problematic files...")
        print("-" * 40)
        
        for file in sorted(zipf.namelist()):
            file_lower = file.lower()
            
            # 检查问题文件类型
            for ext, description in problematic_files.items():
                if file_lower.endswith(ext):
                    info = zipf.getinfo(file)
                    found_problems.append({
                        'file': file,
                        'type': ext,
                        'size': info.file_size,
                        'description': description
                    })
                    break
    
    # 输出结果
    print(f"\n" + "=" * 80)
    print("CHECK RESULTS:")
    print("=" * 80)
    
    if found_problems:
        print(f"[FAIL] Found {len(found_problems)} problematic files:")
        for problem in found_problems:
            print(f"  [FAIL] {problem['file']} ({problem['size']} bytes)")
            print(f"     Type: {problem['type']}")
            print(f"     Issue: {problem['description']}")
            print()
    else:
        print(f"[SUCCESS] No problematic file types found!")
    
    # 必需文件检查
    print(f"\nChecking for required files...")
    print("-" * 40)
    
    required_files = [
        'skill.py',
        'config.yaml',
        'package.json',
        'README.md',
        'SKILL.md',
    ]
    
    missing_required = []
    
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zip_files = [f.lower() for f in zipf.namelist()]
        
        for required in required_files:
            found = any(required in f for f in zip_files)
            if not found:
                missing_required.append(required)
            else:
                print(f"  [OK] {required}")
    
    if missing_required:
        print(f"\n[FAIL] Missing required files:")
        for missing in missing_required:
            print(f"  [FAIL] {missing}")
    else:
        print(f"\n[SUCCESS] All required files present!")
    
    # 总体评估
    print(f"\n" + "=" * 80)
    print("OVERALL ASSESSMENT:")
    print("=" * 80)
    
    has_problems = len(found_problems) > 0
    has_missing = len(missing_required) > 0
    
    if has_problems:
        print("[FAIL] Contains problematic files")
        print("Recommendation: Remove .ps1, .bat files")
        return False
    elif has_missing:
        print("[FAIL] Missing required files")
        return False
    else:
        print("[SUCCESS] File necessity check PASSED!")
        print("Ready for ClawHub submission")
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python file_necessity_check_simple.py <zip_file>")
        return
    
    zip_path = sys.argv[1]
    success = check_file_necessity(zip_path)
    
    if success:
        print("\n[FINAL] PASSED - ready for ClawHub")
        sys.exit(0)
    else:
        print("\n[FINAL] FAILED - need to fix issues")
        sys.exit(1)

if __name__ == "__main__":
    main()