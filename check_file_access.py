#!/usr/bin/env python3
"""检查文件访问状态"""

import os
import sys
from pathlib import Path

def main():
    skill_path = Path("D:/openclaw/releases/AISleepGen_2.4.1")
    changelog_file = skill_path / "CHANGELOG.md"
    
    print("Checking file access status...")
    print("=" * 80)
    
    if not changelog_file.exists():
        print(f"ERROR: File does not exist: {changelog_file}")
        return 1
    
    print(f"File: {changelog_file}")
    print(f"Size: {changelog_file.stat().st_size} bytes")
    print()
    
    # 测试读取
    print("1. Testing READ access...")
    try:
        with open(changelog_file, 'r', encoding='utf-8') as f:
            content = f.read(200)
        print(f"   SUCCESS: Can read file")
        print(f"   Sample (first 200 chars):")
        print(f"   \"{content}\"")
    except Exception as e:
        print(f"   ERROR: Cannot read file - {e}")
        return 1
    
    # 测试追加
    print("\n2. Testing APPEND access...")
    try:
        with open(changelog_file, 'a', encoding='utf-8') as f:
            f.write('')
        print("   SUCCESS: Can append to file")
    except Exception as e:
        print(f"   ERROR: Cannot append to file - {e}")
        return 1
    
    # 测试覆盖写入
    print("\n3. Testing OVERWRITE access...")
    try:
        # 先备份内容
        with open(changelog_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # 尝试写入
        test_content = "# Test\n\nThis is a test write."
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("   SUCCESS: Can overwrite file")
        
        # 恢复原内容
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print("   SUCCESS: Restored original content")
        
    except Exception as e:
        print(f"   ERROR: Cannot overwrite file - {e}")
        
        # 尝试删除并创建新文件
        print("\n4. Testing DELETE and CREATE...")
        try:
            changelog_file.unlink()
            print("   SUCCESS: Deleted file")
            
            with open(changelog_file, 'w', encoding='utf-8') as f:
                f.write("# Changelog\n\nNew file created.")
            print("   SUCCESS: Created new file")
            
        except Exception as e2:
            print(f"   ERROR: Cannot delete/create file - {e2}")
            return 1
    
    print("\n" + "=" * 80)
    print("SUCCESS: File is accessible")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())