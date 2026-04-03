#!/usr/bin/env python3
"""
修复所有Python文件的编码问题
"""

import os
import sys
import chardet

def detect_encoding(file_path):
    """检测文件编码"""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'], result['confidence']

def convert_to_utf8(file_path):
    """将文件转换为UTF-8无BOM"""
    try:
        # 检测当前编码
        encoding, confidence = detect_encoding(file_path)
        print(f"  {file_path}: {encoding} (confidence: {confidence:.2f})")
        
        # 读取文件内容
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        # 写入UTF-8无BOM
        with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"  Error converting {file_path}: {e}")
        return False

def fix_python_files(directory):
    """修复目录中的所有Python文件"""
    print(f"Fixing Python files in: {directory}")
    
    fixed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if convert_to_utf8(file_path):
                    fixed_count += 1
                else:
                    error_count += 1
    
    print(f"\nSummary:")
    print(f"  Fixed: {fixed_count} files")
    print(f"  Errors: {error_count} files")
    
    return fixed_count, error_count

def fix_ps1_files(directory):
    """修复PowerShell脚本文件"""
    print(f"\nFixing PowerShell files in: {directory}")
    
    fixed_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.ps1'):
                file_path = os.path.join(root, file)
                try:
                    # PowerShell文件通常使用UTF-8或ANSI
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # 检查是否有BOM
                    if content.startswith('\ufeff'):
                        content = content[1:]  # 移除BOM
                    
                    # 写入UTF-8无BOM
                    with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(content)
                    
                    print(f"  {file_path}: Fixed (UTF-8 no BOM)")
                    fixed_count += 1
                except Exception as e:
                    print(f"  Error fixing {file_path}: {e}")
                    error_count += 1
    
    return fixed_count, error_count

def main():
    """主函数"""
    print("=== Fixing Encoding Issues ===")
    
    # 修复当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 修复Python文件
    py_fixed, py_errors = fix_python_files(current_dir)
    
    # 修复PowerShell文件
    ps_fixed, ps_errors = fix_ps1_files(current_dir)
    
    print(f"\n=== Summary ===")
    print(f"Python files: {py_fixed} fixed, {py_errors} errors")
    print(f"PowerShell files: {ps_fixed} fixed, {ps_errors} errors")
    
    if py_errors == 0 and ps_errors == 0:
        print("\n[SUCCESS] All files fixed successfully!")
        return 0
    else:
        print("\n[WARNING] Some files had errors.")
        return 1

if __name__ == "__main__":
    sys.exit(main())