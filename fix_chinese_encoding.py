#!/usr/bin/env python3
"""
修复测试套件中的中文编码问题
"""

import os
import sys

def fix_test_suite_encoding():
    """修复测试套件文件中的中文编码"""
    file_path = "improved_test_suite.py"
    
    print(f"Fixing Chinese encoding in: {file_path}")
    
    try:
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换中文描述为英文
        replacements = {
            '测试帮助命令': 'Test help command',
            '测试简单文件分析': 'Test simple file analysis',
            '测试第三方库分析': 'Test third-party library analysis',
            '测试数据流分析': 'Test data flow analysis',
            '测试性能分析': 'Test performance analysis',
            '分析依赖': 'Analyze dependencies',
            '分析数据流': 'Analyze data flow',
            '分析性能问题': 'Analyze performance issues',
            '综合深度分析': 'Comprehensive deep analysis',
            '大文件性能测试': 'Large file performance test',
            '测试不存在的文件': 'Test non-existent file',
            '测试无效语法': 'Test invalid syntax'
        }
        
        # 应用替换
        for chinese, english in replacements.items():
            content = content.replace(chinese, english)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Fixed: {len(replacements)} Chinese strings replaced with English")
        return True
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

def fix_all_files():
    """修复所有相关文件"""
    print("=== Fixing Chinese Encoding Issues ===")
    
    files_to_fix = [
        "improved_test_suite.py",
        "run_tool_tests.py"
    ]
    
    fixed_count = 0
    error_count = 0
    
    for file in files_to_fix:
        if os.path.exists(file):
            print(f"\nProcessing: {file}")
            
            try:
                # 简单的编码修复：确保UTF-8
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 移除可能的BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  Fixed encoding: {file}")
                fixed_count += 1
                
            except Exception as e:
                print(f"  Error fixing {file}: {e}")
                error_count += 1
        else:
            print(f"\nFile not found: {file}")
    
    # 专门修复测试套件的中文
    if fix_test_suite_encoding():
        fixed_count += 1
    
    print(f"\n=== Summary ===")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    
    if error_count == 0:
        print("\n[SUCCESS] All files fixed successfully!")
        return 0
    else:
        print("\n[WARNING] Some files had errors.")
        return 1

if __name__ == "__main__":
    sys.exit(fix_all_files())