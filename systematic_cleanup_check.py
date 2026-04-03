#!/usr/bin/env python3
"""
系统性清理检查工具
基于2026-03-29 AISleepGen系统性清理教训
检查所有相关位置的问题文件
"""

import os
import zipfile
import sys

def check_systematic_cleanup(project_name, version):
    """检查系统性清理"""
    
    print("=" * 80)
    print("Systematic Cleanup Check Tool")
    print("Based on 2026-03-29 AISleepGen systematic cleanup lesson")
    print("=" * 80)
    
    # 定义所有需要检查的位置
    locations = [
        {
            "name": "Source Directory",
            "path": f"D:/openclaw/{project_name}/openclaw_skill",
            "type": "directory"
        },
        {
            "name": "Release Folder",
            "path": f"D:/openclaw/releases/{project_name}/v{version}",
            "type": "directory"
        },
        {
            "name": "ZIP Package",
            "path": f"D:/openclaw/releases/{project_name}/{project_name}-v{version}.zip",
            "type": "zip"
        },
        {
            "name": "Backup Directory",
            "path": f"D:/openclaw/{project_name}/openclaw_skill/backup_md_files",
            "type": "directory",
            "optional": True
        }
    ]
    
    # 问题文件类型
    problematic_files = {
        '.ps1': 'PowerShell scripts',
        '.bat': 'Batch files',
        '.exe': 'Executable files',
        '.dll': 'DLL files',
    }
    
    all_results = {}
    all_clean = True
    
    print(f"Project: {project_name}")
    print(f"Version: {version}")
    print(f"\nChecking {len(locations)} locations...")
    print("=" * 80)
    
    for location in locations:
        location_name = location["name"]
        location_path = location["path"]
        location_type = location["type"]
        is_optional = location.get("optional", False)
        
        print(f"\n{location_name}:")
        print(f"  Path: {location_path}")
        
        if not os.path.exists(location_path):
            if is_optional:
                print(f"  [INFO] Optional location not found (OK)")
                continue
            else:
                print(f"  [ERROR] Location not found")
                all_clean = False
                all_results[location_name] = {"status": "missing", "files": []}
                continue
        
        location_results = []
        
        if location_type == "zip":
            # 检查ZIP文件
            try:
                with zipfile.ZipFile(location_path, 'r') as zipf:
                    for file in zipf.namelist():
                        file_lower = file.lower()
                        for ext, description in problematic_files.items():
                            if file_lower.endswith(ext):
                                info = zipf.getinfo(file)
                                location_results.append({
                                    'file': file,
                                    'type': ext,
                                    'size': info.file_size,
                                    'description': description
                                })
            except Exception as e:
                print(f"  [ERROR] Could not check ZIP: {e}")
                all_clean = False
        else:
            # 检查目录
            for root, dirs, files in os.walk(location_path):
                for file in files:
                    file_lower = file.lower()
                    for ext, description in problematic_files.items():
                        if file_lower.endswith(ext):
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            location_results.append({
                                'file': os.path.relpath(file_path, location_path),
                                'type': ext,
                                'size': file_size,
                                'description': description
                            })
        
        if location_results:
            print(f"  [FAIL] Found {len(location_results)} problematic files")
            all_clean = False
            for result in location_results[:3]:  # 只显示前3个
                print(f"    {result['file']} ({result['type']})")
            if len(location_results) > 3:
                print(f"    ... and {len(location_results) - 3} more")
        else:
            print(f"  [SUCCESS] No problematic files")
        
        all_results[location_name] = {
            "status": "clean" if not location_results else "dirty",
            "files": location_results,
            "count": len(location_results)
        }
    
    # 总体评估
    print(f"\n" + "=" * 80)
    print("SYSTEMATIC CLEANUP ASSESSMENT:")
    print("=" * 80)
    
    dirty_locations = []
    for location_name, result in all_results.items():
        if result["status"] == "dirty":
            dirty_locations.append(location_name)
    
    if dirty_locations:
        print(f"[FAIL] {len(dirty_locations)} locations still contain problematic files:")
        for location in dirty_locations:
            print(f"  - {location}: {all_results[location]['count']} files")
        all_clean = False
    else:
        print(f"[SUCCESS] All locations are clean!")
    
    # 一致性检查
    print(f"\n" + "=" * 80)
    print("CONSISTENCY CHECK:")
    print("=" * 80)
    
    # 检查源目录和发布文件夹的一致性
    source_dir = f"D:/openclaw/{project_name}/openclaw_skill"
    release_dir = f"D:/openclaw/releases/{project_name}/v{version}"
    
    if os.path.exists(source_dir) and os.path.exists(release_dir):
        print("Checking consistency between source and release directories...")
        
        # 简单的一致性检查：比较文件数量
        source_files = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if not file.endswith('.backup') and not file.endswith('.tmp'):
                    source_files.append(file)
        
        release_files = []
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                if not file.endswith('.backup') and not file.endswith('.tmp'):
                    release_files.append(file)
        
        print(f"  Source directory: {len(source_files)} files")
        print(f"  Release directory: {len(release_files)} files")
        
        if abs(len(source_files) - len(release_files)) > 5:
            print(f"  [WARNING] Significant file count difference")
        else:
            print(f"  [OK] File counts are similar")
    else:
        print("  [INFO] Cannot perform consistency check (directories missing)")
    
    # 建议
    print(f"\n" + "=" * 80)
    print("RECOMMENDATIONS:")
    print("=" * 80)
    
    if all_clean:
        print("1. All locations are clean - ready for release")
        print("2. Maintain this clean state throughout development")
        print("3. Run this check before every release")
    else:
        print("1. Clean up problematic files in all locations:")
        for location_name, result in all_results.items():
            if result["status"] == "dirty":
                print(f"   - {location_name}: {result['count']} files to remove")
        
        print("\n2. Follow systematic cleanup process:")
        print("   a. Identify all problematic files")
        print("   b. Remove from ALL locations")
        print("   c. Verify all locations are clean")
        print("   d. Recreate release package")
        
        print("\n3. Prevent recurrence:")
        print("   a. Add pre-commit hooks")
        print("   b. Add CI/CD checks")
        print("   c. Document cleanup procedures")
    
    print(f"\n" + "=" * 80)
    print("FINAL STATUS:")
    print("=" * 80)
    
    if all_clean:
        print("[SUCCESS] Systematic cleanup check PASSED")
        print("All locations are clean and consistent")
        return True
    else:
        print("[FAIL] Systematic cleanup check FAILED")
        print("Need to clean up problematic files in all locations")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python systematic_cleanup_check.py <project_name> <version>")
        print("Example: python systematic_cleanup_check.py AISleepGen 1.0.6")
        return
    
    project_name = sys.argv[1]
    version = sys.argv[2]
    
    success = check_systematic_cleanup(project_name, version)
    
    if success:
        print("\n[FINAL] Ready for ClawHub submission")
        sys.exit(0)
    else:
        print("\n[FINAL] Need to fix systematic cleanup issues")
        sys.exit(1)

if __name__ == "__main__":
    main()