#!/usr/bin/env python3
"""清理备份文件"""

import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python cleanup_backups.py <path>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    
    # 查找备份文件
    backup_patterns = ["*backup*.md", "*OLD*.md", "*_backup.md"]
    
    backup_files = []
    for pattern in backup_patterns:
        backup_files.extend(list(skill_path.rglob(pattern)))
    
    # 去重
    backup_files = list(set(backup_files))
    
    print(f"Found {len(backup_files)} backup files")
    
    if backup_files:
        print("\nBackup files to delete:")
        for backup in sorted(backup_files):
            print(f"  {backup.name}")
        
        # 确认删除
        confirm = input("\nDelete these files? (y/n): ")
        
        if confirm.lower() == 'y':
            deleted_count = 0
            for backup in backup_files:
                try:
                    backup.unlink()
                    print(f"Deleted: {backup.name}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {backup.name}: {e}")
            
            print(f"\nDeleted {deleted_count}/{len(backup_files)} files")
        else:
            print("Cancelled")
    else:
        print("No backup files found")

if __name__ == "__main__":
    main()