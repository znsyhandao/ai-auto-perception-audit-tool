#!/usr/bin/env python3
"""
文件必要性检查工具
基于2026-03-29 AISleepGen非文本文件教训
检查发布包中是否包含不必要的文件
"""

import os
import zipfile
import sys

def check_file_necessity(zip_path):
    """检查ZIP文件中的文件必要性"""
    
    print("=" * 80)
    print("File Necessity Check Tool")
    print("Based on 2026-03-29 AISleepGen non-text files lesson")
    print("=" * 80)
    
    if not os.path.exists(zip_path):
        print(f"[ERROR] ZIP file not found: {zip_path}")
        return False
    
    zip_size = os.path.getsize(zip_path) / 1024
    print(f"Checking: {zip_path}")
    print(f"Size: {zip_size:.1f} KB")
    
    # 问题文件类型
    problematic_files = {
        '.ps1': 'PowerShell scripts (often check/install scripts, not needed)',
        '.bat': 'Batch files (ClawHub flags as non-text files)',
        '.exe': 'Executable files (should not be in skill packages)',
        '.dll': 'DLL files (system dependencies, not skill files)',
        '.sh': 'Shell scripts (Linux, usually not needed)',
    }
    
    # 不必要的文件模式
    unnecessary_patterns = [
        'check_',      # 检查脚本
        'test_',       # 测试脚本（除非是必需的测试文件）
        'security_',   # 安全检查脚本
        'install',     # 安装脚本
        'setup',       # 设置脚本
        'backup',      # 备份文件
        '.backup',     # 备份文件后缀
        '.tmp',        # 临时文件
        '.temp',       # 临时文件
    ]
    
    found_problems = []
    found_unnecessary = []
    
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
            
            # 检查不必要的文件模式
            for pattern in unnecessary_patterns:
                if pattern in file_lower:
                    info = zipf.getinfo(file)
                    found_unnecessary.append({
                        'file': file,
                        'pattern': pattern,
                        'size': info.file_size,
                        'reason': f'Matches unnecessary pattern: {pattern}'
                    })
                    break
    
    # 输出结果
    print(f"\n" + "=" * 80)
    print("CHECK RESULTS:")
    print("=" * 80)
    
    if found_problems:
        print(f"[FAIL] Found {len(found_problems)} problematic files:")
        for problem in found_problems:
            print(f"  [ERROR] {problem['file']} ({problem['size']} bytes)")
            print(f"     Type: {problem['type']}")
            print(f"     Issue: {problem['description']}")
            print()
    else:
        print(f"[SUCCESS] No problematic file types found!")
    
    if found_unnecessary:
        print(f"[WARNING] Found {len(found_unnecessary)} potentially unnecessary files:")
        for unnecessary in found_unnecessary[:5]:  # 只显示前5个
            print(f"  [WARN]  {unnecessary['file']} ({unnecessary['size']} bytes)")
            print(f"     Reason: {unnecessary['reason']}")
            print()
        
        if len(found_unnecessary) > 5:
            print(f"  ... and {len(found_unnecessary) - 5} more files")
    else:
        print(f"[SUCCESS] No unnecessary files found!")
    
    # 必需文件检查
    print(f"\nChecking for required files...")
    print("-" * 40)
    
    required_files = [
        'skill.py',        # 主技能文件
        'config.yaml',     # 配置文件
        'package.json',    # 包元数据
        'README.md',       # 说明文档
        'SKILL.md',        # 技能文档
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
            print(f"  [ERROR] {missing}")
    else:
        print(f"\n[SUCCESS] All required files present!")
    
    # 总体评估
    print(f"\n" + "=" * 80)
    print("OVERALL ASSESSMENT:")
    print("=" * 80)
    
    has_problems = len(found_problems) > 0
    has_missing = len(missing_required) > 0
    
    if has_problems:
        print("[FAIL] Contains problematic files that may fail ClawHub validation")
        print("       Recommendation: Remove .ps1, .bat, and other non-text files")
    elif has_missing:
        print("[FAIL] Missing required files")
        print("       Recommendation: Add missing required files")
    else:
        print("[SUCCESS] File necessity check PASSED!")
        print("          Expected to pass ClawHub file validation")
    
    # 建议
    print(f"\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if found_problems:
        print("1. Remove these problematic files:")
        for problem in found_problems:
            print(f"   - {problem['file']} ({problem['type']})")
    
    if found_unnecessary:
        print("\n2. Consider removing these unnecessary files:")
        for unnecessary in found_unnecessary[:3]:
            print(f"   - {unnecessary['file']} ({unnecessary['reason']})")
    
    if not found_problems and not found_unnecessary:
        print("1. File necessity check passed - no changes needed")
    
    print("\n3. General guidelines:")
    print("   - Only include files necessary for skill operation")
    print("   - Remove all check, test, and install scripts")
    print("   - Use OpenClaw standard installation commands")
    print("   - Keep the package minimal and clean")
    
    print(f"\n" + "=" * 80)
    
    return not has_problems and not has_missing

def main():
    if len(sys.argv) < 2:
        print("Usage: python file_necessity_check.py <zip_file>")
        print("Example: python file_necessity_check.py AISleepGen-v1.0.6.zip")
        return
    
    zip_path = sys.argv[1]
    success = check_file_necessity(zip_path)
    
    if success:
        print("[FINAL] File necessity check PASSED - ready for ClawHub")
        sys.exit(0)
    else:
        print("[FINAL] File necessity check FAILED - need to fix issues")
        sys.exit(1)

if __name__ == "__main__":
    main()