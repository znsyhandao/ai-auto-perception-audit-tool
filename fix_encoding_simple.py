#!/usr/bin/env python3
"""
简单修复编码问题 - 不依赖chardet
"""

import os
import sys

def fix_file_encoding(file_path):
    """修复单个文件的编码"""
    try:
        # 尝试用不同编码读取
        encodings = ['utf-8', 'gbk', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # 成功读取，写入UTF-8无BOM
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  {file_path}: Fixed with {encoding} -> UTF-8")
                return True
                
            except UnicodeDecodeError:
                continue
        
        # 所有编码都失败，尝试二进制读取
        print(f"  {file_path}: All encodings failed, using binary fallback")
        with open(file_path, 'rb') as f:
            binary_content = f.read()
        
        # 尝试解码为ASCII兼容
        try:
            content = binary_content.decode('ascii', errors='ignore')
        except:
            content = binary_content.decode('latin-1', errors='ignore')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"  Error fixing {file_path}: {e}")
        return False

def fix_all_files(directory):
    """修复目录中的所有文件"""
    print(f"Fixing files in: {directory}")
    
    extensions = ['.py', '.ps1', '.md', '.txt', '.json', '.yaml', '.yml']
    fixed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件扩展名
            should_fix = any(file.endswith(ext) for ext in extensions)
            
            # 排除缓存和临时文件
            if '__pycache__' in root or file.startswith('.'):
                continue
            
            if should_fix:
                file_path = os.path.join(root, file)
                if fix_file_encoding(file_path):
                    fixed_count += 1
                else:
                    error_count += 1
    
    print(f"\nSummary:")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Errors: {error_count} files")
    
    return fixed_count, error_count

def main():
    """主函数"""
    print("=== Fixing Encoding Issues (Simple Version) ===")
    
    # 修复当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    fixed, errors = fix_all_files(current_dir)
    
    print(f"\n=== Final Summary ===")
    print(f"Total files fixed: {fixed}")
    print(f"Total errors: {errors}")
    
    if errors == 0:
        print("\n[SUCCESS] All files fixed successfully!")
        return 0
    else:
        print("\n[WARNING] Some files had errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())