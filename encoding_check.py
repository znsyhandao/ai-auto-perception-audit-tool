#!/usr/bin/env python3
"""
文件编码检查工具
基于2026-03-29 AISleepGen编码问题教训
检查BOM、编码一致性、乱码等问题
"""

import os
import sys

def check_file_encoding(file_path):
    """检查单个文件的编码问题"""
    
    results = {
        'file': os.path.basename(file_path),
        'bom': False,
        'encoding_issues': [],
        'warnings': []
    }
    
    try:
        # 检查BOM
        with open(file_path, 'rb') as f:
            first_3 = f.read(3)
            
        if first_3.startswith(b'\xef\xbb\xbf'):
            results['bom'] = True
            results['encoding_issues'].append('UTF-8 BOM detected')
        
        # 尝试用UTF-8解码
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 检查可能的乱码
            if '鐪' in content or '犲' in content or '皬' in content:
                results['warnings'].append('Possible Chinese character corruption detected')
                
            # 检查BOM字符
            if '\ufeff' in content:
                results['encoding_issues'].append('BOM character (\\ufeff) in content')
                
        except UnicodeDecodeError as e:
            results['encoding_issues'].append(f'UTF-8 decode error: {e}')
            
            # 尝试用GBK解码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
                results['warnings'].append('File uses GBK encoding (should be UTF-8)')
            except:
                results['encoding_issues'].append('Cannot decode with UTF-8 or GBK')
                
    except Exception as e:
        results['encoding_issues'].append(f'Error checking file: {e}')
    
    return results

def check_directory_encoding(directory_path):
    """检查目录中所有文件的编码"""
    
    print("=" * 80)
    print("File Encoding Check Tool")
    print("Based on 2026-03-29 AISleepGen encoding lesson")
    print("=" * 80)
    
    # 需要检查的文件类型
    extensions = ['.py', '.js', '.md', '.yaml', '.yml', '.json', '.txt', '.html', '.css']
    
    files_to_check = []
    for root, dirs, files in os.walk(directory_path):
        # 排除备份目录
        if 'backup' in root.lower() or 'node_modules' in root:
            continue
            
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                files_to_check.append(os.path.join(root, file))
    
    print(f"Checking {len(files_to_check)} files in {directory_path}")
    print("=" * 80)
    
    all_results = []
    bom_files = []
    encoding_issue_files = []
    warning_files = []
    
    for file_path in files_to_check:
        results = check_file_encoding(file_path)
        all_results.append(results)
        
        if results['bom']:
            bom_files.append(results['file'])
            
        if results['encoding_issues']:
            encoding_issue_files.append(results['file'])
            
        if results['warnings']:
            warning_files.append(results['file'])
    
    # 输出结果
    if bom_files:
        print(f"\n[FAIL] Files with BOM ({len(bom_files)}):")
        for file in bom_files:
            print(f"  {file}")
    else:
        print(f"\n[OK] No files with BOM")
    
    if encoding_issue_files:
        print(f"\n[FAIL] Files with encoding issues ({len(encoding_issue_files)}):")
        for file in encoding_issue_files:
            print(f"  {file}")
    else:
        print(f"\n[OK] No files with encoding issues")
    
    if warning_files:
        print(f"\n[WARNING] Files with warnings ({len(warning_files)}):")
        for file in warning_files:
            print(f"  {file}")
    else:
        print(f"\n[OK] No warnings")
    
    # 详细报告
    print(f"\n" + "=" * 80)
    print("Detailed Report:")
    print("=" * 80)
    
    for results in all_results:
        if results['bom'] or results['encoding_issues']:
            print(f"\n{results['file']}:")
            if results['bom']:
                print(f"  [BOM] UTF-8 BOM detected")
            for issue in results['encoding_issues']:
                print(f"  [ISSUE] {issue}")
            for warning in results['warnings']:
                print(f"  [WARNING] {warning}")
    
    # 总体评估
    print(f"\n" + "=" * 80)
    print("Overall Assessment:")
    print("=" * 80)
    
    total_issues = len(bom_files) + len(encoding_issue_files)
    
    if total_issues == 0:
        print("[SUCCESS] All files have correct encoding")
        print("No BOM, no encoding issues")
        return True
    else:
        print(f"[FAIL] Found {total_issues} encoding issues")
        print(f"  BOM files: {len(bom_files)}")
        print(f"  Encoding issues: {len(encoding_issue_files)}")
        print(f"  Warnings: {len(warning_files)}")
        
        print(f"\nRecommendations:")
        print("1. Remove BOM from affected files")
        print("2. Convert files to UTF-8 encoding")
        print("3. Test file reading with UTF-8")
        print("4. Re-run this check after fixes")
        
        return False

def fix_bom_in_file(file_path):
    """修复文件的BOM问题"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        if content.startswith(b'\xef\xbb\xbf'):
            # 移除BOM
            new_content = content[3:]
            with open(file_path, 'wb') as f:
                f.write(new_content)
            return True, "BOM removed"
        else:
            return False, "No BOM"
            
    except Exception as e:
        return False, f"Error: {e}"

def fix_all_bom(directory_path):
    """修复目录中所有文件的BOM"""
    
    print("=" * 80)
    print("Fix BOM in Files")
    print("=" * 80)
    
    extensions = ['.py', '.js', '.md', '.yaml', '.yml', '.json', '.txt']
    
    files_fixed = []
    errors = []
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                fixed, message = fix_bom_in_file(file_path)
                
                if fixed:
                    files_fixed.append(file)
                elif "Error" in message:
                    errors.append(f"{file}: {message}")
    
    print(f"\nResults:")
    print(f"  Files fixed: {len(files_fixed)}")
    print(f"  Errors: {len(errors)}")
    
    if files_fixed:
        print(f"\nFixed files:")
        for file in files_fixed:
            print(f"  {file}")
    
    if errors:
        print(f"\nErrors:")
        for error in errors:
            print(f"  {error}")
    
    # 重新检查
    print(f"\n" + "=" * 80)
    print("Re-checking after fixes...")
    print("=" * 80)
    
    success = check_directory_encoding(directory_path)
    
    return success

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python encoding_check.py <directory>          # Check encoding")
        print("  python encoding_check.py <directory> --fix    # Check and fix BOM")
        print("  python encoding_check.py <file>               # Check single file")
        return
    
    target = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == '--fix':
        # 检查并修复
        if os.path.isdir(target):
            success = fix_all_bom(target)
        else:
            print(f"[ERROR] {target} is not a directory")
            return
    else:
        # 只检查
        if os.path.isdir(target):
            success = check_directory_encoding(target)
        elif os.path.isfile(target):
            results = check_file_encoding(target)
            print(f"\nFile: {results['file']}")
            if results['bom']:
                print(f"[FAIL] Has BOM")
            if results['encoding_issues']:
                for issue in results['encoding_issues']:
                    print(f"[ISSUE] {issue}")
            if results['warnings']:
                for warning in results['warnings']:
                    print(f"[WARNING] {warning}")
            
            if not results['bom'] and not results['encoding_issues']:
                print("[OK] No encoding issues")
                success = True
            else:
                success = False
        else:
            print(f"[ERROR] {target} not found")
            return
    
    if success:
        print(f"\n[SUCCESS] Encoding check passed")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Encoding check failed")
        sys.exit(1)

if __name__ == "__main__":
    main()